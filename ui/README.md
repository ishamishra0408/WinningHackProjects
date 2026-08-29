# UI — the two calls, in a browser

```bash
pip install -r ui/requirements.txt
streamlit run ui/app.py
```

| Mode | You give it | You get back |
|---|---|---|
| **Evaluate a project** | a GitHub link, plus whatever the event page tells you | every contract task with its value, its state, its reason, and what it caps |
| **Evaluate a spec** | the one-sentence payoff, the day-1 plan, and a tick per commitment | winnable or not, why, and the ordered work that is still undone |

**It renders. It computes no verdict.** Every number comes from
[`api/runners.py`](../api/runners.py) and [`api/spec.py`](../api/spec.py), which read the
[contracts](../scopes/README.md) at call time. No threshold, cap or weight is written here — a
second copy of any of them is exactly the drift `builder/generate-gate.py --check` exists to catch.

## What the screen refuses to do

- **No overall score.** Each scope's cap is a *ceiling*, and the banner says which blocking tasks
  did not run to produce it. `UNEVALUABLE` is drawn as its own state, never folded into a pass.
- **No prediction.** The project mode answers whether a repo *holds up*. 28 winning repos fail
  these contracts, and the page says so under the verdict.
- **The two modes are never pooled.** Different units. A design card that reads well is not a
  forecast that the built thing passes an audit.

## Why the spec mode asks you to tick boxes

The plan you paste is scanned for keywords, and each box is **pre-ticked** from that scan. The
scan is a suggestion and is labelled as one: *no Dockerfile yet* contains the same substring as
*Dockerfile on day 1*, so a keyword cannot read a negation, and a silently wrong `PASS` is worse
than an unanswered question. **Only the tick is sent.** These rows are declarations about a thing
that does not exist yet — the design layer reports them and never scores them.

## Known limits

| Limit | Consequence |
|---|---|
| The event link is not fetched | criteria counts, the window and `criteria_source` are typed in by hand |
| One dependency, unpinned by hash | `ui/requirements.txt` would fail `F-10` if this repo audited itself; `api/` stays stdlib-only for that reason |
| Single user, no auth | `streamlit run` on localhost, not a deployment |
