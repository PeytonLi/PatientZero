#!/usr/bin/env python3
"""Load data/graph Parquet into HydraDB. One writer, UNWIND batch 1000.

Skips when the demo sentinel package is already present so a second pass
does not duplicate CREATE edges. Wipe the HydraDB volume (or delete the
store) to reload.

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
from patient_zero.ids import hydra_id
from patient_zero.loader import load_from_dir, load_plan, package_exists, read_checkpoint
from patient_zero.paths import LOAD_SENTINEL_PID, graph_dir, repo_root

ROOT = repo_root()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--graph-dir", type=Path, default=graph_dir())
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
            exists = package_exists(session, hydra_id(LOAD_SENTINEL_PID))
            plan = load_plan(sentinel_exists=exists, checkpoint=read_checkpoint(args.checkpoint))
            if plan == "skip":
                summary = {
                    "status": "skipped",
                    "reason": "sentinel already present; refusing to CREATE duplicate edges",
                    "sentinel": LOAD_SENTINEL_PID,
                    "checkpoint": str(args.checkpoint),
                }
                print(json.dumps(summary, indent=2))
                return 0
            if plan == "reset" and args.checkpoint.is_file():
                args.checkpoint.unlink()
            summary = load_from_dir(
                session,
                args.graph_dir,
                batch_size=args.batch_size,
                checkpoint_path=args.checkpoint,
            )
            summary["status"] = "loaded"
            summary["plan"] = plan
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
