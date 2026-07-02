"""Gen-tests: shops are ALWAYS checks (ShopChecks option removed 2026-07-02).

Shop slots are runtime-detectable (scout / flower icon / preview, all confirmed in-game) and
supply hundreds of early-sphere fill candidates -- removing them starved the region-lock fill
(the seed-44444 early-slot headroom class). merchant_bell_logic=logic_only must still gate
merchant slots on their Bell Bearing (see test_merchant_bells.py for the standalone half).
"""
from test.bases import WorldTestBase

KALE_SLOT = "LG/(CE): Torch - Kalé Shop"
TWIN_MAIDEN_SLOT = "RH: Dagger - Twin maiden shop"


class ShopsAlwaysOn_BaseGame(WorldTestBase):
    game = "EldenRing"
    options = {"enable_dlc": False, "world_logic": "region_lock",
               "merchant_bell_logic": "logic_only"}

    def test_shop_slots_are_checks(self):
        names = {l.name for l in self.multiworld.get_locations(self.player)
                 if l.address is not None}
        for slot in (KALE_SLOT, TWIN_MAIDEN_SLOT):
            self.assertIn(slot, names, "shop slot missing from the randomized check set")


class ShopsAlwaysOn_DLC(WorldTestBase):
    game = "EldenRing"
    options = {"enable_dlc": True, "world_logic": "region_lock"}

    def test_shop_slots_are_checks(self):
        names = {l.name for l in self.multiworld.get_locations(self.player)
                 if l.address is not None}
        self.assertIn(KALE_SLOT, names)
