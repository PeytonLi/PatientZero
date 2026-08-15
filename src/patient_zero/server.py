"""Launch the Patient Zero API.

Binds 127.0.0.1:8080 by default. PATIENT_ZERO_HOST / PATIENT_ZERO_PORT override.
If PORT is set (Render), bind 0.0.0.0:$PORT.
"""

from __future__ import annotations

import os

import uvicorn

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080


def main() -> None:
    port = int(os.environ.get("PORT") or os.environ.get("PATIENT_ZERO_PORT") or DEFAULT_PORT)
    host = os.environ.get("PATIENT_ZERO_HOST")
    if not host:
        host = "0.0.0.0" if os.environ.get("PORT") else DEFAULT_HOST
    uvicorn.run("patient_zero.api:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
