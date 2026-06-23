#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>

Adafruit_MPU6050 mpu;

float accX, accY, accZ;
float gyroX, gyroY, gyroZ;
sensors_event_t a, g, temp;

const unsigned long SAMPLE_INTERVAL = 10;   // ms -> 100 Hz
unsigned long lastSample = 0;

void setvalues(sensors_event_t a, sensors_event_t g, sensors_event_t temp) {
  accX = a.acceleration.x;
  accY = a.acceleration.y;
  accZ = a.acceleration.z;
  gyroX = g.gyro.x;
  gyroY = g.gyro.y;
  gyroZ = g.gyro.z;
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  pinMode(LED_BUILTIN, OUTPUT);
  Wire.setClock(100000);   // force standard 100kHz
  delay(100);              // let the bus settle before begin()


  Wire.setSDA(PB9);   // D14 — the fix
  Wire.setSCL(PB8);   // D15
  Wire.begin();

  
  Serial.println("Scanning...");
  bool found = false;
  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("  scan found 0x");
      Serial.println(addr, HEX);
      found = true;
    }
  }
  if (!found) Serial.println("  scan found NOTHING");

  // Then: try the library on the SAME bus
  Serial.println("Trying mpu.begin()...");
  if (mpu.begin()) {
    Serial.println("  mpu.begin() SUCCESS");
  } else {
    Serial.println("  mpu.begin() FAILED");
  }
}

void loop() {
  unsigned long now = millis();

  if (now - lastSample >= SAMPLE_INTERVAL) {
    lastSample += SAMPLE_INTERVAL;          // grid-locked, no drift

    mpu.getEvent(&a, &g, &temp);
    setvalues(a, g, temp);

    Serial.print(now);    Serial.print(", ");
    Serial.print(accX);   Serial.print(", ");
    Serial.print(accY);   Serial.print(", ");
    Serial.print(accZ);   Serial.print(", ");
    Serial.print(gyroX);  Serial.print(", ");
    Serial.print(gyroY);  Serial.print(", ");
    Serial.println(gyroZ);          // println ends the line
  }
}