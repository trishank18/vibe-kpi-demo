# vibe-kpi-demo

Customer city KPI demo using Python, CSV, and SQLite.

```bash
python -m src.etl_load_sqlite
python -m src.kpi_city
pytest -q
```

The ETL script loads `data/raw/customers_raw.csv` into `data/db/analytics.db`.
The KPI script reports customer count, total spend, and average spend per city.