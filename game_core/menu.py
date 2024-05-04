import math

from colorama import Fore, Style

from assets.resources.resource_manager import ResourceManager
from characters.character import Player
from game_core import config
from game_core.battle import initiate_battle
from items.item import Weapon, Armor
from save_load.save_load import save_game, load_game
from settings_admin import show_settings_window

# Instancia global de ResourceManager
resource_manager = ResourceManager()


def main_menu():
    while True:
        # Cargar la configuración de música y sonido
        music_volume, sound_volume = config.load_config()

        # Detener la música menos la que voy a reproducir a continuación
        resource_manager.stop_all_music("a_robust_crew")
        # Iniciar música de fondo si aún no se ha iniciado
        if not resource_manager.is_music_playing("a_robust_crew"):
            resource_manager.play_music("a_robust_crew", loops=-1)

        print("="*60)
        print("Menú principal:")
        options = ["Iniciar partida nueva", "Cargar partida", "Opciones", "Salir"]
        print_main_menu_options(options)

        choice = input(f"Elige una opción (1-{len(options)}): ")

        if choice == "1":
            start_new_game(music_volume, sound_volume)
        elif choice == "2":
            load_saved_game(music_volume, sound_volume)
        elif choice == "3":
            music_volume, sound_volume = music_sound_options(music_volume, sound_volume)
            # Guardar la configuración de música y sonido
            config.save_config(music_volume, sound_volume)
        elif choice == "4":
            print("¡Hasta la próxima!")
            break
        else:
            print_invalid_option(options)


def print_main_menu_options(options):
    for index, option in enumerate(options, start=1):
        print(f"{index}. {option}")


def start_new_game(music_volume, sound_volume):
    player_name = ""  # Inicializa el nombre del jugador como una cadena vacía
    print("¡Bienvenido al juego!")
    # Bucle while para seguir pidiendo al usuario que ingrese un nombre hasta que ingresen al menos un caracter
    while len(player_name) == 0:
        player_name = input("Por favor, introduce tu nombre: ")
        if len(player_name) == 0:
            print(f"{Fore.RED}El nombre debe contener al menos un caracter. Por favor, inténtalo de nuevo.{Style.RESET_ALL}")
    unlocked_enemies = ["Goblin"]  # Lista de enemigos desbloqueados al inicio

    # Inicializa la lista de enemigos derrotados si no hay datos guardados
    defeated_enemies = []

    # Creación del jugador
    player = Player(player_name)

    # Iniciar el juego
    start_game(player, unlocked_enemies, defeated_enemies, music_volume, sound_volume)


def load_saved_game(music_volume, sound_volume):
    # Preguntar al jugador por su nombre para cargar su partida guardada
    player_name = input("Por favor, introduce tu nombre de jugador: ")

    # Crear un objeto de jugador con el nombre proporcionado
    player = Player(player_name)

    # Cargar la partida guardada del jugador específico
    player_data = load_game(player)

    if player_data:
        player_name, unlocked_enemies, defeated_enemies = player_data
        print(f"¡Bienvenido de nuevo, {player_name}!")
        # Iniciar el juego con los datos cargados
        start_game(player, unlocked_enemies, defeated_enemies, music_volume, sound_volume)


def music_sound_options(music_volume, sound_volume):
    # Construir las rutas a los efectos de sonido
    level_up = resource_manager.get_sound("level_up")
    # Lista de efectos de sonido
    sound_effects = [level_up]

    print("=" * 60)
    options = ["Música", "Sonido"]
    print("Opciones:")
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")

    choice = input(f"Elige una opción (1-{len(options)}): ")
    if choice.isdigit():
        choice = int(choice)
        if 1 <= choice <= len(options):
            selected_option = options[choice - 1]
            print(f"Has seleccionado: {Fore.LIGHTGREEN_EX}{Style.BRIGHT}{selected_option}{Style.RESET_ALL}")
            if selected_option == "Música":
                # Mostrar el volumen actual
                current_volume = math.ceil(music_volume * 10)
                print(f"{Fore.CYAN}{Style.BRIGHT}Volumen de la música actual: {current_volume}{Style.RESET_ALL}")
                volume = input("Selecciona el volumen de la música (0-10): ")
                if volume.isdigit():
                    volume = int(volume)
                    if 0 <= volume <= 10:
                        music_volume = volume / 10
                        resource_manager.set_all_music_volume(music_volume)
                        print(f"{Fore.GREEN}Volumen de la música ajustado a {Style.BRIGHT}{volume}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}{Style.BRIGHT}El volumen de la música debe estar entre 1 y 10.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}{Style.BRIGHT}Por favor, ingresa un número válido para el volumen de la música.{Style.RESET_ALL}")
            elif selected_option == "Sonido":
                # Mostrar el volumen actual
                current_volume = math.ceil(sound_volume * 10)
                print(f"{Fore.CYAN}{Style.BRIGHT}Volumen de sonido actual: {current_volume}{Style.RESET_ALL}")
                volume = input("Selecciona el volumen del sonido (0-10): ")
                if volume.isdigit():
                    volume = int(volume)
                    if 0 <= volume <= 10:
                        sound_volume = volume / 10
                        for sound in sound_effects:
                            sound.set_volume(sound_volume)
                            volume_change_sound = resource_manager.get_sound("level_up")
                            volume_change_sound.set_volume(sound_volume)
                            volume_change_sound.play()
                            print(f"{Fore.GREEN}Volumen del sonido ajustado a {Style.BRIGHT}{volume}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}{Style.BRIGHT}El volumen del sonido debe estar entre 0 y 10.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}{Style.BRIGHT}Por favor, ingresa un número válido para el volumen del sonido.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{Style.BRIGHT}Opción no válida. Por favor, selecciona un número dentro del rango proporcionado.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}{Style.BRIGHT}Por favor, ingresa un número válido.{Style.RESET_ALL}")

    # Devolver los volúmenes actualizados
    return music_volume, sound_volume


def start_game(player, unlocked_enemies, defeated_enemies, music_volume, sound_volume):
    if not defeated_enemies:  # Verifica si la lista de enemigos derrotados está vacía
        defeated_enemies = []  # Inicializa la lista solo si está vacía

    while True:
        # Detener la música menos la que voy a reproducir a continuación
        resource_manager.stop_all_music("a_robust_crew")
        # Iniciar música de fondo si aún no se ha iniciado
        if not resource_manager.is_music_playing("a_robust_crew"):
            resource_manager.play_music("a_robust_crew", loops=-1)

        print("="*60)
        options = ["Luchar", "Inventario", "Tienda", "Estadísticas", "Equipar arma", "Equipar armadura", "Opciones", "Guardar partida",
                   "Volver al menú principal", "Salir del juego"]

        if player.name == "asdasd":
            options.append("Configuracion")

        print_game_menu_options(options)
        choice = input(f"Elige una opción (1-{len(options)}): ")

        if choice == "1":
            initiate_battle(player, unlocked_enemies, defeated_enemies)
        elif choice == "2":
            player.show_inventory()
            input(f"Presiona {Fore.GREEN}Enter{Style.RESET_ALL} para continuar...")
        elif choice == "3":
            print(f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}¡Opción de tienda aún no implementada! Próximamente disponible.{Style.RESET_ALL}")
        elif choice == "4":
            player.show_stats()
        elif choice == "5":
            # Mostrar inventario y equipar arma solo si hay armas disponibles
            weapons_in_inventory = [item for item in player.inventory.items if isinstance(item, Weapon)]
            player.show_inventory()
            if weapons_in_inventory:
                try:
                    weapon_index = int(input("Selecciona el número del arma que deseas equipar: ")) - 1
                    player.equip_weapon_by_index(weapon_index)
                except ValueError:
                    print("¡Ingresa un número válido!")
            else:
                print(f"{Fore.RED}{Style.BRIGHT}No tienes armas en tu inventario para equipar.{Style.RESET_ALL}")
        elif choice == "6":
            # Mostrar inventario y equipar armadura solo si hay armaduras disponibles
            armors_in_inventory = [item for item in player.inventory.items if isinstance(item, Armor)]
            if armors_in_inventory:
                player.show_inventory()
                try:
                    armor_index = int(input("Selecciona el número de la armadura que deseas equipar: ")) - 1
                    player.equip_armor_by_index(armor_index)
                except ValueError:
                    print("¡Ingresa un número válido!")
            else:
                print(f"{Fore.RED}{Style.BRIGHT}No tienes armaduras en tu inventario para equipar.{Style.RESET_ALL}")
        elif choice == "7":
            music_volume, sound_volume = music_sound_options(music_volume, sound_volume)
            # Guardar la configuración de música y sonido
            config.save_config(music_volume, sound_volume)
        elif choice == "8":
            save_game(player, unlocked_enemies, defeated_enemies)
            print("¡Partida guardada!")
        elif choice == "9":
            print("Volviendo al menú principal...")
            break  # Sale del bucle actual y vuelve al menú principal
        elif choice == "10":
            print("¡Hasta la próxima!")
            # input("Pulsa cualquier tecla para salir...")
            exit()  # Sale del juego directamente
        elif choice == "11" and player.name == "asdasd":
            if player.name == "asdasd":
                show_settings_window(player)
        else:
            print_invalid_option(options)


def print_game_menu_options(options):
    print("Menú del juego:")
    for index, option in enumerate(options, start=1):
        print(f"{index}. {option}")


def print_invalid_option(options):
    print(f"{Fore.RED}Opción no válida. Por favor, elige una de las opciones (1-{len(options)}).{Style.RESET_ALL}")
