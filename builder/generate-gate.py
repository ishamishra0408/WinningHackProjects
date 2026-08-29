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
            tasks[m.group(1)] = (task, cols[5], "✅" in cols[6])
    return tasks


def render(task_id: str, tasks: dict[str, tuple[str, str, bool]]) -> str:
    """A threshold alone ("breaks", "exits 0") has no subject, so the task names it."""
    task, threshold, blocking = tasks[task_id]
    lock = "🔒 " if blocking else ""
    body = f"- [ ] {lock}`{task_id}` {task} — {threshold}{NOTES.get(task_id, '')}"
    return "\n".join(textwrap.wrap(body, width=98, subsequent_indent="      "))


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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
