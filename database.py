import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('usuarios.db')
cursor = conn.cursor()



# Crear la tabla 'docentes'
cursor.execute('''
CREATE TABLE IF NOT EXISTS docente (
    id_docente INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    rfid_code TEXT NOT NULL UNIQUE,
    imageurl TEXT NOT NULL
);
''')

# Crear la tabla 'aulas'
cursor.execute('''
CREATE TABLE IF NOT EXISTS aula (
    id_aula INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
);
''')
# Crear la tabla 'dias'
cursor.execute('''
CREATE TABLE IF NOT EXISTS dia (
    id_dia INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
);
''')
# Crear la tabla 'clases'
cursor.execute('''
CREATE TABLE IF NOT EXISTS clase (
    id_clase INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    id_aula INTEGER,
    FOREIGN KEY (id_aula) REFERENCES aula(id_aula)
);
''')
# Crear la tabla 'clase_dia' (relación muchos a muchos entre clases y días)
cursor.execute('''
CREATE TABLE IF NOT EXISTS clase_dia (
    id_clase INTEGER,
    id_dia INTEGER,
    hora_inicio DATETIME NOT NULL,
    hora_fin DATETIME NOT NULL,
    PRIMARY KEY (id_clase, id_dia),
    FOREIGN KEY (id_clase) REFERENCES clase(id_clase),
    FOREIGN KEY (id_dia) REFERENCES dia(id_dia)
);
''')


# Crear la tabla 'docentes_clases' (relación muchos a muchos entre docentes y clases)
cursor.execute('''
CREATE TABLE IF NOT EXISTS docente_clase (
    id_docente INTEGER,
    id_clase INTEGER,
    PRIMARY KEY (id_docente,id_clase),
    FOREIGN KEY (id_docente) REFERENCES docente(id_docente),
    FOREIGN KEY (id_clase) REFERENCES clase(id_clase)
);
''')

# Crear la tabla 'asistencias'
cursor.execute('''
CREATE TABLE IF NOT EXISTS asistencia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_docente int,
    id_clase int,
    entrada DATETIME,
    salida DATETIME,
    FOREIGN KEY (id_clase) REFERENCES clase(id_clase),
    FOREIGN KEY (id_docente) REFERENCES docente(id_docente)
);
''')





#insercion de datos
# Insertar datos en la tabla 'aula'
cursor.execute("INSERT INTO aula (nombre) VALUES (?)", ('Laboratorio 1',))
cursor.execute("INSERT INTO aula (nombre) VALUES (?)", ('Laboratorio 2',))
cursor.execute("INSERT INTO aula (nombre) VALUES (?)", ('Laboratorio 3',))
cursor.execute("INSERT INTO aula (nombre) VALUES (?)", ('Laboratorio 4',))
cursor.execute("INSERT INTO aula (nombre) VALUES (?)", ('C1',))
cursor.execute("INSERT INTO aula (nombre) VALUES (?)", ('C2',))

# Insertar datos en la tabla 'dia'
cursor.execute("INSERT INTO dia (nombre) VALUES (?)", ('Lunes',))
cursor.execute("INSERT INTO dia (nombre) VALUES (?)", ('Martes',))
cursor.execute("INSERT INTO dia (nombre) VALUES (?)", ('Miércoles',))
cursor.execute("INSERT INTO dia (nombre) VALUES (?)", ('Jueves',))
cursor.execute("INSERT INTO dia (nombre) VALUES (?)", ('Viernes',))
cursor.execute("INSERT INTO dia (nombre) VALUES (?)", ('Sábado',))

# Insertar datos en la tabla 'clase'
cursor.execute("INSERT INTO clase (nombre, id_aula) VALUES (?, ?)", ('Programación I', 1))
cursor.execute("INSERT INTO clase (nombre, id_aula) VALUES (?, ?)", ('Sistemas Operativos', 2))
cursor.execute("INSERT INTO clase (nombre, id_aula) VALUES (?, ?)", ('Ingeniería de Software I', 3))
cursor.execute("INSERT INTO clase (nombre, id_aula) VALUES (?, ?)", ('Electrónica Digital', 4))
cursor.execute("INSERT INTO clase (nombre, id_aula) VALUES (?, ?)", ('Analisis y Diseño', 5))
cursor.execute("INSERT INTO clase (nombre, id_aula) VALUES (?, ?)", ('Seguridad de la Información', 6))


# Insertar datos en la tabla 'clase_dia'
cursor.execute("INSERT INTO clase_dia (id_clase, id_dia, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)", (1, 3, '12:00:00', '14:00:00'))  # Programación I Miércoles
cursor.execute("INSERT INTO clase_dia (id_clase, id_dia, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)", (1, 1, '12:00:00', '14:00:00'))  # Programación I Lunes
cursor.execute("INSERT INTO clase_dia (id_clase, id_dia, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)", (2, 2, '07:00:00', '10:00:00'))  # Sistemas Operativos Martes
cursor.execute("INSERT INTO clase_dia (id_clase, id_dia, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)", (2, 4, '07:00:00', '10:00:00'))  # Sistemas Operativos Jueves
cursor.execute("INSERT INTO clase_dia (id_clase, id_dia, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)", (3, 1, '17:00:00', '20:00:00'))  # Ingeniería de Software I Lunes
cursor.execute("INSERT INTO clase_dia (id_clase, id_dia, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)", (3, 3, '17:00:00', '20:00:00'))  # Ingeniería de Software I Miércoles
cursor.execute("INSERT INTO clase_dia (id_clase, id_dia, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)", (4, 6, '13:00:00', '15:00:00'))  # Electrónica Digital Viernes
cursor.execute("INSERT INTO clase_dia (id_clase, id_dia, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)", (4, 5, '13:00:00', '15:00:00'))  # Electrónica viernes
cursor.execute("INSERT INTO clase_dia (id_clase, id_dia, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)", (5, 5, '17:00:00', '20:00:00'))  # analisis viernes
cursor.execute("INSERT INTO clase_dia (id_clase, id_dia, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)", (6, 5, '10:00:00', '12:00:00'))  # Seguridad viernes

# Insertar datos de ejemplo
cursor.execute("INSERT INTO docente (id_docente,nombre, rfid_code,imageurl) VALUES (?,?, ?,?)", (2021210025,'Axel Castillo', '1E4FD318','/static/img/yo.jpg'))
cursor.execute("INSERT INTO docente (id_docente,nombre, rfid_code,imageurl) VALUES (?,?, ?,?)", (2020230026,'Angel Carranza', '3582E4C5','/static/img/angel.jpg'))
cursor.execute("INSERT INTO docente (id_docente,nombre, rfid_code,imageurl) VALUES (?,?, ?,?)", (2021210096,'Fabiana Guzman', '836A95EC','/static/img/fabiana.jpg'))
cursor.execute("INSERT INTO docente (id_docente,nombre, rfid_code,imageurl) VALUES (?,?, ?,?)", (2022210122,'Francisco Villanueva', 'F5CA6579','/static/img/user.jpg'))
cursor.execute("INSERT INTO docente (id_docente,nombre, rfid_code,imageurl) VALUES (?,?, ?,?)", (2021210076,'Arnold Mejia', 'B38D83D','/static/img/user.jpg'))
cursor.execute("INSERT INTO docente (id_docente,nombre, rfid_code,imageurl) VALUES (?,?, ?,?)", (2013210000,'Angel Aleman', 'E32F7DFA','/static/img/user.jpg'))

# Insertar datos en la tabla 'docente_clase'
cursor.execute("INSERT INTO docente_clase (id_docente, id_clase) VALUES (?, ?)", (2021210096, 1))  # Axel Castillo - Programación I
cursor.execute("INSERT INTO docente_clase (id_docente, id_clase) VALUES (?, ?)", (2021210096, 2))  # Fabiana Guzmán - Sistemas Operativos
cursor.execute("INSERT INTO docente_clase (id_docente, id_clase) VALUES (?, ?)", (2020230026, 3))  # Ángel Carranza - Ingeniería de Software I
cursor.execute("INSERT INTO docente_clase (id_docente, id_clase) VALUES (?, ?)", (2021210025, 4))  # Axel Castillo - Electrónica Digital
cursor.execute("INSERT INTO docente_clase (id_docente, id_clase) VALUES (?, ?)", (2021210025, 5))  # Axel Castillo - Analisis y diseno
cursor.execute("INSERT INTO docente_clase (id_docente, id_clase) VALUES (?, ?)", (2021210025, 6))  # Axel Castillo - Analisis y diseno


# Guardar cambios y cerrar
conn.commit()
conn.close()
print("Base de datos y tabla creadas con éxito.")