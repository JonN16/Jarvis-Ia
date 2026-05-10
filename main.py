import subprocess
import psutil
import time
import keyboard
from core.listener import ouvir, reset_microphone
from core.actions import executar
from core.brain import processar_comando, obter_contexto_obsidian
from services.ollama_service import pensar, adicionar_ao_historico, limpar_historico
from core.voice import falar
from core.memory import adicionar_historico as salvar_historico_disco
from services.obsidian_service import buscar_aprendizado


def verificar_ollama():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == "ollama app.exe":
            print("[System] Ollama já está em execução.")
            return True
    print("[System] Ollama não detectado. Iniciando servidor...")
    try:
        subprocess.Popen(["ollama", "serve"], shell=True)
        time.sleep(3)
        return True
    except Exception as e:
        print(f"[Erro] Falha ao iniciar Ollama: {e}")
        return False


def ciclo_de_comando():
    print("\n[Ouvindo] Como posso ajudar?")
    falar("Diga seu comando.")

    comando = ouvir()
    if not comando:
        return

    print(f"[Processando] Comando: {comando}")

    # Salva no histórico em disco (memory.py)
    salvar_historico_disco(comando)

    # Comando especial: limpar histórico de conversa
    if any(w in comando.lower() for w in ["esquece tudo", "limpar histórico", "limpar conversa",
                                           "nova conversa", "recomeçar conversa", "zerar conversa"]):
        limpar_historico()
        falar("Histórico de conversa limpo. Podemos começar do zero.")
        print("\n[Standby] Aperte F9 para falar novamente...")
        return

    # ── Passo 1: comando rápido (brain.py) ───────────────────────────
    resultado = processar_comando(comando)

    if resultado:
        print("[Info] Comando direto detectado.")
        # Registra comandos diretos no histórico do Ollama também,
        # para ele saber o que aconteceu (ex: "você acabou de pausar o Spotify")
        adicionar_ao_historico("user", comando)
        adicionar_ao_historico("assistant", resultado.get("resposta", ""))
    else:
        # ── Passo 2: contexto do Obsidian ────────────────────────────
        print("[Info] Buscando contexto no Obsidian...")
        contexto_obsidian = obter_contexto_obsidian(comando)
        if contexto_obsidian:
            print("[Info] Contexto encontrado.")
        else:
            print("[Info] Nenhum contexto relevante no Obsidian")

        # ── Passo 3: Ollama (já registra no histórico internamente) ──
        print("[Info] Consultando Ollama com contexto...")
        resultado = pensar(comando, contexto_obsidian)

        # ── Passo 4: complementa com Obsidian se IA não soube ────────
        if resultado and "não" in resultado.get("resposta", "").lower():
            palavras = [
                p for p in comando.lower().split()
                if len(p) > 3 and p not in {"como", "quando", "onde", "que", "qual", "quem"}
            ]
            if palavras:
                infos = buscar_aprendizado(termo=" ".join(palavras[:2]))
                if infos:
                    resultado["resposta"] += f" (Também sei que: {'; '.join(infos[:2])})"

    executar(resultado)
    print("\n[Standby] Aperte F9 para falar novamente...")


def main():
    print("=" * 50)
    print("  JARVIS - Professional AI Assistant")
    print("=" * 50)

    if not verificar_ollama():
        print("[Erro Crítico] Não foi possível conectar ao Ollama.")
        return

    print("\n[Boot] Sistemas prontos.")
    falar("Sistemas inicializados e Ollama conectado.")

    ATALHO = 'f9'
    keyboard.add_hotkey(ATALHO, ciclo_de_comando)
    print(f"[Ready] Pressione '{ATALHO}' para falar")
    print("[Ready] Pressione 'ESC' para encerrar\n")

    keyboard.wait('esc')
    print("[Shutdown] Encerrando aplicação...")
    falar("Desligando sistemas. Até logo.")
    reset_microphone()


if __name__ == "__main__":
    main()