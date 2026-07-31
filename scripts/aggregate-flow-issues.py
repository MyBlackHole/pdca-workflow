#!/usr/bin/env python3
"""Build the deterministic Flow Issue backlog projection."""

from __future__ import annotations

import argparse
from pathlib import Path

from flow_issues import FlowIssueError, aggregate_occurrences, resolve_root, run_command


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise FlowIssueError("INVALID_ARGUMENT", "/", message)


def main() -> int:
    def command() -> dict:
        parser = Parser()
        parser.add_argument("--projection-version", default="v1")
        parser.add_argument("--fingerprint-version", default="v1")
        parser.add_argument("--root", type=Path)
        args = parser.parse_args()
        return aggregate_occurrences(
            resolve_root(args.root),
            projection_version=args.projection_version,
            fingerprint_version=args.fingerprint_version,
        )

    return run_command(command)


if __name__ == "__main__":
    raise SystemExit(main())
