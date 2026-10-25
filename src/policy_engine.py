"""Deterministic interpretation of the supplied deletion policy."""


def evaluate_policy(_resource, _rule):
    """Evaluate a resource against a parsed, dataset-derived policy rule."""
    raise NotImplementedError(
        "Policy evaluation requires inspection of deletion_rules.csv."
    )
