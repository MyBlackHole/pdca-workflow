# Small Writer Pool Parallelism

When a client receives packed small files, tune local writer concurrency with paired GET measurements rather than assuming more workers is faster.

## Reusable pattern

- Keep the default synchronous path unchanged unless the measurements justify a behavior change.
- Bound the producer queue and expose enqueue, completion, peak queue, peak active, backpressure, and failure counters through an existing progress channel.
- Latch the first worker error, clear pending work, stop accepting frames, and drain only at ordering barriers before hardlinks, directory metadata, or TREE_END.
- Compare workers `0/1/2/4/8` in paired samples, then repeat the selected candidate under checksum and strict durability.

## Round 60 result

On the tested host with 10000 small files and four pairs, worker 1 regressed against worker 0, worker 4 had the best average throughput in the baseline matrix, and worker 8 did not improve over worker 4. The safe disposition was to keep default worker 0 and use worker 4 only as an explicit deployment candidate.

This result is workload- and storage-dependent; repeat the paired matrix on the target host before changing defaults.
