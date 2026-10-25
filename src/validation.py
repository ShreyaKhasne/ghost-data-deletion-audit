"""Output shape validation."""

import csv
import json

from src.config import ALLOWED_STATUSES, OUTPUT_COLUMNS


def validate_output(path, expected_case_ids):
    with open(path, newline="", encoding="utf-8") as output_file:
        reader = csv.DictReader(output_file)
        if tuple(reader.fieldnames or ()) != OUTPUT_COLUMNS:
            raise ValueError(f"Expected columns {OUTPUT_COLUMNS!r}")
        rows = list(reader)

    actual_ids = [row["case_id"] for row in rows]
    if actual_ids != sorted(expected_case_ids):
        raise ValueError("Output case IDs are not sorted or do not match input cases")
    if len(actual_ids) != len(set(actual_ids)):
        raise ValueError("Output contains duplicate case IDs")

    for row in rows:
        if row["deletion_status"] not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status for case {row['case_id']!r}")
        steps = json.loads(row["steps_json"])
        if not isinstance(steps, list):
            raise ValueError(f"steps_json must be an array for {row['case_id']!r}")
