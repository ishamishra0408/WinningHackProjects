# Pre-submit gate

The audit contracts run against your own repo, ordered so failures surface while you can still
fix them. Anything marked 🔒 caps your score if it fails — fix it or accept the cap knowingly.

Run from a **clean clone in a fresh container**, not your working tree. Half of these checks
exist specifically to catch things that only work on the author's machine.

> Every checkbox below carrying a task ID is **generated** by
> [`generate-gate.py`](generate-gate.py) from the [contracts](../scopes/README.md), so a threshold
> has one home. Edit the section order, the prose and the bash here; edit a threshold in the
> contract; edit the editorial note in the script's `NOTES`. Then re-run the script.

## 1 · Targets exist (else unscorable)

- [ ] `payoff.json` — exactly one observable, verifiable without you present
- [ ] `criteria.json` — ≥3 event criteria, each with a pass condition
- [ ] thresholds frozen and written down before running anything below

## 2 · The probes that must FAIL 🔒

Both of these are inverted: **passing is failing.** A demo that still works with no network or
no credentials is not calling anything real.

```bash
docker build -t submission .
docker run --rm --network none submission            # V-3 — must break
docker run --rm -e OPENAI_API_KEY= -e ANTHROPIC_API_KEY= -e API_KEY= submission   # V-4 — must break
```

<!-- checks: V-3 V-4 -->
- [ ] 🔒 `V-3` Offline probe — demo breaks or visibly degrades
- [ ] 🔒 `V-4` Credential-removal probe — breaks
<!-- /checks -->

## 3 · Does the README actually execute 🔒

Extract every fenced shell block from the README, run them in order in a clean container.

<!-- checks: U-6 U-7 U-4 U-5 -->
- [ ] 🔒 `U-6` README blocks actually run — all blocks exit 0; *the single most common cheap
      failure*
- [ ] `U-7` Prerequisites honesty — empty
- [ ] `U-4` One-click run exists and works — present, exits 0
- [ ] 🔒 `U-5` Setup failure rate across environments — 3/3 green; three *different* environments —
      3/3 on three identical Linux runners is 1/1
<!-- /checks -->

## 4 · Build and dependency integrity 🔒

<!-- checks: F-7 F-8 F-10 F-9 F-11 -->
- [ ] 🔒 `F-7` Builds from clean clone — exits 0, **twice**; passes once and fails once is a fail
- [ ] 🔒 `F-8` Runs off the author's machine — payoff reached in neutral env
- [ ] 🔒 `F-10` Lockfile integrity — exits 0; `npm ci` / `pip-compile --generate-hashes` / `go mod
      verify` / `cargo --locked`
- [ ] `F-9` CI present + green — present, >85% green
- [ ] `F-11` Single-file LOC share — no file >30% of LOC
<!-- /checks -->

## 5 · Timeline and authorship 🔒

Capture within 90 days of the event or the authoritative record is gone.

```bash
gh api "repos/<owner>/<repo>/events" --paginate > push-events.json   # F-2b
git log --format='%H %ad %cd' --date=unix > commit-dates.txt         # F-2c
awk '{d=$3-$2; if (d<0) d=-d; if (d>3600) print $1, d}' commit-dates.txt > date-drift.txt
echo "drift $(wc -l < date-drift.txt) / $(wc -l < commit-dates.txt) commits"
git shortlog -sne                                                    # F-4
```

<!-- checks: F-2b F-2c F-3 F-4 F-12 -->
- [ ] 🔒 `F-2b` Observed timeline — ≥80% inside window
- [ ] 🔒 `F-2c` Tamper check — drift <1h on ≥90% of commits; **report both numbers** — a violation
      count with no commit total is not a share
- [ ] 🔒 `F-3` Opening-commit mass, over the team's own first commit — <50% of final LOC
- [ ] 🔒 `F-4` Author roster match — every author on roster
- [ ] `F-12` Cadence shape — ≥8 distinct commit hours
<!-- /checks -->

## 6 · Demo honesty

<!-- checks: V-5 V-6 V-8 V-9 V-10 -->
- [ ] `V-5` Demo-path coverage → executed file set — ≥1 file executed outside main/entrypoint
- [ ] 🔒 `V-6` Mock ratio over the executed set only — <20% of demo-path LOC; **report the LOC
      denominator** — a ratio over 40 lines is not a ratio
- [ ] `V-8` Reproduce their claimed number — within ±20% of claim
- [ ] `V-9` Is there a claim at all? — claim stated with a number
- [ ] 🔒 `V-10` Demo artifact — present and reachable
<!-- /checks -->

## 7 · The cold-clone test 🔥 one shot

**Do this last, and do it for real.** You get one naive operator per person, ever.

- [ ] Operator is not an author, has not seen the repo
- [ ] No author present or reachable during the run — a hovering author turns a usability test
      into a demo
- [ ] Session is recorded (`asciinema`) — an unrecorded run is not evidence
- [ ] Any hint given voids the timing: record the assist and restart
<!-- checks: U-2 U-3 U-11 U-12 -->
- [ ] 🔒 `U-2` Cold-clone time to payoff — median <10 min
- [ ] 🔒 `U-3` Undocumented steps — 0
- [ ] `U-11` Doc sufficiency — true
- [ ] `U-12` SEQ per task, 1–7 — median ≥5
<!-- /checks -->

## 8 · Can you explain your own code 🔒

<!-- checks: F-6 -->
- [ ] 🔒 `F-6` Comprehension probe — 3/3 explained, ≥2/3 output predicted; published seed. The
      authorship test, and the one an AI-heavy build fails.
<!-- /checks -->

---

## If you're out of time

Fix in this order — highest cap relief per minute:

1. **`U-6` README blocks** — usually minutes, lifts a 2/5 Usability cap
2. **`F-7`/`F-10` clean build + lockfile** — lifts a 2/5 Feasibility cap
3. **`V-6` mock ratio** — delete mocks on the demo path, or make the demo execute the real path
4. **`U-2` cold clone** — needs a human you haven't burned; find one early or lose the option

Not fixable at this point: `F-2b`, `F-3`, `F-12` (timeline), `F-6` (comprehension),
`V-3`/`V-4` if the demo was never wired to anything real.
