# WinningHackathons

Research repo on **what actually wins hackathons** across the 7 topics we build in — so our own
project is designed to win rather than designed and then submitted.

## Topics

1. Agent Tool Call · 2. Retrieval · 3. Agent Memory · 4. Evals · 5. Loop Engineering ·
6. Graph Engineering · 7. Harness

## The three layers

The repo answers three questions in order. Each layer feeds the next.

| Layer | Question | Where |
|-------|----------|-------|
| **Evidence** | Who won, at which events, with what? | [data/](data/) |
| **Measurement** | How good was it *really*, on Value / Usability / Feasibility? | [scopes/](scopes/) + [evaluator/](evaluator/) |
| **Construction** | How do I build something that passes all three? | [builder/](builder/) |

## Layout

| Path | Contents |
|------|----------|
| [data/events-by-topic.md](data/events-by-topic.md) | 16 events mapped to the 7 topics, with relevance verdicts and gallery links. |
| [data/winners-top3.md](data/winners-top3.md) | Top 3 winners for every event, what each built, and a link. |
| [scopes/](scopes/README.md) | The three audit contracts, verbatim: [value](scopes/value.md), [usability](scopes/usability.md), [feasibility](scopes/feasibility.md). |
| [evaluator/](evaluator/README.md) | Merged run order, caps, and a [scorecard template](evaluator/scorecard-TEMPLATE.md) for auditing any won project. Results land in [evaluator/audits/](evaluator/audits/). |
| [builder/](builder/README.md) | The contracts inverted into a build spec, plus the [pre-submit gate](builder/pre-submit-gate.md). |
| [winners/](winners/_TEMPLATE.md) | Narrative deep-dives — demo shape, transferable moves. Complements the scorecard rather than replacing it: the scorecard measures, this one explains. |

## Workflow

1. Pick a topic; read its winners in `data/winners-top3.md`.
2. Audit two or three of them with `evaluator/` — the goal is not to catch them out, but to
   find **where the bar actually sat**. A project that won while failing a scope proves the
   judges didn't test that scope.
3. Feed that into `builder/` when speccing our own project.
4. Run `builder/pre-submit-gate.md` before submitting.

## Status

- Event table: 16 rows across 7 topics, all gallery URLs resolved.
- Top-3 winners: pulled for 14 of 16 events. Two have no ranked winners to pull — Enterprise
  MCP (still open voting) and Agentic Orchestration (6 unranked finalists).
- Scope contracts: all three captured.
- Audits run: **none yet** — `evaluator/audits/` is empty.

## Open question

The source contracts weight Usability 25 and Feasibility 20 but never state Value's weight.
Nothing here invents one. Set `w_value` before running a weighted total, and record it in the
scorecard *before* reading any result.
