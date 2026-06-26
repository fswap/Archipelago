"""Standalone invariants for merchant bell-bearing gating (no Archipelago import).

Parses locations.py directly so it runs in any environment, then exercises
merchant_bells.resolve_merchant_bells against a stand-in location table. Guards:
  * every gating bell has a real pickup location (else its shop checks unreachable)
  * tokens resolve with no double-match and no leak into excluded merchants
  * base+DLC gated-check count matches the reviewed expectation
Run: python -m worlds.eldenring.tests.test_merchant_bells   (or pytest)
"""
import os, re, types, unittest

HERE = os.path.dirname(__file__)
ELDEN = os.path.dirname(HERE)
SRC = open(os.path.join(ELDEN, "locations.py"), encoding="utf-8", errors="replace").read()

import importlib.util
spec = importlib.util.spec_from_file_location("merchant_bells", os.path.join(ELDEN, "merchant_bells.py"))
mb = importlib.util.module_from_spec(spec); spec.loader.exec_module(mb)

SHOP_NAMES = list(dict.fromkeys(
    re.findall(r'ERLocationData\(\s*"([^"]+)"[^\n]*shop=True[^\n]*\)', SRC)))
DEFAULT_ITEMS = set(i for _, i in re.findall(r'ERLocationData\(\s*"([^"]+)"\s*,\s*"([^"]+)"', SRC))

def fake_locdict(names):
    return {n: types.SimpleNamespace(shop=True) for n in names}

EXCLUDED_TOKENS = ["Enia", "Twin maiden", "Nomadic Merchant", "Isolated Merchant",
                   "Hermit Merchant", "Kal\u00e9"]

class MerchantBellTests(unittest.TestCase):
    def test_every_gating_bell_has_world_drop(self):
        for bell in mb.merchant_bell_names(include_dlc=True):
            self.assertIn(bell, DEFAULT_ITEMS,
                          f"{bell} has no pickup location -> shop gate unreachable")

    def test_no_double_match_and_resolves(self):
        res = mb.resolve_merchant_bells(fake_locdict(SHOP_NAMES), include_dlc=True)
        self.assertEqual(set(res), set(mb.merchant_bell_names(True)))
        seen = {}
        for bell, locs in res.items():
            self.assertTrue(locs, f"{bell} resolved to no shop checks")
            for n in locs:
                self.assertNotIn(n, seen, f"double-match {n}: {seen.get(n)} vs {bell}")
                seen[n] = bell

    def test_no_leak_into_excluded(self):
        res = mb.resolve_merchant_bells(fake_locdict(SHOP_NAMES), include_dlc=True)
        gated = {n for locs in res.values() for n in locs}
        for n in gated:
            for tok in EXCLUDED_TOKENS:
                self.assertNotIn(tok, n, f"gated check leaks into excluded set: {n}")

    def test_expected_counts(self):
        base = mb.resolve_merchant_bells(fake_locdict(SHOP_NAMES), include_dlc=False)
        full = mb.resolve_merchant_bells(fake_locdict(SHOP_NAMES), include_dlc=True)
        self.assertEqual(sum(len(v) for v in base.values()), 74)
        self.assertEqual(sum(len(v) for v in full.values()), 83)

if __name__ == "__main__":
    unittest.main()
