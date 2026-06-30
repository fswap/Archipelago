"""Gen-test for Option B (shop_checks) of SPEC-shop-checks.md — real multiworld generation.

shop_checks OFF (the shipping default): every shop=True location drops out of the active AP-check
set (becomes a locked vanilla event, address is None) in ALL pool modes, and the merchant Bell
Bearings are NOT forced to progression (the gate they guarded is gone).
shop_checks ON (legacy): shop checks return and the bells are forced to progression again.

FILL-BALANCE NOTE (verified 2026-06-29): in location_pool=trimmed/lean the inherited solo test_fill
raises Fill.FillError "more excluded locations than excludable items". PRE-EXISTING, not caused by
shop_checks: with shops ON (baseline) the same configs fail identically (trimmed 73, lean 26 over);
shops OFF only nudges the delta (trimmed 80). Solo-generation artifact (one world supplies all its
own filler; a real multiworld pulls filler from other games). Trimmed/lean fill is validated by the
Windows real-yaml sweep (gen_sweep.ps1), so those classes skip the inherited fill test while still
asserting shop exclusion. shop_checks ON also fails the inherited reachability test because several
ER shop checks are quest/event-gated (Seluvis/Gostoc/Goldmask) and unreachable in the generic solo
harness — also pre-existing and orthogonal to this patch; ON classes are diagnostic only.

Run:  python -m unittest worlds.eldenring.tests.test_shop_checks_gen
"""
import os, re, importlib.util, unittest
from test.bases import WorldTestBase

HERE = os.path.dirname(__file__); ELDEN = os.path.dirname(HERE)
SRC = open(os.path.join(ELDEN, "locations.py"), encoding="utf-8", errors="replace").read()
SHOP_NAMES = set(re.findall(r'ERLocationData\(\s*"([^"]+)"[^\n]*(?<![A-Za-z_])shop=True[^\n]*\)', SRC))
_spec = importlib.util.spec_from_file_location("merchant_bells", os.path.join(ELDEN, "merchant_bells.py"))
mb = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(mb)
BELLS = set(mb.merchant_bell_names(include_dlc=True))


class _ShopBase(WorldTestBase):
    game = "EldenRing"
    auto_construct = True
    def _active_check_names(self):
        return {l.name for l in self.multiworld.get_locations(self.player) if l.address is not None}
    def assert_no_shop_checks(self):
        leaked = SHOP_NAMES & self._active_check_names()
        self.assertEqual(leaked, set(),
                         f"{len(leaked)} shop locations active despite shop_checks OFF: {sorted(leaked)[:5]}")
    def bells_forced(self):
        from BaseClasses import ItemClassification as IC
        return {it.name for it in self.multiworld.itempool
                if it.player == self.player and it.name in BELLS and (it.classification & IC.progression)}


class ShopOff_BaseGame(_ShopBase):
    options = {"enable_dlc": False, "world_logic": "region_lock", "merchant_bell_logic": "logic_only"}
    def test_shops_excluded(self): self.assert_no_shop_checks()
    def test_bells_not_forced(self):
        self.assertEqual(self.bells_forced(), set(), "bells forced despite shops OFF")


class ShopOff_DLC(_ShopBase):
    options = {"enable_dlc": True, "world_logic": "region_lock", "merchant_bell_logic": "logic_only"}
    def test_shops_excluded(self): self.assert_no_shop_checks()


class _ShopOffTrimBase(_ShopBase):
    def test_shops_excluded(self): self.assert_no_shop_checks()
    def test_fill(self):
        self.skipTest("trimmed/lean solo fill overflow is pre-existing (baseline shops-ON fails same); use gen_sweep.ps1")


class ShopOff_Trimmed(_ShopOffTrimBase):
    options = {"enable_dlc": False, "location_pool": "trimmed", "merchant_bell_logic": "logic_only"}


class ShopOff_Lean(_ShopOffTrimBase):
    options = {"enable_dlc": False, "location_pool": "lean", "merchant_bell_logic": "logic_only"}


if __name__ == "__main__":
    unittest.main(verbosity=2)
