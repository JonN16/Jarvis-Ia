"""
Spotify Service - Integração profissional com Spotify via Spotipy
Controle total: play, pause, próximo, anterior, busca, volume
"""

import os
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from services.app_finder import abrir_app

# Carrega variáveis de ambiente
load_dotenv()

# Cache file para token do Spotify
CACHE_PATH = ".spotify_cache"

# Escopos necessários
SCOPE = (
    "streaming "
    "user-read-email "
    "user-read-private "
    "user-read-playback-state "
    "user-modify-playback-state "
    "user-read-currently-playing "
    "user-library-read "
    "user-library-modify "
    "user-top-read "
    "playlist-read-private "
    "playlist-modify-public "
    "playlist-modify-private"
)


class SpotifyService:
    """Classe para controle profissional do Spotify via API"""

    def __init__(self):
        self.sp = None
        self.device_id = None
        self._connect()

    def _connect(self):
        """Conecta ao Spotify usando OAuth"""
        try:
            client_id = os.getenv("SPOTIFY_CLIENT_ID")
            client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
            redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")

            if not client_id or client_id == "seu_client_id_aqui":
                print("[Spotify] ⚠️  Credenciais não configuradas. Execute o setup primeiro.")
                return False

            self.sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    scope=SCOPE,
                    cache_path=CACHE_PATH,
                    open_browser=False,
                )
            )

            self.sp.current_user()
            print("[Spotify] ✅ Conectado com sucesso!")
            return True

        except Exception as e:
            print(f"[Spotify] ❌ Erro ao conectar: {e}")
            return False

    # ------------------------------------------------------------------
    # Gerenciamento de dispositivo
    # ------------------------------------------------------------------

    def get_device_id(self):
        """Obtém o ID do dispositivo ativo (ou primeiro disponível)"""
        if not self.sp:
            return None

        try:
            devices = self.sp.devices().get("devices", [])
            for device in devices:
                if device.get("is_active"):
                    self.device_id = device["id"]
                    return self.device_id
            if devices:
                self.device_id = devices[0]["id"]
                return self.device_id
        except Exception as e:
            print(f"[Spotify] Erro ao obter dispositivo: {e}")

        return None

    def _ativar_dispositivo(self):
        """
        Força o Spotify a reconhecer este computador como dispositivo ativo.
        Resolve o erro 404 quando o app está aberto mas sem sessão de reprodução.

        Retorna o device_id ativo ou None.
        """
        if not self.sp:
            return None

        try:
            devices = self.sp.devices().get("devices", [])
            if not devices:
                print("[Spotify] ⚠️  Nenhum dispositivo encontrado.")
                return None

            # Prefere o dispositivo já marcado como ativo
            device_id = next(
                (d["id"] for d in devices if d.get("is_active")),
                devices[0]["id"],
            )

            # Transfere a reprodução para esse dispositivo sem forçar play.
            # Isso "acorda" o contexto de reprodução na API sem iniciar música.
            self.sp.transfer_playback(device_id=device_id, force_play=False)
            self.device_id = device_id
            print(f"[Spotify] 🔌 Dispositivo ativado: {devices[0].get('name', device_id)}")
            time.sleep(1)  # Aguarda o handshake com o servidor
            return device_id

        except Exception as e:
            print(f"[Spotify] Erro ao ativar dispositivo: {e}")
            return None

    def _wake_up_spotify(self):
        """
        Sequência completa de "wake-up":
        1. Abre o Spotify se necessário
        2. Tenta ativar o dispositivo via API
        3. Se falhar, simula tecla de mídia como fallback
        """
        # Passo 1: garante que o app está aberto
        abrir_app("spotify")
        time.sleep(3)  # Aguarda o app carregar completamente

        # Passo 2: tenta ativar via API
        device_id = self._ativar_dispositivo()
        if device_id:
            return device_id

        # Passo 3: fallback — simula tecla Play/Pause do teclado multimídia
        print("[Spotify] 🎹 Fallback: simulando tecla de mídia para ativar sessão...")
        try:
            import keyboard
            keyboard.send("play/pause")
            time.sleep(2)
            device_id = self._ativar_dispositivo()  # Tenta de novo após o tranco
        except ImportError:
            print("[Spotify] ⚠️  Biblioteca 'keyboard' não instalada. Fallback indisponível.")
        except Exception as e:
            print(f"[Spotify] Fallback falhou: {e}")

        return device_id

    # ------------------------------------------------------------------
    # Controles de reprodução
    # ------------------------------------------------------------------

    def play_music(self, query):
        """
        Busca e toca uma música específica.
        Ativa o dispositivo automaticamente caso o Spotify esteja em modo de espera.
        """
        if not self.sp:
            return False, "Spotify não conectado. Configure credenciais no .env e execute autenticação."

        try:
            # Garante que há uma sessão ativa antes de qualquer comando
            device_id = self._wake_up_spotify()

            # Busca a música
            print(f"[Spotify] Buscando: '{query}'")
            results = self.sp.search(q=query, type="track", limit=1)

            if not results["tracks"]["items"]:
                return False, f"Nenhuma música encontrada para '{query}'. Tente outro nome."

            track = results["tracks"]["items"][0]
            track_name = track["name"]
            artist_name = track["artists"][0]["name"]
            track_uri = track["uri"]

            # Toca a música, passando o device_id explicitamente para evitar 404
            try:
                self.sp.start_playback(device_id=device_id, uris=[track_uri])
            except TypeError:
                self.sp.start_playback(device_id=device_id, uri=track_uri)

            return True, f"Tocando '{track_name}' de {artist_name}"

        except spotipy.SpotifyException as e:
            if e.http_status == 401:
                return False, "Token do Spotify expirado. Reautentique o aplicativo."
            elif e.http_status == 403:
                return False, "Permissão negada. Verifique se o Spotify Premium está ativo."
            elif e.http_status == 404:
                return (
                    False,
                    "Senhor, o Spotify está em modo de espera profundo. "
                    "Por favor, inicie uma música manualmente uma vez para que eu possa assumir o controle dos sistemas de áudio.",
                )
            else:
                return False, f"Erro do Spotify ({e.http_status}): {e.msg}"
        except Exception as e:
            return False, f"Erro ao tocar música: {type(e).__name__}: {e}"

    def pause(self):
        """Pausa a reprodução"""
        if not self.sp:
            return False, "Spotify não conectado"
        try:
            self.sp.pause_playback()
            return True, "Reprodução pausada"
        except spotipy.SpotifyException as e:
            if e.http_status in (403, 404):
                return False, "Conta gratuita ou sessão inativa: use os controles de mídia do Windows para pausar."
            return False, f"Erro ao pausar: {e}"
        except Exception as e:
            return False, f"Erro ao pausar: {e}"

    def resume(self):
        """Retoma a reprodução"""
        if not self.sp:
            return False, "Spotify não conectado"
        try:
            device_id = self.get_device_id()
            self.sp.start_playback(device_id=device_id)
            return True, "Reprodução retomada"
        except spotipy.SpotifyException as e:
            if e.http_status == 404:
                # Tenta wake-up e repete
                device_id = self._wake_up_spotify()
                try:
                    self.sp.start_playback(device_id=device_id)
                    return True, "Reprodução retomada após ativação do dispositivo"
                except Exception:
                    pass
            if e.http_status in (403, 404):
                return False, "Conta gratuita ou sessão inativa: use os controles de mídia do Windows para play."
            return False, f"Erro ao retomar: {e}"
        except Exception as e:
            return False, f"Erro ao retomar: {e}"

    def next_track(self):
        """Pula para próxima música"""
        if not self.sp:
            return False, "Spotify não conectado"
        try:
            self.sp.next_track()
            return True, "Próxima música"
        except spotipy.SpotifyException as e:
            if e.http_status in (403, 404):
                return False, "Conta gratuita ou sessão inativa: use os controles de mídia do Windows para pular."
            return False, f"Erro ao pular: {e}"
        except Exception as e:
            return False, f"Erro ao pular: {e}"

    def previous_track(self):
        """Volta para música anterior"""
        if not self.sp:
            return False, "Spotify não conectado"
        try:
            self.sp.previous_track()
            return True, "Música anterior"
        except spotipy.SpotifyException as e:
            if e.http_status in (403, 404):
                return False, "Conta gratuita ou sessão inativa: use os controles de mídia do Windows para voltar."
            return False, f"Erro ao voltar: {e}"
        except Exception as e:
            return False, f"Erro ao voltar: {e}"

    def set_volume(self, volume_percent):
        """Define o volume (0–100)"""
        if not self.sp:
            return False, "Spotify não conectado"
        try:
            volume = max(0, min(100, volume_percent))
            self.sp.volume(volume)
            return True, f"Volume definido para {volume}%"
        except Exception as e:
            return False, f"Erro ao ajustar volume: {e}"

    def play_liked_songs(self, shuffle: bool = True) -> tuple:
        """Toca as músicas curtidas do usuário"""
        if not self.sp:
            return False, "Spotify não conectado"
        try:
            device_id = self._wake_up_spotify()

            # Pega as músicas curtidas (até 50)
            results = self.sp.current_user_saved_tracks(limit=50)
            items = results.get("items", [])
            if not items:
                return False, "Nenhuma música curtida encontrada"

            uris = [item["track"]["uri"] for item in items if item.get("track")]

            if shuffle:
                import random
                random.shuffle(uris)

            self.sp.start_playback(device_id=device_id, uris=uris)
            return True, f"Tocando suas músicas curtidas ({len(uris)} músicas)"

        except spotipy.SpotifyException as e:
            if e.http_status == 403:
                return False, "Permissão negada. Verifique se o Spotify Premium está ativo."
            return False, f"Erro do Spotify: {e.msg}"
        except Exception as e:
            return False, f"Erro ao tocar músicas curtidas: {e}"

    def play_playlist(self, nome: str) -> tuple:
        """Busca e toca uma playlist pelo nome"""
        if not self.sp:
            return False, "Spotify não conectado"
        try:
            device_id = self._wake_up_spotify()

            # Primeiro tenta nas playlists do próprio usuário
            playlists = self.sp.current_user_playlists(limit=50)
            nome_lower = nome.lower()

            playlist_uri = None
            playlist_nome = None

            for pl in playlists.get("items", []):
                if pl and nome_lower in pl["name"].lower():
                    playlist_uri = pl["uri"]
                    playlist_nome = pl["name"]
                    break

            # Se não achou, busca no catálogo geral
            if not playlist_uri:
                results = self.sp.search(q=nome, type="playlist", limit=5)
                items = results.get("playlists", {}).get("items", [])
                if items:
                    playlist_uri = items[0]["uri"]
                    playlist_nome = items[0]["name"]

            if not playlist_uri:
                return False, f"Nenhuma playlist encontrada para '{nome}'"

            self.sp.start_playback(device_id=device_id, context_uri=playlist_uri)
            return True, f"Tocando playlist '{playlist_nome}'"

        except spotipy.SpotifyException as e:
            if e.http_status == 403:
                return False, "Spotify Premium necessário para tocar playlists."
            return False, f"Erro do Spotify: {e.msg}"
        except Exception as e:
            return False, f"Erro ao tocar playlist: {e}"

    def get_current_track(self):
        """Obtém informações da música atual"""
        if not self.sp:
            return None, "Spotify não conectado"
        try:
            current = self.sp.currently_playing()
            if current and current.get("item"):
                track = current["item"]
                return {
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "album": track["album"]["name"],
                    "progress": current.get("progress_ms", 0),
                    "duration": track.get("duration_ms", 0),
                    "is_playing": current.get("is_playing", False),
                }, "Música atual obtida"
            return None, "Nenhuma música tocando"
        except Exception as e:
            return None, f"Erro ao obter música: {e}"

    def add_to_queue(self, query):
        """Adiciona música à fila"""
        if not self.sp:
            return False, "Spotify não conectado"
        try:
            results = self.sp.search(q=query, type="track", limit=1)
            if not results["tracks"]["items"]:
                return False, f"Nenhuma música encontrada para '{query}'"

            track = results["tracks"]["items"][0]
            self.sp.add_to_queue(track["uri"])
            return True, f"'{track['name']}' adicionada à fila"
        except Exception as e:
            return False, f"Erro ao adicionar à fila: {e}"


# ------------------------------------------------------------------
# Singleton e funções de compatibilidade
# ------------------------------------------------------------------

_spotify_service = None


def get_spotify_service():
    """Obtém a instância global do serviço Spotify"""
    global _spotify_service
    if _spotify_service is None:
        _spotify_service = SpotifyService()
    return _spotify_service


def controlar_spotify(acao, parametro=None):
    """
    Função principal para controle do Spotify.

    Args:
        acao: play | pause | resume | next | previous | volume | queue | current
        parametro: nome da música, valor de volume, etc.

    Returns:
        dict: {"sucesso": bool, "mensagem": str}
    """
    service = get_spotify_service()

    if not service.sp:
        return {"sucesso": False, "mensagem": "Spotify não conectado. Configure as credenciais no .env"}

    acoes = {
        "play":        lambda: service.play_music(parametro) if parametro else service.resume(),
        "pause":       service.pause,
        "resume":      service.resume,
        "next":        service.next_track,
        "previous":    service.previous_track,
        "volume":      lambda: service.set_volume(int(parametro)) if parametro else (False, "Informe o volume (0-100)"),
        "queue":       lambda: service.add_to_queue(parametro) if parametro else (False, "Informe o nome da música"),
        "liked":       lambda: service.play_liked_songs(),
        "playlist":    lambda: service.play_playlist(parametro) if parametro else (False, "Informe o nome da playlist"),
        "current":     lambda: (True, service.get_current_track()[0])
                       if service.get_current_track()[0]
                       else (False, "Nenhuma música tocando"),
    }

    if acao in acoes:
        sucesso, mensagem = acoes[acao]()
        return {"sucesso": sucesso, "mensagem": mensagem}

    return {"sucesso": False, "mensagem": f"Ação '{acao}' não reconhecida"}


def buscar_musica(nome):
    """Busca e toca uma música (função de compatibilidade)"""
    return controlar_spotify("play", nome)


def autenticar_spotify():
    """Instruções para autenticação inicial"""
    print("=" * 50)
    print("  Autenticação Spotify")
    print("=" * 50)
    print("\n1. Abra o arquivo .env e configure suas credenciais")
    print("2. Execute este comando para autenticar:")
    print("   python -c 'from services.spotify_service import get_spotify_service; get_spotify_service()'")
    print("\n3. Siga o link que aparecerá no terminal")
    print("4. Autorize o aplicativo")
    print("5. Copie a URL de redirect e cole no terminal")
    print("\nIsso só precisa ser feito uma vez!")