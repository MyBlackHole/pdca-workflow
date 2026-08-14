# T0251 Triage Brief

## Classification

- Category: enhancement / production observability
- Scenario: development
- Priority: high; logs are required to operate and diagnose the large-tree incremental/resume paths.

## Verified Gap

- `backupctl.cpp`, `backup_agent.cpp`, data-lane runtime and TLS runtime write operational state directly to `std::cerr`.
- There is no common level, timestamp, component, event, sink, JSON escaping, or file rotation contract.
- Existing metadata incremental and TREE checkpoint paths expose useful counters only as ad-hoc progress text.
- TREE checkpoint currently stores confirmed paths in an in-memory `unordered_map`; this is a separate follow-up scalability slice, not silently included in this round.

## Recommended Slice

Introduce a small dependency-free logging module, wire it into both entrypoints and the highest-value transfer lifecycle/error points, retain text output by default, and add JSONL/file configuration for production collection.

## Deduplication

T0250 covers the missing external `MDB_VL32` LMDB branch. Existing rounds cover transfer metrics, but none provide a common logging abstraction or persistent structured event sink.
