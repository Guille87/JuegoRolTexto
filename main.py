import os

import pygame
from colorama import init

from assets.resources.resource_manager import ResourceManager
from game_core.menu import main_menu

# Inicializa colorama
init()

# Inicializa pygame
pygame.init()

# Directorio de recursos
DIR_RECURSOS = os.path.join(os.path.dirname(os.path.abspath(__file__)))

# Sonidos
SONIDOS = {
    "a_robust_crew": "assets\\music\\A-Robust-Crew.ogg",
    "ale_and_anecdotes": "assets\\music\\Ale-and-Anecdotes.ogg",
    "scaring_Crows": "assets\\music\\Scaring-Crows.ogg",
    "level_up": "assets\\sfx\\level-up.ogg",
    "metal_hit_woosh": "assets\\sfx\\metal-hit-woosh.ogg",
    "sword_slash_swoosh": "assets\\sfx\\sword-slash-swoosh.ogg",
}


def cargar_sonidos(resource_manager, directorio, sonidos):
    for nombre, ruta in sonidos.items():
        resource_manager.load_sound(nombre, os.path.join(directorio, ruta))


def main():
    # Cargar recursos
    resource_manager = ResourceManager()
    cargar_sonidos(resource_manager, DIR_RECURSOS, SONIDOS)

    # Mostrar el menú
    main_menu()


if __name__ == "__main__":
    main()
