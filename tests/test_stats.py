from juego_rol_texto.characters.stats import Stats


def test_health_is_clamped_to_max_health():
    stats = Stats(health=50, max_health=100, min_atk=1, max_atk=2, armor=0)
    stats.health = 500
    assert stats.health == 100


def test_health_is_clamped_to_zero():
    stats = Stats(health=50, max_health=100, min_atk=1, max_atk=2, armor=0)
    stats.health = -30
    assert stats.health == 0


def test_str_representation():
    stats = Stats(health=10, max_health=20, min_atk=1, max_atk=5, armor=3, magic_resist=1,
                   crit_chance=0.1, crit_damage=1.75)
    assert str(stats) == "HP: 10/20 | ATK: 1-5 | ARM: 3 | RES.MAG: 1 | CRIT: 10% x1.75"


def test_magic_resist_defaults_to_zero():
    stats = Stats(health=10, max_health=20, min_atk=1, max_atk=5, armor=3)
    assert stats.magic_resist == 0


def test_crit_defaults(player):
    assert player.stats.crit_chance == 0.0
    assert player.stats.crit_damage == 1.5
