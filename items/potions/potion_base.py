from abc import ABC, abstractmethod

from items.item_base import Item


class Potion(Item, ABC):
    def __init__(self, name, description, value, duration=0):
        super().__init__(name, description, value)
        self.duration = duration

    @abstractmethod
    def get_stats_info(self):
        """Este método DEBE ser implementado por todas las pociones."""
        pass

    def to_dict(self):
        data = super().to_dict()
        data["duration"] = self.duration
        return data