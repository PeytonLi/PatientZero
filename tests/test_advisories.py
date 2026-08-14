"""Advisory rows. One GHSA covering the seed vids is enough for T1 AFFECTS."""

from patient_zero.advisories import advisory_tables


def test_advisory_tables_fan_out_affects_to_every_seed_vid():
    ioc = [
        {"vid": "npm:@tanstack/query-core@5.90.2", "split": "seed", "ecosystem": "npm"},
        {"vid": "npm:@tanstack/query-core@5.90.3", "split": "seed", "ecosystem": "npm"},
        {"vid": "npm:other@1.0.0", "split": "validation", "ecosystem": "npm"},
    ]
    advisories, affects = advisory_tables(ioc)
    assert advisories == [
        {"aid": "ghsa:GHSA-g7cv-rxg3-hmpx", "source": "ghsa", "severity": "high"}
    ]
    assert [row["vid"] for row in affects] == [
        "npm:@tanstack/query-core@5.90.2",
        "npm:@tanstack/query-core@5.90.3",
    ]
    assert all(row["aid"] == "ghsa:GHSA-g7cv-rxg3-hmpx" for row in affects)
