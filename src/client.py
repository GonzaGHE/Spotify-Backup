import requests
import time
from .utils import console

class SpotifyClient:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.spotify.com/v1"
        self.user_id = None
        self.display_name = None

    def conectar(self):
        """Verifica el token y obtiene datos del usuario"""
        try:
            r = requests.get(f"{self.base_url}/me", headers=self.headers)
            if r.status_code == 200:
                data = r.json()
                self.user_id = data['id']
                self.display_name = data.get('display_name', self.user_id)
                return True
            return False
        except Exception as e:
            console.print(f"[danger]Error conectando: {e}[/danger]")
            return False

    def _get_paginated(self, url, description="Cargando"):
        """Helper genérico para endpoints paginados"""
        items = []
        while url:
            try:
                r = requests.get(url, headers=self.headers)
                if r.status_code == 429:
                    retry_after = int(r.headers.get("Retry-After", 5))
                    console.print(f"[warning]Rate limit hit. Esperando {retry_after}s...[/warning]")
                    time.sleep(retry_after)
                    continue
                
                if r.status_code != 200:
                    console.print(f"[danger]Error {r.status_code} en {url}[/danger]")
                    break

                data = r.json()
                items.extend(data.get('items', []))
                url = data.get('next')
                
            except Exception as e:
                console.print(f"[danger]Excepción en paginación: {e}[/danger]")
                break
        return items

    def get_playlists(self):
        """Obtiene playlists creadas por el usuario"""
        raw_items = self._get_paginated(f"{self.base_url}/me/playlists?limit=50", "Playlists")
        playlists = []
        for item in raw_items:
            # Filtramos solo las que son del usuario o colaborativas
            if item['owner']['id'] == self.user_id or item.get('collaborative'):
                playlists.append({
                    "name": item['name'],
                    "description": item['description'],
                    "public": item['public'],
                    "tracks_href": item['tracks']['href'],
                    "uri": item['uri']
                })
        return playlists

    def get_tracks_from_url(self, url):
        """Obtiene URIs de canciones de una URL de tracks"""
        raw_items = self._get_paginated(url, "Tracks")
        uris = []
        for item in raw_items:
            track = item.get('track')
            if track and track.get('uri'):
                uris.append(track['uri'])
        return uris

    def get_liked_songs(self):
        """Obtiene Canciones que Me Gustan"""
        raw_items = self._get_paginated(f"{self.base_url}/me/tracks?limit=50", "Liked Songs")
        ids = []
        for item in raw_items:
            track = item.get('track')
            if track and track.get('id'):
                ids.append(track['id'])
        return ids

    def create_playlist(self, name, description="Restored by Backup Tool"):
        """Crea una nueva playlist y retorna su ID"""
        url = f"{self.base_url}/users/{self.user_id}/playlists"
        payload = {"name": name, "description": description, "public": False}
        r = requests.post(url, headers=self.headers, json=payload)
        if r.status_code in [200, 201]:
            return r.json()
        return None

    def add_tracks(self, playlist_id, uris):
        """Añade canciones a una playlist en lotes de 100"""
        url = f"{self.base_url}/playlists/{playlist_id}/tracks"
        for i in range(0, len(uris), 100):
            batch = uris[i:i+100]
            requests.post(url, headers=self.headers, json={"uris": batch})
            time.sleep(0.1) # Breve pausa para no saturar

    def save_tracks(self, ids):
        """Da 'Me Gusta' a canciones por ID"""
        url = f"{self.base_url}/me/tracks"
        for i in range(0, len(ids), 50):
            batch = ids[i:i+50]
            requests.put(url, headers=self.headers, json={"ids": batch})
            time.sleep(0.1)
