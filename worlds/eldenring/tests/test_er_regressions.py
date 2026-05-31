"""
Elden Ring generation regression tests.

Each JSON file in regressions/ becomes a named pytest test case.
Populate the directory by running the fuzzer:

    python worlds/eldenring/tests/fuzz_er.py

Then commit any confirmed bugs so they are replayed on every future run via:

    pytest worlds/eldenring/tests/
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import pytest

from .fuzz_er import check_world_errors, load_regression, run_generation

_REGRESSION_DIR = Path(__file__).parent / "regressions"


def _collect_regressions() -> List[Tuple[str, Path]]:
    if not _REGRESSION_DIR.exists():
        return []
    return [(p.stem, p) for p in sorted(_REGRESSION_DIR.glob("*.json"))]


_REGRESSION_CASES = _collect_regressions()


@pytest.mark.parametrize(
    "regression_path",
    [p for _, p in _REGRESSION_CASES],
    ids=[name for name, _ in _REGRESSION_CASES],
)
def test_regression(regression_path: Path) -> None:
    seed, options, description, original_violations = load_regression(regression_path)
    multiworld = run_generation(seed, options)
    violations = check_world_errors(multiworld, options)
    assert not violations, (
        f"Regression [{regression_path.name}] seed={seed} description={description!r}:\n"
        + "\n".join(f"  - {v}" for v in violations)
        + (
            "\n\nOriginal failure:\n" + "\n".join(f"  {v}" for v in original_violations)
            if original_violations
            else ""
        )
    )
