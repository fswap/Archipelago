"""Slot-expanding capped uniques must not exceed their GAME cap in the item pool.

Talisman Pouch and Memory Stone are hard-capped by Elden Ring (3 pouches -> 4 talisman slots;
8 memory stones). Force-granting past the cap crashes the game natively -- playtest 2026-07-03:
buying a Talisman Pouch from a shop crashed ER, and the seed's pool held 4 pouches (> cap 3).
curation.UPLIFT_UNIQUE_CAPS declares the safe caps, but pool_builder's uplift injects these
uniques ON TOP of the base pool's vanilla copies without subtracting them, so the total can blow
past the cap. This pins that the FINAL pool honors the caps under the loot-shaping config that
reproduced the crash.
"""
from collections import Counter

from test.bases import WorldTestBase
from worlds.eldenring.curation import UPLIFT_UNIQUE_CAPS


class CappedUniquesPoolBuilder(WorldTestBase):
    game = "EldenRing"
    # The loot-shaping config from the playtest that crashed (pool_builder is the injector;
    # dlc_gear_curation + enable_dlc match the example yaml's DLC-loot setup).
    options = {
        "enable_dlc": True,
        "world_logic": "region_lock",
        "pool_builder": True,
        "dlc_gear_curation": True,
    }

    def test_capped_uniques_within_game_cap(self):
        pool = Counter(i.name for i in self.multiworld.itempool if i.player == self.player)
        over = {name: {"pool": pool[name], "cap": cap}
                for name, cap in UPLIFT_UNIQUE_CAPS.items() if pool[name] > cap}
        self.assertEqual(
            over, {},
            f"capped slot-expander(s) exceed the game cap {over} -- granting past the cap "
            f"crashes ER (pool_builder uplift injects on top of base copies without subtracting)")
