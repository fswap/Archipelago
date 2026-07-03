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

# name -> lock=<bool literal> kwarg value, regex-extracted the same way ITEM_NAMES is (avoids
# a full items.py import, matching this file's no-Archipelago-import design). Entries missing
# an explicit lock= kwarg are absent from this dict (treated as "no lock flag" by callers).
_ITEM_LOCK_FLAGS = {}
for _m in re.finditer(
        r'ERItemData\(\s*"((?:[^"\\]|\\.)*)"[^\n]*?lock\s*=\s*(True|False)', _ITEMS_SRC):
    _ITEM_LOCK_FLAGS[_m.group(1)] = (_m.group(2) == "True")


def _item_lock_flag(name):
    """True/False if items.py declares an explicit lock= kwarg for `name`, else None."""
    return _ITEM_LOCK_FLAGS.get(name)


_LOCATIONS_MODULE = None


def _load_locations_module():
    """locations.py imports BaseClasses (a real AP module) at top level, so it can't use the
    lightweight `_load()` helper above (which assumes standalone-importable pure data). Import
    it the normal way, added to sys.path, and cache -- if BaseClasses is unavailable (this
    file's docstring promises "no Archipelago import", but SPINE-region-key coverage needs the
    real table so we degrade gracefully instead of hard-failing the whole module)."""
    global _LOCATIONS_MODULE
    if _LOCATIONS_MODULE is not None:
        return _LOCATIONS_MODULE
    import sys
    ap_root = os.path.abspath(os.path.join(ELDEN, "..", ".."))
    added = ap_root not in sys.path
    if added:
        sys.path.insert(0, ap_root)
    try:
        _LOCATIONS_MODULE = _load("locations")
    except Exception as exc:  # pragma: no cover - environment-dependent fallback
        raise unittest.SkipTest("locations.py could not be imported standalone: %s" % exc)
    finally:
        if added:
            sys.path.remove(ap_root)
    return _LOCATIONS_MODULE

# Client-side dedicated event flags (mirrored constants; sources noted so drift is findable):
#   76970 = region-kick flag (eldenring-archipelago/src/region.rs)
#   76996 = DEATHLINK_KILL_FLAG (er-logic/src/hook.rs, baked common.emevd event 6996)
#   76968/76969 = random-start freebie flags; 76966 = Morne; 76967 = Godrick
# NOTE: this is the CLIENT-reserved subset only -- deliberately NOT
# map_region_data.RESERVED_OPEN_FLAGS wholesale, because that set ALSO unions in the
# HAND_PICKED lock flags themselves (76965 MT / 76961 SF / 76964 Haligtree)
# so the band walker skips them; asserting THOSE locks' own flags are "disjoint from
# themselves" would be a tautological false-positive. This set stays the true client/runtime
# reserved list (region-spine surgery SS6, closing the 76996 collision for real).
CLIENT_DEDICATED_FLAGS = {76970, 76996, 76968, 76969, 76966, 76967}


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
        # HAND_PICKED locks (region-spine surgery SS6: Mountaintops/Snowfield/Haligtree)
        # are DELIBERATELY below OPEN_FLAG_BASE -- they reuse pre-existing natural-key apparatus
        # flags -- so they are exempted from the lower-bound check but still must clear the
        # probed-valid ceiling (covered separately by test_all_flags_within_probed_band in
        # TestLockRoster, which has no band-vs-hand-picked distinction to make).
        hand_picked = set(mrd.HAND_PICKED)
        for lock, flag in self._slot_data()["lockOpenFlags"].items():
            if lock in hand_picked:
                continue
            self.assertGreaterEqual(flag, mrd.OPEN_FLAG_BASE, lock)
            self.assertLess(flag, mrd.OPEN_FLAG_BASE + 40, "%s flag %d beyond probed band" % (lock, flag))

    def test_open_flags_disjoint_from_client_flags(self):
        """CLOSED 2026-07 (region-spine surgery SS6): the open-flag band allocator now skips
        every reserved runtime flag (map_region_data.RESERVED_OPEN_FLAGS: 76996 deathlink-kill,
        76970 KICK, 76968/76969 random-start, 76966 Morne, 76967 Godrick, plus the HAND_PICKED
        values) instead of walking a blind alphabetical band. What was a live collision
        (Stormveil Lock aliasing 76996 -- every incoming DeathLink silently marked Stormveil
        OPEN, a region-lock bypass) is now a hard invariant instead of an expectedFailure."""
        colliding = {lock: flag for lock, flag in self._slot_data()["lockOpenFlags"].items()
                     if flag in CLIENT_DEDICATED_FLAGS}
        self.assertFalse(
            colliding,
            "lock open flags alias client dedicated flags (kick/deathlink/reserved): %s" % colliding)


class TestLockRoster(unittest.TestCase):
    """Region-spine surgery (SPEC-region-spine-surgery.md SS2/SS6) lock-roster invariants:
    renames, retirements, additions, and the hand-picked open-flag contract."""

    # Pure renames (SS3.3): the OLD directional names must no longer exist as item names at
    # all -- these are renames, not aliases-with-a-dead-flag like Dragonbarrow/SW below.
    RETIRED_BY_RENAME = ("South East Underground Lock", "North Underground Lock")

    # Retired-but-present (SS2, Volcano Lock pattern): item stays defined, lock=False, pulled
    # from REGION_LOCK_ITEM coverage.
    RETIRED_LOCK_FALSE = ("Dragonbarrow Lock", "South West Underground Lock")

    # First-class lock=True items this surgery adds or promotes to always-on.
    ALWAYS_ON_ADDED_OR_PROMOTED = (
        "Mountaintops Lock", "Snowfield Lock", "Haligtree Lock", "Limgrave Lock",
        "Nokron Lock", "Nokstella Lock",
    )

    HAND_PICKED_CONTRACT = {
        "Mountaintops Lock": 76965,
        "Snowfield Lock": 76961,
        "Haligtree Lock": 76964,
    }

    def test_renamed_locks_absent_by_old_name(self):
        for old_name in self.RETIRED_BY_RENAME:
            self.assertNotIn(
                old_name, ITEM_NAMES,
                "%r should no longer exist as an item name (renamed, not aliased)" % old_name)

    def test_renamed_locks_present_by_new_name(self):
        for new_name in ("Nokron Lock", "Nokstella Lock"):
            self.assertIn(new_name, ITEM_NAMES, "%r missing from items.py" % new_name)
            self.assertTrue(
                _item_lock_flag(new_name),
                "%r must be lock=True" % new_name)

    def test_retired_locks_present_but_lock_false(self):
        for name in self.RETIRED_LOCK_FALSE:
            self.assertIn(name, ITEM_NAMES, "%r should still be defined (retired, not deleted)" % name)
            flag = _item_lock_flag(name)
            self.assertIsNotNone(flag, "%r item entry missing a lock= kwarg" % name)
            self.assertFalse(flag, "%r must be lock=False (retired)" % name)

    def test_always_on_locks_present_and_locking(self):
        for name in self.ALWAYS_ON_ADDED_OR_PROMOTED:
            self.assertIn(name, ITEM_NAMES, "%r missing from items.py" % name)
            self.assertTrue(_item_lock_flag(name), "%r must be lock=True" % name)

    def test_hand_picked_open_flags_match_contract(self):
        self.assertEqual(dict(mrd.HAND_PICKED), self.HAND_PICKED_CONTRACT)

    def test_all_flags_within_probed_band(self):
        # Every allocated open flag (band-walked or hand-picked) must stay <= 76997 (the
        # probe-confirmed valid group upper edge -- er-event-flag-validity).
        for lock, flag in self._slot_data()["lockOpenFlags"].items():
            self.assertLessEqual(flag, 76997, "%s flag %d beyond the probed-valid group" % (lock, flag))

    def _slot_data(self):
        return mrd.build_region_lock_slot_data(gd.REGION_LOCK_ITEM)


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

    def test_spine_has_twelve_steps(self):
        # Region-spine surgery (SPEC-region-spine-surgery.md SS5): Limgrave (1) + Weeping (2)
        # + Stormveil (3) + Liurnia (4) + Caelid (5, Dragonbarrow folded in) + Altus (6) +
        # Mt. Gelmir (7) + Siofra/Nokron (8) + Ainsel/Nokstella (9) + Mountaintops (10) +
        # Consecrated Snowfield (11) + Haligtree (12).
        self.assertEqual(len(spine.SPINE), 12, "expected the 12-step post-surgery spine")

    def test_rune_steps_contract(self):
        self.assertEqual(spine.RUNE_STEPS, {3, 4, 5, 7}, "Godrick/Rennala/Radahn/Rykard steps")

    def test_every_spine_lock_exists_and_locks(self):
        for step in spine.SPINE:
            for lock_name in step["locks"]:
                self.assertIn(
                    lock_name, ITEM_NAMES,
                    "SPINE step %r references %r, missing from items.py"
                    % (step["name"], lock_name))
                self.assertTrue(
                    _item_lock_flag(lock_name),
                    "SPINE step %r lock %r must be lock=True" % (step["name"], lock_name))

    def test_every_spine_region_is_a_known_location_table_key(self):
        loc = _load_locations_module()
        location_keys = set(loc.location_tables.keys())
        for step in spine.SPINE:
            for region in step["regions"]:
                self.assertIn(
                    region, location_keys,
                    "SPINE step %r region %r not a locations.py location_tables key"
                    % (step["name"], region))


if __name__ == "__main__":
    unittest.main()
