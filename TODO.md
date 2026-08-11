# Próximas Implementaciones 🚀

## Sistema de Economía (Tienda)
- [x] Crear clase `Shop` con inventario propio.
- [x] Implementar comando `vender` en el menú de la ciudad.
- [x] Lógica para que los ítems tengan un precio de compra y otro de venta.

## Sistema de Forja (Crafting)
- [x] Crear `CraftingRecipe` que pida (Material + Oro).
- [x] **RECETA ESPECIAL:** 1x Piel de Troll + 200 Oro = *Armadura Regenerativa*.
- [x] Añadir submenú "Herrería" en la ciudad.
- [x] Añadir más recetas (una por hueco de armadura nuevo, reutilizando los materiales comunes).
- [ ] Dar a la Armadura Regenerativa su efecto de regeneración real por turno (hoy solo es una armadura fuerte en stats; hace falta un mecanismo de "efecto pasivo de equipo" que no existe todavía).

## Mejoras de Combate
- [x] Implementar daño elemental (Fuego vs. Troll).
- [ ] Añadir más elementos (Rayo, Veneno, Hielo) reutilizando `Enemy.ELEMENTAL_WEAKNESSES`.

## Slots de Equipamiento (estilo Diablo 3)
- [x] 8 huecos de armadura (casco, hombreras, peto, brazales, guantes, cinturón, perneras, botas) además del arma.
- [x] Cada hueco puede dar un tipo de bonus distinto (armadura, vida, resistencia mágica, crítico, elemento).
- [x] Sistema de golpe crítico (probabilidad + multiplicador).
- [x] Recetas de crafteo para llenar los huecos que no tenían ningún objeto todavía.
- [x] 2 huecos de anillo (comparten "tipo" pero son huecos independientes) + amuleto.
- [x] Bonus de daño plano en equipo (no solo en el arma), para los anillos.
- [ ] Objetos de casco/hombreras/peto/cinturón/perneras/anillos/amuleto que sueltan los enemigos por combate (hoy casi todo el contenido nuevo viene del crafteo, no hay drops).
- [ ] Revisar el reparto de bonus de hombreras/cinturón/perneras/amuleto (fueron propuestas propias, no especificadas por el usuario en detalle, así que pueden ajustarse).
- [ ] Solo hay 2 anillos distintos craftables (Fuerza/Precisión) — como llevar dos copias del mismo anillo no es posible (`Inventory.add_item()` auto-vende el duplicado), añadir más variantes de anillo daría más opciones de combinación.