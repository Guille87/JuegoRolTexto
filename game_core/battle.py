import random
import time

from colorama import Fore, Style

from assets.resources.resource_manager import ResourceManager
from characters.enemies import Goblin, Skeleton, Orc, Troll, Mago
from items.item import Potion

from utils.utils import print_player_enemy_info, print_status

# Instancia global de ResourceManager
resource_manager = ResourceManager()


def auto_battle(player, enemy, defeated_enemies):
    print("="*60)
    print(f"{Style.BRIGHT}¡Ha comenzado la batalla automática!{Style.RESET_ALL}")
    print_player_enemy_info(player, enemy, defeated_enemies)

    # Define una bandera para controlar si el ataque ya ha sido reducido a la mitad por el estado de quemado
    attack_reduced = False
    # Define una bandera para controlar si se ha aplicado un emboscada
    ambush_applied = False

    # Antes de aplicar el efecto de aumento/reducción de daño, guarda los valores originales del ataque
    original_min_attack = player.min_attack
    original_max_attack = player.max_attack
    # Antes de aplicar el efecto de aumento/reducción de defensa, guardar el valor original de la defensa
    original_defense = player.defense

    # Ciclo de batalla, continúa mientras ambos tienen vida
    while player.health > 0 and enemy.health > 0:
        random_number = random.random()
        # Aplicar efectos del estado al jugador si está afectado
        if player.status_effect:
            if player.status_effect == "quemado":
                # Reducir un 6.25% de la salud máxima
                health_reduction = player.max_health // 16
                player.health = max(0, player.health - health_reduction)
                # Reducir el ataque a la mitad solo si no ha sido reducido antes
                if not attack_reduced:
                    player.min_attack //= 2
                    player.max_attack //= 2
                    attack_reduced = True  # Marcar que el ataque ha sido reducido
                print(f"{Fore.GREEN}{player.name}{Style.RESET_ALL} sufre de {Fore.RED}quemadura{Style.RESET_ALL} y pierde "
                      f"{Fore.RED}{health_reduction}{Style.RESET_ALL} puntos de salud.")
                if player.health <= 0:
                    player.health = 0  # Asegura que la salud no sea negativa
                    print(f"{Fore.RED}{Style.BRIGHT}{player.name} ha sido derrotado a causa del {player.status_effect}.{Style.RESET_ALL}")
                    restore_player_after_battle(player, original_min_attack, original_max_attack, original_defense)
                    break
            elif player.status_effect == "paralizado":
                # Hay un 50% de probabilidad de que el jugador no pueda atacar
                if random.random() < 0.5:
                    print(f"{Fore.GREEN}{player.name}{Style.RESET_ALL} está paralizado y no puede atacar.")
                    # El jugador no realiza ninguna acción en este turno
            elif player.status_effect == "envenenado":
                # Calcular el daño del veneno en función del turno actual del envenenamiento
                poison_damage = (2 ** (3 - player.status_duration)) * (player.max_health // 16)
                # Aplicar el daño al jugador
                player.health = max(0, player.health - poison_damage)
                print(f"{Fore.GREEN}{player.name}{Style.RESET_ALL} sufre de {Fore.GREEN}envenenamiento{Style.RESET_ALL} y pierde "
                      f"{Fore.RED}{poison_damage}{Style.RESET_ALL} puntos de salud.")
                if player.health <= 0:
                    player.health = 0  # Asegura que la salud no sea negativa
                    print(f"{Fore.RED}{Style.BRIGHT}{player.name} ha sido derrotado a causa del veneno.{Style.RESET_ALL}")
                    restore_player_after_battle(player, original_min_attack, original_max_attack, original_defense)
                    break
            elif player.status_effect == "congelado":
                print(f"{Fore.GREEN}{player.name}{Style.RESET_ALL} está {Fore.BLUE}congelado{Style.RESET_ALL} y no puede realizar ninguna acción.")
                # El jugador no realiza ninguna acción en este turno

        # Aplica una emboscada si el enemigo es un Goblin y aún no se ha aplicado una emboscada
        if enemy.name == "Goblin" and not ambush_applied:
            if enemy.ambush_probability():
                enemy.apply_ambush(player)
                print_status(player, enemy, defeated_enemies)
            ambush_applied = True
            # Pausa la ejecución por un breve período de tiempo para que sea más legible
            time.sleep(1)

        # Ataque del jugador comprobando los efectos de estado
        if player.status_effect != "congelado" or player.status_effect == "paralizado" and random_number >= 0.5:
            player_attack(player, enemy, defeated_enemies)
            if check_enemy_defeated(player, enemy, original_min_attack, original_max_attack, original_defense):
                return True  # Salir del bucle si el enemigo está derrotado

        # Reducir 1 turno la duración de los efectos de estado
        if player.status_effect is not None:
            player.reduce_status_duration()
        # Cuando el efecto de quemado se disipe, restaura los valores originales del ataque
        if player.status_effect is None or player.status_duration == 0:
            if attack_reduced:
                restore_attack_after_burn(player, original_min_attack, original_max_attack)
                attack_reduced = False  # Restaurar la bandera

        # Pausa la ejecución por un breve período de tiempo para que sea más legible
        time.sleep(1)

        # Si el enemigo es un Orc, se incrementa el contador de turnos para activar la Furia.
        if isinstance(enemy, Orc):
            enemy.increase_fury_turns()

        # Regeneración de salud del Troll
        if isinstance(enemy, Troll):  # Verifica si el enemigo es un Troll
            if enemy.health < Troll.max_health:  # Verificar si la salud del Troll no está al máximo
                regen_amount = enemy.regenerate_health()  # Obtiene la cantidad de salud regenerada
                # Calcula la cantidad máxima que el Troll puede regenerar
                max_regen_amount = Troll.max_health - enemy.health
                # Determina la cantidad real de salud regenerada
                actual_regen_amount = min(regen_amount, max_regen_amount)
                if actual_regen_amount > 0:  # Verifica si el Troll realmente regenera salud
                    enemy.health += actual_regen_amount  # Actualiza la salud del Troll
                    print(
                        f"{Fore.RED}{enemy.name}{Style.RESET_ALL} regenera {Fore.GREEN}{actual_regen_amount}"
                        f"{Style.RESET_ALL} de salud.")
                    # Pausa la ejecución por un breve período de tiempo para que sea más legible
                    time.sleep(1)

        if isinstance(enemy, Mago) and random_number < 0.5:  # 50% de probabilidad de que el Mago realice un hechizo
            spell_type = enemy.cast_spell()
            # Si el hechizo fue de daño, inflige daño al jugador
            if spell_type != "Curación":
                # Calcula el daño del hechizo del enemigo y cualquier efecto de estado asociado.
                enemy_spell_damage_spell_type = enemy.spell_damage(spell_type)
                # Extrae el daño del hechizo y el efecto de estado del resultado obtenido.
                spell_damage, status_effect = enemy_spell_damage_spell_type
                # Reduce el daño del hechizo por la defensa del jugador.
                spell_damage -= player.defense
                # Asegura que el daño no sea negativo y actualiza la salud del jugador.
                player.health = max(0, player.health - spell_damage)
                print(f"{Fore.RED}{enemy.name}{Style.RESET_ALL} lanza un hechizo de ", end="")
                if spell_type == "Bola de fuego":
                    print(f"{Fore.RED}{spell_type}{Style.RESET_ALL}", end="")
                elif spell_type == "Rayo":
                    print(f"{Fore.YELLOW}{spell_type}{Style.RESET_ALL}", end="")
                elif spell_type == "Veneno":
                    print(f"{Fore.GREEN}{spell_type}{Style.RESET_ALL}", end="")
                elif spell_type == "Ventisca":
                    print(f"{Fore.BLUE}{spell_type}{Style.RESET_ALL}", end="")
                else:
                    print(spell_type, end="")
                print(f" y hace {Fore.RED}{spell_damage}{Style.RESET_ALL} de daño a {Fore.GREEN}{player.name}{Style.RESET_ALL}.")
                if status_effect:
                    effect_color = Fore.WHITE  # Por defecto
                    duration = random.randint(1, 5)  # Duración por defecto
                    if status_effect == "quemado":
                        duration = random.randint(2, 5)  # Quemado dura entre 2 y 5 turnos
                    elif status_effect == "paralizado":
                        duration = random.randint(2, 4)  # Paralizado dura entre 2 y 4 turnos
                    elif status_effect == "envenenado":
                        duration = random.randint(2, 3)  # Envenenado dura entre 2 y 3 turnos
                    elif status_effect == "congelado":
                        duration = random.randint(1, 2)  # Congelado dura entre 1 y 2 turnos
                    if spell_type == "Bola de fuego":
                        effect_color = Fore.RED
                    elif spell_type == "Rayo":
                        effect_color = Fore.YELLOW
                    elif spell_type == "Veneno":
                        effect_color = Fore.GREEN
                    elif spell_type == "Ventisca":
                        effect_color = Fore.BLUE
                    if player.apply_status_effect(status_effect, duration):  # Aplicar el efecto de estado por 3 turnos
                        print(f"{effect_color}{player.name} ha sido {status_effect} durante {player.status_duration} turnos.{Style.RESET_ALL}")
            # Si el hechizo fue de curación, se cura a sí mismo
            else:
                # Verificar si la salud del Mago no está al máximo antes de utilizar magia curativa
                if enemy.health < Mago.max_health:  # Verificar si la salud del Mago no está al máximo
                    heal_amount = enemy.cast_heal()  # Obtiene la cantidad de salud recuperada
                    # Calcula la cantidad máxima que el Mago puede recuperada
                    max_regen_amount = Mago.max_health - enemy.health
                    # Determina la cantidad real de salud recuperada
                    actual_heal_amount = min(heal_amount, max_regen_amount)
                    if actual_heal_amount > 0:  # Verifica si el Mago realmente recupera salud
                        enemy.health += actual_heal_amount  # Actualiza la salud del Mago
                        print(f"{Fore.RED}{enemy.name}{Style.RESET_ALL} utiliza magia curativa y se cura "
                              f"{Fore.GREEN}{actual_heal_amount}{Style.RESET_ALL} de salud.")
                    print_status(player, enemy, defeated_enemies)
                else:
                    # Si la salud del Mago está al máximo, lanza un ataque
                    enemy_attack(player, enemy)
                    print_status(player, enemy, defeated_enemies)
                    if check_player_defeated(player, original_min_attack, original_max_attack, original_defense):
                        break  # Salir del bucle si el jugador está derrotado
            # Pausa la ejecución por un breve período de tiempo para que sea más legible
            time.sleep(1)
            if check_player_defeated(player, original_min_attack, original_max_attack, original_defense):
                break  # Salir del bucle si el jugador está derrotado
        else:
            enemy_attack(player, enemy)
            print_status(player, enemy, defeated_enemies)
            # Pausa la ejecución por un breve período de tiempo para que sea más legible
            time.sleep(1)
            if check_player_defeated(player, original_min_attack, original_max_attack, original_defense):
                break  # Salir del bucle si el jugador está derrotado
        # Si el enemigo es un Orc, se incrementa el contador de turnos para desactivar la Furia.
        if isinstance(enemy, Orc):
            enemy.increment_fury_turns_for_deactivation()
        # Comprobar la duración de la poción
        player.check_duration()


def battle(player, enemy, defeated_enemies):
    print("="*60)
    print(f"{Style.BRIGHT}¡Ha comenzado la batalla!{Style.RESET_ALL}")
    print_player_enemy_info(player, enemy, defeated_enemies)

    # Bandera para controlar si el ataque ya ha sido reducido a la mitad por el estado de quemado
    attack_reduced = False
    # Bbandera para controlar si se ha aplicado un emboscada
    ambush_applied = False
    # Bandera para controlar si se ha realizado el primer movimiento
    first_movement_made = False

    # Guarda los valores originales del ataque
    original_min_attack = player.min_attack
    original_max_attack = player.max_attack
    original_defense = player.defense

    # Ciclo de batalla, continúa mientras ambos tienen vida
    while player.health > 0 and enemy.health > 0:
        valid_options = ["Atacar", "Objetos", "Información", "Huir"]
        if enemy.name in defeated_enemies and not first_movement_made:
            valid_options.append("Batalla automática")

        print_menu_options(valid_options)
        choice = input(f"Elige una opción (1-{len(valid_options)}): ")
        print("="*60)

        # Turno del jugador
        if choice == "1":
            first_movement_made = True  # El jugador ha realizado el primero movimiento
            # Aplicar efectos del estado al jugador si está afectado
            if player.status_effect:
                if player.status_effect == "quemado":
                    # Reducir un 6.25% de la salud máxima
                    health_reduction = player.max_health // 16
                    player.health = max(0, player.health - health_reduction)
                    # Reducir el ataque a la mitad solo si no ha sido reducido antes
                    if not attack_reduced:
                        player.min_attack //= 2
                        player.max_attack //= 2
                        attack_reduced = True  # Marcar que el ataque ha sido reducido
                    print(f"{Fore.GREEN}{player.name}{Style.RESET_ALL} sufre de {Fore.RED}quemadura{Style.RESET_ALL} y pierde "
                          f"{Fore.RED}{health_reduction}{Style.RESET_ALL} puntos de salud.")
                    if player.health <= 0:
                        player.health = 0  # Asegura que la salud no sea negativa
                        print(f"{Fore.RED}{Style.BRIGHT}{player.name} ha sido derrotado a causa del {player.status_effect}.{Style.RESET_ALL}")
                        restore_player_after_battle(player, original_min_attack, original_max_attack, original_defense)
                        break
                elif player.status_effect == "paralizado":
                    # Hay un 50% de probabilidad de que el jugador no pueda atacar
                    if random.random() < 0.5:
                        print(f"{Fore.GREEN}{player.name}{Style.RESET_ALL} está paralizado y no puede atacar.")
                        # El jugador no realiza ninguna acción en este turno
                        choice = None
                elif player.status_effect == "envenenado":
                    # Calcular el daño del veneno en función del turno actual del envenenamiento
                    poison_damage = (2 ** (3 - player.status_duration)) * (player.max_health // 16)
                    # Aplicar el daño al jugador
                    player.health = max(0, player.health - poison_damage)
                    print(f"{Fore.GREEN}{player.name}{Style.RESET_ALL} sufre de {Fore.GREEN}envenenamiento{Style.RESET_ALL} y pierde "
                          f"{Fore.RED}{poison_damage}{Style.RESET_ALL} puntos de salud.")
                    if player.health <= 0:
                        player.health = 0  # Asegura que la salud no sea negativa
                        print(f"{Fore.RED}{Style.BRIGHT}{player.name} ha sido derrotado a causa del veneno.{Style.RESET_ALL}")
                        restore_player_after_battle(player, original_min_attack, original_max_attack, original_defense)
                        break
                elif player.status_effect == "congelado":
                    print(f"{Fore.GREEN}{player.name}{Style.RESET_ALL} está {Fore.BLUE}congelado{Style.RESET_ALL} y no puede realizar ninguna acción.")
                    # El jugador no realiza ninguna acción en este turno
                    choice = None

            # Aplica una emboscada si el enemigo es un Goblin y aún no se ha aplicado una emboscada
            if enemy.name == "Goblin" and not ambush_applied:
                if enemy.ambush_probability():
                    enemy.apply_ambush(player)
                    print_status(player, enemy, defeated_enemies)
                    input(
                        f"Es el turno de {Fore.GREEN}{player.name}{Style.RESET_ALL}. Presiona {Fore.GREEN}Enter{Style.RESET_ALL} "
                        f"para que {Fore.GREEN}{player.name}{Style.RESET_ALL} ataque...")
                    print("="*60)
                ambush_applied = True

            # Reducir 1 turno la duración de los efectos de estado
            if player.status_effect is not None:
                player.reduce_status_duration()
            # Cuando el efecto de quemado se disipe, restaura los valores originales del ataque
            if player.status_effect is None or player.status_duration == 0:
                if attack_reduced:
                    restore_attack_after_burn(player, original_min_attack, original_max_attack)
                    attack_reduced = False  # Restaurar la bandera

            # Si el jugador puede atacar después de aplicar los efectos del estado
            if choice == "1":
                player_attack(player, enemy, defeated_enemies)
                if check_enemy_defeated(player, enemy, original_min_attack, original_max_attack, original_defense):
                    return True  # Salir del bucle si el enemigo está derrotado

            # Turno del enemigo
            enemy_turn(player, enemy, defeated_enemies, original_min_attack, original_max_attack, original_defense)

            if check_player_defeated(player, original_min_attack, original_max_attack, original_defense):
                return  # Salir del bucle si el jugador está derrotado

            # Comprobar la duración de la poción
            player.check_duration()
        elif choice == "2":
            first_movement_made = True  # El jugador ha realizado el primero movimiento
            # Mostrar los objetos del jugador y permitirle usarlos
            player.show_inventory()
            item_choice = player.inventory.select_item_from_inventory()  # Utilizar el método para seleccionar un objeto del inventario
            if item_choice:
                item = item_choice
                if isinstance(item, Potion):  # Verificar si el objeto es una poción
                    if item.healing_amount is not None:  # Verificar si la poción restaura salud
                        if player.health >= player.max_health:
                            print(f"{Fore.RED}¡Tu salud ya está al máximo! No puedes usar {item.name} en este momento.{Style.RESET_ALL}")
                        else:
                            # Calcular la cantidad de salud que se restaurará sin exceder la salud máxima
                            healing_amount = min(item.healing_amount, player.max_health - player.health)
                            # Usar la poción para curar al jugador
                            player.health += healing_amount
                            # Restar la poción del inventario del jugador
                            player.inventory.remove_item(item)
                            print(f"¡Has usado {Fore.GREEN}{Style.BRIGHT}{item.name}{Style.RESET_ALL} y recuperaste "
                                  f"{Fore.GREEN}{Style.BRIGHT}{item.healing_amount}{Style.RESET_ALL} puntos de salud!")
                            # Turno del enemigo
                            enemy_turn(player, enemy, defeated_enemies, original_min_attack, original_max_attack, original_defense)
                    elif item.defense_boost is not None:  # Verificar si la poción otorga un aumento de defensa
                        if any(potion.name == "Poción de Resistencia" for potion in player.active_potions):
                            print(f"{Fore.RED}Ya tienes el efecto de la poción de resistencia activo.{Style.RESET_ALL}")
                        else:
                            # Aplicar el efecto de la poción
                            player.apply_potion_effect("Poción de Resistencia", 3)
                            # Aplicar el aumento de defensa al jugador
                            player.defense += item.defense_boost
                            # Restar la poción del inventario del jugador
                            player.inventory.remove_item(item)
                            print(f"¡Has usado {Fore.LIGHTBLUE_EX}{item.name}{Style.RESET_ALL} y obtuviste un aumento de {item.defense_boost} de defensa!")
                            # Turno del enemigo
                            enemy_turn(player, enemy, defeated_enemies, original_min_attack, original_max_attack, original_defense)
                            # Comprobar la duración de la poción
                            player.check_duration()
                    elif item.damage_boost is not None:  # Verificar si la poción otorga un aumento de daño
                        if any(potion.name == "Poción de Fuerza" for potion in player.active_potions):
                            print(f"{Fore.RED}Ya tienes el efecto de la poción de fuerza activo.{Style.RESET_ALL}")
                        else:
                            # Aplicar el efecto de la poción
                            player.apply_potion_effect("Poción de Fuerza", 3)
                            # Aplicar el aumento de daño al jugador
                            player.min_attack += item.damage_boost
                            player.max_attack += item.damage_boost
                            # Restar la poción del inventario del jugador
                            player.inventory.remove_item(item)
                            print(f"¡Has usado {Fore.LIGHTRED_EX}{item.name}{Style.RESET_ALL} y obtuviste un aumento "
                                  f"de {Fore.LIGHTRED_EX}{item.damage_boost}{Style.RESET_ALL} de daño!")
                            # Turno del enemigo
                            enemy_turn(player, enemy, defeated_enemies, original_min_attack, original_max_attack, original_defense)
                            # Comprobar la duración de la poción
                            player.check_duration()
                    elif item.regeneration_amount is not None:  # Verificar si la poción otorga regeneración de salud
                        if any(potion.name == "Poción de Regeneración" for potion in player.active_potions):
                            print(f"{Fore.RED}Ya tienes el efecto de la poción de regeneración activo.{Style.RESET_ALL}")
                        else:
                            # Aplicar el efecto de la poción
                            player.apply_potion_effect("Poción de Regeneración", 3)
                            # Restar la poción del inventario del jugador
                            player.inventory.remove_item(item)
                            print(f"¡Has usado {Fore.LIGHTGREEN_EX}{item.name}{Style.RESET_ALL} y comenzaste a regenerar "
                                  f"{Fore.LIGHTGREEN_EX}{item.regeneration_amount}{Style.RESET_ALL} puntos de salud por turno!")
                            # Turno del enemigo
                            enemy_turn(player, enemy, defeated_enemies, original_min_attack, original_max_attack, original_defense)
                            # Comprobar la duración de la poción
                            player.check_duration()
                else:
                    print("No puedes usar ese objeto en combate.")
        elif choice == "3":
            print_player_enemy_info(player, enemy, defeated_enemies)
        elif choice == "4":
            # El jugador decide huir
            print(f"{Fore.GREEN}{player.name}{Style.RESET_ALL} ha huido del combate.")
            restore_player_after_battle(player, original_min_attack, original_max_attack, original_defense)
            return
        elif choice == "5" and enemy.name in defeated_enemies:
            auto_battle(player, enemy, defeated_enemies)
        else:
            print_invalid_option(valid_options)
    restore_player_after_battle(player, original_min_attack, original_max_attack, original_defense)


def enemy_turn(player, enemy, defeated_enemies, original_min_attack, original_max_attack, original_defense):
    # Turno del enemigo
    input(f"Es el turno de {Fore.RED}{enemy.name}{Style.RESET_ALL}. Presiona {Fore.GREEN}Enter{Style.RESET_ALL} "
          f"para que {Fore.RED}{enemy.name}{Style.RESET_ALL} ataque...")
    print("="*60)

    if isinstance(enemy, Orc):
        enemy.increase_fury_turns()

    # Regeneración de salud del Troll
    if isinstance(enemy, Troll):  # Verifica si el enemigo es un Troll
        if enemy.health < Troll.max_health:  # Verificar si la salud del Troll no está al máximo
            regen_amount = enemy.regenerate_health()  # Obtiene la cantidad de salud regenerada
            # Calcula la cantidad máxima que el Troll puede regenerar
            max_regen_amount = Troll.max_health - enemy.health
            # Determina la cantidad real de salud regenerada
            actual_regen_amount = min(regen_amount, max_regen_amount)
            if actual_regen_amount > 0:  # Verifica si el Troll realmente regenera salud
                enemy.health += actual_regen_amount  # Actualiza la salud del Troll
                print(
                    f"{Fore.RED}{enemy.name}{Style.RESET_ALL} regenera {Fore.GREEN}{actual_regen_amount}"
                    f"{Style.RESET_ALL} de salud.")

    if isinstance(enemy, Mago) and random.random() < 0.5:  # 50% de probabilidad de que el Mago realice un hechizo
        spell_type = enemy.cast_spell()
        # Si el hechizo fue de daño, inflige daño al jugador
        if spell_type != "Curación":
            # Calcula el daño del hechizo del enemigo y cualquier efecto de estado asociado.
            enemy_spell_damage_spell_type = enemy.spell_damage(spell_type)
            # Extrae el daño del hechizo y el efecto de estado del resultado obtenido.
            spell_damage, status_effect = enemy_spell_damage_spell_type
            # Resta la defensa del jugador del daño del hechizo.
            spell_damage = max(0, spell_damage - player.defense)
            # Asegura que el daño no sea negativo y actualiza la salud del jugador.
            player.health = max(0, player.health - spell_damage)
            print(f"{Fore.RED}{enemy.name}{Style.RESET_ALL} lanza un hechizo de ", end="")
            if spell_type == "Bola de fuego":
                print(f"{Fore.RED}{spell_type}{Style.RESET_ALL}", end="")
            elif spell_type == "Rayo":
                print(f"{Fore.YELLOW}{spell_type}{Style.RESET_ALL}", end="")
            elif spell_type == "Veneno":
                print(f"{Fore.GREEN}{spell_type}{Style.RESET_ALL}", end="")
            elif spell_type == "Ventisca":
                print(f"{Fore.BLUE}{spell_type}{Style.RESET_ALL}", end="")
            else:
                print(spell_type, end="")
            if spell_damage > 0:
                print(f" y hace {Fore.RED}{spell_damage}{Style.RESET_ALL} de daño a {Fore.GREEN}{player.name}{Style.RESET_ALL}.")
            else:
                print(f" y {Fore.GREEN}{player.name}{Style.RESET_ALL} {Fore.BLUE}bloquea{Style.RESET_ALL} el hechizo.")
            if status_effect:
                effect_color = Fore.WHITE  # Color por defecto
                duration = random.randint(1, 5)  # Duración por defecto
                if status_effect == "quemado":
                    duration = random.randint(2, 5)  # Quemado dura entre 2 y 5 turnos
                elif status_effect == "paralizado":
                    duration = random.randint(2, 4)  # Paralizado dura entre 2 y 4 turnos
                elif status_effect == "envenenado":
                    duration = random.randint(2, 3)  # Envenenado dura entre 2 y 3 turnos
                elif status_effect == "congelado":
                    duration = random.randint(1, 2)  # Congelado dura entre 1 y 2 turnos
                if spell_type == "Bola de fuego":
                    effect_color = Fore.RED
                elif spell_type == "Rayo":
                    effect_color = Fore.YELLOW
                elif spell_type == "Veneno":
                    effect_color = Fore.GREEN
                elif spell_type == "Ventisca":
                    effect_color = Fore.BLUE
                if player.apply_status_effect(status_effect, duration):  # Aplicar el efecto de estado por X turnos
                    print(f"{effect_color}{player.name} ha sido {status_effect} durante {player.status_duration} turnos.{Style.RESET_ALL}")
            print_status(player, enemy, defeated_enemies)
        # Si el hechizo fue de curación, se cura a sí mismo
        else:
            # Verificar si la salud del Mago no está al máximo antes de utilizar magia curativa
            if enemy.health < Mago.max_health:  # Verificar si la salud del Mago no está al máximo
                heal_amount = enemy.cast_heal()  # Obtiene la cantidad de salud recuperada
                # Calcula la cantidad máxima que el Mago puede recuperar
                max_regen_amount = Mago.max_health - enemy.health
                # Determina la cantidad real de salud recuperada
                actual_heal_amount = min(heal_amount, max_regen_amount)
                if actual_heal_amount > 0:  # Verifica si el Mago realmente recupera salud
                    enemy.health += actual_heal_amount  # Actualiza la salud del Mago
                    print(f"{Fore.RED}{enemy.name}{Style.RESET_ALL} utiliza magia curativa y se cura "
                          f"{Fore.GREEN}{actual_heal_amount}{Style.RESET_ALL} de salud.")
                print_status(player, enemy, defeated_enemies)
            else:
                # Si la salud del Mago está al máximo, lanzar un hechizo de daño
                enemy_attack(player, enemy)
                print_status(player, enemy, defeated_enemies)
    else:
        enemy_attack(player, enemy)
        print_status(player, enemy, defeated_enemies)
    # Si el enemigo es un Orc y está en estado de Furia, se incrementa el contador de turnos para desactivar la Furia.
    if isinstance(enemy, Orc):
        enemy.increment_fury_turns_for_deactivation()


def player_attack(player, enemy, defeated_enemies):
    """
    Maneja la lógica de ataque del jugador.
    """
    player_damage = player.attack_damage() - enemy.defense
    if player_damage <= 0:
        print(f"{Fore.RED}{enemy.name}{Style.RESET_ALL} ha {Fore.BLUE}bloqueado{Style.RESET_ALL} el ataque de "
              f"{Fore.GREEN}{player.name}{Style.RESET_ALL}.")
    else:
        enemy.health = max(0, enemy.health - player_damage)  # Asegura que la salud no sea negativa
        print(
            f"{Fore.GREEN}{player.name}{Style.RESET_ALL} ataca a {Fore.RED}{enemy.name}{Style.RESET_ALL} y le "
            f"hace {Fore.GREEN}{player_damage}{Style.RESET_ALL} de daño.")
    print_status(player, enemy, defeated_enemies)

    # Reproducir aleatoriamente uno de los dos sonidos
    sound_to_play = random.choice(["metal_hit_woosh", "sword_slash_swoosh"])
    resource_manager.play_sound(sound_to_play)

    # Si el esqueleto aún no ha sido derrotado y no tiene salud, resucita con la mitad de la vida máxima
    if isinstance(enemy, Skeleton) and not enemy.defeated_once and enemy.health <= 0:
        enemy.health = enemy.max_health // 2  # Esqueleto resucita con la mitad de vida
        enemy.defeated_once = True
        print(f"{Fore.RED}{enemy.name}{Style.RESET_ALL} está a punto de ser {Fore.RED}derrotado{Style.RESET_ALL}, "
              f"pero resucita de entre los muertos.")
        print_status(player, enemy, defeated_enemies)


def check_enemy_defeated(player, enemy, original_min_attack, original_max_attack, original_defense):
    if enemy.health <= 0:
        enemy.health = 0  # Asegura que la salud no sea negativa
        print(f"{Fore.GREEN}{Style.BRIGHT}{enemy.name} ha sido derrotado.{Style.RESET_ALL}")
        restore_player_after_battle(player, original_min_attack, original_max_attack, original_defense)

        exp = random.randint(20, 30)
        if isinstance(enemy, Goblin):
            player.gain_experience(exp)
        elif isinstance(enemy, Skeleton):
            player.gain_experience(exp*2)
        elif isinstance(enemy, Orc):
            player.gain_experience(exp*6)
        elif isinstance(enemy, Troll):
            player.gain_experience(exp*12)
        elif isinstance(enemy, Mago):
            player.gain_experience(exp*20)

        # Verifica si el enemigo tiene un ítem para soltar
        if hasattr(enemy, 'drop_item'):
            dropped_items = enemy.drop_item()
            for item in dropped_items:
                player.inventory.add_item(item)

        # Obtener el oro del enemigo derrotado
        enemy_gold = enemy.drop_gold()

        # Añadir el oro al inventario del jugador
        player.inventory.add_gold(enemy_gold)
        return True
    return False


def enemy_attack(player, enemy):
    """
    Maneja la lógica de ataque del enemigo.
    """
    enemy_damage = enemy.attack_damage_enemy()
    damage_taken = player.take_damage(enemy_damage)
    if enemy_damage <= 0:
        print(
            f"{Fore.GREEN}{player.name}{Style.RESET_ALL} ha {Fore.BLUE}bloqueado{Style.RESET_ALL} el ataque "
            f"de {Fore.RED}{enemy.name}{Style.RESET_ALL}")
    else:
        if player.health <= 0:
            player.health = 0  # Asegura que la salud no sea negativa
        print(f"{Fore.RED}{enemy.name}{Style.RESET_ALL} ataca a {Fore.GREEN}{player.name}"
              f"{Style.RESET_ALL} y le hace {Fore.RED}{damage_taken}{Style.RESET_ALL} de daño")


def check_player_defeated(player, original_min_attack, original_max_attack, original_defense):
    if player.health <= 0:
        print(f"{Fore.RED}{Style.BRIGHT}{player.name} ha sido derrotado.{Style.RESET_ALL}")
        # Calcular el 10% del oro total del jugador
        gold_to_remove = int(player.inventory.gold * 0.1)
        # Verificar si la cantidad calculada es mayor que la cantidad actual de oro
        if 0 < gold_to_remove <= player.inventory.gold:
            # Restar el 10% del oro total del inventario del jugador
            player.inventory.remove_gold(gold_to_remove)
            print(f"{Fore.RED}Has perdido {Fore.YELLOW}{gold_to_remove}{Style.RESET_ALL}{Fore.RED} de oro.{Style.RESET_ALL}")
        elif gold_to_remove > 0:
            print("No tienes suficiente oro para perder.")
        restore_player_after_battle(player, original_min_attack, original_max_attack, original_defense)
        return True
    return False


def restore_attack_after_burn(player, original_min_attack, original_max_attack):
    """
    Restaura los valores originales del ataque del jugador después de que el efecto de quemado se disipe.
    """
    player.min_attack = original_min_attack
    player.max_attack = original_max_attack


def restore_player_after_battle(player, original_min_attack, original_max_attack, original_defense):
    """
    Restaura los valores originales del jugador después de la batalla.
    """
    # Recuperar la vida del jugador al finalizar la batalla
    player.health = player.max_health
    # Restaura el efecto de estado al finalizar la batalla
    player.status_effect = None
    # Restaura los valores originales del ataque
    player.min_attack = original_min_attack
    player.max_attack = original_max_attack
    # Restaura el valor original de la defensa
    player.defense = original_defense


def print_invalid_option(options):
    print(f"{Fore.RED}Opción no válida. Por favor, elige una de las opciones (1-{len(options)}).{Style.RESET_ALL}")


def print_menu_options(valid_options):
    print("Opciones:")
    for idx, option in enumerate(valid_options, start=1):
        print(f"{idx}. {option}")


def initiate_battle(player, unlocked_enemies, defeated_enemies):
    # Lista de enemigos disponibles con sus clases correspondientes
    all_enemy_types = [("Goblin", Goblin), ("Esqueleto", Skeleton), ("Orco", Orc), ("Troll", Troll), ("Mago", Mago)]

    # Filtra los enemigos disponibles según los desbloqueados
    available_enemies = [(name, enemy_class) for name, enemy_class in all_enemy_types if name in unlocked_enemies]

    if not available_enemies:
        print("No hay enemigos desbloqueados. Derrota a los enemigos anteriores primero.")
        return

    while True:  # Bucle para solicitar la elección del enemigo hasta que se elija uno válido
        print("="*60)
        print("Enemigos disponibles:")
        print("0. Volver atrás")  # Opción para volver atrás
        # Muestra los nombres de los enemigos disponibles con sus números correspondientes
        for i, (enemy_name, _) in enumerate(available_enemies, start=1):
            print(f"{i}. {enemy_name}")

        # Solicita al jugador que elija un número correspondiente al enemigo contra el que quiere pelear
        enemy_choice = input("Elige contra qué enemigo quieres pelear: ")
        try:
            # Convierte la opción del jugador en un número entero
            enemy_index = int(enemy_choice)
            if enemy_index == 0:
                return  # Salir de la función si se elige volver atrás
            elif 0 < enemy_index <= len(available_enemies):  # Verifica si el índice está dentro del rango
                # Obtiene el nombre y la clase del enemigo seleccionado
                selected_enemy_name, selected_enemy_type = available_enemies[enemy_index - 1]
                # Crea una instancia del enemigo seleccionado
                enemy = selected_enemy_type(selected_enemy_name)

                if isinstance(enemy, Orc):
                    # Detener la música menos la que voy a reproducir a continuación
                    resource_manager.stop_all_music("scaring_Crows")
                    # Iniciar música de fondo si aún no se ha iniciado
                    if not resource_manager.is_music_playing("scaring_Crows"):
                        resource_manager.play_music("scaring_Crows", loops=-1)

                # Comienza la batalla con el jugador y el enemigo seleccionados
                won_battle = battle(player, enemy, defeated_enemies)
                # Actualiza la lista de enemigos desbloqueados después de la batalla exitosa
                if won_battle and selected_enemy_name == unlocked_enemies[-1]:  # Verifica si se ganó la batalla y si es el último enemigo desbloqueado
                    defeated_enemies.append(enemy.name)  # Agrega el nombre del enemigo a la lista de enemigos derrotados
                    next_enemy_index = unlocked_enemies.index(selected_enemy_name) + 1
                    if next_enemy_index < len(all_enemy_types):
                        next_enemy_name, _ = all_enemy_types[next_enemy_index]
                        unlocked_enemies.append(next_enemy_name)
                # Salir de la función de batalla después de que termine
                return
            else:
                print(f"{Fore.RED}Opción no válida. Por favor, elige un {Style.BRIGHT}número{Style.RESET_ALL}"
                      f"{Fore.RED} entre 0 y {len(available_enemies)}.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Opción no válida. Por favor, ingresa un {Style.BRIGHT}número{Style.RESET_ALL}{Fore.RED}"
                  f" entre 0 y {len(available_enemies)}.{Style.RESET_ALL}")
