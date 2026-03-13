import random

from colorama import Fore, Style

from characters.enemies import Enemy
from characters.stats import Stats
from items.equipment import Weapon
from items.materials import Material
from items.potions import RegenPotion


class Troll(Enemy):
    def __init__(self):
        super().__init__("Troll", Stats(250, 250, 12, 18, 4), gold_drop=50)

    def on_turn_end(self):
        """Habilidad especial: Regeneración Aleatoria"""
        if self.is_alive() and self.stats.health < self.stats.max_health:
            regen = random.randint(5, 15)

            self.stats.health = min(self.stats.max_health, self.stats.health + regen)
            print(f"{Fore.GREEN}✨ El Troll gruñe mientras sus heridas se cierran (+{regen} HP).{Style.RESET_ALL}")

    def drop_item(self):
        items = []
        # 20% Maza de Piedra
        if random.random() <= 0.2:
            items.append(Weapon(
                "Maza de Piedra",
                "Un bloque de granito atado a un tronco. Pesada y brutal.",
                15, 20
            ))

        # 70% Poción de Regeneración
        if random.random() <= 0.7:
            items.append(RegenPotion(
                "Poción de Regeneración",
                "Un brebaje verde que burbujea. Cura 10 HP durante 3 turnos.",
                8, 10, 3
            ))

        if random.random() <= 0.05:
            items.append(Material(
                "Piel de Troll",
                "Una piel gruesa y rugosa que parece pulsar con vida propia. Muy valiosa para un sastre.",
                150,
                rarity="Legendario"
            ))
        return items