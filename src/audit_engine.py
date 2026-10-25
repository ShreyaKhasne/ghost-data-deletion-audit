"""Case-level decisions based on policy and cutoff-valid evidence."""


def audit_case(_case, _dataset):
    """Return an evidence-backed deletion status and ordered audit steps."""
    raise NotImplementedError(
        "Case auditing requires actual dataset schemas and policy semantics."
    )
