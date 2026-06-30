#!/usr/bin/env python3
"""Run the Elden Ring apworld gen-tests and tee full output (results + tracebacks) to a timestamped
log file, so failures can be reviewed or shared without copy-pasting console output.

Run from the Archipelago root (the dir with Generate.py), using your AP python/venv (3.11+):

    python worlds/eldenring/tests/run_tests.py

Writes: <Archipelago>/test_logs/er_tests_<YYYYMMDD_HHMMSS>.log  (also printed to console).
Exit code 0 if all green, 1 otherwise. Pass test-name fragments to filter, e.g.:

    python worlds/eldenring/tests/run_tests.py key_gates        # only modules matching *key_gates*
"""
import sys, os, unittest, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
AP_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))  # worlds/eldenring/tests -> AP root
TESTS_DIR = HERE
os.chdir(AP_ROOT)
if AP_ROOT not in sys.path:
    sys.path.insert(0, AP_ROOT)


class _Tee:
    def __init__(self, *streams):
        self.streams = streams
    def write(self, s):
        for st in self.streams:
            st.write(s)
    def flush(self):
        for st in self.streams:
            st.flush()


def main() -> int:
    filt = sys.argv[1] if len(sys.argv) > 1 else None
    # Windows globbing is case-insensitive so "test*.py" also catches TestER.py / TestEROptionMatrix.py.
    suite = unittest.TestLoader().discover(start_dir=TESTS_DIR, top_level_dir=AP_ROOT, pattern="test*.py")
    if filt:
        keep = unittest.TestSuite()
        for grp in suite:
            for sub in grp:
                if filt.lower() in str(sub).lower():
                    keep.addTest(sub)
        suite = keep

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = os.path.join(AP_ROOT, "test_logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"er_tests_{ts}.log")

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"ER apworld test run {ts}\nAP_ROOT={AP_ROOT}\nfilter={filt!r}\n\n")
        f.flush()
        tee = _Tee(sys.stderr, f)
        result = unittest.TextTestRunner(stream=tee, verbosity=2).run(suite)
        f.write(
            f"\n=== SUMMARY: ran={result.testsRun} failures={len(result.failures)} "
            f"errors={len(result.errors)} skipped={len(result.skipped)} "
            f"-> {'OK' if result.wasSuccessful() else 'FAILED'} ===\n"
        )

    print(f"\nLog written to: {log_path}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
