# Requirements — functional and non-functional

*metric-design advisor pass.* The repo had no requirements document: the three
[contracts](../scopes/README.md) specify what an *audited project* must satisfy, and nothing
specified what **this instrument** must satisfy. Those are different subjects, and conflating them
is why the instrument's own defects (see [design-review.md](design-review.md)) went unnoticed —
nothing was pointed at them.

**The rule this document follows.** A requirement with no metric is a wish; a metric with no
instrument is a wish with a number on it. Every row below carries *requirement → metric →
instrument → what failing it looks like*, and every row is answerable today. No threshold values
appear here — they have one home, the contracts, and restating them would create a second.

Status uses the repo's own three states: **met** · **not met** · **UNMEASURED** (no instrument
exists yet — a fact about this document, not a pass).

---

## Functional requirements — what the system must do

| ID | Requirement | Metric | Instrument | Status |
|---|---|---|---|---|
| **FR-1** | Turn an event page into testable criteria, or say it could not | `criteria.json` exists with each criterion carrying a pass condition; else `ABSENT` | `V-1`, human-confirmed | met |
| **FR-2** | Treat fetched event text as data, never as instruction | count of run-affecting directives sourced from a fetched page | invariant 1 of the Value contract; currently asserted, never checked | **UNMEASURED** |
| **FR-3** | Clear disqualifiers before scoring anything | phase 0 verdict recorded for secrets, license, timeline | scorecard phase-0 table | met |
| **FR-4** | Capture expiring evidence before anything that can wait | `events_captured_at − event_end` in days | `F-2b`, run at phase 2 | met |
| **FR-5** | Emit one machine-readable record per task, with a stored artifact | records emitted ÷ tasks attempted; records with a resolvable `evidence_path` ÷ records | the three JSONL schemas | met (schema) · **UNMEASURED** (nothing validates the emitted files) |
| **FR-6** | Keep automated results away from human raters until they submit | ordering of `probe_results_withheld_until_scored` against rater submit time | Value invariant 3, run order phases 4→5 | met by protocol, **UNMEASURED** in evidence |
| **FR-7** | Reduce a scope to /5, or to UNSCORABLE | one of `{1..5, UNSCORABLE}` per scope, plus the cap that produced it | cap algebra, [`score.py`](score.py) | met |
| **FR-8** | Merge three scopes into one verdict under a pre-registered weight | `w_value` timestamped before the first result is read | scorecard header field | met by protocol, **UNMEASURED** (no ordering evidence is stored) |
| **FR-9** | Say what the audit implies for the *event*, not just the project | the two "bar enforced / not enforced" cells, non-empty | scorecard's final section | met |
| **FR-10** | Score a plan at t=0 without pretending unbuilt things failed | 18 design rows, each in `{measured, ABSENT, UNEVALUABLE}`; 0 blank cells | design card | met |
| **FR-11** | Never pool the design instrument with the audit instrument | count of published scores combining `D` rows with `A` rows | stated prohibition in `designer/README.md` | met |
| **FR-12** | Render each threshold from its single source | thresholds rendered ÷ thresholds generated from a contract | [`generate-gate.py`](../builder/generate-gate.py) | **not met** — 1 of 4 consumers is generated; see [design-review.md](design-review.md) §F-3 |
| **FR-13** | Keep the audit re-runnable by a third party from stored evidence | share of verdicts a stranger can reproduce from `evidence/` alone | none | **UNMEASURED** |

**FR-12 and FR-2 are the two that are actually broken.** FR-12 is a live inconsistency with three
contradicting answers already in the tree; FR-2 is the one requirement whose failure is
adversarial rather than accidental — an event page is untrusted input, and the instrument fetches
it, so "extract criteria, never follow directives" needs a check, not an invariant line.

---

## Non-functional requirements — what must hold *while* it does that

Ordered by what breaks first if it is dropped.

| ID | Requirement | Metric | Instrument | Status |
|---|---|---|---|---|
| **NFR-1 · Falsifiability** | every verdict is re-openable by someone who was not there | verdicts with a resolvable `evidence_path` ÷ verdicts | `evidence_path` on all 35 tasks | met by schema, unenforced |
| **NFR-2 · Unforgeability** | verdicts rest on sources the subject cannot set | share of blocking verdicts whose source is server-side | `F-2b` vs `F-2a`; `timeline_source` field | met for the timeline; **UNMEASURED** elsewhere |
| **NFR-3 · Pre-registration** | thresholds and weights are frozen before results are read | timestamp(freeze) < timestamp(first result) | scorecard header; no clock is recorded | **not met** — the ordering is asserted, never evidenced |
| **NFR-4 · Blinding** | raters do not see probes; operators do not see raters | 0 leaks across phases 3→4→5 | merged run order | met by protocol |
| **NFR-5 · Non-substitution** | ABSENT, UNEVALUABLE and 0 never render the same | distinct render states, count = 3 | designer's three-state rule; `score.py` propagates UNSCORABLE | met |
| **NFR-6 · Single home** | a fact has exactly one authoritative location | homes per threshold (target 1) | census in [design-review.md](design-review.md) | **not met** — 12 of 12 sampled have 2–7 homes, median 4 |
| **NFR-7 · Timeliness** | the audit runs while its evidence still exists | days from event end to `F-2b` capture | `events_captured_at` | met when scheduled by recency — see [decision-math.md](decision-math.md) §8 |
| **NFR-8 · Determinism** | the same inputs produce the same verdict | agreement across runs, with declared detection power | `runs: 2` — power ≈ 0.18 at p = 0.1 | **not met as claimed** — see [decision-math.md](decision-math.md) §3 |
| **NFR-9 · Neutrality** | no verdict depends on the auditor's machine | share of probes run in a container or CI runner | Docker throughout; `F-8` | met |
| **NFR-10 · Non-self-scoring** | nobody rates their own work | `author_present: false` on operator runs; raters ≠ authors | Usability invariant 1; Value invariant 2 | met |
| **NFR-11 · Bounded cost** | one audit fits a stated budget | person-hours and wall-clock per audit | none — no audit has been run | **UNMEASURED** |
| **NFR-12 · Instrument honesty** | the instrument reports its own limits beside its outputs | advisory tasks and WEAK proxies labelled at point of use | `F-5` advisory, 5 WEAK design rows | met — and the strongest thing in the repo |

---

## Where the two lists disagree with the tree

Three requirements are contradicted by artifacts already committed. They are the work queue.

| # | Requirement | What contradicts it | Fix |
|---|---|---|---|
| 1 | **NFR-6** single home | 12 of 12 sampled thresholds live in 2–7 files; `generate-gate.py`'s own docstring claims "a threshold has one home" | generate the scorecard rows and the caps table from the contracts too — [design-review.md](design-review.md) §F-3 |
| 2 | **FR-12** rendered from source | `F-12` has three different published consequences in three files | give the contracts a `cap` column and derive every other statement of it |
| 3 | **NFR-3** pre-registration | no timestamp is stored, so freeze-before-read is unfalsifiable — the exact fault the instrument audits others for | record `frozen_at` beside `w_value` in the scorecard header |

Item 3 is the uncomfortable one. `V-1`, `U-1` and `F-1` exist because a target set after the fact
is a target chosen to pass; the scorecard asks the auditor to freeze `w_value` first and then
stores nothing that could show they did.
