# Winner audits — the contracts run against 28 winning repos

First contact between the [contracts](../scopes/README.md) and projects that actually won.
The result indicts the contracts, not the projects.

## How the repos were found

[winners-top3.md](winners-top3.md) links a Cerebral Valley **team profile** for most winners — a
person's page, with no repo. That is where the trail appeared to end.

It does not. Every CV gallery page embeds a schema.org `ItemList` in its Next.js payload, carrying
for each project a `name`, a **per-project permalink** (`?project=N`) and a `sameAs` array with its
GitHub URL. Markdown-converting the page strips all of it; the raw HTML has it.

| | |
|---|---|
| Projects harvested across 12 galleries | **1,092** |
| Carrying a GitHub link | **1,060** |
| Winner rows matched by exact name | 27 |
| …of those, public and clonable | 23 |
| Plus winners linked directly from non-CV writeups | 5 |
| **Audited** | **28 of 42 (67%)** |

The 14 not audited are 4 whose repos 404 and 10 from the Qdrant, Zilliz and Neo4j Aura writeups
whose names have no gallery entry to match.

## The matrix

**Bold = fails that task's threshold.** Tasks needing an operator (`U-2` `U-3` `U-11` `U-12`), a
live probe (`F-6`), containers (`V-3` `V-4` `U-5` `U-6` `F-7` `F-8`), the Events API (`F-2b`) or
published criteria (`V-1` `V-2`) were not run — **NOT-CHECKED**, not passes.

| | Project | Event | cmt | auth | own LOC | `F-2a` | `F-2c` | `F-3` | `F-11` | `F-12` | `F-10` | `F-9` | `V-9` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 🥇 | SplatForge | AIEWF | 70 | 3 | 8,862 | **75.7%** | 100.0% | 0.0% | 10.9% | 17 | ✅ | ❌ | ✅ |
| 🥉 | rote | AIEWF | 112 | 7 | 11,146 | **67.0%** | 100.0% | 2.7% | 4.6% | 19 | ✅ | ❌ | ❌ |
| 🥇 | Keskin — Medkit | Opus 4.7 | 1 | 1 | 32,227 | 100.0% | 100.0% | **100.0%** | 22.3% | **1** | ✅ | ❌ | ❌ |
| 🥈 | Alexis Chapellier — Wren | Opus 4.7 | 16 | 1 | 159,032 | **0.0%** | **87.5%** | **88.1%** | 3.4% | 11 | ❌ | ❌ | ❌ |
| 🥇 | Mike — CrossBeam | Opus 4.6 | 69 | 1 | 32,703 | **0.0%** | 100.0% | 33.4% | 3.9% | 35 | ❌ | ✅ | ✅ |
| 🥈 | Jon McBee — Elisa | Opus 4.6 | 331 | 6 | 126,338 | **3.3%** | 95.8% | 0.0% | 1.3% | 142 | ✅ | ✅ | ❌ |
| 🥇 | thinking | JetBrains×OpenAI | 5 | 1 | 27,128 | 80.0% | 100.0% | **100.0%** | 9.5% | **5** | ✅ | ❌ | ✅ |
| 🥈 | Scopecreep | JetBrains×OpenAI | 61 | 2 | 4,797 | 100.0% | 100.0% | 0.0% | 9.1% | 10 | ❌ | ✅ | ❌ |
| 🥇 | Le Chathlétique | Mistral MCP | 86 | 9 | 1,435 | **39.5%** | 100.0% | 0.0% | **30.5%** | 38 | ✅ | ✅ | ❌ |
| 🥈 | Team1 — S3 Butler | Mistral MCP | 14 | 2 | 1,279 | **71.4%** | 100.0% | 0.0% | **35.3%** | **7** | ✅ | ❌ | ❌ |
| 🥉 | EduAdapt | Mistral MCP | 24 | 1 | 8,359 | 100.0% | 100.0% | 0.0% | 11.4% | 11 | ✅ | ❌ | ❌ |
| 🥇 | ForgetMeNot | MongoDB Memory | 51 | 5 | 14,206 | 98.0% | 94.1% | 0.0% | 5.5% | 8 | ✅ | ❌ | ❌ |
| 🥉 | WebBrain | MongoDB Memory | 32 | 4 | 10,366 | 100.0% | 100.0% | 0.0% | 6.7% | **7** | ❌ | ❌ | ❌ |
| 🥇 | MealPrep | Neo4j | 37 | 4 | 8,669 | **24.3%** | 100.0% | **55.5%** | 20.9% | 11 | ❌ | ✅ | ❌ |
| 🥈 | Rehearsal | Neo4j | 7 | 3 | 6,588 | **14.3%** | 100.0% | **73.0%** | 12.7% | **5** | ❌ | ❌ | ❌ |
| 🥉 | ZooVision | Neo4j | 86 | 5 | 49,645 | **52.3%** | 98.8% | 0.0% | 18.9% | 23 | ✅ | ✅ | ❌ |
| 🥇 | openCortex | Codex | 303 | 2 | 21,634 | **0.0%** | 99.0% | 0.0% | 5.4% | 103 | ❌ | ❌ | ❌ |
| 🥉 | Paradigm | Codex | 21 | 4 | 795 | 100.0% | 100.0% | 28.4% | 28.7% | **4** | ❌ | ✅ | ❌ |
| 🥇 | Noclue — Kube SRE Gym | OpenEnv | 106 | 3 | 5,282 | **20.8%** | 100.0% | 0.0% | 13.6% | 22 | ❌ | ❌ | ❌ |
| 🥈 | Zero Shot Cancer | OpenEnv | 58 | 5 | 51,982 | **50.0%** | 98.3% | 0.6% | 13.4% | 18 | ✅ | ❌ | ✅ |
| 🥉 | Lambda — ShopRLVE-GYM | OpenEnv | 8 | 2 | 24,019 | **62.5%** | 100.0% | 0.0% | 7.1% | **3** | ❌ | ❌ | ❌ |
| 🥇 | Amelia for the Deaf | Persistent Context | 121 | 6 | 17,589 | 81.0% | 99.2% | 0.0% | 5.3% | 11 | ✅ | ❌ | ❌ |
| 🥈 | TraceCase | Persistent Context | 32 | 2 | 6,377 | 90.6% | 100.0% | **68.4%** | 6.8% | **7** | ❌ | ✅ | ✅ |
| 🥉 | Perpetual | Persistent Context | 24 | 2 | 2,956 | 100.0% | 100.0% | 0.0% | 12.6% | **4** | ✅ | ❌ | ✅ |
| 🥇 | MemoryAtlas | Qdrant | 5 | 1 | 7,288 | 80.0% | 100.0% | 31.9% | 11.3% | **3** | ❌ | ❌ | ❌ |
| 🥈 | Crowd Whisperer | Qdrant | 40 | 3 | 10,356 | 100.0% | 100.0% | 0.0% | 9.7% | 25 | ❌ | ❌ | ❌ |
| 🥇 | blartclaw | Zero to Agent | 51 | 3 | 5,453 | 98.0% | 100.0% | 0.0% | 13.3% | 12 | ✅ | ❌ | ❌ |
| 🥉 | Watchlog | Zero to Agent | 46 | 2 | 3,065 | 100.0% | 100.0% | 0.0% | 12.5% | 8 | ✅ | ❌ | ❌ |

## Pass rates

| Task | Pass | |
|---|---|---|
| `F-2c` author/committer drift | **27 / 28** (96%) | 🔒 |
| `F-11` single-file LOC share | 26 / 28 (93%) | |
| `F-3` opening-commit mass | **22 / 28** (79%) | 🔒 |
| `F-12` ≥8 distinct commit hours | 18 / 28 (64%) | |
| `F-10` lockfile present | **15 / 28** (54%) | 🔒 |
| `F-2a` commits in window | 14 / 28 (50%) | |
| `F-9` CI present | 8 / 28 (29%) | |
| `V-9` numeric claim in README | 6 / 28 (21%) | |

- **0 of 28 pass all eight.**
- **13 of 28** pass even the three measurable blocking tasks together.
- `F-2a` at 50% is a coin flip — it carries no information about winning.

Median winner: **43 commits · 3 authors · 9,609 own LOC · 11 distinct commit hours.**

## Three faults in the contracts, each found by running them

### 1 · LOC tasks do not exclude vendored code

`crowd-whisperer` checks in React: `react-dom.development.js` at 29,924 lines, 33,271 vendored
total. `F-11` reads **68.6% — FAIL** on raw LOC and **9.7% — PASS** once vendored code is excluded.
`F-3`, `F-5` and `V-6` share the denominator and the blind spot. Every LOC figure in the matrix
above already excludes vendored paths; without that correction the table would be wrong.

### 2 · `F-3` assumes the opening commit is the team's

`MealPrep` and `Rehearsal` have the **identical first commit** — sha `857113ee`, tree
`eeb9fea223003d8a04bf8201c613f02beae60321` — dated nine days before the event. The Neo4j writeup is
titled *one starter repo, three winners*. **The organizers supplied it.**

| | `F-3` as written | from the team's own first commit |
|---|---|---|
| MealPrep | **55.5% — FAIL** | **0.1% — PASS** |
| Rehearsal | **73.0% — FAIL** | **0.2% — PASS** |

`F-3` caps two winners at 1/5 for using the starter their event advertised.

### 3 · `F-2a` has no window shape

Qdrant ran five weeks, Neo4j and most CV events ran one day, Opus 4.7 ran six. The same threshold
over all of them asks different questions, and the 50% pass rate is the result. Winners routinely
commit before and after the stated date — `MemoryAtlas` finishes ten days early, `MealPrep` runs
seven days late.

## What the winners carry

| | share |
|---|---|
| any test files | 19 / 28 (68%) |
| media in the README (image, GIF or video) | 10 / 28 (36%) |
| a numeric claim in the README | 6 / 28 (21%) |

## What changed in the contracts because of this

Applied, with two external rubrics as corroboration — the hacktribe blueprint (Innovation 25 ·
Technical execution 25 · Impact & feasibility 25 · Presentation & demo 15 · Theme/sponsor 10) and
Derrell's PRIME (Problem · Real-world impact · Implementation · Messaging · Execution potential).

| Change | Evidence |
|---|---|
| **`V-10` added** — demo artifact present and reachable, blocking | Presentation & demo is 15% of one rubric and 1 of 5 PRIME letters; the repo had **no task for either**. The Mistral event judged a demo video plus two 5-minute pitches. |
| **`V-7` promoted to blocking** | "Innovation & originality" is a joint-heaviest 25% criterion. `V-7` was its only counterpart, non-blocking, and NOT-CHECKED in all 28 audits. |
| **`V-9` demoted to advisory** | 6 of 28 winners pass, and neither rubric asks for a numeric claim. Kept only because `V-8` needs the claim to reproduce. |
| **`vendored_loc`** on `F-3` `F-5` `F-11` `V-6` | fault 1 above |
| **`starter_sha`** on `F-3` | fault 2 above |
| **`window_kind`** on `F-1` `F-2a` `F-2b` | fault 3 above |
| **Feasibility restated** as forensic build-verification | the rubrics' "feasibility" asks whether a thing *can* be built; this scope asks whether it *was*. Two instruments, one name. |

Still open: neither rubric's **Impact** criterion (25% + 2 of 5 PRIME letters) has any task. That is
a deliberate omission, not an oversight — it is a judgment about the product, and nothing in a repo
measures it.

## Re-run under the machine-readable caps

The matrix above asks *which thresholds did each winner miss?*. Once the contracts' `Caps at`
column became machine-readable, a second and different question could be asked: **given those
caps, what ceiling does each scope land on?** A missed threshold only costs a score if the
contract says it caps something.

Reproduce with:

```bash
python3 research/rerun-winners.py --clones /tmp/winners     # 28 clones, keyed by winners-28.json
```

| Scope | Capped | At what |
|---|---|---|
| Feasibility | **17 / 28** | 6 at `1/5`, 11 at `2/5` |
| Value | **0 / 28** | — |
| Usability | **0 / 28** | — |

| Blocking task | Failed |
|---|---|
| `F-10` lockfile integrity → `2/5` | 15 / 28 |
| `F-3` opening-commit mass → `1/5` | 6 / 28 |
| `F-2c` author/committer drift → `1/5` | 1 / 28 |

Caps compose as a **minimum**, so the six repos that miss `F-3` land at `1/5` whatever else they
pass: TraceCase, Wrench Board, MealPrep, thinking, Medkit, Rehearsal.

### The two zeroes are the finding, and they are not passes

**Value and Usability cap nobody because none of their blocking tasks ran.** Every one needs
published criteria, a container, or a naive operator, and a clone supplies none of the three — so
each returns `UNEVALUABLE`, which is a fact about the instrument. A reader who takes `0 / 28
capped` as *28 clean projects* has invented a score the run never produced. The same caveat
applies to the 11 Feasibility repos with no cap: `F-6`, `F-7`, `F-8` and `F-2b` did not run there
either, so *uncapped* means *nothing we could measure caps it*, never *it passed*.

Two of the six `F-3` caps are the starter-repo fault already recorded above, not the projects':
MealPrep and Rehearsal cap at `1/5` because this run passes no `starter_sha`. Supplying the
organizers' sha `857113ee` clears both. **The caps inherit every fault the tasks have** — making
them machine-readable made them consistent, not correct.

### What the caps changed about the headline

Nothing about the projects, and one thing about how the earlier number should be read. **0 of 28
pass all eight measured tasks** stays true. But only **17 of 28** are *penalised* by that, because
`F-2a`, `F-11`, `F-12` and `F-9` are advisory — a winner can miss all four and take no cap at all.
The gap between those two numbers is the distance between *the contracts flag everyone* and *the
contracts punish most people*.

## What this does NOT establish

**28 winners, 0 losers.** The set is selected on the outcome, so no shared trait here is evidence
about winning — that is survivorship. The 10 events are also structurally different populations and
must not be pooled for any comparison.

The harvest does make the negative class reachable for the first time: **1,092 projects, of which
~42 won.** Auditing a sample of the ~1,050 non-winners is the one move that would turn any of this
into a claim about winning rather than a claim about the contracts.

What this establishes is narrower and solid: **the contracts, run unchanged against 28 projects
that demonstrably cleared their events' bars, fail every one of them.**
