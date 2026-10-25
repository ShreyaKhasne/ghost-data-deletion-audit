"""Exact submission CSV serialization."""

import csv
import json

from src.config import OUTPUT_COLUMNS


def write_output(rows, output_path):
    """Write rows with the exact required header and JSON-encoded step arrays."""
    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=OUTPUT_COLUMNS,
            extrasaction="raise",
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "case_id": row["case_id"],
                    "deletion_status": row["deletion_status"],
                    "steps_json": json.dumps(
                        row["steps"], ensure_ascii=False, separators=(",", ":")
                    ),
                }
            )
