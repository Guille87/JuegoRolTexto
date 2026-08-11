import random

from juego_rol_texto.characters.base import Character
from juego_rol_texto.characters.stats import Stats
from juego_rol_texto.inventory.inventory import Inventory
from juego_rol_texto.items.equipment import ARMOR_SLOTS, slot_label
from juego_rol_texto.ui import console


class Player(Character):
    def __init__(self, name: str, stats: Stats):
        super().__init__(name, stats)
        self.level = 1
        self.experience = 0
        self.inventory = Inventory(self)
        self.equipped_weapon = None
        self.equipped_armor = {slot: None for slot in ARMOR_SLOTS}
        self.just_leveled_up = False
        self.in_combat = False

        # Sistema de estados alterados: [{"name": "quemado", "duration": 3, "power": 5}, ...]
        self.status_effects = []
        # Sistema de pociones de Stats
        self.active_effects = []

    # --- LÓGICA DE COMBATE ---

    def take_damage(self, amount: int, is_fire: bool = False, is_magical: bool = False) -> int:
        """Calcula el daño final tras aplicar armadura o resistencia mágica y lo resta de la vida."""
        mitigation = self.get_total_magic_resist() if is_magical else self.get_total_armor()
        final_damage = max(0, amount - mitigation)
        self.stats.health -= final_damage

        if is_fire:
            # Si recibimos fuego, buscamos el efecto 'congelado' y lo borramos
            congelado = next((e for e in self.status_effects if e["name"] == "congelado"), None)
            if congelado:
                self.status_effects.remove(congelado)
                console.warning("¡El calor del ataque ha derretido el hielo!")

        return final_damage

    def get_attack_damage(self) -> int:
        """Genera un valor de daño aleatorio basado en el rango actual."""
        min_atk, max_atk = self.get_attack_range()
        return random.randint(min_atk, max_atk)

    def get_attack_range(self) -> tuple[int, int]:
        """Devuelve el rango de ataque sumando el arma y el equipo (p. ej. anillos) equipados."""
        weapon_bonus = self.equipped_weapon.damage if self.equipped_weapon else 0
        armor_bonus = sum(item.damage for item in self.equipped_armor.values() if item)
        bonus = weapon_bonus + armor_bonus
        min_atk = self.stats.min_atk + bonus
        max_atk = self.stats.max_atk + bonus

        # Penalización por Quemadura: Ataque a la mitad
        if any(e["name"] == "quemado" for e in self.status_effects):
            min_atk //= 2
            max_atk //= 2

        return min_atk, max_atk

    def get_total_armor(self) -> int:
        """Devuelve la armadura total sumando todas las piezas equipadas."""
        bonus = sum(item.defense for item in self.equipped_armor.values() if item)
        return self.stats.armor + bonus

    def get_total_magic_resist(self) -> int:
        """Devuelve la resistencia mágica total sumando todas las piezas equipadas."""
        bonus = sum(item.magic_resist for item in self.equipped_armor.values() if item)
        return self.stats.magic_resist + bonus

    def get_total_crit_chance(self) -> float:
        """Devuelve la probabilidad de golpe crítico total sumando todas las piezas equipadas."""
        bonus = sum(item.crit_chance for item in self.equipped_armor.values() if item)
        return self.stats.crit_chance + bonus

    def get_total_crit_damage(self) -> float:
        """Devuelve el multiplicador de daño crítico total sumando todas las piezas equipadas."""
        bonus = sum(item.crit_damage for item in self.equipped_armor.values() if item)
        return self.stats.crit_damage + bonus

    def get_equipped_element(self) -> str | None:
        """Devuelve el elemento del arma equipada; si no tiene, el de los brazales."""
        if self.equipped_weapon and self.equipped_weapon.element:
            return self.equipped_weapon.element
        brazales = self.equipped_armor.get("brazales")
        return brazales.element if brazales else None

    def is_alive(self) -> bool:
        return self.stats.health > 0

    # --- GESTIÓN DE TURNOS Y ESTADOS ---

    def on_turn_start(self) -> bool:
        """Procesa los estados alterados al inicio del turno."""
        can_act = True
        # 1. Comprobación de estados que bloquean el turno
        for effect in self.status_effects[:]:
            if effect["name"] == "congelado":
                if random.random() < 0.20:
                    console.info("¡El hielo se rompe! Te has descongelado.")
                    self.status_effects.remove(effect)
                else:
                    print(console.colorize("❄️ Estás congelado y no puedes moverte.", console.Fore.BLUE))
                    # Si está congelado, no procesamos parálisis, pero SÍ veneno/quemadura más abajo
                    can_act = False
                    break  # Salimos del check de movimiento, pero seguimos con el daño

            elif effect["name"] == "paralizado":
                if random.random() < 0.5:
                    console.warning("⚡ ¡La parálisis te impide actuar!")
                    can_act = False

        # 2. Procesamiento de daño/curación (Ocurre aunque no puedas actuar)
        for effect in self.status_effects[:]:
            if effect["name"] == "quemado":
                dmg = max(1, self.stats.max_health // 16)
                self.stats.health -= dmg
                console.error(f"🔥 La quemadura te quita {dmg} HP.")

            elif effect["name"] == "veneno":
                dmg = max(1, self.stats.max_health // 8)
                self.stats.health -= dmg
                console.success(f"☣️ El veneno te quita {dmg} HP.")

            elif effect["name"] == "regeneración":
                heal = effect.get("power", 0)
                self.stats.health = min(self.stats.max_health, self.stats.health + heal)
                console.success(f"❤️ La regeneración te cura {heal} HP.")

        return can_act

    def on_turn_end(self) -> None:
        """Se ejecuta al terminar el turno (jugador y enemigo han actuado)."""
        for effect in self.status_effects[:]:
            effect["duration"] -= 1
            if effect["duration"] <= 0:
                console.info(f"✨ El efecto de {effect['name']} ha desaparecido.")
                self.status_effects.remove(effect)
            else:
                # Esto ayuda al jugador a planificar (Estilo Raid/RPG moderno)
                print(console.colorize(
                    f"⏳ {effect['name'].capitalize()} persistirá por {effect['duration']} turnos más.",
                    console.Fore.WHITE
                ))

        for buff in self.active_effects[:]:
            buff.duration -= 1
            if buff.duration <= 0:
                buff.remove(self)  # Llama al método remove de StatBuffPotion
                self.active_effects.remove(buff)

    def apply_status(self, name: str, duration: int, power: int = 0) -> None:
        """Añade un nuevo estado alterado."""
        # Evitamos duplicados, solo refrescamos duración si ya existe
        for effect in self.status_effects:
            if effect["name"] == name:
                effect["duration"] = max(effect["duration"], duration)
                return

        self.status_effects.append({
            "name": name,
            "duration": duration,
            "power": power
        })

    # --- PROGRESIÓN ---

    def gain_experience(self, amount: int) -> None:
        self.experience += amount
        console.info(f"Has obtenido {amount} XP.")
        while self.experience >= self.required_xp():
            self._level_up()

    def required_xp(self) -> int:
        """Fórmula de curva de experiencia escalable."""
        if self.level == 1: return 40
        lv = float(self.level)
        return int(100 * ((lv - 1) ** 0.95) * lv * (lv + 1) / (6 + lv ** 2 / 50))

    def _level_up(self) -> None:
        self.level += 1
        self.just_leveled_up = True

        # Mejora de Stats
        self.stats.max_health += 20
        self.stats.health = self.stats.max_health
        self.stats.min_atk += 2
        self.stats.max_atk += 3
        self.stats.armor += 1

        # La resistencia mágica sube más despacio (cada 2 niveles), mientras
        # no exista equipamiento que la conceda, para no desequilibrar al Mago.
        gained_magic_resist = self.level % 2 == 0
        if gained_magic_resist:
            self.stats.magic_resist += 1

        print(f"\n{console.colorize(f'⭐ ¡HAS SUBIDO AL NIVEL {self.level}! ⭐', console.Fore.YELLOW)}")
        stats_line = "HP Max +20 | Ataque +2-3 | Armadura +1"
        if gained_magic_resist:
            stats_line += " | Resistencia Mágica +1"
        print(console.colorize(stats_line, console.Fore.WHITE))

    def show_stats(self) -> None:
        print(f"\n{console.colorize('=' * 10 + ' ESTADÍSTICAS ' + '=' * 10, console.Fore.CYAN)}")
        print(f"Nombre: {self.name.ljust(15)} Nivel: {self.level}")
        print(f"Vida: {str(self.stats.health).rjust(4)} / {self.stats.max_health}")
        print(f"Ataque: {self.get_attack_range()} | Armadura: {self.get_total_armor()}")
        print(f"Resistencia Mágica: {self.get_total_magic_resist()}")
        print(f"Prob. Crítico: {self.get_total_crit_chance() * 100:.0f}% | "
              f"Daño Crítico: x{self.get_total_crit_damage():.2f}")
        print(f"XP: {self.experience} / {self.required_xp()}")
        if self.equipped_weapon:
            print(f"Arma: {console.colorize(self.equipped_weapon.name, console.Fore.RED)}")

        print(console.colorize("--- Equipamiento ---", console.Fore.CYAN))
        for slot in ARMOR_SLOTS:
            item = self.equipped_armor.get(slot)
            label = console.colorize(item.name, console.Fore.BLUE) if item else "-- vacío --"
            print(f"  {slot_label(slot)}: {label}")

        print(console.colorize("=" * 34, console.Fore.CYAN))
