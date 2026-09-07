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
- CI (Ruff + tests en Python 3.10–3.13), badge de cobertura, workflow de release (v0.3.0).

## Juego — planeado

- **Recalibrar la cadena de 14 enemigos** tras cambiar `BASE_HIT_CHANCE` de 90 a
  100 — hasta ahora solo se ha reverificado el Goblin.
- **Bonus de conjunto de armadura** (2/4/6 piezas de un mismo set).
- **Combate contra varios enemigos de verdad** — hoy varios lo fingen con un
  «golpe extra» en vez de un segundo combatiente con su propio medidor de turno.
- Separación MVC más limpia en la capa de presentación.

## Proyecto y herramientas — planeado

Impacto alto:

- **Soporte multiplataforma** — aislar la única llamada a `msvcrt` (cancelar la
  auto-batalla con `q`) tras un pequeño helper para que el juego, los tests y el
  CI puedan correr también en Linux/macOS.
- **Captura / grabación de partida en el README** — ahora mismo el repo solo
  muestra badges y texto.
- **Protección de la rama `main`** — exigir el CI en verde (y opcionalmente una
  review) antes de fusionar.
- **Test de arranque (smoke test)** — un único test que ejecute `app.main()` con
  el input mockeado y salga, para cazar errores de wiring/imports (tanto `app.py`
  como `ui/menus.py` están excluidos de la cobertura).

Medio / pulido:

- **Comprobación estática de tipos** en el CI (`pyright` o `ty`), sin bloquear al principio.
- **`__version__`** en `src/juego_rol_texto/__init__.py` vía `importlib.metadata`.
- **Metadatos del repo en GitHub** — descripción, topics, imagen de social preview.
- Ampliar el conjunto de reglas de Ruff (`UP`, `B`, `SIM`, …).
- `concurrency:` en `ci.yml` para cancelar runs superados.
- Limpiar las notas de release autogeneradas; enlazar el CHANGELOG.
- Job opcional del CI que construya el paquete de PyInstaller sin publicarlo
  (solo cuando cambie el `.spec`) para detectar un `.spec` roto antes de un release.

## Ideas (sin compromiso)

- **Actualizaciones in situ** — que una build repartida pueda descargar una nueva
  versión sin reinstalar y sin tocar `saved_games/` / `config.ini`.
- Canal de feedback dentro del juego (una opción de menú que publique en Discord,
  como el informe de errores).
- Localización / soporte multi-idioma en el propio juego.
