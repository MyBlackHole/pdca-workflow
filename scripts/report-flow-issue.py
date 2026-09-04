#!/usr/bin/env python3
# 本体投射[T2053]：ontology:concept/pdca-continuous-improvement（occurrence 上报接缝）；本体是源、代码是投射。
"""Report one immutable Flow Issue occurrence through the public CLI seam."""

from __future__ import annotations

import argparse
from pathlib import Path

from flow_issues import FlowIssueError, create_occurrence, resolve_root, run_command


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise FlowIssueError("INVALID_ARGUMENT", "/", message)


def main() -> int:
    def command() -> dict:
        parser = Parser()
        parser.add_argument("--record", required=True)
        parser.add_argument("--task-id", required=True)
        parser.add_argument("--source", required=True)
        parser.add_argument("--category", required=True)
        parser.add_argument("--phase", required=True)
        parser.add_argument("--transition")
        parser.add_argument("--rule-id", default="manual-report")
        parser.add_argument("--rule-version", default="v1")
        parser.add_argument("--affected-component", required=True)
        parser.add_argument("--normalized-location", required=True)
        parser.add_argument("--issue-code", required=True)
        parser.add_argument("--idempotency-key", required=True)
        parser.add_argument("--occurred-at", required=True)
        parser.add_argument("--evidence-ref", action="append", default=[])
        parser.add_argument("--confidence", default="observed")
        parser.add_argument("--gate-effect", default="unknown")
        parser.add_argument("--exit-code", type=int)
        parser.add_argument("--before-state")
        parser.add_argument("--after-state")
        parser.add_argument("--summary")
        parser.add_argument("--root", type=Path)
        args = parser.parse_args()
        return create_occurrence(
            resolve_root(args.root),
            record_id=args.record,
            task_id=args.task_id,
            source=args.source,
            category=args.category,
            phase=args.phase,
            transition=args.transition,
            rule_id=args.rule_id,
            rule_version=args.rule_version,
            affected_component=args.affected_component,
            normalized_location=args.normalized_location,
            issue_code=args.issue_code,
            idempotency_key=args.idempotency_key,
            occurred_at=args.occurred_at,
            evidence_refs=args.evidence_ref,
            confidence=args.confidence,
            gate_effect=args.gate_effect,
            exit_code=args.exit_code,
            before_state=args.before_state,
            after_state=args.after_state,
            summary=args.summary,
        )

    return run_command(command)


if __name__ == "__main__":
    raise SystemExit(main())
