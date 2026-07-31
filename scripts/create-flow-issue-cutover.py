#!/usr/bin/env python3
"""Create the immutable Flow Issue v1 cutover receipt."""

from __future__ import annotations

import argparse
from pathlib import Path

from flow_issues import FlowIssueError, create_cutover, resolve_root, run_command


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise FlowIssueError("INVALID_ARGUMENT", "/", message)


def main() -> int:
    def command() -> dict:
        parser = Parser()
        parser.add_argument("--commit", required=True)
        parser.add_argument("--started-at", required=True)
        parser.add_argument("--root", type=Path)
        args = parser.parse_args()
        return create_cutover(resolve_root(args.root), args.commit, args.started_at)

    return run_command(command)


if __name__ == "__main__":
    raise SystemExit(main())
