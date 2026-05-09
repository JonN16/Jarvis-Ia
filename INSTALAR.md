# 🚀 Guia de Instalação - Jarvis em Português

## O Que Você Precisa Instalar

### 1️⃣ OLLAMA (OBRIGATÓRIO!)

**O que é?** Inteligência Artificial que roda no seu computador (offline).

**Passo a passo:**

1. Baixe em: https://ollama.com/
2. Abra o instalador e siga as instruções
3. Após instalar, **abra um terminal novo** e execute:

```bash
ollama run llama3.2:3b
```

**⚠️ IMPORTANTE:** Este terminal deve **FICAR ABERTO** enquanto você usa o Jarvis!

---

### 2️⃣ DEPENDÊNCIAS PYTHON (Já estão prontas!)

Execute este comando **UMA VEZ** (já fizemos para você):

```bash
# Vá para a pasta do projeto
cd c:\Users\joaoe\OneDrive\Área de Trabalho\programação\jarvis_projeto

# Ative o ambiente virtual
venv\Scripts\activate

# Instale tudo
pip install setuptools
pip install -r requirements.txt
```

**Se der erro**, tente:

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir
```

---

## Requisitos de Hardware

| Item | Mínimo | Recomendado |
|------|--------|-------------|
| **RAM** | 4 GB | 8 GB |
| **Disco** | 5 GB livres | 10 GB livres |
| **Processador** | Qualquer um | Atual |
| **GPU** | Não precisa | Nvidia/AMD (opcional) |

---

## Checklist Antes de Rodar

- [ ] Ollama instalado?
- [ ] Terminal do Ollama aberto (`ollama run llama3.2:3b`)?
- [ ] venv ativado (`venv\Scripts\activate`)?
- [ ] Dependências instaladas (`pip install -r requirements.txt`)?
- [ ] Microfone do computador conectado?
- [ ] Volume do computador ligado?

---

## Como Rodar o Jarvis

### Terminal 1: Ativar Ambiente

```bash
cd c:\Users\joaoe\OneDrive\Área de Trabalho\programação\jarvis_projeto
venv\Scripts\activate
```

### Terminal 2: Rodar Ollama (Deixar aberto!)

```bash
ollama run llama3.2:3b
```

### Terminal 3: Rodar Jarvis

```bash
python main.py
```

---

## Arquitetura - O Que Está Instalado

```
Jarvis
├── Python 3.x (Linguagem de programação)
├── pyttsx3 (Fala - converte texto em voz)
├── SpeechRecognition (Ouve - converte voz em texto)
├── customtkinter (Interface - tela bonita)
├── requests (Comunica com Ollama)
├── psutil (Info do sistema)
├── keyboard (Controla teclado)
├── pyautogui (Controla mouse)
└── Ollama (IA Local)
    └── llama3.2:3b (Modelo de IA)
```

---

## Tamanho das Instalações

| Componente | Tamanho |
|-----------|---------|
| Python + venv | ~500 MB |
| Dependências | ~300 MB |
| Ollama | ~2 GB |
| Modelo llama3.2:3b | ~2 GB |
| **TOTAL** | **~4.8 GB** |

---

## Pronto! Agora...

### Teste Rápido

Diga esses comandos para o Jarvis:

```
"jarvis olá"
"jarvis abre spotify"
"jarvis qual é sua cor favorita?"
"jarvis encerrar"
```

### Se Algo Não Funcionar

| Problema | Solução |
|----------|---------|
| "Não consegui conectar ao Ollama" | Verifique se `ollama run llama3.2:3b` está rodando |
| "Não entendi o que você disse" | Fale mais devagar e claro |
| Sem som | Verifique volume do Windows |
| Sem reconhecimento | Teste microfone nas configurações do Windows |
| ImportError | Reinstale: `pip install -r requirements.txt` |

---

## 📚 Arquivos Importantes

- **main.py** - Arquivo principal (execute este!)
- **config.py** - Configurações do Jarvis
- **requirements.txt** - Lista de dependências
- **core/** - Cérebro do Jarvis
- **services/** - Integrações (Ollama, apps)
- **ui/** - Interface gráfica

---

## 🎯 Próximos Passos

Quando tudo estiver funcionando:

1. Customize `config.py` (velocidade de voz, wake word, etc)
2. Adicione mais comandos em `core/brain.py`
3. Explore o arquivo `ROADMAP.md` para melhorias

---

## 💡 Dicas Importantes

- ✅ Use 3 terminais simultaneamente (venv + Ollama + Jarvis)
- ✅ Deixe Ollama sempre aberto
- ✅ Se vir erro de distutils → instale `pip install setuptools`
- ✅ Se PyAudio falhar → tente `pip install pyaudio==0.2.14`
- ✅ Ctrl+C para parar o Jarvis

---

## 📞 Resumo Rápido

```bash
# TERMINAL 1
cd c:\Users\joaoe\OneDrive\Área de Trabalho\programação\jarvis_projeto
venv\Scripts\activate

# TERMINAL 2
ollama run llama3.2:3b

# TERMINAL 3
python main.py
```

**Pronto! Seu assistente de IA pessoal está rodando! 🎉**

---

**Dúvidas? Veja os outros arquivos:**
- **QUICK_START.md** - Início rápido
- **README.md** - Documentação completa
- **ARCHITECTURE.md** - Como funciona por dentro
- **ROADMAP.md** - Futuros recursos
