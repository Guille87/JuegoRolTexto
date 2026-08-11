import random

# Tirada de acierto compartida por el ataque estándar del jugador
# (combat/battle.py::_execute_turn) y el ataque por defecto del enemigo
# (characters/enemies/enemy_base.py::Enemy.perform_turn). Vive aquí, en un
# módulo hoja sin dependencias de combate ni de personajes concretos, para que
# ambos puedan importarla sin crear un ciclo de imports.
BASE_HIT_CHANCE = 90
MIN_HIT_CHANCE = 5
MAX_HIT_CHANCE = 100


def resolve_hit(attacker_precision: int, defender_evasion: int) -> bool:
    """Tirada de acierto: precisión del atacante vs evasión del defensor.

    Parte de un 90% de acierto base; cada punto de diferencia entre precisión
    y evasión suma o resta un 1%, con un suelo del 5% y un techo del 100% (un
    ataque nunca falla ni acierta con una probabilidad absoluta del 0%/100%
    salvo que la diferencia de stats sea muy grande).
    """
    chance = BASE_HIT_CHANCE + attacker_precision - defender_evasion
    chance = max(MIN_HIT_CHANCE, min(MAX_HIT_CHANCE, chance))
    return random.random() * 100 < chance


class Stats:
    """Maneja las estadísticas básicas con validación de límites."""
    def __init__(self, health: int, max_health: int, min_atk: int, max_atk: int, armor: int,
                 magic_resist: int = 0, crit_chance: float = 0.0, crit_damage: float = 1.5,
                 speed: int = 10, precision: int = 0, evasion: int = 0):
        self.max_health = max_health
        self._health = health
        self.min_atk = min_atk
        self.max_atk = max_atk
        self.armor = armor
        self.magic_resist = magic_resist
        self.crit_chance = crit_chance
        self.crit_damage = crit_damage
        # Velocidad: alimenta el sistema de barra ATB en combat/battle.py (más
        # velocidad = actuar con más frecuencia, no solo "ir primero").
        self.speed = speed
        # Precisión/Evasión: alimentan resolve_hit() de más arriba.
        self.precision = precision
        self.evasion = evasion

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
