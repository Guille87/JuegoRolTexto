from juego_rol_texto.items.equipment import Armor, Weapon
from juego_rol_texto.items.potions.buff_potion import StatBuffPotion
from juego_rol_texto.items.potions.healing_potion import HealingPotion


def test_add_item_stacks_consumables(player):
    potion = HealingPotion("Poción de Salud", "desc", 2, 20)
    player.inventory.add_item(potion)
    player.inventory.add_item(HealingPotion("Poción de Salud", "desc", 2, 20))

    assert len(player.inventory.items) == 1
    assert player.inventory.quantities["Poción de Salud"] == 2


def test_add_item_auto_sells_duplicate_equipment(player):
    weapon = Weapon("Espada Goblin", "desc", value=5, damage=4)
    player.inventory.add_item(weapon)
    player.inventory.add_item(Weapon("Espada Goblin", "desc", value=5, damage=4))

    assert len(player.inventory.items) == 1
    assert player.inventory.gold == 5


def test_equip_menu_equips_selected_weapon(player, monkeypatch):
    weapon = Weapon("Espada Goblin", "desc", value=5, damage=4)
    player.inventory.add_item(weapon)

    monkeypatch.setattr("juego_rol_texto.inventory.inventory.console.ask", lambda prompt: "1")
    used = player.inventory.equip_menu(Weapon)

    assert used is True
    assert player.equipped_weapon is weapon


def test_equip_menu_rejects_wrong_category(player, monkeypatch):
    player.inventory.add_item(Armor("Casco", "desc", value=8, defense=5))

    monkeypatch.setattr("juego_rol_texto.inventory.inventory.console.ask", lambda prompt: "1")
    used = player.inventory.equip_menu(Weapon)

    assert used is False
    assert player.equipped_weapon is None


def test_using_healing_potion_heals_and_consumes_one(player, monkeypatch):
    player.inventory.add_item(HealingPotion("Poción de Salud", "desc", 2, 20))
    player.stats.health = 50

    monkeypatch.setattr("juego_rol_texto.inventory.inventory.console.ask", lambda prompt: "1")
    used = player.inventory.equip_menu()  # filter_class=None -> inventario general

    assert used is True
    assert player.stats.health == 70
    assert "Poción de Salud" not in player.inventory.quantities
    assert player.inventory.items == []


def test_using_stat_buff_potion_in_combat_consumes_one_from_stack(player, monkeypatch):
    player.in_combat = True
    player.inventory.add_item(StatBuffPotion("Poción de Fuerza", "desc", 5, "max_atk", 5, 3))

    monkeypatch.setattr("juego_rol_texto.inventory.inventory.console.ask", lambda prompt: "1")
    used = player.inventory.equip_menu()

    assert used is True
    assert "Poción de Fuerza" not in player.inventory.quantities
    assert player.inventory.items == []
    assert len(player.active_effects) == 1
