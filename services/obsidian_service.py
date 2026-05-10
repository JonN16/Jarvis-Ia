"""
Obsidian Service - Integração profissional com Obsidian
Criação, busca, edição e aprendizado de notas no vault
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path


# ------------------------------------------------------------------
# Configuração do Vault
# ------------------------------------------------------------------

_VAULT_PATH_CACHE = None

_VAULT_SEARCH_PATHS = [
    Path.home() / "Documents" / "Obsidian Vault",
    Path.home() / "OneDrive" / "Obsidian Vault",
    Path.home() / "Obsidian Vault",
    Path.home() / "Documents" / "Notas",
    Path.home() / "Desktop" / "Obsidian Vault",
]

# Pasta onde o Jarvis armazena seus aprendizados dentro do vault
_JARVIS_FOLDER = "_jarvis"


def get_vault_path() -> Path:
    """
    Retorna o caminho do vault do Obsidian.
    Procura nos locais mais comuns; usa o primeiro que existir.
    Pode ser sobrescrito pela variável de ambiente OBSIDIAN_VAULT_PATH.
    """
    global _VAULT_PATH_CACHE
    if _VAULT_PATH_CACHE:
        return _VAULT_PATH_CACHE

    # Variável de ambiente tem prioridade
    env_path = os.getenv("OBSIDIAN_VAULT_PATH")
    if env_path:
        _VAULT_PATH_CACHE = Path(env_path)
        return _VAULT_PATH_CACHE

    for path in _VAULT_SEARCH_PATHS:
        if path.exists():
            _VAULT_PATH_CACHE = path
            return _VAULT_PATH_CACHE

    # Fallback: cria o vault padrão
    _VAULT_PATH_CACHE = _VAULT_SEARCH_PATHS[0]
    return _VAULT_PATH_CACHE


def _sanitize_filename(titulo: str) -> str:
    """Remove caracteres inválidos para nome de arquivo"""
    return re.sub(r'[<>:"/\\|?*\n\r]', "", titulo).strip()


def _ensure_dir(path: Path):
    """Cria diretório se não existir"""
    path.mkdir(parents=True, exist_ok=True)


def _note_path(titulo: str, subfolder: str = "") -> Path:
    """Retorna o Path completo para uma nota"""
    vault = get_vault_path()
    base = vault / subfolder if subfolder else vault
    return base / (_sanitize_filename(titulo) + ".md")


def _format_timestamp() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M")


# ------------------------------------------------------------------
# CRUD de Notas
# ------------------------------------------------------------------

def criar_nota(titulo: str, conteudo: str = "", tags: list = None, pasta: str = "") -> tuple:
    """
    Cria uma nova nota no vault.

    Args:
        titulo:   Título da nota
        conteudo: Corpo da nota (Markdown)
        tags:     Lista de tags Obsidian (ex: ["jarvis", "lembrete"])
        pasta:    Subpasta dentro do vault (ex: "Projetos")

    Returns:
        (bool, str): sucesso, mensagem
    """
    vault = get_vault_path()
    destino = vault / pasta if pasta else vault
    _ensure_dir(destino)

    caminho = destino / (_sanitize_filename(titulo) + ".md")

    if caminho.exists():
        return False, f"Nota '{titulo}' já existe em '{destino}'"

    # Frontmatter YAML
    frontmatter_tags = ""
    if tags:
        tag_list = "\n".join(f"  - {t}" for t in tags)
        frontmatter_tags = f"tags:\n{tag_list}\n"

    texto = (
        f"---\n"
        f"criado: {_format_timestamp()}\n"
        f"{frontmatter_tags}"
        f"---\n\n"
        f"# {titulo}\n\n"
        f"{conteudo}\n"
    )

    try:
        caminho.write_text(texto, encoding="utf-8")
        return True, f"Nota '{titulo}' criada em '{destino}'"
    except Exception as e:
        return False, f"Erro ao criar nota: {e}"


def ler_nota(titulo: str, pasta: str = "") -> tuple:
    """
    Lê o conteúdo de uma nota.

    Returns:
        (str | None, str): conteúdo ou None, mensagem
    """
    # Busca na pasta especificada ou em todo o vault
    if pasta:
        caminho = _note_path(titulo, pasta)
        if caminho.exists():
            return caminho.read_text(encoding="utf-8"), "Nota lida com sucesso"
        return None, f"Nota '{titulo}' não encontrada em '{pasta}'"

    # Busca recursiva no vault inteiro
    vault = get_vault_path()
    nome = _sanitize_filename(titulo) + ".md"
    for found in vault.rglob(nome):
        return found.read_text(encoding="utf-8"), "Nota lida com sucesso"

    return None, f"Nota '{titulo}' não encontrada no vault"


def editar_nota(titulo: str, novo_conteudo: str, pasta: str = "") -> tuple:
    """
    Substitui o corpo da nota preservando o frontmatter.

    Returns:
        (bool, str)
    """
    conteudo_atual, msg = ler_nota(titulo, pasta)
    if conteudo_atual is None:
        return False, msg

    vault = get_vault_path()
    nome = _sanitize_filename(titulo) + ".md"

    caminho = None
    for found in vault.rglob(nome):
        caminho = found
        break

    # Preserva frontmatter se existir
    if conteudo_atual.startswith("---"):
        partes = conteudo_atual.split("---", 2)
        if len(partes) >= 3:
            frontmatter = f"---{partes[1]}---\n\n"
            novo_texto = frontmatter + f"# {titulo}\n\n{novo_conteudo}\n"
        else:
            novo_texto = novo_conteudo
    else:
        novo_texto = novo_conteudo

    try:
        caminho.write_text(novo_texto, encoding="utf-8")
        return True, f"Nota '{titulo}' atualizada"
    except Exception as e:
        return False, f"Erro ao editar nota: {e}"


def adicionar_ao_final(titulo: str, texto: str, pasta: str = "") -> tuple:
    """
    Acrescenta texto ao final de uma nota existente.

    Returns:
        (bool, str)
    """
    vault = get_vault_path()
    nome = _sanitize_filename(titulo) + ".md"

    caminho = None
    if pasta:
        candidate = vault / pasta / nome
        if candidate.exists():
            caminho = candidate
    if caminho is None:
        for found in vault.rglob(nome):
            caminho = found
            break

    if caminho is None:
        return False, f"Nota '{titulo}' não encontrada"

    try:
        with caminho.open("a", encoding="utf-8") as f:
            f.write(f"\n{texto}\n")
        return True, f"Texto adicionado à nota '{titulo}'"
    except Exception as e:
        return False, f"Erro ao adicionar texto: {e}"


def deletar_nota(titulo: str, pasta: str = "") -> tuple:
    """
    Move a nota para a lixeira do vault (_lixeira/).

    Returns:
        (bool, str)
    """
    vault = get_vault_path()
    nome = _sanitize_filename(titulo) + ".md"

    caminho = None
    if pasta:
        candidate = vault / pasta / nome
        if candidate.exists():
            caminho = candidate
    if caminho is None:
        for found in vault.rglob(nome):
            caminho = found
            break

    if caminho is None:
        return False, f"Nota '{titulo}' não encontrada"

    lixeira = vault / "_lixeira"
    _ensure_dir(lixeira)
    destino = lixeira / nome

    try:
        caminho.rename(destino)
        return True, f"Nota '{titulo}' movida para a lixeira"
    except Exception as e:
        return False, f"Erro ao deletar nota: {e}"


def abrir_nota(titulo: str) -> tuple:
    """
    Abre a nota no Obsidian via os.startfile (Windows).

    Returns:
        (bool, str)
    """
    vault = get_vault_path()
    nome = _sanitize_filename(titulo) + ".md"

    for found in vault.rglob(nome):
        try:
            os.startfile(str(found))
            return True, f"Nota '{titulo}' aberta no Obsidian"
        except Exception as e:
            return False, f"Erro ao abrir nota: {e}"

    return False, f"Nota '{titulo}' não encontrada"


# ------------------------------------------------------------------
# Busca
# ------------------------------------------------------------------

def buscar_notas(termo: str, pasta: str = "", max_resultados: int = 10) -> list:
    """
    Busca notas cujo título OU conteúdo contenha o termo.

    Returns:
        list[dict]: [{"titulo": str, "caminho": str, "trecho": str}, ...]
    """
    vault = get_vault_path()
    base = vault / pasta if pasta else vault
    termo_lower = termo.lower()
    resultados = []

    for caminho in base.rglob("*.md"):
        try:
            conteudo = caminho.read_text(encoding="utf-8")
        except Exception:
            continue

        if termo_lower in conteudo.lower():
            # Extrai um trecho com contexto
            idx = conteudo.lower().find(termo_lower)
            inicio = max(0, idx - 60)
            fim = min(len(conteudo), idx + 80)
            trecho = "..." + conteudo[inicio:fim].replace("\n", " ") + "..."

            resultados.append({
                "titulo": caminho.stem,
                "caminho": str(caminho.relative_to(vault)),
                "trecho": trecho,
            })

        if len(resultados) >= max_resultados:
            break

    return resultados


def listar_notas(pasta: str = "") -> list:
    """
    Lista todas as notas do vault (ou de uma pasta).

    Returns:
        list[str]: títulos das notas
    """
    vault = get_vault_path()
    base = vault / pasta if pasta else vault

    if not base.exists():
        return []

    return sorted(p.stem for p in base.rglob("*.md"))


# ------------------------------------------------------------------
# Sistema de Aprendizado do Jarvis
# ------------------------------------------------------------------

def _jarvis_path(tipo: str) -> Path:
    """Retorna o path do arquivo de aprendizado para um tipo"""
    pasta = get_vault_path() / _JARVIS_FOLDER
    _ensure_dir(pasta)
    return pasta / (_sanitize_filename(tipo) + ".md")


def aprender_informacao(tipo: str, conteudo: str) -> tuple:
    """
    Registra uma informação aprendida pelo Jarvis.

    Args:
        tipo:     Categoria (ex: "preferencia", "fato", "lembrete")
        conteudo: Informação a registrar

    Returns:
        (bool, str)
    """
    caminho = _jarvis_path(tipo)
    now = _format_timestamp()

    try:
        if not caminho.exists():
            caminho.write_text(
                f"# {tipo.title()}\n\n*Informações registradas pelo Jarvis*\n\n",
                encoding="utf-8",
            )

        with caminho.open("a", encoding="utf-8") as f:
            f.write(f"- [{now}] {conteudo}\n")

        return True, f"Registrei: {conteudo}"
    except Exception as e:
        return False, f"Erro ao aprender informação: {e}"


def buscar_aprendizado(tipo: str = None, termo: str = None) -> list:
    """
    Busca informações aprendidas pelo Jarvis.

    Args:
        tipo:  Filtra por categoria
        termo: Filtra pelo conteúdo

    Returns:
        list[str]: entradas encontradas
    """
    pasta = get_vault_path() / _JARVIS_FOLDER
    if not pasta.exists():
        return []

    def _extrair_entradas(caminho: Path, filtro: str = None) -> list:
        linhas = []
        try:
            for linha in caminho.read_text(encoding="utf-8").splitlines():
                if linha.startswith("- ["):
                    partes = linha.split("] ", 1)
                    entrada = partes[1].strip() if len(partes) > 1 else linha
                    if filtro is None or filtro.lower() in entrada.lower():
                        linhas.append(entrada)
        except Exception:
            pass
        return linhas

    if tipo:
        return _extrair_entradas(_jarvis_path(tipo), filtro=termo)

    # Busca em todos os arquivos
    resultados = []
    for arq in sorted(pasta.glob("*.md")):
        resultados.extend(_extrair_entradas(arq, filtro=termo))
    return resultados


# ------------------------------------------------------------------
# Preferências do Usuário
# ------------------------------------------------------------------

def _prefs_path(usuario: str) -> Path:
    pasta = get_vault_path() / _JARVIS_FOLDER
    _ensure_dir(pasta)
    return pasta / f"prefs_{_sanitize_filename(usuario.lower())}.json"


def salvar_preferencia(usuario: str, chave: str, valor: str) -> bool:
    """
    Salva (ou atualiza) uma preferência do usuário em JSON.

    Returns:
        bool: sucesso
    """
    caminho = _prefs_path(usuario)

    # Carrega existente ou começa vazio
    prefs = {}
    if caminho.exists():
        try:
            prefs = json.loads(caminho.read_text(encoding="utf-8"))
        except Exception:
            prefs = {}

    prefs[chave.lower()] = {
        "valor": valor,
        "atualizado": _format_timestamp(),
    }

    try:
        caminho.write_text(json.dumps(prefs, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False


def lembrar_preferencia(usuario: str, chave: str = None) -> dict:
    """
    Recupera preferências do usuário.

    Args:
        usuario: Nome do usuário
        chave:   Chave específica (None = retorna todas)

    Returns:
        dict: {chave: valor} ou {chave: {valor, atualizado}}
    """
    caminho = _prefs_path(usuario)
    if not caminho.exists():
        return {}

    try:
        prefs = json.loads(caminho.read_text(encoding="utf-8"))
    except Exception:
        return {}

    if chave:
        entrada = prefs.get(chave.lower(), {})
        return {chave: entrada.get("valor", "")} if entrada else {}

    # Retorna mapa simples {chave: valor}
    return {k: v.get("valor", "") for k, v in prefs.items()}


# ------------------------------------------------------------------
# Nota Diária (Daily Note)
# ------------------------------------------------------------------

def nota_diaria(conteudo_extra: str = "") -> tuple:
    """
    Cria ou atualiza a nota diária do Jarvis.
    Arquivo: _jarvis/diario/YYYY-MM-DD.md

    Returns:
        (bool, str)
    """
    hoje = datetime.now().strftime("%Y-%m-%d")
    pasta_diario = get_vault_path() / _JARVIS_FOLDER / "diario"
    _ensure_dir(pasta_diario)

    caminho = pasta_diario / f"{hoje}.md"

    if not caminho.exists():
        caminho.write_text(
            f"---\ndata: {hoje}\n---\n\n# Diário — {hoje}\n\n",
            encoding="utf-8",
        )

    if conteudo_extra:
        with caminho.open("a", encoding="utf-8") as f:
            f.write(f"\n- [{_format_timestamp()}] {conteudo_extra}\n")
        return True, f"Adicionado ao diário de {hoje}"

    return True, f"Nota diária de {hoje} pronta"


# ------------------------------------------------------------------
# Função de alto nível para o Jarvis
# ------------------------------------------------------------------

def controlar_obsidian(acao: str, **kwargs) -> dict:
    """
    Interface unificada para o Jarvis controlar o Obsidian.

    Ações disponíveis:
        criar        → titulo, conteudo="", tags=[], pasta=""
        ler          → titulo, pasta=""
        editar       → titulo, novo_conteudo, pasta=""
        adicionar    → titulo, texto, pasta=""
        deletar      → titulo, pasta=""
        abrir        → titulo
        buscar       → termo, pasta=""
        listar       → pasta=""
        aprender     → tipo, conteudo
        lembrar      → tipo=None, termo=None
        salvar_pref  → usuario, chave, valor
        pref         → usuario, chave=None
        diario       → conteudo_extra=""

    Returns:
        dict: {"sucesso": bool, "mensagem": str, "dados": any}
    """
    mapa = {
        "criar":       lambda: criar_nota(**kwargs),
        "ler":         lambda: ler_nota(**kwargs),
        "editar":      lambda: editar_nota(**kwargs),
        "adicionar":   lambda: adicionar_ao_final(**kwargs),
        "deletar":     lambda: deletar_nota(**kwargs),
        "abrir":       lambda: abrir_nota(**kwargs),
        "buscar":      lambda: (bool(buscar_notas(**kwargs)), buscar_notas(**kwargs)),
        "listar":      lambda: (True, listar_notas(**kwargs)),
        "aprender":    lambda: aprender_informacao(**kwargs),
        "lembrar":     lambda: (True, buscar_aprendizado(**kwargs)),
        "salvar_pref": lambda: (salvar_preferencia(**kwargs), "Preferência salva"),
        "pref":        lambda: (True, lembrar_preferencia(**kwargs)),
        "diario":      lambda: nota_diaria(**kwargs),
    }

    if acao not in mapa:
        return {
            "sucesso": False,
            "mensagem": f"Ação '{acao}' não reconhecida. Disponíveis: {', '.join(mapa)}",
            "dados": None,
        }

    try:
        resultado = mapa[acao]()

        # Normaliza retorno — pode ser (bool, str) ou (bool, dados)
        if isinstance(resultado, tuple) and len(resultado) == 2:
            sucesso, dados = resultado
            mensagem = dados if isinstance(dados, str) else "OK"
            return {"sucesso": bool(sucesso), "mensagem": mensagem, "dados": dados}

        return {"sucesso": True, "mensagem": "OK", "dados": resultado}

    except TypeError as e:
        return {"sucesso": False, "mensagem": f"Parâmetros inválidos para '{acao}': {e}", "dados": None}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro inesperado em '{acao}': {e}", "dados": None}