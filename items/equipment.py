from colorama import Fore, Style

from items.item_base import Item


class Weapon(Item):
    def __init__(self, name, description, value, damage):
        super().__init__(name, description, value)
        self.damage = damage

    def use(self, player):
        player.equipped_weapon = self
        print(f"Has equipado {self.name}. (+{self.damage} ATK)")

    def get_stats_info(self):
        return f"{Fore.RED}Daño: {self.damage}{Style.RESET_ALL}"

    def to_dict(self):
        # Aseguramos que el daño se guarde con la llave correcta
        data = super().to_dict()
        data.update({"damage": self.damage, "type": "Weapon"})
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            description=data["description"],
            value=data["value"],
            damage=data.get("damage", 0)  # Parámetro extra de Weapon
        )


class Armor(Item):
    def __init__(self, name, description, value, defense):
        super().__init__(name, description, value)
        self.defense = defense

    def use(self, player):
        player.equipped_armor = self
        print(f"Has equipado {self.name}. (+{self.defense} DEF)")

    def get_stats_info(self):
        return f"{Fore.BLUE}Defensa: {self.defense}{Style.RESET_ALL}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"defense": self.defense, "type": "Armor"})
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            description=data["description"],
            value=data["value"],
            defense=data.get("defense", 0)
        )