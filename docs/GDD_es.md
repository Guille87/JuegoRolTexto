# Documento de Diseño del Juego — Valeterna

<p align="center"><a href="../GDD.md">English</a> · <a href="GDD_es.md">Español</a></p>

Documento vivo del diseño para la evolución del juego: pasar de un bucle de
combate a un RPG de texto con mundo, historia, NPCs, clases, habilidades y un
bestiario grande. Historial de versiones: [CHANGELOG](CHANGELOG_es.md). Plan de
entrega: [ROADMAP](ROADMAP_es.md). Notas de balance: [TODO.md](../TODO.md).

**Estado: planificación.** Casi nada de esto está hecho — es el objetivo, y
seguirá creciendo. **No hay objetivo de 1.0**: el juego publica versiones
pre-lanzamiento hasta que el mantenedor decida que está listo para salir.

---

## 1. Visión y pilares

Hoy el juego es: eliges un enemigo de una lista → peleas → repites. La idea es
mantener ese combate (funciona y está calibrado) y envolverlo en un **mundo por
el que merezca la pena moverse**: zonas con nombre en un mapa, ~10 enemigos por
zona, NPCs con diálogo, una questline de fantasía oscura, clases, habilidades
que se aprenden por nivel, siete elementos de daño con debilidades,
resistencias e inmunidades.

1. **El combate sigue siendo el protagonista.** El sistema ATB, los enemigos,
   el botín y la herrería son el núcleo. Todo lo nuevo profundiza el bucle de
   *hacerse fuerte → llegar más lejos*, no lo sustituye.
2. **Explorar es elegir, no relleno.** Cada pantalla ofrece una decisión real:
   avanzar, farmear, gastar, hablar, entregar una misión, volver a por algo.
3. **Fantasía oscura seria.** Valeterna es un reino que se muere. Sin alivio
   cómico.
4. **Sigue siendo un juego de consola.** Menús numerados con `input()`, color
   con `colorama`, sin ventana. El mundo se describe, no se dibuja.
5. **Aditivo, no una reescritura.** Cada fase se monta sobre la anterior sin
   romper partidas ni la suite de tests.
6. **Traducible desde el principio.** Todo el texto nuevo de cara al jugador
   pasa por una capa de strings (`i18n`) para que el multi-idioma futuro sea
   barato (ver §9.1).

---

## 2. Historia — "La Brecha"

**Premisa.** Hace años, el **Dragón de Ceniza** arrasó la capital, Valeterna.
Su fuego agrietó el velo entre el mundo mortal y los planos infernales. Por esa
**brecha** se cuelan nigromantes, ángeles caídos y demonios, y la corrupción se
extiende hacia fuera desde la capital en ruinas como la podredumbre de una
herida. El jugador es uno de los pocos supervivientes del arrasamiento que
todavía puede empuñar un arma; desde **Piedrablanca**, la última aldea libre,
parte hacia la guarida del Dragón para cerrar la brecha en su origen.

### Misión principal — 7 actos, uno por región

| Acto | Región | Momento | Abre |
|------|--------|---------|------|
| I | Los Yermos | Halbrand: rompe las incursiones de bandidos que asfixian la aldea. | Bosque de los Susurros |
| II | Bosque de los Susurros | Cael explica la brecha; un espíritu está atado a un altar del bosque que la alimenta. | Ciénaga de los Ahogados |
| III | Ciénaga de los Ahogados | Algo más antiguo que la brecha se agita en el pantano anegado y la corrupción se encharca aquí. | Cañón del Trueno |
| IV | Cañón del Trueno | Mirelle: la corrupción baja por el viejo camino de montaña; un Gólem sella el paso. | Torre de los Arcanos |
| V | Torre de los Arcanos / Necrópolis | Sella: la torre del mago canaliza la brecha; el Nigromante levanta la Necrópolis. | Ciudadela en Ruinas |
| VI | Ciudadela en Ruinas | Aldric: la catedral es el corazón de la brecha; el Ángel Caído cayó defendiéndola, el Demonio la ocupa ahora. | Antesala del Dragón |
| VII | Antesala del Dragón | El ancla real de la brecha es el Dragón. Acaba con ello. | final |

*(Se añade una región nueva, **Ciénaga de los Ahogados**, entre bosque y cañón
para dar sitio a 7 zonas × ~10 enemigos. Su roster es diseño nuevo.)*

### Misiones secundarias (conjunto inicial, opcionales, nunca bloquean)

- **La muñeca de Nia** (Los Yermos) — una muñeca perdida en el campamento de bandidos.
- **El encargo de Dorn** (Bosque) — piel de Troll para una coraza legendaria única.
- **El tomo prohibido de Sella** (Necrópolis) — desbloquea una receta de daño mágico.
- Más por diseñar por región.

### Coleccionables de lore

Notas (cartas, páginas de diario, inscripciones) que se encuentran explorando.
Se leen una vez y quedan en un **Diario** que se relee desde el menú de
personaje. Opcional.

---

## 3. Mundo — zonas y mapa

Un grafo de **zonas** con vuelta atrás libre. Desde cualquier zona viajas a una
conectada; desde Piedrablanca (o un nodo "camino") viajas rápido a cualquier
zona **ya visitada**. Una zona se desbloquea al derrotar a su **guardián**
(mini-jefe) o completar el momento de historia que la abre. Piedrablanca
siempre es accesible.

```
Piedrablanca (hub, sin enemigos)
   │
Los Yermos ── Bosque de los Susurros ── Ciénaga de los Ahogados ── Cañón del Trueno ──
   Torre de los Arcanos / Necrópolis ── Ciudadela en Ruinas ── Antesala del Dragón
```

| Zona | Tema | Enemigos esqueleto (existentes) | Sub-lugares | NPCs clave |
|------|------|--------------------------------|-------------|------------|
| **Piedrablanca** | Última aldea libre | — | Taberna, Herrería, Mercado, Refugio | Yerma, Dorn, Halbrand, Nia |
| **Los Yermos** | Descampados junto a la aldea | Goblin, Huargo, Esqueleto, Bandido | Campamento de bandidos, Túmulo | Cael |
| **Bosque de los Susurros** | Bosque encantado | Orco, Espíritu Vengativo, Troll | Claro del altar, Cabaña quemada | Mirelle |
| **Ciénaga de los Ahogados** | Pantano anegado | *(todos nuevos)* | Templo hundido, Embarcadero podrido | *(nuevo)* |
| **Cañón del Trueno** | Paso de montaña, piedra | Gárgola, Gólem de Piedra | Mina derrumbada, Puente colgante | Kort |
| **Torre de los Arcanos / Necrópolis** | Torre de mago + cementerio | Mago, Nigromante | Biblioteca, Cripta | Sella |
| **Ciudadela en Ruinas** | La capital arrasada, suelo infernal | Ángel Caído, Demonio | Catedral rota, Plaza | Aldric |
| **Antesala del Dragón** | La aproximación a la guarida | Dragón (jefe final) | — | — |

Tienda / herrería / descanso / guardado pasan a sub-lugares de Piedrablanca; un
"Mercado errante" y un "Fuego de campamento" (descanso de pago) aparecen en
zonas posteriores.

---

## 4. Enemigos — diseño del roster

**Objetivo: ~10 enemigos por zona, ~70 en total.** Los 14 actuales son el
*esqueleto* (los mecánicamente únicos con nombre); el resto es diseño nuevo. El
**Dragón se diseña el último**, cuando exista todo el roster, para que quede
estrictamente por encima de todo como la pelea más difícil del juego — sus
estadísticas finales no se pueden saber hasta entonces y son un tema abierto a
propósito.

### 4.1 Estructura por zona

Los ~10 enemigos de cada zona se reparten en:

- **1 guardián** — mini-jefe; derrotarlo una vez abre la siguiente zona. Sigue
  farmeable después.
- **2–3 élite** — encuentros más duros y raros con una habilidad distintiva fuerte.
- **6–7 estándar** — el pan de cada día; los encuentros aleatorios pesan hacia estos.

### 4.2 Plantilla de enemigo

Cada enemigo se diseña contra esta plantilla (se mantendrá como tabla viva en
`docs/design/bestiario.md` cuando empiecen las fases):

| Campo | Significado |
|-------|-------------|
| `nombre` | español, fantasía oscura, sin repetir |
| `zona` / `tier` | zona + rango de poder 1–10 dentro de ella |
| `arquetipo` | bruto / hostigador / lanzador / apoyo / tanque / emboscador |
| `habilidad` | una mecánica distintiva (ver §4.4) |
| `elemento` | elemento que infligen sus ataques (o físico) |
| `debilidades` | 0–2 elementos a ×1.5 o ×2.0 |
| `resistencias` | 0–1 elemento a ×0.5 (rara vez ×0.25) |
| `inmunidades` | estados alterados que no puede recibir |
| `stats` | vida / ataque / velocidad / armadura / res. mágica / crítico, del presupuesto de poder (§4.3) |
| `drops` | materiales + probabilidad de un único; los comunes se tiran del tier de la zona (§7.3) |

### 4.3 Presupuesto de poder

70 enemigos no se calibran a ojo. Cada enemigo tiene un **score de poder**; por
la matemática del ATB (ver `TODO.md`), la amenaza efectiva escala con
`vida × velocidad × daño_neto` (daño neto = daño medio − mitigación efectiva).
Se define un score normalizado y una curva objetivo: `objetivo(zona N, tier T)
= base · f(N) · g(T)`. Cada enemigo se diseña para caer dentro de ±10 % de su
objetivo, y luego se verifica con playtest el guardián y una muestra de cada
tier, igual que se verifica hoy la cadena. La fórmula y sus constantes viven en
`TODO.md`.

### 4.4 Habilidades distintivas (menú de mecánicas del que tirar)

Reutilizar y ampliar los patrones que ya hay en el código: emboscada previa,
golpe extra periódico, autocuración bajo umbral, ataque inevitable, debuff
aplicado tras tirada de acierto, invocar un aliado (patrón de golpe extra).
Nuevas: ataque a distancia (ignora parte de la evasión), robo de oro, aturdir
(pierde un turno), desgaste de armadura (acumulable), drenaje de vida, frenesí
bajo umbral, "consagrar" (marca al jugador para recibir daño extra), maldición
que bloquea la curación.

### 4.5 Zona de ejemplo — Los Yermos (10)

Demuestra la plantilla; las otras seis zonas son trabajo de diseño posterior.

| Tier | Nombre | Arquetipo | Distintivo | Inflige | Débil | Resiste | Inmune |
|------|--------|-----------|------------|---------|-------|---------|--------|
| 1 | Rata Gigante | hostigador | mordisco rápido, prob. veneno leve | veneno | fuego | — | — |
| 2 | Goblin | bruto | emboscada tras la 1ª derrota | físico | — | — | — |
| 3 | Goblin Montaraz | lanzador | flechas (ignoran parte de la evasión) | físico | fuego | — | — |
| 4 | Huargo | hostigador | mordisco de manada (golpe extra) | físico | — | — | — |
| 5 | Chamán Goblin | apoyo | cura a un aliado / se cura, maldición leve | oscuridad | sagrado | oscuridad | — |
| 6 | Esqueleto | tanque | revive una vez | físico | sagrado, contundente | veneno | veneno, sangrado |
| 7 | Bandido | emboscador | desarme | físico | veneno | — | — |
| 8 | Salteador | hostigador | golpe rápido doble, roba oro | físico | — | — | — |
| 9 | Ogro del Yermo *(élite)* | bruto | golpe demoledor que aturde | físico | fuego | físico | — |
| 10 | El Carnicero *(guardián)* | bruto/tanque | frenesí bajo 40 % vida, aplica sangrado | físico | sagrado | veneno | veneno |

---

## 5. Elementos y afinidades

**Siete elementos** + físico (el default, sin elemento):

| Elemento | Sabor | Estado al golpear | Patrones típicos débil / resiste |
|----------|-------|-------------------|----------------------------------|
| **fuego** | quema con el tiempo | `quemado` (baja ataque + daño/turno) | derrite `congelado`; fuerte vs plantas/no-muertos |
| **veneno** | envenena con el tiempo | `veneno` (daño/turno vs vida máx) | la carne es débil; no-muertos y constructos inmunes |
| **rayo** | descarga | `paralizado` (prob. de saltar turno) | metal/mojado débil |
| **hielo** | congela / ralentiza | `congelado` (prob. de saltar turno) | lo alineado al fuego es débil; lo derrite el fuego |
| **sagrado** | luz divina | `consagrado` (recibe +daño, no puede autocurarse) | no-muertos y demonios débiles; los vivos neutrales; el Ángel Caído lo **resiste** |
| **oscuridad** | sombra de la brecha | `marchito` (curación/regen recibida −50 %) | vivos y alineados a la luz débiles; demonios y no-muertos lo **resisten** |
| **arcano** | magia pura | `silenciado` (el enemigo no puede lanzar) — siempre `is_magical`, perfora parte de la armadura física | lo mundano es débil; los constructos (Gólem, Gárgola) y el Mago lo **resisten** |

Modelo en la capa de datos:

- `Enemy.weaknesses: dict[str, float]` (multiplicador > 1),
  `Enemy.resistances: dict[str, float]` (multiplicador < 1),
  `Enemy.immune_statuses: set[str]`.
- Daño: `final = base × (weaknesses.get(el) or resistances.get(el) or 1.0)`
  antes de la mitigación por armadura/res. mágica.
- El jugador también tiene defensa elemental: `Armor` puede llevar `resist` (un
  dict pequeño), sumado bajo demanda como `Player.get_total_resist(elemento)` —
  unas pocas piezas y un conjunto (Sudario del Nigromante) lo dan.
- `apply_status` en cualquiera de los dos lados no hace nada si el objetivo
  lista ese estado en `immune_statuses`.

`is_fire` se mantiene (es ortogonal — solo derrite `congelado`).

### Reacciones elementales *(idea, sin comprometer)*

El `fuego` ya derrite `congelado`. Se podría ampliar: `rayo` sobre un objetivo
`congelado` lo rompe por daño extra; `fuego` + `veneno` = un daño/turno más
fuerte. Añade profundidad y complejidad — aparcado hasta tener la base de
elementos.

---

## 6. Sistemas de combate

### 6.1 Clases

Se elige una vez al crear el personaje; se guarda; las partidas viejas usan
**Vagabundo**.

| Clase | Identidad | Efecto |
|-------|-----------|--------|
| **Vagabundo** | equilibrado (el personaje de hoy) | estadísticas base y curvas actuales; el default seguro |
| **Guerrero** | tanque / bruto | +Vida, +armadura, +daño físico; crecimiento más tanque; sin magia |
| **Pícaro** | rápido / crítico | +velocidad, +evasión, +prob. crítico; crecimiento ágil; frágil |
| **Arcanista** | daño mágico | menos vida/armadura; **su ataque estándar es mágico** (`is_magical`), escala con un stat nuevo de *poder mágico* — por fin hace que importe la `magic_resist` de los enemigos |

Las clases tocan la creación del personaje, `Stats`, las constantes
`_*_GROWTH_RATE` de subida por nivel y (Arcanista) la rama del jugador en
`_execute_turn`.

### 6.2 Habilidades (se aprenden por nivel, por clase)

Sin barra de maná. Cada clase aprende **~6 habilidades** a niveles fijos (3, 6,
9, 12, 15, 18). Dos tipos:

- **Pasiva** — modifica el combate sola, sin UI (p. ej. "cura al matar").
- **Activa** — una acción en vez de atacar, con **enfriamiento en turnos**
  ("usada, lista de nuevo en N turnos"). El estado del enfriamiento vive solo en
  el combate, no en el guardado.

El combate gana una opción **"Habilidades"**. En auto/turbo la política es
simple: usa una activa lista si la hay, si no ataca. Todas las pasivas
aprendidas están siempre activas; si las activas necesitan "equiparse" (p. ej.
máx. 2) es un tema abierto — empezamos con "todas usables".

Esbozo (sujeto a balanceo):

| Nvl | Vagabundo | Guerrero | Pícaro | Arcanista |
|-----|-----------|----------|--------|-----------|
| 3 | Segundo Aliento — *p:* cura 15 % vida máx. al matar | Embate — *a3:* golpe fuerte, 40 % aturdir | Golpe Bajo — *a3:* crítico garantizado + sangrado | Proyectil Arcano — *a2:* daño mágico alto, perfora res. mágica |
| 6 | Golpe Certero — *a3:* próximo golpe +50 %, no falla | Piel de Piedra — *p:* −15 % daño físico recibido | Reflejos — *p:* +15 % evasión | Escudo de Maná — *a4:* absorbe por completo el próximo golpe |
| 9 | Aguante — *p:* bajo 30 % vida, +20 % armadura y res. mágica | Represalia — *p:* 30 % de contraatacar al recibir un golpe cuerpo a cuerpo | Veneno de Contacto — *p:* 20 % de aplicar veneno al golpear | Sintonía Elemental — *p:* eliges el elemento de tu ataque al empezar el combate |
| 12 | Adrenalina — *a5:* +30 % velocidad 3 turnos | Grito de Guerra — *a5:* +25 % daño 3 turnos | Sombra — *a4:* esquivas garantizado el próximo ataque enemigo | Descarga — *a5:* daño mágico + aplica el estado del elemento activo |
| 15 | Botín Afortunado — *p:* +25 % oro, +10 % prob. de drop | Fortaleza — *p:* +40 % vida máxima | Golpe Mortal — *p:* +50 % daño crítico | Mente Aguda — *p:* −1 turno a todos los enfriamientos |
| 18 | Voluntad de Hierro — *p:* sobrevives a un golpe letal con 1 de vida (1 vez/combate) | Último Bastión — *a6:* 2 turnos inmune a daño físico | Asalto — *a6:* 3 golpes rápidos | Cataclismo — *a8:* daño mágico masivo, ignora toda mitigación |

*(p = pasiva, aN = activa con enfriamiento de N turnos.)*

### 6.3 Bonus de conjunto de armadura

`Armor` gana un `set_name` opcional. `Player` cuenta las piezas equipadas por
conjunto y aplica **tramos a 2 y 4 piezas** (los conjuntos son de 4). Temáticos
por región, sueltan allí:

| Conjunto | Región | 2 piezas | 4 piezas |
|----------|--------|----------|----------|
| Atavío del Proscrito | Los Yermos | +evasión | el primer golpe de cada combate es crítico garantizado |
| Placas del Guardián | Cañón del Trueno | +armadura | −10 % a todo el daño físico recibido |
| Sudario del Nigromante | Necrópolis | +res. mágica y +res. oscuridad | 20 % de reflejar parte del daño mágico recibido |
| Vestiduras del Caído | Ciudadela | +regeneración | curas el 15 % del daño que infliges |

Todos los `get_total_*` ya suman el equipo bajo demanda — los bonus de conjunto
se enganchan igual. Ninguna pieza de conjunto es estrictamente mejor que las
otras opciones de su hueco.

### 6.4 Armas que infligen estados

`Weapon` gana `inflicts` = `{estado, probabilidad, duración, poder}`. En un
golpe del jugador, se tira `probabilidad` y `enemy.apply_status(...)`
(respetando `immune_statuses`). Exige que **`Enemy` procese estados en su
turno** — un espejo de `Player.on_turn_start` / `on_turn_end` (daño/turno de
quemadura/veneno vs `max_health`, parálisis/congelación saltan turno). Mapa de
infección de las armas elementales: veneno→`veneno`, fuego→`quemado`,
hielo→`congelado`, rayo→`paralizado`, oscuridad→`marchito`,
sagrado→`consagrado`, arcano→`silenciado`.

### 6.5 Modo Arena

Un lugar de Piedrablanca que se desbloquea tras el Acto III (o con una
entrada). Eliges un nivel de dificultad → **N oleadas crecientes** seguidas,
enemigos de las zonas superadas. La curación entre oleadas se paga con oro. Las
recompensas escalan con la oleada: oro, probabilidad de piezas de conjunto, un
**título** cosmético en la pantalla de estadísticas. El guardado registra
`arena_mejor_oleada`. Combina con la auto-batalla turbo.

---

## 7. Progresión y economía

### 7.1 Subida de nivel

Curva sin cambios (`Player._required_xp_for_level`). Los niveles ahora también
desbloquean habilidades (§6.2). `poder mágico` es un campo nuevo de `Stats`, 0
para no-Arcanistas, creciente para el Arcanista.

### 7.2 Bestiario — revelado progresivo

Según `enemy_kill_counts`:

| Kills | Se revela |
|-------|-----------|
| 0 | no aparece (como hoy) |
| 1 | nombre, vida, rango de ataque, oro |
| 3 | armadura, res. mágica, velocidad, crítico |
| 5 | debilidades, resistencias, inmunidades a estados |
| 10 | tabla de drops completa (primera vez que se muestra) |

### 7.3 Escalado del botín

Híbrido, para que el toque hecho a mano sobreviva a 70 enemigos:

- **Únicos** — hechos a mano, baja tasa de drop, de enemigos concretos (como
  hoy). Las piezas de conjunto y la herrería siguen a mano.
- **Comunes** — `items/loot.py` tira una pieza para un hueco de los **rangos
  del tier de la zona**: magnitud del stat base + 0–3 secundarias, mismas
  reglas que verifica `tests/test_armor_progression.py`. Mantiene las zonas
  tempranas en 1–2 stats y las tardías en 3–4.

### 7.4 Penalización por muerte *(abierto — ver §11)*

Hoy: pierdes ⅓ del oro + cura total. Candidato: reaparecer en la última ciudad
visitada; el oro perdido se queda como un "saco" en la zona donde caíste,
recuperable si vuelves (estilo Souls). Sin decidir.

---

## 8. Sistemas de mundo

### 8.1 Bucle de exploración

Sustituye al menú plano de `game_loop`. Dentro de una zona: **Explorar**
(tirada ponderada: encuentro / hallazgo / mini-evento raro), **Ir a
`<sub-lugar>`** (NPC / servicio / entrega de misión), **Viajar** (conectada o
viaje rápido), **Personaje** (el menú de personaje siempre disponible:
inventario, estadísticas, equipar, habilidades, bestiario, diario, misiones,
guardar — extraído del `game_loop` actual).

### 8.2 Diálogo

Ligero. Un NPC tiene una lista ordenada de **nodos de diálogo**; cada uno con
texto, una condición opcional (estado de misión / bandera de historia / objeto
en inventario) y un efecto opcional (iniciar/avanzar una misión, poner una
bandera, dar un objeto, abrir un servicio). Sin árboles ramificados en la v1 —
el nodo *disponible* cambia según el estado del mundo.

### 8.3 Misiones

`Quest`: id, título, descripción, **objetivo** (matar N de X, llegar a la zona
Y, hablar con Z, conseguir W, o una bandera manual), **recompensa** (oro /
objeto / receta / bandera), **estado** (`no_iniciada` / `activa` / `completada`
/ `entregada`). El progreso se comprueba desde hooks que ya saltan
(`_handle_victory`, llegar a una zona, `Inventory.add_item`). Una entrada
**Misiones** en el menú de personaje las lista.

---

## 9. Técnica

### 9.1 Capa de strings (i18n) — se monta primero

Todo el texto de cara al jugador pasa por `t(clave, **kwargs)`.
Implementación: un paquete `i18n/` con `catalog_es.py` (y luego
`catalog_en.py`) — diccionarios planos con clave por id de string
(`"enemy.goblin.name"`, `"skill.golpe_bajo.desc"`, …) — y un `t()` que resuelve
según el idioma activo de `config.ini` `[IDIOMA]` (por defecto `es`). Los
helpers de `ui/console.py` no cambian (reciben strings ya resueltos). **El
contenido nuevo se escribe con `t()` desde el principio;** el español
hardcodeado se migra módulo a módulo (una tarea de fondo por área), empezando
por combate y menús en la fase de fundaciones.

### 9.2 Paquete `world/`

Guiado por datos como `characters/enemies/` (un archivo por zona):

- `world/zone.py` — `Zone` (id, nombre, descripción, sub-lugares, grupo de
  enemigos, conexiones, puerta).
- `world/npc.py` — `NPC`, `DialogueNode`.
- `world/quest.py` — `Quest`, enum de estado, tipos de objetivo/recompensa.
- `world/map.py` — el grafo de zonas, viaje, viaje rápido, puertas.
- `world/data/*.py` — un módulo por zona que conecta NPCs, diálogos, encuentros
  y lore.

### 9.3 Otros módulos nuevos

- `characters/skills.py` — definiciones de habilidades; `Player` deriva
  `known_skills` de clase + nivel (no se guarda).
- `items/loot.py` — las tablas de tirada de drops comunes por tier de zona.
- `ui/exploration.py` — el bucle de zona (`omit`ido de la cobertura como
  `ui/menus.py`).

### 9.4 Esquema de guardado v2

Añade un bloque `mundo`: `clase`, `zona_actual`, `zonas_visitadas`,
`misiones`, `banderas`, `diario`, `arena_mejor_oleada`. Migración v1 → v2
(`persistence/save_load.py`, mismo patrón que los back-fills de huecos de
armadura y `discovered_materials`): sin bloque `mundo` → se coloca en la zona
que corresponda al progreso de `defeated_enemies`, clase `vagabundo`, sin
misiones/banderas. `unlocked_enemies` / `defeated_enemies` siguen siendo la
fuente de verdad para las puertas de zona.

### 9.5 Tests

Toda la lógica no interactiva va con tests unitarios: matemática de afinidades,
inmunidad a estados, efectos y enfriamientos de habilidades, diferencias de
stats/crecimiento por clase, conteo de bonus de conjunto, rangos de tirada de
loot, progreso de misiones, condiciones de diálogo, viaje y puertas del mapa,
resolución y fallback de claves i18n, migración de guardado. El bucle de
exploración y los menús siguen `omit`idos de la métrica de cobertura.

---

## 10. Fases de desarrollo (pre-lanzamiento, abiertas)

Cada fase es una release; **las releases se etiquetan solo con la luz verde del
mantenedor** — las funcionalidades se acumulan en `main` por PRs. El orden
puede cambiar.

| Fase | Tema | Contenido |
|------|------|-----------|
| **v0.9.0** | Fundaciones | capa de strings i18n + migrar el núcleo de combate/menús · modelo de afinidades de enemigos (debilidades / resistencias / inmunidades a estados) + los 3 elementos nuevos registrados como datos · armas que infligen estados + procesado de estados en `Enemy` |
| **v0.10.0** | Clases y habilidades | 4 clases al crear · árboles de habilidades por clase (pasivas + activas con enfriamiento) · menú "Habilidades" en combate · stat `poder mágico` |
| **v0.11.0** | Equipo y afinidades | 4 conjuntos de armadura · resistencia elemental en armadura · aplicar debilidades / resistencias / inmunidades reales a los 14 enemigos actuales · armas elementales nuevas (sagrado / oscuridad / arcano) |
| **v0.12.0** | El mundo, parte 1 | zonas + mapa + bucle de exploración + migración de guardado v2 · tienda / herrería / descanso reubicados · encuentros aleatorios + hallazgos |
| **v0.13.0** | Bestiario y enemigos I | bestiario progresivo · herramienta de presupuesto de poder · rellenar 2–3 zonas a ~10 enemigos cada una |
| **v0.14.0** | Enemigos II | terminar el roster hasta ~70 · escalado del botín (únicos + comunes tirados) |
| **v0.15.0** | Historia y misiones | sistema de misiones · questline "La Brecha" (7 actos) + secundarias · diálogo de NPC · notas de lore + Diario |
| **v0.16.0** | La Arena | modo de oleadas crecientes |
| **más adelante** | Endgame y pulido | ajuste final del Dragón (necesita el roster completo) · rebalanceo completo de la cadena · firma Ed25519 del updater · GIF de gameplay · MVC más limpia · *(ampliación)* combate multi-enemigo |
| **1.0** | — | la declara el mantenedor cuando el juego esté listo para salir |

---

## 11. Preguntas abiertas

- **Ritmo de encuentros** — ¿superar una zona por un número fijo de encuentros,
  o superar = derrotar al guardián una vez y el grupo sigue farmeable?
  *(inclinación: lo segundo.)*
- **Descanso** — ¿cura del todo o un %? ¿Coste fijo de oro o escala con nivel?
- **Viaje rápido** — ¿gratis, o cuesta oro / un turno de encuentros en el camino?
- **Penalización por muerte** — ¿como hoy, o el "saco" estilo Souls (§7.4)?
- **Equipar activas** — ¿todas las habilidades aprendidas usables, o máx. 2 equipadas?
- **Profundidad de diálogo en v1** — ¿unas líneas que cambian con el estado por
  NPC, o un pequeño menú de temas?
- **Recompensas de la Arena** — ¿solo títulos cosméticos, o también una vía
  lenta a piezas de conjunto?
- **Estados por elemento** — ¿comprometemos `consagrado` / `marchito` /
  `silenciado` como están diseñados, o empezamos solo con los cuatro clásicos y
  añadimos el resto después?
- **Reacciones elementales** (§5) — ¿en alcance algún día, o un "no" permanente?
- **Nombre de la región nueva** — ¿es **Ciénaga de los Ahogados** la 3ª zona
  correcta, o otro bioma (costa, catacumbas, tierras de cultivo malditas…)?
