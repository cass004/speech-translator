import os, json, pyaudio, pyttsx3, time  # Added 'time' for better control
from vosk import Model, KaldiRecognizer
import argostranslate.package, argostranslate.translate

# ---------------- SETUP ---------------- #
# Vosk Model (download & unzip into folder)
vosk_model_path = "vosk-model-small-en-us-0.15"
if not os.path.exists(vosk_model_path):
    raise FileNotFoundError(f"Download the Vosk model and unzip it as a folder named '{vosk_model_path}' here!")

# 1. Initialize Vosk Model
model = Model(vosk_model_path)
rec = KaldiRecognizer(model, 16000)

# 2. PyAudio for microphone initialization
mic = pyaudio.PyAudio()

# --- FIX 1: Explicitly set input device (Optional but highly recommended) ---
# To find your device index, run the PyAudio check script mentioned previously.
# If you leave it out, PyAudio uses the system's default input device (index 0).
INPUT_DEVICE_INDEX = None # Set to your device index (e.g., 2) if default doesn't work

stream = mic.open(rate=16000, channels=1, format=pyaudio.paInt16,
                  input=True, frames_per_buffer=8192,
                  input_device_index=INPUT_DEVICE_INDEX)
# Note: stream.start_stream() is automatically called by mic.open() when input=True

# 3. TTS Engine
engine = pyttsx3.init()

# Argos Translate setup (install language models once)
# Example: English ↔ Hindi
# argostranslate.package.install_from_path("translate-en_hi.argosmodel")
# ---------------- FUNCTIONS ---------------- #

def recognize_speech():
    """Listen from mic and return recognized text"""
    # FIX 2: Added logic to wait for silence (or an empty result) before restarting the loop
    # and a check for partial results to make the experience feel more responsive.
    print("🎙 Speak now (listening for 5 seconds of silence)...")
    rec.Reset() # Reset the recognizer state before a new utterance
    
    # Simple silence/inactivity detection
    silence_counter = 0
    SILENCE_THRESHOLD = 20 # Number of silent frames before assuming end of utterance

    while True:
        try:
            # Note: 4096 is the frame size, 8192 is buffer size. 
            # Reading 4096 frames at a time is common.
            data = stream.read(4096, exception_on_overflow=False) 
        except IOError as e:
            # Handle PyAudio buffer overflow gracefully
            if e.errno == pyaudio.paInputOverflowed:
                continue
            raise

        if len(data) == 0:
            # If no data is available (shouldn't happen in blocking mode), continue
            continue
            
        if rec.AcceptWaveform(data):
            # Final result detected (user paused/finished speaking)
            result = json.loads(rec.Result())
            text = result.get("text")
            if text and text.strip():
                return text
            # If the result is empty (e.g., noise that didn't form a word), continue listening
            
            # Reset silence counter after a recognized word, to handle continued speech
            silence_counter = 0

        else:
            # Check for partial results to give user feedback
            # partial = json.loads(rec.PartialResult()).get("partial")
            # if partial and partial.strip():
            #     print(f"Partial: {partial}", end='\r') # Optional: Show partial results

            # Simple logic to break loop after a pause (assuming rec.AcceptWaveform()
            # is checking for silence as part of its internal logic)
            if rec.Result(): # Vosk often returns an empty result object after prolonged silence
                result = json.loads(rec.Result())
                text = result.get("text")
                if text and text.strip():
                    return text
                else:
                    # Increment silence counter if no final or partial text was recognized
                    silence_counter += 1
                    if silence_counter > SILENCE_THRESHOLD:
                        print("\nListening paused due to silence. Waiting for new speech...")
                        # FIX 3: Return an empty string or a sentinel value 
                        # to indicate silence, or restart the loop entirely.
                        # We'll just break and let the main loop handle the empty result.
                        rec.Reset()
                        return ""
        
        # Adding a small sleep can sometimes help with system resource management
        time.sleep(0.01) 


def translate_text(text, from_lang, to_lang):
    """Translate text offline"""
    return argostranslate.translate.translate(text, from_lang, to_lang)

def speak_text(text):
    """Speak output"""
    if text: # Ensure we only try to speak non-empty text
        engine.say(text)
        engine.runAndWait()

# ---------------- MAIN ---------------- #
if __name__ == "__main__":
    from_lang = "en"   # source language
    to_lang = "hi"     # target language

    while True:
        spoken = recognize_speech()

        if spoken: # Only process if actual speech was returned
            print("\nYou said:", spoken)

            translated = translate_text(spoken, from_lang, to_lang)
            print("Translated:", translated)

            speak_text(translated)
            print("✅ Spoke translation\n")
        else:
            # Optional: Add a short pause before restarting the recognition loop after silence
            time.sleep(1)