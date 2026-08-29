# The Three Scopes

Three audit contracts, captured verbatim from source. Each scores a project **/5** with
blocking tasks that cap the score regardless of how well everything else went.

| Scope | Weight | Asks | Contract |
|-------|--------|------|----------|
| **Value** | *unset* | Does it do something real, against this event's actual criteria? | [value.md](value.md) |
| **Usability** | 25 | Can a stranger reach the payoff from a cold clone? | [usability.md](usability.md) |
| **Feasibility** | 20 | Was it actually built, by these people, in this window? | [feasibility.md](feasibility.md) |

## Reading the task IDs

`V-…`, `U-…` and `F-…` are verbatim source keys, not descriptive names, and are deliberately
left unrenamed — they are the join key between these contracts, the
[builder](../builder/README.md), the [run order](../evaluator/README.md) and every filled
scorecard, and renaming them would desync all four from the source.

They are opaque on their own, so they get exactly one decoder: the requirement column of
[../evaluator/scorecard-TEMPLATE.md](../evaluator/scorecard-TEMPLATE.md), which lists all 35 IDs
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

## Two things that expire

These constrain the order you must run tasks in, across scopes:

- **F-2b** reads the GitHub Events API, which retains ~90 days. Miss the window and the
  authoritative timeline record is gone permanently — a `git log` verdict can't replace it,
  because author and committer dates are settable by the committer.
- **U-2/U-3/U-11/U-12** need a *naive* operator. Naiveté is consumed on first contact: each
  person is cold exactly once, so n is spent, not sampled. Burn your operators on a
  misconfigured run and you cannot re-run the task with the same people.

See [../evaluator/README.md](../evaluator/README.md) for the merged run order that respects both.

## Known gap

The source states Usability = 25 and Feasibility = 20 but never states Value's weight.
45 of 100 is accounted for; the remaining 55 covers Value plus any scopes not captured here.
Nothing in this repo invents a number for it — pick one before running a weighted total.
