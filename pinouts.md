# ESP32 Pinout Configuration

## Display (ST7735 TFT)

| Function | Pin (ESP32) |
| :--- | :--- |
| **SCL** | GPIO 12 |
| **SDA** | GPIO 11 |
| **RST** | GPIO 05 |
| **DC** | GPIO 04 |
| **CS** | GPIO 10 |

## RFID Reader (MFRC522)

| Function | Pin (ESP32) | Notes |
| :--- | :--- | :--- |
| **SDA** | GPIO 13 | (Chip Select / CS) |
| **SCK** | GPIO 14 | |
| **MOSI** | GPIO 15 | |
| **MISO** | GPIO 16 | |
| **RST** | GPIO 17 | |

## LEDs (Door Simulation)

| Function | Pin (ESP32) | Description |
| :--- | :--- | :--- |
| **Green** | GPIO 06 | Access Allowed |
| **Red** | GPIO 07 | Access Denied |
