# Scope: Usability

Audit contract, captured from source — see [provenance](README.md#provenance). **Weight: see the [scopes table](README.md).**

Core constraint: a naive operator is single-use — each person is cold exactly once, so n is *consumed*, not sampled.

## Contract header

| Field | Value |
|---|---|
| input.repo_url | winning project link |
| input.payoff | frozen from U-1 before any run |
| precondition | V-1 criteria exist; disqualifiers clear |
| invariant 1 | operator is not an author, has not seen the repo, and no author is present or reachable during the run |
| invariant 2 | automated tasks run first; operator results collected before automated results are shown to anyone scoring |
| invariant 3 | every operator session is recorded — an unrecorded run is not evidence |
| output | usability.jsonl + session casts |
| verdict | Usability score /5 · blocking pass/fail |

## Usability tasks

| ID | Task | Run by | devTool | Script | Output | Threshold | Caps at |
|---|---|---|---|---|---|---|---|
| U-1 | Define the payoff — the one observable that means "it worked" | judge, from README/demo claim | none | manual | payoff.json | exactly 1, observable without the author | unscorable | 
| U-2 | Cold-clone time to payoff | naive operator ×2, timed | asciinema + clean container | u2_cold_clone_timing.sh | cold-clone.cast, minutes | median <10 min | 3/5 | 
| U-3 | Undocumented steps | auto, over U-2's recording | asciinema + comm | u3_undocumented_steps.sh | undocumented.txt | 0 | 3/5 | 
| U-4 | One-click run exists and works | auto | devcontainer CLI · Codespaces · docker compose | u4_oneclick.sh | exit code | present, exits 0 | — | 
| U-5 | Setup failure rate across environments | auto | Actions matrix | u5_environment_matrix.yml | matrix results | 3/3 green | 3/5 | 
| U-6 | README blocks actually run — extract every fenced shell block, execute in order, clean container | auto | awk + Docker | u6_readme.sh | readme-run.log | all blocks exit 0 | 2/5 | 
| U-7 | Prerequisites honesty | auto, falls out of U-6 | Docker | u6_readme.sh diff pass | missing-prereqs.txt | empty | — | 
| U-8 | Happy path scripted headless | auto | Playwright · Cypress · pexpect | u8_happy_path.sh | pass/fail + duration | passes, <2× human time | — | 
| U-9 | UI audit (web only) | auto | Lighthouse · pa11y / axe-core | u9_ui.sh | lh.json, pa11y.json | perf ≥70 · a11y ≥90 · 0 WCAG-A errors | — | 
| U-10 | Error recovery — 4 injected faults | auto | Docker + fault script | u10_faults.sh | faults.json | ≥3 of 4 name cause and fix | — | 
| U-11 | Doc sufficiency — payoff reached without opening source | auto, from session record | asciinema grep | u11_source_opens.sh | bool | true | — | 
| U-12 | SEQ per task, 1–7 | operator | none | manual | seq.json | median ≥5 | — | 

## Metrics beyond tool + script

| Field | Applies to | Why |
|---|---|---|
| operators: n, operator_is_naive: true | U-2, U-3, U-11, U-12 | naiveté is consumed on first contact; n=1 is an anecdote |
| median not mean | U-2 | n≤3 — a mean is dominated by one bad run |
| author_present: false | U-2 | a hovering author converts a usability test into a demo |
| session_cast path | U-2, U-3, U-11 | the recording is the evidence |
| assists: n | U-2 | any hint voids the timing — record and restart |
| matrix_size | U-5 | 3/3 on three identical Linux runners is 1/1 |
| blocks_total / blocks_failed | U-6 | a README with one block passing 1/1 is not documented |
| faults_injected: 4 | U-10 | fixed set, declared in advance, identical across submissions |
| ui_applicable: bool | U-9 | absent UI scores n/a, never 0 and never 100 |

## Output schema

```json
{
  "task": "U-6",
  "scope": "usability",
  "repo": "https://github.com/owner/repo",
  "run_by": "auto",
  "tool": "awk+docker",
  "script": "u6_readme.sh",
  "runs": 2,
  "deterministic": true,
  "result": { "blocks_total": 7, "blocks_failed": 2,
              "first_failure": "npm run seed", "missing_prereqs": ["postgres@16"] },
  "threshold": "blocks_failed == 0",
  "verdict": "FAIL",
  "blocking": true,
  "evidence_path": "evidence/u6/readme-run.log",
  "notes": "README omits DB provisioning; block 4 assumes a running server"
}
```

## Scripts

```bash
#!/usr/bin/env bash
set -euo pipefail
REPO="$1"; OUT=evidence; mkdir -p "$OUT"/{u2,u3,u5,u6,u8,u9,u10}
# ---------- U-6: do the README's own instructions work? ----------
git clone --depth 1 "$REPO" src && cd src
docker build -t submission .   # U-10 below runs this image; every scope builds the same tag
awk '/^```(bash|sh|shell|console)$/{f=1;next} /^```/{f=0} f' README.md \
  | sed 's/^\$ //' > "../$OUT/u6/readme-steps.sh"
cd ..
docker run --rm -v "$PWD/src:/w" -v "$PWD/$OUT/u6:/o" -w /w ubuntu:24.04 \
  bash -c 'set -x; bash /o/readme-steps.sh' 2>&1 | tee "$OUT/u6/readme-run.log"
grep -cE '^\+ ' "$OUT/u6/readme-run.log"
grep -iE 'command not found|no such file|cannot find' "$OUT/u6/readme-run.log" \
  > "$OUT/u6/missing-prereqs.txt" || true          # U-7 falls out here
# ---------- U-2: cold-clone run, recorded ----------
asciinema rec "$OUT/u2/cold-clone.cast" --command \
  "docker run --rm -it -e HISTFILE=/o/typed.txt -v $PWD/$OUT/u2:/o ubuntu:24.04 bash -l"
jq -r '.duration' "$OUT/u2/cold-clone.cast" 2>/dev/null || asciinema play -s 999 "$OUT/u2/cold-clone.cast"
# ---------- U-3: undocumented steps (u3_undocumented_steps.sh) ----------
sort -u "$OUT/u2/typed.txt"        > "$OUT/u3/typed.sorted"
sort -u "$OUT/u6/readme-steps.sh"  > "$OUT/u3/readme.sorted"
comm -13 "$OUT/u3/readme.sorted" "$OUT/u3/typed.sorted" | tee "$OUT/u3/undocumented.txt"
# ---------- U-11: did the operator open source to reach the payoff? (u11_source_opens.sh) ----------
grep -cE '\b(cat|less|vim|nano|code)\b .*\.(ts|js|py|go|rs)' "$OUT/u2/typed.txt" || echo 0
# ---------- U-4: one-click ----------
test -d src/.devcontainer && devcontainer up --workspace-folder src
test -f src/docker-compose.yml && docker compose -f src/docker-compose.yml up -d --wait
# ---------- U-9: UI ----------
lighthouse http://localhost:3000 --output json --output-path "$OUT/u9/lh.json" --quiet
pa11y --standard WCAG2AA --reporter json http://localhost:3000 > "$OUT/u9/pa11y.json"
# ---------- U-10: fixed fault set, identical for every submission ----------
for f in missing_dep unset_env bad_input port_taken; do
  docker run --rm -e FAULT="$f" submission > "$OUT/u10/$f.log" 2>&1 || true
done
```

### `u5_environment_matrix.yml` — setup failure rate across environments

```yaml
strategy:
  fail-fast: false
  matrix:
    os: [ubuntu-24.04, macos-15, windows-2025]
    node: [20, 22]
steps:
  - uses: actions/checkout@v4
  - run: bash evidence/u6/readme-steps.sh
```

## Execution order

| Step | Tasks | Gate |
|---|---|---|
| 1 | U-1 | no single observable payoff → Usability unscorable, stop |
| 2 | U-6, U-7 | any README block fails → capped at 2/5 |
| 3 | U-4, U-5, U-8, U-9, U-10 (parallel, auto) | U-5 <3/3 → capped at 3/5 |
| 4 | U-2, U-3, U-11, U-12 — operators, steps 2–3 results withheld until submitted | U-3 >0 or U-2 >10 min → capped at 3/5 |

## Score bands

| /5 | Means |
|---|---|
| 5 | README blocks 100% green · cold clone <10 min · 0 undocumented steps · one-click present |
| 4 | one of the above misses narrowly, rest clean |
| 3 | payoff reached, but needed inferred steps or >10 min |
| 2 | README instructions do not execute as written |
| 1 | payoff unreachable without the author |

| Field | Value |
|---|---|
| Tier | A — blocking detection: U-6 executes the documentation itself and exits non-zero |
| Moved from | B (Lighthouse + stopwatch, no executable check of the README) |
| Climb to S | U-6 runs in the submission's own CI, so a repo whose README does not execute cannot be submitted |
