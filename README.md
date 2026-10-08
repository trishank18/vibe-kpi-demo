# Applied Analytics KPI Mini Project

This beginner-friendly project loads customer data from CSV into SQLite and calculates
city-level customer KPIs.

## Run the project

Run these commands from the project folder after activating `.venv`:

```powershell
pip install -r requirements.txt
python src/etl_load_sqlite.py
python src/kpi_city.py
pytest -q
```

## Project files

- `data/raw/customers_raw.csv` - Small sample customer dataset.
- `data/db/analytics.db` - SQLite database created by the ETL script.
- `src/etl_load_sqlite.py` - Loads and validates the CSV into `customers_raw`.
- `src/kpi_city.py` - Calculates one city's KPIs with a parameterized SQL query.
- `tests/test_kpi_city.py` - Tests the normal KPI result and SQL injection protection.
- `requirements.txt` - Lists pandas and pytest.
- `.gitignore` - Keeps virtual-environment, cache, environment, and database files out of Git.