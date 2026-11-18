"""Where the Gobbler asks its humans, and how it hears them.

Only logins in config `authorized_humans` count. An answer is the first line of
a reply: A / B / C (or 1 / 2 / 3), or "ok" for the preferred pick. An option
marked irreversible needs the word "send" next to it ("A send"); nothing
irreversible is ever taken on a timeout. "OK $0.03/day" from an authorized
login sets the model allowance.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import urllib.request

from .budget import parse_allowance

_ANSWER = re.compile(r"^\s*(?P<pick>[abc123]|ok)\b(?P<rest>.*)$", re.I)


def parse_answer(text: str, question: dict) -> str | None:
    first = (text or "").strip().splitlines()[0] if (text or "").strip() else ""
    m = _ANSWER.match(first)
    if not m or parse_allowance(first):
        return None
    pick = m.group("pick").upper()
    pick = {"1": "A", "2": "B", "3": "C", "OK": question["preferred"]}.get(pick, pick)
    if pick == "A" and not question.get("reversible", True) and "send" not in m.group("rest").lower():
        return None                      # an outside send needs the typed word
    return pick


def render_question(q: dict) -> str:
    opts = "\n".join(f"- **{o['id']}**: {o['label']} ({o['effect']})" for o in q["options"])
    when = (f"If nobody authorized answers by **{q['deadline_utc']}**, the Gobbler takes **{q['preferred']}**."
            if q["reversible"] else "This one is irreversible: it waits for a typed answer and is never taken on a timeout.")
    return (f"{q['question']}\n\nWhy ask: {q['why']}\n\n{opts}\n\nPreferred pick: **{q['preferred']}**. {when}\n\n"
            f"Reply with A, B or C (or `ok` for the preferred pick){' and the word send for A' if not q['reversible'] else ''}. "
            f"Only {', '.join(q['authorized'])} can answer.\n")


class FileChannel:
    """Local mode (his PC, a Flyte sandbox): questions and answers are JSON files in the state folder."""

    def __init__(self, root: Path, authorized: list[str]):
        self.q, self.a = root / "questions", root / "answers"
        self.q.mkdir(parents=True, exist_ok=True)
        self.a.mkdir(parents=True, exist_ok=True)
        self.authorized = {x.lower() for x in authorized}

    def post(self, q: dict) -> str:
        p = self.q / f"{q['cycle']:05d}.md"
        p.write_text(render_question(q))
        return str(p.name)

    def poll(self, ref: str, q: dict, now: str) -> dict | None:
        p = self.a / f"{q['cycle']:05d}.json"
        if not p.exists():
            return None
        a = json.loads(p.read_text())
        if a.get("by", "").lower() not in self.authorized:
            return None
        pick = parse_answer(a.get("text", ""), q)
        return {"choice": pick, "by": a["by"], "via": "file", "utc": a.get("utc", now), "ref": ref} if pick else None

    def allowance(self) -> dict | None:
        p = self.a / "allowance.json"
        if not p.exists():
            return None
        a = json.loads(p.read_text())
        parsed = parse_allowance(a.get("text", ""))
        if parsed and a.get("by", "").lower() in self.authorized:
            return {**parsed, "approved_by": a["by"], "approved_ref": str(p), "approved_utc": a.get("utc")}
        return None

    def close(self, ref: str, d: dict) -> None:
        pass


class GitHubIssues:
    """24/7 mode on GitHub Actions: one issue per question, labelled, closed when resolved."""

    def __init__(self, repo: str, label: str, authorized: list[str], token: str | None = None):
        self.repo, self.label = repo, label
        self.authorized = {x.lower() for x in authorized}
        self.token = token or os.environ.get("GITHUB_TOKEN")

    def _api(self, method: str, path: str, body: dict | None = None):
        req = urllib.request.Request(f"https://api.github.com/repos/{self.repo}{path}", method=method,
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {self.token}",
                                              "User-Agent": "gobbler-flyte/0.1", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read() or b"null")

    def post(self, q: dict) -> str:
        issue = self._api("POST", "/issues", {"title": f"[Gobbler.flyte] {q['question'][:110]}", "body": render_question(q),
                                               "labels": [self.label]})
        return str(issue["number"])

    def poll(self, ref: str, q: dict, now: str) -> dict | None:
        for c in self._api("GET", f"/issues/{ref}/comments?per_page=100"):
            if c["user"]["login"].lower() not in self.authorized:
                continue                 # anyone may comment; only the authorized are heard
            pick = parse_answer(c["body"], q)
            if pick:
                return {"choice": pick, "by": c["user"]["login"], "via": f"issue #{ref}", "utc": c["created_at"], "ref": c["html_url"]}
        return None

    def allowance(self) -> dict | None:
        found = None
        for issue in self._api("GET", f"/issues?labels={self.label}&state=all&per_page=30"):
            for c in self._api("GET", f"/issues/{issue['number']}/comments?per_page=100"):
                parsed = parse_allowance(c["body"])
                if parsed and c["user"]["login"].lower() in self.authorized:
                    if not found or c["created_at"] > found["approved_utc"]:
                        found = {**parsed, "approved_by": c["user"]["login"], "approved_ref": c["html_url"], "approved_utc": c["created_at"]}
        return found

    def close(self, ref: str, d: dict) -> None:
        self._api("POST", f"/issues/{ref}/comments", {"body": f"Resolved: **{d['choice']}** by {d['by']} ({d['status']})."})
        self._api("PATCH", f"/issues/{ref}", {"state": "closed"})


class SimHumans:
    """The simulated day's HagopJay: answers by question order (1st, 2nd, ...): reply after N minutes, or silence."""

    def __init__(self, script: dict[int, dict], allowance_reply: dict | None = None):
        self.script, self.allowance_reply = script, allowance_reply
        self.order: dict[int, int] = {}

    def post(self, q: dict) -> str:
        self.order[q["cycle"]] = len(self.order) + 1
        return f"sim-{q['cycle']}"

    def poll(self, ref: str, q: dict, now: str) -> dict | None:
        s = self.script.get("irreversible") if not q["reversible"] else self.script.get(self.order.get(q["cycle"], 0))
        if not s:
            return None
        from datetime import datetime, timedelta
        asked = datetime.strptime(q["asked_utc"], "%Y-%m-%dT%H:%M:%SZ")
        at = asked + timedelta(minutes=s["after_minutes"])
        if datetime.strptime(now, "%Y-%m-%dT%H:%M:%SZ") < at:
            return None
        pick = parse_answer(s["text"], q)
        return {"choice": pick, "by": s.get("by", "hagopjay"), "via": "simulated reply", "utc": at.strftime("%Y-%m-%dT%H:%M:%SZ"), "ref": ref} if pick else None

    def allowance(self) -> dict | None:
        a, self.allowance_reply = self.allowance_reply, None      # typed once
        return a

    def close(self, ref: str, d: dict) -> None:
        pass
