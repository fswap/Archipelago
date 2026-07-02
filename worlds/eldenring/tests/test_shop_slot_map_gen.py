"""Gen-test for SPEC-shop-slot-map.md -- verify slot_data carries shopLocationIds.

With shop_checks ON, fill_slot_data() must emit slot_data["shopLocationIds"] as a sorted
list of int AP location ids, each (a) a real location id in the seed and (b) a shop=True
location (cross-checked against locationIdsToKeys + the shop=True flag).

Run:  python -m unittest worlds.eldenring.tests.test_shop_slot_map_gen
"""
import os
import re
import unittest
from test.bases import WorldTestBase

HERE = os.path.dirname(__file__)
ELDEN = os.path.dirname(HERE)
with open(os.path.join(ELDEN, "locations.py"), encoding="utf-8", errors="replace") as _f:
    SRC = _f.read()
SHOP_NAMES = set(re.findall(r'ERLocationData\(\s*"([^"]+)"[^\n]*(?<![A-Za-z_])shop=True[^\n]*\)', SRC))


class ShopSlotMap_On(WorldTestBase):
    game = "EldenRing"
    auto_construct = True
    options = {
        "enable_dlc": False,
        "world_logic": "region_lock",
        "merchant_bell_logic": "logic_only",
        "accessibility": "minimal",
    }

    def test_shop_location_ids_present_and_wellformed(self):
        sd = self.world.fill_slot_data()
        self.assertIsInstance(sd, dict, "fill_slot_data returned non-dict")
        self.assertIn("shopLocationIds", sd, "slot_data missing shopLocationIds")
        ids = sd["shopLocationIds"]
        self.assertIsInstance(ids, list)
        self.assertTrue(ids, "shopLocationIds empty despite shop_checks ON")
        self.assertTrue(all(isinstance(i, int) for i in ids), "non-int ids present")
        self.assertEqual(ids, sorted(ids), "ids not sorted")
        self.assertEqual(len(ids), len(set(ids)), "duplicate ids")

        by_addr = {}
        for loc in self.multiworld.get_locations(self.player):
            if loc.address is not None:
                by_addr[loc.address] = loc
        shop_keys = sd.get("locationIdsToKeys", {})

        for i in ids:
            self.assertIn(i, by_addr, "shopLocationId not a real location: " + str(i))
            loc = by_addr[i]
            self.assertTrue(getattr(loc.data, "shop", False),
                            "shopLocationId not shop=True: " + str(i) + " " + loc.name)
            self.assertIn(i, shop_keys, "shopLocationId absent from locationIdsToKeys: " + str(i))
            self.assertIn(loc.name, SHOP_NAMES, "name not in static SHOP_NAMES: " + loc.name)

        self.assertGreaterEqual(len(ids), 1, "no shop locations emitted")
        print("[shop-slot-map] count=" + str(len(ids)) + " sample=" + str(ids[:8]))
        for i in ids[:3]:
            print("[shop-slot-map] key " + str(i) + " -> " + str(shop_keys.get(i)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
