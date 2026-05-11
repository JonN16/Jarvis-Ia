# Configuration file for Jarvis AI Assistant

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"
VOICE_RATE = 190
WAKE_WORD = "jarvis"

VOICE_ENGINE = "sapi5"
LANGUAGE = "pt-BR"
SPEECH_RECOGNITION_TIMEOUT = 8
AMBIENT_NOISE_DURATION = 0.8

STREAM = False

# Carrega mapeamento de apps automaticamente via scanner
# Na primeira vez escaneia o PC e salva cache; depois usa o cache
from app_scanner import get_apps
APPS = get_apps()