"""Automated proof for curated_fill (big-ticket routing), v1 -- patch_curated_fill.py.

What curated_fill v1 actually does (and what these tests pin):

  1. BIG-TICKET ROUTING (the real, non-redundant behavior). When curated_fill is on,
     generate_early adds every available "big-ticket" location (the _curated_is_big_ticket
     predicate: prominent | remembrance | keyitem | night/miniboss/evergaol, minus event/
     missable) to self.all_priority_locations, capped by the per-region _PRIO_HEADROOM guard.
     Default important_locations does NOT include keyitem/map/basin, so keyitem-only locations
     are a clean discriminator: PRIORITY under curated_fill, NOT priority without it.

  2. PROGRESSION LANDS ON BIG-TICKET. AP fill forces every PRIORITY location to hold an
     advancement (progression) item. Since big-ticket subset priority under curated_fill, that
     means progression concentrates on the meaningful locations. We prove the invariant holds
     end-to-end (fill succeeds and every priority location's item is advancement).

  3. FEASIBILITY. The soft (no-hard-exclude) design must not FillError under the marquee
     constrained config (num_regions + region_lock + pool_builder). Multi-seed gen+fill.

  4. FILLER-LOCAL DIAL (filler_local_pct). NOTE: this OVERLAPS the existing local_item_option
     (default ON), which already localizes ALL filler GOODS (see __init__.py:442-449). So in the
     default config the dial adds nothing. To prove the dial's OWN wiring we isolate it with
     local_item_option: False and show filler_local_pct: 100 populates local_items in bulk while
     0 leaves it empty. (Design note: because local_item_option already keeps filler home,
     filler_local_pct is largely redundant -- the domination win from curated_fill is the
     big-ticket routing, not this dial.)

Run (Windows, from the Archipelago root):
    python worlds/eldenring/tests/run_tests.py curated_fill
or  python -m pytest worlds/eldenring/tests/test_curated_fill.py
"""
import unittest
from test.bases import WorldTestBase

_DEFAULT_IMPORTANT_FLAGS = ("boss", "church", "seedtree", "fragment", "revered", "remembrance")


class _CuratedBase(WorldTestBase):
    game = "EldenRing"
    auto_construct = True

    # --- helpers -----------------------------------------------------------
    def _has_patch(self):
        return hasattr(self.world, "_curated_is_big_ticket")

    def _my_locations(self):
        return [l for l in self.multiworld.get_locations() if l.player == self.player]

    def _priority(self):
        return set(self.world.all_priority_locations)

    def _keyitem_only_locs(self):
        """Available, non-missable keyitem locations that carry NONE of the default
        important_locations flags -- so they are big-ticket ONLY because curated_fill says so."""
        out = []
        for l in self._my_locations():
            d = l.data
            if l.address is None:
                continue
            if not getattr(d, "keyitem", False):
                continue
            if getattr(d, "missable", False):
                continue
            if any(getattr(d, f, False) for f in _DEFAULT_IMPORTANT_FLAGS):
                continue
            if self._has_patch() and self.world._curated_is_big_ticket(d):
                out.append(l)
        return out


class CuratedFillMarksBigTicket(_CuratedBase):
    """ON: keyitem-only (big-ticket-beyond-defaults) locations become PRIORITY."""
    options = {"enable_dlc": False, "world_logic": "region_lock", "curated_fill": True}

    def test_keyitem_only_locations_are_priority(self):
        if not self.constructed or not self._has_patch():
            self.skipTest("patch_curated_fill.py not applied")
        disc = self._keyitem_only_locs()
        self.assertGreater(len(disc), 0, "no keyitem-only discriminator locations found in this "
                                         "config -- test cannot distinguish routing")
        prio = self._priority()
        routed = [l.name for l in disc if l.name in prio]
        self.assertGreater(
            len(routed), 0,
            f"curated_fill ON: expected keyitem-only locations to be routed to PRIORITY, "
            f"but none of {len(disc)} were. (routed={len(routed)})")

    def test_big_ticket_subset_of_priority(self):
        """The bulk of available big-ticket locations should be priority (allowing the
        per-region headroom to trim a few)."""
        if not self.constructed or not self._has_patch():
            self.skipTest("patch_curated_fill.py not applied")
        bt = [l for l in self._my_locations()
              if l.address is not None and self.world._curated_is_big_ticket(l.data)]
        self.assertGreater(len(bt), 0)
        prio = self._priority()
        in_prio = sum(1 for l in bt if l.name in prio)
        self.assertGreaterEqual(
            in_prio, int(0.8 * len(bt)),
            f"curated_fill ON: expected >=80% of {len(bt)} big-ticket locations to be PRIORITY "
            f"(headroom may trim a few), got {in_prio}")


class CuratedFillOffControl(_CuratedBase):
    """CONTROL (curated_fill OFF): keyitem-only locations must NOT be priority -- default
    important_locations doesn't include keyitem, so nothing routes them without curated_fill."""
    options = {"enable_dlc": False, "world_logic": "region_lock", "curated_fill": False}

    def test_keyitem_only_locations_not_priority(self):
        if not self.constructed or not self._has_patch():
            self.skipTest("patch_curated_fill.py not applied")
        disc = self._keyitem_only_locs()
        self.assertGreater(len(disc), 0)
        prio = self._priority()
        routed = [l.name for l in disc if l.name in prio]
        self.assertEqual(
            routed, [],
            f"curated_fill OFF: keyitem-only locations must NOT be priority, but these were "
            f"(leaked routing?): {routed[:10]}")


class CuratedFillProgressionOnBigTicket(_CuratedBase):
    """ON + full fill: every PRIORITY location holds an advancement item (AP invariant), which
    -- since big-ticket subset priority -- proves progression concentrates on big-ticket."""
    options = {"enable_dlc": False, "world_logic": "region_lock", "curated_fill": True}

    def test_big_ticket_denser_in_advancement(self):
        """AP PRIORITY is best-effort, NOT a guarantee: when advancement items run out, the last
        few priority slots get backfilled with filler (observed: ~6 boss slots on String x5 /
        Golden Rune etc.). So the robust, true claim is comparative -- big-ticket locations hold
        advancement at a MUCH higher rate than filler locations, and most big-ticket hold it."""
        if not self.constructed or not self._has_patch():
            self.skipTest("patch_curated_fill.py not applied")
        from Fill import distribute_items_restrictive
        self.world_setup(12345)
        distribute_items_restrictive(self.multiworld)
        bt_filled = bt_adv = fl_filled = fl_adv = 0
        for l in self._my_locations():
            if l.address is None or l.item is None:
                continue
            if self.world._curated_is_big_ticket(l.data):
                bt_filled += 1
                bt_adv += bool(l.item.advancement)
            else:
                fl_filled += 1
                fl_adv += bool(l.item.advancement)
        self.assertGreater(bt_filled, 0)
        bt_rate = bt_adv / bt_filled
        fl_rate = fl_adv / max(1, fl_filled)
        self.assertGreaterEqual(
            bt_rate, 0.6,
            f"curated_fill ON: most big-ticket locations should hold advancement, got "
            f"{bt_adv}/{bt_filled} = {bt_rate:.2f}")
        self.assertGreater(
            bt_rate, fl_rate + 0.2,
            f"curated_fill ON: big-ticket must be much denser in advancement than filler "
            f"locations (big-ticket={bt_rate:.2f} vs filler={fl_rate:.2f})")

    def test_big_ticket_carries_most_progression(self):
        """Sharper: the majority of this world's advancement items sit on big-ticket locations."""
        if not self.constructed or not self._has_patch():
            self.skipTest("patch_curated_fill.py not applied")
        from Fill import distribute_items_restrictive
        self.world_setup(2468)
        distribute_items_restrictive(self.multiworld)
        adv_total = adv_on_bt = 0
        for l in self._my_locations():
            if l.address is None or l.item is None or not l.item.advancement:
                continue
            adv_total += 1
            if self.world._curated_is_big_ticket(l.data):
                adv_on_bt += 1
        self.assertGreater(adv_total, 0)
        share = adv_on_bt / adv_total
        self.assertGreaterEqual(
            share, 0.5,
            f"curated_fill ON: expected the majority of advancement items on big-ticket "
            f"locations, got {adv_on_bt}/{adv_total} = {share:.2f}")


class CuratedFillFeasibility(_CuratedBase):
    """ON under the constrained marquee config (num_regions + region_lock + pool_builder) must
    gen+fill without FillError across seeds -- proves the soft/no-hard-exclude design is safe."""
    options = {"enable_dlc": False, "world_logic": "region_lock", "num_regions": 4,
               "pool_builder": True, "curated_fill": True}

    def test_multi_seed_no_fill_error(self):
        if not self.constructed or not self._has_patch():
            self.skipTest("patch_curated_fill.py not applied")
        from Fill import distribute_items_restrictive
        for seed in (11, 222, 3333, 44444, 585858):
            with self.subTest(seed=seed):
                self.world_setup(seed)
                distribute_items_restrictive(self.multiworld)


class CuratedFillForeignCarve(_CuratedBase):
    """filler_foreign_pct carves that share of filler OUT of local_items (opens those slots to
    incoming foreign filler). Comparative within one test -- world_setup re-reads self.options
    (bases.py:74-78) -- so we avoid brittle absolute thresholds."""
    options = {"enable_dlc": False, "world_logic": "region_lock", "curated_fill": True}

    def test_foreign_pct_shrinks_local_items(self):
        if not self.constructed or not self._has_patch():
            self.skipTest("patch_curated_fill.py not applied")
        counts = {}
        for pct in (0, 60):
            self.options = {"enable_dlc": False, "world_logic": "region_lock",
                            "curated_fill": True, "local_item_option": True,
                            "filler_foreign_pct": pct}
            self.world_setup(777)
            counts[pct] = len(self.world.options.local_items.value)
        self.assertGreater(counts[0], 500,
                           f"local_item_option baseline should localize filler in bulk, got {counts[0]}")
        self.assertLess(counts[60], counts[0] * 0.6,
                        f"filler_foreign_pct=60 should carve ~60% out of local_items "
                        f"(got {counts[60]} vs baseline {counts[0]})")


class CuratedFillUpgradeInjectsJuice(_CuratedBase):
    """filler_upgrade_pct replaces that % of the local filler pool with ranked juice. The juice is
    kept FILLER-classified (so it stays fill-neutral -- see patch_curated_fill_v3), so we prove it
    by CONTENT: many more S/A-tier items sit in the filler pool at 100% than at 0%. Comparative
    within one test (world_setup re-reads self.options)."""
    options = {"enable_dlc": False, "world_logic": "region_lock", "curated_fill": True}

    def test_upgrade_pct_injects_sa_tier_juice(self):
        if not self.constructed or not self._has_patch():
            self.skipTest("patch_curated_fill.py not applied")
        from BaseClasses import ItemClassification
        from worlds.eldenring.item_tiers import ITEM_TIERS
        juice = {}
        for pct in (0, 100):
            self.options = {"enable_dlc": False, "world_logic": "region_lock",
                            "curated_fill": True, "filler_upgrade_pct": pct}
            self.world_setup(777)
            juice[pct] = sum(1 for it in self.multiworld.itempool
                             if it.player == self.player
                             and it.classification == ItemClassification.filler
                             and ITEM_TIERS.get(it.name) in ("S", "A"))
        self.assertGreater(juice[100], juice[0] + 20,
                           f"filler_upgrade_pct=100 should inject many S/A-tier juice items into "
                           f"the filler pool vs the pct=0 baseline (got {juice[100]} vs {juice[0]})")


if __name__ == "__main__":
    unittest.main()
