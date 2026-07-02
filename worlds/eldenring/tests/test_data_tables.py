"""Standalone cross-consistency invariants for the pure data tables (no Archipelago import).

Same pattern as test_merchant_bells.py: importlib-load the pure modules, regex-parse the heavy
ones (items.py), so this runs in any environment in milliseconds. These tables are only exercised
indirectly by the gen/fuzz gates; a typo'd region name or aliased flag survives generation and
degrades silently in-game -- exactly the class SWEEP-SILENT-DEGRADES hunts. Guards:

  * REGION_MAP_ITEM / REGION_LOCK_ITEM / REGIONS key alignment (Limgrave = documented de-hub extra)
  * area_id ranges well-formed AND disjoint across regions (an overlap double-kicks)
  * lockOpenFlags unique, in the allocated band, and disjoint from the CLIENT's dedicated flags
    (76970 kick, 76996 deathlink-kill -- see test_open_flags_disjoint_from_client_flags)
  * ITEM_TIERS keys spell real item names; grades within S/A/B/C/D/F
  * every lock item name (grace_data + spine) exists in items.py
  * SPINE: unique step names, step regions partition (no region in two steps), step-index
    constants in range

Run: python -m pytest worlds/eldenring/tests/test_data_tables.py   (or unittest)
"""
import importlib.util
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ELDEN = os.path.dirname(HERE)


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ELDEN, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mrd = _load("map_region_data")
gd = _load("grace_data")
tiers = _load("item_tiers")
spine = _load("region_spine")

_ITEMS_SRC = open(os.path.join(ELDEN, "items.py"), encoding="utf-8", errors="replace").read()
ITEM_NAMES = set(re.findall(r'ERItemData\(\s*"((?:[^"\\]|\\.)*)"', _ITEMS_SRC))

# Client-side dedicated event flags (mirrored constants; sources noted so drift is findable):
#   76970 = region-kick flag (eldenring-archipelago/src/region.rs)
#   76996 = DEATHLINK_KILL_FLAG (er-logic/src/hook.rs, baked common.emevd event 6996)
CLIENT_DEDICATED_FLAGS = {76970, 76996}


class TestRegionTables(unittest.TestCase):
    def test_region_map_item_keys_exist_in_regions(self):
        self.assertFalse(set(mrd.REGION_MAP_ITEM) - set(mrd.REGIONS))

    def test_lock_regions_align_with_regions_table(self):
        self.assertFalse(
            set(gd.REGION_LOCK_ITEM) - set(mrd.REGIONS),
            "grace_data lock region missing from map_region_data.REGIONS")
        extras = set(mrd.REGIONS) - set(gd.REGION_LOCK_ITEM)
        self.assertLessEqual(
            extras, {"Limgrave"},
            "REGIONS entries with no lock item (only the de-hub Limgrave special is allowed): %s"
            % sorted(extras))

    def test_area_id_ranges_well_formed(self):
        for region, d in mrd.REGIONS.items():
            for lo, hi in d["area_ids"]:
                self.assertLessEqual(lo, hi, "%s: inverted range (%d, %d)" % (region, lo, hi))
                self.assertGreaterEqual(lo, 0, "%s: negative area id" % region)

    def test_area_id_ranges_disjoint_across_regions(self):
        spans = [(r, lo, hi) for r, d in mrd.REGIONS.items() for lo, hi in d["area_ids"]]
        clashes = [(a, b) for i, a in enumerate(spans) for b in spans[i + 1:]
                   if a[0] != b[0] and not (a[2] < b[1] or b[2] < a[1])]
        self.assertFalse(
            clashes, "area_id ranges overlap across regions (double-kick): %s" % clashes)


class TestOpenFlags(unittest.TestCase):
    def _slot_data(self):
        return mrd.build_region_lock_slot_data(gd.REGION_LOCK_ITEM)

    def test_open_flags_unique(self):
        flags = list(self._slot_data()["lockOpenFlags"].values())
        self.assertEqual(len(flags), len(set(flags)),
                         "two locks alias one open flag: %s" % sorted(flags))

    def test_open_flags_within_allocated_band(self):
        # 76971+ is the probed-valid group (er-event-flag-validity); an invented id no-ops in-game.
        for lock, flag in self._slot_data()["lockOpenFlags"].items():
            self.assertGreaterEqual(flag, mrd.OPEN_FLAG_BASE, lock)
            self.assertLess(flag, mrd.OPEN_FLAG_BASE + 40, "%s flag %d beyond probed band" % (lock, flag))

    @unittest.expectedFailure
    def test_open_flags_disjoint_from_client_flags(self):
        """KNOWN LIVE COLLISION (found 2026-07-02 writing this test): the 27-lock band
        76971..76997 contains 76996 = DEATHLINK_KILL_FLAG. Today that lands on Stormveil Lock:
        every incoming DeathLink best-effort-sets 76996 (client deathlink.rs drive_kill), which
        silently marks Stormveil OPEN for the rest of the save -- a region-lock bypass; and on
        bake-compat setups, RECEIVING Stormveil Lock force-kills the player (emevd event 6996).
        Fix = re-band or re-pick the kill flag (needs a flag-validity probe); flip this to a hard
        assert when done."""
        colliding = {lock: flag for lock, flag in self._slot_data()["lockOpenFlags"].items()
                     if flag in CLIENT_DEDICATED_FLAGS}
        self.assertFalse(
            colliding,
            "lock open flags alias client dedicated flags (kick/deathlink): %s" % colliding)


class TestItemNameSpelling(unittest.TestCase):
    def test_regex_extracted_a_plausible_item_table(self):
        # Guard the guard: if items.py's shape changes and the regex goes blind, fail loudly
        # instead of vacuously passing the subset checks below.
        self.assertGreater(len(ITEM_NAMES), 2000, "items.py regex extraction broke")

    def test_item_tiers_spell_real_item_names(self):
        missing = sorted(k for k in tiers.ITEM_TIERS if k not in ITEM_NAMES)
        self.assertFalse(missing[:20], "%d ITEM_TIERS keys match no item: %s" % (len(missing), missing[:20]))

    def test_item_tier_grades_valid(self):
        self.assertLessEqual(set(tiers.ITEM_TIERS.values()), set("SABCDF"))

    def test_lock_items_exist(self):
        locks = set(gd.REGION_LOCK_ITEM.values())
        for step in spine.SPINE:
            locks |= set(step["locks"])
        missing = sorted(locks - ITEM_NAMES)
        self.assertFalse(missing, "lock items with no items.py entry: %s" % missing)


class TestSpine(unittest.TestCase):
    def test_step_names_unique(self):
        names = [s["name"] for s in spine.SPINE]
        self.assertEqual(len(names), len(set(names)))

    def test_step_regions_partition(self):
        seen = {}
        for step in spine.SPINE:
            for region in step["regions"]:
                self.assertNotIn(
                    region, seen,
                    "region '%s' in two spine steps: %s / %s" % (region, seen.get(region), step["name"]))
                seen[region] = step["name"]

    def test_step_index_constants_in_range(self):
        n = len(spine.SPINE)
        self.assertTrue(all(1 <= i <= n for i in spine.RUNE_STEPS), spine.RUNE_STEPS)
        self.assertTrue(1 <= spine.ALTUS_STEP <= n)
        self.assertEqual(spine.MAX_PRE_LEYNDELL_RUNES, len(spine.RUNE_STEPS))


if __name__ == "__main__":
    unittest.main()
