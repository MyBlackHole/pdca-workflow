#!/usr/bin/env python3
"""Run deterministic public-CLI fixtures for the Flow Issue feedback loop."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


SOURCE_ROOT = Path(__file__).resolve().parents[1]


def fixture_root(temporary: str) -> Path:
    root = Path(temporary)
    shutil.copytree(SOURCE_ROOT / "schemas", root / "schemas")
    (root / "ontology/process").mkdir(parents=True)
    (root / "ontology/process/flow-plan.md").write_text("# plan\n", encoding="utf-8")
    (root / "records").mkdir()
    return root


def call(root: Path, script: str, *arguments: str) -> tuple[int, dict[str, Any], bytes, str]:
    completed = subprocess.run(
        [
            "python3",
            str(SOURCE_ROOT / "scripts" / script),
            *arguments,
            "--root",
            str(root),
        ],
        capture_output=True,
        text=True,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {
            "status": "rejected",
            "error": "CLI_PROTOCOL_ERROR",
            "message": "CLI did not return one JSON object",
        }
    return completed.returncode, payload, completed.stdout.encode("utf-8"), completed.stderr


def report_arguments(*overrides: str) -> list[str]:
    return [
        "--record",
        "R9901",
        "--task-id",
        "T9901",
        "--source",
        "user",
        "--category",
        "tooling-failure",
        "--phase",
        "do",
        "--affected-component",
        "scripts.transition-phase",
        "--normalized-location",
        "scripts/transition-phase.py:48",
        "--issue-code",
        "TRANSITION_WRITE_FAILED",
        "--idempotency-key",
        "fixture-midphase-event",
        "--occurred-at",
        "2026-07-30T19:01:00+08:00",
        "--evidence-ref",
        "fixture:midphase",
        *overrides,
    ]


def write_confirmation_task(root: Path, issue_id: str, candidate_id: str) -> str:
    task_dir = root / "pdca/tasks/active/0730-fixture-confirmation"
    task_dir.mkdir(parents=True)
    confirmed_at = "2026-07-30T19:05:00+08:00"
    task = {
        "id": "T9902",
        "slug": "0730-fixture-confirmation",
        "title": "fixture confirmation",
        "parent": None,
        "children": [],
        "status": "Pending",
        "meta": {
            "phase": "plan",
            "active": True,
            "scenario_type": "development",
            "created_at": "2026-07-30T19:00:00+08:00",
            "convergence": ["fixture confirmation"],
        },
        "states": {
            "created": "2026-07-30T19:00:00+08:00",
            "plan": "2026-07-30T19:00:00+08:00",
            "do": None,
            "check": None,
            "act": None,
            "archive": None,
        },
    }
    (task_dir / "task.json").write_text(json.dumps(task), encoding="utf-8")
    (task_dir / "clarifications.jsonl").write_text(
        json.dumps(
            {
                "source": "user_decision",
                "summary": "fixture promotion approval",
                "response": "confirmed",
                "decision": {
                    "action": "promote-candidate",
                    "issue_id": issue_id,
                    "candidate_id": candidate_id,
                },
                "at": confirmed_at,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return confirmed_at


def result(identifier: str, expected: str, observed: str) -> dict[str, Any]:
    return {
        "id": identifier,
        "expected": expected,
        "observed": observed,
        "pass": expected == observed,
    }


def run_all() -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    context_bytes = {"list": 0, "show": 0}
    with tempfile.TemporaryDirectory() as temporary:
        root = fixture_root(temporary)

        _code, before, _stdout, _stderr = call(root, "report-flow-issue.py", *report_arguments())
        results.append(result("midphase-before-cutover", "CUTOVER_MISSING", str(before.get("error"))))

        cutover_code, cutover, _stdout, _stderr = call(
            root,
            "create-flow-issue-cutover.py",
            "--commit",
            "b" * 40,
            "--started-at",
            "2026-07-30T19:00:00+08:00",
        )
        results.append(result("cutover-create", "created", str(cutover.get("status") if cutover_code == 0 else cutover.get("error"))))

        report_code, after, _stdout, _stderr = call(root, "report-flow-issue.py", *report_arguments())
        results.append(
            result("midphase-after-cutover", "created", str(after.get("status") if report_code == 0 else after.get("error")))
        )

        retry_code, retry, _stdout, _stderr = call(root, "report-flow-issue.py", *report_arguments())
        results.append(result("idempotent-retry", "unchanged", str(retry.get("status") if retry_code == 0 else retry.get("error"))))

        aggregate_code, aggregate, _stdout, _stderr = call(root, "aggregate-flow-issues.py")
        if aggregate_code == 0:
            issue_id = json.loads((root / aggregate["path"]).read_text(encoding="utf-8"))["issues"][0]["issue_id"]
        else:
            issue_id = ""
        results.append(result("deterministic-projection", "generated", str(aggregate.get("status") if aggregate_code == 0 else aggregate.get("error"))))

        list_code, listing, list_stdout, _stderr = call(root, "query-flow-issues.py", "--limit", "1")
        show_code, shown, show_stdout, _stderr = call(root, "query-flow-issues.py", "--issue-id", issue_id)
        context_bytes = {
            "list": len(list_stdout) if list_code == 0 else 0,
            "show": len(show_stdout) if show_code == 0 else 0,
        }
        results.append(result("compact-query", "ok", str(listing.get("status") if list_code == 0 else listing.get("error"))))

        _code, path_attack, _stdout, _stderr = call(
            root,
            "report-flow-issue.py",
            *report_arguments("--record", "../escape"),
        )
        results.append(result("path-attack", "PATH_INVALID", str(path_attack.get("error"))))

        candidate_code, candidate, _stdout, _stderr = call(
            root,
            "create-improvement-candidate.py",
            "--record",
            "R9901",
            "--issue-id",
            issue_id,
            "--event-id",
            after.get("event_id", ""),
            "--idempotency-key",
            "fixture-candidate",
            "--created-at",
            "2026-07-30T19:04:00+08:00",
            "--root-cause",
            "fixture root cause",
            "--target-component",
            "scripts.transition-phase",
            "--baseline",
            "10 failures per 100 attempts",
            "--metric",
            "failure-rate:10:5",
            "--risk",
            "fixture regression risk",
            "--rule-id",
            "manual-report",
            "--rule-version",
            "v1",
            "--min-opportunities",
            "3",
            "--max-observation-days",
            "14",
        )
        confirmed_at = write_confirmation_task(root, issue_id, candidate.get("candidate_id", ""))
        decision_code, decision, _stdout, _stderr = call(
            root,
            "decide-flow-issue.py",
            "--record",
            "R9901",
            "--issue-id",
            issue_id,
            "--candidate-id",
            candidate.get("candidate_id", ""),
            "--action",
            "promote-candidate",
            "--reason",
            "fixture approval",
            "--idempotency-key",
            "fixture-decision",
            "--decided-at",
            "2026-07-30T19:06:00+08:00",
            "--confirmation-task-id",
            "T9902",
            "--confirmation-source",
            "user_decision",
            "--confirmation-at",
            confirmed_at,
            "--confirmed-by",
            "fixture-owner",
        )
        promotion_code, promotion, _stdout, _stderr = call(
            root,
            "promote-improvement-candidate.py",
            "--record",
            "R9901",
            "--candidate-id",
            candidate.get("candidate_id", ""),
            "--decision-id",
            decision.get("decision_id", ""),
            "--slug",
            "0730-fixture-improvement",
            "--title",
            "Fixture improvement task",
            "--created-at",
            "2026-07-30T19:07:00+08:00",
        )
        verdict_code, verdict, _stdout, _stderr = call(
            root,
            "verify-flow-effectiveness.py",
            "--record",
            "R9901",
            "--candidate-id",
            candidate.get("candidate_id", ""),
            "--idempotency-key",
            "fixture-verdict",
            "--deployment-receipt",
            "deployment:T9903",
            "--deployed-at",
            "2026-07-30T19:08:00+08:00",
            "--observed-at",
            "2026-07-30T19:09:00+08:00",
            "--opportunities",
            "3",
            "--observed-metric",
            "failure-rate:4",
        )
        complete = all(
            [
                candidate_code == 0,
                decision_code == 0,
                promotion_code == 0,
                verdict_code == 0,
                verdict.get("verdict", {}).get("outcome") == "improved",
                verdict.get("follow_up", {}).get("kind") == "verified-decision",
            ]
        )
        results.append(result("end-to-end-feedback-loop", "created", "created" if complete else "failed"))

    return {
        "schema": "pdca.flow-issue-fixture-results/v1",
        "fixture_count": len(results),
        "passed": sum(item["pass"] for item in results),
        "failed": sum(not item["pass"] for item in results),
        "context_bytes": context_bytes,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", required=True)
    args = parser.parse_args()
    payload = run_all()
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
