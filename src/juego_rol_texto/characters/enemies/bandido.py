import random

from juego_rol_texto.characters.enemies.enemy_base import Enemy
from juego_rol_texto.characters.stats import Stats, resolve_hit
from juego_rol_texto.items.equipment import Armor, Weapon
from juego_rol_texto.items.materials import Material
from juego_rol_texto.items.potions import HealingPotion
from juego_rol_texto.ui import console


class Bandido(Enemy):
    def __init__(self):
        super().__init__(
            "Bandido", Stats(85, 85, 13, 19, 5, speed=12, precision=10, evasion=6,
                             crit_chance=0.10, crit_damage=1.6, armor_penetration=2),
            gold_min=16, gold_max=22
        )
        self.ambush_done = False

    def check_ambush(self, player) -> bool:
        """Ataque sorpresa desde las sombras, igual que la emboscada del Goblin."""
        if not self.ambush_done and random.random() <= 0.35:
            self.ambush_done = True
            damage = self.get_attack_damage() + 4
            final_dmg = player.take_damage(damage, armor_penetration=self.stats.armor_penetration)
            print(f"\n¡{console.colorize('EMBOSCADA!', console.Fore.YELLOW)} El {self.name} te ataca desde las "
                  f"sombras y te hace {console.colorize(str(final_dmg), console.Fore.RED)} de daño.")
            return True
        return False

    def perform_turn(self, player) -> None:
        # Un turno de cada cuatro, de media, intenta desarmar en vez de atacar.
        if random.random() < 0.25:
            self._attempt_disarm(player)
        else:
            super().perform_turn(player)

    def _attempt_disarm(self, player) -> None:
        """Desarme temporal: anula el bonus de daño del arma equipada durante 2 turnos."""
        if not resolve_hit(self.stats.precision, player.get_total_evasion()):
            print(f"{console.colorize(self.name, console.Fore.RED)} intenta desarmar a "
                  f"{console.colorize(player.name, console.Fore.GREEN)}, pero falla.")
            return

        player.apply_status("desarmado", 2)
        print(f"{console.colorize(self.name, console.Fore.RED)} te arranca el arma de las manos. "
              f"{console.colorize('¡Desarmado durante 2 turnos!', console.Fore.YELLOW)}")

    def drop_item(self) -> list:
        items = []
        if random.random() <= 0.6:
            items.append(HealingPotion("Poción de Salud", "Restaura 20 HP", 2, 20))
        if random.random() <= 0.25:
            items.append(Material("Capa de Sombras", "Tela oscura que parece absorber la luz.", 8, rarity="Común"))
        if random.random() <= 0.15:
            items.append(Weapon("Daga Robada", "Ligera y afilada, perfecta para golpear rápido y desaparecer.", 12, 6))
        if random.random() <= 0.15:
            items.append(Armor("Guantes de Ladrón", "Sin apenas grosor; perfectos para no perder el tacto al robar.", 18,
                                slot="guantes", crit_chance=0.04))
        return items
