# Roadmap

<p align="center"><a href="../ROADMAP.md">English</a> · <a href="ROADMAP_es.md">Español</a></p>

Documento vivo de lo que hay y lo que está planeado. Para el historial detallado
de versiones, mira el [CHANGELOG](CHANGELOG_es.md); para el diseño completo de la
dirección de mundo/historia/RPG, el [GDD](GDD_es.md); para el registro de
balance, [TODO.md](../TODO.md).

## Hecho

- Combate ATB (Active Time Battle), 1 contra 1, con críticos, daño físico y
  mágico, penetración, debilidades elementales y efectos de estado.
- 14 enemigos con mecánicas propias y una cadena de desbloqueo fija.
- 11 huecos de equipo estilo Diablo; herrería (12 recetas), tienda, bestiario.
- Panel de administración/debug protegido con contraseña.
- Música de fondo por «mood».
- Guardado/carga en JSON con copia de seguridad; reconocimiento del jugador por
  nombre sin distinguir mayúsculas/minúsculas.
- Registro de errores en disco e informe opcional (opt-in) a Discord.
- CI (Ruff, pyright, tests en Python 3.10–3.13 Linux + un job de Windows), badge de cobertura, workflow de release (v0.8.0).
- Protección de la rama `main` (PR + check `all-green`); smoke test de arranque.
- Entrada de teclado multiplataforma (`ui/keyboard.py`) — el juego y los tests ya no necesitan Windows.
- Ruff `UP`/`B`/`SIM`, `__version__` vía `importlib.metadata`, `concurrency` en el CI.
- Captura de partida en el README; descripción y topics del repo.
- `build-check` en el CI — construye el `.exe` cuando cambian los archivos de empaquetado.
- **Auto-updater** — la build empaquetada comprueba los GitHub Releases y puede
  descargar, verificar (SHA-256) y aplicar una actualización, reiniciándose sin
  reinstalar y sin tocar `saved_games/` / `config.ini`.

## Planeado — plan por fases

Diseño completo en el [GDD](GDD_es.md). Dirección: mantener el combate y
construir un mundo alrededor (zonas en un mapa con vuelta atrás libre, NPCs,
una questline de fantasía oscura). Cada fase es una release; **las releases se
etiquetan solo con la luz verde del mantenedor** — las funcionalidades se
acumulan en `main` por PRs.

### v0.9.0 — Profundidad de combate *(sin rework de mundo)*
- Armas que infligen estados + procesado de estados en `Enemy` (cierra el hueco
  de "los enemigos tienen `magic_resist` pero nada les aplica estados").
- Bonus de conjunto de armadura (4 conjuntos temáticos, tramos a 2/4 piezas).
- Clases de personaje al crear (Vagabundo / Guerrero / Pícaro / Arcanista).
- Rebalanceo ligero por lo anterior.

### v0.10.0 — El mundo, parte 1
- Sistema de zonas + grafo de viaje + bucle de exploración en vez del menú plano.
- La cadena de 14 enemigos migrada a 6 zonas + una aldea hub.
- Sub-lugares; tienda / herrería / descanso de pago reubicados. Encuentros
  aleatorios + hallazgos. Migración de guardado v1 → v2.

### v0.11.0 — Historia y misiones
- Sistema de misiones; questline principal "La Brecha" (6 actos) + 3
  secundarias.
- Diálogo de NPC condicional al estado de misión/historia. Notas de lore + Diario.

### v0.12.0 — La Arena y pulido
- Modo Arena / oleadas crecientes (combina con la auto-batalla turbo).
- Firma Ed25519 en el auto-updater (sobre SHA-256 + HTTPS — ver `SECURITY.md`).
- GIF de gameplay, imagen de social-preview.

### v1.0.0 — Valeterna
- Recalibrado completo de la cadena de 14 enemigos (post `BASE_HIT_CHANCE`
  90→100) contra el ritmo de la questline.
- Playthrough completo verificado de principio a fin.
- Separación MVC más limpia en la capa de presentación.
- *(Ampliación)* combate multi-enemigo de verdad — hoy varios enemigos lo
  fingen con un «golpe extra» en vez de un segundo combatiente con su medidor.

## Tareas menores de herramientas (sin fecha)

- Extender `pyright` para que revise también `tests/`, y subir de `basic` a `standard`.
- Limpiar las notas de release autogeneradas; enlazar el CHANGELOG.
- Canal de feedback dentro del juego (una opción de menú que publique en Discord,
  como el informe de errores).
- Localización / soporte multi-idioma en el propio juego.
