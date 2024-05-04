from colorama import Fore, Style


def print_player_enemy_info(player, enemy, defeated_enemies):
    print(f"Información del jugador {Fore.GREEN}{player.name}{Style.RESET_ALL}:")
    print(f"  {Fore.CYAN}Nivel: {player.level}{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}{Style.BRIGHT}Vida: {player.health}{Style.RESET_ALL}")
    # Si el jugador tiene un arma equipada, muestra el daño del arma y actualiza el rango de ataque
    if player.equipped_weapon:
        player_min_attack_with_weapon = player.min_attack + player.equipped_weapon.damage
        player_max_attack_with_weapon = player.max_attack + player.equipped_weapon.damage
        print(f"  {Fore.RED}{Style.BRIGHT}Ataque: {player_min_attack_with_weapon}-{player_max_attack_with_weapon}{Style.RESET_ALL}")
    else:
        print(f"  {Fore.RED}{Style.BRIGHT}Ataque: {player.min_attack}-{player.max_attack}{Style.RESET_ALL}")
    if player.equipped_armor:
        player_defense_with_armor = player.defense + player.equipped_armor.defense
        print(f"  {Fore.BLUE}{Style.BRIGHT}Defensa: {player_defense_with_armor}{Style.RESET_ALL}")
    else:
        print(f"  {Fore.BLUE}{Style.BRIGHT}Defensa: {player.defense}{Style.RESET_ALL}")
    print()

    if enemy.name in defeated_enemies:
        print(f"Información del enemigo {Fore.RED}{enemy.name}{Style.RESET_ALL}:")
        print(f"  Vida: {enemy.health}")
        print(f"  Ataque: {enemy.min_attack}-{enemy.max_attack}")
        print(f"  Defensa: {enemy.defense}")
    else:
        print(f"Enemigo {Fore.RED}{enemy.name}{Style.RESET_ALL} no derrotado. Información oculta.")
    print()
    print("============================================================")


def print_status(player, enemy, defeated_enemies):
    # Calcula la longitud máxima de los nombres de jugador y enemigo
    max_name_length = max(len(player.name), len(enemy.name))

    # Calcula el porcentaje de salud del jugador y del enemigo
    player_health_percentage = player.health / player.max_health
    enemy_health_percentage = enemy.health / enemy.max_health

    # Convierte el porcentaje de salud en una barra horizontal
    player_health_bar = "|" + "#" * int(player_health_percentage * 20) + "-" * (
            20 - int(player_health_percentage * 20)) + "|"

    # Alinea los nombres del jugador y del enemigo
    aligned_player_name = player.name.ljust(max_name_length)
    aligned_enemy_name = enemy.name.ljust(max_name_length)

    # Imprime la salud del jugador y del enemigo con barras de salud gráficas
    print(
        f"{Fore.CYAN}{aligned_player_name}: {player_health_bar} {player.health}/{player.max_health} HP{Style.RESET_ALL}")
    if enemy.name in defeated_enemies:
        enemy_health_bar = "|" + "#" * int(enemy_health_percentage * 20) + "-" * (
                20 - int(enemy_health_percentage * 20)) + "|"
        print(
            f"{Fore.LIGHTRED_EX}{aligned_enemy_name}: {enemy_health_bar} {enemy.health}/{enemy.max_health} HP{Style.RESET_ALL}")
    else:
        print(f"{Fore.LIGHTRED_EX}{aligned_enemy_name}: |????????????????????| ??/?? HP{Style.RESET_ALL}")
    print("============================================================")
