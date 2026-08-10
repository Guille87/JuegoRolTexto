from juego_rol_texto.items.item_base import Item
from juego_rol_texto.ui import console


class Weapon(Item):
    def __init__(self, name: str, description: str, value: int, damage: int):
        super().__init__(name, description, value)
        self.damage = damage

    def use(self, player) -> bool:
        player.equipped_weapon = self
        print(f"Has equipado {self.name}. (+{self.damage} ATK)")
        return True

    def get_stats_info(self) -> str:
        return console.colorize(f"Daño: {self.damage}", console.Fore.RED)

    def to_dict(self) -> dict:
        # Aseguramos que el daño se guarde con la llave correcta
        data = super().to_dict()
        data.update({"damage": self.damage, "type": "Weapon"})
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Weapon":
        return cls(
            name=data["name"],
            description=data["description"],
            value=data["value"],
            damage=data.get("damage", 0)  # Parámetro extra de Weapon
        )


class Armor(Item):
    def __init__(self, name: str, description: str, value: int, defense: int):
        super().__init__(name, description, value)
        self.defense = defense

    def use(self, player) -> bool:
        player.equipped_armor = self
        print(f"Has equipado {self.name}. (+{self.defense} DEF)")
        return True

    def get_stats_info(self) -> str:
        return console.colorize(f"Defensa: {self.defense}", console.Fore.BLUE)

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"defense": self.defense, "type": "Armor"})
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Armor":
        return cls(
            name=data["name"],
            description=data["description"],
            value=data["value"],
            defense=data.get("defense", 0)
        )
