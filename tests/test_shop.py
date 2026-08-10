from juego_rol_texto.items.equipment import Weapon
from juego_rol_texto.shop.shop import Shop


def test_buy_with_enough_gold_deducts_price_and_adds_item(player, monkeypatch):
    shop = Shop()
    player.inventory.gold = 100

    monkeypatch.setattr("juego_rol_texto.shop.shop.console.ask", lambda prompt: "1")
    shop._buy_menu(player)

    bought = shop.catalog[0]
    assert player.inventory.gold == 100 - bought.buy_price
    assert bought.template.name in player.inventory.quantities


def test_buy_without_enough_gold_does_nothing(player, monkeypatch):
    shop = Shop()
    player.inventory.gold = 0

    monkeypatch.setattr("juego_rol_texto.shop.shop.console.ask", lambda prompt: "1")
    shop._buy_menu(player)

    assert player.inventory.gold == 0
    assert player.inventory.items == []


def test_sell_item_from_inventory_grants_gold_and_removes_it(player, monkeypatch):
    shop = Shop()
    weapon = Weapon("Espada Vieja", "desc", value=7, damage=3)
    player.inventory.add_item(weapon)

    monkeypatch.setattr("juego_rol_texto.shop.shop.console.ask", lambda prompt: "1")
    shop._sell_menu(player)

    assert player.inventory.gold == 7
    assert weapon not in player.inventory.items


def test_cannot_sell_equipped_item(player, monkeypatch):
    shop = Shop()
    weapon = Weapon("Espada Equipada", "desc", value=7, damage=3)
    player.inventory.add_item(weapon)
    player.equipped_weapon = weapon

    monkeypatch.setattr("juego_rol_texto.shop.shop.console.ask", lambda prompt: "1")
    shop._sell_menu(player)

    assert player.inventory.gold == 0
    assert weapon in player.inventory.items
