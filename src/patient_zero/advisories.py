"""Seed GHSA advisory fan-out onto seed-set versions."""

from __future__ import annotations

from typing import Any

AID = "ghsa:GHSA-g7cv-rxg3-hmpx"


def advisory_tables(
    ioc_records: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    advisories = [{"aid": AID, "source": "ghsa", "severity": "high"}]
    vids = sorted(
        {
            rec["vid"]
            for rec in ioc_records
            if rec.get("split") == "seed" and rec.get("vid")
        }
    )
    affects = [{"aid": AID, "vid": vid} for vid in vids]
    return advisories, affects
