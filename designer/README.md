# Designer — deciding what to build, before there is anything to audit

The [scopes](../scopes/README.md) audit a finished repo. Every one of their tasks needs the
artefact to exist. Given only a Luma event page and an idea, **26 of the 32 are ABSENT — a fact
about the subject, not a failure of the project.**

This layer is the other direction: the 19 checks that *can* run at t=0, each one buying a specific
ex-post task you would otherwise discover too late to fix.

Task IDs below are cited bare. Their plain-language requirements live in one place —
the requirement column of [../evaluator/scorecard-TEMPLATE.md](../evaluator/scorecard-TEMPLATE.md).

## Two instruments, never pooled

| | `D` — design-time *(this layer)* | `A` — audit-time *([evaluator](../evaluator/README.md))* |
|---|---|---|
| Input | event page + your plan | the built repo |
| Rows | 19 | 32 |
| Answers | *what do I build, and will it clear the bar* | *did it hold up* |
| Solve for | **your plan** | nothing — read-only |

Their units differ, so **there is no combined score.** A design card that reads well is not a
prediction that the project will pass an audit; it is a statement that the unrecoverable things
have been scheduled.

## Proxy strength

| | Means |
|---|---|
| **STRONG** | mechanically checkable from the event page and the plan, no judgment |
| **WEAK** | a declaration you make now and cannot verify until later — report it as a declaration, never as a measurement |

16 of 19 are STRONG. Those are the deterministic core: the same event page and the same plan
produce the same answer.

## Value — 8 rows, covering all 10 Value tasks

| Row | Check at t=0 | Buys | Strength |
|---|---|---|---|
| `D1` | count of published judging criteria on the event page | `V-1` | STRONG |
| `D2` | share of those criteria the plan names a mechanism for — **report both numbers** | `V-2` | STRONG |
| `D3` | closest existing tools, 15-min box, plus one delta sentence | `V-7` | STRONG |
| `D4` | plan names ≥1 authenticated external call the demo executes | `V-2` | STRONG |
| `D8` | demo crosses a module boundary — ≥2 planned files on the demo path | `F-11` | STRONG |
| `D9` | every planned stub on the demo path has a scheduled replacement slot | `V-2` | WEAK |
| `D10` | the number you intend to claim is written down **before** building | `V-8` `V-9` | STRONG |
| `D19` | a slot for recording the demo video or deck is in the plan, before the last hour | `V-10` | STRONG |

`D10` is free and it is the one people skip. A claim declared after the measurement is a claim
chosen to pass.

## Usability — 5 rows, covering 8 of 12

| Row | Check at t=0 | Buys | Strength |
|---|---|---|---|
| `D5` | the payoff states in one sentence, observable without you present | `U-1` | STRONG |
| `D7` | the single screen the payoff appears on is named; `ui_applicable` declared | `U-9` | STRONG |
| `D11` | ≥2 naive operators reserved by name, unburned | `U-2` `U-12` | STRONG |
| `D12` | one-click entrypoint named **and** 3 *distinct* target environments named | `U-4` `U-5` | STRONG |
| `D18` | README written alongside the build, not after | `U-3` `U-6` | WEAK |

`D11` is the only row with a deadline. Naiveté is consumed on first contact — reserve operators
before you burn one on a misconfigured run, because you cannot re-run the task with the same
person.

`D12`'s second half is the whole point: three identical Linux runners is one environment, not three.

## Feasibility — 6 rows, covering 12 of 14

| Row | Check at t=0 | Buys | Strength |
|---|---|---|---|
| `D6` | planned person-hours ÷ (team size × event hours), **from the event page** | `F-5` `F-14` | STRONG |
| `D13` | window fixed, and every intended contributor is on the entrant roster | `F-1` `F-4` | STRONG |
| `D14` | committed build start is at or after window open | `F-1` `F-2c` | STRONG |
| `D15` | LOC of any starter or prior code you intend to import, declared before start | `F-3` | STRONG |
| `D16` | committed read-rate — the share of shipped code you will actually read | `F-6` | WEAK |
| `D17` | Dockerfile, lockfile and CI are inside day-1 scope | `F-7` `F-8` `F-9` `F-10` | STRONG |

`D6` carries a known bias: COCOMO-style effort models assume human-typed code, so with heavy AI
codegen this ratio reads **pessimistic**. State that beside the figure or do not publish it.

`D13` and `D14` are five-minute checks against the event page that buy two blocking tasks which
cannot be fixed afterwards at any price.

## The 6 with no ex-ante proxy

Recorded here so a reader does not assume they were forgotten. **At t=0 these are ABSENT — a fact
about the subject — not FAIL.** Scoring them zero would be the instrument testifying about a
project that does not exist.

| Task | Why nothing at t=0 reaches it | When it first becomes measurable |
|---|---|---|
| `U-7` | falls out of executing the README; there is no README yet | first README run |
| `U-8` | plannable, but the timing bar needs a human baseline to divide by | after `U-2` |
| `U-10` | the fault set is the auditor's, injected into a running system | first neutral-environment run |
| `U-11` | a fact about an operator's recorded session | first cold clone |
| `F-2c` | a property of commits that do not exist | first push |
| `F-11` | a property of a finished tree | first build |

Do not invent a design-time stand-in for these. The correct design-time output for all six is
`ABSENT`, with the date they become measurable.

## Every row returns three states

| State | Means | Example input that reaches it |
|---|---|---|
| measured | the check ran and produced a value | event page lists 4 criteria → `D1 = 4` |
| **ABSENT** | a fact about the subject | event page publishes no criteria → `D1 = ABSENT` |
| **UNEVALUABLE** | a fact about the instrument | event page unreachable → `D1 = UNEVALUABLE` |

`D1 = ABSENT` and `D1 = 0` are different findings and must never render the same. When `D1` is
ABSENT, `D2` is undefined rather than zero — fall back to the topic's patterns in
[../research/winners-top3.md](../research/winners-top3.md) and record the substitution on the card.

## Run order

| Step | Rows | Gate |
|---|---|---|
| 1 | `D1` `D13` | `D1` ABSENT → substitute the research fallback and record it · roster mismatch → stop, you cannot enter |
| 2 | `D5` `D10` `D14` `D15` `D19` | all five are free, all five are unrecoverable later |
| 3 | `D2` `D3` `D6` | the go / no-go. `D6` above the bar → cut scope before writing code |
| 4 | `D4` `D7` `D8` `D12` `D17` | day-1 build commitments |
| 5 | `D11` | reserve operators now; they expire on first contact |
| 6 | `D9` `D16` `D18` | declarations — restate them on the card, do not score them |

## Relationship to builder/

[builder/](../builder/README.md) is the next layer, not an overlapping one.

- **This layer decides and predicts:** given this event, is the plan worth building, and what must
  be scheduled on day 1.
- **builder/ executes:** the build order, and the five things that cannot be retrofitted.

Where `builder/README.md` names an unrecoverable requirement, this layer holds the check that
schedules it. The requirement text itself lives in the contracts; neither layer restates it.
