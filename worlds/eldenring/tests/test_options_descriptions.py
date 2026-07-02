"""Description-required gate for the ER option surface (standalone, no AP import).

Every option class reachable from the EROptions dataclass must carry a REAL docstring:
the yaml options wizard (wizard/wizard.html) renders each option's explainer verbatim
from that docstring, so a missing or placeholder docstring becomes a blank/useless
wizard question. Enforced, not aspirational (HANDOFF-OPTIONS-WIZARD.md decision #2).

QUALITY BAR (documented here; the wizard and dump tool rely on it):
  1. non-empty after stripping;
  2. at least 40 characters after whitespace collapse -- long enough to say something
     a display_name can't ("Early Legacy Dungeons are early" is 31 and fails);
  3. not an echo of the display_name or the class name (normalized: lowercased,
     punctuation-insensitive). "Enable DLC" / "Messmer Kindle Shards" fail here.

Core AP classes used directly as fields (DeathLink) are held to bar #1 only -- their
docstrings are upstream surface we don't control.

Same pattern as test_data_tables.py: ast-parse the source, no Archipelago import, runs
in any Python 3.8+ in milliseconds. NUL bytes are stripped before parsing (sandbox
mount writes can null-pad files; real source never contains NULs).

Run: python -m pytest worlds/eldenring/tests/test_options_descriptions.py   (or unittest)
"""
import ast
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ELDEN = os.path.dirname(HERE)
OPTIONS = os.path.join(ELDEN, "options.py")
CORE_OPTIONS = os.path.abspath(os.path.join(ELDEN, "..", "..", "Options.py"))

MIN_LEN = 40  # collapsed-whitespace character floor (bar #2)


def _parse(path):
    src = open(path, "r", encoding="utf-8", errors="replace").read().replace("\x00", "")
    tree = ast.parse(src)
    return {c.name: c for c in tree.body if isinstance(c, ast.ClassDef)}


def _norm(s):
    """Lowercase, collapse whitespace, drop punctuation -- echo comparison form."""
    return re.sub(r"[^a-z0-9 ]+", "", " ".join(s.lower().split()))


def _display_name(cls):
    for n in cls.body:
        if (isinstance(n, ast.Assign) and len(n.targets) == 1
                and isinstance(n.targets[0], ast.Name)
                and n.targets[0].id == "display_name"):
            try:
                return ast.literal_eval(n.value)
            except Exception:
                return None
    return None


class TestOptionDescriptions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.local = _parse(OPTIONS)
        cls.core = _parse(CORE_OPTIONS) if os.path.isfile(CORE_OPTIONS) else {}
        ero = cls.local.get("EROptions")
        assert ero is not None, "EROptions dataclass not found in options.py"
        cls.fields = [(n.target.id, n.annotation.id)
                      for n in ero.body
                      if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)
                      and isinstance(n.annotation, ast.Name)]

    def test_every_field_class_found(self):
        missing = [c for _, c in self.fields
                   if c not in self.local and c not in self.core]
        self.assertFalse(
            missing,
            "EROptions field classes not found in options.py or core Options.py: "
            + ", ".join(missing))

    def test_every_option_has_real_description(self):
        failures = []
        for key, cls_name in self.fields:
            cls, is_core = self.local.get(cls_name), False
            if cls is None:
                cls, is_core = self.core.get(cls_name), True
            if cls is None:
                continue  # covered by test_every_field_class_found
            doc = (ast.get_docstring(cls) or "").strip()
            if not doc:
                failures.append(f"{cls_name} ({key}): EMPTY docstring")
                continue
            if is_core:
                continue  # upstream classes: bar #1 only
            collapsed = " ".join(doc.split())
            dn = _display_name(cls) or ""
            if _norm(collapsed) in (_norm(dn), _norm(cls_name),
                                    _norm(re.sub(r"(?<!^)(?=[A-Z])", " ", cls_name))):
                failures.append(
                    f"{cls_name} ({key}): docstring is just an echo of the display/class "
                    f"name ({collapsed!r})")
            elif len(collapsed) < MIN_LEN:
                failures.append(
                    f"{cls_name} ({key}): docstring too short "
                    f"({len(collapsed)} < {MIN_LEN} chars: {collapsed!r})")
        self.assertFalse(
            failures,
            "\n\nOption docstrings below the wizard quality bar (see module docstring; "
            "fix via patch_option_descriptions.py):\n  " + "\n  ".join(failures))


if __name__ == "__main__":
    unittest.main()
