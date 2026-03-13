class Stats:
    """Maneja las estadísticas básicas con validación de límites."""
    def __init__(self, health, max_health, min_atk, max_atk, defense):
        self.max_health = max_health
        self._health = health
        self.min_atk = min_atk
        self.max_atk = max_atk
        self.defense = defense

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        # Encapsulamiento: Aseguramos que la vida esté en el rango [0, max_health]
        self._health = max(0, min(value, self.max_health))

    def __str__(self):
        return f"HP: {self.health}/{self.max_health} | ATK: {self.min_atk}-{self.max_atk} | DEF: {self.defense}"