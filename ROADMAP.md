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
- CI (Ruff + tests on Python 3.10–3.13), coverage badge, release workflow.

## Next / under consideration

- **Re-balance the 14-enemy chain** after `BASE_HIT_CHANCE` changed from 90 to
  100 — only the Goblin has been re-verified so far.
- **Armour set bonuses** (2/4/6-piece bonuses for themed sets).
- **Real multi-enemy fights** — today several enemies fake it with an "extra
  hit" instead of a second combatant with its own turn gauge.
- **Cross-platform auto-battle** — currently Windows-only because of `msvcrt`.
- Expand the Ruff rule set (`UP`, `B`, …) and raise coverage of the UI layer.
- Cleaner MVC separation in the presentation layer.

## Ideas (no commitment)

- In-game feedback channel (a menu option that posts to Discord, like the crash report).
- Localisation / multi-language support in the game itself.
