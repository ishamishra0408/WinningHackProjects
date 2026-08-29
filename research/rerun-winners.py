#!/usr/bin/env python3
"""Re-run the three contracts against the 28 winning repos, and report the CAPS.

    python3 research/rerun-winners.py --clones /tmp/winners

The matrix in winner-audits.md answers "which thresholds did each winner miss?".
This answers the later question: "given the machine-readable `Caps at` column,
what CEILING does each scope land on?" They are different questions -- a failed
task only matters to a score if the contract says it caps something.

--clones points at a directory holding one clone per manifest `dir`. Without it
each repo is cloned fresh, which is correct but slow. A repo that is missing or
404s is reported as SKIPPED and excluded from every denominator: a repo we could
not read is a fact about our access, not about the project.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "api"))

import runners  # noqa: E402

MANIFEST = ROOT / "research" / "winners-28.json"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--clones", help="directory of existing clones, keyed by manifest 'dir'")
    ap.add_argument("--json", help="write the full per-repo result here")
    args = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text())
    capped = collections.Counter()
    at_level = collections.defaultdict(collections.Counter)
    blocking_fails = collections.Counter()
    rows, skipped = [], []

    for entry in manifest:
        local = None
        if args.clones:
            local = os.path.join(args.clones, entry["dir"])
            if not os.path.isdir(os.path.join(local, ".git")):
                skipped.append(entry["name"])
                continue
        # criteria_source is left unset on purpose: we did not read these events'
        # criteria, and an unknown must not cap. Same for starter_sha, except the
        # two Neo4j repos the writeup names as sharing the organizers' starter.
        result = runners.audit_repo(entry["repo_url"], local_path=local)
        if "tasks" not in result:
            skipped.append(f"{entry['name']} ({result.get('error')})")
            continue
        scopes = runners.summarise(result["tasks"])
        row = {"name": entry["name"], "event": entry["event"], "medal": entry["medal"],
               "caps": {k: v["cap"] for k, v in scopes.items()},
               "failed_blocking": sorted({t for v in scopes.values()
                                          for t in v["failed_blocking"]})}
        for scope, cap in row["caps"].items():
            if cap:
                capped[scope] += 1
                at_level[scope][cap] += 1
        for tid in row["failed_blocking"]:
            blocking_fails[tid] += 1
        rows.append(row)
        print(f"{entry['medal']} {entry['name'][:28]:<30} "
              + "  ".join(f"{s[0].upper()}={row['caps'][s] or '-':<10}"
                          for s in ("value", "usability", "feasibility")))

    n = len(rows)
    print(f"\n{n} audited, {len(skipped)} skipped: {', '.join(skipped) or 'none'}")
    for scope in ("value", "usability", "feasibility"):
        levels = ", ".join(f"{c} at {lv}" for lv, c in sorted(at_level[scope].items()))
        print(f"  {scope:<12} capped {capped[scope]}/{n}" + (f"  ({levels})" if levels else ""))
    print("  failed blocking tasks: "
          + ", ".join(f"{t} {c}/{n}" for t, c in blocking_fails.most_common()))

    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(
            {"audited": n, "skipped": skipped, "rows": rows}, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
