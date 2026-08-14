#!/usr/bin/env python3
"""deps.dev REST probe (v3alpha). Fetch package + version + dependencies.

HANDOFF v2: data path is REST-first, not BigQuery. This is a small-package
probe only — do not pull the whole slice here.

Usage:
    python scripts/depsdev.py
    python scripts/depsdev.py --system npm --name @tanstack/query-core
    python scripts/depsdev.py --system npm --name @tanstack/query-core --version 5.0.1
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://api.deps.dev/v3alpha"
CACHE_DIR = Path("data/depsdev")


def enc(part: str) -> str:
    return urllib.parse.quote(part, safe="")


def url_package(system: str, name: str) -> str:
    return f"{BASE}/systems/{enc(system)}/packages/{enc(name)}"


def url_version(system: str, name: str, version: str) -> str:
    return f"{url_package(system, name)}/versions/{enc(version)}"


def url_dependencies(system: str, name: str, version: str) -> str:
    return f"{url_version(system, name, version)}:dependencies"


def url_dependents(system: str, name: str, version: str) -> str:
    """Counts only — not a list of dependent packages."""
    return f"{url_version(system, name, version)}:dependents"


def cache_path(cache_dir: Path, kind: str, system: str, name: str, version: str | None = None) -> Path:
    safe = name.replace("/", "__").replace("@", "_at_")
    if version:
        return cache_dir / system / safe / f"{kind}-{version}.json"
    return cache_dir / system / safe / f"{kind}.json"


def fetch(url: str, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return json.loads(dest.read_text(encoding="utf-8"))
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "patient-zero-probe"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code} for {url}\n{e.read().decode('utf-8', errors='replace')}") from e
    dest.write_bytes(body)
    return json.loads(body.decode("utf-8"))


def default_version(package: dict) -> str | None:
    versions = package.get("versions") or []
    for v in versions:
        if v.get("isDefault"):
            vk = v.get("versionKey") or {}
            return vk.get("version")
    if versions:
        vk = versions[-1].get("versionKey") or {}
        return vk.get("version")
    return None


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--system", default="npm")
    p.add_argument("--name", default="@tanstack/query-core")
    p.add_argument("--version", default=None, help="omit to use deps.dev default version")
    p.add_argument("--cache-dir", default=str(CACHE_DIR))
    args = p.parse_args(argv)

    cache_dir = Path(args.cache_dir)

    pkg_url = url_package(args.system, args.name)
    package = fetch(pkg_url, cache_path(cache_dir, "package", args.system, args.name))
    n_versions = len(package.get("versions") or [])
    version = args.version or default_version(package)
    if not version:
        print(json.dumps({"error": "no versions", "package_url": pkg_url}, indent=2))
        return 1

    ver = fetch(
        url_version(args.system, args.name, version),
        cache_path(cache_dir, "version", args.system, args.name, version),
    )
    deps = fetch(
        url_dependencies(args.system, args.name, version),
        cache_path(cache_dir, "dependencies", args.system, args.name, version),
    )
    nodes = deps.get("nodes") or []
    edges = deps.get("edges") or []
    relation = {}
    for n in nodes:
        rel = n.get("relation") or "UNSPECIFIED"
        relation[rel] = relation.get(rel, 0) + 1

    dependents = None
    dep_url = url_dependents(args.system, args.name, version)
    try:
        dependents = fetch(
            dep_url,
            cache_path(cache_dir, "dependents", args.system, args.name, version),
        )
    except SystemExit as exc:
        dependents = {"error": str(exc)}

    out = {
        "system": args.system,
        "name": args.name,
        "version": version,
        "package_versions": n_versions,
        "dependency_nodes": len(nodes),
        "dependency_edges": len(edges),
        "nodes_by_relation": relation,
        "dependent_counts": dependents,
        "licenses": ver.get("licenses") or [],
        "cached_under": str(cache_dir / args.system),
        "note": (
            "GetDependents returns aggregate counts, not a reverse-closure listing. "
            "Leg 1 reverse DEPENDS_ON still needs BigQuery (docs.deps.dev/bigquery/v1) "
            "or a lockfile-only PINS slice."
        ),
        "urls": {
            "package": pkg_url,
            "version": url_version(args.system, args.name, version),
            "dependencies": url_dependencies(args.system, args.name, version),
            "dependents": dep_url,
        },
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
