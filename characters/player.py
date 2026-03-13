import random
from colorama import Fore, Style
from characters.base import Character
from game_core.inventory import Inventory


class Player(Character):
    def __init__(self, name, stats):
        super().__init__(name, stats)
        self.level = 1
        self.experience = 0
        self.inventory = Inventory(self)
        self.equipped_weapon = None
        self.equipped_armor = None
        self.just_leveled_up = False

        # Sistema de estados alterados: [{"name": "quemado", "duration": 3, "power": 5}, ...]
        self.status_effects = []
        # Sistema de pociones de Stats
        self.active_effects = []

    # --- LÓGICA DE COMBATE ---

    def take_damage(self, amount, is_fire=False):
        """Calcula el daño final tras aplicar defensa y lo resta de la vida."""
        final_damage = max(0, amount - self.get_total_defense())
        self.stats.health -= final_damage

        if is_fire:
            # Si recibimos fuego, buscamos el efecto 'congelado' y lo borramos
            congelado = next((e for e in self.status_effects if e["name"] == "congelado"), None)
            if congelado:
                self.status_effects.remove(congelado)
                print(f"{Fore.YELLOW}¡El calor del ataque ha derretido el hielo!{Style.RESET_ALL}")

        return final_damage

    def get_attack_damage(self):
        """Genera un valor de daño aleatorio basado en el rango actual."""
        min_atk, max_atk = self.get_attack_range()
        return random.randint(min_atk, max_atk)

    def get_attack_range(self):
        """Devuelve el rango de ataque sumando el arma equipada."""
        bonus = self.equipped_weapon.damage if self.equipped_weapon else 0
        min_atk = self.stats.min_atk + bonus
        max_atk = self.stats.max_atk + bonus

        # Penalización por Quemadura: Ataque a la mitad
        if any(e["name"] == "quemado" for e in self.status_effects):
            min_atk //= 2
            max_atk //= 2

        return min_atk, max_atk

    def get_total_defense(self):
        """Devuelve la defensa total sumando la armadura."""
        bonus = self.equipped_armor.defense if self.equipped_armor else 0
        return self.stats.defense + bonus

    def is_alive(self):
        return self.stats.health > 0

    # --- GESTIÓN DE TURNOS Y ESTADOS ---

    def on_turn_start(self):
        """Procesa los estados alterados al inicio del turno."""
        can_act = True
        # 1. Comprobación de estados que bloquean el turno
        for effect in self.status_effects[:]:
            if effect["name"] == "congelado":
                if random.random() < 0.20:
                    print(f"{Fore.CYAN}¡El hielo se rompe! Te has descongelado.{Style.RESET_ALL}")
                    self.status_effects.remove(effect)
                else:
                    print(f"{Fore.BLUE}❄️ Estás congelado y no puedes moverte.{Style.RESET_ALL}")
                    # Si está congelado, no procesamos parálisis, pero SÍ veneno/quemadura más abajo
                    can_act = False
                    break  # Salimos del check de movimiento, pero seguimos con el daño

            elif effect["name"] == "paralizado":
                if random.random() < 0.5:
                    print(f"{Fore.YELLOW}⚡ ¡La parálisis te impide actuar!{Style.RESET_ALL}")
                    can_act = False

        # 2. Procesamiento de daño/curación (Ocurre aunque no puedas actuar)
        for effect in self.status_effects[:]:
            if effect["name"] == "quemado":
                dmg = max(1, self.stats.max_health // 16)
                self.stats.health -= dmg
                print(f"{Fore.RED}🔥 La quemadura te quita {dmg} HP.{Style.RESET_ALL}")

            elif effect["name"] == "veneno":
                dmg = max(1, self.stats.max_health // 8)
                self.stats.health -= dmg
                print(f"{Fore.GREEN}☣️ El veneno te quita {dmg} HP.{Style.RESET_ALL}")

            elif effect["name"] == "regeneración":
                heal = effect.get("power", 0)
                self.stats.health = min(self.stats.max_health, self.stats.health + heal)
                print(f"{Fore.GREEN}❤️ La regeneración te cura {heal} HP.{Style.RESET_ALL}")

        return can_act

    def on_turn_end(self):
        """Se ejecuta al terminar el turno (jugador y enemigo han actuado)."""
        for effect in self.status_effects[:]:
            effect["duration"] -= 1
            if effect["duration"] <= 0:
                print(f"{Fore.CYAN}✨ El efecto de {effect['name']} ha desaparecido.{Style.RESET_ALL}")
                self.status_effects.remove(effect)
            else:
                # Esto ayuda al jugador a planificar (Estilo Raid/RPG moderno)
                print(f"{Fore.WHITE}⏳ {effect['name'].capitalize()} persistirá por {effect['duration']} turnos más.{Style.RESET_ALL}")

        for buff in self.active_effects[:]:
            buff.duration -= 1
            if buff.duration <= 0:
                buff.remove(self)  # Llama al método remove de StatBuffPotion
                self.active_effects.remove(buff)

    def apply_status(self, name, duration, power=0):
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

    def gain_experience(self, amount):
        self.experience += amount
        print(f"{Fore.CYAN}Has obtenido {amount} XP.{Style.RESET_ALL}")
        while self.experience >= self.required_xp():
            self._level_up()

    def required_xp(self):
        """Fórmula de curva de experiencia escalable."""
        if self.level == 1: return 40
        lv = float(self.level)
        return int(100 * ((lv - 1) ** 0.95) * lv * (lv + 1) / (6 + lv ** 2 / 50))

    def _level_up(self):
        self.level += 1
        self.just_leveled_up = True

        # Mejora de Stats
        self.stats.max_health += 20
        self.stats.health = self.stats.max_health
        self.stats.min_atk += 2
        self.stats.max_atk += 3
        self.stats.defense += 1
        print(f"\n{Fore.YELLOW}⭐ ¡HAS SUBIDO AL NIVEL {self.level}! ⭐")
        print(f"{Fore.WHITE}HP Max +20 | Ataque +2 | Defensa +1{Style.RESET_ALL}")

    def show_stats(self):
        print(f"\n{Fore.CYAN}{'=' * 10} ESTADÍSTICAS {'=' * 10}{Style.RESET_ALL}")
        print(f"Nombre: {self.name.ljust(15)} Nivel: {self.level}")
        print(f"Vida: {str(self.stats.health).rjust(4)} / {self.stats.max_health}")
        print(f"Ataque: {self.get_attack_range()} | Defensa: {self.get_total_defense()}")
        print(f"XP: {self.experience} / {self.required_xp()}")
        if self.equipped_weapon:
            print(f"Arma: {Fore.RED}{self.equipped_weapon.name}{Style.RESET_ALL}")
        if self.equipped_armor:
            print(f"Armadura: {Fore.BLUE}{self.equipped_armor.name}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 34}{Style.RESET_ALL}")