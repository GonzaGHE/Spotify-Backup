import time
import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from .utils import console

def obtener_token_spotify(tipo_cuenta="USUARIO"):
    """
    Abre un navegador (Incógnito) para obtener el token de Spotify.
    No guarda caché para permitir múltiples cuentas.
    """
    console.print(f"\n[info]Iniciando navegador seguro para {tipo_cuenta}...[/info]")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--incognito")  # MODO INCÓGNITO: Para asegurar sesión limpia
    options.add_argument("--log-level=3")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    try:
        # Instalación automática del driver compatible
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        url_developer = "https://developer.spotify.com/console/get-current-user-playlists/"
        driver.get(url_developer)
        
        # Intentar click automático en Log In si aparece
        try:
            xpath_login = "//button[contains(., 'Log in')]"
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath_login))).click()
        except:
            pass

        console.print(f"""
[bold yellow]INSTRUCCIONES ({tipo_cuenta}):[/bold yellow]
1. Inicia sesión en Spotify (si se pide).
2. Pulsa el botón [green]GET TOKEN[/green].
3. [bold red]MARCA:[/bold red] 
   - [white]playlist-modify-public[/white]
   - [white]playlist-modify-private[/white]
   - [white]user-library-read[/white]
   - [white]user-library-modify[/white]
4. Click en [bold]Request Token[/bold].
5. ¡El programa detectará el token automáticamente!
""")

        token_valido = None
        intentos = 0
        
        while not token_valido and intentos < 600: # Timeout de 5 minutos aprox
            try:
                # Leemos los logs de red del navegador
                logs = driver.get_log("performance")
            except:
                break # Navegador cerrado manualmente

            for entry in logs:
                try:
                    obj = json.loads(entry["message"])
                    message = obj.get("message", {})
                    if message.get("method") == "Network.requestWillBeSent":
                        headers = message["params"]["request"].get("headers", {})
                        auth = headers.get("Authorization")
                        if auth and "Bearer" in auth:
                            candidate = auth.replace("Bearer ", "").strip()
                            # Validación simple de longitud
                            if len(candidate) > 50:
                                token_valido = candidate
                                break
                except:
                    continue
            
            if token_valido:
                break
                
            time.sleep(0.5)
            intentos += 1

        if token_valido:
            console.print(f"[success]¡Token capturado exitosamente![/success]")
            driver.quit()
            return token_valido
        else:
            console.print("[danger]No se detectó token o se cerró el navegador.[/danger]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[danger]Error lanzando navegador: {e}[/danger]")
        try:
            driver.quit()
        except:
            pass
        sys.exit(1)
