"""Load raw customer data into SQLite."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

REQUIRED_COLUMNS = {"customer_id", "name", "city", "spend"}


def load_customers(input_path: Path, database_path: Path) -> int:
    """Validate and load customer records, returning the number of rows loaded."""
    with input_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        rows: list[tuple[str, str, str, float]] = []
        for line_number, record in enumerate(reader, start=2):
            customer_id = (record["customer_id"] or "").strip()
            name = (record["name"] or "").strip()
            city = (record["city"] or "").strip()
            spend_text = (record["spend"] or "").strip()
            if not customer_id or not name or not city:
                raise ValueError(f"Line {line_number}: customer_id, name, and city are required")
            try:
                spend = float(spend_text)
            except ValueError as exc:
                raise ValueError(f"Line {line_number}: spend must be numeric") from exc
            if spend < 0:
                raise ValueError(f"Line {line_number}: spend cannot be negative")
            rows.append((customer_id, name, city, spend))

    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.execute("DROP TABLE IF EXISTS customers")
        connection.execute(
            """
            CREATE TABLE customers (
                customer_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                spend REAL NOT NULL
            )
            """
        )
        connection.executemany(
            "INSERT INTO customers (customer_id, name, city, spend) VALUES (?, ?, ?, ?)",
            rows,
        )
        connection.commit()
    return len(rows)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    count = load_customers(root / "data" / "raw" / "customers_raw.csv", root / "data" / "db" / "analytics.db")
    print(f"Loaded {count} customers")


if __name__ == "__main__":
    main()
