from juego_rol_texto.items.equipment import Armor, Weapon
from juego_rol_texto.items.factory import item_factory
from juego_rol_texto.items.potions.buff_potion import StatBuffPotion
from juego_rol_texto.items.potions.healing_potion import HealingPotion
from juego_rol_texto.items.potions.regen_potion import RegenPotion
from juego_rol_texto.ui import console


class ShopItem:
    """Una entrada del catálogo: una plantilla de ítem y su precio de compra."""
    def __init__(self, template, buy_price: int):
        self.template = template
        self.buy_price = buy_price

    def create_item(self):
        """Crea una copia independiente de la plantilla para entregar al jugador."""
        return item_factory(self.template.to_dict())

    def __str__(self) -> str:
        return f"{self.template.name} - Compra: {self.buy_price} oro | {self.template.description}"


class Shop:
    def __init__(self):
        self.catalog = [
            ShopItem(HealingPotion("Poción de Salud", "Restaura 20 HP", 2, 20), buy_price=5),
            ShopItem(RegenPotion("Poción de Regeneración", "Un brebaje verde que burbujea. Cura 10 HP durante 3 turnos.", 8, 10, 3), buy_price=18),
            ShopItem(StatBuffPotion("Poción de Fuerza", "Aumenta el ataque temporalmente", 5, "max_atk", 5, 3), buy_price=12),
            ShopItem(Weapon("Espada de Hierro", "Una espada bien forjada, superior a las improvisadas", 10, damage=6), buy_price=25),
            ShopItem(Armor("Armadura de Cuero", "Protección ligera pero fiable", 10,
                            slot="peto", defense=4, max_health=10), buy_price=25),
        ]

    def open(self, player) -> None:
        """Punto de entrada del menú interactivo de la tienda."""
        while True:
            print(console.colorize("\n--- TIENDA ---", console.Fore.YELLOW))
            print(f"Oro disponible: {console.colorize(str(player.inventory.gold), console.Fore.YELLOW)}")
            print("1. Comprar")
            print("2. Vender")
            print("3. Volver")

            choice = console.ask("\nSelecciona una opción: ")
            if choice == "1":
                self._buy_menu(player)
            elif choice == "2":
                self._sell_menu(player)
            elif choice == "3":
                break
            else:
                console.error("Opción no válida.")

    def _buy_menu(self, player) -> None:
        if not self.catalog:
            print("No hay objetos en venta.")
            return

        print(console.colorize("\n--- OBJETOS EN VENTA ---", console.Fore.CYAN))
        for idx, shop_item in enumerate(self.catalog, 1):
            print(f"{idx}. {shop_item}")
        print(f"{len(self.catalog) + 1}. Volver")

        choice = console.ask(f"\nElige qué comprar (1-{len(self.catalog) + 1}): ")
        if not choice.isdigit():
            console.error("Entrada no válida.")
            return

        idx = int(choice) - 1
        if idx == len(self.catalog):
            return
        if not (0 <= idx < len(self.catalog)):
            console.error("Opción fuera de rango.")
            return

        shop_item = self.catalog[idx]
        if player.inventory.gold < shop_item.buy_price:
            console.error("No tienes suficiente oro para comprar este objeto.")
            return

        player.inventory.gold -= shop_item.buy_price
        player.inventory.add_item(shop_item.create_item())
        console.success(f"Has comprado {shop_item.template.name}.")

    def _sell_menu(self, player) -> None:
        items = player.inventory.items
        if not items:
            print("No tienes objetos para vender.")
            return

        print(console.colorize("\n--- VENDER OBJETOS ---", console.Fore.CYAN))
        for idx, item in enumerate(items, 1):
            qty = player.inventory.quantities.get(item.name, 1)
            qty_str = f" x{qty}" if qty > 1 else ""
            print(f"{idx}. {item.name}{qty_str} - Venta: {item.value} oro")
        print(f"{len(items) + 1}. Volver")

        choice = console.ask(f"\nElige qué vender (1-{len(items) + 1}): ")
        if not choice.isdigit():
            console.error("Entrada no válida.")
            return

        idx = int(choice) - 1
        if idx == len(items):
            return
        if not (0 <= idx < len(items)):
            console.error("Opción fuera de rango.")
            return

        item = items[idx]
        gold_gained = player.inventory.sell_item(item)
        if gold_gained is not None:
            console.success(f"Has vendido {item.name} por {gold_gained} oro.")
