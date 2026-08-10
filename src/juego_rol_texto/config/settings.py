"""Persistencia de la configuración de volumen en config.ini."""
import configparser

from juego_rol_texto.config.paths import CONFIG_FILE

DEFAULT_MUSIC_VOLUME = 0.4
DEFAULT_SFX_VOLUME = 0.5


def save_config(music_volume: float, sound_volume: float) -> None:
    """Guarda la configuración de volumen en un archivo .ini"""
    config = configparser.ConfigParser()
    config['VOLUME'] = {
        'music': str(round(float(music_volume), 2)),
        'sound': str(round(float(sound_volume), 2))
    }
    try:
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
    except IOError as e:
        print(f"Error al guardar la configuración: {e}")


def load_config() -> tuple[float, float]:
    """Lee la configuración y devuelve valores por defecto si hay errores."""
    config = configparser.ConfigParser()

    if not CONFIG_FILE.exists():
        return DEFAULT_MUSIC_VOLUME, DEFAULT_SFX_VOLUME

    try:
        config.read(CONFIG_FILE)
        # Usamos fallback directamente en el get para simplificar
        music = config.getfloat('VOLUME', 'music', fallback=DEFAULT_MUSIC_VOLUME)
        sound = config.getfloat('VOLUME', 'sound', fallback=DEFAULT_SFX_VOLUME)
        return music, sound
    except (configparser.Error, ValueError):
        return DEFAULT_MUSIC_VOLUME, DEFAULT_SFX_VOLUME
