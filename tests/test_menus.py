import pytest

from juego_rol_texto import updater
from juego_rol_texto.ui import menus


@pytest.fixture(autouse=True)
def _reset_notice(monkeypatch):
    monkeypatch.setattr(menus, "_update_notice_shown", False)


def _info(tag="v0.4.0"):
    return updater.UpdateInfo(version=tag.lstrip("v"), tag=tag, zip_url="https://x/z.zip", sha256=None, notes="")


def test_update_notice_prints_once_when_an_update_is_available(monkeypatch, capsys):
    monkeypatch.setattr(menus.updater, "available", lambda: _info("v0.5.0"))

    menus._maybe_show_update_notice(in_game=False)
    first = capsys.readouterr().out
    menus._maybe_show_update_notice(in_game=False)
    second = capsys.readouterr().out

    assert "v0.5.0" in first
    assert second == ""  # ya se avisó


def test_update_notice_in_game_points_to_the_main_menu(monkeypatch, capsys):
    monkeypatch.setattr(menus.updater, "available", lambda: _info())
    menus._maybe_show_update_notice(in_game=True)
    assert "Menú Principal" in capsys.readouterr().out


def test_no_update_notice_when_nothing_is_available(monkeypatch, capsys):
    monkeypatch.setattr(menus.updater, "available", lambda: None)
    menus._maybe_show_update_notice(in_game=False)
    assert capsys.readouterr().out == ""


def test_check_updates_now_reports_a_new_version(monkeypatch, capsys):
    monkeypatch.setattr(menus.updater, "check", lambda: _info("v9.0.0"))
    menus._check_updates_now()
    assert "v9.0.0" in capsys.readouterr().out


def test_check_updates_now_reports_up_to_date(monkeypatch, capsys):
    monkeypatch.setattr(menus.updater, "check", lambda: None)
    monkeypatch.setattr(menus.updater, "_current_version", lambda: "0.3.0")
    menus._check_updates_now()
    assert "0.3.0" in capsys.readouterr().out
