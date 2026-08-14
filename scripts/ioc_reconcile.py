#!/usr/bin/env python3
"""Reconcile Mini Shai-Hulud / TanStack IOC listings into the W3 contract.

Reads the checked-in mapping `artifacts/ioc_sources.json` and writes:
  artifacts/ioc.json
  artifacts/ioc.md
  artifacts/seed_packages.txt
  data/truth/ioc.parquet   (gitignored)

Rebuild the mapping from vendor TSVs + GHSA raw JSON:
  python scripts/ioc_reconcile.py --build-sources
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

ARTIFACTS = ROOT / "artifacts"
DATA_TRUTH = ROOT / "data" / "truth"
RAW = DATA_TRUTH / "raw"
SOURCES_PATH = ARTIFACTS / "ioc_sources.json"
IOC_JSON = ARTIFACTS / "ioc.json"
IOC_MD = ARTIFACTS / "ioc.md"
SEED_TXT = ARTIFACTS / "seed_packages.txt"
IOC_PARQUET = DATA_TRUTH / "ioc.parquet"

INSTALL_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

# Vendors that published a (claimed) complete package table. Missing from one
# of these, while present in another, is a coverage disagreement.
FULL_TABLE_SOURCES = ("wiz", "aikido", "safedep")


def parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def to_epoch(dt: datetime | None) -> int | None:
    if dt is None:
        return None
    return int(dt.timestamp())


def pid_of(ecosystem: str, name: str) -> str:
    return f"{ecosystem}:{name}"


def vid_of(ecosystem: str, name: str, version: str) -> str:
    return f"{ecosystem}:{name}@{version}"


def version_key(version: str) -> tuple:
    parts = []
    for token in version.split("."):
        num = ""
        rest = ""
        for ch in token:
            if ch.isdigit() and not rest:
                num += ch
            else:
                rest += ch
        parts.append((int(num) if num else 0, rest))
    return tuple(parts)


def load_ghsa_listings() -> list[dict]:
    path = RAW / "osv_GHSA-g7cv-rxg3-hmpx.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    merged: dict[tuple[str, str], set[str]] = defaultdict(set)
    for item in data.get("affected", []):
        pkg = item.get("package") or {}
        eco = (pkg.get("ecosystem") or "npm").lower()
        if eco == "npm":
            eco = "npm"
        name = pkg.get("name")
        if not name:
            continue
        for ver in item.get("versions") or []:
            merged[(eco, name)].add(ver)
    rows = []
    for (eco, name), versions in sorted(merged.items()):
        rows.append(
            {
                "ecosystem": eco,
                "name": name,
                "versions": sorted(versions, key=version_key),
            }
        )
    return rows


def build_sources_json() -> dict:
    import ioc_listings as listings

    catalog = json.loads(json.dumps(listings.SOURCE_CATALOG))
    parsed = listings.parse_all()
    ghsa_rows = load_ghsa_listings()
    if ghsa_rows:
        parsed["ghsa"] = ghsa_rows
        parsed["osv"] = ghsa_rows
        parsed["tanstack_postmortem"] = ghsa_rows
    else:
        catalog["ghsa"]["notes"] += " RAW JSON missing at build time; GHSA rows not expanded."
        catalog["osv"]["notes"] += " RAW JSON missing at build time."
        catalog["tanstack_postmortem"]["notes"] += (
            " Could not expand the 42-package table without GHSA raw JSON."
        )

    payload = {
        "campaign": "Mini Shai-Hulud / TanStack npm worm",
        "incident_date_utc": "2026-05-11",
        "seed_policy": {
            "description": (
                "seed = the 42 @tanstack/* packages published in the 19:20–19:26 UTC "
                "burst. validation = every other confirmed name, including PyPI."
            ),
            "namespace_prefix": "@tanstack/",
            "ecosystem": "npm",
            "first_batch_utc": listings.SEED_BATCH1_UTC,
            "second_batch_utc": listings.SEED_BATCH2_UTC,
            "source": "https://tanstack.com/blog/npm-supply-chain-compromise-postmortem",
        },
        "source_catalog": catalog,
        "listings": parsed,
        "built_from": {
            "ghsa_raw": str(RAW / "osv_GHSA-g7cv-rxg3-hmpx.json"),
            "ghsa_packages": len(ghsa_rows),
        },
    }
    return payload


def is_seed(ecosystem: str, name: str, seed_policy: dict) -> bool:
    return (
        ecosystem == seed_policy.get("ecosystem", "npm")
        and name.startswith(seed_policy.get("namespace_prefix", "@tanstack/"))
    )


def confidence_score(n_version_sources: int, n_package_sources: int) -> float:
    if n_version_sources >= 4:
        return 0.95
    if n_version_sources == 3:
        return 0.9
    if n_version_sources == 2:
        return 0.75
    if n_version_sources == 1 and n_package_sources >= 3:
        return 0.6
    if n_version_sources == 1:
        return 0.45
    return 0.3


def reconcile(mapping: dict) -> dict:
    catalog = mapping["source_catalog"]
    seed_policy = mapping["seed_policy"]
    batch1 = parse_utc(seed_policy["first_batch_utc"])
    batch2 = parse_utc(seed_policy["second_batch_utc"])

    # pkg_key -> source_id -> set[version]  (empty set = name-only listing)
    pkg_sources: dict[tuple[str, str], dict[str, set[str]]] = defaultdict(dict)
    for source_id, rows in mapping["listings"].items():
        for row in rows:
            eco, name = row["ecosystem"], row["name"]
            vers = set(row.get("versions") or [])
            existing = pkg_sources[(eco, name)].get(source_id)
            if existing is None:
                pkg_sources[(eco, name)][source_id] = set(vers)
            else:
                existing.update(vers)

    records = []
    disagreements = []
    for (eco, name), by_source in sorted(pkg_sources.items()):
        version_sets = {
            sid: vers
            for sid, vers in by_source.items()
            if vers  # ignore name-only for set comparison
        }
        union_versions: set[str] = set()
        for vers in version_sets.values():
            union_versions |= vers
        if not union_versions:
            # Name-only: keep a row with vid using a placeholder? Contract wants vid.
            # Skip fabricating a version. Record in disagreements notes only.
            disagreements.append(
                {
                    "pid": pid_of(eco, name),
                    "kind": "name_only_no_version",
                    "sources": sorted(by_source),
                }
            )
            continue

        unique_sets = {frozenset(v) for v in version_sets.values()}
        version_disagree = len(unique_sets) > 1
        present_full = [s for s in FULL_TABLE_SOURCES if s in by_source]
        missing_full = [s for s in FULL_TABLE_SOURCES if s not in by_source]
        coverage_disagree = bool(present_full) and bool(missing_full)
        if version_disagree or coverage_disagree:
            disagreements.append(
                {
                    "pid": pid_of(eco, name),
                    "kind": "version_set" if version_disagree else "coverage",
                    "version_disagree": version_disagree,
                    "coverage_disagree": coverage_disagree,
                    "missing_full_table_sources": missing_full,
                    "version_sets": {sid: sorted(v, key=version_key) for sid, v in version_sets.items()},
                    "sources": sorted(by_source),
                }
            )

        seed = is_seed(eco, name, seed_policy)
        ordered = sorted(union_versions, key=version_key)
        for idx, ver in enumerate(ordered):
            version_listers = [
                sid for sid, vers in by_source.items() if (not vers) or (ver in vers)
            ]
            exact_listers = [sid for sid, vers in by_source.items() if ver in vers]
            # Name-only sources support the package but not a specific vid.
            name_only = [sid for sid, vers in by_source.items() if not vers]

            if seed and batch1 and batch2:
                first_seen = batch1 if idx == 0 else batch2
                first_seen_note = (
                    "TanStack postmortem: first-version batch 19:20:39, "
                    "second-version batch 19:26:14 UTC."
                )
            else:
                times = []
                for sid in exact_listers or version_listers:
                    dt = parse_utc(catalog.get(sid, {}).get("published_utc"))
                    if dt:
                        times.append((dt, sid))
                times.sort()
                if times:
                    first_seen = times[0][0]
                    first_seen_note = (
                        f"Earliest citing source published_utc: {times[0][1]} "
                        f"({times[0][0].isoformat().replace('+00:00', 'Z')}). "
                        "Not the npm/PyPI publish time — vendors did not give one."
                    )
                else:
                    first_seen = None
                    first_seen_note = (
                        "No source published_utc available; first_seen_utc left null."
                    )

            sources_urls = []
            for sid in sorted(set(exact_listers + name_only)):
                url = catalog.get(sid, {}).get("url")
                if url:
                    sources_urls.append(url)
            # Always include the source id URL even if duplicates
            sources_urls = list(dict.fromkeys(sources_urls))

            records.append(
                {
                    "pid": pid_of(eco, name),
                    "vid": vid_of(eco, name, ver),
                    "ecosystem": eco,
                    "name": name,
                    "version": ver,
                    "first_seen_utc": to_epoch(first_seen),
                    "first_seen_note": first_seen_note,
                    "sources": sources_urls,
                    "source_ids": sorted(set(exact_listers + name_only)),
                    "confidence": confidence_score(len(exact_listers), len(by_source)),
                    "split": "seed" if seed else "validation",
                }
            )

    seed_pkgs = sorted({r["pid"] for r in records if r["split"] == "seed"})
    val_pkgs = sorted({r["pid"] for r in records if r["split"] == "validation"})
    pypi_pkgs = sorted({r["pid"] for r in records if r["ecosystem"] == "pypi"})

    pkg_disagree = [d for d in disagreements if d["kind"] != "name_only_no_version"]
    summary = {
        "seed_packages": len(seed_pkgs),
        "seed_versions": sum(1 for r in records if r["split"] == "seed"),
        "validation_packages": len(val_pkgs),
        "validation_versions": sum(1 for r in records if r["split"] == "validation"),
        "total_packages": len(seed_pkgs) + len(val_pkgs),
        "total_versions": len(records),
        "pypi_packages": len(pypi_pkgs),
        "pypi_pids": pypi_pkgs,
        "disagreement_packages": len(pkg_disagree),
        "name_only_unversioned": sum(1 for d in disagreements if d["kind"] == "name_only_no_version"),
        "target_seed": 42,
        "target_validation": "170+",
        "honest_note": (
            "Aikido claimed 169 npm names (no PyPI). SafeDep published 170 npm + 2 PyPI "
            "= 172 total. Vendor '170+' figures are end-of-day totals including the 42 "
            "seed packages, not a 170-row validation split. Union here is 180 packages "
            "(42 seed + 138 validation) and 415 versions (84 seed + 331 validation). "
            "Wiz-only extras kept per union policy: @cap-js/*, intercom-client, lightning, "
            "mbt, and unscoped npm mistralai/guardrails-ai (those two 404 on npm; they "
            "exist on PyPI)."
        ),
    }
    return {
        "summary": summary,
        "records": records,
        "disagreements": disagreements,
        "seed_packages": seed_pkgs,
        "validation_packages": val_pkgs,
    }


def write_ioc_json(result: dict, mapping: dict) -> None:
    rows = []
    for r in result["records"]:
        rows.append(
            {
                "pid": r["pid"],
                "vid": r["vid"],
                "ecosystem": r["ecosystem"],
                "first_seen_utc": r["first_seen_utc"],
                "sources": r["sources"],
                "confidence": r["confidence"],
                "split": r["split"],
            }
        )
    payload = {
        "contract": (
            "pid, vid, ecosystem, first_seen_utc, sources[], confidence, split "
            "where split in {seed, validation}; timestamps are epoch seconds UTC"
        ),
        "summary": result["summary"],
        "source_catalog": {
            sid: {"url": meta["url"], "published_utc": meta.get("published_utc")}
            for sid, meta in mapping["source_catalog"].items()
        },
        "records": rows,
        "disagreements": result["disagreements"],
    }
    IOC_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_seed_txt(result: dict) -> None:
    names = []
    for pid in result["seed_packages"]:
        names.append(pid.split(":", 1)[1])
    SEED_TXT.write_text("\n".join(names) + "\n", encoding="utf-8")


def write_ioc_md(result: dict, mapping: dict) -> None:
    s = result["summary"]
    lines = [
        "# Reconciled IOC set — Mini Shai-Hulud / TanStack (May 11 2026)",
        "",
        "Union of public vendor listings. A package one vendor lists and another",
        "omits is **kept**, with the disagreement recorded. Do not treat this as",
        "npm's unpublished-tarball ground truth; several malicious versions were",
        "removed from the registry the same evening.",
        "",
        "## Counts",
        "",
        f"- **Seed packages:** {s['seed_packages']} / 42 target "
        f"({s['seed_versions']} malicious versions)",
        f"- **Validation packages:** {s['validation_packages']} "
        f"(target was 170+; see honesty note) "
        f"({s['validation_versions']} malicious versions)",
        f"- **Source disagreements:** {s['disagreement_packages']} packages",
        f"- **PyPI packages:** {s['pypi_packages']} — {', '.join(s['pypi_pids']) or 'none'}",
        "",
        "### Honesty note",
        "",
        s["honest_note"],
        "",
        "Seed timestamps are the two publish batches from TanStack's postmortem",
        f"(`{mapping['seed_policy']['first_batch_utc']}` and "
        f"`{mapping['seed_policy']['second_batch_utc']}`). Validation timestamps",
        "are the **earliest citing article `published_utc`**, not the registry",
        "publish time — vendors rarely give one. `first_seen_utc` is null only",
        "when no source timestamp exists; we did not guess 19:26 for later victims.",
        "",
        "## Sources",
        "",
        "| id | published_utc | url |",
        "|---|---|---|",
    ]
    for sid, meta in mapping["source_catalog"].items():
        lines.append(
            f"| `{sid}` | {meta.get('published_utc', '')} | {meta['url']} |"
        )
    lines += [
        "",
        "## Disagreements (package-level)",
        "",
        "Coverage = listed by at least one of Wiz / Aikido / SafeDep but not all three.",
        "Version-set = those sources that gave versions do not agree on the set.",
        "",
        "| pid | kind | missing full-table sources |",
        "|---|---|---|",
    ]
    for d in result["disagreements"]:
        if d["kind"] == "name_only_no_version":
            continue
        missing = ", ".join(d.get("missing_full_table_sources") or []) or "—"
        kind = []
        if d.get("version_disagree"):
            kind.append("version_set")
        if d.get("coverage_disagree"):
            kind.append("coverage")
        lines.append(f"| `{d['pid']}` | {'+'.join(kind)} | {missing} |")

    lines += [
        "",
        "## Seed (`split=seed`)",
        "",
        "| pid | vid | first_seen_utc | confidence | source ids |",
        "|---|---|---|---|---|",
    ]
    for r in result["records"]:
        if r["split"] != "seed":
            continue
        src = ", ".join(r["source_ids"])
        lines.append(
            f"| `{r['pid']}` | `{r['vid']}` | {r['first_seen_utc']} | "
            f"{r['confidence']:.2f} | {src} |"
        )

    lines += [
        "",
        "### Seed timestamp note",
        "",
        result["records"][0]["first_seen_note"] if result["records"] else "",
        "",
        "## Validation (`split=validation`)",
        "",
        "| pid | vid | first_seen_utc | confidence | source ids | first_seen note |",
        "|---|---|---|---|---|---|",
    ]
    for r in result["records"]:
        if r["split"] != "validation":
            continue
        src = ", ".join(r["source_ids"])
        note = r["first_seen_note"].replace("|", "/")
        fs = r["first_seen_utc"] if r["first_seen_utc"] is not None else "null"
        lines.append(
            f"| `{r['pid']}` | `{r['vid']}` | {fs} | {r['confidence']:.2f} | {src} | {note} |"
        )
    lines.append("")
    IOC_MD.write_text("\n".join(lines), encoding="utf-8")


def write_parquet(result: dict) -> None:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        print("pyarrow not available; skipped data/truth/ioc.parquet")
        return
    DATA_TRUTH.mkdir(parents=True, exist_ok=True)
    table = pa.table(
        {
            "pid": [r["pid"] for r in result["records"]],
            "vid": [r["vid"] for r in result["records"]],
            "ecosystem": [r["ecosystem"] for r in result["records"]],
            "first_seen_utc": pa.array(
                [r["first_seen_utc"] for r in result["records"]], type=pa.int64()
            ),
            "sources": [r["sources"] for r in result["records"]],
            "confidence": [r["confidence"] for r in result["records"]],
            "split": [r["split"] for r in result["records"]],
        }
    )
    pq.write_table(table, IOC_PARQUET)
    print(f"wrote {IOC_PARQUET}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--build-sources",
        action="store_true",
        help="Rebuild artifacts/ioc_sources.json from scripts/ioc_listings.py + GHSA raw",
    )
    args = parser.parse_args()

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    DATA_TRUTH.mkdir(parents=True, exist_ok=True)

    if args.build_sources or not SOURCES_PATH.exists():
        mapping = build_sources_json()
        SOURCES_PATH.write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {SOURCES_PATH}")
    else:
        mapping = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))

    result = reconcile(mapping)
    write_ioc_json(result, mapping)
    write_ioc_md(result, mapping)
    write_seed_txt(result)
    write_parquet(result)

    s = result["summary"]
    print(
        f"seed={s['seed_packages']} pkgs / {s['seed_versions']} vids  "
        f"validation={s['validation_packages']} pkgs / {s['validation_versions']} vids  "
        f"disagreements={s['disagreement_packages']}  "
        f"pypi={s['pypi_packages']}"
    )
    print(f"wrote {IOC_JSON}")
    print(f"wrote {IOC_MD}")
    print(f"wrote {SEED_TXT}")


if __name__ == "__main__":
    main()
