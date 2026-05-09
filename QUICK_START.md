# 🚀 Jarvis - Guia Rápido de Inicialização

## PASSO 1: Instalar Dependências (2 minutos)

```bash
# Certifique-se de estar na pasta do projeto
cd c:\Users\joaoe\OneDrive\Área de Trabalho\programação\jarvis_projeto

# Ativar venv
venv\Scripts\activate

# Instalar
pip install -r requirements.txt
```

## PASSO 2: Iniciar Ollama (Abrir NOVO Terminal)

```bash
# Em um terminal NOVO e separado:
ollama run llama3.2:3b
```

**⚠️ DEIXE ESTE TERMINAL ABERTO ENQUANTO USA JARVIS**

## PASSO 3: Rodar Jarvis (Terceiro Terminal)

```bash
# Volta para a pasta do projeto
cd c:\Users\joaoe\OneDrive\Área de Trabalho\programação\jarvis_projeto

# Ativar venv (se já não estiver)
venv\Scripts\activate

# Rodar
python main.py
```

## 🎤 Testando Jarvis

Depois que aparecer `[Ready]`, diga os seguintes comandos:

### Comandos Rápidos (sem IA)
```
"jarvis abre spotify"
"jarvis abre chrome"
"jarvis abre discord"
"jarvis abre vscode"
"jarvis encerrar"
```

### Comandos com IA
```
"jarvis qual é sua cor favorita?"
"jarvis conte uma piada"
"jarvis qual é a capital da França?"
"jarvis me dê uma dica de produtividade"
```

## ✅ Checklist de Problemas

- [ ] Conseguiu instalar requirements.txt?
- [ ] Ollama está rodando em terminal separado?
- [ ] Microfone funciona?
- [ ] Consegue ouvir o Jarvis falar?
- [ ] Jarvis recebeu "jarvis" nos comandos?

## 🔧 Se Algo Quebrar

| Problema | Solução |
|----------|---------|
| "Não consegui conectar ao Ollama" | Abra novo terminal e rode `ollama run llama3.2:3b` |
| "Não entendi o que você disse" | Fale mais devagar e claro |
| ImportError (módulo não encontrado) | Execute `pip install -r requirements.txt` novamente |
| Sem som | Verifique volume do Windows |
| Sem reconhecimento de fala | Verifique microfone nas configurações do Windows |

## 📁 Estrutura do Projeto

```
jarvis_projeto/
├── main.py              ← EXECUTE ESTE ARQUIVO
├── config.py            ← Edite aqui para customizar
├── requirements.txt     ← Instale com pip
├── memory.json          ← Memória do assistente
├── README.md            ← Documentação completa
├── core/                ← Módulos principais
├── services/            ← Integrações externas
├── ui/                  ← Interface gráfica
└── assets/              ← Imagens, sons (futuros)
```

## 🎯 Próximas Melhorias

1. **Mais Comandos Rápidos** (edite `core/brain.py`)
   ```python
   if "seu_comando" in comando_lower:
       return {"acao": "falar", "resposta": "resposta aqui"}
   ```

2. **Mais Apps** (edite `config.py` - APPS dict)
   ```python
   "seu_app": "nome_executable"
   ```

3. **Customizar Voz** (edite `config.py`)
   ```python
   VOICE_RATE = 190  # Aumenta = mais rápido
   ```

## 💡 Dicas

- Use `CTRL+C` para parar o Jarvis a qualquer momento
- Mantenha 3 terminais abertos: venv + Ollama + Jarvis
- O Ollama consome bastante RAM (depende da máquina)
- Primeira execução do modelo é mais lenta
- Comandos rápidos NÃO usam IA (mais rápidos e eficientes)

## 📞 Suporte

Se tiver problemas:
1. Verifique o README.md completo
2. Veja o terminal para mensagens de erro
3. Certifique-se que Ollama está rodando
4. Restart do Ollama em caso de travamento

---

**Você agora tem um assistente de IA profissional funcionando! 🎉**

Sucesso! 🚀
