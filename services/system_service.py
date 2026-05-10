"""
System Service - Controle completo do sistema Windows
Volume, brilho, desligar, reiniciar, screenshot, processos, bateria, hora
"""

import os
import time
import psutil
import subprocess
import threading
from datetime import datetime
from pathlib import Path


# ------------------------------------------------------------------
# Volume do sistema (via pycaw)
# ------------------------------------------------------------------

def _get_volume_interface():
    """Obtém interface de controle de volume do Windows"""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))
    except Exception:
        return None


def obter_volume() -> tuple:
    """
    Retorna o volume atual do sistema (0-100).
    Returns: (int | None, str)
    """
    volume = _get_volume_interface()
    if volume:
        try:
            nivel = round(volume.GetMasterVolumeLevelScalar() * 100)
            return nivel, f"Volume atual: {nivel}%"
        except Exception as e:
            return None, f"Erro ao obter volume: {e}"

    # Fallback: lê via PowerShell
    try:
        resultado = subprocess.check_output(
            ["powershell", "-Command", "(Get-AudioDevice -Playback).Volume"],
            stderr=subprocess.DEVNULL, text=True
        ).strip()
        return int(float(resultado)), f"Volume atual: {resultado}%"
    except Exception:
        return None, "Não foi possível obter o volume"


def definir_volume(nivel: int) -> tuple:
    """
    Define o volume do sistema.
    Args:
        nivel: 0 a 100
    Returns: (bool, str)
    """
    nivel = max(0, min(100, nivel))

    volume = _get_volume_interface()
    if volume:
        try:
            volume.SetMasterVolumeLevelScalar(nivel / 100, None)
            return True, f"Volume definido para {nivel}%"
        except Exception as e:
            return False, f"Erro ao definir volume: {e}"

    # Fallback via PowerShell
    try:
        subprocess.run(
            ["powershell", "-Command", f"(New-Object -ComObject WScript.Shell).SendKeys([char]174)"],
            check=False, capture_output=True
        )
        # Método alternativo via nircmd se disponível
        subprocess.run(["nircmd", "setsysvolume", str(int(nivel * 655.35))],
                       check=True, capture_output=True)
        return True, f"Volume definido para {nivel}%"
    except Exception:
        return False, "Instale 'pycaw' para controle de volume: pip install pycaw"


def aumentar_volume(incremento: int = 10) -> tuple:
    """Aumenta o volume em X%"""
    atual, _ = obter_volume()
    if atual is None:
        atual = 50
    return definir_volume(atual + incremento)


def diminuir_volume(decremento: int = 10) -> tuple:
    """Diminui o volume em X%"""
    atual, _ = obter_volume()
    if atual is None:
        atual = 50
    return definir_volume(atual - decremento)


def mutar_volume() -> tuple:
    """Muta/desmuta o volume"""
    volume = _get_volume_interface()
    if volume:
        try:
            mutado = volume.GetMute()
            volume.SetMute(not mutado, None)
            estado = "mutado" if not mutado else "desmutado"
            return True, f"Volume {estado}"
        except Exception as e:
            return False, f"Erro ao mutar: {e}"

    try:
        import pyautogui
        pyautogui.press('volumemute')
        return True, "Volume mutado/desmutado"
    except Exception:
        return False, "Não foi possível mutar o volume"


# ------------------------------------------------------------------
# Brilho da tela (via screen_brightness_control)
# ------------------------------------------------------------------

def obter_brilho() -> tuple:
    """Retorna o brilho atual (0-100)"""
    try:
        import screen_brightness_control as sbc
        nivel = sbc.get_brightness(display=0)
        if isinstance(nivel, list):
            nivel = nivel[0]
        return nivel, f"Brilho atual: {nivel}%"
    except ImportError:
        return None, "Instale 'screen-brightness-control': pip install screen-brightness-control"
    except Exception as e:
        return None, f"Erro ao obter brilho: {e}"


def definir_brilho(nivel: int) -> tuple:
    """Define o brilho da tela (0-100)"""
    try:
        import screen_brightness_control as sbc
        nivel = max(0, min(100, nivel))
        sbc.set_brightness(nivel, display=0)
        return True, f"Brilho definido para {nivel}%"
    except ImportError:
        return False, "Instale 'screen-brightness-control': pip install screen-brightness-control"
    except Exception as e:
        return False, f"Erro ao definir brilho: {e}"


def aumentar_brilho(incremento: int = 10) -> tuple:
    atual, _ = obter_brilho()
    if atual is None:
        atual = 50
    return definir_brilho(atual + incremento)


def diminuir_brilho(decremento: int = 10) -> tuple:
    atual, _ = obter_brilho()
    if atual is None:
        atual = 50
    return definir_brilho(atual - decremento)


# ------------------------------------------------------------------
# Screenshot
# ------------------------------------------------------------------

_SCREENSHOT_DIR = Path.home() / "Pictures" / "Jarvis Screenshots"


def tirar_screenshot(nome: str = None) -> tuple:
    """
    Tira screenshot e salva em ~/Pictures/Jarvis Screenshots/
    Usa PIL direto (mais confiável que pyautogui.screenshot com Pillow 12+)
    Returns: (bool, str) com caminho ou erro
    """
    try:
        from PIL import ImageGrab
        _SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

        if not nome:
            nome = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        caminho = _SCREENSHOT_DIR / f"{nome}.png"
        img = ImageGrab.grab()  # captura a tela inteira via PIL nativo
        img.save(str(caminho))

        return True, f"Screenshot salvo: {caminho.name}"

    except ImportError:
        return False, "Instale 'pyautogui': pip install pyautogui"
    except Exception as e:
        return False, f"Erro ao tirar screenshot: {e}"


# ------------------------------------------------------------------
# Energia — desligar, reiniciar, suspender, hibernar
# ------------------------------------------------------------------

def _confirmar_e_executar(comando_powershell: str, delay: int = 5):
    """Executa comando de energia após delay (dá tempo de cancelar)"""
    def _executar():
        time.sleep(delay)
        subprocess.run(["powershell", "-Command", comando_powershell], check=False)

    t = threading.Thread(target=_executar, daemon=True)
    t.start()


def desligar_pc(delay: int = 5) -> tuple:
    """Desliga o computador após X segundos"""
    try:
        subprocess.run(f"shutdown /s /t {delay}", shell=True, check=True)
        return True, f"Computador será desligado em {delay} segundos. Diga 'cancelar desligamento' para abortar."
    except Exception as e:
        return False, f"Erro ao desligar: {e}"


def reiniciar_pc(delay: int = 5) -> tuple:
    """Reinicia o computador após X segundos"""
    try:
        subprocess.run(f"shutdown /r /t {delay}", shell=True, check=True)
        return True, f"Computador será reiniciado em {delay} segundos."
    except Exception as e:
        return False, f"Erro ao reiniciar: {e}"


def cancelar_desligamento() -> tuple:
    """Cancela um desligamento/reinício agendado"""
    try:
        subprocess.run("shutdown /a", shell=True, check=True)
        return True, "Desligamento cancelado."
    except Exception as e:
        return False, f"Nenhum desligamento agendado ou erro: {e}"


def suspender_pc() -> tuple:
    """Suspende o computador (sleep)"""
    try:
        subprocess.run(
            ["powershell", "-Command", "Add-Type -Assembly System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)"],
            check=False
        )
        return True, "Suspendendo o sistema."
    except Exception as e:
        return False, f"Erro ao suspender: {e}"


def bloquear_pc() -> tuple:
    """Bloqueia a tela do Windows"""
    try:
        subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
        return True, "Tela bloqueada."
    except Exception as e:
        return False, f"Erro ao bloquear: {e}"


# ------------------------------------------------------------------
# Informações do sistema
# ------------------------------------------------------------------

def obter_info_sistema() -> dict:
    """Retorna CPU, memória, disco e bateria"""
    info = {}
    try:
        info["cpu"] = psutil.cpu_percent(interval=1)
        info["memoria"] = psutil.virtual_memory().percent
        info["disco"] = psutil.disk_usage('/').percent

        bateria = psutil.sensors_battery()
        if bateria:
            info["bateria"] = round(bateria.percent)
            info["carregando"] = bateria.power_plugged
    except Exception as e:
        print(f"[System] Erro ao obter info: {e}")
    return info


def relatar_sistema() -> tuple:
    """Gera relatório falado do sistema"""
    info = obter_info_sistema()
    partes = []

    if "cpu" in info:
        partes.append(f"CPU em {info['cpu']}%")
    if "memoria" in info:
        partes.append(f"memória em {info['memoria']}%")
    if "disco" in info:
        partes.append(f"disco em {info['disco']}%")
    if "bateria" in info:
        estado = "carregando" if info.get("carregando") else "na bateria"
        partes.append(f"bateria em {info['bateria']}% ({estado})")

    if partes:
        return True, "Sistema: " + ", ".join(partes) + "."
    return False, "Não foi possível obter informações do sistema."


def obter_hora_data() -> tuple:
    """Retorna hora e data atual formatadas"""
    agora = datetime.now()
    hora = agora.strftime("%H:%M")
    data = agora.strftime("%d de %B de %Y")
    dia_semana = agora.strftime("%A")

    # Tradução simples do dia da semana
    dias = {
        "Monday": "segunda-feira", "Tuesday": "terça-feira",
        "Wednesday": "quarta-feira", "Thursday": "quinta-feira",
        "Friday": "sexta-feira", "Saturday": "sábado", "Sunday": "domingo"
    }
    meses = {
        "January": "janeiro", "February": "fevereiro", "March": "março",
        "April": "abril", "May": "maio", "June": "junho",
        "July": "julho", "August": "agosto", "September": "setembro",
        "October": "outubro", "November": "novembro", "December": "dezembro"
    }

    dia_semana_pt = dias.get(dia_semana, dia_semana)
    for en, pt in meses.items():
        data = data.replace(en, pt)

    resposta = f"São {hora} de {dia_semana_pt}, {data}."
    return True, resposta


# ------------------------------------------------------------------
# Processos
# ------------------------------------------------------------------

def obter_processos_em_uso() -> list:
    """Retorna lista de processos rodando"""
    try:
        return [p.info['name'] for p in psutil.process_iter(['name'])]
    except Exception:
        return []


def encerrar_processo(nome: str) -> tuple:
    """Encerra um processo pelo nome"""
    encerrados = 0
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == nome.lower():
                    proc.terminate()
                    encerrados += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        if encerrados:
            return True, f"{encerrados} processo(s) '{nome}' encerrado(s)."
        return False, f"Nenhum processo '{nome}' encontrado."
    except Exception as e:
        return False, f"Erro ao encerrar processo: {e}"


# ------------------------------------------------------------------
# Interface unificada para o brain.py
# ------------------------------------------------------------------

def controlar_sistema(acao: str, parametro=None) -> dict:
    """
    Interface única para o brain.py chamar qualquer função de sistema.

    Ações:
        volume_obter, volume_definir, volume_aumentar, volume_diminuir, volume_mutar
        brilho_obter, brilho_definir, brilho_aumentar, brilho_diminuir
        screenshot
        desligar, reiniciar, cancelar_desligamento, suspender, bloquear
        info_sistema, hora_data
        encerrar_processo
    """
    mapa = {
        "volume_obter":          lambda: obter_volume(),
        "volume_definir":        lambda: definir_volume(int(parametro)) if parametro else (False, "Informe o nível (0-100)"),
        "volume_aumentar":       lambda: aumentar_volume(int(parametro) if parametro else 10),
        "volume_diminuir":       lambda: diminuir_volume(int(parametro) if parametro else 10),
        "volume_mutar":          lambda: mutar_volume(),
        "brilho_obter":          lambda: obter_brilho(),
        "brilho_definir":        lambda: definir_brilho(int(parametro)) if parametro else (False, "Informe o nível (0-100)"),
        "brilho_aumentar":       lambda: aumentar_brilho(int(parametro) if parametro else 10),
        "brilho_diminuir":       lambda: diminuir_brilho(int(parametro) if parametro else 10),
        "screenshot":            lambda: tirar_screenshot(parametro),
        "desligar":              lambda: desligar_pc(int(parametro) if parametro else 5),
        "reiniciar":             lambda: reiniciar_pc(int(parametro) if parametro else 5),
        "cancelar_desligamento": lambda: cancelar_desligamento(),
        "suspender":             lambda: suspender_pc(),
        "bloquear":              lambda: bloquear_pc(),
        "info_sistema":          lambda: relatar_sistema(),
        "hora_data":             lambda: obter_hora_data(),
        "encerrar_processo":     lambda: encerrar_processo(parametro) if parametro else (False, "Informe o nome do processo"),
    }

    if acao not in mapa:
        return {"sucesso": False, "mensagem": f"Ação '{acao}' não reconhecida"}

    try:
        sucesso, mensagem = mapa[acao]()
        return {"sucesso": sucesso, "mensagem": mensagem}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro em '{acao}': {e}"}