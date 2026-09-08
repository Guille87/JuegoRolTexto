import pytest

from juego_rol_texto import updater


@pytest.fixture(autouse=True)
def _reset_updater_state(monkeypatch):
    monkeypatch.setattr(updater, "_available", None)
    monkeypatch.setattr(updater, "_current_version", lambda: "0.3.0")
    updater._stop.clear()
    yield
    updater._available = None
    updater._stop.clear()


def _release(tag, assets=None, body="Notas del release"):
    return {
        "tag_name": tag,
        "body": body,
        "assets": [{"name": n, "browser_download_url": f"https://x/{n}"} for n in (assets or [])],
    }


@pytest.mark.parametrize(
    ("text", "expected"),
    [("1.2.3", (1, 2, 3)), ("v0.4.0", (0, 4, 0)), ("V2", (2,)), ("1.2.3-rc1", (1, 2, 3)), ("", (0,))],
)
def test_version_tuple(text, expected):
    assert updater._version_tuple(text) == expected


def test_is_active_is_false_outside_a_frozen_build():
    assert updater.is_active() is False


def test_current_version_matches_the_package(monkeypatch):
    monkeypatch.undo()  # deshacer el mock de la fixture
    import juego_rol_texto

    assert updater._current_version() == juego_rol_texto.__version__


@pytest.mark.parametrize(
    ("sums", "expected"),
    [
        ("ABC123  JuegoRolTexto-v0.4.0-windows.zip\ndef  otro.zip", "abc123"),
        ("abc  *JuegoRolTexto-v0.4.0-windows.zip", "abc"),  # prefijo '*' de modo binario
        ("abc  otra-cosa.zip", None),  # el zip no aparece
    ],
)
def test_sha_for_parses_the_right_line(monkeypatch, sums, expected):
    monkeypatch.setattr(updater, "_get_text", lambda url: sums)
    assert updater._sha_for("JuegoRolTexto-v0.4.0-windows.zip", "https://x/SHA256SUMS") == expected


def test_sha_for_returns_none_without_a_url_or_on_error(monkeypatch):
    assert updater._sha_for("z.zip", None) is None
    monkeypatch.setattr(updater, "_get_text", lambda url: (_ for _ in ()).throw(OSError()))
    assert updater._sha_for("z.zip", "https://x/SHA256SUMS") is None


def test_check_returns_info_for_a_newer_release(monkeypatch):
    monkeypatch.setattr(updater, "_get_json", lambda url: _release("v0.4.0", ["JuegoRolTexto-v0.4.0-windows.zip"]))
    monkeypatch.setattr(updater, "_sha_for", lambda name, url: "abc123")

    info = updater.check()

    assert info is not None
    assert info.version == "0.4.0"
    assert info.tag == "v0.4.0"
    assert info.zip_url.endswith("JuegoRolTexto-v0.4.0-windows.zip")
    assert info.sha256 == "abc123"
    assert updater.available() is info  # se guarda


@pytest.mark.parametrize("tag", ["v0.3.0", "v0.2.0", "v0.1.5"])
def test_check_returns_none_when_not_newer(monkeypatch, tag):
    monkeypatch.setattr(updater, "_get_json", lambda url: _release(tag, [f"JuegoRolTexto-{tag}-windows.zip"]))
    assert updater.check() is None
    assert updater.available() is None


def test_check_returns_none_when_there_is_no_windows_zip(monkeypatch):
    monkeypatch.setattr(updater, "_get_json", lambda url: _release("v0.4.0", ["source.tar.gz"]))
    assert updater.check() is None


def test_check_returns_none_and_does_not_raise_on_network_error(monkeypatch):
    def boom(url):
        raise OSError("sin red")

    monkeypatch.setattr(updater, "_get_json", boom)
    assert updater.check() is None


def test_a_failed_check_does_not_clear_a_previous_result(monkeypatch):
    monkeypatch.setattr(updater, "_get_json", lambda url: _release("v0.4.0", ["JuegoRolTexto-v0.4.0-windows.zip"]))
    monkeypatch.setattr(updater, "_sha_for", lambda name, url: None)
    found = updater.check()
    assert found is not None

    monkeypatch.setattr(updater, "_get_json", lambda url: (_ for _ in ()).throw(OSError()))
    assert updater.check() is None
    assert updater.available() is found  # sigue ahí


def test_background_check_stores_the_result_and_stops_cleanly(monkeypatch):
    monkeypatch.setattr(updater, "_get_json", lambda url: _release("v0.9.0", ["JuegoRolTexto-v0.9.0-windows.zip"]))
    monkeypatch.setattr(updater, "_sha_for", lambda name, url: None)

    updater.start_background_check()
    assert updater._thread is not None
    updater._thread.join(timeout=5)
    updater.stop_background_check()

    assert not updater._thread.is_alive()
    assert updater.available() is not None


def test_cleanup_staging_is_a_noop_when_there_is_nothing_to_clean():
    updater.cleanup_staging()  # sin excepción
