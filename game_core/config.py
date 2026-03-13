import configparser
import os

CONFIG_FILE = 'config.ini'


def save_config(music_volume, sound_volume):
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


def load_config():
    """Lee la configuración y devuelve valores por defecto si hay errores."""
    config = configparser.ConfigParser()

    # Valores por defecto centralizados
    default_music = 0.4
    default_sfx = 0.5

    if not os.path.exists(CONFIG_FILE):
        return default_music, default_sfx

    try:
        config.read(CONFIG_FILE)
        # Usamos fallback directamente en el get para simplificar
        music = config.getfloat('VOLUME', 'music', fallback=default_music)
        sound = config.getfloat('VOLUME', 'sound', fallback=default_sfx)
        return music, sound
    except (configparser.Error, ValueError):
        return default_music, default_sfx