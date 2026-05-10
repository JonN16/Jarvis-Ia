"""
Memory module - Usa Obsidian como sistema de memória
Substitui o memory.json por notas no Obsidian
"""

import os
import re
import json
from datetime import datetime
from services.obsidian_service import get_vault_path, criar_nota, buscar_notas

# Arquivo de fallback (caso Obsidian não esteja disponível)
MEMORY_FILE = "memory.json"


def get_memory_note_path():
    """Obtém o caminho da nota de memória do Jarvis"""
    vault_path = get_vault_path()
    return os.path.join(vault_path, "_jarvis_memory.md")


def carregar_memoria():
    """Carrega memória do Obsidian (ou fallback JSON)"""
    memory_path = get_memory_note_path()
    
    try:
        # Tenta carregar do Obsidian
        if os.path.exists(memory_path):
            with open(memory_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extrai JSON do conteúdo da nota
                # Procura por ```json ... ``` ou apenas o JSON
                json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                else:
                    # Tenta parsear o conteúdo direto como JSON
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(0))
    except Exception as e:
        print(f"[Memória] Erro ao carregar do Obsidian: {e}")
    
    # Fallback para JSON local
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    
    # Memória padrão
    return {"historico": [], "preferencias": {}, "contexto": {}, "ultimo_comando": ""}


def salvar_memoria(memoria):
    """Salva memória no Obsidian (e fallback JSON)"""
    memory_path = get_memory_note_path()
    
    try:
        # Formata como nota Markdown
        now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        content = f"""# 🧠 Jarvis Memory

*Última atualização: {now}*

Esta nota contém a memória do assistente Jarvis. Não edite manualmente!

## Dados Estruturados

```json
{json.dumps(memoria, indent=2, ensure_ascii=False)}
```

## Histórico Recente

"""
        # Adiciona últimos comandos como lista legível
        historico = memoria.get("historico", [])[-10:]
        for i, cmd in enumerate(reversed(historico), 1):
            content += f"{i}. {cmd}\n"
        
        # Cria/atualiza nota no Obsidian
        vault_path = get_vault_path()
        if not os.path.exists(vault_path):
            os.makedirs(vault_path)
        
        with open(memory_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        print(f"[Memória] Erro ao salvar no Obsidian: {e}")
    
    # Sempre salva fallback JSON
    try:
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memoria, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def adicionar_historico(comando):
    """Adiciona comando ao histórico"""
    memoria = carregar_memoria()
    
    if "historico" not in memoria:
        memoria["historico"] = []
    
    memoria["historico"].append(comando)
    memoria["ultimo_comando"] = comando
    
    # Mantém apenas últimos 100 comandos
    if len(memoria["historico"]) > 100:
        memoria["historico"] = memoria["historico"][-100:]
    
    salvar_memoria(memoria)


def adicionar_contexto(chave, valor):
    """Adiciona informação ao contexto da memória"""
    memoria = carregar_memoria()
    
    if "contexto" not in memoria:
        memoria["contexto"] = {}
    
    memoria["contexto"][chave] = {
        "valor": valor,
        "data": datetime.now().strftime('%d/%m/%Y %H:%M')
    }
    
    salvar_memoria(memoria)


def obter_contexto(chave, default=None):
    """Obtém informação do contexto"""
    memoria = carregar_memoria()
    contexto = memoria.get("contexto", {})
    
    if chave in contexto:
        return contexto[chave].get("valor", default)
    return default


def adicionar_preferencia(chave, valor):
    """Adiciona preferência do usuário"""
    memoria = carregar_memoria()
    
    if "preferencias" not in memoria:
        memoria["preferencias"] = {}
    
    memoria["preferencias"][chave] = valor
    salvar_memoria(memoria)


def obter_preferencia(chave, default=None):
    """Obtém preferência do usuário"""
    memoria = carregar_memoria()
    preferencias = memoria.get("preferencias", {})
    return preferencias.get(chave, default)


def limpar_historico():
    """Limpa o histórico de comandos"""
    memoria = carregar_memoria()
    memoria["historico"] = []
    salvar_memoria(memoria)


def get_ultimos_comandos(n=5):
    """Retorna os últimos N comandos"""
    memoria = carregar_memoria()
    return memoria.get("historico", [])[-n:]