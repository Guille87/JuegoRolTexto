# Game Design Document — Valeterna

<p align="center"><a href="GDD.md">English</a> · <a href="docs/GDD_es.md">Español</a></p>

Living design document for the game's evolution from a combat loop into a
small text RPG with a world, a story and NPCs. Version history lives in
[CHANGELOG.md](CHANGELOG.md); the phased delivery plan is in
[ROADMAP.md](ROADMAP.md); balance notes stay in [TODO.md](TODO.md).

Status: **planning**. Nothing here is built yet — this is the target.

---

## 1. Vision

Today the game is: pick an enemy from a list → fight → repeat. The goal is to
keep that combat (it works and is tuned) and wrap it in a **world worth moving
through**: named zones connected on a map, NPCs with dialogue, a main
questline that explains why you are marching toward the Dragón, side quests,
lore to find, and enemies that belong to places instead of to a flat list.

### Design pillars

1. **The combat stays the star.** The ATB system, the 14 enemies, the loot and
   crafting are the core. Everything new serves the loop of *get stronger →
   push deeper*, it does not replace it.
2. **Exploration is choice, not filler.** Every screen offers a real decision:
   push forward, farm, spend, talk, turn in a quest, go back for something.
3. **Serious dark fantasy.** Valeterna is a dying kingdom. No comic relief —
   NPCs have lost people, places are ruined, the tone is grim but not hopeless.
4. **Still a console game.** Numbered `input()` menus, `colorama` colour, no
   graphical window. The world is described, not drawn.
5. **Additive, not a rewrite.** Each phase ships on top of the last without
   breaking saves or the test suite.

---

## 2. Story — "La Brecha" (The Breach)

**Premise.** Years ago the **Dragón de Ceniza** razed the capital, Valeterna.
Its fire did more than burn: it cracked the veil between the mortal world and
the infernal planes. Through that **breach**, necromancers, fallen angels and
demons now spill into the kingdom, and the corruption spreads outward from the
ruined capital like rot from a wound.

The player is one of the few survivors of the razing who can still hold a
weapon. From **Piedrablanca**, the last free village, they set out to reach the
Dragón's lair and close the breach at its source — passing through six
increasingly corrupted regions to get there.

### Main questline (6 acts, one per region)

| Act | Region | Beat | Gate it opens |
|-----|--------|------|---------------|
| I | Los Yermos | Halbrand asks you to break the bandit raids strangling the village. | Bosque de los Susurros |
| II | Bosque de los Susurros | The hermit Cael explains the breach; a vengeful spirit is bound to a forest altar feeding it. | Cañón del Trueno |
| III | Cañón del Trueno | The druid Mirelle: the corruption flows down the old mountain road, and a Gólem seals the pass. | Torre de los Arcanos |
| IV | Torre de los Arcanos / Necrópolis | The apprentice Sella: the Mago's tower is channelling the breach and the Nigromante is raising the Necrópolis. | Ciudadela en Ruinas |
| V | Ciudadela en Ruinas | The paladin Aldric: the cathedral is the breach's heart; the Ángel Caído fell defending it and the Demonio holds it now. | Antesala del Dragón |
| VI | Antesala del Dragón | The breach's true anchor is the Dragón. End it. | — (ending) |

### Side quests (initial set)

- **La muñeca de Nia** (Los Yermos) — a child in Piedrablanca lost her doll when
  the family fled; it's in the abandoned bandit camp.
- **El encargo de Dorn** (Bosque) — the blacksmith wants Troll hide for a
  one-off legendary chest piece; ties into the forge.
- **El tomo prohibido de Sella** (Necrópolis) — recover a forbidden book from
  the tower library; unlocks a magic-damage crafting recipe.

Side quests are optional, give meaningful rewards (unique items, recipes,
gold), and never block the main path.

### Lore collectibles

Scattered "notes" (letters, journal pages, inscriptions) found while exploring.
Read once, then stored in a **Diario** you can re-read from the character menu.
Purely optional world-building.

---

## 3. World map

A graph of **zones** with free backtracking. From any zone you may travel to a
connected zone; from Piedrablanca (or a "camino" node) you may fast-travel to
any **visited** zone.

```
Piedrablanca (hub, no enemies)
   │
Los Yermos ── Bosque de los Susurros ── Cañón del Trueno ──
   Torre de los Arcanos / Necrópolis ── Ciudadela en Ruinas ── Antesala del Dragón
```

A zone unlocks when you defeat its **guardian** (its last enemy) or complete
the story beat that opens it. Piedrablanca is always reachable.

### Zones

| Zone | Theme | Enemies (from today's chain) | Sub-locations | Key NPCs |
|------|-------|------------------------------|---------------|----------|
| **Piedrablanca** | Last free village | — | Taberna, Herrería, Mercado, Refugio | Yerma (tabernera), Dorn (herrero), Halbrand (veterano), Nia |
| **Los Yermos** | Wilds around the village | Goblin, Huargo, Esqueleto, Bandido | Campamento de bandidos, Túmulo | Cael (ermitaño) |
| **Bosque de los Susurros** | Haunted forest | Orco, Espíritu Vengativo, Troll | Claro del altar, Cabaña quemada | Mirelle (druida) |
| **Cañón del Trueno** | Mountain pass, stone | Gárgola, Gólem de Piedra | Mina derrumbada, Puente colgante | Kort (minero) |
| **Torre de los Arcanos / Necrópolis** | Mage tower + graveyard | Mago, Nigromante | Biblioteca, Cripta | Sella (aprendiza) |
| **Ciudadela en Ruinas** | The razed capital, infernal ground | Ángel Caído, Demonio | Catedral rota, Plaza | Aldric (paladín) |
| **Antesala del Dragón** | The lair approach | Dragón (final boss) | — | — |

The **shop, forge, rest and save** points move into Piedrablanca's
sub-locations; a small "Mercado errante" and a "Fuego de campamento" (paid rest)
appear in later zones so you don't have to walk back every time.

---

## 4. Systems

### 4.1 Exploration loop

Replaces the flat `game_loop` menu. Inside a zone:

- **Explorar la zona** — a weighted roll: enemy encounter (from the zone pool),
  a discovery (materials / gold / a lore note / nothing), or a rare mini-event.
- **Ir a `<sub-lugar>`** — enter a sub-location: talk to an NPC, use a service
  (shop / forge / rest), turn in a quest.
- **Viajar** — move to a connected zone, or fast-travel to a visited one.
- **Personaje** — the always-available character menu: inventory, stats, equip
  weapon/armour, bestiary, diary, quests, save. (Extracted from today's
  `game_loop` so it works identically everywhere.)

Turbo auto-battle stays exactly as it is and is ideal for farming a zone's
encounter pool.

### 4.2 Dialogue

Lightweight. An NPC owns an ordered list of **dialogue nodes**; each node has
text, an optional condition (quest state / story flag / item held) and an
optional effect (start/advance a quest, set a flag, give an item, open a
service). No branching trees in v1 — the *available* node changes as the world
state changes, which is enough for a text RPG of this size.

### 4.3 Quests

`Quest`: id, title, description, an **objective** (kill N of enemy X, reach
zone Y, talk to NPC Z, collect item W, or a manual story flag), a **reward**
(gold / item / recipe / flag), and a **state** (`no_iniciada` / `activa` /
`completada` / `entregada`). Objective progress is checked from the combat and
exploration hooks that already fire (`_handle_victory`, arriving in a zone,
`Inventory.add_item`). A **Misiones** entry in the character menu lists active
quests and their progress.

### 4.4 Classes

Chosen once at character creation. Replaces "everyone is identical". Persisted
in the save; old saves default to **Vagabundo** (today's stats).

| Class | Identity | Effect |
|-------|----------|--------|
| **Vagabundo** | Balanced (today's character) | Current base stats and growth rates. The safe default. |
| **Guerrero** | Tank / bruiser | +HP, +armadura, +daño físico base; tankier growth. No magic. |
| **Pícaro** | Fast / crit | +velocidad, +evasión, +prob. crítico; agile growth. Fragile. |
| **Arcanista** | Magic damage | Lower HP/armour; **standard attack is magical** (`is_magical=True`), scaling with a new *poder mágico* stat — finally makes enemy `magic_resist` matter. |

Classes only touch character creation, `Stats`, the per-level `_*_GROWTH_RATE`
constants, and (Arcanista only) the player branch in `_execute_turn`.

### 4.5 Equipment set bonuses

`Armor` gains an optional `set_name`. `Player` counts equipped pieces per set
and applies **tiered bonuses at 2 and 4 pieces** (sets are 4 pieces each).
Sets are themed to regions and drop there:

| Set | Region | 2-piece | 4-piece |
|-----|--------|---------|---------|
| **Atavío del Proscrito** | Los Yermos | +evasión | First hit of each battle is a guaranteed crit |
| **Placas del Guardián** | Cañón del Trueno | +armadura | −10% to all physical damage taken |
| **Sudario del Nigromante** | Necrópolis | +resistencia mágica | 20% chance to reflect part of magic damage taken |
| **Vestiduras del Caído** | Ciudadela | +regeneración | Heal 15% of damage dealt |

Every `get_total_*` already sums equipment on demand — set bonuses hook the
same way. No `set` piece is strictly better than its slot's other options, same
rule as crafting today.

### 4.6 Status-inflicting weapons

`Weapon` gains `inflicts` = `{status, chance, duration, power}`. On a player
hit, roll `chance` and `enemy.apply_status(...)`. This requires **`Enemy` to
process status effects on its own turn** — a mirror of `Player.on_turn_start`
/ `on_turn_end` (burn/poison damage over time vs `max_health`, paralysis/freeze
skip a turn). The four elemental weapons get thematic infliction: veneno →
`veneno`, fuego → `quemado`, hielo → `congelado`, rayo → `paralizado`. Closes
the long-standing gap where enemies have `magic_resist` but nothing on the
player side ever uses statuses against them.

### 4.7 Arena mode

A location unlocked in Piedrablanca after clearing Act III (or via a ticket
item). Pick a difficulty tier → fight **N escalating waves** back to back,
enemies drawn from the zones you've cleared. The only healing between waves is
paid for in gold. Rewards scale with the wave reached: gold, a chance at set
pieces, and a cosmetic **título** shown on the stats screen. The save tracks
`arena_mejor_oleada`. Designed to pair with turbo auto-battle.

---

## 5. Save schema (v2)

Today's save (v1) holds player state + `unlocked_enemies` + `defeated_enemies`.
v2 adds a `mundo` block:

```
mundo:
  clase: "vagabundo"
  zona_actual: "piedrablanca"
  zonas_visitadas: ["piedrablanca", "los_yermos"]
  misiones: { "<id>": { estado, progreso } }
  banderas: ["breach_revelada", ...]
  diario: ["<id de nota>", ...]
  arena_mejor_oleada: 0
```

**Migration v1 → v2** (`persistence/save_load.py`, same pattern as the
armour-slot and `discovered_materials` back-fills): a save with no `mundo`
block is placed in the zone matching its `defeated_enemies` progress, class
`vagabundo`, no quests, no flags. `unlocked_enemies` / `defeated_enemies` stay
as the source of truth for zone gating during and after migration.

---

## 6. Technical architecture

New `world/` package, data-driven the same way `characters/enemies/` is
(one file per zone):

- `world/zone.py` — `Zone` dataclass (id, name, description, sub-locations,
  enemy pool, connections, gate condition).
- `world/npc.py` — `NPC`, `DialogueNode`.
- `world/quest.py` — `Quest`, quest state enum, objective/reward types.
- `world/map.py` — the zone graph, travel, fast-travel, gating.
- `world/data/*.py` — one module per zone wiring its NPCs, dialogue, encounters,
  lore notes.

Presentation:

- `ui/exploration.py` — the new zone loop (the exploration menu). `omit`ted
  from coverage like `ui/menus.py`.
- `ui/menus.py` — `game_loop` shrinks; the character sub-menu is extracted so it
  is reused by both the hub and every zone.
- `combat/battle.py` — untouched through phases 0.9–0.11 except: enemy status
  processing (0.9), the Arcanista magical standard attack (0.9), set-bonus
  hooks reading from `Player.get_total_*` (0.9).

Testing: all `world/` logic (gating, quest progress, dialogue conditions, map
travel, save migration) is unit-tested; the interactive exploration loop is
`omit`ted from the coverage metric, same as the existing menu code.

---

## 7. Phased delivery

Each phase is one release; **no release is tagged until the maintainer gives
the go-ahead** — features land on `main` via PRs and accumulate.

### v0.9.0 — Combat depth *(no world rework, lowest risk)*
- Status-inflicting weapons + `Enemy` status processing.
- Equipment set bonuses (4 sets).
- Character classes (4).
- Light rebalance for the above.

### v0.10.0 — The world, part 1
- Zone system + travel graph + exploration loop.
- Enemies moved into zones; the linear chain migrated to 6 zones + hub.
- Sub-locations; shop / forge / paid rest relocated.
- Random encounters + discoveries.
- Save migration v1 → v2.

### v0.11.0 — Story & quests
- Quest system; main questline "La Brecha" (6 acts) + 3 side quests.
- NPC dialogue conditional on quest/story state.
- Lore notes + Diario.

### v0.12.0 — The Arena & polish
- Arena / wave mode.
- Ed25519 signature on the auto-updater.
- Gameplay GIF, social-preview image.

### v1.0.0 — Valeterna
- Full rebalance of the 14-enemy chain (post `BASE_HIT_CHANCE` 90→100) across
  the questline's pacing.
- Full playthrough verified end to end.
- Cleaner MVC separation in the presentation layer.
- *(Stretch)* multi-enemy combat.

---

## 8. Open questions

- Encounter pacing: fixed number of encounters to "clear" a zone, or clear =
  defeat the guardian once and encounters continue for farming? *(leaning: the
  latter — guardian unlocks the next zone, the pool stays farmable.)*
- Does resting fully heal or a percentage? Does it cost a flat gold amount or
  scale with level?
- Fast-travel: free, or costs gold / a turn of encounters on the road?
- How much dialogue per NPC in v1 — a few fixed lines that swap on state, or a
  small menu of topics?
- Arena rewards: cosmetic titles only, or also a slow way to grind set pieces?
