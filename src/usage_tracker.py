"""Usage accounting for model calls; deterministic mode reports zero usage."""


def offline_usage_report(run_id, timestamp, request_count=0, processed_count=0):
    return {
        "run_id": run_id,
        "timestamp": timestamp,
        "input_requests": request_count,
        "processed_requests": processed_count,
        "model_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "estimated_model_api_cost": 0,
        "note": "No model was called; no provider token usage was incurred.",
    }
