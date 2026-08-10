from juego_rol_texto.combat.battle import ENEMY_PROGRESSION, initiate_battle


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
