# Changelog

<p align="center"><a href="CHANGELOG.md">English</a> · <a href="docs/CHANGELOG_es.md">Español</a></p>

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed

- Auto-update: the relauncher `.bat` is now started with `os.startfile`
  (ShellExecute) instead of `subprocess.Popen`, which intermittently failed with
  `0xC0000142` (cmd.exe init failure) when spawned during the game's shutdown.
  A short grace period was also added before the game exits.

## [0.7.0] - 2026-09-08

### Added

- Battle start always shows both combat sheets (player and enemy) regardless of
  turn order; an enemy you haven't defeated yet is shown as `???`.
- Turbo auto-battle: a second auto-battle option with no turn pauses, no
  per-turn health bar and no victory prompt — for fast farming of enemies you
  can already beat easily.
- Stat sheets (player, enemy info, bestiary) are colour-coded per stat.
- Any text mentioning a status effect is colour-coded consistently everywhere:
  poison green, burn red, paralysis yellow, freeze blue.

### Changed

- The Goblin never ambushes until it has been defeated at least once (the very
  first fight of the game is always clean).

## [0.6.0] - 2026-09-08

### Fixed

- Auto-update apply step: the relauncher `.bat` now runs in its own console
  (so it survives the game closing and its commands actually work), waits for
  the game by process name, mirrors the new build with `robocopy /MIR` (removing
  stale files — notably the old version's `*.dist-info`, which left the updated
  game still reporting the previous version), protects `config.ini` and the save
  folder, and writes an `apply.log`.

## [0.5.0] - 2026-09-08

### Added

- "Defender" combat action: spend your turn to halve the damage you take until
  your next turn.
- Antidote potion: instantly clears poison, burn, paralysis and freeze. Sold in
  the shop.
- The game version is shown under the main-menu and in-game menu titles.

## [0.4.0] - 2026-09-08

### Added

- Cross-platform, non-blocking keyboard input (`ui/keyboard.py`); the game and
  test suite no longer require Windows.
- Static type checking with `pyright` (basic mode) as a required CI check.
- Boot smoke test (`app.main()` starts and exits cleanly).
- README screenshot generated from a real battle (`tools/capture_screenshot.py`).
- CI `build-check` — builds the `.exe` when packaging files change.
- Auto-update (frozen build): checks GitHub Releases on startup and shows a
  notice when a newer version is available; toggle and manual check in Options.
- Auto-update can now download, verify (SHA-256 against the Release's
  `SHA256SUMS`) and apply an update, restarting the game via a `.bat` relauncher
  without touching `saved_games/` or `config.ini`.
- Release workflow publishes a `SHA256SUMS` file alongside the Windows zip.

### Changed

- CI runs the test matrix on Linux (3.10–3.13) plus one Windows job.
- Branch protection on `main`: PR + green CI required; the coverage badge lives
  on an orphan `badges` branch.
- Ruff rule set extended with `UP`, `B` and `SIM`.

## [0.3.0] - 2026-09-07

First tagged release. Adds error reporting, project infrastructure and a large
test-coverage pass on top of the 0.2.0 baseline.

### Added

- On-disk error logging: `logs/juego.log` (rotating) and a standalone
  `logs/crash_<timestamp>.txt` per crash, with the window held open so a
  packaged `.exe` player can read the path.
- Optional, opt-in crash report to a Discord webhook, with the developer
  mentioned and OS username / home paths scrubbed. Configured via
  `config/secrets.py`; toggleable under *Options*.
- `config/secrets.py` (git-ignored) for the Discord webhook, mention ID and the
  admin password hash, with a committed `config/secrets.example.py` template and
  a tolerant `config/secret_store.py` accessor.
- The player is now recognised by the name they registered the save with:
  loading is case-insensitive and the canonical name is restored; *New Game*
  refuses a name that already has a save.
- Continuous integration (GitHub Actions): Ruff and the test suite on Python
  3.10–3.13 (Windows), plus a self-committed coverage badge.
- Release workflow: tagging `vX.Y.Z` builds the Windows package and attaches it
  to the GitHub Release.
- Project files: `LICENSE` (MIT), `CONTRIBUTING`, `ROADMAP`, this `CHANGELOG`,
  `CODE_OF_CONDUCT`, `SECURITY`, issue/PR templates, Dependabot, `.editorconfig`.
- Ruff as linter and formatter (conservative rule set), configured in `pyproject.toml`.
- Test-coverage pass: 70% → 91% (238 tests). `ui/menus.py` and `app.py` are
  excluded from the metric as interactive glue.

### Fixed

- The game crashed when opening the inventory while holding a crafting material
  (items with no stats did not implement `get_stats_info()`).
- Audio error `Audio device hasn't been opened` printed on exit, caused by the
  music watchdog thread running after the mixer was closed.

### Removed

- `tools/settings_admin.py` — dead code (an unused Tkinter settings window).

## [0.2.0] - 2026-09-06

Baseline: the state of the game when this changelog started. Earlier changes
were not formally tracked.

### Added

- Active Time Battle turn system, 1-vs-1.
- 14 enemies with unique mechanics and a fixed unlock chain.
- 11 Diablo-style equipment slots with a per-slot base stat and secondary stats.
- Forge (12 recipes), shop and bestiary.
- Password-protected admin/debug panel.
- Mood-based background music (adventure / battle).
- JSON + base64 save/load with backup fallback.
- PyInstaller packaging for Windows.

## [0.1.0] - 2024-05-04

### Added

- Initial version: basic console turn-based combat.

[Unreleased]: https://github.com/Guille87/JuegoRolTexto/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/Guille87/JuegoRolTexto/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/Guille87/JuegoRolTexto/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/Guille87/JuegoRolTexto/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Guille87/JuegoRolTexto/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Guille87/JuegoRolTexto/releases/tag/v0.3.0
