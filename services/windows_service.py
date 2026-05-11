"""
Windows Service - Controle de janelas e área de trabalho
Minimizar, maximizar, fechar, trocar, listar, mover, redimensionar
"""

import subprocess
import psutil
import ctypes
import ctypes.wintypes
from typing import Optional

# Win32 API via ctypes
user32 = ctypes.windll.user32
EnumWindows = user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
GetWindowText = user32.GetWindowTextW
GetWindowTextLength = user32.GetWindowTextLengthW
IsWindowVisible = user32.IsWindowVisible
ShowWindow = user32.ShowWindow
SetForegroundWindow = user32.SetForegroundWindow
GetForegroundWindow = user32.GetForegroundWindow
PostMessage = user32.PostMessageW
FindWindow = user32.FindWindowW

# Constantes ShowWindow
SW_HIDE = 0
SW_MINIMIZE = 6
SW_MAXIMIZE = 3
SW_RESTORE = 9
SW_SHOW = 5

# WM_CLOSE para fechar janela
WM_CLOSE = 0x0010

# Mapeamento nome amigável → processo
_APP_PROCESSOS = {
    "chrome":       "chrome.exe",
    "navegador":    "chrome.exe",
    "firefox":      "firefox.exe",
    "edge":         "msedge.exe",
    "spotify":      "spotify.exe",
    "discord":      "discord.exe",
    "vscode":       "code.exe",
    "code":         "code.exe",
    "notepad":      "notepad.exe",
    "bloco de notas": "notepad.exe",
    "explorer":     "explorer.exe",
    "paint":        "mspaint.exe",
    "teams":        "teams.exe",
    "zoom":         "zoom.exe",
    "obs":          "obs64.exe",
    "steam":        "steam.exe",
    "calculadora":  "calculator.exe",
    "calculator":   "calculator.exe",
    "word":         "winword.exe",
    "excel":        "excel.exe",
    "powerpoint":   "powerpnt.exe",
    "outlook":      "outlook.exe",
    "cmd":          "cmd.exe",
    "terminal":     "wt.exe",
    "powershell":   "powershell.exe",
    "task manager": "taskmgr.exe",
    "gerenciador":  "taskmgr.exe",
    "obsidian":     "obsidian.exe",
    "lol":          "leagueclient.exe",
    "league":       "leagueclient.exe",
    "vlc":          "vlc.exe",
    "telegram":     "telegram.exe",
    "whatsapp":     "whatsapp.exe",
}


# ------------------------------------------------------------------
# Enumeração de janelas
# ------------------------------------------------------------------

def listar_janelas(somente_visiveis: bool = True) -> list[dict]:
    """
    Lista todas as janelas abertas com título e handle.

    Returns:
        list[dict]: [{"titulo": str, "hwnd": int}, ...]
    """
    janelas = []

    def _callback(hwnd, _):
        if somente_visiveis and not IsWindowVisible(hwnd):
            return True
        length = GetWindowTextLength(hwnd)
        if length > 0:
            buf = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buf, length + 1)
            titulo = buf.value.strip()
            if titulo:
                janelas.append({"titulo": titulo, "hwnd": hwnd})
        return True

    EnumWindows(EnumWindowsProc(_callback), 0)
    return janelas


def encontrar_janela(nome: str) -> Optional[dict]:
    """
    Encontra a janela mais relevante pelo nome (busca parcial, case-insensitive).

    Returns:
        dict {"titulo", "hwnd"} ou None
    """
    nome_lower = nome.lower()
    janelas = listar_janelas()

    # Correspondência exata primeiro
    for j in janelas:
        if nome_lower == j["titulo"].lower():
            return j

    # Correspondência parcial
    for j in janelas:
        if nome_lower in j["titulo"].lower():
            return j

    # Tenta pelo nome do processo
    processo = _APP_PROCESSOS.get(nome_lower)
    if processo:
        for j in janelas:
            if processo.lower().replace(".exe", "") in j["titulo"].lower():
                return j

    return None


def janela_ativa() -> Optional[dict]:
    """Retorna a janela que está em foco agora"""
    hwnd = GetForegroundWindow()
    if hwnd:
        length = GetWindowTextLength(hwnd)
        if length > 0:
            buf = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buf, length + 1)
            return {"titulo": buf.value.strip(), "hwnd": hwnd}
    return None


# ------------------------------------------------------------------
# Controles de janela
# ------------------------------------------------------------------

def _operar_janela(nome: str, operacao: int, nome_op: str) -> tuple:
    """Aplica ShowWindow a uma janela pelo nome"""
    janela = encontrar_janela(nome)
    if not janela:
        return False, f"Janela '{nome}' não encontrada. Verifique se o app está aberto."
    ShowWindow(janela["hwnd"], operacao)
    return True, f"'{janela['titulo']}' {nome_op}"


def minimizar(nome: str = None) -> tuple:
    """Minimiza uma janela pelo nome, ou a janela ativa se nome=None"""
    if nome is None:
        j = janela_ativa()
        if not j:
            return False, "Nenhuma janela ativa encontrada"
        ShowWindow(j["hwnd"], SW_MINIMIZE)
        return True, f"'{j['titulo']}' minimizado"
    return _operar_janela(nome, SW_MINIMIZE, "minimizado")


def maximizar(nome: str = None) -> tuple:
    """Maximiza uma janela pelo nome, ou a janela ativa"""
    if nome is None:
        j = janela_ativa()
        if not j:
            return False, "Nenhuma janela ativa encontrada"
        ShowWindow(j["hwnd"], SW_MAXIMIZE)
        return True, f"'{j['titulo']}' maximizado"
    return _operar_janela(nome, SW_MAXIMIZE, "maximizado")


def restaurar(nome: str = None) -> tuple:
    """Restaura janela ao tamanho normal"""
    if nome is None:
        j = janela_ativa()
        if not j:
            return False, "Nenhuma janela ativa encontrada"
        ShowWindow(j["hwnd"], SW_RESTORE)
        return True, f"'{j['titulo']}' restaurado"
    return _operar_janela(nome, SW_RESTORE, "restaurado")


def fechar_janela(nome: str = None) -> tuple:
    """Fecha uma janela (envia WM_CLOSE, equivalente a clicar no X)"""
    if nome is None:
        j = janela_ativa()
        if not j:
            return False, "Nenhuma janela ativa encontrada"
        PostMessage(j["hwnd"], WM_CLOSE, 0, 0)
        return True, f"'{j['titulo']}' fechado"

    janela = encontrar_janela(nome)
    if not janela:
        return False, f"Janela '{nome}' não encontrada"
    PostMessage(janela["hwnd"], WM_CLOSE, 0, 0)
    return True, f"'{janela['titulo']}' fechado"


def focar_janela(nome: str) -> tuple:
    """Traz uma janela para frente / troca para ela"""
    janela = encontrar_janela(nome)
    if not janela:
        return False, f"'{nome}' não está aberto"

    hwnd = janela["hwnd"]
    # Restaura se estiver minimizado
    ShowWindow(hwnd, SW_RESTORE)
    SetForegroundWindow(hwnd)
    return True, f"Mudei para '{janela['titulo']}'"


def alternar_janela() -> tuple:
    """Simula Alt+Tab para trocar de janela"""
    import pyautogui
    pyautogui.hotkey('alt', 'tab')
    return True, "Alternando janela"


def minimizar_tudo() -> tuple:
    """Minimiza todas as janelas (Win+D)"""
    import pyautogui
    pyautogui.hotkey('win', 'd')
    return True, "Todas as janelas minimizadas"


def mostrar_area_trabalho() -> tuple:
    """Mostra a área de trabalho (Win+D toggle)"""
    return minimizar_tudo()


def encerrar_processo_janela(nome: str) -> tuple:
    """Encerra o processo pelo nome (tenta com e sem .exe, e variações)"""
    nome_lower = nome.lower().strip()

    # Monta lista de candidatos a nome de processo
    candidatos = set()
    candidatos.add(nome_lower)
    candidatos.add(nome_lower + ".exe")
    # Usa mapeamento se disponível
    if nome_lower in _APP_PROCESSOS:
        proc_mapeado = _APP_PROCESSOS[nome_lower]
        candidatos.add(proc_mapeado.lower())
    # Variações comuns
    _extras = {
        "opera": ["opera.exe", "launcher.exe"],
        "opera gx": ["opera.exe", "launcher.exe"],
        "chrome": ["chrome.exe"],
        "edge": ["msedge.exe"],
        "vscode": ["code.exe"],
        "code": ["code.exe"],
        "obsidian": ["obsidian.exe"],
        "discord": ["discord.exe", "discordptb.exe", "discordcanary.exe"],
        "spotify": ["spotify.exe"],
        "explorer": ["explorer.exe"],
        "notepad": ["notepad.exe", "notepad++.exe"],
        "paint": ["mspaint.exe"],
        "calculator": ["calculator.exe", "calculatorapp.exe"],
        "teams": ["teams.exe", "ms-teams.exe"],
        "zoom": ["zoom.exe"],
        "word": ["winword.exe"],
        "excel": ["excel.exe"],
        "powerpoint": ["powerpnt.exe"],
    }
    for key, procs in _extras.items():
        if key in nome_lower or nome_lower in key:
            candidatos.update(procs)

    encerrados = 0
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pname = proc.info['name'].lower()
            if pname in candidatos:
                proc.terminate()
                encerrados += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if encerrados:
        return True, f"'{nome}' encerrado"
    return False, f"Processo '{nome}' não encontrado — verifique se está aberto"


def listar_apps_abertos() -> tuple:
    """Lista os apps abertos de forma legível para o Jarvis falar"""
    janelas = listar_janelas()
    _ignorar = [
        "program manager", "default ime", "nvidia", "realtek", "settingssynchhost",
        "windows input", "msctfmonitor", "application frame host", "shell_",
        "dde server", "gdip", "gdi+", "ole", "tooltip", "popupmenu",
    ]
    titulos = []
    vistos = set()
    for j in janelas:
        t = j["titulo"].strip()
        if not t or len(t) < 2:
            continue
        if any(ig in t.lower() for ig in _ignorar):
            continue
        # Pega o segmento mais descritivo do título
        partes = [p.strip() for p in t.split(" - ") if p.strip()]
        nome_curto = partes[-1] if partes else t  # último segmento geralmente é o app
        if nome_curto.lower() not in vistos and len(nome_curto) > 1:
            vistos.add(nome_curto.lower())
            titulos.append(nome_curto)

    if titulos:
        lista = ", ".join(titulos[:10])
        return True, f"Apps abertos: {lista}"
    return False, "Não encontrei janelas abertas"


# ------------------------------------------------------------------
# Atalhos de teclado do Windows
# ------------------------------------------------------------------

def _hotkey(*keys) -> tuple:
    try:
        import pyautogui
        pyautogui.hotkey(*keys)
        return True, None
    except Exception as e:
        return False, str(e)


def abrir_configuracoes() -> tuple:
    subprocess.Popen("start ms-settings:", shell=True)
    return True, "Abrindo configurações do Windows"


def abrir_gerenciador_tarefas() -> tuple:
    subprocess.Popen("taskmgr", shell=True)
    return True, "Abrindo gerenciador de tarefas"


def travar_orientacao_tela() -> tuple:
    return True, "Use as configurações do Windows para travar a orientação da tela"


# ------------------------------------------------------------------
# Interface unificada para o brain.py
# ------------------------------------------------------------------

def controlar_janela(acao: str, parametro: str = None) -> dict:
    """
    Interface única para o brain.py.

    Ações:
        minimizar, maximizar, restaurar, fechar, focar,
        alternar, minimizar_tudo, listar, encerrar,
        configuracoes, gerenciador_tarefas, area_trabalho
    """
    mapa = {
        "minimizar":            lambda: minimizar(parametro),
        "maximizar":            lambda: maximizar(parametro),
        "restaurar":            lambda: restaurar(parametro),
        "fechar":               lambda: fechar_janela(parametro),
        "focar":                lambda: focar_janela(parametro) if parametro else (False, "Informe o app"),
        "alternar":             lambda: alternar_janela(),
        "minimizar_tudo":       lambda: minimizar_tudo(),
        "area_trabalho":        lambda: mostrar_area_trabalho(),
        "listar":               lambda: listar_apps_abertos(),
        "encerrar":             lambda: encerrar_processo_janela(parametro) if parametro else (False, "Informe o app"),
        "configuracoes":        lambda: abrir_configuracoes(),
        "gerenciador_tarefas":  lambda: abrir_gerenciador_tarefas(),
    }

    if acao not in mapa:
        return {"sucesso": False, "mensagem": f"Ação '{acao}' não reconhecida"}

    try:
        sucesso, mensagem = mapa[acao]()
        return {"sucesso": sucesso, "mensagem": mensagem}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro em '{acao}': {e}"}