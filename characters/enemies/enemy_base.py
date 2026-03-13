import random

from colorama import Fore, Style


class Enemy:
    def __init__(self, name, stats, gold_drop):
        self.name = name
        self.stats = stats  # Objeto de la clase Stats
        self.gold_drop = gold_drop

    def take_damage(self, damage):
        # Usamos el sistema de defensa de stats
        actual_damage = max(0, damage - self.stats.defense)
        self.stats.health -= actual_damage
        return actual_damage

    def is_alive(self):
        return self.stats.health > 0

    def get_attack_damage(self):
        return random.randint(self.stats.min_atk, self.stats.max_atk)

    def perform_turn(self, player):
        """Lógica por defecto: atacar. Las subclases pueden sobrescribir esto."""
        damage = self.get_attack_damage()
        final_damage = player.take_damage(damage)
        print(f"{Fore.RED}{self.name}{Style.RESET_ALL} ataca y hace {Fore.RED}{final_damage}{Style.RESET_ALL} de daño.")

    def drop_item(self):
        """Por defecto no sueltan nada, las subclases lo implementan."""
        return []
