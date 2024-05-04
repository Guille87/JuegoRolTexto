import random

from colorama import Fore, Style

from items.item import Potion, Weapon, Armor


class Enemy:
    def __init__(self, name, health, max_health, min_attack, max_attack, defense, gold):
        self.name = name
        self.health = health
        self.max_health = max_health
        self.min_attack = min_attack
        self.max_attack = max_attack
        self.defense = defense
        self.gold = gold

    def attack_damage_enemy(self):
        damage = random.randint(self.min_attack, self.max_attack)
        return damage

    def drop_gold(self):
        return self.gold


class Goblin(Enemy):
    def __init__(self, name):
        super().__init__(name, health=40, max_health=40, min_attack=8, max_attack=12, defense=2, gold=5)

    def ambush_probability(self):
        return random.random() <= 0.5  # Probabilidad del 50% de emboscada

    def apply_ambush(self, player):
        ambush_damage = random.randint(self.min_attack + 5, self.max_attack + 5)  # Aumenta el daño del ataque
        damage_taken = player.take_damage(ambush_damage)
        print(f"{Fore.RED}{self.name}{Style.RESET_ALL} realiza una {Fore.YELLOW}emboscada{Style.RESET_ALL} y hace "
              f"{Fore.RED}{damage_taken}{Style.RESET_ALL} de daño a {Fore.GREEN}{player.name}{Style.RESET_ALL}!")
        # player.health = max(0, player.health - damage_taken)  # Aplica el daño al jugador

    def drop_item(self):
        dropped_items = []

        # Probabilidad del 20% para soltar un objeto
        if random.random() <= 0.2:
            # Crear una espada
            weapon_name = "Espada Goblin"
            weapon_description = "Una espada básica utilizada por los Goblins."
            weapon_value = 5  # El valor del arma
            weapon_damage = 4  # El daño del arma
            goblin_sword = Weapon(weapon_name, weapon_description, weapon_value, weapon_damage)
            dropped_items.append(goblin_sword)

        # Probabilidad del 70% para soltar una poción de salud
        if random.random() <= 0.7:
            # Crear una poción
            item_name = "Poción de Salud"
            item_description = "Restaura una pequeña cantidad de salud."
            item_value = 2  # El valor de la poción
            healing_amount = 20  # La cantidad de salud restaurada
            healing_potion = Potion(item_name, item_description, item_value, healing_amount)
            dropped_items.append(healing_potion)

        return dropped_items


class Skeleton(Enemy):
    def __init__(self, name):
        super().__init__(name, health=60, max_health=60, min_attack=10, max_attack=14, defense=3, gold=10)
        self.defeated_once = False  # Atributo para rastrear si el esqueleto ha sido derrotado al menos una vez

    def drop_item(self):
        dropped_items = []

        # Probabilidad del 20% para soltar un objeto
        if random.random() <= 0.2:
            # Crear un hueso afilado
            weapon_name = "Hueso Afilado"
            weapon_description = "Un hueso afilado que puede usarse como arma cuerpo a cuerpo."
            weapon_value = 8  # El valor del arma
            weapon_damage = 6  # El daño del arma
            sharp_bone = Weapon(weapon_name, weapon_description, weapon_value, weapon_damage)
            dropped_items.append(sharp_bone)

        # Probabilidad del 20% para soltar un objeto
        if random.random() <= 0.2:
            # Crear un escudo de hueso
            shield_name = "Escudo de Hueso"
            shield_description = "Un escudo hecho de huesos de otros aventureros caídos."
            shield_value = 8  # El valor del escudo
            shield_defense = 5  # La defensa proporcionada por el escudo
            bone_shield = Armor(shield_name, shield_description, shield_value, shield_defense)
            dropped_items.append(bone_shield)

        # Probabilidad del 70% para soltar una poción de resistencia
        if random.random() <= 0.7:
            # Crear una poción de resistencia
            potion_name = "Poción de Resistencia"
            potion_description = "Aumenta temporalmente la defensa."
            potion_value = 3  # El valor de la poción
            defense_bonus = 5  # El bono de defensa proporcionado por la poción
            defense_potion = Potion(potion_name, potion_description, potion_value, defense_boost=defense_bonus)
            dropped_items.append(defense_potion)

        return dropped_items


class Orc(Enemy):
    fury_turns = 3  # Número de turnos después de recibir daño para activar la Furia

    def __init__(self, name):
        super().__init__(name, health=150, max_health=150, min_attack=15, max_attack=20, defense=6, gold=25)
        self.damage_received_turns = 0  # Contador de turnos después de recibir daño

    def drop_item(self):
        dropped_items = []

        # Probabilidad del 20% para soltar un objeto
        if random.random() <= 0.2:
            # Crear un hacha de Batalla
            weapon_name = "Hacha de Batalla"
            weapon_description = "Un arma pesada y contundente utilizada por los Orcos."
            weapon_value = 15  # El valor del arma
            weapon_damage = 12  # El daño del arma
            orc_axe = Weapon(weapon_name, weapon_description, weapon_value, weapon_damage)
            dropped_items.append(orc_axe)

        # Probabilidad del 70% para soltar una poción de fuerza
        if random.random() <= 0.7:
            # Crear una poción de fuerza
            potion_name = "Poción de Fuerza"
            potion_description = "Aumenta temporalmente el daño."
            potion_value = 5  # El valor de la poción
            damage_bonus = 5  # El bono de daño proporcionado por la poción
            strength_potion = Potion(potion_name, potion_description, potion_value, damage_boost=damage_bonus)
            dropped_items.append(strength_potion)

        return dropped_items

    # Método para incrementar el contador de turnos antes de activar la Furia
    def increase_fury_turns(self):
        if not self.is_in_fury():  # Verifica si la Furia no está activa
            self.damage_received_turns += 1
            if self.damage_received_turns == Orc.fury_turns:
                self.activate_fury()  # Activar la Furia después de 3 turnos

    # Método para incrementar el contador de turnos antes de desactivar la Furia
    def increment_fury_turns_for_deactivation(self):
        if self.is_in_fury():
            self.damage_received_turns += 1
            if self.damage_received_turns == Orc.fury_turns:
                self.deactivate_fury()  # Desactiva la Furia

    # Método para activar la habilidad Furia
    def activate_fury(self):
        print(f"{Fore.RED}{self.name}{Style.RESET_ALL} entra en estado de {Fore.RED}Furia{Style.RESET_ALL}, su ataque se duplica.")
        print("============================================================")
        self.min_attack *= 2
        self.max_attack *= 2
        self.damage_received_turns = 0  # Reiniciar el contador después de activar la Furia

    # Método para desactivar la habilidad Furia
    def deactivate_fury(self):
        print(f"{Fore.RED}{self.name}{Style.RESET_ALL} sale del estado de {Fore.RED}Furia{Style.RESET_ALL}, su ataque vuelve a la normalidad.")
        print("============================================================")
        self.min_attack //= 2
        self.max_attack //= 2
        self.damage_received_turns = 0  # Reiniciar el contador después de activar la Furia

    # Método para verificar si el Orco está en estado de Furia
    def is_in_fury(self):
        return self.min_attack > 15  # Si el ataque mínimo es mayor a 15, el Orco está en Furia


class Troll(Enemy):
    max_health = 200  # Variable de clase para la salud máxima del Troll

    def __init__(self, name):
        super().__init__(name, health=200, max_health=Troll.max_health, min_attack=12, max_attack=18, defense=8, gold=50)

    def drop_item(self):
        dropped_items = []

        # Probabilidad del 20% para soltar un objeto
        if random.random() <= 0.2:
            # Crear una piedra encantada
            weapon_name = "Maza de Piedra"
            weapon_description = "Un arma primitiva pero efectiva utilizada por los Troles."
            weapon_value = 20  # El valor del arma
            weapon_damage = 15  # El daño del arma
            enchanted_stone = Weapon(weapon_name, weapon_description, weapon_value, weapon_damage)
            dropped_items.append(enchanted_stone)

        # Probabilidad del 70% para soltar una poción de regeneración
        if random.random() <= 0.7:
            # Crear una poción de regeneración
            potion_name = "Poción de Regeneración"
            potion_description = "Restaura gradualmente la salud durante varios turnos."
            potion_value = 8  # El valor de la poción
            regeneration_amount = 10  # La cantidad de salud regenerada por turno
            regeneration_potion = Potion(potion_name, potion_description, potion_value, regeneration_amount=regeneration_amount)
            dropped_items.append(regeneration_potion)

        return dropped_items

    def regenerate_health(self):
        return random.randint(5, 15)  # Cantidad de salud regenerada


class Mago(Enemy):
    max_health = 400

    def __init__(self, name):
        super().__init__(name, health=400, max_health=Mago.max_health, min_attack=10, max_attack=15, defense=6, gold=100)

    def drop_item(self):
        dropped_items = []

        # Probabilidad del 20% para soltar un objeto
        if random.random() <= 0.2:
            # Crear una capa de Éter
            armor_name = "Capa de Éter"
            armor_description = "Una capa mágica que otorga protección adicional contra ataques mágicos."
            armor_value = 30  # El valor de la armadura
            armor_defense = 5  # La defensa adicional proporcionada por la armadura
            ether_cape = Armor(armor_name, armor_description, armor_value, armor_defense)
            dropped_items.append(ether_cape)

        return dropped_items

    def cast_spell(self):
        # Elige aleatoriamente entre lanzar un hechizo de daño o utilizar magia curativa
        return random.choice(["Bola de fuego"])
        # return random.choice(["Bola de fuego", "Rayo", "Veneno", "Ventisca", "Curación"])

    def spell_damage(self, spell_type):
        # Implementación de los daños para cada tipo de hechizo
        if spell_type == "Bola de fuego":
            # Hay un 30% de probabilidad de que queme al jugador
            burn_chance = random.random() <= 0.3
            if burn_chance:
                return random.randint(15, 25), "quemado"
            else:
                return random.randint(15, 25), None
        elif spell_type == "Rayo":
            # Hay un 30% de probabilidad de que paralice al jugador
            paralysis_chance = random.random() <= 0.3
            if paralysis_chance:
                return random.randint(10, 30), "paralizado"
            else:
                return random.randint(10, 30), None
        elif spell_type == "Veneno":
            # Hay un 30% de probabilidad de que envenene al jugador
            poison_chance = random.random() <= 0.3
            if poison_chance:
                return random.randint(10, 15), "envenenado"
            else:
                return random.randint(10, 15), None
        elif spell_type == "Ventisca":
            # Hay un 10% de probabilidad de que congele al jugador
            freeze_chance = random.random() <= 0.1
            if freeze_chance:
                return random.randint(5, 15), "congelado"
            else:
                return random.randint(5, 15), None
        elif spell_type == "Curación":
            return random.randint(15, 25), None

    def cast_heal(self):
        # Implementación básica de magia curativa
        return random.randint(15, 25)  # Cantidad aleatoria de curación entre 15 y 25
