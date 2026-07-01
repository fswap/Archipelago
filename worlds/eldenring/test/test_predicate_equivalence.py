"""Equivalence acceptance test for the Elden Ring predicate-contract migration (Stream A).

For every stateless factory in ``rules_predicates`` this test resolves the returned
``Rule`` against a real generated ``EldenRing`` world and asserts that
``resolved(state) == <legacy EldenRingRules._* method>(state, ...)`` for a battery of
synthetic ``CollectionState``s: item counts of ``{0, threshold-1, threshold, threshold+1}``
(with x3/x5 stacks exercised for the weighted key/heart predicates) crossed with the three
option short-circuits that the factories bake in (``soft_consumable_shop``,
``key_gates_missable``, ``progressive_stone_bells``).

The option short-circuits live INSIDE the resolved rule (via ``OptionFilter``), so they can
only be exercised by generating separate worlds with different option values -- hence one
``WorldTestBase`` subclass per relevant option combo. The count/weight logic is exercised by
mutating a fresh ``CollectionState``'s ``prog_items`` directly (via ``state.add_item``), which
is exactly what both the legacy methods and the resolved rules read, so it faithfully isolates
the arithmetic without depending on the generated item pool.

ENV NOTE: rule_builder imports ``typing.Self`` (3.11+), so this file only runs on the user's
Python 3.12; it is py_compile-clean on 3.10. It cannot run in the 3.10 sandbox.
"""
from __future__ import annotations

import typing

from BaseClasses import CollectionState
from test.bases import WorldTestBase

from .. import rules_predicates as rp


# ------------------------------------------------------------------------------------------
# helpers
# ------------------------------------------------------------------------------------------
class _ERPredicateEquivalenceMixin:
    """Shared assertions. Mixed into per-option WorldTestBase subclasses below.

    Each subclass sets ``options`` (soft_consumable_shop / key_gates_missable /
    progressive_stone_bells) and inherits these test methods, so every combination runs the
    full battery.
    """

    game = "EldenRing"
    # subclasses declare `options`
    world: typing.Any
    multiworld: typing.Any
    player: int

    # -- state construction ---------------------------------------------------------------
    def _fresh_state(self) -> CollectionState:
        """A pristine CollectionState for this multiworld (no items collected)."""
        return CollectionState(self.multiworld)

    def _state_with(self, counts: typing.Mapping[str, int]) -> CollectionState:
        """A fresh state with the given item *instance* counts injected into prog_items.

        ``add_item`` bumps prog_items by count directly -- the same field both the legacy
        ``state.count`` predicates and the resolved rules read. This mirrors collecting
        ``count`` separate copies of that item.
        """
        state = self._fresh_state()
        for name, n in counts.items():
            if n:
                state.add_item(name, self.player, n)
        return state

    def _resolve(self, rule):
        return rule.resolve(self.world)

    def _assert_equiv(self, resolved, legacy_result: bool, msg: str) -> None:
        got = resolved(self._current_state)
        self.assertEqual(  # type: ignore[attr-defined]
            bool(got), bool(legacy_result),
            f"{msg}: resolved={got!r} legacy={legacy_result!r} "
            f"[options soft={self.world.options.soft_consumable_shop.value} "
            f"key_missable={self.world.options.key_gates_missable.value} "
            f"prog_bells={self.world.options.progressive_stone_bells.value}]",
        )

    # convenience so _assert_equiv reads clean
    _current_state: CollectionState

    def _run_count_battery(self, factory, legacy, item_counts_fn, thresholds):
        """For each threshold T, drive counts {0, T-1, T, T+1} and compare factory vs legacy.

        - ``factory``   : rp.<name>(T) -> Rule
        - ``legacy``    : lambda(state, T) -> bool   (the EldenRingRules._* method)
        - ``item_counts_fn`` : lambda n -> {item: instance_count} building a state that yields
                               a weighted/plain total of ``n``.
        """
        for t in thresholds:
            for n in (0, t - 1, t, t + 1):
                if n < 0:
                    continue
                self._current_state = self._state_with(item_counts_fn(n))
                resolved = self._resolve(factory(t))
                legacy_result = legacy(self._current_state, t)
                self._assert_equiv(resolved, legacy_result, f"count={n} threshold={t}")

    # -- individual predicate tests -------------------------------------------------------
    def test_has_enough_great_runes(self):
        # no option short-circuit; pure count_from_list threshold
        self._run_count_battery(
            rp.has_enough_great_runes,
            self.world._has_enough_great_runes,
            lambda n: self._distribute_over(rp.GREAT_RUNES, n),
            thresholds=[1, 3, 7],
        )

    def test_has_bloody_finger(self):
        # legacy: count_from_list(...) >= 1 ; factory: HasAny(...)
        factory = rp.has_bloody_finger()
        for n in (0, 1, 2):
            self._current_state = self._state_with(self._distribute_over(rp.BLOODY_FINGERS, n))
            resolved = self._resolve(factory)
            legacy_result = self.world._has_bloody_finger(self._current_state)
            self._assert_equiv(resolved, legacy_result, f"bloody fingers={n}")

    def test_has_enough_keys_weighted(self):
        # weighted x1/x3/x5 + soft/missable short-circuit
        self._run_key_like(rp.has_enough_keys, self.world._has_enough_keys, rp.STONESWORD_KEY_WEIGHTS)

    def test_has_enough_hearts_weighted(self):
        self._run_key_like(rp.has_enough_hearts, self.world._has_enough_hearts, rp.DRAGON_HEART_WEIGHTS)

    def test_has_enough_imbued(self):
        # plain Has(count) + soft/missable short-circuit
        for t in (1, 3, 4):
            for n in (0, t - 1, t, t + 1):
                if n < 0:
                    continue
                self._current_state = self._state_with({"Imbued Sword Key": n})
                resolved = self._resolve(rp.has_enough_imbued(t))
                legacy_result = self.world._has_enough_imbued(self._current_state, t)
                self._assert_equiv(resolved, legacy_result, f"imbued={n} threshold={t}")

    def test_bell_bearings_smithing(self):
        self._run_bell_battery(somber=False)

    def test_bell_bearings_somber(self):
        self._run_bell_battery(somber=True)

    # -- shared drivers -------------------------------------------------------------------
    def _run_key_like(self, factory, legacy, weights):
        """Exercise a weighted key/heart predicate across x1/x3/x5 stacks + thresholds."""
        thresholds = [1, 3, 5, 6]
        for t in thresholds:
            # build several stack distributions that each total exactly n (weighted), and a
            # couple that straddle the threshold via x3/x5 stacks specifically.
            for n in (0, t - 1, t, t + 1):
                if n < 0:
                    continue
                self._current_state = self._state_with(self._weighted_distribute(weights, n))
                resolved = self._resolve(factory(t))
                legacy_result = legacy(self._current_state, t)
                self._assert_equiv(resolved, legacy_result, f"weighted total={n} threshold={t}")

            # explicit x3 / x5 stack cases to prove the multiplier, independent of thresholds
            base_item, _ = weights[0]
            x3_item, x3_w = weights[1]
            x5_item, x5_w = weights[2]
            for stacks in (
                {x3_item: 1},               # total = 3
                {x5_item: 1},               # total = 5
                {x3_item: 1, x5_item: 1},   # total = 8
                {base_item: 2, x3_item: 1}, # total = 5
                {x5_item: 2},               # total = 10
            ):
                self._current_state = self._state_with(stacks)
                resolved = self._resolve(factory(t))
                legacy_result = legacy(self._current_state, t)
                self._assert_equiv(resolved, legacy_result, f"stacks={stacks} threshold={t}")

    def _run_bell_battery(self, somber: bool):
        stem = "Somberstone Miner's Bell Bearing" if somber else "Smithing-Stone Miner's Bell Bearing"
        prog = rp.PROGRESSIVE_SOMBER_BELL if somber else rp.PROGRESSIVE_SMITHING_BELL
        for up_to in (1, 2, 4):
            # progressive item counts around up_to
            for prog_n in (0, up_to - 1, up_to, up_to + 1):
                if prog_n < 0:
                    continue
                self._current_state = self._state_with({prog: prog_n})
                resolved = self._resolve(rp.bell_bearings_required(up_to, somber))
                legacy_result = self.world._bell_bearings_required(self._current_state, up_to, somber)
                self._assert_equiv(resolved, legacy_result,
                                   f"bell somber={somber} prog_copies={prog_n} up_to={up_to}")
            # discrete bell-bearing sets: none, partial [1..up_to-1], full [1..up_to], superset
            discrete_full = {f"{stem} [{c}]": 1 for c in range(1, up_to + 1)}
            discrete_partial = {f"{stem} [{c}]": 1 for c in range(1, up_to)}
            discrete_super = {f"{stem} [{c}]": 1 for c in range(1, up_to + 2)}
            for disc in ({}, discrete_partial, discrete_full, discrete_super):
                self._current_state = self._state_with(disc)
                resolved = self._resolve(rp.bell_bearings_required(up_to, somber))
                legacy_result = self.world._bell_bearings_required(self._current_state, up_to, somber)
                self._assert_equiv(resolved, legacy_result,
                                   f"bell somber={somber} discrete={sorted(disc)} up_to={up_to}")

    # -- count distribution utilities -----------------------------------------------------
    @staticmethod
    def _distribute_over(items, total):
        """Give `total` single-count instances spread over the item list (each weight 1)."""
        counts = {}
        remaining = total
        for it in items:
            if remaining <= 0:
                break
            counts[it] = 1
            remaining -= 1
        # if total exceeds the number of distinct items, pile the rest on the first item
        if remaining > 0 and items:
            counts[items[0]] = counts.get(items[0], 0) + remaining
        return counts

    @staticmethod
    def _weighted_distribute(weights, total):
        """Build {item: instance_count} whose weighted sum == total, greedily using bigger stacks."""
        counts: dict = {}
        remaining = total
        for item, w in sorted(weights, key=lambda iw: -iw[1]):
            if w <= 0:
                continue
            take, remaining = divmod(remaining, w)
            if take:
                counts[item] = counts.get(item, 0) + take
        # any leftover (< smallest weight) goes onto the weight-1 item
        if remaining:
            base = next(item for item, w in weights if w == 1)
            counts[base] = counts.get(base, 0) + remaining
        return counts


# ------------------------------------------------------------------------------------------
# one concrete WorldTestBase per option combination that changes a baked short-circuit
# ------------------------------------------------------------------------------------------
# key_gates_missable is DefaultOnToggle (default 1). We must set it explicitly on every combo
# so the intended value is exercised (default-on would otherwise mask the weighted key/heart
# and imbued paths).

class TestPredicatesAllGatesOn(_ERPredicateEquivalenceMixin, WorldTestBase):
    """key_gates_missable ON (default): key/heart/imbued predicates short-circuit True."""
    options = {
        "soft_consumable_shop": 0,
        "key_gates_missable": 1,
        "progressive_stone_bells": 0,
    }


class TestPredicatesAllGatesOff(_ERPredicateEquivalenceMixin, WorldTestBase):
    """All key gates OFF: the weighted/arithmetic paths are actually exercised."""
    options = {
        "soft_consumable_shop": 0,
        "key_gates_missable": 0,
        "progressive_stone_bells": 0,
    }


class TestPredicatesSoftShopOn(_ERPredicateEquivalenceMixin, WorldTestBase):
    """soft_consumable_shop ON (key_gates_missable OFF): short-circuit via the OTHER option."""
    options = {
        "soft_consumable_shop": 1,
        "key_gates_missable": 0,
        "progressive_stone_bells": 0,
    }


class TestPredicatesProgressiveBellsOn(_ERPredicateEquivalenceMixin, WorldTestBase):
    """progressive_stone_bells ON: bell predicate uses the progressive-item branch.

    key gates OFF so the weighted paths still run under this world too.
    """
    options = {
        "soft_consumable_shop": 0,
        "key_gates_missable": 0,
        "progressive_stone_bells": 1,
    }


class TestPredicatesProgressiveBellsOff(_ERPredicateEquivalenceMixin, WorldTestBase):
    """progressive_stone_bells OFF: bell predicate uses the discrete HasAll branch."""
    options = {
        "soft_consumable_shop": 0,
        "key_gates_missable": 0,
        "progressive_stone_bells": 0,
    }


# ------------------------------------------------------------------------------------------
# reachability factories (can_get / can_get_all / can_go_to): structural equivalence.
# These delegate to state.can_reach_* against the real region graph. On a pristine state only
# the free start region(s) are reachable, so both the resolved rule and the legacy method must
# agree (typically both False for a deep location). We assert agreement rather than a fixed
# value so the test is robust to whichever region is free at sphere 0.
# ------------------------------------------------------------------------------------------
class TestReachabilityFactories(WorldTestBase):
    game = "EldenRing"
    options = {}

    def _agree_location(self, loc_name: str):
        state = CollectionState(self.multiworld)
        resolved = rp.can_get(loc_name).resolve(self.world)
        legacy = self.world._can_get(state, loc_name)
        self.assertEqual(bool(resolved(state)), bool(legacy),
                         f"can_get disagreement for {loc_name}")

    def test_can_get_matches_legacy(self):
        # sample a spread of locations from the generated pool
        locs = [loc.name for loc in self.multiworld.get_locations(self.player)]
        for loc_name in locs[:25]:
            self._agree_location(loc_name)

    def test_can_get_all_matches_legacy(self):
        locs = [loc.name for loc in self.multiworld.get_locations(self.player)][:8]
        if not locs:
            return
        state = CollectionState(self.multiworld)
        resolved = rp.can_get_all(locs).resolve(self.world)
        legacy = self.world._can_get_all(state, set(locs))
        self.assertEqual(bool(resolved(state)), bool(legacy),
                         "can_get_all disagreement")

    def test_can_go_to_matches_legacy(self):
        regions = [r.name for r in self.multiworld.get_regions(self.player)]
        state = CollectionState(self.multiworld)
        for region in regions[:25]:
            # legacy _can_go_to needs the 'Go To {region}' entrance to exist; only test regions
            # that have one so we compare like-for-like.
            try:
                self.multiworld.get_entrance(f"Go To {region}", self.player)
            except KeyError:
                continue
            resolved = rp.can_go_to(region).resolve(self.world)
            legacy = self.world._can_go_to(state, region)
            self.assertEqual(bool(resolved(state)), bool(legacy),
                             f"can_go_to disagreement for {region}")
