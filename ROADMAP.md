# Roadmap

<p align="center"><a href="ROADMAP.md">English</a> · <a href="docs/ROADMAP_es.md">Español</a></p>

A living document of what exists and what is planned. See the
[CHANGELOG](CHANGELOG.md) for the detailed version history, the
[GDD](GDD.md) for the full design of the world/story/RPG direction, and
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
- CI (Ruff, pyright, tests on Python 3.10–3.13 Linux + one Windows job), coverage badge, release workflow (v0.8.0).
- Branch protection on `main` (PR + `all-green` check); boot smoke test.
- Cross-platform keyboard input (`ui/keyboard.py`) — the game and test suite no longer need Windows.
- Ruff `UP`/`B`/`SIM`, `__version__` via `importlib.metadata`, CI `concurrency`.
- README screenshot; repo description and topics.
- CI `build-check` — builds the `.exe` when packaging files change.
- **Auto-updater** — the frozen build checks GitHub Releases, and can download,
  verify (SHA-256) and apply an update, restarting itself without a reinstall and
  without touching `saved_games/` / `config.ini`.

## Planned — phased plan

Full design in the [GDD](GDD.md). Direction: keep the combat, build a world
around it (zones on a map with free backtracking, NPCs, a dark-fantasy
questline). Each phase is one release; **releases are tagged only on the
maintainer's go-ahead** — features accumulate on `main` via PRs.

### v0.9.0 — Combat depth *(no world rework)*
- Status-inflicting weapons + `Enemy` status processing (closes the "enemies
  have `magic_resist` but nothing uses statuses on them" gap).
- Equipment set bonuses (4 themed sets, tiers at 2/4 pieces).
- Character classes at creation (Vagabundo / Guerrero / Pícaro / Arcanista).
- Light rebalance for the above.

### v0.10.0 — The world, part 1
- Zone system + travel graph + exploration loop replacing the flat menu.
- The 14-enemy chain migrated into 6 zones + a hub village.
- Sub-locations; shop / forge / paid rest relocated. Random encounters +
  discoveries. Save migration v1 → v2.

### v0.11.0 — Story & quests
- Quest system; main questline "La Brecha" (6 acts) + 3 side quests.
- NPC dialogue conditional on quest/story state. Lore notes + Diario.

### v0.12.0 — The Arena & polish
- Arena / escalating-wave mode (pairs with turbo auto-battle).
- Ed25519 signature on the auto-updater (on top of SHA-256 + HTTPS — see
  `SECURITY.md`).
- Gameplay GIF, social-preview image.

### v1.0.0 — Valeterna
- Full rebalance of the 14-enemy chain (post `BASE_HIT_CHANCE` 90→100) against
  the questline pacing.
- Full playthrough verified end to end.
- Cleaner MVC separation in the presentation layer.
- *(Stretch)* real multi-enemy combat — today several enemies fake it with an
  "extra hit" instead of a second combatant with its own turn gauge.

## Smaller tooling items (unscheduled)

- Extend `pyright` to also check `tests/`, and step up from `basic` to `standard`.
- Tidy the auto-generated release notes; link the CHANGELOG.
- In-game feedback channel (a menu option that posts to Discord, like the crash report).
- Localisation / multi-language support in the game itself.
