import pygame
from colorama import init

from juego_rol_texto.audio.catalog import AUDIO_ASSETS
from juego_rol_texto.audio.resource_manager import ResourceManager
from juego_rol_texto.config import paths, settings
from juego_rol_texto.ui import console
from juego_rol_texto.ui.menus import main_menu


def setup_resources() -> None:
    """Inicializa el ResourceManager y carga los archivos de audio."""
    rm = ResourceManager()

    # 1. Cargar volúmenes desde config.ini antes de cargar audios
    music_vol, sfx_vol = settings.load_config()
    rm.set_volume_music(music_vol)
    rm.set_volume_sfx(sfx_vol)

    # 2. Cargar Música
    for name, relative_path in AUDIO_ASSETS["music"].items():
        full_path = paths.ASSETS_DIR / relative_path
        rm.load_audio(name, str(full_path), is_music=True)

    # 3. Cargar Efectos
    for name, relative_path in AUDIO_ASSETS["sfx"].items():
        full_path = paths.ASSETS_DIR / relative_path
        rm.load_audio(name, str(full_path), is_music=False)


def main() -> None:
    # Inicialización de librerías
    init(autoreset=True)  # Colorama
    pygame.init()
    pygame.mixer.init()

    try:
        setup_resources()

        # Iniciar música inicial
        rm = ResourceManager()
        rm.update()

        # Lanzar el bucle principal del juego (Menú)
        main_menu()

    except Exception as e:
        console.error(f"\nError crítico durante la ejecución: {e}")
    finally:
        pygame.mixer.quit()
        pygame.quit()


if __name__ == "__main__":
    main()
