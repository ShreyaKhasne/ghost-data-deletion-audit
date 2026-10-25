# AI interview explanation

## Current implementation status

This repository currently contains a safe, deterministic project scaffold, not the completed challenge solution. The required dataset and evidence are not available, so no identity, temporal-state, policy, or case-level result has been derived. The command line fails closed rather than fabricate answers.

## Intended architecture

The planned pipeline separates evidence ingestion, identity resolution, cutoff-aware temporal reconstruction, policy enforcement, audit decisions, remediation planning, output serialization, validation, and usage accounting. Stable internal user IDs are intended to be the primary linkage key, with every historical identifier association backed by evidence.

## Safety and validation approach

The completed pipeline should inspect rather than execute evidence; exclude post-cutoff events from claims about earlier state; treat attempted operations as distinct from verified outcomes; and produce only proposed remediation instructions. Output validation should check exact columns, case coverage, permitted statuses and step fields, citations, ordering, and JSON validity.

## AI usage, evaluation, and limitations

No external model is used in this scaffold. Deterministic processing is preferred for joins, timestamp filtering, policy logic, sorting, and schema checks. If a future implementation adds an LLM for ambiguous unstructured evidence, it must validate all structured fields against actual dataset vocabularies and record provider-reported usage. No measured accuracy, full-run token use, or cost can be reported until the actual dataset is supplied and a full run is executed.
