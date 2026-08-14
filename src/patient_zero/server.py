"""Launch the Patient Zero stub API.

Binds 127.0.0.1:8080 by default.

Port 8000 is occupied on this machine by another docker compose project
(clashroyaledecks). HANDOFF.md still names localhost:8000 as the W2→W4
contract; we serve 8080 so the stub is actually reachable. Override with
PATIENT_ZERO_HOST / PATIENT_ZERO_PORT.
"""

from __future__ import annotations

import os

import uvicorn

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080  # not 8000: clashroyaledecks already owns that port


def main() -> None:
    host = os.environ.get("PATIENT_ZERO_HOST", DEFAULT_HOST)
    port = int(os.environ.get("PATIENT_ZERO_PORT", str(DEFAULT_PORT)))
    uvicorn.run("patient_zero.api:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
