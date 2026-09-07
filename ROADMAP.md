# Roadmap

<p align="center"><a href="ROADMAP.md">English</a> · <a href="docs/ROADMAP_es.md">Español</a></p>

A living document of what exists and what is planned. See the
[CHANGELOG](CHANGELOG.md) for the detailed version history and
[TODO.md](TODO.md) for the balance-tuning log.

## Done

- Active Time Battle combat, 1-vs-1, with crits, physical/magical damage,
  penetration, elemental weaknesses and status effects.
- 14 enemies with unique mechanics and a fixed unlock chain.
- 11 Diablo-style equipment slots; forge (12 recipes), shop, bestiary.
- Password-protected admin/debug panel.
- Mood-based background music.
- JSON save/load with backup; case-insensitive player-name recognition.
- On-disk error logging and optional opt-in Discord crash reports.
- CI (Ruff + tests on Python 3.10–3.13), coverage badge, release workflow (v0.3.0).

## Game — planned

- **Re-balance the 14-enemy chain** after `BASE_HIT_CHANCE` changed from 90 to
  100 — only the Goblin has been re-verified so far.
- **Armour set bonuses** (2/4/6-piece bonuses for themed sets).
- **Real multi-enemy fights** — today several enemies fake it with an "extra
  hit" instead of a second combatant with its own turn gauge.
- Cleaner MVC separation in the presentation layer.

## Project & tooling — planned

High impact:

- **Cross-platform support** — abstract the one `msvcrt` call (auto-battle
  cancel with `q`) behind a small helper so the game, the test suite and CI can
  also run on Linux/macOS.
- **README screenshot / gameplay recording** — the repo currently shows only
  badges and text.
- **Branch protection on `main`** — require CI green (and optionally one review)
  before merge.
- **Boot smoke test** — a single test that runs `app.main()` with mocked input
  and exits, so wiring/import errors are caught (both `app.py` and `ui/menus.py`
  are excluded from coverage).

Medium / polish:

- **Static type checking** in CI (`pyright` or `ty`), non-blocking at first.
- **`__version__`** in `src/juego_rol_texto/__init__.py` via `importlib.metadata`.
- **GitHub repo metadata** — description, topics, social-preview image.
- Expand the Ruff rule set (`UP`, `B`, `SIM`, …).
- `concurrency:` in `ci.yml` to cancel superseded runs.
- Tidy the auto-generated release notes; link the CHANGELOG.
- Optional CI job that builds the PyInstaller package without publishing
  (only when the `.spec` changes) so a broken spec is caught before a release.

## Ideas (no commitment)

- **In-place updates** — let a distributed build pull a new version without a
  full reinstall and without touching `saved_games/` / `config.ini`.
- In-game feedback channel (a menu option that posts to Discord, like the crash report).
- Localisation / multi-language support in the game itself.
