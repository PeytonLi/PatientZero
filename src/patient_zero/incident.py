"""An incident is the unit of investigation. May 11 is fixture #1, not a constant."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SENTINEL_VALID_TO = 4102444800  # 2100-01-01 UTC

# Baked May 11 so tests and Docker still boot if the JSON is missing.
_MAY11: dict[str, Any] = {
    "id": "may11-tanstack",
    "title": "TanStack / Mini Shai-Hulud",
    "window_start": 1778527200,
    "window_end": 1778557800,
    "named_at": 1778527560,
    "world_found_out_at": 1778528760,
    "true_origin": {"id": "npm:tannerlinsley", "kind": "maintainer"},
    "default_blast": {
        "ecosystem": "npm",
        "name": "@tanstack/react-query",
        "version": "5.101.4",
    },
    "default_sid": "svc:mattermost",
    "ticks": [
        {"at": 1778527200, "label": "worm begins"},
        {"at": 1778527560, "label": "42 @tanstack/* packages compromised (seed set)"},
        {"at": 1778528760, "label": "first public detection (StepSecurity)"},
        {"at": 1778543400, "label": "npm -> PyPI crossing"},
        {"at": 1778557800, "label": "end of day: 170+ packages"},
    ],
}

WORM_START = int(_MAY11["window_start"])
TRUE_ORIGIN_MID = str(_MAY11["true_origin"]["id"])


@dataclass(frozen=True)
class IncidentTick:
    at: int
    label: str


@dataclass(frozen=True)
class Incident:
    id: str
    title: str
    window_start: int
    window_end: int
    named_at: int
    world_found_out_at: int
    true_origin_id: str
    true_origin_kind: str
    default_blast: dict[str, str]
    default_sid: str
    ticks: tuple[IncidentTick, ...]

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["true_origin"] = {
            "id": self.true_origin_id,
            "kind": self.true_origin_kind,
        }
        payload["ticks"] = [{"at": t.at, "label": t.label} for t in self.ticks]
        del payload["true_origin_id"]
        del payload["true_origin_kind"]
        return payload

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Incident:
        origin = raw.get("true_origin") or {}
        ticks = tuple(
            IncidentTick(at=int(row["at"]), label=str(row["label"]))
            for row in (raw.get("ticks") or [])
        )
        blast = dict(raw.get("default_blast") or _MAY11["default_blast"])
        return cls(
            id=str(raw.get("id") or "unknown"),
            title=str(raw.get("title") or raw.get("id") or "incident"),
            window_start=int(raw["window_start"]),
            window_end=int(raw["window_end"]),
            named_at=int(raw.get("named_at") or raw["window_start"]),
            world_found_out_at=int(
                raw.get("world_found_out_at") or raw.get("named_at") or raw["window_start"]
            ),
            true_origin_id=str(origin.get("id") or TRUE_ORIGIN_MID),
            true_origin_kind=str(origin.get("kind") or "maintainer"),
            default_blast={
                "ecosystem": str(blast.get("ecosystem") or "npm"),
                "name": str(blast.get("name") or ""),
                "version": str(blast.get("version") or ""),
            },
            default_sid=str(raw.get("default_sid") or "svc:mattermost"),
            ticks=ticks,
        )

    @classmethod
    def may11(cls) -> Incident:
        from .paths import repo_root

        path = repo_root() / "artifacts" / "incidents" / "may11.json"
        if path.is_file():
            return cls.load(path)
        return cls.from_dict(_MAY11)

    @classmethod
    def load(cls, path: Path) -> Incident:
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))

    @classmethod
    def from_env(cls) -> Incident:
        env = os.environ.get("PATIENT_ZERO_INCIDENT")
        if env:
            return cls.load(Path(env))
        return cls.may11()
