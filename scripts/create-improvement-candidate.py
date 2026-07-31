#!/usr/bin/env python3
"""Create a dry-run Flow Improvement candidate without changing any task."""

from __future__ import annotations

import argparse
from pathlib import Path

from flow_issues import FlowIssueError, create_candidate, resolve_root, run_command


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise FlowIssueError("INVALID_ARGUMENT", "/", message)


def main() -> int:
    def command() -> dict:
        parser = Parser()
        parser.add_argument("--record", required=True)
        parser.add_argument("--issue-id", required=True)
        parser.add_argument("--event-id", action="append", default=[])
        parser.add_argument("--idempotency-key", required=True)
        parser.add_argument("--created-at", required=True)
        parser.add_argument("--root-cause", required=True)
        parser.add_argument("--target-component", required=True)
        parser.add_argument("--baseline", required=True)
        parser.add_argument("--metric", action="append", default=[])
        parser.add_argument("--risk", action="append", default=[])
        parser.add_argument("--rule-id", required=True)
        parser.add_argument("--rule-version", required=True)
        parser.add_argument("--min-opportunities", required=True, type=int)
        parser.add_argument("--max-observation-days", required=True, type=int)
        parser.add_argument("--root", type=Path)
        args = parser.parse_args()
        return create_candidate(
            resolve_root(args.root),
            record_id=args.record,
            issue_id=args.issue_id,
            event_ids=args.event_id,
            idempotency_key=args.idempotency_key,
            created_at=args.created_at,
            root_cause_hypothesis=args.root_cause,
            target_component=args.target_component,
            baseline=args.baseline,
            metrics=args.metric,
            risks=args.risk,
            rule_id=args.rule_id,
            rule_version=args.rule_version,
            min_opportunities=args.min_opportunities,
            max_observation_days=args.max_observation_days,
        )

    return run_command(command)


if __name__ == "__main__":
    raise SystemExit(main())
