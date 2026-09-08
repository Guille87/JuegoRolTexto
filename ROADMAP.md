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
- CI (Ruff, pyright, tests on Python 3.10–3.13 Linux + one Windows job), coverage badge, release workflow (v0.5.0).
- Branch protection on `main` (PR + `all-green` check); boot smoke test.
- Cross-platform keyboard input (`ui/keyboard.py`) — the game and test suite no longer need Windows.
- Ruff `UP`/`B`/`SIM`, `__version__` via `importlib.metadata`, CI `concurrency`.
- README screenshot; repo description and topics.
- CI `build-check` — builds the `.exe` when packaging files change.
- **Auto-updater** — the frozen build checks GitHub Releases, and can download,
  verify (SHA-256) and apply an update, restarting itself without a reinstall and
  without touching `saved_games/` / `config.ini`.

## Game — planned

- **Re-balance the 14-enemy chain** after `BASE_HIT_CHANCE` changed from 90 to
  100 — only the Goblin has been re-verified so far.
- **Armour set bonuses** (2/4/6-piece bonuses for themed sets).
- **Real multi-enemy fights** — today several enemies fake it with an "extra
  hit" instead of a second combatant with its own turn gauge.
- Cleaner MVC separation in the presentation layer.

## Project & tooling — planned

Medium / polish:

- **Ed25519 signature** on the auto-update, on top of the current SHA-256 +
  HTTPS, to also defend against a compromised GitHub account (see `SECURITY.md`).

- **Gameplay recording (GIF / asciinema)** for the README, beyond the static screenshot.
- **Social-preview image** for the repo (via GitHub settings).
- Extend `pyright` to also check `tests/`, and step up from `basic` to `standard`.
- Tidy the auto-generated release notes; link the CHANGELOG.

## Ideas (no commitment)

- In-game feedback channel (a menu option that posts to Discord, like the crash report).
- Localisation / multi-language support in the game itself.
