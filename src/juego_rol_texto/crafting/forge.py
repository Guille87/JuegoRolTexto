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
                    value=60, slot="peto", defense=14, max_health=35, regen=8
                )
            ),
            CraftingRecipe(
                name="Guantes de Combate",
                materials={"Colmillo de Goblin": 1, "Colmillo de Orco": 1},
                gold_cost=60,
                result_template=Armor(
                    "Guantes de Combate",
                    "Refuerzos de cuero y colmillos afilados cosidos en los nudillos.",
                    value=15, slot="guantes", crit_chance=0.05, crit_damage=0.15
                )
            ),
            CraftingRecipe(
                name="Brazales Arcanos",
                materials={"Esencia Arcana": 1},
                gold_cost=80,
                result_template=Armor(
                    "Brazales Arcanos",
                    "Energía mágica condensada en forma de brazales; arden con un fuego que no quema al portador.",
                    value=25, slot="brazales", magic_resist=3, element="fuego"
                )
            ),
            CraftingRecipe(
                name="Hombreras Reforzadas",
                materials={"Colmillo de Orco": 1, "Fragmento de Hueso": 1},
                gold_cost=70,
                result_template=Armor(
                    "Hombreras Reforzadas",
                    "Placas de hueso y colmillo unidas con remaches toscos pero efectivos.",
                    value=18, slot="hombreras", defense=2, max_health=15
                )
            ),
            CraftingRecipe(
                name="Cinturón de Resistencia",
                materials={"Fragmento de Hueso": 1},
                gold_cost=40,
                result_template=Armor(
                    "Cinturón de Resistencia",
                    "Tejido con fragmentos óseos que parecen absorber el dolor, tanto físico como arcano.",
                    value=12, slot="cinturon", max_health=15, magic_resist=4
                )
            ),
            CraftingRecipe(
                name="Perneras de Placa",
                materials={"Colmillo de Orco": 1},
                gold_cost=50,
                result_template=Armor(
                    "Perneras de Placa",
                    "Protección rígida para las piernas, forjada con colmillos de orco fundidos.",
                    value=14, slot="perneras", defense=3, max_health=12
                )
            ),
            CraftingRecipe(
                name="Botas Ligeras",
                materials={"Colmillo de Goblin": 1},
                gold_cost=30,
                result_template=Armor(
                    "Botas Ligeras",
                    "Suelas flexibles que facilitan golpear en el punto justo y moverse con más soltura.",
                    value=10, slot="botas", crit_damage=0.10, speed=3
                )
            ),
            CraftingRecipe(
                name="Anillo de Fuerza",
                materials={"Colmillo de Orco": 1, "Fragmento de Hueso": 1},
                gold_cost=55,
                result_template=Armor(
                    "Anillo de Fuerza",
                    "Un aro pesado grabado con runas de poder bruto.",
                    value=16, slot="anillo", damage=3
                )
            ),
            CraftingRecipe(
                name="Anillo de Precisión",
                materials={"Colmillo de Goblin": 1, "Esencia Arcana": 1},
                gold_cost=65,
                result_template=Armor(
                    "Anillo de Precisión",
                    "Un aro fino que agudiza el instinto para encontrar el punto débil.",
                    value=20, slot="anillo", crit_damage=0.12
                )
            ),
            CraftingRecipe(
                name="Amuleto de Resistencia",
                materials={"Esencia Arcana": 1, "Fragmento de Hueso": 1},
                gold_cost=90,
                result_template=Armor(
                    "Amuleto de Resistencia",
                    "Un talismán que envuelve al portador en una tenue barrera contra la magia.",
                    value=28, slot="amuleto", defense=2, magic_resist=5
                )
            ),
            CraftingRecipe(
                name="Anillo de Vitalidad",
                materials={"Fragmento de Hueso": 2},
                gold_cost=45,
                result_template=Armor(
                    "Anillo de Vitalidad",
                    "Un aro sencillo grabado con símbolos de sanación; late al mismo ritmo que el corazón.",
                    value=14, slot="anillo", regen=2
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
