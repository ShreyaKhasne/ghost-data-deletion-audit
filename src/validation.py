"""Output shape validation."""

import csv
import json

from src.config import (
    ALLOWED_STATUSES,
    OPERATION_ORDER,
    OPERATION_STATES,
    OUTPUT_COLUMNS,
    PHASE_ORDER,
    STEP_FIELDS,
)


def validate_steps(case_id, status, steps, allowed_evidence_ids=None):
    if status == "NOT_APPLICABLE":
        if steps:
            raise ValueError(f"Not-applicable case {case_id!r} must have no steps")
        return

    if status == "COMPLETE" and any(
        step.get("phase") != "VERIFICATION" for step in steps
    ):
        raise ValueError(f"Complete case {case_id!r} may contain only verifications")

    expected_sort_keys = []
    previous_phase = -1
    for expected_step_no, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise ValueError(
                f"Case {case_id!r} step {expected_step_no} must be an object"
            )
        if set(step) != STEP_FIELDS:
            raise ValueError(
                f"Case {case_id!r} step {expected_step_no} must contain exactly "
                f"{sorted(STEP_FIELDS)!r}"
            )
        if step["step_no"] != expected_step_no:
            raise ValueError(
                f"Case {case_id!r} step numbers must be consecutive from 1"
            )

        operation = step["operation"]
        if operation not in OPERATION_STATES:
            raise ValueError(f"Unknown operation {operation!r} in case {case_id!r}")
        expected_phase, expected_state = OPERATION_STATES[operation]
        if step["phase"] != expected_phase or step["state"] != expected_state:
            raise ValueError(
                f"Invalid phase/state for operation {operation!r} in case {case_id!r}"
            )
        if not isinstance(step["system_id"], str) or not step["system_id"]:
            raise ValueError(f"Missing system_id in case {case_id!r}")
        if not isinstance(step["resource_id"], str) or not step["resource_id"]:
            raise ValueError(f"Missing resource_id in case {case_id!r}")
        if not isinstance(step["evidence_id"], str):
            raise ValueError(f"evidence_id must be a string in case {case_id!r}")

        phase_order = PHASE_ORDER[expected_phase]
        if phase_order < previous_phase:
            raise ValueError(f"Incorrect phase ordering in case {case_id!r}")
        previous_phase = phase_order

        if expected_phase == "FINDING":
            if not step["evidence_id"]:
                raise ValueError(
                    f"Finding step {expected_step_no} in case {case_id!r} "
                    "requires an evidence ID"
                )
            if allowed_evidence_ids is not None and (
                step["evidence_id"] not in allowed_evidence_ids
            ):
                raise ValueError(
                    f"Unknown evidence ID in case {case_id!r} step {expected_step_no}"
                )
        elif status == "INCOMPLETE" and step["evidence_id"]:
            raise ValueError(
                f"Proposed steps in incomplete case {case_id!r} must have "
                "empty evidence IDs"
            )
        elif status == "COMPLETE":
            if not step["evidence_id"]:
                raise ValueError(
                    f"Verification step {expected_step_no} in complete case "
                    f"{case_id!r} requires an evidence ID"
                )
            if allowed_evidence_ids is not None and (
                step["evidence_id"] not in allowed_evidence_ids
            ):
                raise ValueError(
                    f"Unknown evidence ID in case {case_id!r} step {expected_step_no}"
                )

        expected_sort_keys.append(
            (
                phase_order,
                OPERATION_ORDER[operation],
                step["system_id"],
                step["resource_id"],
            )
        )

    if expected_sort_keys != sorted(expected_sort_keys):
        raise ValueError(
            f"Incorrect operation/system/resource ordering in case {case_id!r}"
        )


def validate_output(path, expected_case_ids, allowed_evidence_ids=None):
    expected_case_ids = list(expected_case_ids)
    if len(expected_case_ids) != len(set(expected_case_ids)):
        raise ValueError("Input case IDs contain duplicates")

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
        validate_steps(
            row["case_id"],
            row["deletion_status"],
            steps,
            allowed_evidence_ids,
        )
