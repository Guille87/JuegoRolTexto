# Changelog

<p align="center"><a href="../CHANGELOG.md">English</a> · <a href="CHANGELOG_es.md">Español</a></p>

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y este proyecto sigue el [Versionado Semántico](https://semver.org/lang/es/).

## [Unreleased]

### Añadido

- Entrada de teclado no bloqueante y multiplataforma (`ui/keyboard.py`); el juego
  y la suite de tests ya no necesitan Windows.
- Comprobación estática de tipos con `pyright` (modo `basic`) como check obligatorio del CI.
- Smoke test de arranque (`app.main()` arranca y sale limpio).

### Cambiado

- El CI ejecuta la matriz de tests en Linux (3.10–3.13) más un job de Windows.
- Protección de la rama `main`: PR + CI en verde obligatorios; el badge de
  cobertura vive en una rama huérfana `badges`.
- El conjunto de reglas de Ruff añade `UP`, `B` y `SIM`.

## [0.3.0] - 2026-09-07

Primera versión etiquetada. Añade el informe de errores, la infraestructura de
proyecto y una gran pasada de cobertura de tests sobre la línea base 0.2.0.

### Añadido

- Registro de errores en disco: `logs/juego.log` (rotativo) y un
  `logs/crash_<timestamp>.txt` por cada cierre inesperado, manteniendo la
  ventana abierta para que quien juega con el `.exe` pueda leer la ruta.
- Informe opcional (opt-in) del cierre inesperado a un webhook de Discord, con
  mención al desarrollador y las rutas del perfil / nombre de usuario
  censurados. Se configura en `config/secrets.py`; se activa/desactiva en *Opciones*.
- `config/secrets.py` (no versionado) para el webhook de Discord, el ID de
  mención y el hash de la contraseña de admin, con la plantilla
  `config/secrets.example.py` versionada y el accesor tolerante `config/secret_store.py`.
- El jugador se reconoce por el nombre con el que registró la partida: la carga
  no distingue mayúsculas/minúsculas y se restaura el nombre canónico; *Nueva
  Partida* rechaza un nombre que ya tiene partida guardada.
- Integración continua (GitHub Actions): Ruff y la suite de tests en Python
  3.10–3.13 (Windows), más un badge de cobertura que se autocommitea.
- Workflow de release: al empujar un tag `vX.Y.Z` se construye el paquete de
  Windows y se adjunta al GitHub Release.
- Archivos de proyecto: `LICENSE` (MIT), `CONTRIBUTING`, `ROADMAP`, este
  `CHANGELOG`, `CODE_OF_CONDUCT`, `SECURITY`, plantillas de issue/PR, Dependabot, `.editorconfig`.
- Ruff como linter y formateador (conjunto de reglas conservador), configurado en `pyproject.toml`.
- Pasada de cobertura de tests: 70% → 91% (238 tests). `ui/menus.py` y `app.py`
  se excluyen de la métrica por ser pegamento interactivo.

### Corregido

- El juego se cerraba al abrir el inventario teniendo un material de crafteo
  (los objetos sin estadísticas no implementaban `get_stats_info()`).
- El error de audio `Audio device hasn't been opened` al salir, provocado por el
  hilo watchdog de música ejecutándose tras cerrarse el mezclador.

### Eliminado

- `tools/settings_admin.py` — código muerto (una ventana de ajustes en Tkinter sin usar).

## [0.2.0] - 2026-09-06

Línea base: el estado del juego cuando se empezó a llevar este changelog. Los
cambios anteriores no se registraron formalmente.

### Añadido

- Sistema de turnos ATB (Active Time Battle), 1 contra 1.
- 14 enemigos con mecánicas propias y una cadena de desbloqueo fija.
- 11 huecos de equipo estilo Diablo con estadística base por hueco y secundarias.
- Herrería (12 recetas), tienda y bestiario.
- Panel de administración/debug protegido con contraseña.
- Música de fondo por «mood» (aventura / combate).
- Guardado/carga en JSON + base64 con copia de seguridad.
- Empaquetado con PyInstaller para Windows.

## [0.1.0] - 2024-05-04

### Añadido

- Versión inicial: combate por turnos básico en consola.

[Unreleased]: https://github.com/Guille87/JuegoRolTexto/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/Guille87/JuegoRolTexto/releases/tag/v0.3.0
