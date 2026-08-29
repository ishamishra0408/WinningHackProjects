# The Three Scopes

Three audit contracts, captured verbatim from source. Each scores a project **/5** with
blocking tasks that cap the score regardless of how well everything else went.

**This table is the one home for the scope weights.** Every other file cites the scope, never the
number.

| Scope | Weight | Asks | Contract |
|-------|--------|------|----------|
| **Value** | **30** | Does it do something real, against this event's actual criteria? | [value.md](value.md) |
| **Usability** | **30** | Can a stranger reach the payoff from a cold clone? | [usability.md](usability.md) |
| **Feasibility** | **40** | Was it actually built, by these people, in this window? | [feasibility.md](feasibility.md) |
| | **100** | | |

## Reading the task IDs

`V-…`, `U-…` and `F-…` are verbatim source keys, not descriptive names, and are deliberately
left unrenamed — they are the join key between these contracts, the
[builder](../builder/README.md), the [run order](../evaluator/README.md) and every filled
scorecard, and renaming them would desync all four from the source.

They are opaque on their own, so they get exactly one decoder: the requirement column of
[../evaluator/scorecard-TEMPLATE.md](../evaluator/scorecard-TEMPLATE.md), which lists all 36 IDs
with their plain-language requirement. Cite an ID anywhere else and gloss it inline; do not
start a second index.

## What makes these contracts rather than checklists

Three properties recur across all three, and they're the reason the model works:

1. **Deterministic before human.** Every scope runs its automated probes first and withholds
   those results from human raters until the raters have submitted. A rubric score anchored on
   a probe result isn't an independent measurement.
2. **Blocking tasks cap, they don't subtract.** A failed offline probe caps Value at 1/5 no
   matter how strong the idea is. Caps compose: the final score is the *lowest* cap triggered.
3. **Evidence or it didn't happen.** Every task names an `evidence_path`. A verdict without a
   stored artifact is not reviewable.

## Provenance

Captured from a Claude Code session transcript, not generated here. The capture was lossy, and
the following were repaired rather than re-pulled — **verify each against the original session
before trusting it**:

| File | Line | Was | Now | Reconstructed from |
|---|---|---|---|---|
| value.md | V-6 schema | `"threshold": "` | `"ratio < 0.20"` | the V-6 row's own threshold, `<20% of demo-path LOC` |
| feasibility.md | F-2a | `'$0>=s && $0` | `'$0>=s && $0<=e'` + count | F-2a's threshold, `≥80% inside window` |
| feasibility.md | F-2c | `if (d3600)` | `if (d<0) d=-d; if (d>3600)` | F-2c's threshold, `drift <1h` |
| feasibility.md | F-6 | `--random-source=` | `--random-source=<(yes "$PROBE_SEED")` | the `probe_seed` metric, "must be reproducible" |

Also repaired, without loss of meaning: all three script blocks closed their code fence early and
spilled the remaining shell into prose; `u5_environment_matrix.yml` had no fence of its own; and
`usability.md` ended on a line of chat from the source session.

Names were also made self-describing across the tree — see the naming commit. So these files are
**faithful in substance, not verbatim in text**.

## Who owns the caps

Each scope's own *Execution order* table is the source of truth for its caps. The table in
[../evaluator/README.md](../evaluator/README.md) is the merged view across all three, and
[../builder/README.md](../builder/README.md) restates the five that cannot be retrofitted. A cap
that changes must change in all three — the contract first.

## Two things that expire

These constrain the order you must run tasks in, across scopes:

- **F-2b** reads the GitHub Events API, which retains ~90 days. Miss the window and the
  authoritative timeline record is gone permanently — a `git log` verdict can't replace it,
  because author and committer dates are settable by the committer.
- **U-2/U-3/U-11/U-12** need a *naive* operator. Naiveté is consumed on first contact: each
  person is cold exactly once, so n is spent, not sampled. Burn your operators on a
  misconfigured run and you cannot re-run the task with the same people.

See [../evaluator/README.md](../evaluator/README.md) for the merged run order that respects both.

## The `Caps at` column, and one unresolved row

Each task's `Caps at` cell is the **one home** for what its failure costs: `1/5`, `2/5`, `3/5`,
`unscorable` (the task's absence makes the scope unmeasurable, it is not a low score), or `—` for
non-blocking. [`generate-gate.py`](../builder/generate-gate.py) and
[`api/runners.py`](../api/runners.py) both parse it, so the fact has one home and two readers.

### Conditional caps, and why `V-2` needed one

A cap may carry a condition: `2/5 when criteria_source=published`. **`V-2` is the case that forced
it.**

`V-2` scores topic fit against `criteria.json`, which `V-1` extracts from the event page. But
events differ: Neo4j and Qdrant published real criteria with pass conditions, while the Mistral
event published none — four adjectives from a kickoff deck, which an auditor had to turn into a
rubric. **Capping a project for missing a bar we inferred is capping it against our bar, not the
event's.**

So `V-2` caps at 2/5 only when the criteria were **published**, and is advisory when they were
`inferred` or drawn from the `research-fallback`. `V-1` now records which, in `criteria_source`.

**An unstated provenance does not cap.** An unknown is not a published bar, and the API treats a
missing `criteria_source` as advisory rather than assuming the strict case.

This is very likely why the source left `V-2` uncapped and never wrote down the reason.

## Weight provenance — read this before citing a total

The **source contracts** stated Usability = 25 and Feasibility = 20 and never stated Value's
weight, leaving 55 of 100 unaccounted.

The weights in the table above are **the operator's, not the source's**. On 2026-08-29 they were
set to Value 30 · Usability 30 · Feasibility 40, which:

- **fills the budget** — 100 points, nothing unaccounted, which the source never achieved;
- **matches the `w_value = 30` recommendation** already reached by the ds-ic pass in
  [../requirements.md](../requirements.md);
- **overrides two weights the source did state.** Usability moved 25 → 30 and Feasibility 20 → 40.
  Those are departures from the source, not gap-filling, and no source supports them.

**The freeze rule was not met.** The contracts require a weight be recorded before any result is
read. These were set after the Redline audit (Value 4 · Usability 3 · Feasibility 2) and after the
28-winner pass. Recorded here rather than hidden, because a weight chosen after results is exactly
what the rule exists to catch.

Mitigating, and checkable: under the source's own numbers Redline scores **0.67**; under these it
scores **0.58**. The choice made the operator's own project score *worse*, which is the opposite of
a weight chosen to pass.
