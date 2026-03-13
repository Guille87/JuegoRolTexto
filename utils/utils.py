from colorama import Fore, Style


def print_player_enemy_info(player, enemy, defeated_enemies):
    """Muestra estadísticas detalladas."""
    print(f"\nInformación de {Fore.GREEN}{player.name}{Style.RESET_ALL}:")
    print(f"  {Fore.CYAN}Nivel: {player.level}{Style.RESET_ALL}")

    # Usamos las propiedades de la clase Stats que ya manejan los topes
    print(f"  {Fore.GREEN}{Style.BRIGHT}Vida: {player.stats.health}/{player.stats.max_health}{Style.RESET_ALL}")

    # Delegamos el cálculo del ataque y defensa al objeto Player (que ya sabe sumar su equipo)
    # Asumiendo que añadimos métodos get_total_attack_range() y get_total_defense() en Player
    atk_min, atk_max = player.get_attack_range()
    print(f"  {Fore.RED}{Style.BRIGHT}Ataque: {atk_min}-{atk_max}{Style.RESET_ALL}")
    print(f"  {Fore.BLUE}{Style.BRIGHT}Defensa: {player.get_total_defense()}{Style.RESET_ALL}")
    print()

    # Lógica de información oculta para enemigos
    if enemy.name in defeated_enemies:
        print(f"Información de {Fore.RED}{enemy.name}{Style.RESET_ALL}:")
        print(f"  Vida: {enemy.stats.health}/{enemy.stats.max_health}")
        print(f"  Ataque: {enemy.stats.min_atk}-{enemy.stats.max_atk}")
        print(f"  Defensa: {enemy.stats.defense}")
    else:
        print(
            f"Enemigo {Fore.RED}{enemy.name}{Style.RESET_ALL}: {Fore.BLACK}{Style.BRIGHT}??? [Información oculta]{Style.RESET_ALL}")

    print("\n" + "=" * 60)


def print_status(player, enemy, defeated_enemies):
    """Muestra las barras de salud gráficas de forma profesional."""

    # Encapsulamos la lógica de la barra en una función interna para no repetir código (DRY)
    def create_bar(current, maximum, color, hidden=False):
        if hidden:
            return f"|{'?' * 20}| ??/?? HP"

        percent = max(0, min(current / maximum, 1))
        filled_length = int(20 * percent)
        bar = "#" * filled_length + "-" * (20 - filled_length)
        return f"|{color}{bar}{Style.RESET_ALL}| {current}/{maximum} HP"

    max_name = max(len(player.name), len(enemy.name))

    # Barra del Jugador
    player_bar = create_bar(player.stats.health, player.stats.max_health, Fore.GREEN)
    print(f"{Fore.CYAN}{player.name.ljust(max_name)}{Style.RESET_ALL}: {player_bar}")

    # Barra del Enemigo
    is_hidden = enemy.name not in defeated_enemies
    enemy_bar = create_bar(enemy.stats.health, enemy.stats.max_health, Fore.RED, is_hidden)
    print(f"{Fore.LIGHTRED_EX}{enemy.name.ljust(max_name)}{Style.RESET_ALL}: {enemy_bar}")

    print("=" * 60)
