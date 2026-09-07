# Juego de Rol por Turnos

<p align="center"><a href="../README.md">English</a> · <a href="README_es.md">Español</a></p>

[![CI](https://github.com/Guille87/JuegoRolTexto/actions/workflows/ci.yml/badge.svg)](https://github.com/Guille87/JuegoRolTexto/actions/workflows/ci.yml)
[![Coverage](../.github/badges/coverage.svg)](https://github.com/Guille87/JuegoRolTexto/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Un RPG de batalla por turnos en consola, en español, escrito en Python. Enfréntate
a una cadena de 14 enemigos, gestiona equipo y pociones, fabrica objetos en la
herrería y haz crecer a tu personaje. Se juega enteramente en la terminal — no hay
ventana gráfica; `colorama` da color y `pygame` (solo el mixer) pone la música.

## Características

- Combate **ATB (Active Time Battle)**: el combatiente más rápido actúa más veces,
  no es una alternancia estricta.
- **14 enemigos** con mecánicas propias y una cadena de desbloqueo fija que termina en el Dragón.
- **11 huecos de equipo estilo Diablo**, cada uno con una estadística base garantizada más secundarias aleatorias.
- **Herrería** (12 recetas), **tienda** y un **bestiario** que se completa a medida que ganas.
- Daño físico y mágico, penetración, debilidades elementales y efectos de estado.
- Guardado/carga en JSON con copia de seguridad automática; registro de errores en disco e informe opcional a Discord.

## Requisitos

- Python **3.10 o superior** (la CI prueba 3.10–3.13).
- **Solo Windows** por ahora: el modo auto-batalla usa `msvcrt` para poder cancelarse con `q`.

## Instalación

```powershell
git clone https://github.com/Guille87/JuegoRolTexto.git
cd JuegoRolTexto
python -m venv env
.\env\Scripts\activate
pip install -e ".[dev]"
```

El extra `[dev]` añade `pytest`, `pytest-cov` y `ruff`. Si solo quieres jugar, `pip install -e .` es suficiente.

## Ejecutar

```bash
python main.py
# o: python -m juego_rol_texto
# o, tras instalar: juego-rol-texto
```

## Tests

```bash
pytest                              # ejecutar la suite
pytest --cov=juego_rol_texto        # con cobertura
ruff check . && ruff format --check .
```

## Generar un ejecutable

```powershell
pip install pyinstaller
pyinstaller JuegoRolTexto.spec
```

El resultado queda en `dist\JuegoRolTexto\` — copia la **carpeta entera** (necesita
los assets y las DLLs que la acompañan). `config.ini`, `saved_games\` y `logs\` se
crean junto al `.exe`. Usa `--onedir` (el `.spec` ya lo hace), nunca `--onefile`.

El informe opcional de errores a Discord vive en `src/juego_rol_texto/config/secrets.py`
(no versionado). Copia `config/secrets.example.py` a `config/secrets.py` y rellénalo
antes de compilar; sin él el juego funciona igual, solo sin informes de errores.

## Documentación

- [Guía de contribución](CONTRIBUTING_es.md) — flujo de trabajo y convenciones.
- [Roadmap](ROADMAP_es.md) — qué está hecho y qué está planeado.
- [Changelog](CHANGELOG_es.md) — historial de versiones.
- [CLAUDE.md](../CLAUDE.md) — notas de arquitectura detalladas (en inglés).
- [TODO.md](../TODO.md) — historial detallado de decisiones de balance.

## Licencia

[MIT](../LICENSE) © 2026 Guillermo Amado.
