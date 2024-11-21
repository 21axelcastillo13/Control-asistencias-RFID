import sqlite3
from datetime import datetime

def obtener_clases_hoy():
    # Obtener el día de la semana actual (0=Lunes, 1=Martes, ..., 6=Sábado)
    hoy = datetime.now()
    dia_actual = hoy.weekday() + 1  # Ajustar el día para que coincida con la tabla 'dia'

    # Establecer la conexión a la base de datos
    try:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()

        # Obtener el nombre del día actual desde la tabla 'dia'
        cursor.execute("SELECT id_dia, nombre FROM dia WHERE id_dia = ?", (dia_actual,))
        dia = cursor.fetchone()

        if not dia:
            return "No se encontró el día actual en la base de datos."

        # Consultar las clases programadas para hoy junto con los docentes que las imparten
        cursor.execute('''
            SELECT c.nombre AS clase_nombre, cd.hora_inicio, cd.hora_fin, d.nombre AS docente_nombre 
            FROM clase_dia cd
            JOIN clase c ON cd.id_clase= c.id_clase
            JOIN docente_clase dc ON c.id_clase = dc.id_clase
            JOIN docente d ON dc.id_docente = d.id_docente
            WHERE cd.id_dia = ?
        ''', (dia[0],))

        clases = cursor.fetchall()

        conn.close()

        if not clases:
            return "No hay clases programadas para hoy."

        # Mostrar las clases de hoy con el docente
        return clases

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        return "Error al obtener las clases."

# Llamar a la función y mostrar las clases
clases_hoy = obtener_clases_hoy()
print(clases_hoy)
