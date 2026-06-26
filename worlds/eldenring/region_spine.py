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
"""

from typing import Dict, List, Optional, Set, Tuple


# ---- The ordered spine. step (1-based) -> (label, locks owned, AP regions whose checks belong) ----
# Step 1 (Limgrave) owns no lock: it is the free starting region. Every other step owns the lock(s)
# that gate its regions; keeping the step keeps those locks injectable, sealing it removes them.
SPINE: List[Dict] = [
    {
        "name": "Limgrave",
        "locks": set(),
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
        "name": "Caelid",                     # Radahn -> great rune (+ Redmane folded in)
        "locks": {"Caelid Lock", "Redmane Lock"},
        "regions": [
            "Caelid", "Caelid Catacombs", "Gaol Cave", "Sellia Crystal Tunnel",
            "Abandoned Cave", "Minor Erdtree Catacombs", "Great-Jar", "Gale Tunnel",
            "Redmane Castle Post Radahn", "Wailing Dunes", "War-Dead Catacombs",
        ],
    },
    {
        "name": "Dragonbarrow",               # new lock (was Caelid-shared / bell-gated)
        "locks": {"Dragonbarrow Lock"},
        "regions": [
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
]

# 1-based spine indices whose region holds a great-rune mainboss. Used for the floor calc.
RUNE_STEPS = {3, 4, 5, 8}        # Godrick, Rennala, Radahn, Rykard
ALTUS_STEP = 7                   # the lowest count that physically reaches Leyndell
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

    Need Altus (step 7) physically, AND great_runes_required rune-bosses in scope. Steps 1..7 cover
    runes {Godrick, Rennala, Radahn} = 3; step 8 (Rykard) adds the 4th. More than 4 is impossible
    because only 4 great-rune bosses exist before Leyndell.
    """
    if great_runes_required > MAX_PRE_LEYNDELL_RUNES:
        raise ValueError(
            f"Capital/Morgott goal needs great_runes_required <= {MAX_PRE_LEYNDELL_RUNES} "
            f"(only that many great-rune bosses exist before Leyndell); got {great_runes_required}."
        )
    floor = ALTUS_STEP
    if great_runes_required > len({s for s in RUNE_STEPS if s <= ALTUS_STEP}):
        floor = max(floor, 8)     # need Rykard too
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
# fill spheres become 1..N. Limgrave is the free sphere-1 hub (link 0). The rolled middle
# majors are shuffled by the world rng, with Altus PINNED LAST among the middles (capstone
# tail: Altus -> Capital Outskirts -> Leyndell; Leyndell is great-rune gated, has no lock and
# is the terminus). __init__.py consumes this order: it precollects the first middle's lock and
# breadcrumbs every later middle's lock onto the PRIOR middle's prominent boss drop.

# Per (1-based) middle SPINE step: the region whose boss hosts the NEXT link's lock, and the
# lock item this step contributes to the chain (the one gating its overworld region under
# region_lock / REGION_LOCK_ITEM). The host REGION is resolved dynamically in __init__.py from
# this region's actual locations (prefer a remembrance/prominent boss drop, then any
# non-missable boss drop, then any non-missable check), so a region without a great-rune
# remembrance (Weeping / Dragonbarrow / Altus) still gets a stable host. Only the LOCK NAME and
# the candidate host-region NAMES are fixed here.
NUM_REGIONS_CHAIN_STEP_LOCK: Dict[int, str] = {
    2: "Weeping Lock",
    3: "Stormveil Lock",
    4: "Liurnia Lock",
    5: "Caelid Lock",
    6: "Dragonbarrow Lock",
    7: "Altus Lock",
    8: "Mt. Gelmir Lock",
    9: "Spelunker's Torch",                   # Limgrave Underground (limgrave_underground)
    10: "Spelunker's Ghostflame Torch",       # Liurnia Caves (liurnia_caves)
    11: "Spelunker's Steel-Wire Torch",       # Altus Caves (altus_caves)
    12: "Spelunker's Beast-Repellent Torch",  # Mountaintops Caves (mountaintops_caves)
}

# The overworld AP region(s) whose checks/bosses belong to each middle step, used by __init__.py
# to find a breadcrumb HOST location. First name is the primary (where the prominent boss lives);
# the rest are fallbacks searched in order if the primary has no usable host.
NUM_REGIONS_CHAIN_STEP_HOST_REGIONS: Dict[int, List[str]] = {
    2: ["Weeping Peninsula"],
    3: ["Stormveil Throne", "Stormveil Castle", "Stormveil Start"],
    4: ["Raya Lucaria Academy Library", "Raya Lucaria Academy", "Liurnia of The Lakes"],
    5: ["Caelid"],  # no-wailing-dunes-host: NOT Wailing Dunes -- Radahn's drop is Altus-gated, a breadcrumb lock there deadlocks (Altus Lock <-> Wailing Dunes).
    6: ["Dragonbarrow"],
    7: ["Altus Plateau"],
    8: ["Volcano Manor", "Mt. Gelmir"],
    9: ["Stormfoot Catacombs", "Limgrave Tunnels", "Murkwater Catacombs", "Deathtouched Catacombs",
        "Fringefolk Hero's Grave", "Coastal Cave", "Groveside Cave", "Murkwater Cave",
        "Highroad Cave", "Church of Dragon Communion"],
    10: ["Black Knife Catacombs", "Road's End Catacombs", "Cliffbottom Catacombs", "Stillwater Cave",
         "Lakeside Crystal Cave", "Academy Crystal Cave", "Raya Lucaria Crystal Tunnel",
         "Ruin-Strewn Precipice"],
    11: ["Sainted Hero's Grave", "Unsightly Catacombs", "Perfumer's Grotto", "Sage's Cave",
         "Old Altus Tunnel", "Altus Tunnel"],
    12: ["Giants' Mountaintop Catacombs", "Giant-Conquering Hero's Grave", "Spiritcaller Cave",
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

    Returns [m_1, m_2, ..., m_k] where the regions open in that order off the Limgrave hub:
    m_1's lock is free (precollected), m_{i+1}'s lock is breadcrumbed onto m_i's boss. Altus
    (step 7) is forced to the END (capstone tail). Dragonbarrow (step 6) is kept ADJACENT to and
    IMMEDIATELY AFTER Caelid (step 5) when both are kept -- Dragonbarrow has no own hub warp
    (absent from REGION_LOCK_ITEM); it is reached by warping to Caelid then walking in with the
    Dragonbarrow Lock, so it must sit right behind Caelid in the chain to stay reachable. The
    remaining middles are shuffled. (If Dragonbarrow is kept WITHOUT Caelid -- possible because
    compute_num_regions_scope does not couple them -- it is ordered normally and flagged by the
    caller; that combo needs a gen-test, see SPEC  9.)
    """
    middles = _kept_middle_steps(kept_locks)
    altus = ALTUS_STEP if ALTUS_STEP in middles else None
    rest = [s for s in middles if s != altus]
    rng.shuffle(rest)
    # Keep Dragonbarrow (6) directly after Caelid (5) when both present.
    if 6 in rest and 5 in rest:
        rest = [s for s in rest if s != 6]
        ci = rest.index(5)
        rest.insert(ci + 1, 6)
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
# majors (Weeping .. Mt. Gelmir) are rolled. A great-rune floor keeps enough great-rune bosses in
# scope to open Leyndell. Reachability is by WARP (the caller forces region_access=warp), so a
# non-contiguous random subset is still reachable from the Limgrave hub via each region's own lock.
# Everything not kept is sealed exactly like a region_count seal (lock pulled, checks -> events).
# See SPEC-num-regions.md.

# 1-based SPINE indices that are "middle" overworld majors eligible for the random roll
# (step 1 Limgrave is the always-kept free hub; the Leyndell capstone is the always-kept goal).
NUM_REGIONS_MIDDLE_STEPS: List[int] = [2, 3, 4, 5, 6, 7, 8]   # Weeping, Stormveil, Liurnia, Caelid, Dragonbarrow, Altus, Mt. Gelmir


def num_regions_floor(great_runes_required: int) -> int:
    """Lowest num_regions that keeps the capital reachable under WARP access.

    Limgrave + Leyndell (= 2) plus great_runes_required rune-boss majors. Unlike the geographic
    region_count floor there is NO Altus-route requirement (warp travel ignores adjacency).
    """
    if great_runes_required > MAX_PRE_LEYNDELL_RUNES:
        raise ValueError(
            f"num_regions capital goal needs great_runes_required <= {MAX_PRE_LEYNDELL_RUNES} "
            f"(only that many great-rune bosses exist before Leyndell); got {great_runes_required}."
        )
    return 2 + max(0, int(great_runes_required)) + (1 if ALTUS_STEP not in RUNE_STEPS else 0)  # +1: Altus is the only route to Leyndell


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
    # 1) guarantee the great-rune floor: pick great_runes_required rune-boss steps at random.
    _rs = [s for s in rune_steps if s not in picked]
    n_rune = min(int(great_runes_required), len(_rs), max(0, need_random - len(picked)))
    picked += list(rng.sample(_rs, n_rune)) if n_rune > 0 else []
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
# and Limgrave is NOT force-kept -- ALL eight overworld majors (Limgrave + the seven middles) are a
# single rollable/sealable pool. The only always-kept content is the Roundtable hub + the Leyndell
# capstone, so the content floor is 1 middle region. Reachability is by WARP from the Roundtable hub
# (the caller forces region_access=warp and sets the Roundtable-hub re-root), so a non-contiguous
# random subset -- including a sealed Limgrave / Altus -- is still reachable via each region's lock.

# Every overworld major step (1-based SPINE index) is rollable in pool mode -- including Limgrave (1).
NUM_REGIONS_POOL_STEPS: List[int] = [1] + list(NUM_REGIONS_MIDDLE_STEPS)   # Limgrave + the seven middles


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
    # chain mode: Limgrave (step 1) has no chain lock (NUM_REGIONS_CHAIN_STEP_LOCK starts at 2), so a
    # rolled Limgrave cannot join the breadcrumb chain -- it leaks a loose off-chain start lock.
    # Exclude it from the roll when chaining (Limgrave then seals; never a 2nd start lock).
    _pool_steps = NUM_REGIONS_MIDDLE_STEPS if chain_excludes_limgrave else NUM_REGIONS_POOL_STEPS
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
    8: "Rykard's Great Rune",           # Mt. Gelmir / Volcano Manor (Rykard)
}



# ===== Cave-bundle steps (chainable minor-dungeon clusters) ==============================
# When a cave bundle's extra_region_locks key is active under num_regions, the cluster SPLITS
# OUT of its parent overworld spine step into its own selectable + chainable step (synthetic
# 1-based indices past len(SPINE)=8). It then COMPETES with the overworld majors for the
# num_regions slots and, with num_regions_chain, can be any link in the chain -- reached by warp
# (its torch lights the cluster's entrance graces; see grace_data.BUNDLE_LOCK_GRACES and the
# _BUNDLE_WARP block in __init__). parent = the SPINE index whose regions list holds these
# dungeons (None = not in SPINE, e.g. Mountaintops/Snowfield, so nothing to split out).
CAVE_BUNDLE_STEPS: Dict[int, Dict] = {
    9: {
        "key": "limgrave_underground", "name": "Limgrave Underground",
        "lock": "Spelunker's Torch", "parent": 1,
        "regions": ["Fringefolk Hero's Grave", "Coastal Cave", "Church of Dragon Communion",
                    "Groveside Cave", "Stormfoot Catacombs", "Limgrave Tunnels", "Murkwater Cave",
                    "Murkwater Catacombs", "Highroad Cave", "Deathtouched Catacombs"],
    },
    10: {
        "key": "liurnia_caves", "name": "Liurnia Caves",
        "lock": "Spelunker's Ghostflame Torch", "parent": 4,
        "regions": ["Stillwater Cave", "Lakeside Crystal Cave", "Academy Crystal Cave",
                    "Road's End Catacombs", "Black Knife Catacombs", "Cliffbottom Catacombs",
                    "Raya Lucaria Crystal Tunnel", "Ruin-Strewn Precipice"],
    },
    11: {
        "key": "altus_caves", "name": "Altus Caves",
        "lock": "Spelunker's Steel-Wire Torch", "parent": 7,
        "regions": ["Sainted Hero's Grave", "Unsightly Catacombs", "Perfumer's Grotto",
                    "Sage's Cave", "Old Altus Tunnel", "Altus Tunnel"],
    },
    12: {
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
