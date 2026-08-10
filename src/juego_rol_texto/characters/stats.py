class Stats:
    """Maneja las estadísticas básicas con validación de límites."""
    def __init__(self, health: int, max_health: int, min_atk: int, max_atk: int, defense: int):
        self.max_health = max_health
        self._health = health
        self.min_atk = min_atk
        self.max_atk = max_atk
        self.defense = defense

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, value: int) -> None:
        # Encapsulamiento: Aseguramos que la vida esté en el rango [0, max_health]
        self._health = max(0, min(value, self.max_health))

    def __str__(self) -> str:
        return f"HP: {self.health}/{self.max_health} | ATK: {self.min_atk}-{self.max_atk} | DEF: {self.defense}"
