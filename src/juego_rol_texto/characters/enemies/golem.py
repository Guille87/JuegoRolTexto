import random

from juego_rol_texto.characters.enemies.enemy_base import Enemy
from juego_rol_texto.characters.stats import Stats
from juego_rol_texto.items.equipment import Armor, Weapon
from juego_rol_texto.items.materials import Material
from juego_rol_texto.items.potions import HealingPotion
from juego_rol_texto.ui import console


class GolemDePiedra(Enemy):
    def __init__(self):
        # Defensa casi impenetrable: la armadura más alta de todos los enemigos.
        super().__init__(
            "Gólem de Piedra", Stats(450, 450, 42, 54, 20, magic_resist=4, speed=12, precision=8, evasion=0,
                                      crit_chance=0.05, crit_damage=1.6, armor_penetration=12),
            gold_min=90, gold_max=120
        )

    def perform_turn(self, player) -> None:
        # Un turno de cada cinco, de media, provoca un terremoto en vez de golpear:
        # sacude el suelo bajo los pies del jugador, así que no hay forma de esquivarlo.
        if random.random() < 0.2:
            self._earthquake(player)
        else:
            super().perform_turn(player)

    def _earthquake(self, player) -> None:
        print(console.colorize(f"¡{self.name} golpea el suelo con fuerza! La tierra tiembla...", console.Fore.RED))

        damage = self.get_attack_damage()
        final_damage = player.take_damage(damage, armor_penetration=self.stats.armor_penetration)
        print(f"El terremoto hace {console.colorize(str(final_damage), console.Fore.RED)} de daño. "
              f"{console.colorize('(imposible de esquivar)', console.Fore.BLACK, bright=True)}")

    def drop_item(self) -> list:
        items = []
        if random.random() <= 0.5:
            items.append(HealingPotion("Poción de Salud", "Restaura 20 HP", 2, 20))
        if random.random() <= 0.25:
            items.append(Material("Núcleo de Gólem", "Un núcleo de piedra pulida que aún retiene calor.", 30, rarity="Raro"))
        if random.random() <= 0.15:
            items.append(Armor("Coraza de Gólem", "Una plancha de roca maciza tallada para envolver el torso entero.", 55,
                                slot="peto", defense=22, max_health=30))
        if random.random() <= 0.08:
            items.append(Weapon("Mazo de Gólem", "Un fragmento del propio brazo del gólem, todavía duro como la roca.", 30, 20))
        if random.random() <= 0.15:
            items.append(Armor("Cinturón de Roca", "Un anillo de piedra tallada que ancla al portador al suelo.", 30,
                                slot="cinturon", defense=4, max_health=20))
        return items
