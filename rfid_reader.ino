#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define SS_PIN 10
#define RST_PIN 9
#define BUZZER_PIN 3

MFRC522 mfrc522(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("     Control   ");
  lcd.setCursor(0, 1);
  lcd.print("   Asistencias  ");
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  if (mfrc522.PICC_IsNewCardPresent()) {  
    if (mfrc522.PICC_ReadCardSerial()) {
      // Lee el UID de la tarjeta
      String rfidCode = "";
      for (byte i = 0; i < mfrc522.uid.size; i++) {
        rfidCode += String(mfrc522.uid.uidByte[i], HEX);
      }
      rfidCode.toUpperCase();
      Serial.println(rfidCode);

      String action = ""; // Acción (Entrada/Salida)
      String nombre = ""; // Nombre de la persona

      unsigned long tiempoEspera = millis();
      bool respuestaRecibida = false;

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("  Espera...  ");

      // Espera hasta recibir respuesta o hasta que pase el tiempo de espera
      while (millis() - tiempoEspera < 3000) {
        if (Serial.available()) {
          // Lee la acción (Entrada/Salida) y el nombre
          action = Serial.readStringUntil('\n'); // Lee la acción (Entrada/Salida)
          nombre = Serial.readStringUntil('\n'); // Lee el nombre
          respuestaRecibida = true;
          break;
        }
      }

      lcd.clear();
      if (respuestaRecibida && action.length() > 0 && nombre.length() > 0) {
        action = reemplazarAcentos(action);
        nombre = reemplazarAcentos(nombre);
        sonidoConfirmacion();
        lcd.setCursor(0, 1);
        lcd.print(nombre);
        desplazarTexto(action, 0, 0);
      } else {
        lcd.setCursor(0, 0);
        lcd.print("     Acceso     ");
        lcd.setCursor(0, 1);
        lcd.print("    Denegado    ");
        sonidoError();
      }
      delay(2000);  
      lcd.clear();
    }
  }
  lcd.setCursor(0, 0);
  lcd.print("     Control   ");
  lcd.setCursor(0, 1);
  lcd.print("   Asistencias  ");

  mfrc522.PICC_HaltA();
}

// Función para reemplazar acentos y caracteres especiales
String reemplazarAcentos(String texto) {
  texto.replace("á", "a");
  texto.replace("é", "e");
  texto.replace("í", "i");
  texto.replace("ó", "o");
  texto.replace("ú", "u");
  texto.replace("ñ", "n");
  texto.replace("Á", "A");
  texto.replace("É", "E");
  texto.replace("Í", "I");
  texto.replace("Ó", "O");
  texto.replace("Ú", "U");
  texto.replace("Ñ", "N");
  return texto;
}

// Función para desplazar el texto en la pantalla LCD
void desplazarTexto(String texto, int fila, int columna) {
  int textLength = texto.length();
  int screenWidth = 16;
  if (textLength > screenWidth) {
    // Desplazar el texto hacia la izquierda
    for (int i = 0; i < textLength - screenWidth + 1; i++) {
      lcd.setCursor(columna, fila);
      lcd.print(texto.substring(i)); // Mostrar el texto desplazado
      delay(300);
    }
  } else {
    lcd.setCursor(columna, fila);
    lcd.print(texto);
  }
}
void sonidoConfirmacion() {
  tone(BUZZER_PIN, 1500, 200);
  delay(250);                 
  tone(BUZZER_PIN, 1800, 200); 
}

void sonidoError() {
  for (int i = 0; i < 3; i++) {  
    tone(BUZZER_PIN, 1000, 150);
    delay(200);
  }
}
