from colorama import Fore, Style

from assets.resources.resource_manager import ResourceManager
from characters.enemies import Goblin, Skeleton, Orc, Troll
from characters.enemies.mage import Mago
from characters.player import Player
from characters.stats import Stats
from game_core import config
from game_core.battle import initiate_battle
from items.equipment import Weapon, Armor
from save_load.save_load import save_game, load_game

# Instancia global de ResourceManager
resource_manager = ResourceManager()


def main_menu():
    resource_manager.set_mood("adventure")

    while True:
        # 1. Comprobamos si la música terminó y hay que poner otra
        resource_manager.update()

        print("\n" + "="*30)
        print(f"{Fore.YELLOW}⚔️  MENÚ PRINCIPAL  ⚔️{Style.RESET_ALL}")
        print("=" * 30)

        options = {
            "1": ("Nueva Partida", start_new_game),
            "2": ("Cargar Partida", load_saved_game),
            "3": ("Opciones", open_options),
            "4": ("Salir", exit)
        }

        for key, (text, _) in options.items():
            print(f"{key}. {text}")

        choice = input(f"\nSelecciona (1-{len(options)}): ")

        if choice in options:
            if choice == "4": break
            options[choice][1]()  # Ejecuta la función asociada
        else:
            print(f"{Fore.RED}Opción inválida.{Style.RESET_ALL}")


def start_new_game():
    print(f"\n{Fore.CYAN}--- NUEVA AVENTURA ---{Style.RESET_ALL}")
    name = ""  # Inicializa el nombre del jugador como una cadena vacía

    # Bucle while para seguir pidiendo al usuario que ingrese un nombre hasta que ingresen al menos un caracter
    while not name:
        name = input("Introduce tu nombre: ").strip()

    # --- LÓGICA DE CHEATS / ADMIN ---
    # TODO: eliminar después de hacer pruebas
    if name.lower() == "admin":  # Puedes poner el nombre que prefieras
        print(f"{Fore.MAGENTA}⚠️  MODO DESARROLLADOR ACTIVADO ⚠️{Style.RESET_ALL}")
        # Stats muy altas: Vida 500, Ataque 50-70, Defensa 20
        initial_stats = Stats(500, 500, 20, 40, 10)
        player = Player(name, initial_stats)
        player.level = 10
        player.inventory.gold = 5000

        # Desbloqueamos todo para testear cualquier enemigo
        unlocked = ["Goblin", "Esqueleto", "Orco", "Troll", "Mago"]
        defeated = ["Goblin", "Esqueleto", "Orco", "Troll"]

    else:
        initial_stats = Stats(100, 100, 5, 10, 2)
        player = Player(name, initial_stats)
        unlocked = ["Goblin"]
        defeated = []

    # Datos iniciales del mundo
    game_loop(player, unlocked, defeated)


def load_saved_game():
    name = ""
    while not name:  # FALLO 3 (Validación): No permitir nombre vacío al cargar
        name = input("Nombre del personaje a cargar: ").strip()

    # Creamos un player temporal para que load_game lo rellene
    temp_player = Player(name, Stats(1, 1, 1, 1, 1))
    data = load_game(temp_player)

    if data:
        player_name, unlocked, defeated = data
        game_loop(temp_player, unlocked, defeated)


def open_options():
    # Cargamos volúmenes actuales
    music_vol, sfx_vol = config.load_config()

    while True:
        print(f"\n{Fore.YELLOW}--- AJUSTES DE AUDIO ---{Style.RESET_ALL}")
        print(f"1. Música (Actual: {int(music_vol * 10)})")
        print(f"2. Efectos (Actual: {int(sfx_vol * 10)})")
        print("3. Volver")

        choice = input("\nSelecciona una opción: ")

        if choice == "1":
            vol = input("Volumen Música (0-10): ")
            if vol.isdigit() and 0 <= int(vol) <= 10:
                music_vol = int(vol) / 10
                resource_manager.set_volume_music(music_vol)
                config.save_config(music_vol, sfx_vol)
                print(f"{Fore.GREEN}Música ajustada.{Style.RESET_ALL}")

        elif choice == "2":
            vol = input("Volumen Efectos (0-10): ")
            if vol.isdigit() and 0 <= int(vol) <= 10:
                sfx_vol = int(vol) / 10
                resource_manager.set_volume_sfx(sfx_vol)
                config.save_config(music_vol, sfx_vol)
                resource_manager.play_sfx("level_up")  # Feedback auditivo
                print(f"{Fore.GREEN}Efectos ajustados.{Style.RESET_ALL}")

        elif choice == "3":
            break


def game_loop(player, unlocked_enemies, defeated_enemies):
    """Bucle principal de la estancia en el mundo"""
    def start_battle_flow():
        print(f"\n{Fore.YELLOW}--- SELECCIONAR ENEMIGO ---{Style.RESET_ALL}")

        # Mostramos la lista de enemigos desbloqueados con números
        for enemy_idx, name in enumerate(unlocked_enemies, 1):
            # Opcional: poner un check si ya fue derrotado antes
            status = "✅" if name in defeated_enemies else "❌"
            print(f"{enemy_idx}. {name} {status}")

        print(f"{len(unlocked_enemies) + 1}. Volver")

        battle_choice = input(f"\nElige a tu oponente (1-{len(unlocked_enemies) + 1}): ")

        if battle_choice.isdigit():
            target_idx = int(battle_choice) - 1

            # Si elige un enemigo de la lista
            if 0 <= target_idx < len(unlocked_enemies):
                enemy_name = unlocked_enemies[target_idx]
                enemy_obj = _get_enemy_instance(enemy_name)
                # Iniciamos la batalla
                initiate_battle(player, enemy_obj, defeated_enemies, unlocked_enemies)

            # Si elige la opción de volver
            elif target_idx == len(unlocked_enemies):
                return
            else:
                print(f"{Fore.RED}Opción fuera de rango.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Entrada no válida.{Style.RESET_ALL}")

    while True:
        print("\n" + "=" * 40)
        print(f"{Fore.CYAN}ESTADO: {player.name} | Nivel: {player.level}{Style.RESET_ALL}")
        print("=" * 40)

        # Usamos una lista de tuplas para mantener el orden de tus 10 opciones
        options = [
            ("Luchar", start_battle_flow),
            ("Inventario", lambda: player.inventory.show_inventory(mode="use")),
            ("Tienda", lambda: print(f"{Fore.YELLOW}Tienda no implementada...{Style.RESET_ALL}")),
            ("Estadísticas", player.show_stats),

            # Pasamos la clase Weapon a la opción 5
            ("Equipar Arma", lambda: player.inventory.equip_menu(Weapon)),

            # Pasamos la clase Armor a la opción 6
            ("Equipar Armadura", lambda: player.inventory.equip_menu(Armor)),

            ("Opciones", open_options),
            ("Guardar Partida", lambda: save_game(player, unlocked_enemies, defeated_enemies)),
            ("Volver al Menú Principal", "break"),
            ("Salir del Juego", exit)
        ]

        for i, (text, _) in enumerate(options, 1):
            print(f"{i}. {text}")

        choice = input(f"\nElige (1-{len(options)}): ")

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                action = options[idx][1]
                if action == "break": break
                action()
                if idx in [1, 3]: input("\nPresiona Enter para continuar...")
            else:
                print(f"{Fore.RED}Opción fuera de rango.{Style.RESET_ALL}")

def _get_enemy_instance(name):
    """Convierte un string en una instancia de clase de enemigo."""
    enemies = {
        "Goblin": Goblin,
        "Esqueleto": Skeleton,
        "Orco": Orc,
        "Troll": Troll,
        "Mago": Mago
    }
    # Si el nombre no existe, por defecto crea un Goblin para evitar errores
    return enemies.get(name, Goblin)()

def smart_input(prompt):
    """Llama al gestor de recursos antes de esperar la entrada del usuario."""
    from assets.resources.resource_manager import ResourceManager
    ResourceManager().update() # Revisamos la música justo antes de pausar el programa
    return input(prompt)