# Pre-submit gate

The audit contracts run against your own repo, ordered so failures surface while you can still
fix them. Anything marked 🔒 caps your score if it fails — fix it or accept the cap knowingly.

Run from a **clean clone in a fresh container**, not your working tree. Half of these checks
exist specifically to catch things that only work on the author's machine.

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

- [ ] 🔒 `V-3` offline run breaks or visibly degrades
- [ ] 🔒 `V-4` credential-stripped run breaks

## 3 · Does the README actually execute 🔒

Extract every fenced shell block from the README, run them in order in a clean container.

- [ ] 🔒 `U-6` all blocks exit 0 — *this is the single most common cheap failure*
- [ ] `U-7` no prerequisites needed that the README doesn't state
- [ ] `U-4` one-click path exists and exits 0
- [ ] 🔒 `U-5` 3/3 environments green — three *different* environments; 3/3 on three identical
      Linux runners is 1/1

## 4 · Build and dependency integrity 🔒

- [ ] 🔒 `F-7` builds from clean clone, **twice** — passes once and fails once is a fail
- [ ] 🔒 `F-8` reaches the payoff in a neutral environment
- [ ] 🔒 `F-10` lockfile integrity: `npm ci` / `pip-compile --generate-hashes` / `go mod verify` / `cargo --locked`
- [ ] `F-9` CI present and >85% green
- [ ] `F-11` no single file >30% of LOC

## 5 · Timeline and authorship 🔒

Capture within 90 days of the event or the authoritative record is gone.

```bash
gh api "repos/<owner>/<repo>/events" --paginate > push-events.json   # F-2b
git log --format='%ad %cd' > date-drift.txt                          # F-2c
git shortlog -sne                                                    # F-4
```

- [ ] 🔒 `F-2b` ≥80% of push events inside the window
- [ ] 🔒 `F-2c` author/committer drift <1h on ≥90% of commits
- [ ] 🔒 `F-3` opening commit <50% of final LOC
- [ ] 🔒 `F-4` every author on the entrant roster
- [ ] `F-12` ≥8 distinct commit hours

## 6 · Demo honesty

- [ ] `V-5` demo executes ≥1 file outside the entrypoint
- [ ] 🔒 `V-6` mock ratio <20% over the executed demo path only — **report the LOC denominator**;
      a ratio over 40 lines is not a ratio
- [ ] `V-8` your claimed number reproduces within ±20%
- [ ] `V-9` a numeric claim is present in the README at all

## 7 · The cold-clone test 🔥 one shot

**Do this last, and do it for real.** You get one naive operator per person, ever.

- [ ] Operator is not an author, has not seen the repo
- [ ] No author present or reachable during the run — a hovering author turns a usability test
      into a demo
- [ ] Session is recorded (`asciinema`) — an unrecorded run is not evidence
- [ ] Any hint given voids the timing: record the assist and restart
- [ ] 🔒 `U-2` median time to payoff <10 min
- [ ] 🔒 `U-3` 0 undocumented steps
- [ ] `U-11` payoff reached without opening the source
- [ ] `U-12` SEQ median ≥5

## 8 · Can you explain your own code 🔒

- [ ] 🔒 `F-6` pick 3 functions at random with a published seed. Explain each; predict the
      output of 2. This is the authorship test, and it's the one an AI-heavy build fails.

---

## If you're out of time

Fix in this order — highest cap relief per minute:

1. **`U-6` README blocks** — usually minutes, lifts a 2/5 Usability cap
2. **`F-7`/`F-10` clean build + lockfile** — lifts a 2/5 Feasibility cap
3. **`V-6` mock ratio** — delete mocks on the demo path, or make the demo execute the real path
4. **`U-2` cold clone** — needs a human you haven't burned; find one early or lose the option

Not fixable at this point: `F-2b`, `F-3`, `F-12` (timeline), `F-6` (comprehension),
`V-3`/`V-4` if the demo was never wired to anything real.
