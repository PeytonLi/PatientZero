"""Union graph tables by stable id. Extra depends_on endpoints become Version nodes."""

from __future__ import annotations

from typing import Any

from patient_zero.assemble import _split_pid, _version_of

_KEYS = {
    "packages": "pid",
    "versions": "vid",
    "maintainers": "mid",
    "repos": "rid",
    "workflows": "wid",
    "services": "sid",
    "advisories": "aid",
    "edges_depends_on": ("src_vid", "dst_vid"),
    "edges_pins": ("sid", "dst_vid"),
    "edges_maintains": ("mid", "pid"),
    "edges_published_from": ("pid", "rid"),
    "edges_has_workflow": ("rid", "wid"),
    "edges_publishes_via_oidc": ("wid", "pid"),
    "edges_affects": ("aid", "vid"),
}


def _row_key(table: str, row: dict[str, Any]) -> tuple:
    key = _KEYS[table]
    if isinstance(key, tuple):
        return tuple(row[k] for k in key)
    return (row[key],)


def merge_tables(
    base: dict[str, list[dict[str, Any]]],
    extra: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    names = set(base) | set(extra) | set(_KEYS)
    for name in names:
        seen: dict[tuple, dict[str, Any]] = {}
        for row in list(base.get(name) or []) + list(extra.get(name) or []):
            if name not in _KEYS:
                continue
            seen[_row_key(name, row)] = row
        if name in _KEYS:
            out[name] = sorted(seen.values(), key=_row_key_sort(name))
    return out


def _row_key_sort(name: str):
    def sort_key(row: dict[str, Any]) -> tuple:
        return _row_key(name, row)

    return sort_key


def ensure_endpoint_nodes(tables: dict[str, list[dict[str, Any]]]) -> None:
    versions = {row["vid"]: row for row in tables.get("versions") or []}
    packages = {row["pid"]: row for row in tables.get("packages") or []}
    vids: list[str] = []
    for row in tables.get("edges_depends_on") or []:
        vids.extend([row["src_vid"], row["dst_vid"]])
    for row in tables.get("edges_pins") or []:
        vids.append(row["dst_vid"])
    for vid_s in vids:
        if vid_s in versions:
            continue
        # vid = "eco:name@version" — name may contain '@' (scoped).
        eco, _, rest = vid_s.partition(":")
        if "@" not in rest:
            continue
        name, version = rest.rsplit("@", 1)
        pid_s = f"{eco}:{name}"
        packages.setdefault(pid_s, {"pid": pid_s, "ecosystem": eco, "name": name})
        versions[vid_s] = {
            "vid": vid_s,
            "pid": pid_s,
            "ecosystem": eco,
            "name": name,
            "version": version,
            "published_at": None,
            "unpublished_at": None,
            "has_install_script": False,
            "install_hooks": [],
        }
    tables["packages"] = sorted(packages.values(), key=lambda r: r["pid"])
    tables["versions"] = sorted(versions.values(), key=lambda r: r["vid"])
