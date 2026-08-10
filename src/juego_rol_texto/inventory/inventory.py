from juego_rol_texto.items.equipment import Weapon, Armor
from juego_rol_texto.items.potions.potion_base import Potion
from juego_rol_texto.ui import console


class Inventory:
    def __init__(self, player):
        self.items = []  # Lista de objetos únicos
        self.quantities = {}  # { "Poción de Salud": 5 }
        self.gold = 0
        self.player = player  # Guarda una referencia al objeto Player
        self.item_mapping = {}

    def add_item(self, item) -> None:
        """Añade un ítem gestionando stacks para consumibles y oro para equipo repetido."""
        # Si es equipo (Arma/Armadura), comprobamos si ya existe por nombre
        if isinstance(item, (Weapon, Armor)):
            existing = next((i for i in self.items if i.name == item.name), None)
            if existing:
                self.gold += item.value
                console.warning(f"¡Repetido! Has vendido el {item.name} por {item.value} de oro.")
                return

        # Lógica de Stacking
        if item.name in self.quantities:
            self.quantities[item.name] += 1
        else:
            self.items.append(item)
            self.quantities[item.name] = 1

        console.success(f"Obtenido: {item.name}")

    def load_items(self, items_list: list) -> None:
        """Limpia y carga una lista de objetos reconstruyendo el stacking."""
        self.items = []
        self.quantities = {}
        for item in items_list:
            # Usamos la misma lógica que add_item pero sin prints
            if item.name in self.quantities:
                self.quantities[item.name] += 1
            else:
                self.items.append(item)
                self.quantities[item.name] = 1

    def show_inventory(self, filter_class=None, mode: str = "view") -> bool:
        """
        mode "view": Solo lectura
        mode "use": Permite seleccionar número para usar
        """
        print("\n" + "=" * 45)
        title = "INVENTARIO COMPLETO"
        if filter_class == Weapon: title = "SELECCIONAR ARMA"
        elif filter_class == Armor: title = "SELECCIONAR ARMADURA"

        print(console.colorize(f"--- {title} ---", console.Fore.CYAN))

        items_to_show = [i for i in self.items if not filter_class or isinstance(i, filter_class)]

        if not items_to_show:
            print("No hay objetos en esta categoría.")
            print("=" * 45)
            return False

        self.item_mapping = {}
        for idx, item in enumerate(items_to_show, 1):
            self.item_mapping[idx] = item
            qty = self.quantities.get(item.name, 1)

            # Formato de línea
            is_eq = f"{console.colorize('(E)', console.Fore.BLUE)} " if (item == self.player.equipped_weapon or item == self.player.equipped_armor) else ""
            qty_str = console.colorize(f" x{qty}", console.Fore.YELLOW) if qty > 1 else ""

            print(f"{idx}. {is_eq}{item.name}{qty_str} | {item.description}")
            print(f"   [{item.get_stats_info()}]")

        print(f"\n{console.colorize(f'Oro: {self.gold}', console.Fore.YELLOW)}")
        print("=" * 45)

        if mode == "use":
            return self._handle_selection(filter_class=filter_class)
        return False

    def _handle_selection(self, filter_class=None) -> bool:
        choice = console.ask("\nSelecciona un número (0 para volver): ")
        if choice == "0" or not choice.isdigit(): return False

        idx = int(choice)
        item = self.item_mapping.get(idx)

        if item:
            # 1. Caso: Inventario General (filter_class es None)
            if filter_class is None:
                if not isinstance(item, Potion):
                    console.error("Las armas y armaduras se equipan desde sus respectivos menús.")
                    return False

                # 2. Caso: Menú de Equipo específico (filter_class tiene valor)
            else:
                if not isinstance(item, filter_class):
                    console.error("No puedes equipar eso aquí.")
                    return False

            # Si pasa las validaciones, usamos el objeto
            success = item.use(self.player)
            if success:
                # Si es un consumible (Poción), restamos cantidad
                if not isinstance(item, (Weapon, Armor)):
                    self.quantities[item.name] -= 1
                    if self.quantities[item.name] <= 0:
                        self.items.remove(item)
                        del self.quantities[item.name]
                return True
            else:
                # Si success es False, devolvemos False para no cerrar el menú ni gastar turno
                return False
        return False

    def equip_menu(self, filter_class=None) -> bool:
        """Llamado desde las opciones 5 y 6 del menú principal."""
        return self.show_inventory(filter_class=filter_class, mode="use")

    def load_saved_inventory(self, items_list: list, quantities_dict: dict) -> None:
        """Sincroniza la lista de items con sus cantidades reales al cargar."""
        self.items = items_list
        self.quantities = quantities_dict
