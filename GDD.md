# Game Design Document — Valeterna

<p align="center"><a href="GDD.md">English</a> · <a href="docs/GDD_es.md">Español</a></p>

Living design document for the game's evolution from a combat loop into a text
RPG with a world, a story, NPCs, character classes, skills and a large bestiary.
Version history: [CHANGELOG.md](CHANGELOG.md). Delivery plan:
[ROADMAP.md](ROADMAP.md). Balance notes: [TODO.md](TODO.md).

**Status: planning.** Almost nothing here is built yet — this is the target, and
it will keep growing. There is **no 1.0 target**: the game ships pre-release
versions until the maintainer decides it is launch-ready.

---

## 1. Vision & pillars

Today the game is: pick an enemy from a list → fight → repeat. The goal is to
keep that combat (it works and is tuned) and wrap it in a **world worth moving
through**: named zones on a map, ~10 enemies per zone, NPCs with dialogue, a
dark-fantasy questline, classes, level-learned skills, seven damage elements
with weaknesses/resistances/immunities.

1. **The combat stays the star.** The ATB system, the enemies, the loot and
   crafting are the core. Everything new deepens the loop of *get stronger →
   push deeper*, it does not replace it.
2. **Exploration is choice, not filler.** Every screen offers a real decision:
   push forward, farm, spend, talk, turn in a quest, go back for something.
3. **Serious dark fantasy.** Valeterna is a dying kingdom. No comic relief.
4. **Still a console game.** Numbered `input()` menus, `colorama` colour, no
   window. The world is described, not drawn.
5. **Additive, not a rewrite.** Each phase ships on top of the last without
   breaking saves or the test suite.
6. **Translatable from the start.** All new player-facing text goes through a
   strings layer (`i18n`) so multi-language is cheap later (see §9.1).

---

## 2. Story — "La Brecha" (The Breach)

**Premise.** Years ago the **Dragón de Ceniza** razed the capital, Valeterna.
Its fire cracked the veil between the mortal world and the infernal planes.
Through that **breach**, necromancers, fallen angels and demons spill into the
kingdom, and corruption spreads outward from the ruined capital like rot from a
wound. The player is one of the few survivors of the razing who can still hold
a weapon; from **Piedrablanca**, the last free village, they set out to reach
the Dragón's lair and close the breach at its source.

### Main questline — 7 acts, one per region

| Act | Region | Beat | Opens |
|-----|--------|------|-------|
| I | Los Yermos | Halbrand: break the bandit raids strangling the village. | Bosque de los Susurros |
| II | Bosque de los Susurros | Cael explains the breach; a spirit is bound to a forest altar feeding it. | Ciénaga de los Ahogados |
| III | Ciénaga de los Ahogados | Something older than the breach stirs in the drowned marsh and the corruption pools here. | Cañón del Trueno |
| IV | Cañón del Trueno | Mirelle: the corruption flows down the old mountain road; a Gólem seals the pass. | Torre de los Arcanos |
| V | Torre de los Arcanos / Necrópolis | Sella: the mage tower channels the breach; the Nigromante is raising the Necrópolis. | Ciudadela en Ruinas |
| VI | Ciudadela en Ruinas | Aldric: the cathedral is the breach's heart; the Ángel Caído fell defending it, the Demonio holds it now. | Antesala del Dragón |
| VII | Antesala del Dragón | The breach's true anchor is the Dragón. End it. | ending |

*(A new region, **Ciénaga de los Ahogados**, is added between forest and canyon
to make room for 7 zones × ~10 enemies. Its roster is new design.)*

### Side quests (initial set, optional, never block the path)

- **La muñeca de Nia** (Los Yermos) — a child's doll lost in the bandit camp.
- **El encargo de Dorn** (Bosque) — Troll hide for a one-off legendary chest.
- **El tomo prohibido de Sella** (Necrópolis) — unlocks a magic-damage recipe.
- More to be designed per region.

### Lore collectibles

Notes (letters, journal pages, inscriptions) found while exploring. Read once,
then stored in a **Diario** re-readable from the character menu. Optional.

---

## 3. World — zones & map

A graph of **zones** with free backtracking. From any zone you travel to a
connected zone; from Piedrablanca (or a "camino" node) you fast-travel to any
**visited** zone. A zone unlocks when you defeat its **guardian** (a mini-boss)
or complete the story beat that opens it. Piedrablanca is always reachable.

```
Piedrablanca (hub, no enemies)
   │
Los Yermos ── Bosque de los Susurros ── Ciénaga de los Ahogados ── Cañón del Trueno ──
   Torre de los Arcanos / Necrópolis ── Ciudadela en Ruinas ── Antesala del Dragón
```

| Zone | Theme | Backbone enemies (existing) | Sub-locations | Key NPCs |
|------|-------|-----------------------------|---------------|----------|
| **Piedrablanca** | Last free village | — | Taberna, Herrería, Mercado, Refugio | Yerma, Dorn, Halbrand, Nia |
| **Los Yermos** | Wilds around the village | Goblin, Huargo, Esqueleto, Bandido | Campamento de bandidos, Túmulo | Cael |
| **Bosque de los Susurros** | Haunted forest | Orco, Espíritu Vengativo, Troll | Claro del altar, Cabaña quemada | Mirelle |
| **Ciénaga de los Ahogados** | Drowned marsh | *(all new)* | Templo hundido, Embarcadero podrido | *(new)* |
| **Cañón del Trueno** | Mountain pass, stone | Gárgola, Gólem de Piedra | Mina derrumbada, Puente colgante | Kort |
| **Torre de los Arcanos / Necrópolis** | Mage tower + graveyard | Mago, Nigromante | Biblioteca, Cripta | Sella |
| **Ciudadela en Ruinas** | The razed capital, infernal ground | Ángel Caído, Demonio | Catedral rota, Plaza | Aldric |
| **Antesala del Dragón** | The lair approach | Dragón (final boss) | — | — |

Shop / forge / rest / save move into Piedrablanca's sub-locations; a "Mercado
errante" and a "Fuego de campamento" (paid rest) appear in later zones.

---

## 4. Enemies — roster design

**Target: ~10 enemies per zone, ~70 total.** The current 14 are the *backbone*
(the mechanically-unique named ones); the rest is new design. The **Dragón is
designed last**, once the whole roster exists, so it can sit strictly above
everything as the hardest fight in the game — its final stats are unknowable
until then and are a deliberate open item.

### 4.1 Per-zone structure

Each zone's ~10 enemies break down as:

- **1 guardian** — a mini-boss; defeating it once opens the next zone. Stays
  farmable afterwards.
- **2–3 elite** — tougher, rarer encounters with a strong signature ability.
- **6–7 standard** — the bread and butter; random encounters weight toward these.

### 4.2 Enemy template

Every enemy is designed against this template (kept as a living table in
`docs/design/bestiario.md` once phase work starts):

| Field | Meaning |
|-------|---------|
| `nombre` | Spanish, dark-fantasy, no repeats |
| `zona` / `tier` | zone + power rank 1–10 within it |
| `arquetipo` | bruiser / skirmisher / caster / support / tank / ambusher |
| `habilidad` | one signature mechanic (see §4.4) |
| `elemento` | element its attacks deal (or physical) |
| `debilidades` | 0–2 elements at ×1.5 or ×2.0 |
| `resistencias` | 0–1 element at ×0.5 (rarely ×0.25) |
| `inmunidades` | status effects it cannot receive |
| `stats` | HP / atk / speed / armour / magic-resist / crit, from the power budget (§4.3) |
| `drops` | materials + a chance at a unique; commons roll from the zone tier (§7.3) |

### 4.3 Power budget

70 enemies cannot be tuned by eye. Each enemy gets a **power score**; from the
ATB math (see `TODO.md`), effective threat scales with
`hp × speed × daño_neto` (net damage = mean damage − effective mitigation).
Define a normalised score and a target curve: `objetivo(zona N, tier T) = base ·
f(N) · g(T)`. Design each enemy to land within ±10 % of its target, then
playtest-verify the guardian and a sample of each tier the way the chain is
verified today. The formula and its constants live in `TODO.md`.

### 4.4 Signature abilities (menu of mechanics to draw from)

Reuse and extend the patterns already in the code: pre-battle ambush, periodic
extra hit, self-heal under a threshold, unavoidable attack, applied debuff
through a hit roll, summon an ally (extra-hit pattern). New ones to add:
ranged attack (partially ignores evasion), gold theft, stun (skip a turn),
armour shred (stacking), life drain, enrage under a threshold, "consagrar"
(marks the player for bonus damage), curse that blocks healing.

### 4.5 Sample zone — Los Yermos (10)

Demonstrates the template; the other six zones are follow-up design work.

| Tier | Name | Archetype | Signature | Deals | Weak | Resists | Immune |
|------|------|-----------|-----------|-------|------|---------|--------|
| 1 | Rata Gigante | skirmisher | quick bite, minor poison chance | veneno | fuego | — | — |
| 2 | Goblin | bruiser | ambush after first defeat | físico | — | — | — |
| 3 | Goblin Montaraz | caster/ranged | arrows (partly ignore evasion) | físico | fuego | — | — |
| 4 | Huargo | skirmisher | pack bite (extra hit) | físico | — | — | — |
| 5 | Chamán Goblin | support | heals an ally / self, minor curse | oscuridad | sagrado | oscuridad | — |
| 6 | Esqueleto | tank | revives once | físico | sagrado, contundente | veneno | veneno, sangrado |
| 7 | Bandido | ambusher | disarm | físico | veneno | — | — |
| 8 | Salteador | skirmisher | double quick strike, steals gold | físico | — | — | — |
| 9 | Ogro del Yermo *(elite)* | bruiser | crushing blow that stuns | físico | fuego | físico | — |
| 10 | El Carnicero *(guardian)* | bruiser/tank | enrage below 40 % HP, applies sangrado | físico | sagrado | veneno | veneno |

---

## 5. Elements & affinities

**Seven elements** + physical (the default, no element):

| Element | Flavour | On-hit status | Notable weak / resist patterns |
|---------|---------|---------------|--------------------------------|
| **fuego** | burn over time | `quemado` (atk down + DoT) | melts `congelado`; strong vs plants/undead |
| **veneno** | poison over time | `veneno` (DoT vs max HP) | flesh weak; undead & constructs immune |
| **rayo** | shock | `paralizado` (chance to skip) | metal/wet weak |
| **hielo** | freeze / slow | `congelado` (chance to skip) | fire-aligned weak; melted by fuego |
| **sagrado** | divine light | `consagrado` (takes +dmg, can't self-heal) | undead & demons weak; living neutral; the Ángel Caído **resists** it |
| **oscuridad** | breach shadow | `marchito` (healing/regen received −50 %) | living & holy-aligned weak; demons & undead **resist** it |
| **arcano** | raw magic | `silenciado` (enemy can't cast) — always `is_magical`, pierces some physical armour | mundane things weak; constructs (Gólem, Gárgola) & the Mago **resist** it |

Model on the data layer:

- `Enemy.weaknesses: dict[str, float]` (multiplier > 1), `Enemy.resistances:
  dict[str, float]` (multiplier < 1), `Enemy.immune_statuses: set[str]`.
- Damage: `final = base × (weaknesses.get(el) or resistances.get(el) or 1.0)`
  before armour/magic-resist mitigation.
- The player gets elemental defence too: `Armor` may carry `resist` (a small
  dict), summed on demand as `Player.get_total_resist(element)` — a few pieces
  and one set (Sudario del Nigromante) grant it.
- `apply_status` on either side is a no-op if the target lists that status in
  `immune_statuses`.

Existing `is_fire` stays (it is orthogonal — it only melts `congelado`).

### Elemental reactions *(idea, not committed)*

`fuego` already melts `congelado`. Could extend: `rayo` on a `congelado` target
shatters for bonus damage; `fuego` + `veneno` = a stronger DoT. Adds depth and
complexity — parked until the base element set is in.

---

## 6. Combat systems

### 6.1 Classes

Chosen once at character creation; persisted; old saves default to **Vagabundo**.

| Class | Identity | Effect |
|-------|----------|--------|
| **Vagabundo** | balanced (today's character) | current base stats & growth; the safe default |
| **Guerrero** | tank / bruiser | +HP, +armour, +physical damage; tankier growth; no magic |
| **Pícaro** | fast / crit | +speed, +evasion, +crit chance; agile growth; fragile |
| **Arcanista** | magic damage | lower HP/armour; **standard attack is magical** (`is_magical`), scales with a new *poder mágico* stat — finally makes enemy `magic_resist` matter |

Classes touch character creation, `Stats`, the per-level `_*_GROWTH_RATE`
constants, and (Arcanista) the player branch in `_execute_turn`.

### 6.2 Skills (learned by level, per class)

No mana bar. Each class learns **~6 skills** at fixed levels (3, 6, 9, 12, 15,
18). Two kinds:

- **Passive** — modifies combat automatically, no UI (e.g. "heal on kill").
- **Active** — an action instead of attacking, with a **cooldown in turns**
  ("used, ready again in N turns"). Cooldown state lives in the battle only, not
  the save.

Combat gains a **"Habilidades"** menu option. In auto/turbo the policy is
simple: use a ready active if one exists, else attack. All learned passives are
always on; whether active skills need slotting (e.g. max 2 equipped) is an open
question — start with "all usable".

Sketch (subject to balancing):

| Lvl | Vagabundo | Guerrero | Pícaro | Arcanista |
|-----|-----------|----------|--------|-----------|
| 3 | Segundo Aliento — *p:* heal 15 % max HP on kill | Embate — *a3:* strong hit, 40 % stun | Golpe Bajo — *a3:* guaranteed crit + sangrado | Proyectil Arcano — *a2:* high magic dmg, pierces magic resist |
| 6 | Golpe Certero — *a3:* next hit +50 %, cannot miss | Piel de Piedra — *p:* −15 % physical dmg taken | Reflejos — *p:* +15 % evasion | Escudo de Maná — *a4:* fully absorb next hit |
| 9 | Aguante — *p:* below 30 % HP, +20 % armour & magic resist | Represalia — *p:* 30 % counter on melee hit | Veneno de Contacto — *p:* 20 % poison on hit | Sintonía Elemental — *p:* choose your attack element at battle start |
| 12 | Adrenalina — *a5:* +30 % speed for 3 turns | Grito de Guerra — *a5:* +25 % damage for 3 turns | Sombra — *a4:* dodge next enemy attack | Descarga — *a5:* magic dmg + applies the active element's status |
| 15 | Botín Afortunado — *p:* +25 % gold, +10 % drop chance | Fortaleza — *p:* +40 % max HP | Golpe Mortal — *p:* +50 % crit damage | Mente Aguda — *p:* −1 turn to all cooldowns |
| 18 | Voluntad de Hierro — *p:* survive a lethal hit at 1 HP (once/battle) | Último Bastión — *a6:* 2 turns immune to physical damage | Asalto — *a6:* 3 quick strikes | Cataclismo — *a8:* massive magic dmg, ignores all mitigation |

*(p = passive, aN = active with cooldown N turns.)*

### 6.3 Equipment set bonuses

`Armor` gains optional `set_name`. `Player` counts equipped pieces per set and
applies **tiers at 2 and 4 pieces** (sets are 4 pieces). Themed to regions,
drop there:

| Set | Region | 2-piece | 4-piece |
|-----|--------|---------|---------|
| Atavío del Proscrito | Los Yermos | +evasion | first hit of each battle is a guaranteed crit |
| Placas del Guardián | Cañón del Trueno | +armour | −10 % to all physical damage taken |
| Sudario del Nigromante | Necrópolis | +magic resist & +oscuridad resist | 20 % chance to reflect part of magic damage taken |
| Vestiduras del Caído | Ciudadela | +regen | heal 15 % of damage dealt |

Every `get_total_*` already sums equipment on demand — set bonuses hook the
same way. No set piece is strictly better than its slot's other options.

### 6.4 Status-inflicting weapons

`Weapon` gains `inflicts` = `{status, chance, duration, power}`. On a player
hit, roll `chance` and `enemy.apply_status(...)` (respecting `immune_statuses`).
Requires **`Enemy` to process status effects on its turn** — a mirror of
`Player.on_turn_start` / `on_turn_end` (burn/poison DoT vs `max_health`,
paralysis/freeze skip). The elemental weapons infliction map: veneno→`veneno`,
fuego→`quemado`, hielo→`congelado`, rayo→`paralizado`, oscuridad→`marchito`,
sagrado→`consagrado`, arcano→`silenciado`.

### 6.5 Arena mode

A Piedrablanca location unlocked after Act III (or via a ticket). Pick a
difficulty tier → **N escalating waves** back to back, enemies drawn from
cleared zones. Healing between waves is paid in gold. Rewards scale with the
wave reached: gold, a chance at set pieces, a cosmetic **título** on the stats
screen. Save tracks `arena_mejor_oleada`. Pairs with turbo auto-battle.

---

## 7. Progression & economy

### 7.1 Leveling

Unchanged curve (`Player._required_xp_for_level`). Levels now also gate skills
(§6.2). `poder mágico` is a new `Stats` field, 0 for non-Arcanista, growing for
Arcanista.

### 7.2 Bestiary — progressive reveal

Keyed on `enemy_kill_counts`:

| Kills | Revealed |
|-------|----------|
| 0 | not listed (as today) |
| 1 | name, HP, attack range, gold |
| 3 | armour, magic resist, speed, crit |
| 5 | weaknesses, resistances, status immunities |
| 10 | full drop table (first time it is ever shown) |

### 7.3 Loot scaling

Hybrid, so hand-crafted feel survives 70 enemies:

- **Uniques** — hand-designed, low drop rate, from specific enemies (as today).
  Set pieces and the forge stay hand-designed.
- **Commons** — `items/loot.py` rolls a piece for a slot from the **zone tier's
  ranges**: base stat magnitude + 0–3 secondaries, same rules as
  `tests/test_armor_progression.py` enforces. Keeps early zones at 1–2 stats,
  late zones at 3–4.

### 7.4 Death penalty *(open — see §11)*

Today: lose 1/3 gold + full heal. Candidate: respawn at the last visited town;
the lost gold becomes a "saco" left in the zone where you fell, recoverable if
you go back (Souls-lite). Undecided.

---

## 8. World systems

### 8.1 Exploration loop

Replaces the flat `game_loop` menu. Inside a zone: **Explorar** (weighted roll:
encounter / discovery / rare mini-event), **Ir a `<sub-lugar>`** (NPC / service
/ quest turn-in), **Viajar** (connected or fast-travel), **Personaje** (the
always-available character menu: inventory, stats, equip, skills, bestiary,
diary, quests, save — extracted from today's `game_loop`).

### 8.2 Dialogue

Lightweight. An NPC owns an ordered list of **dialogue nodes**; each has text,
an optional condition (quest state / story flag / item held) and an optional
effect (start/advance a quest, set a flag, give an item, open a service). No
branching trees in v1 — the *available* node changes with world state.

### 8.3 Quests

`Quest`: id, title, description, **objective** (kill N of X, reach zone Y, talk
to Z, collect W, or a manual flag), **reward** (gold / item / recipe / flag),
**state** (`no_iniciada` / `activa` / `completada` / `entregada`). Progress is
checked from hooks that already fire (`_handle_victory`, arriving in a zone,
`Inventory.add_item`). A **Misiones** entry in the character menu lists them.

---

## 9. Technical

### 9.1 Strings layer (i18n) — set up first

All player-facing text goes through `t(key, **kwargs)`. Implementation: an
`i18n/` package with `catalog_es.py` (and later `catalog_en.py`) — plain dicts
keyed by string id (`"enemy.goblin.name"`, `"skill.golpe_bajo.desc"`, …) — and
a `t()` resolver reading the active locale from `config.ini` `[IDIOMA]`
(default `es`). `ui/console.py` helpers are unchanged (they take resolved
strings). **New content is authored through `t()` from the start;** existing
hardcoded Spanish is migrated module by module (a background task per area),
starting with combat and menus in the foundations phase.

### 9.2 `world/` package

Data-driven like `characters/enemies/` (one file per zone):

- `world/zone.py` — `Zone` (id, name, description, sub-locations, enemy pool,
  connections, gate).
- `world/npc.py` — `NPC`, `DialogueNode`.
- `world/quest.py` — `Quest`, state enum, objective/reward types.
- `world/map.py` — the zone graph, travel, fast-travel, gating.
- `world/data/*.py` — one module per zone wiring NPCs, dialogue, encounters, lore.

### 9.3 Other new modules

- `characters/skills.py` — skill definitions; `Player` derives `known_skills`
  from class + level (not stored).
- `items/loot.py` — the common-drop roll tables per zone tier.
- `ui/exploration.py` — the zone loop (`omit`ted from coverage like `ui/menus.py`).

### 9.4 Save schema v2

Adds a `mundo` block: `clase`, `zona_actual`, `zonas_visitadas`, `misiones`,
`banderas`, `diario`, `arena_mejor_oleada`. Migration v1 → v2
(`persistence/save_load.py`, same pattern as the armour-slot and
`discovered_materials` back-fills): no `mundo` block → placed in the zone
matching `defeated_enemies` progress, class `vagabundo`, no quests/flags.
`unlocked_enemies` / `defeated_enemies` stay the source of truth for zone
gating.

### 9.5 Testing

All non-interactive logic is unit-tested: affinity maths, status immunity,
skill effects & cooldowns, class stat/growth differences, set-bonus counting,
loot roll ranges, quest progress, dialogue conditions, map travel & gating,
i18n key resolution & fallback, save migration. The exploration loop and menus
stay `omit`ted from the coverage metric.

---

## 10. Development phases (pre-release, open-ended)

Each phase is one release; **releases are tagged only on the maintainer's
go-ahead** — features accumulate on `main` via PRs. Order may shuffle.

| Phase | Theme | Contents |
|-------|-------|----------|
| **v0.9.0** | Foundations | i18n strings layer + migrate combat/menu core · enemy affinity model (weaknesses / resistances / status immunities) + the 3 new elements registered as data · status-inflicting weapons + `Enemy` status processing |
| **v0.10.0** | Classes & skills | 4 classes at creation · class skill trees (passives + cooldown actives) · "Habilidades" combat menu · `poder mágico` stat |
| **v0.11.0** | Gear & affinities | 4 armour sets · elemental resistance on armour · apply real weaknesses / resistances / immunities to the current 14 enemies · new elemental weapons (sagrado / oscuridad / arcano) |
| **v0.12.0** | The world, part 1 | zones + map + exploration loop + save migration v2 · shop / forge / rest relocated · random encounters + discoveries |
| **v0.13.0** | Bestiary & enemies I | progressive bestiary · power-budget tool · flesh out 2–3 zones to ~10 enemies each |
| **v0.14.0** | Enemies II | finish the roster to ~70 · loot scaling (uniques + rolled commons) |
| **v0.15.0** | Story & quests | quest system · "La Brecha" questline (7 acts) + side quests · NPC dialogue · lore notes + Diario |
| **v0.16.0** | The Arena | escalating-wave mode |
| **later** | Endgame & polish | Dragón final tuning (needs the full roster) · full chain rebalance · Ed25519 updater signature · gameplay GIF · cleaner MVC · *(stretch)* multi-enemy combat |
| **1.0** | — | called by the maintainer when the game is launch-ready |

---

## 11. Open questions

- **Encounter pacing** — clear a zone by a fixed encounter count, or clear =
  defeat the guardian once and the pool stays farmable? *(leaning: the latter.)*
- **Rest** — full heal or a %? Flat gold cost or scaling with level?
- **Fast-travel** — free, or costs gold / a turn of road encounters?
- **Death penalty** — keep current, or the Souls-lite "saco" (§7.4)?
- **Active-skill slotting** — all learned skills usable, or a max of 2 equipped?
- **Dialogue depth in v1** — a few state-swapped lines per NPC, or a small topic menu?
- **Arena rewards** — cosmetic titles only, or also a slow route to set pieces?
- **Per-element statuses** — commit to `consagrado` / `marchito` / `silenciado`
  as designed, or start with just the four classic ones and add the rest later?
- **Elemental reactions** (§5) — in scope eventually, or a permanent "no"?
- **New region name** — is **Ciénaga de los Ahogados** the right 3rd zone, or a
  different biome (coast, catacombs, blighted farmland…)?
