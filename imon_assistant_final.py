
import tkinter as tk
import json
import datetime
import os
import urllib.request
import shutil
import sys
import threading
from gtts import gTTS
import pygame
import winreg  # For auto startup (Windows only)

# Auto-Updater Settings
def check_for_update():
    local_version = "1.0"
    version_url = "https://raw.githubusercontent.com/webimon/Imon-Smart-Asistant/main/version.txt"
    file_url = "https://raw.githubusercontent.com/webimon/Imon-Smart-Asistant/main/imon_assistant_latest.py"
    local_filename = sys.argv[0]

    try:
        with urllib.request.urlopen(version_url) as response:
            latest_version = response.read().decode("utf-8").strip()

        if latest_version != local_version:
            with urllib.request.urlopen(file_url) as response, open("update_temp.py", 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

            os.replace("update_temp.py", local_filename)
            print("✅ আপডেট সম্পন্ন হয়েছে। অ্যাপ আবার চালু করুন।")
            exit()
    except Exception as e:
        print("❌ আপডেট চেক করতে সমস্যা হয়েছে:", e)

# Auto Startup (Windows)
def enable_auto_startup(app_name="ImonSmartAssistant", file_path=None):
    try:
        if not file_path:
            file_path = os.path.realpath(sys.argv[0])
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, file_path)
        winreg.CloseKey(key)
    except Exception as e:
        print("Auto-startup ব্যর্থ:", e)

# Voice
def speak_bengali(text):
    try:
        tts = gTTS(text=text, lang='bn')
        tts.save("temp_voice.mp3")
        pygame.mixer.init()
        pygame.mixer.music.load("temp_voice.mp3")
        pygame.mixer.music.play()
    except Exception as e:
        print("ভয়েস চালু হয়নি:", e)

# Routine
default_routine = [
    {
        "time": ["09:00", "10:00"],
        "task": "ডিফল্ট কাজ: জব খোঁজা",
        "note": "routine.json ফাইল না পেলে এই ডিফল্ট কাজ দেখাবে।"
    }
]

def load_routine(filename='routine.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default_routine

def get_current_task(routine):
    now = datetime.datetime.now().time()
    for item in routine:
        try:
            start = datetime.datetime.strptime(item["time"][0], "%H:%M").time()
            end = datetime.datetime.strptime(item["time"][1], "%H:%M").time()
            if start <= now < end:
                return item
        except:
            continue
    return {"task": "এখন কোনো কাজ নির্ধারিত নেই", "note": "বাকি সময় বিশ্রাম নিতে পারো।", "time": ["", ""]}

def update_task():
    global last_announced_task
    routine = load_routine()
    current = get_current_task(routine)
    task_text = current['task']
    note_text = current['note']

    task_label.config(text=f"🔹 {task_text}", fg="#003366")
    note_label.config(text=f"📝 {note_text}", fg="#333333")

    if task_text != last_announced_task:
        announcement = f"ইমন, তোমার এখন {task_text} করার সময় শুরু হয়েছে।"
        threading.Thread(target=speak_bengali, args=(announcement,), daemon=True).start()
        last_announced_task = task_text

    root.after(60000, update_task)

def update_transparency(val):
    alpha = float(val) / 100
    root.attributes('-alpha', alpha)

# Init
check_for_update()
enable_auto_startup()

last_announced_task = None

root = tk.Tk()
root.title("Imon's Smart Assistant")
root.configure(bg="#e0f7ff")
root.geometry("380x220+100+100")
root.resizable(False, False)
root.attributes('-topmost', True)

if os.path.exists("icon.ico"):
    root.iconbitmap("icon.ico")

root.attributes('-alpha', 0.88)

header = tk.Label(root, text="🔔 এখনকার কাজ:", font=("Helvetica", 14, "bold"), bg="#e0f7ff")
header.pack(pady=(10, 0))

task_label = tk.Label(root, text="", font=("Helvetica", 12), bg="#e0f7ff", wraplength=360, justify="center")
task_label.pack(pady=(5, 0))

note_label = tk.Label(root, text="", font=("Helvetica", 10), bg="#e0f7ff", wraplength=360, justify="center")
note_label.pack(pady=(5, 10))

slider_label = tk.Label(root, text="🔆 ট্রান্সপারেন্সি কন্ট্রোল:", font=("Helvetica", 10), bg="#e0f7ff")
slider_label.pack()
slider = tk.Scale(root, from_=50, to=100, orient='horizontal', command=update_transparency, bg="#e0f7ff")
slider.set(88)
slider.pack()

update_task()
root.mainloop()
