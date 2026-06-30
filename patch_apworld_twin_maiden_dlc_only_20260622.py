"""
patch_apworld_twin_maiden_dlc_only_20260622.py

Re-add the Twin Maiden Husks (Roundtable Hold) shop checks to randomization
under dlc_only.

Background
---------
dlc_only inverts the normal scope rule in `_content_in_scope`: it keeps ONLY
dlc-flagged locations and strips every base-game check (base map is kept solely
for free transit). The 21 "RH: <item> - Twin maiden shop" slots are base-game
shop locations (dlc=False), so they were dropped from the pool -- the vendor
showed vanilla stock in dlc_only seeds. Alaric wants them randomized again.

This patch adds a single exception in `_content_in_scope`: under dlc_only, also
keep locations whose name contains "Twin maiden shop". The Roundtable vendor is
always reachable (dlc_only gives free base transit + a Roundtable grace), so the
checks fill cleanly under accessibility: minimal, and the change is count-neutral
(each re-added slot contributes its vanilla item back to the pool, and
create_items sizes filler off get_unfilled_locations).

Scope: apworld / generation only. No datapackage, slot_data, baker, or client
change -- these 21 locations already have stable AP location IDs.

Run on Windows from the Archipelago repo root:
    python patch_apworld_twin_maiden_dlc_only_20260622.py

Idempotent: re-running after a successful patch is a no-op.
"""

import os
import sys
import py_compile

REL = os.path.join("worlds", "eldenring", "__init__.py")

OLD = (
    "        if self.options.dlc_only:\r\n"
    "            return bool(data.dlc)\r\n"
    "        return (not data.dlc) or bool(self.options.enable_dlc)\r\n"
)

NEW = (
    "        if self.options.dlc_only:\r\n"
    "            # Re-include the Twin Maiden Husks (Roundtable Hold) base-game shop\r\n"
    "            # slots as randomized checks under dlc_only. The Roundtable vendor is\r\n"
    "            # always reachable (base map is free-transit in dlc_only), so these 21\r\n"
    "            # shop checks fill cleanly and stay count-neutral (each re-adds its\r\n"
    "            # vanilla item to the pool). patch_apworld_twin_maiden_dlc_only_20260622.\r\n"
    "            if \"Twin maiden shop\" in data.name:\r\n"
    "                return True\r\n"
    "            return bool(data.dlc)\r\n"
    "        return (not data.dlc) or bool(self.options.enable_dlc)\r\n"
)

MARKER = 'if "Twin maiden shop" in data.name:'


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, REL)
    if not os.path.isfile(path):
        print(f"ERROR: not found: {path}")
        print("Run this from the Archipelago repo root.")
        return 1

    with open(path, "r", encoding="utf-8", newline="") as f:
        src = f.read()

    if MARKER in src:
        print("Already patched (marker present); nothing to do.")
        return 0

    n = src.count(OLD)
    if n != 1:
        print(f"ERROR: anchor matched {n} times (expected 1). Aborting -- "
              f"_content_in_scope may have changed; re-inspect before patching.")
        return 1

    src = src.replace(OLD, NEW, 1)

    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)

    # Purge stale bytecode so the edit can't be masked by a cached .pyc.
    pyc_dir = os.path.join(os.path.dirname(path), "__pycache__")
    if os.path.isdir(pyc_dir):
        for fn in os.listdir(pyc_dir):
            if fn.startswith("__init__.") and fn.endswith(".pyc"):
                try:
                    os.remove(os.path.join(pyc_dir, fn))
                except OSError:
                    pass

    # Verify it still compiles.
    try:
        py_compile.compile(path, doraise=True)
    except py_compile.PyCompileError as e:
        print("ERROR: file no longer byte-compiles after patch:")
        print(e)
        return 1

    print("Patched _content_in_scope: Twin Maiden Husks shop checks re-included under dlc_only.")
    print("Byte-compiles OK. __pycache__ purged.")
    print("Next: build.ps1 -Generate with a dlc_only yaml and confirm 21 'Twin maiden shop' checks are in-seed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
