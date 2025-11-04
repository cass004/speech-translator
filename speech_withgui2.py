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
    elif os.uname().sysname == "Darwin":
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
root.geometry("650x500")
root.config(bg="#222831")

style = ttk.Style()
style.theme_use("clam")

# Combobox Style
style.configure("TCombobox", fieldbackground="#eeeeee", background="white", padding=5)

# Frame top
frame_top = tk.Frame(root, bg="#222831")
frame_top.pack(pady=15)

tk.Label(frame_top, text="Input Language:", font=("Arial", 12, "bold"), fg="white", bg="#222831").grid(row=0, column=0, padx=8)
input_lang_var = tk.StringVar(value="english")
ttk.Combobox(frame_top, textvariable=input_lang_var, values=list(lang_map.keys()), width=15).grid(row=0, column=1, padx=8)

tk.Label(frame_top, text="Output Language:", font=("Arial", 12, "bold"), fg="white", bg="#222831").grid(row=0, column=2, padx=8)
output_lang_var = tk.StringVar(value="hindi")
ttk.Combobox(frame_top, textvariable=output_lang_var, values=list(lang_map.keys()), width=15).grid(row=0, column=3, padx=8)

# Text Display Frames
frame_text = tk.Frame(root, bg="#393e46")
frame_text.pack(pady=15, padx=20, fill="both", expand=True)

tk.Label(frame_text, text="🎙️ Recognized Speech:", font=("Arial", 11, "bold"), fg="white", bg="#393e46").pack(anchor="w")
input_text_box = tk.Text(frame_text, height=5, width=70, wrap="word", font=("Arial", 11), bg="#eeeeee", fg="black")
input_text_box.pack(pady=5)

tk.Label(frame_text, text="🌍 Translated Output:", font=("Arial", 11, "bold"), fg="white", bg="#393e46").pack(anchor="w", pady=(10, 0))
output_text_box = tk.Text(frame_text, height=5, width=70, wrap="word", font=("Arial", 11), bg="#eeeeee", fg="black")
output_text_box.pack(pady=5)

# Buttons Frame
frame_buttons = tk.Frame(root, bg="#222831")
frame_buttons.pack(pady=10)

btn_start = tk.Button(frame_buttons, text="🎤 Start Translation", command=start_translation,
                      bg="#00adb5", fg="white", font=("Arial", 12, "bold"), width=20, relief="raised")
btn_start.grid(row=0, column=0, padx=15)

btn_replay = tk.Button(frame_buttons, text="🔁 Replay Translation", command=replay_translation,
                       bg="#ff5722", fg="white", font=("Arial", 12, "bold"), width=20, relief="raised")
btn_replay.grid(row=0, column=1, padx=15)

# Status bar
status_var = tk.StringVar(value="Ready")
status_label = tk.Label(root, textvariable=status_var, bg="#00adb5", fg="white", font=("Arial", 10), relief="sunken", anchor="w")
status_label.pack(fill="x", side="bottom")

root.mainloop()
