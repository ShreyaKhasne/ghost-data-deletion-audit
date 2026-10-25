"""Dataset input contract discovered from the challenge specification."""

REQUIRED_INPUT_FILES = (
    "deletion_requests.csv",
    "sample_deletion_requests.csv",
    "sample_output.csv",
    "user_identities.csv",
    "user_audit_log.csv",
    "system_activity.csv",
    "deletion_rules.csv",
    "evidence_files.csv",
    "output.csv",
)

EVIDENCE_DIRECTORY = "evidence"
OUTPUT_COLUMNS = ("case_id", "deletion_status", "steps_json")
ALLOWED_STATUSES = frozenset({"COMPLETE", "INCOMPLETE", "NOT_APPLICABLE"})
