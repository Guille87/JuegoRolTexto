from juego_rol_texto.characters.player import Player
from juego_rol_texto.characters.stats import Stats
from juego_rol_texto.items.equipment import Armor, Weapon


def test_take_damage_subtracts_total_armor(player):
    dealt = player.take_damage(10)
    assert dealt == 8  # 10 - armor(2)
    assert player.stats.health == 92


def test_take_damage_magical_uses_magic_resist_instead_of_armor(player):
    player.stats.armor = 100  # no debería influir en absoluto en daño mágico
    player.stats.magic_resist = 3

    dealt = player.take_damage(10, is_magical=True)

    assert dealt == 7  # 10 - magic_resist(3), ignora los 100 de armadura
    assert player.stats.health == 93


def test_take_damage_never_negative(player):
    dealt = player.take_damage(1)
    assert dealt == 0
    assert player.stats.health == 100


def test_get_attack_range_includes_weapon_bonus(player):
    player.equipped_weapon = Weapon("Espada", "desc", 1, damage=3)
    assert player.get_attack_range() == (8, 13)


def test_get_attack_range_halved_when_quemado(player):
    player.equipped_weapon = Weapon("Espada", "desc", 1, damage=3)
    player.apply_status("quemado", duration=2)
    assert player.get_attack_range() == (4, 6)


def test_get_total_armor_includes_equipped_armor_bonus(player):
    player.equipped_armor = Armor("Escudo", "desc", 1, defense=5)
    assert player.get_total_armor() == 7


def test_gain_experience_levels_up_and_boosts_stats(player):
    old_max_health, old_min_atk, old_max_atk, old_armor = (
        player.stats.max_health, player.stats.min_atk, player.stats.max_atk, player.stats.armor
    )
    player.gain_experience(40)  # required_xp() en nivel 1 es 40

    assert player.level == 2
    assert player.stats.max_health == old_max_health + 20
    assert player.stats.health == player.stats.max_health
    assert player.stats.min_atk == old_min_atk + 2
    assert player.stats.max_atk == old_max_atk + 3
    assert player.stats.armor == old_armor + 1
    assert player.stats.magic_resist == 1  # nivel 2 es par -> gana resistencia mágica


def test_gain_experience_can_trigger_multiple_level_ups():
    player = Player("Heroe", Stats(health=100, max_health=100, min_atk=5, max_atk=10, armor=2))
    player.gain_experience(1000)
    assert player.level > 2


def test_level_up_grants_magic_resist_only_on_even_levels(player):
    assert player.stats.magic_resist == 0

    player._level_up()  # nivel 1 -> 2 (par)
    assert player.stats.magic_resist == 1

    player._level_up()  # nivel 2 -> 3 (impar)
    assert player.stats.magic_resist == 1

    player._level_up()  # nivel 3 -> 4 (par)
    assert player.stats.magic_resist == 2


def test_apply_status_refreshes_duration_instead_of_duplicating(player):
    player.apply_status("veneno", duration=2)
    player.apply_status("veneno", duration=5)
    assert len(player.status_effects) == 1
    assert player.status_effects[0]["duration"] == 5


def test_on_turn_start_applies_poison_damage(player):
    player.apply_status("veneno", duration=3)
    can_act = player.on_turn_start()
    assert can_act is True
    assert player.stats.health == 100 - max(1, 100 // 8)


def test_on_turn_start_paralysis_can_block_action(player, monkeypatch):
    player.apply_status("paralizado", duration=2)
    monkeypatch.setattr("juego_rol_texto.characters.player.random.random", lambda: 0.1)
    can_act = player.on_turn_start()
    assert can_act is False


def test_on_turn_start_frozen_blocks_action_and_can_thaw(player, monkeypatch):
    player.apply_status("congelado", duration=2)
    monkeypatch.setattr("juego_rol_texto.characters.player.random.random", lambda: 0.9)
    assert player.on_turn_start() is False

    player.apply_status("congelado", duration=2)
    monkeypatch.setattr("juego_rol_texto.characters.player.random.random", lambda: 0.01)
    assert player.on_turn_start() is True
    assert not any(e["name"] == "congelado" for e in player.status_effects)


def test_on_turn_end_expires_status_effects(player):
    player.apply_status("veneno", duration=1)
    player.on_turn_end()
    assert player.status_effects == []


def test_on_turn_end_removes_expired_stat_buffs(player):
    class FakeBuff:
        def __init__(self):
            self.duration = 1
            self.removed_for = None

        def remove(self, target):
            self.removed_for = target

    buff = FakeBuff()
    player.active_effects.append(buff)
    player.on_turn_end()
    assert buff.removed_for is player
    assert player.active_effects == []
