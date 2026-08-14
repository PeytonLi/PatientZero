#!/usr/bin/env python3
"""Load data/graph Parquet into HydraDB. One writer, UNWIND batch 1000.

    python scripts/load.py
    python scripts/load.py --graph-dir data/graph --checkpoint runs/load-checkpoint.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from patient_zero.cypher import PRELIMINARY_BATCH_SIZE
from patient_zero.db import bolt_driver
from patient_zero.loader import load_from_dir

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--graph-dir", type=Path, default=ROOT / "data" / "graph")
    p.add_argument("--checkpoint", type=Path, default=ROOT / "runs" / "load-checkpoint.json")
    p.add_argument("--batch-size", type=int, default=PRELIMINARY_BATCH_SIZE)
    args = p.parse_args(argv)
    if not args.graph_dir.is_dir():
        print(f"missing graph dir: {args.graph_dir}", file=sys.stderr)
        return 1
    driver = bolt_driver()
    t0 = time.perf_counter()
    try:
        driver.verify_connectivity()
        with driver.session() as session:
            summary = load_from_dir(
                session,
                args.graph_dir,
                batch_size=args.batch_size,
                checkpoint_path=args.checkpoint,
            )
    finally:
        driver.close()
    summary["seconds"] = round(time.perf_counter() - t0, 3)
    if summary["seconds"] > 0:
        summary["elements_per_sec"] = round(
            (summary["nodes"] + summary["edges"]) / summary["seconds"], 1
        )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
