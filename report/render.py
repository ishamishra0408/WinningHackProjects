#!/usr/bin/env python3
"""One PDF report, for either question.

    python3 report/render.py project --input body.json -o report.pdf
    python3 report/render.py spec    --input body.json -o report.pdf

`--input` takes exactly the body `api/app.py` accepts for the matching endpoint,
so the report and the endpoint cannot disagree about what an input means. There
is no second input format to keep in step.

HTML is built with the standard library. The PDF is printed by headless Chromium
if one can be found; when none can, the HTML is written and the reason is said
out loud rather than a PDF being silently skipped.

Every threshold, cap, weight and task name in the output is read from
scopes/*.md and designer/README.md at call time, through api/runners.py and
api/spec.py. This module lays out numbers it did not compute.
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
import os
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "api"))

import runners  # noqa: E402
import spec as spec_mod  # noqa: E402

# Where a headless Chromium may live. PLAYWRIGHT_BROWSERS_PATH is checked first
# because an environment that sets it has already chosen its browser.
CHROME_CANDIDATES = (
    "chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome",
)

STATE_NOTE = {
    "MEASURED": "the check ran and produced this value",
    "ABSENT": "a fact about the project — the thing being measured is not there",
    "UNEVALUABLE": "a fact about the instrument — this check needs something a clone cannot supply",
}

CSS = """
@page { size: A4; margin: 16mm 14mm 18mm; }
* { box-sizing: border-box; }
body { font: 10.5pt/1.45 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
       color: #14181f; margin: 0; }
h1 { font-size: 21pt; margin: 0 0 2mm; letter-spacing: -.02em; }
h2 { font-size: 13pt; margin: 9mm 0 2mm; padding-bottom: 1.5mm;
     border-bottom: 1.5px solid #14181f; page-break-after: avoid; }
h3 { font-size: 11pt; margin: 5mm 0 1.5mm; page-break-after: avoid; }
.sub { color: #5b6472; font-size: 9pt; margin: 0 0 6mm; }
.banner { padding: 4mm 5mm; border-radius: 2mm; margin: 4mm 0;
          border-left: 3mm solid; page-break-inside: avoid; }
.banner .t { font-size: 14pt; font-weight: 700; }
.bad  { background: #fdeceb; border-color: #c0392b; }
.warn { background: #fdf4e3; border-color: #c78a12; }
.good { background: #ecf7ee; border-color: #1e7e34; }
.flat { background: #f2f4f7; border-color: #8b95a3; }
table { width: 100%; table-layout: fixed; border-collapse: collapse; margin: 2mm 0 4mm;
        font-size: 8.5pt; }
td { overflow-wrap: anywhere; }
th { text-align: left; background: #f2f4f7; font-weight: 600; color: #3d4653;
     border-bottom: 1px solid #ccd2da; }
th, td { padding: 1.6mm 2mm; vertical-align: top; }
tr { page-break-inside: avoid; }
tbody tr + tr td { border-top: 1px solid #e6eaef; }
td.id { font-family: ui-monospace, "SF Mono", Menlo, monospace; white-space: nowrap; }
.st { font-size: 7.5pt; letter-spacing: .04em; font-weight: 600;
      overflow-wrap: normal; word-break: keep-all; }
.PASS { color: #1e7e34; } .FAIL { color: #c0392b; }
.UNEVALUABLE { color: #8b95a3; } .ABSENT { color: #c78a12; }
.reason { color: #4b5563; }
.cards { display: flex; gap: 3mm; margin: 4mm 0; }
.card { flex: 1; border: 1px solid #ccd2da; border-radius: 2mm; padding: 3mm; }
.card .k { font-size: 8pt; color: #5b6472; } .card .v { font-size: 15pt; font-weight: 700; }
.note { background: #f2f4f7; border-left: 2mm solid #8b95a3; padding: 3mm 4mm;
        font-size: 9pt; margin: 4mm 0; page-break-inside: avoid; }
footer { margin-top: 8mm; padding-top: 2mm; border-top: 1px solid #e6eaef;
         font-size: 8pt; color: #8b95a3; }
"""


def esc(v) -> str:
    return html.escape("" if v is None else str(v))


# A value cell is a fixed-width column in print. A task that returns a long list
# -- F-4 returns every contributor address it found -- would otherwise squeeze
# every other column to nothing, so the tail is elided and the count kept.
VALUE_CHARS = 150


def _clip(text: str) -> str:
    if len(text) <= VALUE_CHARS:
        return text
    return text[:VALUE_CHARS].rsplit(" ", 1)[0] + f" … (+{len(text) - VALUE_CHARS} more characters)"


def show(value) -> str:
    """A dict value is a set of named numbers, not a blob. Render it as one."""
    if isinstance(value, dict):
        parts = []
        for k, v in value.items():
            # per_criterion has its own table above; repeating it here as a
            # clipped blob is noise, not detail.
            if v is None or k in ("note", "per_criterion"):
                continue
            if isinstance(v, (list, tuple)):
                if not v:
                    v = "none"
                elif len(v) == 1:
                    v = str(v[0])
                else:
                    head = ", ".join(str(x) for x in v[:2])
                    v = f"{head}" if len(v) == 2 else f"{len(v)} incl. {head} …"
            parts.append(f"{k} = {v}")
        note = value.get("note")
        body = esc(_clip(" · ".join(parts) or "—"))
        return body + (f"<div class='reason'>{esc(note)}</div>" if note else "")
    return esc(_clip("—" if value is None else str(value)))


def _page(title: str, subtitle: str, body: str) -> str:
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    tasks = runners.load_tasks()
    w = runners.load_weights()
    return (f"<!doctype html><meta charset='utf-8'><title>{esc(title)}</title>"
            f"<style>{CSS}</style><h1>{esc(title)}</h1><p class='sub'>{subtitle}</p>{body}"
            f"<footer>WinningHackProjects · generated {stamp} · "
            f"{len(tasks)} audit tasks, {sum(1 for t in tasks.values() if t['blocking'])} blocking, "
            f"{len(spec_mod.ROWS)} design checks · weights "
            f"value {w['value']} / usability {w['usability']} / feasibility {w['feasibility']} · "
            f"every threshold, cap and weight above was read from the contracts at run time"
            f"</footer>")


# ------------------------------------------------------------------ project
def project_html(body: dict) -> str:
    result = runners.audit_repo(
        body["repo_url"],
        window_end=body.get("window_end"),
        window_days=int(body.get("window_days") or 1),
        starter_sha=body.get("starter_sha"),
        demo_artifact=body.get("demo_artifact"),
        criteria_source=body.get("criteria_source"),
        criteria=body.get("criteria"),
        prior_art=body.get("prior_art"),
        eval_command=body.get("eval_command"),
        walkthrough_runs=body.get("walkthrough_runs"),
        team_size=body.get("team_size"),
        event_hours=body.get("event_hours"))
    if "tasks" not in result:
        raise SystemExit(f"could not audit: {result.get('error')} — {result.get('detail', '')}")
    tasks, scopes = result["tasks"], runners.summarise(result["tasks"])
    weights = runners.load_weights()

    capped = [k for k, v in scopes.items() if v["cap"]]
    if capped:
        banner = ("bad", f"Does not hold up — {len(capped)} of 3 scopes capped",
                  "A cap is a ceiling the contract imposes when a blocking task fails.")
    else:
        banner = ("flat", "Nothing we could measure caps this project",
                  "Which is not the same as passing — see the ceiling note under each scope.")

    measured = sum(s["measured"] for s in scopes.values())
    could_not = sum(s["unevaluable"] for s in scopes.values())
    cards = [("Commits", result.get("commits", "—")),
             ("Own lines of code", f"{result.get('own_loc', 0):,}"),
             ("Vendored (excluded)", f"{result.get('vendored_loc', 0):,}"),
             ("Metrics measured", measured),
             ("Could not be run", could_not)]

    out = [f"<div class='banner {banner[0]}'><div class='t'>{esc(banner[1])}</div>"
           f"<div>{esc(banner[2])}</div></div>",
           "<div class='cards'>" + "".join(
               f"<div class='card'><div class='k'>{esc(k)}</div><div class='v'>{esc(v)}</div></div>"
               for k, v in cards) + "</div>"]

    v2 = tasks.get("V-2", {}).get("value")
    if isinstance(v2, dict) and v2.get("per_criterion"):
        out.append("<h2>The criteria, and where the project meets them</h2>"
                   "<p class='sub'>V-1 checks these are well formed; V-2 looks for each one in "
                   "the project's own source. A citation is a place you can go and read \u2014 "
                   "it is evidence the criterion was addressed, not a judgment that it was "
                   "addressed well. That judgment is V-7's, and a human's.</p>")
        cols = "".join(f"<col style='width:{w}%'>" for w in (6, 26, 26, 10, 32))
        rows = []
        for c in v2["per_criterion"]:
            cites = "<br>".join(
                f"<code>{esc(h['cited_at'])}</code> <span class='reason'>"
                f"{esc(', '.join(h.get('distinctive') or h.get('matched') or []))}</span>"
                for h in (c.get("cited_at") or [])) or "<span class='reason'>nothing in the "\
                "project's source matched this criterion's terms</span>"
            rows.append(
                f"<tr><td class='id'>{esc(c.get('id'))}"
                f"<div class='st {'PASS' if c['evidenced'] else 'FAIL'}'>"
                f"{'MET' if c['evidenced'] else 'NOT MET'}</div></td>"
                f"<td><b>{esc(c.get('text'))}</b></td><td>{esc(c.get('pass_when'))}</td>"
                f"<td class='reason'>{esc(', '.join(c.get('searched_for') or []))}</td>"
                f"<td>{cites}</td></tr>")
        out.append(f"<table>{cols}<thead><tr><th>ID</th><th>Criterion</th><th>Passes when</th>"
                   "<th>Searched for</th><th>Found at</th></tr></thead><tbody>"
                   + "".join(rows) + "</tbody></table>")

    for scope, summary in scopes.items():
        out.append(f"<h2>{scope.title()} — weight {weights[scope]}</h2>")
        cap = summary["cap"]
        if cap == "unscorable":
            out.append("<div class='banner bad'><div class='t'>Unscorable</div><div>A task whose "
                       "absence makes this scope unmeasurable failed. That is <b>never "
                       "measured</b>, not <b>measured and bad</b>.</div></div>")
        elif cap:
            out.append(f"<div class='banner warn'><div class='t'>Capped at {esc(cap)}</div>"
                       f"<div>by {esc(', '.join(summary['failed_blocking']))}</div></div>")
        else:
            out.append("<div class='banner flat'><div class='t'>No cap triggered</div>"
                       "<div>by anything we were able to measure.</div></div>")
        ceiling = summary.get("score_is_a_ceiling_because")
        if ceiling:
            out.append(f"<div class='note'><b>This is a ceiling, not a score.</b> "
                       f"{len(ceiling)} blocking tasks did not run here: "
                       f"{esc(', '.join(ceiling))}. Each needs published criteria, a container or "
                       f"a person, and a clone supplies none of the three.</div>")
        out.append(_task_table(tasks, scope))

    out.append("<h2>What this report does not say</h2><div class='note'>"
               "<b>There is no overall score.</b> Every scope here has blocking tasks that did not "
               "run, so each cap is a ceiling rather than a score, and averaging ceilings would "
               "invent a number.<br><br>"
               "<b>UNEVALUABLE is not a pass.</b> It records that the instrument could not reach "
               "the thing, which is a different fact from the thing being fine.<br><br>"
               "<b>This does not predict winning.</b> 28 repos that demonstrably won their events "
               "fail these contracts. This says whether a project holds up.</div>")
    src = result.get("criteria_source")
    sub = (f"{esc(body['repo_url'])}"
           + (f" · event {esc(body['event_url'])}" if body.get("event_url") else "")
           + (f" · criteria {esc(src)} (per {esc(result.get('criteria_source_from'))})"
              if src else " · criteria not supplied"))
    return _page("Project audit", sub, "".join(out))


def _task_table(tasks: dict, scope: str) -> str:
    rows = []
    for tid, t in sorted(tasks.items()):
        if t["scope"] != scope:
            continue
        reason = t.get("reason") or t.get("cap_demoted_because") or STATE_NOTE.get(t["state"], "")
        rows.append(
            f"<tr><td class='id'>{esc(tid)}</td><td><b>{esc(t['task'])}</b>"
            f"<div class='reason'>{esc(reason)}</div></td>"
            f"<td>{esc(t['threshold'])}</td><td>{show(t['value'])}</td>"
            f"<td class='st {esc(t['state'])}'>{esc(t['state'])}</td>"
            f"<td class='st {esc(t['verdict'] or '')}'>{esc(t['verdict'] or '—')}</td>"
            f"<td>{esc(t['cap'] or '—')}</td></tr>")
    cols = "".join(f"<col style='width:{w}%'>" for w in (6, 28, 14, 23, 11, 8, 10))
    return (f"<table>{cols}<thead><tr><th>ID</th><th>Metric, and why it reads this way</th>"
            "<th>Must be</th><th>Value</th><th>State</th><th>Verdict</th><th>Caps at</th>"
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>")


# --------------------------------------------------------------------- spec
def spec_html(body: dict) -> str:
    results = spec_mod.evaluate(body)
    by_scope = spec_mod.strengths_and_weaknesses(results)
    flow = spec_mod.workflow(results)
    weights = runners.load_weights()

    weak = sum(len(v["weak"]) for v in by_scope.values())
    unknown = sum(len(v["not_stated"]) for v in by_scope.values())
    if weak == 0 and unknown == 0:
        banner = ("good", "Winnable — yes, on everything checkable before you build",
                  "Every design check the plan can answer at t=0 passes. The audit still happens "
                  "after you build; this says the unrecoverable things are scheduled.")
    elif weak == 0:
        banner = ("warn", f"Not yet answerable — {unknown} "
                          f"check{'s are' if unknown != 1 else ' is'} unstated",
                  "Nothing in the plan fails. Nothing in the plan settles these either.")
    else:
        banner = ("bad", f"Not winnable as written — {weak} check{'s' if weak != 1 else ''} "
                         f"{'fail' if weak != 1 else 'fails'}, {unknown} unstated",
                  "Each failing row below names the audit task it would have bought you.")

    out = [f"<div class='banner {banner[0]}'><div class='t'>{esc(banner[1])}</div>"
           f"<div>{esc(banner[2])}</div></div>",
           "<div class='cards'>" + "".join(
               f"<div class='card'><div class='k'>{esc(n.title())} · weight {weights[n]}</div>"
               f"<div class='v'>{esc(v['verdict'])}</div>"
               f"<div class='k'>{len(v['strong'])} strong · {len(v['weak'])} weak · "
               f"{len(v['not_stated'])} unstated</div></div>"
               for n, v in by_scope.items()) + "</div>"]

    # strengths_and_weaknesses returns row IDs for strong and not_stated, and
    # dicts for weak. Look the full row back up rather than re-deriving it here.
    by_row = {r["row"]: r for r in results}

    out.append("<h2>Why not — what fails, and what each one costs</h2>")
    if weak or unknown:
        for name, v in by_scope.items():
            if not v["weak"] and not v["not_stated"]:
                continue
            cols = "".join(f"<col style='width:{w}%'>" for w in (9, 34, 13, 44))
            out.append(f"<h3>{esc(name.title())}</h3><table>{cols}<thead><tr><th>Row</th>"
                       "<th>What is missing</th><th>Audit tasks you forfeit</th>"
                       "<th>Do this instead</th></tr></thead><tbody>")
            for w in v["weak"]:
                out.append(f"<tr><td class='id'>{esc(w['row'])}"
                           f"<div class='st FAIL'>FAIL</div></td><td>{esc(w['check'])}</td>"
                           f"<td>{esc(' '.join(w['costs_you']) or '—')}</td>"
                           f"<td>{esc(w['action'] or '—')}</td></tr>")
            for rid in v["not_stated"]:
                r = by_row[rid]
                out.append(f"<tr><td class='id'>{esc(rid)}"
                           f"<div class='st ABSENT'>UNSTATED</div></td><td>{esc(r['check'])}</td>"
                           f"<td>{esc(' '.join(r['buys']) or '—')}</td>"
                           f"<td>{esc(r['action'] or 'state it, either way — silence is not a pass')}"
                           f"</td></tr>")
            out.append("</tbody></table>")
    else:
        out.append("<div class='note'>Nothing fails and nothing is left unstated. Every row is in "
                   "the table below with the value it was answered with.</div>")

    out.append("<h2>Why yes — what the plan already buys</h2>")
    cols = "".join(f"<col style='width:{w}%'>" for w in (9, 34, 13, 44))
    out.append(f"<table>{cols}<thead><tr><th>Row</th><th>Check that passes</th>"
               "<th>Audit tasks it buys</th><th>Scope</th></tr></thead><tbody>")
    # One row can buy tasks in two scopes, so collect its scopes before printing
    # rather than emitting the row twice under different headings.
    scopes_of: dict[str, list[str]] = {}
    for name, v in by_scope.items():
        for rid in v["strong"]:
            scopes_of.setdefault(rid, []).append(name.title())
    for rid, names in scopes_of.items():
        r = by_row[rid]
        out.append(f"<tr><td class='id'>{esc(rid)}</td><td>{esc(r['check'])}</td>"
                   f"<td>{esc(' '.join(r['buys']) or '—')}</td>"
                   f"<td>{esc(', '.join(names))}</td></tr>")
    if not scopes_of:
        out.append("<tr><td colspan='4'>Nothing in the plan passes a design check yet.</td></tr>")
    out.append("</tbody></table>")

    if flow:
        out.append("<h2>Do this, in this order</h2>")
        for step in flow:
            cols = "".join(f"<col style='width:{w}%'>" for w in (7, 60, 20, 13))
            out.append(f"<h3>Step {step['step']} — {esc(step['gate'])}</h3><table>{cols}"
                       "<thead><tr><th>Row</th><th>Therefore today I will…</th>"
                       "<th>Buys</th><th>Strength</th></tr></thead><tbody>"
                       + "".join(f"<tr><td class='id'>{esc(d['row'])}</td>"
                                 f"<td>{esc(d['therefore_today_i_will'])}</td>"
                                 f"<td>{esc(' '.join(d['buys']))}</td>"
                                 f"<td class='st'>{esc(d['strength'])}</td></tr>"
                                 for d in step["do"]) + "</tbody></table>")

    cols = "".join(f"<col style='width:{w}%'>" for w in (6, 31, 11, 23, 11, 9, 9))
    out.append(f"<h2>Every design check</h2><table>{cols}<thead><tr><th>Row</th><th>Check</th>"
               "<th>Buys</th><th>Value</th><th>State</th><th>Verdict</th><th>Strength</th>"
               "</tr></thead><tbody>"
               + "".join(f"<tr><td class='id'>{esc(r['row'])}</td><td>{esc(r['check'])}</td>"
                         f"<td>{esc(' '.join(r['buys']))}</td><td>{show(r['value'])}</td>"
                         f"<td class='st {esc(r['state'])}'>{esc(r['state'])}</td>"
                         f"<td class='st {esc(r['verdict'] or '')}'>{esc(r['verdict'] or '—')}</td>"
                         f"<td class='st'>{esc(r['strength'])}</td></tr>"
                         for r in results) + "</tbody></table>")

    strong = sum(1 for r in results if r["strength"] == "STRONG")
    out.append(f"<div class='note'><b>{strong} of {len(results)} checks are mechanical</b> — the "
               "same event page and the same plan give the same answer. The rest are declarations "
               "about work not yet done; they are reported and never scored.<br><br>"
               "<b>This is not pooled with a project audit.</b> Different units. A design card "
               "that reads well is not a forecast that the built thing passes an audit.</div>")

    ev = body.get("event", {})
    sub = ((f"event {esc(body['event_url'])} · " if body.get("event_url") else "")
           + f"team {esc(ev.get('team_size'))} · {esc(ev.get('event_hours'))} build hours")
    return _page("Spec review", sub, "".join(out))


# ---------------------------------------------------------------------- pdf
def find_chrome() -> str | None:
    packaged = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if packaged:
        for rel in ("chromium/chrome-linux/chrome", "chromium/chrome-mac/Chromium.app/"
                    "Contents/MacOS/Chromium"):
            cand = os.path.join(packaged, rel)
            if os.path.exists(cand):
                return cand
    for name in CHROME_CANDIDATES:
        found = shutil.which(name)
        if found:
            return found
    for cand in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                 "/opt/pw-browsers/chromium"):
        if os.path.exists(cand):
            return cand
    return None


def to_pdf(html_text: str, out: pathlib.Path) -> pathlib.Path:
    """Print the HTML. If no browser exists, keep the HTML and say why."""
    html_path = out.with_suffix(".html")
    html_path.write_text(html_text)
    chrome = find_chrome()
    if not chrome:
        print(f"no Chromium found, so no PDF was printed — the report is at {html_path}\n"
              f"  install one, or open that file and print it to PDF from the browser",
              file=sys.stderr)
        return html_path
    proc = subprocess.run(
        [chrome, "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
         f"--print-to-pdf={out}", html_path.as_uri()],
        capture_output=True, text=True, timeout=180)
    if proc.returncode or not out.exists():
        print(f"Chromium exited {proc.returncode} without a PDF; the report is at {html_path}\n"
              f"  {proc.stderr.strip()[:300]}", file=sys.stderr)
        return html_path
    html_path.unlink()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=("project", "spec"))
    ap.add_argument("--input", required=True, help="JSON body, same shape the endpoint takes")
    ap.add_argument("-o", "--out", default=None, help="output PDF path")
    args = ap.parse_args()

    body = json.loads(pathlib.Path(args.input).read_text())
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    out = pathlib.Path(args.out or f"{args.mode}-report-{stamp}.pdf")
    out.parent.mkdir(parents=True, exist_ok=True)
    written = to_pdf(project_html(body) if args.mode == "project" else spec_html(body), out)
    print(written)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
