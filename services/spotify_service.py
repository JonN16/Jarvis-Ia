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
        """Inicializa o serviço do Spotify"""
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
                    open_browser=False  # Não abrir navegador automaticamente
                )
            )
            
            # Testa conexão
            self.sp.current_user()
            print("[Spotify] ✅ Conectado com sucesso!")
            return True
            
        except Exception as e:
            print(f"[Spotify] ❌ Erro ao conectar: {e}")
            return False
    
    def get_device_id(self):
        """Obtém o ID do dispositivo ativo"""
        if not self.sp:
            return None
        
        try:
            devices = self.sp.devices()
            for device in devices.get("devices", []):
                if device.get("is_active"):
                    self.device_id = device["id"]
                    return self.device_id
            
            # Se nenhum dispositivo ativo, usa o primeiro disponível
            devices_list = devices.get("devices", [])
            if devices_list:
                self.device_id = devices_list[0]["id"]
                return self.device_id
                
        except Exception as e:
            print(f"[Spotify] Erro ao obter dispositivo: {e}")
        
        return None
    
    def play_music(self, query):
        """
        Busca e toca uma música específica
        
        Args:
            query: Nome da música/artista para buscar
        """
        if not self.sp:
            return False, "Spotify não conectado"
        
        try:
            # Abre o Spotify primeiro se não estiver aberto
            abrir_app("spotify")
            time.sleep(3)  # Aguarda o Spotify abrir
            
            # Busca a música
            results = self.sp.search(q=query, type="track", limit=1)
            
            if not results["tracks"]["items"]:
                return False, f"Nenhuma música encontrada para '{query}'"
            
            track = results["tracks"]["items"][0]
            track_name = track["name"]
            artist_name = track["artists"][0]["name"]
            track_uri = track["uri"]
            
            # Toca a música
            self.sp.start_playback(uri=track_uri)
            
            return True, f"Tocando '{track_name}' de {artist_name}"
            
        except Exception as e:
            return False, f"Erro ao tocar música: {e}"
    
    def pause(self):
        """Pausa a reprodução"""
        if not self.sp:
            return False, "Spotify não conectado"
        
        try:
            self.sp.pause_playback()
            return True, "Reprodução pausada"
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "Restriction violated" in error_msg:
                return False, "Conta gratuita: use controles de mídia do Windows para pausar"
            return False, f"Erro ao pausar: {e}"
    
    def resume(self):
        """Retoma a reprodução"""
        if not self.sp:
            return False, "Spotify não conectado"
        
        try:
            self.sp.start_playback()
            return True, "Reprodução retomada"
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "Restriction violated" in error_msg:
                return False, "Conta gratuita: use controles de mídia do Windows para play"
            return False, f"Erro ao retomar: {e}"
    
    def next_track(self):
        """Pula para próxima música"""
        if not self.sp:
            return False, "Spotify não conectado"
        
        try:
            self.sp.next_track()
            return True, "Próxima música"
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "Restriction violated" in error_msg:
                return False, "Conta gratuita: use controles de mídia do Windows para pular"
            return False, f"Erro ao pular: {e}"
    
    def previous_track(self):
        """Volta para música anterior"""
        if not self.sp:
            return False, "Spotify não conectado"
        
        try:
            self.sp.previous_track()
            return True, "Música anterior"
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "Restriction violated" in error_msg:
                return False, "Conta gratuita: use controles de mídia do Windows para voltar"
            return False, f"Erro ao voltar: {e}"
    
    def set_volume(self, volume_percent):
        """
        Define o volume
        
        Args:
            volume_percent: Volume de 0 a 100
        """
        if not self.sp:
            return False, "Spotify não conectado"
        
        try:
            volume = max(0, min(100, volume_percent))
            self.sp.volume(volume)
            return True, f"Volume definido para {volume}%"
        except Exception as e:
            return False, f"Erro ao ajustar volume: {e}"
    
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
                    "is_playing": current.get("is_playing", False)
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
            
            track_uri = results["tracks"]["items"][0]["uri"]
            track_name = results["tracks"]["items"][0]["name"]
            
            self.sp.add_to_queue(track_uri)
            return True, f"'{track_name}' adicionada à fila"
            
        except Exception as e:
            return False, f"Erro ao adicionar à fila: {e}"


# Instância global do serviço
_spotify_service = None


def get_spotify_service():
    """Obtém a instância global do serviço Spotify"""
    global _spotify_service
    if _spotify_service is None:
        _spotify_service = SpotifyService()
    return _spotify_service


def controlar_spotify(acao, parametro=None):
    """
    Função principal para controle do Spotify
    
    Args:
        acao: Ação a ser executada (play, pause, next, previous, volume, etc)
        parametro: Parâmetro adicional (nome da música, volume, etc)
    
    Returns:
        dict: {"sucesso": bool, "mensagem": str}
    """
    service = get_spotify_service()
    
    if not service.sp:
        return {"sucesso": False, "mensagem": "Spotify não conectado. Configure as credenciais no .env"}
    
    acoes = {
        "play": lambda: service.play_music(parametro) if parametro else service.resume(),
        "pause": service.pause,
        "resume": service.resume,
        "next": service.next_track,
        "previous": service.previous_track,
        "volume": lambda: service.set_volume(int(parametro)) if parametro else (False, "Informe o volume (0-100)"),
        "queue": lambda: service.add_to_queue(parametro) if parametro else (False, "Informe o nome da música"),
        "current": lambda: (True, service.get_current_track()[0]) if service.get_current_track()[0] else (False, "Nenhuma música tocando")
    }
    
    if acao in acoes:
        sucesso, mensagem = acoes[acao]()
        return {"sucesso": sucesso, "mensagem": mensagem}
    
    return {"sucesso": False, "mensagem": f"Ação '{acao}' não reconhecida"}


def buscar_musica(nome):
    """
    Busca uma música no Spotify (função de compatibilidade)
    
    Args:
        nome: Nome da música para buscar
    
    Returns:
        dict: {"sucesso": bool, "mensagem": str}
    """
    return controlar_spotify("play", nome)


# Função de autenticação inicial (executar uma vez)
def autenticar_spotify():
    """
    Realiza a autenticação inicial com o Spotify
    Deve ser executada uma vez para autorizar o aplicativo
    """
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