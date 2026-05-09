"""
Jarvis Professional AI Assistant
Main entry point for the application
"""

from core.listener import ouvir
from core.actions import executar
from core.brain import processar_comando
from services.ollama_service import pensar
from core.voice import falar
from core.memory import carregar_memoria, salvar_memoria, adicionar_historico
from config import WAKE_WORD


def main():
    """Main application loop"""
    print("=" * 50)
    print("  JARVIS - Professional AI Assistant")
    print("=" * 50)
    print(f"\n[Boot] Inicializando sistemas...")
    
    falar("Sistemas inicializados. Pronto para receber comandos.")
    print(f"[Boot] Aguardando palavra-chave: '{WAKE_WORD}'")
    print("[Ready] Digite 'sair' ou diga 'encerrar' para parar\n")

    while True:
        try:
            # Listen to user input
            comando = ouvir()

            if not comando:
                continue

            # Check for wake word
            if WAKE_WORD not in comando:
                continue

            print(f"[Processando] Comando detectado: {comando}")
            adicionar_historico(comando)

            # Try fast command first (without AI)
            resultado_rapido = processar_comando(comando)
            
            if resultado_rapido:
                # Fast command found
                print("[Info] Usando comando rápido (sem IA)")
                resultado = resultado_rapido
            else:
                # Need to use AI
                print("[Info] Consultando Ollama...")
                resultado = pensar(comando)

            # Execute the action
            continuar = executar(resultado)

            if not continuar:
                print("[Shutdown] Encerrando aplicação...")
                break

        except KeyboardInterrupt:
            print("\n[Shutdown] Interrupção do usuário detectada.")
            falar("Até logo!")
            break
        except Exception as e:
            print(f"[Erro] {e}")


if __name__ == "__main__":
    main()