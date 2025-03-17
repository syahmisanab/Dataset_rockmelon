
#include <SoftwareSerial.h>

SoftwareSerial mySerial(2, 3);  // RX, TX

float tem, hum, ph;
int ec;

void setup() {
  Serial.begin(9600);
  mySerial.begin(4800);
}

void loop() {
  readHumitureECPH();
  Serial.print("TEM = ");
  Serial.print(tem, 1);
  Serial.print(" °C  ");
  Serial.print("HUM = ");
  Serial.print(hum, 1);
  Serial.print(" %RH  ");
  Serial.print("EC = ");
  Serial.print(ec);
  Serial.print(" us/cm ");
  Serial.print("PH = ");
  Serial.println(ph, 1);
  delay(1000);
}

void readHumitureECPH() {
  byte queryData[] = {0x01, 0x03, 0x00, 0x00, 0x00, 0x04, 0x44, 0x09};
  uint8_t Data[13] = { 0 };
  uint8_t ch = 0;
  bool flag = 1;

  while (flag) {
    delay(100);
    mySerial.write(queryData, sizeof(queryData));
    delay(10);

    if (readN(&ch, 1) == 1) {
      if (ch == 0x01) {
        Data[0] = ch;
        if (readN(&ch, 1) == 1) {
          if (ch == 0x03) {
            Data[1] = ch;
            if (readN(&ch, 1) == 1) {
              if (ch == 0x08) {
                Data[2] = ch;
                if (readN(&Data[3], 10) == 10) {
                  if (CRC16_2(Data, 11) == (Data[11] << 8 | Data[12])) {
                    hum = (Data[3] << 8 | Data[4]) / 10.0;
                    tem = (Data[5] << 8 | Data[6]) / 10.0;
                    ec = Data[7] << 8 | Data[8];
                    ph = (Data[9] << 8 | Data[10]) / 10.0;
                    flag = 0;
                  }
                }
              }
            }
          }
        }
      }
    }
    mySerial.flush();
  }
}

uint8_t readN(uint8_t *buf, size_t len) {
  size_t offset = 0, left = len;
  int16_t timeout = 500;
  uint8_t *buffer = buf;
  long curr = millis();
  while (left) {
    if (mySerial.available()) {
      buffer[offset] = mySerial.read();
      offset++;
      left--;
    }
    if (millis() - curr > timeout) {
      break;
    }
  }
  return offset;
}

unsigned int CRC16_2(unsigned char *buf, int len) {
  unsigned int crc = 0xFFFF;
  for (int pos = 0; pos < len; pos++) {
    crc ^= (unsigned int)buf[pos];
    for (int i = 8; i != 0; i--) {
      if ((crc & 0x0001) != 0) {
        crc >>= 1;
        crc ^= 0xA001;
      } else {
        crc >>= 1;
      }
    }
  }
  return (crc << 8) | (crc >> 8 & 0xFF); // Swap the bytes
}
