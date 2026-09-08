import random

from juego_rol_texto.characters.base import Character
from juego_rol_texto.characters.classes import CharClass, get_profile
from juego_rol_texto.characters.stats import Stats, apply_mitigation
from juego_rol_texto.inventory.inventory import Inventory
from juego_rol_texto.items.equipment import ARMOR_SLOTS, slot_label
from juego_rol_texto.ui import console


class Player(Character):
    def __init__(self, name: str, stats: Stats, char_class: CharClass | str | None = None):
        super().__init__(name, stats)
        # Clase de personaje (GDD §6.1). Por defecto Vagabundo = el personaje de
        # siempre. Guía los stats de arranque (ui/menus.py), los multiplicadores
        # de crecimiento por nivel y si el ataque estándar es mágico.
        self._class_profile = get_profile(char_class)
        self.level = 1
        self.experience = 0
        # Ids de las habilidades activas equipadas (≤4). Se rellena en v0.10.0-b;
        # aquí solo se persiste para no romper el guardado al añadirlo luego.
        self.equipped_skills: list[str] = []
        self.inventory = Inventory(self)
        self.equipped_weapon = None
        self.equipped_armor = {slot: None for slot in ARMOR_SLOTS}
        self.just_leveled_up = False
        self.in_combat = False
        # Postura defensiva (acción "Defender" en combate): mientras está activa,
        # take_damage() reduce a la mitad el daño recibido. Dura hasta el
        # siguiente turno del jugador, que la limpia en combat/battle.py.
        self.defending = False

        # Sistema de estados alterados: [{"name": "quemado", "duration": 3, "power": 5}, ...]
        self.status_effects = []
        # Sistema de pociones de Stats
        self.active_effects = []
        # Veces que se ha derrotado a cada enemigo (por nombre), no solo la primera
        # vez (a diferencia de defeated_enemies, que solo marca "ya visto"). Usado
        # por el Bestiario.
        self.enemy_kill_counts: dict[str, int] = {}

    # --- LÓGICA DE COMBATE ---

    def take_damage(
        self,
        amount: int,
        is_fire: bool = False,
        is_magical: bool = False,
        armor_penetration: int = 0,
        magic_penetration: int = 0,
    ) -> int:
        """Calcula el daño final tras aplicar armadura o resistencia mágica y lo resta de la vida."""
        if is_magical:
            mitigation = self.get_total_magic_resist() - magic_penetration
        else:
            mitigation = self.get_total_armor() - armor_penetration
        final_damage = apply_mitigation(amount, mitigation)

        # Postura defensiva: el golpe entra a la mitad.
        if self.defending and final_damage > 0:
            final_damage //= 2
            console.info(f"🛡️ Tu postura defensiva reduce el golpe a {final_damage}.")

        self.stats.health -= final_damage

        if is_fire:
            # Si recibimos fuego, buscamos el efecto 'congelado' y lo borramos
            congelado = next((e for e in self.status_effects if e["name"] == "congelado"), None)
            if congelado:
                self.status_effects.remove(congelado)
                console.warning("¡El calor del ataque ha derretido el hielo!")

        return final_damage

    @property
    def char_class(self) -> CharClass:
        return self._class_profile.id

    @char_class.setter
    def char_class(self, value: CharClass | str | None) -> None:
        self._class_profile = get_profile(value)

    def is_magical_attacker(self) -> bool:
        """El ataque estándar es mágico y escala con `poder_magico` (Arcanista)."""
        return self._class_profile.is_magical_attacker

    def get_total_magic_power(self) -> int:
        """Poder mágico total (hoy solo el stat base; ningún equipo lo otorga aún)."""
        return self.stats.magic_power

    def get_magic_attack_range(self) -> tuple[int, int]:
        """Rango de daño del ataque mágico estándar del Arcanista, derivado del
        poder mágico (no del arma). La quemadura —solo física— no lo reduce."""
        power = self.get_total_magic_power()
        return power, power + max(1, power // 3)

    def get_attack_damage(self) -> int:
        """Genera un valor de daño aleatorio basado en el rango actual."""
        if self.is_magical_attacker():
            min_atk, max_atk = self.get_magic_attack_range()
        else:
            min_atk, max_atk = self.get_attack_range()
        return random.randint(min_atk, max_atk)

    def get_attack_range(self) -> tuple[int, int]:
        """Devuelve el rango de ataque sumando el arma y el equipo (p. ej. anillos) equipados."""
        # Desarmado (Bandido): el bonus del arma no cuenta mientras dure el estado.
        is_disarmed = any(e["name"] == "desarmado" for e in self.status_effects)
        weapon_bonus = self.equipped_weapon.damage if self.equipped_weapon and not is_disarmed else 0
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
        total = self.stats.armor + bonus

        # Maldición (Espíritu Vengativo): resta armadura mientras dure el estado.
        curse = next((e for e in self.status_effects if e["name"] == "maldicion"), None)
        if curse:
            total = max(0, total - curse.get("power", 0))

        return total

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

    def get_total_speed(self) -> int:
        """Devuelve la velocidad total sumando todas las piezas equipadas (en la práctica, solo las botas)."""
        bonus = sum(item.speed for item in self.equipped_armor.values() if item)
        return self.stats.speed + bonus

    def get_total_precision(self) -> int:
        """Devuelve la precisión total sumando todas las piezas equipadas (stat base de las hombreras)."""
        bonus = sum(item.precision for item in self.equipped_armor.values() if item)
        return self.stats.precision + bonus

    def get_total_evasion(self) -> int:
        """Devuelve la evasión total sumando todas las piezas equipadas (stat base de las perneras)."""
        bonus = sum(item.evasion for item in self.equipped_armor.values() if item)
        total = self.stats.evasion + bonus

        # Confusión (Demonio): resta evasión mientras dure el estado.
        confusion = next((e for e in self.status_effects if e["name"] == "confusion"), None)
        if confusion:
            total = max(0, total - confusion.get("power", 0))

        return total

    def get_total_armor_penetration(self) -> int:
        """Devuelve la penetración de armadura total (hoy solo el stat base; el equipo no otorga todavía)."""
        return self.stats.armor_penetration

    def get_total_regen(self) -> int:
        """Devuelve la regeneración de salud total sumando todas las piezas equipadas.

        A diferencia del resto de get_total_*, el stat base (Stats.regen) es
        siempre 0 para el jugador: esta stat no sube al subir de nivel, solo
        se consigue vía objetos (típicamente anillos/amuleto).
        """
        bonus = sum(item.regen for item in self.equipped_armor.values() if item)
        return self.stats.regen + bonus

    def get_total_magic_penetration(self) -> int:
        """Devuelve la penetración mágica total (hoy solo el stat base; el equipo no otorga todavía)."""
        return self.stats.magic_penetration

    def get_equipped_element(self) -> str | None:
        """Devuelve el elemento del arma equipada; si no tiene (o estás
        desarmado), el de los brazales."""
        is_disarmed = any(e["name"] == "desarmado" for e in self.status_effects)
        if self.equipped_weapon and self.equipped_weapon.element and not is_disarmed:
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
                # El primer turno tras congelarte pierdes el turno seguro; a
                # partir de ahí hay un 20% por turno de romper el hielo.
                if not effect.get("fresh") and random.random() < 0.20:
                    console.info("¡El hielo se rompe! Te has descongelado.")
                    self.status_effects.remove(effect)
                else:
                    effect["fresh"] = False
                    print(console.colorize("❄️ Estás congelado y no puedes moverte.", console.Fore.BLUE))
                    # Si está congelado, no procesamos parálisis, pero SÍ veneno/quemadura más abajo
                    can_act = False
                    break  # Salimos del check de movimiento, pero seguimos con el daño

            elif effect["name"] == "paralizado":
                # Primer turno seguro; después, 50% por turno.
                if effect.get("fresh") or random.random() < 0.5:
                    console.warning("⚡ ¡La parálisis te impide actuar!")
                    can_act = False
                effect["fresh"] = False

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

        # 3. Regeneración de salud pasiva por equipo (no es un status temporal,
        # se aplica todos los turnos mientras el objeto siga puesto).
        passive_regen = self.get_total_regen()
        if passive_regen > 0 and self.stats.health < self.stats.max_health:
            self.stats.health = min(self.stats.max_health, self.stats.health + passive_regen)
            console.success(f"💚 Tu regeneración te cura {passive_regen} HP.")

        return can_act

    def on_turn_end(self) -> None:
        """Se ejecuta al terminar el turno (jugador y enemigo han actuado)."""
        for effect in self.status_effects[:]:
            effect["duration"] -= 1
            if effect["duration"] <= 0:
                console.info(f"✨ El efecto de {effect['name']} ha desaparecido.")
                self.status_effects.remove(effect)
        # Los turnos restantes de cada estado se ven en las barras de vida
        # (print_status), así no hay que repetir un "persistirá por N turnos".

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

        self.status_effects.append({"name": name, "duration": duration, "power": power, "fresh": True})

    # --- PROGRESIÓN ---

    def gain_experience(self, amount: int) -> None:
        self.experience += amount
        console.info(f"Has obtenido {amount} XP.")
        while self.experience >= self.required_xp():
            self._level_up()

    @staticmethod
    def _required_xp_for_level(level: int) -> int:
        """Umbral de XP acumulada (no un coste que se descuenta, ver
        gain_experience()) para pasar de `level` al siguiente.

        Nivel 1 -> 2 deliberadamente muy barato (8 XP: el mínimo que da
        incluso el primer Goblin, gold_min=4 * 2): la primera victoria del
        juego ya sube de nivel siempre.

        Los niveles 2-9 aplican un "descuento" sobre la curva normal de abajo
        que se va cerrando poco a poco: empieza en ~50% del coste normal en
        el nivel 2 (98.68 * 0.5 ≈ 49, un punto intermedio calculado a
        propósito entre los 8 XP del nivel 1 y los 98 XP que pedía la curva
        original sin suavizar) y llega al 100% en el nivel 10 — subir sigue
        siendo rápido y gratificante justo después de empezar, y se va
        ralentizando de forma gradual hasta la curva de siempre en vez de dar
        un salto brusco de golpe (que es lo que pasaba antes de suavizarlo:
        nivel 1->2 costaba 8 XP y nivel 2->3 ya pedía 375, un frenazo
        demasiado repentino).
        """
        if level == 1:
            return 8

        lv = float(level)
        base_cost = 100 * ((lv - 1) ** 0.95) * lv * (lv + 1) / (6 + lv**2 / 50)
        damping = min(1.0, 0.5 + (lv - 2) * 0.0625)
        return int(base_cost * damping)

    def required_xp(self) -> int:
        """Fórmula de curva de experiencia escalable.

        gain_experience() nunca resetea self.experience (es un umbral
        acumulado, no un coste que se descuenta al subir), así que este valor
        TIENE que ser no decreciente con el nivel — si no, una sola pelea
        pequeña podría subir más de un nivel de golpe. El `max()` con el
        umbral del nivel anterior lo garantiza sin tener que cuadrar a mano
        la fórmula y el descuento para que ya salgan siempre en orden.
        """
        cost = self._required_xp_for_level(self.level)
        if self.level > 1:
            cost = max(cost, self._required_xp_for_level(self.level - 1))
        return cost

    # Ritmo de crecimiento por nivel de cada stat (ganancia media por nivel).
    # Igual que en Pokémon (stat = floor(base + tasa * nivel / 100 + ...)), la
    # cantidad exacta que se gana en un nivel concreto sale de redondear hacia
    # abajo una curva continua, no de un valor fijo ni de una tirada aleatoria:
    # con una tasa fraccionaria (p. ej. 1.5), el resultado alterna +1/+2 de
    # forma determinista, así que la progresión varía de nivel en nivel pero es
    # exactamente la misma en todas las partidas.
    _HEALTH_GROWTH_RATE = 20.0
    _MIN_ATK_GROWTH_RATE = 1.5
    _MAX_ATK_GROWTH_RATE = 2.5
    _ARMOR_GROWTH_RATE = 1.4
    _SPEED_GROWTH_RATE = 1.6
    _PRECISION_GROWTH_RATE = 0.7
    _EVASION_GROWTH_RATE = 0.6

    @staticmethod
    def _growth_gain(rate: float, level: int) -> int:
        """Ganancia determinista para `level` según una tasa continua por nivel."""
        return int(rate * level) - int(rate * (level - 1))

    def _level_up(self) -> None:
        self.level += 1
        self.just_leveled_up = True

        health_gain = self._growth_gain(self._HEALTH_GROWTH_RATE, self.level)
        min_atk_gain = self._growth_gain(self._MIN_ATK_GROWTH_RATE, self.level)
        max_atk_gain = self._growth_gain(self._MAX_ATK_GROWTH_RATE, self.level)
        armor_gain = self._growth_gain(self._ARMOR_GROWTH_RATE * self._class_profile.armor_growth_mult, self.level)
        speed_gain = self._growth_gain(self._SPEED_GROWTH_RATE * self._class_profile.speed_growth_mult, self.level)
        precision_gain = self._growth_gain(self._PRECISION_GROWTH_RATE, self.level)
        evasion_gain = self._growth_gain(self._EVASION_GROWTH_RATE, self.level)

        self.stats.max_health += health_gain
        self.stats.health = self.stats.max_health
        self.stats.min_atk += min_atk_gain
        self.stats.max_atk += max_atk_gain
        self.stats.armor += armor_gain
        self.stats.speed += speed_gain
        self.stats.precision += precision_gain
        self.stats.evasion += evasion_gain

        # La resistencia mágica sube más despacio (cada 2 niveles) y en cantidad
        # fija, mientras no exista equipamiento que la conceda, para no
        # desequilibrar al Mago.
        gained_magic_resist = self.level % 2 == 0
        if gained_magic_resist:
            self.stats.magic_resist += 1

        # Poder mágico: solo crece para la clase que lo usa (Arcanista).
        magic_power_gain = 0
        if self._class_profile.magic_power_growth_rate:
            magic_power_gain = self._growth_gain(self._class_profile.magic_power_growth_rate, self.level)
            self.stats.magic_power += magic_power_gain

        print(f"\n{console.colorize(f'⭐ ¡HAS SUBIDO AL NIVEL {self.level}! ⭐', console.Fore.YELLOW)}")
        stats_line = (
            f"HP Max +{health_gain} | Ataque +{min_atk_gain}-{max_atk_gain} | "
            f"Armadura +{armor_gain} | Velocidad +{speed_gain}"
        )
        if precision_gain:
            stats_line += f" | Precisión +{precision_gain}"
        if evasion_gain:
            stats_line += f" | Evasión +{evasion_gain}"
        if gained_magic_resist:
            stats_line += " | Resistencia Mágica +1"
        if magic_power_gain:
            stats_line += f" | Poder Mágico +{magic_power_gain}"
        print(console.colorize(stats_line, console.Fore.WHITE))

    def show_stats(self) -> None:
        print(f"\n{console.colorize('=' * 10 + ' ESTADÍSTICAS ' + '=' * 10, console.Fore.CYAN)}")
        print(f"Nombre: {self.name.ljust(15)} {console.stat_line(f'Nivel: {self.level}', 'nivel')}")
        print(f"Clase: {console.colorize(self._class_profile.name, console.Fore.MAGENTA)}")
        print(console.stat_line(f"Vida: {str(self.stats.health).rjust(4)} / {self.stats.max_health}", "vida"))
        if self.is_magical_attacker():
            lo, hi = self.get_magic_attack_range()
            print(console.stat_line(f"Ataque mágico: {lo}-{hi}", "ataque"))
        else:
            lo, hi = self.get_attack_range()
            print(console.stat_line(f"Ataque: {lo}-{hi}", "ataque"))
        print(console.stat_line(f"Armadura: {self.get_total_armor()}", "armadura"))
        print(console.stat_line(f"Resistencia Mágica: {self.get_total_magic_resist()}", "magica"))
        if self.is_magical_attacker() or self.get_total_magic_power():
            print(console.stat_line(f"Poder Mágico: {self.get_total_magic_power()}", "magica"))
        print(
            console.stat_line(
                f"Prob. Crítico: {self.get_total_crit_chance() * 100:.0f}% | "
                f"Daño Crítico: x{self.get_total_crit_damage():.2f}",
                "critico",
            )
        )
        print(console.stat_line(f"Velocidad: {self.get_total_speed()}", "velocidad"))
        print(console.stat_line(f"Precisión: {self.get_total_precision()}", "precision"))
        print(console.stat_line(f"Evasión: {self.get_total_evasion()}", "evasion"))
        print(
            console.stat_line(
                f"Penetración de Armadura: {self.get_total_armor_penetration()} | "
                f"Penetración Mágica: {self.get_total_magic_penetration()}",
                "penetracion",
            )
        )
        regen = self.get_total_regen()
        if regen:
            print(console.stat_line(f"Regeneración: {regen} HP/turno", "regen"))
        print(console.stat_line(f"XP: {self.experience} / {self.required_xp()}", "xp"))
        if self.equipped_weapon:
            print(f"Arma: {console.colorize(self.equipped_weapon.name, console.Fore.RED)}")

        print(console.colorize("--- Equipamiento ---", console.Fore.CYAN))
        for slot in ARMOR_SLOTS:
            item = self.equipped_armor.get(slot)
            label = console.colorize(item.name, console.Fore.BLUE) if item else "-- vacío --"
            print(f"  {slot_label(slot)}: {label}")

        print(console.colorize("=" * 34, console.Fore.CYAN))
