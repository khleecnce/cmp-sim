"""The static-asset route that the 3D tool view depends on.

Why over a real socket rather than calling the handler
------------------------------------------------------
Path containment and MIME selection are exactly the kind of code that looks
right and silently is not. A traversal check written against ``".." in path``
passes review and still lets ``%2e%2e%2f`` through; a Content-Type guessed with
``mimetypes`` returns ``text/plain`` for ``.js`` on some systems, and a browser
then refuses to execute the module — the 3D view degrades to a blank canvas with
no error anywhere in Python. Both failures are invisible unless a real client
asks a real server, so these tests do that.
"""
from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from cmp_sim import api as api_mod


def _serve():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), api_mod.Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()

    def stop():
        srv.shutdown()
        srv.server_close()

    return f"http://127.0.0.1:{srv.server_address[1]}", stop


def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), e.read()


@pytest.fixture()
def server(monkeypatch):
    monkeypatch.setattr(api_mod.Handler, "log_message",
                        lambda *a, **k: None, raising=False)
    base, stop = _serve()
    yield base
    stop()


# ---------------------------------------------------------------------------
# the routes exist and serve the right thing
# ---------------------------------------------------------------------------

def test_tool_view_is_served(server):
    """/tool must return the 3D view, not a 404 and not the form view."""
    for path in ("/tool", "/tool.html"):
        status, ctype, body = _get(server + path)
        assert status == 200, (path, status)
        assert "text/html" in ctype, (path, ctype)
        text = body.decode("utf-8")
        assert "tool3d.js" in text, "the tool view must load the scene module"
        assert 'id="scene"' in text


def test_form_view_still_served(server):
    """Adding /tool must not have displaced the original form view."""
    status, ctype, body = _get(server + "/")
    assert status == 200
    assert "text/html" in ctype
    assert b"CMP-Sim" in body


def test_vendored_modules_are_served_as_javascript(server):
    """A wrong MIME here makes the browser refuse the module, silently.

    three.js is vendored rather than pulled from a CDN so the tool works on a
    fab machine with no outbound network — which only helps if the files are
    actually served, and served as JavaScript.
    """
    for asset in ("three.module.min.js", "OrbitControls.js", "tool3d.js"):
        status, ctype, body = _get(f"{server}/vendor/{asset}")
        assert status == 200, (asset, status)
        assert "javascript" in ctype, (asset, ctype)
        assert len(body) > 500, (asset, len(body))


def test_orbitcontrols_imports_the_vendored_three(server):
    """The vendored copy must not import a bare 'three' specifier.

    OrbitControls ships with ``from 'three'``, which a browser cannot resolve
    without an import map. If this regresses, the scene throws on load and the
    view falls back to the no-WebGL notice — looking like a driver problem
    rather than a packaging one.
    """
    _, _, body = _get(server + "/vendor/OrbitControls.js")
    text = body.decode("utf-8")
    assert "from 'three'" not in text, "bare specifier would not resolve"
    assert "./three.module.min.js" in text


# ---------------------------------------------------------------------------
# and refuse everything else
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", [
    "/vendor/../api.py",
    "/vendor/%2e%2e/api.py",
    "/vendor/../../etc/passwd",
    "/vendor/../cmp_sim/api.py",
])
def test_traversal_out_of_vendor_is_refused(server, path):
    """Containment is checked on the RESOLVED path, not on the raw string.

    URL-escaped traversal is the case a substring check misses, so it is
    listed explicitly.
    """
    status, _, body = _get(server + path)
    assert status == 404, (path, status, body[:200])
    assert b"api.py" not in body or b"no such asset" in body


def test_unknown_extension_is_refused_rather_than_guessed(server, tmp_path):
    """An unlisted type must 415, not be served as octet-stream.

    Guessing is how a mis-typed asset becomes a module the browser quietly
    declines to run. The refusal names the fix.
    """
    from cmp_sim.api import WEB_DIR

    probe = WEB_DIR / "vendor" / "_probe_unknown.xyz"
    probe.write_text("not a real asset")
    try:
        status, ctype, body = _get(server + "/vendor/_probe_unknown.xyz")
        assert status == 415, (status, body[:200])
        payload = json.loads(body)
        assert "_CONTENT_TYPES" in payload.get("detail", ""), payload
    finally:
        probe.unlink()


def test_missing_asset_is_a_clean_404(server):
    status, ctype, body = _get(server + "/vendor/does_not_exist.js")
    assert status == 404
    assert "json" in ctype
    assert "no such asset" in json.loads(body)["error"]


def test_404_lists_the_new_routes(server):
    """The 404 payload is the discovery surface; it must not go stale."""
    status, _, body = _get(server + "/nope")
    assert status == 404
    paths = json.loads(body)["valid_get_paths"]
    assert "/tool" in paths
    assert any("vendor" in p for p in paths)
