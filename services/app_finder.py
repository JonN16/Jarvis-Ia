import subprocess
import shutil
import psutil
from config import APPS

# Mapeamento de processos para verificar se app está aberto
PROCESS_NAMES = {
    "spotify": ["spotify.exe", "spotify"],
    "discord": ["discord.exe", "discord"],
    "chrome": ["chrome.exe", "chromium.exe", "chrome"],
    "vscode": ["code.exe", "code", "vscodium.exe"],
    "calculator": ["calculator.exe", "calc.exe"],
    "notepad": ["notepad.exe", "notepad"],
    "explorer": ["explorer.exe", "explorer"],
    "paint": ["mspaint.exe", "paint.exe"],
    "lol": ["leagueclient.exe", "league of legends.exe"],
    "vlc": ["vlc.exe", "vlc"],
    "firefox": ["firefox.exe", "firefox"],
    "edge": ["msedge.exe", "edge"],
}


def app_ja_aberto(nome):
    """Verifica se o aplicativo já está em execução"""
    nome_lower = nome.lower().strip()
    
    # Pega os nomes de processo possíveis
    processos_possiveis = PROCESS_NAMES.get(nome_lower, [f"{nome_lower}.exe", nome_lower])
    
    # Verifica processos em execução
    for proc in psutil.process_iter(['name']):
        try:
            proc_name = proc.info['name'].lower()
            if proc_name in processos_possiveis:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return False


def abrir_app(nome, forcar=False):
    """
    Open application by name
    
    Args:
        nome: Nome do aplicativo
        forcar: Se True, abre mesmo se já estiver rodando
    """
    nome_lower = nome.lower().strip()

    # Verifica se já está aberto (a menos que forcar=True)
    if not forcar and app_ja_aberto(nome_lower):
        return True  # Já está aberto, não faz nada

    # Try direct mapping first
    if nome_lower in APPS:
        try:
            subprocess.Popen(APPS[nome_lower], shell=True, 
                           creationflags=subprocess.CREATE_NO_WINDOW if nome_lower != "spotify" else 0)
            return True
        except Exception:
            pass

    # Try to find app in system PATH
    try:
        caminho = shutil.which(nome_lower)
        if caminho:
            subprocess.Popen(caminho, shell=True)
            return True
    except Exception:
        pass

    # Try with .exe suffix
    try:
        caminho = shutil.which(nome_lower + ".exe")
        if caminho:
            subprocess.Popen(caminho, shell=True)
            return True
    except Exception:
        pass

    # Try direct execution (works for Windows shortcuts)
    try:
        subprocess.Popen(nome_lower, shell=True)
        return True
    except Exception:
        pass

    return False
