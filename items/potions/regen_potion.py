from colorama import Fore, Style

from items.potions import Potion


class RegenPotion(Potion):
    def __init__(self, name, description, value, regen_amount, duration):
        super().__init__(name, description, value, duration)
        self.regen_amount = regen_amount
        self.is_combat_only = True

    def use(self, player):
        if getattr(player, 'in_combat', False):
            # Usamos el método apply_status que ya tienes en Player
            player.apply_status("regeneración", self.duration, power=self.regen_amount)
            print(f"{Fore.GREEN}¡Te sientes revitalizado! Recuperarás vida cada turno.{Style.RESET_ALL}")
            return True

        print(f"{Fore.RED}Esta poción solo surte efecto durante el fragor de la batalla.{Style.RESET_ALL}")
        return False

    def get_stats_info(self):
        return f"{Fore.GREEN}Regen: {self.regen_amount} HP/turno ({self.duration} turnos){Style.RESET_ALL}"

    def to_dict(self):
        data = super().to_dict()
        data["regen_amount"] = self.regen_amount
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["description"], data["value"],
                   data["regen_amount"], data["duration"])