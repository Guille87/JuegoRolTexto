import random

from juego_rol_texto.characters.enemies.enemy_base import Enemy
from juego_rol_texto.characters.stats import Stats
from juego_rol_texto.items.equipment import Armor, Weapon
from juego_rol_texto.items.materials import Material
from juego_rol_texto.items.potions import RegenPotion
from juego_rol_texto.ui import console


class Troll(Enemy):
    ELEMENTAL_WEAKNESSES = {"fuego": 2.0}

    def __init__(self):
        super().__init__(
            "Troll", Stats(250, 250, 12, 18, 4, magic_resist=1, speed=10, precision=3, evasion=0,
                           crit_chance=0.03, crit_damage=1.5, regen=10),
            gold_min=42, gold_max=58
        )

    def on_turn_end(self) -> None:
        """Habilidad especial: regeneración aleatoria alrededor de su stat de
        regeneración (el Troll es de los pocos enemigos "aptos" para esto)."""
        if self.is_alive() and self.stats.health < self.stats.max_health:
            regen = random.randint(self.stats.regen - 5, self.stats.regen + 5)

            self.stats.health = min(self.stats.max_health, self.stats.health + regen)
            console.success(f"✨ El Troll gruñe mientras sus heridas se cierran (+{regen} HP).")

    def drop_item(self) -> list:
        items = []
        # 12% Maza de Piedra (la mejor arma actual, drop más bajo a propósito)
        if random.random() <= 0.12:
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

        if random.random() <= 0.15:
            items.append(Armor(
                "Hombreras de Troll",
                "Placas de hueso trolluno unidas a la piel; se regeneran casi tan rápido como su dueño original.",
                25, slot="hombreras", defense=3, regen=2
            ))
        return items
