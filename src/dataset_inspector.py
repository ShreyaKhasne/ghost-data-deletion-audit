"""Read-only structural inventory for supplied dataset files."""

import csv
import json
import os
import sqlite3
from pathlib import Path


def _csv_summary(path):
    last_error = None
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            with path.open("r", encoding=encoding, newline="") as source:
                sample = source.read(8192)
                source.seek(0)
                delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
                if path.suffix.lower() != ".tsv" and sample:
                    try:
                        delimiter = csv.Sniffer().sniff(
                            sample, delimiters=",;\t|"
                        ).delimiter
                    except csv.Error:
                        pass
                reader = csv.reader(source, delimiter=delimiter)
                headers = next(reader, [])
                row_count = sum(1 for _ in reader)
            return {
                "format": "csv" if path.suffix.lower() != ".tsv" else "tsv",
                "encoding": encoding,
                "columns": headers,
                "duplicate_column_names": sorted(
                    {name for name in headers if headers.count(name) > 1}
                ),
                "data_rows": row_count,
            }
        except UnicodeDecodeError as error:
            last_error = error
    raise UnicodeError(f"Could not decode {path.name}") from last_error


def _json_summary(path):
    if path.suffix.lower() == ".jsonl":
        record_count = 0
        malformed_lines = 0
        with path.open("r", encoding="utf-8-sig") as source:
            for line in source:
                if not line.strip():
                    continue
                try:
                    json.loads(line)
                    record_count += 1
                except json.JSONDecodeError:
                    malformed_lines += 1
        return {
            "format": "jsonl",
            "valid_records": record_count,
            "malformed_lines": malformed_lines,
        }

    with path.open("r", encoding="utf-8-sig") as source:
        value = json.load(source)
    summary = {"format": "json", "root_type": type(value).__name__}
    if isinstance(value, (list, dict)):
        summary["top_level_items"] = len(value)
        if isinstance(value, dict):
            summary["top_level_keys"] = sorted(str(key) for key in value)
    return summary


def _sqlite_summary(path):
    uri = path.resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    try:
        tables = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        result = {}
        for (table_name,) in tables:
            quoted_name = '"' + table_name.replace('"', '""') + '"'
            result[table_name] = connection.execute(
                f"SELECT COUNT(*) FROM {quoted_name}"
            ).fetchone()[0]
        return {"format": "sqlite", "tables_and_rows": result}
    finally:
        connection.close()


def _file_summary(path):
    suffix = path.suffix.lower()
    result = {"name": path.name, "bytes": path.stat().st_size}
    if suffix in {".csv", ".tsv"}:
        result.update(_csv_summary(path))
    elif suffix in {".json", ".jsonl"}:
        result.update(_json_summary(path))
    elif suffix in {".sqlite", ".sqlite3", ".db"}:
        result.update(_sqlite_summary(path))
    elif suffix in {".sql"}:
        result.update(
            {
                "format": "sql-text",
                "note": "Not executed; SQL exports are treated as untrusted text.",
            }
        )
    elif suffix in {".pdf"}:
        result.update(
            {
                "format": "pdf",
                "text_extracted": False,
                "note": "Content extraction requires format inspection and a vetted parser.",
            }
        )
    elif suffix in {".png", ".jpg", ".jpeg"}:
        result.update(
            {
                "format": "image",
                "text_extracted": False,
                "note": "OCR is not run by the structural inventory.",
            }
        )
    elif suffix in {".log", ".txt"}:
        with path.open("rb") as source:
            line_count = sum(1 for _ in source)
        result.update({"format": "text", "lines": line_count})
    else:
        result["format"] = suffix.lstrip(".") or "unknown"
    return result


def inspect_dataset(dataset):
    """Summarize file structure without printing records or executing exports."""
    root = Path(dataset)
    if not root.is_dir():
        raise NotADirectoryError(f"Dataset directory does not exist: {root}")

    inventory = []
    walk_errors = []

    def on_walk_error(error):
        walk_errors.append(
            {"path": os.path.basename(error.filename or ""), "error": type(error).__name__}
        )

    for directory, subdirectories, filenames in os.walk(
        root, followlinks=False, onerror=on_walk_error
    ):
        subdirectories.sort()
        for filename in sorted(filenames):
            path = Path(directory) / filename
            if path.is_symlink():
                inventory.append(
                    {
                        "relative_path": str(path.relative_to(root)),
                        "format": "symlink",
                        "note": "Not followed.",
                    }
                )
                continue
            try:
                summary = _file_summary(path)
            except (OSError, UnicodeError, json.JSONDecodeError, csv.Error, sqlite3.Error) as error:
                summary = {
                    "name": path.name,
                    "inspection_error": f"{type(error).__name__}: {error}",
                }
            summary["relative_path"] = str(path.relative_to(root))
            inventory.append(summary)

    return {"files": inventory, "walk_errors": walk_errors}
