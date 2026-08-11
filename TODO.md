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
- [x] Velocidad + sistema de turnos ATB (barra de "gauge" estilo Final Fantasy X, no una simple alternancia 1 a 1): `Stats.speed`, `Player.get_total_speed()`, y `combat/battle.py` acumula un gauge por combatiente (`ATB_THRESHOLD`) que se llena a un ritmo proporcional a la velocidad, permitiendo que el más rápido actúe varias veces antes de que el más lento tenga su primer turno. Iniciativa se fusionó con Velocidad (no tiene sentido como stat separada en un combate 1 vs 1; revisar si hace falta separarla el día que haya combates con varios enemigos).
- [x] Huir ahora depende de la velocidad relativa (`_attempt_flee`, fórmula `min(1.0, player_speed / enemy_speed)`: 100% si el jugador iguala o supera la velocidad del enemigo, si no baja pero nunca llega a 0%) y siempre se resuelve antes que cualquier otra acción del enemigo en el mismo tick, sea el jugador más rápido o más lento.
- [x] Al subir de nivel, `Player._level_up()` ahora también sube `speed` — junto con vida/ataque/armadura, con una curva de crecimiento **determinista pero no uniforme** (`Player._growth_gain`, inspirada en cómo Pokémon calcula stats por nivel: `floor(tasa * nivel) - floor(tasa * (nivel-1))` con una tasa fraccionaria por stat, p.ej. armadura a 1.4/nivel da la secuencia fija 1,2,1,2,1...). Así la progresión varía de nivel en nivel (unos dan más ataque, otros más armadura/velocidad) pero es exactamente igual en todas las partidas, no aleatoria. La resistencia mágica sigue siendo fija (+1, solo niveles pares) porque es un ajuste de balance deliberado contra el Mago, no "crecimiento genérico". Crítico (probabilidad y daño), regeneración de salud y penetración de defensa quedan fuera de la progresión por nivel a propósito: solo se conseguirán vía objetos/equipo.
- [x] Precisión y Evasión: tirada de acierto compartida (`characters/stats.py::resolve_hit`, importada tanto por `combat/battle.py::_execute_turn` como por `characters/enemies/enemy_base.py::Enemy.perform_turn` — vive en `stats.py`, un módulo hoja, para que ambos la usen sin crear un ciclo de imports). Parte de un 90% de acierto base (`BASE_HIT_CHANCE`), cada punto de diferencia precisión-evasión suma/resta 1%, con suelo del 5% y techo del 100% (`MIN_HIT_CHANCE`/`MAX_HIT_CHANCE`). Un fallo no llega a tocar armadura/elemento/crítico, se resuelve el primero. `Player.get_total_precision()`/`get_total_evasion()` ya existen (solo stat base, igual que velocidad). **Pendiente:** el Orco en furia (daño manual en `orc.py`) y los 4 hechizos del Mago (`mage.py`) todavía no pasan por `resolve_hit` — de momento aciertan siempre, igual que `ELEMENTAL_WEAKNESSES` empezó siendo solo del Troll.
- [ ] Crit Chance para enemigos (hoy es solo del jugador — ver `combat/battle.py::_execute_turn`).
- [ ] Crit Damage para enemigos (mismo caso que arriba).
- [ ] Resistencia Mágica para enemigos (el jugador ya la tiene vía `get_total_magic_resist()`).
- [ ] Regeneración de Salud: curación por turno o tras ciertos eventos (más allá del status "regeneración" actual).
- [ ] Penetración de Defensa: ignora parte de la defensa/armadura del objetivo.
- Nota: la velocidad hoy es solo el stat base (`Stats.speed`), sin bonus de equipo — igual que hizo `ELEMENTAL_WEAKNESSES` al empezar solo con "fuego", se puede sumar bonus de armadura/anillos más adelante si hace falta equilibrar mejor.
- [ ] Bonus de velocidad en el slot "botas" (nuevo campo en `Armor`, sumado en `Player.get_total_speed()` igual que `get_total_armor()` etc.) — decidido como la fuente de velocidad vía equipo; crítico/regeneración/penetración de defensa también quedan reservados para objetos, ver arriba.