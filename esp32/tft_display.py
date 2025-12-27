# Display-Modul fuer RFID-Zutrittskontrolle

from ST7735 import TFT
from sysfont import sysfont
from machine import SPI, Pin
import time

# LED Pins (Tuersimulation)
LED_GREEN = Pin(6, Pin.OUT)   # Gruen = Zutritt erlaubt
LED_RED = Pin(7, Pin.OUT)     # Rot = Zutritt verweigert

# LEDs initial aus
LED_GREEN.value(0)
LED_RED.value(0)

# SPI initialisieren
spi = SPI(
    2,
    baudrate=20000000,
    polarity=0,
    phase=0,
    sck=Pin(12),
    mosi=Pin(11),
)

# TFT initialisieren
tft = TFT(
    spi,
    Pin(4),
    Pin(5),
    Pin(10)
)

tft.initr()
tft.rgb(True)

# Display sofort loeschen und Startbildschirm zeigen
tft.fill(TFT.BLACK)
tft.text((0, 40), "Starte...", TFT.WHITE, sysfont, 2)

# Farben
COLOR_BG = TFT.BLACK
COLOR_TEXT = TFT.WHITE
COLOR_ALLOW = TFT.GREEN
COLOR_DENY = TFT.RED
COLOR_INFO = TFT.YELLOW
COLOR_OFFLINE = TFT.BLUE

def clear():
    tft.fill(COLOR_BG)

def show_waiting(sperrzeit_start=None, sperrzeit_end=None, offline=False):
    clear()
    
    if offline:
        tft.text((0, 0), "OFFLINE", COLOR_OFFLINE, sysfont, 1)
    else:
        tft.text((0, 0), "ONLINE", COLOR_ALLOW, sysfont, 1)
    
    tft.text((0, 30), "Bitte Karte", COLOR_TEXT, sysfont, 2)
    tft.text((0, 55), "auflegen", COLOR_TEXT, sysfont, 2)
    
    if sperrzeit_start and sperrzeit_end:
        tft.text((0, 90), "Sperrzeit:", COLOR_INFO, sysfont, 1)
        sperrzeit_text = str(sperrzeit_start) + " - " + str(sperrzeit_end)
        tft.text((0, 105), sperrzeit_text, COLOR_INFO, sysfont, 1)

def show_access_granted():
    clear()
    # LEDs: Gruen an, Rot aus
    LED_GREEN.value(1)
    LED_RED.value(0)
    tft.fillrect((0, 30), (128, 60), COLOR_ALLOW)
    tft.text((10, 45), "ZUTRITT", TFT.BLACK, sysfont, 2)
    tft.text((10, 70), "GEWAEHRT", TFT.BLACK, sysfont, 2)
    time.sleep(2)
    # LED wieder aus
    LED_GREEN.value(0)

def show_access_denied(reason=""):
    clear()
    # LEDs: Rot an, Gruen aus
    LED_RED.value(1)
    LED_GREEN.value(0)
    tft.fillrect((0, 30), (128, 60), COLOR_DENY)
    tft.text((5, 45), "ZUTRITT", TFT.WHITE, sysfont, 2)
    tft.text((5, 70), "VERWEIGERT", TFT.WHITE, sysfont, 2)
    if reason:
        tft.text((0, 110), reason[:20], COLOR_TEXT, sysfont, 1)
    time.sleep(2)
    # LED wieder aus
    LED_RED.value(0)

def show_connecting():
    clear()
    tft.text((0, 40), "Verbinde...", COLOR_INFO, sysfont, 2)

def show_connection_status(attempt, max_attempts):
    clear()
    tft.text((0, 30), "Verbinde mit", COLOR_TEXT, sysfont, 1)
    tft.text((0, 45), "Server...", COLOR_TEXT, sysfont, 1)
    tft.text((0, 70), "Versuch " + str(attempt) + "/" + str(max_attempts), COLOR_INFO, sysfont, 2)

def show_offline_mode():
    clear()
    tft.text((0, 30), "OFFLINE", COLOR_OFFLINE, sysfont, 2)
    tft.text((0, 60), "MODUS", COLOR_OFFLINE, sysfont, 2)
    tft.text((0, 90), "Nutze lokale", COLOR_TEXT, sysfont, 1)
    tft.text((0, 105), "Liste", COLOR_TEXT, sysfont, 1)
    time.sleep(2)

def show_reconnected():
    clear()
    tft.text((0, 40), "SERVER", COLOR_ALLOW, sysfont, 2)
    tft.text((0, 65), "VERBUNDEN", COLOR_ALLOW, sysfont, 2)
    time.sleep(1)

def show_list_updated():
    clear()
    tft.text((0, 40), "Liste", COLOR_INFO, sysfont, 2)
    tft.text((0, 65), "aktualisiert", COLOR_INFO, sysfont, 1)
    time.sleep(1)

def show_wlan_connecting():
    clear()
    tft.text((0, 30), "WLAN", COLOR_INFO, sysfont, 2)
    tft.text((0, 55), "Verbinde...", COLOR_TEXT, sysfont, 1)

def show_wlan_connected():
    clear()
    tft.text((0, 30), "WLAN", COLOR_ALLOW, sysfont, 2)
    tft.text((0, 55), "Verbunden!", COLOR_ALLOW, sysfont, 1)
    time.sleep(1)

def show_wlan_error():
    clear()
    tft.text((0, 30), "WLAN", COLOR_DENY, sysfont, 2)
    tft.text((0, 55), "FEHLER", COLOR_DENY, sysfont, 2)
    tft.text((0, 90), "Neustart...", COLOR_TEXT, sysfont, 1)
    time.sleep(3)

def test_display():
    show_connecting()
    time.sleep(1)
    show_connection_status(1, 3)
    time.sleep(1)
    show_waiting(offline=False)
    time.sleep(2)
    show_access_granted()
    show_waiting(sperrzeit_start="08:00", sperrzeit_end="17:00", offline=False)
    time.sleep(2)
    show_access_denied("Sperrzeit aktiv")
    show_offline_mode()
    show_waiting(offline=True)
    time.sleep(2)
    show_reconnected()
    show_waiting(offline=False)

if __name__ == "__main__":
    test_display()
