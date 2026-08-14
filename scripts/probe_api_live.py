"""Live smoke: one trust forecast + one blast-radius against HydraDB."""

from __future__ import annotations

from patient_zero.db import bolt_driver
from patient_zero.engine import Engine


def main() -> None:
    driver = bolt_driver()
    try:
        def run(cypher, params):
            with driver.session() as session:
                return [record["path"] for record in session.run(cypher, **params)]

        engine = Engine.live(run_paths=run)
        blast = engine.blast_radius(
            ecosystem="npm",
            name="@tanstack/react-query",
            version="5.101.4",
            window_start=1778527200,
            window_end=1778527200 + 360,
            max_hops=4,
            limit=20,
        )
        print("blast stub-n/a services", blast["stats"], "n", len(blast["services"]))
        print("blast cypher", blast["cypher"].splitlines()[0])
        fc = engine.forecast(
            seeds=["npm:@tanstack/react-query"],
            as_of=1778527200 + 360,
            k=8,
            topology="trust",
            max_hops=3,
            limit=50,
        )
        print("forecast n", len(fc["predictions"]))
        for row in fc["predictions"][:8]:
            print(" ", row["pid"], row["score"], "->", row["justification_path"][:4])
        idx = engine.index_case(
            observed=["npm:@tanstack/react-query"],
            as_of=1778527200 + 360,
            k=5,
            max_hops=4,
            limit=50,
        )
        print("index", [(c["kind"], c["id"], c["score"]) for c in idx["candidates"]], "origin", idx["stats"]["true_origin_rank"])
    finally:
        driver.close()


if __name__ == "__main__":
    main()
