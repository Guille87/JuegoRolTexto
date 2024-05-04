import configparser

CONFIG_FILE = 'config.ini'


def save_config(music_volume, sound_volume):
    config = configparser.ConfigParser()
    config['VOLUME'] = {
        'music': str(music_volume),
        'sound': str(sound_volume)
    }
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)


def load_config():
    config = configparser.ConfigParser()

    try:
        config.read(CONFIG_FILE)

        music_volume = float(config.get('VOLUME', 'music', fallback=0.5))
        sound_volume = float(config.get('VOLUME', 'sound', fallback=0.5))
    except (configparser.Error, ValueError):
        music_volume = 0.5
        sound_volume = 0.5

    return music_volume, sound_volume
