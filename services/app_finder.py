"""
App Finder - Abre aplicativos pelo nome.
Ordem de busca: config.APPS → scanner cache → PATH → palavra-chave.
"""

import subprocess
import shutil
import psutil
import unicodedata
import json
import os
from config import APPS

# Cache do scanner em memória (carregado uma vez)
_apps_cache: dict | None = None

# Apps que precisam de janela visível (não usar CREATE_NO_WINDOW)
_APPS_COM_JANELA = {
    "spotify", "discord", "chrome", "firefox", "edge", "opera",
    "obsidian", "steam", "epicgameslauncher", "leagueclient",
    "telegram", "whatsapp", "vlc", "obs64", "obs32",
}

# Mapeamento apelido → processos esperados (para verificar se já está aberto)
PROCESS_NAMES = {
    "spotify":           ["spotify.exe"],
    "discord":           ["discord.exe", "discordptb.exe", "discordcanary.exe"],
    "chrome":            ["chrome.exe", "chromium.exe"],
    "vscode":            ["code.exe", "vscodium.exe"],
    "calculator":        ["calculator.exe", "calc.exe"],
    "calculadora":       ["calculator.exe", "calc.exe"],
    "notepad":           ["notepad.exe"],
    "bloco de notas":    ["notepad.exe"],
    "explorer":          ["explorer.exe"],
    "paint":             ["mspaint.exe"],
    "lol":               ["leagueclient.exe", "leagueclientux.exe"],
    "league of legends": ["leagueclient.exe", "leagueclientux.exe"],
    "league":            ["leagueclient.exe", "leagueclientux.exe"],
    "vlc":               ["vlc.exe"],
    "firefox":           ["firefox.exe"],
    "edge":              ["msedge.exe"],
    "opera":             ["opera.exe"],
    "opera gx":          ["opera.exe"],
    "steam":             ["steam.exe"],
    "obsidian":          ["obsidian.exe"],
    "epic":              ["epicgameslauncher.exe"],
    "epic games":        ["epicgameslauncher.exe"],
    "telegram":          ["telegram.exe"],
    "whatsapp":          ["whatsapp.exe"],
    "obs":               ["obs64.exe", "obs32.exe"],
    "intellij":          ["idea64.exe"],
    "pycharm":           ["pycharm64.exe"],
    "roblox":            ["robloxplayerbeta.exe", "robloxplayer.exe"],
    "onedrive":          ["onedrive.exe"],
}


def _normalizar(texto: str) -> str:
    """Remove acentos e lowercasa."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto.lower())
        if unicodedata.category(c) != 'Mn'
    )


def _carregar_cache() -> dict:
    """Carrega o apps_cache.json do scanner (uma vez, depois fica em RAM)."""
    global _apps_cache
    if _apps_cache is not None:
        return _apps_cache
    try:
        cache_file = "apps_cache.json"
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                _apps_cache = json.load(f)
            return _apps_cache
    except Exception as e:
        print(f"[AppFinder] Aviso: cache não carregado — {e}")
    _apps_cache = {}
    return _apps_cache


def buscar_no_cache(nome: str) -> str | None:
    """
    Busca no cache com ranking de qualidade (sem ser guloso):
      1. Exata          "opera gx" == "opera gx"
      2. Prefixo        chave começa com nome ou nome começa com chave
      3. Subconjunto    todas as palavras do nome são palavras da chave
      4. Palavra longa  qualquer palavra >3 chars do nome bate como palavra inteira
    Retorna o caminho/comando ou None.
    """
    cache = _carregar_cache()
    if not cache:
        return None

    nome_norm = _normalizar(nome)
    palavras_nome = set(nome_norm.split())

    # Nível 1: exata
    if nome_norm in cache:
        return cache[nome_norm]

    # Nível 2: prefixo
    for chave, caminho in cache.items():
        if chave.startswith(nome_norm) or nome_norm.startswith(chave):
            return caminho

    # Nível 3: subconjunto de palavras
    for chave, caminho in cache.items():
        palavras_chave = set(chave.split())
        if palavras_nome and palavras_nome.issubset(palavras_chave):
            return caminho

    # Nível 4: palavra longa (>3 chars) como palavra inteira na chave
    palavras_longas = [p for p in palavras_nome if len(p) > 3]
    for palavra in palavras_longas:
        for chave, caminho in cache.items():
            if palavra in chave.split():
                return caminho

    return None


def app_ja_aberto(nome: str) -> bool:
    """Verifica se o app já está rodando."""
    nome_lower = _normalizar(nome)
    processos = PROCESS_NAMES.get(nome_lower, [f"{nome_lower}.exe", nome_lower])
    processos_lower = [p.lower() for p in processos]

    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() in processos_lower:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def _executar_caminho(caminho: str) -> bool:
    """Executa um caminho. Usa CREATE_NO_WINDOW só para apps sem UI."""
    nome_exe = os.path.basename(str(caminho)).replace(".exe", "").lower()
    precisa_janela = any(app in nome_exe for app in _APPS_COM_JANELA)
    flags = 0 if precisa_janela else subprocess.CREATE_NO_WINDOW
    try:
        subprocess.Popen(str(caminho), shell=True, creationflags=flags)
        return True
    except Exception:
        return False


def abrir_app(nome: str, forcar: bool = False) -> bool:
    """
    Abre um aplicativo pelo nome.
    Retorna True se conseguiu lançar, False se não encontrou.
    """
    nome_lower = _normalizar(nome)

    # Não reabre se já está rodando (exceto se forcar=True)
    if not forcar and app_ja_aberto(nome_lower):
        print(f"[AppFinder] '{nome}' já está aberto")
        return True

    # 1. config.APPS — mapeamento manual tem prioridade
    if nome_lower in APPS:
        if _executar_caminho(APPS[nome_lower]):
            print(f"[AppFinder] ✅ Via config: {nome}")
            return True

    # 2. Cache do app_scanner
    caminho = buscar_no_cache(nome_lower)
    if caminho and _executar_caminho(caminho):
        print(f"[AppFinder] ✅ Via cache: {nome} → {caminho}")
        return True

    # 3. PATH do sistema
    for tentativa in [nome_lower, nome_lower.replace(" ", ""), nome_lower + ".exe"]:
        caminho_path = shutil.which(tentativa)
        if caminho_path and _executar_caminho(caminho_path):
            print(f"[AppFinder] ✅ Via PATH: {caminho_path}")
            return True

    # 4. Palavra a palavra (ex: "league of legends" → busca "league" no cache)
    for palavra in sorted(nome_lower.split(), key=len, reverse=True):
        if len(palavra) > 3:
            caminho = buscar_no_cache(palavra)
            if caminho and _executar_caminho(caminho):
                print(f"[AppFinder] ✅ Via palavra '{palavra}': {caminho}")
                return True

    print(f"[AppFinder] ❌ Não encontrei '{nome}'")
    return False


def listar_apps_disponiveis() -> list[str]:
    """Retorna todos os apelidos conhecidos (config + cache)."""
    disponiveis = list(APPS.keys())
    for chave in _carregar_cache():
        if chave not in disponiveis:
            disponiveis.append(chave)
    return sorted(disponiveis)