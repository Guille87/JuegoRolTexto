from colorama import Fore, Style

from items.potions import Potion


class HealingPotion(Potion):
    def __init__(self, name, description, value, heal_amount):
        super().__init__(name, description, value, duration=0)
        self.heal_amount = heal_amount

    def use(self, player):
        player.stats.health += self.heal_amount
        print(f"Te has curado {self.heal_amount} HP.")

    def to_dict(self):
        data = super().to_dict()
        data["heal_amount"] = self.heal_amount
        return data

    def get_stats_info(self):
        return f"{Fore.GREEN}Cura: {self.heal_amount} HP{Style.RESET_ALL}"

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["description"], data["value"], data["heal_amount"])