import os
import sys
import json
import ctypes
import re
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.align import Align

# Configuración visual robusta
custom_theme = Theme({
    "info": "cyan",
    "warning": "bold magenta",
    "success": "bold green",
    "danger": "bold red",
    "input": "bold yellow"
})

console = Console(theme=custom_theme, force_terminal=True)

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def header(texto):
    console.print(Panel(Align.center(f"[bold white]{texto}[/bold white]"), style="info", subtitle="Spotify Backup Tool"))

def forzar_colores_windows():
    """Habilita colores ANSI en Windows 10/11"""
    if os.name == 'nt':
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass

def sanitize_filename(name):
    """Limpia caracteres inválidos para nombres de archivo"""
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()

def guardar_json(data, filename):
    try:
        # Asegurar que el directorio existe
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        console.print(f"[danger]Error guardando archivo: {e}[/danger]")
        return False

def cargar_json(filename):
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[danger]Error leyendo archivo: {e}[/danger]")
        return None
