"""Command-line entry point for the audit pipeline."""

import argparse
import json
import logging
from pathlib import Path

from src.config import EVIDENCE_DIRECTORY, REQUIRED_INPUT_FILES
from src.dataset_inspector import inspect_dataset


def check_dataset(dataset: Path) -> list[str]:
    missing = [
        str(dataset / filename)
        for filename in REQUIRED_INPUT_FILES
        if not (dataset / filename).is_file()
    ]
    if not (dataset / EVIDENCE_DIRECTORY).is_dir():
        missing.append(str(dataset / EVIDENCE_DIRECTORY))
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit deletion requests against supplied evidence."
    )
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("output.csv"))
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="Print a structural inventory without emitting audit results.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Use deterministic local processing only (the default scaffold mode).",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args.inspect:
        try:
            print(json.dumps(inspect_dataset(args.dataset), indent=2, ensure_ascii=False))
        except OSError as error:
            logging.error("Dataset inspection failed: %s", error)
            return 2
        return 0

    missing = check_dataset(args.dataset)
    if missing:
        logging.error(
            "Dataset is incomplete; no output was generated. Missing required inputs:"
        )
        for path in missing:
            logging.error("  %s", path)
        return 2

    logging.error(
        "Dataset files exist, but schema inspection and the audit engine are not "
        "implemented yet. Refusing to generate potentially misleading results."
    )
    return 3
