# SPEC: Options Consolidation

Status: proposal (2026-06-21). Audit of `worlds/eldenring/options.py` with concrete
removes, merges, grouping, and bug fixes. No logic changes are *required* — the
highest-value change (rebuilding `option_groups`) is pure presentation.

## Why

`EROptions` currently exposes **83 game options**. The `option_groups` block only
covers ~40 of them across 5 groups, so on the webhost / template the other ~43 spill
into the ungrouped default bucket. Several option *families* (progressive items, short
runs, great runes, pool curation) are spread across many sibling toggles that could
collapse, and a handful of options are dead, broken, or self-labeled experimental.

Target after this pass: **~70 options, every one in a sensible group.**

---

## Part 1 — Bugs to fix first (independent of consolidation)

These are correctness issues found while reading the file; fix regardless of whether
the rest of the consolidation lands.

### 1.1 `extra_region_locks` `limgrave_caves` / `limgrave_underground` — NOT a bug (corrected)
On inspection these are NOT an accidental duplicate: `__init__.py` (L159-165) and
`region_spine.py` (L631-636) deliberately normalize `limgrave_caves` ->
`limgrave_underground` as a documented alias, and the Alaric playtest yaml relies on
`limgrave_caves`. Removing it would break that yaml. Only the docstring was misleading
(it documented both identically with no mention of the alias).

Action (DONE, `patch_apworld_options_cleanup.py`): keep both keys; mark `limgrave_caves`
in the docstring as "ALIAS of limgrave_underground (auto-normalized in code)". No
behaviour change.

### 1.2 `exclude_locations` (ERExcludeLocations) was genuinely broken — FIXED
The keys `dlc / hidden / blizzard` did not resolve: there was no `dlc` or `blizzard`
location group, and the existing group is `"Hidden"` (capitalized) which the lowercase
key never matched -- so any of the three raised "... is not a valid location name from
'EldenRing'" (hence `default = frozenset({}) # still errors`). The author left a
commented-out DLC-group experiment at the end of locations.py.

Action (DONE, `patch_apworld_exclude_locations_groups.py`): wire the three keys at
module load (additive; replaces the dead experiment):
- `hidden`   -> the existing `"Hidden"` group (lowercase alias)
- `dlc`      -> union of every region in `region_order_dlc` (the full DLC region list)
- `blizzard` -> every non-event location tagged `blizzard=True` (Consecrated Snowfield)
The world already registers `location_name_groups` (__init__ L138). Default is empty, so
existing seeds are unaffected. The options.py `# still errors` / captured-Exception
comments are corrected by the text patch. Gen-test: `gen-test/cleanup-yamls/`.

### 1.3 Leftover dev-uncertainty comments — FIXED
- `MessmerKindle`: `# another toggle to make them only spawn in dlc?`
- `MessmerKindleRequired`: `# i just picked these numbers idk how many would be good`

Action (DONE, `patch_apworld_options_cleanup.py`): stripped both trailing comments.

---

## Part 2 — Remove / deprecate candidates

Each is low-traffic, redundant, or unfinished. "Deprecate" = keep the field but mark
advanced / hide from default groups; "Remove" = delete field + dataclass entry + any
branches.

| Option | Verdict | Reason |
|---|---|---|
| `global_scadutree_blessing` | Deprecate or shelve | Self-labeled EXPERIMENTAL; `scaled` "currently behaves like player_only"; enemy-side baker work doesn't exist. Collapse to a single toggle or pull until the baker side lands. |
| `great_runes_present` | Deprecate (advanced) | Only fires under `num_regions` + `rune_source=pool`. Extremely narrow surface. |
| `pool_builder_dlc_gear` | Remove or fold | Overlaps `dlc_gear_curation`; reintroduces a DLC dependency on base runs (docstring admits the footgun). Fold its behavior into `dlc_gear_curation` when `pool_builder` is on. |
| `completion_scaling_basis` (`sphere`) | Gate | `sphere` needs a baker bridge that isn't wired; only `geographic` actually applies. Keep `geographic`, hide/flag `sphere` as not-yet-active. |
| `region_count` | Deprecate toward `num_regions` | Two implementations of the short Capital run. See Part 3.2. |
| `royal_access` | Question | Single niche convenience toggle. |
| `disable_serpent_hunter_upgrade` | Question | Very niche base-randomizer balance tweak. |
| `deathless_routing` | Question | Niche logic exclusion (Volcano abduction only). |
| `region_boss_type` | Question | Sub-knob that only matters under `region_bosses` world logic; could fold into that mode's defaults. |

The "Question" rows aren't strong removes — they're candidates to confirm usage before
keeping. None block the grouping work.

**DONE 2026-06-21 (`patch_apworld_options_advanced_group.py`):** rather than delete
(each of these has real backing logic — 51 refs across __init__.py / region_spine.py —
so removal is feature surgery, not cleanup), all 8 are HIDDEN: moved into a new
**"Advanced & Experimental"** OptionGroup with `start_collapsed=True`. They drop out of
the default webhost view but still work. The patch rebuilds the whole `option_groups`
block (13 groups, all 84 members) and supersedes the regroup block (removes its marker
first), so it is self-contained and order-independent. Presentation only; gen unchanged.
Hidden set: global_scadutree_blessing, completion_scaling_basis, great_runes_present,
pool_builder_dlc_gear, region_boss_type, deathless_routing, royal_access,
disable_serpent_hunter_upgrade. TRUE deletion of any still needs a per-option logic pass
+ a usage decision (the "Question" rows) — left for later.

---

## Part 3 — Merge candidates (collapse families)

### 3.1 Progressive items → one OptionSet
`progressive_stone_bells`, `progressive_glovewort_bells`, `progressive_flasks`,
`progressive_physick` are the same concept (collapse discrete upgrade items into
progressive items) expressed four times.

Proposal: one `progressive_items: OptionSet` with keys
`{stone_bells, glovewort_bells, flasks, physick}`. Likewise merge the two parallel
sphere-1 forcing knobs `progressive_bell_early_count` + `progressive_flask_early_count`
into a single `progressive_early_count`.

Net: 6 options → ~3. Keep `progressive_bell_count` (pool-count) as its own range, or
generalize to `progressive_pool_count`.

Migration: accept the old boolean fields as deprecated aliases that populate the set,
so existing yamls don't break. Confirm each backing implementation reads the set.

**DONE 2026-06-21** (`patch_apworld_progressive_items_options.py` +
`patch_apworld_progressive_items_init.py`): added `progressive_items` OptionSet
{stone_bells, glovewort_bells, flasks, physick} as the primary front-end. The four
boolean options STAY in the dataclass as the internal source of truth (read via the
`_progressive_*_active` accessors + slot_data, untouched); `generate_early` OR-unions the
set onto them right after the limgrave alias block. Backward compatible — legacy
`progressive_flasks: true` yamls still work. The four legacy toggles moved to a collapsed
"Superseded (use progressive_items)" group (options.py now 85 members / 14 groups, 2
collapsed; this rebuild supersedes the advanced-group block). Count knobs NOT merged
(deferred — low value, ambiguous default handling). Gen-test:
`gen-test/progressive-items-yamls/` (set + legacy back-compat). Mapping OR-union semantics
unit-validated. Needs run on Windows.

### 3.2 Short-run family: `region_count` vs `num_regions`  — TODO (deferred)
Both build a "reach the Capital and kill Morgott" short run — one fixed first-N spine,
one random N. `num_regions_chain` already bridges them (linear breadcrumb).

Proposal: make `num_regions` the single entry point and express the fixed spine as an
ordering mode (e.g. `num_regions_order: spine | random`), deprecating `region_count`.
Lower priority than 3.1 — the two genuinely differ today, so only do this if the unify
is clean.

**TODO — NOT done. Deferred.** Both have substantial, distinct spine-building logic in
__init__.py / region_spine.py, and `region_count` is the FillError-prone config, so the
unify needs careful mapping. Arguably the `num_regions` fill-overflow
([[er-num-regions-fill-overflow]] / `er-important-locations-scope`) is worth fixing first,
as a separate task, before folding the two together.

### 3.3 Vanilla-upgrade shortcuts overlap `important_locations`  — TODO (deferred)
`flask_upgrade_option` and `blessing_option` are, by their own docstrings, shortcuts
that duplicate listing Seedtree/Church (flasks) and Fragment/Revered (blessings) in
`important_locations`, plus a `do_not_randomize` escape.

Proposal: keep them (real convenience) but add an explicit cross-reference in each
docstring, OR fold both into one `vanilla_upgrades: OptionSet {seeds, tears, fragments,
revered}` controlling the do-not-randomize lock, leaving priority to `important_locations`.
Low priority; mostly a clarity win.

**TODO — NOT done. Deferred.** Lightest of the remaining merges; mostly a clarity/UX win,
low payoff, so left as future work.

---

## Part 4 — Grouping (the high-value, low-risk change)

Rebuild `option_groups` so all 83 (→70) options land in a named group. This is pure
presentation — no logic touched. Proposed groups:

```
Goal & World Logic
  ending_condition, world_logic, region_boss_percent, region_boss_type,
  soft_logic, region_access, deathless_routing, extra_region_locks, royal_access

Great Runes
  great_runes_required, great_runes_final_boss, great_runes_mountaintops,
  great_runes_present

Short Runs (Capital)
  region_count, num_regions, num_regions_rune_source, num_regions_chain,
  graces_per_region

Start
  random_start_region, start_region_freebie, early_leveling, torrent_start,
  random_start (loadout)

DLC
  enable_dlc, dlc_only, dlc_timing, messmer_kindle, messmer_kindle_required,
  messmer_kindle_max, scadu_frontload, blessing_option

DLC-Only Catch-up
  quick_start, dlc_only_rune_catchup, progressive_early_count(s)

Pool & Curation
  location_pool, pool_builder, pool_builder_dlc_gear, dlc_gear_curation,
  filler_replacement, junk_retention, junk_retention_style, tidy_fun_consumables,
  soft_consumable_shop, derandomize_gurranq, derandomize_questlines,
  soft_progression, no_spirit_ashes, randomize_enia

Progressive Items
  progressive_items (set) + pool/early counts

Fill Priority
  important_locations, exclude_locations, excluded_location_behavior,
  missable_location_behavior, flask_upgrade_option, merchant_bell_logic,
  local_item_option, exclude_local_item_only

Sweep
  dungeon_sweep, grace_sweep

Enemy Randomizer
  enemy_rando, swap_multiboss, boss_runes_match, impolite_enemies,
  completion_scaling, completion_scaling_floor, completion_scaling_basis

Equipment & QoL
  auto_equip, auto_upgrade, no_weapon_requirements, crafting_kit_option,
  map_option, smithing_bell_bearing_option, spell_shop_spells_only,
  early_legacy_dungeons, material_rando, disable_serpent_hunter_upgrade,
  bell_physick_option, death_link
```

Misfilings to correct from the current block specifically:
- `region_boss_percent` / `region_boss_type` / `soft_logic` are currently ungrouped → World Logic.
- `auto_upgrade` is currently ungrouped → Equipment & QoL.
- `dlc_only`, `scadu_frontload`, `dlc_only_rune_catchup` are currently ungrouped → DLC / DLC-Only.
- `completion_scaling` ×3, `num_regions` ×3, `random_start_region`, `start_region_freebie`,
  all `progressive_*`, `location_pool`, `pool_builder*`, `dungeon_sweep`, `grace_sweep`,
  `junk_*`, `filler_replacement`, `no_spirit_ashes`, `no_weapon_requirements`,
  `torrent_start`, `randomize_enia`, `merchant_bell_logic` — all currently ungrouped.

---

## Rollout order (lowest risk first)

1. **Part 4 grouping** — presentation only. DONE (`patch_apworld_options_regroup.py`);
   gen-test PASSED 2026-06-21 (0 cfgerr across 4 configs / 20 gens).
2. **Part 1 bugs** — DONE 2026-06-21. `patch_apworld_options_cleanup.py` (text: limgrave
   alias docstring, stray comments, `frozenset()`) + `patch_apworld_exclude_locations_groups.py`
   (wires dlc/hidden/blizzard groups). 1.1 was a non-bug (intentional alias). Gen-test
   `gen-test/cleanup-yamls/`. Needs run on Windows.
3. **Part 2 deprecations** — DONE 2026-06-21 (`patch_apworld_options_advanced_group.py`):
   8 experimental/niche options hidden in a collapsed "Advanced & Experimental" group
   (supersedes the regroup block). Presentation only; reuse the regroup gen-test yamls.
4. **Part 3 merges** — 3.1 progressive-items set: DONE 2026-06-21
   (`patch_apworld_progressive_items_options.py` + `_init.py`); gen-test PASSED (set +
   legacy back-compat both 100%). 3.2 region_count→num_regions and 3.3 flask/blessing
   overlap: TODO / deferred (see those sections).

## Status (2026-06-21)

Done + gen-clean on Windows: Part 4 (regroup), Part 1 (exclude_locations wiring + alias/
comment cleanup), Part 2 (Advanced collapsed group), Part 3.1 (progressive_items merge).
Outstanding: Part 2 true deletions (per-option surgery + usage decisions), Part 3.2/3.3
merges. Patches (apply order): `patch_apworld_options_cleanup`,
`patch_apworld_exclude_locations_groups`, `patch_apworld_progressive_items_options`,
`patch_apworld_progressive_items_init` (the progressive options patch rebuilds the full
option_groups and supersedes the regroup / advanced-group blocks, so it is the current
option_groups authority — run it last among the group-rebuilding patches).

All ER option work runs on Windows: write `patch_*.py` for Alaric to apply + a
gen-test, never edit `options.py` / the apworld in place from the sandbox.

## Open decisions

- `exclude_locations`: fix the key→location resolution, or remove?
- `region_count`: unify into `num_regions`, or keep both?
- `global_scadutree_blessing`: shelve entirely, or keep `player_only` as a shipped knob?
- Which `limgrave_*` key to keep (check for existing yaml/seed usage first).
