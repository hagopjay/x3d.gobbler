"""No network: policy and receipt checks for every Scout fetch path."""
import json
import urllib.request

import pytest

from gobbler_flyte.runner import load_config
from gobbler_flyte.sources import _HTTPSRedirects, _get, fetch, fetch_url, parse


def test_every_fixture_fetch_has_destination_and_transport_receipt():
    for source in load_config()["sources"]:
        result = fetch(source, "offline")
        assert result["fetch_url"] == fetch_url(source)
        assert result["transport"] == "fixture"


def test_private_link_redaction_covers_titles():
    body = json.dumps({"hits": [{"objectID": "test", "title": ("X3D https://" + "claude.ai" + "/code/private-example"), "url": "https://example.org"}]}).encode()
    result = parse("hn", {"id": "hn-x3d"}, body)[0]
    assert "private-example" not in result["title"]


def test_insecure_config_is_rejected_before_any_request():
    source = {"id": "bad", "kind": "rss", "url": "http://example.org/feed"}
    result = fetch(source, "live")
    assert result["status"] == "error" and "before request" in result["note"]
    with pytest.raises(ValueError, match="HTTPS"):
        _get(source["url"])


@pytest.mark.parametrize("url", ["http://example.org/feed", "https://elsewhere.example/feed", "https://user:pass@example.org/feed"])
def test_redirects_cannot_leave_configured_https_origin(url):
    request = urllib.request.Request("https://example.org/feed")
    with pytest.raises(ValueError, match="origin"):
        _HTTPSRedirects().redirect_request(request, None, 302, "Found", {}, url)
