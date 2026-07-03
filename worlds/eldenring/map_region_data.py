"""Region-lock region data: one dictionary + one function.

`REGIONS` is the single source of truth for the map-tracker + physical region-lock enforcement. One
entry per AP region (keys = grace_data.REGION_LOCK_ITEM keys), each with:
  - area_ids:     list of (lo, hi) inclusive ranges over the FieldArea area id (the value the client
                  reads @0xE4; e.g. 61002 = Weeping). The client is in region X when the current area
                  id (5-digit major, or a 7-digit sub-area normalized via //100) lands in a range.
  - reveal_flags: that region's world-map piece reveal flags (WorldMapPieceParam.openEventFlagId).
                  These are CONFIRMED-VALID event flags (unlike the dead 69M scheme); they double as
                  (a) the map-tracker reveal and (b) the enforcement OPEN-STATE: the client sets them
                  when the region's lock item is received, and treats reveal_flags[0] being OFF as
                  "locked" for the kick check.

`build_region_lock_slot_data(region_lock_item)` is the one function: it turns REGIONS into the two
slot_data tables the client consumes -- areaLockFlags (detection) and lockRevealFlags (open on receipt).

Filling status (see er-map-grant-region-tracker memory):
  - Overworld majors (Weeping/Liurnia/Caelid/Altus/Gelmir): area_ids HIGH-confidence by the mapNameId
    prefix grouping (61xxx Limgrave, 62xxx Liurnia, 63xxx Caelid, 64xxx Altus). Altus vs Mt. Gelmir
    split inside 64xxx is a best guess (VERIFY via the client area-log).
  - DLC (68xxx-69xxx), legacy dungeons (Stormveil ~10010, etc.) and undergrounds (m12) use other id
    schemes -> area_ids left [] and captured empirically (the client logs every area id on change).
  - reveal_flags: overworld HIGH; DLC/underground PROVISIONAL (VERIFY); legacy dungeons [] (no piece).
To add/refine a region: edit its one REGIONS entry. Nothing else changes.
"""

# World-map piece reveal flags (WorldMapPieceParam.openEventFlagId) -> human label, for reference.
WORLD_MAP_PIECE_FLAGS = {
    62010: "Limgrave, West", 62011: "Limgrave, East", 62012: "Weeping Peninsula",
    62020: "Liurnia, East", 62021: "Liurnia, North", 62022: "Liurnia, West",
    62030: "Caelid", 62031: "Dragonbarrow", 62032: "Caelid (SW)",
    62040: "Altus Plateau", 62041: "Mt. Gelmir",
    62050: "Mountaintops (W)", 62051: "Mountaintops of the Giants, W", 62052: "Mountaintops, E",
    62053: "Consecrated Snowfield",
    # base underground (WorldMapPieceParam pieces 100-105) -- NOT SotE. Earlier SotE labels here
    # were wrong (matches the client's grounded table); the real DLC pieces are 62080-84 below.
    62060: "Ainsel River", 62061: "Lake of Rot", 62062: "Mohgwyn Palace",
    62063: "Siofra River", 62064: "Deeproot Depths", 62065: "Underground (piece 105)",
    # DLC Land of Shadow map pieces (WorldMapPieceParam 1000-1004, openEventFlagId)
    62080: "SotE: Gravesite Plain", 62081: "SotE: Scadu Altus", 62082: "SotE: Cerulean/Southern Shore",
    62083: "SotE: Rauh", 62084: "SotE: Abyssal Woods",
    # subterranean quadrants
    62000: "Underground hub (S)", 62002: "Underground hub (C)", 62004: "Underground center",
    62005: "Underground SW", 62006: "Underground NW", 62007: "Underground SE", 62008: "Underground NE",
    62009: "Underground far N",
}

# Granted at spawn: Limgrave is the free sphere-1 hub.
START_REVEAL_FLAGS = [62010, 62011]

# Limgrave/Stormhill grace warp-unlock flags granted at game START (region_lock): the free starting
# region should be fully fast-travelable from the jump, no Torrent slog to re-find each grace. Derived
# offline from grace_flags.tsv x MapName.txt (tiles whose primary region is Limgrave/Stormhill); boss
# graces + the Caelid-border grace 73207 excluded so none warp you into a locked play-region.
LIMGRAVE_START_GRACES = [
    73100, 73201, 76100, 76101, 76102, 76103, 76104, 76105, 76106, 76108,
    76110, 76111, 76113, 76114, 76116, 76117, 76118, 76119, 76120,
]

# Base for the dedicated per-lock OPEN-STATE event flags. Kept SEPARATE from the 62xxx map-reveal flags
# so that revealing maps (reveal_all_maps grant, or the tracker) never flips a region open -> maps + lock
# are independent. Valid free flags in the grace-tail gap (grace max = 76960; 76970 = KICK flag, probe-
# confirmed valid, so 76971+ are the same allocated group).
#
# HAND_PICKED (SPEC-region-spine-surgery.md SS6): Mountaintops Lock / Snowfield Lock / Haligtree Lock
# get flags BELOW the computed band, consulted before the band walk runs. This reuses the already-
# minted natural-key apparatus (Mountaintops 76965, Snowfield 76961, Haligtree 76964), DISJOINT from
# the 76971+ computed band. Limgrave Lock takes an ordinary band flag (76962/76963 are TAKEN by the
# Raya Lucaria / Volcano NK2 apparatus in __init__.py -- no free hand-pick slot remains below band).
#
# RESERVED (never assigned by the band walk, and never collided with by HAND_PICKED): 76996 = the
# client's DEATHLINK_KILL_FLAG (er-open-flag-collision-bug); 76970 = KICK; 76968/76969 = random-start;
# 76967 = Godrick; 76966 = Morne; 76962 = Raya Lucaria NK2; 76963 = Volcano NK2; plus every
# HAND_PICKED value (76965 MT, 76961 SF, 76964 Haligtree). The band walk skips all of these and takes the next free value instead, so no
# lock open flag -- hand-picked or computed -- can ever collide with a reserved runtime flag. Every
# assigned flag is asserted <= 76997 (the probe-confirmed valid group ceiling).
OPEN_FLAG_BASE = 76971

# Hand-picked open-state flags for locks that reuse pre-existing natural-key apparatus, or that
# otherwise need a below-band flag. Consulted BEFORE the band walk in build_region_lock_slot_data.
HAND_PICKED = {
    "Mountaintops Lock": 76965,
    "Snowfield Lock": 76961,
    "Haligtree Lock": 76964,
}

# Runtime flags the band walk must never assign: 76996 = client DEATHLINK_KILL_FLAG,
# 76970 = KICK, 76968/76969 = random-start, 76966 = Morne, 76967 = Godrick, plus every
# HAND_PICKED value (so a computed-band lock can never collide with a hand-picked one).
RESERVED_OPEN_FLAGS = {76996, 76970, 76968, 76969, 76966, 76967, 76962, 76963} | set(HAND_PICKED.values())

# ---- THE dictionary: one entry per AP region ----
REGIONS = {
    # ---- overworld majors: area_ids HIGH confidence (prefix), reveal_flags HIGH ----
    # area_ids: CONFIRMED-ONLY now (the 61-65 prefix guess was WRONG -- 63xxx is Altus, not Caelid).
    # Confirmed in-game: 61002=Weeping, 62000-62999=Liurnia, 63000-63999=Altus. Unconfirmed regions get
    # [] (NOT enforced) until a real area= log id arrives -- under-enforce beats wrong-kicking unlocked
    # regions. Add a region's range only once its area= id is observed.
    # reveal_flags = the region's ACTUAL map-pillar flags (from the locations.py keys -- authoritative;
    # the old WorldMapPieceParam-derived values were systematically wrong). These drive map reveal on
    # unlock AND fire the reclaimed pillar checks. Open-state is separate (76971+), so this is reveal-only.
    # de-hub (Roundtable re-root): area=61000 CONFIRMED in-game (First Step); 61001 = Limgrave East
    # (VERIFY via area log); Weeping = 61002. ONLY enforced when region_lock_item maps Limgrave
    # (random-start hub_only) -> inert for normal seeds AND for to_limgrave.
    "Limgrave":             {"area_ids": [(61000, 61001)], "reveal_flags": [62010]},
    "Weeping Peninsula":    {"area_ids": [(61002, 61002)], "reveal_flags": [62011]},
    "Liurnia of The Lakes": {"area_ids": [(62000, 62999)], "reveal_flags": [62020, 62021, 62022]},
    "Altus Plateau":        {"area_ids": [(63000, 63000), (63002, 63003)], "reveal_flags": [62030]},   # CONFIRMED area=63000
    "Caelid":               {"area_ids": [(64000, 64000), (64002, 64002)], "reveal_flags": [62040]},  # CONFIRMED area=64000; Caelid + Dragonbarrow pillars
    "Dragonbarrow":         {"area_ids": [(64001, 64001)], "reveal_flags": [62041]},  # folded into Caelid Lock (SPEC-region-spine-surgery.md SS3.2); own map piece, shared open flag; play_region 64001
    "Mt. Gelmir":           {"area_ids": [(63001, 63001), (39200, 39200)], "reveal_flags": [62032]},                 # TBD area id (NOT 64xxx -- that's Caelid)

    # ---- SPEC-region-spine-surgery.md SS3.4/3.5/3.6: Mountaintops/Snowfield/Haligtree cluster ----
    # reveal_flags cross-checked against _NK_REVEAL in __init__.py (Mountaintops [62050,62051],
    # Snowfield [62052]). area_ids RESOLVED STATICALLY 2026-07-02 from
    # elden_ring_artifacts/REGION_ID_MAP.md (BonfireWarpParam.bonfireSubCategoryId == runtime
    # play_region_id, verified against every empirically-confirmed capture).
    "Mountaintops of the Giants": {"area_ids": [(65000, 65001)], "reveal_flags": [62050, 62051]},  # 65000 = MT West (Zamor/Castle Sol), 65001 = MT East (Fire Giant/Forge)
    "Flame Peak":                 {"area_ids": [], "reveal_flags": []},  # play_region 65001, already inside the MotG range above (same Mountaintops Lock) -- no own entry needed
    "Forbidden Lands":            {"area_ids": [], "reveal_flags": []},  # play_region 63003 is a SHARED bucket (E Altus / Divine Tower of East Altus / Rold corridor), keyed to Altus Lock via the Altus entry -- assigning it here would wrong-kick DToEA. Physical boundary is deliberately lenient; KICK begins at 65000/65002. Logic still gates the region on Mountaintops Lock.
    "Consecrated Snowfield":      {"area_ids": [(65002, 65002)], "reveal_flags": [62052]},  # 65002 = Snowfield (Ordina, Yelough Anix) -- REGION_ID_MAP.md
    "Hidden Path to the Haligtree": {"area_ids": [], "reveal_flags": []},  # graces bucket under shared 63003 (see Forbidden Lands note) -- lenient by design; rides Snowfield Lock in logic
    "Miquella's Haligtree":       {"area_ids": [], "reveal_flags": []},  # area lock (15000 Elphael + 15001 Haligtree) emitted by the __init__ Haligtree apparatus block -- kept [] HERE to avoid duplicate areaLockFlags rows

    # ---- base-game legacy dungeons: own area-id scheme (TBD empirical) ----
    "Stormveil Castle":         {"area_ids": [(10000, 10000)], "reveal_flags": []},   # area=10000 CONFIRMED in-game 2026-06-17 (godrick playtest); whole Stormveil map -> walls the Margit gatehouse too (region-lock: Stormveil Lock = key in; softlock-safe, lock is at Roundtable)
    "Farum Azula":              {"area_ids": [(13000, 13000)], "reveal_flags": []},   # m13 Crumbling Farum Azula; grace-warpable AP lock + random_start:any_major eligible
    "Sellia Crystal Tunnel":    {"area_ids": [], "reveal_flags": []},
    "Leyndell, Ashen Capital":  {"area_ids": [], "reveal_flags": [62031]},   # Leyndell/Capital map pillar

    # ---- base-game undergrounds (m12): area id = tile-based 12BB0 (m12_BB), confirmed Siofra 12070 ----
    "Ainsel River":              {"area_ids": [(12010, 12010), (12012, 12019), (12040, 12049)], "reveal_flags": [62060]},  # m12_01, m12_04
    "Lake of Rot":               {"area_ids": [(12011, 12011)], "reveal_flags": [62061]},  # 12011 CONFIRMED static (REGION_ID_MAP.md); 12012 Astel/Ainsel Depths sits in the Ainsel entry (same Nokstella Lock)
    "Siofra River":              {"area_ids": [(12020, 12029), (12070, 12089)], "reveal_flags": [62063]},  # m12_02, m12_07(=12070 confirmed), m12_08
    "Nokron, Eternal City Start":{"area_ids": [], "reveal_flags": []},  # Nokron graces bucket = 12020 (Ancestral Woods / Night's Sacred Ground -- REGION_ID_MAP.md), already inside the Siofra River ranges above; same Nokron Lock, so no own entry needed
    "Deeproot Depths":           {"area_ids": [(12030, 12039)], "reveal_flags": [62064]},  # m12_03
    "Mohgwyn Palace":            {"area_ids": [(12050, 12059)], "reveal_flags": [62062]},  # m12_05

    # ---- DLC (SotE): area ids 68xxx-69xxx (TBD empirical); reveal_flags = actual DLC map-pillar flags ----
    "Gravesite Plain":      {"area_ids": [(6800, 6800)], "reveal_flags": [62080]},
    "Belurat":              {"area_ids": [(20000, 20009)], "reveal_flags": []},                 # INFERRED m20_00 Belurat Tower Settlement (+swamp)
    "Castle Ensis":         {"area_ids": [(6820, 6820)], "reveal_flags": []},
    "Fog Rift Fort":        {"area_ids": [], "reveal_flags": []},
    "Scadu Altus":          {"area_ids": [(6900, 6900), (6920, 6920)], "reveal_flags": [62081]},
    "Shadow Keep":          {"area_ids": [(21000, 21029)], "reveal_flags": []},                 # INFERRED m21_00/01/02 Keep+Storehouse+W.Rampart
    "Recluses' River":      {"area_ids": [], "reveal_flags": []},
    "Enir Ilim":            {"area_ids": [(20010, 20019)], "reveal_flags": []},                 # INFERRED m20_01 Enir-Ilim (goal region)
    "Cerulean Coast":       {"area_ids": [(6830, 6830)], "reveal_flags": [62082]},
    "Charo's Hidden Grave": {"area_ids": [(6840, 6840)], "reveal_flags": []},
    "Stone Coffin Fissure": {"area_ids": [(22000, 22009)], "reveal_flags": []},                 # INFERRED m22_00 Stone Coffin Fissure
    "Jagged Peak Foot":     {"area_ids": [(6850, 6851)], "reveal_flags": []},
    "Abyssal Woods":        {"area_ids": [(6860, 6860), (28000, 28000)], "reveal_flags": [62084]},
    "Rauh Base":            {"area_ids": [(6950, 6950)], "reveal_flags": [62083]},
    "Ancient Ruins of Rauh":{"area_ids": [(6940, 6940)], "reveal_flags": []},
}


# Region -> a representative Map fragment item er_code (GOODS) for the unlock NOTIFICATION: on lock
# receipt the client grants this, so the game's native item ticker fires and NAMES the region (e.g.
# "Map: Liurnia, East"). None = no overworld map fragment; that lock falls back to a generic token,
# OR is already covered because it shares a lock with a mapped region (e.g. Sellia shares Caelid Lock).
# DLC region maps (2008600+) omitted here (added when DLC support lands; off in current seeds).
REGION_MAP_ITEM = {
    "Limgrave": 8600,                    # Map: Limgrave, West -- de-hub unlock notification
    "Weeping Peninsula": 8601,
    "Liurnia of The Lakes": 8603,
    "Caelid": 8609,
    "Altus Plateau": 8606,
    "Mt. Gelmir": 8608,
    "Leyndell, Ashen Capital": 8607,
    "Ainsel River": 8613,
    "Lake of Rot": 8614,
    "Siofra River": 8615,
    "Deeproot Depths": 8617,
    "Mohgwyn Palace": 8616,
    "Stormveil Castle": None,            # no overworld map -> token
    "Sellia Crystal Tunnel": None,       # shares Caelid Lock -> Caelid map
    "Nokron, Eternal City Start": None,  # shares SE Underground Lock -> Siofra map
}


def build_region_lock_slot_data(region_lock_item):
    """The one function. Turns REGIONS into the two slot_data tables the client consumes.

    region_lock_item: grace_data.REGION_LOCK_ITEM ({region_name: lock_item_name}).
    Returns {
        "areaLockFlags":   [[lo, hi, open_flag], ...]   # detection: in [lo,hi] & open_flag OFF => kick
        "lockRevealFlags": {lock_item_name: [flag,...]} # client sets these when the lock is received
                                                        # (region opens + map reveals). Shared locks union.
    }
    Also returns "lockOpenFlags" {lock_item_name: open_flag} -- one DEDICATED open-state flag per lock
    (OPEN_FLAG_BASE+), set on receipt; areaLockFlags uses these (NOT the 62xxx map flags) so revealing
    maps never unlocks a region. Regions with area_ids contribute to areaLockFlags; regions with reveal
    flags contribute to lockRevealFlags (map reveal). Shared locks share one open flag and union reveals.
    """
    # Dedicated per-lock OPEN-STATE flags (independent of the 62xxx map flags). Shared locks share one.
    locks = sorted({region_lock_item[r] for r in REGIONS if region_lock_item.get(r)})
    # HAND_PICKED locks take their reserved below-band flag; everything else walks the
    # computed band starting at OPEN_FLAG_BASE, skipping RESERVED_OPEN_FLAGS so a computed
    # assignment can never collide with a hand-picked one or a runtime-reserved flag
    # (SPEC-region-spine-surgery.md SS6; closes the 76996 deathlink-kill collision for real).
    lock_open = {}
    _next = OPEN_FLAG_BASE
    for lk in locks:
        if lk in HAND_PICKED:
            lock_open[lk] = HAND_PICKED[lk]
            continue
        while _next in RESERVED_OPEN_FLAGS or _next in lock_open.values():
            _next += 1
        lock_open[lk] = _next
        _next += 1
    for _lk, _flag in lock_open.items():
        assert _flag <= 76997, "lock open flag out of the probe-confirmed valid group: %s=%s" % (_lk, _flag)
    area_lock = []
    lock_reveal = {}
    for region, info in REGIONS.items():
        lock = region_lock_item.get(region)
        open_flag = lock_open.get(lock)
        if open_flag is not None:
            for (lo, hi) in info.get("area_ids", []):
                area_lock.append([lo, hi, open_flag])      # detection checks the OPEN-STATE flag
        flags = info.get("reveal_flags", [])
        if lock and flags:
            lock_reveal.setdefault(lock, set()).update(flags)
    return {
        "areaLockFlags": area_lock,                        # [lo,hi,open_flag] -> detection
        "lockOpenFlags": lock_open,                        # {lock: open_flag} -> set on receipt (enforcement)
        "lockRevealFlags": {lk: sorted(fs) for lk, fs in lock_reveal.items()},  # {lock: 62xxx} -> map reveal only
    }
