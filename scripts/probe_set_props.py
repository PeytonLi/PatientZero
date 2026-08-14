#!/usr/bin/env python3
"""Probe whether HydraDB 0.1.0 accepts SET of extra node properties.

MEASURED.md: UNWIND node patterns only permit `id`. W2 needs to know if a
follow-up SET can attach vid/name/etc. This is a tiny write; run after the
spike, with a disjoint id range.

Usage:
    python scripts/probe_set_props.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import neo4j

ROOT = Path(__file__).resolve().parents[1]
TOKEN = (ROOT / "hydradb-data" / "auth-token").read_text(encoding="utf-8").strip()
URI = "bolt://127.0.0.1:7687"
OFFSET = 9_000_000_000


def try_query(session, label, query, **params):
    t0 = time.perf_counter()
    try:
        session.run(query, **params).consume()
        ok, err = True, None
    except Exception as exc:
        ok, err = False, f"{type(exc).__name__}: {exc}"
    elapsed = round(time.perf_counter() - t0, 4)
    rec = {"probe": label, "ok": ok, "seconds": elapsed, "error": err, "cypher": query}
    print(json.dumps(rec))
    return rec


def main() -> None:
    nid = OFFSET + int(time.time()) % 1000
    driver = neo4j.GraphDatabase.driver(URI, auth=neo4j.basic_auth("neo4j", TOKEN))
    out = []
    try:
        with driver.session() as s:
            out.append(try_query(
                s, "merge_id_set_label",
                "UNWIND $rows AS row MERGE (a {id: row.id}) SET a:Version",
                rows=[{"id": nid}],
            ))
            out.append(try_query(
                s, "unwind_set_string_prop",
                "UNWIND $rows AS row MATCH (a:Version {id: row.id}) SET a.name = row.name",
                rows=[{"id": nid, "name": "probe"}],
            ))
            out.append(try_query(
                s, "unwind_set_two_props",
                "UNWIND $rows AS row MATCH (a:Version {id: row.id}) SET a.name = row.name, a.ecosystem = row.eco",
                rows=[{"id": nid, "name": "probe", "eco": "npm"}],
            ))
            out.append(try_query(
                s, "match_set_one_prop",
                "MATCH (a:Version {id: $id}) SET a.name = $name",
                id=nid, name="probe2",
            ))
            out.append(try_query(
                s, "unwind_set_label_and_prop",
                "UNWIND $rows AS row MERGE (a {id: row.id}) SET a:Package SET a.name = row.name",
                rows=[{"id": nid + 1, "name": "pkg"}],
            ))
            t0 = time.perf_counter()
            try:
                rec = s.run(
                    "MATCH (a:Version {id: $id}) RETURN a.name AS name",
                    id=nid,
                ).single()
                name = rec["name"] if rec else None
                err = None
            except Exception as exc:
                name, err = None, f"{type(exc).__name__}: {exc}"
            out.append({
                "probe": "read_back_name",
                "ok": err is None,
                "seconds": round(time.perf_counter() - t0, 4),
                "name": name,
                "error": err,
            })
            print(json.dumps(out[-1]))
    finally:
        driver.close()
    (ROOT / "runs").mkdir(exist_ok=True)
    (ROOT / "runs" / "set_props.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
