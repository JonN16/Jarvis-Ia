import requests
import json
from config import OLLAMA_URL, MODEL_NAME, STREAM

SYSTEM_PROMPT = """
Você é Jarvis, um assistente de IA pessoal e profissional.

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

REGRAS IMPORTANTES:
- Seja conciso, direto e profissional
- Você tem acesso ao histórico da conversa — use-o para dar respostas coerentes
- O contexto do Obsidian são informações de memória — use APENAS se o usuário perguntar algo relacionado
- NUNCA use o contexto para responder um comando que não seja uma pergunta
- Se o usuário pedir para fazer algo (abrir app, tocar música, etc), faça — não comente o contexto
- Responda sempre em português do Brasil
"""

# ------------------------------------------------------------------
# Histórico de conversa em memória RAM
# Formato: [{"role": "user"|"assistant", "content": str}, ...]
# ------------------------------------------------------------------

_historico: list = []
_MAX_TURNOS = 10  # mantém os últimos 10 pares (user + assistant)


def adicionar_ao_historico(role: str, content: str):
    """Adiciona uma mensagem ao histórico da sessão"""
    _historico.append({"role": role, "content": content})
    max_items = _MAX_TURNOS * 2
    if len(_historico) > max_items:
        del _historico[:-max_items]


def limpar_historico():
    """Limpa o histórico — use quando quiser 'esquece tudo' """
    _historico.clear()
    print("[Ollama] Histórico de conversa limpo.")


def obter_historico() -> list:
    """Retorna cópia do histórico atual"""
    return list(_historico)


def _data_atual() -> str:
    """Retorna data e hora atual formatada para injetar no contexto"""
    from datetime import datetime
    agora = datetime.now()
    dias = ["segunda-feira","terça-feira","quarta-feira","quinta-feira","sexta-feira","sábado","domingo"]
    meses = ["janeiro","fevereiro","março","abril","maio","junho",
             "julho","agosto","setembro","outubro","novembro","dezembro"]
    dia_semana = dias[agora.weekday()]
    return (f"{dia_semana}, {agora.day} de {meses[agora.month-1]} de {agora.year}, "
            f"{agora.strftime('%H:%M')}")


def _montar_prompt(comando: str, contexto_obsidian: str = None) -> str:
    """
    Serializa o histórico no prompt (o endpoint /api/generate não suporta
    messages[], então incluímos o histórico como texto estruturado).
    """
    partes = []

    # Data e hora atual — sempre presente para o modelo não inventar
    partes.append(f"[Data e hora atual: {_data_atual()}]")

    if contexto_obsidian:
        partes.append(
            "[Memória do usuário — use só se a pergunta for relacionada]\n"
            + contexto_obsidian
            + "\n---"
        )

    if _historico:
        partes.append("[Histórico desta conversa]")
        for msg in _historico[-(_MAX_TURNOS * 2):]:
            prefixo = "Usuário" if msg["role"] == "user" else "Jarvis"
            partes.append(f"{prefixo}: {msg['content']}")
        partes.append("---")

    partes.append(f"Usuário: {comando}")
    return "\n".join(partes)


def pensar(comando: str, contexto_obsidian: str = None) -> dict:
    """
    Envia o comando ao Ollama com histórico de conversa.

    Args:
        comando:           O que o usuário disse agora
        contexto_obsidian: Memória do Obsidian (opcional)
    """
    prompt = _montar_prompt(comando, contexto_obsidian)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": STREAM,
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        resposta_text = response.json().get("response", "")

        try:
            limpo = (
                resposta_text.strip()
                .removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )
            resultado = json.loads(limpo)

            # Registra no histórico
            adicionar_ao_historico("user", comando)
            adicionar_ao_historico("assistant", resultado.get("resposta", ""))

            return resultado

        except json.JSONDecodeError:
            resposta_limpa = resposta_text[:300]
            adicionar_ao_historico("user", comando)
            adicionar_ao_historico("assistant", resposta_limpa)
            return {"acao": "falar", "parametro": "", "resposta": resposta_limpa}

    except requests.exceptions.ConnectionError:
        print("[Ollama] Erro: servidor não encontrado.")
        return {
            "acao": "falar",
            "parametro": "",
            "resposta": "Não consegui conectar ao servidor de IA. Verifique se o Ollama está rodando.",
        }
    except Exception as e:
        print(f"[Ollama] Erro inesperado: {e}")
        return {"acao": "falar", "parametro": "", "resposta": "Tive um problema ao processar seu comando."}