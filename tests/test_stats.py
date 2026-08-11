from juego_rol_texto.characters.stats import (
    BASE_HIT_CHANCE, MAX_HIT_CHANCE, MIN_HIT_CHANCE, Stats, resolve_hit,
)


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


def test_speed_precision_evasion_default(player):
    assert player.stats.speed == 10
    assert player.stats.precision == 0
    assert player.stats.evasion == 0


def test_resolve_hit_uses_base_chance_when_precision_and_evasion_are_equal(monkeypatch):
    # BASE_HIT_CHANCE% de acierto: justo por debajo del umbral acierta, justo por encima falla.
    monkeypatch.setattr("juego_rol_texto.characters.stats.random.random", lambda: (BASE_HIT_CHANCE - 1) / 100)
    assert resolve_hit(0, 0) is True

    monkeypatch.setattr("juego_rol_texto.characters.stats.random.random", lambda: (BASE_HIT_CHANCE + 1) / 100)
    assert resolve_hit(0, 0) is False


def test_resolve_hit_chance_is_clamped_between_min_and_max(monkeypatch):
    # Precisión muy superior a la evasión -> se limita a MAX_HIT_CHANCE, nunca "acierto absoluto" sin tirada
    monkeypatch.setattr("juego_rol_texto.characters.stats.random.random", lambda: (MAX_HIT_CHANCE - 1) / 100)
    assert resolve_hit(1000, 0) is True

    # Evasión muy superior a la precisión -> se limita a MIN_HIT_CHANCE, nunca 0% de posibilidad
    monkeypatch.setattr("juego_rol_texto.characters.stats.random.random", lambda: (MIN_HIT_CHANCE - 1) / 100)
    assert resolve_hit(0, 1000) is True
    monkeypatch.setattr("juego_rol_texto.characters.stats.random.random", lambda: (MIN_HIT_CHANCE + 1) / 100)
    assert resolve_hit(0, 1000) is False
