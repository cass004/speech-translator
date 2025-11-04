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
root.title("🎤 Translator")
root.config(bg="#222831")

# --- Dynamically scale for small screens ---
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# For 3.5" display, keep compact size (90% width, 95% height)
win_width = int(screen_width * 0.85)
win_height = int(screen_height * 0.85)

x_pos = (screen_width // 2) - (win_width // 2)
y_pos = (screen_height // 2) - (win_height // 2)
root.geometry(f"{win_width}x{win_height}+{x_pos}+{y_pos}")

# Smaller font sizes for compact display
FONT_SMALL = ("Arial", 9)
FONT_MEDIUM = ("Arial", 10, "bold")

style = ttk.Style()
style.theme_use("clam")
style.configure("TCombobox", fieldbackground="#eeeeee", background="white", padding=2)

# ------------ Layout ------------
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# Frame top (language selection)
frame_top = tk.Frame(root, bg="#222831")
frame_top.grid(row=0, column=0, pady=3)

tk.Label(frame_top, text="Input:", font=FONT_SMALL, fg="white", bg="#222831").grid(row=0, column=0, padx=3)
input_lang_var = tk.StringVar(value="english")
ttk.Combobox(frame_top, textvariable=input_lang_var, values=list(lang_map.keys()), width=8).grid(row=0, column=1, padx=3)

tk.Label(frame_top, text="→", font=FONT_SMALL, fg="white", bg="#222831").grid(row=0, column=2, padx=3)

tk.Label(frame_top, text="Output:", font=FONT_SMALL, fg="white", bg="#222831").grid(row=0, column=3, padx=3)
output_lang_var = tk.StringVar(value="hindi")
ttk.Combobox(frame_top, textvariable=output_lang_var, values=list(lang_map.keys()), width=8).grid(row=0, column=4, padx=3)

# Text Display Frames
frame_text = tk.Frame(root, bg="#393e46")
frame_text.grid(row=1, column=0, padx=5, pady=3, sticky="nsew")

frame_text.grid_rowconfigure(1, weight=1)
frame_text.grid_rowconfigure(3, weight=1)
frame_text.grid_columnconfigure(0, weight=1)

tk.Label(frame_text, text="🎙️ Speech:", font=FONT_SMALL, fg="white", bg="#393e46").grid(row=0, column=0, sticky="w")
input_text_box = tk.Text(frame_text, height=3, wrap="word", font=FONT_SMALL, bg="#eeeeee", fg="black")
input_text_box.grid(row=1, column=0, sticky="nsew", pady=2)

tk.Label(frame_text, text="🌍 Translation:", font=FONT_SMALL, fg="white", bg="#393e46").grid(row=2, column=0, sticky="w")
output_text_box = tk.Text(frame_text, height=3, wrap="word", font=FONT_SMALL, bg="#eeeeee", fg="black")
output_text_box.grid(row=3, column=0, sticky="nsew", pady=2)

# Buttons Frame
frame_buttons = tk.Frame(root, bg="#222831")
frame_buttons.grid(row=2, column=0, pady=3)

btn_start = tk.Button(frame_buttons, text="🎤 Start", command=start_translation,
                      bg="#00adb5", fg="white", font=FONT_SMALL, width=10, relief="raised")
btn_start.grid(row=0, column=0, padx=5)

btn_replay = tk.Button(frame_buttons, text="🔁 Replay", command=replay_translation,
                       bg="#ff5722", fg="white", font=FONT_SMALL, width=10, relief="raised")
btn_replay.grid(row=0, column=1, padx=5)

# Status bar
status_var = tk.StringVar(value="Ready")
status_label = tk.Label(root, textvariable=status_var, bg="#00adb5", fg="white",
                        font=("Arial", 8), relief="sunken", anchor="w")
status_label.grid(row=3, column=0, sticky="ew")

root.mainloop()