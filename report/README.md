# Report — one PDF, for either question

```bash
python3 report/render.py project --input body.json -o project-report.pdf
python3 report/render.py spec    --input body.json -o spec-report.pdf
```

`--input` takes **exactly the body [`api/app.py`](../api/README.md) accepts** for the matching
endpoint. There is deliberately no second input format: a report and an endpoint that disagreed
about what `criteria_source` means would be two homes for one contract.

| Mode | Input | The PDF answers |
|---|---|---|
| `project` | a repo that exists | every metric with its value, its state, its verdict, its reason, and what it caps |
| `spec` | a plan that does not | winnable or not, **why not** row by row, **why yes** row by row, then the ordered work |

## What it depends on

**The HTML is built with the standard library.** The PDF is printed by a headless Chromium found
on the machine — `PLAYWRIGHT_BROWSERS_PATH` first, then `chromium`, `google-chrome` and the usual
install paths. When none is found the HTML is written next to the requested path and the reason is
printed. A missing browser must not look like a report that came out empty.

## It lays out numbers it did not compute

Every task name, threshold, cap and weight in the output is read from [`scopes/`](../scopes/README.md)
and [`designer/README.md`](../designer/README.md) at run time, through `api/runners.py` and
`api/spec.py`. Nothing is restated here, so a contract edit changes the next PDF with no code change.

The footer of every page carries the counts and weights that were live when it ran, so a printed
report can be checked against the contracts it claims to come from.

## What the project report refuses to print

- **No overall score.** Every scope has blocking tasks that cannot run from a clone, so each cap is
  a *ceiling*. The report names which tasks did not run, under each scope.
- **`UNEVALUABLE` is drawn as its own state**, never as a pass. It is a fact about the instrument.
- **No prediction of winning.** 28 repos that won their events fail these contracts, and the last
  section of every project report says so.

## Example input

```json
{"repo_url": "https://github.com/owner/repo",
 "event_url": "https://luma.com/…",
 "window_end": "2026-08-22", "window_days": 1,
 "starter_sha": "857113ee",
 "criteria": [{"id": "c1", "text": "Showcases Mistral",
               "pass_when": "a Mistral model is called on the demo path",
               "criteria_source": "published"}],
 "demo_artifact": {"url": "https://…"}}
```

Leave `criteria` out and `V-1` reports **ABSENT**, which keeps the whole Value scope unscorable —
every task in it scores against those criteria. Supply fewer than three, or one without a pass
condition, and `V-1` **fails**, which is a different and louder answer.

```json
{"event_url": "https://luma.com/…",
 "event": {"criteria_found": 4, "team_size": 3, "event_hours": 8},
 "plan": {"criteria_covered": 4, "planned_person_hours": 24,
          "payoff_sentence": "a stranger sees the receipt graded against the query that ran",
          "real_call": true, "day1_infra": true, "demo_slot": true, "one_click_and_envs": false}}
```

Any `plan` field you leave out is reported **unstated**, not failed — the design layer separates
*we chose not to* from *we have not said*.

## Known limits

| Limit | Consequence |
|---|---|
| The event link is recorded, not fetched | criteria counts, the window and `criteria_source` are yours to supply |
| A value cell is clipped at 150 characters | `F-4` returns every contributor it found; the tail is elided, and the elision is labelled |
| Page breaks are Chromium's | rows are kept off breaks, whole tables are not |
