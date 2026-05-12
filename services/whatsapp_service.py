"""
WhatsApp Service - Abre conversas e envia mensagens via automação de UI.
Suporta WhatsApp Desktop (standalone) e WhatsApp Store.
"""

import os
import time
import subprocess
import pyautogui
import pyperclip

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3

_DELAY_CURTO  = 0.5
_DELAY_MEDIO  = 1.2
_DELAY_LONGO  = 2.5

# Caminhos conhecidos do WhatsApp Desktop (versão standalone, não Store)
_LOCAL    = os.environ.get("LOCALAPPDATA", "")
_ROAMING  = os.environ.get("APPDATA", "")

_CAMINHOS_WA = [
    os.path.join(_LOCAL,   "WhatsApp", "WhatsApp.exe"),
    os.path.join(_ROAMING, "WhatsApp", "WhatsApp.exe"),
    os.path.join(_LOCAL,   "Programs", "WhatsApp", "WhatsApp.exe"),
]


# ------------------------------------------------------------------
# Encontrar e abrir o WhatsApp
# ------------------------------------------------------------------

def _caminho_whatsapp() -> str | None:
    """Retorna o caminho do executável do WhatsApp, ou None se não encontrado."""
    for p in _CAMINHOS_WA:
        if os.path.exists(p):
            return p

    # Tenta via 'where' (funciona se estiver no PATH — Store ou Desktop)
    try:
        resultado = subprocess.check_output(
            ["where", "WhatsApp.exe"],
            stderr=subprocess.DEVNULL, text=True, timeout=3
        ).strip().splitlines()
        if resultado and os.path.exists(resultado[0].strip()):
            return resultado[0].strip()
    except Exception:
        pass

    return None


def _abrir_whatsapp_processo() -> bool:
    """
    Tenta abrir o WhatsApp por vários métodos.
    Retorna True se conseguiu disparar o processo.
    """
    # 1. Caminho direto do executável
    caminho = _caminho_whatsapp()
    if caminho:
        try:
            subprocess.Popen(caminho)
            print(f"[WhatsApp] Aberto via executável: {caminho}")
            return True
        except Exception as e:
            print(f"[WhatsApp] Falha no executável: {e}")

    # 2. URI scheme da Store (abre qualquer versão instalada pela Store)
    try:
        subprocess.Popen("start whatsapp:", shell=True)
        print("[WhatsApp] Aberto via URI scheme (Store)")
        return True
    except Exception:
        pass

    # 3. Comando 'WhatsApp' no PATH (versão Store adiciona ao PATH)
    try:
        subprocess.Popen("WhatsApp.exe", shell=False)
        print("[WhatsApp] Aberto via PATH (WhatsApp.exe)")
        return True
    except Exception:
        pass

    # 4. explorer com URI
    try:
        subprocess.Popen(["explorer.exe", "whatsapp:"])
        print("[WhatsApp] Aberto via explorer URI")
        return True
    except Exception:
        pass

    print("[WhatsApp] ❌ Não consegui abrir o WhatsApp por nenhum método")
    return False


def _encontrar_janela_whatsapp():
    """Retorna a janela do WhatsApp ou None."""
    try:
        import pygetwindow as gw
        todas = gw.getAllWindows()
        for j in todas:
            if "whatsapp" in j.title.lower():
                return j
    except Exception:
        pass
    return None


def _focar_whatsapp(espera_max: int = 15) -> bool:
    """
    Garante que o WhatsApp está aberto e em foco.
    Abre se necessário, espera até espera_max segundos.
    """
    janela = _encontrar_janela_whatsapp()
    if janela:
        try:
            if janela.isMinimized:
                janela.restore()
            janela.activate()
            time.sleep(_DELAY_MEDIO)
            return True
        except Exception:
            pass

    # Não encontrou — abre
    print("[WhatsApp] Abrindo WhatsApp...")
    if not _abrir_whatsapp_processo():
        return False

    # Aguarda a janela aparecer
    inicio = time.time()
    while time.time() - inicio < espera_max:
        time.sleep(1.5)
        janela = _encontrar_janela_whatsapp()
        if janela:
            try:
                janela.activate()
                time.sleep(_DELAY_MEDIO)
                return True
            except Exception:
                pass

    print("[WhatsApp] ⚠️ Janela não apareceu após abrir")
    return False


# ------------------------------------------------------------------
# Navegação no WhatsApp
# ------------------------------------------------------------------

def _buscar_contato(nome: str) -> bool:
    """Abre a busca e procura o contato."""
    try:
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(_DELAY_MEDIO)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyperclip.copy(nome)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(_DELAY_LONGO)
        pyautogui.press('enter')
        time.sleep(_DELAY_MEDIO)
        return True
    except Exception as e:
        print(f"[WhatsApp] Erro ao buscar contato '{nome}': {e}")
        return False


def _digitar_e_enviar(mensagem: str) -> bool:
    """
    Cola a mensagem na caixa de texto do WhatsApp e envia.
    Estratégia: clica na parte inferior central da janela (onde fica a caixa)
    em vez de usar Tab/Escape que pode fechar a conversa.
    """
    try:
        janela = _encontrar_janela_whatsapp()
        if not janela:
            print("[WhatsApp] Janela não encontrada para digitar")
            return False

        # Calcula posição da caixa de mensagem:
        # centro horizontal, 92% da altura (parte inferior da janela)
        x = janela.left + janela.width // 2
        y = janela.top + int(janela.height * 0.92)

        # Clica na caixa de mensagem
        pyautogui.click(x, y)
        time.sleep(0.4)

        # Garante que está vazia antes de colar (Ctrl+A não apaga msgs anteriores no WA)
        # Cola a mensagem via clipboard (preserva acentos e emojis)
        pyperclip.copy(mensagem)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)

        # Envia com Enter
        pyautogui.press('enter')
        time.sleep(0.5)

        print(f"[WhatsApp] ✅ Mensagem colada e enviada")
        return True

    except Exception as e:
        print(f"[WhatsApp] Erro ao enviar: {e}")
        return False


# ------------------------------------------------------------------
# API pública
# ------------------------------------------------------------------

def enviar_mensagem(contato: str, mensagem: str) -> tuple:
    print(f"[WhatsApp] Enviando para '{contato}': {mensagem[:60]}...")
    if not _focar_whatsapp():
        return False, "Não consegui abrir o WhatsApp. Verifique se está instalado."
    if not _buscar_contato(contato):
        return False, f"Não encontrei '{contato}' no WhatsApp"
    # Re-foca a janela após a busca (Enter pode ter desfocado)
    time.sleep(0.5)
    janela = _encontrar_janela_whatsapp()
    if janela:
        try:
            janela.activate()
            time.sleep(0.5)
        except Exception:
            pass
    if not _digitar_e_enviar(mensagem):
        return False, "Não consegui enviar a mensagem"
    return True, f"Mensagem enviada para {contato}"


def abrir_conversa(contato: str) -> tuple:
    if not _focar_whatsapp():
        return False, "Não consegui abrir o WhatsApp"
    if not _buscar_contato(contato):
        return False, f"Contato '{contato}' não encontrado"
    return True, f"Conversa com {contato} aberta"


def abrir_whatsapp() -> tuple:
    if _focar_whatsapp():
        return True, "WhatsApp aberto"
    return False, "Não consegui abrir o WhatsApp. Verifique a instalação."


# ------------------------------------------------------------------
# Interface unificada para o brain.py
# ------------------------------------------------------------------

def controlar_whatsapp(acao: str, contato: str = None, mensagem: str = None) -> dict:
    if acao == "enviar":
        if not contato:
            return {"sucesso": False, "mensagem": "Informe o nome do contato"}
        if not mensagem:
            return {"sucesso": False, "mensagem": "Qual mensagem você quer enviar?"}
        s, m = enviar_mensagem(contato, mensagem)
        return {"sucesso": s, "mensagem": m}
    elif acao == "abrir":
        s, m = abrir_whatsapp()
        return {"sucesso": s, "mensagem": m}
    elif acao == "conversa":
        if not contato:
            return {"sucesso": False, "mensagem": "Informe o nome do contato"}
        s, m = abrir_conversa(contato)
        return {"sucesso": s, "mensagem": m}
    return {"sucesso": False, "mensagem": f"Ação '{acao}' não reconhecida"}