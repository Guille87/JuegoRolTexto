import os
import pygame
from colorama import init, Fore, Style

from assets.resources.resource_manager import ResourceManager
from game_core.menu import main_menu
from game_core import config  # Importamos para cargar el volumen guardado

# Configuraciones de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

AUDIO_ASSETS = {
    "music": {
        "a_robust_crew": "music/A-Robust-Crew.ogg",
        "ale_and_anecdotes": "music/Ale-and-Anecdotes.ogg",
        "Wanderers_Hearth": "music/Wanderers-Hearth.ogg",
        "scaring_crows": "music/Scaring-Crows.ogg",
        "Siege_of_the_Black_Gate": "music/Siege-of-the-Black-Gate.ogg",
    },
    "sfx": {
        "level_up": "sfx/level-up.ogg",
        "hit": "sfx/metal-hit-woosh.ogg",
        "slash": "sfx/sword-slash-swoosh.ogg",
        "fireball": "sfx/fireball-variation1.ogg",
        "lightning": "sfx/lightning-variation1.ogg",
    }
}


def setup_resources():
    """Inicializa el ResourceManager y carga los archivos de audio."""
    rm = ResourceManager()

    # 1. Cargar volúmenes desde config.ini antes de cargar audios
    music_vol, sfx_vol = config.load_config()
    rm.set_volume_music(music_vol)
    rm.set_volume_sfx(sfx_vol)

    # 2. Cargar Música
    for name, relative_path in AUDIO_ASSETS["music"].items():
        full_path = os.path.join(ASSETS_DIR, relative_path)
        rm.load_audio(name, full_path, is_music=True)

    # 3. Cargar Efectos
    for name, relative_path in AUDIO_ASSETS["sfx"].items():
        full_path = os.path.join(ASSETS_DIR, relative_path)
        rm.load_audio(name, full_path, is_music=False)


def main():
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
        print(f"\n{Fore.RED}Error crítico durante la ejecución: {e}{Style.RESET_ALL}")
    finally:
        pygame.mixer.quit()
        pygame.quit()


if __name__ == "__main__":
    main()