"""
App Scanner - Varre o PC e encontra executáveis automaticamente
Gera o mapeamento de apps para o config.py sem precisar hardcodar caminhos
"""

import os
import json
from pathlib import Path

_CACHE_FILE = "apps_cache.json"

_USER = os.path.expanduser("~")
_LOCAL = os.environ.get("LOCALAPPDATA", "")
_ROAMING = os.environ.get("APPDATA", "")

_PASTAS_PRIORITARIAS = [
    _LOCAL,
    _ROAMING,
    os.environ.get("PROGRAMFILES", "C:\\Program Files"),
    os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
    os.path.join(_LOCAL, "Programs"),
    os.path.join(_USER, "scoop", "apps"),
    # Pastas extras
    "C:\\Riot Games",
    "C:\\Games",
    "C:\\Program Files\\Riot Games",
    os.path.join(_ROAMING, "Riot Games"),
]

# Pastas de atalhos .lnk para resolver
_PASTAS_ATALHOS = [
    os.path.join(_USER, "Desktop"),                                          # Área de trabalho do usuário
    os.path.join(os.environ.get("PUBLIC", "C:\\Users\\Public"), "Desktop"),  # Área de trabalho pública
    os.path.join(_ROAMING, "Microsoft", "Windows", "Start Menu", "Programs"),   # Menu iniciar
    os.path.join(_LOCAL,   "Microsoft", "Windows", "Start Menu", "Programs"),   # Menu iniciar (local)
]

_IGNORAR_EXECUTAVEIS = {
    "uninstall.exe","unins000.exe","unins001.exe","uninst.exe",
    "update.exe","updater.exe","crashreporter.exe","crashpad_handler.exe",
    "helper.exe","installer.exe","setup.exe","install.exe",
    "elevated_trampoline.exe","squirrel.exe","7zg.exe",
    "dllhost.exe","svchost.exe","rundll32.exe","regsvr32.exe",
    "msiexec.exe","conhost.exe","werfault.exe",
}

_IGNORAR_PASTAS = {
    "windows\\system32","windows\\syswow64","windows\\winsxs",
    "microsoft.net","common files\\microsoft shared",
}

# Mapeamento: nome_exe → lista de apelidos que o Jarvis vai reconhecer
_APELIDOS = {
    "obsidian":          ["obsidian", "notas obsidian"],
    "spotify":           ["spotify"],
    "discord":           ["discord"],
    "discordptb":        ["discord"],
    "discordcanary":     ["discord"],
    "chrome":            ["chrome", "google chrome", "navegador", "browser"],
    "firefox":           ["firefox"],
    "msedge":            ["edge", "microsoft edge"],
    "opera":             ["opera", "opera gx"],
    "brave":             ["brave"],
    "vivaldi":           ["vivaldi"],
    "code":              ["vscode", "vs code", "visual studio code", "editor"],
    "notepad":           ["notepad", "bloco de notas"],
    "notepad++":         ["notepad++", "npp"],
    "mspaint":           ["paint", "pintura"],
    "calc":              ["calculadora", "calculator"],
    "explorer":          ["explorer", "arquivos", "explorador"],
    "vlc":               ["vlc", "video", "vídeo"],
    "obs64":             ["obs", "streaming"],
    "obs32":             ["obs", "streaming"],
    "telegram":          ["telegram"],
    "whatsapp":          ["whatsapp", "zap"],
    "steam":             ["steam"],
    "epicgameslauncher": ["epic", "epic games"],
    "leagueclient":      ["league", "lol", "league of legends"],
    "leagueclientux":    ["league", "lol"],
    "riotclientservices":["riot", "riot client"],
    "riotclientux":      ["riot", "riot client"],
    "valorant":          ["valorant"],
    "valorant-win64-shipping": ["valorant"],
    "tft":               ["tft", "teamfight tactics"],
    "powershell":        ["powershell"],
    "wt":                ["terminal", "windows terminal"],
    "cmd":               ["cmd", "prompt"],
    "taskmgr":           ["gerenciador de tarefas", "task manager"],
    "msteams":           ["teams", "microsoft teams"],
    "zoom":              ["zoom"],
    "slack":             ["slack"],
    "notion":            ["notion"],
    "figma":             ["figma"],
    "postman":           ["postman"],
    "insomnia":          ["insomnia"],
    "gimp":              ["gimp"],
    "blender":           ["blender"],
    "audacity":          ["audacity"],
    "winrar":            ["winrar"],
    "7zfm":              ["7zip", "7z"],
    "pycharm64":         ["pycharm"],
    "idea64":            ["intellij", "idea"],
    "webstorm64":        ["webstorm"],
    "cursor":            ["cursor"],
    "androidstudio":     ["android studio"],
    "virtualbox":        ["virtualbox"],
    "vmware":            ["vmware"],
}

# Apps que estão no PATH do Windows — não precisam de caminho completo
_NO_PATH = {
    "spotify","chrome","firefox","msedge","code","notepad",
    "calc","mspaint","explorer","powershell","cmd","taskmgr","wt",
}


def _deve_ignorar(caminho: str) -> bool:
    c = caminho.lower().replace("\\", "/")
    return any(ig in c for ig in _IGNORAR_PASTAS)


def _resolver_atalho(caminho_lnk: str) -> str | None:
    """Resolve um atalho .lnk e retorna o caminho do executável alvo"""
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        atalho = shell.CreateShortCut(caminho_lnk)
        alvo = atalho.Targetpath
        if alvo and alvo.lower().endswith(".exe") and os.path.exists(alvo):
            return alvo
    except Exception:
        pass

    # Fallback via PowerShell se win32com não estiver disponível
    try:
        import subprocess
        cmd = f'(New-Object -COM WScript.Shell).CreateShortcut("{caminho_lnk}").TargetPath'
        resultado = subprocess.check_output(
            ["powershell", "-Command", cmd],
            stderr=subprocess.DEVNULL, text=True, timeout=3
        ).strip()
        if resultado and resultado.lower().endswith(".exe") and os.path.exists(resultado):
            return resultado
    except Exception:
        pass
    return None


def escanear_atalhos(verbose: bool = True) -> dict:
    """
    Varre áreas de trabalho e menus iniciar por atalhos .lnk
    e resolve o executável real de cada um.
    """
    encontrados = {}

    for pasta in _PASTAS_ATALHOS:
        if not pasta or not os.path.exists(pasta):
            continue
        try:
            for root, dirs, files in os.walk(pasta):
                for arq in files:
                    if not arq.lower().endswith(".lnk"):
                        continue
                    caminho_lnk = os.path.join(root, arq)
                    exe_alvo = _resolver_atalho(caminho_lnk)
                    if not exe_alvo:
                        continue

                    nome_exe = os.path.basename(exe_alvo).lower().replace(".exe", "")
                    nome_atalho = arq.lower().replace(".lnk", "")

                    if nome_exe in _IGNORAR_EXECUTAVEIS or not exe_alvo:
                        continue

                    # Adiciona se está no mapeamento de apelidos
                    if nome_exe in _APELIDOS and _APELIDOS[nome_exe]:
                        if nome_exe not in encontrados:
                            encontrados[nome_exe] = exe_alvo
                            if verbose:
                                print(f"  🔗 {arq:35} → {exe_alvo}")
                    else:
                        # App desconhecido — só adiciona se parece um launcher/app real
                        # Ignora: contatos, documentos, pastas, links web
                        _parece_app = any(keyword in exe_alvo.lower() for keyword in
                                         [".exe", "launcher", "client", "app", "game"])
                        _ignorar_nomes = ["chrome", "edge", "firefox", "opera",  # já cobertos
                                          "uninstall", "setup", "install", "update",
                                          "shortcut", "atalho"]
                        _nome_ok = not any(ig in nome_atalho.lower() for ig in _ignorar_nomes)
                        if _parece_app and _nome_ok and len(nome_atalho) > 2:
                            if nome_exe not in encontrados:
                                encontrados[nome_exe] = exe_alvo
                                if nome_exe not in _APELIDOS:
                                    _APELIDOS[nome_exe] = [nome_atalho.strip().lower()]
                                if verbose:
                                    print(f"  🔗 {arq:35} → {exe_alvo} (novo: '{nome_atalho}')")
        except (PermissionError, OSError):
            continue

    return encontrados


def escanear_executaveis(verbose: bool = True) -> dict:
    """Varre as pastas e atalhos, retorna {nome_exe: caminho_completo}"""
    encontrados = {}
    total = 0

    if verbose:
        print("[Scanner] Varrendo seu PC... aguarde alguns segundos.")
        print("[Scanner] Lendo atalhos da área de trabalho e menu iniciar...")

    # Primeiro resolve atalhos .lnk (mais rápido e pega o League, etc.)
    atalhos = escanear_atalhos(verbose=verbose)
    encontrados.update(atalhos)

    for pasta in _PASTAS_PRIORITARIAS:
        if not pasta or not os.path.exists(pasta):
            continue
        try:
            for root, dirs, files in os.walk(pasta):
                if _deve_ignorar(root):
                    dirs.clear()
                    continue
                # Limita profundidade para velocidade
                if root.replace(pasta, "").count(os.sep) > 5:
                    dirs.clear()
                    continue
                for arq in files:
                    if not arq.lower().endswith(".exe"):
                        continue
                    total += 1
                    nome = arq.lower().replace(".exe", "")
                    if arq.lower() in _IGNORAR_EXECUTAVEIS:
                        continue
                    # Só salva se está no nosso mapeamento de apelidos
                    if nome in _APELIDOS and _APELIDOS[nome] and nome not in encontrados:
                        caminho = os.path.join(root, arq)
                        encontrados[nome] = caminho
                        if verbose:
                            print(f"  ✅ {arq:35} {caminho}")
        except (PermissionError, OSError):
            continue

    if verbose:
        print(f"\n[Scanner] {total} executáveis verificados | {len(encontrados)} apps encontrados")

    return encontrados


def gerar_mapeamento(executaveis: dict) -> dict:
    """Converte {nome_exe: caminho} → {apelido: caminho}"""
    mapa = {}
    for nome_exe, caminho in executaveis.items():
        apelidos = _APELIDOS.get(nome_exe, [])
        # Usa PATH para apps conhecidos, caminho completo para os outros
        valor = nome_exe if nome_exe in _NO_PATH else caminho
        for apelido in apelidos:
            mapa[apelido] = valor
    return mapa


def salvar_cache(mapa: dict):
    try:
        with open(_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(mapa, f, ensure_ascii=False, indent=2)
        print(f"[Scanner] Cache salvo em '{_CACHE_FILE}'")
    except Exception as e:
        print(f"[Scanner] Erro ao salvar: {e}")


def carregar_cache() -> dict:
    try:
        if os.path.exists(_CACHE_FILE):
            with open(_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


# Apps da Microsoft Store — ficam em WindowsApps (pasta protegida)
# São abertos via URI scheme ou pelo nome do pacote
_STORE_APPS = {
    "whatsapp":     "WhatsApp.exe",          # tenta via PATH (WindowsApps está no PATH)
    "zap":          "WhatsApp.exe",
    "calculadora":  "calc",
    "calculator":   "calc",
    "fotos":        "ms-photos:",            # URI scheme
    "photos":       "ms-photos:",
    "camera":       "microsoft.windows.camera:",
    "xbox":         "xbox:",
    "groove":       "mswindowsmusic:",
    "filmes":       "mswindowsvideo:",
    "mapas":        "bingmaps:",
    "clima":        "bingweather:",
}

_STORE_APELIDOS = {
    "WhatsApp":     ["whatsapp", "zap"],
    "calc":         ["calculadora", "calculator"],
}


def _encontrar_whatsapp() -> str | None:
    """
    Tenta encontrar o executável do WhatsApp em locais conhecidos.
    O WhatsApp Desktop (não Store) instala em AppData.
    """
    import subprocess

    caminhos_possiveis = [
        # WhatsApp Desktop (versão standalone)
        os.path.join(_LOCAL, "WhatsApp", "WhatsApp.exe"),
        os.path.join(_ROAMING, "WhatsApp", "WhatsApp.exe"),
        os.path.join(_LOCAL, "Programs", "WhatsApp", "WhatsApp.exe"),
        # WhatsApp via WindowsApps (Store) — acessível via PATH
        "WhatsApp.exe",
    ]

    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            return caminho

    # Tenta achar via where (se estiver no PATH)
    try:
        resultado = subprocess.check_output(
            ["where", "WhatsApp.exe"],
            stderr=subprocess.DEVNULL, text=True, timeout=3
        ).strip().splitlines()
        if resultado:
            return resultado[0].strip()
    except Exception:
        pass

    # Busca no WindowsApps (requer permissão de admin, mas tenta)
    windowsapps = os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files"), "WindowsApps")
    try:
        for pasta in os.listdir(windowsapps):
            if "whatsapp" in pasta.lower():
                exe = os.path.join(windowsapps, pasta, "WhatsApp.exe")
                if os.path.exists(exe):
                    return exe
    except (PermissionError, OSError):
        pass

    # Último recurso: usa o comando direto (funciona se estiver no PATH via Store)
    return "WhatsApp"


def _adicionar_store_apps(mapa: dict) -> dict:
    """Adiciona apps da Store ao mapeamento"""
    # WhatsApp
    wa_path = _encontrar_whatsapp()
    if wa_path:
        mapa["whatsapp"] = wa_path
        mapa["zap"] = wa_path
        print(f"  📱 WhatsApp encontrado: {wa_path}")
    else:
        # Fallback: usa o nome direto (funciona se estiver instalado via Store)
        mapa["whatsapp"] = "WhatsApp"
        mapa["zap"] = "WhatsApp"
        print("  📱 WhatsApp: usando comando direto (Store)")

    return mapa


def get_apps(forcar_rescan: bool = False) -> dict:
    """
    Retorna o mapeamento de apps prontos para uso.
    Na primeira execução escaneia o PC e salva em cache.
    Nas próximas execuções usa o cache (instantâneo).
    Use forcar_rescan=True quando instalar novos programas.
    """
    if not forcar_rescan:
        cache = carregar_cache()
        if cache:
            return cache
    exes = escanear_executaveis(verbose=True)
    mapa = gerar_mapeamento(exes)
    mapa = _adicionar_store_apps(mapa)  # adiciona WhatsApp e outros Store apps
    salvar_cache(mapa)
    return mapa


def listar_apps():
    """Exibe todos os apps encontrados"""
    apps = get_apps()
    if not apps:
        print("Nenhum app encontrado. Rode: python app_scanner.py")
        return

    por_exe = {}
    for apelido, caminho in sorted(apps.items()):
        exe = os.path.basename(str(caminho)).replace(".exe","") if str(caminho).endswith(".exe") else caminho
        if exe not in por_exe:
            por_exe[exe] = {"caminho": caminho, "apelidos": []}
        por_exe[exe]["apelidos"].append(apelido)

    print("\n" + "="*60)
    print("  Apps encontrados no seu PC")
    print("="*60)
    for exe, info in sorted(por_exe.items()):
        print(f"\n  {exe}")
        print(f"    Caminho : {info['caminho']}")
        print(f"    Apelidos: {', '.join(info['apelidos'])}")
    print(f"\n  Total: {len(por_exe)} apps | {len(apps)} apelidos\n")


if __name__ == "__main__":
    print("="*50)
    print("  Jarvis App Scanner")
    print("="*50)
    print("\n1. Escanear e salvar")
    print("2. Ver cache atual")
    print("3. Re-escanear (atualizar)")
    op = input("\nEscolha (1/2/3): ").strip()
    if op == "2":
        listar_apps()
    elif op == "3":
        get_apps(forcar_rescan=True)
        listar_apps()
    else:
        get_apps()
        listar_apps()