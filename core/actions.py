import webbrowser
from services.app_finder import abrir_app
from core.voice import falar


def executar(resultado):
    """Execute action based on AI response"""
    acao = resultado.get("acao")
    parametro = resultado.get("parametro", "")
    resposta = resultado.get("resposta", "")

    if resposta:
        falar(resposta)

    try:
        if acao == "abrir_app":
            abrir_app(parametro)

        elif acao == "abrir_site":
            webbrowser.open(parametro)

        elif acao == "encerrar":
            falar("Desligando o sistema.")
            return False

        elif acao == "falar":
            pass  # Already spoke above

    except Exception as e:
        print(f"Erro ao executar ação: {e}")

    return True
