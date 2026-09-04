#!/usr/bin/env python3
# 本体投射[T2053]：ontology:domain/skill-wayfinder（决策票认领状态机）；本体是源、代码是投射。
"""Wayfinder ticket claim 状态机（T0265）。

维护 wayfinding 决策票的认领状态，防止并发 session 重复处理同一张票。
状态记录在 tickets/claims.jsonl（每行一个 claim 事件）。

用法：
  check-ticket-claims.py claim   --ticket TK-1 --by sess-a
  check-ticket-claims.py resolve --ticket TK-1 --by sess-a
  check-ticket-claims.py status  --ticket TK-1   # 可选：查询当前状态
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def default_claims_path() -> Path:
    root = os.environ.get("PDCA_HOME") or Path.cwd()
    return Path(root) / "tickets" / "claims.jsonl"


def load_claims(path: Path) -> list[dict]:
    if not path.exists():
        return []
    claims: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            claims.append(json.loads(line))
    return claims


def current_state(claims: list[dict], ticket: str) -> dict | None:
    """按事件顺序重放，返回该票当前 claim 状态；无记录返回 None。"""
    state: dict | None = None
    for ev in claims:
        if ev.get("ticket") != ticket:
            continue
        state = ev
    return state


def append_event(path: Path, event: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def cmd_claim(args: argparse.Namespace) -> int:
    claims_path = Path(args.claims) if args.claims else default_claims_path()
    claims = load_claims(claims_path)
    state = current_state(claims, args.ticket)
    if state is not None and state.get("action") == "claim":
        sys.stderr.write(
            f"ALREADY_CLAIMED: ticket {args.ticket} is claimed by "
            f"{state.get('claimed_by')} and not yet resolved\n"
        )
        return 1
    event = {
        "action": "claim",
        "ticket": args.ticket,
        "claimed_by": args.by,
        "state": "in-progress",
        "status": "claimed",
        "at": datetime.now(timezone.utc).isoformat(),
    }
    append_event(claims_path, event)
    print(json.dumps(event, ensure_ascii=False))
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    claims_path = Path(args.claims) if args.claims else default_claims_path()
    claims = load_claims(claims_path)
    state = current_state(claims, args.ticket)
    if state is None or state.get("action") != "claim":
        sys.stderr.write(f"NOT_CLAIMED: ticket {args.ticket} has no active claim\n")
        return 1
    if state.get("claimed_by") != args.by:
        sys.stderr.write(
            f"NOT_CLAIMANT: ticket {args.ticket} is claimed by "
            f"{state.get('claimed_by')}, not {args.by}\n"
        )
        return 1
    event = {
        "action": "resolve",
        "ticket": args.ticket,
        "claimed_by": args.by,
        "state": "resolved",
        "at": datetime.now(timezone.utc).isoformat(),
    }
    append_event(claims_path, event)
    print(json.dumps(event, ensure_ascii=False))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    claims_path = Path(args.claims) if args.claims else default_claims_path()
    claims = load_claims(claims_path)
    state = current_state(claims, args.ticket)
    if state is None:
        print(json.dumps({"ticket": args.ticket, "state": "unclaimed"}))
        return 0
    print(json.dumps(state, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tickets", dest="claims", help="claims.jsonl 路径（默认 tickets/claims.jsonl）")
    sub = parser.add_subparsers(dest="command", required=True)

    claim = sub.add_parser("claim", help="认领一张票")
    claim.add_argument("--ticket", required=True)
    claim.add_argument("--by", required=True)
    claim.set_defaults(func=cmd_claim)

    resolve = sub.add_parser("resolve", help="解决并清除认领")
    resolve.add_argument("--ticket", required=True)
    resolve.add_argument("--by", required=True)
    resolve.set_defaults(func=cmd_resolve)

    status = sub.add_parser("status", help="查询票的当前状态")
    status.add_argument("--ticket", required=True)
    status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
