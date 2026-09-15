"""FabSim Studio 실행 진입점 — `fabsim-studio` 명령과 Mac 앱이 여기로 들어온다.

streamlit은 스크립트 경로를 받아 자기 런타임을 띄우는 구조라, 설치된 패키지에서
경로를 찾아 넘겨주는 얇은 층이 필요하다.
"""
from __future__ import annotations

import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

APP = Path(__file__).resolve().parent / "studio.py"
DEFAULT_PORT = 8790


def _free_port(start: int = DEFAULT_PORT, tries: int = 20) -> int:
    for p in range(start, start + tries):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    return start


def _alive(port: int) -> bool:
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def _open_when_ready(url: str, port: int, timeout: float = 25.0):
    end = time.time() + timeout
    while time.time() < end:
        if _alive(port):
            webbrowser.open(url)
            return
        time.sleep(0.3)


def main() -> int:
    port = int(os.environ.get("FABSIM_PORT") or 0) or DEFAULT_PORT
    # 이미 떠 있으면 새로 띄우지 않고 그 창을 연다
    if _alive(port):
        webbrowser.open(f"http://127.0.0.1:{port}")
        print(f"이미 실행 중 → http://127.0.0.1:{port}")
        return 0
    port = _free_port(port)
    url = f"http://127.0.0.1:{port}"

    if not os.environ.get("FABSIM_NO_BROWSER"):
        threading.Thread(target=_open_when_ready, args=(url, port), daemon=True).start()

    try:
        from streamlit.web import cli as stcli
    except ImportError:
        print("Streamlit이 없습니다. 설치: pip install 'fabsim[ui]'", file=sys.stderr)
        return 2

    print(f"FabSim Studio → {url}")
    sys.argv = ["streamlit", "run", str(APP),
                "--server.port", str(port),
                "--server.address", os.environ.get("FABSIM_HOST", "127.0.0.1"),
                "--server.headless", "true",
                "--browser.gatherUsageStats", "false"]
    return int(stcli.main() or 0)


if __name__ == "__main__":
    sys.exit(main())
