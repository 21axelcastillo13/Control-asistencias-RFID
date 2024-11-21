#Proyecto Control de acceso con Arduino y Flask

Este proyecto utiliza un módulo RFID MFRC522 para leer identificaciones de tarjetas y un servidor Flask para gestionar los registros de acceso y generar informes en PDF.

#Requisitos de Hardware
- **Arduino Uno** (o compatible)
- **Módulo RFID MFRC522**
- **Pantalla LCD 16x2 I2C**
- **Protoboard** (Opcional)
- **Cables de conexión**
- **Tarjetas RFID** (con los UIDs especificados en el código)

### Conexiones del Módulo RFID
- Conectar el módulo MFRC522 al Arduino de la siguiente manera:
  - SDA (pin10)
  - SCK (pin 13)
  - MOSI (pin 11)
  - MISO (pin 12)
  - IRQ (no se conecta)
  - GND (pin GND)
  - RST (pin 9)
  - 3.3V (pin 3.3V)

## Conexiones de la pantalla LCD
- Conectar la pantalla LCD 16x2 I2C de la siguiente manera:
 - GND (GND)
 - VCC (5V)
 - SDA (pin A4)
 - SCL (pin A5)
 
## Requisitos de Software

### Para el Proyecto de Python (Flask)

Este proyecto utiliza las siguientes librerías de Python:

- **Flask**: Framework para desarrollo web.
- **PySerial**: Comunicación con el puerto de Arduino.
- **FPDF**: Para generar los PDF.
- **PyPDF2**: Para manipulación de archivos PDF existentes.
- **datetime**: Para manejo de fechas y horas.
- **sqlite3**: Para gestionar bases de datos SQLite.
- **os**: Para interactuar con el sistema operativo.

#### Instalación de Dependencias

Puedes instalar las dependencias de Python utilizando pip:

```bash
pip install Flask
pip install pyserial
pip install fpdf
pip install PyPDF2