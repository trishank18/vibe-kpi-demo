"""Load the raw customer CSV into SQLite."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

REQUIRED_COLUMNS = {"customer_id", "city", "monthly_spend", "churned"}


def load_customers(input_path: Path, database_path: Path) -> int:
    """Validate and load customer records, returning the number of rows loaded."""
    with input_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        rows: list[tuple[int, str, float, int]] = []
        for line_number, record in enumerate(reader, start=2):
            customer_id = (record["customer_id"] or "").strip()
            city = (record["city"] or "").strip()
            spend_text = (record["monthly_spend"] or "").strip()
            churned_text = (record["churned"] or "").strip()
            if not customer_id or not city:
                raise ValueError(f"Line {line_number}: customer_id and city are required")
            try:
                customer_id_value = int(customer_id)
                monthly_spend = float(spend_text)
            except ValueError as exc:
                raise ValueError(f"Line {line_number}: customer_id and monthly_spend must be numeric") from exc
            if monthly_spend < 0 or churned_text not in {"0", "1"}:
                raise ValueError(f"Line {line_number}: monthly_spend must be non-negative and churned must be 0 or 1")
            rows.append((customer_id_value, city, monthly_spend, int(churned_text)))

    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.execute("DROP TABLE IF EXISTS customers_raw")
        connection.execute(
            """
            CREATE TABLE customers_raw (
                customer_id INTEGER PRIMARY KEY,
                city TEXT NOT NULL,
                monthly_spend REAL NOT NULL,
                churned INTEGER NOT NULL CHECK (churned IN (0, 1))
            )
            """
        )
        connection.executemany(
            "INSERT INTO customers_raw (customer_id, city, monthly_spend, churned) VALUES (?, ?, ?, ?)",
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
