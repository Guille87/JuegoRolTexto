import contextlib
import getpass
import hashlib
import random
import sys

from juego_rol_texto.audio.resource_manager import ResourceManager
from juego_rol_texto.characters.enemies import (
    AngelCaido, Bandido, Demonio, Dragon, EspirituVengativo, Gargola, GolemDePiedra, Goblin, Huargo, Nigromante,
    Skeleton, Orc, Troll,
)
from juego_rol_texto.characters.enemies.mage import Mago
from juego_rol_texto.characters.player import Player
from juego_rol_texto.characters.stats import Stats
from juego_rol_texto.combat.battle import initiate_battle
from juego_rol_texto.config import settings
from juego_rol_texto.crafting.forge import Forge
from juego_rol_texto.items.equipment import ARMOR_SLOTS, Weapon, Armor, slot_label
from juego_rol_texto.items.materials import Material
from juego_rol_texto.persistence.save_load import save_game, load_game
from juego_rol_texto.shop.shop import Shop
from juego_rol_texto.ui import console
from juego_rol_texto.ui.formatting import print_bestiary_entry

# Instancia global de ResourceManager
resource_manager = ResourceManager()

ALL_ENEMY_NAMES = ["Goblin", "Huargo", "Esqueleto", "Bandido", "Orco", "Espíritu Vengativo", "Troll", "Gárgola",
                    "Gólem de Piedra", "Mago", "Nigromante", "Ángel Caído", "Demonio", "Dragón"]

# Hash SHA-256 de la contraseña de administrador (nunca en texto plano aquí ni
# en ningún otro archivo del repo/juego, para que no se pueda leer buscando
# entre los archivos instalados). Comparamos hashes, nunca la contraseña real.
_ADMIN_PASSWORD_HASH = "8b8a67d2a9a6bb428f10e10243b0789f37105779bb5bc2874d25cfb2578aeaec"


def _check_admin_password() -> bool:
    """Pide la contraseña de admin (sin mostrarla en pantalla si la consola lo
    permite) y compara su hash contra el guardado, sin manejar nunca el texto
    plano más que en el momento de teclearla."""
    try:
        entered = getpass.getpass("Contraseña de administrador: ")
    except Exception:
        # getpass puede fallar en consolas sin terminal real (p. ej. algunos
        # IDEs); recurrimos a una entrada visible antes que bloquear el acceso.
        entered = console.ask("Contraseña de administrador: ")
    return hashlib.sha256(entered.encode("utf-8")).hexdigest() == _ADMIN_PASSWORD_HASH


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
            "4": ("Salir", sys.exit)
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
    is_admin = False

    # Bucle while para seguir pidiendo al usuario que ingrese un nombre hasta que ingresen al menos un caracter.
    # "admin" es un nombre reservado: si se escribe pero la contraseña falla,
    # no se puede jugar con ese nombre en absoluto, hay que volver a elegir uno.
    while not name:
        candidate = console.ask("Introduce tu nombre: ").strip()
        if not candidate:
            continue

        if candidate.lower() == "admin":
            if _check_admin_password():
                is_admin = True
                name = candidate
            else:
                console.error("Contraseña incorrecta. El nombre \"admin\" está reservado, elige otro nombre.")
        else:
            name = candidate

    # --- LÓGICA DE CHEATS / ADMIN ---
    if is_admin:
        print(console.colorize("⚠️  MODO DESARROLLADOR ACTIVADO ⚠️", console.Fore.MAGENTA))
        # Stats muy altas: Vida 500, Ataque 50-70, Armadura 20
        initial_stats = Stats(500, 500, 20, 40, 10, crit_chance=0.15)
        player = Player(name, initial_stats)
        player.level = 10
        player.inventory.gold = 5000

        # Desbloqueamos todo para testear cualquier enemigo
        unlocked = list(ALL_ENEMY_NAMES)
        defeated = list(ALL_ENEMY_NAMES)
        player.enemy_kill_counts = {name: 1 for name in defeated}

    else:
        initial_stats = Stats(100, 100, 5, 10, 2, crit_chance=0.15)
        player = Player(name, initial_stats)
        unlocked = ["Goblin"]
        defeated = []

    # Datos iniciales del mundo
    game_loop(player, unlocked, defeated, is_admin=is_admin)


def load_saved_game() -> None:
    name = ""
    is_admin = False

    # Mismo nombre reservado que en Nueva Partida: cargar una partida guardada
    # como "admin" tampoco se permite sin acertar la contraseña.
    while not name:
        candidate = console.ask("Nombre del personaje a cargar: ").strip()
        if not candidate:
            continue

        if candidate.lower() == "admin":
            if _check_admin_password():
                is_admin = True
                name = candidate
            else:
                console.error("Contraseña incorrecta. El nombre \"admin\" está reservado, elige otro nombre.")
        else:
            name = candidate

    # Creamos un player temporal para que load_game lo rellene
    temp_player = Player(name, Stats(1, 1, 1, 1, 1))
    data = load_game(temp_player)

    if data:
        player_name, unlocked, defeated = data
        game_loop(temp_player, unlocked, defeated, is_admin=is_admin)


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


def game_loop(player, unlocked_enemies: list, defeated_enemies: list, is_admin: bool = False) -> None:
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
        resource_manager.update()  # Por si la pista de aventura ya ha terminado

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
            ("Bestiario", lambda: _bestiary_flow(player, defeated_enemies)),

            # Pasamos la clase Weapon a la opción de equipar arma
            ("Equipar Arma", lambda: player.inventory.equip_menu(Weapon)),

            ("Equipar Armadura", lambda: _equip_armor_flow(player)),

            ("Opciones", open_options),
            ("Guardar Partida", lambda: save_game(player, unlocked_enemies, defeated_enemies)),
            ("Volver al Menú Principal", "break"),
            ("Salir del Juego", sys.exit)
        ]

        # Panel de control total: requiere el nombre "admin" Y haber acertado
        # la contraseña al entrar (comprobado una sola vez, en start_new_game()
        # o load_saved_game(), no en cada vuelta de este bucle).
        if is_admin:
            options.insert(-2, ("Panel de Admin", lambda: _admin_panel_flow(player, unlocked_enemies, defeated_enemies)))

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


def _equip_armor_flow(player) -> None:
    """Submenú para elegir en qué hueco de armadura equipar algo."""
    while True:
        print(console.colorize("\n--- EQUIPAR ARMADURA ---", console.Fore.YELLOW))
        for idx, slot in enumerate(ARMOR_SLOTS, 1):
            equipped = player.equipped_armor.get(slot)
            label = equipped.name if equipped else "-- vacío --"
            print(f"{idx}. {slot_label(slot)}: {label}")
        print(f"{len(ARMOR_SLOTS) + 1}. Volver")

        choice = console.ask(f"\nElige un hueco (1-{len(ARMOR_SLOTS) + 1}): ")
        if not choice.isdigit():
            console.error("Entrada no válida.")
            continue

        idx = int(choice) - 1
        if idx == len(ARMOR_SLOTS):
            return
        if not (0 <= idx < len(ARMOR_SLOTS)):
            console.error("Opción fuera de rango.")
            continue

        player.inventory.equip_menu(Armor, filter_slot=ARMOR_SLOTS[idx])


def _bestiary_flow(player, defeated_enemies: list) -> None:
    """Submenú de solo lectura con la ficha de los enemigos ya derrotados alguna vez."""
    while True:
        print(console.colorize("\n--- BESTIARIO ---", console.Fore.YELLOW))

        if not defeated_enemies:
            print("Todavía no has derrotado a ningún enemigo.")
            console.ask("\nPresiona Enter para volver...")
            return

        for idx, name in enumerate(defeated_enemies, 1):
            print(f"{idx}. {name}")
        print(f"{len(defeated_enemies) + 1}. Volver")

        choice = console.ask(f"\nElige un enemigo (1-{len(defeated_enemies) + 1}): ")
        if not choice.isdigit():
            console.error("Entrada no válida.")
            continue

        idx = int(choice) - 1
        if idx == len(defeated_enemies):
            return
        if not (0 <= idx < len(defeated_enemies)):
            console.error("Opción fuera de rango.")
            continue

        enemy_name = defeated_enemies[idx]
        print_bestiary_entry(_get_enemy_instance(enemy_name), player.enemy_kill_counts.get(enemy_name, 0))
        console.ask("\nPresiona Enter para continuar...")


# Estadísticas editables desde el Panel de Admin: (atributo en Stats, etiqueta, tipo).
_ADMIN_STAT_FIELDS = [
    ("health", "Vida actual", int), ("max_health", "Vida máxima", int),
    ("min_atk", "Ataque mínimo", int), ("max_atk", "Ataque máximo", int),
    ("armor", "Armadura", int), ("magic_resist", "Resistencia Mágica", int),
    ("speed", "Velocidad", int), ("precision", "Precisión", int), ("evasion", "Evasión", int),
    ("armor_penetration", "Penetración de Armadura", int), ("magic_penetration", "Penetración Mágica", int),
    ("regen", "Regeneración", int),
    ("crit_chance", "Prob. Crítico (0.0-1.0)", float), ("crit_damage", "Daño Crítico (multiplicador, ej. 1.5)", float),
]


def _admin_panel_flow(player, unlocked_enemies: list, defeated_enemies: list) -> None:
    """Control total del personaje de pruebas 'admin': oro, nivel, cualquier
    estadística y combate directo contra cualquier enemigo sin restricciones."""
    while True:
        print(console.colorize("\n--- PANEL DE ADMIN ---", console.Fore.MAGENTA, bright=True))
        options = [
            ("Poner oro", lambda: _admin_set_gold(player)),
            ("Poner nivel", lambda: _admin_set_level(player)),
            ("Editar estadísticas", lambda: _admin_edit_stats(player)),
            ("Curación completa", lambda: _admin_full_heal(player)),
            ("Desbloquear y marcar como derrotados todos los enemigos",
             lambda: _admin_unlock_all(player, unlocked_enemies, defeated_enemies)),
            ("Combate directo contra cualquier enemigo",
             lambda: _admin_direct_battle(player, defeated_enemies, unlocked_enemies)),
            ("Conseguir todos los materiales (desbloquea también sus recetas)",
             lambda: _admin_give_all_materials(player)),
            ("Conseguir todas las armas y armaduras de los enemigos",
             lambda: _admin_give_all_equipment(player)),
            ("Volver", "break"),
        ]

        for i, (text, _) in enumerate(options, 1):
            print(f"{i}. {text}")

        choice = console.ask(f"\nElige (1-{len(options)}): ")
        if not choice.isdigit():
            console.error("Entrada no válida.")
            continue

        idx = int(choice) - 1
        if idx == len(options) - 1:
            return
        if not (0 <= idx < len(options)):
            console.error("Opción fuera de rango.")
            continue

        options[idx][1]()


def _admin_set_gold(player) -> None:
    value = console.ask(f"Nuevo oro (actual {player.inventory.gold}): ")
    if not value.isdigit():
        console.error("Entrada no válida.")
        return
    player.inventory.gold = int(value)
    console.success(f"Oro puesto a {player.inventory.gold}.")


def _admin_set_level(player) -> None:
    value = console.ask(f"Nuevo nivel (actual {player.level}): ")
    if not value.isdigit() or int(value) < 1:
        console.error("Entrada no válida.")
        return

    target = int(value)
    if target > player.level:
        # Reutiliza la curva de subida de nivel real, así las stats suben de
        # forma coherente con lo que tocaría a ese nivel en una partida normal.
        while player.level < target:
            player._level_up()
        console.success(f"Nivel subido a {player.level} (estadísticas recalculadas con la curva normal de subida).")
    elif target < player.level:
        player.level = target
        console.warning(f"Nivel bajado a {player.level} — las estadísticas no bajan solas, edítalas a mano si hace falta.")
    else:
        console.info("Ya estás en ese nivel.")


def _admin_edit_stats(player) -> None:
    while True:
        print(console.colorize("\n--- EDITAR ESTADÍSTICAS ---", console.Fore.MAGENTA))
        for idx, (attr, label, _) in enumerate(_ADMIN_STAT_FIELDS, 1):
            print(f"{idx}. {label}: {getattr(player.stats, attr)}")
        print(f"{len(_ADMIN_STAT_FIELDS) + 1}. Volver")

        choice = console.ask(f"\nElige qué editar (1-{len(_ADMIN_STAT_FIELDS) + 1}): ")
        if not choice.isdigit():
            console.error("Entrada no válida.")
            continue

        idx = int(choice) - 1
        if idx == len(_ADMIN_STAT_FIELDS):
            return
        if not (0 <= idx < len(_ADMIN_STAT_FIELDS)):
            console.error("Opción fuera de rango.")
            continue

        attr, label, cast = _ADMIN_STAT_FIELDS[idx]
        raw = console.ask(f"Nuevo valor para {label}: ")
        try:
            value = cast(raw)
        except ValueError:
            console.error("Entrada no válida.")
            continue

        setattr(player.stats, attr, value)
        # Leemos el valor de vuelta en vez de echar el que escribió el usuario:
        # "health" tiene un setter que lo recorta a max_health, por ejemplo.
        console.success(f"{label} puesto a {getattr(player.stats, attr)}.")


def _admin_full_heal(player) -> None:
    player.stats.health = player.stats.max_health
    console.success("Vida restaurada al máximo.")


def _admin_unlock_all(player, unlocked_enemies: list, defeated_enemies: list) -> None:
    for name in ALL_ENEMY_NAMES:
        if name not in unlocked_enemies:
            unlocked_enemies.append(name)
        if name not in defeated_enemies:
            defeated_enemies.append(name)
        player.enemy_kill_counts.setdefault(name, 1)
    console.success("Todos los enemigos desbloqueados y marcados como derrotados (Bestiario incluido).")


def _admin_direct_battle(player, defeated_enemies: list, unlocked_enemies: list) -> None:
    """Combate contra cualquier enemigo, sin importar si está desbloqueado todavía."""
    print(console.colorize("\n--- COMBATE DIRECTO (ADMIN) ---", console.Fore.MAGENTA))
    for idx, name in enumerate(ALL_ENEMY_NAMES, 1):
        print(f"{idx}. {name}")
    print(f"{len(ALL_ENEMY_NAMES) + 1}. Volver")

    choice = console.ask(f"\nElige un enemigo (1-{len(ALL_ENEMY_NAMES) + 1}): ")
    if not choice.isdigit():
        console.error("Entrada no válida.")
        return

    idx = int(choice) - 1
    if idx == len(ALL_ENEMY_NAMES):
        return
    if not (0 <= idx < len(ALL_ENEMY_NAMES)):
        console.error("Opción fuera de rango.")
        return

    enemy = _get_enemy_instance(ALL_ENEMY_NAMES[idx])
    initiate_battle(player, enemy, defeated_enemies, unlocked_enemies)


def _collect_all_possible_drops() -> list:
    """Fuerza random.random() a 0 mientras se piden los drops de los 14
    enemigos, para que caigan absolutamente todos los objetos posibles de
    cada uno (en vez de solo los que la tirada real habría dado)."""
    original_random = random.random
    random.random = lambda: 0.0
    try:
        drops = []
        for name in ALL_ENEMY_NAMES:
            drops.extend(_get_enemy_instance(name).drop_item())
        return drops
    finally:
        random.random = original_random


@contextlib.contextmanager
def _quiet_pickups():
    """Silencia los 'Obtenido: X' de Inventory.add_item() durante una entrega
    masiva del panel de admin — si no, imprime cientos de líneas seguidas."""
    original = console.success
    console.success = lambda *_a, **_k: None
    try:
        yield
    finally:
        console.success = original


def _admin_give_all_materials(player) -> None:
    """Da 50 unidades de cada material del juego (y, de paso, descubre las
    recetas de la herrería que los piden, ya que Inventory.add_item() marca
    un Material como descubierto la primera vez que se consigue)."""
    seen = set()
    with _quiet_pickups():
        for item in _collect_all_possible_drops():
            if isinstance(item, Material) and item.name not in seen:
                seen.add(item.name)
                for _ in range(50):
                    player.inventory.add_item(item)
    console.success(f"Conseguidas 50 unidades de cada uno de los {len(seen)} materiales del juego. "
                     f"Todas las recetas de la herrería ya deberían estar descubiertas.")


def _admin_give_all_equipment(player) -> None:
    """Da una copia de cada arma y armadura que puede soltar algún enemigo."""
    equipment = [item for item in _collect_all_possible_drops() if isinstance(item, (Weapon, Armor))]
    with _quiet_pickups():
        for item in equipment:
            player.inventory.add_item(item)
    console.success(f"Conseguidas {len(equipment)} armas y armaduras: una de cada objeto que puede soltar algún enemigo.")


def _get_enemy_instance(name: str):
    """Convierte un string en una instancia de clase de enemigo."""
    enemies = {
        "Goblin": Goblin,
        "Huargo": Huargo,
        "Esqueleto": Skeleton,
        "Bandido": Bandido,
        "Orco": Orc,
        "Espíritu Vengativo": EspirituVengativo,
        "Troll": Troll,
        "Gárgola": Gargola,
        "Gólem de Piedra": GolemDePiedra,
        "Mago": Mago,
        "Nigromante": Nigromante,
        "Ángel Caído": AngelCaido,
        "Demonio": Demonio,
        "Dragón": Dragon
    }
    # Si el nombre no existe, por defecto crea un Goblin para evitar errores
    return enemies.get(name, Goblin)()
