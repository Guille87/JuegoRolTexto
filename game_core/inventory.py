from colorama import Fore, Style

from items.item import Weapon, Potion, Armor


class Inventory:
    def __init__(self, player):
        self.items = []
        self.gold = 0
        self.player = player  # Guarda una referencia al objeto Player
        self.item_mapping = {}

    def add_item(self, item):
        # Verificar si el objeto es una poción
        if isinstance(item, Potion):
            # Si es una poción, simplemente la añadimos al inventario
            self.items.append(item)
            print(f"{Fore.GREEN}{Style.BRIGHT}Has obtenido: {item.name}.{Style.RESET_ALL}")
        else:
            # Busca si ya hay un objeto del mismo nombre en el inventario
            same_name_item = next((i for i in self.items if i.name == item.name), None)
            if same_name_item:
                # Si el objeto ya está en el inventario, se añade el valor del objeto al oro del jugador
                self.gold += item.value
                print(f"{Fore.GREEN}{Style.BRIGHT}¡Ya tienes {item.name}! "
                      f"{Fore.YELLOW}{Style.BRIGHT}Se ha convertido en {item.value} de oro.{Style.RESET_ALL}")
            else:
                # Si el objeto no está en el inventario, se añade al inventario
                self.items.append(item)
                if item.name not in ["Espada de principiante", "Escudo de principiante"]:
                    # Si el objeto no es la espada ni el escudo principiante, muestra el mensaje
                    print(f"{Fore.GREEN}{Style.BRIGHT}Has obtenido: {item.name}.{Style.RESET_ALL}")

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
        else:
            print("El objeto no está en el inventario.")

    def add_gold(self, amount):
        self.gold += amount
        print(f"{Fore.YELLOW}{Style.BRIGHT}Has conseguido {amount} de oro.{Style.RESET_ALL}")

    def remove_gold(self, amount):
        if self.gold >= amount:
            self.gold -= amount
        else:
            print("No tienes suficiente oro.")

    def sort_inventory(self):
        # Definir una función de clave personalizada para ordenar los elementos del inventario
        def custom_sort_key(item):
            if isinstance(item, Weapon):
                return 0, item.name  # Ordenar armas primero por nombre
            elif isinstance(item, Armor):
                return 1, item.name  # Luego ordenar armaduras por nombre
            else:
                return 2, item.name  # Por último, ordenar otros objetos por nombre

        # Ordenar los elementos del inventario utilizando la función de clave personalizada
        self.items.sort(key=custom_sort_key)

    def show_inventory(self):
        print("=" * 60)
        if self.items:
            print("Inventario del jugador:")
            self.sort_inventory()
            current_category = None
            item_number = 1  # Inicializamos el número del objeto

            # Utilizaremos este diccionario para rastrear la cantidad de cada tipo de objeto
            item_count = {}

            for item in self.items:
                # Actualizamos el contador para el tipo de objeto actual
                item_count[item.name] = item_count.get(item.name, 0) + 1

                # Si este es el primer elemento de su tipo, mostramos su información
                if item_count[item.name] == 1:
                    # Imprimir el título de la categoría si es diferente al anterior
                    if isinstance(item, Weapon):
                        category = "Armas"
                    elif isinstance(item, Armor):
                        category = "Armaduras"
                    else:
                        category = "Objetos"
                    if category != current_category:
                        print(f"\n== {category} ==")
                        current_category = category

                    # Etiqueta (E) para objetos equipados
                    equipped_label = "(E)" if item.name == self.player.equipped_weapon.name or item.name == self.player.equipped_armor.name else ""

                    # Calcular la cantidad total de este tipo de objeto
                    total_count = sum(1 for i in self.items if i.name == item.name)

                    # Imprimir el objeto con su cantidad
                    if isinstance(item, Potion):
                        effect_description = self.get_potion_effect_description(item)
                        print(f"  {item_number}. {Style.BRIGHT}{equipped_label} {item.name}{Style.RESET_ALL}: {item.description} | "
                              f"{Fore.YELLOW}{Style.BRIGHT}Valor: {item.value}{Style.RESET_ALL} | {Fore.GREEN}{Style.BRIGHT}{effect_description} "
                              f"{Style.RESET_ALL} | Cantidad: {total_count}")
                    elif isinstance(item, Weapon):
                        print(f"  {item_number}. {Style.BRIGHT}{equipped_label} {item.name}{Style.RESET_ALL}: {item.description} | "
                              f"{Fore.YELLOW}{Style.BRIGHT}Valor: {item.value}{Style.RESET_ALL} | {Fore.GREEN}{Style.BRIGHT}Daño: {item.damage}"
                              f"{Style.RESET_ALL} | Cantidad: {total_count}")
                    elif isinstance(item, Armor):
                        print(f"  {item_number}. {Style.BRIGHT}{equipped_label} {item.name}{Style.RESET_ALL}: {item.description} | "
                              f"{Fore.YELLOW}{Style.BRIGHT}Valor: {item.value}{Style.RESET_ALL} | {Fore.GREEN}{Style.BRIGHT}Defensa: {item.defense}"
                              f"{Style.RESET_ALL} | Cantidad: {total_count}")
                    else:
                        print(f"  {item_number}. {Style.BRIGHT}{item.name}{Style.RESET_ALL}: {item.description} | "
                              f"{Fore.YELLOW}{Style.BRIGHT}Valor: {item.value}{Style.RESET_ALL} | Cantidad: {total_count}")

                    # Guardamos el mapeo entre el número de objeto y el índice real del objeto en la lista
                    self.item_mapping[item_number] = item
                    item_number += 1  # Incrementamos el número de objeto para la siguiente iteración
        else:
            print("No tienes objetos 😓")
        # Imprimir la cantidad de oro del jugador
        print(f"\n== Oro ==")
        print(f"  - {Fore.YELLOW}{Style.BRIGHT}Oro: {self.gold}{Style.RESET_ALL}")

    def select_item_from_inventory(self):
        # Pedir al jugador que seleccione un número de objeto
        item_number = input("Selecciona el número del objeto que deseas usar (0 para cancelar): ")
        try:
            item_number = int(item_number)
            # Obtener el objeto asociado al número de objeto seleccionado
            selected_item = self.item_mapping.get(item_number)
            if selected_item:
                return selected_item
            else:
                print("Número de objeto inválido.")
                return None
        except ValueError:
            print("¡Ingresa un número válido!")
            return None

    def get_potion_effect_description(self, potion):
        if potion.name == "Poción de Salud":
            return f"Cantidad de Curación: {potion.healing_amount}"
        elif potion.name == "Poción de Resistencia":
            return f"Aumento de Defensa: {potion.defense_boost}"
        elif potion.name == "Poción de Fuerza":
            return f"Aumento de Daño: {potion.damage_boost}"
        elif potion.name == "Poción de Regeneración":
            return f"Regeneración por Turno: {potion.regeneration_amount}"
        else:
            return "Efecto Desconocido"
