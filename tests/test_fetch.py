"""HTTP cache. ETL must be resumable; tests never touch the network."""

import json
import urllib.parse
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError

from patient_zero.fetch import (
    cached_json,
    fetch_dep_graphs,
    fetch_lockfiles,
    fetch_npm_searches,
    fetch_workflows,
)


class _Resp:
    def __init__(self, body: bytes):
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_cached_json_hits_opener_once(tmp_path: Path):
    calls: list[str] = []

    def opener(req, timeout=60):
        url = req if isinstance(req, str) else req.full_url
        calls.append(url)
        return _Resp(b'{"ok": true}')

    dest = tmp_path / "x.json"
    first = cached_json("https://example.test/x", dest, opener=opener)
    second = cached_json("https://example.test/x", dest, opener=opener)
    assert first == {"ok": True}
    assert second == {"ok": True}
    assert calls == ["https://example.test/x"]


def test_fetch_dep_graphs_caches_by_vid(tmp_path: Path):
    graph = {"nodes": [], "edges": []}
    calls: list[str] = []

    def opener(req, timeout=60):
        url = req if isinstance(req, str) else req.full_url
        calls.append(url)
        return _Resp(json.dumps(graph).encode())

    graphs = fetch_dep_graphs(
        [{"vid": "npm:@tanstack/react-query@5.90.2", "ecosystem": "npm"}],
        tmp_path,
        opener=opener,
    )
    dest = tmp_path / "npm" / "_at_tanstack__react-query" / "dependencies-5.90.2.json"
    assert dest.is_file()
    assert graphs["npm:@tanstack/react-query@5.90.2"] == graph
    assert calls == [
        "https://api.deps.dev/v3alpha/systems/npm/packages/%40tanstack%2Freact-query/versions/5.90.2:dependencies"
    ]


def test_fetch_dep_graphs_skips_http_404(tmp_path: Path):
    def opener(req, timeout=60):
        url = req if isinstance(req, str) else req.full_url
        raise HTTPError(url, 404, "Not Found", None, BytesIO(b"{}"))

    graphs = fetch_dep_graphs(
        [{"vid": "npm:missing@1.0.0", "ecosystem": "npm"}],
        tmp_path,
        opener=opener,
    )
    assert graphs == {}


def test_fetch_dep_graphs_falls_back_to_package_default_version(tmp_path: Path):
    graph = {
        "nodes": [
            {"versionKey": {"system": "NPM", "name": "left-pad", "version": "1.3.0"}},
            {"versionKey": {"system": "NPM", "name": "repeat-string", "version": "1.6.1"}},
        ],
        "edges": [{"fromNode": 0, "toNode": 1, "requirement": "^1.6.1"}],
    }
    package = {
        "versions": [
            {
                "versionKey": {"system": "NPM", "name": "left-pad", "version": "1.3.0"},
                "isDefault": True,
            }
        ]
    }

    def opener(req, timeout=60):
        url = req if isinstance(req, str) else req.full_url
        if ":dependencies" in url and "1.0.0" in url:
            raise HTTPError(url, 404, "Not Found", None, BytesIO(b"{}"))
        if ":dependencies" in url and "1.3.0" in url:
            return _Resp(json.dumps(graph).encode())
        if "/packages/left-pad" in url:
            return _Resp(json.dumps(package).encode())
        raise AssertionError(url)

    graphs = fetch_dep_graphs(
        [{"vid": "npm:left-pad@1.0.0", "pid": "npm:left-pad", "ecosystem": "npm"}],
        tmp_path,
        opener=opener,
    )
    assert "npm:left-pad@1.3.0" in graphs
    assert graphs["npm:left-pad@1.3.0"] == graph
    dest = tmp_path / "npm" / "left-pad" / "dependencies-1.3.0.json"
    assert dest.is_file()


def test_fetch_npm_searches_skips_bot_logins(tmp_path: Path):
    calls: list[str] = []

    def opener(req, timeout=60):
        url = req if isinstance(req, str) else req.full_url
        calls.append(url)
        return _Resp(b'{"objects":[]}')

    searches = fetch_npm_searches(
        ["tannerlinsley", "GitHub Actions"],
        tmp_path,
        opener=opener,
    )
    assert "tannerlinsley" in searches
    assert "GitHub Actions" not in searches
    assert len(calls) == 1
    assert "tannerlinsley" in urllib.parse.unquote(calls[0])


def test_fetch_lockfiles_writes_catalog_and_json(tmp_path: Path):
    lock = {
        "lockfileVersion": 3,
        "packages": {"": {"name": "app"}, "node_modules/left-pad": {"version": "1.3.0"}},
    }

    def opener(req, timeout=60):
        return _Resp(json.dumps(lock).encode())

    catalog = fetch_lockfiles(
        [
            {
                "sid": "svc:app",
                "name": "app",
                "source_repo": "github:acme/app",
                "url": "https://example.test/package-lock.json",
                "lockfile_at": 50,
            }
        ],
        tmp_path,
        opener=opener,
    )
    assert catalog == [
        {
            "sid": "svc:app",
            "name": "app",
            "source_repo": "github:acme/app",
            "path": "app/package-lock.json",
            "lockfile_at": 50,
        }
    ]
    saved = json.loads((tmp_path / "app" / "package-lock.json").read_text(encoding="utf-8"))
    assert saved["lockfileVersion"] == 3
    on_disk = json.loads((tmp_path / "catalog.json").read_text(encoding="utf-8"))
    assert on_disk == catalog


def test_fetch_workflows_lists_and_downloads_yaml(tmp_path: Path):
    def opener(req, timeout=60):
        url = req if isinstance(req, str) else req.full_url
        if url.endswith("/contents/.github/workflows"):
            listing = [
                {
                    "name": "release.yml",
                    "path": ".github/workflows/release.yml",
                    "type": "file",
                    "download_url": "https://example.test/release.yml",
                }
            ]
            return _Resp(json.dumps(listing).encode())
        return _Resp(b"on:\n  pull_request_target:\n")

    catalog = fetch_workflows(["github:TanStack/query"], tmp_path, opener=opener)
    assert catalog == [
        {
            "rid": "github:TanStack/query",
            "path": ".github/workflows/release.yml",
            "file": "TanStack/query/release.yml",
        }
    ]
    text = (tmp_path / "TanStack" / "query" / "release.yml").read_text(encoding="utf-8")
    assert "pull_request_target" in text

