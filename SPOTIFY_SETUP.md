# 🎵 Configuração do Spotify - Integração Profissional

## Visão Geral

O Jarvis agora possui integração profissional com o Spotify usando a API oficial via biblioteca **Spotipy**. Isso permite controle total:
- ✅ Tocar músicas específicas
- ✅ Pausar/retomar reprodução
- ✅ Pular músicas
- ✅ Controlar volume
- ✅ Adicionar à fila
- ✅ Ver música atual

## 📋 Pré-requisitos

1. **Conta Spotify** (gratuita ou premium)
2. **Criar um App no Spotify Developer Dashboard**

## 🚀 Passo a Passo

### 1. Criar App no Spotify Developer

1. Acesse: https://developer.spotify.com/dashboard
2. Faça login com sua conta Spotify
3. Clique em **"Create App"** ou **"Crear una aplicación"**
4. Preencha os dados:
   - **App name**: `Jarvis AI Assistant`
   - **App description**: `Assistente de voz com controle do Spotify`
   - **What are you building?**: Selecione qualquer opção
   - **Redirect URI**: `http://localhost:8888/callback`
   - **Website**: (deixe em branco)
5. Marque a caixa de termos e clique em **"Save"**

### 2. Obter Credenciais

1. Na página do seu app, clique em **"Settings"**
2. Copie as seguintes informações:
   - **Client ID**
   - **Client Secret** (clique em "Show client secret")

### 3. Configurar Arquivo .env

1. Abra o arquivo `.env` na pasta do projeto
2. Substitua os valores:

```env
# Antes:
SPOTIFY_CLIENT_ID=seu_client_id_aqui
SPOTIFY_CLIENT_SECRET=seu_client_secret_aqui

# Depois (exemplo):
SPOTIFY_CLIENT_ID=abc123def456ghi789
SPOTIFY_CLIENT_SECRET=xyz987uvw654rst321
```

### 4. Instalar Dependências

```bash
# Ative o ambiente virtual
venv\Scripts\activate

# Instale as novas dependências
pip install spotipy python-dotenv
```

### 5. Autenticação Inicial (Uma Única Vez)

Execute este comando no terminal:

```bash
python -c "from services.spotify_service import get_spotify_service; get_spotify_service()"
```

**O que vai acontecer:**
1. O terminal mostrará uma URL
2. Copie e cole no navegador
3. Faça login no Spotify (se necessário)
4. Autorize o aplicativo
5. Você será redirecionado para `http://localhost:8888/callback?code=...`
6. Copie toda a URL e cole no terminal
7. Pressione Enter

**Pronto!** O token será salvo em `.spotify_cache` e reutilizado automaticamente.

## 🎤 Comandos de Voz Disponíveis

### Tocar Músicas
```
"jarvis spotify tocar música crônicas de um babaca"
"jarvis spotify tocar quarta cadeira"
"jarvis spotify colocar música angra"
```

### Controles de Reprodução
```
"jarvis spotify pausar"
"jarvis spotify retomar"
"jarvis spotify próxima música"
"jarvis spotify música anterior"
```

### Volume
```
"jarvis spotify volume 50"
"jarvis spotify volume 80"
```

### Fila
```
"jarvis spotify adicionar à fila next track"
"jarvis spotify colocar na fila metallica"
```

### Informações
```
"jarvis spotify música atual"
"jarvis spotify o que está tocando"
```

## 🔧 Solução de Problemas

### Erro: "Spotify não conectado"
- Verifique se as credenciais no `.env` estão corretas
- Execute a autenticação inicial novamente

### Erro: "Nenhuma música encontrada"
- Tente usar nomes mais específicos
- Use nome do artista + música (ex: "matuê máquina do tempo")

### Erro: "No active device found"
- Abra o aplicativo do Spotify no computador
- Comece a reproduzir algo manualmente primeiro

### Erro: "403 - Restriction violated" ou "Conta gratuita"
⚠️ **Limitação do Spotify Gratuito**: A API do Spotify tem restrições para contas gratuitas.
- **O que funciona**: Buscar músicas, tocar músicas específicas, ver música atual
- **O que NÃO funciona**: Pausar, pular, voltar, controlar volume via API

**Solução para contas gratuitas**: Use os comandos de mídia gerais (sem "spotify"):
```
"jarvis pausar música"      # Pausa qualquer player
"jarvis próxima música"     # Pula para próxima
"jarvis música anterior"    # Volta para anterior
"jarvis dar play"           # Retoma reprodução
```

### Token expirado
- O token é renovado automaticamente
- Se persistir, delete o arquivo `.spotify_cache` e reautentique

## 📁 Arquivos Criados

- `.env` - Credenciais (NÃO compartilhe!)
- `.spotify_cache` - Token cache (automático)
- `services/spotify_service.py` - Serviço atualizado
- `SPOTIFY_SETUP.md` - Este guia

## 🔒 Segurança

- **NUNCA** compartilhe seu arquivo `.env`
- As credenciais ficam salvas localmente
- O token é armazenado em `.spotify_cache`
- O Jarvis só tem acesso às permissões que você autorizou

## 🎯 Próximos Passos

Agora que o Spotify está configurado, você pode:

1. **Testar os comandos** - Use os exemplos acima
2. **Personalizar** - Edite `core/brain.py` para adicionar mais comandos
3. **Integrar com IA** - O Ollama também pode controlar o Spotify
4. **Criar playlists** - Use a fila para organizar músicas

## 💡 Dicas

- Músicas em português funcionam melhor com nomes completos
- Para artistas internacionais, use o nome em inglês
- O volume vai de 0 a 100
- Você pode pedir para "adicionar à fila" sem pausar a música atual

---

**Dúvidas?** Consulte a documentação oficial do [Spotipy](https://spotipy.readthedocs.io/) ou do [Spotify Web API](https://developer.spotify.com/documentation/web-api/).

**Aproveite sua experiência musical com o Jarvis! 🎵**