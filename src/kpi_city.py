"""Calculate customer KPIs grouped by city."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def calculate_city_kpis(database_path: Path) -> list[dict[str, float | int | str]]:
    """Return customer count, total spend, and average spend for each city."""
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT city, COUNT(*) AS customer_count, SUM(spend) AS total_spend,
                   AVG(spend) AS average_spend
            FROM customers
            GROUP BY city
            ORDER BY city
            """
        ).fetchall()
    return [
        {
            "city": city,
            "customer_count": customer_count,
            "total_spend": round(total_spend, 2),
            "average_spend": round(average_spend, 2),
        }
        for city, customer_count, total_spend, average_spend in rows
    ]


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    metrics = calculate_city_kpis(root / "data" / "db" / "analytics.db")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
