#!/usr/bin/env python3
"""Wait for HydraDB, load the snapshot if needed, serve the UI.

Starts the HTTP server immediately so Render health checks can pass, then
loads the graph in this process. Queries retry Bolt until HydraDB is up.

    python scripts/demo.py
"""

from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from patient_zero.db import ping  # noqa: E402
from patient_zero.server import main as serve  # noqa: E402


def wait_for_bolt(*, timeout_s: float = 300.0) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if ping():
            print("hydradb: reachable", flush=True)
            return
        print("hydradb: waiting for Bolt…", flush=True)
        time.sleep(2)
    raise SystemExit("HydraDB did not become reachable on Bolt")


def main() -> None:
    os.chdir(ROOT)
    server = threading.Thread(target=serve, name="patient-zero-http", daemon=False)
    server.start()
    wait_for_bolt()
    if os.environ.get("PATIENT_ZERO_SKIP_LOAD") != "1":
        from load import main as load_main

        rc = load_main([])
        if rc != 0:
            print(f"load failed rc={rc}; serving degraded", flush=True)
    server.join()


if __name__ == "__main__":
    main()
