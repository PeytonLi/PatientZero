"""Parse npm lockfiles into Service PINS. Real lockfiles, not invented trees."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patient_zero.assemble import SENTINEL_VALID_TO
from patient_zero.ids import vid


def _package_name_from_lock_key(key: str) -> str | None:
    if not key or key == "":
        return None
    if "node_modules/" not in key.replace("\\", "/"):
        return None
    tail = key.replace("\\", "/").rsplit("node_modules/", 1)[-1]
    if not tail or tail.startswith("."):
        return None
    return tail


def parse_npm_lockfile(
    lock: dict[str, Any],
    *,
    sid: str,
    lockfile_at: int,
) -> list[dict[str, Any]]:
    rows = []
    for key, meta in (lock.get("packages") or {}).items():
        name = _package_name_from_lock_key(key)
        if not name:
            continue
        version = (meta or {}).get("version")
        if not version:
            continue
        rows.append(
            {
                "sid": sid,
                "dst_vid": vid("npm", name, version),
                "lockfile_at": lockfile_at,
                "valid_from": lockfile_at,
                "valid_to": SENTINEL_VALID_TO,
            }
        )
    rows.sort(key=lambda r: r["dst_vid"])
    return rows


def pins_from_lockfile(
    path: Path,
    *,
    sid: str,
    name: str,
    source_repo: str,
    lockfile_at: int,
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    lock = json.loads(path.read_text(encoding="utf-8"))
    service = {"sid": sid, "name": name, "source_repo": source_repo}
    return service, parse_npm_lockfile(lock, sid=sid, lockfile_at=lockfile_at)
