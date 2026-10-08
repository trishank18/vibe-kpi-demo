"""Calculate customer KPIs for one city."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def city_kpi(city: str, database_path: Path | None = None) -> dict[str, float | int | str]:
    """Return customer count, total monthly spend, and average spend for one city."""
    if database_path is None:
        root = Path(__file__).resolve().parent.parent
        database_path = root / "data" / "db" / "analytics.db"

    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT COUNT(*) AS customer_count,
                   COALESCE(SUM(monthly_spend), 0),
                   COALESCE(AVG(monthly_spend), 0)
            FROM customers_raw
            WHERE city = ?
            """,
            (city,),
        ).fetchone()

    customer_count, total_spend, average_spend = row
    return {
        "city": city,
        "customer_count": customer_count,
        "total_spend": round(total_spend, 2),
        "average_spend": round(average_spend, 2),
    }


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    database_path = root / "data" / "db" / "analytics.db"
    print(city_kpi("Mumbai", database_path))
    print(city_kpi("Mumbai' OR 1=1 --", database_path))


if __name__ == "__main__":
    main()
