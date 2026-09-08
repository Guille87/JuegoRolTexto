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
- CI (Ruff, pyright, tests en Python 3.10–3.13 Linux + un job de Windows), badge de cobertura, workflow de release (v0.9.0).
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
| **v0.9.0** | Fundaciones | capa de strings i18n + migrar el núcleo de combate/menús · modelo de afinidades completo (×1.5/×2 débil, ×0.5/×0.25 resiste, ×0 inmune = sin daño, sin estado) + los 3 elementos nuevos como datos · el jugador y `Enemy` procesan estados (armas que infligen estados) · `quemado` solo penaliza el ataque físico |
| **v0.10.0** | Clases y primeras habilidades | 4 clases al crear · stat `poder mágico` · sistema de habilidades (pasivas / activas con enfriamiento) · menú "Habilidades" + elegir 4 activas equipadas · las primeras ~2-3 habilidades por clase |
| **v0.11.0** | Equipo y afinidades reales | 4 conjuntos de armadura · resistencia elemental en armadura · debilidades / resistencias / inmunidades reales en los 14 enemigos actuales · armas elementales nuevas (sagrado / oscuridad / arcano) · reacciones elementales |
| **v0.12.0** | El mundo, parte 1 | zonas + mapa + bucle de exploración · posada / descanso (coste por nivel) · viaje frontera + viaje rápido · migración de guardado v2 · tienda / herrería reubicadas · encuentros aleatorios + hallazgos |
| **v0.13.0** | Diálogo y NPCs | diálogo ramificado con respuestas del jugador · conversaciones únicas vs repetibles · NPCs de Piedrablanca + las 6 regiones actuales · notas de lore + Diario |
| **v0.14.0** | Bestiario y enemigos I | bestiario progresivo · herramienta de presupuesto de poder (fija la curva de nivel) · Los Yermos + Bosque rellenados a ~10 · habilidades de clase de nivel medio atadas a esos enemigos |
| **v0.15.0** | Enemigos II | Ciénaga (nueva) + Cañón + Torre/Necrópolis a ~10 · escalado del botín (únicos + comunes tirados) · drop-scaling entre zonas · más habilidades de clase |
| **v0.16.0** | Enemigos III | Ciudadela a ~10 · habilidades de clase de hito alto · misiones secundarias de esas regiones |
| **v0.17.0** | Historia principal | sistema de misiones · questline "La Brecha" (7 actos) enganchada a los NPCs / guardianes existentes · progresión por historia en vez de elegir enemigo |
| **v0.18.0** | La Arena | modo de oleadas crecientes · recompensas de Arena (títulos + algunas piezas de conjunto + un único difícil) |
| **más adelante** | Endgame y pulido | roster completo → ajuste final del Dragón + El Corazón de la Brecha · rebalanceo completo de la cadena · firma Ed25519 del updater · GIF de gameplay · MVC más limpia · *(ampliación)* combate multi-enemigo · *(muy a largo plazo)* posibles actos nuevos |
| **1.0** | — | la declara el mantenedor cuando el juego esté listo para salir |

## Tareas menores de herramientas (sin fecha)

- Extender `pyright` para que revise también `tests/`, y subir de `basic` a `standard`.
- Limpiar las notas de release autogeneradas; enlazar el CHANGELOG.
- Canal de feedback dentro del juego (una opción de menú que publique en Discord,
  como el informe de errores).
- Localización / soporte multi-idioma en el propio juego.
