# Configuration file for Jarvis AI Assistant
import os

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"
VOICE_RATE = 190
WAKE_WORD = "jarvis"

# Voice settings
VOICE_ENGINE = "sapi5"
LANGUAGE = "pt-BR"
SPEECH_RECOGNITION_TIMEOUT = 8
AMBIENT_NOISE_DURATION = 0.8

# Ollama settings
STREAM = False

# Caminhos base comuns
_LOCAL  = os.environ.get("LOCALAPPDATA", "")
_ROAMING = os.environ.get("APPDATA", "")
_PFILES  = os.environ.get("PROGRAMFILES", "C:\\Program Files")
_PFILES86 = os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")
_USER = os.path.expanduser("~")

# App mappings — usa caminhos completos para apps que não estão no PATH
APPS = {
    # Spotify (está no PATH normalmente)
    "spotify":          "spotify",

    # Discord
    "discord":          os.path.join(_ROAMING, "Discord", "Update.exe") + " --processStart Discord.exe",

    # Navegadores
    "chrome":           "chrome",
    "chromium":         "chrome",
    "navegador":        "chrome",
    "browser":          "chrome",
    "opera":            os.path.join(_ROAMING, "Opera Software", "Opera GX Stable", "launcher.exe"),
    "opera gx":         os.path.join(_ROAMING, "Opera Software", "Opera GX Stable", "launcher.exe"),
    "firefox":          "firefox",
    "edge":             "msedge",
    "microsoft edge":   "msedge",

    # Editores / IDEs
    "vscode":           "code",
    "code":             "code",
    "visual studio":    "code",
    "vs code":          "code",
    "vsc":              "code",
    "editor":           "code",

    # Ferramentas Windows
    "calculator":       "calc",
    "calc":             "calc",
    "calculadora":      "calc",
    "notepad":          "notepad",
    "notas":            "notepad",
    "texto":            "notepad",
    "txt":              "notepad",
    "paint":            "mspaint",
    "pintura":          "mspaint",
    "explorer":         "explorer",
    "windows explorer": "explorer",
    "files":            "explorer",
    "arquivos":         "explorer",
    "powershell":       "powershell",
    "terminal":         "wt",       # Windows Terminal (mais moderno que powershell)
    "cmd":              "cmd",
    "command prompt":   "cmd",

    # Entretenimento
    "vlc":              "vlc",
    "vídeo":            "vlc",
    "player":           "vlc",
    "obs":              "obs64",
    "streaming":        "obs64",

    # Mensagens
    "whatsapp":         os.path.join(_ROAMING, "WhatsApp", "WhatsApp.exe"),
    "telegram":         os.path.join(_ROAMING, "Telegram Desktop", "Telegram.exe"),
    "messenger":        "messenger",
    "instagram":        "instagram",
    "twitter":          "twitter",

    # Obsidian — caminho completo necessário (não está no PATH)
    "obsidian":         os.path.join(_LOCAL, "Obsidian", "Obsidian.exe"),

    # Games
    "league":           "lol",
    "league of legends": "lol",
    "lol":              "lol",
    "pbe":              "lol",
    "steam":            os.path.join(_PFILES86, "Steam", "steam.exe"),
}