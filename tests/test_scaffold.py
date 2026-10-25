import json
import csv
import tempfile
import unittest
from pathlib import Path

from src.main import check_dataset
from src.output_serializer import write_output
from src.validation import validate_output


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
                    "steps": [{"step_no": 1, "phase": "VERIFICATION"}],
                }
            ]
            write_output(rows, output)
            validate_output(output, ["case-a"])
            with output.open(newline="", encoding="utf-8") as output_file:
                saved_row = next(csv.DictReader(output_file))
            self.assertEqual(json.loads(saved_row["steps_json"]), rows[0]["steps"])


if __name__ == "__main__":
    unittest.main()
