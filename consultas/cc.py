import sqlite3

def obtener_registros_de_todas_las_tablas():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    # Obtiene el nombre de todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()

    # Recorre cada tabla y obtiene sus registros 
    for tabla in tablas:
        nombre_tabla = tabla[0]
        print(f"Registros de la tabla: {nombre_tabla}")
        
        # Ejecuta una consulta para obtener todos los registros de la tabla
        cursor.execute(f"SELECT * FROM {nombre_tabla};")
        registros = cursor.fetchall()

        # Imprime los registros de la tabla
        if registros:
            for registro in registros:
                print(registro)
        else:
            print("No hay registros en esta tabla.")
        print("-" * 50)  # Separador entre tablas

    conn.close()

# Llamar a la función
obtener_registros_de_todas_las_tablas()
