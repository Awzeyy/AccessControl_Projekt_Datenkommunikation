# main.py - Auto-start script
import time
import machine

print("Booting... Waiting 3 seconds (Press Ctrl+C to abort)...")
time.sleep(3)

try:
    import client_main
    print("Starting client_main...")
    client_main.main()
except Exception as e:
    print("Error starting client_main:", e)
    
