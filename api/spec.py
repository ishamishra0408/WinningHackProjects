"""The design layer, served: given an event and a plan, what to do about it.

This is the instrument you can solve for. `runners.py` reads a repo that already
exists; this one reads a plan that does not, and returns the ordered work that
makes it clear the bar.

The two are never pooled into one score -- their units differ, and a design card
that reads well is not a prediction that the project will pass an audit.
"""

from __future__ import annotations

# The 19 checks, in the order designer/README.md runs them. Each names the
# ex-post task it buys, so a weak row points at what it will cost later.
# STRONG = mechanical from the event page and the plan. WEAK = a declaration
# you make now and cannot verify until later; reported, never scored.
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

# The 19 checks live in ONE home: designer/README.md's per-scope tables, parsed
# here at import. They were duplicated in this file and drifted -- the README
# claimed "14 of 19 STRONG" while its own rows counted 16. runners.py reads the
# contracts the same way; this is the same rule applied to the design layer.
STEP_OF = {"D1": 1, "D13": 1, "D5": 2, "D10": 2, "D14": 2, "D15": 2, "D19": 2,
           "D2": 3, "D3": 3, "D6": 3, "D4": 4, "D7": 4, "D8": 4, "D12": 4, "D17": 4,
           "D11": 5, "D9": 6, "D16": 6, "D18": 6}
FIELD_OF = {"D1": "criteria_found", "D2": "criteria_covered", "D3": "prior_art",
            "D4": "real_call", "D5": "payoff_sentence", "D6": "scope_ratio",
            "D7": "payoff_surface", "D8": "demo_modules", "D9": "stub_replacement",
            "D10": "claim_declared", "D11": "operators_reserved", "D12": "one_click_and_envs",
            "D13": "roster_ok", "D14": "start_in_window", "D15": "prior_code_declared",
            "D16": "read_rate", "D17": "day1_infra", "D18": "readme_alongside",
            "D19": "demo_slot"}


def _load_rows() -> list[tuple]:
    text = (ROOT / "designer" / "README.md").read_text()
    rows = []
    for m in re.finditer(r"^\|\s*`(D\d+)`\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(STRONG|WEAK)\s*\|",
                         text, re.M):
        rid, desc, buys, strength = m.groups()
        rows.append((rid, STEP_OF[rid], strength, FIELD_OF[rid],
                     " ".join(re.findall(r"`([VUF]-\d+[abc]?)`", buys)),
                     re.sub(r"\*\*|`", "", desc)))
    return sorted(rows, key=lambda r: (r[1], list(STEP_OF).index(r[0])))


ROWS = _load_rows()


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
