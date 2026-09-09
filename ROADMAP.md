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
- CI (Ruff, pyright, tests on Python 3.10–3.13 Linux + one Windows job), coverage badge, release workflow (v0.10.0).
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
around it — 7 zones on a map with free backtracking, ~10 enemies per zone
(~70 total), 4 classes, level-learned skills, 7 damage elements with
weaknesses / resistances / immunities, a dark-fantasy questline. Each phase is
one release; **releases are tagged only on the maintainer's go-ahead** —
features accumulate on `main` via PRs. There is **no 1.0 target**; pre-release
versions ship until the game is launch-ready. Order may shuffle.

| Phase | Theme | Contents |
|-------|-------|----------|
| **v0.9.0** | Foundations | i18n strings layer + migrate combat/menu core · full affinity model (×1.5/×2 weak, ×0.5/×0.25 resist, ×0 immune = no damage, no status) + the 3 new elements as data · player & `Enemy` status processing (status-inflicting weapons) · `quemado` penalises physical attack only |
| **v0.10.0** | Classes & first skills | 4 classes at creation · `poder mágico` stat · skill system (passives / cooldown actives) · "Habilidades" menu + choose 4 equipped actives · first ~2–3 skills per class |
| **v0.11.0** | Gear & real affinities | 4 armour sets · elemental resistance on armour · real weaknesses / resistances / immunities on the current 14 enemies · new elemental weapons (sagrado / oscuridad / arcano) · elemental reactions |
| **v0.12.0** | The world, part 1 | zones + map + exploration loop · inn / rest (cost scales with level) · frontier travel + fast-travel · save migration v2 · shop / forge relocated · random encounters + discoveries |
| **v0.13.0** | Dialogue & NPCs | branching dialogue with player choices · one-time vs repeatable conversations · NPCs for Piedrablanca + the 6 existing regions · lore notes + Diario |
| **v0.14.0** | Bestiary & enemies I | progressive bestiary · power-budget tool (sets the level curve) · Los Yermos + Bosque fleshed to ~10 · mid-progression class skills tied to those enemies |
| **v0.15.0** | Enemies II | Ciénaga (new) + Cañón + Torre/Necrópolis to ~10 · loot scaling (uniques + rolled commons) · cross-zone drop-scaling · more class skills |
| **v0.16.0** | Enemies III | Ciudadela to ~10 · high-milestone class skills · side quests for those regions |
| **v0.17.0** | Main story | quest system · "La Brecha" questline (7 acts) wired to the existing NPCs / guardians · progression by story instead of picking an enemy |
| **v0.18.0** | The Arena | escalating-wave mode · Arena rewards (titles + some set pieces + a hard-to-get unique) |
| **later** | Endgame & polish | full roster → Dragón final tuning + El Corazón de la Brecha · full chain rebalance · Ed25519 updater signature · gameplay GIF · cleaner MVC · *(stretch)* multi-enemy combat · *(very long term)* possible extra acts |
| **1.0** | — | called by the maintainer when the game is launch-ready |

## Smaller tooling items (unscheduled)

- Extend `pyright` to also check `tests/`, and step up from `basic` to `standard`.
- Tidy the auto-generated release notes; link the CHANGELOG.
- In-game feedback channel (a menu option that posts to Discord, like the crash report).
- Localisation / multi-language support in the game itself.
