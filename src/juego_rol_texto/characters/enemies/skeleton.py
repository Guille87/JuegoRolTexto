import random

from juego_rol_texto.characters.enemies.enemy_base import Enemy
from juego_rol_texto.characters.stats import Stats
from juego_rol_texto.items.equipment import Armor
from juego_rol_texto.items.materials import Material
from juego_rol_texto.items.potions import HealingPotion
from juego_rol_texto.ui import console


class Skeleton(Enemy):
    def __init__(self):
        # Los esqueletos tienen buena defensa pero poca vida
        super().__init__("Esqueleto", Stats(60, 60, 10, 15, 5), gold_min=10, gold_max=14)
        self.has_revived = False

    def take_damage(self, amount: int, defeated_enemies: list | None = None, element: str | None = None) -> int:
        # Calculamos el daño normal usando la lógica de la clase padre
        final_damage = super().take_damage(amount, element=element)

        # LÓGICA DE REANIMACIÓN
        # Si la vida llega a 0 y aún no ha revivido...
        if self.stats.health <= 0 and not self.has_revived:
            self.has_revived = True
            # Revive con la mitad de su vida máxima
            self.stats.health = self.stats.max_health // 2

            print(f"\n{console.colorize('☠️  ¡Los huesos del Esqueleto se reensamblan mágicamente!', console.Fore.WHITE)}")

            # Verificamos si mostramos la vida o no
            # Si defeated_enemies es None o el nombre no está en la lista, ocultamos
            if defeated_enemies and self.name in defeated_enemies:
                console.info(f"El Esqueleto ha revivido con {self.stats.health} HP.")
            else:
                print(console.colorize("El Esqueleto ha revivido con ??? HP.", console.Fore.BLACK, bright=True))
            return final_damage

        return final_damage

    def perform_turn(self, player) -> None:
        super().perform_turn(player)

    def drop_item(self) -> list:
        items = []
        # 18% de soltar un casco de hueso
        if random.random() <= 0.18:
            items.append(Armor("Casco de Hueso", "Hecho con restos de otros guerreros", 8, 5))
        # 50% de soltar una poción de salud
        if random.random() <= 0.5:
            items.append(HealingPotion("Poción de Salud", "Restaura 20 HP", 2, 20))
        # 25% de soltar un fragmento de hueso
        if random.random() <= 0.25:
            items.append(Material("Fragmento de Hueso", "Un resto óseo todavía impregnado de magia residual.", 4, rarity="Común"))
        return items
