# Scope: Feasibility

Verbatim audit contract. **Weight: 20.**

Core finding that shapes the contract: git author/committer dates are trivially forgeable, so the timeline must come from GitHub's server-side record, not the clone.

## Contract header

| Field | Value |
|---|---|
| input.event_url | window start/end + timezone + entrant roster |
| input.repo_url | winning project link |
| precondition | disqualifiers clear; V-1 criteria exist |
| invariant 1 | timeline verdict uses GitHub Events API, not git log — GIT_AUTHOR_DATE and GIT_COMMITTER_DATE are settable by the committer |
| invariant 2 | Events API retains ~90 days — capture within the window or the evidence expires |
| invariant 3 | COCOMO effort estimates assume human-typed code; heavy AI codegen breaks the model, so F-5 is advisory and F-6 carries the authorship verdict |
| output | feasibility.jsonl |
| verdict | score /5 · blocking pass/fail |

## Feasibility tasks

| ID | Task | Run by | devTool | Script | Output | Threshold | Blocks? |
|---|---|---|---|---|---|---|---|
| F-1 | Fix the window — start/end/TZ + entrant roster | judge, from event page | WebFetch | f1_window.sh | window.json | both timestamps + roster present | ✅ |
| F-2a | Claimed timeline | auto | git log | f2_timeline.sh | commit histogram | ≥80% inside window | ⬜ claimed only |
| F-2b | Observed timeline — server push events | auto | gh api .../events | f2_timeline.sh | push-events.json | ≥80% inside window | ✅ authoritative |
| F-2c | Tamper check — author vs committer date drift | auto | git log --format='%ad %cd' | f2_timeline.sh | date-drift.txt | drift <1h on ≥90% of commits | ✅ mismatch with F-2b = rewritten history |
| F-3 | Opening-commit mass | auto | git log --numstat | f3_dump.sh | first-commit LOC share | <50% of final LOC | ✅ |
| F-4 | Author roster match | auto | git shortlog -sne + Co-authored-by trailers | f4_authors.sh | authors.json | every author on roster | ✅ |
| F-5 | Effort plausibility | auto | scc (COCOMO dev-months) | f5_effort.sh | effort.json | ≲3× available person-hours | ⬜ advisory only |
| F-6 | Comprehension probe — 3 randomly picked functions, author explains + predicts output | judge, live, seeded random | ripgrep + shuf --random-source | f6_probe.sh | comprehension.json | 3/3 explained, ≥2/3 output predicted | ✅ the real authorship test |
| F-7 | Builds from clean clone | auto | Docker | f7_build.sh | exit code | exits 0 | ✅ |
| F-8 | Runs off the author's machine | auto | Docker / Actions runner | f7_build.sh | run log | payoff reached in neutral env | ✅ |
| F-9 | CI present + green | auto | gh run list | f9_ci.sh | run history | present, >85% green | ⬜ |
| F-10 | Lockfile integrity | auto | npm ci · pip-compile --generate-hashes · go mod verify · cargo --locked | f10_lock.sh | exit code | exits 0 | ✅ |
| F-11 | Complexity wall | auto | scc --by-file · CodeScene | f11_hotspot.sh | hotspots.json | no file >30% of LOC | ⬜ |
| F-12 | Cadence shape | auto | git log histogram | f2_timeline.sh | per-hour commit counts | ≥8 distinct commit hours | ⬜ one dump = F-3 signal |

## Metrics beyond tool + script

| Field | Applies to | Why |
|---|---|---|
| timeline_source: git \| events \| both | F-2 | a verdict from git log alone is unfalsifiable — record which source produced it |
| events_captured_at | F-2b | 90-day retention; after that the authoritative record is gone |
| entrants: n, hours_available | F-5 | denominator for the effort ratio; absent, the ratio is meaningless |
| ai_disclosed: bool | F-5, F-6 | if the event required disclosure, undisclosed heavy codegen is a rules issue, not a feasibility one |
| probe_seed | F-6 | random selection must be reproducible or the author can dispute the picks |
| probe_live: true, author_present: true | F-6 | the only task where the author's presence is required, not disqualifying |
| runs: 2 | F-7, F-10 | a build that passes once and fails once is a fail |
| squash_merged: bool | F-4 | squash rewrites authorship — fall back to Co-authored-by trailers and PR authorship |

## Output schema

```json
{
  "task": "F-2b",
  "scope": "feasibility",
  "repo": "https://github.com/owner/repo",
  "run_by": "auto",
  "tool": "gh api events",
  "script": "f2_timeline.sh",
  "timeline_source": "events",
  "events_captured_at": "2026-08-19T00:00:00Z",
  "result": { "push_events": 41, "inside_window": 39, "share": 0.95,
              "git_claimed_share": 0.95, "date_drift_violations": 0 },
  "threshold": "share >= 0.80 AND matches F-2a",
  "verdict": "PASS",
  "blocking": true,
  "evidence_path": "evidence/f2/push-events.json"
}
```

## Scripts

```bash
#!/usr/bin/env bash
set -euo pipefail
O=owner; R=repo; START=2026-08-15T09:00:00Z; END=2026-08-17T17:00:00Z
OUT=evidence; mkdir -p "$OUT"/{f2,f3,f4,f5,f6,f7,f9,f11}
git clone "https://github.com/$O/$R" src && cd src
# ---------- F-2b: AUTHORITATIVE timeline (server-side, unforgeable) ----------
gh api "repos/$O/$R/events" --paginate \
  --jq '.[] | select(.type=="PushEvent") | .created_at' > "../$OUT/f2/push-events.json"
gh api "repos/$O/$R" --jq '{created_at,pushed_at,default_branch}' > "../$OUT/f2/repo-meta.json"
# ---------- F-2a: claimed timeline ----------
git log --format='%ad' --date=iso-strict | sort > "../$OUT/f2/git-dates.txt"
awk -v s="$START" -v e="$END" '$0>=s && $0
# ---------- F-2c: tamper check — author vs committer drift ----------
git log --format='%H %ad %cd' --date=unix \
```
  | awk '{d=$3-$2; if (d3600) print $1, d}' \

  | tee "../$OUT/f2/date-drift.txt" | wc -l

# ---------- F-12: cadence shape ----------

git log --format=%ad --date=format:'%Y-%m-%d %H' | sort | uniq -c | tee "../$OUT/f2/cadence.txt"

# ---------- F-3: opening-commit mass ----------

FIRST=$(git rev-list --max-parents=0 HEAD | tail -1)

git show --numstat --format= "$FIRST" | awk '{s+=$1} END{print "first_commit_loc="s}'

scc --format json . | jq '[.[].Code] | add' | xargs -I{} echo "final_loc={}"

# ---------- F-4: authorship ----------

git shortlog -sne --all | tee "../$OUT/f4/shortlog.txt"

git log --format='%(trailers:key=Co-authored-by)' | sort -u >> "../$OUT/f4/shortlog.txt"

# ---------- F-5: effort (ADVISORY — COCOMO assumes human-typed code) ----------

scc --format json . > "../$OUT/f5/scc.json"

scc . | grep -Ei 'estimated|cost'

# ---------- F-6: seeded random function picker ----------

rg -n --no-heading -e '^\s*(export\s+)?(async\s+)?function\s+\w+' \

   -e '^\s*def \w+' -e '^func \w+' -e '^\s*(pub )?fn \w+' \

   | shuf -n3 --random-source=

# ---------- F-7 / F-8: clean build, neutral environment, twice ----------

for i in 1 2; do docker build --no-cache -t "feas:$i" . ; done

docker run --rm feas:1 2>&1 | tee "../$OUT/f7/neutral-run.log"

# ---------- F-10: lockfile integrity ----------

test -f package-lock.json && npm ci

test -f go.sum && go mod verify

test -f Cargo.lock && cargo build --locked

test -f requirements.txt && pip install --require-hashes -r requirements.txt

# ---------- F-9 / F-11 ----------

gh run list -R "$O/$R" -L 100 --json conclusion --jq '.[].conclusion' | sort | uniq -c

scc --by-file --format json . | jq 'sort_by(-.Code) | .[0:5]'

## Execution order

| Step | Tasks | Gate |
|---|---|---|
| 1 | F-1 | no window or roster → Feasibility unscorable, stop |
| 2 | F-2b first (evidence expires), then F-2a, F-2c, F-12 | F-2b <80% or F-2a/F-2b disagree → capped at 1/5, escalate to organizers |
| 3 | F-3, F-4 | F-3 ≥50% or unrostered author → capped at 1/5 |
| 4 | F-7, F-8, F-10 (auto) | any fail → capped at 2/5 |
| 5 | F-5, F-9, F-11 | advisory, no cap |
| 6 | F-6, live with authors, seed published | <3/3 explained → capped at 2/5 |

## Score bands

| /5 | Means |
|---|---|
| 5 | timeline clean on both sources · roster exact · clean build ×2 · lockfile integral · 3/3 comprehension |
| 4 | one advisory miss (effort ratio, CI, hotspot) |
| 3 | builds and runs neutrally, but cadence is one dump or CI absent |
| 2 | fails clean-build, lockfile, or comprehension probe |
| 1 | timeline outside window, sources disagree, or unrostered authorship |

| Field | Value |
|---|---|
| Quality-ladder tier | A — blocking detection |
| Came from | B — git log forensics with thresholds, trusting client-settable dates as evidence |
| Why A | the timeline verdict moved to a server-side, unforgeable source (Events API) with a cross-check that exits non-zero on disagreement; build, lockfile and roster checks all exit non-zero |
| Cheapest climb to S | organizers record a server-side snapshot at window open and close — the timeline becomes a fact of the event rather than something reconstructed afterward, and the 90-day expiry stops mattering |
