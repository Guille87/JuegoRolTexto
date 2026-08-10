class ShopItem:
    def __init__(self, item, price):
        self.item = item
        self.price = price

    def __str__(self):
        return f"{self.item.name} - Precio: {self.price}"

    def purchase(self, player):
        if player.gold >= self.price:
            player.gold -= self.price
            player.inventory.append(self.item)
            print(f"Has comprado {self.item.name}.")
        else:
            print("No tienes suficiente oro para comprar este objeto.")


class Shop:
    def __init__(self):
        self.items = []

    def add_item(self, shop_item):
        self.items.append(shop_item)

    def show_items(self):
        print("Objetos en venta:")
        for i, shop_item in enumerate(self.items, start=1):
            print(f"{i}. {shop_item}")

    def buy_item(self, player, choice):
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(self.items):
                selected_item = self.items[choice_index]
                selected_item.purchase(player)
            else:
                print("Opción no válida.")
        except ValueError:
            print("Por favor, introduce un número válido.")
