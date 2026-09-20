"""The link-protection gate on a hosted instance.

A token check is the kind of code that looks right and silently is not, so
these exercise the real server over a real socket rather than calling the
handler's methods directly.
"""
from __future__ import annotations

import json
import os
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from cmp_sim import api as api_mod


def _serve():
    """Start the real server on an ephemeral port; return (base_url, stop)."""
    srv = ThreadingHTTPServer(("127.0.0.1", 0), api_mod.Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    port = srv.server_address[1]

    def stop():
        srv.shutdown()
        srv.server_close()

    return f"http://127.0.0.1:{port}", stop


def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


@pytest.fixture()
def quiet_logs(monkeypatch):
    monkeypatch.setenv("CMPSIM_QUIET", "1")


def test_no_token_configured_means_open(quiet_logs, monkeypatch):
    """A laptop run must not demand a key. Anything else punishes the
    common case to protect the rare one."""
    monkeypatch.delenv("CMPSIM_TOKEN", raising=False)
    base, stop = _serve()
    try:
        code, _ = _get(f"{base}/api/meta")
        assert code == 200
    finally:
        stop()


def test_token_configured_blocks_anonymous_access(quiet_logs, monkeypatch):
    monkeypatch.setenv("CMPSIM_TOKEN", "s3cret-demo-key")
    base, stop = _serve()
    try:
        code, body = _get(f"{base}/api/meta")
        assert code == 401
        # The refusal must say how to comply; a bare 401 sends a reviewer
        # to the source to find out what the server wanted.
        detail = json.loads(body)["detail"]
        assert "?t=" in detail
    finally:
        stop()


def test_correct_token_in_query_is_accepted(quiet_logs, monkeypatch):
    monkeypatch.setenv("CMPSIM_TOKEN", "s3cret-demo-key")
    base, stop = _serve()
    try:
        code, _ = _get(f"{base}/api/meta?t=s3cret-demo-key")
        assert code == 200
    finally:
        stop()


def test_correct_token_in_header_is_accepted(quiet_logs, monkeypatch):
    """Scripted callers should not have to put the secret in a URL, which
    is the part that ends up in proxy and server logs."""
    monkeypatch.setenv("CMPSIM_TOKEN", "s3cret-demo-key")
    base, stop = _serve()
    try:
        code, _ = _get(f"{base}/api/meta",
                       headers={"X-CMPSim-Token": "s3cret-demo-key"})
        assert code == 200
    finally:
        stop()


def test_wrong_token_is_rejected(quiet_logs, monkeypatch):
    monkeypatch.setenv("CMPSIM_TOKEN", "s3cret-demo-key")
    base, stop = _serve()
    try:
        for bad in ("", "wrong", "s3cret-demo-ke", "s3cret-demo-keyy",
                    "S3CRET-DEMO-KEY"):
            code, _ = _get(f"{base}/api/meta?t={bad}")
            assert code == 401, f"{bad!r} should not open the door"
    finally:
        stop()


def test_the_page_itself_is_protected_not_just_the_api(quiet_logs, monkeypatch):
    """Serving the UI to anyone and only gating the data would leak the
    model's structure — the pack names, the axes, the whole recipe form."""
    monkeypatch.setenv("CMPSIM_TOKEN", "s3cret-demo-key")
    base, stop = _serve()
    try:
        assert _get(f"{base}/")[0] == 401
        assert _get(f"{base}/?t=s3cret-demo-key")[0] == 200
    finally:
        stop()


def test_post_routes_are_gated(quiet_logs, monkeypatch):
    """The GET gate alone would leave simulate/sweep wide open — the
    expensive routes, and the ones that reveal predictions."""
    monkeypatch.setenv("CMPSIM_TOKEN", "s3cret-demo-key")
    base, stop = _serve()
    try:
        body = json.dumps({"film": "oxide"}).encode()
        req = urllib.request.Request(f"{base}/api/simulate", data=body,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        assert code == 401
    finally:
        stop()


def test_token_is_compared_without_early_exit(monkeypatch):
    """Guard the comparison itself. `==` on a secret leaks its length and
    prefix through timing; this asserts the constant-time path is used."""
    import inspect
    src = inspect.getsource(api_mod.Handler._authorised)
    assert "compare_digest" in src
    assert "given == want" not in src and "want == given" not in src
