import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import os


def speech_to_text(lang_code="en-IN"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Speak now...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language=lang_code)
        print(f"✅ You said: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return None
    except sr.RequestError:
        print("❌ Error with API request")
        return None


def translate_text(text, target_lang):
    translated = GoogleTranslator(source="auto", target=target_lang).translate(text)
    print(f"🌍 Translated: {translated}")
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


# Mapping languages with their gTTS codes
lang_map = {
    "english": "en",
    "hindi": "hi",
    "tamil": "ta",
    "bengali": "bn"
}

print("Available languages: english, hindi, tamil, bengali")

input_lang = input("🎤 Input language: ").strip().lower()
input_code = lang_map.get(input_lang, "en")

output_lang = input("🌍 Output language: ").strip().lower()
output_code = lang_map.get(output_lang, "en")

print("Say 'stop' when you want to end.")

while True:
    spoken_text = speech_to_text(lang_code=input_code)

    if spoken_text:
        if spoken_text.lower() in ["stop", "exit", "quit"]:
            print("🛑 Exiting.")
            break

        translated_text = translate_text(spoken_text, target_lang=output_code)
        text_to_speech(translated_text, output_code)
    else:
        print("Please speak again.")
