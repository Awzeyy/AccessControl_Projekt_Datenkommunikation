import socket
import time
import eeprom_storage
import tft_display as display
import rfid_reader

# Verbindungsstatus
MODE_ONLINE = "ONLINE"
MODE_OFFLINE = "OFFLINE"

# Konfiguration
MAX_CONNECT_RETRIES = 3        # Anzahl Verbindungsversuche beim Start
RECONNECT_INTERVAL = 60        # Sekunden zwischen Reconnect-Versuchen im Offline-Modus
RFID_POLL_INTERVAL = 0.2       # Sekunden zwischen RFID-Polls

def try_connect(host, port, silent=False):
    """Versucht eine Verbindung zum Server herzustellen"""
    try:
        addr_info = socket.getaddrinfo(host, port)[0][-1]
        s = socket.socket()
        s.settimeout(5.0)
        s.connect(addr_info)
        return s
    except Exception as e:
        if not silent:
            print(f"[VERBINDUNG] Server nicht erreichbar: {e}")
        return None

def initial_connect(host, port):
    """Versucht beim Start mehrfach eine Verbindung herzustellen"""
    for attempt in range(1, MAX_CONNECT_RETRIES + 1):
        print(f"[VERBINDUNG] Versuch {attempt}/{MAX_CONNECT_RETRIES}...")
        display.show_connection_status(attempt, MAX_CONNECT_RETRIES)
        sock = try_connect(host, port)
        if sock:
            return sock
        if attempt < MAX_CONNECT_RETRIES:
            print(f"[VERBINDUNG] Warte 2 Sekunden vor nächstem Versuch...")
            time.sleep(2)
    return None

def check_local_access(personalnummer):
    """Prüft Zugang gegen lokale EEPROM-Liste"""
    local_list = eeprom_storage.load_local_list()
    if not local_list:
        print("[OFFLINE] Keine lokale Liste vorhanden - Zugang verweigert")
        return False
    return personalnummer in local_list

def tcp_client(host, port):
    current_mode = MODE_OFFLINE
    sock = None
    last_reconnect_attempt = 0
    
    print("=" * 40)
    print("  RFID-Zutrittskontrolle Client")
    print("=" * 40)
    
    # RFID Reader initialisieren
    print("[RFID] Initialisiere Reader...")
    if not rfid_reader.init():
        print("[RFID] WARNUNG: Reader konnte nicht initialisiert werden!")
    
    # Display initialisieren
    display.show_connecting()
    
    # Initiale Verbindung versuchen (3 Versuche)
    print(f"\n[VERBINDUNG] Versuche Verbindung zu {host}:{port}...")
    sock = initial_connect(host, port)
    
    if sock:
        current_mode = MODE_ONLINE
        print(f"[STATUS] Modus: {current_mode} - Verbunden mit Server")
        display.show_reconnected()
        display.show_waiting(offline=False)
    else:
        current_mode = MODE_OFFLINE
        print(f"[STATUS] Modus: {current_mode} - Nutze lokale Liste aus EEPROM")
        print(f"[INFO] Reconnect-Versuch alle {RECONNECT_INTERVAL} Sekunden")
        display.show_offline_mode()
        display.show_waiting(offline=True)
        last_reconnect_attempt = time.time()
    
    while True:
        # Im Offline-Modus: Periodisch versuchen, Verbindung wiederherzustellen
        if current_mode == MODE_OFFLINE:
            current_time = time.time()
            if current_time - last_reconnect_attempt >= RECONNECT_INTERVAL:
                last_reconnect_attempt = current_time
                print(f"\n[VERBINDUNG] Periodischer Reconnect-Versuch...")
                sock = try_connect(host, port)
                if sock:
                    current_mode = MODE_ONLINE
                    print(f"[STATUS] Modus gewechselt: {current_mode} - Server wieder erreichbar!")
                    display.show_reconnected()
                    display.show_waiting(offline=False)
                else:
                    print(f"[VERBINDUNG] Server noch nicht verfügbar. Nächster Versuch in {RECONNECT_INTERVAL}s")
        
        # RFID-Karte lesen
        personalnummer = rfid_reader.read_uid()
        
        if personalnummer is None:
            # Keine Karte erkannt - kurz warten und erneut versuchen
            time.sleep(RFID_POLL_INTERVAL)
            continue
        
        print(f"\n[{current_mode}] RFID gelesen: {personalnummer}")
        
        if current_mode == MODE_ONLINE and sock:
            # Online-Modus: Server anfragen
            try:
                sock.send(personalnummer.encode("utf-8"))
                sock.settimeout(5.0)
                data = sock.recv(1024)
                
                if data:
                    response = data.decode("utf-8")
                    print(f"[ONLINE] Server Antwort: {response}")
                    
                    if response == "ALLOW":
                        print(">>> ZUGANG ERLAUBT (Server) <<<")
                        display.show_access_granted()
                        display.show_waiting(offline=False)
                    elif response == "DENY":
                        print(">>> ZUGANG VERWEIGERT (Server) <<<")
                        display.show_access_denied()
                        display.show_waiting(offline=False)
                    elif response.startswith("UPDATE_LIST:"):
                        # Lokale Liste vom Server empfangen und in EEPROM speichern
                        liste = response[12:].split(",")
                        print("[ONLINE] Neue lokale Liste empfangen:", liste)
                        eeprom_storage.save_local_list(liste)
                        display.show_list_updated()
                        display.show_waiting(offline=False)
                else:
                    # Keine Daten = Verbindung verloren
                    raise OSError("Verbindung verloren")
                    
            except OSError as e:
                print(f"[ONLINE] Verbindungsfehler: {e}")
                print(f"[STATUS] Wechsle zu OFFLINE-Modus...")
                print(f"[INFO] Reconnect-Versuch alle {RECONNECT_INTERVAL} Sekunden")
                current_mode = MODE_OFFLINE
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
                    sock = None
                last_reconnect_attempt = time.time()
                display.show_offline_mode()
                # Sofort lokal prüfen nach Verbindungsverlust
                if check_local_access(personalnummer):
                    print(">>> ZUGANG ERLAUBT (Lokal) <<<")
                    display.show_access_granted()
                else:
                    print(">>> ZUGANG VERWEIGERT (Lokal) <<<")
                    display.show_access_denied()
                display.show_waiting(offline=True)
        
        else:
            # Offline-Modus: Lokale Liste prüfen
            if check_local_access(personalnummer):
                print(">>> ZUGANG ERLAUBT (Lokal) <<<")
                display.show_access_granted()
                display.show_waiting(offline=True)
            else:
                print(">>> ZUGANG VERWEIGERT (Lokal) <<<")
                display.show_access_denied()
                display.show_waiting(offline=True)
        
        # Kurze Pause nach Kartenlesung um Mehrfachlesung zu vermeiden
        time.sleep(2)

# main
if __name__ == "__main__":
    tcp_client("172.20.10.2", 5050)