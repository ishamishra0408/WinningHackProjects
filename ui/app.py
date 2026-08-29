#!/usr/bin/env python3
"""Streamlit front end for the two layers.

    Evaluate a project   github link + event link -> per-metric value and reason
    Evaluate a spec      spec + build plan + event link -> winnable? why / why not

Run:  streamlit run ui/app.py

Layout, chosen on the merits rather than copied from a gallery app: a sidebar
form for the two or three inputs, a verdict banner, a metric row, then one
expander per scope carrying every metric with its value AND the reason. The
reason column is the point -- a score with no reason is the thing this repo
exists to refuse.

This file renders. It computes no verdict: every number comes from api/runners.py
and api/spec.py, which read the contracts at call time. A second implementation
of the scoring here would be a second home for it.
"""

from __future__ import annotations

import pathlib
import sys

import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "api"))

import runners  # noqa: E402
import spec as spec_mod  # noqa: E402

STATE_HELP = {
    "MEASURED": "the check ran and produced a value",
    "ABSENT": "a fact about the subject — the thing being measured is not there",
    "UNEVALUABLE": "a fact about the instrument — this check needs something we do not have here",
}
BADGE = {"PASS": "🟢", "FAIL": "🔴", None: "⚪"}

# The design layer asks yes/no questions whose answers are DECLARATIONS, not
# measurements: nothing exists yet to measure. Each row is (the field spec.py
# reads, what the operator is confirming, words that pre-tick it from the prose).
DECLARATIONS = [
    ("prior_art", "We spent 15 minutes on prior art and wrote the delta sentence",
     ("prior art", "existing tool", "delta")),
    ("real_call", "A real API call sits on the demo path", ("api", "endpoint", "real call")),
    ("claim_declared", "The number we will claim is written down first", ("claim", "number")),
    ("demo_slot", "The demo is recorded before the last hour", ("demo", "record", "video")),
    ("operators_reserved", "Naive operators are reserved", ("operator", "tester", "naive")),
    ("one_click_and_envs", "One command starts it, env vars documented",
     ("one-click", "docker compose", "devcontainer")),
    ("day1_infra", "Dockerfile, lockfile and CI land on day 1", ("dockerfile", "lockfile", "ci")),
    ("prior_code_declared", "Starter or prior code is declared up front",
     ("starter", "prior code", "existing repo")),
    ("start_in_window", "We start at or after the window opens", ("window", "kickoff")),
    ("roster_ok", "Every contributor is on the entrant roster", ("roster", "registered")),
    ("payoff_surface", "The payoff is visible on one screen", ("screen", "page", "ui", "dashboard")),
    ("demo_modules", "The demo path crosses more than one module", ("module", "service")),
    ("stub_replacement", "Every stub has a named replacement", ("stub", "mock")),
    ("read_rate", "Someone else reads the code before submit", ("review", "read")),
    ("readme_alongside", "The README is written alongside the code", ("readme",)),
]


def _scan(plan_text: str, words: tuple) -> bool:
    """Pre-tick a box. A keyword cannot see a negation, so this only suggests."""
    low = plan_text.lower()
    return any(w in low for w in words)


st.set_page_config(page_title="WinningHackProjects", page_icon="🏆", layout="wide")


@st.cache_data(show_spinner=False)
def contract_meta() -> tuple[int, int, dict]:
    tasks = runners.load_tasks()
    return len(tasks), sum(1 for t in tasks.values() if t["blocking"]), runners.load_weights()


TASKS, BLOCKING, WEIGHTS = contract_meta()


def scope_header(name: str, summary: dict) -> None:
    cap = summary["cap"]
    if cap == "unscorable":
        st.error(f"**{name.title()} — UNSCORABLE.** A task whose absence makes the scope "
                 f"unmeasurable failed. This is *never measured*, not *measured and bad*.")
    elif cap:
        st.warning(f"**{name.title()} — capped at {cap}** by {', '.join(summary['failed_blocking'])}")
    else:
        st.success(f"**{name.title()} — no cap triggered** by anything we could measure")
    if summary.get("score_is_a_ceiling_because"):
        st.caption(f"⚠️ This is a **ceiling, not a score**. "
                   f"{len(summary['score_is_a_ceiling_because'])} blocking tasks did not run: "
                   f"{', '.join(summary['score_is_a_ceiling_because'])}")


def metric_rows(tasks: dict, scope: str) -> list[dict]:
    out = []
    for tid, t in sorted(tasks.items()):
        if t["scope"] != scope:
            continue
        val = t["value"]
        if isinstance(val, dict):
            shown = " · ".join(f"{k}={v}" for k, v in val.items() if v is not None and k != "note")
        else:
            shown = "—" if val is None else str(val)
        out.append({
            "": BADGE.get(t["verdict"], "⚪"),
            "Metric": f"{tid} — {t['task']}",
            "Must be": t["threshold"],
            "Value": shown or "—",
            "State": t["state"],
            "Reason": t.get("reason") or t.get("cap_demoted_because")
                      or STATE_HELP.get(t["state"], ""),
            "Caps at": t["cap"] or "—",
        })
    return out


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.title("🏆 WinningHackProjects")
    st.caption(f"{TASKS} audit tasks · {BLOCKING} blocking · {len(spec_mod.ROWS)} design checks\n\n"
               f"weights {WEIGHTS['value']}/{WEIGHTS['usability']}/{WEIGHTS['feasibility']}")
    mode = st.radio("What do you want to do?",
                    ["Evaluate a project", "Evaluate a spec"],
                    captions=["A repo that exists — what holds up",
                              "A plan that does not — will it be winnable"])
    st.divider()

    if mode == "Evaluate a project":
        repo_url = st.text_input("GitHub link", placeholder="https://github.com/owner/repo")
        event_url = st.text_input("Event link", placeholder="https://luma.com/…")
        with st.expander("Event details that change the verdict"):
            window_end = st.text_input("Submission deadline (YYYY-MM-DD)", "")
            window_days = st.number_input("Window length in days", 1, 60, 1)
            criteria_source = st.selectbox(
                "Where did the judging criteria come from?",
                ["not stated", "published", "inferred", "research-fallback"],
                help="V-2 caps at 2/5 only when the event PUBLISHED its criteria. Criteria you "
                     "inferred from a deck are your bar, not the event's, so they cannot cap.")
            starter_sha = st.text_input("Organizer starter-repo SHA (if any)", "",
                                        help="F-3 then measures from the team's own first commit.")
            demo_url = st.text_input("Demo video / deck URL (if submitted outside the repo)", "")
        go = st.button("Evaluate project", type="primary", width="stretch")
    else:
        event_url = st.text_input("Event link", placeholder="https://luma.com/…")
        c1, c2 = st.columns(2)
        criteria_found = c1.number_input("Criteria the event published", 0, 12, 0)
        criteria_covered = c2.number_input("…your plan has a mechanism for", 0, 12, 0)
        c3, c4, c5 = st.columns(3)
        team_size = c3.number_input("Team size", 1, 10, 3)
        event_hours = c4.number_input("Build hours", 1.0, 400.0, 8.0)
        planned = c5.number_input("Planned person-hours", 0.0, 2000.0, 24.0)
        spec_text = st.text_area("Spec — what is the one-sentence payoff?", height=80,
                                 placeholder="A stranger can see X happen without you present")
        build_plan = st.text_area("Build plan — one line per day-1 commitment", height=120,
                                  placeholder="real API call on the demo path\n"
                                              "Dockerfile + lockfile + CI\n"
                                              "demo recorded by 4pm, not the last hour\n"
                                              "2 naive operators reserved: …")
        st.caption("**Confirm each commitment below.** A box is pre-ticked by scanning the plan "
                   "for a keyword, and a keyword cannot read a negation — *no Dockerfile yet* "
                   "scans the same as *Dockerfile on day 1*. The scan suggests; the tick is the "
                   "declaration, and only the tick is sent.")
        commitments = {}
        for field, label, words in DECLARATIONS:
            commitments[field] = st.checkbox(
                label, value=_scan(f"{spec_text}\n{build_plan}", words))
        go = st.button("Evaluate spec", type="primary", width="stretch")

# ---------------------------------------------------------------- project
if mode == "Evaluate a project":
    st.header("Evaluate a project")
    st.caption("Runs every contract task computable from a clone. Everything else returns "
               "UNEVALUABLE — which is **not** a pass.")
    if go:
        if not repo_url.strip():
            st.error("A GitHub link is required.")
            st.stop()
        with st.spinner("Cloning and running the probes…"):
            result = runners.audit_repo(
                repo_url.strip(),
                window_end=window_end.strip() or None,
                window_days=int(window_days),
                starter_sha=starter_sha.strip() or None,
                demo_artifact={"url": demo_url.strip()} if demo_url.strip() else None,
                criteria_source=None if criteria_source == "not stated" else criteria_source)
        if "tasks" not in result:
            st.error(f"{result.get('error')} — {result.get('detail','')}")
            st.stop()
        tasks = result["tasks"]
        scopes = runners.summarise(tasks)

        caps = [s["cap"] for s in scopes.values() if s["cap"]]
        if caps:
            st.error(f"### Does not hold up — {len(caps)} of 3 scopes capped")
        else:
            st.success("### Nothing we could measure caps this project")
        st.caption("This says whether a project **holds up**, not whether it wins. "
                   "28 winning repos fail these contracts.")

        m = st.columns(5)
        m[0].metric("Commits", result.get("commits", "—"))
        m[1].metric("Own LOC", f"{result.get('own_loc', 0):,}")
        m[2].metric("Vendored LOC", f"{result.get('vendored_loc', 0):,}",
                    help="Excluded from every LOC denominator — checked-in deps are not your code.")
        m[3].metric("Measured", sum(s["measured"] for s in scopes.values()))
        m[4].metric("Could not run", sum(s["unevaluable"] for s in scopes.values()),
                    help="UNEVALUABLE — needs Docker, an operator, or the GitHub Events API.")

        for name, summary in scopes.items():
            with st.expander(f"{name.title()} — weight {WEIGHTS[name]}", expanded=True):
                scope_header(name, summary)
                st.dataframe(metric_rows(tasks, name), width="stretch", hide_index=True)

        st.info("**No overall score.** Every scope has blocking tasks that did not run here, so "
                "each cap is a ceiling rather than a score. Weights are "
                f"{WEIGHTS['value']}/{WEIGHTS['usability']}/{WEIGHTS['feasibility']}, from the "
                "scopes table, read at call time.")

# ---------------------------------------------------------------- spec
else:
    st.header("Evaluate a spec")
    st.caption("Runs the design checks against a plan that does not exist yet. "
               "This is the layer you can **solve for**.")
    if go:
        payload = {
            "event": {"criteria_found": int(criteria_found) or None,
                      "team_size": int(team_size), "event_hours": float(event_hours)},
            "plan": {"criteria_covered": int(criteria_covered) or None,
                     "planned_person_hours": float(planned) or None,
                     "payoff_sentence": spec_text.strip(),
                     **commitments},
        }
        results = spec_mod.evaluate(payload)
        by_scope = spec_mod.strengths_and_weaknesses(results)
        flow = spec_mod.workflow(results)

        weak = sum(len(v["weak"]) for v in by_scope.values())
        unknown = sum(len(v["not_stated"]) for v in by_scope.values())
        if weak == 0 and unknown == 0:
            st.success("### Winnable — yes, on everything checkable before you build")
        elif weak == 0:
            st.warning(f"### Not yet answerable — {unknown} checks are not stated in the plan")
        else:
            st.error(f"### Not winnable as written — {weak} checks fail, {unknown} unstated")

        st.caption("**Why:** every row below names the audit task it buys. A check left undone "
                   "is a task you will fail later, when it is too late to fix.")

        cols = st.columns(3)
        for col, (name, v) in zip(cols, by_scope.items()):
            col.metric(f"{name.title()} (weight {WEIGHTS[name]})", v["verdict"],
                       delta=f"{len(v['strong'])} strong / {len(v['weak'])} weak",
                       delta_color="off")

        if flow:
            st.subheader("Do this, in this order")
            for step in flow:
                with st.expander(f"Step {step['step']} — {step['gate']}", expanded=step["step"] <= 3):
                    st.dataframe(
                        [{"Row": d["row"], "Therefore today I will…": d["therefore_today_i_will"],
                          "Buys": " ".join(d["buys"]), "Strength": d["strength"]}
                         for d in step["do"]],
                        width="stretch", hide_index=True)

        st.subheader("Every design check")
        st.dataframe(
            [{"": BADGE.get(r["verdict"], "⚪"), "Row": r["row"], "Check": r["check"],
              "Buys": " ".join(r["buys"]), "State": r["state"],
              "Strength": r["strength"],
              "Value": "—" if r["value"] is None else str(r["value"])} for r in results],
            width="stretch", hide_index=True)

        st.info(f"**{sum(1 for r in results if r['strength']=='STRONG')} of {len(results)} checks "
                "are mechanical** — same event page and plan, same answer. The rest are "
                "declarations and are reported, never scored. This is **not pooled** with the "
                "project audit: different units, no combined score.")
