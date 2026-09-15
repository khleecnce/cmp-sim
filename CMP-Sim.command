#!/bin/bash
# CMP-Sim launcher — double-click this file in Finder.
#
# Creates the virtual environment on first run, starts the local web server and
# opens the UI in the default browser. Nothing leaves the machine.
set -e
cd "$(dirname "$0")"

PORT=8765
PY=.venv/bin/python

if [ ! -x "$PY" ]; then
  echo "First run: creating the virtual environment (this takes a minute)..."
  python3 -m venv .venv
  .venv/bin/pip install -q --upgrade pip
  .venv/bin/pip install -q numpy scipy pyyaml pint
  echo "done."
fi

# If something is already serving on the port, just open it.
if curl -s -m 2 "http://127.0.0.1:$PORT/api/meta" >/dev/null 2>&1; then
  echo "CMP-Sim is already running."
  open "http://127.0.0.1:$PORT/"
  exit 0
fi

echo "Starting CMP-Sim on http://127.0.0.1:$PORT ..."
"$PY" -m cmp_sim.api --port "$PORT" &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null' EXIT

# Wait for readiness instead of sleeping blindly.
for _ in $(seq 1 40); do
  if curl -s -m 1 "http://127.0.0.1:$PORT/api/meta" >/dev/null 2>&1; then
    break
  fi
  sleep 0.25
done

if ! curl -s -m 2 "http://127.0.0.1:$PORT/api/meta" >/dev/null 2>&1; then
  echo "ERROR: the server did not come up. Run this for the reason:"
  echo "  cd $(pwd) && $PY -m cmp_sim.api"
  exit 1
fi

open "http://127.0.0.1:$PORT/"
echo
echo "CMP-Sim is running. Close this window (or press Ctrl-C) to stop it."
wait $SERVER_PID
