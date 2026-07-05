#!/usr/bin/env python3
r"""pool_builder_sweep.py -- scaling harness for the ER pool_builder.

WHAT IT DOES
    Runs the apworld's item-pool composition (generate_early -> create_items,
    i.e. everything that decides WHAT goes in the pool, but NOT the placement
    fill) over N pinned seeds, for each N in a sweep (default 100, 1000). For
    every seed it records the resulting pool make-up and the wall-time, then
    aggregates per-N so you can watch the numbers converge as N grows and spot
    seed-to-seed variance.

    It stops at create_items on purpose: pool_builder only touches the pool
    (the LOCATION always stays a check, only the item on it changes), so the
    fill step -- the slow, region_lock-retry-prone part -- is irrelevant to
    what we're measuring here. That's why we can afford N=1000.

WHY
    "Run the pool builder for n=100, 1000, ... to see what it does at scale":
    convergence of the injected-juice mix + tier histogram, plus a feel for
    per-seed compose time.

RUN (Windows, from the Archipelago root, with your AP python 3.11+):
    python worlds/eldenring/tests/pool_builder_sweep.py
    python worlds/eldenring/tests/pool_builder_sweep.py --counts 100,1000,5000
    python worlds/eldenring/tests/pool_builder_sweep.py --intensity 2 --compare
    python worlds/eldenring/tests/pool_builder_sweep.py --curated --tag curated

    --counts     comma list of N to sweep (nested: the N=100 seed set is the
                 first 100 seeds of N=1000, so convergence is honest).  default 100,1000
    --intensity  pool_builder_intensity 0 normal / 1 high / 2 max.           default 0
    --curated    also turn curated_fill on (filler_upgrade_pct 50).
    --compare    ALSO run each seed with pool_builder OFF and report the delta
                 (juice injected vs the native pool). Doubles the run time.
    --dlc        enable_dlc on (default off, matching the pool_builder tests).
    --logic      world_logic (default region_lock).
    --junk       junk_retention (default 0).
    --seed-base  RNG base for reproducible seed sampling.  default 20260704
    --tag        label for the output filenames.           default poolbuild

OUTPUTS (Archipelago root)
    poolbuild_sweep_<tag>_<ts>.csv   one row per (N,seed): every metric + elapsed
    poolbuild_sweep_<tag>_<ts>.md    per-N summary: mean/stdev/min/max + convergence

    Determinism is relative to the apworld SOURCE (same contract as gen_sweep.ps1):
    edit the world and the same seed can move -- that's the point.
"""
import os
import sys
import csv
import time
import random
import argparse
import datetime
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
AP_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))  # worlds/eldenring/tests -> AP root
os.chdir(AP_ROOT)
if AP_ROOT not in sys.path:
    sys.path.insert(0, AP_ROOT)

from test.bases import WorldTestBase                    # noqa: E402
from worlds.eldenring.item_tiers import ITEM_TIERS      # noqa: E402

TIERS = ("S", "A", "B", "C", "D", "F")


class _Harness(WorldTestBase):
    """Minimal WorldTestBase subclass we drive by hand (not via unittest).

    run_default_tests off + a real (non-base) test method name so world_setup's
    base-class guard lets it run. auto_construct off so setUp does nothing --
    we call world_setup(seed) ourselves per seed.
    """
    game = "EldenRing"
    auto_construct = False
    run_default_tests = False

    def runTest(self):  # noqa: N802  -- satisfies TestCase ctor; never executed
        pass


def _classify(item):
    """(class_bucket, tier) for one pool item."""
    if item.advancement:
        bucket = "progression"
    elif getattr(item, "trap", False):
        bucket = "trap"
    elif item.useful:
        bucket = "useful"
    else:
        bucket = "filler"
    return bucket, ITEM_TIERS.get(item.name)


def measure_one(seed, options):
    """Compose the pool for one seed; return a flat metrics dict."""
    h = _Harness("runTest")
    h.options = dict(options)
    t0 = time.perf_counter()
    h.world_setup(seed)
    elapsed = time.perf_counter() - t0

    items = [i for i in h.multiworld.itempool if i.player == h.player]
    m = {
        "seed": seed,
        "elapsed_s": round(elapsed, 4),
        "total": len(items),
        "progression": 0, "useful": 0, "filler": 0, "trap": 0,
        "sa_juice_filler": 0,   # S/A-tier items classified filler == pool_builder's injected juice
        "pool_builder_local": int(getattr(h.world, "_pool_builder_local_count", 0)),
    }
    for t in TIERS:
        m["tier_" + t] = 0
    m["tier_none"] = 0
    for it in items:
        bucket, tier = _classify(it)
        m[bucket] += 1
        if tier in ("S", "A") and bucket == "filler":
            m["sa_juice_filler"] += 1
        m["tier_" + tier if tier in TIERS else "tier_none"] += 1
    return m


def sample_seeds(n, base):
    """n reproducible seeds; nested so smaller sweeps are prefixes of larger ones."""
    rng = random.Random(base)
    return [rng.getrandbits(48) for _ in range(n)]


def agg(rows, key):
    vals = [r[key] for r in rows]
    return {
        "mean": statistics.fmean(vals),
        "stdev": statistics.pstdev(vals) if len(vals) > 1 else 0.0,
        "min": min(vals),
        "max": max(vals),
        "median": statistics.median(vals),
    }


def main():
    ap = argparse.ArgumentParser(description="ER pool_builder scaling sweep")
    ap.add_argument("--counts", default="100,1000")
    ap.add_argument("--intensity", type=int, default=0, choices=(0, 1, 2))
    ap.add_argument("--curated", action="store_true")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--dlc", action="store_true")
    ap.add_argument("--logic", default="region_lock")
    ap.add_argument("--junk", type=int, default=0)
    ap.add_argument("--seed-base", type=int, default=20260704)
    ap.add_argument("--tag", default="poolbuild")
    args = ap.parse_args()

    counts = sorted({int(c) for c in args.counts.split(",") if c.strip()})
    max_n = max(counts)

    base_opts = {
        "enable_dlc": bool(args.dlc),
        "world_logic": args.logic,
        "junk_retention": args.junk,
    }
    on_opts = dict(base_opts, pool_builder=True, pool_builder_intensity=args.intensity)
    off_opts = dict(base_opts, pool_builder=False)
    if args.curated:
        on_opts["curated_fill"] = True
        on_opts["filler_upgrade_pct"] = 50

    seeds = sample_seeds(max_n, args.seed_base)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    csv_path = os.path.join(AP_ROOT, f"poolbuild_sweep_{args.tag}_{ts}.csv")
    md_path = os.path.join(AP_ROOT, f"poolbuild_sweep_{args.tag}_{ts}.md")

    metric_keys = ["elapsed_s", "total", "progression", "useful", "filler", "trap",
                   "sa_juice_filler", "pool_builder_local"] + \
                  ["tier_" + t for t in TIERS] + ["tier_none"]
    if args.compare:
        metric_keys += ["off_sa_juice_filler", "juice_injected"]

    all_rows = []       # per (N-bucket, seed) for CSV
    per_n_rows = {}     # N -> list of metric dicts (measured once, reused for nested Ns)
    measured = []       # metrics for the seeds measured so far (index-aligned to seeds)

    print(f"[pool_builder_sweep] intensity={args.intensity} curated={args.curated} "
          f"compare={args.compare} dlc={args.dlc} logic={args.logic} junk={args.junk}")
    print(f"[pool_builder_sweep] sweeping N={counts} (max {max_n} seeds), base={args.seed_base}")

    t_start = time.perf_counter()
    for i, seed in enumerate(seeds):
        m = measure_one(seed, on_opts)
        if args.compare:
            mo = measure_one(seed, off_opts)
            m["off_sa_juice_filler"] = mo["sa_juice_filler"]
            m["juice_injected"] = m["sa_juice_filler"] - mo["sa_juice_filler"]
        measured.append(m)
        if (i + 1) % 50 == 0 or (i + 1) == max_n:
            print(f"  {i + 1}/{max_n} seeds  (elapsed {time.perf_counter() - t_start:0.1f}s)")

    for n in counts:
        per_n_rows[n] = measured[:n]
        for r in measured[:n]:
            row = {"N": n}
            row.update(r)
            all_rows.append(row)

    # ---- CSV ----
    fieldnames = ["N", "seed"] + metric_keys
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in all_rows:
            w.writerow(row)

    # ---- MD summary ----
    headline = ["total", "filler", "useful", "progression", "sa_juice_filler",
                "pool_builder_local", "elapsed_s"]
    if args.compare:
        headline.insert(5, "juice_injected")
    lines = []
    lines.append(f"# pool_builder scaling sweep -- {ts}")
    lines.append("")
    lines.append(f"- intensity **{args.intensity}**, curated_fill **{args.curated}**, "
                 f"enable_dlc **{args.dlc}**, world_logic **{args.logic}**, "
                 f"junk_retention **{args.junk}**, compare **{args.compare}**")
    lines.append(f"- seed base `{args.seed_base}`, sweep `N={counts}` (nested: N=k is the first k seeds)")
    lines.append(f"- stopped at `create_items` (pool composition only; no fill)")
    lines.append("")
    lines.append("## Convergence (mean +/- population stdev across the N seeds)")
    lines.append("")
    header = "| N | " + " | ".join(headline) + " |"
    sep = "|" + "---|" * (len(headline) + 1)
    lines.append(header)
    lines.append(sep)
    for n in counts:
        cells = [str(n)]
        for k in headline:
            a = agg(per_n_rows[n], k)
            if k == "elapsed_s":
                cells.append(f"{a['mean']:.3f} +/- {a['stdev']:.3f}")
            else:
                cells.append(f"{a['mean']:.1f} +/- {a['stdev']:.1f}")
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    # full stat block for the largest N
    lines.append(f"## Full metric spread at N={max_n} (min / median / mean / max, pop-stdev)")
    lines.append("")
    lines.append("| metric | min | median | mean | max | stdev |")
    lines.append("|---|---|---|---|---|---|")
    for k in metric_keys:
        a = agg(per_n_rows[max_n], k)
        fmt = (lambda v: f"{v:.3f}") if k == "elapsed_s" else (lambda v: f"{v:g}")
        lines.append(f"| {k} | {fmt(a['min'])} | {fmt(a['median'])} | "
                     f"{a['mean']:.2f} | {fmt(a['max'])} | {a['stdev']:.2f} |")
    lines.append("")
    total_wall = time.perf_counter() - t_start
    lines.append(f"_Total compose runs: {len(measured)}{' x2 (compare)' if args.compare else ''}; "
                 f"wall {total_wall:0.1f}s._")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\n[pool_builder_sweep] wrote:\n  {csv_path}\n  {md_path}")
    # echo the convergence table to console too
    print("\n".join(lines[lines.index(header):]))


if __name__ == "__main__":
    sys.exit(main())
