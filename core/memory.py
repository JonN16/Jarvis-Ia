import json

MEMORY_FILE = "memory.json"


def carregar_memoria():
    """Load memory from JSON file"""
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Aviso: {MEMORY_FILE} não encontrado. Criando novo arquivo.")
        salvar_memoria({"ultimo_app": "", "historico": [], "preferencias": {}})
        return {"ultimo_app": "", "historico": [], "preferencias": {}}
    except Exception as e:
        print(f"Erro ao carregar memória: {e}")
        return {"ultimo_app": "", "historico": [], "preferencias": {}}


def salvar_memoria(data):
    """Save memory to JSON file"""
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar memória: {e}")


def adicionar_historico(comando):
    """Add command to history"""
    memoria = carregar_memoria()
    if "historico" not in memoria:
        memoria["historico"] = []
    memoria["historico"].append(comando)
    if len(memoria["historico"]) > 100:  # Keep only last 100
        memoria["historico"] = memoria["historico"][-100:]
    salvar_memoria(memoria)
