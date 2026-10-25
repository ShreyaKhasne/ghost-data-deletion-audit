"""Read-only ingestion entry points; implement after real schema inspection."""


def load_dataset(_dataset_dir):
    """Load challenge inputs after their schemas and formats are inspected."""
    raise NotImplementedError(
        "Dataset ingestion requires the actual challenge files and evidence inventory."
    )
