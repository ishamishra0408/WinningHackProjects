# Winner audits — the contracts run against real winning repos

First contact between the [contracts](../scopes/README.md) and projects that actually won.
The result indicts the contracts more than the projects.

## Scope, and why it is 5 and not 42

| | |
|---|---|
| Winner rows in [winners-top3.md](winners-top3.md) | **42** |
| Rows linking a GitHub repo | **6** |
| Repos that are public and clonable | **5** — `RBG-Synthara` needs auth (private or deleted) |
| Rows linking only a Cerebral Valley **team profile** | **30** |

A team profile is a person's page. It has no repo, no README, no commits. **30 of 42 winners cannot
be audited at all**, and no amount of effort changes that — Cerebral Valley publishes no per-project
permalink. The 5 below are the entire auditable population.

| Repo | Event | Window used |
|---|---|---|
| `aritra741/MemoryAtlas` · 1st | Qdrant Vector Space Day | 5 weeks to 2026-06-11 |
| `Gustavobrg/crowd-whisperer` · 2nd | Qdrant Vector Space Day | 5 weeks to 2026-06-11 |
| `roopadevihosur-07/MealPrep_VideoContexGraph` · 1st | Neo4j Video Context Graph | 1 day, 2026-07-30 |
| `altonalexander/rehearsal` · 2nd | Neo4j Video Context Graph | 1 day, 2026-07-30 |
| `rishabhcli/ZooVision` · 3rd | Neo4j Video Context Graph | 1 day, 2026-07-30 |

Tasks needing a naive operator (`U-2` `U-3` `U-11` `U-12`), a live probe (`F-6`), containers
(`V-3` `V-4` `U-5` `U-6` `F-7` `F-8`), the Events API (`F-2b`) or published criteria (`V-1` `V-2`)
were not run. Those are **NOT-CHECKED**, not passes.

## The matrix

| Repo | `F-2a` share in window | `F-2c` drift | `F-3` opening | `F-11` file share | `F-12` hours | `F-10` lock | `F-9` CI | `V-9` claim |
|---|---|---|---|---|---|---|---|---|
| MemoryAtlas | PASS 80.0% | PASS 100% | PASS 31.9% | PASS 11.3% | **FAIL 3** | **FAIL** | **FAIL** | **FAIL** |
| crowd-whisperer | PASS 100% | PASS 100% | PASS 0.0% | PASS 9.7% | PASS 25 | **FAIL** | **FAIL** | **FAIL** |
| MealPrep | **FAIL 24.3%** | PASS 100% | **FAIL 55.5%** | PASS 20.9% | PASS 11 | **FAIL** | PASS | **FAIL** |
| rehearsal | **FAIL 14.3%** | PASS 100% | **FAIL 73.0%** | PASS 12.7% | **FAIL 5** | **FAIL** | **FAIL** | **FAIL** |
| ZooVision | **FAIL 52.3%** | PASS 98.8% | PASS 0.0% | PASS 18.9% | PASS 23 | PASS | PASS | **FAIL** |

**Not one of the five passes all eight. Every winner fails at least two.**

| Task | Fails |
|---|---|
| `V-9` numeric claim in README | **5 / 5** |
| `F-10` lockfile | 4 / 5 |
| `F-2a` share in window · `F-9` CI | 3 / 5 |
| `F-3` opening commit · `F-12` commit hours | 2 / 5 |
| `F-2c` drift · `F-11` file share | 0 / 5 |

## Three faults the contracts have, found by running them

### 1 · LOC tasks do not exclude vendored code

`crowd-whisperer` vendors React into the repo:

```
29,924  frontend/lib/react-dom.development.js
 3,343  frontend/lib/react.development.js
```

`F-11` on raw LOC: **68.6% — FAIL.** Excluding vendored: **9.7% — PASS.** The contract would fail a
2nd-place winner for checking in a dependency. `F-3`, `F-5` and `V-6` share the denominator and the
blind spot.

### 2 · `F-3` assumes the opening commit is the team's

`MealPrep` and `rehearsal` have the **identical first commit** — sha `857113ee`, tree
`eeb9fea223003d8a04bf8201c613f02beae60321`, both dated 2026-07-21, nine days before the event. The
Neo4j writeup is titled *one starter repo, three winners*. **The organizers supplied it.**

| | `F-3` as written | measured from the team's own first commit |
|---|---|---|
| MealPrep | **55.5% — FAIL** | **0.1% — PASS** |
| rehearsal | **73.0% — FAIL** | **0.2% — PASS** |

`F-3` caps Feasibility at 1/5 for using the starter the event advertised.

### 3 · `F-2a` has no window shape

Qdrant ran **5 weeks**; Neo4j ran **one day**. The same threshold over both is two different
questions. Observed commit spans:

| Repo | first → last commit | event date |
|---|---|---|
| MemoryAtlas | 2026-04-30 → 2026-06-01 | Jun 11 (ends 10 days *before*) |
| crowd-whisperer | 2026-05-20 → 2026-06-01 | Jun 11 |
| rehearsal | 2026-07-21 → 2026-07-30 | Jul 30 (starts 9 days early) |
| MealPrep | 2026-07-21 → 2026-08-06 | Jul 30 (runs 7 days late) |
| ZooVision | 2026-07-30 → 2026-08-04 | Jul 30 (runs 5 days late) |

**Winners routinely commit before and after the stated date.** A single-day window is the wrong
model for every one of these.

## What the winners actually carry

| Repo | README lines | video refs | images | demo link | arch diagram |
|---|---|---|---|---|---|
| MealPrep | 334 | 8 | 0 | 0 | 1 |
| ZooVision | 402 | 3 | 0 | 0 | 2 |
| crowd-whisperer | 233 | 0 | 4 | 1 | 3 |
| MemoryAtlas | 210 | 1 | 0 | 1 | 1 |
| rehearsal | 60 | 0 | 0 | 0 | 0 |

**4 of 5 carry a video or images; 4 of 5 carry an architecture diagram; 0 of 5 carry a numeric
claim.** The contract asks for the one thing none of them has, and never asks for the two things
four of them have.

## What this does NOT establish

**Five winners, zero losers.** Every property above is drawn from a set selected on the outcome, so
any shared trait is survivorship, not signal. Nothing here says *why* they won — no losing project
from these events was audited, and the Qdrant and Neo4j fields are structurally different
populations that must not be pooled.

What it does establish is narrower and solid: **the contracts, run unchanged against projects that
demonstrably cleared their events' bars, reject all five.** That is a fact about the contracts.
