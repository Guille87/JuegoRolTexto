import sys
import threading

from juego_rol_texto.config import logging_setup


def test_report_crash_writes_a_crash_file_with_traceback(tmp_path, monkeypatch):
    monkeypatch.setattr(logging_setup, "LOG_DIR", tmp_path)
    monkeypatch.setattr(logging_setup, "LOG_FILE", tmp_path / "juego.log")

    try:
        raise ValueError("objeto raro sin get_stats_info")
    except ValueError as exc:
        crash_path = logging_setup.report_crash(exc, context="test inventario")

    assert crash_path is not None
    assert crash_path.exists()
    contents = crash_path.read_text(encoding="utf-8")
    assert "ValueError: objeto raro sin get_stats_info" in contents
    assert "Traceback" in contents
    assert "test inventario" in contents


def test_setup_logging_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr(logging_setup, "LOG_DIR", tmp_path)
    monkeypatch.setattr(logging_setup, "LOG_FILE", tmp_path / "juego.log")
    monkeypatch.setattr(logging_setup, "_configured", False)
    monkeypatch.setattr(logging_setup.logger, "handlers", [])
    # setup_logging instala hooks globales; los restauramos al acabar el test.
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
    monkeypatch.setattr(threading, "excepthook", threading.excepthook)

    logging_setup.setup_logging()
    logging_setup.setup_logging()

    assert len(logging_setup.logger.handlers) == 1
