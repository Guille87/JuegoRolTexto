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
construir un mundo alrededor — 7 zonas en un mapa con vuelta atrás libre, ~10
enemigos por zona (~70 en total), 4 clases, habilidades por nivel, 7 elementos
de daño con debilidades / resistencias / inmunidades, una questline de fantasía
oscura. Cada fase es una release; **las releases se etiquetan solo con la luz
verde del mantenedor** — las funcionalidades se acumulan en `main` por PRs. **No
hay objetivo de 1.0**; se publican versiones pre-lanzamiento hasta que el juego
esté listo para salir. El orden puede cambiar.

| Fase | Tema | Contenido |
|------|------|-----------|
| **v0.9.0** | Fundaciones | capa de strings i18n + migrar el núcleo de combate/menús · modelo de afinidades de enemigos (debilidades / resistencias / inmunidades a estados) + los 3 elementos nuevos como datos · armas que infligen estados + procesado de estados en `Enemy` |
| **v0.10.0** | Clases y habilidades | 4 clases al crear · árboles de habilidades por clase (pasivas + activas con enfriamiento) · menú "Habilidades" en combate · stat `poder mágico` |
| **v0.11.0** | Equipo y afinidades | 4 conjuntos de armadura · resistencia elemental en armadura · debilidades / resistencias / inmunidades reales en los 14 enemigos actuales · armas elementales nuevas (sagrado / oscuridad / arcano) |
| **v0.12.0** | El mundo, parte 1 | zonas + mapa + bucle de exploración + migración de guardado v2 · tienda / herrería / descanso reubicados · encuentros aleatorios + hallazgos |
| **v0.13.0** | Bestiario y enemigos I | bestiario progresivo · herramienta de presupuesto de poder · rellenar 2–3 zonas a ~10 enemigos cada una |
| **v0.14.0** | Enemigos II | terminar el roster hasta ~70 · escalado del botín (únicos + comunes tirados) |
| **v0.15.0** | Historia y misiones | sistema de misiones · questline "La Brecha" (7 actos) + secundarias · diálogo de NPC · notas de lore + Diario |
| **v0.16.0** | La Arena | modo de oleadas crecientes |
| **más adelante** | Endgame y pulido | ajuste final del Dragón (necesita el roster completo) · rebalanceo completo de la cadena · firma Ed25519 del updater · GIF de gameplay · MVC más limpia · *(ampliación)* combate multi-enemigo |
| **1.0** | — | la declara el mantenedor cuando el juego esté listo para salir |

## Tareas menores de herramientas (sin fecha)

- Extender `pyright` para que revise también `tests/`, y subir de `basic` a `standard`.
- Limpiar las notas de release autogeneradas; enlazar el CHANGELOG.
- Canal de feedback dentro del juego (una opción de menú que publique en Discord,
  como el informe de errores).
- Localización / soporte multi-idioma en el propio juego.
