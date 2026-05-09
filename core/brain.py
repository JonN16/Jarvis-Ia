"""
Brain module - Contains core AI processing logic
"""

import re
import time
import pyautogui
from services.app_finder import abrir_app


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


def processar_comando(comando):
    """
    Process user command before sending to AI.
    Can implement fast commands without AI here.
    """
    comando_lower = comando.lower()

    # SPOTIFY - with music search
    if "spotify" in comando_lower:
        # Check if it's a search command
        if any(word in comando_lower for word in ["música", "musica", "tocar", "play", "colocar", "botar"]):
            # Extract song name
            musica = extrair_musica(comando)
            
            if musica:
                # Open Spotify
                abrir_app("spotify")
                time.sleep(2)  # Wait for Spotify to open
                
                # Try to search for the music
                try:
                    # Ctrl+L focuses the search bar in Spotify
                    pyautogui.hotkey('ctrl', 'l')
                    time.sleep(0.5)
                    # Type the music name
                    pyautogui.typewrite(musica, interval=0.05)
                    time.sleep(0.5)
                    # Press Enter to search
                    pyautogui.press('return')
                except Exception:
                    # If automation fails, just tell user to search manually
                    pass
                
                resposta = f"Abrindo Spotify e buscando '{musica}'."
                return {"acao": "falar", "parametro": "", "resposta": resposta}
        
        # Just open Spotify if no music specified
        abrir_app("spotify")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Spotify"}
    
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
