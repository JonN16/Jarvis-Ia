import pyttsx3
import threading
import time
from config import VOICE_RATE, VOICE_ENGINE

# Lock to prevent multiple engines from running simultaneously
speech_lock = threading.Lock()


def falar(texto):
    """Speak out text using text-to-speech"""
    print(f"Jarvis: {texto}")

    def _speak():
        try:
            with speech_lock:
                # Create a new engine instance per thread
                engine = pyttsx3.init(VOICE_ENGINE)
                try:
                    voices = engine.getProperty('voices')
                    engine.setProperty('voice', voices[0].id)
                    engine.setProperty('rate', VOICE_RATE)
                    engine.say(texto)
                    engine.runAndWait()
                finally:
                    # Clean up the engine
                    engine.stop()
        except RuntimeError:
            # Ignore "run loop already started" errors
            pass
        except Exception as e:
            # Log other errors silently
            pass

    t = threading.Thread(target=_speak, daemon=True)
    t.start()
