from pathlib import Path

from src.etl_load_sqlite import load_customers
from src.kpi_city import city_kpi


def test_city_kpi_returns_mumbai_metrics(tmp_path: Path) -> None:
    database_path = tmp_path / "analytics.db"
    load_customers(Path("data/raw/customers_raw.csv"), database_path)

    assert city_kpi("Mumbai", database_path) == {
        "city": "Mumbai",
        "customer_count": 3,
        "total_spend": 4120.75,
        "average_spend": 1373.58,
    }


def test_injection_attempt_is_treated_as_city_text(tmp_path: Path) -> None:
    database_path = tmp_path / "analytics.db"
    load_customers(Path("data/raw/customers_raw.csv"), database_path)

    result = city_kpi("Mumbai' OR 1=1 --", database_path)

    assert result["customer_count"] == 0
    assert result["total_spend"] == 0
