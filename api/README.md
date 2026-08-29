# API — the two layers, served

```bash
python3 api/app.py --port 8000      # stdlib only, no install
```

| Endpoint | Input | Answers |
|---|---|---|
| `POST /evaluateproject` | a repo that exists | what holds up, what does not, what was never measured |
| `POST /evaluatespec` | a plan that does not exist yet | the ordered work that makes it clear the bar |
| `GET /health` | — | task counts, so a caller can tell the contracts loaded |

**Zero dependencies, deliberately.** No lockfile to drift, and it builds from a clean clone
anywhere — the properties `F-7` and `F-10` demand of everyone else. Single-threaded, for one
operator on localhost; not a production service.

**Thresholds are never restated here.** Every one is read from [`../scopes/`](../scopes/README.md)
at call time, so this code cannot drift from the contracts.

## `POST /evaluateproject`

```bash
curl -X POST localhost:8000/evaluateproject -H 'Content-Type: application/json' -d '{
  "repo_url": "https://github.com/owner/repo",
  "window_end": "2026-08-22",
  "window_days": 1,
  "starter_sha": "857113ee"
}'
```

`window_end` + `window_days` set `window_kind` for `F-2a`. `starter_sha` makes `F-3` measure from
the **team's** first commit when the event shipped a starter repo. Both optional; without them the
tasks that need them return `ABSENT`, not a guess.

### Every task returns one of three states

| State | Means | Example |
|---|---|---|
| `MEASURED` | the check ran | `F-2c` → `{"drift_violations": 0, "commits_total": 41, "within_1h_share": 1.0}` |
| `ABSENT` | a fact about **the subject** | `F-4` → no entrant roster supplied |
| `UNEVALUABLE` | a fact about **the instrument** | `V-3` → needs Docker |

**`UNEVALUABLE` is not a pass.** Ten Usability tasks need an operator or a container and will
always return it from a clone alone. A caller that treats them as passes has invented a score.

### It returns no overall, on purpose

```json
"overall": null,
"overall_refused_because": [
  "w_value is unset in the source contracts",
  "caps are stated in prose in the contracts, so a /5 here would be a second home for them",
  "UNEVALUABLE is not a pass"
]
```

Per scope you get `passed`, `failed`, `failed_blocking` and `capped`. **The number is yours to
compute once you have set `w_value`** — and the contracts require you to set it before reading any
result.

**It does not predict winning.** 28 winning repos fail these contracts. This says whether a project
holds up, not whether it wins.

## `POST /evaluatespec`

```bash
curl -X POST localhost:8000/evaluatespec -H 'Content-Type: application/json' -d '{
  "event": {"criteria_found": 4, "team_size": 3, "event_hours": 7.5},
  "plan":  {"criteria_covered": 3, "planned_person_hours": 30,
            "payoff_sentence": "grade the receipt against the query that ran",
            "real_call": true, "claim_declared": "", "demo_slot": "",
            "operators_reserved": [], "day1_infra": ""}
}'
```

Returns three things:

- **`scopes`** — per scope: `strong`, `weak` (each with what it will cost you and what to do), and
  `not_stated`. Verdict is `READY` · `AT RISK` · `UNDERSPECIFIED`.
- **`workflow`** — the six steps, in order, with only what is still undone. Every item carries a
  `therefore_today_i_will`. A ranking that does not end in an action is not built.
- **`checks`** — all 19 rows with state, value and verdict.

16 of the 19 are mechanical: the same event page and the same plan give the same answer. The other
3 are declarations and are reported, **never scored**.

### The two are never pooled

Their units differ. A design card that reads well is not a prediction that the project will pass an
audit — it is a statement that the unrecoverable things have been scheduled. There is no combined
score and the response says so.

## Known limits

| Limit | Consequence |
|---|---|
| `F-2a` is computed at **day** granularity | an event with an hours-long submission deadline needs the finer window; the day figure is optimistic |
| `V-10` only sees media referenced **in the README** | a video submitted to Discord or a form is invisible and reads `FAIL` |
| `F-4` cannot verify a roster | always `ABSENT` until `F-1` supplies one |
| 10 Usability tasks need an operator or container | always `UNEVALUABLE` here |
| No auth, no rate limit, single host | localhost only |
