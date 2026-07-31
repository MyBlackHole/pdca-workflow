#!/usr/bin/env python3
"""Record a user-confirmed immutable Flow Issue governance decision."""

from __future__ import annotations

import argparse
from pathlib import Path

from flow_issues import FlowIssueError, create_decision, resolve_root, run_command


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise FlowIssueError("INVALID_ARGUMENT", "/", message)


def main() -> int:
    def command() -> dict:
        parser = Parser()
        parser.add_argument("--record", required=True)
        parser.add_argument("--issue-id", required=True)
        parser.add_argument("--candidate-id")
        parser.add_argument("--action", required=True)
        parser.add_argument("--reason", required=True)
        parser.add_argument("--impact")
        parser.add_argument("--idempotency-key", required=True)
        parser.add_argument("--decided-at", required=True)
        parser.add_argument("--confirmation-task-id", required=True)
        parser.add_argument("--confirmation-source", required=True)
        parser.add_argument("--confirmation-at", required=True)
        parser.add_argument("--confirmed-by", required=True)
        parser.add_argument("--root", type=Path)
        args = parser.parse_args()
        return create_decision(
            resolve_root(args.root),
            record_id=args.record,
            issue_id=args.issue_id,
            candidate_id=args.candidate_id,
            action=args.action,
            reason=args.reason,
            impact=args.impact,
            idempotency_key=args.idempotency_key,
            decided_at=args.decided_at,
            confirmation_task_id=args.confirmation_task_id,
            confirmation_source=args.confirmation_source,
            confirmation_at=args.confirmation_at,
            confirmed_by=args.confirmed_by,
        )

    return run_command(command)


if __name__ == "__main__":
    raise SystemExit(main())
