#IMPORTS

import socket
import threading
import sys
import os
from datetime import datetime, time

#KONFIGURATION

HOST = "0.0.0.0"   # auf allen Netzwerk-Interfaces lauschen
PORT = 5050        # Port >1024 wg. Admin-Rechten

#Zutrittsliste (Personalnummern)

userID = ['F39A370E', '20047935', '00220394', '72349395']

#Sperrzeitfenster (Standardwerte: kein Sperrzeitfenster aktiv)
lock_start = None  # Beginn des Sperr-Zeitfensters
lock_end = None    # Ende des Sperr-Zeitfensters

# Aktive Client-Verbindungen für update_local_list
connected_clients = []

# Server-Socket Referenz für sauberes Beenden
server_socket_ref = None
shutdown_flag = False

#Sperrzeitfenster prüfen - gibt True zurück wenn GESPERRT

def is_locked():
    """Prüft ob aktuell ein Sperrzeitfenster aktiv ist"""
    if lock_start is None or lock_end is None:
        return False
    
    jetzt = datetime.now().time()
    
    # Fall 1: Sperrzeitfenster liegt am selben Tag (z. B. 08:00–17:00)
    if lock_start <= lock_end:
        return lock_start <= jetzt <= lock_end
    # Fall 2: Sperrzeitfenster geht über Mitternacht (z. B. 22:00–05:00)
    else:
        return jetzt >= lock_start or jetzt <= lock_end

def log_access_attempt(personalnummer, result, reason=""):
    """Gibt alle Zutrittsversuche im Terminal aus"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if reason:
        print(f"[{timestamp}] Personalnummer: {personalnummer} -> {result} ({reason})")
    else:
        print(f"[{timestamp}] Personalnummer: {personalnummer} -> {result}")

def handle_client(conn, addr):
    """Behandelt eine Client-Verbindung"""
    global shutdown_flag
    print(f"[INFO] Verbunden mit {addr}")
    connected_clients.append(conn)
    
    try:
        while not shutdown_flag:
            conn.settimeout(1.0)  # Timeout für regelmäßige Shutdown-Prüfung
            try:
                data = conn.recv(1024)
            except socket.timeout:
                continue
            
            if not data:
                print(f"[INFO] Client {addr} beendet Verbindung")
                break

            personalnummer = data.decode('utf-8').strip()
            
            # Prüflogik gemäß Lastenheft
            if is_locked():
                # Sperrzeitfenster aktiv - niemand hat Zutritt
                response = "DENY"
                log_access_attempt(personalnummer, "DENY", "Sperrzeitfenster aktiv")
            elif personalnummer in userID:
                # Personalnummer in Zutrittsliste gefunden
                response = "ALLOW"
                log_access_attempt(personalnummer, "ALLOW")
            else:
                # Personalnummer nicht in Zutrittsliste
                response = "DENY"
                log_access_attempt(personalnummer, "DENY", "Personalnummer nicht berechtigt")
            
            conn.sendall(response.encode('utf-8'))
    except ConnectionResetError:
        print(f"[INFO] Verbindung zu {addr} wurde zurückgesetzt")
    except Exception as e:
        if not shutdown_flag:
            print(f"[ERROR] Fehler bei Client {addr}: {e}")
    finally:
        if conn in connected_clients:
            connected_clients.remove(conn)
        try:
            conn.close()
        except:
            pass

def send_update_local_list():
    """Sendet die aktuelle Zutrittsliste an alle verbundenen ESP32s"""
    if not connected_clients:
        print("[INFO] Keine Clients verbunden")
        return
    
    # Format: UPDATE_LIST:id1,id2,id3,...
    list_data = "UPDATE_LIST:" + ",".join(userID)
    
    for client in connected_clients[:]:  # Kopie der Liste iterieren
        try:
            client.sendall(list_data.encode('utf-8'))
            print(f"[INFO] Lokale Liste an Client gesendet")
        except Exception as e:
            print(f"[ERROR] Fehler beim Senden: {e}")
            if client in connected_clients:
                connected_clients.remove(client)

def set_lock_start_time(hour, minute):
    """Setzt den Beginn des Sperr-Zeitfensters"""
    global lock_start
    try:
        lock_start = time(hour, minute)
        print(f"[INFO] Sperrzeitfenster-Beginn gesetzt auf {hour:02d}:{minute:02d} Uhr")
    except ValueError as e:
        print(f"[ERROR] Ungültige Zeit: {e}")

def set_lock_end_time(hour, minute):
    """Setzt das Ende des Sperr-Zeitfensters"""
    global lock_end
    try:
        lock_end = time(hour, minute)
        print(f"[INFO] Sperrzeitfenster-Ende gesetzt auf {hour:02d}:{minute:02d} Uhr")
    except ValueError as e:
        print(f"[ERROR] Ungültige Zeit: {e}")

def show_status():
    """Zeigt aktuellen Serverstatus an"""
    print("\n=== Server Status ===")
    print(f"Zutrittsliste: {userID}")
    if lock_start and lock_end:
        print(f"Sperrzeitfenster: {lock_start.strftime('%H:%M')} - {lock_end.strftime('%H:%M')}")
        print(f"Aktuell gesperrt: {'JA' if is_locked() else 'NEIN'}")
    else:
        print("Sperrzeitfenster: Nicht konfiguriert")
    print(f"Verbundene Clients: {len(connected_clients)}")
    print("=====================\n")

def show_help():
    """Zeigt verfügbare Befehle an"""
    print("\n=== Verfügbare Befehle ===")
    print("update_local_list          - Synchronisiert die lokale Liste auf dem ESP32 EEPROM")
    print("set_lock_start(x, y)       - Setzt Beginn des Sperr-Zeitfensters (z.B. set_lock_start(8, 45))")
    print("set_lock_end(x, y)         - Setzt Ende des Sperr-Zeitfensters (z.B. set_lock_end(17, 15))")
    print("status                     - Zeigt aktuellen Serverstatus")
    print("clear_lock                 - Entfernt das Sperrzeitfenster")
    print("help                       - Zeigt diese Hilfe")
    print("exit                       - Beendet den Server")
    print("==========================\n")

def shutdown_server():
    """Fährt den Server sauber herunter"""
    global shutdown_flag, server_socket_ref
    print("[INFO] Server wird beendet...")
    shutdown_flag = True
    
    # Alle Client-Verbindungen schließen
    for client in connected_clients[:]:
        try:
            client.close()
        except:
            pass
    connected_clients.clear()
    
    # Server-Socket schließen um accept() zu unterbrechen
    if server_socket_ref:
        try:
            server_socket_ref.close()
        except:
            pass
    
    print("[INFO] Server beendet.")
    os._exit(0)

def command_input_handler():
    """Thread für Befehlseingabe im Terminal"""
    while True:
        try:
            cmd = input().strip()
            
            if cmd == "update_local_list":
                send_update_local_list()
            
            elif cmd.startswith("set_lock_start(") and cmd.endswith(")"):
                # Parse set_lock_start(x, y)
                params = cmd[15:-1]  # Entferne "set_lock_start(" und ")"
                parts = params.split(",")
                if len(parts) == 2:
                    hour = int(parts[0].strip())
                    minute = int(parts[1].strip())
                    set_lock_start_time(hour, minute)
                else:
                    print("[ERROR] Ungültiges Format. Verwende: set_lock_start(x, y)")
            
            elif cmd.startswith("set_lock_end(") and cmd.endswith(")"):
                # Parse set_lock_end(x, y)
                params = cmd[13:-1]  # Entferne "set_lock_end(" und ")"
                parts = params.split(",")
                if len(parts) == 2:
                    hour = int(parts[0].strip())
                    minute = int(parts[1].strip())
                    set_lock_end_time(hour, minute)
                else:
                    print("[ERROR] Ungültiges Format. Verwende: set_lock_end(x, y)")
            
            elif cmd == "status":
                show_status()
            
            elif cmd == "clear_lock":
                global lock_start, lock_end
                lock_start = None
                lock_end = None
                print("[INFO] Sperrzeitfenster entfernt")
            
            elif cmd == "help":
                show_help()
            
            elif cmd == "exit":
                shutdown_server()
            
            elif cmd:
                print(f"[ERROR] Unbekannter Befehl: {cmd}")
                print("Gib 'help' ein für verfügbare Befehle.")
                
        except ValueError as e:
            print(f"[ERROR] Ungültige Parameter: {e}")
        except EOFError:
            break
        except Exception as e:
            print(f"[ERROR] Fehler: {e}")

# TCP-Server Hauptfunktion

def main():
    global server_socket_ref
    
    print("=" * 50)
    print("  RFID-Zutrittskontrolle Server")
    print("  Datenkommunikation Projekt - Welzel/Ettl")
    print("=" * 50)
    print("\nStarte TCP-Server...")

    # Starte Befehlseingabe-Thread
    cmd_thread = threading.Thread(target=command_input_handler, daemon=True)
    cmd_thread.start()

    # Server-Socket erstellen
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket_ref = server_socket  # Referenz für sauberes Beenden
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)  # Mehrere Clients möglich

        print(f"TCP-Server läuft auf {HOST}:{PORT}")
        print("Gib 'help' ein für verfügbare Befehle.\n")
        
        # Endlosschleife für Verbindungen
        while not shutdown_flag:
            try:
                server_socket.settimeout(1.0)  # Timeout für Shutdown-Check
                try:
                    conn, addr = server_socket.accept()
                except socket.timeout:
                    continue
                # Starte neuen Thread für jeden Client
                client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                client_thread.start()
            except OSError:
                if shutdown_flag:
                    break
            except KeyboardInterrupt:
                shutdown_server()
                break

if __name__ == "__main__":
    main()