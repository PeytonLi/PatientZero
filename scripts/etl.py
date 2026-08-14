#!/usr/bin/env python3
"""Reproduce the W1 Parquet graph from artifacts + caches.

    python scripts/etl.py --offline
    python scripts/etl.py
"""

from patient_zero.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
