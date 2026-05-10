import speech_recognition as sr
from config import LANGUAGE, SPEECH_RECOGNITION_TIMEOUT, AMBIENT_NOISE_DURATION
import time

# Inicializa o reconecedor uma única vez (mais eficiente)
recognizer = sr.Recognizer()

# Microfone global - inicializado uma vez para evitar problemas de reconnect
microphone = None


def _get_microphone():
    """Obtém o microfone global, inicializando se necessário"""
    global microphone
    if microphone is None:
        try:
            microphone = sr.Microphone()
            print("[Listener] Microfone inicializado")
        except Exception as e:
            print(f"[Listener] Erro ao inicializar microfone: {e}")
            return None
    return microphone


def _ajustar_mic(source):
    """Ajusta o microfone para o ruído ambiente"""
    try:
        # Ajusta o nível de ruído ambiente
        recognizer.adjust_for_ambient_noise(source, duration=AMBIENT_NOISE_DURATION)
        
        # Ajusta sensibilidade do microfone (opcional)
        # recognizer.energy_threshold = 300  # Valor padrão é 300
        # recognizer.dynamic_energy_threshold = True
    except Exception as e:
        print(f"[Listener] Aviso: erro ao ajustar ruído: {e}")


def ouvir(max_tentativas=3):
    """
    Listen to user input from microphone with retry mechanism
    
    Args:
        max_tentativas: Número máximo de tentativas em caso de falha
    
    Returns:
        str: Texto reconhecido ou string vazia se falhar
    """
    mic = _get_microphone()
    if mic is None:
        return ""
    
    for tentativa in range(max_tentativas):
        try:
            with mic as source:
                _ajustar_mic(source)
                print(f"\n[Ouvindo...] (tentativa {tentativa + 1}/{max_tentativas})")
                
                # Escuta o áudio com timeout
                try:
                    audio = recognizer.listen(source, timeout=SPEECH_RECOGNITION_TIMEOUT, 
                                            phrase_time_limit=15)  # Limite de 15s de fala
                except sr.WaitTimeoutError:
                    print("[Listener] Timeout: nenhuma fala detectada")
                    return ""
                except sr.RequestError as e:
                    print(f"[Listener] Erro na requisição: {e}")
                    return ""
                
                # Reconhece a fala
                try:
                    texto = recognizer.recognize_google(audio, language=LANGUAGE)
                    print(f"Você: {texto}")
                    return texto.lower()
                except sr.UnknownValueError:
                    if tentativa < max_tentativas - 1:
                        print("[Listener] Não entendi, tentando novamente...")
                        time.sleep(0.5)
                        continue
                    else:
                        print("[Listener] Não entendi o que foi dito")
                        return ""
                except sr.RequestError as e:
                    print(f"[Listener] Erro no reconhecimento: {e}")
                    return ""
                except Exception as e:
                    print(f"[Listener] Erro inesperado: {e}")
                    return ""
                    
        except OSError as e:
            # Erro de dispositivo de áudio
            print(f"[Listener] Erro no dispositivo de áudio (tentativa {tentativa + 1}): {e}")
            if tentativa < max_tentativas - 1:
                time.sleep(1)  # Aguarda antes de tentar novamente
                continue
            else:
                print("[Listener] Falha ao acessar microfone após múltiplas tentativas")
                return ""
        except Exception as e:
            print(f"[Listener] Erro geral: {e}")
            return ""
    
    return ""


def reset_microphone():
    """Reseta o microfone global (útil em caso de problemas)"""
    global microphone
    microphone = None
    print("[Listener] Microfone resetado")


# Função de teste
def test_microphone():
    """Testa o microfone e o reconhecimento"""
    print("=" * 50)
    print("  Teste de Microfone")
    print("=" * 50)
    print("\nDiga algo (ou pressione Ctrl+C para sair):")
    
    while True:
        try:
            texto = ouvir()
            if texto:
                print(f"✅ Reconhecido: '{texto}'")
            else:
                print("❌ Nenhum texto reconhecido")
        except KeyboardInterrupt:
            print("\n\nTeste encerrado.")
            break
        except Exception as e:
            print(f"Erro: {e}")
            break