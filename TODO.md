# Próximas Implementaciones 🚀

## Sistema de Economía (Tienda)
- [x] Crear clase `Shop` con inventario propio.
- [x] Implementar comando `vender` en el menú de la ciudad.
- [x] Lógica para que los ítems tengan un precio de compra y otro de venta.

## Sistema de Forja (Crafting)
- [x] Crear `CraftingRecipe` que pida (Material + Oro).
- [x] **RECETA ESPECIAL:** 1x Piel de Troll + 200 Oro = *Armadura Regenerativa*.
- [x] Añadir submenú "Herrería" en la ciudad.
- [ ] Añadir más recetas (una por material común: Colmillo de Goblin, Fragmento de Hueso, Colmillo de Orco, Esencia Arcana).
- [ ] Dar a la Armadura Regenerativa su efecto de regeneración real por turno (hoy solo es una armadura fuerte en stats; hace falta un mecanismo de "efecto pasivo de equipo" que no existe todavía).

## Mejoras de Combate
- [x] Implementar daño elemental (Fuego vs. Troll).
- [ ] Añadir más elementos (Rayo, Veneno, Hielo) reutilizando `Enemy.ELEMENTAL_WEAKNESSES`.