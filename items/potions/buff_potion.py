from colorama import Fore, Style

from items.potions import Potion


class StatBuffPotion(Potion):
    def __init__(self, name, description, value, stat_name, boost, duration):
        super().__init__(name, description, value, duration)
        self.stat_name = stat_name  # e.g., "defense" o "min_atk"
        self.boost = boost
        self.is_combat_only = True

    def use(self, player):
        if getattr(player, 'in_combat', False):
            # Sumamos +1 a la duración para compensar el turno actual de uso
            # Así, si la poción es de 3 turnos, el jugador atacará 3 veces con el buff.
            self.duration += 1

            # El ítem se encarga de añadirse a la lista de efectos del jugador
            player.active_effects.append(self)

            # Aplicamos el efecto inicial
            current_val = getattr(player.stats, self.stat_name)
            setattr(player.stats, self.stat_name, current_val + self.boost)

            print(f"{Fore.CYAN}¡Efecto {self.name} activado! (+{self.boost} {self.stat_name} por {self.duration} turnos){Style.RESET_ALL}")
            return True

        print(f"{Fore.RED}No puedes usar este objeto fuera del combate.{Style.RESET_ALL}")
        return False

    def remove(self, player):
        current_val = getattr(player.stats, self.stat_name)
        setattr(player.stats, self.stat_name, current_val - self.boost)
        print(f"El efecto de {self.name} ha terminado.")

    def to_dict(self):
        data = super().to_dict()
        data.update({"stat_name": self.stat_name, "boost": self.boost})
        return data

    def get_stats_info(self):
        return f"{Fore.CYAN}+{self.boost} {self.stat_name} ({self.duration} turnos){Style.RESET_ALL}"

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["description"], data["value"],
                   data["stat_name"], data["boost"], data["duration"])