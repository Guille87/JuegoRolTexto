class Item:
    def __init__(self, name, description, value):
        self.name = name
        self.description = description
        self.value = value

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "value": self.value
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"],
            data["description"],
            data["value"]
        )


class Potion(Item):
    def __init__(self, name, description, value, healing_amount=None, defense_boost=None, damage_boost=None, regeneration_amount=None, duration=3):
        super().__init__(name, description, value)
        self.healing_amount = healing_amount
        self.defense_boost = defense_boost
        self.damage_boost = damage_boost
        self.regeneration_amount = regeneration_amount
        self.duration = duration
        self.turns_remaining = 0

    def to_dict(self):
        item_dict = super().to_dict()
        item_dict["healing_amount"] = self.healing_amount
        item_dict["defense_boost"] = self.defense_boost
        item_dict["damage_boost"] = self.damage_boost
        item_dict["regeneration_amount"] = self.regeneration_amount
        return item_dict

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"],
            data["description"],
            data["value"],
            data["healing_amount"],
            data.get("defense_boost"),
            data.get("damage_boost"),
            data.get("regeneration_amount")
        )


class Weapon(Item):
    def __init__(self, name, description, value, damage):
        super().__init__(name, description, value)
        self.damage = damage

    def to_dict(self):
        item_dict = super().to_dict()
        item_dict["damage"] = self.damage
        return item_dict

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"],
            data["description"],
            data["value"],
            data["damage"]
        )


class Armor(Item):
    def __init__(self, name, description, value, defense):
        super().__init__(name, description, value)
        self.defense = defense

    def to_dict(self):
        item_dict = super().to_dict()
        item_dict["defense"] = self.defense
        return item_dict

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"],
            data["description"],
            data["value"],
            data["defense"]
        )
