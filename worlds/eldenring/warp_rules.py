"""Elden Ring -- grace-warp entrances (rule_builder migration, Phase 4 / Stream B).

Declarative port of ``EldenRingRules._region_lock_warp_access`` (rules_mixin.py:336-394). Under
``region_access == warp`` a region's OWN lock unlocks its graces, so receiving that lock lets you
fast-travel straight in -- access is that lock ALONE, not the geographic chain. The legacy method
imperatively creates a direct hub->region ``"Warp To {region}"`` ``Entrance`` gated on
``state.has(<lock>)`` for every grace-granted region, plus bundle-lock warps for the opt-in cave
bundles.

This is the WARP environment, kept cleanly SEPARATE from the geographic builder (region_lock_data.py
/ region_rules_table) per SPEC-region-rules-rulebuilder.md §4h: the only seam between the two
environments is ``can_go_to`` in rules_predicates.py. These entrances are ADDITIVE new edges; they
do not participate in the ``"Go To"`` AND-composition -- so they are returned as their own list, not
merged into ``region_rules_table``.

Because entrance creation depends on ``world.options`` (region_access, extra_region_locks),
``world._random_start_region`` (hub re-root), and ``world.created_regions`` (membership), this is a
COMPUTED builder that returns a plain description of the edges to create. It creates NO entrances and
mutates nothing -- the rejoin step in ``set_rules`` materializes the ``Entrance`` objects.
"""
from __future__ import annotations

from dataclasses import dataclass

from rule_builder.rules import Rule, Has

from .grace_data import REGION_LOCK_ITEM


__all__ = ["WarpEdge", "build_warp_rules"]


@dataclass(frozen=True)
class WarpEdge:
    """One hub -> ``target`` warp edge to be created as ``Entrance(player, name, hub_region)``.

    * ``name``   -- the entrance name (``"Warp To {target}"``), matching legacy.
    * ``target`` -- the destination region the entrance connects to.
    * ``rule``   -- the access ``Rule`` (always ``Has(<lock item>)``), mirroring the legacy
                    ``add_rule(warp, lambda state: state.has(item, player))``.
    The hub region is supplied by the rejoin step (see ``build_warp_rules`` return doc); it is the
    same for every edge in a build, so it is not repeated per-edge.
    """
    name: str
    target: str
    rule: Rule


def build_warp_rules(world) -> dict:
    """Grace-warp entrance description imposed by legacy ``_region_lock_warp_access``.

    Returns a dict::

        {"hub": <hub region name>, "edges": [WarpEdge, ...]}

    where the rejoin step creates, for each edge, ``Entrance(world.player, edge.name, hub_region)``,
    appends it to ``hub_region.exits``, connects it to ``world.get_region(edge.target)``, and attaches
    ``edge.rule``. Returns ``{"hub": <hub>, "edges": []}`` when ``region_access != warp`` (legacy
    early-return at line 343-344) -- no warp edges exist off the warp model.

    Faithful to rules_mixin.py ``_region_lock_warp_access`` lines 336-394, INCLUDING:
      * only active under ``region_access == warp`` (line 343);
      * the random_start hub re-root: hub = "Roundtable Hold" when ``world._random_start_region`` is
        truthy, else "Limgrave" (line 348);
      * one ``"Warp To {region}"`` per REGION_LOCK_ITEM region present in created_regions, gated on
        that region's lock (line 350-356);
      * under random_start, an extra ``"Warp To Limgrave"`` gated on "Limgrave Lock" (line 362-366),
        since Limgrave is not in REGION_LOCK_ITEM (it was the free hub);
      * the ``_BUNDLE_WARP`` bundle-lock warps, each dungeon gated on the bundle lock, only when the
        bundle's ``extra_region_locks`` key is active (line 371-394).
    """
    hub = "Roundtable Hold" if getattr(world, "_random_start_region", None) else "Limgrave"

    if world.options.region_access != "warp":  # exact legacy comparison (rules_mixin.py:343)
        # Legacy: return immediately; access stays the geographic "Go To" chain. No warp edges.
        return {"hub": hub, "edges": []}

    created = getattr(world, "created_regions", None)

    def present(region: str) -> bool:
        if created is None:
            return True
        return region in created

    edges: list[WarpEdge] = []

    # --- per-region warps (line 350-356) : one Warp To <region> gated on that region's own lock ---
    for region, lock in REGION_LOCK_ITEM.items():
        if not present(region):
            continue
        edges.append(WarpEdge(name=f"Warp To {region}", target=region, rule=Has(lock)))

    # --- legacy random_start Limgrave warp (line 362-366) -- SUPERSEDED: Limgrave now has a
    # static REGION_LOCK_ITEM entry (region-spine surgery SS3.1), so the per-region loop above
    # already emits its warp edge. Guard prevents a DUPLICATE "Warp To Limgrave" entrance
    # (entrance names must be unique per player).
    if (getattr(world, "_random_start_region", None) and present("Limgrave")
            and "Limgrave" not in REGION_LOCK_ITEM):
        edges.append(WarpEdge(name="Warp To Limgrave", target="Limgrave", rule=Has("Limgrave Lock")))

    # --- bundle-lock warps (line 371-394) : each bundled dungeon gated on the shared bundle lock,
    #     only when that bundle's extra_region_locks key is active (logic == warp reality) ----------
    _BUNDLE_WARP = {
        "dlc_catacombs": ("Spelunker's Messmerflame Torch", ["Fog Rift Catacombs", "Belurat Gaol"]),
        "altus_caves": ("Spelunker's Steel-Wire Torch", [
            "Sainted Hero's Grave", "Unsightly Catacombs", "Perfumer's Grotto", "Sage's Cave",
            "Old Altus Tunnel", "Altus Tunnel",
        ]),
        "mountaintops_caves": ("Spelunker's Beast-Repellent Torch", [
            "Giant-Conquering Hero's Grave", "Giants' Mountaintop Catacombs", "Spiritcaller Cave",
            "Consecrated Snowfield Catacombs", "Cave of the Forlorn", "Yelough Anix Tunnel",
        ]),
        "liurnia_caves": ("Spelunker's Ghostflame Torch", [
            "Stillwater Cave", "Lakeside Crystal Cave", "Academy Crystal Cave", "Road's End Catacombs",
            "Black Knife Catacombs", "Cliffbottom Catacombs", "Raya Lucaria Crystal Tunnel",
            "Ruin-Strewn Precipice",
        ]),
        "limgrave_underground": ("Spelunker's Torch", [
            "Fringefolk Hero's Grave", "Coastal Cave", "Church of Dragon Communion", "Groveside Cave",
            "Stormfoot Catacombs", "Limgrave Tunnels", "Murkwater Cave", "Murkwater Catacombs",
            "Highroad Cave", "Deathtouched Catacombs",
        ]),
    }
    erl = world.options.extra_region_locks.value
    for _bkey, (_block, _bdungeons) in _BUNDLE_WARP.items():
        if _bkey not in erl:
            continue
        for _bdn in _bdungeons:
            if not present(_bdn):
                continue
            edges.append(WarpEdge(name=f"Warp To {_bdn}", target=_bdn, rule=Has(_block)))

    return {"hub": hub, "edges": edges}
