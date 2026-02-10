# 🎵 Spotify Backup & Restore Tool

Esta herramienta permite realizar **copias de seguridad** de tus playlists y canciones favoritas de Spotify, y **restaurarlas** en otra cuenta. Ideal para migrar de cuenta o simplemente tener un respaldo local de tu música.

---

## ⚠️ AVISO LEGAL (DISCLAIMER)

> **ESTE SOFTWARE SE PROVEE "TAL CUAL", SIN GARANTÍA DE NINGÚN TIPO.**
>
> Este proyecto tiene **fines estrictamente educativos** para demostrar la automatización de navegadores y el manejo de APIs. El uso de este software es responsabilidad exclusiva del usuario. El autor no se hace responsable por:
> 1. Bloqueos de cuentas de Spotify.
> 2. Pérdida de datos.
> 3. Mal uso de la herramienta para fines ilícitos.
>
> **Nota:** Este programa NO descarga archivos de audio (MP3), solo gestiona metadatos (nombres de canciones, playlists, IDs) usando las herramientas públicas de desarrollo de Spotify.

---

## 🚀 Características

- **Respaldo Completo**: Playlists (propias y colaborativas) y Canciones "Me Gusta".
- **Restauración Inteligente**: Recrea tus playlists y vuelve a dar "Like" a tus canciones en una cuenta nueva.
- **Sin Credenciales**: No necesitas dar tu contraseña al programa. Usa un navegador seguro para obtener un token temporal.
- **Portable**: Disponible como archivo `.exe` único para Windows (no requiere instalación).

---

## 📥 ¿Dónde Descargar el Programa?

Cada vez que se actualiza el código, GitHub genera un nuevo ejecutable automáticamente. Esta es la forma más rápida de tener la última versión.

1. Ve a la sección de **[Releases](../../releases/latest)** de este repositorio (a la derecha).
2. Descarga el archivo `SpotifyBackup.exe`.
3. ¡Listo! Ya puedes usarlo.

---

## 🛠️ Uso
### Modo Interactivo (Doble Click)
Si ejecutas el programa sin argumentos, verás un menú:
1. **Hacer Respaldo**: Se abrirá un navegador. Inicia sesión en Spotify y sigue las instrucciones en pantalla para autorizar.
2. **Restaurar**: Selecciona el archivo de respaldo y autoriza la cuenta de destino.

### Modo Avanzado (CMD / Powershell)
Puedes automatizar tareas usando la línea de comandos:

**1. Realizar un respaldo:**
```powershell
SpotifyBackup.exe --backup --file "mi_musica_2024.json"
```

**2. Restaurar un respaldo:**
```powershell
SpotifyBackup.exe --restore --file "mi_musica_2024.json"
```

---

## 🐍 Ejecutar con Python (Para Desarrolladores)

Si prefieres usar el código fuente:

1. Clona el repositorio.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta el script:
   ```bash
   python main.py
   ```

---

## 🤖 Automatización y GitHub Actions
Este repositorio incluye un flujo de trabajo de **GitHub Actions**. Cada vez que se hace un `push` al repositorio, GitHub compila automáticamente una nueva versión del `.exe`.