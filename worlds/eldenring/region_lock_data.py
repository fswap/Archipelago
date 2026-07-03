"""Elden Ring -- region-lock ACCESS clauses (rule_builder migration, Phase 4 / Stream B).

Declarative port of ``EldenRingRules._region_lock`` (rules_mixin.py, MARK: Region Lock Items).
That method imperatively AND-attaches ``state.has(<lock item>)`` gates onto the geographic
``"Go To {region}"`` entrances (via ``self._add_entrance_rule(region, "Lock")``, which ANDs a
``Has(item)`` onto ``"Go To " + region``). Here we return the SAME per-region lock clause as pure
data, so a later rejoin step can And-combine it with the geographic ``region_rules_table``.

SCOPE / faithfulness (mirrors legacy ``_region_lock`` exactly):
  * ``build_region_lock_rules`` produces ONLY the region-lock clause -- i.e. the ``Has(lock)`` (or,
    for the two non-item gates below, the item/logic gate) that ``_region_lock`` composes for a
    region's ``"Go To"`` entrance. It does NOT include the geographic gates that live in
    ``set_rules`` / ``region_rules_table`` (e.g. the Dectus-medallion gate on Altus at
    rules_mixin.py set_rules, which is NOT part of ``_region_lock``).
  * The whole block is gated on ``world_logic != region_bosses`` (legacy line 398). Under
    ``region_bosses`` (or ``open_world``), ``_region_lock`` adds nothing, so this returns ``{}``.
  * Option-gated sub-blocks (extra_region_locks members, enable_dlc) are honored by reading
    ``world.options`` -- these are option-*membership* decisions, not the count short-circuits the
    predicate contract bakes in, so they must be resolved here at build time (SPEC §4b: option-valued
    region gates live in a builder, not a static dict).

NOT region-access clauses (these live in the geographic ``region_rules_table``, NOT here):
  * ``set_rules`` line 86: Altus Plateau's Dectus-medallion gate. It is added in ``set_rules``,
    not ``_region_lock``, so it is out of scope for this builder.

LOCATION-scoped (NOT a region entrance -- returned separately, see ``build_region_lock_location_rules``):
  * ``godrick`` extra lock: ``_add_location_rule(GODRICK_GOAL_LOCATION, "Godrick Lock")`` gates a
    single LOCATION, not a region entrance. Kept out of the region dict; exposed via a sibling helper
    so the rejoin step can attach it with ``set_rule`` on that location.

CONTRACT NOTE: region-lock gates are plain ``state.has(item)`` gates with no option short-circuit, so
they map to bare ``Has(item)`` from ``rule_builder.rules`` -- there is no predicate factory for them
(and none is needed). The dynamic part is *which* clauses exist (option membership), handled here.
"""
from __future__ import annotations

from rule_builder.rules import Rule, Has

from . import region_spine
from .locations import location_tables


__all__ = ["build_region_lock_rules", "build_region_lock_location_rules"]


def _wl_is_region_bosses(world) -> bool:
    """Legacy guard ``self.options.world_logic != "region_bosses"`` (rules_mixin.py:398).

    ``_region_lock``'s whole entrance block runs only when world_logic is NOT region_bosses.
    Uses the exact legacy string comparison (AP ``Choice.__eq__`` supports comparing to a key)."""
    return world.options.world_logic == "region_bosses"


def _erl(world) -> set:
    """The active ``extra_region_locks`` set (``self.options.extra_region_locks.value``)."""
    return world.options.extra_region_locks.value


def build_region_lock_rules(world) -> dict[str, Rule]:
    """Per-region region-lock ACCESS clause imposed by legacy ``_region_lock``.

    Returns ``{region_name: Rule}`` where ``Rule`` is the lock clause that ``_region_lock`` ANDs onto
    that region's ``"Go To {region}"`` entrance. Pure computation: reads ``world.options`` and
    ``world.created_regions`` for membership only; creates no entrances and mutates nothing.

    The rejoin step And-combines each entry with the geographic ``region_rules_table`` clause (if any)
    for the same region, then attaches the result to the ``"Go To {region}"`` entrance.

    Faithful to rules_mixin.py ``_region_lock`` lines 396-529. Under ``world_logic == region_bosses``
    (legacy line 398) the method adds no locks -> we return ``{}``.
    """
    if _wl_is_region_bosses(world):
        return {}

    created = getattr(world, "created_regions", None)

    def present(region: str) -> bool:
        # _add_entrance_rule no-ops when region not in created_regions (rules_mixin.py:1983).
        if created is None:
            return True
        return region in created

    rules: dict[str, Rule] = {}

    def add(region: str, item: str) -> None:
        """Mirror one ``_add_entrance_rule(region, item)`` call: AND ``Has(item)`` onto the region's
        lock clause. Repeated calls for the same region AND (matches legacy ``add_rule`` stacking)."""
        if not present(region):
            return
        clause = Has(item)
        rules[region] = clause if region not in rules else (rules[region] & clause)

    erl = _erl(world)

    # --- base locks (always, under non-region_bosses) : rules_mixin.py 399-457 -------------------
    # Limgrave: always-on first-class lock (SPEC-region-spine-surgery.md SS3.1). The rolled
    # start region's lock is spawn-granted (Track D / __init__.py), so this entrance clause
    # never dead-locks the start -- Limgrave is either the spawn region (lock pre-granted) or
    # an ordinary locked region reached later like any other.
    add("Limgrave", "Limgrave Lock")

    add("Weeping Peninsula", "Weeping Lock")

    if "limgrave_underground" in erl:
        # Limgrave underground bundle: 10 minor-dungeon regions share Spelunker's Torch (line 400-411)
        for _r in (
            "Fringefolk Hero's Grave", "Coastal Cave", "Church of Dragon Communion",
            "Groveside Cave", "Stormfoot Catacombs", "Limgrave Tunnels", "Murkwater Cave",
            "Murkwater Catacombs", "Highroad Cave", "Deathtouched Catacombs",
        ):
            add(_r, "Spelunker's Torch")

    # Stormveil Start intentionally FREE (legacy comment 412-415); only the deeper castle is gated.
    add("Stormveil Castle", "Stormveil Lock")

    if "stormhill" in erl:
        add("Stormhill", "Stormhill Lock")
    # NOTE: "godrick" gates a LOCATION, not an entrance -> see build_region_lock_location_rules.
    if "castle_morne" in erl and "Castle Morne" in location_tables:
        add("Castle Morne", "Morne Lock")

    add("Liurnia of The Lakes", "Liurnia Lock")
    if "liurnia_caves" in erl:
        # Liurnia minor-dungeon bundle: 8 dungeons share Spelunker's Ghostflame Torch (line 430-439)
        for _r in (
            "Stillwater Cave", "Lakeside Crystal Cave", "Academy Crystal Cave", "Road's End Catacombs",
            "Black Knife Catacombs", "Cliffbottom Catacombs", "Raya Lucaria Crystal Tunnel",
            "Ruin-Strewn Precipice",
        ):
            add(_r, "Spelunker's Ghostflame Torch")

    add("Siofra River", "Nokron Lock")
    add("Nokron, Eternal City Start", "Nokron Lock")

    add("Ainsel River", "Nokstella Lock")
    add("Ainsel River Main", "Nokstella Lock")
    add("Deeproot Depths", "Nokstella Lock")

    add("Lake of Rot", "Nokstella Lock")

    add("Altus Plateau", "Altus Lock")

    add("Caelid", "Caelid Lock")
    add("Sellia Crystal Tunnel", "Caelid Lock")
    add("Redmane Castle Post Radahn", "Redmane Lock")
    add("Dragonbarrow", "Caelid Lock")  # folded into Caelid Lock; was its own Dragonbarrow Lock

    # Mountaintops cluster: always-on first-class lock (SPEC-region-spine-surgery.md SS3.4).
    # Flame Peak and Forbidden Lands ride the same lock (Flame Peak is Mountaintops past Fire
    # Giant; Forbidden Lands is the start of the Mountaintops approach) -- reuses the NK
    # apparatus (open flag 76965) that was previously trigger-gated.
    add("Mountaintops of the Giants", "Mountaintops Lock")
    add("Flame Peak", "Mountaintops Lock")
    add("Forbidden Lands", "Mountaintops Lock")

    add("Altus Plateau", "Altus Lock")  # duplicate in legacy (line 459); idempotent Has & Has.
    add("Mt. Gelmir", "Mt. Gelmir Lock")
    if "altus_caves" in erl:
        # Altus minor-dungeon bundle: 6 dungeons share Spelunker's Steel-Wire Torch (line 461-468)
        for _r in (
            "Sainted Hero's Grave", "Unsightly Catacombs", "Perfumer's Grotto", "Sage's Cave",
            "Old Altus Tunnel", "Altus Tunnel",
        ):
            add(_r, "Spelunker's Steel-Wire Torch")
    add("Volcano Manor Entrance", "Mt. Gelmir Lock")  # folded: Volcano Manor is part of Mt. Gelmir
    add("Volcano Manor Dungeon", "Mt. Gelmir Lock")

    add("Mohgwyn Palace", "Mohgwyn Lock")

    add("Farum Azula", "Farum Azula Lock")
    add("Leyndell, Ashen Capital", "Ashen Lock")

    # Miquella's Haligtree: an ITEM gate (Haligtree Secret Medallion (Right)) inside _region_lock
    # (line 476-477), not a REGION_LOCK_ITEM lock. Ported faithfully as a plain Has.
    # Miquella's Haligtree: first-class lock (SPEC-region-spine-surgery.md SS3.6). Replaces
    # the legacy Haligtree Secret Medallion (Right) item-gate clause -- the medallions are
    # unpooled entirely (Track D / __init__.py inject=False), the lock functionally replaces
    # them.
    add("Miquella's Haligtree", "Haligtree Lock")

    # chokepoint_locks (line 483-488): gate a region's BACK half on reaching its choke-boss drop.
    # Pure logic -- ``self._can_get(state, loc)`` == predicate ``can_get(loc)``. Uses can_get so the
    # clause is a location-reachability rule, faithfully mirroring legacy. Requires a location
    # availability check equivalent to ``self._is_location_available``.
    if "chokepoint_locks" in erl:
        from .rules_predicates import can_get
        for _after, (_befores, _trigs) in region_spine.CHOKEPOINTS.items():
            if not present(_after):
                continue
            _trig = next((t for t in _trigs if world._is_location_available(t)), None)
            if _trig is None:
                continue
            clause = can_get(_trig)
            rules[_after] = clause if _after not in rules else (rules[_after] & clause)

    if "mountaintops_caves" in erl:
        # Mountaintops/Snowfield minor-dungeon bundle: 6 dungeons (line 489-496)
        for _r in (
            "Giant-Conquering Hero's Grave", "Giants' Mountaintop Catacombs", "Spiritcaller Cave",
            "Consecrated Snowfield Catacombs", "Cave of the Forlorn", "Yelough Anix Tunnel",
        ):
            add(_r, "Spelunker's Beast-Repellent Torch")

    # Consecrated Snowfield: always-on first-class lock (SPEC-region-spine-surgery.md SS3.5).
    # No longer opt-in -- the "snowfield" extra_region_locks member is retired (options.py).
    add("Consecrated Snowfield", "Snowfield Lock")
    # Hidden Path to the Haligtree: the Snowfield approach tunnel; rides Snowfield Lock (was
    # medallion-halves gated).
    add("Hidden Path to the Haligtree", "Snowfield Lock")

    # --- DLC locks (enable_dlc) : rules_mixin.py 505-529 -----------------------------------------
    if world.options.enable_dlc:
        add("Gravesite Plain", "Gravesite Lock")
        add("Belurat", "Belurat Lock")
        add("Castle Ensis", "Ensis Lock")
        add("Fog Rift Fort", "Ensis Lock")
        add("Ellac River", "Ellac Lock")
        add("Cerulean Coast", "Cerulean Lock")
        add("Stone Coffin Fissure", "Stone Coffin Lock")
        add("Jagged Peak Foot", "Jagged Peak Lock")
        add("Charo's Hidden Grave", "Charo's Lock")
        add("Scadu Altus", "Scadu Altus Lock")
        add("Rauh Base", "Rauh Base Lock")
        add("Shadow Keep", "Shadow Keep Lock")
        add("Shadow Keep, Church District", "Shadow Keep Lock")
        add("Recluses' River", "Recluses' Lock")
        add("Abyssal Woods", "Abyssal Lock")
        add("Ancient Ruins of Rauh", "Ancient Ruins Lock")
        add("Enir Ilim", "Enir Ilim Lock")
        if "dlc_catacombs" in erl:
            add("Fog Rift Catacombs", "Spelunker's Messmerflame Torch")
            add("Belurat Gaol", "Spelunker's Messmerflame Torch")

    return rules


def build_region_lock_location_rules(world) -> dict[str, Rule]:
    """LOCATION-scoped region-lock clauses from ``_region_lock`` (not region entrances).

    Currently only the ``godrick`` extra lock (rules_mixin.py:425-426), which does
    ``self._add_location_rule(GODRICK_GOAL_LOCATION, "Godrick Lock")`` -- gating the Godrick goal
    LOCATION, not a ``"Go To"`` entrance. Returned separately so the rejoin step attaches it with
    ``set_rule`` on the location rather than folding it into ``region_rules_table``.

    Returns ``{location_name: Rule}``. Empty under ``world_logic == region_bosses`` or when
    ``godrick`` is not in ``extra_region_locks``.
    """
    if _wl_is_region_bosses(world):
        return {}
    rules: dict[str, Rule] = {}
    if "godrick" in _erl(world):
        # Faithful to _add_location_rule(GODRICK_GOAL_LOCATION, "Godrick Lock") -> Has("Godrick Lock").
        rules[region_spine.GODRICK_GOAL_LOCATION] = Has("Godrick Lock")
    # --- BOSS_LOCKS_PATCH (SPEC-boss-locks.md v0.1): gate each major sweep TRIGGER drop -------
    # Client-side the group's sweep only fires while the boss lock is held (slot_data
    # sweepLockGates); logic mirrors that by AND-gating the trigger drop location on Has(lock).
    # Members keep their own geographic rules (still reachable by hand without the lock), and
    # the sweep-OR in _apply_dungeon_sweep_logic wraps the trigger's FINAL rule, so it inherits
    # this clause -- fill can never expect a sweep before the lock. Locks not in this seed's
    # pool (sealed/absent groups) gate nothing. Escape hatch: the lock gates ONLY the trigger
    # drop, so fill can always place it (or another region's lock) in the region-lock-only
    # sphere; a self-gated placement would fail accessibility and re-roll.
    if (getattr(region_spine, "ENABLE_BOSS_LOCKS", False)
            and (world.options.world_logic == "region_lock"
                 or world.options.world_logic == "region_lock_bosses")
            and world.options.dungeon_sweep >= 2):
        world._compute_dungeon_sweeps()  # (re)records _sweep_lock_gates_by_trigger
        _bl_items = world.item_table
        for _bl_trig, (_bl_addr, _bl_lock) in getattr(world, "_sweep_lock_gates_by_trigger", {}).items():
            _bl_data = _bl_items.get(_bl_lock)
            if _bl_data is None or not getattr(_bl_data, "inject", False):
                continue
            _bl_clause = Has(_bl_lock)
            rules[_bl_trig] = _bl_clause if _bl_trig not in rules else (rules[_bl_trig] & _bl_clause)
    return rules
