#!/usr/bin/env python3
"""
Elden Ring archi fuzzer.

Copies the fuzzing strategy from Golang to test out different configurations and
record failing option combinations and saves them as JSON regression files that
test_er_regressions.py replays automatically on every future pytest run.

to use:

    python worlds/eldenring/tests/fuzz_er.py
    python worlds/eldenring/tests/fuzz_er.py --iterations 500
    python worlds/eldenring/tests/fuzz_er.py --iterations 50 --seed 42
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Make the repo root importable when run as a standalone script.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from BaseClasses import MultiWorld
from Fill import FillError, distribute_items_restrictive
from Options import Choice, DefaultOnToggle, OptionList, OptionSet, Range, Toggle
from test.bases import WorldTestBase
from worlds import AutoWorld
from worlds.AutoWorld import call_all
from worlds.eldenring.options import EROptions

GAME = "EldenRing"
REGRESSION_DIR = Path(__file__).parent / "regressions"


class _ERFuzzCase(WorldTestBase):
    """Basic WorldTestBase used by the fuzzer to set up worlds."""
    game = GAME
    auto_construct = False

    def runTest(self) -> None:  # required by unittest.TestCase
        pass


# ---------------------------------------------------------------------------
# Option Section
# ---------------------------------------------------------------------------

def _sample_option_value(opt_cls: type, rng: random.Random) -> Any:
    """Given an option class, pick a random value that the option will actually accept."""
    if issubclass(opt_cls, (Toggle, DefaultOnToggle)):
        return rng.choice([0, 1])
    if issubclass(opt_cls, Range):
        return rng.randint(opt_cls.range_start, opt_cls.range_end)
    if issubclass(opt_cls, Choice):
        return rng.choice(list(opt_cls.options.values()))
    if issubclass(opt_cls, (OptionSet, OptionList)):
        keys = list(getattr(opt_cls, "valid_keys", None) or [])
        if not keys:
            return []
        return rng.sample(keys, rng.randint(0, len(keys)))
    return opt_cls.default


def sample_random_options(rng: random.Random) -> Dict[str, Any]:
    """Return a dict of randomly sampled values for all ER-specific options.

    Only options declared directly on EROptions are randomized; the rest use their
    defaults. This might not account for all test variations and options
    """
    type_hints = AutoWorld.AutoWorldRegister.world_types[GAME].options_dataclass.type_hints
    # EROptions.__annotations__ contains only the fields declared on EROptions itself
    er_names = set(EROptions.__annotations__.keys())
    return {
        name: _sample_option_value(cls, rng)
        for name, cls in type_hints.items()
        if name in er_names
    }


# ---------------------------------------------------------------------------
# Generation Section
# ---------------------------------------------------------------------------

def run_generation(seed: int, options: Dict[str, Any]) -> MultiWorld:
    """Build, fill, and compute the spoiler playthrough for a single-player ER world."""
    case = _ERFuzzCase()
    case.options = options
    case.world_setup(seed)
    mw = case.multiworld
    distribute_items_restrictive(mw)
    call_all(mw, "post_fill")
    mw.spoiler.create_playthrough()
    return mw


# ---------------------------------------------------------------------------
# World error checking (this needs to be expanded, or put into another file)
# ---------------------------------------------------------------------------

def check_world_errors(multiworld: MultiWorld, options: Dict[str, Any]) -> List[str]:
    """Returns a list of error strings describing generation problems, or empty if clean."""
    errors: List[str] = []

    # I'm PRETTY sure under all circumstances, having unreachables is bad, so even a single one is cause for regression
    if multiworld.spoiler.unreachables:
        names = sorted(loc.name for loc in multiworld.spoiler.unreachables)
        errors.append(f"unreachable_progression: {names}")

    # Base case check, probably need more of these
    if not multiworld.spoiler.playthrough:
        errors.append("empty_playthrough: game cannot be completed")

    # Another low confidence thing, if dlc is disabled, ANY DLC location present should trigger a regression write
    enable_dlc = int(options.get("enable_dlc", 0))
    if not enable_dlc:
        dlc_locs = [loc.name for loc in multiworld.get_locations() if "DLC" in loc.name]
        if dlc_locs:
            errors.append(f"dlc_leak: DLC disabled but DLC locations present: {dlc_locs[:5]!r}")

    # There definitely needs to be an explicit world logic section here
    # Determining what is technically invalid and would create regressions

    return errors


# ---------------------------------------------------------------------------
# Regression Section
# ---------------------------------------------------------------------------

def save_regression(
    seed: int,
    options: Dict[str, Any],
    description: str,
    violations: Optional[List[str]] = None,
) -> Path:
    """Write a failing seed+options combo to a JSON file in REGRESSION_DIR."""
    REGRESSION_DIR.mkdir(parents=True, exist_ok=True)
    safe_desc = description[:60].replace(" ", "_").replace("/", "-").replace(":", "")
    filename = f"{safe_desc}_seed{seed}.json"
    path = REGRESSION_DIR / filename
    payload: Dict[str, Any] = {
        "seed": seed,
        "options": options,
        "description": description,
        "violations": violations or [],
    }
    with path.open("w") as fh:
        json.dump(payload, fh, indent=2, default=list)
    return path


def load_regression(path: Path) -> Tuple[int, Dict[str, Any], str, List[str]]:
    """Load a regression file. Returns (seed, options, description, original_violations)."""
    with path.open() as fh:
        data = json.load(fh)
    return int(data["seed"]), data["options"], data.get("description", "unknown"), data.get("violations", [])


# ---------------------------------------------------------------------------
# Fuzzer Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Fuzz Elden Ring world generation.")
    parser.add_argument("--iterations", type=int, default=100,
                        help="Number of random option combinations to try (default: 100).")
    parser.add_argument("--seed", type=int, default=None,
                        help="Master RNG seed for reproducibility.")
    args = parser.parse_args()

    master_rng = random.Random(args.seed)
    passed = 0
    failed = 0
    regressions_written: List[Path] = []

    # We literally just generate args.iterations seeds and generations, and check for defined world errors
    for i in range(args.iterations):
        seed = master_rng.randint(0, 2 ** 32 - 1)
        rng = random.Random(seed)
        options = sample_random_options(rng)
        violations = []
        description = "exception"

        try:
            mw = run_generation(seed, options)
            violations = check_world_errors(mw, options)
            if violations:
                description = violations[0].split(":")[0]
        except FillError as exc:
            tb = traceback.format_exc()
            violations = [f"fill_error: {exc}\n{tb}"]
            description = "fill_error"
        except Exception as exc:
            tb = traceback.format_exc()
            violations = [f"exception: {type(exc).__name__}: {exc}\n{tb}"]
            description = f"exception_{type(exc).__name__}"

        if violations:
            failed += 1
            path = save_regression(seed, options, description, violations)
            regressions_written.append(path)
            print(f"[FAIL] iter={i:>4}  seed={seed}  {violations[0].splitlines()[0]}")
            print(f"         saved -> {path.name}")
        else:
            passed += 1
            print(f"[ok]   iter={i:>4}  seed={seed}")

    print()
    print(f"Results: {passed} passed, {failed} failed out of {args.iterations}")
    if regressions_written:
        print(f"Regressions written ({len(regressions_written)}):")
        for p in regressions_written:
            print(f"  {p}")


if __name__ == "__main__":
    main()
