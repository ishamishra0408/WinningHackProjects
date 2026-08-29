# Decision math — the aggregation function, and the tradeoffs hiding inside it

*DataScientist advisor pass.* Everything below is computed by
[`score.py`](score.py) (`python3 spec/score.py --selftest`, 13 checks) rather than asserted.
No threshold value lives here — caps arrive already triggered, bands already read. Which
predicate fires which cap is the [contracts'](../scopes/README.md) business.

## 1 · The instrument contradicts itself at the last step

Every scope is scored **non-compensatorily**: a blocking failure sets a ceiling and the score is
the lowest ceiling triggered. `min`, not `−`. That is the model the whole repo is built on.

Then the merge is a weighted arithmetic mean:

```
overall = (value/5 × w_value + usability/5 × 25 + feasibility/5 × 20) / (w_value + 45)
```

which is **compensatory** — a 5/5 elsewhere buys back a 1/5 here. Four caps' worth of design
is spent making a staged demo fatal to Value, and the final line hands most of it back.

Here is the cost, at `w_value = 55`:

| Profile | arithmetic | geometric |
|---|---|---|
| clean on all three | 5.00 | 5.00 |
| **staged demo** — `V-3`/`V-4` pass when they must break, Value capped 1/5 | **2.80** | **2.06** |
| payoff unreachable without the author, Usability capped 1/5 | 4.00 | 3.34 |
| timeline outside the window, Feasibility capped 1/5 | 4.20 | 3.62 |
| mock-heavy demo path, Value capped 2/5 | 3.35 | 3.02 |
| mediocre and honest everywhere (3, 3, 3) | 3.00 | 3.00 |

Read the two bolded rows against the last one. **At `w_value = 45` the staged demo scores 3.00 —
exactly the honest mediocre project.** A project that faked the thing the contract exists to
detect is ranked identically to one that did everything adequately and lied about nothing. That
is not a weighting preference; it is the aggregator undoing the measurement.

**The fix is one line.** Use the weighted *geometric* mean, which is the merge that agrees with
the cap model:

```
overall = 5 · Π (score_i / 5) ^ (w_i / Σw)
```

Any scope at 0 sends the total to 0; a scope at 1/5 stays visible through the total. Both modes
are implemented in [`score.py`](score.py); pick one **and record which**, because the two disagree
by up to 0.74 on the profiles above and that is larger than most gaps between audited projects.

## 2 · `w_value` — stop trying to pick it, bound the decision instead

The repo's [open question](../README.md#open-question) is right to refuse a number. But refusing
is not the end of the analysis, because **most of the time the number does not matter and you can
prove it.**

For two projects *A* and *B* with normalized scope scores, *A* outranks *B* iff

```
w·Δv + 25·Δu + 20·Δf > 0        where Δx = a_x − b_x   (the denominator is common and positive)
```

so the rank flips at exactly one weight:

```
w* = −(25·Δu + 20·Δf) / Δv           (undefined when Δv = 0 — then rank never depends on w)
```

If `w* ∉ (0, 55]`, **the ranking is invariant over every admissible weight** and the honest report
is "the choice of `w_value` did not change the answer" — strictly stronger than defending a number
with no source. If it lands inside, you have to pick, and now you know it matters:

| Comparison | `w*` | Verdict |
|---|---|---|
| A(4,2,2) vs B(2,4,4) | 45.0 | inside — rank depends on the weight |
| A(5,3,3) vs B(3,4,4) | 22.5 | inside |
| A(5,5,4) vs B(4,5,5) | 20.0 | inside — even near-ties flip |
| any pair with Δv = 0 | — | invariant, report and move on |

The admissible range is `(0, 55]` and comes from the source, not from us: 100 total, 25 + 20
allocated, and the remaining 55 covers Value **plus any scope the capture missed**. So 55 is a
ceiling, not an estimate — treating it as the default silently asserts that nothing was missed.

**Rule.** Freeze `w_value` in the scorecard before reading any result (already required), *and*
report `w*` against every project you are comparing to. A verdict that survives the whole range is
reported as robust; one that does not is reported with the weight it depends on.

## 3 · `runs: 2` is an agreement check, not a determinism proof

Three contracts carry `runs: 2` with `deterministic: bool`, on the stated logic that differing
results mean the probe is flaky. Correct — but the *power* of that test is low. Probability that
`n` runs of a probe that fails with probability `p` do not all agree:

| p(flake) | n=2 | n=3 | n=5 | n=10 | n=20 | n=25 |
|---|---|---|---|---|---|---|
| 0.02 | 0.04 | 0.06 | 0.10 | 0.18 | 0.33 | 0.40 |
| 0.05 | 0.10 | 0.14 | 0.23 | 0.40 | 0.64 | 0.72 |
| **0.10** | **0.18** | 0.27 | 0.41 | 0.65 | 0.88 | 0.93 |
| 0.20 | 0.32 | 0.48 | 0.67 | 0.89 | 0.99 | 1.00 |

Two runs catch a 10%-flaky probe **18% of the time**. Catching it 9 times in 10 needs ~22 runs,
which no audit will spend.

**Do not scale the runs — scale the claim.** Rename the emitted field: `deterministic: true` is
not supported by two agreeing runs and should read `agreed_on_2_runs: true`. Reserve
`deterministic` for probes whose inputs are pinned (published seed, no network, fixed image), where
it is an argument rather than a sample. This costs one schema edit and removes an
unfalsifiable claim from every JSONL record the instrument emits.

## 4 · A median of two is a mean of two

`scopes/usability.md` requires **median not mean** for `U-2`, reasoning that at n ≤ 3 a mean is
dominated by one bad run. At the contract's own operator count that rationale does not hold:
**for n = 2 the median and the mean are the same number.** The stated protection is absent exactly
where it was purchased.

| n | median = mean? | What to report |
|---|---|---|
| 2 | **yes — identical** | the interval `[min, max]`, never a central value |
| 3 | no | the median, plus the interval |
| ≥4 | no | the median |

At n = 2, report both times and let the reader see the spread. A single number over two
observations conceals the only thing two observations can tell you.

Same defect, same fix, for `U-12` (SEQ median ≥5).

## 5 · Two raters and no agreement statistic

`V-2` and `V-7` run two independent raters, and the contract says to report raw agreement and
escalate to a third on disagreement. That is the right protocol. Do **not** upgrade it to Cohen's
κ: over 4 binary criteria, κ's variance is so large that it is compatible with almost any true
agreement, and a κ reported at k=4 is a statistic used decoratively.

Report instead: **per-criterion agreement, the disagreement list, and whether escalation fired.**
Three facts a reader can check beat one coefficient they cannot.

## 6 · `F-5` should publish an interval or publish nothing

The contract already knows COCOMO assumes human-typed code and marks `F-5` advisory. Advisory is
not enough — the number still gets read. Publish the ratio as a **declared interval**:

```
r  = COCOMO_hours / (entrants × window_hours)          the uncorrected ratio
r' ∈ [r / k, r]     where k = the AI-codegen multiplier you are assuming, stated explicitly
```

`k` is a declaration, not a measurement, so it belongs beside the figure the way
`designer/README.md` already handles `D6`. A point estimate from a model whose assumption you have
documented as violated is the one output most likely to be quoted back at you.

## 7 · The tradeoffs, stated as decisions rather than preferences

| Tradeoff | The two horns | What the math says | Decide by |
|---|---|---|---|
| **Cap vs. subtract** | ceilings are legible and brutal; subtraction is smooth and forgiving | caps are already chosen per scope — §1 shows the *merge* silently reverts to subtraction | make the merge geometric, or state in the scorecard that compensation is intended |
| **`w_value` point vs. range** | a point estimate is quotable; a range is honest | `w*` decides it per comparison, exactly (§2) | report `w*`; pick a point only when `w*` is inside `(0, 55]` |
| **More runs vs. narrower claims** | ~22 runs per probe, or drop the word "deterministic" | detection power table (§3) | narrow the claim; the runs are unaffordable |
| **More operators vs. accepting the interval** | naiveté is consumed, so n=2 is a budget, not a sample | at n=2 no central statistic is defensible (§4) | report the interval; buy a 3rd operator only if the median is load-bearing |
| **Audit now vs. audit well** | `F-2b` evidence expires at ~90 days | past 90 days Feasibility drops from an unforgeable source to a forgeable one — a tier drop, not a score drop | schedule by event recency (§8) |

## 8 · Scheduling falls out of the expiry, and it is a step function

`F-2b` reads the GitHub Events API (~90-day retention). The *quality* of a Feasibility verdict is
therefore not a smooth function of how long you wait:

```
tier(days_since_event) = A  if days_since_event < 90     (server-side, unforgeable)
                         B  otherwise                    (git log only — settable by the committer)
```

So audit priority is `1{days_since_event < 90}`, tie-broken by topic relevance — not by how
interesting the project looks. An event at day 85 outranks a more relevant one at day 95, because
after day 90 the second can never yield an A-tier Feasibility verdict at any effort.

Of the 16 events in [`research/events-by-topic.md`](../research/events-by-topic.md), this ordering
is the only input needed to pick which to audit first, and it is currently not recorded anywhere.

## 9 · Where the output is undefined, and why that is not a gap

`overall` is a **partial function**. If any scope is UNSCORABLE (`V-1`, `U-1` or `F-1` missing),
there is no total — `score.py` propagates UNSCORABLE rather than averaging over it. Substituting a
low score would report "measured and bad" for something never measured, which is the single
failure mode the three-state discipline in [`designer/`](../designer/README.md) exists to prevent.

`ABSENT`, `UNEVALUABLE` and `0` must render differently at every layer, including this one.
