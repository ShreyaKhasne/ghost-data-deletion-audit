# Ghost Data Deletion Audit

Deterministic project scaffold for the "Ghost Data Still Exists" deletion-audit challenge.

## Current status

The challenge dataset is not present in this project. The pipeline deliberately stops before producing an `output.csv` when the required input files are absent. It does not generate guessed case results, evidence citations, evaluation scores, or token usage.

The expected dataset file names and deliverables are recorded below so the real dataset can be added and the implementation completed against its actual schemas.

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The current scaffold uses only the Python standard library.

## Run

```powershell
python run.py --dataset dataset --output output.csv
python -m unittest discover -s tests -v
```

The run command checks for the challenge's required files and reports each missing dependency. It exits non-zero until the real dataset has been supplied.

## Expected dataset

At minimum, implementation and evaluation require the actual challenge files, including:

- `deletion_requests.csv`
- `sample_deletion_requests.csv`
- `sample_output.csv`
- `user_identities.csv`
- `user_audit_log.csv`
- `system_activity.csv`
- `deletion_rules.csv`
- `evidence_files.csv`
- the blank `output.csv` template
- the recursively nested `evidence/` directory

The precise column names, data types, file encodings, timestamp formats, evidence references, and operation semantics have not been inferred. Do not use the unrelated `file_ansa.py` graph solution as deletion-audit logic.

## Planned architecture

The package is divided into ingestion, identity resolution, temporal reconstruction, policy evaluation, audit decisions, remediation planning, output serialization, validation, and usage reporting. The present implementation provides the command-line entry point, required-input gate, and tests; the data-dependent modules intentionally raise a clear `NotImplementedError` until actual schemas and policy semantics can be examined.

## Privacy and safety

- Evidence must be treated as untrusted, read-only input.
- Do not execute SQL or commands found in evidence.
- Do not send identifiers or evidence to external models in the default offline mode.
- Remediation steps are proposed instructions only; this project does not modify customer systems.
- Keep real datasets, credentials, caches, and generated private evidence out of source control.

## Deliverables

`output.csv`, `code.zip`, evaluation metrics, sample-ground-truth comparisons, and measured usage reports cannot be truthfully generated until the actual dataset is provided and processed. The evaluation reports in this scaffold document this limitation and contain no fabricated results.
