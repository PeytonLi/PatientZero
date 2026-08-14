"""ETL reads local caches and emits the W1 Parquet contract. Network stays out."""

import json
from pathlib import Path

from patient_zero.etl import run_etl
from patient_zero.emit import GRAPH_FILES


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")


def test_run_etl_emits_graph_from_local_files(tmp_path: Path):
    ioc = {
        "records": [
            {
                "pid": "npm:@tanstack/react-query",
                "vid": "npm:@tanstack/react-query@5.90.2",
                "ecosystem": "npm",
                "split": "seed",
            }
        ]
    }
    packuments = [
        {
            "pid": "npm:@tanstack/react-query",
            "vid": "npm:@tanstack/react-query@5.90.2",
            "has_install_script": False,
            "install_hooks": [],
            "maintainer_logins": ["tannerlinsley"],
            "repo_url": "github:TanStack/query",
            "published_at": 100,
        }
    ]
    graph = {
        "nodes": [
            {"versionKey": {"system": "NPM", "name": "@tanstack/react-query", "version": "5.90.2"}},
            {"versionKey": {"system": "NPM", "name": "@tanstack/query-core", "version": "5.90.2"}},
        ],
        "edges": [{"fromNode": 0, "toNode": 1, "requirement": "5.90.2"}],
    }
    lock = {
        "lockfileVersion": 3,
        "packages": {
            "": {"name": "app"},
            "node_modules/@tanstack/react-query": {"version": "5.90.2"},
        },
    }
    ioc_path = tmp_path / "ioc.json"
    packs_path = tmp_path / "packuments.json"
    deps_dir = tmp_path / "deps"
    searches_dir = tmp_path / "searches"
    lock_path = tmp_path / "locks" / "app" / "package-lock.json"
    catalog = tmp_path / "locks" / "catalog.json"
    wf_path = tmp_path / "workflows" / "release.yml"
    out_dir = tmp_path / "graph"

    _write(ioc_path, ioc)
    _write(packs_path, packuments)
    _write(
        deps_dir / "npm" / "_at_tanstack__react-query" / "dependencies-5.90.2.json",
        graph,
    )
    _write(searches_dir / "tannerlinsley.json", {"objects": [{"package": {"name": "@tanstack/store"}}]})
    _write(lock_path, lock)
    _write(
        catalog,
        [
            {
                "sid": "svc:app",
                "name": "app",
                "source_repo": "github:acme/app",
                "path": "app/package-lock.json",
                "lockfile_at": 50,
            }
        ],
    )
    wf_path.parent.mkdir(parents=True, exist_ok=True)
    wf_path.write_text(
        "on:\n  pull_request_target:\npermissions:\n  id-token: write\n",
        encoding="utf-8",
    )
    _write(
        tmp_path / "workflows" / "catalog.json",
        [
            {
                "rid": "github:TanStack/query",
                "path": ".github/workflows/release.yml",
                "file": "release.yml",
            }
        ],
    )

    manifest = run_etl(
        ioc_path=ioc_path,
        packuments_path=packs_path,
        out_dir=out_dir,
        deps_dir=deps_dir,
        searches_dir=searches_dir,
        lockfiles_dir=tmp_path / "locks",
        workflows_dir=tmp_path / "workflows",
    )
    for name in GRAPH_FILES:
        assert (out_dir / name).is_file(), name
    assert manifest["files"]["packages.parquet"]["rows"] >= 2
    assert manifest["files"]["edges_depends_on.parquet"]["rows"] == 1
    assert manifest["files"]["edges_pins.parquet"]["rows"] == 1
    assert manifest["files"]["workflows.parquet"]["rows"] == 1
    assert (out_dir / "MANIFEST.json").is_file()
