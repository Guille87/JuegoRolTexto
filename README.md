# Juego de Batalla por Turnos
¡Bienvenido al juego de **Batalla** por **Turnos** en Python! Enfréntate a enemigos, gestiona objetos y mejora habilidades en este emocionante juego de estrategia por turnos.
## Descripción
Este juego te **desafía** a enfrentarte a una **variedad de enemigos** en batallas por turnos. Adquiere **objetos** y derrota a los enemigos para avanzar en tu aventura.  
## Instrucciones de instalación

> **Nota:** por ahora el juego solo funciona en **Windows** (el modo auto-batalla depende de `msvcrt`, exclusivo de Windows, para poder cancelarse con la tecla `q`).

Sigue estos pasos para configurar el entorno de desarrollo en tu máquina local:
1. **Clona** el repositorio:  
Asegúrate de tener **Python 3.10 o superior instalado** en tu sistema.  
    ```bash
   git clone https://github.com/Guille87/JuegoRolTexto.git
   cd JuegoRolTexto
   ```
2. **Crea y activa un entorno virtual:**
    ```powershell
    python -m venv env
    .\env\Scripts\activate
    ```
3. **Instala el proyecto y sus dependencias:**
    ```
    pip install -e ".[dev]"
    ```
    (El extra `[dev]` añade `pytest` para poder correr los tests. Si solo quieres jugar, `pip install -e .` es suficiente.)
4. **Inicia el juego:**
    ```
    python main.py
    ```
    También puedes usar `python -m juego_rol_texto` o, tras la instalación, el comando `juego-rol-texto`.

## Tests

El proyecto usa `pytest`. Con las dependencias de desarrollo instaladas:
```
pytest
```

## Generar un ejecutable (.exe)

Para jugar sin necesidad de tener Python/PyCharm instalado, puedes empaquetar el juego con [PyInstaller](https://pyinstaller.org/):

```powershell
pip install pyinstaller
pyinstaller --onedir --name JuegoRolTexto --add-data "assets;assets" main.py
```

El resultado queda en `dist\JuegoRolTexto\` — copia esa carpeta entera (no solo el `.exe`) a donde quieras, ya que necesita los assets y las DLLs que la acompañan. Al ejecutarlo, `config.ini` y `saved_games\` se crean automáticamente junto al `.exe`.

> Usa `--onedir` (carpeta), no `--onefile`: en `--onefile` el juego se descomprime en una carpeta temporal distinta en cada arranque, así que las partidas guardadas y los ajustes de volumen no persistirían entre ejecuciones.

## Contribución
**¡Contribuciones son bienvenidas!** Si encuentras algún **problema**, tienes **sugerencias** de mejoras o deseas **contribuir** con código, no dudes en abrir un **issue** o enviar un **pull request**.
# Contacto
Para cualquier **pregunta** o **comentario**, puedes contactarme en **guillermo_amado@hotmail.es**.
