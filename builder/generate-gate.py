#!/usr/bin/env python3
"""Regenerate the checkbox lines in pre-submit-gate.md from the scope contracts.

Run from the repo root:  python3 builder/generate-gate.py

The gate has two owners and this script keeps them apart.

  scopes/*.md own    every threshold value.  Change 20% to 15% there and only there.
  this directory owns the section grouping, the order within a section, the prose,
                     the bash blocks, and the editorial NOTES below.

Only the lines between `<!-- checks: ... -->` and `<!-- /checks -->` are rewritten.
Everything else in the gate is left exactly as written. The script is idempotent:
running it on an already-current gate changes nothing and exits 0.
"""

import pathlib
import re
import sys
import textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent
GATE = ROOT / "builder" / "pre-submit-gate.md"
CONTRACTS = ["scopes/value.md", "scopes/usability.md", "scopes/feasibility.md"]

# The gate's editorial voice, and the only place it lives. A threshold like
# "exits 0" is true but tells a builder at 2am nothing, so the note carries the
# context the contract's Threshold column cannot.
NOTES = {
    "U-6": "; *the single most common cheap failure*",
    "U-5": "; three *different* environments — 3/3 on three identical Linux runners is 1/1",
    "F-7": ", **twice**; passes once and fails once is a fail",
    "F-10": "; `npm ci` / `pip-compile --generate-hashes` / `go mod verify` / `cargo --locked`",
    "F-2c": "; **report both numbers** — a violation count with no commit total is not a share",
    "V-6": "; **report the LOC denominator** — a ratio over 40 lines is not a ratio",
    "F-6": "; published seed. The authorship test, and the one an AI-heavy build fails.",
}


def read_contracts() -> dict[str, tuple[str, str, bool]]:
    """Map task id -> (task, threshold, blocking), read from the contracts' task tables."""
    tasks: dict[str, tuple[str, str, bool]] = {}
    for rel in CONTRACTS:
        for line in (ROOT / rel).read_text().splitlines():
            m = re.match(r"^\|\s*([VUF]-\d+[abc]?)\s*\|(.+)", line)
            if not m:
                continue
            cols = [c.strip() for c in m.group(2).split("|")]
            if len(cols) < 7:
                continue
            # the head of the Task column, before any em-dash gloss
            task = cols[0].split(" — ")[0].strip()
            # a task blocks when the Caps at column declares a cap
            blocking = bool(re.match(r"\s*(\d/5|unscorable|uncapped)", cols[6]))
            tasks[m.group(1)] = (task, cols[5], blocking)
    return tasks


def render(task_id: str, tasks: dict[str, tuple[str, str, bool]]) -> str:
    """A threshold alone ("breaks", "exits 0") has no subject, so the task names it."""
    task, threshold, blocking = tasks[task_id]
    lock = "🔒 " if blocking else ""
    body = f"- [ ] {lock}`{task_id}` {task} — {threshold}{NOTES.get(task_id, '')}"
    return "\n".join(textwrap.wrap(body, width=98, subsequent_indent="      "))


# A threshold's value belongs to its contract. These are the only other files
# allowed to carry one, and each has a stated reason.
ALLOWED = {
    "scopes/value.md", "scopes/usability.md", "scopes/feasibility.md",   # the owners
    "evaluator/scorecard-TEMPLATE.md",   # the single ID decoder, per scopes/README.md
    "scopes/README.md",                  # the provenance table's historical record
    "builder/pre-submit-gate.md",        # generated between the markers, by this script
}


def check_drift(tasks: dict[str, tuple[str, str, bool]]) -> list[str]:
    """Report threshold values that have grown a second home."""
    tokens = set()
    for _, threshold, _ in tasks.values():
        tokens |= set(re.findall(r"[<>≥≤±]\s*\d+\s*(?:%|min|h\b)|\b\d+/\d+\b", threshold))
    findings = []
    for path in sorted(ROOT.rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        if rel in ALLOWED or ".git" in rel:
            continue
        text = path.read_text()
        hits = sorted({t for t in tokens if t in text})
        if hits:
            findings.append(f"{rel}: {', '.join(hits)}")
    return findings


# ---- derived counts ---------------------------------------------------------
# Thresholds, weights and caps each got one home and a reader. The counts ABOUT
# them did not, and drifted the same way: the README said "21 blocking" while
# the contracts said 22. Prose cannot be templated without littering markers, so
# these are CHECKED rather than generated -- the drift is caught, the wording
# stays a human's.
COUNT_CLAIMS = [
    (r"(\d+) (?:audit )?tasks\b", "tasks"),
    (r"(\d+) blocking\b", "blocking"),
    (r"(\d+) of the (\d+) are ABSENT", "absent_of_total"),
    (r"(\d+) of (\d+) audit tasks", "covered_of_total"),
]


def derived_counts(tasks: dict) -> dict[str, int]:
    return {"tasks": len(tasks),
            "blocking": sum(1 for t in tasks.values() if t[2])}


def check_counts(tasks: dict) -> list[str]:
    """Every count a markdown file claims about the contracts must match them."""
    truth = derived_counts(tasks)
    findings = []
    for path in sorted(ROOT.rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        if ".git" in rel:
            continue
        text = path.read_text()
        for m in re.finditer(r"(\d+) tasks?,?\s*\*{0,2}(\d+) blocking", text):
            if (int(m.group(1)), int(m.group(2))) != (truth["tasks"], truth["blocking"]):
                findings.append(f"{rel}: claims {m.group(1)} tasks / {m.group(2)} blocking, "
                                f"contracts say {truth['tasks']} / {truth['blocking']}")
        for m in re.finditer(r"\b(\d+) audit tasks\b", text):
            if int(m.group(1)) != truth["tasks"]:
                findings.append(f"{rel}: claims {m.group(1)} audit tasks, contracts say {truth['tasks']}")
        for m in re.finditer(r"of the (\d+) are ABSENT|of (\d+) audit tasks|(\d+) tasks V-\*", text):
            n = next((g for g in m.groups() if g), None)
            if n and int(n) != truth["tasks"]:
                findings.append(f"{rel}: '{m.group(0)}' but contracts have {truth['tasks']} tasks")
    return findings


def main() -> int:
    tasks = read_contracts()
    text = GATE.read_text()
    unknown: list[str] = []

    def replace(match: re.Match[str]) -> str:
        ids = match.group(1).split()
        missing = [i for i in ids if i not in tasks]
        unknown.extend(missing)
        lines = [render(i, tasks) for i in ids if i in tasks]
        return f"<!-- checks: {match.group(1)} -->\n" + "\n".join(lines) + "\n<!-- /checks -->"

    out = re.sub(
        r"<!-- checks: ([^>]+?) -->\n.*?\n<!-- /checks -->",
        replace,
        text,
        flags=re.DOTALL,
    )

    if unknown:
        print(f"error: not in any contract: {', '.join(sorted(set(unknown)))}", file=sys.stderr)
        return 1

    changed = out != text
    GATE.write_text(out)
    print(f"{GATE.relative_to(ROOT)}: {'rewritten' if changed else 'already current'} "
          f"({len(tasks)} tasks read from {len(CONTRACTS)} contracts)")

    counts = check_counts(tasks)
    if counts:
        print("\ncounts that disagree with the contracts:", file=sys.stderr)
        for c in counts:
            print(f"  {c}", file=sys.stderr)
        return 1

    drift = check_drift(tasks)
    if drift:
        print("\nthreshold values found outside their contract:", file=sys.stderr)
        for d in drift:
            print(f"  {d}", file=sys.stderr)
        return 1
    print("no threshold value has a second home; every claimed count matches the contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
