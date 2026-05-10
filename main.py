import subprocess
import psutil
import time
import keyboard
from core.listener import ouvir, reset_microphone
from core.actions import executar
from core.brain import processar_comando
from services.ollama_service import pensar
from core.voice import falar
from core.memory import adicionar_historico

def verificar_ollama():
    """Verifica se o Ollama está rodando, se não, inicia o processo"""
    process_name = "ollama app.exe" # Nome padrão do executável no Windows
    
    # Verifica se já está aberto
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == process_name.lower():
            print("[System] Ollama já está em execução.")
            return True

    print("[System] Ollama não detectado. Iniciando servidor...")
    try:
        # Tenta abrir o executável padrão (ajuste o caminho se necessário)
        subprocess.Popen(["ollama", "serve"], shell=True)
        time.sleep(3) # Aguarda o servidor subir
        return True
    except Exception as e:
        print(f"[Erro] Falha ao iniciar Ollama: {e}")
        return False

def ciclo_de_comando():
    """Função que executa quando a tecla é pressionada"""
    print("\n[Ouvindo] Como posso ajudar?")
    falar("Diga seu comando.")
    
    comando = ouvir()
    
    if not comando:
        return

    print(f"[Processando] Comando: {comando}")
    adicionar_historico(comando)

    # Lógica de processamento
    resultado_rapido = processar_comando(comando)
    
    if resultado_rapido:
        print("[Info] Comando rápido detectado.")
        resultado = resultado_rapido
    else:
        print("[Info] Consultando Ollama...")
        resultado = pensar(comando)

    # Executa a ação
    executar(resultado)
    print("\n[Standby] Aperte F9 para falar novamente...")

def main():
    """Main application setup"""
    print("=" * 50)
    print("  JARVIS - Professional AI Assistant")
    print("=" * 50)
    
    # 1. Garante que o motor de IA está ligado
    if not verificar_ollama():
        print("[Erro Crítico] Não foi possível conectar ao Ollama.")
        return

    print(f"\n[Boot] Sistemas prontos.")
    falar("Sistemas inicializados e Ollama conectado.")
    
    # 2. Configura a Tecla de Atalho (Hotkey)
    # Usei F9, mas pode trocar por 'ctrl+shift+j' ou qualquer outra
    ATALHO = 'f9'
    keyboard.add_hotkey(ATALHO, ciclo_de_comando)

    print(f"[Ready] Pressione '{ATALHO}' para falar")
    print("[Ready] Pressione 'ESC' para encerrar o programa\n")

    # 3. Mantém o programa rodando em standby (quase zero CPU)
    keyboard.wait('esc')
    print("[Shutdown] Encerrando aplicação...")
    falar("Desligando sistemas. Até logo.")
    
    # 4. Limpa recursos do microfone
    reset_microphone()

if __name__ == "__main__":
    main()