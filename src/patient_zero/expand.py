"""Expand a maintainer login into the packages they publish (npm search JSON)."""

from __future__ import annotations

from typing import Any

from patient_zero.assemble import is_human_login
from patient_zero.ids import mid, pid


def packages_from_search(
    search: dict[str, Any],
    *,
    login: str,
    ecosystem: str,
) -> list[dict[str, str]]:
    if not is_human_login(login):
        return []
    mid_s = mid(ecosystem, login)
    rows = []
    for obj in search.get("objects") or []:
        name = (obj.get("package") or {}).get("name")
        if not name:
            continue
        rows.append({"mid": mid_s, "pid": pid(ecosystem, name)})
    rows.sort(key=lambda r: r["pid"])
    return rows
