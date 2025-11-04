import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import os


# ------------ Core Functions ------------ #
def speech_to_text(lang_code="en-IN"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        status_var.set("🎙️ Speak now...")
        root.update()
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language=lang_code)
        status_var.set("✅ Speech recognized")
        return text
    except sr.UnknownValueError:
        status_var.set("❌ Could not understand audio")
        return None
    except sr.RequestError:
        status_var.set("❌ Error with API request")
        return None


def translate_text(text, target_lang):
    translated = GoogleTranslator(source="auto", target=target_lang).translate(text)
    return translated


def text_to_speech(text, lang_code):
    tts = gTTS(text=text, lang=lang_code)
    tts.save("output.mp3")

    if os.name == "nt":
        os.system("start output.mp3")
    elif hasattr(os, "uname") and os.uname().sysname == "Darwin":
        os.system("open output.mp3")
    else:
        os.system("xdg-open output.mp3")


def start_translation():
    global last_translation, last_output_code

    input_lang = input_lang_var.get().lower()
    output_lang = output_lang_var.get().lower()

    input_code = lang_map.get(input_lang, "en")
    output_code = lang_map.get(output_lang, "en")

    spoken_text = speech_to_text(lang_code=input_code)
    if not spoken_text:
        messagebox.showerror("Error", "Speech not recognized. Try again!")
        return

    input_text_box.delete(1.0, tk.END)
    input_text_box.insert(tk.END, spoken_text)

    translated_text = translate_text(spoken_text, target_lang=output_code)
    output_text_box.delete(1.0, tk.END)
    output_text_box.insert(tk.END, translated_text)

    last_translation = translated_text
    last_output_code = output_code

    text_to_speech(translated_text, output_code)
    status_var.set("✅ Translation complete & spoken aloud!")


def replay_translation():
    if last_translation:
        text_to_speech(last_translation, last_output_code)
        status_var.set("🔁 Replayed translation")
    else:
        messagebox.showinfo("Info", "No translation available yet!")


# ------------ Language Map ------------ #
lang_map = {
    "english": "en",
    "hindi": "hi",
    "tamil": "ta"
}

last_translation = None
last_output_code = None


# ------------ GUI Setup ------------ #
root = tk.Tk()
root.title("🎤 Speech Translator")
root.config(bg="#222831")

# --- Dynamically fit window to screen size ---
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Scale proportionally (e.g., 90% of screen)
win_width = int(screen_width * 0.9)
win_height = int(screen_height * 0.9)

# Center the window on the screen
x_pos = (screen_width // 2) - (win_width // 2)
y_pos = (screen_height // 2) - (win_height // 2)

root.geometry(f"{win_width}x{win_height}+{x_pos}+{y_pos}")
root.minsize(500, 400)
root.resizable(True, True)

style = ttk.Style()
style.theme_use("clam")

# Combobox Style
style.configure("TCombobox", fieldbackground="#eeeeee", background="white", padding=5)

# ------------ Layout ------------
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# Frame top
frame_top = tk.Frame(root, bg="#222831")
frame_top.grid(row=0, column=0, pady=10)

tk.Label(frame_top, text="Input Language:", font=("Arial", 12, "bold"), fg="white", bg="#222831").grid(row=0, column=0, padx=8)
input_lang_var = tk.StringVar(value="english")
ttk.Combobox(frame_top, textvariable=input_lang_var, values=list(lang_map.keys()), width=15).grid(row=0, column=1, padx=8)

tk.Label(frame_top, text="Output Language:", font=("Arial", 12, "bold"), fg="white", bg="#222831").grid(row=0, column=2, padx=8)
output_lang_var = tk.StringVar(value="hindi")
ttk.Combobox(frame_top, textvariable=output_lang_var, values=list(lang_map.keys()), width=15).grid(row=0, column=3, padx=8)

# Text Display Frames
frame_text = tk.Frame(root, bg="#393e46")
frame_text.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

frame_text.grid_rowconfigure(1, weight=1)
frame_text.grid_rowconfigure(3, weight=1)
frame_text.grid_columnconfigure(0, weight=1)

tk.Label(frame_text, text="🎙️ Recognized Speech:", font=("Arial", 11, "bold"), fg="white", bg="#393e46").grid(row=0, column=0, sticky="w", pady=(5, 0))
input_text_box = tk.Text(frame_text, height=5, wrap="word", font=("Arial", 11), bg="#eeeeee", fg="black")
input_text_box.grid(row=1, column=0, sticky="nsew", pady=5)

tk.Label(frame_text, text="🌍 Translated Output:", font=("Arial", 11, "bold"), fg="white", bg="#393e46").grid(row=2, column=0, sticky="w", pady=(10, 0))
output_text_box = tk.Text(frame_text, height=5, wrap="word", font=("Arial", 11), bg="#eeeeee", fg="black")
output_text_box.grid(row=3, column=0, sticky="nsew", pady=5)

# Buttons Frame
frame_buttons = tk.Frame(root, bg="#222831")
frame_buttons.grid(row=2, column=0, pady=10)

btn_start = tk.Button(frame_buttons, text="🎤 Start Translation", command=start_translation,
                      bg="#00adb5", fg="white", font=("Arial", 12, "bold"), width=20, relief="raised")
btn_start.grid(row=0, column=0, padx=15)

btn_replay = tk.Button(frame_buttons, text="🔁 Replay Translation", command=replay_translation,
                       bg="#ff5722", fg="white", font=("Arial", 12, "bold"), width=20, relief="raised")
btn_replay.grid(row=0, column=1, padx=15)

# Status bar
status_var = tk.StringVar(value="Ready")
status_label = tk.Label(root, textvariable=status_var, bg="#00adb5", fg="white", font=("Arial", 10),
                        relief="sunken", anchor="w")
status_label.grid(row=3, column=0, sticky="ew")

root.mainloop()