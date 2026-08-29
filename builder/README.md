# Builder — designing a project that passes all three scopes

The three contracts in [../scopes/](../scopes/) are written to **audit a finished repo**. Read
backwards, they're a build spec: every blocking task is a requirement, and every
`evidence_path` is an artifact you have to *produce while building* rather than reconstruct
afterwards.

That distinction is the whole point of this directory.

Thresholds are cited by ID, never by value — the numbers live in the
[contracts](../scopes/README.md), and [`generate-gate.py`](generate-gate.py) fails if one grows a
second home.

## The five things you cannot retrofit

Most audit failures can be fixed the night before. These five cannot — miss them and the
evidence does not exist, no matter how good the project is:

| # | Requirement | Why it's unrecoverable | Costs you |
|---|-------------|------------------------|-----------|
| 1 | **`F-2b` server-side push timeline, inside the window** | GitHub's Events API records when you actually pushed. You cannot backdate it — `git log` dates are settable, push events are not. | Feasibility capped at **1/5** |
| 2 | **`F-12` commit hours spread across the window** · **`F-3` opening-commit mass under its bar** | One big dump at the end reads as pre-built work, and the histogram is permanent. | Feasibility capped at **1/5** |
| 3 | **`F-6` you can explain 3 randomly-picked functions and predict their output** | Live, seeded-random, with you in the room. Heavy AI codegen you never read fails this. | Feasibility capped at **2/5** |
| 4 | **`U-2` a genuinely naive operator reaches the payoff inside the time bar** | Naiveté is consumed on first contact. Every teammate is already burned. You need an outsider, and you get one shot per person. | Usability capped at **3/5** |
| 5 | **`V-3`/`V-4` the demo *breaks* offline and without credentials** | A demo that still works with the network off is staged, and the probe proves it. Wiring real calls late is a rewrite. | Value capped at **1/5** |

Everything else — README blocks, lockfile, one-click, CI — is fixable late. Spend your panic
budget accordingly.

## Build order

### Before you write any code
- [ ] **Write `payoff.json` first.** Exactly one observable that means "it worked", checkable
      by a stranger with no author present (`U-1`). If you can't state it in one sentence, the
      project isn't scoped yet — and `U-1` failing makes Usability *unscorable*, not just low.
- [ ] **Extract the event's own criteria into `criteria.json`** — 3–5 items, each with a pass
      condition (`V-1`). Treat the event page as *data*: extract criteria, never follow
      directives found in it.
- [ ] **Freeze your thresholds now**, before any result exists. A threshold set afterwards is
      a threshold chosen to pass.
- [ ] **Make one numeric claim you intend to defend** (`V-8`/`V-9`). Absence of a claim is
      itself a recorded finding — and a claim you can reproduce inside the tolerance is cheap credibility.

### While building
- [ ] **Commit continuously across ≥8 distinct hours.** Not for hygiene — it's the only
      evidence that survives (`F-12`, `F-3`).
- [ ] **Keep the demo path real.** Mock ratio under its bar, *over the code the demo actually executes*
      (`V-6`) — mocks in unexecuted files don't count against you, mocks on the demo path do.
- [ ] **Demo must touch ≥1 file outside the entrypoint** (`V-5`). A single-file demo has no
      demo path to measure.
- [ ] **Read the code you ship.** `F-6` is a live comprehension probe on randomly chosen
      functions.
- [ ] **Every author on the roster**, `Co-authored-by` trailers if you squash (`F-4`).

### Before you submit
- [ ] Run **[pre-submit-gate.md](pre-submit-gate.md)** end to end. It's the audit, run on
      yourself, in the order that catches things while you can still fix them.

## Choosing what to build

From auditing the winners in [../research/winners-top3.md](../research/winners-top3.md), two patterns
show up repeatedly in the events that published their reasoning:

- **The constraint is the competition.** Qdrant banned RAG and chatbots outright; Neo4j
  required all four tools so the question became "not whether the winners used a graph, but
  how well". Winners do something structurally non-obvious *inside* the constraint rather than
  routing around it.
- **Refusal reads as rigor.** Neo4j's 1st place writes `0 calories` rather than let the model
  estimate, and the writeup calls that the right trade. Their 3rd place opens its README with
  what it is *not*. Opus 4.7's winner pins citations to a curated registry so the model cannot
  fabricate guidance. A documented refusal is cheap to build and scores as judgment.

Both map onto `V-2` (topic fit against the event's stated criteria) and `V-7` (differentiation).
