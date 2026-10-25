"""Exact submission CSV serialization."""

import csv
import json

from src.config import OPERATION_ORDER, OUTPUT_COLUMNS, PHASE_ORDER


def order_steps(steps):
    """Sort steps by the required phase/operation/system/resource ordering."""
    ordered = sorted(
        steps,
        key=lambda step: (
            PHASE_ORDER[step["phase"]],
            OPERATION_ORDER[step["operation"]],
            step["system_id"],
            step["resource_id"],
        ),
    )
    return [dict(step, step_no=index) for index, step in enumerate(ordered, start=1)]


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
        for row in sorted(rows, key=lambda item: item["case_id"]):
            writer.writerow(
                {
                    "case_id": row["case_id"],
                    "deletion_status": row["deletion_status"],
                    "steps_json": json.dumps(
                        order_steps(row["steps"]),
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                }
            )
