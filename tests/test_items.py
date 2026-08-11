import pytest

from juego_rol_texto.items.equipment import Armor, Weapon
from juego_rol_texto.items.factory import item_factory
from juego_rol_texto.items.materials import Material
from juego_rol_texto.items.potions.buff_potion import StatBuffPotion
from juego_rol_texto.items.potions.healing_potion import HealingPotion
from juego_rol_texto.items.potions.regen_potion import RegenPotion

ITEM_SAMPLES = [
    Weapon("Espada", "desc", 5, damage=4),
    Weapon("Espada Flamígera", "desc", 15, damage=10, element="fuego"),
    Armor("Casco", "desc", 8, defense=5),
    Armor("Armadura Regenerativa", "desc", 60, defense=14),
    HealingPotion("Poción de Salud", "desc", 2, heal_amount=20),
    StatBuffPotion("Poción de Fuerza", "desc", 5, stat_name="max_atk", boost=5, duration=3),
    RegenPotion("Poción de Regeneración", "desc", 8, regen_amount=10, duration=3),
    Material("Piel de Troll", "desc", 150, rarity="Legendario"),
]


@pytest.mark.parametrize("item", ITEM_SAMPLES, ids=lambda i: type(i).__name__)
def test_item_round_trips_through_factory(item):
    rebuilt = item_factory(item.to_dict())

    assert type(rebuilt) is type(item)
    assert rebuilt.name == item.name
    assert rebuilt.to_dict() == item.to_dict()


def test_item_factory_returns_none_for_unknown_type():
    assert item_factory({"type": "NoExiste"}) is None


def test_item_factory_returns_none_for_empty_data():
    assert item_factory(None) is None
    assert item_factory({}) is None
