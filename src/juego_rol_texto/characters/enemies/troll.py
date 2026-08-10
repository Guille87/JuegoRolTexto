import random

from juego_rol_texto.characters.enemies.enemy_base import Enemy
from juego_rol_texto.characters.stats import Stats
from juego_rol_texto.items.equipment import Weapon
from juego_rol_texto.items.materials import Material
from juego_rol_texto.items.potions import RegenPotion
from juego_rol_texto.ui import console


class Troll(Enemy):
    def __init__(self):
        super().__init__("Troll", Stats(250, 250, 12, 18, 4), gold_drop=50)

    def on_turn_end(self) -> None:
        """Habilidad especial: Regeneración Aleatoria"""
        if self.is_alive() and self.stats.health < self.stats.max_health:
            regen = random.randint(5, 15)

            self.stats.health = min(self.stats.max_health, self.stats.health + regen)
            console.success(f"✨ El Troll gruñe mientras sus heridas se cierran (+{regen} HP).")

    def drop_item(self) -> list:
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
