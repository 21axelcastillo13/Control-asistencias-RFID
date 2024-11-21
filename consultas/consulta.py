import sqlite3

# Función para mostrar los registros de cada tabla
def mostrar_registros():
    try:
        # Conexión a la base de datos SQLite
        connection = sqlite3.connect('usuarios.db') 
        cursor = connection.cursor()

        # Consultas para obtener todos los registros de cada tabla
        tablas = ['docente', 'aula', 'dia', 'clase', 'clase_dia', 'docente_clase','asistencia']
        
        for tabla in tablas:
            print(f"\nRegistros de la tabla '{tabla}':")
            query_select = f"SELECT * FROM {tabla};"
            cursor.execute(query_select)
            registros = cursor.fetchall()

            if registros:
                for registro in registros:
                    print(registro)
            else:
                print(f"No hay registros en la tabla '{tabla}'.")

    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    
    finally:
        if connection:
            connection.close()  # Cierra la conexión

if __name__ == "__main__":
    mostrar_registros()
