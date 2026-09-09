import random
import time
from typing import TYPE_CHECKING

from juego_rol_texto import i18n
from juego_rol_texto.audio.resource_manager import ResourceManager
from juego_rol_texto.characters.enemies.enemy_base import status_label
from juego_rol_texto.characters.stats import resolve_hit
from juego_rol_texto.ui import console
from juego_rol_texto.ui.formatting import print_combatant_bar, print_player_enemy_info, print_status
from juego_rol_texto.ui.keyboard import key_pressed

if TYPE_CHECKING:
    from juego_rol_texto.characters.enemies.enemy_base import Enemy
    from juego_rol_texto.characters.player import Player

# Mapa de progresión: Al derrotar a la LLAVE, se desbloquea el VALOR.
# Orden de tiers acordado con el usuario (ver TODO.md): los enemigos nuevos se
# van insertando en el hueco que les corresponde según su potencia relativa a
# los que ya existían, no necesariamente al final de la cadena.
ENEMY_PROGRESSION = {
    "Goblin": "Huargo",
    "Huargo": "Esqueleto",
    "Esqueleto": "Bandido",
    "Bandido": "Orco",
    "Orco": "Espíritu Vengativo",
    "Espíritu Vengativo": "Troll",
    "Troll": "Gárgola",
    "Gárgola": "Gólem de Piedra",
    "Gólem de Piedra": "Mago",
    "Mago": "Nigromante",
    "Nigromante": "Ángel Caído",
    "Ángel Caído": "Demonio",
    "Demonio": "Dragón",
    "Dragón": None,  # Jefe final de la cadena
}

# Umbral de la barra ATB: cuando el "gauge" de un combatiente llega aquí, actúa
# y se le resta el umbral (el sobrante se conserva, no se pierde). Con esto la
# velocidad no decide solo quién va primero, sino con qué frecuencia actúa cada
# uno (estilo Final Fantasy X), permitiendo que el más rápido actúe varias
# veces antes de que el más lento llegue a su primer turno.
ATB_THRESHOLD = 100


def check_for_interrupt() -> bool:
    """Retorna True si el usuario ha pulsado 'q' o 'Q'."""
    return key_pressed() == "q"


_MAX_CHAIN_BATTLES = 20


def _ask_chain_count() -> int:
    """Pregunta cuántas peleas seguidas quiere el jugador al activar la
    auto-batalla contra un enemigo ya derrotado. Enter / algo no numérico -> 1;
    por encima del máximo, se avisa y se recorta."""
    raw = console.ask(f"¿Cuántas peleas seguidas? (1-{_MAX_CHAIN_BATTLES}, Enter = 1): ").strip()
    if not raw:
        return 1
    if not raw.isdigit():
        console.warning("Eso no es un número; se hará una sola pelea.")
        return 1
    n = int(raw)
    if n > _MAX_CHAIN_BATTLES:
        console.warning(f"El máximo son {_MAX_CHAIN_BATTLES} peleas seguidas.")
        return _MAX_CHAIN_BATTLES
    return max(1, n)


def initiate_battle(player, enemy, defeated_enemies: list, unlocked_enemies: list, *, enemy_factory=None) -> str:
    """Punto de entrada principal para cualquier combate.

    Si al activar la auto-batalla (o el turbo) contra un enemigo ya derrotado el
    jugador pide varias peleas seguidas, aquí se encadenan: cada pelea es como
    siempre (botín, oro, XP, curación) y la siguiente arranca sola en el mismo
    modo. `enemy_factory` (una función que crea una instancia nueva del enemigo)
    es necesaria para poder encadenar; sin ella solo se juega una pelea.

    Devuelve el desenlace de la última pelea: `"victory"`, `"defeat"`, `"fled"`
    o `"cancelled"` (el jugador pulsó 'Q' y terminó a mano sin volver a auto)."""
    rm = ResourceManager()
    rm.enter_battle(enemy.name)
    player.in_combat = True

    # Estado de la cadena, compartido con _run_player_turn: cuando el jugador
    # elige auto/turbo se rellenan "count" y "mode"; "mode" puede cambiar a mitad
    # (p. ej. pasar de auto a turbo tras pulsar 'Q').
    chain = {"factory": enemy_factory, "chosen": False, "count": 1, "mode": False}

    fight_index = 1
    current_enemy = enemy
    outcome = "victory"
    while True:
        if fight_index > 1:
            print(
                console.colorize(
                    f"\n=== CADENA DE BATALLA: PELEA {fight_index}/{chain['count']} ===",
                    console.Fore.MAGENTA,
                    bright=True,
                )
            )
        outcome = _run_one_battle(player, current_enemy, defeated_enemies, unlocked_enemies, chain, fight_index)
        if outcome != "victory" or fight_index >= chain["count"]:
            break
        fight_index += 1
        current_enemy = chain["factory"]()

    player.in_combat = False
    rm.exit_battle()

    if chain["count"] > 1:
        if outcome == "victory":
            console.success(f"🔗 Cadena completada: {chain['count']}/{chain['count']} peleas.")
        else:
            done = fight_index - 1 if outcome in ("defeat", "fled") else fight_index
            motivo = {
                "defeat": "Has caído en combate",
                "fled": "Has huido",
                "cancelled": "Has salido del modo automático",
            }.get(outcome, "Cadena interrumpida")
            console.warning(f"🔗 {motivo}. Cadena interrumpida ({done}/{chain['count']} peleas completadas).")

    # Pausa para leer el resultado: siempre salvo tras una victoria limpia en
    # turbo (ahí el jugador está farmeando y quiere volver al menú ya) y salvo
    # tras una derrota (ya pausó _handle_defeat).
    clean_turbo_win = outcome == "victory" and chain["mode"] == "turbo"
    if outcome in ("victory", "cancelled", "fled") and not clean_turbo_win:
        console.ask(f"\n{console.colorize('Presiona Enter para continuar...', console.Fore.YELLOW)}")

    return outcome


def _run_one_battle(
    player, enemy, defeated_enemies: list, unlocked_enemies: list, chain: dict, fight_index: int
) -> str:
    """Una sola pelea completa. `chain` guía el modo automático de arranque (en
    la 2ª pelea de una cadena en adelante) y recoge la elección del jugador si
    activa la auto-batalla aquí. Devuelve `"victory"` / `"defeat"` / `"fled"` /
    `"cancelled"`."""
    print("=" * 60)
    print(f"{console.colorize(f'¡Ha comenzado la batalla contra {enemy.name}!', console.Fore.WHITE, bright=True)}")
    rm = ResourceManager()
    # Vida justo al entrar en combate: si el jugador huye, solo debe poder
    # recuperar parte de lo que ha perdido en ESTA pelea.
    health_before_battle = player.stats.health

    # En la 2ª pelea de una cadena en adelante arrancamos ya en el modo elegido.
    start_auto: bool | str = chain["mode"] if fight_index > 1 else False

    # --- LÓGICA DE EMBOSCADA (Ataque previo) ---
    if hasattr(enemy, "check_ambush"):
        if enemy.check_ambush(player, defeated_enemies):
            print_status(player, enemy, defeated_enemies)

        if not player.is_alive():
            _handle_defeat(player)
            _restore_player(player, {"atk": (player.stats.min_atk, player.stats.max_atk), "armor": player.stats.armor})
            return "defeat"

    # Ficha de ambos combatientes al empezar. En turbo se omite (farmeo).
    if start_auto != "turbo":
        print_player_enemy_info(player, enemy, defeated_enemies)

    snapshot = {"atk": (player.stats.min_atk, player.stats.max_atk), "armor": player.stats.armor}

    is_auto: bool | str = start_auto
    if start_auto:
        modo = "TURBO (sin pausas)" if start_auto == "turbo" else "ACTIVADO"
        print(console.colorize(f">>> MODO AUTO: {modo}. (Pulsa 'Q' para detener)", console.Fore.CYAN))
    auto_cancelled = False
    player_won = False
    player_fled = False
    player_defeated = False
    gauge_player = 0.0
    gauge_enemy = 0.0
    enemy_acted = True  # el primer turno del jugador no cuenta como "repetido"
    while player.is_alive() and enemy.is_alive():
        rm.update()

        # --- BARRA ATB: avanzamos el "reloj" hasta que alguien esté listo ---
        while gauge_player < ATB_THRESHOLD and gauge_enemy < ATB_THRESHOLD:
            gauge_player += player.get_total_speed()
            gauge_enemy += enemy.stats.speed

        # El turno del jugador (y una posible huida) se resuelve siempre antes que
        # el del enemigo si ambos gauges están listos en el mismo "tick".
        if gauge_player >= ATB_THRESHOLD:
            gauge_player -= ATB_THRESHOLD
            was_auto = bool(is_auto)
            signal, is_auto = _run_player_turn(
                player, enemy, defeated_enemies, is_auto, repeated=not enemy_acted, chain=chain
            )
            if was_auto and not is_auto:
                auto_cancelled = True  # pulsó 'Q'; si vuelve a activar auto se corrige abajo
            enemy_acted = False
            if signal == "huir":
                player_fled = True
                break

        if not enemy.is_alive():
            player_won = True
            new_atk, new_armor = _handle_victory(player, enemy, defeated_enemies, unlocked_enemies)
            if player.just_leveled_up:
                snapshot["atk"] = new_atk
                snapshot["armor"] = new_armor
            break

        # --- TURNO DEL ENEMIGO (solo si su gauge también está lista) ---
        if player.is_alive() and gauge_enemy >= ATB_THRESHOLD:
            gauge_enemy -= ATB_THRESHOLD
            _run_enemy_turn(player, enemy, defeated_enemies, turbo=is_auto == "turbo")
            enemy_acted = True

        # El enemigo pudo morir por veneno/quemadura al empezar su turno.
        if not enemy.is_alive():
            player_won = True
            new_atk, new_armor = _handle_victory(player, enemy, defeated_enemies, unlocked_enemies)
            if player.just_leveled_up:
                snapshot["atk"] = new_atk
                snapshot["armor"] = new_armor
            break

        if not player.is_alive():
            _handle_defeat(player)  # cura al jugador por completo, de ahí el flag
            player_defeated = True
            break

        # En auto normal, una pausa para poder leer el resultado. En turbo no.
        if is_auto == "auto" and player.is_alive() and enemy.is_alive():
            print(console.colorize("(Esperando siguiente turno...)", console.Fore.BLACK, bright=True))
            time.sleep(1)

    if player_fled:
        _restore_player(player, snapshot, max_recovery=health_before_battle - player.stats.health)
    else:
        _restore_player(player, snapshot)

    if player_defeated:
        return "defeat"
    if player_fled:
        return "fled"
    # "cancelled" solo si pulsó 'Q' y NO volvió a activar la auto-batalla.
    if auto_cancelled and not is_auto:
        return "cancelled"
    return "victory" if player_won else "fled"

    if player_defeated:
        return "defeat"
    if player_fled:
        return "fled"
    if auto_cancelled:
        return "cancelled"
    return "victory" if player_won else "fled"


def _player_menu(player, enemy, defeated_enemies: list, immobilized: bool = False) -> str:
    """Maneja la interfaz de usuario durante el combate. Si `immobilized`
    (parálisis/congelación), no se ofrece "Defender" y "Atacar" pierde el turno,
    pero sí se puede usar un objeto (poción, antídoto) o intentar huir."""
    while True:
        atacar = "1. Atacar (no puedes moverte)" if immobilized else "1. Atacar"
        options = [atacar, "2. Objetos", "3. Info", "4. Huir"]
        if not immobilized:
            options.append("5. Defender")
        if enemy.name in defeated_enemies:
            options.append("6. Auto-Batalla")
            options.append("7. Auto-Batalla Turbo")

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
        elif choice == "5" and not immobilized:
            return "defender"
        elif choice == "6" and enemy.name in defeated_enemies:
            return "auto"
        elif choice == "7" and enemy.name in defeated_enemies:
            return "turbo"
        else:
            console.error("Opción no válida.")


def _attempt_flee(player, enemy, chance_mult: float = 1.0) -> bool:
    """Probabilidad de huir con éxito.

    Si el jugador es igual o más rápido que el enemigo, la huida es siempre
    segura (100%). Por debajo de eso, la probabilidad baja junto con la
    velocidad relativa, pero nunca llega a 0. `chance_mult` la reduce (0.5 si el
    jugador está inmovilizado por parálisis/congelación).
    """
    player_speed = max(1, player.get_total_speed())
    enemy_speed = max(1, enemy.stats.speed)
    flee_chance = min(1.0, player_speed / enemy_speed) * chance_mult
    return random.random() < flee_chance


def _run_player_turn(player, enemy, defeated_enemies: list, is_auto, repeated: bool = False, chain: dict | None = None):
    """Ejecuta el turno del jugador cuando su gauge ATB está lista.

    `is_auto` es `False`, `"auto"` (auto normal, con pausas) o `"turbo"` (auto
    sin pausas, para farmear). `repeated` = el jugador vuelve a actuar sin que el
    enemigo haya actuado por el medio (es más rápido). `chain` (si se pasa) recibe
    la elección del jugador al activar la auto-batalla: la primera vez se le
    pregunta cuántas peleas seguidas quiere; el modo (`"auto"`/`"turbo"`) se
    actualiza siempre, para poder cambiar de uno a otro a mitad de una cadena.
    Devuelve `(señal, is_auto actualizado)`; señal es `"huir"` o `"ok"`.
    """
    # --- INICIO DE TURNO (Procesar veneno, quemaduras, parálisis) ---
    # La postura defensiva del turno anterior solo cubre hasta que al jugador le
    # vuelve a tocar: al empezar su turno se limpia.
    player.defending = False
    hp_before = player.stats.health
    can_act = player.on_turn_start()
    turn_consumed = False

    # Si el veneno/quemadura le hizo daño, una línea con su vida (barra +
    # estados) para que sepa con cuánta se queda antes de decidir.
    if player.is_alive() and player.stats.health != hp_before:
        print_combatant_bar(player, is_player=True)

    if repeated and not is_auto and player.is_alive():
        print(console.colorize(f"⏩ Eres más rápido: actúas de nuevo antes que {enemy.name}.", console.Fore.CYAN))

    # --- COMPROBAR CANCELACIÓN DE AUTO ---
    if is_auto and check_for_interrupt():
        was_turbo = is_auto == "turbo"
        is_auto = False
        console.warning("\n🛑 Auto-batalla detenida. Vuelves a controlar el combate.")
        if not was_turbo:
            time.sleep(1)  # Pausa para que el usuario lo vea

    action = None
    if player.is_alive():  # El veneno podría haberlo matado en on_turn_start
        if not is_auto:
            action = _player_menu(player, enemy, defeated_enemies, immobilized=not can_act)
            if action == "huir":
                # Inmovilizado, la probabilidad de huir baja a la mitad.
                if _attempt_flee(player, enemy, chance_mult=1.0 if can_act else 0.5):
                    console.warning("Has huido del combate...")
                    return "huir", is_auto
                console.error(f"¡No has podido escapar de {enemy.name}!")
                turn_consumed = True

            if action in ("auto", "turbo"):
                is_auto = action
                # Cadena de peleas: se pregunta la primera vez que se activa la
                # auto-batalla; el modo se actualiza siempre (permite cambiar de
                # auto a turbo o viceversa a mitad de una cadena).
                if chain is not None:
                    if chain["factory"] and not chain["chosen"]:
                        chain["chosen"] = True
                        chain["count"] = _ask_chain_count()
                    chain["mode"] = action
                modo = "TURBO (sin pausas)" if action == "turbo" else "ACTIVADO"
                print(console.colorize(f">>> MODO AUTO: {modo}. (Pulsa 'Q' para detener)", console.Fore.CYAN))

            if action == "defender":
                player.defending = True
                turn_consumed = True
                print(
                    console.colorize(
                        f"{player.name} adopta una postura defensiva: el daño recibido hasta su "
                        "siguiente turno se reduce a la mitad.",
                        console.Fore.CYAN,
                    )
                )

            if action == "objeto_usado":
                turn_consumed = True

            if action == "atacar" and not can_act:
                console.warning("Intentas moverte, pero no puedes. Pierdes el turno.")

        # --- ATAQUE DEL JUGADOR (Si puede actuar) ---
        if (is_auto or action == "atacar") and can_act and not turn_consumed:
            _execute_turn(player, enemy, defeated_enemies)

    player.on_turn_end()
    return "ok", is_auto


def _run_enemy_turn(player, enemy, defeated_enemies: list, turbo: bool = False) -> None:
    """Ejecuta el turno del enemigo cuando su gauge ATB está lista. En `turbo`
    no hay pausa ni barra de vida por turno (solo el texto del ataque)."""
    if not turbo:
        time.sleep(1)

    # Estados alterados: veneno/quemadura (daño), parálisis/congelación (pierde turno).
    hp_before = enemy.stats.health
    can_act = enemy.on_turn_start()
    if not enemy.is_alive():
        console.info(i18n.t("combat.enemy_succumbs", name=enemy.name))
        enemy.decay_status_effects()
        return
    took_dot = enemy.stats.health != hp_before

    if can_act:
        print(f"\nTurno de {console.colorize(enemy.name, console.Fore.RED)}...")
        enemy.perform_turn(player)
    enemy.on_turn_end()
    enemy.decay_status_effects()

    # Si el enemigo pierde el turno y no hubo daño por veneno/quemadura, no
    # repetimos las barras de vida: el mensaje de parálisis/congelación basta.
    if not turbo and (can_act or took_dot):
        print_status(player, enemy, defeated_enemies)

    announcements = enemy.pop_announcements()
    if not turbo:
        for message in announcements:
            print(message)


def _execute_turn(attacker: "Player", defender: "Enemy", defeated_enemies: list) -> None:
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
        print(
            f"{console.colorize(attacker.name, console.Fore.GREEN)} ataca a "
            f"{console.colorize(defender.name, console.Fore.RED)}, pero falla el golpe."
        )
        if isinstance(attacker, Player):
            print_status(attacker, defender, defeated_enemies)
        else:
            print_status(defender, attacker, defeated_enemies)
        return

    damage = attacker.get_attack_damage()

    # Arcanista: su ataque estándar es mágico (escala con poder mágico, no con el
    # arma) y su elemento es "arcano" por defecto si nada más lo fija.
    is_magical_attack = isinstance(attacker, Player) and attacker.is_magical_attacker()
    if is_magical_attack:
        from juego_rol_texto.characters.classes import ARCANIST_DEFAULT_ELEMENT

        element = attacker.get_equipped_element() or ARCANIST_DEFAULT_ELEMENT
    elif isinstance(attacker, Player):
        element = attacker.get_equipped_element()
    else:
        element = None

    # Golpe crítico: el jugador suma el bonus de su equipo, los enemigos usan su stat base
    attacker_crit_chance = (
        attacker.get_total_crit_chance() if isinstance(attacker, Player) else attacker.stats.crit_chance
    )
    attacker_crit_damage = (
        attacker.get_total_crit_damage() if isinstance(attacker, Player) else attacker.stats.crit_damage
    )
    is_crit = random.random() < attacker_crit_chance
    if is_crit:
        damage = int(damage * attacker_crit_damage)

    # Afinidad del defensor al elemento (débil / resistente / inmune). Lo
    # comprobamos antes de aplicar el daño para poder mostrar el mensaje
    # correspondiente (take_damage no expone esa info).
    affinity = defender.affinity_for({element}) if element and hasattr(defender, "affinity_for") else 1.0
    is_super_effective = affinity > 1.0
    is_immune_hit = element and affinity == 0.0
    is_resisted_hit = 0.0 < affinity < 1.0

    # Penetración de armadura: solo tiene efecto en ataques físicos (is_magical=False,
    # el único caso que pasa por aquí hoy), reduce la armadura del defensor antes
    # de restar el daño.
    attacker_armor_penetration = (
        attacker.get_total_armor_penetration() if isinstance(attacker, Player) else attacker.stats.armor_penetration
    )
    if is_magical_attack:
        final_dmg = defender.take_damage(
            damage,
            defeated_enemies=defeated_enemies,
            element=element,
            is_magical=True,
            magic_penetration=attacker.get_total_magic_penetration(),
        )
    else:
        final_dmg = defender.take_damage(
            damage, defeated_enemies=defeated_enemies, element=element, armor_penetration=attacker_armor_penetration
        )

    element_name = i18n.t(f"element.{element}") if element else ""
    if is_super_effective:
        print(
            console.colorize(
                i18n.t("combat.super_effective", element=element_name, name=defender.name),
                console.Fore.RED,
                bright=True,
            )
        )
    elif is_immune_hit:
        print(
            console.colorize(i18n.t("combat.immune_hit", element=element_name, name=defender.name), console.Fore.BLUE)
        )
    elif is_resisted_hit:
        print(
            console.colorize(i18n.t("combat.resisted_hit", element=element_name, name=defender.name), console.Fore.BLUE)
        )

    if final_dmg > 0:
        dmg_color = console.Fore.YELLOW if is_crit else console.Fore.CYAN
        print(
            f"{console.colorize(attacker.name, console.Fore.GREEN)} ataca a "
            f"{console.colorize(defender.name, console.Fore.RED)} y hace "
            f"{console.colorize(str(final_dmg), dmg_color, bright=is_crit)} de daño"
            f"{console.crit_suffix(is_crit)}"
        )
    else:
        print(f"{console.colorize(defender.name, console.Fore.BLUE)} ha bloqueado el ataque.")

    # Estado alterado del arma elemental, DESPUÉS de anunciar el golpe. Solo el
    # jugador; si el enemigo resiste el elemento, la probabilidad y la duración
    # se reducen a la mitad; si es inmune al elemento, no se aplica.
    if isinstance(attacker, Player) and hasattr(defender, "apply_status"):
        _try_inflict_weapon_status(attacker, defender, element)

    if isinstance(attacker, Player):
        print_status(attacker, defender, defeated_enemies)
    else:
        print_status(defender, attacker, defeated_enemies)


def _try_inflict_weapon_status(player: "Player", enemy, element: str | None) -> None:
    """Si el arma equipada inflige un estado (explícito en `inflicts` o derivado
    de su elemento), lo tira. La resistencia del enemigo al elemento reduce a la
    mitad la probabilidad y la duración; la inmunidad al elemento lo anula."""
    # Desarmado: el arma no está en tus manos, así que no inflige nada
    # (igual que no cuenta su bonus de daño ni su elemento).
    if any(e["name"] == "desarmado" for e in player.status_effects):
        return
    weapon = player.equipped_weapon
    inflicts = weapon.get_inflicts() if weapon and hasattr(weapon, "get_inflicts") else None
    if not inflicts:
        return
    if element and enemy.affinity_for({element}) == 0.0:
        return  # inmune al elemento -> tampoco el estado

    chance = inflicts["chance"]
    duration = inflicts["duration"]
    if element and enemy.resists_element(element):
        chance *= 0.5
        duration = max(1, duration // 2)

    if random.random() < chance and enemy.apply_status(inflicts["status"], duration, inflicts.get("power", 0)):
        console.warning(_status_inflicted_message(enemy.name, inflicts["status"]))


def _status_inflicted_message(name: str, status: str) -> str:
    """'X ha sido envenenado/quemado/...' (o un mensaje propio para estados sin
    participio natural como `fractura_magica`)."""
    override = f"combat.status_inflicted.{status}"
    if i18n.has(override):
        return i18n.t(override, name=name)
    verb = i18n.t(f"status.verb.{status}")
    if verb == f"status.verb.{status}":  # sin participio -> forma genérica
        verb = status_label(status)
    return i18n.t("combat.status_inflicted", name=name, verb=verb)


def _handle_victory(player, enemy, defeated_enemies: list, unlocked_enemies: list) -> tuple:
    print(f"\n{console.colorize(f'¡VICTORIA! {enemy.name} ha sido derrotado.', console.Fore.YELLOW, bright=True)}")

    player.enemy_kill_counts[enemy.name] = player.enemy_kill_counts.get(enemy.name, 0) + 1

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


def _restore_player(player, snapshot: dict, max_recovery: int | None = None) -> None:
    """Elimina efectos, restaura stats base y cura al jugador.

    `max_recovery`, si se indica (huida), limita la curación a como mucho la
    vida perdida durante ESTE combate — huir no es una victoria, así que no
    debería curar daño acumulado de peleas anteriores.
    """
    # Restaurar stats base (por si hubo pociones de fuerza/defensa)
    player.stats.min_atk, player.stats.max_atk = snapshot["atk"]
    player.stats.armor = snapshot["armor"]

    # Limpiar estados alterados
    player.status_effects = []
    player.defending = False

    if hasattr(player, "active_effects"):
        player.active_effects = []

    # Recuperar Salud al finalizar
    if player.is_alive():
        if player.just_leveled_up:
            print(console.colorize("✨ ¡Energía renovada por el nuevo nivel!", console.Fore.MAGENTA))
            player.just_leveled_up = False  # Reseteamos el flag
        else:
            # Lógica de curación normal (50% de lo perdido)
            missing_health = player.stats.max_health - player.stats.health
            if max_recovery is not None:
                missing_health = max(0, min(missing_health, max_recovery))
            recovery = missing_health // 2
            player.stats.health += recovery
            if recovery > 0:
                print(
                    f"\n{console.colorize(f'Tras el combate, descansas y recuperas {recovery} HP.', console.Fore.GREEN)}"
                )
                print(
                    console.colorize(
                        f"Vida actual: {player.stats.health}/{player.stats.max_health}", console.Fore.GREEN
                    )
                )
