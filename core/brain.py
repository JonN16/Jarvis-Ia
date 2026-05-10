"""
Brain module - Contains core AI processing logic
"""

import re
import webbrowser
import pyautogui
from services.app_finder import abrir_app
from services.spotify_service import controlar_spotify, buscar_musica
from services.obsidian_service import (
    criar_nota, buscar_notas, abrir_nota,
    aprender_informacao, buscar_aprendizado,
    lembrar_preferencia, salvar_preferencia
)
from services.system_service import controlar_sistema


# ------------------------------------------------------------------
# Gatilhos de memória — qualquer frase que signifique "salve isso"
# ------------------------------------------------------------------
_GATILHOS_MEMORIA = [
    # variantes de "lembrar"
    "lembre-se que", "lembre-se de que",
    "lembre que", "lembre de que",
    "lembra que", "lembra-se que",
    "quero que lembre", "quero que você lembre",
    "preciso que lembre", "preciso que você lembre",
    "pode lembrar que", "pode se lembrar que",
    # variantes de "guardar / anotar / salvar"
    "quero que guarde", "quero que você guarde",
    "quero que anote", "quero que você anote",
    "quero que saiba", "quero que você saiba",
    "pode anotar que", "pode guardar que",
    "anota que", "anote que",
    "guarda que", "guarde que",
    "salva que", "salve que", "salvar que",
    # variantes de "aprender / decorar / memorizar"
    "aprenda que", "aprende que",
    "decora que", "decore que",
    "memorize que", "memoriza que",
    # negação
    "não esqueça que", "nao esqueca que",
    "não se esqueça que", "nao se esqueca que",
]

# Mapeamento palavra-chave → categoria no Obsidian
_CATEGORIAS = {
    "estud":        "estudo",
    "faculdade":    "estudo",
    "universidade": "estudo",
    "usp":          "estudo",
    "curso":        "estudo",
    "engenharia":   "estudo",
    "computação":   "estudo",
    "trabalh":      "trabalho",
    "emprego":      "trabalho",
    "empresa":      "trabalho",
    "mor":          "moradia",
    "cidade":       "moradia",
    "gost":         "preferencia",
    "prefer":       "preferencia",
    "favorit":      "preferencia",
    "odi":          "preferencia",
    "chamo":        "perfil",
    "nome":         "perfil",
    "idade":        "perfil",
    "anos":         "perfil",
    "nasc":         "perfil",
}


def _detectar_gatilho_memoria(comando_lower: str):
    """
    Verifica se o comando contém algum gatilho de memória.
    Retorna (gatilho, posição) ou (None, -1).
    """
    for gatilho in sorted(_GATILHOS_MEMORIA, key=len, reverse=True):  # mais longo primeiro
        if gatilho in comando_lower:
            return gatilho, comando_lower.find(gatilho)
    return None, -1


def _detectar_categoria(comando_lower: str) -> str:
    for palavra_chave, categoria in _CATEGORIAS.items():
        if palavra_chave in comando_lower:
            return categoria
    return "geral"


def extrair_informacao_aprendizado(comando: str):
    """
    Tenta extrair o conteúdo a salvar de qualquer frase de memória.
    Retorna (categoria, conteudo) ou None.
    """
    cmd_lower = comando.lower()
    gatilho, pos = _detectar_gatilho_memoria(cmd_lower)

    if not gatilho:
        return None

    # Pega tudo que vem depois do gatilho
    conteudo = comando[pos + len(gatilho):].strip().rstrip(".,!?")

    if not conteudo or len(conteudo) < 3:
        return None

    categoria = _detectar_categoria(cmd_lower)
    return categoria, conteudo


# ------------------------------------------------------------------
# Extratores auxiliares
# ------------------------------------------------------------------

def extrair_musica(comando):
    triggers = ["música", "musica", "tocar", "play", "colocar", "botar", "abrir"]
    comando_lower = comando.lower()
    for trigger in triggers:
        if trigger in comando_lower:
            pos = comando_lower.find(trigger)
            depois = comando_lower[pos + len(trigger):].strip()
            depois = depois.replace("spotify", "").replace("jarvis", "").replace("no ", "").strip()
            palavras_remover = [
                "e ", "ou ", "a ", "o ", "de ", "da ", "do ", "das ", "dos ",
                "uma ", "um ", "na ", "no ", "em ", "para ", "por "
            ]
            mudou = True
            while mudou:
                mudou = False
                for palavra in palavras_remover:
                    if depois.startswith(palavra):
                        depois = depois[len(palavra):].strip()
                        mudou = True
                        break
            if depois and len(depois) > 2:
                return depois
    return None


def extrair_acao_spotify(comando):
    comando_lower = comando.lower()
    if any(w in comando_lower for w in ["pausar", "pause", "parar"]):
        return "pause", None
    if any(w in comando_lower for w in ["retomar", "continuar", "dar play", "iniciar", "despausar"]):
        return "resume", None
    if any(w in comando_lower for w in ["próxima", "proximo", "pular", "avançar", "next"]):
        return "next", None
    if any(w in comando_lower for w in ["anterior", "voltar", "previous"]):
        return "previous", None
    if "volume" in comando_lower:
        numeros = re.findall(r'\d+', comando_lower)
        return "volume", numeros[0] if numeros else None
    if any(w in comando_lower for w in ["fila", "queue", "adicionar"]):
        return "queue", extrair_musica(comando)
    if any(w in comando_lower for w in ["tocando", "atual", "agora", "música atual"]):
        return "current", None
    return None, None


def extrair_titulo_nota(comando):
    comando_lower = comando.lower()
    for trigger in ["criar nota", "nova nota", "criar", "fazer nota"]:
        if trigger in comando_lower:
            pos = comando_lower.find(trigger)
            depois = comando_lower[pos + len(trigger):].strip()
            for palavra in ["a ", "o ", "uma ", "um ", "de ", "do ", "da ", "sobre ", "no ", "na ", "para "]:
                if depois.startswith(palavra):
                    depois = depois[len(palavra):].strip()
            depois = depois.replace("obsidian", "").replace("jarvis", "").strip()
            if depois and len(depois) > 2:
                return depois.title()
    return None


def extrair_termo_busca(comando):
    comando_lower = comando.lower()
    for trigger in ["buscar", "procurar", "achar", "abrir nota"]:
        if trigger in comando_lower:
            pos = comando_lower.find(trigger)
            depois = comando_lower[pos + len(trigger):].strip()
            for palavra in ["por ", "a ", "o ", "uma ", "um ", "de ", "do ", "da ", "sobre ", "no ", "na "]:
                if depois.startswith(palavra):
                    depois = depois[len(palavra):].strip()
            depois = depois.replace("obsidian", "").replace("jarvis", "").replace("notas", "").strip()
            if depois and len(depois) > 1:
                return depois
    return None


def extrair_informacao_padrao(comando):
    """Detecta padrões como 'X chama Y' ou 'X é Y'"""
    cmd = comando.lower().replace("jarvis", "").strip()
    if " chama " in cmd:
        partes = cmd.split(" chama ", 1)
        if len(partes) == 2 and len(partes[1].strip()) > 1:
            return f"{partes[0].strip()} é {partes[1].strip()}"
    if " se chama " in cmd:
        partes = cmd.split(" se chama ", 1)
        if len(partes) == 2 and len(partes[1].strip()) > 1:
            return f"{partes[0].strip()} é {partes[1].strip()}"
    if " é " in cmd:
        perguntas = ("quem é", "o que é", "como é", "quando é", "onde é", "por que é")
        if not any(cmd.startswith(p) for p in perguntas):
            partes = cmd.split(" é ", 1)
            if len(partes) == 2 and len(partes[1].strip()) > 1:
                sujeito = partes[0].strip().lstrip("o ").lstrip("a ").lstrip("um ").lstrip("uma ")
                predicado = partes[1].strip()
                if sujeito and predicado:
                    return f"{sujeito} é {predicado}"
    return None


def extrair_termo_aprendizado(comando):
    comando_lower = comando.lower()
    for trigger in ["o que você sabe sobre", "me fale sobre", "o que você lembra de", "o que você aprendeu sobre"]:
        if trigger in comando_lower:
            pos = comando_lower.find(trigger)
            depois = comando_lower[pos + len(trigger):].strip()
            depois = depois.replace("jarvis", "").strip()
            for palavra in ["o ", "a ", "os ", "as ", "um ", "uma "]:
                if depois.startswith(palavra):
                    depois = depois[len(palavra):].strip()
            if depois and len(depois) > 1:
                return depois
    return None


def extrair_nome(comando):
    comando_lower = comando.lower()
    for trigger in ["meu nome é", "me chamo", "eu sou"]:
        if trigger in comando_lower:
            pos = comando_lower.find(trigger)
            depois = comando_lower[pos + len(trigger):].strip()
            depois = depois.replace("jarvis", "").strip()
            nome = depois.split(',')[0].split('.')[0].strip()
            if nome and len(nome) > 1:
                return nome.title()
    return None


def extrair_palavras_chave(comando):
    irrelevantes = {
        "como", "quando", "onde", "por", "que", "qual", "quem", "o", "a", "os", "as",
        "um", "uma", "de", "do", "da", "dos", "das", "em", "para", "com", "sem",
        "eu", "você", "me", "te", "se", "nos", "vos", "lhe", "lhes",
        "é", "são", "foi", "foram", "ser", "estar", "ter", "haver",
        "isso", "isto", "aquilo", "tudo", "nada", "algo",
        "mais", "menos", "muito", "pouco", "tanto", "quanto",
        "meu", "minha", "meus", "minhas", "seu", "sua", "seus", "suas",
        "jarvis",
    }
    limpo = re.sub(r'[^\w\s]', '', comando.lower())
    return [p for p in limpo.split() if len(p) > 2 and p not in irrelevantes][:5]


def extrair_site(comando):
    comando_lower = comando.lower()
    for trigger in ["entrar no site", "abrir site", "entrar site", "acessar site", "site"]:
        if trigger in comando_lower:
            pos = comando_lower.find(trigger)
            depois = comando_lower[pos + len(trigger):].strip()
            for palavra in ["o ", "a ", "os ", "as ", "um ", "uma ", "de ", "do ", "da "]:
                if depois.startswith(palavra):
                    depois = depois[len(palavra):].strip()
            depois = depois.replace("jarvis", "").strip()
            if depois and len(depois) > 1:
                return depois
    return None


def montar_url(site):
    sites_conhecidos = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
        "gitlab": "https://gitlab.com",
        "stackoverflow": "https://stackoverflow.com",
        "reddit": "https://www.reddit.com",
        "twitter": "https://twitter.com",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "linkedin": "https://www.linkedin.com",
        "netflix": "https://www.netflix.com",
        "amazon": "https://www.amazon.com.br",
        "mercadolivre": "https://www.mercadolivre.com.br",
        "g1": "https://g1.globo.com",
        "uol": "https://www.uol.com.br",
        "chatgpt": "https://chat.openai.com",
        "chat gpt": "https://chat.openai.com",
        "gpt": "https://chat.openai.com",
        "claude": "https://claude.ai",
        "bing": "https://www.bing.com",
        "yahoo": "https://br.yahoo.com",
        "twitch": "https://www.twitch.tv",
        "discord": "https://discord.com",
        "telegram": "https://web.telegram.org",
        "whatsapp": "https://web.whatsapp.com",
        "spotify": "https://open.spotify.com",
        "deezer": "https://www.deezer.com",
        "soundcloud": "https://soundcloud.com",
    }
    site_lower = site.lower().strip()
    if site_lower.startswith(("http://", "https://", "www.")):
        return site_lower if site_lower.startswith("http") else "https://" + site_lower
    for nome, url in sites_conhecidos.items():
        if nome in site_lower:
            return url
    site_limpo = re.sub(r'[^a-z0-9]', '', site_lower)
    return f"https://www.{site_limpo}.com"


# ------------------------------------------------------------------
# Contexto do Obsidian para a IA
# ------------------------------------------------------------------

def obter_contexto_obsidian(comando):
    comando_lower = comando.lower()

    # Perguntas sobre o próprio usuário → carrega TUDO que foi aprendido
    _GATILHOS_SOBRE_MIM = [
        "o que você sabe sobre mim", "o que você já sabe sobre mim",
        "o que você lembra de mim", "o que você já lembra de mim",
        "o que você aprendeu sobre mim", "o que você já aprendeu sobre mim",
        "o que sabe sobre mim", "o que lembra de mim",
        "me conta o que sabe", "me fala o que sabe",
        "quem sou eu", "o que você sabe de mim",
        "me descreva", "o que você conhece sobre mim",
    ]
    if any(g in comando_lower for g in _GATILHOS_SOBRE_MIM):
        tudo = buscar_aprendizado()  # sem filtro = retorna tudo
        if not tudo:
            return None
        contexto = "Tudo que aprendi sobre o usuário:\n"
        for info in tudo:
            contexto += f"- {info}\n"
        return contexto

    # Busca normal por palavras-chave
    palavras_chave = extrair_palavras_chave(comando)
    if not palavras_chave:
        return None

    infos = []
    for palavra in palavras_chave[:3]:
        for r in buscar_aprendizado(termo=palavra):
            if r not in infos:
                infos.append(r)

    if len(palavras_chave) >= 2:
        for r in buscar_aprendizado(termo=" ".join(palavras_chave[:2])):
            if r not in infos:
                infos.append(r)

    if not infos:
        return None

    contexto = "Informações relevantes que aprendi anteriormente:\n"
    for info in infos[:5]:
        contexto += f"- {info}\n"
    return contexto


# ------------------------------------------------------------------
# Processador principal
# ------------------------------------------------------------------

def processar_comando(comando):
    """
    Processa o comando antes de enviar à IA.
    Retorna um dict de resultado ou None (para a IA processar).
    """
    comando_lower = comando.lower()

    # ── 1. MEMÓRIA — gatilhos amplos ─────────────────────────────────
    resultado_memoria = extrair_informacao_aprendizado(comando)
    if resultado_memoria:
        categoria, conteudo = resultado_memoria
        aprender_informacao(categoria, conteudo)
        print(f"[Obsidian] ✅ Salvo em '{categoria}': {conteudo}")
        return {"acao": "falar", "parametro": "", "resposta": f"Anotado. Vou lembrar que {conteudo}."}

    # ── 2. PADRÃO "X chama Y" / "X é Y" ─────────────────────────────
    # Ignora se o comando tem palavras de ação (música, spotify, abrir, etc.)
    _PALAVRAS_ACAO = ["spotify", "música", "musica", "tocar", "play", "colocar",
                      "abrir", "abre", "chrome", "discord", "vscode", "site",
                      "volume", "brilho", "screenshot", "desligar", "reiniciar"]
    _tem_acao = any(p in comando_lower for p in _PALAVRAS_ACAO)

    if not _tem_acao and any(w in comando_lower for w in ["chama", " é ", "se chama"]):
        info = extrair_informacao_padrao(comando)
        if info:
            aprender_informacao("fatos", info)
            print(f"[Obsidian] ✅ Fato salvo: {info}")
            return {"acao": "falar", "parametro": "", "resposta": f"Aprendi que {info}"}

    # ── 3. NOME DO USUÁRIO ────────────────────────────────────────────
    if any(w in comando_lower for w in ["meu nome é", "me chamo", "eu sou"]):
        nome = extrair_nome(comando)
        if nome:
            salvar_preferencia("usuario", "nome", nome)
            return {"acao": "falar", "parametro": "", "resposta": f"Prazer, {nome}! Vou lembrar seu nome."}

    # ── 4. TUDO QUE SEI SOBRE O USUÁRIO ──────────────────────────────
    _GATILHOS_SOBRE_MIM = [
        "o que você sabe sobre mim", "o que você já sabe sobre mim",
        "o que você lembra de mim", "o que você já lembra de mim",
        "o que você aprendeu sobre mim", "o que você já aprendeu sobre mim",
        "o que sabe sobre mim", "o que lembra de mim",
        "me conta o que sabe", "me fala o que sabe",
        "o que você sabe de mim", "me descreva",
        "o que você conhece sobre mim",
    ]
    if any(g in comando_lower for g in _GATILHOS_SOBRE_MIM):
        tudo = buscar_aprendizado()
        if tudo:
            resposta = "Aqui está tudo que sei sobre você: " + "; ".join(tudo)
        else:
            resposta = "Ainda não aprendi nada sobre você. Me conte algo!"
        return {"acao": "falar", "parametro": "", "resposta": resposta}

    # ── 5. CONSULTAR O QUE APRENDEU SOBRE UM TEMA ────────────────────
    if any(w in comando_lower for w in ["o que você sabe sobre", "me fale sobre", "o que você lembra de", "o que você aprendeu sobre"]):
        termo = extrair_termo_aprendizado(comando)
        if termo:
            resultados = buscar_aprendizado(termo=termo)
            if resultados:
                return {"acao": "falar", "parametro": "", "resposta": f"Sei que: {'; '.join(resultados[:3])}"}
            return {"acao": "falar", "parametro": "", "resposta": f"Não tenho informações sobre '{termo}'"}

    # ── 6. CONSULTAR PREFERÊNCIAS ─────────────────────────────────────
    if any(w in comando_lower for w in ["quem sou eu", "qual meu nome", "o que eu gosto", "meu favorito", "minha preferência"]):
        preferencias = lembrar_preferencia("usuario")
        if preferencias:
            infos = [f"{k}: {v}" for k, v in preferencias.items()]
            return {"acao": "falar", "parametro": "", "resposta": f"Lembro que: {', '.join(infos)}"}

    # ── 6. SPOTIFY ────────────────────────────────────────────────────
    if "spotify" in comando_lower:
        acao, parametro = extrair_acao_spotify(comando)
        if acao:
            resultado = controlar_spotify(acao, parametro)
            return {"acao": "falar", "parametro": "", "resposta": resultado["mensagem"]}
        # Músicas curtidas
        if any(w in comando_lower for w in ["curtidas", "favoritas", "favoritos", "liked", "curtidos", "que eu curti", "que curtei"]):
            resultado = controlar_spotify("liked")
            return {"acao": "falar", "parametro": "", "resposta": resultado["mensagem"]}

        # Playlist específica
        if any(w in comando_lower for w in ["playlist", "lista de reprodução", "lista de musicas"]):
            # Extrai nome da playlist
            nome_playlist = None
            for trigger in ["playlist", "lista de reprodução", "lista de musicas"]:
                if trigger in comando_lower:
                    pos = comando_lower.find(trigger)
                    depois = comando_lower[pos + len(trigger):].strip()
                    for rem in ["no spotify", "do spotify", "spotify", "a ", "o ", "de ", "da ", "do "]:
                        depois = depois.replace(rem, "").strip()
                    if depois and len(depois) > 1:
                        nome_playlist = depois
                    break
            if nome_playlist:
                resultado = controlar_spotify("playlist", nome_playlist)
            else:
                resultado = controlar_spotify("liked")  # sem nome = curtidas
            return {"acao": "falar", "parametro": "", "resposta": resultado["mensagem"]}
        if any(w in comando_lower for w in ["música", "musica", "tocar", "play", "colocar", "botar"]):
            musica = extrair_musica(comando)
            if musica:
                resultado = buscar_musica(musica)
                return {"acao": "falar", "parametro": "", "resposta": resultado["mensagem"]}
        abrir_app("spotify")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Spotify"}

    # ── 7. SITES ──────────────────────────────────────────────────────
    if any(w in comando_lower for w in ["entrar no site", "abrir site", "entrar site", "acessar site"]):
        site = extrair_site(comando)
        if site:
            webbrowser.open(montar_url(site))
            return {"acao": "falar", "parametro": "", "resposta": f"Abrindo {site}"}

    # ── 8. CONTROLES DE MÍDIA ─────────────────────────────────────────
    if any(w in comando_lower for w in ["pausar música", "pausar tudo", "pause a música"]):
        pyautogui.press('playpause')
        return {"acao": "falar", "parametro": "", "resposta": "Reprodução pausada"}
    if any(w in comando_lower for w in ["retomar música", "continuar música", "dar play"]):
        pyautogui.press('playpause')
        return {"acao": "falar", "parametro": "", "resposta": "Reprodução retomada"}
    if any(w in comando_lower for w in ["próxima música", "pular música", "avançar música"]):
        pyautogui.press('nexttrack')
        return {"acao": "falar", "parametro": "", "resposta": "Próxima música"}
    if any(w in comando_lower for w in ["música anterior", "voltar música"]):
        pyautogui.press('prevtrack')
        return {"acao": "falar", "parametro": "", "resposta": "Música anterior"}

    # ── 9. APLICATIVOS ────────────────────────────────────────────────
    if "discord" in comando_lower:
        abrir_app("discord")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Discord"}
    if any(w in comando_lower for w in ["chrome", "navegador", "browser"]):
        abrir_app("chrome")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Chrome"}
    if any(w in comando_lower for w in ["vscode", "visual studio", "code"]):
        abrir_app("vscode")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Visual Studio Code"}
    if any(w in comando_lower for w in ["calc", "calculadora"]):
        abrir_app("calculator")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Calculadora"}
    if any(w in comando_lower for w in ["notepad", "bloco de notas"]):
        abrir_app("notepad")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Notepad"}
    if any(w in comando_lower for w in ["explorer", "arquivos", "files"]):
        abrir_app("explorer")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Explorador de Arquivos"}
    if any(w in comando_lower for w in ["paint", "pintura"]):
        abrir_app("paint")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Paint"}
    if any(w in comando_lower for w in ["league", "lol", "tft"]):
        abrir_app("lol")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo League of Legends"}

    # ── 10. OBSIDIAN ──────────────────────────────────────────────────
    if "obsidian" in comando_lower:
        if any(w in comando_lower for w in ["abrir", "iniciar", "entrar"]):
            abrir_app("obsidian")
            return {"acao": "falar", "parametro": "", "resposta": "Abrindo Obsidian"}
        if any(w in comando_lower for w in ["nova nota", "criar nota", "criar"]):
            titulo = extrair_titulo_nota(comando)
            if titulo:
                sucesso, msg = criar_nota(titulo)
                if sucesso:
                    abrir_app("obsidian")
                    return {"acao": "falar", "parametro": "", "resposta": f"Nota '{titulo}' criada!"}
                return {"acao": "falar", "parametro": "", "resposta": msg}
            abrir_app("obsidian")
            return {"acao": "falar", "parametro": "", "resposta": "Abrindo Obsidian para criar nova nota"}
        if any(w in comando_lower for w in ["buscar", "procurar", "achar", "abrir nota"]):
            termo = extrair_termo_busca(comando)
            if termo:
                resultados = buscar_notas(termo)
                qtd = len(resultados)
                msg = f"Encontradas {qtd} nota(s) sobre '{termo}'" if qtd else f"Nenhuma nota encontrada sobre '{termo}'"
                return {"acao": "falar", "parametro": "", "resposta": msg}
        abrir_app("obsidian")
        return {"acao": "falar", "parametro": "", "resposta": "Abrindo Obsidian"}

    # ── 11. COMANDOS DE SISTEMA ──────────────────────────────────────

    # Screenshot — ANTES do brilho para "tela" não conflitar
    _gatilhos_screenshot = [
        "screenshot", "captura de tela", "printscreen",
        "tire um print", "tira um print", "tire o print", "tira o print",
        "tirar print", "tirar um print", "fazer print", "faz um print",
        "foto da tela", "tire uma foto da tela", "tira uma foto da tela",
        "fotografar a tela", "capturar tela", "capturar a tela",
    ]
    if any(g in comando_lower for g in _gatilhos_screenshot):
        r = controlar_sistema("screenshot")
        return {"acao": "falar", "parametro": "", "resposta": r["mensagem"]}

    # Volume
    if "volume" in comando_lower:
        numeros = re.findall(r"\d+", comando_lower)
        # "para X%", "em X%", "para X", "em X" → sempre DEFINIR, independente de "aumentar"
        _define_forcado = any(p in comando_lower for p in ["para ", "em ", "coloca", "deixa", "definir", "definir para", "vai para"])
        if any(w in comando_lower for w in ["mutar", "mudo", "silencio", "silêncio", "sem som"]):
            r = controlar_sistema("volume_mutar")
        elif any(w in comando_lower for w in ["qual", "quanto", "ver", "status", "atual"]):
            r = controlar_sistema("volume_obter")
        elif numeros and _define_forcado:
            # "aumentar volume para 80%" → definir para 80, não somar 80
            r = controlar_sistema("volume_definir", numeros[0])
        elif numeros:
            if any(w in comando_lower for w in ["aumentar", "subir", "mais alto", "sobe", "aumenta"]):
                r = controlar_sistema("volume_aumentar", numeros[0])
            elif any(w in comando_lower for w in ["diminuir", "baixar", "mais baixo", "desce", "diminui"]):
                r = controlar_sistema("volume_diminuir", numeros[0])
            else:
                r = controlar_sistema("volume_definir", numeros[0])
        elif any(w in comando_lower for w in ["aumentar", "subir", "mais alto", "sobe", "aumenta"]):
            r = controlar_sistema("volume_aumentar", None)
        elif any(w in comando_lower for w in ["diminuir", "baixar", "mais baixo", "desce", "diminui"]):
            r = controlar_sistema("volume_diminuir", None)
        else:
            r = controlar_sistema("volume_obter")
        return {"acao": "falar", "parametro": "", "resposta": r["mensagem"]}

    # Brilho — "tela" só aqui, nunca confunde com screenshot
    if any(w in comando_lower for w in ["brilho", "iluminacao", "iluminação"]):
        numeros = re.findall(r"\d+", comando_lower)
        if numeros:
            if any(w in comando_lower for w in ["aumentar", "mais", "subir", "sobe"]):
                r = controlar_sistema("brilho_aumentar", numeros[0])
            elif any(w in comando_lower for w in ["diminuir", "baixar", "menos", "desce"]):
                r = controlar_sistema("brilho_diminuir", numeros[0])
            else:
                r = controlar_sistema("brilho_definir", numeros[0])
        elif any(w in comando_lower for w in ["aumentar", "mais", "subir", "sobe", "aumenta"]):
            r = controlar_sistema("brilho_aumentar", None)
        elif any(w in comando_lower for w in ["diminuir", "baixar", "menos", "desce", "diminui"]):
            r = controlar_sistema("brilho_diminuir", None)
        else:
            r = controlar_sistema("brilho_obter")
        return {"acao": "falar", "parametro": "", "resposta": r["mensagem"]}



    # Hora e data

    if any(w in comando_lower for w in ["que horas", "qual hora", "que dia", "qual data", "que dia é hoje", "data de hoje"]):

        r = controlar_sistema("hora_data")

        return {"acao": "falar", "parametro": "", "resposta": r["mensagem"]}



    # Info do sistema

    if any(w in comando_lower for w in ["como está o sistema", "status do sistema", "uso da cpu", "uso de memória", "uso de memoria", "bateria"]):

        r = controlar_sistema("info_sistema")

        return {"acao": "falar", "parametro": "", "resposta": r["mensagem"]}



    # Desligar

    if any(w in comando_lower for w in ["desligar o computador", "desligar pc", "desligue o pc", "desligue o computador"]):

        numeros = re.findall(r"\d+", comando_lower)

        delay = numeros[0] if numeros else 10

        r = controlar_sistema("desligar", delay)

        return {"acao": "falar", "parametro": "", "resposta": r["mensagem"]}



    # Reiniciar

    if any(w in comando_lower for w in ["reiniciar o computador", "reiniciar pc", "reinicie o pc", "reiniciar sistema"]):

        r = controlar_sistema("reiniciar")

        return {"acao": "falar", "parametro": "", "resposta": r["mensagem"]}



    # Cancelar desligamento

    if any(w in comando_lower for w in ["cancelar desligamento", "cancela o desligamento", "não desligue", "nao desligue"]):

        r = controlar_sistema("cancelar_desligamento")

        return {"acao": "falar", "parametro": "", "resposta": r["mensagem"]}



    # Suspender

    if any(w in comando_lower for w in ["suspender", "modo sleep", "dormir", "hibernar"]):

        r = controlar_sistema("suspender")

        return {"acao": "falar", "parametro": "", "resposta": r["mensagem"]}



    # Bloquear tela

    if any(w in comando_lower for w in ["bloquear tela", "bloquear pc", "bloquear", "travar tela"]):

        r = controlar_sistema("bloquear")

        return {"acao": "falar", "parametro": "", "resposta": r["mensagem"]}



    # ── 11. ENCERRAR ──────────────────────────────────────────────────
    if any(w in comando_lower for w in ["encerrar", "desligar", "goodbye"]):
        return {"acao": "encerrar", "parametro": "", "resposta": ""}

    # Nenhum comando rápido detectado → vai para a IA
    return None


# ------------------------------------------------------------------
# Teste local
# ------------------------------------------------------------------
def testar_extracao():
    testes = [
        "eu quero que lembre que eu estudo na USP de São Carlos faço engenharia da computação",
        "lembre-se que eu gosto de pizza",
        "quero que você guarde que moro em São Paulo",
        "preciso que lembre que trabalho na Google",
        "lembra que meu nome é Leonardo",
        "tocar música no spotify metallica enter sandman",
    ]
    print("=" * 55)
    print("  Teste de Extração")
    print("=" * 55)
    for cmd in testes:
        r = extrair_informacao_aprendizado(cmd)
        musica = extrair_musica(cmd)
        print(f"\nComando : {cmd}")
        print(f"Memória : {r}")
        print(f"Música  : {musica}")


if __name__ == "__main__":
    testar_extracao()