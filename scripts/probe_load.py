"""One-shot Bolt lookups. Not part of the product API."""

from patient_zero.db import bolt_driver
from patient_zero.ids import hydra_id

CHECKS = [
    ("Version", "npm:@tanstack/query-core@5.101.4"),
    ("Package", "npm:@tanstack/query-core"),
    ("Service", "svc:axios"),
    ("Repo", "github:mistralai/client-python"),
    ("Maintainer", "npm:tannerlinsley"),
]


def parquet_has_vid(vid: str) -> bool:
    import pyarrow.parquet as pq
    from pathlib import Path

    path = Path("data/graph/versions.parquet")
    if not path.is_file():
        return False
    return vid in pq.read_table(path).column("vid").to_pylist()


def main() -> None:
    driver = bolt_driver()
    try:
        with driver.session() as session:
            for label, stable in CHECKS:
                hid = hydra_id(stable)
                rec = session.run(
                    f"MATCH (a:{label} {{id: $hid}}) RETURN a.id AS id",
                    hid=hid,
                ).single()
                extra = ""
                if label == "Version":
                    extra = f" parquet={parquet_has_vid(stable)}"
                    import pyarrow.parquet as pq
                    vids = [
                        v for v in pq.read_table("data/graph/versions.parquet").column("vid").to_pylist()
                        if v and "query-core@" in v
                    ]
                    print("  query-core vids in parquet:", vids[:12], "n=", len(vids))
                print(label, stable, hid, "OK" if rec else "MISSING", extra)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
