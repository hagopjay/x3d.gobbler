"""Scout's eyes: RSS, Atom, the HN Algolia API and GitHub releases. Stdlib only.

Live mode fetches; offline mode reads fixtures/feeds (a dated snapshot); every
item keeps the source id and URL so any number downstream can name its source.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import urllib.request
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

UA = "gobbler-flyte/0.1 (+https://github.com/hagopjay/x3d.gobbler)"
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "feeds"
FIXTURE_FOR = {"web3d-news": "web3d_rss.xml", "hn-x3d": "hn_x3d_title.json", "hn-webgpu": "hn_webgpu.json",
               "arxiv-x3d": "arxiv.xml", "loom-commits": "loom_commits.atom"}
SYNTHETIC = FIXTURES / "synthetic_releases.json"   # labelled synthetic: this container's proxy blocks those repos
ATOM = "{http://www.w3.org/2005/Atom}"
MAX_FEED_BYTES = 2 * 1024 * 1024


def fetch_url(source: dict) -> str:
    return (f"https://api.github.com/repos/{source['repo']}/releases?per_page=5"
            if source.get("kind") == "github-releases" else source.get("url", ""))


def _https(url: str) -> bool:
    parsed = urlsplit(url)
    return parsed.scheme == "https" and bool(parsed.hostname) and parsed.username is None and parsed.password is None


class _HTTPSRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _https(newurl) or urlsplit(newurl).netloc != urlsplit(req.full_url).netloc:
            raise ValueError("feed redirect leaves configured HTTPS origin")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _id(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:16]


def _get(url: str, timeout: int = 20, headers: dict | None = None) -> bytes:
    if not _https(url):
        raise ValueError("feed URL must be HTTPS without embedded credentials")
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.build_opener(_HTTPSRedirects()).open(req, timeout=timeout) as r:
        body = r.read(MAX_FEED_BYTES + 1)
        if len(body) > MAX_FEED_BYTES:
            raise ValueError('feed exceeds the 2 MiB input budget')
        return body


_PRIVATE_LINK = re.compile(r"https?://claude\.ai/(?:code|project|artifact)/\S*")


def _clean(url: str) -> str:
    """Links into claude.ai sessions/artifacts never enter a ledger or a commit, even someone else's public one."""
    return _PRIVATE_LINK.sub("https://claude.ai/[link-withheld]", url or "")


def parse(kind: str, source: dict, body: bytes) -> list[dict]:
    if len(body) > MAX_FEED_BYTES:
        raise ValueError('feed exceeds the 2 MiB input budget')
    if kind not in ('hn', 'rss', 'atom', 'github-releases'):
        raise ValueError('unsupported feed kind')
    return [{**i, "title": _clean(i["title"]), "url": _clean(i["url"]), "summary": _clean(i.get("summary", ""))}
            for i in _parse(kind, source, body)]


def _observed(items: list[dict], *, mode: str, transport: str, body: bytes, fixture: str | None = None,
              synthetic: bool = False) -> list[dict]:
    provenance = {'mode': mode, 'transport': transport, 'body_sha256': hashlib.sha256(body).hexdigest()}
    if fixture:
        provenance['fixture'] = fixture
    return [{**item, 'provenance': dict(provenance), **({'synthetic': True} if synthetic else {})} for item in items]


def _parse(kind: str, source: dict, body: bytes) -> list[dict]:
    sid = source["id"]
    out = []
    if kind == "hn":
        for h in json.loads(body).get("hits", []):
            title = h.get("title") or ""
            url = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"
            out.append({"id": _id(sid, str(h.get("objectID"))), "source": sid, "title": title, "url": url,
                        "published": h.get("created_at", ""), "summary": (h.get("story_text") or "")[:1500]})
    elif kind == "rss":
        root = ET.fromstring(body)
        for it in root.iter("item"):
            title, link = it.findtext("title", ""), it.findtext("link", "")
            out.append({"id": _id(sid, link or title), "source": sid, "title": title.strip(), "url": link.strip(),
                        "published": it.findtext("pubDate", ""), "summary": re.sub(r"<[^>]+>", " ", it.findtext("description", ""))[:1500]})
    elif kind == "atom":
        root = ET.fromstring(body)
        for e in root.iter(ATOM + "entry"):
            link = e.find(ATOM + "link")
            href = link.get("href", "") if link is not None else ""
            summary = e.findtext(ATOM + "summary") or e.findtext(ATOM + "content") or ""
            out.append({"id": _id(sid, href or e.findtext(ATOM + "id", "")), "source": sid,
                        "title": " ".join((e.findtext(ATOM + "title") or "").split()), "url": href,
                        "published": e.findtext(ATOM + "published") or e.findtext(ATOM + "updated") or "",
                        "summary": " ".join(re.sub(r"<[^>]+>", " ", summary).split())[:1500]})
    elif kind == "github-releases":
        for r in json.loads(body)[:5]:
            out.append({"id": _id(sid, str(r.get("id") or r.get("tag_name"))), "source": sid,
                        "title": f"{source['repo']} {r.get('tag_name')}: {r.get('name') or ''}".strip(), "url": r.get("html_url", ""),
                        "published": r.get("published_at", ""), "summary": (r.get("body") or "")[:1500],
                        **({"synthetic": True} if r.get("synthetic") else {})})
    return out


def _fetch(source: dict, mode: str) -> dict:
    """Return {'source', 'status', 'items', 'note'}; never raises (a dead feed is a tape row, not a crash)."""
    if mode not in ('offline', 'sim', 'live'):
        raise ValueError('mode must be live, offline or sim; unknown modes never fetch')
    kind = source["kind"]
    try:
        if mode in ("offline", "sim"):
            if kind == "github-releases":
                if not SYNTHETIC.exists():
                    return {"source": source["id"], "status": "skipped", "items": [], "note": "no fixture"}
                rel = json.loads(SYNTHETIC.read_text()).get(source["repo"], [])
                body = json.dumps(rel).encode()
                items = _observed(parse(kind, source, body), mode=mode, transport='fixture', body=body,
                                  fixture=SYNTHETIC.name, synthetic=True)
                return {"source": source["id"], "status": "fixture-synthetic", "items": items,
                        "note": "synthetic release fixture (labelled)"}
            name = FIXTURE_FOR.get(source["id"])
            if not name:
                return {"source": source["id"], "status": "skipped", "items": [], "note": "no fixture for this source"}
            body = (FIXTURES / name).read_bytes()
            return {"source": source["id"], "status": "fixture", "items": _observed(parse(kind, source, body),
                    mode=mode, transport='fixture', body=body, fixture=name),
                    "note": f"snapshot fixtures/feeds/{name}"}
        if kind == "github-releases":
            headers = {"Accept": "application/vnd.github+json"}
            if os.environ.get("GITHUB_TOKEN"):
                headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
            body = _get(f"https://api.github.com/repos/{source['repo']}/releases?per_page=5", headers=headers)
        else:
            body = _get(source["url"])
        return {"source": source["id"], "status": "live", "items": _observed(parse(kind, source, body),
                mode=mode, transport='live', body=body), "note": source.get("url") or source.get("repo")}
    except Exception as e:  # noqa: BLE001 - every failure is reported on the tape
        return {"source": source["id"], "status": "error", "items": [], "note": f"{type(e).__name__}: {str(e)[:160]}"}


def fetch(source: dict, mode: str) -> dict:
    """Fetch attempt receipt, including failures and fixtures; fixtures are never live observations."""
    if mode not in ("offline", "sim", "live"):
        raise ValueError("mode must be live, offline or sim")
    url = fetch_url(source)
    receipt = {"fetch_url": url, "transport": "fixture" if mode in ("offline", "sim") else "live",
               "request_policy": "configured-https-origin; cross-origin redirects refused"}
    if not _https(url):
        return {"source": source["id"], "status": "error", "items": [],
                "note": "fetch refused before request: invalid configured HTTPS URL", **receipt}
    result = _fetch(source, mode)
    return {**result, **receipt}
