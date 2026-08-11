# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A Spanish-language, terminal-based turn-based RPG ("Juego de Batalla por Turnos") written in Python. Uses `colorama` for colored terminal text and `pygame` (mixer only) for background music/SFX — there is no graphical window, the game is played entirely via `input()`/`print()` in the console.

Packaged as an installable Python package (`src/` layout) under `src/juego_rol_texto/`.

## Commands

Setup (Windows, PowerShell):
```powershell
python -m venv env
.\env\Scripts\activate
pip install -e ".[dev]"
```

Run the game:
```bash
python main.py
# or: python -m juego_rol_texto
# or, after install: juego-rol-texto
```

Run tests:
```bash
pytest
```

There is no linter configured in this repo.

## Architecture

**Entry point**: `main.py` at the repo root is a thin compatibility shim that calls `juego_rol_texto.app.main()`. The real entry point is `src/juego_rol_texto/app.py::main()`, which initializes `colorama`/`pygame`, loads saved volume settings (`config/settings.py`), registers all audio assets (`audio/catalog.py`) with `ResourceManager`, then hands off to `ui/menus.py::main_menu()`.

**`config/` — centralized paths and settings**: `config/paths.py` resolves `BASE_DIR`/`ASSETS_DIR`/`SAVE_DIR`/`CONFIG_FILE` as absolute `pathlib.Path`s relative to the repo root, regardless of the process's current working directory. `config/settings.py` reads/writes volume settings to `config.ini` at the repo root.

**`ui/` — presentation layer**: `ui/console.py` centralizes all `colorama` usage behind `success()`/`error()`/`warning()`/`info()`/`title()` (full-line semantic messages) and `colorize(text, color, bright=False)` (inline fragments, used when a single line mixes multiple colors — the dominant pattern in combat/status messages). `ui.console.ask()` wraps `input()`. Domain modules (`player.py`, `battle.py`, enemies, `inventory.py`, `save_load.py`, `menus.py`) import from `ui.console` instead of `colorama` directly, but still print directly from within domain logic — there is **no full MVC separation**; this was a deliberate choice to keep the refactor behavior-preserving rather than an architectural rewrite. `ui/menus.py` is the menu/game-loop hub (former `game_core/menu.py`), `ui/formatting.py` holds the health-bar and detailed-info renderers (former `utils/utils.py`).

**Menu/game loop (`ui/menus.py`)**: Everything is driven by simple numbered `input()`-based menus, no state machine framework.
- `main_menu()` → new game / load game / options / exit
- `start_new_game()` creates a `Player` with base `Stats`; typing the name `"admin"` grants a debug/cheat character (high stats, gold, all enemies unlocked) — this is a known intentional test hook, not a bug.
- `game_loop(player, unlocked_enemies, defeated_enemies)` is the per-session hub (fight, inventory, equip weapon/armor, options, save, return to main menu). `unlocked_enemies`/`defeated_enemies` are plain lists of enemy name strings threaded through the whole session and persisted on save.
- Enemy names are looked up via a hardcoded Spanish-name → class dict in `_get_enemy_instance()`.

**Combat (`combat/battle.py`)**: `initiate_battle()` is the turn loop entry point.
- `ENEMY_PROGRESSION` dict defines the fixed unlock chain: Goblin → Esqueleto → Orco → Troll → Mago. Beating a new enemy for the first time unlocks the next one and adds it to `unlocked_enemies`.
- Player stat changes from potions during battle are snapshotted at battle start and restored via `_restore_player()` at battle end (so buffs don't persist outside combat).
- Status effects (`quemado`/burn, `veneno`/poison, `paralizado`/paralysis, `congelado`/freeze, `regeneración`) live as dicts in `player.status_effects` and are processed in `Player.on_turn_start()` / `on_turn_end()`.
- "Auto-battle" mode (only unlockable against previously-defeated enemies) polls `msvcrt.kbhit()` each turn to let the player cancel by pressing `q` — this makes `battle.py` Windows-only (`msvcrt` has no cross-platform equivalent here).
- On defeat, the player loses 1/3 of gold and is fully healed rather than getting a game over.

**Characters (`characters/`)**:
- `base.py`: abstract `Character` (name, stats, status_effects) — note `Player` and `Enemy` do NOT actually share this base in practice; `Enemy` (`characters/enemies/enemy_base.py`) is defined independently with its own `take_damage`/`is_alive`. Don't assume polymorphism between `Player` and `Enemy` beyond duck-typing (`is_alive()`, `take_damage()`, `get_attack_damage()`).
- `stats.py`: `Stats` encapsulates HP/attack range/`armor` (physical mitigation)/`magic_resist` (magical mitigation, default 0); `health` is a property clamped to `[0, max_health]`.
- `player.py`: combat math (attack range/armor including equipped weapon/armor bonuses), status effect processing, leveling (`required_xp()` is a scaling curve, `_level_up()` on XP threshold — `armor` grows every level, `magic_resist` only every *even* level, since no gear grants magic resist yet and the Mago would otherwise get disproportionately harder).
- **Damage types**: `Player.take_damage(amount, is_fire=False, is_magical=False)` picks `get_total_armor()` or `get_total_magic_resist()` for mitigation based on `is_magical`. Only the Mago's four spells (`_cast_fireball`/`_cast_thunder`/`_cast_poison`/`_cast_blizzard` in `enemies/mage.py`) currently pass `is_magical=True` — everything else (melee attacks, Orc's fury hit) is physical. `is_fire` is orthogonal to `is_magical`: it only controls whether the "congelado" status gets melted, unrelated to mitigation. The `Armor` item class (`items/equipment.py`) and its `defense` attribute were deliberately **not** renamed to match `Stats.armor` — that class represents the equipped item's bonus and is slated for a bigger rework (multi-slot equipment) later; only its on-screen label changed to "Armadura".
- `enemies/`: one file per enemy (`goblin.py`, `skeleton.py`, `orc.py`, `troll.py`, `mage.py`), each subclassing `Enemy` and overriding `perform_turn()`/`drop_item()` for unique mechanics (e.g. Mago casts elemental spells and heals itself, Troll self-regenerates each turn end).
- **Elemental weapon damage** (separate from the Mago's magical damage above — this is a *physical* mechanic): `Enemy.ELEMENTAL_WEAKNESSES` is a class-level `dict[str, float]` (empty = neutral to everything); `Enemy.take_damage(damage, defeated_enemies=None, element=None)` multiplies `damage` by the matching weakness before subtracting armor. `Weapon.element` (`items/equipment.py`, default `None`) carries the element, read via `Player.get_equipped_element()`. Only `Troll.ELEMENTAL_WEAKNESSES = {"fuego": 2.0}` exists so far — this was deliberately built as a reusable one-element MVP (currently just `"fuego"`, a bare string like the status-effect names already are) before adding more elements. `combat/battle.py::_execute_turn` computes the element from the attacker's equipped weapon, calls `take_damage()` with it, and separately checks `type(defender).ELEMENTAL_WEAKNESSES` beforehand to print a "¡Es supereficaz!" message — that check is duplicated because `take_damage()`'s return value (final HP damage after armor) doesn't distinguish "no bonus applied" from "bonus applied but armor absorbed it all". All `Enemy` subclasses (including `Skeleton`, which has its own `take_damage` override for its revive mechanic) share the exact same `take_damage()` signature now, which is what let `_execute_turn` drop the `try/except TypeError` fallback dance it used to need.

**Items (`items/`)**: `item_base.py` defines only the abstract `Item` class. `factory.py` holds `item_factory(data)`, a dict → class dispatcher used by save/load to reconstruct items from JSON (`type` field selects the class: `HealingPotion`, `StatBuffPotion`, `RegenPotion`, `Material`, `Weapon`, `Armor`) — it imports the concrete classes at module level (no circular import, since `item_base.py` doesn't import `factory.py`). Every concrete item class implements `to_dict()`/`from_dict()` matching this factory — when adding a new item type, register it in `_ITEM_CLASSES` and implement both methods or save/load will silently drop it.
- `equipment.py`: `Weapon`/`Armor`, equipped via `Inventory.equip_menu()`.
- `potions/`: `potion_base.Potion` (abstract) + `healing_potion.py`, `buff_potion.py` (temporary stat buffs tracked in `player.active_effects`, decremented in `on_turn_end`), `regen_potion.py`.
- `materials.py`: crafting materials, non-usable directly (`use()` always returns `False`) — consumed instead by `crafting/forge.py` recipes.

**Inventory (`inventory/inventory.py`)**: consumables stack via a `quantities` dict keyed by item name; `Weapon`/`Armor` don't stack — picking up a duplicate auto-sells it for gold instead. `show_inventory(filter_class, mode)` is reused both for read-only viewing and interactive selection (`mode="use"`), filtered by class for the weapon/armor equip menus. All `Item.use()` implementations return `True` on success, which `_handle_selection()` relies on to decide whether to decrement a consumable from the stack and, in combat, whether the action consumes a turn (`"objeto_usado"`); when adding a new item type, make sure `use()` returns `True`/`False` accordingly. `Inventory.sell_item(item)` (used by the shop) removes one unit via the shared `_remove_one()` helper and credits `item.value` gold — refuses to sell whatever is currently equipped as weapon/armor. `has_item(name, quantity)`/`consume_item(name, quantity)` look up and remove stock **by name** rather than by object reference (unlike `_remove_one()`) — used by the crafting system, which knows *what* material it needs but doesn't have a handle to the player's actual item instance.

**Shop (`shop/shop.py`)**: `Shop` holds a fixed, in-memory `catalog` of `ShopItem` (an item template + buy price); wired into `game_loop`'s "Tienda" option via `Shop().open(player)`. Buying clones the template through `items/factory.py::item_factory(template.to_dict())` (so each purchase is an independent instance) and calls the existing `Inventory.add_item()`; selling lists `player.inventory.items` and calls `Inventory.sell_item()`. The catalog is static code, not persisted — `persistence/save_load.py` doesn't know about it.

**Crafting (`crafting/forge.py`)**: `Forge` mirrors `Shop`'s structure — a fixed `recipes` list of `CraftingRecipe` (materials-by-name + gold cost + a result item template, cloned the same way as `ShopItem` via `item_factory`), wired into `game_loop`'s "Herrería" option via `Forge().open(player)`. `CraftingRecipe.can_craft(player)` checks gold and `Inventory.has_item()` for every required material; `Forge._craft()` only mutates state (deduct gold, `Inventory.consume_item()` each material, `Inventory.add_item()` the result) after confirming `can_craft()`. Only one recipe exists so far (Piel de Troll + 200 oro → Armadura Regenerativa, the current best armor in the game) — deliberately shipped as a single case to validate the mechanism before adding more. That recipe's result is a plain stat boost; it does **not** grant any special regeneration behavior despite the name — equipped items have no passive-effect hook in the combat loop yet (weapons/armor only ever contribute static `damage`/`defense`/`element`), so a "true" regenerating armor is a follow-up, not implemented here.

**Save/load (`persistence/save_load.py`)**: game state is serialized to JSON, then base64-encoded, written to `saved_games/<player_name>.sav`. Saving always backs up the previous file to `<player_name>.bak` first; loading falls back to the `.bak` file if the `.sav` fails with an error *not* in `{json.JSONDecodeError, binascii.Error, UnicodeDecodeError, KeyError}` (those specific failures return `None` immediately without a fallback attempt — this is existing, deliberately-preserved behavior, not something to "fix" silently). Item reconstruction goes through `items/factory.py::item_factory`.

**Audio (`audio/resource_manager.py`)**: `ResourceManager` is a singleton (`__new__` override) wrapping `pygame.mixer`. It self-manages background music via a `mood` field (`"adventure"` vs `"battle"`) — call `set_mood()` then `update()` (called every menu/battle loop tick) to let it pick appropriate tracks; direct calls to `play_music()`/`play_sfx()` are used for one-off cues (e.g. mage spell SFX, level-up jingle). Volumes persist to `config.ini` via `config/settings.py`. `audio/catalog.py` holds the `AUDIO_ASSETS` dict of relative asset paths.

## Tests (`tests/`)

`pytest`-based. `tests/conftest.py` sets `SDL_AUDIODRIVER=dummy` and initializes `pygame.mixer` headlessly (session-scoped autouse fixture) so `ResourceManager`/`battle.py` can run without real audio hardware, and provides a `tmp_save_dir` fixture that monkeypatches `juego_rol_texto.persistence.save_load.SAVE_DIR` so save/load tests never touch the real `saved_games/` directory. Coverage: `Stats` clamping, `Player` combat math/status effects/leveling, `Inventory` stacking/equip/use/sell/craft-support flows, `Shop` buy/sell flows, `Forge` crafting flows, item `to_dict()`/`from_dict()` round-trips through `item_factory`, save/load round-trip + backup fallback, and `initiate_battle()` victory/defeat outcomes (enemy unlock progression, gold penalty on defeat, elemental weakness bonus) using deterministic fixtures (`weak_enemy`) and `monkeypatch` for `input()`/`time.sleep()`/`random`.

## Known incomplete/dead areas (see TODO.md)

- `tools/settings_admin.py` (a Tkinter debug settings window) is not imported anywhere in the game; it's leftover/experimental.
- Only one crafting recipe exists (see `crafting/forge.py` above); more are planned but not designed yet.
