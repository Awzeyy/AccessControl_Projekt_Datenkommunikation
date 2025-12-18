import machine
import network
import time

# Mit dem AP <ssid> verbinden
# Der Schlüssel <key> ist für gesicherte AP nötig 
# Wenn der AP gefunden wird, aber die Anmeldung trotz des richtigen Schlüssels nicht funktioniert,
# dann ist wahrscheinlich die Sendeleistung des ESP32 zu hoch
# Reduzieren txpower etwas (z.B. von 10 auf 5 oder von 5 auf 0) und versuchen Sie es erneut
# Der Grund dürfte eine Fehlanpassung der integrierten Antenne (auf dem ESP32) sein
def wlan_connect(ssid, key, skipscan=False, timeout=10000, txpower=5):
    wlan = network.WLAN()
    
    # WLAN-Modul abschalten, um eine Neukonfigutarion zu erzwingen
    wlan.active(False)
    
    # WLAN-Modul neu starten
    wlan.active(True)
    
    # Billige Boards haben eventuell schlecht angepasste Antennen
    # Das Herabsetzen der Sendeleistung hilft dann,
    # zu hohe Reflexionen zu vermieden
    wlan.config(txpower=txpower)
    
    # Alle APs finden, die eine SSID ausstrahlen
    if not skipscan:
        time.sleep(1)  # Warte kurz vor dem Scan
        networks = wlan.scan()
        ssidlist = [x[0].decode("utf-8") for x in networks]
        print("Gefundene Netzwerke:", ssidlist)
        if ssid not in ssidlist:
            # Zweiter Versuch
            time.sleep(2)
            networks = wlan.scan()
            ssidlist = [x[0].decode("utf-8") for x in networks]
            print("Zweiter Scan:", ssidlist)
            if ssid not in ssidlist:
                raise ValueError(f'Kein AP mit der SSID {ssid} gefunden. Verfügbar: {ssidlist}')
    
    # Mit dem AP verbinden, dabei einen Timeout beachten
    t = 0
    if not wlan.isconnected():
        wlan.connect(ssid, key) 
        while not wlan.isconnected():
            time.sleep(0.2)
            t = t + 200
            if (t > timeout):
                raise ValueError('AP gefunden, aber die '+
                'Verbindung konnte nicht hergestellt werden.')

    return wlan

