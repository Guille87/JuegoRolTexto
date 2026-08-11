from juego_rol_texto.crafting.forge import Forge
from juego_rol_texto.items.materials import Material


def _give_piel_de_troll(player):
    player.inventory.add_item(Material("Piel de Troll", "desc", 150, rarity="Legendario"))


def test_craft_with_materials_and_gold_succeeds(player):
    forge = Forge()
    recipe = forge.recipes[0]
    _give_piel_de_troll(player)
    player.inventory.gold = 200

    assert recipe.can_craft(player) is True
    forge._craft(player, recipe)

    assert player.inventory.gold == 0
    assert "Piel de Troll" not in player.inventory.quantities
    assert "Armadura Regenerativa" in player.inventory.quantities


def test_craft_without_enough_gold_does_nothing(player):
    forge = Forge()
    recipe = forge.recipes[0]
    _give_piel_de_troll(player)
    player.inventory.gold = 199

    assert recipe.can_craft(player) is False
    forge._craft(player, recipe)

    assert player.inventory.gold == 199
    assert player.inventory.quantities["Piel de Troll"] == 1
    assert "Armadura Regenerativa" not in player.inventory.quantities


def test_craft_without_material_does_nothing(player):
    forge = Forge()
    recipe = forge.recipes[0]
    player.inventory.gold = 500  # oro de sobra, pero sin el material

    assert recipe.can_craft(player) is False
    forge._craft(player, recipe)

    assert player.inventory.gold == 500
    assert "Armadura Regenerativa" not in player.inventory.quantities
