"""Read-only Bolt helper for /api/health.

Never writes. A failed ping is a boolean, not an exception — HydraDB being down
must not take the stub API with it.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from neo4j import GraphDatabase, basic_auth

from .cypher import Q_HEALTH

log = logging.getLogger("patient_zero.db")

DEFAULT_BOLT_URI = "bolt://127.0.0.1:7687"
DEFAULT_TOKEN = "local-development-token-32-bytes"
HEALTH_CYPHER = Q_HEALTH
_CONNECT_TIMEOUT_S = 2.0


def _token() -> str:
    env_file = os.environ.get("HYDRADB_AUTH_TOKEN_FILE")
    candidates = []
    if env_file:
        candidates.append(Path(env_file))
    candidates.append(Path.cwd() / "hydradb-data" / "auth-token")
    # src/patient_zero/db.py -> repo root when running editable / from source
    candidates.append(Path(__file__).resolve().parents[2] / "hydradb-data" / "auth-token")
    for path in candidates:
        try:
            if path.is_file():
                return path.read_text(encoding="utf-8").strip()
        except OSError:
            continue
    return os.environ.get("HYDRADB_AUTH_TOKEN", DEFAULT_TOKEN)


def _uri() -> str:
    return os.environ.get("HYDRADB_BOLT_URI", DEFAULT_BOLT_URI)


def bolt_driver(*, timeout: float = 10.0):
    """Bolt driver. Caller owns close(). Writes go through scripts/load.py only."""
    return GraphDatabase.driver(
        _uri(),
        auth=basic_auth("neo4j", _token()),
        connection_timeout=timeout,
        connection_acquisition_timeout=timeout,
    )


def ping(uri: str | None = None) -> bool:
    """True iff Bolt answers. Never raises, never writes.

    Connectivity is the health signal. Do not run MATCH ... RETURN count(*)
    here — that is a full vertex scan and will get slower as the load grows
    (already 2.6s after the 5k probe). Bare `RETURN 1` is not in the accepted
    Cypher subset; verify_connectivity is enough for /api/health.
    """
    try:
        with GraphDatabase.driver(
            uri or _uri(),
            auth=basic_auth("neo4j", _token()),
            connection_timeout=_CONNECT_TIMEOUT_S,
            connection_acquisition_timeout=_CONNECT_TIMEOUT_S,
        ) as driver:
            driver.verify_connectivity()
            return True
    except Exception as exc:
        log.info("HydraDB ping failed (%s)", type(exc).__name__)
        return False
