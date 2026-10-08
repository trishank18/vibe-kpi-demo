"""Load learner CSV data into a SQLite database."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

REQUIRED_COLUMNS = {"learner_id", "course", "status", "score"}
VALID_STATUSES = {"completed", "in_progress", "not_started"}


def load_csv(input_path: Path, database_path: Path) -> int:
    """Validate and load learner records, returning the number of rows loaded."""
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        rows: list[tuple[str, str, str, float | None]] = []
        for line_number, record in enumerate(reader, start=2):
            learner_id = (record["learner_id"] or "").strip()
            course = (record["course"] or "").strip()
            status = (record["status"] or "").strip()
            score_text = (record["score"] or "").strip()

            if not learner_id or not course:
                raise ValueError(f"Line {line_number}: learner_id and course are required")
            if status not in VALID_STATUSES:
                raise ValueError(f"Line {line_number}: invalid status {status!r}")
            if score_text:
                try:
                    score = float(score_text)
                except ValueError as exc:
                    raise ValueError(f"Line {line_number}: score must be numeric") from exc
                if not 0 <= score <= 100:
                    raise ValueError(f"Line {line_number}: score must be between 0 and 100")
            else:
                score = None
            rows.append((learner_id, course, status, score))

    with sqlite3.connect(database_path) as connection:
        connection.execute("DROP TABLE IF EXISTS learner_records")
        connection.execute(
            """
            CREATE TABLE learner_records (
                learner_id TEXT NOT NULL,
                course TEXT NOT NULL,
                status TEXT NOT NULL,
                score REAL
            )
            """
        )
        connection.executemany(
            """
            INSERT INTO learner_records (learner_id, course, status, score)
            VALUES (?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()
    return len(rows)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    input_path = root / "data" / "learners.csv"
    database_path = root / "data" / "kpi.db"
    count = load_csv(input_path, database_path)
    print(f"Loaded {count} learner records into {database_path}")


if __name__ == "__main__":
    main()
