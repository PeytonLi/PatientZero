"""Resumable JSON fetches. Opener is injected so unit tests never hit the network."""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable

from patient_zero.assemble import is_human_login
from patient_zero.ids import vid as make_vid

UA = "PatientZero-W1/0.1 (hackathon ETL; polite cache)"
DEPSDEV = "https://api.deps.dev/v3alpha"
Opener = Callable[..., Any]


def _enc(part: str) -> str:
    return urllib.parse.quote(part, safe="")


def split_vid(vid_s: str) -> tuple[str, str, str]:
    eco, _, rest = vid_s.partition(":")
    name, version = rest.rsplit("@", 1)
    return eco, name, version


def safe_package_name(name: str) -> str:
    return name.replace("/", "__").replace("@", "_at_")


def deps_cache_path(cache_dir: Path, vid_s: str) -> Path:
    eco, name, version = split_vid(vid_s)
    return cache_dir / eco / safe_package_name(name) / f"dependencies-{version}.json"


def deps_url(vid_s: str) -> str:
    eco, name, version = split_vid(vid_s)
    return (
        f"{DEPSDEV}/systems/{_enc(eco)}/packages/{_enc(name)}"
        f"/versions/{_enc(version)}:dependencies"
    )


def package_url(eco: str, name: str) -> str:
    return f"{DEPSDEV}/systems/{_enc(eco)}/packages/{_enc(name)}"


def package_cache_path(cache_dir: Path, eco: str, name: str) -> Path:
    return cache_dir / eco / safe_package_name(name) / "package.json"


def default_version(package: dict[str, Any]) -> str | None:
    versions = package.get("versions") or []
    for row in versions:
        if row.get("isDefault"):
            key = row.get("versionKey") or {}
            if key.get("version"):
                return key["version"]
    if versions:
        key = versions[-1].get("versionKey") or {}
        return key.get("version")
    return None


def _graph_or_404(
    vid_s: str,
    cache_dir: Path,
    opener: Opener | None,
) -> dict[str, Any] | None:
    try:
        return cached_json(deps_url(vid_s), deps_cache_path(cache_dir, vid_s), opener=opener)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def cached_bytes(
    url: str,
    dest: Path,
    *,
    opener: Opener | None = None,
    headers: dict[str, str] | None = None,
) -> bytes:
    if dest.exists():
        return dest.read_bytes()
    dest.parent.mkdir(parents=True, exist_ok=True)
    open_url = opener or urllib.request.urlopen
    hdrs = {"User-Agent": UA, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with open_url(req, timeout=60) as resp:
                body = resp.read()
            dest.write_bytes(body)
            if opener is None:
                time.sleep(0.05)
            return body
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code in {429, 503} and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise
        except urllib.error.URLError as exc:
            last_error = exc
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise
    raise last_error or RuntimeError(url)


def cached_json(
    url: str,
    dest: Path,
    *,
    opener: Opener | None = None,
    headers: dict[str, str] | None = None,
) -> Any:
    return json.loads(cached_bytes(url, dest, opener=opener, headers=headers).decode("utf-8"))


def fetch_dep_graphs(
    ioc_records: list[dict[str, Any]],
    cache_dir: Path,
    *,
    opener: Opener | None = None,
) -> dict[str, dict[str, Any]]:
    by_pid: dict[str, list[str]] = {}
    for rec in ioc_records:
        vid_s = rec.get("vid")
        if not vid_s:
            continue
        eco, name, _version = split_vid(vid_s)
        pid_s = rec.get("pid") or f"{eco}:{name}"
        vids = by_pid.setdefault(pid_s, [])
        if vid_s not in vids:
            vids.append(vid_s)

    graphs: dict[str, dict[str, Any]] = {}
    skipped = 0
    fallback = 0
    for i, (pid_s, vids) in enumerate(by_pid.items(), start=1):
        if i % 25 == 1:
            print(f"deps.dev {i} {pid_s}", file=sys.stderr, flush=True)
        resolved: str | None = None
        graph: dict[str, Any] | None = None
        for vid_s in vids:
            graph = _graph_or_404(vid_s, cache_dir, opener)
            if graph is not None:
                resolved = vid_s
                break
        if graph is None:
            eco, _, name = pid_s.partition(":")
            try:
                package = cached_json(
                    package_url(eco, name),
                    package_cache_path(cache_dir, eco, name),
                    opener=opener,
                )
            except urllib.error.HTTPError as exc:
                if exc.code == 404:
                    skipped += 1
                    continue
                raise
            default = default_version(package)
            if not default:
                skipped += 1
                continue
            resolved = make_vid(eco, name, default)
            graph = _graph_or_404(resolved, cache_dir, opener)
            if graph is None:
                skipped += 1
                continue
            fallback += 1
        graphs[resolved] = graph
    print(
        f"deps.dev graphs={len(graphs)} skipped_404={skipped} fallback_default={fallback}",
        file=sys.stderr,
        flush=True,
    )
    return graphs


def npm_search_url(login: str) -> str:
    q = urllib.parse.urlencode({"text": f"maintainer:{login}", "size": 250})
    return f"https://registry.npmjs.org/-/v1/search?{q}"


def fetch_npm_searches(
    logins: list[str],
    cache_dir: Path,
    *,
    opener: Opener | None = None,
) -> dict[str, dict[str, Any]]:
    searches: dict[str, dict[str, Any]] = {}
    for login in logins:
        if not is_human_login(login):
            continue
        dest = cache_dir / f"{login.replace('/', '_')}.json"
        print(f"npm search {login}", file=sys.stderr, flush=True)
        try:
            searches[login] = cached_json(npm_search_url(login), dest, opener=opener)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                continue
            raise
    return searches


def fetch_lockfiles(
    specs: list[dict[str, Any]],
    dest_dir: Path,
    *,
    opener: Opener | None = None,
) -> list[dict[str, Any]]:
    catalog: list[dict[str, Any]] = []
    for spec in specs:
        rel = f"{spec['name']}/package-lock.json"
        dest = dest_dir / rel
        try:
            cached_bytes(spec["url"], dest, opener=opener)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                continue
            raise
        lockfile_at = spec.get("lockfile_at")
        catalog.append(
            {
                "sid": spec["sid"],
                "name": spec["name"],
                "source_repo": spec["source_repo"],
                "path": rel.replace("\\", "/"),
                "lockfile_at": int(lockfile_at) if lockfile_at else int(time.time()),
            }
        )
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    return catalog


def _split_rid(rid_s: str) -> tuple[str, str] | None:
    if not rid_s.startswith("github:"):
        return None
    rest = rid_s.split(":", 1)[1]
    org, _, repo = rest.partition("/")
    if not org or not repo:
        return None
    return org, repo


def fetch_workflows(
    rids: list[str],
    dest_dir: Path,
    *,
    opener: Opener | None = None,
    token: str | None = None,
) -> list[dict[str, Any]]:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    catalog: list[dict[str, Any]] = []
    seen: set[str] = set()
    for rid_s in rids:
        if rid_s in seen:
            continue
        seen.add(rid_s)
        parts = _split_rid(rid_s)
        if not parts:
            continue
        org, repo = parts
        list_url = f"https://api.github.com/repos/{_enc(org)}/{_enc(repo)}/contents/.github/workflows"
        list_dest = dest_dir / org / repo / "_listing.json"
        try:
            listing = cached_json(list_url, list_dest, opener=opener, headers=headers)
        except urllib.error.HTTPError as exc:
            if exc.code in {404, 403}:
                continue
            raise
        if isinstance(listing, dict):
            listing = [listing]
        for item in listing or []:
            if item.get("type") != "file":
                continue
            path = item.get("path") or ""
            name = item.get("name") or ""
            if not name.endswith((".yml", ".yaml")):
                continue
            download = item.get("download_url")
            if not download:
                continue
            rel = f"{org}/{repo}/{name}"
            dest = dest_dir / rel
            try:
                cached_bytes(download, dest, opener=opener, headers=headers)
            except urllib.error.HTTPError as exc:
                if exc.code == 404:
                    continue
                raise
            catalog.append({"rid": rid_s, "path": path, "file": rel.replace("\\", "/")})
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    return catalog

