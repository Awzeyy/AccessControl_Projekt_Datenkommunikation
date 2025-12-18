# AccessControl Projekt – Datenkommunikation

## Übersicht
Dieses Projekt implementiert ein RFID-basiertes Zutrittskontrollsystem mit ESP32, MFRC522 RFID-Reader, ST7735 TFT-Display und zwei LEDs zur Türsimulation. Die Kommunikation zwischen Client (ESP32) und Server erfolgt über WLAN und TCP/IP.

## Hardware
- **ESP32**
- **RFID-Reader:** MFRC522
- **Display:** ST7735 TFT (128x160)
- **LEDs:** Grün (Allow, Pin 6), Rot (Deny, Pin 7)

### Pinbelegung
Siehe [Pinouts.txt](Pinouts.txt) für alle Verbindungen.

## Softwarestruktur
- **client_main.py:** Startet WLAN, verbindet zum Server, steuert den Client.
- **TCP_client.py:** TCP-Kommunikation, RFID-Lesen, LED/Display-Steuerung.
- **tft_display.py / display.py:** Display- und LED-Anzeige.
- **rfid_reader.py, mfrc522.py:** RFID-Reader-Ansteuerung.
- **eeprom_storage.py:** Lokale Speicherung der Zutrittsliste (EEPROM-Ersatz).
- **wlan_connect.py:** WLAN-Verbindung.
- **server_v2.py:** Python-Server für Zutrittsverwaltung und Synchronisation.
- **Lastenheft.pdf:** Projektanforderungen.

## Funktionen
- **RFID-Lesen:** UID wird gelesen und an den Server gesendet.
- **Zutrittskontrolle:** Server prüft UID, gibt Zugriff frei oder verweigert.
- **LEDs:** Grün = Zutritt gewährt, Rot = Zutritt verweigert.
- **Display:** Zeigt Status, Fehler und Hinweise an.
- **Offline-Modus:** Lokale Liste im EEPROM, falls Server nicht erreichbar.
- **Synchronisation:** Server kann Zutrittsliste an alle Clients verteilen.

## Installation & Nutzung
1. **Hardware wie in Pinouts.txt verdrahten.**
2. **ESP32 mit MicroPython flashen.**
3. **Alle Python-Dateien auf das Board kopieren.**
4. **Server (`server_v2.py`) auf PC starten:**
   ```
   python server_v2.py
   ```
5. **ESP32 starten.**
6. **RFID-Karte auflegen – Status wird auf Display und LEDs angezeigt.**

## Hinweise
- Die Zugangsliste und Sperrzeiten werden am Server verwaltet.
- Die wichtigsten Einstellungen (WLAN, Server-IP) sind in `client_main.py` konfigurierbar.
- Für Details siehe Lastenheft.pdf.

---
(c) Alexander Ettl, 2025
