import time
import sys
import json
import os
import ctypes
import requests

# === 1. PARCHE DE COLORES PARA WINDOWS 10/11 ===
# Esto fuerza a la consola a aceptar colores ANSI (como Linux/Mac)
def forzar_colores_windows():
    try:
        kernel32 = ctypes.windll.kernel32
        # Habilitar el modo de procesamiento virtual (VT100)
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass # Si falla (raro), seguimos sin colores pero sin crashear

forzar_colores_windows()
# ===============================================

# LIBRERÍAS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# VISUAL (RICH)
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.theme import Theme
from rich.align import Align
from rich.table import Table

# Configuración visual robusta
custom_theme = Theme({
    "info": "cyan",
    "warning": "bold magenta",
    "success": "bold green",
    "danger": "bold red",
    "input": "bold yellow"
})
# force_terminal=True asegura que Rich pinte colores aunque esté compilado
console = Console(theme=custom_theme, force_terminal=True)

def limpiar():
    os.system('cls' if os.name == 'nt' else 'clear')

def header(texto):
    console.print(Panel(Align.center(f"[bold white]{texto}[/bold white]"), style="info", subtitle="V9: FINAL + WIN10 SUPPORT"))

# ==============================================================================
# FASE 1: CAPTURADOR
# ==============================================================================
def validar_permisos_token(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.put("https://api.spotify.com/v1/me/tracks?limit=1", headers=headers, json=[])
        return r.status_code in [200, 201, 400] or r.status_code != 403
    except:
        return False

def obtener_token_auto(tipo_cuenta):
    console.print(f"\n[info]Abriendo navegador para {tipo_cuenta}...[/info]")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--log-level=3")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    # IMPORTANTE: Esto descarga el driver automáticamente según el Chrome del usuario
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get("https://developer.spotify.com/console/get-current-user-playlists/")
        
        # Auto-Click Login
        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log in')]"))).click()
        except: pass

        console.print(Panel(f"""
[bold yellow]INSTRUCCIONES PARA {tipo_cuenta}:[/bold yellow]

1. Pulsa [green]GET TOKEN[/green].
2. [bold red]MARCA ESTAS CASILLAS:[/bold red]
   [white]✔ playlist-modify-public / private[/white]
   [white]✔ user-library-read / modify[/white]
3. Request Token -> Aceptar.
""", title="ACCIÓN REQUERIDA", border_style="red"))

        token_valido = None
        while not token_valido:
            try:
                logs = driver.get_log("performance")
            except: break 

            for entry in logs:
                try:
                    message = json.loads(entry["message"])["message"]
                    if message["method"] == "Network.requestWillBeSent":
                        auth = message["params"]["request"]["headers"].get("Authorization")
                        if auth and "Bearer" in auth:
                            candidate = auth.replace("Bearer ", "").strip()
                            if len(candidate) > 50 and validar_permisos_token(candidate):
                                token_valido = candidate
                                break
                except: continue
            
            if token_valido: break
            time.sleep(0.5)

        if token_valido:
            console.print(f"[success]¡TOKEN VÁLIDO![/success]")
            driver.quit()
            return token_valido
        else:
            sys.exit()

    except Exception:
        try: driver.quit()
        except: pass
        sys.exit()

# ==============================================================================
# FASE 2: NATIVE MIGRATOR
# ==============================================================================
class SpotifyNative:
    def __init__(self, token):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        self.base_url = "https://api.spotify.com/v1"
        self.user_id = None
        self.name = None

    def conectar(self):
        r = requests.get(f"{self.base_url}/me", headers=self.headers)
        if r.status_code == 200:
            data = r.json()
            self.user_id = data['id']
            self.name = data.get('display_name', self.user_id)
            return True
        return False

    def get_all_playlists(self):
        playlists = []
        url = f"{self.base_url}/me/playlists?limit=50"
        while url:
            r = requests.get(url, headers=self.headers)
            if r.status_code != 200: break
            data = r.json()
            for item in data.get('items', []):
                if item['owner']['id'] == self.user_id or item.get('collaborative'):
                    playlists.append({"name": item['name'], "desc": item['description'], "public": item['public'], "tracks_href": item['tracks']['href']})
            url = data.get('next')
        return playlists

    def get_liked_songs(self):
        ids = []
        url = f"{self.base_url}/me/tracks?limit=50"
        console.print("   ↳ [dim]Leyendo 'Me Gusta'...[/dim]")
        while url:
            r = requests.get(url, headers=self.headers)
            if r.status_code == 429: time.sleep(3); continue
            if r.status_code != 200: break
            data = r.json()
            for item in data.get('items', []):
                if item.get('track'): ids.append(item['track']['id'])
            url = data.get('next')
        return ids
    
    def get_saved_episodes(self):
        ids = []
        url = f"{self.base_url}/me/episodes?limit=50"
        console.print("   ↳ [dim]Leyendo 'Episodios'...[/dim]")
        while url:
            r = requests.get(url, headers=self.headers)
            if r.status_code != 200: break
            data = r.json()
            for item in data.get('items', []):
                if item.get('episode'): ids.append(item['episode']['id'])
            url = data.get('next')
        return ids

    def get_tracks_uris(self, url):
        uris = []
        while url:
            r = requests.get(url, headers=self.headers)
            if r.status_code == 429: time.sleep(3); continue
            if r.status_code != 200: break
            data = r.json()
            for item in data.get('items', []):
                if item.get('track') and item['track'].get('uri'): uris.append(item['track']['uri'])
            url = data.get('next')
        return uris

    def create_playlist(self, name, desc):
        url = f"{self.base_url}/users/{self.user_id}/playlists"
        r = requests.post(url, headers=self.headers, json={"name": name, "description": desc, "public": False})
        return r.json() if r.status_code in [200, 201] else None

    def add_tracks_playlist(self, playlist_id, uris):
        url = f"{self.base_url}/playlists/{playlist_id}/tracks"
        for i in range(0, len(uris), 100):
            requests.post(url, headers=self.headers, json={"uris": uris[i:i+100]})

    def inject_likes(self, ids):
        url = f"{self.base_url}/me/tracks"
        for i in range(0, len(ids), 50):
            requests.put(url, headers=self.headers, json={"ids": ids[i:i+50]})
            time.sleep(0.1)

    def inject_episodes(self, ids):
        url = f"{self.base_url}/me/episodes"
        for i in range(0, len(ids), 50):
            requests.put(url, headers=self.headers, json={"ids": ids[i:i+50]})
            time.sleep(0.1)

# ==============================================================================
# MAIN
# ==============================================================================
def main():
    limpiar()
    header("SPOTIFY MIGRATOR: NATIVE")

    while True:
        token_origen = obtener_token_auto("ORIGEN")
        origen = SpotifyNative(token_origen)
        if origen.conectar():
            console.print(f"[success]Conectado: {origen.name}[/success]")
            break

    backup = []
    with console.status("[cyan]Analizando...[/cyan]"):
        for pl in origen.get_all_playlists():
            backup.append({"type": "playlist", "data": pl, "items": origen.get_tracks_uris(pl['tracks_href'])})
        
        likes = origen.get_liked_songs()
        if likes: backup.append({"type": "likes", "name": "Me Gusta", "items": likes})
        
        eps = origen.get_saved_episodes()
        if eps: backup.append({"type": "episodes", "name": "Episodios", "items": eps})

    limpiar()
    header(f"RESUMEN: {origen.name}")
    table = Table()
    table.add_column("Tipo")
    table.add_column("Nombre")
    table.add_column("Items")
    for x in backup:
        name = x['data']['name'] if x['type'] == 'playlist' else x['name']
        table.add_row(x['type'].upper(), name, str(len(x['items'])))
    console.print(table)
    
    input("\nENTER para continuar...")

    limpiar()
    header("DESTINO")
    while True:
        token_dest = obtener_token_auto("DESTINO")
        if token_dest == token_origen: continue
        destino = SpotifyNative(token_dest)
        if destino.conectar() and destino.user_id != origen.user_id:
            console.print(f"[success]Destino: {destino.name}[/success]")
            break

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), TaskProgressColumn(), console=console) as progress:
        task = progress.add_task("[green]Migrando...", total=len(backup))
        for item in backup:
            if item['type'] == 'playlist':
                new = destino.create_playlist(item['data']['name'], item['data']['desc'])
                if new and item['items']: destino.add_tracks_playlist(new['id'], item['items'])
            elif item['type'] == 'likes':
                destino.inject_likes(item['items'])
            elif item['type'] == 'episodes':
                destino.inject_episodes(item['items'])
            progress.advance(task)

    console.print("\n[bold green]✨ LISTO ✨[/bold green]")
    time.sleep(5)

if __name__ == "__main__":
    try: main()
    except: pass