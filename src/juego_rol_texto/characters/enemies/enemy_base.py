import random

from juego_rol_texto.characters.stats import Stats, resolve_hit
from juego_rol_texto.ui import console


class Enemy:
    # Multiplicador de daño por elemento recibido; vacío = neutral a todo.
    # Las subclases lo sobrescriben para marcar debilidades (p. ej. {"fuego": 2.0}).
    ELEMENTAL_WEAKNESSES: dict = {}

    def __init__(self, name: str, stats: Stats, gold_min: int, gold_max: int):
        self.name = name
        self.stats = stats  # Objeto de la clase Stats
        self.gold_min = gold_min
        self.gold_max = gold_max

    def get_gold_drop(self) -> int:
        return random.randint(self.gold_min, self.gold_max)

    def take_damage(self, damage: int, defeated_enemies: list | None = None, element: str | None = None,
                     is_magical: bool = False, armor_penetration: int = 0, magic_penetration: int = 0) -> int:
        # Multiplicador elemental (si el ataque tiene elemento y el enemigo es débil a él)
        multiplier = self.ELEMENTAL_WEAKNESSES.get(element, 1.0) if element else 1.0
        damage = int(damage * multiplier)

        # Igual que Player.take_damage: el daño mágico se mitiga con resistencia
        # mágica en vez de con armadura, y la penetración del atacante reduce
        # esa mitigación antes de restar el daño.
        if is_magical:
            mitigation = max(0, self.stats.magic_resist - magic_penetration)
        else:
            mitigation = max(0, self.stats.armor - armor_penetration)
        actual_damage = max(0, damage - mitigation)
        self.stats.health -= actual_damage
        return actual_damage

    def is_alive(self) -> bool:
        return self.stats.health > 0

    def get_attack_damage(self) -> int:
        return random.randint(self.stats.min_atk, self.stats.max_atk)

    def perform_turn(self, player) -> None:
        """Lógica por defecto: atacar. Las subclases pueden sobrescribir esto."""
        if not resolve_hit(self.stats.precision, player.get_total_evasion()):
            print(f"{console.colorize(self.name, console.Fore.RED)} ataca, pero "
                  f"{console.colorize(player.name, console.Fore.GREEN)} esquiva el golpe.")
            return

        damage = self.get_attack_damage()

        is_crit = random.random() < self.stats.crit_chance
        if is_crit:
            damage = int(damage * self.stats.crit_damage)

        final_damage = player.take_damage(damage, armor_penetration=self.stats.armor_penetration)

        if is_crit:
            print(console.colorize("¡Golpe crítico!", console.Fore.YELLOW, bright=True))

        print(f"{console.colorize(self.name, console.Fore.RED)} ataca y hace "
              f"{console.colorize(str(final_damage), console.Fore.RED)} de daño.")

    def on_turn_end(self) -> None:
        """Regeneración de salud pasiva por defecto (self.stats.regen == 0 para
        la mayoría de enemigos: solo los "aptos" para regenerar la usan, p. ej.
        el Troll, que ademas personaliza el mensaje sobrescribiendo este método)."""
        if self.stats.regen > 0 and self.is_alive() and self.stats.health < self.stats.max_health:
            self.stats.health = min(self.stats.max_health, self.stats.health + self.stats.regen)
            console.success(f"💚 {self.name} regenera {self.stats.regen} HP.")

    def drop_item(self) -> list:
        """Por defecto no sueltan nada, las subclases lo implementan."""
        return []
