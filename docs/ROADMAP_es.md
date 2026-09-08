# Roadmap

<p align="center"><a href="../ROADMAP.md">English</a> · <a href="ROADMAP_es.md">Español</a></p>

Documento vivo de lo que hay y lo que está planeado. Para el historial detallado
de versiones, mira el [CHANGELOG](CHANGELOG_es.md); para el registro de balance,
[TODO.md](../TODO.md).

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
- CI (Ruff, pyright, tests en Python 3.10–3.13 Linux + un job de Windows), badge de cobertura, workflow de release (v0.3.0).
- Protección de la rama `main` (PR + check `all-green`); smoke test de arranque.
- Entrada de teclado multiplataforma (`ui/keyboard.py`) — el juego y los tests ya no necesitan Windows.
- Ruff `UP`/`B`/`SIM`, `__version__` vía `importlib.metadata`, `concurrency` en el CI.
- Captura de partida en el README; descripción y topics del repo.
- `build-check` en el CI — construye el `.exe` cuando cambian los archivos de empaquetado.
- **Auto-updater** — la build empaquetada comprueba los GitHub Releases y puede
  descargar, verificar (SHA-256) y aplicar una actualización, reiniciándose sin
  reinstalar y sin tocar `saved_games/` / `config.ini`.

## Juego — planeado

- **Recalibrar la cadena de 14 enemigos** tras cambiar `BASE_HIT_CHANCE` de 90 a
  100 — hasta ahora solo se ha reverificado el Goblin.
- **Bonus de conjunto de armadura** (2/4/6 piezas de un mismo set).
- **Combate contra varios enemigos de verdad** — hoy varios lo fingen con un
  «golpe extra» en vez de un segundo combatiente con su propio medidor de turno.
- Separación MVC más limpia en la capa de presentación.

## Proyecto y herramientas — planeado

Medio / pulido:

- **Firma Ed25519** en la auto-actualización, sobre el SHA-256 + HTTPS actual,
  para protegerse también ante una cuenta de GitHub comprometida (ver
  `SECURITY.md`).

- **Grabación de gameplay (GIF / asciinema)** para el README, más allá de la captura estática.
- **Imagen de social preview** del repo (por los ajustes de GitHub).
- Extender `pyright` para que revise también `tests/`, y subir de `basic` a `standard`.
- Limpiar las notas de release autogeneradas; enlazar el CHANGELOG.

## Ideas (sin compromiso)

- Canal de feedback dentro del juego (una opción de menú que publique en Discord,
  como el informe de errores).
- Localización / soporte multi-idioma en el propio juego.
