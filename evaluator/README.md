# Evaluator — scoring a won project

Point this at any winning project from [../research/winners-top3.md](../research/winners-top3.md) and
get a defensible /5 per scope plus one overall verdict.

**Inputs:** `event_url` (the event page — theme, prompt, published criteria) and `repo_url`.
**Output:** one folder under [audits/](audits/) containing `value.jsonl`, `usability.jsonl`,
`feasibility.jsonl`, an `evidence/` tree, and a filled
[scorecard-TEMPLATE.md](scorecard-TEMPLATE.md).

Start by copying the template:

```bash
cp evaluator/scorecard-TEMPLATE.md "evaluator/audits/<event-slug>-<project>.md"
```

## Merged run order

Each contract has its own execution order. Run them interleaved, not one scope at a time —
two classes of evidence expire, and both are unrecoverable.

| Phase | Tasks | Why here |
|-------|-------|----------|
| **0 — Disqualifiers** | secrets, license, timeline sanity | Precondition for all three contracts. Fail = stop, don't score. |
| **1 — Fix the targets** | `V-1` criteria · `U-1` payoff · `F-1` window+roster | All three are *unscorable-if-absent*. Freeze every threshold here, before any result is read. |
| **2 — Capture what expires** | `F-2b` (GitHub Events API) | ⏳ **Run this the moment phase 1 clears.** ~90-day retention; after that the authoritative timeline is gone and only forgeable `git log` dates remain. |
| **3 — Auto probes** | `V-3 V-4 V-9` · `F-2a F-2c F-3 F-4 F-7 F-8 F-10 F-12` · `U-4 U-5 U-6 U-7 U-8 U-9 U-10` | All deterministic, all parallelizable. Run each twice — differing results mean the probe is flaky, not that the project passed. |
| **4 — Naive operators** | `U-2 U-3 U-11 U-12` | 🔥 **One shot per person.** No author present or reachable. Phase-3 results stay withheld. Every session recorded — an unrecorded run is not evidence. |
| **5 — Human rubric** | `V-2 V-7` (two raters) · `F-6` (live, seeded random) | Only now are phase 2–4 results revealed. `F-6` is the one task where author presence is required rather than disqualifying. |

Phase 4 before phase 5 is deliberate: operators must not have seen a rater's opinion, and
raters must not have seen the operator's struggle.

## Caps

Blocking failures **cap** the score, they don't subtract from it. The scope's score is the
lowest cap any failure triggered.

| Scope | Cap 1/5 | Cap 2/5 | Cap 3/5 |
|-------|---------|---------|---------|
| **Value** | `V-3` or `V-4` passes when it should break (staged demo) | `V-6` mock ratio ≥20% of demo-path LOC | `V-8` claimed number unreproducible |
| **Usability** | payoff unreachable without the author | `U-6` README blocks don't execute as written | `U-5` <3/3 environments · `U-3` >0 undocumented steps · `U-2` >10 min |
| **Feasibility** | `F-2b` <80% in window, or `F-2a`/`F-2b` disagree, or unrostered author, or `F-3` opening commit ≥50% of final LOC | clean build / lockfile / `F-6` comprehension fails | one-dump cadence or CI absent |

`V-1`, `U-1` or `F-1` missing does not cap — it makes that scope **unscorable**. Record it as
unscorable; do not substitute a low score, which reads as "measured and bad" rather than
"never measured".

## Overall verdict

```
overall = (value/5 × w_value + usability/5 × 25 + feasibility/5 × 20) / (w_value + 45)
```

⚠️ `w_value` is not set by the source contracts. Pick and record it in the scorecard before
reading any result — a weight chosen after the fact is a weight chosen to produce an answer.

## Reading a result

The point of auditing a *winner* is not to catch it out. It's to learn where the bar actually
sat: a project that won with Usability 3/5 tells you the event's judges did not test a cold
clone, and that's a fact about the event you can exploit. Log that in the scorecard's
**What this says about the event** section, which is the section that feeds
[../builder/](../builder/).
