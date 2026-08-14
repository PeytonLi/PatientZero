"""Stable HydraDB node ids. Identity is computed offline; HydraDB stores only `id`.

HydraDB 0.1.0 UNWIND requires `id` / `eid` to be non-negative integers. String
keys (vid/pid/…) are hashed to 63-bit ints for Bolt; the API hashes the same way
to look up `sourceValues`.
"""

from __future__ import annotations

import hashlib
import re

_GITHUB = re.compile(
    r"(?:github\.com[:/]|github:)(?P<org>[^/]+)/(?P<name>[^/#?]+)",
    re.IGNORECASE,
)


def pid(ecosystem: str, name: str) -> str:
    return f"{ecosystem}:{name}"


def vid(ecosystem: str, name: str, version: str) -> str:
    return f"{ecosystem}:{name}@{version}"


def mid(ecosystem: str, login: str) -> str:
    return f"{ecosystem}:{login}"


def rid(url: str | None) -> str | None:
    if not url:
        return None
    match = _GITHUB.search(url.strip())
    if not match:
        return None
    name = match.group("name").removesuffix(".git")
    return f"github:{match.group('org')}/{name}"


def wid(repo_id: str, path: str) -> str:
    return f"{repo_id}:{path}"


def hydra_id(stable: str) -> int:
    digest = hashlib.blake2b(stable.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big") & 0x7FFFFFFFFFFFFFFF
