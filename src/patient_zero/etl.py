"""Load local IOC/packument/cache files and emit data/graph Parquet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patient_zero.emit import write_graph
from patient_zero.lockfiles import pins_from_lockfile
from patient_zero.pipeline import build_graph
from patient_zero.workflows import parse_workflow


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_ioc(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    if isinstance(payload, dict) and "records" in payload:
        return list(payload["records"])
    if isinstance(payload, list):
        return payload
    raise ValueError(f"unrecognized IOC file: {path}")


def load_packuments(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".parquet":
        import pyarrow.parquet as pq

        table = pq.read_table(path)
        return table.to_pylist()
    payload = load_json(path)
    if isinstance(payload, dict) and "rows" in payload:
        return list(payload["rows"])
    if isinstance(payload, list):
        return payload
    raise ValueError(f"unrecognized packuments file: {path}")


def _name_from_safe(safe: str) -> str:
    return safe.replace("_at_", "@").replace("__", "/")


def load_dep_graphs(deps_dir: Path | None) -> dict[str, dict[str, Any]]:
    graphs: dict[str, dict[str, Any]] = {}
    if deps_dir is None or not deps_dir.exists():
        return graphs
    for path in deps_dir.rglob("dependencies-*.json"):
        version = path.stem.removeprefix("dependencies-")
        system = path.parent.parent.name
        name = _name_from_safe(path.parent.name)
        eco = system.lower()
        graphs[f"{eco}:{name}@{version}"] = load_json(path)
    return graphs


def load_searches(searches_dir: Path | None) -> dict[str, dict[str, Any]]:
    searches: dict[str, dict[str, Any]] = {}
    if searches_dir is None or not searches_dir.exists():
        return searches
    for path in searches_dir.glob("*.json"):
        searches[path.stem] = load_json(path)
    return searches


def load_lockfiles(lockfiles_dir: Path | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if lockfiles_dir is None:
        return [], []
    catalog_path = lockfiles_dir / "catalog.json"
    if not catalog_path.exists():
        return [], []
    services: list[dict[str, Any]] = []
    pins: list[dict[str, Any]] = []
    for row in load_json(catalog_path):
        path = lockfiles_dir / row["path"]
        try:
            service, service_pins = pins_from_lockfile(
                path,
                sid=row["sid"],
                name=row["name"],
                source_repo=row["source_repo"],
                lockfile_at=int(row["lockfile_at"]),
            )
        except (json.JSONDecodeError, OSError, ValueError, KeyError):
            continue
        services.append(service)
        pins.extend(service_pins)
    return services, pins


def load_workflows(workflows_dir: Path | None) -> list[dict[str, Any]]:
    if workflows_dir is None:
        return []
    catalog_path = workflows_dir / "catalog.json"
    if not catalog_path.exists():
        return []
    rows = []
    for row in load_json(catalog_path):
        text = (workflows_dir / row["file"]).read_text(encoding="utf-8")
        rows.append(parse_workflow(rid=row["rid"], path=row["path"], yaml_text=text))
    return rows


def run_etl(
    *,
    ioc_path: Path,
    packuments_path: Path,
    out_dir: Path,
    deps_dir: Path | None = None,
    searches_dir: Path | None = None,
    lockfiles_dir: Path | None = None,
    workflows_dir: Path | None = None,
) -> dict[str, Any]:
    services, pins = load_lockfiles(lockfiles_dir)
    tables = build_graph(
        ioc_records=load_ioc(ioc_path),
        packuments=load_packuments(packuments_path),
        dep_graphs=load_dep_graphs(deps_dir),
        searches=load_searches(searches_dir),
        services=services,
        pins=pins,
        workflows=load_workflows(workflows_dir),
    )
    return write_graph(out_dir, tables)
