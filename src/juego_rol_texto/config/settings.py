"""Persistencia de la configuración del juego en config.ini.

Guarda volumen de audio (`[VOLUME]`) y si el jugador ha aceptado el envío
automático de informes de error (`[REPORTS]`). Las escrituras conservan el
resto de secciones (leer-modificar-escribir), para que ajustar el volumen no
borre la preferencia de informes ni al revés.
"""

import configparser
import contextlib

from juego_rol_texto.config.paths import CONFIG_FILE

DEFAULT_MUSIC_VOLUME = 0.4
DEFAULT_SFX_VOLUME = 0.5

# El envío de informes está DESACTIVADO por defecto: solo se activa si el
# jugador lo acepta explícitamente (opt-in). "no preguntado" es un tercer
# estado que usamos para lanzar el aviso la primera vez.
CRASH_REPORTS_UNSET = "unset"


def _read() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    if CONFIG_FILE.exists():
        with contextlib.suppress(configparser.Error):
            config.read(CONFIG_FILE)
    return config


def _write(config: configparser.ConfigParser) -> None:
    try:
        with open(CONFIG_FILE, "w") as configfile:
            config.write(configfile)
    except OSError as e:
        print(f"Error al guardar la configuración: {e}")


def save_config(music_volume: float, sound_volume: float) -> None:
    """Guarda la configuración de volumen, conservando el resto de secciones."""
    config = _read()
    if not config.has_section("VOLUME"):
        config.add_section("VOLUME")
    config["VOLUME"]["music"] = str(round(float(music_volume), 2))
    config["VOLUME"]["sound"] = str(round(float(sound_volume), 2))
    _write(config)


def load_config() -> tuple[float, float]:
    """Lee el volumen y devuelve valores por defecto si hay errores."""
    config = _read()
    try:
        music = config.getfloat("VOLUME", "music", fallback=DEFAULT_MUSIC_VOLUME)
        sound = config.getfloat("VOLUME", "sound", fallback=DEFAULT_SFX_VOLUME)
        return music, sound
    except (configparser.Error, ValueError):
        return DEFAULT_MUSIC_VOLUME, DEFAULT_SFX_VOLUME


def load_crash_reporting() -> "bool | str":
    """Devuelve True/False si el jugador ya decidió, o CRASH_REPORTS_UNSET si
    todavía no se le ha preguntado."""
    config = _read()
    if not config.has_option("REPORTS", "send_crash_reports"):
        return CRASH_REPORTS_UNSET
    try:
        return config.getboolean("REPORTS", "send_crash_reports")
    except ValueError:
        return CRASH_REPORTS_UNSET


def save_crash_reporting(enabled: bool) -> None:
    config = _read()
    if not config.has_section("REPORTS"):
        config.add_section("REPORTS")
    config["REPORTS"]["send_crash_reports"] = "true" if enabled else "false"
    _write(config)
