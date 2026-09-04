#!/usr/bin/env python3
# 本体投射[T2053]：ontology:concept/pdca-continuous-improvement（候选晋级正式任务）；本体是源、代码是投射。
"""Create a strict Plan-phase Improvement Task from an authorized candidate."""

from __future__ import annotations

import argparse
from pathlib import Path

from flow_issues import FlowIssueError, promote_candidate, resolve_root, run_command


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise FlowIssueError("INVALID_ARGUMENT", "/", message)


def main() -> int:
    def command() -> dict:
        parser = Parser()
        parser.add_argument("--record", required=True)
        parser.add_argument("--candidate-id", required=True)
        parser.add_argument("--decision-id", required=True)
        parser.add_argument("--slug", required=True)
        parser.add_argument("--title", required=True)
        parser.add_argument("--created-at", required=True)
        parser.add_argument("--root", type=Path)
        args = parser.parse_args()
        return promote_candidate(
            resolve_root(args.root),
            record_id=args.record,
            candidate_id=args.candidate_id,
            decision_id=args.decision_id,
            slug=args.slug,
            title=args.title,
            created_at=args.created_at,
        )

    return run_command(command)


if __name__ == "__main__":
    raise SystemExit(main())
