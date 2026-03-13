import random

from colorama import Fore, Style

from characters.enemies import Enemy
from characters.stats import Stats
from items.equipment import Weapon
from items.potions import StatBuffPotion


class Orc(Enemy):
    def __init__(self):
        super().__init__("Orco", Stats(150, 150, 15, 20, 6), gold_drop=25)
        self.fury_active = False
        self.total_turns = 0  # Contador de turnos transcurridos

    def perform_turn(self, player):
        # Lógica de Furia simplificada
        if self.fury_active:
            print(f"{Fore.RED}¡El Orco está enfurecido!{Style.RESET_ALL}")

            # 1. Obtenemos el daño aleatorio del Orco
            base_damage = self.get_attack_damage()

            # 2. Calculamos cuánto daño pasaría la defensa del jugador
            # (Ataque - Defensa, mínimo 0 para no curar al jugador)
            damage_after_def = max(0, base_damage - player.stats.defense)

            # 3. Multiplicamos el resultado por 2
            final_dmg = damage_after_def * 2

            # 4. Aplicamos el daño directamente a la salud del jugador
            player.stats.health -= final_dmg

            print(f"{Fore.RED}{self.name}{Style.RESET_ALL} lanza un golpe devastador y hace {Fore.RED}{final_dmg}{Style.RESET_ALL} de daño.")
        else:
            super().perform_turn(player)

    def on_turn_end(self):
        """Gestiona el ciclo de 3 turnos calma / 3 turnos furia."""
        self.total_turns += 1

        # Lógica de ciclo (usando el turno actual):
        # Turnos 1, 2, 3 -> Calma
        # Turnos 4, 5, 6 -> Furia
        # Turnos 7, 8, 9 -> Calma...

        # Determinamos en qué fase estamos:
        # (self.total_turns - 1) // 3 nos da 0 para (1,2,3), 1 para (4,5,6), 2 para (7,8,9)...
        fase_furia = (self.total_turns // 3) % 2 == 1

        # Lógica de ACTIVACIÓN: Después del tercer turno (al final del turno 3)
        if fase_furia and not self.fury_active:
            self.fury_active = True
            print(f"\n{Fore.RED}😡 ¡El Orco se ha enfurecido! Sus ojos brillan en rojo...{Style.RESET_ALL}")

        # Lógica de DESACTIVACIÓN: Si está en furia, reducir duración
        elif not fase_furia and self.fury_active:
            self.fury_active = False
            print(f"\n{Fore.YELLOW}😴 El Orco parece haberse cansado y recupera la calma.{Style.RESET_ALL}")

    def drop_item(self):
        items = []
        if random.random() <= 0.2:
            items.append(Weapon("Hacha de Batalla", "Un arma colosal de doble filo, manchada por mil batallas", 15, 12))
        if random.random() <= 0.6:
            # Usamos StatBuffPotion para la fuerza
            items.append(StatBuffPotion("Poción de Fuerza", "Aumenta el ataque temporalmente", 5, "max_atk", 5, 3))
        return items