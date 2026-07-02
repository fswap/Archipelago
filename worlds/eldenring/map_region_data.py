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
# confirmed valid, so 76971+ are the same allocated group). Up to ~27 distinct locks => 76971..76997. Special/NK/extra locks (Morne,
# Godrick, Mountaintops, Snowfield, Raya, Volcano, Haligtree) get hand-picked flags BELOW
# base (76961-76967) in __init__.py, DISJOINT from this computed band.
OPEN_FLAG_BASE = 76971

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
    "Dragonbarrow":         {"area_ids": [(64001, 64001)], "reveal_flags": [62041]},  # split from Caelid (own lock); play_region 64001
    "Mt. Gelmir":           {"area_ids": [(63001, 63001), (39200, 39200)], "reveal_flags": [62032]},                 # TBD area id (NOT 64xxx -- that's Caelid)

    # ---- base-game legacy dungeons: own area-id scheme (TBD empirical) ----
    "Stormveil Castle":         {"area_ids": [(10000, 10000)], "reveal_flags": []},   # area=10000 CONFIRMED in-game 2026-06-17 (godrick playtest); whole Stormveil map -> walls the Margit gatehouse too (region-lock: Stormveil Lock = key in; softlock-safe, lock is at Roundtable)
    "Farum Azula":              {"area_ids": [(13000, 13000)], "reveal_flags": []},   # m13 Crumbling Farum Azula; grace-warpable AP lock + random_start:any_major eligible
    "Sellia Crystal Tunnel":    {"area_ids": [], "reveal_flags": []},
    "Leyndell, Ashen Capital":  {"area_ids": [], "reveal_flags": [62031]},   # Leyndell/Capital map pillar

    # ---- base-game undergrounds (m12): area id = tile-based 12BB0 (m12_BB), confirmed Siofra 12070 ----
    "Ainsel River":              {"area_ids": [(12010, 12010), (12012, 12019), (12040, 12049)], "reveal_flags": [62060]},  # m12_01, m12_04
    "Lake of Rot":               {"area_ids": [(12011, 12011)], "reveal_flags": [62061]},  # VERIFY area id (sub of Ainsel m12? needs a data point)
    "Siofra River":              {"area_ids": [(12020, 12029), (12070, 12089)], "reveal_flags": [62063]},  # m12_02, m12_07(=12070 confirmed), m12_08
    "Nokron, Eternal City Start":{"area_ids": [], "reveal_flags": []},  # m12_09; no Nokron map pillar
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
    lock_open = {lk: OPEN_FLAG_BASE + i for i, lk in enumerate(locks)}
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
