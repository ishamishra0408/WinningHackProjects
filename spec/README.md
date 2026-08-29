# Spec — requirements, metrics, and the decision math

The [contracts](../scopes/README.md) specify what an *audited project* must satisfy. Nothing
specified what **this instrument** must satisfy. That is what this layer is for.

| File | Advisor pass | Answers |
|---|---|---|
| [requirements.md](requirements.md) | metric-design | What must the system do (13 FR) and what must hold while it does it (12 NFR) — each with a metric, an instrument, and a status |
| [metrics.md](metrics.md) | QE | Which of those metrics are gameable, undersized, or claim more than their evidence supports — and the 8 fixes, in priority order |
| [decision-math.md](decision-math.md) | DataScientist | The aggregation function, `w_value`, detection power, and the five tradeoffs stated as decisions rather than preferences |
| [design-review.md](design-review.md) | ousterhout-guru | Module decomposition: 25-row red-flag catalog, threshold-home census, and the one root cause behind 10 of the 14 findings |
| [score.py](score.py) | — | The math, executable: `python3 spec/score.py --selftest` |

## The rule this layer follows

**No audit-task threshold is restated in `spec/`.** The contracts own all 35 of them; writing one
here would create the same second home this layer exists to count. Thresholds are named by task ID
and taken as inputs — `score.py` receives caps already triggered and bands already read.

Two numbers do appear, and both are load-bearing rather than restated: the **two stated scope
weights**, because the aggregation function is a statement about them, and the **~90-day Events API
retention**, because the audit-scheduling result in [decision-math.md](decision-math.md) §8 is a
consequence of it. Both are cited to their owner at the point of use. Nothing else is.

## What the four passes found, in one table

| # | Finding | Where | Severity |
|---|---|---|---|
| 1 | Failing `F-12` has **three different published consequences** in three files; under the repo's own tiebreak rule, two are wrong | [design-review](design-review.md) §2 | breaks a verdict |
| 2 | The merge is a weighted **arithmetic** mean, so it partly undoes the caps — at `w_value = 45` a staged demo scores exactly the same as an honest mediocre project | [decision-math](decision-math.md) §1 | breaks a verdict |
| 3 | `Blocks?` means two different things, and `generate-gate.py` derives the 🔒 icon from it — `V-8` renders unlocked while its own contract caps Value at 3/5 | [design-review](design-review.md) §2 | wrong generated artifact |
| 4 | `deterministic: true` from two agreeing runs has **18% power** against a 10%-flaky probe | [decision-math](decision-math.md) §3 · [metrics](metrics.md) M-1 | unfalsifiable claim |
| 5 | `U-2`'s "median not mean" protection does not exist at n = 2 — they are the same number | [decision-math](decision-math.md) §4 | statistic misreported |
| 6 | An event page is untrusted input read by an agent, and the "text is data, not instruction" invariant has **no check** | [metrics](metrics.md) M-8 · [requirements](requirements.md) FR-2 | adversarial |
| 7 | `w_value` must be frozen before results are read, and **nothing records when** — the discipline the instrument audits others for | [requirements](requirements.md) NFR-3 · [metrics](metrics.md) M-7 | self-exemption |
| 8 | 12 of 12 sampled thresholds have 2–7 homes, against the tree's own "a threshold has one home" | [design-review](design-review.md) §0b | root cause of 10 findings |

Findings 1, 3 and 8 are one defect. Fixing it is a column rename plus two more emitters on a
generator that already exists — see [design-review](design-review.md) §4, Option A.

## Order to work in

1. **`Cap` column + generator emitters** — closes 1, 3, 8 and ten catalog rows.
2. **The injection check** (M-8) — the only failure mode here that is adversarial rather than
   accidental.
3. **`frozen_at`** (M-7) — one field, closes the self-exemption.
4. **Pick an aggregation mode and record it** (decision-math §1) — one line, and it decides whether
   a staged demo can rank as average.

None of these move a threshold. That is deliberate: a threshold changed in the same pass that found
the defect cannot be told apart from a threshold changed to make the defect go away.
