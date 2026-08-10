import random

from juego_rol_texto.characters.stats import Stats
from juego_rol_texto.ui import console


class Enemy:
    def __init__(self, name: str, stats: Stats, gold_min: int, gold_max: int):
        self.name = name
        self.stats = stats  # Objeto de la clase Stats
        self.gold_min = gold_min
        self.gold_max = gold_max

    def get_gold_drop(self) -> int:
        return random.randint(self.gold_min, self.gold_max)

    def take_damage(self, damage: int) -> int:
        # Usamos el sistema de armadura de stats
        actual_damage = max(0, damage - self.stats.armor)
        self.stats.health -= actual_damage
        return actual_damage

    def is_alive(self) -> bool:
        return self.stats.health > 0

    def get_attack_damage(self) -> int:
        return random.randint(self.stats.min_atk, self.stats.max_atk)

    def perform_turn(self, player) -> None:
        """Lógica por defecto: atacar. Las subclases pueden sobrescribir esto."""
        damage = self.get_attack_damage()
        final_damage = player.take_damage(damage)
        print(f"{console.colorize(self.name, console.Fore.RED)} ataca y hace "
              f"{console.colorize(str(final_damage), console.Fore.RED)} de daño.")

    def drop_item(self) -> list:
        """Por defecto no sueltan nada, las subclases lo implementan."""
        return []
