import subprocess
import shutil
from config import APPS


def abrir_app(nome):
    """Open application by name"""
    nome_lower = nome.lower().strip()

    # Try direct mapping first
    if nome_lower in APPS:
        try:
            subprocess.Popen(APPS[nome_lower], shell=True)
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
