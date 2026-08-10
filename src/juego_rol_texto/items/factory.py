"""Reconstrucción de ítems a partir de datos serializados (JSON de guardado)."""
from juego_rol_texto.items.equipment import Weapon, Armor
from juego_rol_texto.items.materials import Material
from juego_rol_texto.items.potions.buff_potion import StatBuffPotion
from juego_rol_texto.items.potions.healing_potion import HealingPotion
from juego_rol_texto.items.potions.regen_potion import RegenPotion
from juego_rol_texto.ui import console

_ITEM_CLASSES = {
    "HealingPotion": HealingPotion,
    "StatBuffPotion": StatBuffPotion,
    "RegenPotion": RegenPotion,
    "Material": Material,
    "Weapon": Weapon,
    "Armor": Armor
}


def item_factory(data: dict):
    """Crea el objeto correcto basado en el diccionario."""
    if not data or not isinstance(data, dict):
        return None

    tipo = data.get("type")
    if tipo in _ITEM_CLASSES:
        try:
            return _ITEM_CLASSES[tipo].from_dict(data)
        except Exception as e:
            console.error(f"Error al reconstruir {tipo}: {e}")
            return None
    return None
