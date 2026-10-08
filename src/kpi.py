"""Calculate learning KPIs from the ETL database."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def calculate_kpis(database_path: Path) -> dict[str, float | int]:
    """Return record count, completion rate, and average score."""
    with sqlite3.connect(database_path) as connection:
        total, completed, average_score = connection.execute(
            """
            SELECT
                COUNT(*),
                COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0),
                AVG(score)
            FROM learner_records
            """,
            ("completed",),
        ).fetchone()

    return {
        "total_learners": total,
        "completed_learners": completed,
        "completion_rate": round((completed / total) * 100, 2) if total else 0.0,
        "average_score": round(average_score, 2) if average_score is not None else 0.0,
    }


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    database_path = root / "data" / "kpi.db"
    output_path = root / "data" / "kpis.json"
    metrics = calculate_kpis(database_path)
    output_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
