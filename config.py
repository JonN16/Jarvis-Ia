# Configuration file for Jarvis AI Assistant

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"
VOICE_RATE = 190
WAKE_WORD = "jarvis"

# Voice settings
VOICE_ENGINE = "sapi5"
LANGUAGE = "pt-BR"
SPEECH_RECOGNITION_TIMEOUT = 8  # Aumentado para dar mais tempo
AMBIENT_NOISE_DURATION = 0.8    # Aumentado para melhor calibração

# Ollama settings
STREAM = False

# App mappings
APPS = {
    "spotify": "spotify",
    "discord": "discord",
    "chrome": "chrome",
    "chromium": "chrome",
    "navegador": "chrome",
    "browser": "chrome",
    "vscode": "code",
    "code": "code",
    "visual studio": "code",
    "vs code": "code",
    "vsc": "code",
    "editor": "code",
    "calculator": "calc",
    "calc": "calc",
    "calculadora": "calc",
    "notepad": "notepad",
    "notas": "notepad",
    "texto": "notepad",
    "txt": "notepad",
    "paint": "mspaint",
    "pintura": "mspaint",
    "explorer": "explorer",
    "windows explorer": "explorer",
    "files": "explorer",
    "arquivos": "explorer",
    "league": "lol",
    "league of legends": "lol",
    "lol": "lol",
    "pbe": "lol",
    "powershell": "powershell",
    "terminal": "powershell",
    "cmd": "cmd",
    "command prompt": "cmd",
    "vlc": "vlc",
    "vídeo": "vlc",
    "player": "vlc",
    "obs": "obs",
    "streaming": "obs",
    "whatsapp": "whatsapp",
    "messenger": "messenger",
    "telegram": "telegram",
    "instagram": "instagram",
    "twitter": "twitter",
    "firefox": "firefox",
    "edge": "edge",
    "microsoft edge": "edge"
}
