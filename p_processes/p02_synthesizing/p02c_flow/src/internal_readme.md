# p02c_synthesizing Internal Documentation: The Glass Box Blueprint

This process is a pure worker that simply sequentially executes `p02a_training` and `p02b_sampling` using the same configuration.

## Architectural Triad

Since this is a compound process, it does not define its own Triad. Instead, it relies on the `TrainingWorker` and `SamplingWorker` defined in its sub-processes.
