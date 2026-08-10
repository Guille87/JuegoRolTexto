import base64
import json

from juego_rol_texto.characters.player import Player
from juego_rol_texto.characters.stats import Stats
from juego_rol_texto.items.equipment import Armor, Weapon
from juego_rol_texto.items.potions.healing_potion import HealingPotion
from juego_rol_texto.persistence.save_load import load_game, save_game


def _build_player(name="Guille"):
    p = Player(name, Stats(health=80, max_health=100, min_atk=5, max_atk=10, armor=2, magic_resist=1))
    p.level = 3
    p.experience = 15
    p.inventory.gold = 42
    p.inventory.add_item(HealingPotion("Poción de Salud", "desc", 2, 20))
    p.equipped_weapon = Weapon("Espada", "desc", 5, damage=4)
    p.equipped_armor = Armor("Casco", "desc", 8, defense=5)
    return p


def test_save_and_load_round_trip(tmp_save_dir):
    original = _build_player()
    save_game(original, unlocked_enemies=["Goblin", "Esqueleto"], defeated_enemies=["Goblin"])

    loaded_player = Player(original.name, Stats(1, 1, 1, 1, 1))
    result = load_game(loaded_player)

    assert result is not None
    player_name, unlocked, defeated = result
    assert player_name == "Guille"
    assert unlocked == ["Goblin", "Esqueleto"]
    assert defeated == ["Goblin"]

    assert loaded_player.level == 3
    assert loaded_player.experience == 15
    assert loaded_player.stats.health == 80
    assert loaded_player.stats.armor == 2
    assert loaded_player.stats.magic_resist == 1
    assert loaded_player.inventory.gold == 42
    assert loaded_player.inventory.quantities["Poción de Salud"] == 1
    assert loaded_player.equipped_weapon.name == "Espada"
    assert loaded_player.equipped_armor.name == "Casco"


def test_save_creates_backup_of_previous_save(tmp_save_dir):
    player = _build_player()
    save_game(player, unlocked_enemies=["Goblin"], defeated_enemies=[])
    player.inventory.gold = 999
    save_game(player, unlocked_enemies=["Goblin"], defeated_enemies=[])

    backup_path = tmp_save_dir / "Guille.bak"
    assert backup_path.exists()


def test_load_falls_back_to_backup_when_main_save_fails_unexpectedly(tmp_save_dir):
    player = _build_player()
    save_game(player, unlocked_enemies=["Goblin"], defeated_enemies=[])  # 1ra vez: crea .sav (sin .bak aún)
    save_game(player, unlocked_enemies=["Goblin"], defeated_enemies=[])  # 2da vez: crea .bak = copia del .sav válido

    sav_path = tmp_save_dir / "Guille.sav"
    bak_path = tmp_save_dir / "Guille.bak"
    assert bak_path.exists()

    # Un JSON válido pero con forma inesperada (lista en vez de dict) provoca un
    # TypeError al indexar save_data["player_stats"], que es lo único que
    # activa la ruta de fallback al backup en load_game().
    corrupt_payload = base64.b64encode(json.dumps([]).encode("utf-8"))
    sav_path.write_bytes(corrupt_payload)

    loaded_player = Player("Guille", Stats(1, 1, 1, 1, 1))
    result = load_game(loaded_player)

    assert result is not None
    assert loaded_player.inventory.gold == 42


def test_load_returns_none_when_no_save_exists(tmp_save_dir):
    loaded_player = Player("Nadie", Stats(1, 1, 1, 1, 1))
    assert load_game(loaded_player) is None


def test_load_falls_back_on_legacy_defense_key(tmp_save_dir):
    """Partidas guardadas antes de renombrar 'defense' a 'armor' deben poder cargarse igualmente."""
    legacy_save_data = {
        "player_name": "Guille",
        "unlocked_enemies": ["Goblin"],
        "defeated_enemies": [],
        "gold": 10,
        "player_stats": {
            "level": 1,
            "experience": 0,
            "health": 100,
            "max_health": 100,
            "min_atk": 5,
            "max_atk": 10,
            "defense": 2,  # clave antigua, sin "armor" ni "magic_resist"
        },
        "inventory": [],
        "inventory_quantities": {},
        "equipped_weapon": None,
        "equipped_armor": None,
    }
    encoded = base64.b64encode(json.dumps(legacy_save_data).encode("utf-8"))
    (tmp_save_dir / "Guille.sav").write_bytes(encoded)

    loaded_player = Player("Guille", Stats(1, 1, 1, 1, 1))
    result = load_game(loaded_player)

    assert result is not None
    assert loaded_player.stats.armor == 2
    assert loaded_player.stats.magic_resist == 0
