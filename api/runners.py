"""Measurement for the two endpoints.

Thresholds are NOT restated here. Every one is read from the contracts in
scopes/*.md at call time, so this file cannot drift from them -- the same rule
builder/generate-gate.py enforces.

Every task returns one of three states, never a bare boolean:

    MEASURED     the check ran and produced a value
    ABSENT       a fact about the subject -- the thing being measured is not there
    UNEVALUABLE  a fact about the instrument -- we could not run the check

A task needing Docker, a naive operator, the GitHub Events API or a live probe
returns UNEVALUABLE with the reason. That is not a pass and must never render
as one.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
from datetime import date, timedelta

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTRACTS = {"value": "scopes/value.md", "usability": "scopes/usability.md",
             "feasibility": "scopes/feasibility.md"}

SRC = re.compile(r"\.(py|js|jsx|ts|tsx|go|rs|java|rb|css|scss|html|sh|sql|ipynb|swift|kt|c|cpp)$")
VENDORED = re.compile(r"node_modules/|/lib/react|vendor/|dist/|build/|\.min\.|third_party/|\.venv/|site-packages/")

MEASURED, ABSENT, UNEVALUABLE = "MEASURED", "ABSENT", "UNEVALUABLE"


CAP_RE = re.compile(r"^\s*(\d)/5|^\s*(unscorable)|^\s*(uncapped)")


def _cap(cell: str) -> tuple[str | None, bool]:
    """(cap, blocking) from the Caps at column. '2/5' -> ('2/5', True);
    'unscorable' -> ('unscorable', True); 'uncapped' -> (None, True) and it is a
    declared defect; '—' -> (None, False)."""
    m = CAP_RE.match(cell)
    if not m:
        return None, False
    if m.group(1):
        return f"{m.group(1)}/5", True
    if m.group(2):
        return "unscorable", True
    return None, True


def load_weights() -> dict:
    """Scope weights, read from their one home: the scopes/README.md table."""
    text = (ROOT / "scopes" / "README.md").read_text()
    out: dict[str, int] = {}
    for scope in ("Value", "Usability", "Feasibility"):
        m = re.search(rf"^\|\s*\*\*{scope}\*\*\s*\|\s*\*\*(\d+)\*\*", text, re.M)
        if m:
            out[scope.lower()] = int(m.group(1))
    out["total"] = sum(v for k, v in out.items() if k != "total")
    out["source"] = "scopes/README.md, read at call time"
    return out


def load_tasks() -> dict[str, dict]:
    """Read every task id, its threshold and whether it blocks, from the contracts."""
    tasks: dict[str, dict] = {}
    for scope, rel in CONTRACTS.items():
        for line in (ROOT / rel).read_text().splitlines():
            m = re.match(r"^\|\s*([VUF]-\d+[abc]?)\s*\|(.+)", line)
            if not m:
                continue
            cols = [c.strip() for c in m.group(2).split("|")]
            if len(cols) < 7:
                continue
            cap, blocking = _cap(cols[6])
            tasks[m.group(1)] = {
                "scope": scope,
                "task": cols[0].split(" — ")[0].strip(),
                "threshold": cols[5],
                "cap": cap,
                "blocking": blocking,
            }
    return tasks


# Why a task cannot run from a clone alone. Naming the blocker is the point:
# an UNEVALUABLE with no reason is indistinguishable from a bug.
NEEDS = {
    "V-2": "two independent raters", "V-3": "Docker", "V-4": "Docker",
    "V-5": "a coverage run of the demo", "V-7": "a timeboxed prior-art search by a rater",
    "V-8": "the project's own eval script",
    "U-2": "a naive operator", "U-3": "a recorded operator session",
    "U-5": "a CI matrix over 3 distinct environments", "U-6": "a clean container",
    "U-7": "a clean container", "U-8": "a headless driver", "U-9": "a running UI",
    "U-10": "fault injection into a running system", "U-11": "a recorded operator session",
    "U-12": "an operator questionnaire",
    "F-2b": "the GitHub Events API", "F-6": "a live probe with the authors present",
    "F-7": "Docker", "F-8": "Docker",
}


def _git(repo: str, *args: str) -> str:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True,
                          text=True, errors="ignore").stdout


def _loc(repo: str, files: list[str]) -> int:
    total = 0
    for f in files:
        try:
            total += len((pathlib.Path(repo) / f).read_text(encoding="utf-8", errors="ignore").splitlines())
        except OSError:
            pass
    return total


# ---- V-10 -------------------------------------------------------------------
# Most events take the demo through a submission form, Discord or a gallery
# field -- not the repo. Scanning only the README answers "is it in the tree",
# which is a different question and the reason V-10 read FAIL on a project whose
# video was submitted and accepted.
MEDIA_IN_README = re.compile(r"!\[|<img|youtu\.be|youtube\.com|loom\.com|vimeo|\.mp4|\.webm|\.gif", re.I)


def _media_duration(path: pathlib.Path) -> float | None:
    """Duration from a WebM/Matroska or MP4 header. None when unreadable."""
    try:
        head = path.open("rb").read(400_000)
    except OSError:
        return None
    if head[:4] == b"\x1a\x45\xdf\xa3":                      # EBML / WebM
        scale, i = 1_000_000, 0
        while i < len(head) - 8:
            if head[i:i + 3] == b"\x2a\xd7\xb1":              # TimecodeScale
                n = head[i + 3] & 0x7F
                scale = int.from_bytes(head[i + 4:i + 4 + n], "big") or scale
                i += 3
            elif head[i:i + 2] == b"\x44\x89":                 # Duration (float)
                n = head[i + 2] & 0x7F
                raw = head[i + 3:i + 3 + n]
                try:
                    import struct
                    return round(struct.unpack(">f" if n == 4 else ">d", raw)[0] * scale / 1e9, 1)
                except Exception:
                    return None
            i += 1
    j = head.find(b"mvhd")                                     # MP4
    if j != -1:
        try:
            ts = int.from_bytes(head[j + 12:j + 16], "big")
            units = int.from_bytes(head[j + 16:j + 20], "big")
            return round(units / ts, 1) if ts else None
        except Exception:
            return None
    return None


def _reachable(url: str) -> tuple[bool | None, str]:
    """(True, ''), (False, reason) or (None, reason) when the CHECK itself failed.

    None is not a failure of the artifact -- a proxy 403 or a DNS error is a fact
    about the instrument, and must not render as a missing demo.
    """
    import urllib.error
    import urllib.request
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "winninghack/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return (200 <= resp.status < 400), f"HTTP {resp.status}"
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 405, 407, 429):
            return None, f"HTTP {exc.code} -- reachability check blocked, not the artifact"
        return False, f"HTTP {exc.code}"
    except Exception as exc:
        return None, f"check failed: {type(exc).__name__}"


def _demo_artifact(out: dict, set_, readme_text: str, declared: dict | None) -> None:
    """A declared submission outranks the README; neither found is ABSENT, not FAIL."""
    def finish(state, value, verdict, reason=None):
        out["V-10"].update(state=state, value=value, verdict=verdict, reason=reason)

    if declared:
        if declared.get("none"):
            finish(MEASURED, {"artifact_source": "none-declared"}, "FAIL",
                   None)
            return
        url = declared.get("url")
        path = declared.get("path")
        kind = declared.get("kind") or ("video" if (url or path) else None)
        if path:
            f = pathlib.Path(path)
            if not f.exists():
                finish(UNEVALUABLE, {"artifact_source": "submission", "path": path},
                       None, "declared file not readable from here")
                return
            finish(MEASURED, {"artifact_source": "submission", "artifact_kind": kind,
                              "path": path, "bytes": f.stat().st_size,
                              "duration_s": _media_duration(f)}, "PASS")
            return
        if url:
            ok, why = _reachable(url)
            if ok is None:
                finish(UNEVALUABLE, {"artifact_source": "submission", "url": url,
                                     "artifact_kind": kind}, None, why)
            else:
                finish(MEASURED, {"artifact_source": "submission", "url": url,
                                  "artifact_kind": kind, "reachable": ok,
                                  "detail": why, "duration_s": None},
                       "PASS" if ok else "FAIL")
            return

    hits = MEDIA_IN_README.findall(readme_text or "")
    if hits:
        finish(MEASURED, {"artifact_source": "repo", "artifact_kind": "in-readme",
                          "references": len(hits), "duration_s": None}, "PASS")
    else:
        finish(ABSENT, {"artifact_source": None},
               None,
               "no artifact in the repo and none declared -- most events take the demo "
               "through a form, Discord or a gallery field. Pass demo_artifact "
               "{url|path|none:true} to resolve this.")


def audit_repo(repo_url: str, window_end: str | None = None, window_days: int = 1,
               starter_sha: str | None = None, demo_artifact: dict | None = None) -> dict:
    """Run every task computable from a clone. Everything else is UNEVALUABLE."""
    tasks = load_tasks()
    out = {tid: {**meta, "state": UNEVALUABLE, "reason": NEEDS.get(tid, "not implemented"),
                 "value": None, "verdict": None} for tid, meta in tasks.items()}
    tmp = tempfile.mkdtemp(prefix="wh-audit-")
    repo = os.path.join(tmp, "src")
    try:
        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_LFS_SKIP_SMUDGE": "1"}
        clone = subprocess.run(["git", "clone", "--quiet", repo_url, repo],
                               capture_output=True, text=True, env=env, timeout=300)
        if clone.returncode:
            return {"error": "clone failed", "detail": clone.stderr.strip()[:300], "tasks": out}

        files = _git(repo, "ls-files").splitlines()
        own = [f for f in files if SRC.search(f) and not VENDORED.search(f)]
        vendored = [f for f in files if SRC.search(f) and VENDORED.search(f)]
        loc, vendored_loc = _loc(repo, own), _loc(repo, vendored)
        commits = int(_git(repo, "rev-list", "--count", "HEAD").strip() or 0)

        def set_(tid, value, ok, **extra):
            out[tid].update(state=MEASURED, value=value, verdict="PASS" if ok else "FAIL",
                            reason=None, **extra)

        if not commits:
            return {"error": "empty repository", "tasks": out}

        # F-2c  author/committer drift -- a share, so the denominator ships with it
        pairs = [l.split() for l in _git(repo, "log", "--format=%H %ad %cd", "--date=unix").splitlines()]
        pairs = [p for p in pairs if len(p) == 3]
        drift = sum(1 for _, a, c in pairs if abs(int(c) - int(a)) > 3600)
        share = 1 - drift / len(pairs)
        set_("F-2c", {"drift_violations": drift, "commits_total": len(pairs),
                      "within_1h_share": round(share, 3)}, share >= 0.90)

        # F-3  opening mass, over the TEAM's first commit when the event shipped a starter
        first = (_git(repo, "rev-list", "--max-parents=0", "HEAD").split() or [""])[-1]
        base = first
        if starter_sha:
            after = [c for c in _git(repo, "rev-list", "--reverse", "HEAD").split()
                     if not c.startswith(starter_sha)]
            base = after[0] if after else first
        added = sum(int(x.split()[0]) for x in _git(repo, "show", "--numstat", "--format=", base).splitlines()
                    if x.split() and x.split()[0].isdigit()
                    and SRC.search(x.split()[-1]) and not VENDORED.search(x.split()[-1]))
        set_("F-3", {"opening_loc": added, "own_loc": loc,
                     "share": round(added / loc, 3) if loc else None,
                     "measured_from": "team_first_commit" if starter_sha else "repo_first_commit",
                     "vendored_loc": vendored_loc},
             bool(loc) and added / loc < 0.50)

        # F-11  single-file share, vendored excluded from BOTH sides
        biggest = max(((_loc(repo, [f]), f) for f in own), default=(0, ""))
        set_("F-11", {"largest_file": biggest[1], "largest_loc": biggest[0],
                      "own_loc": loc, "vendored_loc": vendored_loc,
                      "share": round(biggest[0] / loc, 3) if loc else None},
             bool(loc) and biggest[0] / loc <= 0.30)

        # F-12  cadence
        hours = len(set(_git(repo, "log", "--format=%ad", "--date=format:%Y-%m-%d %H").splitlines()))
        set_("F-12", {"distinct_commit_hours": hours}, hours >= 8)

        # F-4  every author named -- the roster itself is the caller's to supply
        authors = [l.strip() for l in _git(repo, "shortlog", "-sne", "--all").splitlines() if l.strip()]
        out["F-4"].update(state=ABSENT, value={"authors_found": len(authors), "authors": authors[:20]},
                          reason="no entrant roster supplied; F-1 must fix it first")

        # F-2a  claimed timeline -- undefined without a window, which is F-1's job
        if window_end:
            end = date.fromisoformat(window_end)
            start = end - timedelta(days=max(window_days, 1) - 1)
            days = [l[:10] for l in _git(repo, "log", "--format=%ad", "--date=format:%Y-%m-%d").splitlines() if l]
            inside = sum(1 for d in days if start.isoformat() <= d <= end.isoformat())
            set_("F-2a", {"inside": inside, "commits_total": len(days),
                          "share": round(inside / len(days), 3),
                          "window": [start.isoformat(), end.isoformat()],
                          "window_days": window_days},
                 inside / len(days) >= 0.80)
        else:
            out["F-2a"].update(state=ABSENT, reason="no window supplied; F-1 must fix it first")

        # F-9 / F-10  presence checks
        set_("F-9", {"workflows": [f for f in files if f.startswith(".github/workflows")]},
             any(f.startswith(".github/workflows") for f in files))
        # F-10 is integrity, not presence. A real lockfile pins transitively;
        # a requirements.txt only counts when it pins with hashes, which is what
        # `pip install --require-hashes` -- the contract's own command -- demands.
        PINNING = ("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
                   "go.sum", "Cargo.lock", "uv.lock", "Pipfile.lock", "composer.lock")
        locks = [f for f in files if f in PINNING]
        weak = []
        for f in files:
            if f == "requirements.txt":
                body = (pathlib.Path(repo) / f).read_text(encoding="utf-8", errors="ignore")
                (locks if "--hash=" in body else weak).append(f)
        set_("F-10", {"pinning_lockfiles": locks,
                      "unpinned": weak,
                      "note": "requirements.txt without --hash= does not satisfy "
                              "`pip install --require-hashes`" if weak else None},
             bool(locks))

        # V-9 / V-10  README-borne evidence
        readme = next((f for f in files if f.lower().startswith("readme")), None)
        text = (pathlib.Path(repo) / readme).read_text(encoding="utf-8", errors="ignore") if readme else ""
        if readme is None:
            for tid in ("V-9", "U-4"):
                out[tid].update(state=ABSENT, reason="no README in the repository")
            _demo_artifact(out, None, "", demo_artifact)
        else:
            claim = re.search(r"\d+(?:\.\d+)?\s*(?:x\b|%|ms|req/s|faster|cheaper)", text)
            set_("V-9", {"claim": claim.group(0) if claim else None}, bool(claim))
            _demo_artifact(out, set_, text, demo_artifact)
            oneclick = [f for f in files if f in ("Dockerfile", "docker-compose.yml", ".devcontainer/devcontainer.json")]
            set_("U-4", {"entrypoints": oneclick}, bool(oneclick))

        return {"repo": repo_url, "commits": commits, "own_loc": loc,
                "vendored_loc": vendored_loc, "tasks": out}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def summarise(tasks: dict) -> dict:
    """Per scope: what passed, what failed, what was never measured.

    Deliberately emits no /5 and no overall. The caps live in prose in the
    contracts and w_value is unset in the source, so a number here would be
    invented. Callers get the failed blocking ids and decide.
    """
    out = {}
    for scope in CONTRACTS:
        rows = {t: v for t, v in tasks.items() if v["scope"] == scope}
        failed_blocking = sorted(t for t, v in rows.items() if v["blocking"] and v["verdict"] == "FAIL")
        # The score is the LOWEST cap any failure triggered -- a meet, not a sum.
        triggered = [rows[t]["cap"] for t in failed_blocking if rows[t]["cap"]]
        unscorable = [t for t in failed_blocking if rows[t]["cap"] == "unscorable"]
        numeric = sorted(int(c[0]) for c in triggered if c and c[0].isdigit())
        # A blocking task we could not run leaves the cap a CEILING, not a score.
        unmeasured_blocking = sorted(t for t, v in rows.items()
                                     if v["blocking"] and v["state"] != MEASURED)
        out[scope] = {
            "cap": "unscorable" if unscorable else (f"{numeric[0]}/5" if numeric else None),
            "score_is_a_ceiling_because": unmeasured_blocking or None,
            "uncapped_blocking_tasks": sorted(t for t, v in rows.items()
                                              if v["blocking"] and v["cap"] is None),
            "measured": sum(1 for v in rows.values() if v["state"] == MEASURED),
            "absent": sum(1 for v in rows.values() if v["state"] == ABSENT),
            "unevaluable": sum(1 for v in rows.values() if v["state"] == UNEVALUABLE),
            "passed": sorted(t for t, v in rows.items() if v["verdict"] == "PASS"),
            "failed": sorted(t for t, v in rows.items() if v["verdict"] == "FAIL"),
            "failed_blocking": failed_blocking,
            "capped": bool(failed_blocking),
        }
    return out
