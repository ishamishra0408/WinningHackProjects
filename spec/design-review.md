# Design review — module decomposition

**Advisor speaking: `ousterhout-guru`** (John Ousterhout's design philosophy, *A Philosophy of
Software Design*). The question asked was whether this repo's layers are deep or shallow and where
information leaks across them — squarely what this advisor is for.

**Two disclosures before any finding.**

- **`GROUNDING.md` was not readable.** The skill directs every invocation to read its own
  `GROUNDING.md`; the installed copy contains `SKILL.md` only. Every quote below is therefore
  taken from the verbatim-verified list inside `SKILL.md` itself, and no anecdote is used that is
  not named there. Nothing here is quoted from memory.
- **No self-grading.** `spec/` was written in this same pass, so it is **excluded from the review
  target**. Reviewed: `research/`, `scopes/`, `evaluator/`, `designer/`, `builder/`.

---

## 0 · What this is, and what it buys

- It is a **measurement instrument for hackathon projects**: three audit contracts (35 tasks) that
  reduce any finished repo to Value / Usability / Feasibility, each /5, with blocking failures that
  cap rather than subtract.
- It buys **a bar you can point at.** Auditing a *winner* is not prosecution — it locates where the
  judges' bar actually sat, and a scope the winner failed is a scope that event did not test.
- It buys **two unforgeable verdicts.** The timeline comes from server-side push events rather than
  `git log`, and the demo-realism verdict comes from probes that must *fail* to pass.
- It buys **an instrument that reports its own limits**: `F-5` is marked advisory because COCOMO
  assumes human-typed code, 5 of 18 design rows are marked WEAK declarations, and 6 audit tasks are
  recorded `ABSENT` at t=0 rather than scored zero. This is the strongest property in the tree and
  most of what follows is in service of protecting it.

**Four-risk review: not run, and not restated here.** The skill routes value/usability/feasibility/
viability to the `cagan-4-risks` skill, which is not installed in this session. That rubric has one
home and this is not it, so it is left unrun rather than paraphrased. It would in any case be the
wrong instrument: the target is committed artifacts, not a proposed capability.

---

## 0b · The census behind the structural proposal

The proposal in §4 is *"generate the scorecard rows and the caps table from the contracts, and give
the contracts a `cap` column."* That is a structural claim, so it carries its census rather than a
summary of one.

`prongs/reward.mjs importerCensus` does not exist in this tree and does not apply to a
markdown-plus-one-script repo. The equivalent for this target is **where a fact is stated**, run
mechanically over the tree:

**Threshold-home census** — files stating each threshold value, outside any generated region:

| Threshold (named by its task, never restated here) | Homes | Files |
|---|---|---|
| `F-2b` in-window push share | **7** | scorecard-TEMPLATE · evaluator/README · research/winners-top3 · scopes/README · scopes/feasibility · builder/README · pre-submit-gate |
| `U-5` environment matrix | **6** | scorecard-TEMPLATE · evaluator/README · scopes/usability · scopes/feasibility · generate-gate.py · pre-submit-gate |
| `V-6` mock ratio | **6** | scorecard-TEMPLATE · evaluator/README · scopes/README · scopes/value · builder/README · pre-submit-gate |
| `F-3` opening-commit mass | 5 | scorecard-TEMPLATE · evaluator/README · scopes/feasibility · builder/README · pre-submit-gate |
| `U-2` time to payoff | 5 | scorecard-TEMPLATE · evaluator/README · scopes/usability · builder/README · pre-submit-gate |
| `F-12` cadence shape | 4 | scorecard-TEMPLATE · scopes/feasibility · builder/README · pre-submit-gate |
| `V-8` claim reproduction band | 4 | scorecard-TEMPLATE · scopes/value · builder/README · pre-submit-gate |
| the two stated scope weights | 4 | evaluator/README · README · scopes/README · scopes/value |
| `F-2c` drift share | 3 | scorecard-TEMPLATE · scopes/feasibility · pre-submit-gate |
| `F-9` CI green rate | 3 | scorecard-TEMPLATE · scopes/feasibility · pre-submit-gate |
| `F-11` single-file LOC share | 3 | scorecard-TEMPLATE · scopes/feasibility · pre-submit-gate |
| `F-5` effort ratio | 2 | scorecard-TEMPLATE · scopes/feasibility |

**12 of 12 sampled thresholds have more than one home. Median 4, maximum 7.** Against the tree's
own claim, `README.md:31`: *"generated from the contracts by generate-gate.py, so a threshold has
one home."*

**Task-ID citation census** — how wide each module's dependence on the shared ID vocabulary is:

| File | distinct IDs cited |
|---|---|
| evaluator/scorecard-TEMPLATE.md | **35 of 35** |
| designer/README.md | **35 of 35** |
| evaluator/README.md | 31 |
| pre-submit-gate.md | 25 |
| scopes/feasibility.md | 16 *(owns 14)* |
| builder/README.md | 16 |
| scopes/usability.md | 13 *(owns 12)* |
| scopes/value.md | 9 *(owns 9)* |
| research/*.md | 0 |

Two consumers cite the entire vocabulary; the owners cite only their own. That shape is fine — it
is what a shared vocabulary looks like. The defect is not the citing, it is that the *values*
travel with the citations by hand.

---

## 0c · Neighbour table

Markdown, not a diagram, per this advisor's rule — the flowcharts added to `README.md` in the same
change are a separate deliverable answering a different question (what the pipeline computes), not
a second home for this table.

| direction | module | what crosses the boundary |
|---|---|---|
| imported by | `scopes/` ← `evaluator/`, `builder/`, `designer/`, root README | task IDs, thresholds, cap decisions, JSONL schemas |
| imports | `scopes/` → `evaluator/`, `builder/` | the ID decoder, the merged run order, the retrofit list |
| imported by | `evaluator/` ← `scopes/`, `designer/`, root README | the scorecard as ID decoder; the merged run order |
| imports | `evaluator/` → `research/` | which projects are worth auditing |
| imported by | `designer/` ← root README **only** | a filled design card |
| imports | `designer/` → `scopes/`, `evaluator/`, `builder/`, `research/` | task IDs to buy, the decoder, the retrofit list, fallback patterns |
| imported by | `builder/` ← `designer/`, root README | build order, pre-submit gate |
| imports | `builder/` → `scopes/`, `research/` | thresholds to render, winning patterns |
| imported by | `research/` ← `evaluator/`, `builder/`, `designer/` | events, winners |
| imports | `research/` → *(nothing outside itself)* | — |

Two facts fall out. `research/` imports nothing: it is the library, correctly at the bottom.
`designer/` is imported by nothing but the root README: it is a pure consumer, correctly at the
top. **The layering is sound.** `scopes/` sits in the middle importing *and* imported — expected
for the vocabulary owner, and the reason §2 lands where it does.

---

## 1 · Complexity diagnosis

All three symptoms are present, and all three trace to one cause: **the cap decision has no owner.**

- **Change amplification.** Changing one threshold means editing between 2 and 7 files, of which
  exactly one region regenerates.
- **Cognitive load.** To change a threshold safely a newcomer must hold six facts across four
  files: the contract's task row, the contract's execution-order gate, `generate-gate.py`'s
  positional column indices, its `NOTES` dict, the scorecard's requirement row, and the evaluator's
  merged caps table.
- **Unknown unknowns.** Nothing points from a contract to its downstream restatements. Edit
  `scopes/value.md` and `scorecard-TEMPLATE.md` goes stale silently — no error, no diff, no test.

The book's line for this is the one the repo half-applied: *"the most important technique for
achieving deep modules is information hiding."* The contracts hide their thresholds from exactly
one consumer.

---

## 2 · Red flags found — ranked by blast radius

### FAIL · Information Leakage — *the cap decision is stated in three places and they disagree*

**The Ask:** name the design decision in one sentence, then name the files that change if it
changes. *"What does failing `F-12` cost a project?"* Three files answer, three ways:

| Where | What it says |
|---|---|
| `scopes/feasibility.md:37` | `⬜ one dump = F-3 signal` — **non-blocking** |
| `scopes/feasibility.md:133` | its execution-order gate names `F-2b`, `F-2a`, `F-2c` — **`F-12` caps nothing** |
| `evaluator/README.md:43` | `one-dump cadence or CI absent` in the **Cap 3/5** column |
| `builder/README.md:18` | `Feasibility capped at **1/5**` |

And `scopes/README.md:58` declares the tiebreak: *"Each scope's own Execution order table is the
source of truth for its caps."* Under that rule **both other answers are wrong** — one by two
rungs. A builder reading `builder/README.md` will treat a one-dump cadence as fatal; an auditor
reading `evaluator/README.md` will cap at 3/5; the contract caps nothing at all.

**Mechanism.** `evaluator/README.md:43` imported a row from the wrong table. `scopes/feasibility.md:145`
is a **score band** — *"3 | builds and runs neutrally, but cadence is one dump or CI absent"* — and
bands and caps are different instruments. A band is where the rubric puts you; a cap is a ceiling
you cannot rise above. The merged view read one as the other.

The same fault, independently, in Value: `scopes/value.md:31` marks `V-8` `⬜` while
`scopes/value.md:112` reads *"claim unreproducible → capped at 3/5"* — **the same file
contradicting itself**, two tables apart.

**Minimal fix:** replace the `Blocks?` column with a `Cap` column valued in
`{none, 3/5, 2/5, 1/5, unscorable}`. The execution-order gate then derives from the task table
instead of restating it, and every downstream statement of a cap is generated.

### FAIL · Stale or Duplicated Documentation — *12 of 12 thresholds have ≥2 homes*

Census in §0b. `README.md:31` claims one home; `generate-gate.py:8` claims that the contracts own every
threshold value and that changing one there changes it everywhere. Doing exactly that today leaves `scorecard-TEMPLATE.md`, `evaluator/README.md` and `builder/README.md` stating
the old value, silently.

**Minimal fix:** extend `generate-gate.py` from one emitter to three — gate checkboxes (exists),
scorecard requirement rows, caps table — and add the census as a check that exits non-zero on a
second home.

### FAIL · Inconsistency — *`Blocks?` means two different things*

`⬜` means *"does not cap at 1/5"* in some rows and *"does not cap at all"* in others.
`scopes/feasibility.md:34` marks `F-9` `⬜` and `:136` confirms *"advisory, no cap"* — yet
`evaluator/README.md:43` caps 3/5 on CI absent. Meanwhile `V-8` is `⬜` and caps at 3/5.

**Consequence in shipped output:** `generate-gate.py:53` derives the 🔒 lock icon from that column
(`"✅" in cols[6]`), so `pre-submit-gate.md:87` renders `V-8` **unlocked** — telling a builder that
a claim they cannot reproduce is not score-affecting, when their own contract caps Value at 3/5
for it. The ambiguity is not academic; it has already produced a wrong generated artifact.

**Minimal fix:** the `Cap` column above. Same edit, second defect closed.

### FAIL · Vague Name — *`Blocks?`*

**The Ask:** from the name alone, say what it holds. You cannot — you must open the execution-order
table to learn *what* it blocks and *at what ceiling*. This is the root of the two findings above.
**Minimal fix:** rename to `Cap`, whose values answer the question.

### FAIL · Nonobvious Code + Missing Comment — *positional column indices, failing open*

```python
if len(cols) < 7:
    continue
tasks[m.group(1)] = (task, cols[5], "✅" in cols[6])
```

`generate-gate.py:49,53`. Read once: you cannot say what `cols[5]` is without opening a contract
and counting columns, and no comment says. Worse than opaque, it **fails open**: a contract row
that gains a column, or contains a `|` inside a cell, silently shifts the indices; a row that
loses one is silently `continue`d and its check simply never appears in the gate. A generator whose
failure mode is a *missing safety check* is the wrong failure mode.

**Minimal fix:** parse the header row once and look columns up by name; raise on an unmatched
column rather than `continue`.

### FAIL · Special-General Mixture — *the general renderer names seven specific task IDs*

`generate-gate.py:29`, `NOTES = {"U-6": …, "F-7": …}` — the general code names specific callers.
The docstring declares this ownership split deliberately, and the editorial content is genuinely
good, so the split stands. The defect is that it is **unchecked**: rename a task ID and its note
becomes silently dead weight.

**Minimal fix:** one line — assert `set(NOTES) <= set(rendered_ids)` and exit non-zero otherwise.

### FAIL · Overexposure — *`w_value` is required to read a single audit*

**The Ask:** write the smallest call that does the common thing. The common thing is *audit one
winner to find where the bar sat* — for which the three scope scores and the "what this says about
the event" section are the entire payload. The scorecard nonetheless forces the auditor to commit
`w_value`, a parameter that only matters when **ranking projects against each other**, the rare
case.

This is the book's *configuration parameters: flexibility vs. complexity* case study exactly: a
knob exposed because the module could not decide, pushed onto every caller including the ones who
will never use the result.

**Minimal fix:** make `overall` optional. Report three scope scores by default; require `w_value`
only when a comparison is drawn — and then report the crossover weight `w*` beside it
([decision-math.md](decision-math.md) §2), which is a fact the instrument can compute and the
auditor cannot.

### FAIL · Pass-the-Buck Configuration Parameter — *the same knob, from the other side*

**The Ask:** could the module compute this itself, and who has better information? For the *point
value* of `w_value`, the auditor does, and the repo is right to refuse to invent one. But for the
question that actually gets asked — *does the answer depend on it?* — the **instrument** has better
information: `w* = −(25·Δu + 20·Δf)/Δv` is exact and computable, and it says most of the time the
weight is irrelevant. The repo asks the caller anyway.

**Minimal fix:** already implemented — `crossover_w()` in [`score.py`](score.py).

### FAIL · Repetition · Change Amplification · Cognitive Load · Unknown Unknowns

Four rows, one defect, counted separately because each is separately observable: the caps are
written out three times (Repetition); one threshold change touches up to seven files (Change
Amplification); a safe edit requires six facts across four files (Cognitive Load); and no contract
points at its own restatements, so staleness is silent (Unknown Unknowns). **One fix closes all
four** — generate the restatements.

### FAIL · Hard to Describe — *the merged caps table*

Describe `evaluator/README.md`'s caps table in one sentence: *"the caps from all three contracts —
except where it imports a score band as a cap, and except where it caps on tasks the contract marks
advisory."* Two `except`s. **Minimal fix:** generate it.

---

## 3 · What passed, and why it matters that it did

Ten rows passed on their own evidence, and two are worth naming because they are the reason the
findings above are worth fixing rather than the repo worth replacing.

- **Not shallow.** *"The best modules are those whose interfaces are much simpler than their
  implementations."* `designer/` exports one artifact — a filled card — over 18 checks, a
  STRONG/WEAK proxy taxonomy, and a documented list of 6 things it deliberately cannot measure.
  `builder/` exports "run the gate" over a generated 25-check pipeline. These are deep.
- **Not temporally decomposed**, despite reading as a pipeline. The split is by *input and
  audience* — `designer/README.md` states it directly: `D` takes the event page plus your plan, `A`
  takes the built repo, *"their units differ, so there is no combined score."* That is
  *"different layer, different abstraction"* applied correctly, and the refusal to pool the two
  scores is the discipline most instruments skip.
- **Errors defined out of existence.** `ABSENT` (a fact about the subject) and `UNEVALUABLE` (a
  fact about the instrument) are first-class states that must never render as `0`. This is the
  Java-`substring` move — redesign so the error case cannot arise — applied to measurement, and it
  is unusual enough to be the repo's best idea.

---

## 4 · Design it twice

Both alternatives fix the same defect. They differ in what they treat as the source of truth.

**Option A — one generator, three emitters** *(recommended)*

Give the contracts a `Cap` column. `generate-gate.py` becomes `render.py` with three emitters:
gate checkboxes, scorecard requirement rows, merged caps table. Add two checks: no threshold has a
second home; every `NOTES` key is rendered.

| | |
|---|---|
| Cost | ~120 lines on top of the 96 that exist; the parser and the marker convention are already there |
| Buys | all four leakage findings, plus the wrong 🔒 on `V-8`, closed at once |
| Risk | more of the tree becomes generated, so a contributor who hand-edits a generated region loses the edit — mitigated by the marker comments already in use |

**Option B — contracts as data, prose as a view**

Move the 35 task rows into `contracts.yaml` and render every markdown table, contracts included,
from it.

| | |
|---|---|
| Cost | rewrites all three contracts; the "captured verbatim from source" provenance claim becomes harder to defend |
| Buys | a single machine-readable source; the JSONL schemas could validate against it |
| Risk | **it breaks the repo's best property.** `scopes/README.md` documents exactly which four lines were repaired during capture and asks readers to verify them against the original session. A YAML rewrite makes the contracts a derived artifact and that audit trail unverifiable |

**Take Option A.** Option B is the tidier architecture and the wrong trade: it buys schema
validation with the provenance that makes these contracts trustworthy in the first place. *"The
increments of software development should be abstractions, not features"* — the abstraction worth
adding here is *"a threshold is rendered, never typed"*, and Option A adds exactly that without
touching what the contracts are.

---

## 5 · Actions

**Ask before anything else is built:** *"If we change one threshold today, what breaks silently?"*
The answer is currently four files, and no test says so. Every hour spent filling
`evaluator/audits/` before that is fixed produces scorecards whose numbers may already disagree
with the contracts they cite.

**Protect under time pressure, in this order:**

1. The three-state discipline (`ABSENT` ≠ `UNEVALUABLE` ≠ `0`). It is the hardest thing here to
   rebuild and the first thing a deadline erodes.
2. The provenance section in `scopes/README.md`. Its value is that it is honest about a lossy
   capture; the moment it is tidied away, the contracts become unfalsifiable.
3. The `WEAK`/`advisory` labels. An instrument that stops reporting its own limits is not a faster
   instrument, it is a different one.

**Put in the spec:** the `Cap` column, before any audit is filled. It is a column rename plus a
generator emitter now; after ten scorecards exist it is a migration of ten hand-typed tables.

**The pattern to watch for.** The tree shows no sign of a *"tactical tornado"* — the generator, the
provenance section and the ABSENT taxonomy are all strategic investments made before they paid off.
The leakage found here is not carelessness; it is one abstraction that was **built for one consumer
and then relied on by four**. That is worth saying plainly, because the fix is to finish the
abstraction, not to distrust the design.

---

## Catalog run — 25 rows

Target: `research/` `scopes/` `evaluator/` `designer/` `builder/`. `spec/` excluded (self-grading).

| # | Flag | Verdict | Evidence | Minimal fix |
|---|---|---|---|---|
| 2 | Information Leakage | **FAIL** | `F-12` costs nothing / 3/5 / 1/5 in three files | `Cap` column; generate the restatements |
| 24 | Stale or Duplicated Documentation | **FAIL** | 12/12 thresholds, 2–7 homes each | census check, exits non-zero |
| 23 | Inconsistency | **FAIL** | `⬜` on `V-8` + `:112` caps at 3/5 | `Cap` column |
| 11 | Vague Name | **FAIL** | `Blocks?` | rename to `Cap` |
| 14 | Nonobvious Code | **FAIL** | `cols[5]`, `"✅" in cols[6]` | header-name lookup |
| 22 | Missing Comment on Nonobvious Code | **FAIL** | same site, no comment | same fix |
| 7 | Special-General Mixture | **FAIL** | `NOTES = {"U-6": …}` in the general renderer | assert `set(NOTES) <= rendered` |
| 4 | Overexposure | **FAIL** | `w_value` required to read one audit | make `overall` optional |
| 19 | Pass-the-Buck Config Parameter | **FAIL** | asks for `w_value`; `w*` is computable | `crossover_w()` |
| 6 | Repetition | **FAIL** | caps written out 3× | generate |
| 15 | Change Amplification | **FAIL** | 1 threshold → up to 7 files | generate |
| 16 | Cognitive Load | **FAIL** | 6 facts across 4 files to change one number | generate |
| 17 | Unknown Unknowns | **FAIL** | contracts do not point at their restatements | generate |
| 13 | Hard to Describe | **FAIL** | merged caps table needs two `except`s | generate |
| 1 | Shallow Module | PASS | `designer/`: 1 exported artifact over 18 checks | — |
| 3 | Temporal Decomposition | PASS | split is by input/audience, stated explicitly | — |
| 5 | Pass-Through Method | PASS | the merged run order adds cross-scope ordering | — |
| 8 | Conjoined Methods | PASS | `D` rows state their own check; the bought ID is a separate column | — |
| 9 | Comment Repeats Code | PASS | `NOTES` add context the tables cannot carry | — |
| 10 | Impl. Doc Contaminates Interface | PASS | provenance is a trust warning callers need | — |
| 12 | Hard to Pick Name | PASS | every module names in ≤2 words | — |
| 18 | Tactical Programming | PASS | generator, provenance, ABSENT taxonomy are all strategic | — |
| 20 | Special Cases Not Defined Away | PASS | `ABSENT`/`UNEVALUABLE` are first-class states | — |
| 21 | Over-decomposition for Length | PASS | each layer hides a different input from the next | — |
| 25 | Getter/Setter Chatter | N/A | no classes or fields — markdown plus one script | — |

**25 rows: 14 FAIL · 0 FIXED · 0 SUSPECT · 1 N/A · 0 NOT-CHECKED · 10 PASS.**

Counted, not scored. `FIXED` is 0 because nothing here has been re-run against a changed artifact —
findings are open until their own Ask is asked again. **Fourteen FAILs, one root cause:** ten of
them close when a threshold stops being typed twice.
