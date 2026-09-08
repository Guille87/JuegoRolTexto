# Documento de Diseño del Juego — Valeterna

<p align="center"><a href="../GDD.md">English</a> · <a href="GDD_es.md">Español</a></p>

Documento vivo del diseño para la evolución del juego: pasar de un bucle de
combate a un RPG de texto pequeño con mundo, historia y NPCs. El historial de
versiones está en [CHANGELOG](CHANGELOG_es.md); el plan de entrega por fases en
[ROADMAP](ROADMAP_es.md); las notas de balance en [TODO.md](../TODO.md).

Estado: **planificación**. Nada de esto está hecho todavía — esto es el objetivo.

---

## 1. Visión

Hoy el juego es: eliges un enemigo de una lista → peleas → repites. La idea es
mantener ese combate (funciona y está calibrado) y envolverlo en un **mundo por
el que merezca la pena moverse**: zonas con nombre conectadas en un mapa, NPCs
con diálogo, una misión principal que explique por qué avanzas hacia el Dragón,
misiones secundarias, lore por descubrir, y enemigos que pertenezcan a lugares
en vez de a una lista plana.

### Pilares de diseño

1. **El combate sigue siendo el protagonista.** El sistema ATB, los 14
   enemigos, el botín y la herrería son el núcleo. Todo lo nuevo sirve al bucle
   de *hacerse fuerte → llegar más lejos*, no lo sustituye.
2. **Explorar es elegir, no relleno.** Cada pantalla ofrece una decisión real:
   avanzar, farmear, gastar, hablar, entregar una misión, volver a por algo.
3. **Fantasía oscura seria.** Valeterna es un reino que se muere. Sin alivio
   cómico: los NPCs han perdido gente, los sitios están en ruinas, el tono es
   sombrío pero no sin esperanza.
4. **Sigue siendo un juego de consola.** Menús numerados con `input()`, color
   con `colorama`, sin ventana gráfica. El mundo se describe, no se dibuja.
5. **Aditivo, no una reescritura.** Cada fase se monta sobre la anterior sin
   romper partidas guardadas ni la suite de tests.

---

## 2. Historia — "La Brecha"

**Premisa.** Hace años, el **Dragón de Ceniza** arrasó la capital, Valeterna.
Su fuego hizo algo más que quemar: agrietó el velo entre el mundo mortal y los
planos infernales. Por esa **brecha** se cuelan ahora nigromantes, ángeles
caídos y demonios, y la corrupción se extiende hacia fuera desde la capital en
ruinas como la podredumbre de una herida.

El jugador es uno de los pocos supervivientes del arrasamiento que todavía
puede empuñar un arma. Desde **Piedrablanca**, la última aldea libre, parte
hacia la guarida del Dragón para cerrar la brecha en su origen — atravesando
seis regiones cada vez más corrompidas para llegar.

### Misión principal (6 actos, uno por región)

| Acto | Región | Momento | Puerta que abre |
|------|--------|---------|-----------------|
| I | Los Yermos | Halbrand te pide romper las incursiones de bandidos que asfixian la aldea. | Bosque de los Susurros |
| II | Bosque de los Susurros | El ermitaño Cael explica la brecha; un espíritu vengativo está atado a un altar del bosque que la alimenta. | Cañón del Trueno |
| III | Cañón del Trueno | La druida Mirelle: la corrupción baja por el viejo camino de montaña, y un Gólem sella el paso. | Torre de los Arcanos |
| IV | Torre de los Arcanos / Necrópolis | La aprendiza Sella: la torre del Mago canaliza la brecha y el Nigromante está levantando la Necrópolis. | Ciudadela en Ruinas |
| V | Ciudadela en Ruinas | El paladín Aldric: la catedral es el corazón de la brecha; el Ángel Caído cayó defendiéndola y el Demonio la ocupa ahora. | Antesala del Dragón |
| VI | Antesala del Dragón | El ancla real de la brecha es el Dragón. Acaba con ello. | — (final) |

### Misiones secundarias (conjunto inicial)

- **La muñeca de Nia** (Los Yermos) — una niña de Piedrablanca perdió su muñeca
  al huir con su familia; está en el campamento de bandidos abandonado.
- **El encargo de Dorn** (Bosque) — el herrero quiere piel de Troll para una
  coraza legendaria única; se engancha con la herrería.
- **El tomo prohibido de Sella** (Necrópolis) — recupera un libro prohibido de
  la biblioteca de la torre; desbloquea una receta de crafteo de daño mágico.

Las secundarias son opcionales, dan recompensas que importan (objetos únicos,
recetas, oro) y nunca bloquean el camino principal.

### Coleccionables de lore

"Notas" repartidas (cartas, páginas de diario, inscripciones) que se encuentran
explorando. Se leen una vez y quedan guardadas en un **Diario** que puedes
releer desde el menú de personaje. Puro trasfondo, opcional.

---

## 3. Mapa del mundo

Un grafo de **zonas** con vuelta atrás libre. Desde cualquier zona puedes
viajar a una zona conectada; desde Piedrablanca (o un nodo "camino") puedes
viajar rápido a cualquier zona **ya visitada**.

```
Piedrablanca (hub, sin enemigos)
   │
Los Yermos ── Bosque de los Susurros ── Cañón del Trueno ──
   Torre de los Arcanos / Necrópolis ── Ciudadela en Ruinas ── Antesala del Dragón
```

Una zona se desbloquea al derrotar a su **guardián** (su último enemigo) o al
completar el momento de historia que la abre. Piedrablanca siempre es
accesible.

### Zonas

| Zona | Tema | Enemigos (de la cadena actual) | Sub-lugares | NPCs clave |
|------|------|--------------------------------|-------------|------------|
| **Piedrablanca** | Última aldea libre | — | Taberna, Herrería, Mercado, Refugio | Yerma (tabernera), Dorn (herrero), Halbrand (veterano), Nia |
| **Los Yermos** | Descampados junto a la aldea | Goblin, Huargo, Esqueleto, Bandido | Campamento de bandidos, Túmulo | Cael (ermitaño) |
| **Bosque de los Susurros** | Bosque encantado | Orco, Espíritu Vengativo, Troll | Claro del altar, Cabaña quemada | Mirelle (druida) |
| **Cañón del Trueno** | Paso de montaña, piedra | Gárgola, Gólem de Piedra | Mina derrumbada, Puente colgante | Kort (minero) |
| **Torre de los Arcanos / Necrópolis** | Torre de mago + cementerio | Mago, Nigromante | Biblioteca, Cripta | Sella (aprendiza) |
| **Ciudadela en Ruinas** | La capital arrasada, suelo infernal | Ángel Caído, Demonio | Catedral rota, Plaza | Aldric (paladín) |
| **Antesala del Dragón** | La aproximación a la guarida | Dragón (jefe final) | — | — |

La **tienda, la herrería, el descanso y el guardado** pasan a sub-lugares de
Piedrablanca; un "Mercado errante" y un "Fuego de campamento" (descanso de
pago) aparecen en zonas posteriores para no tener que volver andando cada vez.

---

## 4. Sistemas

### 4.1 Bucle de exploración

Sustituye al menú plano de `game_loop`. Dentro de una zona:

- **Explorar la zona** — una tirada ponderada: encuentro con enemigo (del grupo
  de la zona), un hallazgo (materiales / oro / una nota de lore / nada), o un
  mini-evento raro.
- **Ir a `<sub-lugar>`** — entrar en un sub-lugar: hablar con un NPC, usar un
  servicio (tienda / herrería / descanso), entregar una misión.
- **Viajar** — moverse a una zona conectada, o viaje rápido a una ya visitada.
- **Personaje** — el menú de personaje, siempre disponible: inventario,
  estadísticas, equipar arma/armadura, bestiario, diario, misiones, guardar.
  (Extraído del `game_loop` actual para que funcione igual en todas partes.)

La auto-batalla turbo se queda exactamente como está y es ideal para farmear el
grupo de encuentros de una zona.

### 4.2 Diálogo

Ligero. Un NPC tiene una lista ordenada de **nodos de diálogo**; cada nodo
tiene texto, una condición opcional (estado de misión / bandera de historia /
objeto en inventario) y un efecto opcional (iniciar/avanzar una misión, poner
una bandera, dar un objeto, abrir un servicio). Sin árboles ramificados en la
v1 — el nodo *disponible* cambia según cambia el estado del mundo, y eso basta
para un RPG de texto de este tamaño.

### 4.3 Misiones

`Quest`: id, título, descripción, un **objetivo** (matar N del enemigo X,
llegar a la zona Y, hablar con el NPC Z, conseguir el objeto W, o una bandera
de historia manual), una **recompensa** (oro / objeto / receta / bandera) y un
**estado** (`no_iniciada` / `activa` / `completada` / `entregada`). El progreso
del objetivo se comprueba desde los hooks de combate y exploración que ya
saltan (`_handle_victory`, llegar a una zona, `Inventory.add_item`). Una entrada
**Misiones** en el menú de personaje lista las misiones activas y su progreso.

### 4.4 Clases

Se elige una vez al crear el personaje. Sustituye al "todos son idénticos". Se
guarda en la partida; las partidas viejas usan **Vagabundo** por defecto (las
estadísticas de hoy).

| Clase | Identidad | Efecto |
|-------|-----------|--------|
| **Vagabundo** | Equilibrado (el personaje de hoy) | Estadísticas base y curvas de subida actuales. El default seguro. |
| **Guerrero** | Tanque / bruto | +Vida, +armadura, +daño físico base; crecimiento más tanque. Sin magia. |
| **Pícaro** | Rápido / crítico | +velocidad, +evasión, +prob. crítico; crecimiento ágil. Frágil. |
| **Arcanista** | Daño mágico | Menos vida/armadura; **su ataque estándar es mágico** (`is_magical=True`), escala con un nuevo stat de *poder mágico* — por fin hace que importe la `magic_resist` de los enemigos. |

Las clases solo tocan la creación del personaje, `Stats`, las constantes
`_*_GROWTH_RATE` de subida por nivel y (solo Arcanista) la rama del jugador en
`_execute_turn`.

### 4.5 Bonus de conjunto de armadura

`Armor` gana un `set_name` opcional. `Player` cuenta las piezas equipadas por
conjunto y aplica **bonus por tramos a 2 y 4 piezas** (los conjuntos son de 4
piezas). Los conjuntos son temáticos por región y sueltan allí:

| Conjunto | Región | 2 piezas | 4 piezas |
|----------|--------|----------|----------|
| **Atavío del Proscrito** | Los Yermos | +evasión | El primer golpe de cada combate es crítico garantizado |
| **Placas del Guardián** | Cañón del Trueno | +armadura | −10% a todo el daño físico recibido |
| **Sudario del Nigromante** | Necrópolis | +resistencia mágica | 20% de probabilidad de reflejar parte del daño mágico recibido |
| **Vestiduras del Caído** | Ciudadela | +regeneración | Curas el 15% del daño que infliges |

Todos los `get_total_*` ya suman el equipo bajo demanda — los bonus de conjunto
se enganchan igual. Ninguna pieza de conjunto es estrictamente mejor que las
otras opciones de su hueco, misma regla que la herrería hoy.

### 4.6 Armas que infligen estados

`Weapon` gana `inflicts` = `{estado, probabilidad, duración, poder}`. En un
golpe del jugador, se tira `probabilidad` y `enemy.apply_status(...)`. Esto
exige que **`Enemy` procese estados alterados en su propio turno** — un espejo
de `Player.on_turn_start` / `on_turn_end` (daño por turno de quemadura/veneno
contra `max_health`, parálisis/congelación saltan turno). Las cuatro armas
elementales reciben infección temática: veneno → `veneno`, fuego → `quemado`,
hielo → `congelado`, rayo → `paralizado`. Cierra el hueco de siempre en el que
los enemigos tienen `magic_resist` pero nada del lado del jugador usa estados
contra ellos.

### 4.7 Modo Arena

Un lugar que se desbloquea en Piedrablanca tras superar el Acto III (o con un
objeto "entrada"). Eliges un nivel de dificultad → peleas **N oleadas
crecientes** seguidas, con enemigos sacados de las zonas que hayas superado. La
única curación entre oleadas se paga con oro. Las recompensas escalan con la
oleada alcanzada: oro, probabilidad de piezas de conjunto y un **título**
cosmético que se muestra en la pantalla de estadísticas. La partida guarda
`arena_mejor_oleada`. Pensado para combinarse con la auto-batalla turbo.

---

## 5. Esquema de guardado (v2)

La partida de hoy (v1) tiene el estado del jugador + `unlocked_enemies` +
`defeated_enemies`. La v2 añade un bloque `mundo`:

```
mundo:
  clase: "vagabundo"
  zona_actual: "piedrablanca"
  zonas_visitadas: ["piedrablanca", "los_yermos"]
  misiones: { "<id>": { estado, progreso } }
  banderas: ["brecha_revelada", ...]
  diario: ["<id de nota>", ...]
  arena_mejor_oleada: 0
```

**Migración v1 → v2** (`persistence/save_load.py`, mismo patrón que los
back-fills de los huecos de armadura y `discovered_materials`): una partida sin
bloque `mundo` se coloca en la zona que corresponda a su progreso de
`defeated_enemies`, clase `vagabundo`, sin misiones, sin banderas.
`unlocked_enemies` / `defeated_enemies` siguen siendo la fuente de verdad para
las puertas de zona durante y después de la migración.

---

## 6. Arquitectura técnica

Nuevo paquete `world/`, guiado por datos igual que `characters/enemies/` (un
archivo por zona):

- `world/zone.py` — dataclass `Zone` (id, nombre, descripción, sub-lugares,
  grupo de enemigos, conexiones, condición de puerta).
- `world/npc.py` — `NPC`, `DialogueNode`.
- `world/quest.py` — `Quest`, enum de estado, tipos de objetivo/recompensa.
- `world/map.py` — el grafo de zonas, viaje, viaje rápido, puertas.
- `world/data/*.py` — un módulo por zona que conecta sus NPCs, diálogos,
  encuentros y notas de lore.

Presentación:

- `ui/exploration.py` — el nuevo bucle de zona (el menú de exploración).
  `omit`ido de la cobertura, igual que `ui/menus.py`.
- `ui/menus.py` — `game_loop` encoge; el sub-menú de personaje se extrae para
  reutilizarlo desde el hub y desde cada zona.
- `combat/battle.py` — intacto en las fases 0.9–0.11 salvo: procesado de
  estados del enemigo (0.9), el ataque estándar mágico del Arcanista (0.9), y
  los hooks de bonus de conjunto leyendo de `Player.get_total_*` (0.9).

Tests: toda la lógica de `world/` (puertas, progreso de misiones, condiciones
de diálogo, viaje por el mapa, migración de guardado) va con tests unitarios;
el bucle interactivo de exploración se `omit`e de la métrica de cobertura,
igual que el código de menús actual.

---

## 7. Entrega por fases

Cada fase es una release; **no se etiqueta ninguna release hasta que el
mantenedor dé luz verde** — las funcionalidades entran en `main` por PRs y se
van acumulando.

### v0.9.0 — Profundidad de combate *(sin rework de mundo, riesgo mínimo)*
- Armas que infligen estados + procesado de estados en `Enemy`.
- Bonus de conjunto de armadura (4 conjuntos).
- Clases de personaje (4).
- Rebalanceo ligero por lo anterior.

### v0.10.0 — El mundo, parte 1
- Sistema de zonas + grafo de viaje + bucle de exploración.
- Enemigos movidos a zonas; la cadena lineal migrada a 6 zonas + hub.
- Sub-lugares; tienda / herrería / descanso de pago reubicados.
- Encuentros aleatorios + hallazgos.
- Migración de guardado v1 → v2.

### v0.11.0 — Historia y misiones
- Sistema de misiones; questline principal "La Brecha" (6 actos) + 3
  secundarias.
- Diálogo de NPC condicional al estado de misión/historia.
- Notas de lore + Diario.

### v0.12.0 — La Arena y pulido
- Modo Arena / oleadas.
- Firma Ed25519 en el auto-updater.
- GIF de gameplay, imagen de social-preview.

### v1.0.0 — Valeterna
- Recalibrado completo de la cadena de 14 enemigos (post `BASE_HIT_CHANCE`
  90→100) contra el ritmo de la questline.
- Playthrough completo verificado de principio a fin.
- Separación MVC más limpia en la capa de presentación.
- *(Ampliación)* combate multi-enemigo.

---

## 8. Preguntas abiertas

- Ritmo de encuentros: ¿un número fijo de encuentros para "superar" una zona, o
  superar = derrotar al guardián una vez y los encuentros siguen para farmear?
  *(inclinación: lo segundo — el guardián abre la siguiente zona, el grupo
  sigue farmeable.)*
- ¿El descanso cura del todo o un porcentaje? ¿Cuesta una cantidad fija de oro
  o escala con el nivel?
- Viaje rápido: ¿gratis, o cuesta oro / un turno de encuentros en el camino?
- Cuánto diálogo por NPC en la v1 — ¿unas líneas fijas que cambian según el
  estado, o un pequeño menú de temas?
- Recompensas de la Arena: ¿solo títulos cosméticos, o también una vía lenta
  para conseguir piezas de conjunto?
