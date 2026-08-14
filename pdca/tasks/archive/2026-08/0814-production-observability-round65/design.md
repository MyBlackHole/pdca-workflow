# T0251 Design: Structured Logging Boundary

The logger is a process-local, dependency-free service with one mutex protecting sink state and complete-line writes. Callers submit a bounded event containing a level, component, event name, message, and a small whitelist of string/numeric fields. The logger formats either stable text or JSONL, writes to stderr and optionally an append-only `0600` file, and rotates the file before it exceeds the configured byte limit.

The logger never receives authentication tokens. Transfer code emits identifiers and counters rather than raw credentials. Failure to write a log line is best-effort: the transfer operation continues, while the logger falls back to stderr once per sink failure.
