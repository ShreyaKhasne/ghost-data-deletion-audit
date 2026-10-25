import csv
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.dataset_inspector import inspect_dataset
from src.main import check_dataset
from src.output_serializer import write_output
from src.validation import validate_output, validate_steps


class ScaffoldTests(unittest.TestCase):
    def test_missing_dataset_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = check_dataset(Path(directory))
        self.assertTrue(missing)
        self.assertIn("deletion_requests.csv", missing[0])

    def test_output_schema_and_json_serialization(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output.csv"
            rows = [
                {
                    "case_id": "case-a",
                    "deletion_status": "COMPLETE",
                    "steps": [
                        {
                            "step_no": 1,
                            "phase": "VERIFICATION",
                            "system_id": "sys-a",
                            "resource_id": "resource-a",
                            "operation": "VERIFY_RECORD_ABSENT",
                            "state": "ABSENT",
                            "evidence_id": "evidence-a",
                        }
                    ],
                }
            ]
            write_output(rows, output)
            validate_output(output, ["case-a"])
            with output.open(newline="", encoding="utf-8") as output_file:
                saved_row = next(csv.DictReader(output_file))
            self.assertEqual(json.loads(saved_row["steps_json"]), rows[0]["steps"])

    def test_output_rows_are_sorted_lexically(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output.csv"
            empty_steps = []
            rows = [
                {
                    "case_id": "case-b",
                    "deletion_status": "NOT_APPLICABLE",
                    "steps": empty_steps,
                },
                {
                    "case_id": "case-a",
                    "deletion_status": "NOT_APPLICABLE",
                    "steps": empty_steps,
                },
            ]
            write_output(rows, output)
            validate_output(output, ["case-b", "case-a"])

            with output.open(newline="", encoding="utf-8") as output_file:
                saved_ids = [row["case_id"] for row in csv.DictReader(output_file)]
        self.assertEqual(saved_ids, ["case-a", "case-b"])

    def test_step_validation_checks_exact_fields_and_allowed_pair(self):
        valid_step = {
            "step_no": 1,
            "phase": "VERIFICATION",
            "system_id": "sys-a",
            "resource_id": "resource-a",
            "operation": "VERIFY_RECORD_ABSENT",
            "state": "ABSENT",
            "evidence_id": "evidence-a",
        }
        validate_steps("case-a", "COMPLETE", [valid_step], {"evidence-a"})

        invalid_step = dict(valid_step, state="PRESENT")
        with self.assertRaisesRegex(ValueError, "Invalid phase/state"):
            validate_steps("case-a", "COMPLETE", [invalid_step], {"evidence-a"})

    def test_incomplete_proposed_steps_need_empty_evidence(self):
        step = {
            "step_no": 1,
            "phase": "REMEDIATION",
            "system_id": "sys-a",
            "resource_id": "resource-a",
            "operation": "DELETE_RECORD",
            "state": "ABSENT",
            "evidence_id": "",
        }
        validate_steps("case-a", "INCOMPLETE", [step])
        step["evidence_id"] = "evidence-a"
        with self.assertRaisesRegex(ValueError, "empty evidence IDs"):
            validate_steps("case-a", "INCOMPLETE", [step])

    def test_not_applicable_case_must_have_no_steps(self):
        with self.assertRaisesRegex(ValueError, "must have no steps"):
            validate_steps("case-a", "NOT_APPLICABLE", [{"step_no": 1}])

    def test_steps_must_follow_operation_order(self):
        steps = [
            {
                "step_no": 1,
                "phase": "REMEDIATION",
                "system_id": "sys-a",
                "resource_id": "resource-a",
                "operation": "DELETE_RECORD",
                "state": "ABSENT",
                "evidence_id": "",
            },
            {
                "step_no": 2,
                "phase": "REMEDIATION",
                "system_id": "sys-a",
                "resource_id": "resource-a",
                "operation": "DISABLE_DATA_FLOW",
                "state": "DISABLED",
                "evidence_id": "",
            },
        ]
        with self.assertRaisesRegex(ValueError, "ordering"):
            validate_steps("case-a", "INCOMPLETE", steps)

    def test_serializer_orders_steps_and_reassigns_step_numbers(self):
        later_operation = {
            "step_no": 99,
            "phase": "REMEDIATION",
            "system_id": "sys-a",
            "resource_id": "resource-a",
            "operation": "DELETE_RECORD",
            "state": "ABSENT",
            "evidence_id": "",
        }
        earlier_operation = {
            "step_no": 99,
            "phase": "REMEDIATION",
            "system_id": "sys-z",
            "resource_id": "resource-z",
            "operation": "DISABLE_DATA_FLOW",
            "state": "DISABLED",
            "evidence_id": "",
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output.csv"
            write_output(
                [
                    {
                        "case_id": "case-a",
                        "deletion_status": "INCOMPLETE",
                        "steps": [later_operation, earlier_operation],
                    }
                ],
                output,
            )
            validate_output(output, ["case-a"])
            with output.open(newline="", encoding="utf-8") as output_file:
                saved_row = next(csv.DictReader(output_file))

        saved_steps = json.loads(saved_row["steps_json"])
        self.assertEqual(
            [step["operation"] for step in saved_steps],
            ["DISABLE_DATA_FLOW", "DELETE_RECORD"],
        )
        self.assertEqual([step["step_no"] for step in saved_steps], [1, 2])

    def test_dataset_inspector_summarizes_without_record_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "requests.csv").write_text(
                "case_id,email\nc-1,person@example.test\n", encoding="utf-8"
            )
            database_path = root / "snapshot.sqlite"
            connection = sqlite3.connect(database_path)
            connection.execute("CREATE TABLE records (id INTEGER)")
            connection.execute("INSERT INTO records VALUES (1)")
            connection.commit()
            connection.close()

            summary = inspect_dataset(root)

        self.assertEqual(len(summary["files"]), 2)
        csv_summary = next(
            item for item in summary["files"] if item["name"] == "requests.csv"
        )
        self.assertEqual(csv_summary["columns"], ["case_id", "email"])
        self.assertNotIn("person@example.test", json.dumps(summary))
        sqlite_summary = next(
            item for item in summary["files"] if item["name"] == "snapshot.sqlite"
        )
        self.assertEqual(sqlite_summary["tables_and_rows"], {"records": 1})


if __name__ == "__main__":
    unittest.main()
