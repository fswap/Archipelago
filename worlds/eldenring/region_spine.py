"""Region-count / Capital-goal spine (short "reach the capital and kill Morgott" runs).

A small run is defined by an ORDERED spine of overworld region-chunks toward Morgott. The
`region_count` option keeps the first N spine steps; every region NOT kept is SEALED: its lock
item is pulled from the pool (unobtainable) and its checks become locked-vanilla events, so the
fill never has to reach them. Leyndell + Morgott are the always-present capstone goal (gated by
`great_runes_required` as usual), never a toggled step.

This module is pure data + one function. It owns NO Archipelago types; __init__.py consumes it.

Design notes (see SPEC-region-count-morgott.md):
  * Only engages when ending_condition == capital (option value 4). With any other goal the goal
    boss lives past the sealed wall, so region_count is ignored there (the caller warns).
  * "Fixed spine, first-N" (Alaric 2026-06-15): the kept set is deterministic, so the path to
    Morgott is always whole. The caller raises the effective count to a floor that guarantees
    (a) Altus is reachable (the only physical route to Leyndell) and (b) enough great-rune bosses
    are in scope to satisfy great_runes_required.
  * Legacy dungeons fold into their overworld region (Raya Lucaria -> Liurnia, Volcano Manor ->
    Mt. Gelmir). Stormveil keeps its own lock as a milestone step (Godrick = a great rune).
  * Redmane is folded into Caelid (minor post-Radahn sub-area). Its existing "Redmane Lock" rides
    along in the Caelid step so it stays obtainable whenever Caelid is.
  * Dragonbarrow is folded into Caelid too (spine surgery 2026-07-02): its former lock item is
    retired and Dragonbarrow's regions ride the Caelid step under "Caelid Lock".
"""

from typing import Dict, List, Optional, Set, Tuple


# ---- The ordered spine. step (1-based) -> (label, locks owned, AP regions whose checks belong) ----
# Spine surgery 2026-07-02 (SPEC-region-spine-surgery.md): 12 steps. EVERY step owns the lock(s)
# that gate its regions; keeping the step keeps those locks injectable, sealing it removes them.
# The free hub is Roundtable Hold (ALWAYS_OPEN_REGIONS); the rolled start region's lock is
# spawn-granted by __init__.py, so step 1 (Limgrave) owns "Limgrave Lock" like any other step
# (Limgrave is merely the default/most-likely start roll -- no code-level special status).
SPINE: List[Dict] = [
    {
        "name": "Limgrave",
        "locks": {"Limgrave Lock"},
        "regions": [
            "Fringefolk Hero's Grave", "Limgrave", "Stormhill", "Coastal Cave",
            "Church of Dragon Communion", "Groveside Cave", "Stormfoot Catacombs",
            "Limgrave Tunnels", "Murkwater Cave", "Murkwater Catacombs", "Highroad Cave",
            "Deathtouched Catacombs",
        ],
    },
    {
        "name": "Weeping Peninsula",
        "locks": {"Weeping Lock", "Morne Lock"},
        "regions": [
            "Weeping Peninsula", "Impaler's Catacombs", "Tombsward Catacombs",
            "Tombsward Cave", "Morne Tunnel", "Earthbore Cave", "Castle Morne",
        ],
    },
    {
        "name": "Stormveil Castle",          # Godrick -> great rune
        "locks": {"Stormveil Lock"},
        "regions": [
            "Stormveil Start", "Stormveil Castle", "Stormveil Throne",
            "Divine Tower of Limgrave",
        ],
    },
    {
        "name": "Liurnia of The Lakes",      # Rennala (via Raya Lucaria) -> great rune
        "locks": {"Liurnia Lock"},
        "regions": [
            "Liurnia of The Lakes", "Bellum Highway", "Road's End Catacombs",
            "Black Knife Catacombs", "Cliffbottom Catacombs", "Stillwater Cave",
            "Lakeside Crystal Cave", "Academy Crystal Cave", "Raya Lucaria Crystal Tunnel",
            "Caria Manor", "Carian Study Hall", "Carian Study Hall (Inverted)",
            "Ruin-Strewn Precipice",
            "The Four Belfries (Chapel of Anticipation)", "The Four Belfries (Nokron)",
            "The Four Belfries (Farum Azula)",
            "Raya Lucaria Academy", "Raya Lucaria Academy Main",
            "Raya Lucaria Academy Chest", "Raya Lucaria Academy Library",
        ],
    },
    {
        "name": "Caelid",                     # Radahn -> great rune (+ Redmane + Dragonbarrow folded in)
        "locks": {"Caelid Lock", "Redmane Lock"},
        "regions": [
            "Caelid", "Caelid Catacombs", "Gaol Cave", "Sellia Crystal Tunnel",
            "Abandoned Cave", "Minor Erdtree Catacombs", "Great-Jar", "Gale Tunnel",
            "Redmane Castle Post Radahn", "Wailing Dunes", "War-Dead Catacombs",
            "Dragonbarrow", "Dragonbarrow Cave", "Sellia Hideaway", "Divine Tower of Caelid",
        ],
    },
    {
        "name": "Altus Plateau",              # mandatory: the only physical route to Leyndell
        "locks": {"Altus Lock"},
        "regions": [
            "Altus Plateau", "Sainted Hero's Grave", "Unsightly Catacombs",
            "Perfumer's Grotto", "Sage's Cave", "Old Altus Tunnel", "Altus Tunnel",
        ],
    },
    {
        "name": "Mt. Gelmir",                 # Rykard -> great rune (Volcano Manor folded in)
        "locks": {"Mt. Gelmir Lock"},  # Volcano Lock folded into Mt. Gelmir Lock
        "regions": [
            "Mt. Gelmir", "Wyndham Catacombs", "Gelmir Hero's Grave", "Seethewater Cave",
            "Volcano Cave", "Volcano Manor Dungeon", "Volcano Manor Entrance",
            "Volcano Manor Drawing Room", "Volcano Manor", "Volcano Manor Upper",
        ],
    },
    {
        "name": "Siofra/Nokron",              # underground branch A (ex-South East Underground)
        "locks": {"Nokron Lock"},
        "regions": [
            # NOTE: "The Four Belfries (Nokron)" stays in the LIURNIA step (the belfry towers are
            # physically in Liurnia; the portal merely lands in Nokron) -- listing it here too would
            # break the step-region partition invariant (test_step_regions_partition).
            "Siofra River", "Nokron, Eternal City Start", "Nokron, Eternal City",
        ],
    },
    {
        "name": "Ainsel/Nokstella",           # underground branch B (ex-North Underground; Lake of Rot folded in from the retired SW lock)
        "locks": {"Nokstella Lock"},
        "regions": [
            "Ainsel River", "Ainsel River Main", "Deeproot Depths", "Deeproot Depths Upper",
            "Deeproot Depths Boss", "Lake of Rot",
        ],
    },
    {
        "name": "Mountaintops",               # incl. Flame Peak + Forbidden Lands (SPEC 3.4)
        "locks": {"Mountaintops Lock"},
        "regions": [
            "Mountaintops of the Giants", "Flame Peak", "Forbidden Lands",
            "Giant-Conquering Hero's Grave", "Giants' Mountaintop Catacombs",
            "Spiritcaller Cave",
        ],
    },
    {
        "name": "Consecrated Snowfield",      # incl. Hidden Path to the Haligtree (SPEC 3.5)
        "locks": {"Snowfield Lock"},
        "regions": [
            "Consecrated Snowfield", "Hidden Path to the Haligtree",
            "Consecrated Snowfield Catacombs", "Cave of the Forlorn", "Yelough Anix Tunnel",
        ],
    },
    {
        "name": "Haligtree",                  # Elphael is Loretta-gated interior of the same lock
        "locks": {"Haligtree Lock"},
        "regions": [
            "Miquella's Haligtree", "Elphael, Brace of the Haligtree",
        ],
    },
]

# 1-based spine indices whose region holds a great-rune mainboss. Used for the floor calc.
RUNE_STEPS = {3, 4, 5, 7}        # Godrick, Rennala, Radahn, Rykard
ALTUS_STEP = 6                   # the lowest count that physically reaches Leyndell
MAX_PRE_LEYNDELL_RUNES = len(RUNE_STEPS)   # 4 great-rune bosses exist before the capital

# Always kept (hub + the capstone). These have no spine lock; Leyndell is gated by great runes.
ALWAYS_OPEN_REGIONS: Set[str] = {"Menu", "Roundtable Hold"}
GOAL_CAPSTONE_REGIONS: Set[str] = {
    "Capital Outskirts", "Auriza Hero's Grave", "Auriza Side Tomb", "Sealed Tunnel",
    "Leyndell, Royal Capital", "Leyndell, Royal Capital Unmissable",
    "Leyndell, Royal Capital Throne", "Divine Bridge",
}

# The location whose acquisition = beating Morgott (Leyndell Royal Capital mainboss).
MORGOTT_GOAL_LOCATION = "LRC/QB: Remembrance of the Omen King - mainboss drop"


def required_floor(great_runes_required: int) -> int:
    """Lowest region_count that keeps the Capital goal reachable, or raise ValueError if it can't be.

    Need Altus (step 6) physically, AND great_runes_required rune-bosses in scope. Steps 1..6 cover
    runes {Godrick, Rennala, Radahn} = 3; step 7 (Rykard) adds the 4th. More than 4 is impossible
    because only 4 great-rune bosses exist before Leyndell.
    """
    if great_runes_required > MAX_PRE_LEYNDELL_RUNES:
        raise ValueError(
            f"Capital/Morgott goal needs great_runes_required <= {MAX_PRE_LEYNDELL_RUNES} "
            f"(only that many great-rune bosses exist before Leyndell); got {great_runes_required}."
        )
    floor = ALTUS_STEP
    if great_runes_required > len({s for s in RUNE_STEPS if s <= ALTUS_STEP}):
        floor = max(floor, 7)     # need Rykard too
    return floor


def compute_region_scope(
    region_count: int,
    great_runes_required: int,
    all_region_names: Set[str],
    all_lock_names: Set[str],
) -> Tuple[Set[str], Set[str], Set[str], Set[str], int]:
    """Resolve the spine scope for a Capital/Morgott run.

    region_count : the option value (>= 1; caller has already gated on >0 + ending==capital).
    great_runes_required : option value, used for the reachability floor.
    all_region_names : every AP region in this seed (base [+ DLC]).
    all_lock_names : every lock item name that exists (item_table lock=True).

    Returns (kept_regions, sealed_regions, kept_locks, sealed_locks, effective_count).
      kept_regions  : regions that stay live (spine[:N] + always-open + capstone).
      sealed_regions: all_region_names - kept_regions  (checks -> events, unreachable).
      kept_locks    : lock items still injected (owned by a kept spine step).
      sealed_locks  : all_lock_names - kept_locks  (pulled from pool, unobtainable).
      effective_count: region_count raised to required_floor() if needed.
    """
    effective = max(int(region_count), required_floor(great_runes_required))
    effective = min(effective, len(SPINE))

    kept_regions: Set[str] = set(ALWAYS_OPEN_REGIONS) | set(GOAL_CAPSTONE_REGIONS)
    kept_locks: Set[str] = set()
    for step in SPINE[:effective]:
        kept_regions.update(step["regions"])
        kept_locks.update(step["locks"])

    # Only consider regions/locks that actually exist this seed.
    kept_regions &= (all_region_names | ALWAYS_OPEN_REGIONS)
    kept_locks &= all_lock_names

    sealed_regions = set(all_region_names) - kept_regions
    sealed_locks = set(all_lock_names) - kept_locks
    return kept_regions, sealed_regions, kept_locks, sealed_locks, effective


# ===== num_regions CHAIN order (SPEC-num-regions-chain.md  3 / 5) ========================
# Track A: turn the kept num_regions middles into a linear lock-breadcrumb CHAIN so the AP
# fill spheres become 1..N. Sphere 1 is the Roundtable hub + the spawn-granted start region
# (link 0). The rolled middle majors are shuffled by the world rng, with Altus PINNED LAST
# among the middles (capstone tail: Altus -> Capital Outskirts -> Leyndell; Leyndell is
# great-rune gated, has no lock and is the terminus). __init__.py consumes this order: it
# precollects the first middle's lock and breadcrumbs every later middle's lock onto the PRIOR
# middle's prominent boss drop.

# Per (1-based) middle SPINE step: the region whose boss hosts the NEXT link's lock, and the
# lock item this step contributes to the chain (the one gating its overworld region under
# region_lock / REGION_LOCK_ITEM). The host REGION is resolved dynamically in __init__.py from
# this region's actual locations (prefer a remembrance/prominent boss drop, then any
# non-missable boss drop, then any non-missable check), so a region without a great-rune
# remembrance (Weeping / Altus / the 2026-07-02 spine-surgery steps 8..12) still gets a stable
# host. Only the LOCK NAME and the candidate host-region NAMES are fixed here. Steps 13..16 are
# the cave/torch bundle steps (see CAVE_BUNDLE_STEPS; renumbered from 9..12 when the spine grew
# to 12 steps, spine surgery 2026-07-02).
NUM_REGIONS_CHAIN_STEP_LOCK: Dict[int, str] = {
    1: "Limgrave Lock",   # LIMGRAVE_ROLL 2026-07-03: ordinary chain-capable middle (HANDOFF-LIMGRAVE-ROLL A)
    2: "Weeping Lock",
    3: "Stormveil Lock",
    4: "Liurnia Lock",
    5: "Caelid Lock",
    6: "Altus Lock",
    7: "Mt. Gelmir Lock",
    8: "Nokron Lock",
    9: "Nokstella Lock",
    10: "Mountaintops Lock",
    11: "Snowfield Lock",
    12: "Haligtree Lock",
    13: "Spelunker's Torch",                   # Limgrave Underground (limgrave_underground)
    14: "Spelunker's Ghostflame Torch",        # Liurnia Caves (liurnia_caves)
    15: "Spelunker's Steel-Wire Torch",        # Altus Caves (altus_caves)
    16: "Spelunker's Beast-Repellent Torch",   # Mountaintops Caves (mountaintops_caves)
}

# The overworld AP region(s) whose checks/bosses belong to each middle step, used by __init__.py
# to find a breadcrumb HOST location. First name is the primary (where the prominent boss lives);
# the rest are fallbacks searched in order if the primary has no usable host.
NUM_REGIONS_CHAIN_STEP_HOST_REGIONS: Dict[int, List[str]] = {
    1: ["Limgrave", "Stormhill"],  # LIMGRAVE_ROLL: no mainboss -- field bosses host via the picker's non-missable-boss fallback
    2: ["Weeping Peninsula"],
    3: ["Stormveil Throne", "Stormveil Castle", "Stormveil Start"],
    4: ["Raya Lucaria Academy Library", "Raya Lucaria Academy", "Liurnia of The Lakes"],
    5: ["Caelid"],  # no-wailing-dunes-host: NOT Wailing Dunes -- Radahn's drop is Altus-gated, a breadcrumb lock there deadlocks (Altus Lock <-> Wailing Dunes). Dragonbarrow rides Caelid now; Caelid proper stays the host.
    6: ["Altus Plateau"],
    7: ["Volcano Manor", "Mt. Gelmir"],
    8: ["Siofra River"],   # NOT Nokron: "Nokron, Eternal City Start" is Starscourge(Radahn)-gated; a breadcrumb there could deadlock when Caelid is sealed.
    9: ["Ainsel River"],   # branch entry; Ainsel River Main / Nokstella sit behind quest-flavored interior gates.
    10: ["Mountaintops of the Giants"],
    11: ["Consecrated Snowfield"],
    12: ["Miquella's Haligtree"],   # Elphael is Loretta-gated interior; the outer Haligtree hosts.
    13: ["Stormfoot Catacombs", "Limgrave Tunnels", "Murkwater Catacombs", "Deathtouched Catacombs",
         "Fringefolk Hero's Grave", "Coastal Cave", "Groveside Cave", "Murkwater Cave",
         "Highroad Cave", "Church of Dragon Communion"],
    14: ["Black Knife Catacombs", "Road's End Catacombs", "Cliffbottom Catacombs", "Stillwater Cave",
         "Lakeside Crystal Cave", "Academy Crystal Cave", "Raya Lucaria Crystal Tunnel",
         "Ruin-Strewn Precipice"],
    15: ["Sainted Hero's Grave", "Unsightly Catacombs", "Perfumer's Grotto", "Sage's Cave",
         "Old Altus Tunnel", "Altus Tunnel"],
    16: ["Giants' Mountaintop Catacombs", "Giant-Conquering Hero's Grave", "Spiritcaller Cave",
         "Consecrated Snowfield Catacombs", "Cave of the Forlorn", "Yelough Anix Tunnel"],
}


def _kept_middle_steps(kept_locks: Set[str]) -> List[int]:
    """Which 1-based middle SPINE steps are kept, derived from the kept-lock set.

    A middle step is 'kept' iff its chain lock is in kept_locks (compute_num_regions_scope put
    every kept step's locks into kept_locks). Returns them in ascending SPINE order.
    """
    return [s for s in sorted(NUM_REGIONS_CHAIN_STEP_LOCK)
            if NUM_REGIONS_CHAIN_STEP_LOCK[s] in kept_locks]


def compute_num_regions_chain_order(rng, kept_locks: Set[str]) -> List[int]:
    """Order the kept MIDDLE steps into the chain sequence (1-based SPINE indices).

    rng        : world.random (reproducible per seed).
    kept_locks : the kept-lock set returned by compute_num_regions_scope.

    Returns [m_1, m_2, ..., m_k] where the regions open in that order off the hub:
    m_1's lock is free (precollected), m_{i+1}'s lock is breadcrumbed onto m_i's boss. Altus
    (step 6) is forced to the END (capstone tail); every other kept middle is a plain shuffle.
    (The old Dragonbarrow-after-Caelid adjacency special case is GONE -- the 2026-07-02 spine
    surgery folded Dragonbarrow into the Caelid step, and every remaining middle has its own
    hub warp via its lock, so no adjacency pinning is needed.)
    """
    middles = _kept_middle_steps(kept_locks)
    altus = ALTUS_STEP if ALTUS_STEP in middles else None
    rest = [s for s in middles if s != altus]
    rng.shuffle(rest)
    order = rest + ([altus] if altus is not None else [])
    return order


# ===== DLC mini-campaign (Gravesite -> Messmer) =========================================
# A short Land-of-Shadow run: keep only the front-half DLC and end at Messmer the Impaler.
# Unlike the base SPINE this is not a numbered first-N chain (the DLC graph is a tree, not a
# line); it is a FIXED kept-region / kept-lock set. Everything in region_order_dlc not kept is
# sealed exactly like a spine seal (lock pulled from the pool, checks -> locked-vanilla events).
# Derived from the DLC create_connection graph + DLC _add_entrance_rule lock gates in
# __init__.py; see SPEC-dlc-mini-campaign.md. Base regions/locks are NOT touched (dlc_only transit).

# The location whose acquisition = beating Messmer (lives in the 'Shadow Keep Storehouse' table).
MESSMER_GOAL_LOCATION = "SK/DCE: Remembrance of the Impaler - mainboss drop"

# Locks kept in the pool (Gravesite Lock is additionally precollected/free under dlc_only).
DLC_MINI_KEPT_LOCKS: Set[str] = {
    "Gravesite Lock", "Belurat Lock", "Ensis Lock", "Scadu Altus Lock", "Shadow Keep Lock",
}

# DLC regions reachable using ONLY the kept locks (every other DLC lock is pulled). Anything in
# region_order_dlc not listed here is sealed. Keep in sync with the DLC connection graph.
DLC_MINI_KEPT_REGIONS: Set[str] = {
    # Gravesite hub + its lock-free neighbours
    "Gravesite Plain", "Belurat Gaol", "Dragon's Pit", "Fog Rift Catacombs",
    # Belurat (Divine Beast Dancing Lion)
    "Belurat", "Belurat Swamp",
    # Castle Ensis (Rellana); Fog Rift Fort shares the Ensis Lock
    "Castle Ensis", "Fog Rift Fort",
    # Scadu Altus and its lock-free children
    "Scadu Altus", "Bonny Gaol", "Ruined Forge of Starfall Past", "Rauh Ruins Limited",
    # SEALED in messmer (option 2, 2026-06-21): Cathedral of Manus Metyr / Finger Ruins of
    # Miyr (Metyr) / Finger Ruins of Dheo are unreachable here -- the Cathedral 3-bell
    # questline needs Finger Ruins of Rhia, which is on the sealed Cerulean branch. Dropped
    # from the kept set so they seal cleanly instead of being dead checks.
    # Shadow Keep (Messmer) and everything reached through its lock
    "Shadow Keep", "Shadow Keep Storehouse", "Shadow Keep, West Rampart",
    "Shadow Keep, Church District", "Shadow Keep, Church District Lower", "Scadutree Base",
    "Shadow Keep Storehouse Back", "Scaduview", "Hinterland",
}


def compute_dlc_mini_scope(
    all_dlc_region_names: Set[str],
    all_lock_names: Set[str],
    dlc_lock_names: Set[str],
) -> Tuple[Set[str], Set[str], Set[str], Set[str]]:
    """Resolve the seal scope for the DLC mini-campaign (Messmer goal).

    all_dlc_region_names : every DLC AP region this seed (region_order_dlc).
    all_lock_names       : every lock item that exists (item_table lock=True).
    dlc_lock_names       : the lock items that gate DLC regions, so base locks (dlc_only
                           transit) are never sealed.

    Returns (kept_regions, sealed_regions, kept_locks, sealed_locks).
    """
    kept_regions = (set(DLC_MINI_KEPT_REGIONS) & set(all_dlc_region_names)) | set(ALWAYS_OPEN_REGIONS)
    sealed_regions = set(all_dlc_region_names) - kept_regions
    kept_locks = set(DLC_MINI_KEPT_LOCKS) & set(all_lock_names)
    sealed_locks = (set(dlc_lock_names) & set(all_lock_names)) - kept_locks
    return kept_regions, sealed_regions, kept_locks, sealed_locks


# ===== DLC-only chain (SPEC-dlc-only-chain.md) ==========================================
# Linearize the DLC region tree into a breadcrumb chain. The tree (root = the free Gravesite
# hub) is parent->child; a chain needs a single line, so we topologically order the kept locks
# (parent before child) and breadcrumb each onto the previous link's boss. Phase 1 only uses the
# messmer kept-set (Gravesite/Belurat/Ensis/Scadu Altus/Shadow Keep); the full 14-lock maps below
# are populated ready for Phase 2 (the whole dlc_only tree).

# lock -> its tree PARENT lock (None = child of the free Gravesite hub). Drives the topo order:
# a child lock's region only opens once its parent is reachable, so the parent must come first.
DLC_CHAIN_LOCK_PARENT: Dict[str, Optional[str]] = {
    "Belurat Lock":       None,                 # off Gravesite
    "Ellac Lock":         None,
    "Cerulean Lock":      "Ellac Lock",
    "Jagged Peak Lock":   None,                 # via Dragon's Pit (lock-free)
    "Charo's Lock":       "Jagged Peak Lock",
    "Ensis Lock":         None,
    "Scadu Altus Lock":   "Ensis Lock",
    "Rauh Base Lock":     "Scadu Altus Lock",
    "Ancient Ruins Lock": "Rauh Base Lock",
    "Shadow Keep Lock":   "Scadu Altus Lock",
    "Recluses' Lock":     "Shadow Keep Lock",
    "Abyssal Lock":       "Recluses' Lock",
    "Enir Ilim Lock":     "Shadow Keep Lock",   # pinned last under the full-tree (goal)
}

# lock -> the DLC AP region(s) whose boss drop hosts the NEXT link's lock (first = primary).
# "Gravesite Lock" hosts the FIRST gated link (the free root). All names verified present in
# locations.region_order_dlc.
DLC_CHAIN_HOST_REGIONS: Dict[str, List[str]] = {
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
    "Enir Ilim Lock":     ["Enir Ilim"],
}

# Locks pinned to the END of the chain (deepest = the goal region's gate).
DLC_CHAIN_PIN_LAST = "Shadow Keep Lock"     # Phase 1 (messmer): Shadow Keep holds Messmer
DLC_CHAIN_FREE_ROOT = "Gravesite Lock"      # always the free precollected hub


def compute_dlc_mini_chain_order(rng, kept_locks: Set[str]) -> List[str]:
    """Topologically order the messmer kept-set DLC locks into a linear breadcrumb chain.

    rng        : world.random (reproducible per seed).
    kept_locks : the kept-lock set from compute_dlc_mini_scope (includes Gravesite Lock).

    Returns the GATED links only (Gravesite Lock -- the free precollected hub -- is excluded):
    [l_1, ..., l_k] where l_1's lock is breadcrumbed onto a Gravesite boss and l_{i+1}'s onto
    l_i's boss. Parent-before-child is enforced via DLC_CHAIN_LOCK_PARENT (a child lock's region
    only opens once its parent is reachable); DLC_CHAIN_PIN_LAST is forced to the END (Messmer =
    the goal, the deepest region). Siblings are shuffled per seed. Mirrors
    compute_num_regions_chain_order but keyed on lock names + the DLC tree parent map."""
    nodes = set(kept_locks) - {DLC_CHAIN_FREE_ROOT}
    parent = {n: DLC_CHAIN_LOCK_PARENT.get(n) for n in nodes}
    pinned_last = DLC_CHAIN_PIN_LAST if DLC_CHAIN_PIN_LAST in nodes else None
    pool = nodes - ({pinned_last} if pinned_last else set())

    placed: List[str] = []
    placed_set: Set[str] = set()

    def _available() -> List[str]:
        out = []
        for n in pool:
            if n in placed_set:
                continue
            p = parent.get(n)
            # parent satisfied if: free root / outside the kept set / already placed.
            if p is None or p == DLC_CHAIN_FREE_ROOT or p not in nodes or p in placed_set:
                out.append(n)
        return sorted(out)   # deterministic base order before the rng pick

    while len(placed) < len(pool):
        avail = _available()
        if not avail:
            # Unsatisfiable parent / cycle (should not happen for the messmer tree); flush the
            # remainder in a stable order so generation never hangs.
            for n in sorted(pool - placed_set):
                placed.append(n)
                placed_set.add(n)
            break
        pick = rng.choice(avail)
        placed.append(pick)
        placed_set.add(pick)

    if pinned_last:
        placed.append(pinned_last)
    return placed


# ===== Godrick mini-campaign (Limgrave -> Stormveil -> Godrick) =========================
# The shortest base-game run: keep only the first three spine steps (Limgrave, Weeping
# Peninsula, Stormveil Castle) and end at Godrick the Grafted in the Stormveil throne. Like
# the DLC mini-campaign this is a FIXED kept set (not a numbered first-N count the user
# tunes), but it reuses the first three SPINE entries above so the kept regions/locks stay
# in sync with the Capital spine. Everything else -- the rest of the base game AND all DLC
# regions if the DLC is on -- is sealed exactly like a Capital-spine seal (lock pulled from
# the pool, checks -> locked-vanilla events). Leyndell / Morgott (the Capital capstone) is
# NOT kept here; it lives past the wall. See SPEC-region-count-morgott.md for the seal path.

# The location whose acquisition = beating Godrick (Stormveil Throne mainboss drop).
GODRICK_GOAL_LOCATION = "SV/SeC: Remembrance of the Grafted - mainboss drop"

# Spine steps kept for the Godrick goal: 1 Limgrave, 2 Weeping Peninsula, 3 Stormveil Castle.
GODRICK_KEPT_STEPS = 3
# Locks that exist ONLY to add spheres to the Godrick mini-campaign. Kept in godrick scope
# (below) and injected only when ending_condition == godrick (see __init__ inject pass).
GODRICK_ONLY_LOCKS: Set[str] = {"Stormhill Lock", "Godrick Lock"}


# ---- Boss chokepoint locks + sweep split (SPEC-chokepoint-locks.md) ----
# after_region -> (before_regions, choke_trigger_locations). The trigger is the choke boss's
# DROP location (full description); the client already watches its guarding event flag (the
# boss DefeatFlag) via location_flags, so the sweep needs no raw flag and the lock gates purely
# on reaching that drop. Opt in with extra_region_locks: chokepoint_locks. v1 = the two cleanly
# region-split base chokepoints; see the spec for the deferred ones (Leyndell/Godfrey shade has
# no drop, Raya Lucaria needs a back-half carve, the DLC ones need an env/boss flag capture).
CHOKEPOINTS: Dict[str, Tuple[List[str], List[str]]] = {
    # Crumbling Farum Azula: Godskin Duo (flag 510140) gates the post-Godskin half
    # (Maliketh / Dragonlord Placidusax).
    "Farum Azula Main": (
        ["Farum Azula"],
        ["FA/DTT: Ash of War: Black Flame Tornado - boss drop"],
    ),
    # Miquella's Haligtree -> Elphael: Loretta, Knight of the Haligtree (flag 510190) gates the
    # whole Elphael city (-> Malenia). Two drop locations; the first available is used.
    "Elphael, Brace of the Haligtree": (
        ["Miquella's Haligtree"],
        ["MH/HTP: Loretta's War Sickle - boss drop",
         "MH/HTP: Loretta's Mastery - boss drop"],
    ),
}


# Choke boss DefeatFlags (diste/Base/enemy.txt) for the v1 chokepoints above. Used to
# re-home each dungeon's BEFORE-half onto its mid-boss in bosses-mode sweep (the geometric
# attribution otherwise lumps the whole legacy area onto its lowest-id boss = the END boss).
# Keyed by after_region (same key as CHOKEPOINTS). See patch_apworld_chokepoint_boss_attribution.py.
CHOKEPOINT_BOSS_FLAGS: Dict[str, int] = {
    "Farum Azula Main": 13000850,                # Godskin Duo (m13)
    "Elphael, Brace of the Haligtree": 15000850,  # Loretta, Knight of the Haligtree (m15)
}


def compute_godrick_scope(
    all_region_names: Set[str],
    all_lock_names: Set[str],
) -> Tuple[Set[str], Set[str], Set[str], Set[str]]:
    """Resolve the seal scope for the Godrick mini-campaign.

    all_region_names : every AP region this seed (base [+ DLC if enabled]).
    all_lock_names   : every lock item that exists (item_table lock=True).

    Keeps SPINE[:GODRICK_KEPT_STEPS] (Limgrave / Weeping / Stormveil) plus the always-open
    hub; seals every other region and every lock those kept steps do not own (the DLC, if
    present this seed, is sealed wholesale). Returns
    (kept_regions, sealed_regions, kept_locks, sealed_locks).
    """
    kept_regions: Set[str] = set(ALWAYS_OPEN_REGIONS)
    kept_locks: Set[str] = set()
    for step in SPINE[:GODRICK_KEPT_STEPS]:
        kept_regions.update(step["regions"])
        kept_locks.update(step["locks"])
    kept_locks |= GODRICK_ONLY_LOCKS  # godrick-only granularity locks stay in scope
    # Only consider regions/locks that actually exist this seed.
    kept_regions &= (set(all_region_names) | set(ALWAYS_OPEN_REGIONS))
    kept_locks &= set(all_lock_names)
    sealed_regions = set(all_region_names) - kept_regions
    sealed_locks = set(all_lock_names) - kept_locks
    return kept_regions, sealed_regions, kept_locks, sealed_locks


# ===== num_regions (random short capital run) ===========================================
# A short "reach Leyndell and kill Morgott" run like region_count, but the kept overworld majors
# are a RANDOM subset instead of the deterministic first-N spine. Limgrave (the free sphere-1 hub)
# and the Leyndell / Morgott capstone are ALWAYS kept and both count toward num_regions; the middle
# majors (Weeping .. Haligtree, SPINE steps 2..12) are rolled. A great-rune floor keeps enough great-rune bosses in
# scope to open Leyndell. Reachability is by WARP (the caller forces region_access=warp), so a
# non-contiguous random subset is still reachable from the Limgrave hub via each region's own lock.
# Everything not kept is sealed exactly like a region_count seal (lock pulled, checks -> events).
# See SPEC-num-regions.md.

# 1-based SPINE indices that are "middle" overworld majors eligible for the random roll
# (step 1 Limgrave is the always-kept free hub; the Leyndell capstone is the always-kept goal).
NUM_REGIONS_MIDDLE_STEPS: List[int] = list(range(2, 13))   # Weeping .. Haligtree (steps 2..12; Dragonbarrow folded into Caelid, spine surgery 2026-07-02)


def num_regions_floor(great_runes_required: int) -> int:
    """STRUCTURAL minimum num_regions: Limgrave + Leyndell + Altus (= 3). Altus is the only
    route into the capital (Leyndell has no warp lock). Great runes NO LONGER factor in: the
    deficit vs great_runes_required is injected into the item pool from sealed rune bosses
    (rune/region decoupling, 2026-07-02), so rune availability never constrains the roll.

    great_runes_required is still VALIDATED here: only MAX_PRE_LEYNDELL_RUNES rune bosses exist
    before the capital, so a higher requirement can never be satisfied under num_regions. The
    ValueError surfaces as OptionError via the caller's wrap.
    """
    if great_runes_required > MAX_PRE_LEYNDELL_RUNES:
        raise ValueError(
            f"num_regions capital goal needs great_runes_required <= {MAX_PRE_LEYNDELL_RUNES} "
            f"(only that many great-rune bosses exist before Leyndell); got {great_runes_required}."
        )
    return 3  # Limgrave + Leyndell + Altus; runes come from the pool deficit injector


def compute_num_regions_scope(
    rng,
    num_regions: int,
    great_runes_required: int,
    all_region_names: Set[str],
    all_lock_names: Set[str],
    active_cave_steps: Set[int] = frozenset(),
) -> Tuple[Set[str], Set[str], Set[str], Set[str], int]:
    """Resolve a RANDOM short-capital seal scope.

    rng                  : a seeded RNG (world.random) -- the roll is reproducible per seed.
    num_regions          : option value (>= 1; caller gated on >0 + capital + lock logic).
    great_runes_required : option value, used for the rune-boss floor.
    all_region_names     : every AP region this seed (base [+ DLC]).
    all_lock_names       : every lock item that exists (item_table lock=True).

    Returns (kept_regions, sealed_regions, kept_locks, sealed_locks, effective_count), the same
    shape as compute_region_scope. effective_count is num_regions raised to num_regions_floor()
    (and capped at "all majors") when needed.
    """
    floor = num_regions_floor(great_runes_required)
    _caves = [s for s in sorted(active_cave_steps) if s in CAVE_BUNDLE_STEPS]
    _active_cave_dungeons = set()
    for _cs in _caves:
        _active_cave_dungeons |= set(CAVE_BUNDLE_STEPS[_cs]["regions"])
    max_total = 2 + len(NUM_REGIONS_MIDDLE_STEPS) + len(_caves)   # Limgrave + Leyndell + middles + active caves
    effective = max(int(num_regions), floor)
    effective = min(effective, max_total)
    need_random = effective - 2                              # middle steps still to roll

    rune_steps = [s for s in NUM_REGIONS_MIDDLE_STEPS if s in RUNE_STEPS]
    nonrune_steps = [s for s in NUM_REGIONS_MIDDLE_STEPS if s not in RUNE_STEPS]

    # 0) Altus is the ONLY route to Leyndell (the capstone has no warp lock), so force it in.
    picked = [ALTUS_STEP] if (ALTUS_STEP in NUM_REGIONS_MIDDLE_STEPS and need_random >= 1) else []
    # 1) great-rune guarantee REMOVED (rune/region decoupling 2026-07-02): rune availability
    #    is satisfied by the pool deficit injector in __init__ (sealed rune bosses' runes join
    #    the pool), so the roll is free -- no rune-step bias, better kept-set diversity.
    # 2) fill the remaining slots at random from whatever middle steps are left.
    rest_pool = [s for s in (rune_steps + nonrune_steps + _caves) if s not in picked]  # caves COMPETE for fill slots
    n_fill = min(max(0, need_random - len(picked)), len(rest_pool))
    if n_fill > 0:
        picked += list(rng.sample(rest_pool, n_fill))

    kept_steps = [SPINE[0]] + [
        ({"regions": CAVE_BUNDLE_STEPS[s]["regions"], "locks": {CAVE_BUNDLE_STEPS[s]["lock"]}}
         if s in CAVE_BUNDLE_STEPS else SPINE[s - 1])
        for s in picked
    ]   # SPINE[0] = Limgrave (free hub); cave steps split out of their parent
    _picked_cave_dungeons = {r for s in picked if s in CAVE_BUNDLE_STEPS
                             for r in CAVE_BUNDLE_STEPS[s]["regions"]}
    kept_regions: Set[str] = set(ALWAYS_OPEN_REGIONS) | set(GOAL_CAPSTONE_REGIONS)
    kept_locks: Set[str] = set()
    for step in kept_steps:
        kept_regions.update(step["regions"])
        kept_locks.update(step["locks"])
    # Active cave dungeons are governed ONLY by their own cave step: drop any pulled in via a
    # kept parent overworld step unless that cave step was itself picked.
    kept_regions -= (_active_cave_dungeons - _picked_cave_dungeons)

    # Only consider regions/locks that actually exist this seed.
    kept_regions &= (set(all_region_names) | set(ALWAYS_OPEN_REGIONS))
    kept_locks &= set(all_lock_names)

    sealed_regions = set(all_region_names) - kept_regions
    sealed_locks = set(all_lock_names) - kept_locks
    return kept_regions, sealed_regions, kept_locks, sealed_locks, effective


# ===== num_regions POOL rune-source (SPEC-num-regions-pool-runes.md) =====================
# Sibling of compute_num_regions_scope for num_regions_rune_source == pool. The great-rune floor
# is DROPPED (the runes are injected into the item pool by __init__.py, not kept as boss regions),
# and Limgrave is NOT force-kept -- ALL twelve overworld majors (SPINE steps 1..12, Limgrave
# through Haligtree) are ONE uniform rollable/sealable pool (the old "[1] + middles" special-
# casing dissolved with the Roundtable hub re-root, spine surgery 2026-07-02). The only
# always-kept content is the Roundtable hub + the Leyndell capstone, so the content floor is 1
# rolled major. Reachability is by WARP from the Roundtable hub (the caller forces
# region_access=warp and sets the Roundtable-hub re-root), so a non-contiguous random subset --
# including a sealed Limgrave / Altus -- is still reachable via each region's lock.

# Every overworld major step (1-based SPINE index) is rollable in pool mode: steps 1..12 uniformly.
# Underground steps 8 (Siofra/Nokron = Nokron Lock) and 9 (Ainsel/Nokstella = Nokstella Lock)
# RE-ENABLED 2026-07-04: the underground map now paints via the client's underground map
# VIEW-unlock flag 82001 (patch_underground_map_unlock.py; memory er-underground-map-quadrant-flags).
# All 12 spine steps are rollable in pool mode again.
NUM_REGIONS_POOL_STEPS: List[int] = list(range(1, len(SPINE) + 1))


def compute_num_regions_scope_pool(
    rng,
    num_regions: int,
    all_region_names: Set[str],
    all_lock_names: Set[str],
    active_cave_steps: Set[int] = frozenset(),
    chain_excludes_limgrave: bool = False,
) -> Tuple[Set[str], Set[str], Set[str], Set[str], int]:
    """Resolve a RANDOM short-capital seal scope with the great runes sourced from the POOL.

    rng              : a seeded RNG (world.random) -- the roll is reproducible per seed.
    num_regions      : option value (caller gated on >0 + capital + lock logic). Floored to 1.
    all_region_names : every AP region this seed (base [+ DLC]).
    all_lock_names   : every lock item that exists (item_table lock=True).

    Returns (kept_regions, sealed_regions, kept_locks, sealed_locks, effective_count), the same
    shape as compute_num_regions_scope. effective_count = number of overworld MIDDLE majors kept
    (>= 1), NOT counting the always-kept Roundtable hub or the Leyndell capstone. No great-rune
    floor and no Altus force -- the runes ride the pool and warp ignores adjacency.
    """
    _caves = [s for s in sorted(active_cave_steps) if s in CAVE_BUNDLE_STEPS]
    _active_cave_dungeons = set()
    for _cs in _caves:
        _active_cave_dungeons |= set(CAVE_BUNDLE_STEPS[_cs]["regions"])
    # chain_excludes_limgrave is IGNORED (kept only for caller signature compatibility --
    # __init__.py passes it positionally): with the Roundtable hub re-root (spine surgery
    # 2026-07-02) Limgrave is an ordinary step -- its lock exists and the rolled start region
    # is spawn-granted by __init__, so the old "rolled Limgrave cannot join the breadcrumb
    # chain" exclusion is gone. Pool mode always rolls over steps 1..12.
    _pool_steps = NUM_REGIONS_POOL_STEPS
    max_total = len(_pool_steps) + len(_caves)    # overworld majors + active caves
    effective = max(int(num_regions), 1)                    # floor of 1 rolled major is fine
    effective = min(effective, max_total)

    # numregions-pool-keep-altus FIX: Altus is mandatory capstone-route overhead. The lockless
    # Leyndell capstone (Capital Outskirts -> Leyndell) has NO warp lock and is reachable ONLY
    # via the Altus geographic edge, so a sealed Altus strands the goal -> can_beat_game
    # 'unbeatable'. Add one slot for Altus (mirrors the regions-mode force-keep) rather than
    # displacing a rolled content region, then pin Altus into the roll. Cave steps COMPETE for
    # the remaining slots alongside the overworld majors.
    if ALTUS_STEP in _pool_steps:
        effective = min(effective + 1, max_total)
        _rest_pool = [s for s in _pool_steps if s != ALTUS_STEP] + _caves
        picked = [ALTUS_STEP] + list(rng.sample(_rest_pool, max(0, effective - 1)))
    else:
        picked = list(rng.sample(list(_pool_steps) + _caves, effective))

    kept_steps = [
        ({"regions": CAVE_BUNDLE_STEPS[s]["regions"], "locks": {CAVE_BUNDLE_STEPS[s]["lock"]}}
         if s in CAVE_BUNDLE_STEPS else SPINE[s - 1])
        for s in picked
    ]             # NO forced SPINE[0]/Limgrave; cave steps split out of their parent
    _picked_cave_dungeons = {r for s in picked if s in CAVE_BUNDLE_STEPS
                             for r in CAVE_BUNDLE_STEPS[s]["regions"]}
    kept_regions: Set[str] = set(ALWAYS_OPEN_REGIONS) | set(GOAL_CAPSTONE_REGIONS)
    kept_locks: Set[str] = set()
    for step in kept_steps:
        kept_regions.update(step["regions"])
        kept_locks.update(step["locks"])
    # Active cave dungeons are governed ONLY by their own cave step: drop any pulled in via a
    # kept parent overworld step unless that cave step was itself picked.
    kept_regions -= (_active_cave_dungeons - _picked_cave_dungeons)

    # Only consider regions/locks that actually exist this seed.
    kept_regions &= (set(all_region_names) | set(ALWAYS_OPEN_REGIONS))
    kept_locks &= set(all_lock_names)

    sealed_regions = set(all_region_names) - kept_regions
    sealed_locks = set(all_lock_names) - kept_locks
    return kept_regions, sealed_regions, kept_locks, sealed_locks, effective


# 1-based SPINE step -> the great-rune ITEM whose boss lives in that step's region. Used by
# __init__.py to compute the deficit-rune injection in pool mode. Morgott's Great Rune is NOT here:
# it is the goal-side Leyndell mainboss drop and stays where the goal logic expects it.
NUM_REGIONS_STEP_GREAT_RUNE: Dict[int, str] = {
    3: "Godrick's Great Rune",          # Stormveil (Godrick)
    4: "Great Rune of the Unborn",      # Liurnia / Raya Lucaria (Rennala)
    5: "Radahn's Great Rune",           # Caelid (Radahn)
    7: "Rykard's Great Rune",           # Mt. Gelmir / Volcano Manor (Rykard)
}



# ===== Cave-bundle steps (chainable minor-dungeon clusters) ==============================
# When a cave bundle's extra_region_locks key is active under num_regions, the cluster SPLITS
# OUT of its parent overworld spine step into its own selectable + chainable step (synthetic
# 1-based indices past len(SPINE)=12; renumbered 13..16 by the 2026-07-02 spine surgery). It
# then COMPETES with the overworld majors for the num_regions slots and, with num_regions_chain,
# can be any link in the chain -- reached by warp (its torch lights the cluster's entrance
# graces; see grace_data.BUNDLE_LOCK_GRACES and the _BUNDLE_WARP block in __init__). parent =
# the SPINE index whose regions list holds these dungeons; INFORMATIONAL ONLY (no code reads
# it) -- the split-out governance in the compute functions is by region NAME, so
# mountaintops_caves (whose dungeons now span SPINE steps 10 Mountaintops + 11 Consecrated
# Snowfield) keeps parent=None and still splits correctly out of both.
CAVE_BUNDLE_STEPS: Dict[int, Dict] = {
    13: {
        "key": "limgrave_underground", "name": "Limgrave Underground",
        "lock": "Spelunker's Torch", "parent": 1,
        "regions": ["Fringefolk Hero's Grave", "Coastal Cave", "Church of Dragon Communion",
                    "Groveside Cave", "Stormfoot Catacombs", "Limgrave Tunnels", "Murkwater Cave",
                    "Murkwater Catacombs", "Highroad Cave", "Deathtouched Catacombs"],
    },
    14: {
        "key": "liurnia_caves", "name": "Liurnia Caves",
        "lock": "Spelunker's Ghostflame Torch", "parent": 4,
        "regions": ["Stillwater Cave", "Lakeside Crystal Cave", "Academy Crystal Cave",
                    "Road's End Catacombs", "Black Knife Catacombs", "Cliffbottom Catacombs",
                    "Raya Lucaria Crystal Tunnel", "Ruin-Strewn Precipice"],
    },
    15: {
        "key": "altus_caves", "name": "Altus Caves",
        "lock": "Spelunker's Steel-Wire Torch", "parent": 6,
        "regions": ["Sainted Hero's Grave", "Unsightly Catacombs", "Perfumer's Grotto",
                    "Sage's Cave", "Old Altus Tunnel", "Altus Tunnel"],
    },
    16: {
        "key": "mountaintops_caves", "name": "Mountaintops Caves",
        "lock": "Spelunker's Beast-Repellent Torch", "parent": None,
        "regions": ["Giant-Conquering Hero's Grave", "Giants' Mountaintop Catacombs",
                    "Spiritcaller Cave", "Consecrated Snowfield Catacombs", "Cave of the Forlorn",
                    "Yelough Anix Tunnel"],
    },
}


def active_cave_steps(extra_region_locks) -> Set[int]:
    """Map active extra_region_locks keys -> the cave-bundle step indices they enable.

    Accepts the option value (an iterable of key strings). `limgrave_caves` is honored as the
    documented synonym of `limgrave_underground` in case the alias normalization did not run.
    """
    keys = set(extra_region_locks)
    if "limgrave_caves" in keys:
        keys.add("limgrave_underground")
    return {idx for idx, d in CAVE_BUNDLE_STEPS.items() if d["key"] in keys}


# ===== BOSS_LOCKS_PATCH: per-boss sweep locks (SPEC-boss-locks.md, v0.1 sweep-gate model) =====
# v0.1 pivot (Alaric 2026-07-03): there is NO physical boss-arena enforcement yet -- nothing
# stops the player walking into the boss room. The boss lock instead gates the group's DUNGEON
# SWEEP (the client holds the sweep until the lock is in its received-items set, re-checked
# every flag-poll tick so a lock received AFTER the boss kill fires the sweep retroactively)
# plus the group's TRIGGER drop location in AP logic. Pre-boss checks stay on the region lock
# only -- the escape hatch is emergent from fill, exactly as the spec argues. No event flags
# are allocated: the 76971+ open-flag band is full and there is no fog wall to key off one.
ENABLE_BOSS_LOCKS = True  # internal kill-switch for debugging; NO player option (spec: always-on)

# The legacy dungeon-sweep region groups, hoisted VERBATIM out of
# EldenRingWorld._compute_dungeon_sweeps so BOSS_LOCKS keys off the same object and the two can
# never drift (the recording block in _compute_dungeon_sweeps raises on a group with no entry).
# group[0] doubles as the group key.
LEGACY_SWEEP_GROUPS: List[List[str]] = [
    ["Stormveil Start", "Stormveil Castle", "Stormveil Throne"],
    ["Raya Lucaria Academy", "Raya Lucaria Academy Main",
     "Raya Lucaria Academy Chest", "Raya Lucaria Academy Library"],
    ["Volcano Manor", "Volcano Manor Entrance", "Volcano Manor Upper",
     "Volcano Manor Dungeon", "Volcano Manor Drawing Room"],
    ["Leyndell, Royal Capital", "Leyndell, Royal Capital Unmissable",
     "Leyndell, Royal Capital Throne"],
    ["Leyndell, Ashen Capital", "Leyndell, Ashen Capital Throne"],
    ["Farum Azula", "Farum Azula Main"],
    ["Miquella's Haligtree", "Elphael, Brace of the Haligtree"],
    ["Mohgwyn Palace"],
    # DLC
    ["Belurat", "Belurat Swamp"],
    ["Castle Ensis"],
    ["Shadow Keep", "Shadow Keep Storehouse", "Shadow Keep Storehouse Back",
     "Shadow Keep, West Rampart", "Shadow Keep, Church District",
     "Shadow Keep, Church District Lower"],
    ["Midra's Manse"],
    ["Stone Coffin Fissure"],
    ["Enir Ilim"],
    # DLC ruins that ARE their own regions and whose deepest boss
    # drops a remembrance, so they qualify for the legacy rule as-is
    # (trigger = the remembrance). Finger Ruins -> Metyr, Mother of
    # Fingers; Rauh ruins -> Romina, Saint of the Bud. Overworld ruins
    # folded into a parent region (most of them) do NOT belong here --
    # see SPEC-ruins-sweep.md for the ruinsboss-tag route for those.
    ["Finger Ruins of Miyr", "Finger Ruins of Rhia", "Finger Ruins of Dheo"],
    ["Ancient Ruins of Rauh", "Rauh Ruins Limited"],
]

# The Shaded Castle shares the Altus Plateau AP region (its sweep is the NAME-based SCIG/SCR
# block in _compute_dungeon_sweeps), so it cannot appear in LEGACY_SWEEP_GROUPS; explicit key.
SHADED_CASTLE_GROUP_KEY = "The Shaded Castle"

# group key (group[0] / SHADED_CASTLE_GROUP_KEY) -> boss lock ITEM name. One lock per major
# sweep group. "Godrick Lock" is the pre-existing godrick-granularity item folded in rather
# than duplicated (the spec's precedent); every other value is a new items.py lock=True entry.
# Castle Morne is its own AP region, but Leonine Misbegotten drops a WEAPON (Grafted
# Blade Greatsword), NOT a remembrance, so it can't ride LEGACY_SWEEP_GROUPS (that path
# requires a remembrance trigger). Its sweep is the NAME-based CM area-code block in
# _compute_dungeon_sweeps (like the Shaded Castle), so it gets an explicit group key
# plus a base-game boss lock.
CASTLE_MORNE_GROUP_KEY = "Castle Morne"

# JAGGED_PEAK_GROUP_KEY (Bayle): drops "Heart of Bayle" (a Dragon Communion consumable), NOT a
# remembrance, so Jagged Peak can't ride LEGACY_SWEEP_GROUPS (needs a remembrance trigger). Its
# sweep is the NAME-based "JP" area-prefix block in _compute_dungeon_sweeps (like Castle Morne),
# so it gets an explicit group key + a DLC boss lock.
JAGGED_PEAK_GROUP_KEY = "Jagged Peak"
BOSS_LOCKS: Dict[str, str] = {
    "Stormveil Start": "Godrick Lock",
    "Raya Lucaria Academy": "Rennala Lock",
    "Volcano Manor": "Rykard Lock",
    "Leyndell, Royal Capital": "Morgott Lock",
    "Leyndell, Ashen Capital": "Hoarah Loux Lock",
    "Farum Azula": "Maliketh Lock",
    "Miquella's Haligtree": "Malenia Lock",
    "Mohgwyn Palace": "Mohg Lock",
    "Belurat": "Divine Beast Lock",
    "Castle Ensis": "Rellana Lock",
    "Shadow Keep": "Messmer Lock",
    "Midra's Manse": "Midra Lock",
    "Stone Coffin Fissure": "Putrescent Lock",
    "Enir Ilim": "Promised Consort Lock",
    "Finger Ruins of Miyr": "Metyr Lock",
    "Ancient Ruins of Rauh": "Romina Lock",
    SHADED_CASTLE_GROUP_KEY: "Elemer Lock",
    CASTLE_MORNE_GROUP_KEY: "Leonine Lock",
    JAGGED_PEAK_GROUP_KEY: "Bayle Lock",  # DLC: Bayle the Dread (optional superboss); name-based JP sweep
}

# Group keys whose regions only exist with the DLC enabled.
BOSS_LOCK_DLC_KEYS: Set[str] = {
    "Belurat", "Castle Ensis", "Shadow Keep", "Midra's Manse",
    "Stone Coffin Fissure", "Enir Ilim", "Finger Ruins of Miyr", "Ancient Ruins of Rauh",
    JAGGED_PEAK_GROUP_KEY,
}

# group key -> regions used by the generate_early presence prediction (inject the lock iff any
# group region is unsealed this seed). The Shaded Castle rides the shared Altus Plateau region.
BOSS_LOCK_GROUP_REGIONS: Dict[str, List[str]] = {g[0]: list(g) for g in LEGACY_SWEEP_GROUPS}
BOSS_LOCK_GROUP_REGIONS[SHADED_CASTLE_GROUP_KEY] = ["Altus Plateau"]
BOSS_LOCK_GROUP_REGIONS[CASTLE_MORNE_GROUP_KEY] = ["Castle Morne"]
BOSS_LOCK_GROUP_REGIONS[JAGGED_PEAK_GROUP_KEY] = ["Jagged Peak", "Jagged Peak Foot"]
# ===== end BOSS_LOCKS_PATCH ==================================================================
