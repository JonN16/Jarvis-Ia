import requests
import json
from config import OLLAMA_URL, MODEL_NAME, STREAM

SYSTEM_PROMPT = """
Você é Jarvis, um assistente de IA profissional.

Responda SEMPRE em JSON válido com esta estrutura exata:

{
  "acao": "falar" | "abrir_app" | "abrir_site" | "encerrar",
  "parametro": "valor ou vazio",
  "resposta": "o que você vai dizer para o usuário"
}

Ações disponíveis:
- "falar": Apenas responder verbalmente
- "abrir_app": Abrir um aplicativo (spotify, discord, chrome, vscode, etc)
- "abrir_site": Abrir um site no navegador
- "encerrar": Encerrar o assistente

Seja conciso, útil e profissional.
"""


def pensar(comando):
    """Send command to Ollama and get response"""
    payload = {
        "model": MODEL_NAME,
        "prompt": comando,
        "system": SYSTEM_PROMPT,
        "stream": STREAM
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        resposta_text = response.json()["response"]

        # Try to parse JSON response
        try:
            resultado = json.loads(resposta_text)
            return resultado
        except json.JSONDecodeError:
            # If response is not valid JSON, wrap it
            return {
                "acao": "falar",
                "parametro": "",
                "resposta": resposta_text[:200]
            }

    except requests.exceptions.ConnectionError:
        print("Erro: Não consegui conectar ao Ollama. Certifique-se de que 'ollama run llama3.2:3b' está ativo.")
        return {
            "acao": "falar",
            "parametro": "",
            "resposta": "Não consegui conectar ao servidor de IA. Verifique se o Ollama está rodando."
        }
    except Exception as e:
        print(f"Erro ao processar comando: {e}")
        return {
            "acao": "falar",
            "parametro": "",
            "resposta": "Tive um problema ao processar seu comando."
        }
