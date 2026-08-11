from juego_rol_texto.items.equipment import Armor
from juego_rol_texto.items.factory import item_factory
from juego_rol_texto.ui import console


class CraftingRecipe:
    """Una receta: materiales + oro requeridos, y una plantilla del objeto resultante."""
    def __init__(self, name: str, materials: dict, gold_cost: int, result_template):
        self.name = name
        self.materials = materials  # {"Piel de Troll": 1}
        self.gold_cost = gold_cost
        self.result_template = result_template

    def create_result(self):
        """Crea una copia independiente de la plantilla para entregar al jugador."""
        return item_factory(self.result_template.to_dict())

    def can_craft(self, player) -> bool:
        if player.inventory.gold < self.gold_cost:
            return False
        return all(player.inventory.has_item(mat, qty) for mat, qty in self.materials.items())

    def missing_requirements(self, player) -> list:
        """Lista en texto lo que le falta al jugador para poder craftear esta receta."""
        missing = []
        if player.inventory.gold < self.gold_cost:
            missing.append(f"oro (tienes {player.inventory.gold}, hacen falta {self.gold_cost})")
        for mat, qty in self.materials.items():
            have = player.inventory.quantities.get(mat, 0)
            if have < qty:
                missing.append(f"{mat} (tienes {have}, hacen falta {qty})")
        return missing

    def __str__(self) -> str:
        materials_str = ", ".join(f"{name} x{qty}" for name, qty in self.materials.items())
        return (f"{self.name} | Requiere: {materials_str} + {self.gold_cost} oro "
                f"| [{self.result_template.get_stats_info()}]")


class Forge:
    def __init__(self):
        self.recipes = [
            CraftingRecipe(
                name="Armadura Regenerativa",
                materials={"Piel de Troll": 1},
                gold_cost=200,
                result_template=Armor(
                    "Armadura Regenerativa",
                    "Forjada con la piel imperecedera de un Troll; aún parece palpitar con vida propia.",
                    value=60, defense=14
                )
            ),
        ]

    def open(self, player) -> None:
        """Punto de entrada del menú interactivo de la herrería."""
        while True:
            print(console.colorize("\n--- HERRERÍA ---", console.Fore.YELLOW))
            print(f"Oro disponible: {console.colorize(str(player.inventory.gold), console.Fore.YELLOW)}")

            if not self.recipes:
                print("No hay recetas disponibles todavía.")
                return

            for idx, recipe in enumerate(self.recipes, 1):
                print(f"{idx}. {recipe}")
            print(f"{len(self.recipes) + 1}. Volver")

            choice = console.ask(f"\nElige qué craftear (1-{len(self.recipes) + 1}): ")
            if not choice.isdigit():
                console.error("Entrada no válida.")
                continue

            idx = int(choice) - 1
            if idx == len(self.recipes):
                return
            if not (0 <= idx < len(self.recipes)):
                console.error("Opción fuera de rango.")
                continue

            self._craft(player, self.recipes[idx])

    def _craft(self, player, recipe: CraftingRecipe) -> None:
        if not recipe.can_craft(player):
            console.error("Te falta lo siguiente: " + ", ".join(recipe.missing_requirements(player)))
            return

        player.inventory.gold -= recipe.gold_cost
        for mat, qty in recipe.materials.items():
            player.inventory.consume_item(mat, qty)

        player.inventory.add_item(recipe.create_result())
        console.success(f"¡Has forjado {recipe.name}!")
