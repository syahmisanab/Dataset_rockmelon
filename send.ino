#define RE 7
#define DE 6

const uint32_t TIMEOUT = 500UL;

const byte moist[] = {0x3C, 0x61, 0x05, 0x11, 0xDD, 0xA4};
const byte temp[] = {0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xCA};
const byte EC[] = {0x01, 0x03, 0x00, 0x02, 0x00, 0x01, 0x25, 0xCA};
const byte PH[] = {0x01, 0x03, 0x00, 0x03, 0x00, 0x01, 0x74, 0x0A};

// Define commands for NPK sensor readings
const byte nitrogen[] = {0x01, 0x03, 0x00, 0x04, 0x00, 0x01, 0x94, 0x0A};
const byte phosphorus[] = {0x01, 0x03, 0x00, 0x05, 0x00, 0x01, 0xC5, 0xCA};
const byte potassium[] = {0x01, 0x03, 0x00, 0x06, 0x00, 0x01, 0x35, 0xCA};

byte values[11];

void setup() {
  Serial.begin(4800);
  Serial1.begin(4800);
  pinMode(RE, OUTPUT);
  pinMode(DE, OUTPUT);

  delay(500);
}

void loop() {
  uint16_t val1, val2, val3, val4, valN, valP, valK;

  Serial.println("Moisture: ");
  val1 = moisture();
  float Val1 = val1 * 0.1;
  delay(1000);
  Serial.print(Val1);
  Serial.println(" %");
  Serial.println("-----");

  Serial.println("Temperature: ");
  val2 = temperature();
  float Val2 = val2 * 0.1;
  delay(1000);
  Serial.print(Val2);
  Serial.println(" *C");
  Serial.println("-----");

  Serial.println("Conductivity: ");
  val3 = conductivity();
  delay(1000);
  Serial.print(val3);
  Serial.println(" us/cm");
  Serial.println("-----");

  Serial.println("Ph: ");
  val4 = ph();
  float Val4 = val4 * 0.1;
  delay(1000);
  Serial.print(Val4);
  Serial.println(" ph");
  Serial.println("-----");

  // Read NPK values
  Serial.println("Nitrogen: ");
  valN = nitrogenLevel();
  delay(1000);
  Serial.print(valN);
  Serial.println(" mg/kg");
  Serial.println("-----");

  Serial.println("Phosphorus: ");
  valP = phosphorusLevel();
  delay(1000);
  Serial.print(valP);
  Serial.println(" mg/kg");
  Serial.println("-----");

  Serial.println("Potassium: ");
  valK = potassiumLevel();
  delay(1000);
  Serial.print(valK);
  Serial.println(" mg/kg");
  Serial.println("-----");

  delay(5000);
}

int16_t readSensor(const byte* cmd, size_t cmdSize) {
  uint32_t startTime = 0;
  uint8_t byteCount = 0;

  Serial.println("Sending command...");
  for (size_t i = 0; i < cmdSize; i++) {
    printHexByte(cmd[i]);
  }
  Serial.println();

  // Enable RS485 Transmitter
  digitalWrite(DE, HIGH);
  digitalWrite(RE, HIGH);
  delay(50); // Adjust this delay if necessary

  // Send the command
  Serial1.write(cmd, cmdSize);
  Serial1.flush();

  // Disable RS485 Transmitter
  digitalWrite(DE, LOW);
  digitalWrite(RE, LOW);

  Serial.println("Waiting for response...");

  startTime = millis();
  while ( millis() - startTime <= TIMEOUT ) {
    if (Serial1.available() && byteCount < sizeof(values) ) {
      values[byteCount++] = Serial1.read();
    }
  }

  Serial.print("Raw Data: ");
  for (int i = 0; i < byteCount; i++) {
    printHexByte(values[i]);
  }
  Serial.println();

  if (byteCount < 7) {
    // Invalid response length
    Serial.println("Invalid response length");
    return 0;
  }

  // Check CRC
  uint16_t receivedCRC = (values[byteCount - 2] << 8) | values[byteCount - 1];
  if (calculateCRC(values, byteCount - 2) != receivedCRC) {
    // CRC check failed
    Serial.println("CRC check failed");
    return 0;
  }

  return (int16_t)(values[3] << 8 | values[4]);
}

int16_t moisture() {
  return readSensor(moist, sizeof(moist));
}

int16_t temperature() {
  return readSensor(temp, sizeof(temp));
}

int16_t conductivity() {
  return readSensor(EC, sizeof(EC));
}

int16_t ph() {
  return readSensor(PH, sizeof(PH));
}

int16_t nitrogenLevel() {
  return readSensor(nitrogen, sizeof(nitrogen));
}

int16_t phosphorusLevel() {
  return readSensor(phosphorus, sizeof(phosphorus));
}

int16_t potassiumLevel() {
  return readSensor(potassium, sizeof(potassium));
}

void printHexByte(byte b) {
  Serial.print((b >> 4) & 0xF, HEX);
  Serial.print(b & 0xF, HEX);
  Serial.print(' ');
}

uint16_t calculateCRC(byte* data, byte length) {
  uint16_t crc = 0xFFFF;
  for (byte pos = 0; pos < length; pos++) {
    crc ^= (uint16_t)data[pos];
    for (byte i = 8; i != 0; i--) {
      if ((crc & 0x0001) != 0) {
        crc >>= 1;
        crc ^= 0xA001;
      } else {
        crc >>= 1;
      }
    }
  }
  return crc;
}
