# Nightfall Gargoyle

Juego de plataformas original con estética gótica, inspirado en la sensación de los clásicos de mascota de los 90: exploración, saltos, doble salto, ataque cuerpo a cuerpo, fragmentos coleccionables, enemigos, puntos de control, portales y guardado de progreso.

No usa personajes, nombres, música ni assets de juegos existentes; todo se dibuja por código con primitivas de Pygame.

## Características

- Multiplataforma: Ubuntu/Linux, Windows y macOS con Python 3.10+.
- Guardado automático en puntos de control y guardado manual con `F5`.
- Carga rápida con `F9`.
- Resolución configurable desde el menú de opciones.
- Pantalla completa alternable con `F11`.
- Ventana redimensionable.
- Dos niveles jugables con fragmentos, enemigos, picos y portales.

## Ejecutar en Ubuntu/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
nightfall-gargoyle
```

También puedes ejecutar:

```bash
python run_game.py
```

## Ejecutar en Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
nightfall-gargoyle
```

## Controles

- `A/D` o `←/→`: moverse.
- `W`, `↑` o `Espacio`: saltar / doble salto.
- `E`, `J` o `Ctrl`: atacar.
- `P` o `Esc`: pausa.
- `F5`: guardar partida.
- `F9`: cargar partida.
- `F11`: pantalla completa.

## Guardados y configuración

El juego usa carpetas de usuario nativas:

- Linux: `~/.local/share/nightfall_gargoyle/`
- Windows: `%APPDATA%\nightfall_gargoyle\`
- macOS: `~/Library/Application Support/nightfall_gargoyle/`

Archivos:

- `savegame.json`: progreso de partida.
- `config.json`: resolución, pantalla completa, volumen y vsync.

Para pruebas o builds portables puedes cambiar la ubicación con la variable `NIGHTFALL_GARGOYLE_HOME`.

## Crear ejecutables opcionales

Instala PyInstaller dentro del entorno virtual y compila para la plataforma actual:

```bash
python -m pip install pyinstaller
pyinstaller --onefile --windowed --name nightfall-gargoyle run_game.py
```

Para Windows conviene ejecutar el comando desde Windows; para Linux, desde Linux.

## Validación

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile run_game.py nightfall_gargoyle/*.py tests/*.py
```
