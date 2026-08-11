from juego_rol_texto.characters.enemies.goblin import Goblin
from juego_rol_texto.characters.enemies.troll import Troll
from juego_rol_texto.combat.battle import ENEMY_PROGRESSION, _execute_turn, initiate_battle
from juego_rol_texto.items.equipment import Armor, Weapon


def test_victory_unlocks_next_enemy_and_grants_rewards(player, weak_enemy, monkeypatch):
    monkeypatch.setattr("juego_rol_texto.combat.battle.time.sleep", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("juego_rol_texto.combat.battle.console.ask", lambda prompt: "1")

    unlocked = ["Goblin"]
    defeated = []

    initiate_battle(player, weak_enemy, defeated, unlocked)

    assert "Goblin" in defeated
    assert ENEMY_PROGRESSION["Goblin"] in unlocked
    assert weak_enemy.gold_min <= player.inventory.gold <= weak_enemy.gold_max
    assert player.is_alive()


def test_defeat_penalizes_gold_and_fully_heals_player(player, monkeypatch):
    from juego_rol_texto.characters.enemies.orc import Orc

    strong_enemy = Orc()
    strong_enemy.stats.min_atk = strong_enemy.stats.max_atk = 500  # garantiza que mate al jugador en 1 golpe

    player.stats.health = player.stats.max_health
    player.inventory.gold = 90

    monkeypatch.setattr("juego_rol_texto.combat.battle.time.sleep", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("juego_rol_texto.combat.battle.console.ask", lambda prompt: "1")

    unlocked = ["Goblin", "Orco"]
    defeated = ["Goblin"]

    initiate_battle(player, strong_enemy, defeated, unlocked)

    assert player.stats.health == player.stats.max_health
    assert player.inventory.gold == 90 - (90 // 3)


def test_troll_takes_double_damage_from_fire():
    troll = Troll()
    troll.stats.armor = 0
    physical_dmg = troll.take_damage(20)

    another_troll = Troll()
    another_troll.stats.armor = 0
    fire_dmg = another_troll.take_damage(20, element="fuego")

    assert fire_dmg == physical_dmg * 2


def test_goblin_is_not_affected_by_fire_element():
    goblin = Goblin()
    goblin.stats.armor = 0
    normal_dmg = goblin.take_damage(10)

    another_goblin = Goblin()
    another_goblin.stats.armor = 0
    fire_dmg = another_goblin.take_damage(10, element="fuego")

    assert fire_dmg == normal_dmg


def test_execute_turn_applies_elemental_bonus_against_weak_enemy(player, monkeypatch):
    monkeypatch.setattr("juego_rol_texto.characters.player.random.randint", lambda a, b: 10)
    monkeypatch.setattr("juego_rol_texto.combat.battle.random.choice", lambda seq: "hit")

    player.equipped_weapon = Weapon("Espada Flamígera", "desc", 15, damage=0, element="fuego")

    troll = Troll()
    troll.stats.armor = 0
    troll.stats.health = troll.stats.max_health = 1000

    before = troll.stats.health
    _execute_turn(player, troll, defeated_enemies=[])
    dealt = before - troll.stats.health

    assert dealt == 20  # 10 base * 2.0 (débil al fuego) - 0 armadura


def test_execute_turn_applies_crit_multiplier(player, monkeypatch):
    monkeypatch.setattr("juego_rol_texto.characters.player.random.randint", lambda a, b: 10)
    monkeypatch.setattr("juego_rol_texto.combat.battle.random.choice", lambda seq: "hit")
    monkeypatch.setattr("juego_rol_texto.combat.battle.random.random", lambda: 0.0)  # siempre crítico

    player.equipped_armor["guantes"] = Armor("Guantes", "desc", 1, slot="guantes", crit_chance=1.0)
    player.stats.armor = 0

    goblin = Goblin()
    goblin.stats.armor = 0
    goblin.stats.health = goblin.stats.max_health = 1000

    before = goblin.stats.health
    _execute_turn(player, goblin, defeated_enemies=[])
    dealt = before - goblin.stats.health

    assert dealt == int(10 * player.stats.crit_damage)  # 10 base * 1.5 (multiplicador base)


def test_execute_turn_uses_element_from_bracers_when_no_elemental_weapon(player, monkeypatch):
    monkeypatch.setattr("juego_rol_texto.characters.player.random.randint", lambda a, b: 10)
    monkeypatch.setattr("juego_rol_texto.combat.battle.random.choice", lambda seq: "hit")

    player.equipped_weapon = Weapon("Espada de Hierro", "desc", 10, damage=0)  # sin elemento
    player.equipped_armor["brazales"] = Armor("Brazales Arcanos", "desc", 1, slot="brazales", element="fuego")
    player.stats.armor = 0

    troll = Troll()
    troll.stats.armor = 0
    troll.stats.health = troll.stats.max_health = 1000

    before = troll.stats.health
    _execute_turn(player, troll, defeated_enemies=[])
    dealt = before - troll.stats.health

    assert dealt == 20  # 10 base * 2.0 (débil al fuego, heredado de los brazales)
