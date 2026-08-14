"""Fetch machine-readable GHSA/OSV records into data/truth/raw/ (gitignored)."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "truth" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

URLS = {
    "osv_GHSA-g7cv-rxg3-hmpx.json": "https://api.osv.dev/v1/vulns/GHSA-g7cv-rxg3-hmpx",
    "osv_CVE-2026-45321.json": "https://api.osv.dev/v1/vulns/CVE-2026-45321",
    "github_GHSA-g7cv-rxg3-hmpx.json": "https://api.github.com/advisories/GHSA-g7cv-rxg3-hmpx",
    "osv_MAL-2026-3465.json": "https://api.osv.dev/v1/vulns/MAL-2026-3465",
    "osv_MAL-2026-3432.json": "https://api.osv.dev/v1/vulns/MAL-2026-3432",
}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "PatientZero-W3/0.1 (research IOC reconcile; contact: local hackathon)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def main() -> None:
    for name, url in URLS.items():
        dest = RAW / name
        try:
            body = fetch(url)
            dest.write_bytes(body)
            print(f"OK {name} {len(body)} bytes")
        except Exception as exc:
            print(f"FAIL {name}: {type(exc).__name__}: {exc}")
            dest.with_suffix(dest.suffix + ".error").write_text(
                f"{url}\n{type(exc).__name__}: {exc}\n", encoding="utf-8"
            )

    ghsa_path = RAW / "osv_GHSA-g7cv-rxg3-hmpx.json"
    if ghsa_path.exists():
        data = json.loads(ghsa_path.read_text(encoding="utf-8"))
        rows = []
        for a in data.get("affected", []):
            pkg = a.get("package") or {}
            rows.append(
                {
                    "ecosystem": pkg.get("ecosystem"),
                    "name": pkg.get("name"),
                    "purl": pkg.get("purl"),
                    "versions": a.get("versions") or [],
                }
            )
        summary = RAW / "osv_GHSA-g7cv-rxg3-hmpx.packages.json"
        summary.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        print(f"GHSA affected packages: {len(rows)}")
        for r in rows:
            print(f"  {r['ecosystem']} {r['name']} {r['versions']}")


if __name__ == "__main__":
    main()
