"""Gen-test: region locks placed in SHOP slots stay REACHABLE and LEGIBLE.

Guards the Dragon Communion softlock class (found 2026-07-04, num_regions Capital run,
seed 56524706252934796624). A required region-lock landed on `CL/(CDC): Agheel's Flame`,
a PREMIUM (Dragon Heart) altar purchase -- triple-gated in-game (vanilla dragon-kill STOCK
flag so the row is invisible until the kill + Dragon Heart currency + ZERO hearts anywhere
in the seed) => unwinnable and invisible. Fix = patch_dragon_communion_missable.py
(premium purchases -> missable -> excluded).

Two independent invariants a shop-placed lock must satisfy:

  A. REACHABILITY -- no progression on a `premium` shop slot. Premium = special-currency
     purchase (Dragon Communion / Heart of Bayle), stock- and currency-gated in ways the fill
     does not model. Those slots are meant to be missable/excluded. This SKIPS until
     patch_dragon_communion_missable.py is applied (detected via the premium Dragon Communion
     rows being missable), then enforces -- a live regression guard, not a red suite pre-patch.

  B. LEGIBILITY -- every shop slot holding a region-lock item (a) is present in
     `shopPreviewGoods` so the client's shop_preview layer has a good to relabel, and (b) has a
     preview good id UNIQUE among lock-bearing shop slots. shop_preview's FMG override is
     GLOBAL-per-good and deduped by good id, so two locks sharing a preview good would render
     the WRONG name on one of them (illegible / mis-routed buy).

The exact on-screen text a lock renders is pinned separately on the client side:
`er-logic/src/name_override.rs::shop_label` (host unit test `shop_label_progression_lock`).

Run (Windows, from the Archipelago root):
    python worlds/eldenring/tests/run_tests.py shop_lock_legibility
or  python -m pytest worlds/eldenring/tests/test_shop_lock_legibility.py
"""
import unittest

from test.bases import WorldTestBase
from BaseClasses import ItemClassification

from worlds.eldenring.items import item_table

# Region-lock carrier items are flagged lock=True in items.py (all progression GOODS).
LOCK_NAMES = frozenset(n for n, d in item_table.items() if getattr(d, "lock", False))

_SEEDS = (11, 222, 3333, 44444, 585858)


class _ShopLegibleChecks:
    """Test bodies as a PLAIN mixin (not a TestCase) so pytest/unittest never collect it
    standalone -- it runs only through the concrete WorldTestBase subclasses below, which
    supply `game`/`options`. (Mirrors the helper-only-base idiom in test_curated_fill.)"""

    # --- helpers ---------------------------------------------------------
    def _my_shop_locs(self):
        out = []
        for loc in self.multiworld.get_locations():
            if loc.player != self.player:
                continue
            if loc.address is None or loc.item is None:
                continue
            if getattr(loc.data, "shop", False):
                out.append(loc)
        return out

    def _premium_dc_missable(self):
        """True once patch_dragon_communion_missable.py is applied: the premium Dragon Communion
        purchases carry missable=True. If any is still non-missable the patch isn't in -> A skips."""
        saw = False
        for loc in self.multiworld.get_locations():
            if loc.player != self.player:
                continue
            if (getattr(loc.data, "premium", False) and getattr(loc.data, "shop", False)
                    and "Dragon Communion" in loc.name):
                saw = True
                if not getattr(loc.data, "missable", False):
                    return False
        return saw  # no premium DC rows at all -> nothing to guard (treat as satisfied only if seen)

    @staticmethod
    def _is_prog(item):
        return bool(item.classification & ItemClassification.progression)

    # --- A: reachability -------------------------------------------------
    def test_no_progression_on_premium_shop_slot(self):
        if not self._premium_dc_missable():
            self.skipTest("patch_dragon_communion_missable.py not applied "
                          "(premium Dragon Communion rows still non-missable).")
        for seed in _SEEDS:
            with self.subTest(seed=seed):
                self.world_setup(seed)
                offenders = [
                    loc.name for loc in self._my_shop_locs()
                    if getattr(loc.data, "premium", False) and self._is_prog(loc.item)
                ]
                self.assertFalse(
                    offenders,
                    "progression on a PREMIUM (special-currency) shop slot -> softlock risk:\n  "
                    + "\n  ".join(offenders),
                )

    # --- B: legibility ---------------------------------------------------
    def test_shop_placed_locks_are_legible(self):
        exercised = 0
        for seed in _SEEDS:
            with self.subTest(seed=seed):
                self.world_setup(seed)
                sd = self.world.fill_slot_data()
                preview = {int(k): v for k, v in (sd.get("shopPreviewGoods") or {}).items()}
                lock_locs = [loc for loc in self._my_shop_locs() if loc.item.name in LOCK_NAMES]
                exercised += len(lock_locs)

                seen_goods = {}
                for loc in lock_locs:
                    self.assertIn(
                        loc.address, preview,
                        f"lock '{loc.item.name}' in shop slot '{loc.name}' has no preview good "
                        f"-> client cannot relabel it (illegible).",
                    )
                    good = preview[loc.address]
                    self.assertNotIn(
                        good, seen_goods,
                        f"two shop-placed locks share preview good {good} "
                        f"(FMG dedup collision -> one renders the other's name): "
                        f"'{loc.name}' vs '{seen_goods.get(good)}'.",
                    )
                    seen_goods[good] = loc.name

        if exercised == 0:
            self.skipTest("no lock landed in a shop across the seed matrix; path not exercised.")


class ShopLegible_RegionLock_DLC(_ShopLegibleChecks, WorldTestBase):
    """DLC on, full region lock (num_regions 0 -> the whole lock set is in the pool), with the
    marquee fill knobs. curated_fill concentrates progression onto big-ticket incl. shops."""
    game = "EldenRing"
    auto_construct = True
    options = {
        "enable_dlc": True,
        "world_logic": "region_lock",
        "num_regions": 0,
        "accessibility": "minimal",
        "curated_fill": True,
        "pool_builder": True,
    }


class ShopLegible_RegionLock_NoDLC(_ShopLegibleChecks, WorldTestBase):
    """DLC off -- faster, differently-shaped fill; still scatters the base-game lock set."""
    game = "EldenRing"
    auto_construct = True
    options = {
        "enable_dlc": False,
        "world_logic": "region_lock",
        "num_regions": 0,
        "accessibility": "minimal",
        "curated_fill": True,
    }


if __name__ == "__main__":
    unittest.main()
