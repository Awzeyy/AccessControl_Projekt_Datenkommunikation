# EEPROM-ähnlicher Speicher für ESP32 (nutzt Flash-Dateisystem)
# Speichert die lokale Zutrittsliste persistent

import json

EEPROM_FILE = "local_list.json"

def save_local_list(user_list):
    """Speichert die Zutrittsliste im Flash-Speicher (EEPROM-Ersatz)"""
    try:
        with open(EEPROM_FILE, "w") as f:
            json.dump(user_list, f)
        print("[EEPROM] Liste gespeichert:", user_list)
        return True
    except Exception as e:
        print("[EEPROM] Fehler beim Speichern:", e)
        return False

def load_local_list():
    """Lädt die Zutrittsliste aus dem Flash-Speicher"""
    try:
        with open(EEPROM_FILE, "r") as f:
            user_list = json.load(f)
        print("[EEPROM] Liste geladen:", user_list)
        return user_list
    except OSError:
        # Datei existiert noch nicht
        print("[EEPROM] Keine gespeicherte Liste gefunden")
        return []
    except Exception as e:
        print("[EEPROM] Fehler beim Laden:", e)
        return []

def check_local_access(personalnummer):
    """Prüft ob Personalnummer in lokaler Liste (für Offline-Betrieb)"""
    local_list = load_local_list()
    if personalnummer in local_list:
        return True
    return False

def clear_local_list():
    """Löscht die gespeicherte Liste"""
    try:
        import os
        os.remove(EEPROM_FILE)
        print("[EEPROM] Liste gelöscht")
        return True
    except:
        return False
