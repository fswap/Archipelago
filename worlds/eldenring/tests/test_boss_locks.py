"""BOSS_LOCKS_PATCH invariants (SPEC-boss-locks.md v0.1) -- same no-Archipelago-import
pattern as test_data_tables.py: importlib-load region_spine, regex-parse items.py.

  * every BOSS_LOCKS value is a real items.py entry declared lock=True
  * BOSS_LOCKS keys == {group[0] for LEGACY_SWEEP_GROUPS} | {SHADED_CASTLE_GROUP_KEY} (no drift)
  * BOSS_LOCK_DLC_KEYS is a subset of the keys
  * lock names unique (one lock per group); BOSS_LOCK_GROUP_REGIONS covers every key
  * the Stormveil group reuses the pre-existing "Godrick Lock" (fold-in, not a duplicate)

Run: python -m pytest worlds/eldenring/tests/test_boss_locks.py   (or unittest)
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


spine = _load("region_spine")

_ITEMS_SRC = open(os.path.join(ELDEN, "items.py"), encoding="utf-8", errors="replace").read()
_ITEM_LOCK_FLAGS = {}
for _m in re.finditer(
        r'ERItemData\(\s*"((?:[^"\\]|\\.)*)"[^\n]*?lock\s*=\s*(True|False)', _ITEMS_SRC):
    _ITEM_LOCK_FLAGS[_m.group(1)] = (_m.group(2) == "True")


class TestBossLocks(unittest.TestCase):
    def test_every_boss_lock_is_a_lock_item(self):
        for key, name in spine.BOSS_LOCKS.items():
            self.assertIn(name, _ITEM_LOCK_FLAGS, "%s: %r missing from items.py" % (key, name))
            self.assertTrue(_ITEM_LOCK_FLAGS[name], "%s: %r must be lock=True" % (key, name))

    def test_keys_match_sweep_groups_exactly(self):
        want = {g[0] for g in spine.LEGACY_SWEEP_GROUPS} | {spine.SHADED_CASTLE_GROUP_KEY, spine.CASTLE_MORNE_GROUP_KEY}
        self.assertEqual(set(spine.BOSS_LOCKS), want)

    def test_dlc_keys_subset(self):
        self.assertLessEqual(spine.BOSS_LOCK_DLC_KEYS, set(spine.BOSS_LOCKS))

    def test_lock_names_unique(self):
        names = list(spine.BOSS_LOCKS.values())
        self.assertEqual(len(names), len(set(names)))

    def test_group_regions_cover_every_key(self):
        self.assertEqual(set(spine.BOSS_LOCK_GROUP_REGIONS), set(spine.BOSS_LOCKS))
        for key, regions in spine.BOSS_LOCK_GROUP_REGIONS.items():
            self.assertTrue(regions, "%s: empty region list" % key)

    def test_stormveil_reuses_godrick_lock(self):
        self.assertEqual(spine.BOSS_LOCKS["Stormveil Start"], "Godrick Lock")


if __name__ == "__main__":
    unittest.main()
