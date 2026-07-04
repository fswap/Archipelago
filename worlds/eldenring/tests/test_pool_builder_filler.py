"""pool_builder injects its juice as FILLER (patch_pool_builder_filler_class).

Alaric's model: pool_builder is a filler-quality upgrade, so everything it injects should be
classified FILLER regardless of native class (it's upgraded trash, not a useful/progression logic
item). These tests pin that, plus that the reclassification doesn't break fill.

run_default_tests is off: region_lock is retry-prone under a single-shot distribute, so we test
fill explicitly on chosen seeds instead of the random-seed auto test_fill.

Run (Windows, from the Archipelago root):
    python worlds/eldenring/tests/run_tests.py pool_builder_filler
"""
import unittest
from test.bases import WorldTestBase


class _PBBase(WorldTestBase):
    game = "EldenRing"
    auto_construct = True
    run_default_tests = False

    def _mine(self):
        return [i for i in self.multiworld.itempool if i.player == self.player]


class PoolBuilderInjectsJuiceAsFiller(_PBBase):
    """With pool_builder on, the S/A-tier juice it injects must appear in the pool classified
    FILLER (natively those items are useful/progression). Comparative pool_builder off vs on so we
    don't depend on absolute magnitudes."""
    options = {"enable_dlc": False, "world_logic": "region_lock", "pool_builder": True,
               "junk_retention": 0}

    def test_sa_juice_is_filler(self):
        from BaseClasses import ItemClassification
        from worlds.eldenring.item_tiers import ITEM_TIERS
        sa_filler = {}
        for pb in (False, True):
            self.options = {"enable_dlc": False, "world_logic": "region_lock",
                            "pool_builder": pb, "junk_retention": 0}
            self.world_setup(777)
            sa_filler[pb] = sum(1 for it in self._mine()
                                if it.classification == ItemClassification.filler
                                and ITEM_TIERS.get(it.name) in ("S", "A"))
        self.assertGreater(
            sa_filler[True], sa_filler[False] + 10,
            f"pool_builder should inject S/A-tier juice AS FILLER, but the filler-classified S/A "
            f"count barely moved (on={sa_filler[True]} vs off={sa_filler[False]})")

    def test_no_useful_or_progression_leaks_from_juice(self):
        """Sanity: turning pool_builder on must not INCREASE the count of useful+progression items
        in the pool -- its juice is filler now, so it should not swell the non-filler classes."""
        from BaseClasses import ItemClassification
        nonfiller = {}
        for pb in (False, True):
            self.options = {"enable_dlc": False, "world_logic": "region_lock",
                            "pool_builder": pb, "junk_retention": 0}
            self.world_setup(777)
            nonfiller[pb] = sum(1 for it in self._mine()
                                if it.classification != ItemClassification.filler)
        # allow a little slack for incidental option interactions, but pool_builder must not
        # balloon the non-filler pool (that was the old useful-classified behavior).
        self.assertLessEqual(
            nonfiller[True], nonfiller[False] + 5,
            f"pool_builder juice should be filler, but non-filler count grew "
            f"(on={nonfiller[True]} vs off={nonfiller[False]})")


class PoolBuilderFillerStillFills(_PBBase):
    """Re-classing pool_builder juice to filler must not break fill on the pool_builder config."""
    options = {"enable_dlc": False, "world_logic": "region_lock", "pool_builder": True,
               "junk_retention": 0}

    def test_fill_succeeds_multi_seed(self):
        from Fill import distribute_items_restrictive
        for seed in (11, 222, 3333, 44444):
            with self.subTest(seed=seed):
                self.world_setup(seed)
                distribute_items_restrictive(self.multiworld)


class PoolBuilderStonesAndLocality(_PBBase):
    """The ladder's elastic backfill now includes a smithing-stone bucket, and pool_builder's juice
    is added to local_items (kept at home)."""
    options = {"enable_dlc": False, "world_logic": "region_lock", "pool_builder": True,
               "junk_retention": 0}

    def test_ladder_includes_stones(self):
        # force a large budget so the elastic backfill (not just the finite uniques) runs and the
        # stone bucket is exercised regardless of how big the current scrub is.
        self.world_setup(777)
        names = self.world._uplift_inject_names(5000)
        stones = [n for n in names if "Smithing Stone" in n]
        self.assertGreater(
            len(stones), 0,
            "uplift elastic backfill should include smithing stones (new stone bucket)")

    def test_pool_builder_juice_localized(self):
        from worlds.eldenring.item_tiers import ITEM_TIERS
        sa_local = {}
        for pb in (False, True):
            self.options = {"enable_dlc": False, "world_logic": "region_lock",
                            "pool_builder": pb, "junk_retention": 0}
            self.world_setup(777)
            sa_local[pb] = sum(1 for n in self.world.options.local_items.value
                               if ITEM_TIERS.get(n) in ("S", "A"))
        self.assertGreater(
            sa_local[True], sa_local[False],
            f"pool_builder should localize its S/A gear juice via local_items "
            f"(on={sa_local[True]} vs off={sa_local[False]})")


class PoolBuilderIntensityFills(_PBBase):
    """high + max intensity must still fill. Broad goods scrub risks depleting the plain goods
    shop slots need; the stone-heavy juice should keep it safe, but pin it on chosen seeds."""
    options = {"enable_dlc": False, "world_logic": "region_lock", "pool_builder": True,
               "junk_retention": 0}

    def _fill_at(self, level, seeds):
        from Fill import distribute_items_restrictive
        for seed in seeds:
            with self.subTest(level=level, seed=seed):
                self.options = {"enable_dlc": False, "world_logic": "region_lock",
                                "pool_builder": True, "junk_retention": 0,
                                "pool_builder_intensity": level}
                self.world_setup(seed)
                distribute_items_restrictive(self.multiworld)

    def test_high_fills(self):
        self._fill_at("high", (11, 222, 3333))

    def test_max_fills(self):
        self._fill_at("max", (11, 222, 3333))


class PoolBuilderIntensityScrubsMore(_PBBase):
    """Higher intensity = bigger scrub budget = more elastic stone juice injected into the pool."""
    options = {"enable_dlc": False, "world_logic": "region_lock", "pool_builder": True,
               "junk_retention": 0}

    def test_max_injects_more_stones_than_normal(self):
        from BaseClasses import ItemClassification
        stones = {}
        for level in ("normal", "max"):
            self.options = {"enable_dlc": False, "world_logic": "region_lock",
                            "pool_builder": True, "junk_retention": 0,
                            "pool_builder_intensity": level}
            self.world_setup(777)
            stones[level] = sum(1 for it in self._mine()
                                if "Smithing Stone" in it.name
                                and it.classification == ItemClassification.filler)
        self.assertGreater(
            stones["max"], stones["normal"],
            f"max intensity should inject more stone juice than normal "
            f"(max={stones['max']} vs normal={stones['normal']})")

    def test_scrub_never_defers_spells(self):
        """Direct test of the fix: the pool_builder goods scrub must NEVER defer a spell (spells
        are filler GOODS but not trash) at ANY intensity. Tests the predicate itself, isolated
        from downstream pool RNG (max intensity reshuffles the pool, which moves the raw spell
        count around -- but that's backfill noise, not the scrub eating spells)."""
        from worlds.eldenring import _is_spell_code
        from BaseClasses import ItemClassification
        for level in ("normal", "high", "max"):
            self.options = {"enable_dlc": False, "world_logic": "region_lock",
                            "pool_builder": True, "junk_retention": 0,
                            "pool_builder_intensity": level}
            self.world_setup(777)
            spell_names = [n for n, d in self.world.item_table.items()
                           if _is_spell_code(getattr(d, "er_code", None))
                           and d.classification == ItemClassification.filler][:25]
            self.assertTrue(spell_names, "no filler spells found to test")
            offenders = [n for n in spell_names if self.world._pool_builder_defer_native(n)]
            self.assertEqual(
                offenders, [],
                f"intensity={level}: goods scrub must never defer spells, got {offenders[:5]}")


if __name__ == "__main__":
    unittest.main()
