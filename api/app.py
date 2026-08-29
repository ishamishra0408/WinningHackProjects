#!/usr/bin/env python3
"""Two endpoints over the contracts.

    POST /evaluateproject   a repo that exists  -> what holds up, what does not
    POST /evaluatespec      a plan that does not -> the ordered work to make it clear the bar
    GET  /health            task counts, so a caller can tell the contracts loaded

Run:  python3 api/app.py [--port 8000]

Standard library only, deliberately: no lockfile to drift, and it builds from a
clean clone anywhere -- the properties F-7 and F-10 ask of everyone else. It is
single-threaded and meant for one operator on localhost, not for production.
"""

from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))

import runners
import spec as spec_mod

MAX_BODY = 1 << 20


class Handler(BaseHTTPRequestHandler):
    server_version = "winninghack/1.0"

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, indent=1).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict | None:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            self._send(400, {"error": "body must be JSON, 1 byte to 1 MiB"})
            return None
        try:
            return json.loads(self.rfile.read(length))
        except json.JSONDecodeError as exc:
            self._send(400, {"error": "invalid JSON", "detail": str(exc)})
            return None

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))

    def do_GET(self):
        if self.path.rstrip("/") == "/health":
            tasks = runners.load_tasks()
            self._send(200, {"ok": True, "tasks": len(tasks),
                             "blocking": sum(1 for t in tasks.values() if t["blocking"]),
                             "design_checks": len(spec_mod.ROWS),
                             "source": "scopes/*.md, read at call time"})
        else:
            self._send(404, {"error": "not found",
                             "endpoints": ["POST /evaluateproject", "POST /evaluatespec", "GET /health"]})

    def do_POST(self):
        route = self.path.rstrip("/")
        if route == "/evaluateproject":
            self._evaluate_project()
        elif route == "/evaluatespec":
            self._evaluate_spec()
        else:
            self._send(404, {"error": "not found",
                             "endpoints": ["POST /evaluateproject", "POST /evaluatespec", "GET /health"]})

    # ---- POST /evaluateproject -------------------------------------------
    def _evaluate_project(self):
        body = self._read_json()
        if body is None:
            return
        repo = body.get("repo_url")
        if not isinstance(repo, str) or not repo.startswith(("https://", "http://")):
            self._send(400, {"error": "repo_url required, http(s) only"})
            return
        result = runners.audit_repo(
            repo,
            window_end=body.get("window_end"),
            window_days=int(body.get("window_days") or 1),
            starter_sha=body.get("starter_sha"),
            demo_artifact=body.get("demo_artifact"),
            criteria_source=body.get("criteria_source"),
            criteria=body.get("criteria"),
            prior_art=body.get("prior_art"),
            eval_command=body.get("eval_command"),
            walkthrough_runs=body.get("walkthrough_runs"),
            team_size=body.get("team_size"),
            event_hours=body.get("event_hours"),
        )
        if "error" in result and "tasks" not in result:
            self._send(502, result)
            return
        scopes = runners.summarise(result["tasks"])
        self._send(200, {
            "repo": repo,
            "commits": result.get("commits"),
            "own_loc": result.get("own_loc"),
            "vendored_loc": result.get("vendored_loc"),
            "scopes": scopes,
            "tasks": result["tasks"],
            "overall": None,
            "weights": runners.load_weights(),
            "criteria_source": result.get("criteria_source"),
            "criteria_source_from": result.get("criteria_source_from"),
            "overall_refused_because": [
                "UNEVALUABLE is not a pass -- a blocking task that did not run leaves each scope's "
                "cap a CEILING, not a score, and every scope here has at least one",
            ],
            "not_a_prediction": "28 winning repos fail these contracts. This says whether a project holds up, not whether it wins.",
        })

    # ---- POST /evaluatespec ----------------------------------------------
    def _evaluate_spec(self):
        body = self._read_json()
        if body is None:
            return
        if not isinstance(body.get("plan"), dict) and not isinstance(body.get("event"), dict):
            self._send(400, {"error": "send {\"event\": {...}, \"plan\": {...}}",
                             "fields": sorted({r[3] for r in spec_mod.ROWS} |
                                              {"criteria_found", "criteria_covered",
                                               "team_size", "event_hours", "planned_person_hours"})})
            return
        results = spec_mod.evaluate(body)
        self._send(200, {
            "scopes": spec_mod.strengths_and_weaknesses(results),
            "workflow": spec_mod.workflow(results),
            "checks": results,
            "deterministic": f"{sum(1 for r in results if r['strength'] == 'STRONG')} of {len(results)} checks are mechanical; "
                             f"{sum(1 for r in results if r['strength'] == 'WEAK')} are declarations and are reported, never scored",
            "not_pooled_with": "/evaluateproject -- different units, no combined score",
        })


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    tasks = runners.load_tasks()
    print(f"contracts loaded: {len(tasks)} tasks, "
          f"{sum(1 for t in tasks.values() if t['blocking'])} blocking, "
          f"{len(spec_mod.ROWS)} design checks", file=sys.stderr)
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"listening on http://{args.host}:{args.port}", file=sys.stderr)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
