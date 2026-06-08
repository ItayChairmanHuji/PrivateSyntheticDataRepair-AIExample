# Vanilla Repairing Tests (Internal)

Verification suite for the Vanilla repairing process.

## Test Strategy

We use a "Mock Hierarchy" approach to verify the end-to-end flow:
1.  Setup a temporary RPM-like folder structure.
2.  Generate small synthetic datasets and marginals.
3.  Run the `RepairingWorker` with `VanillaVCRepairer`.
4.  Verify that the output exists and that conflicts are resolved.
