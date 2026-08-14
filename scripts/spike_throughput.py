#!/usr/bin/env python3
"""D0-1 throughput spike against HydraDB over Bolt.

Measures real sustained write throughput so W1 can size the ingest slice budget.
Every number this prints is wall-clock measured on the machine it runs on.

HydraDB 0.1.0 implements a narrow slice of openCypher. The exact accepted shapes
were discovered by probing the server's (unusually specific) error messages; see
docs/MEASURED.md "Supported Cypher subset". The queries below are the forms that
actually execute -- do not "clean them up" into idiomatic Cypher, it will not run.

Usage:
    python scripts/spike_throughput.py inline       --batch-size 1000 --rows 100000
    python scripts/spike_throughput.py match_create --batch-size 1000 --rows 100000
    python scripts/spike_throughput.py bitemporal   --batch-size 1000 --rows 100000
    python scripts/spike_throughput.py concurrency  --batch-size 1000 --rows 20000 --writers 4
    python scripts/spike_throughput.py sweep        --rows 100000
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import neo4j

# HydraDB 0.1.0 admission control: UNWIND batches larger than 1024 are rejected
# (client_query_batch_items). 1000 is the largest round size that actually runs.
MAX_UNWIND_BATCH = 1024

# --- the Cypher shapes HydraDB 0.1.0 actually accepts -------------------------
# Inline: nodes are created fresh per row. No labels, no relationship properties,
# and `id` is the only node property permitted in an UNWIND batch.
Q_INLINE = "UNWIND $rows AS row CREATE (a {id: row.src})-[:DEPENDS_ON]->(b {id: row.dst})"

# Node upsert. A label can only be attached via SET, never inline in the pattern.
Q_MERGE_NODES = "UNWIND $rows AS row MERGE (a {id: row.id}) SET a:Version"

# Realistic loader shape: both endpoints must already exist AND carry exactly one
# label, matched by `id`.
Q_MATCH_CREATE = (
    "UNWIND $rows AS row "
    "MATCH (a:Version {id: row.src}), (b:Version {id: row.dst}) "
    "CREATE (a)-[:DEPENDS_ON]->(b)"
)

# Same, carrying bitemporal properties. Relationship property maps MUST lead with
# an `id: row.<field>` entry or the planner rejects the statement.
Q_MATCH_CREATE_BITEMPORAL = (
    "UNWIND $rows AS row "
    "MATCH (a:Version {id: row.src}), (b:Version {id: row.dst}) "
    "CREATE (a)-[:DEPENDS_ON {id: row.eid, valid_from: row.vf, valid_to: row.vt}]->(b)"
)

# 3 hops, filtering every hop on the unindexed bitemporal predicate.
Q_TRAVERSE_3HOP = (
    "MATCH (a:Version)-[r1:DEPENDS_ON]->(b:Version)"
    "-[r2:DEPENDS_ON]->(c:Version)-[r3:DEPENDS_ON]->(d:Version) "
    "WHERE r1.valid_from <= $as_of AND $as_of < r1.valid_to "
    "AND r2.valid_from <= $as_of AND $as_of < r2.valid_to "
    "AND r3.valid_from <= $as_of AND $as_of < r3.valid_to "
    "RETURN count(*) AS c"
)


def connect(uri: str, token_file: str) -> neo4j.Driver:
    """Basic auth with any username works; bearer works too. See MEASURED.md."""
    token = open(token_file).read().strip()
    return neo4j.GraphDatabase.driver(uri, auth=neo4j.basic_auth("neo4j", token))


def batched(rows, size):
    it = iter(rows)
    while chunk := list(itertools.islice(it, size)):
        yield chunk


def edge_rows(n: int, offset: int, node_span: int, clock_span: int = 1000):
    """Synthetic DAG-ish edges. node_span keeps traversals branchy rather than a
    single long chain, so the 3-hop test does real fan-out work."""
    rnd = random.Random(1234 + offset)
    for i in range(n):
        src = offset + (i % node_span)
        dst = offset + ((i * 7 + 1) % node_span)
        vf = rnd.randrange(0, clock_span // 2)
        yield {
            "eid": offset + i,
            "src": src,
            "dst": dst if dst != src else src + 1,
            "vf": vf,
            "vt": vf + rnd.randrange(1, clock_span // 2),
        }


def run_batches(session, query, rows, batch_size):
    """Wall-clock time to push all rows through in batches of batch_size."""
    t0 = time.perf_counter()
    n = 0
    for chunk in batched(rows, batch_size):
        session.run(query, rows=chunk).consume()
        n += len(chunk)
    return time.perf_counter() - t0, n


def preload_nodes(driver, offset, node_span, batch_size):
    """match_create needs labeled endpoints to exist first. Timed separately so it
    never contaminates the relationship-create measurement."""
    nodes = [{"id": offset + i} for i in range(node_span)]
    with driver.session() as s:
        elapsed, _ = run_batches(s, Q_MERGE_NODES, nodes, batch_size)
    return elapsed


def report(mode, batch_size, rows, elapsed, elements_per_row, extra=None):
    result = {
        "mode": mode,
        "batch_size": batch_size,
        "rows": rows,
        "seconds": round(elapsed, 3),
        "edges_per_sec": round(rows / elapsed, 1),
        "elements_per_sec": round(rows * elements_per_row / elapsed, 1),
        "elements_per_row": elements_per_row,
    }
    if extra:
        result.update(extra)
    print(json.dumps(result))
    return result


def cmd_inline(driver, args, offset):
    """2 nodes + 1 relationship per row = 3 elements."""
    rows = list(edge_rows(args.rows, offset, node_span=args.rows))
    with driver.session() as s:
        elapsed, n = run_batches(s, Q_INLINE, rows, args.batch_size)
    return report("inline", args.batch_size, n, elapsed, 3)


def cmd_match_create(driver, args, offset, query=Q_MATCH_CREATE, mode="match_create"):
    """1 relationship per row; endpoint nodes are pre-created and not counted."""
    node_span = max(1000, args.rows // 10)
    preload = preload_nodes(driver, offset, node_span, args.batch_size)
    rows = list(edge_rows(args.rows, offset, node_span=node_span))
    with driver.session() as s:
        elapsed, n = run_batches(s, query, rows, args.batch_size)
    return report(mode, args.batch_size, n, elapsed, 1,
                  {"node_preload_seconds": round(preload, 3), "nodes_preloaded": node_span})


def cmd_bitemporal(driver, args, offset):
    """Load edges carrying valid_from/valid_to, then time the 3-hop predicate."""
    res = cmd_match_create(driver, args, offset, Q_MATCH_CREATE_BITEMPORAL, "bitemporal_load")
    latencies = []
    with driver.session() as s:
        for as_of in (100, 250, 500):
            t0 = time.perf_counter()
            rec = s.run(Q_TRAVERSE_3HOP, as_of=as_of).single()
            latencies.append((as_of, time.perf_counter() - t0, rec["c"]))
    for as_of, lat, count in latencies:
        print(json.dumps({"mode": "bitemporal_traverse_3hop", "as_of": as_of,
                          "seconds": round(lat, 3), "paths_matched": count}))
    return res


def cmd_concurrency(driver, args, offset):
    """Verify the vendor claim that concurrent writers do not raise throughput.
    Each writer gets its own session and a disjoint id range."""
    per_writer = args.rows // args.writers

    def writer(w):
        rows = list(edge_rows(per_writer, offset + w * 10_000_000, node_span=per_writer))
        with driver.session() as s:
            elapsed, n = run_batches(s, Q_INLINE, rows, args.batch_size)
        return elapsed, n

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.writers) as ex:
        results = list(ex.map(writer, range(args.writers)))
    wall = time.perf_counter() - t0
    total = sum(n for _, n in results)
    return report("concurrency", args.batch_size, total, wall, 3,
                  {"writers": args.writers,
                   "per_writer_seconds": [round(e, 3) for e, _ in results]})


def cmd_sweep(driver, args, offset):
    out = []
    for i, bs in enumerate((100, 1000, 1024)):
        args.batch_size = bs
        out.append(cmd_inline(driver, args, offset + (i + 1) * 50_000_000))
        out.append(cmd_match_create(driver, args, offset + (i + 5) * 50_000_000))
    return out


COMMANDS = {
    "inline": cmd_inline,
    "match_create": cmd_match_create,
    "bitemporal": cmd_bitemporal,
    "concurrency": cmd_concurrency,
    "sweep": cmd_sweep,
}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mode", choices=sorted(COMMANDS))
    p.add_argument("--batch-size", type=int, default=1000)
    p.add_argument("--rows", type=int, default=100_000)
    p.add_argument("--writers", type=int, default=4)
    p.add_argument("--uri", default=DEFAULT_URI)
    p.add_argument("--token-file", default=DEFAULT_TOKEN_FILE)
    p.add_argument("--id-offset", type=int, default=None,
                   help="disjoint id range so repeat runs never collide (default: clock-derived)")
    args = p.parse_args(argv)

    if args.batch_size > MAX_UNWIND_BATCH:
        p.error(f"HydraDB rejects UNWIND batches > {MAX_UNWIND_BATCH} (admission control)")
    offset = args.id_offset if args.id_offset is not None else (int(time.time()) % 100_000) * 10_000_000
    driver = connect(args.uri, args.token_file)
    try:
        COMMANDS[args.mode](driver, args, offset)
    finally:
        driver.close()


def demo():
    """Self-check: batching and row generation are the two bits of real logic."""
    assert [len(c) for c in batched(range(10), 3)] == [3, 3, 3, 1]
    assert [len(c) for c in batched(range(9), 3)] == [3, 3, 3]
    assert list(batched([], 5)) == []
    rows = list(edge_rows(50, offset=1000, node_span=10))
    assert len(rows) == 50
    assert all(r["src"] != r["dst"] for r in rows), "self-loops break traversal fan-out"
    assert all(r["vf"] < r["vt"] for r in rows), "valid_from must precede valid_to"
    assert all(1000 <= r["src"] < 1000 + 11 for r in rows), "ids must stay in the offset window"
    assert len({r["eid"] for r in rows}) == 50, "edge ids must be unique"
    print("demo ok")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    else:
        main()
