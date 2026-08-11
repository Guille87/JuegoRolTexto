import msvcrt
import random
import time

from juego_rol_texto.audio.resource_manager import ResourceManager
from juego_rol_texto.characters.stats import resolve_hit
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

# Umbral de la barra ATB: cuando el "gauge" de un combatiente llega aquí, actúa
# y se le resta el umbral (el sobrante se conserva, no se pierde). Con esto la
# velocidad no decide solo quién va primero, sino con qué frecuencia actúa cada
# uno (estilo Final Fantasy X), permitiendo que el más rápido actúe varias
# veces antes de que el más lento llegue a su primer turno.
ATB_THRESHOLD = 100


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
    gauge_player = 0.0
    gauge_enemy = 0.0
    while player.is_alive() and enemy.is_alive():
        rm.update()

        # --- BARRA ATB: avanzamos el "reloj" hasta que alguien esté listo ---
        while gauge_player < ATB_THRESHOLD and gauge_enemy < ATB_THRESHOLD:
            gauge_player += player.get_total_speed()
            gauge_enemy += enemy.stats.speed

        # El turno del jugador (y una posible huida) se resuelve siempre antes que
        # el del enemigo si ambos gauges están listos en el mismo "tick": así la
        # huida nunca puede ser interrumpida por un enemigo más rápido.
        if gauge_player >= ATB_THRESHOLD:
            gauge_player -= ATB_THRESHOLD
            signal, is_auto = _run_player_turn(player, enemy, defeated_enemies, is_auto)
            if signal == "huir":
                break

        if not enemy.is_alive():
            # CAPTURAMOS LOS NUEVOS STATS SI SUBE DE NIVEL
            new_atk, new_armor = _handle_victory(player, enemy, defeated_enemies, unlocked_enemies)

            # SI SUBIÓ DE NIVEL, ACTUALIZAMOS EL SNAPSHOT
            if player.just_leveled_up:
                snapshot["atk"] = new_atk
                snapshot["armor"] = new_armor
            break

        # --- TURNO DEL ENEMIGO (solo si su gauge también está lista) ---
        if player.is_alive() and gauge_enemy >= ATB_THRESHOLD:
            gauge_enemy -= ATB_THRESHOLD
            _run_enemy_turn(player, enemy, defeated_enemies)

        if not player.is_alive():
            _handle_defeat(player)
            break

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


def _attempt_flee(player, enemy) -> bool:
    """Probabilidad de huir con éxito.

    Si el jugador es igual o más rápido que el enemigo, la huida es siempre
    segura (100%). Por debajo de eso, la probabilidad baja junto con la
    velocidad relativa, pero nunca llega a 0.
    """
    player_speed = max(1, player.get_total_speed())
    enemy_speed = max(1, enemy.stats.speed)
    flee_chance = min(1.0, player_speed / enemy_speed)
    return random.random() < flee_chance


def _run_player_turn(player, enemy, defeated_enemies: list, is_auto: bool) -> tuple:
    """Ejecuta el turno del jugador cuando su gauge ATB está lista.

    Devuelve (señal, is_auto actualizado). señal es "huir" si el combate debe
    terminar, o "ok" en cualquier otro caso.
    """
    # --- INICIO DE TURNO (Procesar veneno, quemaduras, parálisis) ---
    can_act = player.on_turn_start()
    turn_consumed = False

    # --- COMPROBAR CANCELACIÓN DE AUTO ---
    if is_auto and check_for_interrupt():
        is_auto = False
        console.warning("\n🛑 ¡Auto-batalla cancelada! Volviendo al menú...")
        time.sleep(1)  # Pausa para que el usuario lo vea

    action = None
    if player.is_alive():  # El veneno podría haberlo matado en on_turn_start
        if not is_auto:
            if can_act:
                action = _player_menu(player, enemy, defeated_enemies)
                if action == "huir":
                    # La huida siempre se resuelve antes que cualquier otra acción,
                    # sea el jugador más rápido o más lento que el enemigo.
                    if _attempt_flee(player, enemy):
                        console.warning("Has huido del combate...")
                        return "huir", is_auto
                    else:
                        console.error(f"¡No has podido escapar de {enemy.name}!")
                        turn_consumed = True

                if action == "auto":
                    is_auto = True
                    print(console.colorize(">>> MODO AUTO: ACTIVADO. (Pulsa 'Q' para detener)", console.Fore.CYAN))

                if action == "objeto_usado":
                    turn_consumed = True
            else:
                console.ask(f"\n{console.colorize('Presiona Enter para pasar turno...', console.Fore.YELLOW)}")

        # --- ATAQUE DEL JUGADOR (Si puede actuar) ---
        if (is_auto or action == "atacar") and can_act and not turn_consumed:
            _execute_turn(player, enemy, defeated_enemies)

    player.on_turn_end()
    return "ok", is_auto


def _run_enemy_turn(player, enemy, defeated_enemies: list) -> None:
    """Ejecuta el turno del enemigo cuando su gauge ATB está lista."""
    time.sleep(1)
    print(f"\nTurno de {console.colorize(enemy.name, console.Fore.RED)}...")
    enemy.perform_turn(player)
    print_status(player, enemy, defeated_enemies)

    if hasattr(enemy, 'on_turn_end'):
        enemy.on_turn_end()


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

    # Tirada de acierto (precisión del atacante vs evasión del defensor):
    # un fallo no llega a tocar armadura ni elementos, así que se resuelve
    # antes que cualquier otro cálculo de daño.
    attacker_precision = attacker.get_total_precision() if isinstance(attacker, Player) else attacker.stats.precision
    defender_evasion = defender.get_total_evasion() if isinstance(defender, Player) else defender.stats.evasion
    if not resolve_hit(attacker_precision, defender_evasion):
        print(f"{console.colorize(attacker.name, console.Fore.GREEN)} ataca a "
              f"{console.colorize(defender.name, console.Fore.RED)}, pero falla el golpe.")
        if isinstance(attacker, Player):
            print_status(attacker, defender, defeated_enemies)
        else:
            print_status(defender, attacker, defeated_enemies)
        return

    damage = attacker.get_attack_damage()
    element = attacker.get_equipped_element() if isinstance(attacker, Player) else None

    # Golpe crítico: el jugador suma el bonus de su equipo, los enemigos usan su stat base
    attacker_crit_chance = attacker.get_total_crit_chance() if isinstance(attacker, Player) else attacker.stats.crit_chance
    attacker_crit_damage = attacker.get_total_crit_damage() if isinstance(attacker, Player) else attacker.stats.crit_damage
    is_crit = random.random() < attacker_crit_chance
    if is_crit:
        damage = int(damage * attacker_crit_damage)

    # ¿Es el defensor débil a este elemento? Lo comprobamos antes de aplicar el daño
    # para poder mostrar el mensaje de "supereficaz" (take_damage no expone esa info).
    weaknesses = getattr(type(defender), "ELEMENTAL_WEAKNESSES", {})
    is_super_effective = bool(element) and weaknesses.get(element, 1.0) > 1.0

    # Penetración de armadura: solo tiene efecto en ataques físicos (is_magical=False,
    # el único caso que pasa por aquí hoy), reduce la armadura del defensor antes
    # de restar el daño.
    attacker_armor_penetration = (
        attacker.get_total_armor_penetration() if isinstance(attacker, Player) else attacker.stats.armor_penetration
    )
    final_dmg = defender.take_damage(damage, defeated_enemies=defeated_enemies, element=element,
                                      armor_penetration=attacker_armor_penetration)

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
