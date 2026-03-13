import random
from abc import ABC, abstractmethod


class Character(ABC):
    def __init__(self, name, stats):
        self.name = name
        self.stats = stats
        self.status_effects = []

    @property
    def is_alive(self):
        return self.stats.health > 0

    def calculate_base_damage(self):
        return random.randint(self.stats.min_atk, self.stats.max_atk)

    @abstractmethod
    def take_damage(self, amount):
        """Lógica de recepción de daño"""
        pass
