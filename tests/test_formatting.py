from juego_rol_texto.characters.enemies.goblin import Goblin
from juego_rol_texto.characters.enemies.troll import Troll
from juego_rol_texto.ui.formatting import (
    print_bestiary_entry,
    print_player_enemy_info,
    print_status,
)


def test_print_status_renders_both_health_bars(player, capsys):
    enemy = Goblin()
    print_status(player, enemy, defeated_enemies=[enemy.name])
    out = capsys.readouterr().out
    assert player.name in out
    assert enemy.name in out
    assert f"{player.stats.health}/{player.stats.max_health} HP" in out


def test_print_status_hides_undefeated_enemy_health(player, capsys):
    enemy = Goblin()
    print_status(player, enemy, defeated_enemies=[])
    out = capsys.readouterr().out
    assert "??/?? HP" in out


def test_print_player_enemy_info_hides_stats_of_undefeated_enemy(player, capsys):
    enemy = Goblin()
    print_player_enemy_info(player, enemy, defeated_enemies=[])
    out = capsys.readouterr().out
    assert "Información oculta" in out


def test_print_player_enemy_info_shows_stats_of_defeated_enemy(player, capsys):
    enemy = Goblin()
    print_player_enemy_info(player, enemy, defeated_enemies=[enemy.name])
    out = capsys.readouterr().out
    assert f"Vida: {enemy.stats.health}/{enemy.stats.max_health}" in out


def test_print_bestiary_entry_includes_kill_count_and_gold(capsys):
    enemy = Goblin()
    print_bestiary_entry(enemy, kill_count=7)
    out = capsys.readouterr().out
    assert "Veces derrotado: 7" in out
    assert f"{enemy.gold_min}-{enemy.gold_max}" in out


def test_print_bestiary_entry_shows_elemental_weakness(capsys):
    print_bestiary_entry(Troll(), kill_count=1)
    out = capsys.readouterr().out
    assert "Debilidad elemental" in out
    assert "Fuego" in out
