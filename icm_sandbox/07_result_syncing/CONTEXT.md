# Stage 07: Result Syncing

## Purpose
Safely retrieve experiment artifacts from the remote server and consolidate them into a format ready for analysis.

## Contract
**Inputs (Layer 4 - `input/`):**
- `job_ids.json` from `06_remote_execution`.

**Process:**
- `src/` contains logic to `rsync` completed experiment folders from Snorlax.
- Verifies integrity of downloaded files.
- Aggregates individual `result.json` files into a single master CSV.

**Outputs (Layer 4 - `output/`):**
- `aggregated_results.csv`: The primary data source for analysis.
- Local copies of experiment artifacts (optional, for debugging).

## Stage Rules
- Support incremental syncing: if a download is interrupted, it should resume without re-downloading everything.
- Log any missing or corrupted experiment results.
