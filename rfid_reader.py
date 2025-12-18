# RFID Reader Modul fuer ESP32 mit MFRC522
# Pins laut Pinouts.txt:
# SDA (CS) = Pin 13
# SCK      = Pin 14
# MOSI     = Pin 15
# MISO     = Pin 16
# RST      = Pin 17

import mfrc522

# RFID Pins fuer ESP32
RFID_SCK = 14
RFID_MOSI = 15
RFID_MISO = 16
RFID_RST = 17
RFID_CS = 13  # SDA

# RFID Reader Instanz
rdr = None

def init():
    """Initialisiert den RFID Reader"""
    global rdr
    try:
        rdr = mfrc522.MFRC522(RFID_SCK, RFID_MOSI, RFID_MISO, RFID_RST, RFID_CS)
        print("[RFID] Reader initialisiert")
        return True
    except Exception as e:
        print("[RFID] Fehler bei Initialisierung:", e)
        return False

def read_uid():
    """
    Liest eine RFID-Karte und gibt die UID als String zurueck.
    Gibt None zurueck wenn keine Karte erkannt wurde.
    """
    global rdr
    if rdr is None:
        if not init():
            return None
    
    try:
        # Karte anfordern
        (stat, tag_type) = rdr.request(rdr.REQIDL)
        
        if stat == rdr.OK:
            # Antikollision - UID lesen
            (stat, raw_uid) = rdr.anticoll()
            
            if stat == rdr.OK:
                # UID als Hex-String formatieren (8 Zeichen)
                uid = "%02X%02X%02X%02X" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                print("[RFID] Karte erkannt: " + uid)
                return uid
    except Exception as e:
        print("[RFID] Lesefehler:", e)
    
    return None

def read_uid_decimal():
    """
    Liest eine RFID-Karte und gibt die UID als Dezimalzahl-String zurueck.
    Format: 8 Zeichen mit fuehrenden Nullen (wie Personalnummer)
    """
    global rdr
    if rdr is None:
        if not init():
            return None
    
    try:
        (stat, tag_type) = rdr.request(rdr.REQIDL)
        
        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()
            
            if stat == rdr.OK:
                # UID als 32-bit Zahl, dann als 8-stellige Dezimalzahl
                uid_num = (raw_uid[0] << 24) | (raw_uid[1] << 16) | (raw_uid[2] << 8) | raw_uid[3]
                uid = str(uid_num).zfill(8)
                print("[RFID] Karte erkannt: " + uid)
                return uid
    except Exception as e:
        print("[RFID] Lesefehler:", e)
    
    return None

def wait_for_card(timeout_ms=5000):
    """
    Wartet auf eine RFID-Karte mit Timeout.
    Gibt die UID zurueck oder None bei Timeout.
    """
    import time
    start = time.ticks_ms()
    
    while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
        uid = read_uid()
        if uid:
            return uid
        time.sleep_ms(100)
    
    return None

# Test
if __name__ == "__main__":
    import time
    print("RFID Reader Test")
    print("Halte eine Karte vor den Reader...")
    
    init()
    
    while True:
        uid = read_uid()
        if uid:
            print("UID (hex): " + uid)
            uid_dec = read_uid_decimal()
            if uid_dec:
                print("UID (dezimal): " + uid_dec)
            time.sleep(2)
        time.sleep_ms(200)
