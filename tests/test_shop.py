import pytest

from juego_rol_texto.items.equipment import Weapon
from juego_rol_texto.shop.shop import Shop


def _answers(monkeypatch, *responses):
    """Encola respuestas para console.ask dentro de shop.py."""
    it = iter(responses)
    monkeypatch.setattr("juego_rol_texto.shop.shop.console.ask", lambda prompt: next(it))


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


def test_open_loop_buy_then_back(player, monkeypatch):
    """open(): comprar (1) -> volver del submenú -> salir (3)."""
    shop = Shop()
    player.inventory.gold = 100
    # "1" abre comprar, "1" compra el primer objeto, "3" sale del bucle.
    _answers(monkeypatch, "1", "1", "3")
    shop.open(player)

    assert player.inventory.gold == 100 - shop.catalog[0].buy_price


def test_open_loop_sell_then_back(player, monkeypatch):
    shop = Shop()
    player.inventory.add_item(Weapon("Espada Vieja", "desc", value=7, damage=3))
    _answers(monkeypatch, "2", "1", "3")
    shop.open(player)

    assert player.inventory.gold == 7


def test_open_loop_rejects_invalid_option_then_exits(player, monkeypatch, capsys):
    _answers(monkeypatch, "9", "3")
    Shop().open(player)

    assert "Opción no válida." in capsys.readouterr().out


@pytest.mark.parametrize("choice", ["abc", "999", "0"])
def test_buy_menu_handles_bad_input(player, monkeypatch, choice):
    shop = Shop()
    player.inventory.gold = 100
    monkeypatch.setattr("juego_rol_texto.shop.shop.console.ask", lambda prompt: choice)
    shop._buy_menu(player)

    assert player.inventory.gold == 100  # nada comprado
