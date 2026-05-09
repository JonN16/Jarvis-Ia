import speech_recognition as sr
from config import LANGUAGE, SPEECH_RECOGNITION_TIMEOUT, AMBIENT_NOISE_DURATION

recognizer = sr.Recognizer()


def ouvir():
    """Listen to user input from microphone"""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=AMBIENT_NOISE_DURATION)
        print("\n[Ouvindo...]")

        try:
            audio = recognizer.listen(source, timeout=SPEECH_RECOGNITION_TIMEOUT)
        except sr.RequestError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception:
            return ""

    try:
        texto = recognizer.recognize_google(audio, language=LANGUAGE)
        print(f"Você: {texto}")
        return texto.lower()
    except sr.RequestError:
        return ""
    except sr.UnknownValueError:
        return ""
    except Exception:
        return ""
