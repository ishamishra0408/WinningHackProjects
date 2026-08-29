# Enforcement tiers — how strongly each threshold is actually enforced

The [scopes](../scopes/README.md) say what each threshold *measures*. This file says what happens
when one *fails*, and who is allowed to act on it. They are different questions, and only the
first was written down.

## Scope — which requirements this file covers

| | Functional | Non-functional |
|---|---|---|
| **Asks** | does the harness do the thing? | how well, against what bar? |
| **Test** | delete the number — meaning survives | delete the number — nothing remains |
| **Example** | `V-1` extract testable criteria | `U-2` median time to payoff <10 min |
| **Fails as** | it doesn't do X | it does X, too slowly / for too few |
| **Graded here** | no — see the oracle column below | **yes — every row** |

Functional requirements are graded by their **oracle** (what the detector compares against), not by
a tier. Two carry no oracle at all and are called out at the end.

## The triple

Every non-functional requirement is claimed as `(rung, precision, who may stop)`. A rung asserted
with no precision number is inadmissible, exactly as a judge-ruled verdict with no agreement number
is.

| rung | the question that decides it |
|---|---|
| **S** | is there any code path that produces the bad output? if no, S |
| **A** | does something mechanically **stop** it, no human in the loop? |
| **B** | is it **visible in the artifact** without anyone remembering to look? |
| **C** | does a **judge** rule, and is its agreement **measured**? |
| **D** | does someone have to **remember**? |

Two rules govern the claim:

- **A tier is claimed with evidence or it is D.** An exit code, an absent code path, a schema
  field, an agreement number. Never an adjective.
- **Nobody grades their own climb.** The contract that proposes a rung does not confirm it.

## The headline finding

All three contracts claim **tier A — blocking detection** in their own footers:

> `| Tier | A — blocking detection: every deterministic task exits non-zero on fail |` — value.md
> `| Quality-ladder tier | A — blocking detection |` — feasibility.md

**The claim is not evidenced.** A is *"something mechanically stops it, no human in the loop."*
This repo has no `.github/`, no workflow file, and no submission hook. Every probe is a script an
auditor chooses to run. Exiting non-zero is necessary for A and is not sufficient — **something has
to be listening to the exit code**, and nothing is.

- **Claimed rung: A. Evidenced rung: D**, climbing to B the moment a scorecard row makes the result
  visible without anyone remembering to look.
- Each contract already names its own climb to S. Every one of them is unbuilt.

## The twelve, tiered

`Precision` is the number that would make the rung admissible. **Every cell reads unmeasured**, which
is the finding, not an oversight in this table.

| ID | Bar | Claimed | Evidenced | Precision missing | Who may stop | Move that earns the rung |
|---|---|---|---|---|---|---|
| `V-3` `V-4` | offline / no-credential run breaks | A | **D** | false-positive rate | nobody | probe runs in the submission's own CI |
| `U-6` | all README blocks exit 0 | A | **D** | false-positive rate | nobody | CI runs the README; a repo whose README fails cannot submit |
| `F-7` `F-10` | clean build ×2 · lockfile integrity | A | **D** | false-positive rate | nobody | build gate on the submission repo |
| `F-2b` | ≥80% push events in window | A | **D** | — (server-side, unforgeable) | nobody | organizers snapshot at window open/close |
| `F-2c` | drift <1h on ≥90% of commits | A | **B** | false-positive rate | nobody | already emits a share; wire the exit code |
| `U-5` | 3/3 environments green | A | **D** | matrix must be 3 *distinct* environments | nobody | Actions matrix, not three identical runners |
| `V-6` | mock ratio <20% of demo-path LOC | A | **B** | denominator floor — a ratio over 40 LOC is not a ratio | nobody | fail the run when demo-path LOC < floor |
| `F-3` `F-11` | opening commit <50% · no file >30% | A | **B** | false-positive rate | nobody | wire the exit code |
| `F-12` | ≥8 distinct commit hours | ⬜ | **B** | — | nobody | count non-empty commits only |
| `F-9` | CI present, >85% green | ⬜ | **B** | — | nobody | count against a fixed test roster |
| `V-8` | claimed number within ±20% | ⬜ | **C** | reproduction variance across runs | nobody | declare the claim before measuring it |
| `U-2` `U-12` | median <10 min · SEQ median ≥5 | A / ⬜ | **C** | κ across operators, **not** raw agreement; n≤3 | nobody | pre-register the operator pool |
| `V-2` `V-7` | topic fit · differentiation | A | **C** | κ between judge-A and judge-B | nobody | report κ, escalate on disagreement |
| `F-6` | 3/3 explained, ≥2/3 predicted | A | **D** | **single judge — no agreement possible** | nobody | second judge, or the rung is D |

### Three rows worth reading twice

- **`F-6` is the harness's own "real authorship test"**, is blocking, and runs on **one judge with no
  agreement number**. One judge is not C. It is D.
- **`F-2c` passing proves nothing.** A forger who sets both `GIT_AUTHOR_DATE` and
  `GIT_COMMITTER_DATE` produces zero drift. Failing it is strong evidence; passing it is not
  evidence. Record it as a corroborator of `F-2b`, never as a clearance.
- **Every row reads `who may stop: nobody`.** The harness has caps but no andon. Until a name
  appears in that column, `🔒` in the [pre-submit gate](../builder/pre-submit-gate.md) is decoration.

## Which bars deserve to block

A bar earns blocking authority when **the cheapest way to improve the number is the improvement
itself**. On that test, four survive:

| Bar | Cheapest way to move the number |
|---|---|
| `V-3` `V-4` | wire a real network/credential call — *is* the fix |
| `U-6` | write a README that executes — *is* the fix |
| `F-7` `F-10` | build cleanly from a clean clone — *is* the fix |
| `F-2b` | push code during the window — *is* the fix |

The rest have a sub-five-minute path to a better number with no better project behind it: split the
file (`F-11`), split the opening commit (`F-3`), delete the failing test (`F-9`), commit empty every
hour (`F-12`), make the demo execute fewer files (`V-6`), pick a fast operator (`U-2`).

**Demote them to reported-not-blocking.** A blocking gate with an unmeasured false-positive rate is a
gate that gets switched off inside a quarter, and it takes the true positives with it.

## Two functional requirements with no oracle

`V-1` (extract ≥3 testable criteria) and `U-1` (define exactly one payoff) are the two tasks whose
absence makes a whole scope **unscorable** — and neither has anything to compare against. A human
confirms; nothing detects. Everything downstream inherits that.

## What to do next, in order

1. **Fill the `who may stop` column** for the four blocking bars. A bar with no named stopper is a
   preference with a number on it.
2. **Measure precision on those four only.** Pricing every bar's provenance costs more than most of
   these bars are worth.
3. **Demote the other eight** to reported-not-blocking, in one edit, before anyone relies on them.
4. **Correct the three contract footers** from `A` to `D`, or build the CI that earns the `A`.
