from abc import ABC, abstractmethod


class Item(ABC):
    def __init__(self, name: str, description: str, value: int):
        self.name = name
        self.description = description
        self.value = value

    @abstractmethod
    def use(self, target):
        pass

    def to_dict(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "name": self.name,
            "description": self.description,
            "value": self.value
        }
