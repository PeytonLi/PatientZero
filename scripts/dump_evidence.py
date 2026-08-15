"""One live forecast + evidence dump. Do not invent numbers."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from patient_zero.db import bolt_driver  # noqa: E402
from patient_zero.engine import WORM_START, Engine  # noqa: E402

AS_OF = WORM_START + 360  # 19:26
K = 100


def main() -> None:
    driver = bolt_driver()

    def run(cypher: str, params: dict):
        with driver.session() as session:
            return [record["path"] for record in session.run(cypher, **params)]

    engine = Engine.live(run_paths=run)
    t0 = time.perf_counter()
    trust = engine.forecast(
        seeds=None, as_of=AS_OF, k=K, topology="trust", max_hops=3, limit=K
    )
    dep = engine.forecast(
        seeds=None, as_of=AS_OF, k=K, topology="dependency", max_hops=3, limit=K
    )
    evid = engine.evidence(k=K, as_of=AS_OF)
    lev = engine.leverage(k=5, max_hops=4, limit=K)
    idx = engine.index_case(observed=None, as_of=AS_OF, k=5, max_hops=4, limit=50)
    elapsed = round(time.perf_counter() - t0, 3)
    payload = {
        "as_of": AS_OF,
        "elapsed_s": elapsed,
        "seeds": evid.get("stats", {}).get("seeds"),
        "validation_pids": evid.get("stats", {}).get("validation_pids"),
        "forecast_trust": trust,
        "forecast_dependency": dep,
        "evidence": evid,
        "leverage": lev,
        "index_case": idx,
    }
    out = ROOT / "artifacts" / "evidence.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    pt = evid.get("precision_trust") or {}
    pd = evid.get("precision_dependency") or {}
    print(f"wrote {out} in {elapsed}s")
    print(f"trust preds={len(trust['predictions'])} p@10={pt.get('precision_at_10')}")
    print(f"dep   preds={len(dep['predictions'])} p@10={pd.get('precision_at_10')}")
    print(f"r0_trust={evid.get('r0_trust')} r0_dep={evid.get('r0_dependency')}")
    print(f"mincut={[m.get('id') for m in lev.get('mincut') or []]}")
    print(f"blocked={lev.get('stats', {}).get('spread_blocked_pct')}")
    print(f"true_origin_rank={idx.get('stats', {}).get('true_origin_rank')}")
    print(f"measured={evid.get('stats', {}).get('measured')} note={evid.get('note')}")
    if trust["predictions"]:
        top = trust["predictions"][0]
        print(f"trust#1 {top['pid']} score={top['score']}")
    driver.close()


if __name__ == "__main__":
    main()
