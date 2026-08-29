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
| **3 — Auto probes** | `V-3 V-4 V-9 V-10` · `F-2a F-2c F-3 F-4 F-7 F-8 F-10 F-12` · `U-4 U-5 U-6 U-7 U-8 U-9 U-10` | All deterministic, all parallelizable. Run each twice — differing results mean the probe is flaky, not that the project passed. |
| **4 — Naive operators** | `U-2 U-3 U-11 U-12` | 🔥 **One shot per person.** No author present or reachable. Phase-3 results stay withheld. Every session recorded — an unrecorded run is not evidence. |
| **5 — Human rubric** | `V-2 V-7` (two raters) · `F-6` (live, seeded random) | Only now are phase 2–4 results revealed. `F-6` is the one task where author presence is required rather than disqualifying. |

Phase 4 before phase 5 is deliberate: operators must not have seen a rater's opinion, and
raters must not have seen the operator's struggle.

## Caps

Blocking failures **cap** the score, they don't subtract from it. The scope's score is the
lowest cap any failure triggered.

This table says **which failure caps at which level**. It deliberately carries no threshold
values — those live in the [contracts](../scopes/README.md), one home each.

**Superseded.** Caps are now declared per task, in the `Caps at` column of each contract's task
table — one home, machine-readable, and the source `api/runners.py` and `generate-gate.py` both
read. The table below is kept only as the historical merged view and **disagreed with the
contracts in four places** when it was checked: it capped `U-1` at 1/5 where the contract says
*unscorable*, and capped `F-9` and `F-12` where the contract's step 5 says *advisory, no cap*.

| Scope | Cap 1/5 | Cap 2/5 | Cap 3/5 |
|-------|---------|---------|---------|
| **Value** | `V-3` or `V-4` passes when it should break (staged demo) | `V-6` mock ratio over its bar · `V-10` no reachable demo artifact · `V-7` an off-the-shelf equivalent exists | `V-8` claimed number unreproducible |
| **Usability** | `U-1` payoff unreachable without the author | `U-6` README blocks don't execute as written | `U-5` environments short · `U-3` undocumented steps present · `U-2` cold clone over its bar |
| **Feasibility** | `F-2b` timeline under its bar, or `F-2a`/`F-2b` disagree, or `F-2c` drift over its bar, or `F-4` unrostered author, or `F-3` opening commit over its bar | `F-7`/`F-10` clean build or lockfile, or `F-6` comprehension fails | `F-12` one-dump cadence or `F-9` CI absent |

`V-1`, `U-1` or `F-1` missing does not cap — it makes that scope **unscorable**. Record it as
unscorable; do not substitute a low score, which reads as "measured and bad" rather than
"never measured".

## Overall verdict

```
overall = (value/5 × w_v + usability/5 × w_u + feasibility/5 × w_f) / (w_v + w_u + w_f)
```

The weights live in **one place**: the [scopes table](../scopes/README.md). They are the
operator's, not the source's — read the provenance note there before citing any total, including
why the freeze rule was not met for the weights currently set.

## Reading a result

The point of auditing a *winner* is not to catch it out. It's to learn where the bar actually
sat: a project that won with Usability 3/5 tells you the event's judges did not test a cold
clone, and that's a fact about the event you can exploit. Log that in the scorecard's
**What this says about the event** section, which is the section that feeds
[../builder/](../builder/).
