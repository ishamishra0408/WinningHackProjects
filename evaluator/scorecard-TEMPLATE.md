# Audit — <Project> · <Event>

| Field | Value |
|-------|-------|
| event_url | |
| repo_url | |
| topic(s) | 1–7 |
| placement | 1st / 2nd / 3rd |
| audited on | YYYY-MM-DD |
| auditor(s) | |
| w_value chosen | **frozen before any result was read:** |
| F-2b captured within 90 days? | yes / no — *if no, the timeline verdict is `git`-only and unfalsifiable* |
| naive operators available | n = |

## Phase 0 — disqualifiers

| Check | Result | Evidence |
|-------|--------|----------|
| secrets in repo | | |
| license present | | |
| timeline sanity | | |

## Requirement map — one row per task

Columns follow the source prompt: requirement → tested? → how much achieved → how they
implemented it → proof.

### Value
| ID | Requirement | Tested? | Achieved | How they implemented it | Proof (evidence_path) |
|----|-------------|---------|----------|--------------------------|------------------------|
| V-1 | testable criteria extracted | | | | |
| V-2 | topic fit ≥3 of 4, evidence cited | | | | |
| V-3 | offline probe — demo must break | | | | |
| V-4 | credential-removal — must break | | | | |
| V-5 | demo path ≥1 file outside entrypoint | | | | |
| V-6 | mock ratio <20% of demo-path LOC | | | | |
| V-7 | no off-the-shelf equivalent | | | | |
| V-8 | claimed number within ±20% | | | | |
| V-9 | numeric claim present at all *(advisory)* | | | | |
| V-10 | demo artifact present and reachable | | | | |

### Usability
| ID | Requirement | Tested? | Achieved | How they implemented it | Proof |
|----|-------------|---------|----------|--------------------------|-------|
| U-1 | exactly 1 observable payoff | | | | |
| U-2 | cold clone → payoff, median <10 min | | | | |
| U-3 | 0 undocumented steps | | | | |
| U-4 | one-click run exists, exits 0 | | | | |
| U-5 | 3/3 environments green | | | | |
| U-6 | every README block executes | | | | |
| U-7 | prerequisites honest | | | | |
| U-8 | happy path scripted headless | | | | |
| U-9 | perf ≥70 · a11y ≥90 (or n/a) | | | | |
| U-10 | ≥3 of 4 injected faults name cause+fix | | | | |
| U-11 | payoff reached without opening source | | | | |
| U-12 | SEQ median ≥5 | | | | |

### Feasibility
| ID | Requirement | Tested? | Achieved | How they implemented it | Proof |
|----|-------------|---------|----------|--------------------------|-------|
| F-1 | window + roster fixed | | | | |
| F-2a | claimed timeline ≥80% in window | | | | |
| F-2b | **observed** push events ≥80% in window | | | | |
| F-2c | author/committer drift <1h on ≥90% | | | | |
| F-3 | opening commit <50% of final LOC | | | | |
| F-4 | every author on roster | | | | |
| F-5 | effort ≲3× available person-hours *(advisory)* | | | | |
| F-6 | 3/3 explained, ≥2/3 output predicted | | | | |
| F-7 | builds from clean clone ×2 | | | | |
| F-8 | runs off the author's machine | | | | |
| F-9 | CI present, >85% green | | | | |
| F-10 | lockfile integrity | | | | |
| F-11 | no file >30% of LOC | | | | |
| F-12 | ≥8 distinct commit hours | | | | |

## Scores

| Scope | Raw /5 | Cap triggered | Final /5 | Weight |
|-------|--------|---------------|----------|--------|
| Value | | | | *w_value* |
| Usability | | | | 25 |
| Feasibility | | | | 20 |
| **Overall** | | | | |

## Where it failed, and how it could have won

One row per gap. This is the section the source prompt asks for in plain words.

| Topic | Why it failed | How it could be winnable |
|-------|---------------|--------------------------|
| | | |

## What this says about the event

The most valuable output of auditing a winner. If a project won *despite* failing a scope,
that scope was not tested by these judges — which tells you where the real bar sat.

- **Bar that was actually enforced:**
- **Bar that was not enforced:**
- **Cheapest way to beat this field:**
