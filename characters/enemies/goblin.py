import random

from colorama import Fore, Style

from characters.enemies import Enemy
from characters.stats import Stats
from items.equipment import Weapon
from items.potions import HealingPotion


class Goblin(Enemy):
    def __init__(self):
        # health, max_health, min_atk, max_atk, defense
        super().__init__("Goblin", Stats(40, 40, 8, 12, 2), gold_drop=5)
        self.ambush_done = 0  # Añadimos contador de turnos

    def check_ambush(self, player):
        """Intenta realizar un ataque gratuito antes de que empiece la pelea."""
        if not self.ambush_done and random.random() <= 0.4:
            self.ambush_done = True
            damage = self.get_attack_damage() + 5
            final_dmg = player.take_damage(damage)
            print(f"\n¡{Fore.YELLOW}EMBOSCADA!{Style.RESET_ALL} El {self.name} sale de los arbustos y te hace {Fore.RED}{final_dmg}{Style.RESET_ALL} de daño.")
            return True
        return False

    def perform_turn(self, player):
        # El turno normal siempre es el ataque base
        super().perform_turn(player)

    def drop_item(self):
        items = []
        if random.random() <= 0.2:
            items.append(Weapon("Espada Goblin", "Una hoja mellada y cubierta de herrumbre que aún corta", 5, 4))
        if random.random() <= 0.8:
            items.append(HealingPotion("Poción de Salud", "Restaura 20 HP", 2, 20))
        return items