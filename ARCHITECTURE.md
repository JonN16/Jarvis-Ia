# 🏗️ Arquitetura do Jarvis

## 📊 Diagrama de Fluxo

```
┌──────────────────────────────────────────────────────────┐
│                     USUÁRIO                               │
│                 (Fala "jarvis...")                        │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │   core/listener.py       │
        │   (Speech Recognition)   │
        │                          │
        │  - Ouve microfone        │
        │  - Transcreve voz→texto  │
        │  - Retorna comando       │
        └──────────┬───────────────┘
                   │
                   ▼ (comando = "jarvis xyz...")
        ┌──────────────────────────┐
        │   core/brain.py          │
        │   (Fast Commands)        │
        │                          │
        │  - Tenta match rápido    │
        │  - Sem IA                │
        │  - Resposta instantânea  │
        └──────┬──────────┬────────┘
               │          │
           ✅ MATCH    ❌ NÃO MATCH
               │          │
               │          ▼
               │   ┌──────────────────────┐
               │   │services/ollama_service
               │   │   (Ollama LLM)       │
               │   │                      │
               │   │ - Envia prompt       │
               │   │ - Aguarda resposta   │
               │   │ - Parse JSON         │
               │   └──────────┬───────────┘
               │              │
               └──────────┬───┘
                          │
                          ▼ {acao, parametro, resposta}
        ┌──────────────────────────┐
        │   core/actions.py        │
        │   (Executa Ações)        │
        │                          │
        │  - Fala resposta         │
        │  - Abre apps             │
        │  - Abre sites            │
        │  - Encerra program       │
        └──────────┬───────────────┘
                   │
        ┌──────────┴──────────┬──────────────┬──────────────┐
        │                     │              │              │
        ▼                     ▼              ▼              ▼
    ┌────────────┐      ┌────────┐   ┌─────────┐    ┌──────────┐
    │ core/      │      │        │   │ browser │    │ process  │
    │ voice.py   │      │windows │   │ (webbrowser)│ (fim)     │
    │ (Falar)    │      │control │   └─────────┘    └──────────┘
    └────────────┘      └────────┘
        │
        ▼
    ┌──────────────────────────┐
    │   core/memory.py         │
    │   (Salva em memory.json) │
    └──────────────────────────┘
```

## 📁 Estrutura & Responsabilidades

### 🧠 core/ (Cérebro)

#### `main.py` - ORQUESTRADOR PRINCIPAL
- Inicializa o sistema
- Loop principal
- Coordena todos os módulos
- Tratamento de erros global

```python
while True:
    comando = ouvir()          # listener.py
    if WAKE_WORD in comando:
        resultado_rapido = processar_comando(comando)  # brain.py
        if not resultado_rapido:
            resultado = pensar(comando)                # ollama_service.py
        executar(resultado)                            # actions.py
```

#### `listener.py` - ENTRADA DE VOZ
**Responsabilidade:** Capturar e transcrever voz

```python
def ouvir():
    # 1. Ativa microfone
    # 2. Ajusta ruído ambiente
    # 3. Ouve até timeout
    # 4. Reconhece voz → texto (Google API)
    # 5. Retorna texto em minúsculas
```

**Fluxo:** Microfone → Áudio → Google Speech → Texto

#### `voice.py` - SAÍDA DE VOZ
**Responsabilidade:** Sintetizar e reproduzir voz

```python
def falar(texto):
    # 1. Imprime no console
    # 2. Inicializa pyttsx3
    # 3. Configura velocidade
    # 4. Executa em thread
    # 5. Joga áudio no speaker
```

**Fluxo:** Texto → pyttsx3 → Som → Speakers

#### `brain.py` - PROCESSAMENTO RÁPIDO
**Responsabilidade:** Comandos que não precisam de IA

```python
def processar_comando(comando):
    # Retorna ação se for comando rápido
    # Se não for reconhecido, retorna None
    # → main.py envia para Ollama
```

**Vantagem:** Instantâneo, sem latência, sem servidor

#### `memory.py` - PERSISTÊNCIA
**Responsabilidade:** Guardar dados entre execuções

```python
carregar_memoria()   # memory.json → dict
salvar_memoria(data) # dict → memory.json
adicionar_historico(comando)  # Guarda comando executado
```

**Armazenamento:** JSON local

#### `actions.py` - EXECUÇÃO
**Responsabilidade:** Fazer o que a IA mandou

```python
def executar(resultado):
    # Extrai ação, parâmetro, resposta
    # Fala a resposta
    # Executa ação (abrir app, site, etc)
    # Retorna False se for "encerrar"
```

---

### 🔌 services/ (Integrações)

#### `ollama_service.py` - IA LOCAL
**Responsabilidade:** Comunicar com Ollama

```python
def pensar(comando):
    # 1. Monta prompt JSON
    # 2. Envia para Ollama (localhost:11434)
    # 3. Recebe resposta
    # 4. Parse JSON
    # 5. Retorna ação estruturada
```

**Requisitos:** Ollama rodando em terminal separado

#### `app_finder.py` - FINDER DE APPS
**Responsabilidade:** Localizar e abrir aplicativos

```python
def abrir_app(nome):
    # 1. Busca em APPS dict (config.py)
    # 2. Executa subprocess
    # 3. Retorna sucesso/falha
```

#### `system_service.py` - CONTROLE DO SISTEMA
**Responsabilidade:** Info do sistema, controle de processos

```python
obter_info_sistema()      # CPU, RAM, disco
obter_processos_em_uso()  # Lista de processos
encerrar_processo(nome)   # Kill process
```

#### `spotify_service.py` - SPOTIFY (FUTURO)
**Status:** Placeholder para implementação futura

---

### 🎨 ui/ (Interface)

#### `interface.py` - GUI MODERNA
**Responsabilidade:** Visualização moderna (ainda não integrada)

```python
class JarvisInterface:
    # Botões Start/Stop
    # Exibe status
    # Mostra comandos
    # Tema escuro
```

**Framework:** CustomTkinter (moderna, escura)

---

### ⚙️ config.py - CONFIGURAÇÃO CENTRAL

Todos os valores customizáveis em um único lugar:

```python
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"
VOICE_RATE = 190
WAKE_WORD = "jarvis"
APPS = {"spotify": "spotify", ...}
```

---

## 🔄 Fluxos Detalhados

### Cenário 1: Comando Rápido (< 100ms)

```
Usuário: "jarvis abre spotify"
              ↓
        listener.py captura
              ↓
        brain.py reconhece
              ↓
        actions.py executa (abre Spotify)
              ↓
        voice.py fala resposta
              ↓
        memory.py salva histórico
```

### Cenário 2: Comando com IA (2-5s)

```
Usuário: "jarvis qual é sua cor favorita?"
              ↓
        listener.py captura
              ↓
        brain.py não reconhece → None
              ↓
        ollama_service.py conecta (localhost:11434)
              ↓
        Ollama processa com llama3.2:3b
              ↓
        Retorna: {acao: "falar", resposta: "..."}
              ↓
        actions.py executa
              ↓
        voice.py fala
              ↓
        memory.py salva
```

### Cenário 3: Erro de Conexão

```
ollama_service.py tenta conectar
              ↓
        ConnectionError capturado
              ↓
        Retorna resposta de erro
              ↓
        voice.py fala: "Não consegui conectar..."
              ↓
        Aguarda próximo comando
```

---

## 🧬 Padrões de Design

### 1. **Modularidade**
- Cada arquivo = uma responsabilidade
- Funções simples e puras
- Fácil de testar e debugar

### 2. **Configuração Centralizada**
- `config.py` = fonte única da verdade
- Fácil customização sem editar código

### 3. **Error Handling**
- Try/except em pontos críticos
- Mensagens de erro amigáveis
- Continua executando mesmo com erro

### 4. **Logging**
- Print estruturado com [tags]
- Fácil seguir execução
- Pronto para integrar logging.py no futuro

### 5. **Async/Threading**
- Voice.py usa threads (não bloqueia)
- Listener.py usa speech_recognition (nativo)
- Pronto para asyncio no futuro

---

## 🎯 Decisões de Arquitetura

### Por que separar "fast commands" de IA?
```
Tempo de resposta:
- Fast commands: ~50ms
- Com IA: 2-5s

Overhead:
- Fast commands: Nenhum
- Com IA: Rede + processamento + parse JSON
```

### Por que usar Ollama em vez de API Online?
```
Vantagens:
- ✅ Offline (sem internet)
- ✅ Privacidade (roda local)
- ✅ Sem custo API
- ✅ Rápido (GPU se tiver)
- ❌ Requer Ollama rodando
- ❌ Mais lento que APIs
```

### Por que JSON para comunicação Ollama?
```
Razões:
- Estruturado
- Fácil de parse
- Padrão de API
- Extensível
```

---

## 📈 Escalabilidade Futura

```
Atual (v1)
├── Local
├── Pessoal
└── Protótipo

Próximo (v2)
├── Banco de dados
├── API HTTP
├── Interface web
└── Cloud sync

Futuro (v3)
├── Home automation
├── Mobile app
├── Múltiplos usuários
├── Enterprise
└── Open source community
```

---

## 🧪 Como Testar

### Teste Manual
```bash
python main.py
# Diga comandos e verifique resposta
```

### Teste de Componente
```python
# Testar listener sem Jarvis rodando
from core.listener import ouvir
texto = ouvir()
print(texto)
```

### Teste de Ollama
```python
# Testar conexão com Ollama
from services.ollama_service import pensar
resultado = pensar("qual é 2+2?")
print(resultado)
```

---

## 🐛 Debugging

### Modo Verbose
Adicionar `print()` em pontos chave:

```python
def executar(resultado):
    print(f"DEBUG: resultado = {resultado}")
    # ...
```

### Ver Logs
Todos os prints vão para console com [tags]:
```
[Boot] Inicializando...
[Processando] Comando detectado: jarvis abre spotify
[Info] Usando comando rápido
[Shutdown] Encerrando aplicação
```

### Testar Offline
```python
# Mock Ollama response
resultado = {
    "acao": "falar",
    "parametro": "",
    "resposta": "teste"
}
executar(resultado)
```

---

**Você agora entende a arquitetura completa do Jarvis! 🚀**
