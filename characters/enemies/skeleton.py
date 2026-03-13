import random

from colorama import Fore, Style

from characters.enemies import Enemy
from characters.stats import Stats
from items.equipment import Armor
from items.potions import HealingPotion


class Skeleton(Enemy):
    def __init__(self):
        # Los esqueletos tienen buena defensa pero poca vida
        super().__init__("Esqueleto", Stats(60, 60, 10, 15, 5), gold_drop=12)
        self.has_revived = False

    def take_damage(self, amount, defeated_enemies=None):
        # Calculamos el daño normal usando la lógica de la clase padre
        final_damage = super().take_damage(amount)

        # LÓGICA DE REANIMACIÓN
        # Si la vida llega a 0 y aún no ha revivido...
        if self.stats.health <= 0 and not self.has_revived:
            self.has_revived = True
            # Revive con la mitad de su vida máxima
            self.stats.health = self.stats.max_health // 2

            print(f"\n{Fore.WHITE}☠️  ¡Los huesos del Esqueleto se reensamblan mágicamente!{Style.RESET_ALL}")

            # Verificamos si mostramos la vida o no
            # Si defeated_enemies es None o el nombre no está en la lista, ocultamos
            if defeated_enemies and self.name in defeated_enemies:
                print(f"{Fore.CYAN}El Esqueleto ha revivido con {self.stats.health} HP.{Style.RESET_ALL}")
            else:
                print(f"{Fore.BLACK}{Style.BRIGHT}El Esqueleto ha revivido con ??? HP.{Style.RESET_ALL}")
            return final_damage

        return final_damage

    def perform_turn(self, player):
        super().perform_turn(player)

    def drop_item(self):
        items = []
        # 30% de soltar un casco de hueso
        if random.random() <= 0.3:
            items.append(Armor("Casco de Hueso", "Hecho con restos de otros guerreros", 8, 5))
        # 50% de soltar una poción de salud
        if random.random() <= 0.5:
            items.append(HealingPotion("Poción de Salud", "Restaura 20 HP", 2, 20))
        return items