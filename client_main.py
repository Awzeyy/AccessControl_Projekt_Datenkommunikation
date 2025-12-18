# Skript für den WLAN-Start
import wlan_connect
# Modul mit dem TCP-Client
import TCP_client as client
import tft_display as display

# Benötigte Daten - Hotspot Konfiguration
ap_ssid = 'Alexxx'
ap_key = 'jooo12346'

# Server IP (PC auf dem Hotspot) und Port
server_ip = '172.20.10.2'
server_port = 5050

def main():
    # Zeige WLAN-Verbindungsstatus auf Display
    display.show_wlan_connecting()
    
    try:
        print("Verbinde mit WLAN Hotspot...")
        wlan = wlan_connect.wlan_connect(ap_ssid, ap_key)
        print("WLAN verbunden!")
        print("ESP32 IP:", wlan.ifconfig()[0])
        display.show_wlan_connected()
    except Exception as e:
        print('Fehler bei der Anmeldung am AP:', str(e))
        display.show_wlan_error()
        import machine
        machine.reset()
        return
    
    # TCP Client starten - zwei separate Argumente, nicht als Liste!
    client.tcp_client(server_ip, server_port)
    
if __name__ == '__main__':
    main()
