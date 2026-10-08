import sqlite3
from pathlib import Path

import pytest

from src.etl_load_sqlite import load_customers
from src.kpi_city import calculate_city_kpis


def test_city_kpis(tmp_path: Path) -> None:
    database_path = tmp_path / "analytics.db"
    load_customers(Path("data/raw/customers_raw.csv"), database_path)

    assert calculate_city_kpis(database_path) == [
        {"city": "Bengaluru", "customer_count": 2, "total_spend": 2851.0, "average_spend": 1425.5},
        {"city": "Hyderabad", "customer_count": 2, "total_spend": 2230.5, "average_spend": 1115.25},
        {"city": "Mumbai", "customer_count": 1, "total_spend": 1600.0, "average_spend": 1600.0},
    ]


def test_injection_shaped_values_are_stored_as_data(tmp_path: Path) -> None:
    input_path = tmp_path / "customers.csv"
    input_path.write_text(
        "customer_id,name,city,spend\n"
        "C001,Name,Hyderabad'); DROP TABLE customers; --,10\n",
        encoding="utf-8",
    )
    database_path = tmp_path / "analytics.db"

    load_customers(input_path, database_path)

    with sqlite3.connect(database_path) as connection:
        row = connection.execute("SELECT city FROM customers").fetchone()
    assert row == ("Hyderabad'); DROP TABLE customers; --",)
    assert calculate_city_kpis(database_path)[0]["total_spend"] == 10.0


def test_invalid_spend_is_rejected(tmp_path: Path) -> None:
    input_path = tmp_path / "customers.csv"
    input_path.write_text(
        "customer_id,name,city,spend\nC001,Name,Hyderabad,-1\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="cannot be negative"):
        load_customers(input_path, tmp_path / "analytics.db")
