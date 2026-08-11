from juego_rol_texto.characters.enemies.bandido import Bandido
from juego_rol_texto.characters.enemies.huargo import Huargo
from juego_rol_texto.combat.battle import ENEMY_PROGRESSION
from juego_rol_texto.items.equipment import Weapon


def test_huargo_pack_bite_adds_bonus_damage_when_triggered(player, monkeypatch):
    # random.random() es un único objeto compartido por todo el proceso (stats.py,
    # enemy_base.py y huargo.py "importan" la misma función), así que no se puede
    # dar un valor distinto según el módulo que llame: usamos una secuencia con
    # el orden real de las tiradas dentro de Huargo.perform_turn() ->
    # [acierto del golpe principal, crítico del golpe principal, ¿hay mordisco de manada?, acierto del mordisco].
    rolls = iter([0.0, 0.99, 0.0, 0.0])
    monkeypatch.setattr("juego_rol_texto.characters.stats.random.random", lambda: next(rolls))
    monkeypatch.setattr("juego_rol_texto.characters.enemies.enemy_base.random.randint", lambda a, b: 10)
    player.stats.armor = 0

    huargo = Huargo()
    before = player.stats.health
    huargo.perform_turn(player)
    dealt = before - player.stats.health

    # Ataque principal sin crítico: 10. Mordisco de manada: 10 // 2 = 5.
    assert dealt == 10 + 5


def test_huargo_pack_bite_never_triggers_when_roll_is_high(player, monkeypatch):
    # Secuencia: [acierto del golpe principal, crítico del golpe principal, ¿mordisco de manada?]
    rolls = iter([0.0, 0.99, 0.99])
    monkeypatch.setattr("juego_rol_texto.characters.stats.random.random", lambda: next(rolls))
    monkeypatch.setattr("juego_rol_texto.characters.enemies.enemy_base.random.randint", lambda a, b: 10)
    player.stats.armor = 0

    huargo = Huargo()
    before = player.stats.health
    huargo.perform_turn(player)
    dealt = before - player.stats.health

    assert dealt == 10


def test_bandido_disarm_zeroes_weapon_bonus_until_it_expires(player, monkeypatch):
    monkeypatch.setattr("juego_rol_texto.characters.enemies.bandido.random.random", lambda: 0.0)  # siempre desarma y acierta
    player.equipped_weapon = Weapon("Espada", "desc", 1, damage=5)

    assert player.get_attack_range() == (10, 15)  # base(5-10) + arma(+5)

    bandido = Bandido()
    bandido.perform_turn(player)

    assert any(e["name"] == "desarmado" for e in player.status_effects)
    assert player.get_attack_range() == (5, 10)  # el bonus del arma no cuenta mientras esté desarmado

    player.on_turn_end()  # duración 2 -> 1
    assert player.get_attack_range() == (5, 10)

    player.on_turn_end()  # duración 1 -> 0, el estado desaparece
    assert not any(e["name"] == "desarmado" for e in player.status_effects)
    assert player.get_attack_range() == (10, 15)


def test_enemy_progression_includes_new_enemies_in_expected_order():
    assert ENEMY_PROGRESSION["Goblin"] == "Huargo"
    assert ENEMY_PROGRESSION["Huargo"] == "Esqueleto"
    assert ENEMY_PROGRESSION["Esqueleto"] == "Bandido"
    assert ENEMY_PROGRESSION["Bandido"] == "Orco"
