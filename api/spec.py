"""The design layer, served: given an event and a plan, what to do about it.

This is the instrument you can solve for. `runners.py` reads a repo that already
exists; this one reads a plan that does not, and returns the ordered work that
makes it clear the bar.

The two are never pooled into one score -- their units differ, and a design card
that reads well is not a prediction that the project will pass an audit.
"""

from __future__ import annotations

import re

# The 19 checks, in the order designer/README.md runs them. Each names the
# ex-post task it buys, so a weak row points at what it will cost later.
# STRONG = mechanical from the event page and the plan. WEAK = a declaration
# you make now and cannot verify until later; reported, never scored.
ROWS = [
    ("D1",  1, "STRONG", "criteria_found",        "V-1",        "count of published judging criteria"),
    ("D13", 1, "STRONG", "roster_ok",             "F-1 F-4",    "window fixed, every contributor on the entrant roster"),
    ("D5",  2, "STRONG", "payoff_sentence",       "U-1",        "the payoff in one sentence, observable without you"),
    ("D10", 2, "STRONG", "claim_declared",        "V-8 V-9",    "the number you intend to claim, written before building"),
    ("D14", 2, "STRONG", "start_in_window",       "F-2a F-2b",  "committed build start at or after window open"),
    ("D15", 2, "STRONG", "prior_code_declared",   "F-3",        "LOC of starter or prior code you will import"),
    ("D19", 2, "STRONG", "demo_slot",             "V-10",       "a slot for recording the demo, not the last hour"),
    ("D2",  3, "STRONG", "criteria_covered",      "V-2",        "criteria your plan names a mechanism for"),
    ("D3",  3, "STRONG", "prior_art",             "V-7",        "closest existing tools, plus a delta sentence"),
    ("D6",  3, "STRONG", "scope_ratio",           "F-5 F-12",   "planned hours over (team size x event hours)"),
    ("D4",  4, "STRONG", "real_call",             "V-3 V-4",    ">=1 authenticated external call the demo executes"),
    ("D7",  4, "STRONG", "payoff_surface",        "U-9",        "the single screen the payoff appears on"),
    ("D8",  4, "STRONG", "demo_modules",          "V-5",        ">=2 planned files on the demo path"),
    ("D12", 4, "STRONG", "one_click_and_envs",    "U-4 U-5",    "one-click entry, and 3 DISTINCT environments named"),
    ("D17", 4, "STRONG", "day1_infra",            "F-7 F-8 F-9 F-10", "Dockerfile, lockfile and CI in day-1 scope"),
    ("D11", 5, "STRONG", "operators_reserved",    "U-2 U-12",   ">=2 naive operators reserved by name, unburned"),
    ("D9",  6, "WEAK",   "stub_replacement",      "V-6",        "every demo-path stub has a replacement slot"),
    ("D16", 6, "WEAK",   "read_rate",             "F-6",        "share of shipped code you will actually read"),
    ("D18", 6, "WEAK",   "readme_alongside",      "U-3 U-6",    "README written alongside the build, not after"),
]

STEP_GATE = {
    1: "criteria ABSENT -> substitute the research fallback and record it; roster mismatch -> STOP, you cannot enter",
    2: "free now, unrecoverable later",
    3: "the go / no-go",
    4: "day-1 build commitments",
    5: "operators expire on first contact",
    6: "declarations -- restate them, do not score them",
}

SCOPE_OF = {"V": "value", "U": "usability", "F": "feasibility"}

# What to do today when a row is not satisfied. A ranking that does not end in
# an action is not built -- so every row carries one.
ACTION = {
    "D1":  "extract the criteria from the event page; if it publishes none, fall back to the topic's winners and record the substitution",
    "D2":  "add a named mechanism for each criterion you do not yet cover",
    "D3":  "spend 15 minutes on prior art and write the one-sentence delta",
    "D4":  "wire one real authenticated call on the demo path before any UI",
    "D5":  "cut scope until the payoff fits one sentence a stranger can check",
    "D6":  "cut scope -- the plan does not fit the window",
    "D7":  "name the single screen the payoff appears on, and design it first",
    "D8":  "split the demo across at least two files",
    "D9":  "put a replacement date against every stub on the demo path",
    "D10": "write down the number you intend to claim, now, before measuring",
    "D11": "reserve two naive operators by name today",
    "D12": "name the one-click entry and three genuinely different environments",
    "D13": "fix the window and check every contributor is on the roster",
    "D14": "commit to starting at or after window open",
    "D15": "declare the LOC of any starter or prior code you are importing",
    "D16": "commit to a read-rate for generated code",
    "D17": "put Dockerfile, lockfile and CI in day-1 scope",
    "D18": "assign the README to someone, starting day 1",
    "D19": "put the demo recording in the plan, not in the last hour",
}


def evaluate(spec: dict) -> dict:
    """Score a plan against the 19 checks and return the ordered work."""
    plan = spec.get("plan") or {}
    event = spec.get("event") or {}
    given = {**event, **plan}

    criteria_found = given.get("criteria_found")
    criteria_covered = given.get("criteria_covered")
    team = given.get("team_size")
    hours = given.get("event_hours")
    planned = given.get("planned_person_hours")

    def truthy(key):
        v = given.get(key)
        if v is None:
            return None
        if isinstance(v, str):
            return bool(v.strip())
        if isinstance(v, (list, dict)):
            return bool(v)
        return bool(v)

    results = []
    for rid, step, strength, key, buys, desc in ROWS:
        state, value, verdict = "ABSENT", None, None
        if rid == "D1":
            if criteria_found is None:
                state, verdict = "ABSENT", None
            else:
                state, value = "MEASURED", {"criteria_found": criteria_found}
                verdict = "PASS" if criteria_found >= 1 else "FAIL"
        elif rid == "D2":
            if criteria_found and criteria_covered is not None:
                state = "MEASURED"
                value = {"covered": criteria_covered, "found": criteria_found,
                         "share": round(criteria_covered / criteria_found, 3)}
                verdict = "PASS" if criteria_covered / criteria_found >= 0.75 else "FAIL"
            else:
                state = "ABSENT"
                value = {"note": "undefined while D1 is ABSENT -- not zero"}
        elif rid == "D6":
            if team and hours and planned:
                state = "MEASURED"
                ratio = planned / (team * hours)
                value = {"planned_person_hours": planned, "available": team * hours,
                         "ratio": round(ratio, 2),
                         "bias": "reads pessimistic under heavy AI codegen"}
                verdict = "PASS" if ratio <= 1.0 else "FAIL"
        else:
            t = truthy(key)
            if t is not None:
                state, value, verdict = "MEASURED", {key: given.get(key)}, "PASS" if t else "FAIL"

        results.append({"row": rid, "step": step, "strength": strength, "field": key,
                        "buys": buys.split(), "check": desc, "state": state,
                        "value": value, "verdict": verdict,
                        "action": ACTION[rid] if verdict != "PASS" else None})
    return results


def strengths_and_weaknesses(results: list[dict]) -> dict:
    """Per scope: what the plan already has, and what it will cost if left alone."""
    out = {}
    for letter, scope in SCOPE_OF.items():
        rows = [r for r in results if any(b.startswith(letter) for b in r["buys"])]
        strong = [r["row"] for r in rows if r["verdict"] == "PASS"]
        weak = [r for r in rows if r["verdict"] == "FAIL"]
        unknown = [r["row"] for r in rows if r["verdict"] is None]
        out[scope] = {
            "strong": strong,
            "weak": [{"row": r["row"], "check": r["check"],
                      "costs_you": r["buys"], "action": r["action"]} for r in weak],
            "not_stated": unknown,
            "verdict": "AT RISK" if weak else ("UNDERSPECIFIED" if unknown else "READY"),
        }
    return out


def workflow(results: list[dict]) -> list[dict]:
    """The ordered work: only the steps that still have something to do."""
    steps = []
    for step in sorted(STEP_GATE):
        todo = [r for r in results if r["step"] == step and r["verdict"] != "PASS"]
        if not todo:
            continue
        steps.append({
            "step": step,
            "gate": STEP_GATE[step],
            "do": [{"row": r["row"], "therefore_today_i_will": r["action"],
                    "strength": r["strength"], "buys": r["buys"],
                    "state": r["state"]} for r in todo],
        })
    return steps
