# Design card — <Project idea> · <Event>

Filled **before** writing code. Copy to `designer/cards/<event-slug>-<idea>.md`.

| Field | Value |
|-------|-------|
| event_url | |
| event date · window hours | |
| team size | |
| topic(s) | 1–7 |
| filled on | YYYY-MM-DD |
| filled by | |

Every row is `measured` / `ABSENT` / `UNEVALUABLE`. `ABSENT` is a fact about the subject and is a
valid answer; a blank cell is not.

## Step 1 — can we enter at all

| Row | Check | Value | State | Note |
|---|---|---|---|---|
| `D1` | published judging criteria found | n = | | if ABSENT, name the research fallback used |
| `D13` | window fixed · every contributor on the roster | | | roster mismatch → **stop** |

## Step 2 — free now, unrecoverable later

| Row | Check | Value | State | Note |
|---|---|---|---|---|
| `D5` | payoff in one sentence, observable without you | | | write the sentence here |
| `D10` | the number we intend to claim | | | **declared before building** |
| `D19` | who records the demo video, and when | | | not the last hour |
| `D14` | committed build start ≥ window open | | | |
| `D15` | prior/starter code LOC we will import | | | declare it or `F-3` is unarguable |

## Step 3 — go / no-go

| Row | Check | Value | State | Therefore today I will… |
|---|---|---|---|---|
| `D2` | criteria covered / criteria found | / | | |
| `D3` | prior-art count + delta sentence | | | |
| `D6` | planned hrs ÷ (team × event hrs) | | | *(reads pessimistic under AI codegen)* |

**Verdict:** build / cut scope / pick a different idea —

## Step 4 — day-1 build commitments

| Row | Check | Value | State |
|---|---|---|---|
| `D4` | ≥1 authenticated external call on the demo path | | |
| `D7` | the one screen the payoff appears on · `ui_applicable` | | |
| `D8` | ≥2 planned files on the demo path | | |
| `D12` | one-click entrypoint · 3 *distinct* environments | | |
| `D17` | Dockerfile · lockfile · CI in day-1 scope | | |

## Step 5 — expires on first contact

| Row | Check | Value | State |
|---|---|---|---|
| `D11` | naive operators reserved, by name, unburned | n = | |

## Step 6 — declarations, not measurements

Restate these; do not score them.

| Row | Declaration |
|---|---|
| `D9` | every demo-path stub has a replacement slot on: |
| `D16` | share of shipped code we will actually read: |
| `D18` | README written alongside the build, owned by: |

## ABSENT at t=0 — measurable later, by design

Not gaps in this card. Recorded so nobody scores them zero.

| Task | First measurable |
|---|---|
| `U-7` | first README run |
| `U-8` | after `U-2` |
| `U-10` | first neutral-environment run |
| `U-11` | first cold clone |
| `F-2c` | first push |
| `F-11` | first build |

## What we are choosing not to do

The refusal, written down. From the winners in
[../research/winners-top3.md](../research/winners-top3.md): a documented refusal is cheap to build
and reads as judgment.

-
