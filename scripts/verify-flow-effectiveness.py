#!/usr/bin/env python3
# 本体投射[T2053]：ontology:concept/pdca-continuous-improvement（效果 verdict 冻结输入）；本体是源、代码是投射。
"""Write a frozen-input Flow Improvement effectiveness verdict."""

from __future__ import annotations

import argparse
from pathlib import Path

from flow_issues import FlowIssueError, resolve_root, run_command, verify_effectiveness


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise FlowIssueError("INVALID_ARGUMENT", "/", message)


def main() -> int:
    def command() -> dict:
        parser = Parser()
        parser.add_argument("--record", required=True)
        parser.add_argument("--candidate-id", required=True)
        parser.add_argument("--idempotency-key", required=True)
        parser.add_argument("--deployment-receipt", required=True)
        parser.add_argument("--deployed-at", required=True)
        parser.add_argument("--observed-at", required=True)
        parser.add_argument("--opportunities", required=True, type=int)
        parser.add_argument("--observed-metric", action="append", default=[])
        parser.add_argument("--root", type=Path)
        args = parser.parse_args()
        return verify_effectiveness(
            resolve_root(args.root),
            record_id=args.record,
            candidate_id=args.candidate_id,
            idempotency_key=args.idempotency_key,
            deployment_receipt=args.deployment_receipt,
            deployed_at=args.deployed_at,
            observed_at=args.observed_at,
            opportunities=args.opportunities,
            observed_metrics=args.observed_metric,
        )

    return run_command(command)


if __name__ == "__main__":
    raise SystemExit(main())
