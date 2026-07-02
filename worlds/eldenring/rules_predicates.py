"""Elden Ring — predicate rule factories: the FROZEN CONTRACT for the rule_builder migration.

These stateless factories replace the old ``EldenRingRules._*`` predicate *methods* (which took a
``state``). Because a rule_builder ``Rule`` is data, each predicate becomes a pure factory
``(...) -> Rule`` with the ``state`` argument dropped.

CONTRACT RULES (do not break — Phase 3 and Phase 4 code against this interface in parallel):
  1. Each factory returns a context-free ``Rule``. Option short-circuits (soft_consumable_shop /
     key_gates_missable / progressive_stone_bells) are baked INSIDE the returned rule via
     ``OptionFilter``; callers NEVER re-check options.
  2. Dynamic counts are passed as plain ``int`` by the caller (which reads ``world.options``).
     These factories never read options to decide a count — so option-valued region gates live in a
     ``build_region_rules(world)`` builder, not a static dict.
  3. Returned rules compose with ``&`` / ``|`` and are safe to nest.

ACCEPTANCE TEST (Stream A): ``test_predicate_equivalence`` resolves each factory and compares
``resolved(state)`` to the corresponding legacy ``EldenRingRules._*`` method across a battery of
synthetic CollectionStates (item-count × option combos). Equivalence there == behaviour-preserving,
provable without a full generation.

NOTE: ``HasWeighted`` (stacked-consumable count) is the one custom rule here; it is the single item
Stream A must confirm via the equivalence test before trusting (custom frozen-dataclass rule).
"""
from __future__ import annotations

import dataclasses
from collections.abc import Iterable
from typing import ClassVar

from BaseClasses import CollectionState
from rule_builder.rules import (
    Rule, Has, HasAll, HasAny, HasFromList,
    CanReachEntrance, CanReachLocation, CanReachRegion, Filtered, True_, And,
)
from rule_builder.options import OptionFilter

from .options import RegionAccessLogic, ProgressiveStoneBells
from .stone_bells import PROGRESSIVE_SMITHING_BELL, PROGRESSIVE_SOMBER_BELL


# --- item groups (verbatim from the legacy predicates) ----------------------------------------
GREAT_RUNES = (
    "Godrick's Great Rune", "Rykard's Great Rune", "Radahn's Great Rune",
    "Morgott's Great Rune", "Mohg's Great Rune", "Malenia's Great Rune", "Great Rune of the Unborn",
)
BLOODY_FINGERS = (
    "Festering Bloody Finger", "Festering Bloody Finger x2", "Festering Bloody Finger x3",
    "Festering Bloody Finger x5", "Festering Bloody Finger x6", "Festering Bloody Finger x8",
    "Festering Bloody Finger x10",
)
# weighted stacks: (item, per-item weight)
STONESWORD_KEY_WEIGHTS = (("Stonesword Key", 1), ("Stonesword Key x3", 3), ("Stonesword Key x5", 5))
DRAGON_HEART_WEIGHTS = (("Dragon Heart", 1), ("Dragon Heart x3", 3), ("Dragon Heart x5", 5))

# A consumable-key gate is satisfied outright when the gated checks are made
# missable (key_gates_missable). soft_consumable_shop REMOVED 2026-07-02: its
# shop half was baked Twin Maiden rows (baker retired), so the short-circuit
# had become a softlock generator.
# v0.1 single sound mode (key_gates_missable option removed 2026-07-02): consumable-key
# gates are ALWAYS open in logic; the gated checks are EXCLUDED and the keys are filler.
_KEY_GATE_OFF: Rule = True_()


@dataclasses.dataclass()
class HasWeighted(Rule, game="EldenRing"):
    """Has at least ``count`` across stacked items with per-item weights.

    Mirrors the legacy weighted predicates, e.g. Stonesword Key + (x3)*3 + (x5)*5 >= count.
    ``item_weights`` is a tuple of ``(item_name, weight)`` pairs (kept hashable — custom rules are
    frozen dataclasses)."""

    item_weights: tuple
    count: int

    def _instantiate(self, world) -> Rule.Resolved:
        return self.Resolved(
            self.item_weights, self.count,
            player=world.player, caching_enabled=getattr(world, "rule_caching_enabled", False),
        )

    class Resolved(Rule.Resolved):
        item_weights: tuple
        count: int
        skip_cache: ClassVar[bool] = True

        def _evaluate(self, state: CollectionState) -> bool:
            total = 0
            for item, weight in self.item_weights:
                total += state.count(item, self.player) * weight
            return total >= self.count

        def item_dependencies(self) -> dict:
            return {item: set() for item, _ in self.item_weights}

        def __str__(self) -> str:
            return f"HasWeighted({self.count} across {[i for i, _ in self.item_weights]})"


# --- uncached reach rules (patch_priority_fill_fix, 2026-07-01) --------------------------------
# CanReach{Entrance,Location,Region} depend on graph REACHABILITY, not just collected items, and
# the rule-result cache cannot invalidate them soundly in this world:
#   * their only registered invalidation trigger is a reached_region event on the PARENT region
#     of the target entrance/location, and
#   * register_rule_builder_dependencies() would fold the target entrance's item deps in, but it
#     skips every entrance whose access_rule is an add_rule() lambda -- which is ALL of this
#     world's gated "Go To" entrances (geographic rule + region-lock clause are AND-stacked via
#     add_rule in rules_mixin).
# So once the parent region is already reachable in a state (or in any ancestor state that a
# fill sweep copies from -- sweep states inherit rule_builder_cache), a cached False for these
# rules is NEVER cleared by later item collection: whole subtrees (Caelid -> Wailing Dunes ->
# Nokron, Stormveil, Farum Azula, ...) stay "unreachable" inside fill sweeps. Symptoms: FillError
# at Fill.py "Priority Retry" ("No more spots to place N items", "Already placed 0") across
# region_lock combos and, on seeds that happened to fill, silent full-accessibility violations.
# Root-cause proof 2026-07-01: clearing state.rule_builder_cache flipped the three starved
# priority locations back to reachable=True on the repro seed 85920353982860255231.
# Fix: force these three rules (and, via NestedRule force_recalculate propagation, any composite
# containing them) to always re-evaluate. Leaf Has*/HasWeighted rules keep caching. Measured
# gen-time impact: none (~0.4s per gen either way). Scoped to EldenRing subclasses so the
# framework's own caching tests (test_rule_builder) keep their contract.

class ERCanReachEntrance(CanReachEntrance, game="EldenRing"):
    """CanReachEntrance that is never cached (see block comment above)."""
    class Resolved(CanReachEntrance.Resolved):
        force_recalculate: ClassVar[bool] = True


class ERCanReachLocation(CanReachLocation, game="EldenRing"):
    """CanReachLocation that is never cached (see block comment above)."""
    class Resolved(CanReachLocation.Resolved):
        force_recalculate: ClassVar[bool] = True


class ERCanReachRegion(CanReachRegion, game="EldenRing"):
    """CanReachRegion that is never cached (see block comment above)."""
    class Resolved(CanReachRegion.Resolved):
        force_recalculate: ClassVar[bool] = True


# =============================== the frozen factory contract ===================================

def can_go_to(region: str) -> Rule:
    """Reachable via the geographic 'Go To {region}' entrance, or — under region_access=warp —
    by reaching the region directly (its grace warp). The single seam between the geographic and
    warp environments (SPEC §4b/§4h)."""
    return (
        ERCanReachEntrance(f"Go To {region}")
        | Filtered(ERCanReachRegion(region),
                   options=[OptionFilter(RegionAccessLogic, RegionAccessLogic.option_warp)])
    )


def can_get(location: str) -> Rule:
    """Legacy _can_get: the given location is logically reachable."""
    return ERCanReachLocation(location)


def can_get_all(locations: Iterable[str]) -> Rule:
    """Legacy _can_get_all: every listed location is reachable."""
    return And(*(ERCanReachLocation(loc) for loc in locations))


def has_enough_great_runes(count: int) -> Rule:
    """Legacy _has_enough_great_runes: total great runes >= count (no option short-circuit)."""
    return HasFromList(*GREAT_RUNES, count=count)


def has_bloody_finger() -> Rule:
    """Legacy _has_bloody_finger: at least one festering bloody finger of any stack size."""
    return HasAny(*BLOODY_FINGERS)


def has_enough_keys(count: int) -> Rule:
    """Legacy _has_enough_keys: weighted Stonesword Key count >= count, OR keys are soft/missable."""
    return HasWeighted(STONESWORD_KEY_WEIGHTS, count) | _KEY_GATE_OFF


def has_enough_hearts(count: int) -> Rule:
    """Legacy _has_enough_hearts: weighted Dragon Heart count >= count, OR keys are soft/missable."""
    return HasWeighted(DRAGON_HEART_WEIGHTS, count) | _KEY_GATE_OFF


def has_enough_imbued(count: int) -> Rule:
    """Legacy _has_enough_imbued: >= count Imbued Sword Keys, OR keys are soft/missable."""
    return Has("Imbued Sword Key", count=count) | _KEY_GATE_OFF


def bell_bearings_required(up_to: int, somber: bool) -> Rule:
    """Legacy _bell_bearings_required (False=smithing, True=somber). Under progressive_stone_bells,
    needs `up_to` of the progressive bell; otherwise needs each discrete bell bearing [1..up_to]."""
    progressive_item = PROGRESSIVE_SOMBER_BELL if somber else PROGRESSIVE_SMITHING_BELL
    stem = "Somberstone Miner's Bell Bearing" if somber else "Smithing-Stone Miner's Bell Bearing"
    discrete = [f"{stem} [{c}]" for c in range(1, up_to + 1)]
    return (
        Filtered(Has(progressive_item, count=up_to),
                 options=[OptionFilter(ProgressiveStoneBells, ProgressiveStoneBells.option_true)])
        | Filtered(HasAll(*discrete),
                   options=[OptionFilter(ProgressiveStoneBells, ProgressiveStoneBells.option_false)])
    )
