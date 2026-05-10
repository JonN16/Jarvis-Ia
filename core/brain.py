"""
Brain module - Contains core AI processing logic
"""

import re
import time
import pyautogui
from services.app_finder import abrir_app
from services.spotify_service import controlar_spotify, buscar_musica


def extrair_musica(comando):
    """Extract music name from command"""
    # Palavras que indicam uma música vem depois
    triggers = ["música", "musica", "tocar", "play", "colocar", "botar", "abrir"]
    
    comando_lower = comando.lower()
    
    for trigger in triggers:
        # Procura pelo trigger e pega tudo que vem depois
        if trigger in comando_lower:
            # Encontra a posição do trigger
            pos = comando_lower.find(trigger)
            # Pega tudo depois do trigger
            depois = comando_lower[pos + len(trigger):].strip()
            
            # Remove palavras conectivas no início
            palavras_remover = ["e ", "ou ", "a ", "o ", "de ", "da ", "do ", "uma ", "um "]
            for palavra in palavras_remover:
                if depois.startswith(palavra):
                    depois = depois[len(palavra):].strip()
            
            # Remove "spotify" e "jarvis" se ainda estiverem lá
            depois = depois.replace("spotify", "").replace("jarvis", "").strip()
            
            if depois and len(depois) > 2:  # Se tem algo válido
                return depois
    
    return None


def extrair_acao_spotify(comando):
    """
    Extrai ação específica do Spotify (pause, next, previous, volume)
    Returns: (acao, parametro) ou (None, None)
    """
    comando_lower = comando.lower()
    
    # Pause
    if any(word in comando_lower for word in ["pausar", "pause", "parar"]):
        return "pause", None
    
    # Resume/Play (inclui "despausar")
    if any(word in comando_lower for word in ["retomar", "continuar", "dar play", "iniciar", "despausar"]):
        return "resume", None
    
    # Next track
    if any(word in comando_lower for word in ["próxima", "proximo", "pular", "avançar", "next"]):
        return "next", None
    
    # Previous track
    if any(word in comando_lower for word in ["anterior", "voltar", "previous"]):
        return "previous", None
    
    # Volume
    if "volume" in comando_lower:
        # Tenta extrair número
        numeros = re.findall(r'\d+', comando_lower)
        if numeros:
            return "volume", numeros[0]
        return "volume", None
    
    # Queue (adicionar à fila)
    if any(word in comando_lower for word in ["fila", "queue", "adicionar"]):
        musica = extrair_musica(comando)
        return "queue", musica
    
    # Current track info
    if any(word in comando_lower for word in ["tocando", "atual", "agora", "música atual"]):
        return "current", None
    
    return None, None


def processar_comando(comando):
    """
    Process user command before sending to AI.
    Can implement fast commands without AI here.
    """
    comando_lower = comando.lower()

    # SPOTIFY - Controle profissional via API
    if "spotify" in comando_lower:
        # Verifica se é uma ação específica (pause, next, volume, etc)
        acao, parametro = extrair_acao_spotify(comando)
        
        if acao:
            resultado = controlar_spotify(acao, parametro)
            return {
                "acao": "falar",
                "parametro": "",
                "resposta": resultado["mensagem"]
            }
        
        # Verifica se é para tocar uma música específica
        if any(word in comando_lower for word in ["música", "musica", "tocar", "play", "colocar", "botar"]):
            musica = extrair_musica(comando)
            
            if musica:
                resultado = buscar_musica(musica)
                return {
                    "acao": "falar",
                    "parametro": "",
                    "resposta": resultado["mensagem"]
                }
        
        # Apenas abrir o Spotify
        abrir_app("spotify")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Spotify"}
    
    # CONTROLES DE MÍDIA GERAIS (funcionam com qualquer player)
    # Pause
    if any(word in comando_lower for word in ["pausar música", "pausar tudo", "pause a música"]):
        pyautogui.press('playpause')
        return {"acao": "falar", "parametro": "", "resposta": "Reprodução pausada"}
    
    # Play/Resume
    if any(word in comando_lower for word in ["retomar música", "continuar música", "dar play"]):
        pyautogui.press('playpause')
        return {"acao": "falar", "parametro": "", "resposta": "Reprodução retomada"}
    
    # Next track
    if any(word in comando_lower for word in ["próxima música", "pular música", "avançar música"]):
        pyautogui.press('nexttrack')
        return {"acao": "falar", "parametro": "", "resposta": "Próxima música"}
    
    # Previous track
    if any(word in comando_lower for word in ["música anterior", "voltar música"]):
        pyautogui.press('prevtrack')
        return {"acao": "falar", "parametro": "", "resposta": "Música anterior"}
    
    # DISCORD
    if "discord" in comando_lower:
        abrir_app("discord")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Discord"}
    
    # CHROME / NAVEGADOR
    if "chrome" in comando_lower or "navegador" in comando_lower or "browser" in comando_lower:
        abrir_app("chrome")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Chrome"}
    
    # VSCODE
    if "vscode" in comando_lower or "visual studio" in comando_lower or "code" in comando_lower:
        abrir_app("vscode")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Visual Studio Code"}
    
    # CALCULATOR
    if "calc" in comando_lower or "calculadora" in comando_lower:
        abrir_app("calculator")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Calculadora"}
    
    # NOTEPAD
    if "notepad" in comando_lower or "notas" in comando_lower or "texto" in comando_lower:
        abrir_app("notepad")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Notepad"}
    
    # FILE EXPLORER
    if "explorer" in comando_lower or "arquivos" in comando_lower or "files" in comando_lower:
        abrir_app("explorer")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Explorador de Arquivos"}
    
    # PAINT
    if "paint" in comando_lower or "pintura" in comando_lower:
        abrir_app("paint")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Paint"}
    
    # LEAGUE OF LEGENDS
    if "league" in comando_lower or "lol" in comando_lower or "tft" in comando_lower:
        abrir_app("lol")
        return {"acao": "falar", "parametro": "", "resposta": "Procurando e abrindo League of Legends"}
    
    # ENCERRAR / DESLIGAR
    if "encerrar" in comando_lower or "desligar" in comando_lower or "goodbye" in comando_lower:
        return {"acao": "encerrar", "parametro": "", "resposta": ""}
    
    # Command needs AI processing
    return None