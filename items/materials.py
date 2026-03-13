from colorama import Fore, Style

from items.item_base import Item


class Material(Item):
    def __init__(self, name, description, value, rarity="Común"):
        super().__init__(name, description, value)
        self.rarity = rarity

    def use(self, player):
        print(f"{Fore.YELLOW}Este objeto es un material de artesanía. No puedes usarlo directamente.{Style.RESET_ALL}")
        return False

    def to_dict(self):
        data = super().to_dict()
        data["rarity"] = self.rarity
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["description"], data["value"], data.get("rarity", "Común"))