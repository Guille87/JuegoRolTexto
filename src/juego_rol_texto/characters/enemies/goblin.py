import random

from juego_rol_texto.characters.enemies.enemy_base import Enemy
from juego_rol_texto.characters.stats import Stats
from juego_rol_texto.items.equipment import Weapon
from juego_rol_texto.items.potions import HealingPotion
from juego_rol_texto.ui import console


class Goblin(Enemy):
    def __init__(self):
        # health, max_health, min_atk, max_atk, defense
        super().__init__("Goblin", Stats(40, 40, 8, 12, 2), gold_drop=5)
        self.ambush_done = 0  # Añadimos contador de turnos

    def check_ambush(self, player) -> bool:
        """Intenta realizar un ataque gratuito antes de que empiece la pelea."""
        if not self.ambush_done and random.random() <= 0.4:
            self.ambush_done = True
            damage = self.get_attack_damage() + 5
            final_dmg = player.take_damage(damage)
            print(f"\n¡{console.colorize('EMBOSCADA!', console.Fore.YELLOW)} El {self.name} sale de los "
                  f"arbustos y te hace {console.colorize(str(final_dmg), console.Fore.RED)} de daño.")
            return True
        return False

    def perform_turn(self, player) -> None:
        # El turno normal siempre es el ataque base
        super().perform_turn(player)

    def drop_item(self) -> list:
        items = []
        if random.random() <= 0.2:
            items.append(Weapon("Espada Goblin", "Una hoja mellada y cubierta de herrumbre que aún corta", 5, 4))
        if random.random() <= 0.8:
            items.append(HealingPotion("Poción de Salud", "Restaura 20 HP", 2, 20))
        return items
