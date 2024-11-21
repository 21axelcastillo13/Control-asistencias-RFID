#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <stdlib.h> // Para malloc y free

#define RST_PIN 9
#define SS_PIN 10
#define BUZZER_PIN 3

MFRC522 mfrc522(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x27, 16, 2); // Cambia la dirección si es necesario

byte LecturaUID[4];
byte Angel[4] = {0x35, 0x82, 0xE4, 0xC5};
byte Axel[4] = {0x1E, 0x4F, 0xD3, 0x18};
byte Francisco[4] = {0x83, 0x6A, 0x95, 0xEC};
byte Fabiana[4] = {0xF5, 0xCA, 0x65, 0x79};
byte Arnold[4] = {0xB3, 0x8D, 0x83, 0x0D};
byte Aleman[4] = {0xE3, 0x2F, 0x7D, 0xFA};

const unsigned long TIEMPO_ESPERA = 10000; // 10 segundos de espera
unsigned long tiempoEntrada[10]; // Aquí puedes tener 10 entradas max
int cantidadUsuariosDentro = 0;
const int cantidadMaxUsuarios = 100; // Número máximo de usuarios que puede manejar

char **usuariosDentro = nullptr; // Puntero a puntero de char para manejar los nombres de los usuarios

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  lcd.init();
  lcd.backlight();
  lcd.clear();

  mostrarMensajeInicio();
  pinMode(BUZZER_PIN, OUTPUT);

  // Asignación dinámica de memoria para los usuarios
  usuariosDentro = (char **)malloc(cantidadMaxUsuarios * sizeof(char *));
}

void loop() {
  if (!mfrc522.PICC_IsNewCardPresent()) {
  return;  // No hay tarjeta presente, sigue esperando
}

if (!mfrc522.PICC_ReadCardSerial()) {
  return;  // Si no se puede leer la tarjeta, vuelve a intentar
}

  // Si la tarjeta es leída, actualizar el tiempo de la última lectura
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    LecturaUID[i] = mfrc522.uid.uidByte[i];
  }

  char nombre[30];
  memset(nombre, 0, sizeof(nombre));  // Limpia el arreglo nombre

  // Compara UID con los usuarios registrados
  if (comparaUID(LecturaUID, Angel)) {
    strcpy(nombre, "Angel Carranza");
  } else if (comparaUID(LecturaUID, Axel)) {
    strcpy(nombre, "Axel Castillo");
  } else if (comparaUID(LecturaUID, Arnold)) {
    strcpy(nombre, "Arnold Mejia");
  } else if (comparaUID(LecturaUID, Francisco)) {
    strcpy(nombre, "Francisco Villanueva");
  } else if (comparaUID(LecturaUID, Fabiana)) {
    strcpy(nombre, "Fabiana Guzman");
  } else if (comparaUID(LecturaUID, Aleman)) {
    strcpy(nombre, "Angel Aleman");
  }

  // Si el nombre no está vacío
  if (nombre[0] != '\0') {
    sonidoConfirmacion();
    lcd.clear();
    if (estaDentro(nombre)) {
      if (puedeSalir(nombre)) {
        lcd.setCursor(0, 0);
        lcd.print("Salida:");
        lcd.setCursor(0, 1);
        lcd.print(nombre);
        quitarUsuario(nombre);
      } else {
        lcd.setCursor(0, 0);
        lcd.print("No puedes salir");
        lcd.setCursor(0, 1);
        lcd.print("  Favor espera");
      }
    } else {
      lcd.setCursor(0, 0);
      lcd.print("Entrada: ");
      lcd.setCursor(0, 1);
      lcd.print(nombre);
      agregarUsuario(nombre);
    }
  } else {
    sonidoError();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("     Acceso     ");
    lcd.setCursor(1, 1);
    lcd.print("   Denegado    ");
  }

  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
}

void mostrarMensajeInicio() {
  lcd.setCursor(0, 0);
  lcd.print("     Acceso     ");
  lcd.setCursor(0, 1);
  lcd.print("  UJCV   ");
}

boolean comparaUID(byte lectura[], byte usuario[]) {
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (lectura[i] != usuario[i])
      return false;
  }
  return true;
}

bool estaDentro(const char* nombre) {
  for (int i = 0; i < cantidadUsuariosDentro; i++) {
    if (strcmp(usuariosDentro[i], nombre) == 0) {
      return true;
    }
  }
  return false;
}

void agregarUsuario(const char* nombre) {
  if (cantidadUsuariosDentro < cantidadMaxUsuarios) {
    // Asignar memoria para el nombre
    usuariosDentro[cantidadUsuariosDentro] = (char *)malloc(strlen(nombre) + 1);
    strcpy(usuariosDentro[cantidadUsuariosDentro], nombre);
    cantidadUsuariosDentro++;
  }
}

bool puedeSalir(const char* nombre) {
  for (int i = 0; i < cantidadUsuariosDentro; i++) {
    if (strcmp(usuariosDentro[i], nombre) == 0) {
      unsigned long tiempoActual = millis();
      return (tiempoActual - tiempoEntrada[i]) >= TIEMPO_ESPERA;
    }
  }
  return false;
}

void quitarUsuario(const char* nombre) {
  for (int i = 0; i < cantidadUsuariosDentro; i++) {
    if (strcmp(usuariosDentro[i], nombre) == 0) {
      free(usuariosDentro[i]);  // Liberar la memoria de la cadena
      for (int j = i; j < cantidadUsuariosDentro - 1; j++) {
        usuariosDentro[j] = usuariosDentro[j + 1];
      }
      cantidadUsuariosDentro--;
      break;
    }
  }
}

void sonidoConfirmacion() {
  tone(BUZZER_PIN, 1500, 200);
}

void sonidoError() {
  tone(BUZZER_PIN, 100, 500);
}
