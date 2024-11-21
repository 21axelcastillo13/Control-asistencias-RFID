import sqlite3

# Conectar a la base de datos (reemplaza 'nombre_de_base_de_datos.db' con el nombre de tu archivo de base de datos)
conn = sqlite3.connect('usuarios.db')

# Crear un cursor
cursor = conn.cursor()

# Ejecutar la consulta SQL para borrar todos los registros de la tabla 'asistencia'
cursor.execute("DELETE FROM asistencia")

# Guardar los cambios
conn.commit()

# Cerrar la conexión
conn.close()

print("Todos los registros de la tabla 'asistencia' han sido eliminados.")
