"""Lockfile PINS. Hand-authored lockfiles would make Leg 1 a prop."""

import json
from pathlib import Path

from patient_zero.assemble import SENTINEL_VALID_TO
from patient_zero.lockfiles import parse_npm_lockfile, pins_from_lockfile


LOCK_V3 = {
    "name": "storefront",
    "lockfileVersion": 3,
    "packages": {
        "": {"name": "storefront", "version": "1.0.0"},
        "node_modules/@tanstack/react-query": {
            "version": "5.90.2",
            "resolved": "https://registry.npmjs.org/@tanstack/react-query/-/react-query-5.90.2.tgz",
        },
        "node_modules/@tanstack/query-core": {
            "version": "5.90.2",
        },
        "node_modules/left-pad": {"version": "1.3.0"},
    },
}


def test_parse_npm_lockfile_v3_emits_pins_for_every_resolved_package():
    rows = parse_npm_lockfile(LOCK_V3, sid="svc:storefront", lockfile_at=1778520000)
    vids = {row["dst_vid"] for row in rows}
    assert "npm:@tanstack/react-query@5.90.2" in vids
    assert "npm:@tanstack/query-core@5.90.2" in vids
    assert "npm:left-pad@1.3.0" in vids
    assert all(row["sid"] == "svc:storefront" for row in rows)
    assert all(row["valid_to"] == SENTINEL_VALID_TO for row in rows)
    assert all(row["lockfile_at"] == 1778520000 for row in rows)
    assert all(row["valid_from"] == 1778520000 for row in rows)


def test_parse_npm_lockfile_skips_root_package_entry():
    rows = parse_npm_lockfile(LOCK_V3, sid="svc:storefront", lockfile_at=1)
    assert not any(row["dst_vid"].endswith("@1.0.0") and "storefront" in row["dst_vid"] for row in rows)


def test_pins_from_lockfile_reads_package_lock_json(tmp_path: Path):
    path = tmp_path / "package-lock.json"
    path.write_text(json.dumps(LOCK_V3), encoding="utf-8")
    service, pins = pins_from_lockfile(
        path, sid="svc:storefront", name="storefront", source_repo="github:acme/storefront", lockfile_at=10
    )
    assert service == {
        "sid": "svc:storefront",
        "name": "storefront",
        "source_repo": "github:acme/storefront",
    }
    assert len(pins) == 3
