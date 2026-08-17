"""Build graph tables from IOC records + packuments. Dedup offline."""

from __future__ import annotations

from typing import Any

from patient_zero.ids import mid, rid

SENTINEL_VALID_TO = 4102444800  # 2100-01-01 UTC
BOT_LOGINS = frozenset({"github actions", "npm", "dependabot", "greenkeeper"})
T2_EDGE_TABLES = (
    "edges_maintains",
    "edges_published_from",
    "edges_has_workflow",
    "edges_publishes_via_oidc",
)


def is_human_login(login: str) -> bool:
    return bool(login) and login.strip().lower() not in BOT_LOGINS


def _split_pid(pid_s: str) -> tuple[str, str]:
    eco, _, name = pid_s.partition(":")
    return eco, name


def _version_of(vid_s: str, pid_s: str) -> str:
    prefix = pid_s + "@"
    if vid_s.startswith(prefix):
        return vid_s[len(prefix) :]
    return vid_s.rsplit("@", 1)[-1]


def stamp_t2_windows(tables: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    """Give T2 edges the same valid_from/valid_to columns T1 already has.

    Packuments do not carry maintainer tenure. Stamp 0 → sentinel so the
    bitemporal filter path exists; a later incident can overwrite with real
    windows. Existing keys are left alone.
    """
    for name in T2_EDGE_TABLES:
        for row in tables.get(name) or []:
            row.setdefault("valid_from", 0)
            row.setdefault("valid_to", SENTINEL_VALID_TO)
    return tables


def assemble(
    ioc_records: list[dict[str, Any]],
    packuments: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    packs = {row["vid"]: row for row in packuments}

    packages: dict[str, dict[str, Any]] = {}
    versions: dict[str, dict[str, Any]] = {}
    maintainers: dict[str, dict[str, Any]] = {}
    repos: dict[str, dict[str, Any]] = {}
    maintains: set[tuple[str, str]] = set()
    published_from: set[tuple[str, str]] = set()

    for rec in ioc_records:
        pid_s = rec["pid"]
        vid_s = rec["vid"]
        eco, name = _split_pid(pid_s)
        packages[pid_s] = {"pid": pid_s, "ecosystem": eco, "name": name}

        pack = packs.get(vid_s, {})
        versions[vid_s] = {
            "vid": vid_s,
            "pid": pid_s,
            "ecosystem": eco,
            "name": name,
            "version": _version_of(vid_s, pid_s),
            "published_at": pack.get("published_at"),
            "unpublished_at": None,
            "has_install_script": bool(pack.get("has_install_script", False)),
            "install_hooks": list(pack.get("install_hooks") or []),
        }

        for login in pack.get("maintainer_logins") or []:
            if not is_human_login(login):
                continue
            mid_s = mid(eco, login)
            maintainers[mid_s] = {
                "mid": mid_s,
                "ecosystem": eco,
                "login": login,
                "email_domain": None,
                "twofa": None,
            }
            maintains.add((mid_s, pid_s))

        repo_id = rid(pack.get("repo_url"))
        if repo_id:
            _, _, rest = repo_id.partition(":")
            org, _, repo_name = rest.partition("/")
            repos[repo_id] = {"rid": repo_id, "host": "github", "org": org, "name": repo_name}
            published_from.add((pid_s, repo_id))

    return stamp_t2_windows(
        {
            "packages": sorted(packages.values(), key=lambda r: r["pid"]),
            "versions": sorted(versions.values(), key=lambda r: r["vid"]),
            "maintainers": sorted(maintainers.values(), key=lambda r: r["login"]),
            "repos": sorted(repos.values(), key=lambda r: r["rid"]),
            "edges_maintains": [
                {"mid": a, "pid": b} for a, b in sorted(maintains)
            ],
            "edges_published_from": [
                {"pid": a, "rid": b} for a, b in sorted(published_from)
            ],
        }
    )
