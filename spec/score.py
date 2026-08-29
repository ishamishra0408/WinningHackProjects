#!/usr/bin/env python3
"""The scoring function, executable — so the aggregation is checkable rather than asserted.

Run the self-test:  python3 spec/score.py --selftest
Score one audit:    python3 spec/score.py evaluator/audits/<file>.json

This module owns the *arithmetic* of the merged verdict and nothing else. It holds no
threshold values: caps arrive already triggered, bands arrive already read. Which predicate
fires which cap is the contracts' business (scopes/*.md) — see spec/decision-math.md for why
that split is the one that matters.
"""

import json
import math
import sys

UNSCORABLE = "UNSCORABLE"

# The source contracts state two of the three weights and leave Value's unset. That is not an
# oversight to patch with a default here: a weight invented by the scorer is a weight chosen
# after the fact. W_VALUE_RANGE is what the source *does* pin down — 100 total, 45 allocated —
# so Value plus any uncaptured scope shares the remainder.
W_USABILITY = 25
W_FEASIBILITY = 20
W_VALUE_RANGE = (0, 100 - W_USABILITY - W_FEASIBILITY)


def scope_score(band, caps):
    """Caps compose by minimum: the score is the lowest ceiling any failure imposed.

    `band` is where the rubric put it; `caps` are the ceilings triggered. A cap never
    subtracts, so a project that earns 5 and trips a 2/5 cap scores 2 — not 3.
    """
    if band == UNSCORABLE:
        return UNSCORABLE
    return min([band] + list(caps))


def overall(scores, w_value, mode="arithmetic"):
    """Merge three /5 scope scores into one /5.

    Returns UNSCORABLE if any scope is — a missing target is not a low score, and averaging
    over it silently reports "measured and bad" for something never measured.

    mode="arithmetic"  the source contracts' weighted mean. Compensatory: a 5/5 elsewhere
                       buys back a 1/5 here.
    mode="geometric"   weighted geometric mean. Non-compensatory, and therefore the mode that
                       agrees with the cap model the rest of the instrument is built on.
    """
    if UNSCORABLE in scores.values():
        return UNSCORABLE
    w = {"value": w_value, "usability": W_USABILITY, "feasibility": W_FEASIBILITY}
    total = sum(w.values())
    if mode == "arithmetic":
        return 5 * sum(scores[k] / 5 * w[k] for k in w) / total
    if mode == "geometric":
        if any(scores[k] <= 0 for k in w):
            return 0.0
        return 5 * math.exp(sum(w[k] / total * math.log(scores[k] / 5) for k in w))
    raise ValueError(f"unknown mode: {mode}")


def crossover_w(a, b):
    """The one w_value at which projects a and b swap rank, or None if they never do.

    Ranking is invariant to w_value unless this lands inside W_VALUE_RANGE. When it does not,
    report that the choice of w_value did not change the answer and move on — which is a
    stronger result than defending a number nobody can source.
    """
    dv, du, df = (a[k] - b[k] for k in ("value", "usability", "feasibility"))
    if dv == 0:
        return None
    w = -(W_USABILITY * du + W_FEASIBILITY * df) / dv
    lo, hi = W_VALUE_RANGE
    return w if lo < w <= hi else None


def flake_detection(p, runs):
    """P(a probe that fails with probability p does not return the same verdict every time).

    This is what re-running buys. `runs: 2` in the contracts is an agreement check, not a
    determinism proof — see the table in spec/decision-math.md.
    """
    return 1 - p**runs - (1 - p) ** runs


def _selftest():
    checks = []

    def eq(name, got, want, tol=1e-9):
        checks.append((name, abs(got - want) < tol if isinstance(want, float) else got == want, got))

    # caps compose by min, and never subtract
    eq("cap takes the lowest ceiling", scope_score(5, [3, 2]), 2)
    eq("no cap leaves the band", scope_score(4, []), 4)
    eq("a cap above the band does nothing", scope_score(2, [3]), 2)
    eq("unscorable survives every cap", scope_score(UNSCORABLE, [1]), UNSCORABLE)

    # a perfect project scores 5 under both modes, at any weight
    perfect = {"value": 5, "usability": 5, "feasibility": 5}
    eq("arithmetic 5/5", overall(perfect, 55), 5.0)
    eq("geometric 5/5", overall(perfect, 55, "geometric"), 5.0)

    # the staged demo: Value capped at 1/5, everything else perfect
    staged = {"value": 1, "usability": 5, "feasibility": 5}
    eq("staged demo, arithmetic", overall(staged, 55), 2.8)
    eq("staged demo, geometric", overall(staged, 55, "geometric"), 5 * 0.2**0.55)

    # unscorable propagates rather than averaging away
    eq("unscorable propagates", overall({**perfect, "value": UNSCORABLE}, 55), UNSCORABLE)

    # rank stability
    eq("no crossover when Value ties", crossover_w(perfect, {**perfect, "usability": 4}), None)
    a = {"value": 4, "usability": 2, "feasibility": 2}
    b = {"value": 2, "usability": 4, "feasibility": 4}
    eq("crossover found", crossover_w(a, b), 45.0)

    eq("two runs on a 10% flake", flake_detection(0.1, 2), 0.18)
    eq("a clean probe never disagrees", flake_detection(0.0, 2), 0.0)

    for name, ok, got in checks:
        print(f"{'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f"  → got {got!r}"))
    failed = sum(1 for _, ok, _ in checks if not ok)
    print(f"\n{len(checks)} checks, {failed} failed")
    return 1 if failed else 0


def main(argv):
    if len(argv) == 2 and argv[1] == "--selftest":
        return _selftest()
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    audit = json.load(open(argv[1]))
    scores = {k: scope_score(v["band"], v.get("caps", [])) for k, v in audit["scopes"].items()}
    w = audit["w_value"]
    print(json.dumps({
        "scopes": scores,
        "w_value": w,
        "overall_arithmetic": overall(scores, w),
        "overall_geometric": overall(scores, w, "geometric"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
