"""Write the W1→W2 Parquet contract. Empty tables still get column schemas."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

GRAPH_FILES = (
    "packages.parquet",
    "versions.parquet",
    "maintainers.parquet",
    "repos.parquet",
    "workflows.parquet",
    "services.parquet",
    "advisories.parquet",
    "edges_depends_on.parquet",
    "edges_pins.parquet",
    "edges_maintains.parquet",
    "edges_published_from.parquet",
    "edges_has_workflow.parquet",
    "edges_publishes_via_oidc.parquet",
    "edges_affects.parquet",
)

_TABLE_KEY = {
    "packages.parquet": "packages",
    "versions.parquet": "versions",
    "maintainers.parquet": "maintainers",
    "repos.parquet": "repos",
    "workflows.parquet": "workflows",
    "services.parquet": "services",
    "advisories.parquet": "advisories",
    "edges_depends_on.parquet": "edges_depends_on",
    "edges_pins.parquet": "edges_pins",
    "edges_maintains.parquet": "edges_maintains",
    "edges_published_from.parquet": "edges_published_from",
    "edges_has_workflow.parquet": "edges_has_workflow",
    "edges_publishes_via_oidc.parquet": "edges_publishes_via_oidc",
    "edges_affects.parquet": "edges_affects",
}

SCHEMAS: dict[str, pa.Schema] = {
    "packages": pa.schema([
        ("pid", pa.string()), ("ecosystem", pa.string()), ("name", pa.string()),
    ]),
    "versions": pa.schema([
        ("vid", pa.string()), ("pid", pa.string()), ("ecosystem", pa.string()),
        ("name", pa.string()), ("version", pa.string()),
        ("published_at", pa.int64()), ("unpublished_at", pa.int64()),
        ("has_install_script", pa.bool_()), ("install_hooks", pa.list_(pa.string())),
    ]),
    "maintainers": pa.schema([
        ("mid", pa.string()), ("ecosystem", pa.string()), ("login", pa.string()),
        ("email_domain", pa.string()), ("twofa", pa.bool_()),
    ]),
    "repos": pa.schema([
        ("rid", pa.string()), ("host", pa.string()), ("org", pa.string()), ("name", pa.string()),
    ]),
    "workflows": pa.schema([
        ("wid", pa.string()), ("rid", pa.string()), ("path", pa.string()),
        ("trigger", pa.string()),
        ("uses_pull_request_target", pa.bool_()), ("has_oidc_publish", pa.bool_()),
    ]),
    "services": pa.schema([
        ("sid", pa.string()), ("name", pa.string()), ("source_repo", pa.string()),
    ]),
    "advisories": pa.schema([
        ("aid", pa.string()), ("source", pa.string()), ("severity", pa.string()),
    ]),
    "edges_depends_on": pa.schema([
        ("src_vid", pa.string()), ("dst_vid", pa.string()), ("range", pa.string()),
        ("resolved_version", pa.string()), ("valid_from", pa.int64()), ("valid_to", pa.int64()),
    ]),
    "edges_pins": pa.schema([
        ("sid", pa.string()), ("dst_vid", pa.string()), ("lockfile_at", pa.int64()),
        ("valid_from", pa.int64()), ("valid_to", pa.int64()),
    ]),
    "edges_maintains": pa.schema([
        ("mid", pa.string()), ("pid", pa.string()),
    ]),
    "edges_published_from": pa.schema([
        ("pid", pa.string()), ("rid", pa.string()),
    ]),
    "edges_has_workflow": pa.schema([
        ("rid", pa.string()), ("wid", pa.string()),
    ]),
    "edges_publishes_via_oidc": pa.schema([
        ("wid", pa.string()), ("pid", pa.string()),
    ]),
    "edges_affects": pa.schema([
        ("aid", pa.string()), ("vid", pa.string()),
    ]),
}


def _table(key: str, rows: list[dict[str, Any]]) -> pa.Table:
    schema = SCHEMAS[key]
    if not rows:
        return pa.Table.from_pylist([], schema=schema)
    # Align keys to schema; missing fields become null.
    aligned = [{field.name: row.get(field.name) for field in schema} for row in rows]
    return pa.Table.from_pylist(aligned, schema=schema)


def write_graph(out_dir: Path, tables: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    files: dict[str, dict[str, int]] = {}
    for filename in GRAPH_FILES:
        key = _TABLE_KEY[filename]
        table = _table(key, tables.get(key) or [])
        path = out_dir / filename
        pq.write_table(table, path)
        files[filename] = {"rows": table.num_rows, "bytes": path.stat().st_size}
    manifest = {
        "files": files,
        "elements": sum(f["rows"] for f in files.values()),
    }
    (out_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
