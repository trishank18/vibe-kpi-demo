import sqlite3
from pathlib import Path

import pytest

from src.etl import load_csv
from src.kpi import calculate_kpis


def test_pipeline_calculates_expected_kpis(tmp_path: Path) -> None:
    database_path = tmp_path / "kpi.db"
    load_csv(Path("data/learners.csv"), database_path)

    assert calculate_kpis(database_path) == {
        "total_learners": 4,
        "completed_learners": 2,
        "completion_rate": 50.0,
        "average_score": 81.67,
    }


def test_sql_injection_shaped_learner_id_is_stored_as_data(tmp_path: Path) -> None:
    input_path = tmp_path / "learners.csv"
    input_path.write_text(
        "learner_id,course,status,score\n"
        "x'); DROP TABLE learner_records; --,Security,completed,100\n",
        encoding="utf-8",
    )
    database_path = tmp_path / "kpi.db"

    load_csv(input_path, database_path)

    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            "SELECT learner_id FROM learner_records"
        ).fetchone()
    assert row == ("x'); DROP TABLE learner_records; --",)
    assert calculate_kpis(database_path)["completed_learners"] == 1


def test_invalid_status_is_rejected(tmp_path: Path) -> None:
    input_path = tmp_path / "learners.csv"
    input_path.write_text(
        "learner_id,course,status,score\nL001,Python,unknown,90\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid status"):
        load_csv(input_path, tmp_path / "kpi.db")
