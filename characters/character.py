import random

import pygame
from colorama import Fore, Style

from assets.resources.resource_manager import ResourceManager
from game_core.inventory import Inventory
from items.item import Weapon, Armor, Potion


# Carga el recurso manager
resource_manager = ResourceManager()


class Character:
    def __init__(self, name, health, max_health, min_attack, max_attack, defense):
        self.name = name
        self.health = health
        self.max_health = max_health
        self.min_attack = min_attack
        self.max_attack = max_attack
        self.defense = defense
        self.status_effect = None  # Efecto de estado actual
        self.status_duration = 0  # Duración restante del efecto de estado

    def attack_damage(self):
        damage = random.randint(self.min_attack, self.max_attack)
        return damage

    def apply_status_effect(self, status_effect, duration):
        if self.status_effect is None:  # Si el personaje no tiene un efecto de estado
            self.status_effect = status_effect
            self.status_duration = duration
            return True
        else:
            return False  # El personaje ya tiene un efecto de estado activo

    def reduce_status_duration(self):
        if self.status_duration > 0:
            self.status_duration -= 1
            if self.status_duration == 0:  # Si la duración llega a cero, eliminar el efecto de estado
                effect_color = Fore.WHITE  # Por defecto
                if self.status_effect == "quemado":
                    effect_color = Fore.RED
                elif self.status_effect == "paralizado":
                    effect_color = Fore.YELLOW
                elif self.status_effect == "envenenado":
                    effect_color = Fore.GREEN
                elif self.status_effect == "congelado":
                    effect_color = Fore.BLUE
                print(f"El efecto {effect_color}{self.status_effect}{Style.RESET_ALL} se ha disipado.")
                self.status_effect = None


class Player(Character):
    def __init__(self, name, level=1, experience=0, health=100, max_health=100, attack_min=4, attack_max=8, defense=3):
        super().__init__(name, health, max_health, attack_min, attack_max, defense)
        self.name = name
        self.level = level
        self.experience = experience
        self.inventory = Inventory(self)
        self.equipped_weapon = None  # Al principio, el jugador no tiene un arma equipada
        self.equipped_armor = None  # Al principio, el jugador no tiene un arma equipada
        self.active_potions = []  # Lista para mantener un seguimiento de las pociones activas en el jugador

        # Darle un arma al jugador
        weapon_name = "Espada de principiante"
        weapon_description = "Una espada básica para comenzar tu aventura."
        weapon_value = 3  # Valor del arma
        weapon_damage = 2  # Daño del arma
        beginner_weapon = Weapon(weapon_name, weapon_description, weapon_value, weapon_damage)
        self.inventory.add_item(beginner_weapon)
        self.equipped_weapon = beginner_weapon

        # Darle una armadura al jugador
        armor_name = "Escudo de principiante"
        armor_description = "Un escudo básico para comenzar tu aventura."
        armor_value = 2  # Valor de la armadura
        armor_defense = 1  # Defensa de la armadura
        beginner_armor = Armor(armor_name, armor_description, armor_value, armor_defense)
        self.inventory.add_item(beginner_armor)
        self.equipped_armor = beginner_armor

    def gain_experience(self, exp):
        self.experience += exp
        print(f"{Fore.CYAN}{Style.BRIGHT}Has ganado {exp} puntos de experiencia - "
              f"({self.experience}/{self.experience_required_for_next_level()}){Style.RESET_ALL}")

        # Verificar si el jugador sube de nivel
        while self.experience >= self.experience_required_for_next_level():
            self.level_up()

    def level_up(self):
        self.level += 1
        # Aumenta las estadísticas del jugador al subir de nivel
        self.max_health += 10
        self.health = self.max_health
        self.min_attack += 2
        self.max_attack += 2
        self.defense += 1

        print(f"{Fore.MAGENTA}{Style.BRIGHT}Has alcanzado el nivel {self.level}.\n"
              f"Tus estadísticas han aumentado.{Style.RESET_ALL}")
        # Reproduce el sonido de subir de nivel
        resource_manager.play_sound("level_up")
        # Muestra las estadísticas al subir de nivel
        self.show_stats()

    def show_stats(self):
        print(f"{Fore.CYAN}{Style.BRIGHT}Nivel: {self.level}")
        print(f"Experiencia: {self.experience}/{self.experience_required_for_next_level()}")
        print(f"Salud: {self.health}/{self.max_health}")
        print(f"Ataque: {self.min_attack}-{self.max_attack}")
        print(f"Defensa: {self.defense}{Style.RESET_ALL}")
        input(f"Presiona {Fore.GREEN}Enter{Style.RESET_ALL} para continuar...")

    def experience_required_for_next_level(self):
        if self.level == 1:  # Si el jugador está en nivel 1
            return 40  # Se devuelve 40 de experiencia necesaria para subir de nivel
        else:
            lv = float(self.level)
            exp_params = [100, 10, 5, 2]
            basis = float(exp_params[0])
            extra = float(exp_params[1])
            acc_a = float(exp_params[2])
            acc_b = float(exp_params[3])
            experience = (basis * ((lv - 1) ** (0.9 + acc_a / 250)) * lv * (lv + 1) /
                          (6 + lv ** 2 / 50 / acc_b) + (lv - 1) * extra)
            return round(experience)

    def stats(self):
        # Devolver las estadísticas actualizadas como un diccionario
        stats = {
            "level": self.level,
            "experience": self.experience,
            "max_health": self.max_health,
            "health": self.health,
            "min_attack": self.min_attack,
            "max_attack": self.max_attack,
            "defense": self.defense
        }
        return stats

    def apply_potion_effect(self, potion_effect, duration):
        # Agregar la poción activa a la lista de pociones activas
        self.active_potions.append(Potion(potion_effect, None, None, duration=duration))
        # Asignar la duración a la nueva poción
        self.active_potions[-1].turns_remaining = duration
        return True

    def remove_potion_effects(self, potion_name):
        # Restaurar los atributos del jugador afectados por la poción
        if potion_name == "Poción de Resistencia":
            self.defense -= 5
            print(f"El efecto de {Fore.BLUE}{potion_name}{Style.RESET_ALL} ha terminado.")
        if potion_name == "Poción de Fuerza":
            self.min_attack -= 5
            self.max_attack -= 5
            print(f"El efecto de {Fore.LIGHTRED_EX}{potion_name}{Style.RESET_ALL} ha terminado.")
        if potion_name == "Poción de Regeneración":
            print(f"El efecto de {Fore.LIGHTGREEN_EX}{potion_name}{Style.RESET_ALL} ha terminado.")

    def check_duration(self):
        potions_to_remove = []  # Lista para almacenar las pociones que deben eliminarse

        # Iterar sobre las pociones activas y reducir su duración
        for potion in self.active_potions:
            if potion.name == "Poción de Regeneración":
                self.health += 10
                print(f"{Fore.GREEN}Regeneras 10 de salud. Salud actual: {self.health}{Style.RESET_ALL}")
            potion.turns_remaining -= 1  # Reducir la duración de la poción actual
            # Si la duración de una poción llega a cero, eliminarla de la lista de pociones activas
            if potion.turns_remaining == 0:
                potions_to_remove.append(potion)

        # Eliminar las pociones que necesitan ser eliminadas de la lista de pociones activas
        for potion in potions_to_remove:
            self.remove_potion_effects(potion.name)
            self.active_potions.remove(potion)

    def attack_damage(self):
        # Calcula el daño base del jugador
        damage = super().attack_damage()
        # Si el jugador tiene un arma equipada, aumenta el daño con el daño del arma
        if self.equipped_weapon:
            damage += self.equipped_weapon.damage
        return damage

    def take_damage(self, damage):
        total_defense = self.defense  # Defensa base del jugador

        if self.equipped_armor:  # Verifica si el jugador tiene una armadura equipada
            total_defense += self.equipped_armor.defense  # Agrega la defensa de la armadura

        damage_reduction = min(damage, total_defense)  # Calcula la reducción de daño total
        damage -= damage_reduction  # Resta la reducción de daño del daño total recibido
        self.health -= damage  # Aplica el daño restante a la salud del jugador
        return damage

    def equip_weapon_by_index(self, weapon_index):
        if 0 <= weapon_index < len(self.inventory.items):
            item = self.inventory.items[weapon_index]
            if isinstance(item, Weapon):
                self.equipped_weapon = item
                print(f"{Fore.GREEN}¡Te has equipado con {Style.BRIGHT}{item.name}!{Style.RESET_ALL}")
            else:
                print("¡Ese ítem no es un arma!")
        else:
            print("¡Índice de arma inválido!")

    def equip_armor_by_index(self, armor_index):
        if 0 <= armor_index < len(self.inventory.items):
            item = self.inventory.items[armor_index]
            if isinstance(item, Armor):
                self.equipped_armor = item
                print(f"{Fore.GREEN}¡Te has equipado con {Style.BRIGHT}{item.name}!{Style.RESET_ALL}")
            else:
                print("¡Ese ítem no es una armadura!")
        else:
            print("¡Índice de armadura inválido!")

    def show_inventory(self):
        self.inventory.show_inventory()  # Mostrar el inventario del jugador
