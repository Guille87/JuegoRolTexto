import pygame


class ResourceManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.resources = {}
            cls._instance.music_playing = {}  # Diccionario para mantener el estado de la música
        return cls._instance

    def __init__(self):
        self.resources = {}
        self.current_music_volume = 0.5  # Volumen de la música actual

    def load_sound(self, name, path):
        sound = pygame.mixer.Sound(path)
        self.resources[name] = sound

    def get_sound(self, name):
        # Devuelve el sonido correspondiente al nombre dado, si existe
        return self.resources.get(name)

    def play_sound(self, sound_name):
        sound = self.get_sound(sound_name)
        if sound:
            sound.play()

    def set_all_music_volume(self, volume):
        self.current_music_volume = volume
        for music_name, music_sound in self.resources.items():
            if music_sound:
                music_sound.set_volume(volume)

    def play_music(self, name, loops=-1):
        music_sound = self.resources.get(name)
        if music_sound:
            music_sound.set_volume(self.current_music_volume)  # Establecer volumen actual
            music_sound.play(loops=loops)
            self.music_playing[name] = True  # Actualiza el estado de reproducción de la música

    def is_music_playing(self, name):
        return self.music_playing.get(name, False)

    def stop_all_music(self, keep_playing_name):
        for name, is_playing in self.music_playing.items():
            if is_playing and name != keep_playing_name:
                music_sound = self.resources.get(name)
                if music_sound:
                    music_sound.stop()
                    self.music_playing[name] = False  # Actualiza el estado de reproducción de la música
