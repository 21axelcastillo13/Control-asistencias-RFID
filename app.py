from flask import Flask, jsonify, render_template, request
import serial
import sqlite3
from datetime import datetime
import os
from fpdf import FPDF

app = Flask(__name__)
try:
    arduino = serial.Serial('COM4', 9600, timeout=1)
    print("Arduino conectado correctamente.")
except serial.SerialException:
    arduino = None
    print("No se pudo conectar al Arduino en COM4. La app seguirá funcionando.")
    
    
def get_db_connection():
    conn = sqlite3.connect('usuarios.db') 
    conn.row_factory = sqlite3.Row
    return conn


# Función para obtener las asistencias del día actual
def obtener_asistencias_del_dia():
    try:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()

        # Obtener las asistencias para la fecha actual
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT d.nombre, a.entrada, a.salida, c.nombre AS clase,d.imageurl as imagen, a.id
            FROM asistencia a
            JOIN docente d ON a.id_docente = d.id_docente
            JOIN docente_clase dc ON d.id_docente = dc.id_docente
            JOIN clase c ON dc.id_clase = c.id_clase
            WHERE DATE(a.entrada) = ? 
            AND a.id_clase = dc.id_clase
        """, (fecha_actual,))           

        asistencias = cursor.fetchall()
        conn.close()

        return asistencias
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        return []


# Función para verificar el RFID y registrar la entrada/salida
def verificar_rfid(rfid_code):
    try:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM docente WHERE rfid_code = ?", (rfid_code,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        return None

def registrar_entrada_salida(rfid_code):
    try:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()

        # Obtener el id_docente asociado al RFID
        cursor.execute("SELECT id_docente FROM docente WHERE rfid_code = ?", (rfid_code,))
        docente = cursor.fetchone()

        if not docente:
            return "RFID no válido"

        id_docente = docente[0]

        # Determinar el día actual y traducirlo
        dia_actual = datetime.now().strftime('%A')
        dias_traducidos = {
            'Monday': 'Lunes',
            'Tuesday': 'Martes',
            'Wednesday': 'Miércoles',
            'Thursday': 'Jueves',
            'Friday': 'Viernes',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        dia_traducido = dias_traducidos.get(dia_actual, None)
        if not dia_traducido:
            return "Error: No se pudo determinar el día actual"

        # Buscar el id_dia en la base de datos
        cursor.execute("SELECT id_dia FROM dia WHERE nombre = ?", (dia_traducido,))
        dia = cursor.fetchone()
        if not dia:
            return f"Día {dia_traducido} no permitido"

        id_dia = dia[0]

        # Obtener la hora actual
        ahora = datetime.now()

        # Consultar las clases activas para el docente y el día actual
        cursor.execute(''' 
            SELECT c.id_clase, c.nombre 
            FROM clase c
            INNER JOIN docente_clase dc ON c.id_clase = dc.id_clase
            INNER JOIN clase_dia cd ON c.id_clase = cd.id_clase
            WHERE dc.id_docente = ? AND cd.id_dia = ?
        ''', (id_docente, id_dia))

        clases_activas = cursor.fetchall()
        if not clases_activas:
            return "No hay clases activas hoy"

        for clase in clases_activas:
            id_clase, nombre_clase = clase

            # Verificar si ya existe un registro de entrada y salida para esta clase en el día actual
            cursor.execute(''' 
                SELECT * FROM asistencia 
                WHERE id_docente = ? AND id_clase = ? 
                  AND DATE(entrada) = DATE(?) AND salida IS NOT NULL
            ''', (id_docente, id_clase, ahora.strftime('%Y-%m-%d')))

            asistencia_existente = cursor.fetchone()
            if asistencia_existente:
                # Ya se ha registrado la entrada y salida para esta clase en el día de hoy
                action = f"Asistencia ya registrada"
                print(action)
                continue  # Pasar a la siguiente clase si ya está registrada

            # Verificar si ya existe una entrada sin salida (entrada activa)
            cursor.execute(''' 
                SELECT id FROM asistencia 
                WHERE id_docente = ? AND id_clase = ? AND salida IS NULL 
                  AND DATE(entrada) = DATE(?)
            ''', (id_docente, id_clase, ahora.strftime('%Y-%m-%d')))

            entrada_activa = cursor.fetchone()

            if entrada_activa:
                # Si ya hay una entrada sin salida, registrar la salida
                cursor.execute(''' 
                    UPDATE asistencia 
                    SET salida = ? 
                    WHERE id = ?
                ''', (ahora.strftime('%Y-%m-%d %H:%M:%S'), entrada_activa[0]))  # Guardar fecha y hora completa
                action = f"Salida: {nombre_clase}"
            else:
                # Si no hay entrada, registrar una nueva entrada
                cursor.execute(''' 
                    INSERT INTO asistencia (id_docente, id_clase, entrada) 
                    VALUES (?, ?, ?)
                ''', (id_docente, id_clase, ahora.strftime('%Y-%m-%d %H:%M:%S')))  # Guardar fecha y hora completa
                action = f"Entrada: {nombre_clase}"

            # Guardar los cambios
            conn.commit()
            return action

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        return "Error al registrar la asistencia"
    finally:
        conn.close()
    return action 


@app.route('/')
def index():
    # Obtener las asistencias del día actual
    asistencias = obtener_asistencias_del_dia()
    return render_template('index.html', asistencias=asistencias)

@app.route('/rfid', methods=['GET'])
def rfid():
    if arduino.in_waiting > 0:
        try:
            rfid_code = arduino.readline().decode().strip()
            nombre = verificar_rfid(rfid_code)

            if nombre:
                # Registra la entrada o salida
                action = registrar_entrada_salida(rfid_code)
                print(f"{action} - {nombre}")

                # Envía el nombre y la acción (entrada/salida) al Arduino
                print(f"Enviando: {action}\n{nombre}")
                arduino.write(f"{action}\n{nombre}\n".encode())

                # Obtener las asistencias actualizadas para la fecha actual
                asistencias = obtener_asistencias_del_dia()

                return jsonify({"asistencias": asistencias}), 200
            else:
                return jsonify({"error": "Usuario no encontrado"}), 404
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Error al procesar RFID"}), 500
    else:
        return jsonify({"message": "Esperando RFID..."}), 400

@app.route('/procesar', methods=['POST'])
def procesar():
    # Obtener datos del formulario
    tipo_reporte = request.form.get('tipo_reporte')
    frecuencia = request.form.get('frecuencia')
    id_docente = request.form.get('id_docente')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').strftime('%Y-%m-%d')
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').strftime('%Y-%m-%d')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if tipo_reporte == 'general' and frecuencia == 'diario' and fecha_inicio:
            cursor.execute("""SELECT a.id,a.id_docente,a.id_clase,TIME(a.entrada) AS entrada,
                           TIME(a.salida) AS salida,d.nombre AS nombre,c.nombre AS clase 
                           FROM asistencia a
                           JOIN docente d ON a.id_docente = d.id_docente
                           JOIN clase c ON a.id_clase = c.id_clase
                           WHERE DATE(a.entrada) = ?""", (fecha_inicio,))
        elif tipo_reporte == 'general' and frecuencia == 'semanal' and fecha_inicio and fecha_fin:
            cursor.execute("""
                SELECT a.*,d.nombre AS nombre, c.nombre AS clase 
                FROM asistencia a
                JOIN docente d ON a.id_docente = d.id_docente
                JOIN clase c ON a.id_clase = c.id_clase
                WHERE DATE(a.entrada) >= ? AND DATE(a.entrada) <= ?
            """, (fecha_inicio, fecha_fin))
        elif tipo_reporte == 'individual' and frecuencia == 'diario' and id_docente and fecha_inicio:
            cursor.execute("""
                SELECT a.id,a.id_docente,a.id_clase,TIME(a.entrada) AS entrada,
                TIME(a.salida) AS salida,d.nombre AS nombre, c.nombre AS clase 
                FROM asistencia a
                JOIN docente d ON a.id_docente = d.id_docente
                JOIN clase c ON a.id_clase = c.id_clase
                WHERE a.id_docente = ? AND DATE(a.entrada) = ?
            """, (id_docente, fecha_inicio))
        elif tipo_reporte == 'individual' and frecuencia == 'semanal' and id_docente and fecha_inicio and fecha_fin:
            cursor.execute("""
                SELECT a.*, d.nombre AS nombre, c.nombre AS clase
                FROM asistencia a
                JOIN docente d ON a.id_docente = d.id_docente 
                JOIN clase c ON a.id_clase = c.id_clase
                WHERE a.id_docente = ? AND DATE(a.entrada) >= ? AND DATE(a.entrada) <= ?
            """, (id_docente, fecha_inicio, fecha_fin))
        else:
            return jsonify({"error": "Condiciones inválidas para la consulta"}), 400

        # Obtener resultados
        asistencias = cursor.fetchall()
        conn.close()
         

        # Convertir resultados en lista de diccionarios
        resultados = [dict(asistencia) for asistencia in asistencias]
        print("Resultados de la consulta:", resultados)
        # return jsonify({"success": True, "data": resultados})
        
           # Si no se encontraron datos
        if not resultados:
            return jsonify({"NoAsistencias": "No se encontraron registros según los requisitos"})
        
        respuesta = generar_pdf_dinamico(
            tipo_reporte=tipo_reporte,
            frecuencia=frecuencia,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            docente=resultados[0].get('nombre') if resultados else None,
            resultados=resultados
        )
        
        
        # Acceder a los datos del JSON retornado
        pdf_message = respuesta.json['message']
        pdf_filename = respuesta.json['nombre']
        pdf_ruta = respuesta.json['ruta']

        return jsonify({
            "status": "success",
            "pdf_message": pdf_message,
            "pdf_filename": pdf_filename,
            "pdf_ruta": pdf_ruta
        })
    
    except Exception as e:
        print(f"Error en el servidor: {e}")
        conn.close()
        return jsonify({"error": str(e)}), 500


def generar_pdf_dinamico(tipo_reporte, frecuencia, fecha_inicio, fecha_fin=None, docente=None, resultados=[]):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Encabezado general
    pdf.add_page()
    pdf.image("./static/img/logo.png", x=10, y=8, w=33)
    pdf.ln(15)
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(29, 25, 52)
    pdf.cell(190, 10, "Registro de Asistencias", 0, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    # Tipo de Reporte
    if tipo_reporte:
        pdf.cell(190, 10, f"Tipo de Reporte: {tipo_reporte.capitalize()}", ln=True)

    # Frecuencia
    if frecuencia:
        pdf.cell(190, 10, f"Frecuencia: {frecuencia.capitalize()}", ln=True)

    # Fecha de Inicio
    if fecha_inicio:
        pdf.cell(190, 10, f"Fecha de Inicio: {fecha_inicio}", ln=True)

    # Fecha de Fin
    if fecha_fin:
        pdf.cell(190, 10, f"Fecha de Fin: {fecha_fin}", ln=True)

    # Docente ID
    if tipo_reporte == 'individual':
        pdf.cell(190, 10, f"Docente: {docente}", ln=True)

    # Espacio adicional después del encabezado
    pdf.ln(10)

    # Crear tabla según los datos disponibles
    pdf.set_font("Arial", "", 10)
    ancho_total = 190
    columnas = []
    anchos = []

    # Configurar columnas dinámicamente según el tipo de reporte
    if tipo_reporte == "general":
        columnas = ["Docente", "Clase", "Entrada", "Salida"]
        anchos = [0.2, 0.3, 0.2, 0.2]
    elif tipo_reporte == "individual":
        columnas = ["Clase", "Entrada", "Salida"]
        anchos = [0.3, 0.3, 0.3]

    # Encabezado de la tabla
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(0, 130, 202)
    for i, columna in enumerate(columnas):
        pdf.cell(anchos[i] * 200, 10, columna, border=1, align="C", fill=True)
    pdf.ln()

    # Alternar el color de las filas y agregar los datos
    pdf.set_text_color(0, 0, 0)
    for index, fila in enumerate(resultados):
        if index % 2 == 0:  # Índices pares (0, 2, 4, ...) son grises
            pdf.set_fill_color(244, 244, 244)  # Color gris claro
        else:  # Índices impares (1, 3, 5, ...) son blancos
            pdf.set_fill_color(255, 255, 255)  # Color blanco como fondo

        # Si el reporte es "general"
        if tipo_reporte == "general":
            docente = fila.get("nombre", "N/A")  # Nombre del docente (si está disponible)
            clase = fila.get("clase", "N/A")  # Nombre de la clase
            entrada = fila.get("entrada", "N/A")  # Entrada
            salida = fila.get("salida", "N/A")  # Salida

            # Imprimir los valores en la tabla
            pdf.cell(anchos[0] * 200, 10, docente, border=1, align="C", fill=True)
            pdf.cell(anchos[1] * 200, 10, clase, border=1, align="C", fill=True)
            pdf.cell(anchos[2] * 200, 10, entrada, border=1, align="C", fill=True)
            pdf.cell(anchos[3] * 200, 10, salida, border=1, align="C", fill=True)

        # Si el reporte es "individual"
        elif tipo_reporte == "individual":
            clase = fila.get("clase", "N/A")  # Nombre de la clase
            entrada = fila.get("entrada", "N/A")  # Entrada
            salida = fila.get("salida", "N/A")  # Salida

            # Imprimir los valores en la tabla
            pdf.cell(anchos[0] * 200, 10, clase, border=1, align="C", fill=True)
            pdf.cell(anchos[1] * 200, 10, entrada, border=1, align="C", fill=True)
            pdf.cell(anchos[2] * 200, 10, salida, border=1, align="C", fill=True)

        pdf.ln()

    # Guardar PDF
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    if tipo_reporte == 'general' and frecuencia == 'diario':
        pdf_filename = f"reporte-{tipo_reporte}-{frecuencia}-{fecha_inicio}.pdf"
        ruta = os.path.join("static","reportes","diarios","general")
    elif tipo_reporte == 'general' and frecuencia == 'semanal':
        pdf_filename=f"reporte-{tipo_reporte}-{frecuencia}-{fecha_inicio}-{fecha_fin}.pdf"
        ruta = os.path.join("static","reportes","rango-fechas","general")
    elif tipo_reporte == 'individual' and frecuencia =='diario':
        docente = resultados[0].get('nombre', "N/A") if resultados and 'nombre' in resultados[0] else "N/A"
        pdf_filename = f"reporte-{tipo_reporte}-{frecuencia}-{fecha_inicio}-{docente}.pdf"
        ruta = os.path.join("static","reportes","diarios","individual")
    elif tipo_reporte == 'individual' and frecuencia == 'semanal':
        docente = resultados[0].get('nombre', "N/A") if resultados and 'nombre' in resultados[0] else "N/A"
        pdf_filename=f"reporte-{tipo_reporte}-{frecuencia}-{fecha_inicio}-{fecha_fin}-{docente}.pdf"
        ruta = os.path.join("static","reportes","rango-fechas","individual")   
    else:
        return jsonify({"error: Invalido" }) ,400   
    
    if not os.path.exists(ruta):
        os.makedirs(ruta)
        
    pdf.output(os.path.join(ruta, pdf_filename))
    return jsonify({
        "message": "PDF generado exitosamente",
        "nombre": pdf_filename,
        "ruta": ruta
    })

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001)
