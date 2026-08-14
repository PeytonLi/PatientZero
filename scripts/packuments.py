#!/usr/bin/env python3
"""Pull npm (and PyPI) packuments for the reconciled IOC set.

Caches JSON under data/enrich/packuments/ (gitignored, resumable).
Writes:
  data/enrich/packuments.parquet
  artifacts/packuments_seed.json   (seed set, committed)

Be polite: timeout, concurrency <= 4, skip cached files.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
CACHE = ROOT / "data" / "enrich" / "packuments"
PARQUET = ROOT / "data" / "enrich" / "packuments.parquet"
SEED_OUT = ARTIFACTS / "packuments_seed.json"
IOC_JSON = ARTIFACTS / "ioc.json"

HOOKS = ("preinstall", "install", "postinstall", "prepare")
UA = "PatientZero-W3/0.1 (packument research; local hackathon; polite 4-wide)"
TIMEOUT = 25
MAX_WORKERS = 4


def parse_utc_epoch(value: str | None) -> int | None:
    if not value:
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.astimezone(timezone.utc).timestamp())


def normalize_repo(repo) -> str | None:
    if not repo:
        return None
    url = ""
    if isinstance(repo, dict):
        url = repo.get("url") or repo.get("web") or ""
    else:
        url = str(repo)
    url = url.strip()
    if url.startswith("git@github.com:"):
        url = "github.com/" + url.split(":", 1)[1]
    # Peel stacked prefixes (git+https://github.com/...).
    while True:
        stripped = False
        for prefix in ("git+", "git://", "https://", "http://", "ssh://git@"):
            if url.startswith(prefix):
                url = url[len(prefix) :]
                stripped = True
                break
        if not stripped:
            break
    if url.startswith("github.com:"):
        url = "github.com/" + url.split(":", 1)[1]
    url = url.removesuffix(".git").rstrip("/")
    if url.startswith("github.com/"):
        parts = url[len("github.com/") :].split("/")
        if len(parts) >= 2:
            return f"github:{parts[0]}/{parts[1]}"
    if url.startswith("github:"):
        return url
    return url or None


def maintainer_logins(packument: dict, version_doc: dict) -> list[str]:
    logins: list[str] = []
    for src in (version_doc.get("maintainers"), packument.get("maintainers")):
        if not src:
            continue
        for item in src:
            if isinstance(item, dict):
                logins.append(item.get("name") or item.get("username") or "")
            elif isinstance(item, str):
                logins.append(item)
    user = version_doc.get("_npmUser")
    if isinstance(user, dict) and user.get("name"):
        logins.append(user["name"])
    return sorted({x for x in logins if x})


def install_hooks_of(version_doc: dict) -> list[str]:
    scripts = version_doc.get("scripts") or {}
    if not isinstance(scripts, dict):
        return []
    return [h for h in HOOKS if h in scripts]


def npm_packument_url(name: str) -> str:
    # Scoped names: https://registry.npmjs.org/@tanstack%2freact-query
    encoded = urllib.parse.quote(name, safe="@")
    encoded = encoded.replace("/", "%2f")
    return f"https://registry.npmjs.org/{encoded}"


def pypi_url(name: str) -> str:
    return f"https://pypi.org/pypi/{urllib.parse.quote(name)}/json"


def cache_path(ecosystem: str, name: str) -> Path:
    safe = name.replace("/", "__")
    return CACHE / f"{ecosystem}__{safe}.json"


def http_get_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_or_fetch(ecosystem: str, name: str, force: bool = False) -> dict:
    path = cache_path(ecosystem, name)
    if path.exists() and not force:
        try:
            cached = json.loads(path.read_text(encoding="utf-8"))
            if cached.get("_fetch_ok"):
                return cached
        except json.JSONDecodeError:
            pass
    url = npm_packument_url(name) if ecosystem == "npm" else pypi_url(name)
    try:
        doc = http_get_json(url)
        wrapper = {
            "_fetch_ok": True,
            "_url": url,
            "_fetched_at": datetime.now(timezone.utc).isoformat(),
            "doc": doc,
        }
    except urllib.error.HTTPError as exc:
        wrapper = {
            "_fetch_ok": False,
            "_url": url,
            "_fetched_at": datetime.now(timezone.utc).isoformat(),
            "_error": f"HTTP {exc.code} {exc.reason}",
            "doc": None,
        }
    except Exception as exc:
        wrapper = {
            "_fetch_ok": False,
            "_url": url,
            "_fetched_at": datetime.now(timezone.utc).isoformat(),
            "_error": f"{type(exc).__name__}: {exc}",
            "doc": None,
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(wrapper), encoding="utf-8")
    return wrapper


def row_from_npm(pid: str, wanted_vid_version: str, wrapper: dict) -> dict:
    """Keep vid = IOC malicious version even when npm has unpublished it.

    Hooks/scripts are read from that version's manifest when present. If the
    version is gone, we still emit the IOC vid, take maintainers/repo from the
    live packument, and set vid_source=ioc_vid_unpublished. We do not copy
    install hooks from latest — that would be the wrong version's predicate.
    """
    name = pid.split(":", 1)[1]
    doc = wrapper.get("doc") or {}
    versions = doc.get("versions") or {}
    times = doc.get("time") or {}
    vdoc = versions.get(wanted_vid_version)
    if vdoc is not None:
        hooks = install_hooks_of(vdoc)
        return {
            "pid": pid,
            "vid": f"npm:{name}@{wanted_vid_version}",
            "has_install_script": bool(hooks),
            "install_hooks": hooks,
            "maintainer_logins": maintainer_logins(doc, vdoc),
            "repo_url": normalize_repo(vdoc.get("repository") or doc.get("repository")),
            "published_at": parse_utc_epoch(times.get(wanted_vid_version) or vdoc.get("_time")),
            "vid_source": "ioc_vid",
            "requested_version": wanted_vid_version,
            "fetch_ok": True,
            "fetch_error": None,
        }
    latest = (doc.get("dist-tags") or {}).get("latest")
    latest_doc = versions.get(latest) if latest else {}
    return {
        "pid": pid,
        "vid": f"npm:{name}@{wanted_vid_version}",
        "has_install_script": False,
        "install_hooks": [],
        "maintainer_logins": maintainer_logins(doc, latest_doc or {}),
        "repo_url": normalize_repo(
            (latest_doc or {}).get("repository") or doc.get("repository")
        ),
        "published_at": parse_utc_epoch(times.get(wanted_vid_version)),
        "vid_source": "ioc_vid_unpublished" if wrapper.get("_fetch_ok") else "missing",
        "live_latest": latest,
        "requested_version": wanted_vid_version,
        "fetch_ok": bool(wrapper.get("_fetch_ok")),
        "fetch_error": wrapper.get("_error"),
    }


def row_from_pypi(pid: str, wanted: str, wrapper: dict) -> dict:
    name = pid.split(":", 1)[1]
    doc = wrapper.get("doc") or {}
    releases = doc.get("releases") or {}
    info = doc.get("info") or {}
    version = wanted if wanted in releases else info.get("version") or wanted
    source = "ioc_vid" if wanted in releases else "packument_latest"
    files = releases.get(version) or []
    published = None
    if files:
        published = parse_utc_epoch(files[0].get("upload_time_iso_8601") or files[0].get("upload_time"))
    project_urls = info.get("project_urls") or {}
    repo = normalize_repo(
        project_urls.get("Source")
        or project_urls.get("Repository")
        or project_urls.get("Homepage")
        or info.get("home_page")
    )
    requires = info.get("requires_dist")  # unused; PyPI has no install hooks analogue
    return {
        "pid": pid,
        "vid": f"pypi:{name}@{version}",
        "has_install_script": False,
        "install_hooks": [],
        "maintainer_logins": [info.get("author")] if info.get("author") else [],
        "repo_url": repo,
        "published_at": published,
        "vid_source": source,
        "requested_version": wanted,
        "fetch_ok": bool(wrapper.get("_fetch_ok")),
        "fetch_error": wrapper.get("_error"),
        "pypi_note": (
            "PyPI has no npm lifecycle hooks; has_install_script is always false. "
            "The May 2026 payload ran on import, not on pip install."
        ),
    }


def load_ioc_records() -> list[dict]:
    if not IOC_JSON.exists():
        sys.exit(f"missing {IOC_JSON}; run scripts/ioc_reconcile.py first")
    data = json.loads(IOC_JSON.read_text(encoding="utf-8"))
    return data["records"]


def write_parquet(rows: list[dict]) -> None:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        print("pyarrow not available; skipped packuments.parquet")
        return
    PARQUET.parent.mkdir(parents=True, exist_ok=True)
    table = pa.table(
        {
            "pid": [r["pid"] for r in rows],
            "vid": [r["vid"] for r in rows],
            "has_install_script": [bool(r["has_install_script"]) for r in rows],
            "install_hooks": [list(r["install_hooks"]) for r in rows],
            "maintainer_logins": [list(r["maintainer_logins"]) for r in rows],
            "repo_url": [r.get("repo_url") for r in rows],
            "published_at": pa.array([r.get("published_at") for r in rows], type=pa.int64()),
        }
    )
    pq.write_table(table, PARQUET)
    print(f"wrote {PARQUET} ({len(rows)} rows)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="refetch even if cached")
    parser.add_argument("--seed-only", action="store_true")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS)
    args = parser.parse_args()
    workers = min(max(args.workers, 1), 4)

    records = load_ioc_records()
    if args.seed_only:
        records = [r for r in records if r["split"] == "seed"]

    # Unique packages to fetch; then emit one row per IOC vid.
    packages = sorted({(r["ecosystem"], r["pid"].split(":", 1)[1]) for r in records})
    CACHE.mkdir(parents=True, exist_ok=True)

    fetched: dict[tuple[str, str], dict] = {}
    print(f"fetching {len(packages)} packuments with workers={workers}")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {
            pool.submit(load_or_fetch, eco, name, args.force): (eco, name)
            for eco, name in packages
        }
        done = 0
        for fut in as_completed(futs):
            eco, name = futs[fut]
            try:
                fetched[(eco, name)] = fut.result()
            except Exception as exc:
                fetched[(eco, name)] = {
                    "_fetch_ok": False,
                    "_error": f"{type(exc).__name__}: {exc}",
                    "doc": None,
                }
            done += 1
            status = "ok" if fetched[(eco, name)].get("_fetch_ok") else "fail"
            print(f"  [{done}/{len(packages)}] {status} {eco}:{name}")
            time.sleep(0.05)

    rows = []
    for rec in records:
        eco = rec["ecosystem"]
        name = rec["pid"].split(":", 1)[1]
        version = rec["vid"].rsplit("@", 1)[-1]
        wrapper = fetched.get((eco, name), {"_fetch_ok": False, "doc": None})
        if eco == "npm":
            rows.append(row_from_npm(rec["pid"], version, wrapper))
        elif eco == "pypi":
            rows.append(row_from_pypi(rec["pid"], version, wrapper))
        else:
            continue

    seed_rows = []
    seed_pids = {r["pid"] for r in records if r.get("split") == "seed"} or {
        r["pid"] for r in load_ioc_records() if r["split"] == "seed"
    }
    # Always emit seed artifact from seed IOC vids even if this run was all-packages.
    ioc_all = json.loads(IOC_JSON.read_text(encoding="utf-8"))["records"]
    seed_ioc = [r for r in ioc_all if r["split"] == "seed"]
    for rec in seed_ioc:
        name = rec["pid"].split(":", 1)[1]
        version = rec["vid"].rsplit("@", 1)[-1]
        wrapper = fetched.get(("npm", name))
        if wrapper is None:
            wrapper = load_or_fetch("npm", name, args.force)
        seed_rows.append(row_from_npm(rec["pid"], version, wrapper))

    contract_seed = [
        {
            "pid": r["pid"],
            "vid": r["vid"],
            "has_install_script": r["has_install_script"],
            "install_hooks": r["install_hooks"],
            "maintainer_logins": r["maintainer_logins"],
            "repo_url": r["repo_url"],
            "published_at": r["published_at"],
            "vid_source": r.get("vid_source"),
            "requested_version": r.get("requested_version"),
            "live_latest": r.get("live_latest"),
            "fetch_ok": r.get("fetch_ok"),
            "fetch_error": r.get("fetch_error"),
        }
        for r in seed_rows
    ]
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    n_hooks = sum(1 for r in seed_rows if r["has_install_script"])
    n_unpublished = sum(1 for r in seed_rows if r.get("vid_source") == "ioc_vid_unpublished")
    n_missing = sum(1 for r in seed_rows if r.get("vid_source") == "missing")
    SEED_OUT.write_text(
        json.dumps(
            {
                "contract": (
                    "pid, vid, has_install_script, install_hooks, "
                    "maintainer_logins[], repo_url, published_at"
                ),
                "note": (
                    "vid is always the IOC malicious version. npm unpublished those "
                    "tarballs the evening of May 11, so vid_source=ioc_vid_unpublished "
                    "means the version document is gone from the live packument. "
                    "Install hooks are NOT copied from latest (wrong version). "
                    "TanStack host manifests did not gain preinstall/install/postinstall/"
                    "prepare — the prepare hook lived on the git optionalDependency "
                    "@tanstack/setup. Seed has_install_script=false is therefore the "
                    "correct property on the package itself, both then and now."
                ),
                "seed_rows": len(contract_seed),
                "seed_with_install_hooks": n_hooks,
                "seed_unpublished_from_registry": n_unpublished,
                "seed_fetch_missing": n_missing,
                "records": contract_seed,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    write_parquet(rows)
    print(f"wrote {SEED_OUT}")
    print(
        f"packuments: {len(packages)} fetched, {len(rows)} ioc rows, "
        f"seed_hooks={n_hooks}/{len(seed_rows)}, "
        f"seed_unpublished={n_unpublished}/{len(seed_rows)}"
    )


if __name__ == "__main__":
    main()
