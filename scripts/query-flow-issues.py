#!/usr/bin/env python3
"""Query compact Flow Issue backlog summaries or expand one issue's events."""

from __future__ import annotations

import argparse
from pathlib import Path

from flow_issues import FlowIssueError, query_occurrences, resolve_root, run_command


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise FlowIssueError("INVALID_ARGUMENT", "/", message)


def main() -> int:
    def command() -> dict:
        parser = Parser()
        parser.add_argument("--limit", type=int, default=20)
        parser.add_argument("--cursor")
        parser.add_argument("--issue-id")
        parser.add_argument("--root", type=Path)
        args = parser.parse_args()
        if args.cursor and args.issue_id:
            raise FlowIssueError("INVALID_ARGUMENT", "--cursor", "cannot be combined with --issue-id")
        return query_occurrences(
            resolve_root(args.root),
            limit=args.limit,
            cursor=args.cursor,
            issue_id=args.issue_id,
        )

    return run_command(command)


if __name__ == "__main__":
    raise SystemExit(main())
