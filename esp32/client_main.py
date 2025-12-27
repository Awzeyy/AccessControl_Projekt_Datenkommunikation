# Skript für den WLAN-Start
import time
import wlan_connect
import TCP_client as client
import tft_display as display
import rfid_reader
import eeprom_storage

# Benötigte Daten - Hotspot Konfiguration
ap_ssid = 'Alexxx'
ap_key = 'jooo12346'

# Server IP (PC auf dem Hotspot) und Port
server_ip = '172.20.10.2'
server_port = 5050

# Konfiguration
MAX_WLAN_RETRIES = 3
RECONNECT_INTERVAL = 60

def try_wifi_connect():
    """Versucht WLAN-Verbindung mit Retry-Logik"""
    for attempt in range(1, MAX_WLAN_RETRIES + 1):
        try:
            print(f"[WLAN] Versuch {attempt}/{MAX_WLAN_RETRIES}...")
            display.show_connection_status(attempt, MAX_WLAN_RETRIES)
            wlan = wlan_connect.wlan_connect(ap_ssid, ap_key)
            print("WLAN verbunden!")
            print("ESP32 IP:", wlan.ifconfig()[0])
            display.show_wlan_connected()
            return wlan
        except Exception as e:
            print(f"[WLAN] Fehler: {e}")
            if attempt < MAX_WLAN_RETRIES:
                display.show_wlan_error()
                time.sleep(1)
    return None

def check_local_access(personalnummer):
    """Prüft Zugang gegen lokale EEPROM-Liste"""
    local_list = eeprom_storage.load_local_list()
    if not local_list:
        print("[OFFLINE] Keine lokale Liste vorhanden - Zugang verweigert")
        return False
    return personalnummer in local_list

def run_offline_mode():
    """Betreibt das System komplett offline (ohne WiFi)"""
    print("\n" + "=" * 40)
    print("  RFID-Zutrittskontrolle (OFFLINE)")
    print("=" * 40)
    
    # RFID Reader mit Hardware-Reset initialisieren
    print("[RFID] Initialisiere Reader mit Hardware-Reset...")
    if not rfid_reader.reset_and_init():
        print("[RFID] WARNUNG: Reader konnte nicht initialisiert werden!")
    
    display.show_offline_mode()
    display.show_waiting(offline=True)
    
    last_reconnect = time.time()
    
    print(f"[INFO] Reconnect-Versuch alle {RECONNECT_INTERVAL} Sekunden")
    
    while True:
        # Periodisch WLAN-Reconnect versuchen (im Hintergrund)
        now = time.time()
        if now - last_reconnect >= RECONNECT_INTERVAL:
            last_reconnect = now
            print("\n[WLAN] Periodischer Reconnect-Versuch...")
            wlan = None
            try:
                # Schneller Versuch ohne Display-Update
                wlan = wlan_connect.wlan_connect(ap_ssid, ap_key)
            except Exception as e:
                print(f"[WLAN] Noch nicht verfügbar: {e}")
            
            if wlan:
                print("[WLAN] Verbunden! Wechsle zu Online-Modus...")
                display.show_wlan_connected()
                # RFID vollständig neu initialisieren nach WLAN-Aktivität
                rfid_reader.reset_and_init()
                # Starte TCP Client
                client.tcp_client(server_ip, server_port)
                return  # Falls TCP Client zurückkehrt, beenden
            else:
                # Zeige wieder Warten-Bildschirm
                display.show_waiting(offline=True)
                # RFID vollständig re-init nach WLAN-Scan
                rfid_reader.reset_and_init()
        
        # RFID-Karte lesen
        personalnummer = rfid_reader.read_uid()
        
        if personalnummer is None:
            time.sleep(0.2)
            continue
        
        print(f"\n[OFFLINE] RFID gelesen: {personalnummer}")
        
        # Zugang gegen lokale Liste prüfen
        if check_local_access(personalnummer):
            print(">>> ZUGANG ERLAUBT (Lokal) <<<")
            display.show_access_granted()
        else:
            print(">>> ZUGANG VERWEIGERT (Lokal) <<<")
            display.show_access_denied()
        
        display.show_waiting(offline=True)
        time.sleep(2)  # Pause um Mehrfachlesung zu vermeiden

def main():
    print("\n" + "=" * 40)
    print("  RFID-Zutrittskontrolle Startup")
    print("=" * 40)
    
    # Zeige WLAN-Verbindungsstatus auf Display
    display.show_wlan_connecting()
    
    # WLAN-Verbindung mit 3 Versuchen
    wlan = try_wifi_connect()
    
    if wlan:
        # WLAN verbunden -> Starte TCP Client (wird Server-Verbindung versuchen)
        print("[STATUS] WLAN verbunden - starte Online-Modus")
        client.tcp_client(server_ip, server_port)
    else:
        # Kein WLAN -> Komplett offline arbeiten (ohne Server-Versuche)
        print("[STATUS] Kein WLAN - starte Offline-Modus")
        display.show_wlan_error()
        time.sleep(2)
        run_offline_mode()

if __name__ == '__main__':
    main()
