from juego_rol_texto import updater
from juego_rol_texto.ui import menus


def _info(tag="v0.4.0"):
    return updater.UpdateInfo(version=tag.lstrip("v"), tag=tag, zip_url="https://x/z.zip", sha256=None, notes="")


def test_update_notice_prints_every_time_an_update_is_available(monkeypatch, capsys):
    """A propósito NO se limita a una vez: debe salir en cada redibujado del
    menú y al entrar a nueva/cargar partida, por si el jugador va rápido."""
    monkeypatch.setattr(menus.updater, "available", lambda: _info("v0.5.0"))

    menus._maybe_show_update_notice(in_game=False)
    first = capsys.readouterr().out
    menus._maybe_show_update_notice(in_game=False)
    second = capsys.readouterr().out

    assert "v0.5.0" in first
    assert "v0.5.0" in second


def test_update_notice_in_game_points_to_the_main_menu(monkeypatch, capsys):
    monkeypatch.setattr(menus.updater, "available", lambda: _info())
    menus._maybe_show_update_notice(in_game=True)
    assert "Menú Principal" in capsys.readouterr().out


def test_no_update_notice_when_nothing_is_available(monkeypatch, capsys):
    monkeypatch.setattr(menus.updater, "available", lambda: None)
    menus._maybe_show_update_notice(in_game=False)
    assert capsys.readouterr().out == ""


def test_load_saved_game_shows_the_update_notice_before_asking(monkeypatch, capsys):
    monkeypatch.setattr(menus.updater, "available", lambda: _info("v0.5.0"))
    monkeypatch.setattr(menus.console, "ask", lambda _="": "Nadie")
    monkeypatch.setattr(menus, "load_game", lambda _p: None)

    menus.load_saved_game()

    assert "v0.5.0" in capsys.readouterr().out


def _answers(monkeypatch, *responses):
    it = iter(responses)
    monkeypatch.setattr(menus.console, "ask", lambda *a, **k: next(it))


def test_ask_chain_setup_empty_means_one_manual_fight(monkeypatch):
    _answers(monkeypatch, "")
    assert menus._ask_chain_setup() == (1, "manual")


def test_ask_chain_setup_one_is_manual_without_asking_mode(monkeypatch):
    _answers(monkeypatch, "1")
    assert menus._ask_chain_setup() == (1, "manual")


def test_ask_chain_setup_several_defaults_to_auto(monkeypatch):
    _answers(monkeypatch, "3", "")
    assert menus._ask_chain_setup() == (3, "auto")


def test_ask_chain_setup_turbo(monkeypatch):
    _answers(monkeypatch, "5", "2")
    assert menus._ask_chain_setup() == (5, "turbo")


def test_ask_chain_setup_caps_the_count(monkeypatch):
    _answers(monkeypatch, "999", "1")
    assert menus._ask_chain_setup() == (menus._MAX_CHAIN_BATTLES, "auto")


def test_ask_chain_setup_rejects_garbage(monkeypatch):
    _answers(monkeypatch, "abc")
    assert menus._ask_chain_setup() is None


def test_run_battle_chain_runs_every_fight_on_wins(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(menus, "_get_enemy_instance", lambda name: name)
    monkeypatch.setattr(menus, "initiate_battle", lambda *a, **k: calls.append(k.get("start_auto")) or "victory")
    _answers(monkeypatch, "")  # la pausa final

    menus._run_battle_chain(object(), "Goblin", ["Goblin"], ["Goblin"], count=4, mode="auto")

    assert len(calls) == 4
    assert "Cadena completada: 4/4" in capsys.readouterr().out


def test_run_battle_chain_stops_on_defeat(monkeypatch, capsys):
    outcomes = iter(["victory", "defeat", "victory"])
    monkeypatch.setattr(menus, "_get_enemy_instance", lambda name: name)
    monkeypatch.setattr(menus, "initiate_battle", lambda *a, **k: next(outcomes))

    menus._run_battle_chain(object(), "Goblin", ["Goblin"], ["Goblin"], count=3, mode="turbo")

    out = capsys.readouterr().out
    assert "Has caído en combate" in out
    assert "1/3 peleas completadas" in out


def test_run_battle_chain_turbo_never_pauses(monkeypatch):
    monkeypatch.setattr(menus, "_get_enemy_instance", lambda name: name)
    monkeypatch.setattr(menus, "initiate_battle", lambda *a, **k: "victory")
    monkeypatch.setattr(menus.console, "ask", lambda *a, **k: (_ for _ in ()).throw(AssertionError("turbo no pausa")))

    menus._run_battle_chain(object(), "Goblin", ["Goblin"], ["Goblin"], count=3, mode="turbo")


def test_check_updates_now_reports_a_new_version(monkeypatch, capsys):
    monkeypatch.setattr(menus.updater, "check", lambda: _info("v9.0.0"))
    menus._check_updates_now()
    assert "v9.0.0" in capsys.readouterr().out


def test_check_updates_now_reports_up_to_date(monkeypatch, capsys):
    monkeypatch.setattr(menus.updater, "check", lambda: None)
    monkeypatch.setattr(menus.updater, "_current_version", lambda: "0.3.0")
    menus._check_updates_now()
    assert "0.3.0" in capsys.readouterr().out
