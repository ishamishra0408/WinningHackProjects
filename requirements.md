# Requirements — functional + non-functional, advisor-reviewed

What this framework must do (FR) and the qualities it must hold (NFR), derived from the four
layers and the 32 audit tasks, then improved by three advisor passes from
[factory-controls / QE Core / Advisor Builder](https://github.com/devpath56/factory-controls/tree/main/QE%20Core/Advisor%20Builder):

- **metric-design** (m-series) — whether a number may be published, and what it honestly measures
- **qe-ic-advisor** (q-series) — whether a bar can be gamed, and who may stop the line
- **ds-ic** (c-series) — whether a question is answerable from the data at all, and at what n

Task IDs (`V-…`, `U-…`, `F-…`, `D…`) are glossed inline; their single decoder remains the
requirement column of [evaluator/scorecard-TEMPLATE.md](evaluator/scorecard-TEMPLATE.md).
Threshold values still live **only** in the [contracts](scopes/README.md) — rows below that
propose a threshold change are proposals, contract-first, never a second home for the number.

## Functional requirements

| ID | The system shall | Where it lives | Advisor note |
|---|---|---|---|
| FR-1 | Extract 3–5 testable judging criteria from an event page, treating page text as data, never instruction | `V-1` (criteria extraction), `D1` (criteria count at t=0) | — |
| FR-2 | Score any finished repo /5 per scope, running every deterministic probe **before** any human rubric | all 32 tasks, [evaluator/](evaluator/README.md) phases 0–5 | — |
| FR-3 | Compose blocking failures as **caps, not subtractions**: scope score = min(rubric, lowest triggered cap) | each scope's execution-order table | formalised below, §Scoring function |
| FR-4 | Emit one JSONL record per task with an `evidence_path`; a verdict without a stored artifact is not reviewable | output schemas in all three contracts | — |
| FR-5 | At t=0, produce a 19-row design card where every row returns one of **measured / ABSENT / UNEVALUABLE** | [designer/](designer/README.md) | m08: extend the three states to audit-time too (NFR-7) |
| FR-6 | Generate the pre-submit gate's checkbox lines from the contracts, idempotently, so every threshold has one home | [builder/generate-gate.py](builder/generate-gate.py) | ousterhout: parse columns by header name, not position (see Findings F-OG-2) |
| FR-7 | Enforce a run order that captures expiring evidence first: naive operators and `U-13`'s judge runs (one shot per person, ~90-day retention) at phase 2; naive operators (`U-2/U-3/U-11/U-12`) before any rubric result is revealed | [evaluator/README.md](evaluator/README.md) merged run order | — |
| FR-8 | Compute an overall verdict only from **weights frozen before any result is read** | evaluator overall formula | c07/m05: refuse the combined headline until `w_value` is frozen — see §Scoring function |
| FR-9 *(new, q09)* | Carry a **pre-committed stop rule**: before the event, name which 🔒 gate failures block submission and who may invoke the stop | proposed addition to [builder/pre-submit-gate.md](builder/pre-submit-gate.md) header | a self-run gate with no stop rule defaults to "note it and submit anyway" |
| FR-10 *(q05/NFR-11)* — **DONE, and it failed** | Calibrate the gate against known-good repos before trusting any cap | [research/winner-audits.md](research/winner-audits.md): **28 winners across 10 events, 0 of 28 pass all eight measured tasks** | the calibration this row asked for has run. It found three faults in the contracts, not three faults in the winners |
| FR-11 *(new)* | Score the **demo artifact judges actually watch**, wherever it was submitted — repo, form, Discord or gallery field | `V-10`, `D19`, `demo_artifact` on [/evaluateproject](api/README.md) | Presentation & demo is 15% of the hacktribe rubric and one of PRIME's five letters; the contracts had no task for either |
| FR-12 *(new)* | Serve both layers over HTTP without pooling them into one score | [api/](api/README.md) — `POST /evaluateproject`, `POST /evaluatespec` | m05: the two instruments have different units, so the response carries `overall: null` and the reasons |

## Non-functional requirements

| ID | Quality | Requirement | Source / advisor |
|---|---|---|---|
| NFR-1 | Determinism | Every automated probe runs twice; differing results mean the probe is flaky, never that the project passed | contracts (`runs: 2`) |
| NFR-2 | Reproducibility | All randomness is seeded and the seed published **before** selection (`probe_seed` for the `F-6` comprehension probe) | contracts; c06: a self-picked seed after seeing the code voids the probe |
| NFR-3 | Auditability | No verdict without a stored `evidence_path` artifact | contracts |
| NFR-4 | Independence | Probe results are withheld from human raters until their scores are submitted; no author scores their own project | contracts, invariants |
| NFR-5 | Single source of truth | A threshold value has exactly one home (the contract); every other appearance is generated or a proposal | builder/ |
| NFR-6 | Idempotence | Generators change nothing when re-run on current input and exit 0 | generate-gate.py |
| NFR-7 *(new, m08)* | Three-state honesty | Every measurement — audit-time as well as design-time — returns one of **measured / ABSENT / UNEVALUABLE**. Proposed: widen the contracts' output-schema `verdict` beyond PASS/FAIL. ABSENT is a fact about the subject; UNEVALUABLE is a fact about the instrument; rendering either as FAIL is the instrument testifying about something it did not measure | metric-design m08 |
| NFR-8 | Timeliness | Evidence with a retention window is captured inside it: naive operators reserved before first contact (naiveté is consumed, not sampled) | contracts |
| NFR-9 *(new, m06)* | Threshold provenance | Every numeric constant states the n and tolerance it implies, or is labelled **convention** — "a bar that cannot state them is a convention wearing a measurement." Today the bars on `U-2`, `F-2a`/`F-2b`, `V-6`, `F-12` and `V-8` state none — cited by ID, because the values have one home and it is the contract. Proposal: add a provenance note per threshold row, contract-first | metric-design m06 |
| NFR-10 *(new, q06)* | Gaming resistance | Every **blocking** metric documents its cheapest green — the cheapest way to move the number without improving anything — and the counter that closes it (see §Gaming probes) | qe-ic-advisor q06 |
| NFR-11 *(new)* | Measured precision | A blocking probe carries a false-positive estimate before its cap is trusted; a tier-A gate with unknown precision is a future switched-off gate. Measured via FR-10 calibration runs | qe-ic-advisor tier triple |
| NFR-12 *(new, m09)* | Error direction | Any published figure with a known bias states the bias's direction in the same sentence (the pattern `D6` already sets: COCOMO reads pessimistic under AI codegen — generalise it) | metric-design m09 |
| NFR-13 *(new, c04)* | Pre-committed small-n rules | Any metric over n≤3 humans pre-commits its disagreement rule: `U-2` (cold-clone time) and `U-12` (ease score) at n=2 resolve a split verdict by a reserved third operator, decided **before** either runs | ds-ic c04 |

## Gaming probes (NFR-10 worked, one row per blocking metric attacked)

The qe-ic-advisor's corpus case for this whole section: a robotic arm rewarded on
block-to-target distance "achieves the goal by moving the table itself" (Chopra, 2018, OpenAI
gym FetchPush-v0). Each row asks: what is this metric's table?

| Metric | Cheapest green (the table) | Counter |
|---|---|---|
| `V-2` criterion evidence, term search over own source | seed the criterion's words into a comment — a decorative match reads like a real one; V-7 and a human rater exist for exactly that the number without touching the demo | the regex is advisory detection; the load-bearing pair is `V-3`/`V-4` (offline/no-credential probes), which no rename can move. Document that `V-6` alone is never sufficient evidence of realism |
| `U-6` README blocks all exit 0 | shrink the README to one trivial block — `blocks_failed == 0` has no floor, and the contract itself notes a 1/1 README "is not documented" | pair with `U-1`: the final README block must observably produce the frozen payoff, not merely exit 0. Proposal, contract-first |
| `D2` share of criteria with a named mechanism | name vague mechanisms ("an agent handles it") | require each mechanism to name the file/module planned to implement it — checkable at audit against `V-5` demo-path coverage |

## Scoring function (ds-ic deliverable)

**Per scope** (k ∈ {value, usability, feasibility}), with rubric score R_k ∈ [0,5] and triggered
caps C_k ⊆ {1,2,3} from that scope's execution-order table:

```
S_k = min( R_k, min(C_k) )        (min over an empty C_k is +∞ — no cap triggered)
```

Caps compose by minimum, never by subtraction — one triggered 1/5 cap dominates any rubric.

**Overall**, from [evaluator/README.md](evaluator/README.md), normalised to [0,1]:

```
Overall = (S_v·w_v + S_u·w_u + S_f·w_f) / (5·(w_v + w_u + w_f))
```

**SUPERSEDED 2026-08-29.** The analysis below held `w_u = 25` and `w_f = 20` fixed and solved for
the one unset weight. The operator has since set all three — **30 · 30 · 40**, in the
[scopes table](scopes/README.md) — so `w_value` is no longer the free variable. The maths is kept
because its conclusion is what matters and it did not change: **the weights are a ranking
decision**, which is why they must be frozen before results are read. They were not.

**Sensitivity to the unset weight** (the tradeoff the source never settled):

```
∂Overall/∂w_v = (S_v/5 − Overall) / (w_v + 45)
```

Raising `w_value` pulls Overall toward S_v/5 at a rate that shrinks as w_v grows. This is not
academic — rankings flip. For A = (5,3,3) and B = (3,5,4):

| | w_v = 20 | w_v = 35 | w_v = 55 |
|---|---|---|---|
| Overall(A) | 0.723 | 0.775 | 0.820 |
| Overall(B) | 0.815 | 0.775 | 0.740 |
| Winner | **B** | tie | **A** |

w_v = 35 is the exact indifference point for this pair — so the choice of `w_value` **is** a
ranking decision, which is why it must be frozen before any result is read (the repo's own rule,
now with the math showing why).

**Tradeoff table for freezing `w_value`** (a convention, labelled as one — NFR-9). *Historical: written when `w_u` was 25; the operator chose 30, the row this table recommended.*

| Option | Rationale | Risk |
|---|---|---|
| 25 | parity with Usability | understates that Value carries the most 1/5 caps |
| 30 | above Feasibility, below Usability's neighbourhood; mid-sensitivity | pure convention — no source support |
| 55 | fills the stated 100-point budget | overstates: the source says the remaining 55 covers "Value **plus any scopes not captured**", so 55 is an upper bound, not a value |

ds-ic recommendation: freeze **w_v = 30** as a labelled convention, record it in the scorecard
before the first audit, and never revisit it between audits of the same event (a weight moved
between projects is a weight chosen to produce an answer).

**Outcome:** the operator set `w_v = 30`, matching this recommendation, and also moved
`w_u` 25 → 30 and `w_f` 20 → 40, which this analysis did not cover and no source supports. Under
the source's own numbers the first audited project (Redline, `S = 4·3·2`) scores **0.67**; under the
new weights it scores **0.58** — the operator's choice cost their own project 9 points, which is
the opposite signature of a weight chosen to pass.

Denominator caution (c01): `F-2c`'s share is computed over **commits**, but the claim is
about when work happened — a single in-window push of pre-authored commits passes it. The
timeline verdict is honest only as the **conjunction** F-2c ∧ F-3; neither of the
four stands alone.

## Module-design findings (ousterhout-guru pass)

Full catalog run reported in the session; the two findings that survive with evidence:

| # | Finding | Evidence | Minimal fix |
|---|---|---|---|
| F-OG-1 | Duplicated documentation (red flag 24): a cap lives in **three homes** — the contract's execution-order table, evaluator/README's caps table, builder/README's five-unrecoverables. The repo knows ("a cap that changes must change in all three") but only the gate is generated | [scopes/README.md](scopes/README.md) §Who owns the caps | extend generate-gate.py (or a sibling `--check` mode) to diff the three views and exit non-zero on drift |
| F-OG-2 | Information leakage (red flag 2): generate-gate.py reads contract tables by **column position** (`cols[5]` threshold, `"✅" in cols[6]`); a reordered column renders wrong thresholds silently | [builder/generate-gate.py:53](builder/generate-gate.py) | locate Threshold/Blocks columns by header name; assert 35 tasks parsed (an m02 unit-existence check: print the count, fail on drift) |

## Change log

| Date | Change |
|---|---|
| 2026-08-29 | Initial FR/NFR set; metric-design, qe-ic-advisor, ds-ic passes; ousterhout module findings. All threshold-touching rows are proposals pending contract-first edits. |
| 2026-08-29 | **Weights set by the operator: Value 30 · Usability 30 · Feasibility 40.** Fills the 100-point budget the source left 55 short. `w_v = 30` matches this file's own ds-ic recommendation; `w_u` 25 → 30 and `w_f` 20 → 40 override weights the source did state. **The freeze rule was not met** — they were set after the Redline audit and the 28-winner pass, and that is recorded in scopes/README.md rather than hidden. |
| 2026-08-29 | Merged with the audit branch. 35 tasks → **36** (`V-10` demo artifact, blocking; `V-7` promoted; `V-9` demoted to advisory at 6/28 winner pass). Design card 18 → **19** rows (`D19`). **FR-10's calibration has now run** — 28 winners, 0 pass — and is recorded in research/winner-audits.md. Added FR-11 (demo artifact, wherever submitted) and FR-12 (the API). Three contract faults the calibration exposed are fixed: `vendored_loc` out of every LOC denominator, `starter_sha` on `F-3`, `window_kind` on `F-1`/`F-2a`/`F-2b`. |
