import sys
import argparse
import time
import os
from src.utils import header, console, guardar_json, cargar_json, forzar_colores_windows, sanitize_filename
from src.auth import obtener_token_spotify
from src.client import SpotifyClient
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

def main():
    forzar_colores_windows()
    
    parser = argparse.ArgumentParser(description="Spotify Backup Tool - Respaldar y Restaurar cuentas.")
    parser.add_argument("--backup", action="store_true", help="Realizar un respaldo de la cuenta.")
    parser.add_argument("--restore", action="store_true", help="Restaurar desde un archivo.")
    parser.add_argument("--file", type=str, default=None, help="Nombre opcional del archivo de respaldo")
    
    args = parser.parse_args()

    # Si no hay argumentos, mostramos menú interactivo simple o ayuda
    if not args.backup and not args.restore:
        header("SPOTIFY BACKUP & RESTORE")
        console.print("[dim]Usa este programa con argumentos para automatización o interactivo.[/dim]\n")
        console.print("1. [bold green]Hacer Respaldo (Backup)[/bold green]")
        console.print("2. [bold cyan]Restaurar Cuenta (Restore)[/bold cyan]")
        console.print("3. Salir")
        choice = input("\n> ")
        if choice == "1":
            args.backup = True
        elif choice == "2":
            args.restore = True
        else:
            sys.exit()

    if args.backup:
        do_backup(args.file)
    elif args.restore:
        # Para restaurar, si no especifica archivo, buscamos el último en backups/
        filename = args.file
        if not filename:
            console.print("[warning]No especificaste archivo. Buscando el más reciente en 'backups/'...[/warning]")
            if os.path.exists("backups"):
                files = [os.path.join("backups", f) for f in os.listdir("backups") if f.endswith(".json")]
                if files:
                    filename = max(files, key=os.path.getctime)
                    console.print(f"[info]Usando: {filename}[/info]")
                else:
                    console.print("[danger]No hay respaldos en la carpeta backups/.[/danger]")
                    return
            else:
                console.print("[danger]No existe la carpeta backups/ y no especificaste --file.[/danger]")
                return
        do_restore(filename)

def do_backup(filename_arg):
    token = obtener_token_spotify("ORIGEN")
    client = SpotifyClient(token)
    
    if not client.conectar():
        console.print("[danger]Falló la conexión con Spotify.[/danger]")
        return

    console.print(f"[success]Conectado como: {client.display_name}[/success]")
    
    backup_data = {
        "user": client.display_name,
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "playlists": [],
        "liked_songs": []
    }

    with console.status("[cyan]Analizando biblioteca...[/cyan]"):
        # Backup Playlists
        playlists = client.get_playlists()
        console.print(f"   ↳ Encontradas {len(playlists)} playlists.")
        
        for pl in playlists:
            tracks = client.get_tracks_from_url(pl['tracks_href'])
            backup_data["playlists"].append({
                "info": pl,
                "tracks": tracks
            })
            console.print(f"     [dim]- {pl['name']} ({len(tracks)} canciones)[/dim]")

        # Backup Liked Songs
        console.print("   ↳ Obteniendo 'Me Gusta'...")
        likes = client.get_liked_songs()
        backup_data["liked_songs"] = likes
        console.print(f"     [dim]- {len(likes)} canciones guardadas[/dim]")

    # Generación de nombre de archivo dinámico
    if filename_arg:
        final_filename = filename_arg
    else:
        # Formato: backups/respaldo_Usuario_YYYY-MM-DD_HH-mm.json
        safe_user = sanitize_filename(client.display_name)
        timestamp = time.strftime("%Y-%m-%d_%H-%M")
        final_filename = os.path.join("backups", f"respaldo_{safe_user}_{timestamp}.json")

    if guardar_json(backup_data, final_filename):
        console.print(f"\n[bold green]✅ Respaldo guardado exitosamente en: {final_filename}[/bold green]")
        time.sleep(3)

def do_restore(filename):
    data = cargar_json(filename)
    if not data:
        return

    console.print(f"[info]Archivo cargado: {data.get('user', 'Desconocido')} ({data.get('date')})[/info]")
    
    token = obtener_token_spotify("DESTINO")
    client = SpotifyClient(token)
    
    if not client.conectar():
        console.print("[danger]Falló la conexión con la cuenta destino.[/danger]")
        return
        
    console.print(f"[warning]¡ATENCIÓN! Se restaurará en la cuenta: {client.display_name}[/warning]")
    confirm = input("¿Continuar? (s/n): ")
    if confirm.lower() != 's':
        return

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), TaskProgressColumn(), console=console) as progress:
        
        # Restaurar Playlists
        task_pl = progress.add_task("[green]Restaurando Playlists...", total=len(data['playlists']))
        for item in data['playlists']:
            pl_info = item['info']
            tracks = item['tracks']
            
            # Crear PL
            new_pl = client.create_playlist(pl_info['name'], pl_info['description'])
            if new_pl:
                # Añadir canciones
                client.add_tracks(new_pl['id'], tracks)
            
            progress.advance(task_pl)

        # Restaurar Likes
        if data.get('liked_songs'):
            task_likes = progress.add_task("[cyan]Restaurando Me Gusta...", total=len(data['liked_songs']))
            # Lo hacemos en un solo batch gigante o chunks, client.save_tracks ya maneja chunks
            client.save_tracks(data['liked_songs'])
            progress.update(task_likes, completed=len(data['liked_songs']))

    console.print(f"\n[bold green]✨ Restauración completada ✨[/bold green]")
    time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        console.print(f"[danger]Error crítico: {e}[/danger]")
        input("Presiona ENTER para salir...")