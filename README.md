# vibe-kpi-demo

Small LMS KPI pipeline demo:

1. Load `data/learners.csv` into SQLite with the ETL script.
2. Calculate completion and score KPIs from the database.
3. Run the tests, including a SQL-injection-shaped input.

## Run

```bash
python -m src.etl
python -m src.kpi
pytest -q
```

The generated SQLite database and `data/kpis.json` are ignored by Git.