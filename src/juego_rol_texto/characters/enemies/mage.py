import random

from juego_rol_texto.characters.enemies.enemy_base import Enemy
from juego_rol_texto.characters.stats import Stats
from juego_rol_texto.items.equipment import Armor, Weapon
from juego_rol_texto.items.materials import Material
from juego_rol_texto.ui import console


class Mago(Enemy):
    def __init__(self):
        super().__init__(
            "Mago", Stats(400, 400, 10, 15, 6, magic_resist=15, speed=12, precision=12, evasion=10,
                          crit_chance=0.12, crit_damage=1.6, magic_penetration=3),
            gold_min=85, gold_max=115
        )

    def perform_turn(self, player) -> None:
        # 1. Lógica de Curación (Vida <= 50%)
        if self.stats.health <= (self.stats.max_health * 0.5) and random.random() < 0.4:
            self._cast_heal()
            return

        # 2. Lista de estados actuales del jugador
        active_statuses = [e["name"] for e in player.status_effects]

        # 3. Inteligencia Táctica: Intentar aplicar lo que el jugador NO tenga
        posibles_hechizos = []

        if "veneno" not in active_statuses: posibles_hechizos.append("poison")
        if "paralizado" not in active_statuses: posibles_hechizos.append("thunder")
        if "congelado" not in active_statuses and "quemado" not in active_statuses:
            posibles_hechizos.append("blizzard")

        # Si ya tiene los estados importantes o por azar, lanzamos Bola de Fuego (daño puro)
        if not posibles_hechizos or random.random() < 0.3:
            self._cast_fireball(player)
        else:
            choice = random.choice(posibles_hechizos)
            if choice == "thunder":
                self._cast_thunder(player)
            elif choice == "poison":
                self._cast_poison(player)
            elif choice == "blizzard":
                self._cast_blizzard(player)

    def _cast_heal(self) -> None:
        heal = random.randint(40, 60)
        self.stats.health = min(self.stats.max_health, self.stats.health + heal)
        print(f"{console.colorize(self.name, console.Fore.MAGENTA)} susurra palabras antiguas y se cura "
              f"{console.colorize(f'{heal} HP', console.Fore.GREEN)}.")

    def _cast_fireball(self, player) -> None:
        from juego_rol_texto.audio.resource_manager import ResourceManager
        ResourceManager().play_sfx("fireball")

        atk_base = random.randint(self.stats.min_atk, self.stats.max_atk)
        dmg = atk_base + random.randint(15, 25)
        print(f"{console.colorize(self.name, console.Fore.MAGENTA)} lanza una "
              f"{console.colorize('Bola de Fuego', console.Fore.RED)}!")
        player.take_damage(dmg, is_fire=True, is_magical=True, magic_penetration=self.stats.magic_penetration)

        if random.random() < 0.3:
            player.apply_status("quemado", 3)
            console.error("¡Tus ropas arden!")

    def _cast_thunder(self, player) -> None:
        from juego_rol_texto.audio.resource_manager import ResourceManager
        ResourceManager().play_sfx("lightning")

        atk_base = random.randint(self.stats.min_atk, self.stats.max_atk)
        dmg = atk_base + random.randint(10, 30)
        print(f"{console.colorize(self.name, console.Fore.MAGENTA)} invoca un "
              f"{console.colorize('Rayo', console.Fore.YELLOW)} del cielo!")
        player.take_damage(dmg, is_magical=True, magic_penetration=self.stats.magic_penetration)

        if random.random() < 0.3:
            player.apply_status("paralizado", 3)
            console.warning("¡El impacto te deja paralizado!")

    def _cast_poison(self, player) -> None:
        atk_base = random.randint(self.stats.min_atk, self.stats.max_atk)
        dmg = atk_base + random.randint(5, 10)
        print(f"{console.colorize(self.name, console.Fore.MAGENTA)} lanza una "
              f"{console.colorize('Dardo de Veneno', console.Fore.GREEN)}!")
        player.take_damage(dmg, is_magical=True, magic_penetration=self.stats.magic_penetration)

        if random.random() < 0.3:
            player.apply_status("veneno", 3)
            console.success("¡El veneno recorre tus venas!")
        else:
            print("Por suerte, el veneno no logra entrar en tu organismo.")

    def _cast_blizzard(self, player) -> None:
        atk_base = random.randint(self.stats.min_atk, self.stats.max_atk)
        dmg = atk_base + random.randint(5, 15)
        print(f"{console.colorize(self.name, console.Fore.MAGENTA)} conjura una "
              f"{console.colorize('Ventisca', console.Fore.CYAN)} helada!")
        player.take_damage(dmg, is_magical=True, magic_penetration=self.stats.magic_penetration)

        if random.random() < 0.1:
            player.apply_status("congelado", 3)
            print(console.colorize("¡Te has quedado congelado en un bloque de hielo!", console.Fore.CYAN))

    def drop_item(self) -> list:
        items = []
        if random.random() <= 0.15:
            items.append(Weapon("Bastón Arcano", "Un bastón rematado con un cristal que pulsa con energía arcana.", 18, damage=15))
        if random.random() <= 0.12:
            items.append(Armor("Túnica Arcana", "Tejida con hilos imbuidos de magia protectora. La mejor protección conocida.", 22,
                                slot="peto", defense=9, max_health=25))
        if random.random() <= 0.1:
            items.append(Material("Esencia Arcana", "Energía mágica condensada, inestable pero muy valiosa.", 35, rarity="Raro"))
        return items
