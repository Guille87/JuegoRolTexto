import random

from colorama import Fore, Style

from characters.enemies import Enemy
from characters.stats import Stats


class Mago(Enemy):
    def __init__(self):
        super().__init__("Mago", Stats(400, 400, 10, 15, 6), gold_drop=100)

    def perform_turn(self, player):
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

    def _cast_heal(self):
        heal = random.randint(40, 60)
        self.stats.health = min(self.stats.max_health, self.stats.health + heal)
        print(
            f"{Fore.MAGENTA}{self.name}{Style.RESET_ALL} susurra palabras antiguas y se cura {Fore.GREEN}{heal} HP{Style.RESET_ALL}.")

    def _cast_fireball(self, player):
        from assets.resources.resource_manager import ResourceManager
        ResourceManager().play_sfx("fireball")

        atk_base = random.randint(self.stats.min_atk, self.stats.max_atk)
        dmg = atk_base + random.randint(15, 25)
        print(f"{Fore.MAGENTA}{self.name}{Style.RESET_ALL} lanza una {Fore.RED}Bola de Fuego{Style.RESET_ALL}!")
        player.take_damage(dmg, is_fire=True)

        if random.random() < 0.3:
            player.apply_status("quemado", 3)
            print(f"{Fore.RED}¡Tus ropas arden!{Style.RESET_ALL}")

    def _cast_thunder(self, player):
        from assets.resources.resource_manager import ResourceManager
        ResourceManager().play_sfx("lightning")

        atk_base = random.randint(self.stats.min_atk, self.stats.max_atk)
        dmg = atk_base +  random.randint(10, 30)
        print(f"{Fore.MAGENTA}{self.name}{Style.RESET_ALL} invoca un {Fore.YELLOW}Rayo{Style.RESET_ALL} del cielo!")
        player.take_damage(dmg)

        if random.random() < 0.3:
            player.apply_status("paralizado", 3)
            print(f"{Fore.YELLOW}¡El impacto te deja paralizado!{Style.RESET_ALL}")

    def _cast_poison(self, player):
        atk_base = random.randint(self.stats.min_atk, self.stats.max_atk)
        dmg = atk_base + random.randint(5, 10)
        print(f"{Fore.MAGENTA}{self.name}{Style.RESET_ALL} lanza una {Fore.GREEN}Dardo de Veneno{Style.RESET_ALL}!")
        player.take_damage(dmg)

        if random.random() < 0.3:
            player.apply_status("veneno", 3)
            print(f"{Fore.GREEN}¡El veneno recorre tus venas!{Style.RESET_ALL}")
        else:
            print(f"Por suerte, el veneno no logra entrar en tu organismo.")

    def _cast_blizzard(self, player):
        atk_base = random.randint(self.stats.min_atk, self.stats.max_atk)
        dmg = atk_base + random.randint(5, 15)
        print(f"{Fore.MAGENTA}{self.name}{Style.RESET_ALL} conjura una {Fore.CYAN}Ventisca{Style.RESET_ALL} helada!")
        player.take_damage(dmg)

        if random.random() < 0.1:
            player.apply_status("congelado", 3)
            print(f"{Fore.CYAN}¡Te has quedado congelado en un bloque de hielo!{Style.RESET_ALL}")