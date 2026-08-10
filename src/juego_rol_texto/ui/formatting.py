from juego_rol_texto.ui import console


def print_player_enemy_info(player, enemy, defeated_enemies: list) -> None:
    """Muestra estadísticas detalladas."""
    print(f"\nInformación de {console.colorize(player.name, console.Fore.GREEN)}:")
    print(f"  {console.colorize(f'Nivel: {player.level}', console.Fore.CYAN)}")

    # Usamos las propiedades de la clase Stats que ya manejan los topes
    print(f"  {console.colorize(f'Vida: {player.stats.health}/{player.stats.max_health}', console.Fore.GREEN, bright=True)}")

    # Delegamos el cálculo del ataque y armadura al objeto Player (que ya sabe sumar su equipo)
    atk_min, atk_max = player.get_attack_range()
    print(f"  {console.colorize(f'Ataque: {atk_min}-{atk_max}', console.Fore.RED, bright=True)}")
    print(f"  {console.colorize(f'Armadura: {player.get_total_armor()}', console.Fore.BLUE, bright=True)}")
    print(f"  {console.colorize(f'Resistencia Mágica: {player.stats.magic_resist}', console.Fore.CYAN, bright=True)}")
    print()

    # Lógica de información oculta para enemigos
    if enemy.name in defeated_enemies:
        print(f"Información de {console.colorize(enemy.name, console.Fore.RED)}:")
        print(f"  Vida: {enemy.stats.health}/{enemy.stats.max_health}")
        print(f"  Ataque: {enemy.stats.min_atk}-{enemy.stats.max_atk}")
        print(f"  Armadura: {enemy.stats.armor}")
    else:
        print(
            f"Enemigo {console.colorize(enemy.name, console.Fore.RED)}: "
            f"{console.colorize('??? [Información oculta]', console.Fore.BLACK, bright=True)}")

    print("\n" + "=" * 60)


def print_status(player, enemy, defeated_enemies: list) -> None:
    """Muestra las barras de salud gráficas de forma profesional."""

    # Encapsulamos la lógica de la barra en una función interna para no repetir código (DRY)
    def create_bar(current, maximum, color, hidden=False):
        if hidden:
            return f"|{'?' * 20}| ??/?? HP"

        percent = max(0, min(current / maximum, 1))
        filled_length = int(20 * percent)
        bar = "#" * filled_length + "-" * (20 - filled_length)
        return f"|{console.colorize(bar, color)}| {current}/{maximum} HP"

    max_name = max(len(player.name), len(enemy.name))

    # Barra del Jugador
    player_bar = create_bar(player.stats.health, player.stats.max_health, console.Fore.GREEN)
    print(f"{console.colorize(player.name.ljust(max_name), console.Fore.CYAN)}: {player_bar}")

    # Barra del Enemigo
    is_hidden = enemy.name not in defeated_enemies
    enemy_bar = create_bar(enemy.stats.health, enemy.stats.max_health, console.Fore.RED, is_hidden)
    print(f"{console.colorize(enemy.name.ljust(max_name), console.Fore.LIGHTRED_EX)}: {enemy_bar}")

    print("=" * 60)
