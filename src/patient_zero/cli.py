"""CLI for the Day-1 ETL. Fetch is optional; emit is always local files → Parquet."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Sequence

from patient_zero.etl import run_etl
from patient_zero.fetch import fetch_dep_graphs, fetch_lockfiles, fetch_npm_searches, fetch_workflows
from patient_zero.ids import rid

ROOT = Path(__file__).resolve().parents[2]
if not (ROOT / "artifacts").exists():
    ROOT = Path.cwd()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_logins(packuments: list[dict[str, Any]]) -> list[str]:
    logins: list[str] = []
    seen: set[str] = set()
    for row in packuments:
        if not str(row.get("pid") or "").startswith("npm:"):
            continue
        for login in row.get("maintainer_logins") or []:
            if login in seen:
                continue
            seen.add(login)
            logins.append(login)
    return logins


def collect_rids(packuments: list[dict[str, Any]]) -> list[str]:
    rids: list[str] = []
    seen: set[str] = set()
    for row in packuments:
        repo_id = rid(row.get("repo_url"))
        if not repo_id or repo_id in seen:
            continue
        seen.add(repo_id)
        rids.append(repo_id)
    return rids


def prepare_caches(
    *,
    ioc_path: Path,
    packuments_path: Path,
    deps_dir: Path,
    searches_dir: Path,
    lockfiles_dir: Path,
    workflows_dir: Path,
    lockfile_specs_path: Path,
    token: str | None,
) -> None:
    from patient_zero.etl import load_ioc, load_packuments

    ioc = load_ioc(ioc_path)
    packs = load_packuments(packuments_path)
    fetch_dep_graphs(ioc, deps_dir)
    fetch_npm_searches(collect_logins(packs), searches_dir)
    specs: list[dict[str, Any]] = []
    if lockfile_specs_path.exists():
        specs = _load_json(lockfile_specs_path)
    fetch_lockfiles(specs, lockfiles_dir)
    fetch_workflows(collect_rids(packs), workflows_dir, token=token)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build data/graph Parquet from IOC + caches.")
    parser.add_argument("--ioc", type=Path, default=ROOT / "artifacts" / "ioc.json")
    parser.add_argument("--packuments", type=Path, default=ROOT / "data" / "enrich" / "packuments.parquet")
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "graph")
    parser.add_argument("--deps-dir", type=Path, default=ROOT / "data" / "depsdev")
    parser.add_argument("--searches-dir", type=Path, default=ROOT / "data" / "npm-search")
    parser.add_argument("--lockfiles-dir", type=Path, default=ROOT / "data" / "lockfiles")
    parser.add_argument("--workflows-dir", type=Path, default=ROOT / "data" / "workflows")
    parser.add_argument(
        "--lockfile-specs",
        type=Path,
        default=ROOT / "artifacts" / "lockfile_specs.json",
    )
    parser.add_argument("--offline", action="store_true", help="Do not fetch; use caches as they are.")
    parser.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not args.offline:
        prepare_caches(
            ioc_path=args.ioc,
            packuments_path=args.packuments,
            deps_dir=args.deps_dir,
            searches_dir=args.searches_dir,
            lockfiles_dir=args.lockfiles_dir,
            workflows_dir=args.workflows_dir,
            lockfile_specs_path=args.lockfile_specs,
            token=args.github_token,
        )

    manifest = run_etl(
        ioc_path=args.ioc,
        packuments_path=args.packuments,
        out_dir=args.out,
        deps_dir=args.deps_dir,
        searches_dir=args.searches_dir,
        lockfiles_dir=args.lockfiles_dir,
        workflows_dir=args.workflows_dir,
    )
    print(json.dumps(manifest, indent=2))
    print(f"elements={manifest['elements']}", file=sys.stderr)
    return 0
