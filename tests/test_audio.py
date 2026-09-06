import pygame
import pytest

from juego_rol_texto.audio.resource_manager import ResourceManager


@pytest.fixture
def restore_mixer():
    """Algunos tests cierran el mezclador a propósito; lo reabrimos al terminar
    para no romper la fixture de audio de sesión que comparten los demás tests."""
    yield
    if not pygame.mixer.get_init():
        pygame.mixer.init()


def test_update_is_silent_when_mixer_is_closed(restore_mixer, capsys):
    """Regresión: al salir del juego el mezclador se cierra mientras el hilo de
    música en segundo plano puede dar una última vuelta. update()/play_music()
    no deben lanzar ni imprimir 'Audio device hasn't been opened'."""
    rm = ResourceManager()
    rm.music_paths.setdefault("ale_and_anecdotes", "no/importa/la/ruta.ogg")

    pygame.mixer.quit()
    assert not pygame.mixer.get_init()

    rm.update()
    rm.play_music("ale_and_anecdotes")

    assert "Audio device hasn't been opened" not in capsys.readouterr().out


def test_music_watchdog_stops_before_join():
    """El hilo de música debe salir de su bucle en cuanto se activa el evento
    de parada, para poder cerrar el mezclador sin carreras al salir del juego."""
    from juego_rol_texto import app

    app._music_watchdog_stop.clear()
    import threading

    t = threading.Thread(target=app._music_watchdog, daemon=True)
    t.start()
    app._music_watchdog_stop.set()
    t.join(timeout=5)

    assert not t.is_alive()
    app._music_watchdog_stop.clear()
