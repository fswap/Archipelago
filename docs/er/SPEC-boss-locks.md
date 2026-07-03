# SPEC — per-boss locks ("The Shattering" boss gating)

Goal (Alaric, 2026-07-03, **direction decided**): in the Shattering marquee configuration,
owning a region lock currently lets you warp straight to that region's mainboss grace and
insta-clear it for the whole dungeon sweep. Kill that shortcut: **every remembrance boss /
major sweep boss (e.g. Leonine Misbegotten) gets its own lock**, separate from the region
lock. The region lock lets you *in*; the boss lock is what lets you actually reach and fight
that region's boss. You have to poke around the region to find its boss lock before you can
clear it.

This is an **extension of the vanilla catacomb pattern** — in a catacomb the boss fog is
sealed until you find and pull the lever elsewhere in the dungeon. Boss locks generalize that
lever to legacy dungeons and major open-world sweep bosses: the mainboss fog stays sealed
until the boss lock is in your inventory, and the lock is scattered into the region's check
pool by fill.

Degenerate case is fine: if you happen to find the boss lock first, this collapses to today's
behaviour — but across seeds it randomizes *when* in a region's clear you can take the boss.

Precedent already in-tree: `GODRICK_ONLY_LOCKS = {"Stormhill Lock", "Godrick Lock"}`
(`region_spine.py:491`) and `region_open_flags["Godrick Lock"] = 76967`
(`__init__.py:3609`) are a working single-boss lock + fog-gate, built for the Godrick
mini-campaign (`ending_condition == godrick`). This spec **generalizes that one boss into the
whole major-boss set** and makes it always-on in the Shattering config.

---

## Core mechanism

A **boss lock** is a synthetic lock item (`ERItemData(..., lock=True)`, same class as region
locks — `items.py:2156+`) named `"<Boss> Lock"` (or `"<Dungeon> Boss Lock"`), one per major
sweep group. It carries a **dedicated fog-open flag** exactly like a region lock carries a
`regionOpenFlags` entry, but the flag is bound to the boss's **arena fog wall** instead of a
region border.

Three effects, all parallel to the region-lock apparatus:

1. **Logic (AP fill).** The boss's drop location(s) — and any check physically behind the boss
   fog — gate on `Has("<Boss> Lock")`, AND-combined with the existing region rule. The boss
   lock is minted into the item pool. Pre-boss checks in the same region **stay on the region
   lock only** (this is what makes the escape hatch work — see below).
2. **Dungeon sweep.** The sweep grant for that group additionally requires `Has("<Boss> Lock")`.
   Reaching the trigger drop already implies holding the lock (the fog gated it), so this falls
   out of (1) once the trigger location is gated — no separate sweep rule needed, but assert it.
3. **Physical (client / fog baker).** The boss arena fog wall is sealed on a reserved open flag
   that the client sets on lock receipt, via the existing `RegionFogGates` baker path
   (`SPEC-region-fog-gates.md`, the same route that already seals Godrick `76967` and Castle
   Morne `76966`). Reuse the hardening already learned for region opens: gate on
   `InventoryInstance()!=0`, persist the latch, poll on the settle-gate (see the quirk tags in
   `SPEC-natural-locks.md`).

Activation: **always-on, no sub-toggle.** Boss locks are minted whenever the Shattering config
is active — i.e. region locks are on (`world_logic == region_lock`) **and** dungeon sweep is at
the legacy tier (`dungeon_sweep >= 2`), which is the tier that produces the major-boss groups.
Keep a single internal constant (`ENABLE_BOSS_LOCKS = True`) so it can be flipped off for
debugging, but expose no player option.

---

## Scope — which bosses get a lock

**Remembrance bosses + major sweep bosses.** Concretely: **the trigger boss of every major
sweep group**, which is exactly the `groups` list produced by `_compute_dungeon_sweeps`
(`__init__.py:3225`) at the `dungeon_sweep >= 2` tier — the `legacy_groups` block
(`__init__.py:3260-3289`) plus the named castle/field sweeps (The Shaded Castle / Elemer,
`__init__.py:3314-3327`; Castle Morne / Leonine Misbegotten). **Derive the boss-lock set from
the same group computation** so the two can never drift.

Explicitly **out of scope: the minidungeon tier** (catacombs, caves, tunnels, heroes' graves,
gaols — the `minidungeon_tags` branch, `__init__.py:3246-3253`). Those already have their
vanilla levers; adding synthetic locks there would bloat the pool for no gameplay gain. Leonine
Misbegotten is *in* scope because Castle Morne is a major sweep, not a minidungeon.

Each group's trigger is already `next((l for l in rem_locs if l.data.prominent), rem_locs[0])`
(`__init__.py:3311`) — the prominent remembrance / mainboss drop. That location is the anchor
the boss lock gates.

---

## Chokepoint bosses (Red Wolf, Godskin Duo, Loretta, Godfrey shade)

Mid-dungeon "choke" bosses are a deliberate gray area: they're major-ish and already have infra
(`CHOKEPOINTS`, `CHOKEPOINT_BOSS_FLAGS`, `region_spine.py:494-524`), but they are **not**
sweep-group triggers. **v0.1: they do NOT get a boss lock. Do not fold them in.**

Two reasons:

1. **Consistency with the chosen scope.** A chokepoint boss is neither a remembrance boss nor a
   major sweep-group trigger — e.g. Rennala is the Raya Lucaria trigger; Red Wolf of Radagon is
   a mid-boss. Excluding it is the scope rule applied, not a special case.
2. **It fixes no exploit.** Boss locks exist to close the "warp to the boss grace and insta-clear"
   shortcut. Chokepoint bosses generally aren't warp-reachable to begin with: Red Wolf's Debate
   Parlor grace (`71401`) is already excluded from the Raya bundle because the warp drops you
   *behind* its fog (`__init__.py:3703` note). So the player already has to run the academy and
   beat Red Wolf vanilla-style to reach Rennala — the mainboss lock on Rennala closes the
   dungeon's only insta-clear. A lock on Red Wolf would add hunt-depth, not fix a bug.

Keep the existing `chokepoint_locks` opt-in (`extra_region_locks: chokepoint_locks`) exactly as
it is — a **logic-only sweep-split**, fully decoupled from boss locks. Do not physically
fog-gate chokepoints in v0.1.

**v0.1 correctness item this raises (do NOT skip):** because a mainboss lock ships a grace bundle
+ warp, audit every locked mainboss to confirm **no bundled grace or warp lands the player past a
mid-dungeon fog**. The Debate Parlor exclusion (`71401`) is the template. A warp that skips the
chokepoint would let the player bypass the mid-boss entirely — and, once the long-term work below
lands, bypass its lock. This audit is the one place chokepoints touch v0.1.

**Long term — promote chokepoint bosses to nested boss locks.** A choke boss gets a real fog gate
and a *second* lock for its dungeon, layered under the mainboss lock, turning big legacy dungeons
into two-stage lock hunts (find the Red Wolf lock to get deeper, then the Rennala lock to finish).
Clean end state: collapse `CHOKEPOINTS` + `BOSS_LOCKS` into one ordered **dungeon-lock chain** per
dungeon — a list of `(boss, lock, fog_flag, region_carve)` whose last entry is the mainboss — and
the existing sweep-split re-homing becomes the per-tier sweep.

Deferred because of known-hard bits (all flagged in `region_spine.py:498-500`):

- **Back-half carve.** Raya doesn't cleanly region-split at the Debate Parlor, so the dungeon
  needs new before/after sub-regions before a Red Wolf fog gate can attach.
- **DLC flag capture.** Several DLC chokepoint fogs need an env/boss-flag capture they don't have
  yet.
- **Nested-fill constraint.** The mainboss lock must not sit behind the chokepoint lock unless the
  chokepoint lock is reachable in the front half with only the region lock. Same escape-hatch
  principle as the mainboss layer, one level deeper — add the assert.

Net: Red Wolf and the other chokepoint bosses stay vanilla fights in v0.1; each becomes a lock only
when the tiered dungeon-lock chain is built.

---

## What exists to build on

| Thing | Where | Note |
|---|---|---|
| Lock item class | `items.py:2156+` | `ERItemData(name, 99999, GOODS, progression, lock=True)` — mint boss locks the same way |
| Existing single-boss lock | `region_spine.py:491` | `GODRICK_ONLY_LOCKS = {"Stormhill Lock", "Godrick Lock"}` — pattern to generalize |
| Region-lock rule builder | `region_lock_data.py:59-234` | `build_region_lock_rules()` → `Has(lock)`; add a parallel boss-lock pass |
| Rule attachment | `rules_mixin.py` (`_region_lock`, warp access ~303-317) | where region rules AND onto entrances; boss-lock rules AND onto boss drop locations |
| Sweep grouping | `__init__.py:3225-3328` | `groups = [(trigger, members)]`; the boss-lock set + gating hooks here |
| Chokepoint precedent | `region_spine.py:501` `CHOKEPOINTS`, `:522` `CHOKEPOINT_BOSS_FLAGS` | closest existing "mid-dungeon boss gates a sub-half" structure; model `BOSS_LOCKS` on it |
| Physical fog gate | `__init__.py:3587-3610`, `4107-4117` `regionOpenFlags`; `SPEC-region-fog-gates.md` | `region_open_flags["Godrick Lock"]=76967`, `["Morne Lock"]=76966` already seal boss/gate fog |
| Fog baker | `RegionFogGates` (referenced `__init__.py:3609`) | keys arena fog walls off the open flag |
| Boss DefeatFlags | `region_spine.py:522` + `enemy.txt` | e.g. Godskin Duo `13000850`, Loretta `15000850` — pattern for capturing each boss's flag |

**Reserved flags — reconcile before allocating.** There are two flag-numbering contexts in the
tree: `__init__.py:3609` uses Godrick `76967` / Morne `76966`, while `SPEC-natural-locks.md`
documents the region-open base as `76971-76998` (Morne `76997`, Godrick `76998`) plus patched
`76996`/`76961`. **Do not hardcode a number blind.** Allocate a fresh reserved block for
boss-lock fog flags, audit against `map_region_data.py` and both tables above, and assert no
collision at generation.

---

## Logic soundness & the escape hatch

The escape hatch is **emergent from fill**, not special-cased: because the boss lock gates only
the boss fog + boss drop + sweep (never the region's other checks), every non-boss check in the
region stays reachable with just the region lock. AP fill scatters progression — including the
boss lock itself and possibly a *different* region's lock — into that region-lock-only pool. So
while hunting the boss lock you may instead surface another region's lock and simply leave. That
is the intended escape hatch, and it means a region is never a hard-lock.

Requirements for the fill/logic layer:

- **The boss lock must NOT gate the region's pre-boss checks**, and must **never be placed
  behind its own boss fog.** Since pre-boss checks gate on the region lock only, fill can place
  the boss lock among them freely. Add a generation-time assert that each boss lock is
  reachable without its own boss lock (i.e. from the region-lock sphere).
- **Behind-fog checks.** For most mainbosses the only thing past the arena fog is the drop
  itself (bosses are terminal in their dungeon). Where a region *does* have checks physically
  past the boss fog, tag those specific locations to gate on the boss lock too. Enumerate these
  in the `BOSS_LOCKS` table per boss (default: just the drop).
- **No new deadlock class.** This is strictly additive to the region graph — a boss lock only
  ever adds a `Has()` clause to locations already inside an owned region. It cannot gate a
  region entrance, so it can't stall the spine.

Worst case, acknowledged and accepted: the boss lock and the region's lone escape-hatch region
lock are the **last two checks** you'd reach in the region, so you clear almost everything
before you can either take the boss or leave. Unlikely, and fine — no mitigation needed.

---

## Spell shops — mixed sorcery/incantation pool (separate item)

Unrelated to boss locks; folding in per the same pass. Spell shops randomize to spells by
default — the requirement is just to **confirm the eligible pool mixes sorceries and
incantations together**, so an incantation can stock a sorcery vendor (Sellen) and a sorcery
can stock an incantation vendor, rather than each vendor being constrained to its own school.

- The right primitive already exists: `_is_spell_code(code)` (`__init__.py:58-60`) is the union
  of both ranges — sorceries `4000-8000` and incantations `2004000-2008000`. Any
  spell-eligibility filter for shop slots must use **this union**, not a per-school test tied to
  the vendor's native school or the location's `sorceries` / `incantations` tag
  (`locations.py`).
- Current state to verify: `SpellShopSpellsOnly` (`options.py:400`) is defined and shipped to
  slot_data (`__init__.py:4060`) but **has no generation-side enforcement in the apworld** —
  grep finds it only in those two places. So the "spells only" constraint is applied
  **client-side** (the C# mod reads slot_data). Fable 5 must: (1) locate where the constraint is
  actually enforced, (2) ensure the eligible set there is the combined pool (`_is_spell_code`
  union), and (3) add a check that a sorcery-in-incant-shop and incant-in-sorcery-shop placement
  are both legal. If it turns out to want fill-side enforcement, gate shop `sorceries|incantations`
  slots on the union predicate, not the tag.

---

## Work items

1. **`BOSS_LOCKS` data (`region_spine.py`).** Add a structure keyed by major sweep group,
   modelled on `CHOKEPOINTS`: `{group_key: (boss_lock_item_name, fog_open_flag,
   [boss_drop_locations], [behind_fog_locations])}`. Populate from the same group set
   `_compute_dungeon_sweeps` uses (legacy_groups + Shaded Castle + Castle Morne). Fold the
   existing `Godrick Lock` / `76967` in as the first entry rather than duplicating it.
2. **Mint boss-lock items (`items.py` + pool builder in `__init__.py`).** One `lock=True` item
   per `BOSS_LOCKS` entry, added to the pool only when `ENABLE_BOSS_LOCKS` and the Shattering
   config is active.
3. **Boss-lock rules (`region_lock_data.py` / `rules_mixin.py`).** Parallel to
   `build_region_lock_rules`: AND `Has("<Boss> Lock")` onto each boss drop location and any
   listed behind-fog location. Do **not** touch region entrances.
4. **Sweep gating (`__init__.py:3225-3328`).** Confirm the sweep trigger inherits the boss-lock
   clause (via the trigger location's rule) so the whole group's auto-grant requires the lock;
   assert it.
5. **Fog flags (`__init__.py` regionOpenFlags + `RegionFogGates` baker).** Allocate a reserved
   boss-lock fog-flag block (after reconciling the `76966/76967` vs `76996/76997/76998`
   contexts), add `region_open_flags["<Boss> Lock"] = <flag>`, and key each boss arena fog wall
   off it. Reuse Godrick's baker wiring as the template.
6. **Generation-time asserts.** (a) each boss lock reachable from the region-lock sphere without
   its own lock; (b) no fog-flag collision; (c) each major group's sweep gated on its boss lock.
6a. **Warp-bypass audit (chokepoints).** For every locked mainboss, confirm no bundled grace or
   warp lands the player past a mid-dungeon fog (Debate Parlor `71401` exclusion is the template).
   See the Chokepoint bosses section.
7. **Spell-shop pool.** Verify/implement the combined `_is_spell_code` pool for spell-shop slots
   (see section above).
8. **Hints/tracker.** The sweep hint already tags "(auto-granted with <boss reward>)"
   (`extend_hint_information`, `__init__.py:3330+`); the boss reward is now lock-gated, so verify
   hint/logic text still reads correctly. Poptracker: the boss lock is a new progression item to
   surface.

## Open questions for implementation

- **Flag range** — final reserved block for boss-lock fog flags (blocked on reconciling the two
  numbering contexts). Pick and document it.
- **Behind-fog checks per boss** — audit which major bosses actually have checks past their
  arena fog vs. only the drop; populate the fourth field of each `BOSS_LOCKS` entry.
- **DLC bosses** — the DLC legacy groups (`__init__.py:3273-3288`: Belurat, Castle Ensis, Shadow
  Keep, Midra's Manse, Enir Ilim, Finger Ruins → Metyr, Rauh → Romina) are in the same group
  computation, so they get boss locks automatically — confirm each has a capturable arena fog
  flag (some DLC fog needs an env/boss-flag capture, per the `CHOKEPOINTS` deferred note,
  `region_spine.py:498-500`).
- **Spell-shop enforcement site** — confirm client-side vs. add fill-side; see spell-shop section.


---

## v0.1 ADDENDUM (implemented 2026-07-03) -- sweep-gate model, NO fog gates

Pivot (Alaric, 2026-07-03): we have no easy way to physically keep the player out of a boss
arena right now, so v0.1 ships WITHOUT the physical layer. The boss lock gates the group's
DUNGEON SWEEP instead:

- **Client** (`sweepLockGates` slot_data, `er_logic::sweep_gate`): a gated trigger's sweep only
  fires while the boss-lock item name is in the cumulative received set. The existing flag-poll
  re-evaluates every tick, so a lock received AFTER the boss kill fires the held sweep
  retroactively -- no staging.
- **Logic** (`build_region_lock_location_rules`): the trigger drop location ANDs `Has(lock)`;
  the sweep-OR in `_apply_dungeon_sweep_logic` wraps the trigger's final rule so members
  inherit the gate. Pre-boss checks stay region-lock-only (escape hatch emergent, unchanged).
- **No flags allocated**: the 76971+ open-flag band is full and nothing physical keys off a
  flag. Work items 5 (fog flags) and 6a (warp-bypass audit) are DEFERRED with the physical
  layer; the flag-range open question is MOOT for v0.1.
- **Killing the boss without the lock**: the boss's own drop check still sends (its location
  flag fires; AP treats it as out-of-logic), the sweep holds until the lock arrives. Goal-send
  is likewise flag-based, so a goal boss killed lock-less still completes the goal.

Known gaps / deviations, deliberate:
- `dungeon_sweep: bosses` (tier 3) overworld GEOMETRIC sweeps ride apconfig `sweep_flags`
  (DefeatFlag-keyed) and are NOT gated -- a legacy boss kill may still sweep its geometric
  bucket at that tier. Fix needs per-boss DefeatFlags (CHOKEPOINT_BOSS_FLAGS pattern); v0.2.
- Castle Morne has NO sweep group in the current computation (the spec's Leonine example was
  stale), so no Leonine lock; add a Castle Morne group first if wanted.
- Groups sealed/absent this seed (spine modes, dlc_only, DLC off) mint no lock and gate
  nothing -- e.g. Morgott Lock under num_regions is auto-pulled because Leyndell is the
  lockless capstone outside SPINE steps... UNLESS the capstone keeps the group present, in
  which case it IS minted and gates the Morgott goal location in logic (fill-sound; physical
  goal-send unaffected). Watch fill pressure in tiny num_regions pools.
- Spell-shop mixed pool: implemented in the C# randomizer fork (Permutation.cs union test);
  the apworld never enforced it (option is bake-side), confirmed 2026-07-03.
