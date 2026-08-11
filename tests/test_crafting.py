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


def _find_recipe(forge, name):
    return next(r for r in forge.recipes if r.name == name)


def test_craft_guantes_de_combate_consumes_two_different_materials(player):
    forge = Forge()
    recipe = _find_recipe(forge, "Guantes de Combate")
    player.inventory.add_item(Material("Colmillo de Goblin", "desc", 3, rarity="Común"))
    player.inventory.add_item(Material("Colmillo de Orco", "desc", 6, rarity="Común"))
    player.inventory.gold = 60

    assert recipe.can_craft(player) is True
    forge._craft(player, recipe)

    assert player.inventory.gold == 0
    assert "Colmillo de Goblin" not in player.inventory.quantities
    assert "Colmillo de Orco" not in player.inventory.quantities
    assert player.equipped_armor.get("guantes") is None  # craftear no equipa automáticamente
    assert "Guantes de Combate" in player.inventory.quantities


def test_craft_brazales_arcanos_grants_element_and_magic_resist(player):
    forge = Forge()
    recipe = _find_recipe(forge, "Brazales Arcanos")
    player.inventory.add_item(Material("Esencia Arcana", "desc", 35, rarity="Raro"))
    player.inventory.gold = 80

    forge._craft(player, recipe)
    brazales = next(i for i in player.inventory.items if i.name == "Brazales Arcanos")

    assert brazales.element == "fuego"
    assert brazales.magic_resist == 3


def test_craft_amuleto_de_resistencia(player):
    forge = Forge()
    recipe = _find_recipe(forge, "Amuleto de Resistencia")
    player.inventory.add_item(Material("Esencia Arcana", "desc", 35, rarity="Raro"))
    player.inventory.add_item(Material("Fragmento de Hueso", "desc", 4, rarity="Común"))
    player.inventory.gold = 90

    assert recipe.can_craft(player) is True
    forge._craft(player, recipe)
    amuleto = next(i for i in player.inventory.items if i.name == "Amuleto de Resistencia")

    assert amuleto.slot == "amuleto"
    assert amuleto.magic_resist == 5
    assert amuleto.defense == 2
