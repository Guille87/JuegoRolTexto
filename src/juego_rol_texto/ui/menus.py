from juego_rol_texto.audio.resource_manager import ResourceManager
from juego_rol_texto.characters.enemies import Goblin, Skeleton, Orc, Troll
from juego_rol_texto.characters.enemies.mage import Mago
from juego_rol_texto.characters.player import Player
from juego_rol_texto.characters.stats import Stats
from juego_rol_texto.combat.battle import initiate_battle
from juego_rol_texto.config import settings
from juego_rol_texto.crafting.forge import Forge
from juego_rol_texto.items.equipment import Weapon, Armor
from juego_rol_texto.persistence.save_load import save_game, load_game
from juego_rol_texto.shop.shop import Shop
from juego_rol_texto.ui import console

# Instancia global de ResourceManager
resource_manager = ResourceManager()


def main_menu() -> None:
    resource_manager.set_mood("adventure")

    while True:
        # 1. Comprobamos si la música terminó y hay que poner otra
        resource_manager.update()

        print("\n" + "=" * 30)
        print(console.colorize("⚔️  MENÚ PRINCIPAL  ⚔️", console.Fore.YELLOW))
        print("=" * 30)

        options = {
            "1": ("Nueva Partida", start_new_game),
            "2": ("Cargar Partida", load_saved_game),
            "3": ("Opciones", open_options),
            "4": ("Salir", exit)
        }

        for key, (text, _) in options.items():
            print(f"{key}. {text}")

        choice = console.ask(f"\nSelecciona (1-{len(options)}): ")

        if choice in options:
            if choice == "4": break
            options[choice][1]()  # Ejecuta la función asociada
        else:
            console.error("Opción inválida.")


def start_new_game() -> None:
    print(console.colorize("\n--- NUEVA AVENTURA ---", console.Fore.CYAN))
    name = ""  # Inicializa el nombre del jugador como una cadena vacía

    # Bucle while para seguir pidiendo al usuario que ingrese un nombre hasta que ingresen al menos un caracter
    while not name:
        name = console.ask("Introduce tu nombre: ").strip()

    # --- LÓGICA DE CHEATS / ADMIN ---
    # TODO: eliminar después de hacer pruebas
    if name.lower() == "admin":  # Puedes poner el nombre que prefieras
        print(console.colorize("⚠️  MODO DESARROLLADOR ACTIVADO ⚠️", console.Fore.MAGENTA))
        # Stats muy altas: Vida 500, Ataque 50-70, Armadura 20
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


def load_saved_game() -> None:
    name = ""
    while not name:  # No permitir nombre vacío al cargar
        name = console.ask("Nombre del personaje a cargar: ").strip()

    # Creamos un player temporal para que load_game lo rellene
    temp_player = Player(name, Stats(1, 1, 1, 1, 1))
    data = load_game(temp_player)

    if data:
        player_name, unlocked, defeated = data
        game_loop(temp_player, unlocked, defeated)


def open_options() -> None:
    # Cargamos volúmenes actuales
    music_vol, sfx_vol = settings.load_config()

    while True:
        print(console.colorize("\n--- AJUSTES DE AUDIO ---", console.Fore.YELLOW))
        print(f"1. Música (Actual: {int(music_vol * 10)})")
        print(f"2. Efectos (Actual: {int(sfx_vol * 10)})")
        print("3. Volver")

        choice = console.ask("\nSelecciona una opción: ")

        if choice == "1":
            vol = console.ask("Volumen Música (0-10): ")
            if vol.isdigit() and 0 <= int(vol) <= 10:
                music_vol = int(vol) / 10
                resource_manager.set_volume_music(music_vol)
                settings.save_config(music_vol, sfx_vol)
                console.success("Música ajustada.")

        elif choice == "2":
            vol = console.ask("Volumen Efectos (0-10): ")
            if vol.isdigit() and 0 <= int(vol) <= 10:
                sfx_vol = int(vol) / 10
                resource_manager.set_volume_sfx(sfx_vol)
                settings.save_config(music_vol, sfx_vol)
                resource_manager.play_sfx("level_up")  # Feedback auditivo
                console.success("Efectos ajustados.")

        elif choice == "3":
            break


def game_loop(player, unlocked_enemies: list, defeated_enemies: list) -> None:
    """Bucle principal de la estancia en el mundo"""
    def start_battle_flow():
        print(console.colorize("\n--- SELECCIONAR ENEMIGO ---", console.Fore.YELLOW))

        # Mostramos la lista de enemigos desbloqueados con números
        for enemy_idx, name in enumerate(unlocked_enemies, 1):
            # Opcional: poner un check si ya fue derrotado antes
            status = "✅" if name in defeated_enemies else "❌"
            print(f"{enemy_idx}. {name} {status}")

        print(f"{len(unlocked_enemies) + 1}. Volver")

        battle_choice = console.ask(f"\nElige a tu oponente (1-{len(unlocked_enemies) + 1}): ")

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
                console.error("Opción fuera de rango.")
        else:
            console.error("Entrada no válida.")

    while True:
        print("\n" + "=" * 40)
        print(console.colorize(f"ESTADO: {player.name} | Nivel: {player.level}", console.Fore.CYAN))
        print("=" * 40)

        # Usamos una lista de tuplas para mantener el orden de las opciones
        options = [
            ("Luchar", start_battle_flow),
            ("Inventario", lambda: player.inventory.show_inventory(mode="use")),
            ("Tienda", lambda: Shop().open(player)),
            ("Herrería", lambda: Forge().open(player)),
            ("Estadísticas", player.show_stats),

            # Pasamos la clase Weapon a la opción de equipar arma
            ("Equipar Arma", lambda: player.inventory.equip_menu(Weapon)),

            # Pasamos la clase Armor a la opción de equipar armadura
            ("Equipar Armadura", lambda: player.inventory.equip_menu(Armor)),

            ("Opciones", open_options),
            ("Guardar Partida", lambda: save_game(player, unlocked_enemies, defeated_enemies)),
            ("Volver al Menú Principal", "break"),
            ("Salir del Juego", exit)
        ]

        for i, (text, _) in enumerate(options, 1):
            print(f"{i}. {text}")

        choice = console.ask(f"\nElige (1-{len(options)}): ")

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                action = options[idx][1]
                if action == "break": break
                action()
                if idx in [1, 4]: console.ask("\nPresiona Enter para continuar...")
            else:
                console.error("Opción fuera de rango.")


def _get_enemy_instance(name: str):
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


def smart_input(prompt: str) -> str:
    """Llama al gestor de recursos antes de esperar la entrada del usuario."""
    ResourceManager().update()  # Revisamos la música justo antes de pausar el programa
    return console.ask(prompt)
