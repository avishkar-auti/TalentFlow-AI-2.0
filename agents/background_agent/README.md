# Background Agent

The Background Agent performs fast, mostly rule-based validation checks on candidate data. 

## Features
- **Duplicate detection**: Checks if the same email or phone already exists for the job.
- **Resume completeness**: Verifies all required fields are present.
- **Experience consistency**: Ensures dates don't overlap and there are no impossible gaps.
- **Education verification**: Validates that degree names and universities seem legitimate.
- **Skills plausibility**: Cross-references experience years vs skill claims.
- **Contact info validation**: Checks email and phone formats.
- **Red flags**: Flags excessive job hopping or unexplained long gaps.

## LLM Usage
This agent is primarily rule-based logic in Python. It only falls back to a lightweight LLM (`llama-3.1-8b-instant`) when rules yield an `INCONCLUSIVE` result (e.g., verifying an ambiguous university name).

## Endpoints
- `POST /api/v1/candidates/{candidate_id}/background`: Trigger background check
- `GET /api/v1/candidates/{candidate_id}/background`: Retrieve results
