class Stats:
    """Maneja las estadísticas básicas con validación de límites."""
    def __init__(self, health: int, max_health: int, min_atk: int, max_atk: int, armor: int,
                 magic_resist: int = 0, crit_chance: float = 0.0, crit_damage: float = 1.5):
        self.max_health = max_health
        self._health = health
        self.min_atk = min_atk
        self.max_atk = max_atk
        self.armor = armor
        self.magic_resist = magic_resist
        self.crit_chance = crit_chance
        self.crit_damage = crit_damage

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, value: int) -> None:
        # Encapsulamiento: Aseguramos que la vida esté en el rango [0, max_health]
        self._health = max(0, min(value, self.max_health))

    def __str__(self) -> str:
        return (f"HP: {self.health}/{self.max_health} | ATK: {self.min_atk}-{self.max_atk} "
                f"| ARM: {self.armor} | RES.MAG: {self.magic_resist} "
                f"| CRIT: {self.crit_chance*100:.0f}% x{self.crit_damage:.2f}")
