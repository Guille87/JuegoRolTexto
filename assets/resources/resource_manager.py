import os
import random

import pygame

# Definimos un evento personalizado para Pygame
MUSIC_END_EVENT = pygame.USEREVENT + 1


class ResourceManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized: return
        self.sounds = {}
        self.music = {}
        self.current_volume_sfx = 0.5
        self.current_volume_music = 0.4
        self.current_track_name = None
        self.mood = "adventure"  # Estado por defecto
        self.target_enemy = None
        self._initialized = True

    def update(self):
        """Se autogestiona según el mood actual."""
        if not pygame.mixer.get_busy():
            if self.mood == "battle":
                self._handle_battle_music(self.target_enemy)
            else:
                self.play_random_adventure_music()

    def set_mood(self, mood, enemy_name=None):
        """Cambia el contexto musical."""
        self.mood = mood
        self.target_enemy = enemy_name

    def _handle_battle_music(self, enemy_name):
        """Lógica interna para música de combate."""
        if enemy_name == "Orco":
            self.play_music("scaring_crows")
        elif enemy_name == "Mago":
            self.play_music("Siege_of_the_Black_Gate")
        else:
            # Música genérica de combate si no es un jefe
            self.play_music("scaring_crows")

    def play_random_adventure_music(self):
        adventure_tracks = ["a_robust_crew", "ale_and_anecdotes", "Wanderers_Hearth"]
        chosen = random.choice(adventure_tracks)
        self.play_music(chosen, loops=0) # loops=0 para que al acabar entre el update

    def is_music_playing(self, name):
        """Verifica si el mixer está ocupado y si la música solicitada está en nuestro diccionario."""
        # Pygame mixer solo dice si suena algo, no el nombre exacto.
        # Pero podemos verificar si el mixer está ocupado.
        is_busy = pygame.mixer.get_busy()
        exists = name in self.music

        return is_busy and exists

    def load_audio(self, name, path, is_music=False):
        if not os.path.exists(path):
            print(f"Archivo no encontrado: {path}")
            return

        try:
            sound = pygame.mixer.Sound(path)
            if is_music:
                sound.set_volume(self.current_volume_music)
                self.music[name] = sound
            else:
                sound.set_volume(self.current_volume_sfx)
                self.sounds[name] = sound
        except Exception as e:
            print(f"Error al cargar audio {name}: {e}")

    def play_music(self, name, loops=0):
        if name in self.music:
            # Si ya está sonando la misma, no la cortamos
            if self.current_track_name == name and pygame.mixer.get_busy():
                return
            self.stop_all_music()
            self.music[name].play(loops=loops)
            self.current_track_name = name

    def play_sfx(self, name):
        """Reproduce un efecto de sonido si existe en el diccionario."""
        if name in self.sounds:
            self.sounds[name].play()
        else:
            print(f"SFX {name} no encontrado.")

    def stop_all_music(self):
        for track in self.music.values():
            track.stop()

    def set_volume_music(self, volume):
        self.current_volume_music = volume
        for track in self.music.values():
            track.set_volume(volume)

    def set_volume_sfx(self, volume):
        self.current_volume_sfx = volume
        for track in self.sounds.values():
            track.set_volume(volume)
