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

## Nuevos Enemigos (ideas del usuario, sin diseñar todavía)
- [ ] Dragón: salud masiva, ataques poderosos, posible aliento de fuego (daño a lo largo del tiempo) y/o esquiva volando.
- [ ] Demonio: invoca criaturas infernales más débiles como refuerzo, o lanza hechizos oscuros con efectos de estado negativos (maldición, confusión).
- [ ] Gólem de Piedra: defensa casi impenetrable, terremotos o rocas a distancia.
- [ ] Nigromante: resucita/convoca esqueletos o zombis para luchar por él.
- [ ] Ángel Caído: habilidades divinas corruptas — se autosana o inflige juicios divinos de daño masivo.
- [ ] Huargo: lobos veloces que cazan en manada, alta evasión, posible ataque grupal.
- [ ] Bandido: cuerpo a cuerpo + sigilo, puede desarmar temporalmente o dar golpes sorpresa.
- [ ] Espíritu Vengativo: maldiciones o proyectiles espectrales que atraviesan la armadura.
- [ ] Gárgola: resistente pero lenta, embestidas o golpes de garra poderosos.

## Estadísticas Extendidas (jugador y enemigos)
- [ ] Velocidad: determina el orden de turno (mayor velocidad actúa primero).
- [ ] Precisión: probabilidad de acertar un golpe.
- [ ] Evasión: probabilidad de esquivar un ataque enemigo.
- [ ] Crit Chance para enemigos (hoy es solo del jugador — ver `combat/battle.py::_execute_turn`).
- [ ] Crit Damage para enemigos (mismo caso que arriba).
- [ ] Resistencia Mágica para enemigos (el jugador ya la tiene vía `get_total_magic_resist()`).
- [ ] Regeneración de Salud: curación por turno o tras ciertos eventos (más allá del status "regeneración" actual).
- [ ] Iniciativa: quién inicia la batalla.
- [ ] Penetración de Defensa: ignora parte de la defensa/armadura del objetivo.
- Nota: esto implica revisar `Stats`, `Enemy` y el orden de turnos en `combat/battle.py`, que hoy no tiene sistema de velocidad/iniciativa (el jugador siempre actúa primero salvo mecánicas puntuales).