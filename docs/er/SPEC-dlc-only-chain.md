# SPEC: chain logic in `dlc_only` (breadcrumb the DLC region tree)

Status: DRAFT 2026-06-21 (Alaric). No code yet — design only.
Companion to: `SPEC-num-regions-chain.md` (archived, the base-spine chain), `SPEC-dlc-mini-campaign.md`,
`SPEC-completion-scaling.md`. Memory anchors: `er-dlc-only-region-lock`, `er-num-regions-chain-spec`,
`er-dlc-only-spec`, `er-numregions-chain-host-reach`.

---

## 1. Motivation

`dlc_only` is the ~3hr Archipelago target (Land of Shadow as a self-contained multiworld). It already
runs `region_lock` with **Gravesite Plain as the free hub** and the rest of the DLC gated by per-region
`.lock` items (see `er-dlc-only-region-lock`). But region gating alone does **not** create spheres:
with `region_access: warp` + a free hub + `graces_per_region` warps, *every* kept DLC region resolves to
sphere ~1, so `get_spheres()` is flat. That makes hints, `completion_scaling`, and any sphere-keyed
difficulty curve meaningless over the DLC — the exact flatness the base `num_regions_chain` was built to
fix, just never applied to the DLC side.

**Goal:** force the `dlc_only` region opening into a linear `1..N` breadcrumb ladder so the DLC plays as a
graded progression (Gravesite → … → Enir Ilim / Messmer), reusing the base chain machinery rather than
inventing a parallel one.

## 2. What already exists (reuse, don't rebuild)

The base chain (`region_spine.py` + `__init__.py`) gives us, generically:

- `NUM_REGIONS_CHAIN_STEP_LOCK` / `NUM_REGIONS_CHAIN_STEP_HOST_REGIONS` — per-step *lock name* + candidate
  *host region names*.
- `compute_num_regions_chain_order(rng, kept_locks)` — orders kept steps into the `[m_1..m_k]` sequence;
  `m_1` free, `m_{i+1}`'s lock breadcrumbed onto `m_i`'s boss.
- `_num_regions_chain_host(self, step)` in `__init__.py` (L2313) — resolves a host **location** from a
  step's host regions: prefers a remembrance/prominent boss drop, then any non-missable boss, then any
  non-missable check. **Reachability-aware** after `patch_apworld_chain_host_reach_20260621.py`: it only
  keeps host candidates reachable under the chain placed *so far*, else returns `None` and the caller
  precollects the lock (chain stays intact, loses one ramp sphere). **Note:** it takes an integer base-
  SPINE `step` and reads `NUM_REGIONS_CHAIN_STEP_HOST_REGIONS[step]` *internally*, so it is **not** drop-in
  for DLC — refactor it to accept a host-region **list** param (base path passes the map lookup, DLC path
  passes `DLC_CHAIN_HOST_REGIONS[lock]`), keeping the prefer-remembrance + reachability-filter body shared.
- The breadcrumb placement itself (`place_locked_item(lock_{i+1}, host_i)`).
- `patch_apworld_chain_freelink_startgraces_20260621.py` — lights the free first link's grace bundle +
  open flag at load.
- `compute_dlc_mini_scope(...)` + `DLC_MINI_KEPT_LOCKS` / `DLC_MINI_KEPT_REGIONS` — a **fixed** kept set
  for the Messmer goal. This is *not* a chain (the in-file comment is explicit: "the DLC graph is a tree,
  not a line; it is a FIXED kept-region/kept-lock set"). It is the natural scope for Option A below.

The base machinery is keyed on the base `SPINE` indices; `_kept_middle_steps()` reads
`NUM_REGIONS_CHAIN_STEP_LOCK`, none of which contain DLC locks. So **the base chain never fires under
`dlc_only`** — we add a DLC-keyed parallel table and a DLC ordering helper, and reuse everything else.

## 3. The DLC region tree (the thing we must linearize)

`dlc_only` precollects only **Gravesite Lock**; the other 13 DLC locks gate a connected tree rooted at
Gravesite Plain (locks from `items.py` L2829-2844, regions from `region_order_dlc` in `locations.py`):

```
Gravesite Plain                         [Gravesite Lock — precollected, free hub]
├─ Belurat                              [Belurat Lock]            → Belurat Swamp
├─ Ellac River                          [Ellac Lock]
│   └─ Cerulean Coast                   [Cerulean Lock]          → Stone Coffin Fissure
├─ Dragon's Pit → Jagged Peak Foot      [Jagged Peak Lock]
│                  └─ Charo's Hidden Grave [Charo's Lock]
└─ Castle Ensis                         [Ensis Lock]
    └─ Scadu Altus                      [Scadu Altus Lock]
        ├─ Rauh Base                    [Rauh Base Lock]
        │   └─ Ancient Ruins of Rauh    [Ancient Ruins Lock]
        └─ Shadow Keep                  [Shadow Keep Lock]       ← Messmer (goal region under messmer)
            ├─ Recluses' River          [Recluses' Lock]         → Abyssal Woods [Abyssal Lock]
            └─ Enir Ilim                [Enir Ilim Lock + Messmer's Kindling]  = FINAL GOAL
```

14 locks total. The shape is a **tree, not a line** — that is the whole design problem. A chain is linear
`1..N`; the tree has parallel branches (Belurat, Ellac→Cerulean, Jagged→Charo's, Rauh→Ancient, Recluses'→
Abyssal) hanging off the Gravesite→Ensis→Scadu Altus→Shadow Keep→Enir Ilim trunk.

## 4. Two linearization strategies

### Option A — trunk-only spine chain (pairs with `ending_condition: messmer`)

Keep only a single critical path and **seal every branch**, then chain the kept locks in trunk order:

```
Gravesite (free) → Belurat → Ensis → Scadu Altus → Shadow Keep → [Enir Ilim | Messmer goal]
```

This is the `dlc_mini_campaign` kept-set turned into a chain: `DLC_MINI_KEPT_LOCKS` is already
`{Gravesite, Belurat, Ensis, Scadu Altus, Shadow Keep}`. Instead of freeing all kept locks, breadcrumb
them: Belurat Lock on a Gravesite boss, Ensis Lock on a Belurat boss, Scadu Altus Lock on an Ensis boss,
Shadow Keep Lock on a Scadu Altus boss, and the goal (Messmer / Enir Ilim) behind Shadow Keep.

- **Pros:** deterministic, few links (5-6 spheres), reuses `compute_dlc_mini_scope` for the seal, no
  branch-ordering problem, naturally a ~3hr run.
- **Cons:** throws away most of the DLC (Cerulean/Jagged/Rauh/Abyssal all sealed). Good for the *campaign*
  goal, not for "play the whole DLC in graded order".

### Option B — full tree linearization (the real `dlc_only` chain) — RECOMMENDED default

Keep **all** DLC regions, but impose a **topological traversal order** over the 14 locks so each lock can
be breadcrumbed onto the previous link's boss. The only hard constraint is the tree's **parent-before-
child** partial order: a child lock may only be hosted in a region reachable with the chain placed so far.
Within that constraint the order is shuffled per seed for variety (mirror of the base
`compute_num_regions_chain_order`, which shuffles middles but pins Altus last and keeps Dragonbarrow
adjacent to Caelid).

Concretely a valid seed order might be:

```
Gravesite(free) → Ellac → Cerulean → Belurat → Ensis → Jagged Peak → Charo's →
Scadu Altus → Rauh Base → Ancient Ruins → Shadow Keep → Recluses' → Abyssal → Enir Ilim
```

…as long as every lock appears *after* its tree parent. Enir Ilim is pinned **last** (it is the goal
region and the Kindling gate sits there) — the DLC analogue of Altus-pinned-last in the base chain.

- **Pros:** every DLC region keeps a place in the ladder; full 14-sphere gradient; reuses the reachability-
  aware host selector verbatim.
- **Cons:** branch siblings must be threaded into a single line (the topological sort), and the warp-grace
  coverage for off-trunk DLC regions is the open risk (§7).

**Recommendation:** ship Option B as the `dlc_only` chain default; Option A is just Option B's order
restricted to the `messmer` kept-set, so it falls out for free when `ending_condition == messmer` seals
the branches first.

## 5. Proposed implementation

### 5.1 Option / wiring

New opt-in toggle **`dlc_only_chain`** (Bool, default off). It only engages when `dlc_only` is on (warn +
no-op otherwise). Kept separate from `num_regions_chain` because `dlc_only` is `region_lock` over the DLC
tree, not a `num_regions` first-N count — coupling them would make `_kept_middle_steps()` (base-spine
keyed) misfire. The two are mutually exclusive in practice (`dlc_only` strips base checks).

### 5.2 New data in `region_spine.py`

```python
# Per DLC lock: the candidate host region(s) whose boss/checks can carry it, and the lock's
# tree PARENT lock (None = child of the free Gravesite hub). Parent drives the topo order.
DLC_CHAIN_LOCK_PARENT: Dict[str, Optional[str]] = {
    "Belurat Lock":       None,            # off Gravesite
    "Ellac Lock":         None,
    "Cerulean Lock":      "Ellac Lock",
    "Jagged Peak Lock":   None,            # via Dragon's Pit (lock-free)
    "Charo's Lock":       "Jagged Peak Lock",
    "Ensis Lock":         None,
    "Scadu Altus Lock":   "Ensis Lock",
    "Rauh Base Lock":     "Scadu Altus Lock",
    "Ancient Ruins Lock": "Rauh Base Lock",
    "Shadow Keep Lock":   "Scadu Altus Lock",
    "Recluses' Lock":     "Shadow Keep Lock",
    "Abyssal Lock":       "Recluses' Lock",
    "Enir Ilim Lock":     "Shadow Keep Lock",   # pinned LAST regardless (goal)
}

DLC_CHAIN_HOST_REGIONS: Dict[str, List[str]] = {
    # lock -> regions whose boss drop hosts the NEXT link's lock (first = primary)
    "Gravesite Lock":     ["Gravesite Plain", "Belurat Gaol", "Dragon's Pit"],
    "Belurat Lock":       ["Belurat", "Belurat Swamp"],
    "Ellac Lock":         ["Ellac River", "Rivermouth Cave"],
    "Cerulean Lock":      ["Cerulean Coast", "Stone Coffin Fissure"],
    "Jagged Peak Lock":   ["Jagged Peak", "Jagged Peak Foot"],
    "Charo's Lock":       ["Charo's Hidden Grave"],
    "Ensis Lock":         ["Castle Ensis", "Fog Rift Fort"],
    "Scadu Altus Lock":   ["Scadu Altus", "Bonny Gaol"],
    "Rauh Base Lock":     ["Rauh Base", "Scorpion River Catacombs"],
    "Ancient Ruins Lock": ["Ancient Ruins of Rauh"],
    "Shadow Keep Lock":   ["Shadow Keep", "Shadow Keep Storehouse", "Shadow Keep, West Rampart"],
    "Recluses' Lock":     ["Recluses' River", "Darklight Catacombs"],
    "Abyssal Lock":       ["Abyssal Woods", "Midra's Manse"],
    "Enir Ilim Lock":     ["Enir Ilim"],           # goal — no NEXT link to host
}

def compute_dlc_chain_order(rng, kept_locks: Set[str]) -> List[str]:
    """Topological order of kept DLC locks (parent before child); Enir Ilim pinned last;
    siblings shuffled. Mirrors compute_num_regions_chain_order but keyed on lock NAMES and
    the DLC parent map rather than the base SPINE indices."""
```

All host-region names above are confirmed present in `region_order_dlc` (`locations.py` L175+).

### 5.3 `__init__.py` hook

In the existing `dlc_only` precollect block (~L748, where today it precollects only `Gravesite Lock` and
pulls base locks): when `dlc_only_chain` is on, instead of leaving the 13 DLC locks as ordinary
`region_lock` pool items, drive them through the same breadcrumb path the base chain uses:

1. `kept_locks` = all 14 DLC locks (or the `compute_dlc_mini_scope` kept set when `ending_condition ==
   messmer`).
2. `order = compute_dlc_chain_order(self.random, kept_locks)`; precollect `order[0]`'s lock is unnecessary
   — Gravesite is already the precollected free hub, so `order[0]` is the first *gated* link.
3. For each adjacent pair, host = `_num_regions_chain_host` over `DLC_CHAIN_HOST_REGIONS[prev]`;
   `place_locked_item(next_lock, host)`. `None` host → precollect that link (same fallback as base).
4. Set `self._num_regions_chain = True`-equivalent state so the existing slot-data emission (Track B)
   treats the run as a chain (see §6).

The free-first-link start-grace fold is **already correct for free**: Gravesite is the precollected hub and
`dlc_only` already lights its start graces, so no Mt.-Gelmir-style special case is needed (contrast
`patch_apworld_chain_freelink_startgraces_20260621.py`).

## 6. Wire contract / sphere emission

Reuse the frozen §4 contract from `SPEC-num-regions-chain.md`: `completion_scaling`,
`completion_scaling_floor`, `completionScalingBasis`, `regionSphereTargets`. Once the DLC chain produces a
linear `get_spheres()`, `patch_apworld_sphere_kept_only.py` + `patch_apworld_sphere_scaling.py` should emit
DLC `regionSphereTargets` the same way — **verify** the kept-only sphere filter uses
`self._spine_sealed_regions` populated from the DLC seal, not just the base spine.

**Baker bridge gap (Track C):** `patch_baker_sphere_scaling_bridge.py` / `patch_baker_resolver_exact_tiles.py`
map MSB→AP region for the **base** overworld majors only; the DLC overworld lives on **m61** tiles that the
resolver does not yet classify (falls to null = geographic). So sphere-keyed *enemy difficulty* will not
follow the DLC chain until the resolver learns m61→DLC-region. Logic/hints/sphere targets work without it;
difficulty scaling is a Phase 3 follow-up. (See `er-dlc-area-ids`: m61 tiles are shared → need in-game
place-name capture.)

## 7. Risks / open questions (decide before coding)

1. **Warp-grace coverage for off-trunk DLC regions (BIGGEST RISK).** A warp chain needs every kept DLC
   lock to carry its region's entry graces (`grace_data.REGION_LOCK_ITEM` / bundle). The Dragonbarrow gap
   (`er-num-regions-chain-spec`) showed auto-gen can drop a region whose graces pooled under a neighbour;
   DLC overworld m61 tiles are *shared* (`er-dlc-area-ids`), so several DLC regions may have **no resolved
   warp graces**. If a chain link opens with no warp, that sphere is unreachable. **Audit `grace_data` for
   all 14 DLC locks before trusting Option B**; trunk-only Option A touches fewer regions and is safer to
   ship first.
2. **Topo order vs reachability.** The parent map must match the real `create_connection` graph or a lock
   breadcrumbs into an unreachable region → FillError (the `chain_host_reach` failure mode). The
   reachability-aware host selector catches this and precollects, but a wrong parent map silently flattens
   spheres. Gen-test must assert the chain length ≈ kept-lock count (few precollect fallbacks).
3. **`ending_condition: messmer` interaction.** messmer already seals the back half via
   `compute_dlc_mini_scope`. `dlc_only_chain` + messmer = Option A; make the chain order operate on the
   messmer kept set, do **not** double-seal or try to chain sealed locks.
4. **Base prereqs untouched.** `dlc_only` precollects great runes, Crafting Kit, 25 Dragon Hearts — the
   chain does not gate or reorder these; they stay start items.
5. **Side-areas gating on base keys.** Rauh Ruins Limited / Cathedral of Manus Metyr / Belurat Swamp can
   gate on base items (e.g. Imbued Sword Key) absent in `dlc_only` (`er-dlc-only-region-lock`); these
   already fall back to `can_go_to(deep region)`. Confirm the chain order doesn't strand them.
6. **`location_pool: trimmed` overflow.** `er-dlc-only-region-lock` documents that trimmed pools spill all
   locks to start (kills gating). A chain made of precollected-spilled locks is no chain — gate
   `dlc_only_chain` to `location_pool: all`, or surface a warning + read `precollected-to-start` in the
   gen-test.

## 8. Phasing

- **Phase 1 (small):** Option A — chain the existing `dlc_mini_campaign` kept set under `ending_condition:
  messmer`. Reuses `compute_dlc_mini_scope`; ~5 links; lowest grace-coverage risk. Ships the mechanism.
- **Phase 2:** Option B — full 14-lock topological chain for general `dlc_only`. Requires the §7.1 grace
  audit + `compute_dlc_chain_order`.
- **Phase 3:** baker m61→DLC-region resolver so `completion_scaling` difficulty follows the DLC chain
  (Track C extension).

## 9. Work items

1. `options.py`: add `dlc_only_chain` (Bool, default off; no-op unless `dlc_only`).
2. `region_spine.py`: `DLC_CHAIN_LOCK_PARENT`, `DLC_CHAIN_HOST_REGIONS`, `compute_dlc_chain_order`.
3. `__init__.py`: in the `dlc_only` precollect block, when `dlc_only_chain`, breadcrumb the DLC locks via
   `_num_regions_chain_host` instead of leaving them as flat `region_lock` pool items; set chain state for
   emission.
4. **Grace audit** (§7.1): confirm `grace_data` resolves warp graces for all kept DLC locks; patch gaps
   (move-not-copy, per the Dragonbarrow fix).
5. Verify sphere emission (`sphere_kept_only`) includes DLC sealed regions in `_spine_sealed_regions`.
6. GEN-TEST (Windows): `dlc_only: true` + `dlc_only_chain: true` + `location_pool: all`. PASS = SUCCESS, no
   FillError, `precollected-to-start` lists only Gravesite + base prereqs (not the chained DLC locks),
   `ER_SPHERE_TIERS.txt` shows a 1..N DLC gradient. Add a fill-regression yaml under
   `gen-test/fill-regression-yamls/`.
7. (Phase 3) baker m61 resolver for DLC difficulty scaling.

## 10. Deferred / not in scope

- Hand-curated single iconic entry grace per DLC region (needs FMG name extraction).
- Random DLC start hub (re-root off Gravesite) — separate from chaining.
- DLC enemy rando interaction (runs are enemy-OFF; emission isn't gated on it, but re-confirm).
