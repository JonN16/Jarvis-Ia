# Jarvis Professional AI Assistant

Um assistente de voz profissional baseado em Python com IA local usando Ollama.

## 🎯 Características

- ✅ Voz offline com pyttsx3
- ✅ IA local com Ollama (llama3.2:3b)
- ✅ Reconhecimento de voz em português
- ✅ Estrutura modular e profissional
- ✅ Comandos rápidos (sem IA)
- ✅ Sistema de memória
- ✅ Interface moderna com CustomTkinter
- ✅ Controle de Windows
- ✅ Automação de aplicativos

## 📁 Estrutura do Projeto

```
jarvis_projeto/
├── main.py                 # Entrada principal
├── config.py              # Configurações
├── requirements.txt       # Dependências
├── memory.json           # Memória do assistente
│
├── core/
│   ├── brain.py          # Processamento de IA (comandos rápidos)
│   ├── voice.py          # Síntese de voz
│   ├── listener.py       # Reconhecimento de voz
│   ├── memory.py         # Sistema de memória
│   └── actions.py        # Execução de ações
│
├── services/
│   ├── ollama_service.py # Integração com Ollama
│   ├── app_finder.py     # Localização de aplicativos
│   ├── spotify_service.py # Integração com Spotify (future)
│   └── system_service.py # Controle do sistema
│
└── ui/
    └── interface.py      # Interface gráfica
```

## 🚀 Como Usar

### 1. Ativar Ambiente Virtual

```bash
venv\Scripts\activate
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Instalar Ollama

1. Baixe em: https://ollama.com/
2. Instale e execute em um terminal separado:

```bash
ollama run llama3.2:3b
```

**IMPORTANTE:** Mantenha o terminal do Ollama aberto enquanto usa o Jarvis.

### 4. Executar o Jarvis

```bash
python main.py
```

## 🎤 Como Usar o Jarvis

Diga "**jarvis**" para ativar e então seu comando:

- "jarvis abre spotify" - Abre o Spotify
- "jarvis abre chrome" - Abre o navegador
- "jarvis qual é sua cor favorita?" - Conversa com IA
- "jarvis encerrar" - Desliga o assistente

## ⚙️ Configurações

Edite `config.py` para personalizar:

```python
WAKE_WORD = "jarvis"        # Palavra-chave
VOICE_RATE = 190            # Velocidade da voz
MODEL_NAME = "llama3.2:3b"  # Modelo Ollama
LANGUAGE = "pt-BR"          # Idioma
```

## 📦 Dependências Principais

- **speech_recognition** - Reconhecimento de voz
- **pyttsx3** - Síntese de voz
- **requests** - HTTP para Ollama
- **customtkinter** - Interface gráfica
- **psutil** - Informações do sistema
- **keyboard** - Controle de teclado
- **pyautogui** - Controle de mouse

## 🔄 Fluxo de Funcionamento

```
1. Ouvir comando do usuário
2. Verificar se contém "jarvis" (wake word)
3. Tentar processar como comando rápido (sem IA)
4. Se não for comando rápido, consultar Ollama
5. Executar ação retornada pela IA
6. Repitir
```

## 📚 Próximos Passos

### Melhorias Rápidas
- [ ] Adicionar mais comandos rápidos
- [ ] Integrar Spotify Web API
- [ ] Controle de volume avançado
- [ ] Automação de tarefas

### Melhorias Avançadas
- [ ] Wake word real (sem "jarvis" explícito)
- [ ] Whisper offline (detecção de som)
- [ ] RAG (Retrieval Augmented Generation)
- [ ] Múltiplos modelos Ollama
- [ ] Banco de dados para memória
- [ ] Interface 3D futurista
- [ ] Integração com assistentes (Home Assistant)

## 🐛 Troubleshooting

### Erro: "Não consegui conectar ao Ollama"
- Verifique se `ollama run llama3.2:3b` está ativo em outro terminal
- Tente acessar: http://localhost:11434

### Erro: "Não entendi o que você disse"
- Verifique o microfone
- Tente falar mais alto e claro
- Certifique-se de que nenhum ruído está interferindo

### Erro: Imports não encontrados
- Reative o ambiente virtual
- Execute `pip install -r requirements.txt` novamente

## 📝 Notas de Desenvolvimento

Este projeto é um ótimo exemplo de:
- Arquitetura de software modular
- Integração de IA local
- Automação do Windows
- Processamento de voz
- Design de sistemas

**Perfeito para portfólio e diferencial em entrevistas!**

## 📄 Licença

Projeto pessoal - Livre para usar e modificar.

---

**Desenvolvido com ❤️ usando Python, Ollama e CustomTkinter**
