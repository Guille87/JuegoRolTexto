import msvcrt
import random
import time
from colorama import Fore, Style

from assets.resources.resource_manager import ResourceManager
from utils.utils import print_player_enemy_info, print_status


# Mapa de progresión: Al derrotar a la LLAVE, se desbloquea el VALOR
ENEMY_PROGRESSION = {
    "Goblin": "Esqueleto",
    "Esqueleto": "Orco",
    "Orco": "Troll",
    "Troll": "Mago",
    "Mago": None  # El Mago es el último por ahora
}

def check_for_interrupt():
    """Retorna True si el usuario ha pulsado 'q' o 'Q'."""
    if msvcrt.kbhit():  # ¿Se ha pulsado alguna tecla?
        key = msvcrt.getch().decode('utf-8').lower()
        if key == 'q':
            return True
    return False

def initiate_battle(player, enemy, defeated_enemies, unlocked_enemies):
    """Punto de entrada principal para cualquier combate."""
    print("=" * 60)
    print(f"{Style.BRIGHT}¡Ha comenzado la batalla contra {enemy.name}!{Style.RESET_ALL}")
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
            _restore_player(player, {"atk": (player.stats.min_atk, player.stats.max_atk), "def": player.stats.defense})
            return

    # Guardamos estado inicial para restaurar después
    snapshot = {
        "atk": (player.stats.min_atk, player.stats.max_atk),
        "def": player.stats.defense
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
                print(f"\n{Fore.YELLOW}🛑 ¡Auto-batalla cancelada! Volviendo al menú...{Style.RESET_ALL}")
                time.sleep(1)  # Pausa para que el usuario lo vea

        action = None
        if player.is_alive():  # El veneno podría haberlo matado en on_turn_start
            if not is_auto:
                if can_act:
                    action = _player_menu(player, enemy, defeated_enemies)
                    if action == "huir":
                        print(f"{Fore.YELLOW}Has huido del combate...{Style.RESET_ALL}")
                        break

                    if action == "auto":
                        is_auto = True
                        print(f"{Fore.CYAN}>>> MODO AUTO: ACTIVADO. (Pulsa 'Q' para detener){Style.RESET_ALL}")

                    if action == "objeto_usado":
                        turn_consumed = True
                else:
                    input(f"\n{Fore.YELLOW}Presiona Enter para pasar turno...{Style.RESET_ALL}")

            # --- TURNO DEL JUGADOR (Si puede actuar) ---
            if (is_auto or action == "atacar") and can_act and not turn_consumed:
                _execute_turn(player, enemy, defeated_enemies)

        if not enemy.is_alive():
            # CAPTURAMOS LOS NUEVOS STATS SI SUBE DE NIVEL
            new_atk, new_def = _handle_victory(player, enemy, defeated_enemies, unlocked_enemies)

            # SI SUBIÓ DE NIVEL, ACTUALIZAMOS EL SNAPSHOT
            if player.just_leveled_up:
                snapshot["atk"] = new_atk
                snapshot["def"] = new_def
            break

        # --- TURNO DEL ENEMIGO ---
        if enemy.is_alive():
            time.sleep(1)
            print(f"\nTurno de {Fore.RED}{enemy.name}{Style.RESET_ALL}...")
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
            print(f"{Fore.BLACK}{Style.BRIGHT}(Esperando siguiente turno...){Style.RESET_ALL}")
            time.sleep(1)  # Pequeña pausa para asimilar el daño recibido

    _restore_player(player, snapshot)
    player.in_combat = False
    # Al salir, volvemos a modo aventura
    rm.set_mood("adventure")
    rm.play_random_adventure_music()


def _player_menu(player, enemy, defeated_enemies):
    """Maneja la interfaz de usuario durante el combate."""
    while True:
        options = ["1. Atacar", "2. Objetos", "3. Info", "4. Huir"]
        if enemy.name in defeated_enemies:
            options.append("5. Auto-Batalla")

        print("\n" + " | ".join(options))
        choice = input(f"Selección: ")

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
            print(f"{Fore.RED}Opción no válida.{Style.RESET_ALL}")


def _execute_turn(attacker, defender, defeated_enemies):
    """Ejecuta un ataque estándar calculando daño y stats."""
    from characters.player import Player
    if isinstance(attacker, Player):
        rm = ResourceManager()
        # Elegimos al azar entre los nombres en AUDIO_ASSETS en main.py
        sonido_ataque = random.choice(["hit", "slash"])
        rm.play_sfx(sonido_ataque)

    # Verificación de seguridad: si attacker es una lista, tenemos un problema de lógica previo
    if isinstance(attacker, list):
        print(f"{Fore.RED}Error Interno: El atacante es una lista, no un objeto.{Style.RESET_ALL}")
        return

    damage = attacker.get_attack_damage()

    # Usamos un try/except o verificamos el tipo por si otros enemigos no aceptan el parámetro aún
    try:
        final_dmg = defender.take_damage(damage, defeated_enemies=defeated_enemies)
    except TypeError:
        # Si el enemigo no tiene lógica especial, llamamos normal
        final_dmg = defender.take_damage(damage)

    if final_dmg > 0:
        print(f"{Fore.GREEN}{attacker.name}{Style.RESET_ALL} ataca a {Fore.RED}{defender.name}{Style.RESET_ALL} y hace {Fore.YELLOW}{final_dmg}{Style.RESET_ALL} de daño")
    else:
        print(f"{Fore.BLUE}{defender.name}{Style.RESET_ALL} ha bloqueado el ataque.")

    from characters.player import Player
    if isinstance(attacker, Player):
        print_status(attacker, defender, defeated_enemies)
    else:
        print_status(defender, attacker, defeated_enemies)


def _handle_victory(player, enemy, defeated_enemies, unlocked_enemies):
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}¡VICTORIA! {enemy.name} ha sido derrotado.{Style.RESET_ALL}")

    if enemy.name not in defeated_enemies:
        defeated_enemies.append(enemy.name)

        # Consultamos si este enemigo desbloquea a otro
        next_enemy = ENEMY_PROGRESSION.get(enemy.name)

        if next_enemy and next_enemy not in unlocked_enemies:
            unlocked_enemies.append(next_enemy)
            print(f"{Fore.MAGENTA}✨ ¡NUEVO ENEMIGO DESBLOQUEADO: {next_enemy}!{Style.RESET_ALL}")

    # Recompensa de Oro
    gold = enemy.gold_drop
    player.inventory.gold += gold
    print(f"💰 Oro obtenido: {Fore.YELLOW}{gold}{Style.RESET_ALL}")

    # Experiencia y Nivel
    old_level = player.level
    player.gain_experience(gold * 2)

    # Comprobamos si subió de nivel
    player.just_leveled_up = player.level > old_level

    # Recompensa de Ítems (Drops)
    drops = enemy.drop_item()
    if drops:
        print(f"\n{Fore.CYAN}--- BOTÍN ENCONTRADO ---{Style.RESET_ALL}")
        for item in drops:
            player.inventory.add_item(item)
            # Imprimimos solo aquí el mensaje del objeto encontrado
            print(f"📦 {Fore.GREEN}{item.name}{Style.RESET_ALL}: {item.description}")

    # Si sube de nivel, devolvemos el nuevo snapshot de stats
    return (player.stats.min_atk, player.stats.max_atk), player.stats.defense


def _handle_defeat(player):
    """Gestiona lo que ocurre cuando el jugador cae en combate."""
    print("\n" + "x" * 60)
    print(f"{Fore.RED}{Style.BRIGHT}¡HAS SIDO DERROTADO!{Style.RESET_ALL}")

    # Penalización de oro (ejemplo: pierdes el 30% de tu oro actual)
    penalty = player.inventory.gold // 3
    player.inventory.gold -= penalty

    # Restauración por "emergencia"
    player.stats.health = player.stats.max_health

    print(f"{Fore.YELLOW}Unos viajeros te han rescatado y llevado a la ciudad.{Style.RESET_ALL}")
    print(f"Penalización: Has perdido {Fore.RED}{penalty} de oro{Style.RESET_ALL}.")
    print(f"{Fore.GREEN}Tu salud ha sido restaurada para que puedas continuar.{Style.RESET_ALL}")
    print("x" * 60)
    input("\nPresiona Enter para volver...")


def _restore_player(player, snapshot):
    """Elimina efectos, restaura stats base y cura al jugador."""
    # Restaurar stats base (por si hubo pociones de fuerza/defensa)
    player.stats.min_atk, player.stats.max_atk = snapshot["atk"]
    player.stats.defense = snapshot["def"]

    # Limpiar estados alterados
    player.status_effects = []

    if hasattr(player, 'active_effects'):
        player.active_effects = []

    # Recuperar Salud al finalizar
    if player.is_alive():
        if player.just_leveled_up:
            print(f"{Fore.MAGENTA}✨ ¡Energía renovada por el nuevo nivel!{Style.RESET_ALL}")
            player.just_leveled_up = False  # Reseteamos el flag
        else:
            # Lógica de curación normal (50% de lo perdido)
            missing_health = player.stats.max_health - player.stats.health
            recovery = missing_health // 2
            player.stats.health += recovery
            if recovery > 0:
                print(f"\n{Fore.GREEN}Tras el combate, descansas y recuperas {recovery} HP.")
                print(f"Vida actual: {player.stats.health}/{player.stats.max_health}{Style.RESET_ALL}")