import msvcrt
import random
import time

from juego_rol_texto.audio.resource_manager import ResourceManager
from juego_rol_texto.ui import console
from juego_rol_texto.ui.formatting import print_player_enemy_info, print_status

# Mapa de progresión: Al derrotar a la LLAVE, se desbloquea el VALOR
ENEMY_PROGRESSION = {
    "Goblin": "Esqueleto",
    "Esqueleto": "Orco",
    "Orco": "Troll",
    "Troll": "Mago",
    "Mago": None  # El Mago es el último por ahora
}


def check_for_interrupt() -> bool:
    """Retorna True si el usuario ha pulsado 'q' o 'Q'."""
    if msvcrt.kbhit():  # ¿Se ha pulsado alguna tecla?
        key = msvcrt.getch().decode('utf-8').lower()
        if key == 'q':
            return True
    return False


def initiate_battle(player, enemy, defeated_enemies: list, unlocked_enemies: list) -> None:
    """Punto de entrada principal para cualquier combate."""
    print("=" * 60)
    print(f"{console.colorize(f'¡Ha comenzado la batalla contra {enemy.name}!', console.Fore.WHITE, bright=True)}")
    player.in_combat = True

    rm = ResourceManager()
    # Sincronizamos el manager con la batalla
    rm.set_mood("battle", enemy.name)
    rm.update()  # Forzamos el cambio de música inmediato

    # Música específica según el enemigo
    if enemy.name == "Orco":
        rm.play_music("scaring_crows")
    elif enemy.name == "Mago":
        rm.play_music("Siege_of_the_Black_Gate")

    # --- LÓGICA DE EMBOSCADA (Ataque previo) ---
    if hasattr(enemy, 'check_ambush'):
        if enemy.check_ambush(player):
            # Mostramos el estado inmediatamente después del daño de emboscada
            print_status(player, enemy, defeated_enemies)

        # Si el jugador muere por la emboscada (poco probable pero posible)
        if not player.is_alive():
            _handle_defeat(player)
            _restore_player(player, {"atk": (player.stats.min_atk, player.stats.max_atk), "armor": player.stats.armor})
            return

    # Guardamos estado inicial para restaurar después
    snapshot = {
        "atk": (player.stats.min_atk, player.stats.max_atk),
        "armor": player.stats.armor
    }

    is_auto = False
    while player.is_alive() and enemy.is_alive():
        rm.update()
        # --- INICIO DE TURNO (Procesar veneno, quemaduras, parálisis) ---
        can_act = player.on_turn_start()
        turn_consumed = False

        # --- COMPROBAR CANCELACIÓN DE AUTO ---
        if is_auto:
            if check_for_interrupt():
                is_auto = False
                console.warning("\n🛑 ¡Auto-batalla cancelada! Volviendo al menú...")
                time.sleep(1)  # Pausa para que el usuario lo vea

        action = None
        if player.is_alive():  # El veneno podría haberlo matado en on_turn_start
            if not is_auto:
                if can_act:
                    action = _player_menu(player, enemy, defeated_enemies)
                    if action == "huir":
                        console.warning("Has huido del combate...")
                        break

                    if action == "auto":
                        is_auto = True
                        print(console.colorize(">>> MODO AUTO: ACTIVADO. (Pulsa 'Q' para detener)", console.Fore.CYAN))

                    if action == "objeto_usado":
                        turn_consumed = True
                else:
                    console.ask(f"\n{console.colorize('Presiona Enter para pasar turno...', console.Fore.YELLOW)}")

            # --- TURNO DEL JUGADOR (Si puede actuar) ---
            if (is_auto or action == "atacar") and can_act and not turn_consumed:
                _execute_turn(player, enemy, defeated_enemies)

        if not enemy.is_alive():
            # CAPTURAMOS LOS NUEVOS STATS SI SUBE DE NIVEL
            new_atk, new_armor = _handle_victory(player, enemy, defeated_enemies, unlocked_enemies)

            # SI SUBIÓ DE NIVEL, ACTUALIZAMOS EL SNAPSHOT
            if player.just_leveled_up:
                snapshot["atk"] = new_atk
                snapshot["armor"] = new_armor
            break

        # --- TURNO DEL ENEMIGO ---
        if enemy.is_alive():
            time.sleep(1)
            print(f"\nTurno de {console.colorize(enemy.name, console.Fore.RED)}...")
            enemy.perform_turn(player)
            print_status(player, enemy, defeated_enemies)

        if not player.is_alive():
            _handle_defeat(player)
            break

        # --- FIN DE TURNO (Reducir duración de efectos) ---
        player.on_turn_end()
        if hasattr(enemy, 'on_turn_end'):
            enemy.on_turn_end()

        # Si estamos en modo auto, esperamos para poder leer el resultado
        if is_auto and player.is_alive() and enemy.is_alive():
            print(console.colorize("(Esperando siguiente turno...)", console.Fore.BLACK, bright=True))
            time.sleep(1)  # Pequeña pausa para asimilar el daño recibido

    _restore_player(player, snapshot)
    player.in_combat = False
    # Al salir, volvemos a modo aventura
    rm.set_mood("adventure")
    rm.play_random_adventure_music()


def _player_menu(player, enemy, defeated_enemies: list) -> str:
    """Maneja la interfaz de usuario durante el combate."""
    while True:
        options = ["1. Atacar", "2. Objetos", "3. Info", "4. Huir"]
        if enemy.name in defeated_enemies:
            options.append("5. Auto-Batalla")

        print("\n" + " | ".join(options))
        choice = console.ask("Selección: ")

        if choice == "1":
            return "atacar"
        elif choice == "2":
            # Si el menú de equipo devuelve True es que se usó un objeto
            if player.inventory.equip_menu():
                return "objeto_usado"
        elif choice == "3":
            print_player_enemy_info(player, enemy, defeated_enemies)
            continue
        elif choice == "4":
            return "huir"
        elif choice == "5" and enemy.name in defeated_enemies:
            return "auto"
        else:
            console.error("Opción no válida.")


def _execute_turn(attacker, defender, defeated_enemies: list) -> None:
    """Ejecuta un ataque estándar calculando daño y stats."""
    from juego_rol_texto.characters.player import Player
    if isinstance(attacker, Player):
        rm = ResourceManager()
        # Elegimos al azar entre los nombres en AUDIO_ASSETS
        sonido_ataque = random.choice(["hit", "slash"])
        rm.play_sfx(sonido_ataque)

    # Verificación de seguridad: si attacker es una lista, tenemos un problema de lógica previo
    if isinstance(attacker, list):
        console.error("Error Interno: El atacante es una lista, no un objeto.")
        return

    damage = attacker.get_attack_damage()
    element = attacker.get_equipped_element() if isinstance(attacker, Player) else None

    # Golpe crítico: solo el jugador puede critear (los enemigos no tienen esta stat)
    is_crit = isinstance(attacker, Player) and random.random() < attacker.get_total_crit_chance()
    if is_crit:
        damage = int(damage * attacker.get_total_crit_damage())

    # ¿Es el defensor débil a este elemento? Lo comprobamos antes de aplicar el daño
    # para poder mostrar el mensaje de "supereficaz" (take_damage no expone esa info).
    weaknesses = getattr(type(defender), "ELEMENTAL_WEAKNESSES", {})
    is_super_effective = bool(element) and weaknesses.get(element, 1.0) > 1.0

    final_dmg = defender.take_damage(damage, defeated_enemies=defeated_enemies, element=element)

    if is_crit:
        print(console.colorize("¡Golpe crítico!", console.Fore.YELLOW, bright=True))

    if is_super_effective:
        print(console.colorize(
            f"¡Es supereficaz! El {element} causa estragos en {defender.name}.", console.Fore.RED, bright=True
        ))

    if final_dmg > 0:
        print(f"{console.colorize(attacker.name, console.Fore.GREEN)} ataca a "
              f"{console.colorize(defender.name, console.Fore.RED)} y hace "
              f"{console.colorize(str(final_dmg), console.Fore.YELLOW)} de daño")
    else:
        print(f"{console.colorize(defender.name, console.Fore.BLUE)} ha bloqueado el ataque.")

    from juego_rol_texto.characters.player import Player
    if isinstance(attacker, Player):
        print_status(attacker, defender, defeated_enemies)
    else:
        print_status(defender, attacker, defeated_enemies)


def _handle_victory(player, enemy, defeated_enemies: list, unlocked_enemies: list) -> tuple:
    print(f"\n{console.colorize(f'¡VICTORIA! {enemy.name} ha sido derrotado.', console.Fore.YELLOW, bright=True)}")

    if enemy.name not in defeated_enemies:
        defeated_enemies.append(enemy.name)

        # Consultamos si este enemigo desbloquea a otro
        next_enemy = ENEMY_PROGRESSION.get(enemy.name)

        if next_enemy and next_enemy not in unlocked_enemies:
            unlocked_enemies.append(next_enemy)
            print(console.colorize(f"✨ ¡NUEVO ENEMIGO DESBLOQUEADO: {next_enemy}!", console.Fore.MAGENTA))

    # Recompensa de Oro
    gold = enemy.get_gold_drop()
    player.inventory.gold += gold
    print(f"💰 Oro obtenido: {console.colorize(str(gold), console.Fore.YELLOW)}")

    # Experiencia y Nivel
    old_level = player.level
    player.gain_experience(gold * 2)

    # Comprobamos si subió de nivel
    player.just_leveled_up = player.level > old_level

    # Recompensa de Ítems (Drops)
    drops = enemy.drop_item()
    if drops:
        print(console.colorize("\n--- BOTÍN ENCONTRADO ---", console.Fore.CYAN))
        for item in drops:
            player.inventory.add_item(item)
            # Imprimimos solo aquí el mensaje del objeto encontrado
            print(f"📦 {console.colorize(item.name, console.Fore.GREEN)}: {item.description}")

    # Si sube de nivel, devolvemos el nuevo snapshot de stats
    return (player.stats.min_atk, player.stats.max_atk), player.stats.armor


def _handle_defeat(player) -> None:
    """Gestiona lo que ocurre cuando el jugador cae en combate."""
    print("\n" + "x" * 60)
    print(console.colorize("¡HAS SIDO DERROTADO!", console.Fore.RED, bright=True))

    # Penalización de oro (ejemplo: pierdes el 30% de tu oro actual)
    penalty = player.inventory.gold // 3
    player.inventory.gold -= penalty

    # Restauración por "emergencia"
    player.stats.health = player.stats.max_health

    console.warning("Unos viajeros te han rescatado y llevado a la ciudad.")
    print(f"Penalización: Has perdido {console.colorize(f'{penalty} de oro', console.Fore.RED)}.")
    console.success("Tu salud ha sido restaurada para que puedas continuar.")
    print("x" * 60)
    console.ask("\nPresiona Enter para volver...")


def _restore_player(player, snapshot: dict) -> None:
    """Elimina efectos, restaura stats base y cura al jugador."""
    # Restaurar stats base (por si hubo pociones de fuerza/defensa)
    player.stats.min_atk, player.stats.max_atk = snapshot["atk"]
    player.stats.armor = snapshot["armor"]

    # Limpiar estados alterados
    player.status_effects = []

    if hasattr(player, 'active_effects'):
        player.active_effects = []

    # Recuperar Salud al finalizar
    if player.is_alive():
        if player.just_leveled_up:
            print(console.colorize("✨ ¡Energía renovada por el nuevo nivel!", console.Fore.MAGENTA))
            player.just_leveled_up = False  # Reseteamos el flag
        else:
            # Lógica de curación normal (50% de lo perdido)
            missing_health = player.stats.max_health - player.stats.health
            recovery = missing_health // 2
            player.stats.health += recovery
            if recovery > 0:
                print(f"\n{console.colorize(f'Tras el combate, descansas y recuperas {recovery} HP.', console.Fore.GREEN)}")
                print(console.colorize(f"Vida actual: {player.stats.health}/{player.stats.max_health}", console.Fore.GREEN))
