"""Regression gen-test for the local_item_option loop in generate_early (break-in-match bug,
fixed 2026-07-01 by patch_local_items_fix.py).

local_item_option (default ON) is meant to add EVERY non-progression/non-useful item whose
category is NOT listed in exclude_local_item_only to options.local_items, keeping filler in
this slot. The old code used `break` inside a match/case; `break` inside `match` breaks the
enclosing FOR loop, so at most ONE item was ever localized. These tests pin the fixed shape:

- default options: exclude_local_item_only defaults to [Weapon, Armor, Accessory, AshofWar],
  so only GOODS are localized -> local_items must be BIG. local_items holds distinct
  NAMES, not pool instances: 947 observed (2026-07-01), so the bound is >500.
- local_item_option OFF: the loop is skipped entirely -> local_items stays empty.
- exclude_local_item_only listing all five categories (incl. Goods): nothing left to
  localize -> strictly fewer entries than the default case (<100 here vs >1000 there).
- exclude_local_item_only = []: all five categories localized -> the largest set.

These classes all run {world_logic: region_lock, enable_dlc: false} under the DEFAULT (full)
accessibility. That combo used to die in AP's priority fill (FillError at 'Priority Retry');
the root cause was rule_builder cache poisoning of the CanReach* reach rules, fixed 2026-07-01
by patch_priority_fill_fix.py (uncached ERCanReach* subclasses in rules_predicates.py; the
patch_local_items_fix2 minimal-accessibility coercion was removed as falsified).
test_accessibility_not_coerced pins that the combo is no longer coerced, and
test_multi_seed_fill re-runs the fill on the seeds that used to FillError.

Run (Windows, from the Archipelago root):  python worlds/eldenring/tests/run_tests.py local_items
"""
import unittest
from test.bases import WorldTestBase


class _LocalItemsBase(WorldTestBase):
    game = "EldenRing"
    auto_construct = True
    options = {"enable_dlc": False, "world_logic": "region_lock", "num_regions": 0}

    def _local_items(self):
        return self.world.options.local_items.value

    def test_accessibility_not_coerced(self):
        """region_lock + enable_dlc:false must keep the player's accessibility.

        patch_local_items_fix2 used to coerce this combo to minimal because AP's priority
        fill starved under full accessibility. The real cause was rule_builder cache
        poisoning (CanReach* rules cached False with no invalidation path once the target's
        parent region was already reachable), fixed by patch_priority_fill_fix (2026-07-01).
        The combo now generates under the DEFAULT (full) accessibility, so generate_early
        must NOT touch it.
        """
        if not self.constructed:
            return
        acc = self.world.options.accessibility
        self.assertNotEqual(acc.value, acc.option_minimal,
                            "region_lock+dlc-off must no longer be coerced to minimal "
                            "accessibility (root cause fixed by patch_priority_fill_fix)")


class LocalItemsOnDefault(_LocalItemsBase):
    """local_item_option defaults ON; the default excludes leave only GOODS to localize."""
    options = {"enable_dlc": False, "world_logic": "region_lock", "num_regions": 0}

    def test_goods_localized_in_bulk(self):
        n = len(self._local_items())
        # Observed on Windows 2026-07-01 (first post-fix run): 947 distinct filler
        # GOODS names. local_items is a set of NAMES, not pool instances, so the old
        # ~3700 (instance-count) guess was wrong. >500 still pins 'bulk' against the
        # old break-in-match bug's cap of 1, with headroom for pool-curation churn.
        # (patch_local_items_fix2)
        self.assertGreater(n, 500,
                           f"expected bulk localized GOODS names with local_item_option"
                           f" ON, got {n} (the old break-in-match bug capped this at 1;"
                           f" observed 947 on 2026-07-01)")


class LocalItemsOff(_LocalItemsBase):
    """local_item_option OFF: the localizing loop must not run at all."""
    options = {"enable_dlc": False, "world_logic": "region_lock", "local_item_option": False, "num_regions": 0}

    def test_local_items_stay_empty(self):
        n = len(self._local_items())
        self.assertLess(n, 50,
                        f"local_item_option OFF should leave local_items empty, got {n}")


class LocalItemsExcludeGoods(_LocalItemsBase):
    """Excluding Goods on top of the default four categories leaves nothing to localize --
    strictly fewer entries than LocalItemsOnDefault (<100 here vs >1000 there)."""
    options = {"enable_dlc": False, "world_logic": "region_lock", "num_regions": 0,
               "exclude_local_item_only": ["Weapon", "Armor", "Accessory", "AshofWar", "Goods"]}

    def test_goods_exclusion_shrinks_local_set(self):
        n = len(self._local_items())
        self.assertLess(n, 100,
                        f"excluding all five categories (incl. Goods) should localize "
                        f"(almost) nothing, got {n}")

    def test_multi_seed_fill(self):
        """Regression sweep for the priority-fill starvation (patch_priority_fill_fix).

        Before the rule-cache fix these seeds (incl. the original repro seed
        85920353982860255231) died at Fill.py 'Priority Retry' with 'No more spots to
        place N items' under this option class -- and a seed that did fill could
        silently violate full accessibility. Each seed is a full gen (~0.5s).
        """
        if not self.constructed:
            return
        from Fill import distribute_items_restrictive
        for seed in (85920353982860255231, 11, 222, 3333, 44444):
            with self.subTest(seed=seed):
                self.world_setup(seed)
                distribute_items_restrictive(self.multiworld)


class LocalItemsNoExclude(_LocalItemsBase):
    """Excluding nothing localizes all five categories -- the largest possible set."""
    options = {"enable_dlc": False, "world_logic": "region_lock", "exclude_local_item_only": [], "num_regions": 0}

    def test_all_categories_localized(self):
        n = len(self._local_items())
        self.assertGreater(n, 1000,
                           f"with no category exclusions every filler item should be "
                           f"localized, got {n}")


if __name__ == "__main__":
    unittest.main()
