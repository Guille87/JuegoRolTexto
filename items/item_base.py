from abc import ABC, abstractmethod
from colorama import Fore, Style


def item_factory(data):
    """Crea el objeto correcto basado en el diccionario."""
    if not data or not isinstance(data, dict):
        return None

    # IMPORTACIÓN LOCAL (Lazy Import) para evitar el error circular
    from items.equipment import Weapon, Armor
    from items.potions.buff_potion import StatBuffPotion
    from items.potions.healing_potion import HealingPotion
    from items.potions.regen_potion import RegenPotion
    from items.materials import Material

    clases = {
        "HealingPotion": HealingPotion,
        "StatBuffPotion": StatBuffPotion,
        "RegenPotion": RegenPotion,
        "Material": Material,
        "Weapon": Weapon,
        "Armor": Armor
    }

    tipo = data.get("type")
    if tipo in clases:
        try:
            return clases[tipo].from_dict(data)
        except Exception as e:
            print(f"{Fore.RED}Error al reconstruir {tipo}: {e}{Style.RESET_ALL}")
            return None
    return None


class Item(ABC):
    def __init__(self, name, description, value):
        self.name = name
        self.description = description
        self.value = value

    @abstractmethod
    def use(self, target):
        pass

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "name": self.name,
            "description": self.description,
            "value": self.value
        }