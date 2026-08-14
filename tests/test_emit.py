"""Parquet handoff. W2 loads these files; a missing column or duplicate id is a silent graph bug."""

from pathlib import Path

import pyarrow.parquet as pq

from patient_zero.assemble import SENTINEL_VALID_TO, assemble
from patient_zero.emit import GRAPH_FILES, write_graph


IOC = [
    {
        "pid": "npm:@tanstack/query-core",
        "vid": "npm:@tanstack/query-core@5.90.2",
        "ecosystem": "npm",
        "first_seen_utc": 1,
        "sources": ["s"],
        "confidence": 1.0,
        "split": "seed",
    }
]
PACKUMENTS = [
    {
        "pid": "npm:@tanstack/query-core",
        "vid": "npm:@tanstack/query-core@5.90.2",
        "has_install_script": False,
        "install_hooks": [],
        "maintainer_logins": ["tannerlinsley"],
        "repo_url": "github:TanStack/query",
        "published_at": 10,
    }
]


def test_write_graph_emits_all_contract_files_and_manifest(tmp_path: Path):
    tables = assemble(IOC, PACKUMENTS)
    tables["edges_depends_on"] = [
        {
            "src_vid": "npm:@tanstack/react-query@5.90.2",
            "dst_vid": "npm:@tanstack/query-core@5.90.2",
            "range": "^5.90.2",
            "resolved_version": "5.90.2",
            "valid_from": 10,
            "valid_to": SENTINEL_VALID_TO,
        }
    ]
    tables["edges_pins"] = []
    tables["services"] = []
    tables["workflows"] = []
    tables["advisories"] = [{"aid": "ghsa:GHSA-g7cv-rxg3-hmpx", "source": "ghsa", "severity": "high"}]
    tables["edges_has_workflow"] = []
    tables["edges_publishes_via_oidc"] = []
    tables["edges_affects"] = [
        {"aid": "ghsa:GHSA-g7cv-rxg3-hmpx", "vid": "npm:@tanstack/query-core@5.90.2"}
    ]

    manifest = write_graph(tmp_path, tables)
    for name in GRAPH_FILES:
        assert (tmp_path / name).is_file(), name
    assert manifest["files"]["packages.parquet"]["rows"] == 1
    assert manifest["files"]["versions.parquet"]["rows"] == 1
    assert manifest["elements"] == sum(f["rows"] for f in manifest["files"].values())
    pkgs = pq.read_table(tmp_path / "packages.parquet")
    assert pkgs.column_names == ["pid", "ecosystem", "name"]
    assert pkgs.to_pydict()["pid"] == ["npm:@tanstack/query-core"]
    deps = pq.read_table(tmp_path / "edges_depends_on.parquet")
    assert None not in deps.to_pydict()["valid_to"]
    assert deps.to_pydict()["valid_to"] == [SENTINEL_VALID_TO]
