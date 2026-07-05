"""Slot data construction for the Elden Ring apworld.

fill_slot_data was moved here VERBATIM from __init__.py by
patch_extract_slot_data.py (pure mechanical relocation, zero behavior
change). EldenRing mixes SlotDataMixin in as its first base. This module
is the client contract: everything the runtime client reads lives here.
"""

from typing import cast, Any, Callable, Dict, Set, List, Optional, TextIO, Union
from .items import ERItem, ERItemData, ERItemCategory, filler_item_names, filler_item_names_vanilla, item_descriptions, item_table, item_table_vanilla, item_name_groups, GRACE_FLAG_TO_ITEM
from .locations import ERLocation, ERLocationData, location_tables, location_descriptions, location_dictionary, location_name_groups, region_order, region_order_dlc
from .grace_data import REGION_LOCK_ITEM, REGION_GRACE_POINTS, BUNDLE_LOCK_GRACES
from .map_region_data import build_region_lock_slot_data, REGION_MAP_ITEM, LIMGRAVE_START_GRACES
from .stone_bells import STONE_BELL_GRANTS, PROGRESSIVE_SMITHING_BELL, PROGRESSIVE_SOMBER_BELL, PROGRESSIVE_BELL_COUNTS, PROGRESSIVE_BELL_POOL_COUNT, PROGRESSIVE_BELL_EARLY_COUNT
from .physick_tears import PROG_PHYSICK, PHYSICK_DROP_NAMES, HIGH_TIER_TEARS, physick_ladder
from .consumable_grants import (FLASK_DISCRETE_TO_PROGRESSIVE, GLOVEWORT_DISCRETE_TO_PROGRESSIVE,
                                CONSUMABLE_GOODS_LADDERS, FLASK_PROGRESSIVE_NAMES, GLOVEWORT_PROGRESSIVE_NAMES)
from . import region_spine


class SlotDataMixin:
    """fill_slot_data for EldenRing, moved verbatim from __init__.py."""
    def fill_slot_data(self) -> Dict[str, object]:
        item_table = self.item_table  # per-world overlay (patch_per_world_item_table)
        slot_data: Dict[str, object] = {}
        # Generate-output counts summary (surfaced by build.ps1; "The Shattering").
        # Post-fill: progression = real checks holding an advancement item; pool_builder
        # local-kept = juice pool_builder swapped in and forced local (create_items swap).
        _cnt_locs = [loc for loc in self.multiworld.get_locations(self.player)
                     if loc.address is not None]
        _cnt_prog = sum(1 for loc in _cnt_locs
                        if loc.item is not None and loc.item.advancement)
        _cnt_pbl = getattr(self, "_pool_builder_local_count", 0)
        print("ER_COUNTS player=%d seed=%s checks=%d progression=%d pool_builder_local=%d"
              % (self.player, self.multiworld.seed_name, len(_cnt_locs), _cnt_prog, _cnt_pbl))
        # Once all clients support overlapping item IDs, adjust the ER AP item IDs to encode the
        # in-game ID as well as the count so that we don't need to send this information at all.
        #
        # We include all the items the game knows about so that users can manually request items
        # that aren't randomized, and then we _also_ include all the items that are placed in
        # practice.
        items_by_name = {
            location.item.name: cast(ERItem, location.item).data
            for location in self.multiworld.get_filled_locations()
            # item.code None is used for events, which we want to skip
            if location.item.code is not None and location.item.player == self.player
        }
        for item in item_table.values():
            if item.name not in items_by_name:
                items_by_name[item.name] = item

        # Pack the item category into the top nibble of the game id, matching BOTH the game's own
        # "gib" encoding and the static randomizer's ItemKey.FullID (weapon=0, armor=1<<28,
        # accessory/talisman=2<<28, goods=4<<28, ash of war/gem=8<<28). The raw er_code alone is
        # ambiguous (armor 2901 vs goods 2901): shipping it unpacked made the randomizer decode
        # every non-weapon id as WEAPON and the client grant armor as goods.
        # Contract change: slot_data "versions" bumped to beta.2 (lockstep with randomizer+client).
        category_nibbles = {
            ERItemCategory.GOODS: 0x40000000,
            ERItemCategory.WEAPON: 0x00000000,
            ERItemCategory.ARMOR: 0x10000000,
            ERItemCategory.ACCESSORY: 0x20000000,
            ERItemCategory.ASHOFWAR: 0x80000000,
        }
        # Progressive stone bells (SPEC-progressive-stone-bells.md): per-tier {goods,flags}.
        # goods GOODS-packed (|0x40000000) so the client grants the cosmetic bell directly;
        # flags = Twin Maiden eventFlag_forStock to set (the real shop unlock). Empty unless active.
        progressive_grants = {}
        if self._progressive_bells_active():
            progressive_grants = {
                _name: [{"goods": _t["goods"] | 0x40000000, "flags": _t["flags"]} for _t in _tiers]
                for _name, _tiers in STONE_BELL_GRANTS.items()
            }
        # Progressive consumables (flasks / glovewort bells, SPEC-progressive-consumables.md):
        # ride the SAME progressiveGrants pipeline with empty flag lists + a goods ladder, so
        # the client grants goods[k] on the Kth copy and a Lord's Rune past the ladder length.
        _consumable_names = []
        if self._progressive_flasks_active():
            _consumable_names += list(FLASK_PROGRESSIVE_NAMES)
        if self._progressive_glovewort_active():
            _consumable_names += list(GLOVEWORT_PROGRESSIVE_NAMES)
        for _cn in _consumable_names:
            progressive_grants[_cn] = [{"goods": _g | 0x40000000, "flags": []}
                                       for _g in CONSUMABLE_GOODS_LADDERS[_cn]]
        # Progressive physick: one ladder whose steps each grant a LIST of goods (a whole tear
        # family), unlike the single-goods bell/consumable steps. Emitted with a "goodsList" key
        # (packed FullIDs) + empty flags; the client grants every id in the step list, and a
        # Lord's Rune for copies past the ladder. Step 1 = the flask itself. REQUIRES the client
        # to honour "goodsList" (see SPEC-progressive-physick.md).
        if self._progressive_physick_active():
            progressive_grants[PROG_PHYSICK] = [
                {"goodsList": [(_g | 0x40000000) for _g in _step], "flags": []}
                for _step in physick_ladder(bool(self.options.enable_dlc.value))
            ]
        ap_ids_to_er_ids: Dict[str, int] = {}
        item_counts: Dict[str, int] = {}
        for item in items_by_name.values():
            if item.ap_code is None: continue
            if item.er_code:
                ap_ids_to_er_ids[str(item.ap_code)] = item.er_code | category_nibbles[item.category]
            if item.count != 1: item_counts[str(item.ap_code)] = item.count

        # A map from Archipelago's location IDs to the keys the static randomizer uses to identify
        # locations.
        location_ids_to_keys: Dict[int, str] = {}
        for location in cast(List[ERLocation], self.multiworld.get_filled_locations(self.player)):
            # Skip events and only look at this world's locations
            if (location.address is not None and location.item.code is not None
                    and location.data.key):
                location_ids_to_keys[location.address] = location.data.key

        # Goal locations for ending_condition 2/3 (all remembrances / all bosses): the client
        # can't detect these via a single event flag, so ship the exact location set that the
        # Victory rule uses; the client sends CLIENT_GOAL once all of them are checked.
        goal_locations: List[int] = []
        if self.options.ending_condition >= 2:
            if self.options.ending_condition == 4:
                # Capital goal: a single location -- beating Morgott. The client fires CLIENT_GOAL
                # when this one check lands (same generic mechanism as the all-bosses set).
                goal_names = {region_spine.MORGOTT_GOAL_LOCATION}
            elif self.options.ending_condition == 5:
                # DLC mini-campaign (Messmer): single goal location, same client mechanism as Capital.
                goal_names = {region_spine.MESSMER_GOAL_LOCATION}
            elif self.options.ending_condition == 6:
                # Godrick mini-campaign: single goal location, same client mechanism as Capital.
                goal_names = {region_spine.GODRICK_GOAL_LOCATION}
            elif self.options.ending_condition == 2:
                goal_names = set(self.location_name_groups["Remembrance"])
                if self.options.enable_dlc:
                    goal_names |= set(self.location_name_groups["Remembrance DLC"])
            else:
                goal_names = set(self.location_name_groups["Boss Reward"])
                if self.options.enable_dlc:
                    goal_names |= set(self.location_name_groups["Boss Reward DLC"])
            for location in self._get_our_locations():
                if location.address is not None and location.name in goal_names:
                    goal_locations.append(location.address)

        # Dungeon sweep (SPEC-dungeon-sweep.md): map of trigger location -> all location ids
        # in that dungeon. The client watches the trigger's guarding event flag (already in
        # apconfig's location_flags, since triggers are boss-drop lots) and sends every member
        # check when it fires. Logic deliberately does NOT model this (early arrivals are safe).
        dungeon_sweeps, _ = self._compute_dungeon_sweeps()

        # BOSS_LOCKS_PATCH (SPEC-boss-locks.md v0.1): {trigger apLocId(str): boss lock item
        # name}. The client HOLDS a gated group's sweep until the named lock is in its
        # received-items set -- evaluated every flag-poll tick, so a lock received after the
        # boss kill fires the sweep retroactively. Only locks actually in this seed's pool are
        # emitted; everything else (minidungeon + chokepoint-carve sweeps) stays ungated.
        sweep_lock_gates: Dict[str, str] = {}
        if (getattr(region_spine, "ENABLE_BOSS_LOCKS", False)
                and (self.options.world_logic == "region_lock"
                     or self.options.world_logic == "region_lock_bosses")
                and self.options.dungeon_sweep >= 2):
            for _sg_name, (_sg_addr, _sg_lock) in getattr(self, "_sweep_lock_gates_by_trigger", {}).items():
                _sg_data = item_table.get(_sg_lock)
                if _sg_addr is None or _sg_data is None or not getattr(_sg_data, "inject", False):
                    continue
                sweep_lock_gates[str(_sg_addr)] = _sg_lock

        # Chokepoint boss attribution (extra_region_locks: chokepoint_locks): in bosses mode the
        # static randomizer's geometric sweep lumps a whole legacy dungeon onto its single
        # lowest-id boss (all Farum Azula -> Maliketh, all Haligtree -> Malenia), which would let
        # the END boss sweep the BEFORE-half the chokepoint hands to the mid-boss. Ship the
        # before-half check ids keyed by the choke boss DefeatFlag so the baker re-homes them onto
        # the choke boss (Godskin Duo 13000850 / Loretta 15000850). Empty unless chokepoint_locks
        # AND a sweep are on; the baker only consumes it in bosses mode. Static randomizer only.
        chokepoint_sweeps: Dict[str, List[int]] = {}
        if ("chokepoint_locks" in self.options.extra_region_locks.value
                and self.options.dungeon_sweep != 0):
            _cp_r2l: Dict[str, List[ERLocation]] = {}
            for _cpl in self._get_our_locations():
                if _cpl.address is None:
                    continue
                _cp_r2l.setdefault(_cpl.parent_region.name, []).append(_cpl)
            for _cp_after, (_cp_bef, _cp_trig) in region_spine.CHOKEPOINTS.items():
                _cp_flag = region_spine.CHOKEPOINT_BOSS_FLAGS.get(_cp_after)
                # only when the dungeon is actually split this seed (after-region present)
                if not _cp_flag or _cp_after not in _cp_r2l:
                    continue
                _cp_ids = sorted({l.address for r in _cp_bef
                                  for l in _cp_r2l.get(r, []) if l.address is not None})
                if len(_cp_ids) > 1:
                    chokepoint_sweeps[str(_cp_flag)] = _cp_ids

        # Region-fusion grace bundle (TODO #13): when region gating is active, ship
        # {lock_item_name: [grace warp-unlock flags]} so the runtime client can enable a
        # region's Sites of Grace (fast travel) when its lock item is received. graces_per_region
        # controls how many per region (0 = all); picks are spatially SPREAD (central hub first,
        # then farthest-point for coverage) from grace_data.py. Inert until the client consumes
        # it; only emitted for region-gating world_logic (< open_world).
        # A SEALED Limgrave (pool+chain rolls it out of the kept set) must be DARK + LOCKED like any
        # other sealed region -- NOT lit by the to_limgrave freebie or left physically open. Gate every
        # Limgrave start-hub special-case below on this. (er-numregions-pool-chain-limgrave)
        _limgrave_sealed = "Limgrave" in getattr(self, "_spine_sealed_regions", set())
        region_graces: Dict[str, list] = {}
        if self.options.world_logic < 3:
            _n = self.options.graces_per_region.value
            def _spread(points, k):
                # points: [[flag, x, z], ...]; return up to k flags maximizing spatial spread
                if k <= 0 or k >= len(points):
                    return [p[0] for p in points]
                cx = sum(p[1] for p in points) / len(points)
                cz = sum(p[2] for p in points) / len(points)
                chosen = [min(points, key=lambda p: (p[1]-cx)**2 + (p[2]-cz)**2)]
                while len(chosen) < k:
                    far = max(points, key=lambda p: min((p[1]-c[1])**2 + (p[2]-c[2])**2 for c in chosen))
                    if far in chosen:
                        break
                    chosen.append(far)
                return [p[0] for p in chosen]
            # Graces we must NOT bundle: (a) BOSS-arena graces -- warping in drops you behind the fog
            # so the boss never aggros (skip/soft-lock); (b) BORDER graces -- their map tile spans two
            # regions (e.g. Grand Lift of Dectus = Liurnia+Altus), so the grace sits in a NEIGHBOURING
            # locked region and warping there kicks you out. Both derived offline from grace_flags.tsv
            # x MapName.txt (boss/arena tiles; cross-region tiles). 71240=Astel, 76422 Radahn, etc.
            _BOSS_GRACE_FLAGS = frozenset({71240, 71401, 76415, 76422, 76508, 76509, 76852, 76853, 76930, 76931})  # 76415=Nox Duo arena (Sellia, Town of Sorcery; 'chair crypt'); 71401=Debate Parlor (Red Wolf of Radagon arena)
            _BORDER_GRACE_FLAGS = frozenset({73204, 73207, 76209, 76229, 76301, 76350, 76351, 76356})
            _SKIP_GRACE_FLAGS = _BOSS_GRACE_FLAGS | _BORDER_GRACE_FLAGS
            for _region, _points in REGION_GRACE_POINTS.items():
                _lock = REGION_LOCK_ITEM.get(_region)
                # Mt. Gelmir REBUCKET: all its grace tiles are m60_3x_5x -> they report the Altus
                # play-region (63xxx) and Mt. Gelmir has no enforced area_ids, so they must ride the
                # ALTUS Lock -- under the Gelmir Lock alone, warping to them kicks you out of locked
                # Altus. The Gelmir Lock stays a pure logic gate on Gelmir's checks. (Alaric 2026-06-20)
                # Mt. Gelmir un-rebucketed 2026-06-26: Gelmir is its OWN play region 63001
                # (not Altus 63000), enforced by Mt. Gelmir Lock (area_ids 63001+16000). Its
                # graces ride Mt. Gelmir Lock like any other region. See REGION_ID_MAP.md.
                _points = [p for p in _points if p[0] not in _SKIP_GRACE_FLAGS]
                if not _lock or not _points:
                    continue
                if getattr(self.options, 'grace_rando', None) and self.options.grace_rando.value:
                    _chosen = getattr(self, '_grace_rando_freebie_by_region', {}).get(_region, [])
                else:
                    _chosen = _spread(_points, _n)
                region_graces.setdefault(_lock, []).extend(_chosen)
            for _lock in region_graces:
                region_graces[_lock] = sorted(set(region_graces[_lock]))
            # Underground map-layer guarantee (belt-and-suspenders, RE 2026-07-03): the
            # underground map only becomes selectable once the player holds an underground
            # GRACE flag (71270 "Siofra River Well Depths" alone flipped the layer on). The
            # _spread bundle above already puts underground graces on Nokron/Nokstella Lock,
            # but graces_per_region/_spread could drop them, so force one guaranteed grace per
            # underground lock. Same shape as the DLC map flag 82001 bundled onto Gravesite
            # Plain's lock below. Harmless if the lock is sealed/absent (only set on receipt).
            for _ulock, _ugrace in (("Nokron Lock", 71270), ("Nokstella Lock", 71211)):
                if _ulock in item_table:
                    region_graces[_ulock] = sorted(set(region_graces.get(_ulock, []) + [_ugrace]))
            # Limgrave Lock (SPEC-region-spine-surgery.md P0): Limgrave is a normal LOCKED region
            # but has NO REGION_GRACE_POINTS entry (never captured there -- only the curated flat
            # LIMGRAVE_START_GRACES list exists). Bundle those curated Limgrave/Stormhill
            # warp-unlock graces onto Limgrave Lock UNCONDITIONALLY (any pool-found Limgrave Lock,
            # not just the spawn freebie, must open the region for fast travel -- same as every
            # other region lock's apparatus), same as every other lock's grace bundle: only a
            # SEALED Limgrave (num_regions rolled it out) stays dark.
            if not _limgrave_sealed:
                region_graces["Limgrave Lock"] = sorted(set(
                    region_graces.get("Limgrave Lock", []) + list(LIMGRAVE_START_GRACES)))
            # Bundle-lock entrance graces (Liurnia Caves / Shadow Catacombs): these minor-dungeon
            # bundles gate via one shared lock and (mostly) aren't in REGION_GRACE_POINTS, so the
            # loop above grants them nothing. Grant each bundled dungeon's ENTRANCE grace on receipt
            # of the bundle lock so fast-travel into the dungeons unlocks with the key. Gated on the
            # lock actually being injected (opt-in option on / always-on Liurnia); inert otherwise.
            # patch_bundle_lock_graces_chain: a bundle lock that is a num_regions/dlc CHAIN-
            # managed lock is precollected (free start link) or breadcrumbed (inject=False) yet
            # very much IN PLAY -- its kept region is part of the seal scope. The old inject-only
            # gate skipped it, so a kept cave-bundle (Spelunker torch) got an EMPTY grace bundle:
            # a link-0 cave start spawned with no cave graces (can't rest / fast-travel) and a
            # breadcrumb cave lock lit nothing on receipt. Include chain-managed bundle locks too.
            _chain_mgd_bundles = (getattr(self, "_num_regions_chain_managed_locks", set())
                                  | getattr(self, "_dlc_chain_managed_locks", set()))
            for _blk, _bflags in BUNDLE_LOCK_GRACES.items():
                if _blk in item_table and (getattr(item_table[_blk], "inject", False)
                                           or _blk in _chain_mgd_bundles):
                    region_graces[_blk] = sorted(set(region_graces.get(_blk, []) + list(_bflags)))
            # DLC map: the Land of Shadow map is a SINGLE flag (82001, Hexinton CT) -- no per-region
            # DLC map flags exist. Bundle it onto the DLC entry region (Gravesite Plain) so reaching
            # the Land of Shadow reveals its map via region progression. Idempotent with
            # reveal_all_maps when map_option=give; the gating path when map_option!=give. enable_dlc only.
            if self.options.enable_dlc:
                _gp_lock = REGION_LOCK_ITEM.get("Gravesite Plain")
                if _gp_lock:
                    region_graces[_gp_lock] = sorted(set(region_graces.get(_gp_lock, []) + [82001]))
        # Region-open flags (physical region-lock enforcement). ONE dedicated VALID event flag per lock
        # item (map_region_data.OPEN_FLAG_BASE = 76971+, grace-tail gap; the old 69_000_000 scheme was an
        # unallocated no-op), set by the client on receipt. Kept SEPARATE from the 62xxx map-reveal flags
        # so revealing maps (reveal_all_maps grant) never unlocks a region -> maps + lock are independent.
        # Built by build_region_lock_slot_data() below and emitted as "regionOpenFlags" (existing client
        # path + baker call-site key).
        region_lock_sd = {"areaLockFlags": [], "lockOpenFlags": {}, "lockRevealFlags": {}}
        # Roundtable-hub re-root (SPEC-region-spine-surgery.md P0): Limgrave is a normal LOCKED
        # region in the STATIC REGION_LOCK_ITEM now (Track A), so no dynamic splice is needed --
        # `_rli` is a plain alias, kept only so the unchanged code below (notify-item table)
        # does not need touching. This emits Limgrave areaLockFlags (physical KICK) +
        # lockOpenFlags["Limgrave Lock"] (-> regionOpenFlags) + map reveal on unlock, exactly
        # like every other region lock.
        _rli = REGION_LOCK_ITEM
        if self.options.world_logic < 3:
            region_lock_sd = build_region_lock_slot_data(_rli)
        # regionOpenFlags now carries the dedicated VALID open-state flags (was the dead 69M scheme).
        # Distinct from the 62xxx map-reveal flags so revealing maps never unlocks a region. The baker
        # call-site still keys off its presence; the client sets them on lock receipt (existing path).
        region_open_flags = region_lock_sd["lockOpenFlags"]
        # Godrick mini-campaign: Godrick Lock gates the goal via a LOCATION rule (no region ->
        # no auto open flag). Mint a dedicated one here (godrick-scoped) so the baked Stormveil
        # fog wall has a flag to gate on; the client sets it on receipt by item name. NOT added
        # to areaLockFlags -> no play-region KICK -> zero effect on non-godrick region_lock seeds.
        if "godrick" in self.options.extra_region_locks.value and "Godrick Lock" in item_table \
                and getattr(item_table["Godrick Lock"], "lock", False):
            region_open_flags["Godrick Lock"] = 76967  # valid grace-tail flag; baker RegionFogGates keys off this
        if "castle_morne" in self.options.extra_region_locks.value and "Morne Lock" in item_table \
                and getattr(item_table["Morne Lock"], "lock", False):
            region_open_flags["Morne Lock"] = 76966    # Castle Morne gate fog wall keys off this
        # Lock -> notify item (packed GOODS address). Granted by the client on lock receipt so the
        # native item ticker fires and NAMES the region (e.g. 'Map: Liurnia, East') -- locks are
        # otherwise invisible (sentinel 99999). Region with no map -> generic token. Shared locks
        # take the first mapped region's map.
        lock_notify_items = {}
        if self.options.world_logic < 3:
            _NOTIFY_TOKEN = 2900  # Golden Rune [1] (GOODS) marker for map-less locks
            _tmp = {}
            for _region, _lock in _rli.items():
                _code = REGION_MAP_ITEM.get(_region)
                if _code:
                    _tmp.setdefault(_lock, _code)
            for _name, _data in item_table.items():
                if getattr(_data, "lock", False):
                    _tmp.setdefault(_name, _NOTIFY_TOKEN)
            lock_notify_items = {_lk: (_c | 0x40000000) for _lk, _c in _tmp.items()}
        # === NATURAL_KEY_TRIGGERS_PATCH: natural-key region apparatus (Mountaintops + Snowfield) ===========
        # Two regions whose locks have NO pool item; the client blooms their apparatus when a
        # vanilla disjunctive trigger fires (see naturalKeyTriggers in slot_data below). We
        # mint their grace bundle / dedicated open-flag / map-reveal / notify token here so the
        # client has something to bloom. Apparatus only -- AP fill logic (Rold/Haligtree +
        # Morgott) is unchanged. Gated to region-gating modes (world_logic < 3).
        natural_key_triggers = {}
        if self.options.world_logic < 3:
            _NK_GRACES = {
                "Mountaintops Lock": [76500, 76501, 76502,
                                      76503, 76504, 76505, 76506, 76507, 76508, 76509, 76510,
                                      76520, 76521, 76522, 76523, 76524],
                "Snowfield Lock":    [76550, 76551, 76652, 76653],
            }
            _NK_OPEN = {"Mountaintops Lock": 76965, "Snowfield Lock": 76961}
            _NK_REVEAL = {"Mountaintops Lock": [62050, 62051], "Snowfield Lock": [62052]}
            for _nlk, _nfs in _NK_GRACES.items():
                region_graces[_nlk] = sorted(set(region_graces.get(_nlk, []) + list(_nfs)))
            for _nlk, _nof in _NK_OPEN.items():
                region_open_flags[_nlk] = _nof
            # NK_AREALOCK_MARKER: KICK enforcement for natural-key regions -- areaLockFlags keyed
            # to the apparatus open flags (build_region_lock_slot_data only covers REGION_LOCK_ITEM
            # regions). Snowfield only on the NATURAL path (the opt-in dedicated snowfield lock
            # supplies its own areaLockFlags via REGIONS).
            # Snowfield always uses the natural-key area apparatus now (SPEC-region-spine-
            # surgery.md SS3.5/SS8): the `snowfield` extra_region_locks opt-in member is DELETED
            # (Track A) -- there is no longer a dedicated-lock alternative path to guard against.
            _NK_AREA = {"Mountaintops Lock": [(65000, 65000), (65001, 65001)],
                        "Snowfield Lock": [(65002, 65002)]}
            _alf = region_lock_sd.setdefault("areaLockFlags", [])
            for _nlk, _ranges in _NK_AREA.items():
                _of = _NK_OPEN.get(_nlk)
                if _of is not None:
                    for (_lo, _hi) in _ranges:
                        if [_lo, _hi, _of] not in _alf:
                            _alf.append([_lo, _hi, _of])
            for _nlk, _nrf in _NK_REVEAL.items():
                lock_reveal = region_lock_sd.get("lockRevealFlags", {})
                lock_reveal[_nlk] = sorted(set(lock_reveal.get(_nlk, []) + list(_nrf)))
                region_lock_sd["lockRevealFlags"] = lock_reveal
            # Notify token: GOODS-packed Map fragment so the native ticker names the region on
            # bloom (Mountaintops -> Map: Mountaintops of the Giants, West 8611; Snowfield -> 8618).
            _NK_NOTIFY = {"Mountaintops Lock": 8611, "Snowfield Lock": 8618}
            for _nlk, _ncode in _NK_NOTIFY.items():
                lock_notify_items.setdefault(_nlk, _ncode | 0x40000000)
            # Mountaintops/Snowfield vanilla-key bloom triggers DELETED (SPEC-region-spine-
            # surgery.md SS3.4/SS3.5/SS8, "one sound mode": pool lock items are THE mechanism
            # now, natural-key blooms are the retired alternate). The apparatus above (graces,
            # open flags, areaLockFlags, reveal flags, notify tokens) is REUSED as ordinary lock
            # apparatus -- it fires on item receipt through the standard slot_data path exactly
            # like every other region lock, no client-side bloom-trigger consumer needed for
            # these two locks anymore. Altus Lock keeps its ADDITIVE natural-key trigger (its
            # item-receipt bloom from the standard apparatus stays; this is a genuinely separate,
            # still-natural-key region -- out of this surgery's scope, SS8 "DO NOT APPLY the
            # MT/SF bloom patches" while leaving Altus's own trigger untouched).
            # ALTUS NATURAL KEY RETIRED (2026-07-03, "Academy Glintstone Key sole
            # natural lock"): Altus Lock is a real pool lock (lock=True), so its
            # apparatus blooms on ordinary item receipt like MT/SF. The additive
            # Dectus/Rold natural trigger is dropped -- Raya is now the only natural key.
            natural_key_triggers = {}
        # === end NATURAL_KEY_TRIGGERS_PATCH ================================================================
        # === NATURAL_KEY_TRIGGERS_P2: natural-key apparatus + triggers (Raya Lucaria + Volcano Manor) =======
        # Two more natural-key regions, EXTENDING the P1 apparatus above (natural_key_triggers,
        # region_graces, region_open_flags, region_lock_sd["lockRevealFlags"], lock_notify_items
        # all already exist). Raya Lucaria Academy has NO lock item (gated by vanilla Academy
        # Glintstone Key); Volcano Manor's "Volcano Lock" is a logic item with NO grace/open
        # apparatus. Both need fresh apparatus so the client (generic EvaluateNaturalKeyTriggers)
        # can bloom them; the triggers are vanilla key items / the Drawing-Room obtained-flag.
        # Gated to region-gating modes (world_logic < 3), same as P1.
        if self.options.world_logic < 3:
            # RAYA LUCARIA = SOLE NATURAL KEY (2026-07-03). The vanilla Academy Glintstone
            # Key IS the Raya Lucaria lock; there is no pool-item analogue, so it stays
            # natural. VOLCANO NATURAL KEY RETIRED: Volcano Lock is lock=False ("folded into
            # Mt. Gelmir Lock"), so its interior apparatus folds onto Mt. Gelmir Lock --
            # Volcano Manor blooms when Mt. Gelmir Lock is received via the ordinary path.
            _NK2_GRACES = {
                # Raya Lucaria Academy interior (m14_00_00 grace_flags.tsv warpUnlockFlags).
                "Raya Lucaria Lock": [71400, 71402, 71403],  # 71401 Debate Parlor EXCLUDED: Red Wolf of Radagon arena (warp drops you behind the fog)
            }
            _NK2_OPEN = {"Raya Lucaria Lock": 76962}
            for _n2k, _n2fs in _NK2_GRACES.items():
                region_graces[_n2k] = sorted(set(region_graces.get(_n2k, []) + list(_n2fs)))
            for _n2k, _n2of in _NK2_OPEN.items():
                region_open_flags[_n2k] = _n2of
            # Volcano Manor interior graces (m16_00_00; 71600 EXCLUDED -- already owned by
            # BUNDLE_LOCK_GRACES["Spelunker's Torch"], Murkwater Cave shares the m16 tile id)
            # FOLD onto Mt. Gelmir Lock. Natural-key blocks run AFTER the graces_per_region
            # spread-trim, so this appends raw (no trimming) -- all seven bloom on receipt.
            _VOLCANO_GRACES = [71601, 71602, 71603, 71604, 71605, 71606, 71607]
            region_graces["Mt. Gelmir Lock"] = sorted(set(
                region_graces.get("Mt. Gelmir Lock", []) + _VOLCANO_GRACES))
            # KICK enforcement: Raya 14000 on its own open flag 76962; Volcano 16000 folded
            # onto Mt. Gelmir Lock's computed open flag (region_open_flags = lockOpenFlags).
            _alf2 = region_lock_sd.setdefault("areaLockFlags", [])
            _NK2_AREA = [(14000, 14000, 76962)]
            _mg_of = region_open_flags.get("Mt. Gelmir Lock")
            if _mg_of is not None:
                _NK2_AREA.append((16000, 16000, _mg_of))
            for (_lo, _hi, _of) in _NK2_AREA:
                if [_lo, _hi, _of] not in _alf2:
                    _alf2.append([_lo, _hi, _of])
            # Raya is a map-less interior: the 2900 packed token names nothing special
            # (matches the apworld _NOTIFY_TOKEN). Volcano rides Mt. Gelmir Lock's notify.
            lock_notify_items.setdefault("Raya Lucaria Lock", 2900 | 0x40000000)
            # Sole disjunctive natural trigger: the Academy Glintstone Key opens Raya Lucaria.
            natural_key_triggers.update({
                "Raya Lucaria Lock": {"anyOf": [
                    {"items": ["Academy Glintstone Key"]},
                    {"items": ["Academy Glintstone Key (Thops)"]},
                ]},
            })
        # === end NATURAL_KEY_TRIGGERS_P2 ===================================================================
        # === NATURAL_KEY_TRIGGERS_P3: Haligtree (Right medallion, semi-natural split) =====================
        # Miquella's Haligtree + Elphael as a natural-key region: bloom on the Right Haligtree
        # Secret Medallion. Graces 71501-71508 (Malenia 71500 EXCLUDED -- boss arena); open flag
        # 76964; KICK area_ids 15000 (Elphael) + 15001 (Miquella's Haligtree). No map pillar.
        if self.options.world_logic < 3:
            region_graces["Haligtree Lock"] = sorted(set(region_graces.get("Haligtree Lock", []) + [
                71501, 71502, 71503, 71504, 71505, 71506, 71507, 71508]))
            region_open_flags["Haligtree Lock"] = 76964
            # Haligtree Lock trigger registration DELETED (SPEC-region-spine-surgery.md SS3.6/SS8,
            # "Repoint onto ordinary item-receipt (remove Haligtree from natural_key_triggers;
            # keep the graces/open-flag/area_ids wiring)"). Haligtree Lock is lock=True and
            # ordinarily injected/found now (change A) -- the standard receipt path fires this
            # apparatus directly, no vanilla-key bloom trigger needed.
            _alf3 = region_lock_sd.setdefault("areaLockFlags", [])
            for (_lo, _hi) in [(15000, 15000), (15001, 15001)]:
                if [_lo, _hi, 76964] not in _alf3:
                    _alf3.append([_lo, _hi, 76964])
        # === end NATURAL_KEY_TRIGGERS_P3 ==================================================================
        # snowfield opt-in-split survival block DELETED (SPEC-region-spine-surgery.md SS8): the
        # `snowfield` extra_region_locks member no longer exists (Track A) -- Snowfield Lock is
        # always-on and never carries a natural_key_triggers entry to begin with (deleted above,
        # change D2), so there is nothing left to pop().
        # --- OPEN-FLAG DISJOINTNESS GUARD (er-open-flag-collision-bug) -----------
        # Every lock owns a UNIQUE open-state flag. The computed band (OPEN_FLAG_BASE+i,
        # 76971+) and the hand-picked special/NK flags (below BASE, 76961-76967) must
        # never alias -- otherwise receiving one lock silently opens another's region.
        # Fail gen LOUDLY here rather than ship a mis-gated seed.
        if self.options.world_logic < 3:
            _of_owner = {}
            for _lk, _fl in region_open_flags.items():
                if _fl in _of_owner:
                    raise Exception(
                        "[ER region-lock] open-flag collision: %r and %r both use flag %d. "
                        "Reassign so the OPEN_FLAG_BASE band (76971+) and the below-BASE "
                        "special flags stay disjoint (see map_region_data.OPEN_FLAG_BASE)."
                        % (_lk, _of_owner[_fl], _fl))
                _of_owner[_fl] = _lk
            if 76970 in _of_owner:
                raise Exception("[ER region-lock] %r claims the reserved KICK flag 76970."
                                % _of_owner[76970])
        # --- end OPEN-FLAG DISJOINTNESS GUARD ------------------------------------

        # Start graces (load-time, FLAG-based -- not name-keyed): the client sets these at
        # load via its startGraces consumer, independent of item-name resolution. Needed
        # because precollected locks arrive name-UNRESOLVED ('Unknown from Server'), so the
        # on-receipt regionGraces path never fires. Under dlc_only this ports the CT
        # 'Unlock DLC Maps' (62080-62084) + 'Unlock DLC Graces / Gravesite Plain' (76800+)
        # so the Land-of-Shadow hub is warpable from load (no Mohg+Radahn route needed).
        start_graces = []
        if self.options.dlc_only and self.options.world_logic < 3:
            start_graces = [62080, 62081, 62082, 62083, 62084]
            # grace_rando (no hub special-treatment): light only the Gravesite graces that did NOT
            # become in-region token drops -- i.e. the rolled freebie + any overflow that found no
            # filler check. Guarantees every Gravesite grace is either lit here or findable as a
            # drop (none vanish). Without grace_rando the hub stays fully fast-travelable.
            if getattr(self.options, 'grace_rando', None) and self.options.grace_rando.value:
                _gp_placed = getattr(self, '_grace_rando_placed_by_region', {}).get("Gravesite Plain", set())
                start_graces += [int(_p[0]) for _p in REGION_GRACE_POINTS.get("Gravesite Plain", [])
                                 if _p[0] not in _gp_placed]
            else:
                start_graces += [int(_p[0]) for _p in REGION_GRACE_POINTS.get("Gravesite Plain", [])]
            start_graces += [71190]  # Roundtable Hold grace (m11_10): Twin Maidens bell bearings + remembrance exchange
            start_graces += [76101]  # The First Step (m60 Limgrave grace, BonfireWarpParam 61423601):
                                     # fast-travel anchor back to the base-game opening from the DLC.
            start_graces = sorted(set(int(_f) for _f in start_graces))

        # Base-game lock seeds: the always-open HUB graces are never lit by the on-receipt
        # regionGraces path (no lock is *received* for an always-open region), and skip-Melina /
        # warp can stop Melina's vanilla Roundtable hand-off from ever firing -- so the player can
        # spawn at Limgrave with NO grace lit and no Roundtable. Pre-light the hub at load for
        # non-dlc_only region_lock / region_lock_bosses seeds. (patch_apworld_base_hub_startgraces.py)
        if not self.options.dlc_only and self.options.world_logic.value in (0, 2):
            start_graces = sorted(set(start_graces + [71190]))  # Roundtable Hold (always-open hub)
            # P0: _random_start_region is always set under region-gating world_logic now (the
            # generate_early default rolls "Limgrave" when nothing else did) -- light the ROLLED
            # (or defaulted) start region's graces instead of The First Step (76101), since
            # Limgrave is a LOCKED region like any other and 76101 would warp in for free.
            # REGION_GRACE_POINTS has no "Limgrave" entry (curated flat LIMGRAVE_START_GRACES
            # exists instead, [flag,...] not [[flag,x,z],...]) -- fall back to it by name.
            if self._random_start_region == "Limgrave":
                start_graces = sorted(set(start_graces + [int(f) for f in LIMGRAVE_START_GRACES]))
            else:
                start_graces = sorted(set(start_graces + [
                    int(_p[0]) for _p in REGION_GRACE_POINTS.get(self._random_start_region, [])]))
        # Spectral Steed Whistle (Torrent): vanilla hands the mount over via Melina's accord at a
        # grace, but the region-lock / pre-lit-grace flow can skip that trigger -- leaving the player
        # mountless even though Bell + Physick were handed up front. Grace-based fast travel is built
        # to avoid the "Torrent slog", so when the convenience companions are granted at start
        # (bell_physick_option == 0), grant Torrent the same way: GRANT the whistle goods item in-world
        # (startItems, GOODS-packed FullID -> client GrantFullID) AND SET the vanilla "obtained" flag
        # 60100 (startGraces pump -> SetEventFlag) so Melina won't re-offer it and possession-gated
        # events behave. Mirrors kCompanionAcquireFlags (Bell 60110, Whetstone 60130).
        # Random/rolled starting region: grant the rolled region's grace bundle at load (minus
        # boss-arena/border graces) + Roundtable (71190) + the region's open flag, and record the
        # centroid grace as the baked WarpPlayer target (_rsr_warp_grace). NO First Step (76101):
        # Limgrave is LOCKED under the Roundtable re-root. "Roundtable Hold" -> empty bundle, warp
        # grace 0 -> baker skips the forced warp. SPEC-random-start-roundtable-hub.md.
        _rsr = getattr(self, "_random_start_region", None)
        _rsr_warp_grace = 0
        # P0: Limgrave has no REGION_GRACE_POINTS entry (curated flat LIMGRAVE_START_GRACES
        # exists instead, [flag,...] not [[flag,x,z],...] -- no coordinates to spread/center on).
        _rsr_is_limgrave = (_rsr == "Limgrave")
        if _rsr and self.options.world_logic < 3:
            _RS_SKIP = frozenset({71240, 76422, 76508, 76509, 76852, 76853, 76930, 76931,
                                  73204, 73207, 76209, 76229, 76301, 76350, 76351, 76356})
            _rs_pts = ([] if _rsr_is_limgrave else
                       [p for p in REGION_GRACE_POINTS.get(_rsr, []) if p[0] not in _RS_SKIP])
            # grace_rando: light only this region's ONE freebie grace (like every other region) and
            # spawn at it; otherwise light the full start-region bundle (warp = centroid, below).
            _rsr_gr_on = bool(getattr(self.options, "grace_rando", None) and self.options.grace_rando.value)
            _rsr_fb = getattr(self, "_grace_rando_freebie_by_region", {}).get(_rsr, [])
            if _rsr_is_limgrave:
                _rs_g = [int(f) for f in LIMGRAVE_START_GRACES]
            elif _rsr_gr_on and _rsr_fb:
                _rs_g = [int(_rsr_fb[0])]
            else:
                _rs_g = [int(p[0]) for p in _rs_pts]
            _rs_g += [71190]  # Roundtable hub only -- Limgrave is LOCKED, do NOT light First Step 76101
            _rs_of = region_open_flags.get(REGION_LOCK_ITEM.get(_rsr))
            if _rs_of:
                _rs_g.append(int(_rs_of))
            start_graces = sorted(set(start_graces + _rs_g))
            if _rsr_is_limgrave:
                _rsr_warp_grace = 76101  # The First Step -- fixed anchor, no x/z data to center on
            elif _rsr_gr_on and _rsr_fb:
                _rsr_warp_grace = int(_rsr_fb[0])   # spawn at the lit freebie grace
            elif _rs_pts:
                _cx = sum(p[1] for p in _rs_pts) / len(_rs_pts)
                _cz = sum(p[2] for p in _rs_pts) / len(_rs_pts)
                _rsr_warp_grace = int(min(_rs_pts, key=lambda p: (p[1] - _cx) ** 2 + (p[2] - _cz) ** 2)[0])
        self._rsr_warp_grace = _rsr_warp_grace
        # num_regions_chain free-link start graces (patch chain_freelink_startgraces): the FIRST
        # chain link's lock is PRECOLLECTED (start item) and arrives name-UNRESOLVED, so the
        # on-receipt regionGraces/regionOpenFlags path never fires -- the start region spawns with
        # no warp graces + no open flag (observed sync 2026-06-20: Mt. Gelmir start link stranded
        # ~67 min). Mirror the random-start fold: light the free link's bundle + open flag here.
        _free_lock = getattr(self, "_num_regions_chain_free_lock", None)
        if getattr(self, "_num_regions_chain", False) and _free_lock and self.options.world_logic < 3:
            _fl_g = list(region_graces.get(_free_lock, []))
            if _free_lock == "Mt. Gelmir Lock":
                # Gelmir REBUCKET escape: its graces ride the Altus Lock (Gelmir tiles read as the
                # 63xxx Altus play-region), so its own bundle is empty. As the START link it must
                # carry its own graces: Gelmir grace points (minus border skips 73204/76351) + open
                # flag 76985 + Altus open flag 76972 (suppress the 63xxx Altus kick on Gelmir tiles).
                # Opens Altus enforcement early; Altus CHECKS stay Lock-gated in fill.
                _gelmir_skip = frozenset({73204, 76351})
                _fl_g += [int(p[0]) for p in REGION_GRACE_POINTS.get("Mt. Gelmir", [])
                          if p[0] not in _gelmir_skip]
                for _ofk in ("Mt. Gelmir Lock", "Altus Lock"):
                    _ofv = region_open_flags.get(_ofk)
                    if _ofv:
                        _fl_g.append(int(_ofv))
            else:
                _fl_of = region_open_flags.get(_free_lock)
                if _fl_of:
                    _fl_g.append(int(_fl_of))
            start_graces = sorted(set(start_graces + [int(_f) for _f in _fl_g]))
        start_items: List[int] = []
        # QoL (patch_start_with_torch.py): always start with a Torch so a dark cave/catacomb
        # is navigable -- you can't fast-travel out of a dungeon until you reach its grace, and
        # the vanilla opening gives no light. Grants the GAME item id, NOT the 'Spelunker's
        # Torch' region-lock AP item (locks key off the received-item NAME set, not inventory),
        # so it opens nothing. Weapons pack with a 0x0 nibble, so the FullID is just the id.
        start_items.append(24000000)  # Torch (+0)
        # Torrent (Spectral Steed Whistle) start-grant, DECOUPLED from the flask/bell start grant
        # into its own torrent_start knob. auto = grant when the normal Melina hand-off is
        # bypassed (bell_physick start_with OR progressive_physick); on = always; off = never.
        # early_leveling force-grants regardless (it suppresses her hand-off via flag 951).
        _ts = self.options.torrent_start.value
        # patch_torrent_regionlock_start.py: auto (_ts==0) ALSO grants Torrent when a rolled/
        # random start region is in effect (_rsr set, incl. the Roundtable re-root). The region-
        # lock flow pre-lights start graces and BYPASSES Melina's first-meeting Torrent hand-off
        # (rest fires her camera pan, but she never spawns to give the whistle) -> mountless.
        # Confirmed via playtester seed (num_regions, randomize bell). Narrow to Roundtable-only
        # by swapping `_rsr is not None` for `_rsr == "Roundtable Hold"`.
        _grant_torrent = (
            _ts == 1
            or (_ts == 0 and (self.options.bell_physick_option.value == 0
                              or self._progressive_physick_active()
                              or _rsr is not None))
            or bool(self.options.early_leveling)
        )
        if _grant_torrent:
            start_items.append(130 | 0x40000000)   # Spectral Steed Whistle = EquipParamGoods 130 (GOODS)
            start_graces = sorted(set(start_graces + [60100]))
        # Early leveling (skip Melina): grant Level Up + suppress her meeting at load via the two
        # flags her accord sets -- 4680 (Level Up enable) + 951 (first-meeting done). Confirmed
        # in-game 2026-06-16 (set both, rest, Level Up works, no cutscene). 951 also suppresses her
        # Torrent hand-off, so co-grant Torrent (goods 130 + flag 60100) to avoid stranding the mount.
        if self.options.early_leveling:
            start_graces = sorted(set(start_graces + [4680, 951]))
            # (Torrent for early_leveling is now handled by the unified torrent_start block above.)
        # QoL (patch_start_with_flasks.py): always grant the two sacred flasks at load-in.
        # The mod unlocks the Limgrave start graces so you can warp straight out of the Chapel
        # of Anticipation, but that skips the base-game opening where vanilla hands you your
        # flasks -- leaving no way to heal. Grant them unconditionally (GOODS-packed FullIDs,
        # like Torrent above); unconditional covers dlc_only, which always did this.
        #   Flask of Crimson Tears = EquipParamGoods 1001, Flask of Cerulean Tears = 1051.
        start_items.append(1001 | 0x40000000)
        start_items.append(1051 | 0x40000000)
        # Quick Start (dlc_only): the DLC start skips the entire base-game rune-earning curve, so
        # optionally hand over enough runes to reach ~Runelevel 120 immediately. RL120 from a fresh
        # level-1 character costs 3,506,749 runes total (Fextralife Level table); 71 Lord's Runes
        # (EquipParamGoods 2919, 50,000 runes each = 3,550,000) covers it with a small buffer.
        # Emitted as ONE [FullID, count] start-item pair so the client grants the whole stack in a
        # single GrantFullID call (one acquisition popup), not 71 paced single grants. The runes
        # are consumable inventory items -- the player levels at a grace when they choose.
        if self.options.quick_start and self.options.dlc_only:
            start_items.append([(2919 | 0x40000000), 71])  # Lord's Rune x71 = 3,550,000 runes (>= RL120)
        # Sphere-ordered completion scaling (SPEC-sphere-ordered-scaling.md): when basis=sphere, tier
        # each REGION by its AP fill sphere so the rolled start region = sphere 1 = tier 1
        # (start-relative). Emits regionSphereTargets {region: frac} + ER_SPHERE_TIERS.txt for
        # inspection. get_spheres is heavy -> computed only on demand. Baker bridge that APPLIES this
        # is a follow-up (TODO #22); for now it's the inspectable table.
        region_sphere_targets = {}
        # Sphere-basis + smoothstep are THE behavior now (SPEC-region-spine-surgery.md SS3b):
        # Track A deletes the CompletionScaling / CompletionScalingBasis Choice option classes
        # (both hardcoded ON: smoothstep curve, sphere basis) but keeps completion_scaling_floor
        # as a live tuning Range. This block is therefore unconditional now (was gated on
        # `completion_scaling.value and completion_scaling_basis.value == 1`); _cs_mode is the
        # smoothstep constant (was a Choice value; 4 == smoothstep in the old enum).
        _cs_mode = 4
        _cs_floor = self.options.completion_scaling_floor.value / 100.0
        import os as _csos
        if True:  # region_sphere_targets is always computed now (sphere basis is THE behavior)
            def _cs_curve(d):
                if _cs_mode == 2:
                    return d ** 1.6
                if _cs_mode == 3:
                    return d ** 0.55
                if _cs_mode == 4:
                    return d * d * (3 - 2 * d)  # smoothstep: 3d^2-2d^3
                return d
            _region_sphere = {}
            _spheres = list(self.multiworld.get_spheres())
            _sealed = getattr(self, "_spine_sealed_regions", set())
            for _si, _sphere in enumerate(_spheres):
                for _loc in _sphere:
                    if getattr(_loc, "player", None) != self.player:
                        continue
                    _rn = _loc.parent_region.name if getattr(_loc, "parent_region", None) else None
                    if _rn and _rn not in _sealed and _rn not in _region_sphere:
                        _region_sphere[_rn] = _si
            _maxsph = max(1, max(_region_sphere.values(), default=1))
            for _rn, _sph in _region_sphere.items():
                _d = _sph / _maxsph
                region_sphere_targets[_rn] = round(_cs_floor + _cs_curve(_d) * (1.0 - _cs_floor), 4)
            try:
                _lines = ["region\tsphere\ttarget"]
                for _rn in sorted(_region_sphere, key=lambda r: (_region_sphere[r], r)):
                    _lines.append(f"{_rn}\t{_region_sphere[_rn]}\t{region_sphere_targets[_rn]}")
                import time as _cstime
                _cs_stamp = _cstime.strftime("%Y%m%d-%H%M%S")
                _lines.insert(0, "# ER_SPHERE_TIERS stamp=" + _cs_stamp + " maxsphere=" + str(_maxsph) + " regions=" + str(len(_region_sphere)))
                with open(_csos.path.join(_csos.path.dirname(__file__), "ER_SPHERE_TIERS_" + _cs_stamp + ".txt"), "w") as _df:
                    _df.write("\n".join(_lines))
            except Exception:
                pass
        # SCALING_WIRE_PATCH (er-completion-scaling P1): the client resolves the PLAYER's
        # play_region_id/100 (the same sub-id bucket areaLockFlags uses); the name-keyed table
        # above was never client-parseable, so the sphere bridge was dead at the wire ("enemy
        # scaling left VANILLA" every session). Emit RANGE-keyed integer targets
        # [[lo_sub, hi_sub, int(frac*10000)], ...] from map_region_data.REGIONS area_ids plus
        # the NK-interior ids REGIONS deliberately leaves empty. AP sub-regions without their
        # own area_ids ride the covering major's range (e.g. Stormveil Throne rides 10000).
        # Unmapped play regions resolve to the floor tier client-side (under-scale = safe).
        region_sphere_target_ranges = []
        if region_sphere_targets:
            _SW_EXTRA_RANGES = {
                # Emitted by the __init__ areaLockFlags apparatus, kept [] in REGIONS to avoid
                # duplicate kick rows: Haligtree 15000/15001, Raya Lucaria 14000, Volcano 16000.
                "Miquella's Haligtree": [(15001, 15001)],   # 15001 = outer Haligtree
                "Elphael, Brace of the Haligtree": [(15000, 15000)],  # 15000 = Elphael (deeper sphere)
                "Raya Lucaria Academy": [(14000, 14000)],
                "Volcano Manor": [(16000, 16000)],
                # Leyndell (REGION_ID_MAP.md static resolve, 2026-07-03): 11000 Royal Capital,
                # 11050 Ashen Capital. SCALING ONLY -- deliberately NOT added to REGIONS
                # area_ids, so no new KICK rows (Ashen physical kick = separate decision).
                "Leyndell, Royal Capital": [(11000, 11000)],
                "Leyndell, Ashen Capital": [(11050, 11050)],
            }
            from .map_region_data import REGIONS as _SW_REGIONS
            _sw_seen = set()
            for _sw_name, _sw_frac in region_sphere_targets.items():
                _sw_ranges = list((_SW_REGIONS.get(_sw_name) or {}).get("area_ids") or [])
                _sw_ranges += _SW_EXTRA_RANGES.get(_sw_name, [])
                for (_sw_lo, _sw_hi) in _sw_ranges:
                    if (_sw_lo, _sw_hi) in _sw_seen:
                        continue  # first (shallowest-sphere) owner of a shared range wins
                    _sw_seen.add((_sw_lo, _sw_hi))
                    region_sphere_target_ranges.append(
                        [int(_sw_lo), int(_sw_hi), int(round(_sw_frac * 10000))])
        # GRANT-ON-RECEIPT rider (SPEC-region-spine-surgery.md SS3.5, decided after the first
        # Track D pass): the medallions are unpooled (change B above) but the client still needs
        # to physically GRANT them in-game on the covering lock's receipt -- keeps the Grand Lift
        # of Rold / of Dectus usable, fires medallion-triggered quest content (Ensha invasion,
        # Latenna) at the natural moment, and the player never sees a do-nothing AP medallion
        # item. {lock_name: [in-game item ids]}; consumed by the existing GrantFullID-style grant
        # path (client wiring is P3, not this patch's job -- this only emits correct data).
        # ENCODING: er_code | 0x40000000 (GOODS-category-packed FullID), matching startItems /
        # lockNotifyItems / progressiveGrants -- every grant-style slot_data table in this file
        # uses this exact convention (see the category_nibbles map earlier in this method:
        # ERItemCategory.GOODS: 0x40000000). Looked up from item_table by name (not hardcoded
        # literals) so a future items.py renumber stays correct automatically; .skip=True only
        # affects pool participation, the ERItemData table entry (and its er_code) stays intact.
        lock_grant_items: Dict[str, list] = {}
        if self.options.world_logic < 3:
            _LGI_SOURCE = {
                "Mountaintops Lock": ["Rold Medallion"],
                "Haligtree Lock": ["Haligtree Secret Medallion (Left)",
                                   "Haligtree Secret Medallion (Right)"],
            }
            for _lgi_lock, _lgi_names in _LGI_SOURCE.items():
                _lgi_ids = []
                for _lgi_name in _lgi_names:
                    _lgi_data = item_table.get(_lgi_name)
                    if _lgi_data is not None and _lgi_data.er_code:
                        _lgi_ids.append(_lgi_data.er_code | 0x40000000)
                if _lgi_ids:
                    lock_grant_items[_lgi_lock] = _lgi_ids
        slot_data = {
            # CONTRACT: options subkeys partially LIVE (2026-07-01 audit): the Rust client reads
            # death_link, auto_upgrade, global_scadutree_blessing, completion_scaling,
            # completion_scaling_floor, enable_dlc; the PopTracker pack reads world_logic,
            # dlc_only, enable_dlc, location_pool. All other subkeys have no slot_data consumer
            # (baker-era ConvertRandomizerOptions inputs or gen-only echoes) -- see
            # SPEC-goal-send-20260701.md Appendix A before adding or trimming any.
            "options": {
                "ending_condition": self.options.ending_condition.value,
                "world_logic": self.options.world_logic.value,
                # Completion-percent scaling (SPEC-completion-scaling.md): mode + floor. The baker
                # reshapes each enemy's native scaling tier by this curve/floor.
                # completion_scaling is HARDCODED 4 (smoothstep) now (SPEC-region-spine-surgery.md
                # SS3b): the CompletionScaling Choice option is deleted (Track A); the slot_data
                # KEY NAME is preserved unchanged (the Rust client reads it by name) but the
                # value is a constant instead of an option read.
                "completion_scaling": 4,
                "completion_scaling_floor": self.options.completion_scaling_floor.value,
                "global_scadutree_blessing": self.options.global_scadutree_blessing.value,
                "location_pool": self.options.location_pool.value,
                "dlc_gear_curation": self.options.dlc_gear_curation.value,
                "soft_logic": self.options.soft_logic.value,
                "great_runes_required": self.options.great_runes_required.value,
                "great_runes_final_boss": self.options.great_runes_final_boss.value,
                "great_runes_mountaintops": self.options.great_runes_mountaintops.value,
                # Capital/Morgott short-run scope. region_count = the EFFECTIVE (floor-raised)
                # spine length actually used; 0 = feature inert. See region_spine.py.
                "region_count": self._spine_effective_count,
                "royal_access": self.options.royal_access.value,
                "enable_dlc": self.options.enable_dlc.value,
                "dlc_only": self.options.dlc_only.value,
                "quick_start": self.options.quick_start.value,
                "messmer_kindle": self.options.messmer_kindle.value,
                "messmer_kindle_required": self.options.messmer_kindle_required.value,
                "messmer_kindle_max": self.options.messmer_kindle_max.value,
                "dlc_timing": self.options.dlc_timing.value,
                "death_link": self.options.death_link.value,
                "random_start": self.options.random_start.value,
                "auto_upgrade": self.options.auto_upgrade.value,
                "flatten_regular_upgrades": self.options.flatten_regular_upgrades.value,
                "progressive_stone_bells": self.options.progressive_stone_bells.value,
                "progressive_physick": self.options.progressive_physick.value,
                "progressive_bell_count": self.options.progressive_bell_count.value,
                "progressive_bell_early_count": self.options.progressive_bell_early_count.value,
                "crafting_kit_option": self.options.crafting_kit_option.value,
                "map_option": self.options.map_option.value,
                "smithing_bell_bearing_option": self.options.smithing_bell_bearing_option.value,
                "merchant_bell_logic": self.options.merchant_bell_logic.value,
                "early_legacy_dungeons": self.options.early_legacy_dungeons.value,
                "local_item_option": self.options.local_item_option.value,
                "exclude_local_item_only": self.options.exclude_local_item_only.value,
                "important_locations": self.options.important_locations.value,
                "exclude_locations": self.options.exclude_locations.value,
                "excluded_location_behavior": self.options.excluded_location_behavior.value,
                "missable_location_behavior": self.options.missable_location_behavior.value,
                "dungeon_sweep": self.options.dungeon_sweep.value,
                # Boss attribution + grace complement (SPEC-boss-attribution.md). The bake reads
                # both from here and emits sweep_flags into apconfig.json when dungeon_sweep==bosses.
                # Deliberately a REAL bool (not 0/1 like the toggles above): the static
                # randomizer's options dict only admits JSON booleans, and this one is
                # consumed there (ConvertRandomizerOptions -> opt["weaponreqs"]).
                "no_weapon_requirements": bool(self.options.no_weapon_requirements.value),
                # Tier-A enemy-rando sub-toggles + Serpent-Hunter tweak. Shipped as REAL
                # bools (not 0/1) so they survive the static randomizer's bool-only
                # options filter, same as no_weapon_requirements above.
                "bell_physick_option": self.options.bell_physick_option.value,
                "torrent_start": self.options.torrent_start.value,
            },
            # CONTRACT: PORT-GAP (seed-verify guard; ds3 check_seed_conflict precedent, not ported)
            "seed": self.multiworld.seed_name,  # to verify the server's multiworld
            # CONTRACT: DEAD (baker-era, no consumer 2026-07-01)
            "slot": self.multiworld.player_name[self.player],  # to connect to server
            "apIdsToItemIds": ap_ids_to_er_ids,
            "itemCounts": item_counts,
            # Optional; only present when dungeon_sweep != none. Consumed by the runtime
            # client only — the static randomizer ignores it.
            "dungeonSweeps": dungeon_sweeps,
            # BOSS_LOCKS_PATCH: sweep gates -- trigger apLocId -> boss lock item name that must
            # be in the client's received set before that trigger's sweep fires. Runtime client
            # only; re-checked every flag-poll tick (late lock => retroactive sweep).
            "sweepLockGates": sweep_lock_gates,
            # Locations whose full completion = goal, for ending_condition 2/3 (empty
            # otherwise). Consumed by the runtime client only.
            # CONTRACT: PORT-GAP (goal send -- SPEC-goal-send-20260701.md)
            "goalLocations": goal_locations,
            # Region-fusion grace bundle: lock-item name -> grace warp flags to enable on
            # receipt (region gating only; empty otherwise). Runtime client only. TODO #13.
            "regionGraces": region_graces,
            # CONTRACT: LIVE (consumed by region.rs::tick_grace_items; SPEC-grace-rando.md B ported to Rust)
            "graceItems": getattr(self, "_grace_items_placed", {}),
            # Region-open flags (physical enforcement, SPEC-region-fog-gates.md): lock-item name
            # -> one reserved event flag the client sets on receipt; baked border fog gates gate
            # on it. Region gating only; empty otherwise.
            "regionOpenFlags": region_open_flags,
            # Progressive stone bells: item name -> ordered [{goods,flags}] per copy. Client
            # keeps a per-item receipt counter; Kth copy sets flags[K] + grants goods[K]. Empty off.
            "progressiveGrants": progressive_grants,
            # Physical region-lock DETECTION table (regression fix 2026-06-16): {[lo,hi,open_flag]}.
            # Built by build_region_lock_slot_data() but previously never emitted, so the client
            # received no ranges and NO region (Belurat etc.) ever kicked. open_flag matches the
            # regionOpenFlags value set on lock receipt, so received locks open their region.
            "areaLockFlags": sorted(region_lock_sd["areaLockFlags"]),
            # Map-reveal/open flags per lock (cosmetic under reveal_all_maps; correct for map gating).
            "lockRevealFlags": region_lock_sd["lockRevealFlags"],
            # GRANT-ON-RECEIPT rider (SPEC-region-spine-surgery.md SS3.5): lock name -> [packed
            # FullIDs] to physically grant in-game on that lock's receipt. Currently the two
            # unpooled medallions (Rold -> Mountaintops Lock; both Secret Medallion halves ->
            # Snowfield Lock). Empty outside region-gating world_logic. CONTRACT: LIVE
            # (consumed by region.rs::first_open_grants + hook_impl.rs).
            "lockGrantItems": lock_grant_items,
            # Natural-key disjunctive triggers (NATURAL_KEY_TRIGGERS_PATCH): lock name -> {"anyOf":[{items,flags}...]}.
            # Client blooms the region apparatus (graces/open-flag/reveal) when ANY clause is satisfied
            # (ALL items received AND ALL flags set). Apparatus-only regions (Mountaintops/Snowfield);
            # Altus is additive to its item-receipt bloom. Region gating only; empty otherwise.
            "naturalKeyTriggers": natural_key_triggers,
            # Load-time grace flags (see build above): fixes the precollected-lock name miss;
            # under dlc_only ports the CT DLC map+grace unlock so Gravesite Plain warps from load.
            "startGraces": start_graces,
            # Random/rolled starting region: rolled hub region name + its central warp grace, for the
            # baked WarpPlayer (ApplyRandomStartEntry). "" / 0 when off (-> baker skips the warp).
            "startRegion": getattr(self, "_random_start_region", None) or "",
            # Random-start auto-entry latch (the runtime client mirrors dlcEntryWarpFlag): warp flag
            # (MUST match RegionFogGates.RANDOM_START_FLAG), the Chapel area id the client watches, and
            # a persistent done-guard so it fires once per save. 0 when not a random-start seed.
            "randomStartWarpFlag": 76969 if getattr(self, "_random_start_region", None) else 0,
            "randomStartAreaId": 18000 if getattr(self, "_random_start_region", None) else 0,
            "randomStartDoneFlag": 76968 if getattr(self, "_random_start_region", None) else 0,
            # DLC-only auto-entry (SPEC, 2026-06-16): the client sets dlcEntryWarpFlag ONCE when it
            # detects the player in dlcStartAreaId (Chapel of Anticipation) -> baked common.emevd
            # WarpPlayer streams them into Gravesite Plain (m61). 0 on non-dlc_only seeds (client no-ops).
            # CONTRACT: PORT-GAP (dlc_only Chapel auto-entry latch; C++-client-era feature, no Rust consumer)
            "dlcEntryWarpFlag": 76999 if self.options.dlc_only else 0,
            # CONTRACT: PORT-GAP (dlc_only Chapel auto-entry latch; pairs with dlcEntryWarpFlag)
            "dlcStartAreaId": 18000 if self.options.dlc_only else 0,  # TODO confirm via RegionLock log
            # Start items granted in-world at load-in (GOODS-packed FullIDs). Used for the Spectral
            # Steed Whistle (Torrent) when companions are handed up front (see fill above). Consumed
            # by the runtime client's startItems handler only; the static randomizer ignores it.
            "startItems": start_items,
            # Map reveal under map_option=give (beta.3): client sets every region map-reveal flag
            # directly, no map fragment items granted. True only for give; False otherwise. TODO #5.
            "reveal_all_maps": self.options.map_option.value == 1,
            # Sphere-ordered completion scaling (SPEC-sphere-ordered-scaling.md): basis + per-region
            # AP-sphere target table. {} / geographic unless completion_scaling on with basis=sphere.
            # The baker bridge that consumes regionSphereTargets is a follow-up (TODO #22).
            # completionScalingBasis is HARDCODED 1 (sphere) now (SPEC-region-spine-surgery.md
            # SS3b): the CompletionScalingBasis Choice option is deleted (Track A); sphere is THE
            # only basis (the geographic alternative no longer exists). Key name preserved.
            "completionScalingBasis": 1,
            "regionSphereTargets": region_sphere_targets,
            # SCALING_WIRE_PATCH: the client-parseable form -- [[lo_sub, hi_sub, target/10000]]
            # in play_region/100 space. The name-keyed table above stays for inspection only.
            "regionSphereTargetRanges": sorted(region_sphere_target_ranges),
            # ER-stack ENCODING / slot_data contract version range (what decisions A–E
            # define), NOT any binary's release number. Enforced by BOTH the static
            # randomizer at bake AND the runtime client at connect, each checking its
            # implemented contract version against this range (single source of truth).
            # Pre-1.0 MVP: per-build lockstep — every contract change bumps beta.N across
            # apworld + randomizer + client. Graduate to ">=0.1.0 <0.2.0" once A–E freeze.
            # beta.2: apIdsToItemIds values are now category-packed (top nibble: weapon=0,
            # armor=1, accessory=2, goods=4, ash-of-war=8) instead of raw er_codes.
            # beta.3: + reveal_all_maps (map_option=give reveals via flags, no map items granted).
            "versions": ">=0.1.0-beta.4 <0.1.0-beta.5",
        }

        # [p1-location-flags] emit the static vanilla acquisition-flag table for active
        # locations, so the runtime client gets detection data from slot_data (no baker).
        try:
            import os as _p1_os, json as _p1_json
            _p1_path = _p1_os.path.join(_p1_os.path.dirname(__file__), "er_static_detection_table.json")
            with open(_p1_path, encoding="utf-8") as _p1_f:
                _p1_tbl = _p1_json.load(_p1_f)["location_flags"]
            slot_data["locationFlags"] = {
                str(_lid): _p1_tbl[str(_lid)]
                for _lid in location_ids_to_keys
                if str(_lid) in _p1_tbl
            }
        except Exception as _p1_e:
            slot_data["locationFlags"] = {}
            print(f"[p1-location-flags] WARN could not load table: {_p1_e}")
        # [emit-location-keys] client key contract (Bedrock/matt-rando): emit the
        # per-location key + targets tables keyed by AP location id (location.address).
        # AP stringifies int dict keys in slot_data, so we emit int keys directly.
        #   locationIdsToKeys[addr]    = the matt-rando key string (e.g. '100000,0:0000060510::')
        #   locationIdsToTargets[addr] = list(targets) (e.g. ['lot:102922'] / ['shop:100075'])
        # Same enumeration + guards as the existing location_ids_to_keys build above
        # (get_filled_locations(self.player); skip events / addressless / keyless locs), so
        # synthetic num_regions / boss-lock / event locations (no key) are skipped. `targets`
        # is read with getattr so this is forward-compatible if ERLocationData gains the field
        # later (empty today -- ERLocationData has no `targets` in this apworld's source).
        # ADDITIVE: does not remove or change the locationFlags emission above.
        try:
            _lk_keys = {}
            _lk_targets = {}
            for _lk_loc in cast(List[ERLocation], self.multiworld.get_filled_locations(self.player)):
                if _lk_loc.address is None or _lk_loc.item.code is None:
                    continue
                _lk_data = getattr(_lk_loc, "data", None)
                if _lk_data is None:
                    continue
                _lk_key = getattr(_lk_data, "key", None)
                if not _lk_key:
                    continue
                _lk_keys[_lk_loc.address] = _lk_key
                _lk_tgt = getattr(_lk_data, "targets", None)
                if _lk_tgt:
                    _lk_targets[_lk_loc.address] = list(_lk_tgt)
            slot_data["locationIdsToKeys"] = _lk_keys
            slot_data["locationIdsToTargets"] = _lk_targets
        except Exception as _lk_e:
            slot_data["locationIdsToKeys"] = {}
            slot_data["locationIdsToTargets"] = {}
            print(f"[emit-location-keys] WARN could not build key/target tables: {_lk_e}")
        # [p2-check-items] emit the vanilla check-item FullIDs (+ guarding flags) for the
        # seed's active checks, so the runtime client can SUPPRESS the vanilla item picked
        # up at a check (player only gets what the AP server sends). FullIDs are packed with
        # the SAME nibble logic as apIdsToItemIds (reuses category_nibbles above).
        try:
            import os as _p2_os, json as _p2_json
            _p2_flags = {}
            try:
                _p2_path = _p2_os.path.join(_p2_os.path.dirname(__file__), "er_static_detection_table.json")
                with open(_p2_path, encoding="utf-8") as _p2_f:
                    _p2_flags = _p2_json.load(_p2_f)["location_flags"]
            except Exception:
                _p2_flags = {}
            _p2_ids = set()
            _p2_id_flags = {}
            for _p2_loc in self.multiworld.get_filled_locations(self.player):
                _p2_data = getattr(_p2_loc, "data", None)
                if _p2_data is None or _p2_loc.address is None:
                    continue
                _p2_name = getattr(_p2_data, "default_item_name", None)
                if not _p2_name:  # events carry no vanilla item
                    continue
                _p2_item = item_table.get(_p2_name)
                if _p2_item is None or not _p2_item.er_code:
                    continue
                _p2_nib = category_nibbles.get(_p2_item.category)
                if _p2_nib is None:
                    continue
                _p2_full = _p2_item.er_code | _p2_nib
                _p2_ids.add(_p2_full)
                _p2_flag = _p2_flags.get(str(_p2_loc.address))
                if _p2_flag:
                    _p2_bucket = _p2_id_flags.setdefault(str(_p2_full), [])
                    if _p2_flag not in _p2_bucket:
                        _p2_bucket.append(_p2_flag)
            # CONTRACT: PORT-GAP (vanilla item suppression at checks; pure-runtime port pending)
            slot_data["checkItemIds"] = sorted(_p2_ids)
            # CONTRACT: PORT-GAP (vanilla item suppression at checks; pairs with checkItemIds)
            slot_data["checkItemFlags"] = _p2_id_flags
        except Exception as _p2_e:
            slot_data["checkItemIds"] = []
            slot_data["checkItemFlags"] = {}
            print(f"[p2-check-items] WARN could not build check items: {_p2_e}")
        # [shop-preview] REMOVED 2026-07-03: the baker shop-preview contract (locationIdsToKeys +
        # shopLocationIds) is dead. Pure-runtime shops resolve via shopRowFlags / locationFlags
        # (below); the baker -- their only consumer -- was retired 2026-07-01.
        # [shop-detect] pure-runtime shop-check detection (see shop_row_flags.json + shop_flags.rs).
        # Gated on shop_checks. loc_row_flags -> client rewrites the row's eventFlag_forStock to this
        # flag (emit as shopRowFlags). loc_extra_flags -> slot has a vanilla stock flag missing from the
        # detection table, so just add it to locationFlags (self-detects on purchase, no rewrite).
        try:
            _shd_row_flags = {}
            if True:  # shops are always checks (ShopChecks removed 2026-07-02)
                import os as _shd_os, json as _shd_json
                _shd_path = _shd_os.path.join(_shd_os.path.dirname(__file__), "shop_row_flags.json")
                with open(_shd_path, encoding="utf-8") as _shd_f:
                    _shd_doc = _shd_json.load(_shd_f)
                _shd_lrf = _shd_doc.get("loc_row_flags", {})
                _shd_lef = _shd_doc.get("loc_extra_flags", {})
                _shd_lf = slot_data.setdefault("locationFlags", {})
                for _shd_loc in cast(List[ERLocation], self.multiworld.get_filled_locations(self.player)):
                    _shd_data = getattr(_shd_loc, "data", None)
                    if _shd_data is None or _shd_loc.address is None or not getattr(_shd_data, "shop", False):
                        continue
                    _shd_key = str(_shd_loc.address)
                    if _shd_key in _shd_lrf:
                        _shd_row, _shd_flag = _shd_lrf[_shd_key]
                        _shd_row_flags[str(_shd_row)] = _shd_flag
                    elif _shd_key in _shd_lef:
                        _shd_lf[_shd_key] = _shd_lef[_shd_key]
            slot_data["shopRowFlags"] = _shd_row_flags
        except Exception as _shd_e:
            slot_data["shopRowFlags"] = {}
            print(f"[shop-detect] WARN could not build shop detection flags: {_shd_e}")

        # [shop-preview-goods] {AP location id -> vanilla good id} for active shop slots whose ware is a
        # GOOD, so the runtime client overwrites that good's GoodsName/Caption with the scouted AP item.
        # Gated on shop_checks; source = shop_row_flags.json loc_good_ids (raw ShopLineupParam.equipId).
        try:
            _spg = {}
            if True:  # shops are always checks (ShopChecks removed 2026-07-02)
                import os as _spg_os, json as _spg_json
                _spg_path = _spg_os.path.join(_spg_os.path.dirname(__file__), "shop_row_flags.json")
                with open(_spg_path, encoding="utf-8") as _spg_f:
                    _spg_map = _spg_json.load(_spg_f).get("loc_good_ids", {})
                for _spg_loc in cast(List[ERLocation], self.multiworld.get_filled_locations(self.player)):
                    _spg_data = getattr(_spg_loc, "data", None)
                    if _spg_data is None or _spg_loc.address is None or not getattr(_spg_data, "shop", False):
                        continue
                    _spg_gid = _spg_map.get(str(_spg_loc.address))
                    if _spg_gid is not None:
                        _spg[str(_spg_loc.address)] = _spg_gid
            slot_data["shopPreviewGoods"] = _spg
        except Exception as _spg_e:
            slot_data["shopPreviewGoods"] = {}
            print(f"[shop-preview-goods] WARN could not build shop preview goods: {_spg_e}")

        return slot_data
