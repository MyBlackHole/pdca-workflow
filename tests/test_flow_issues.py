from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FlowIssueCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "flows/flow-plan").mkdir(parents=True)
        (self.root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")
        shutil.copytree(ROOT / "schemas", self.root / "schemas")
        (self.root / "records").mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_cli(self, script: str, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(ROOT / "scripts" / script),
                *arguments,
                "--root",
                str(self.root),
            ],
            capture_output=True,
            text=True,
        )

    def create_cutover(self) -> None:
        completed = self.run_cli(
            "create-flow-issue-cutover.py",
            "--commit",
            "a" * 40,
            "--started-at",
            "2026-07-30T19:00:00+08:00",
        )
        self.assertEqual(0, completed.returncode, completed.stderr)

    def report_arguments(self, *overrides: str) -> list[str]:
        return [
            "--record",
            "R9001",
            "--task-id",
            "T9001",
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
            "user-mid-phase-1",
            "--occurred-at",
            "2026-07-30T19:01:00+08:00",
            "--evidence-ref",
            "conversation:issue-1",
            *overrides,
        ]

    def create_confirmation_task(
        self,
        *,
        task_id: str = "T9003",
        action: str,
        issue_id: str,
        candidate_id: str | None,
    ) -> tuple[Path, str]:
        slug = f"0730-user-decision-{task_id[1:]}"
        task_dir = self.root / "pdca/tasks/active" / slug
        task_dir.mkdir(parents=True, exist_ok=True)
        confirmed_at = "2026-07-30T19:05:00+08:00"
        task = {
            "id": task_id,
            "slug": slug,
            "title": "user decision fixture",
            "parent": None,
            "children": [],
            "status": "Pending",
            "meta": {
                "phase": "plan",
                "active": True,
                "scenario_type": "development",
                "created_at": "2026-07-30T19:00:00+08:00",
                "convergence": ["user decision is traceable"],
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
                    "summary": "promote the reviewed candidate",
                    "response": "confirmed",
                    "decision": {
                        "action": action,
                        "issue_id": issue_id,
                        "candidate_id": candidate_id,
                    },
                    "at": confirmed_at,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return task_dir, confirmed_at

    def test_report_flow_issue_creates_a_schema_valid_immutable_occurrence(self) -> None:
        self.create_cutover()
        completed = self.run_cli("report-flow-issue.py", *self.report_arguments())

        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("created", payload["status"])
        self.assertRegex(payload["event_id"], r"^FE-[0-9a-f]{24}$")
        self.assertTrue(payload["path"].startswith("records/R9001/flow-events/"))

        occurrence_path = self.root / payload["path"]
        occurrence = json.loads(occurrence_path.read_text(encoding="utf-8"))
        self.assertEqual("pdca.flow-issue-occurrence/v1", occurrence["schema"])
        self.assertEqual("user", occurrence["source"])
        self.assertEqual("tooling-failure", occurrence["category"])
        self.assertNotIn("impact", occurrence)
        self.assertNotIn("status", occurrence)

    def test_report_is_idempotent_and_rejects_content_reuse_of_the_same_key(self) -> None:
        self.create_cutover()
        first = self.run_cli("report-flow-issue.py", *self.report_arguments())
        self.assertEqual(0, first.returncode, first.stderr)
        created = json.loads(first.stdout)

        retry = self.run_cli("report-flow-issue.py", *self.report_arguments())
        self.assertEqual(0, retry.returncode, retry.stderr)
        unchanged = json.loads(retry.stdout)
        self.assertEqual("unchanged", unchanged["status"])
        self.assertEqual(created["event_id"], unchanged["event_id"])
        self.assertEqual(created["digest"], unchanged["digest"])

        conflict = self.run_cli(
            "report-flow-issue.py",
            *self.report_arguments("--category", "capability-gap"),
        )
        self.assertNotEqual(0, conflict.returncode)
        rejected = json.loads(conflict.stdout)
        self.assertEqual("IDEMPOTENCY_CONFLICT", rejected["error"])

        occurrence = json.loads((self.root / created["path"]).read_text(encoding="utf-8"))
        self.assertEqual("tooling-failure", occurrence["category"])

    def test_report_rejects_path_escape_before_writing_any_occurrence(self) -> None:
        self.create_cutover()
        unsafe_record = self.run_cli(
            "report-flow-issue.py",
            *self.report_arguments("--record", "../outside"),
        )
        self.assertNotEqual(0, unsafe_record.returncode)
        self.assertEqual("PATH_INVALID", json.loads(unsafe_record.stdout)["error"])
        self.assertFalse((self.root / "outside").exists())

        unsafe_location = self.run_cli(
            "report-flow-issue.py",
            *self.report_arguments("--normalized-location", "../task.json"),
        )
        self.assertNotEqual(0, unsafe_location.returncode)
        self.assertEqual("PATH_INVALID", json.loads(unsafe_location.stdout)["error"])
        self.assertFalse((self.root / "records/R9001/flow-events").exists())

    def test_cutover_routes_transition_audit_failures_to_new_immutable_events(self) -> None:
        self.create_cutover()
        record_dir = self.root / "records/R9002"
        record_dir.mkdir()
        historical_audit = record_dir / "flow-audit.json"
        historical_audit.write_text(
            json.dumps({"schema": "pdca.flow-audit/v1", "historical": True}) + "\n",
            encoding="utf-8",
        )
        before = historical_audit.read_bytes()

        task_dir = self.root / "pdca/tasks/active/0730-cutover-audit"
        task_dir.mkdir(parents=True)
        task = {
            "id": "T9002",
            "slug": "0730-cutover-audit",
            "title": "cutover fixture",
            "parent": None,
            "children": [],
            "status": "Pending",
            "meta": {
                "phase": "plan",
                "active": True,
                "scenario_type": "development",
                "created_at": "2026-07-30T18:00:00+08:00",
                "convergence": ["cutover routes audit events"],
                "record": "R9002",
            },
            "states": {
                "created": "2026-07-30T18:00:00+08:00",
                "plan": "2026-07-30T18:00:00+08:00",
                "do": None,
                "check": None,
                "act": None,
                "archive": None,
            },
        }
        (task_dir / "task.json").write_text(json.dumps(task), encoding="utf-8")
        (task_dir / "clarifications.jsonl").write_text("", encoding="utf-8")

        completed = subprocess.run(
            [
                "python3",
                str(ROOT / "scripts/transition-phase.py"),
                str(task_dir),
                "--to",
                "do",
                "--root",
                str(self.root),
            ],
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(0, completed.returncode)
        self.assertEqual(before, historical_audit.read_bytes())
        events = list((record_dir / "flow-events").glob("*.json"))
        self.assertEqual(1, len(events))
        occurrence = json.loads(events[0].read_text(encoding="utf-8"))
        self.assertEqual("transition-audit", occurrence["source"])
        self.assertEqual("plan-to-do", occurrence["transition"])
        self.assertEqual("FINAL_CONFIRMATION_MISSING", occurrence["issue_code"])

    def test_aggregate_and_query_keep_fingerprint_boundaries_and_output_stable(self) -> None:
        self.create_cutover()
        first = self.run_cli("report-flow-issue.py", *self.report_arguments())
        self.assertEqual(0, first.returncode, first.stderr)
        second = self.run_cli(
            "report-flow-issue.py",
            *self.report_arguments(
                "--record",
                "R9002",
                "--task-id",
                "T9002",
                "--idempotency-key",
                "same-fingerprint-second-event",
                "--occurred-at",
                "2026-07-30T19:02:00+08:00",
            ),
        )
        self.assertEqual(0, second.returncode, second.stderr)
        different_component = self.run_cli(
            "report-flow-issue.py",
            *self.report_arguments(
                "--idempotency-key",
                "different-component",
                "--affected-component",
                "scripts.flow-audit",
                "--occurred-at",
                "2026-07-30T19:03:00+08:00",
            ),
        )
        self.assertEqual(0, different_component.returncode, different_component.stderr)
        different_rule = self.run_cli(
            "report-flow-issue.py",
            *self.report_arguments(
                "--idempotency-key",
                "different-rule-version",
                "--rule-version",
                "v2",
                "--occurred-at",
                "2026-07-30T19:04:00+08:00",
            ),
        )
        self.assertEqual(0, different_rule.returncode, different_rule.stderr)

        aggregated = self.run_cli("aggregate-flow-issues.py")
        self.assertEqual(0, aggregated.returncode, aggregated.stderr)
        first_projection = json.loads(aggregated.stdout)
        self.assertEqual("generated", first_projection["status"])
        self.assertEqual(3, first_projection["issue_count"])
        backlog_path = self.root / first_projection["path"]
        first_bytes = backlog_path.read_bytes()
        backlog = json.loads(first_bytes)
        self.assertEqual([2, 1, 1], [issue["event_count"] for issue in backlog["issues"]])

        repeated = self.run_cli("aggregate-flow-issues.py")
        self.assertEqual(0, repeated.returncode, repeated.stderr)
        self.assertEqual(first_projection["digest"], json.loads(repeated.stdout)["digest"])
        self.assertEqual(first_bytes, backlog_path.read_bytes())

        page = self.run_cli("query-flow-issues.py", "--limit", "1")
        self.assertEqual(0, page.returncode, page.stderr)
        listing = json.loads(page.stdout)
        self.assertEqual(1, len(listing["issues"]))
        self.assertIsNotNone(listing["next_cursor"])
        self.assertNotIn("event_paths", listing["issues"][0])

        issue_id = backlog["issues"][0]["issue_id"]
        expanded = self.run_cli("query-flow-issues.py", "--issue-id", issue_id)
        self.assertEqual(0, expanded.returncode, expanded.stderr)
        detail = json.loads(expanded.stdout)
        self.assertEqual(issue_id, detail["issue"]["issue_id"])
        self.assertEqual(2, len(detail["occurrences"]))

    def test_aggregate_fails_closed_for_a_corrupt_event_file(self) -> None:
        self.create_cutover()
        reported = self.run_cli("report-flow-issue.py", *self.report_arguments())
        self.assertEqual(0, reported.returncode, reported.stderr)
        bad_event = self.root / "records/R9001/flow-events/FE-corrupt.json"
        bad_event.write_text("{not-json}\n", encoding="utf-8")

        aggregated = self.run_cli("aggregate-flow-issues.py")
        self.assertNotEqual(0, aggregated.returncode)
        rejected = json.loads(aggregated.stdout)
        self.assertEqual("EVENT_CORRUPT", rejected["error"])
        self.assertTrue(rejected["path"].endswith("FE-corrupt.json"))

    def test_candidate_needs_confirmed_decision_before_it_can_create_a_plan_task(self) -> None:
        self.create_cutover()
        reported = self.run_cli("report-flow-issue.py", *self.report_arguments())
        self.assertEqual(0, reported.returncode, reported.stderr)
        event = json.loads(reported.stdout)
        aggregated = self.run_cli("aggregate-flow-issues.py")
        self.assertEqual(0, aggregated.returncode, aggregated.stderr)
        issue_id = json.loads((self.root / json.loads(aggregated.stdout)["path"]).read_text())["issues"][0]["issue_id"]

        candidate = self.run_cli(
            "create-improvement-candidate.py",
            "--record",
            "R9001",
            "--issue-id",
            issue_id,
            "--event-id",
            event["event_id"],
            "--idempotency-key",
            "candidate-1",
            "--created-at",
            "2026-07-30T19:04:00+08:00",
            "--root-cause",
            "the public transition write path is not recoverable",
            "--target-component",
            "scripts.transition-phase",
            "--baseline",
            "10 failures per 100 attempts",
            "--metric",
            "failure-rate:10:5",
            "--risk",
            "a stricter gate can reject valid transitions",
            "--rule-id",
            "manual-report",
            "--rule-version",
            "v1",
            "--min-opportunities",
            "3",
            "--max-observation-days",
            "14",
        )
        self.assertEqual(0, candidate.returncode, candidate.stderr)
        candidate_payload = json.loads(candidate.stdout)
        self.assertEqual("dry-run", candidate_payload["candidate"]["status"])
        self.assertFalse((self.root / "pdca/tasks/active/0730-promoted-improvement").exists())

        _wrong_confirmation_task, wrong_confirmed_at = self.create_confirmation_task(
            task_id="T9004",
            action="close",
            issue_id=issue_id,
            candidate_id=None,
        )
        wrong_binding = self.run_cli(
            "decide-flow-issue.py",
            "--record",
            "R9001",
            "--issue-id",
            issue_id,
            "--candidate-id",
            candidate_payload["candidate_id"],
            "--action",
            "promote-candidate",
            "--reason",
            "candidate has an acceptable observation plan",
            "--idempotency-key",
            "wrong-binding",
            "--decided-at",
            "2026-07-30T19:06:00+08:00",
            "--confirmation-task-id",
            "T9004",
            "--confirmation-source",
            "user_decision",
            "--confirmation-at",
            wrong_confirmed_at,
            "--confirmed-by",
            "workflow-owner",
        )
        self.assertNotEqual(0, wrong_binding.returncode)
        self.assertEqual("CONFIRMATION_INVALID", json.loads(wrong_binding.stdout)["error"])

        _confirmation_task, confirmed_at = self.create_confirmation_task(
            action="promote-candidate",
            issue_id=issue_id,
            candidate_id=candidate_payload["candidate_id"],
        )
        rejected_decision = self.run_cli(
            "decide-flow-issue.py",
            "--record",
            "R9001",
            "--issue-id",
            issue_id,
            "--candidate-id",
            candidate_payload["candidate_id"],
            "--action",
            "promote-candidate",
            "--reason",
            "candidate has an acceptable observation plan",
            "--idempotency-key",
            "decision-1",
            "--decided-at",
            "2026-07-30T19:06:00+08:00",
            "--confirmation-task-id",
            "T9003",
            "--confirmation-source",
            "user_decision",
            "--confirmation-at",
            "2026-07-30T19:05:01+08:00",
            "--confirmed-by",
            "workflow-owner",
        )
        self.assertNotEqual(0, rejected_decision.returncode)
        self.assertEqual("CONFIRMATION_INVALID", json.loads(rejected_decision.stdout)["error"])

        decision = self.run_cli(
            "decide-flow-issue.py",
            "--record",
            "R9001",
            "--issue-id",
            issue_id,
            "--candidate-id",
            candidate_payload["candidate_id"],
            "--action",
            "promote-candidate",
            "--reason",
            "candidate has an acceptable observation plan",
            "--idempotency-key",
            "decision-1",
            "--decided-at",
            "2026-07-30T19:06:00+08:00",
            "--confirmation-task-id",
            "T9003",
            "--confirmation-source",
            "user_decision",
            "--confirmation-at",
            confirmed_at,
            "--confirmed-by",
            "workflow-owner",
        )
        self.assertEqual(0, decision.returncode, decision.stderr)
        decision_payload = json.loads(decision.stdout)
        self.assertEqual("promote-candidate", decision_payload["decision"]["action"])

        promoted = self.run_cli(
            "promote-improvement-candidate.py",
            "--record",
            "R9001",
            "--candidate-id",
            candidate_payload["candidate_id"],
            "--decision-id",
            decision_payload["decision_id"],
            "--slug",
            "0730-promoted-improvement",
            "--title",
            "Promoted improvement fixture",
            "--created-at",
            "2026-07-30T19:07:00+08:00",
        )
        self.assertEqual(0, promoted.returncode, promoted.stderr)
        promoted_payload = json.loads(promoted.stdout)
        promoted_task = self.root / promoted_payload["path"] / "task.json"
        task = json.loads(promoted_task.read_text(encoding="utf-8"))
        self.assertEqual("plan", task["meta"]["phase"])
        self.assertEqual(candidate_payload["candidate_id"], task["meta"]["improvement_source"]["candidate_id"])
        clarifications = (promoted_task.parent / "clarifications.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("final_confirmation", clarifications)

    def test_effectiveness_verdict_generates_only_the_allowed_follow_up_artifact(self) -> None:
        self.create_cutover()
        reported = self.run_cli("report-flow-issue.py", *self.report_arguments())
        self.assertEqual(0, reported.returncode, reported.stderr)
        event = json.loads(reported.stdout)
        aggregated = self.run_cli("aggregate-flow-issues.py")
        self.assertEqual(0, aggregated.returncode, aggregated.stderr)
        issue_id = json.loads((self.root / json.loads(aggregated.stdout)["path"]).read_text())["issues"][0]["issue_id"]

        def candidate(key: str, created_at: str) -> dict:
            completed = self.run_cli(
                "create-improvement-candidate.py",
                "--record",
                "R9001",
                "--issue-id",
                issue_id,
                "--event-id",
                event["event_id"],
                "--idempotency-key",
                key,
                "--created-at",
                created_at,
                "--root-cause",
                "the transition path needs a recoverable write",
                "--target-component",
                "scripts.transition-phase",
                "--baseline",
                "10 failures per 100 attempts",
                "--metric",
                "failure-rate:10:5",
                "--risk",
                "a stricter gate can reject valid transitions",
                "--rule-id",
                "manual-report",
                "--rule-version",
                "v1",
                "--min-opportunities",
                "3",
                "--max-observation-days",
                "14",
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            return json.loads(completed.stdout)

        improved_candidate = candidate("candidate-improved", "2026-07-30T19:04:00+08:00")
        improved = self.run_cli(
            "verify-flow-effectiveness.py",
            "--record",
            "R9001",
            "--candidate-id",
            improved_candidate["candidate_id"],
            "--idempotency-key",
            "verdict-improved",
            "--deployment-receipt",
            "deployment:T9004",
            "--deployed-at",
            "2026-07-30T19:05:00+08:00",
            "--observed-at",
            "2026-07-30T19:06:00+08:00",
            "--opportunities",
            "3",
            "--observed-metric",
            "failure-rate:4",
        )
        self.assertEqual(0, improved.returncode, improved.stderr)
        improved_payload = json.loads(improved.stdout)
        self.assertEqual("improved", improved_payload["verdict"]["outcome"])
        self.assertEqual("verified-decision", improved_payload["follow_up"]["kind"])
        verified = json.loads((self.root / improved_payload["follow_up"]["path"]).read_text())
        self.assertEqual("verified", verified["action"])

        neutral_candidate = candidate("candidate-neutral", "2026-07-30T19:07:00+08:00")
        neutral = self.run_cli(
            "verify-flow-effectiveness.py",
            "--record",
            "R9001",
            "--candidate-id",
            neutral_candidate["candidate_id"],
            "--idempotency-key",
            "verdict-neutral",
            "--deployment-receipt",
            "deployment:T9005",
            "--deployed-at",
            "2026-07-30T19:08:00+08:00",
            "--observed-at",
            "2026-07-30T19:09:00+08:00",
            "--opportunities",
            "3",
            "--observed-metric",
            "failure-rate:7",
        )
        self.assertEqual(0, neutral.returncode, neutral.stderr)
        self.assertEqual("neutral", json.loads(neutral.stdout)["verdict"]["outcome"])
        self.assertEqual("retriage", json.loads(neutral.stdout)["follow_up"]["kind"])

        regressed_candidate = candidate("candidate-regressed", "2026-07-30T19:10:00+08:00")
        regressed = self.run_cli(
            "verify-flow-effectiveness.py",
            "--record",
            "R9001",
            "--candidate-id",
            regressed_candidate["candidate_id"],
            "--idempotency-key",
            "verdict-regressed",
            "--deployment-receipt",
            "deployment:T9006",
            "--deployed-at",
            "2026-07-30T19:11:00+08:00",
            "--observed-at",
            "2026-07-30T19:12:00+08:00",
            "--opportunities",
            "3",
            "--observed-metric",
            "failure-rate:12",
        )
        self.assertEqual(0, regressed.returncode, regressed.stderr)
        regressed_payload = json.loads(regressed.stdout)
        self.assertEqual("regressed", regressed_payload["verdict"]["outcome"])
        self.assertEqual("rollback-candidate", regressed_payload["follow_up"]["kind"])
        rollback = json.loads((self.root / regressed_payload["follow_up"]["path"]).read_text())
        self.assertEqual("rollback", rollback["kind"])
        self.assertEqual("pending-confirmation", rollback["status"])
        self.assertFalse((self.root / "pdca/tasks/active").exists())

    def test_aggregate_orders_occurrences_by_instant_not_timestamp_text(self) -> None:
        self.create_cutover()
        first = self.run_cli(
            "report-flow-issue.py",
            *self.report_arguments(
                "--idempotency-key",
                "offset-earlier",
                "--occurred-at",
                "2026-07-30T19:30:00+08:00",
            ),
        )
        self.assertEqual(0, first.returncode, first.stderr)
        second = self.run_cli(
            "report-flow-issue.py",
            *self.report_arguments(
                "--idempotency-key",
                "offset-later",
                "--occurred-at",
                "2026-07-30T12:00:00+00:00",
            ),
        )
        self.assertEqual(0, second.returncode, second.stderr)

        aggregated = self.run_cli("aggregate-flow-issues.py")
        self.assertEqual(0, aggregated.returncode, aggregated.stderr)
        backlog = json.loads((self.root / json.loads(aggregated.stdout)["path"]).read_text(encoding="utf-8"))
        issue = backlog["issues"][0]
        self.assertEqual("2026-07-30T19:30:00+08:00", issue["first_occurred_at"])
        self.assertEqual("2026-07-30T12:00:00+00:00", issue["last_occurred_at"])

    def test_concurrent_reports_create_one_occurrence_and_one_unchanged_retry(self) -> None:
        self.create_cutover()
        command = [
            "python3",
            str(ROOT / "scripts/report-flow-issue.py"),
            *self.report_arguments(),
            "--root",
            str(self.root),
        ]
        first = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        second = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        first_stdout, first_stderr = first.communicate()
        second_stdout, second_stderr = second.communicate()

        self.assertEqual(0, first.returncode, first_stderr)
        self.assertEqual(0, second.returncode, second_stderr)
        statuses = sorted(
            [
                json.loads(first_stdout)["status"],
                json.loads(second_stdout)["status"],
            ]
        )
        self.assertEqual(["created", "unchanged"], statuses)
        events = list((self.root / "records/R9001/flow-events").glob("*.json"))
        self.assertEqual(1, len(events))

    def test_concurrent_promotion_creates_one_task_even_with_different_requested_slugs(self) -> None:
        self.create_cutover()
        reported = self.run_cli("report-flow-issue.py", *self.report_arguments())
        self.assertEqual(0, reported.returncode, reported.stderr)
        event = json.loads(reported.stdout)
        aggregated = self.run_cli("aggregate-flow-issues.py")
        self.assertEqual(0, aggregated.returncode, aggregated.stderr)
        issue_id = json.loads((self.root / json.loads(aggregated.stdout)["path"]).read_text())["issues"][0]["issue_id"]
        candidate = self.run_cli(
            "create-improvement-candidate.py",
            "--record",
            "R9001",
            "--issue-id",
            issue_id,
            "--event-id",
            event["event_id"],
            "--idempotency-key",
            "concurrent-promotion-candidate",
            "--created-at",
            "2026-07-30T19:04:00+08:00",
            "--root-cause",
            "promotion must be exclusive",
            "--target-component",
            "scripts.transition-phase",
            "--baseline",
            "10 failures per 100 attempts",
            "--metric",
            "failure-rate:10:5",
            "--risk",
            "duplicate tasks split the evidence chain",
            "--rule-id",
            "manual-report",
            "--rule-version",
            "v1",
            "--min-opportunities",
            "3",
            "--max-observation-days",
            "14",
        )
        self.assertEqual(0, candidate.returncode, candidate.stderr)
        candidate_payload = json.loads(candidate.stdout)
        _task, confirmed_at = self.create_confirmation_task(
            action="promote-candidate",
            issue_id=issue_id,
            candidate_id=candidate_payload["candidate_id"],
        )
        decision = self.run_cli(
            "decide-flow-issue.py",
            "--record",
            "R9001",
            "--issue-id",
            issue_id,
            "--candidate-id",
            candidate_payload["candidate_id"],
            "--action",
            "promote-candidate",
            "--reason",
            "one task is authorized",
            "--idempotency-key",
            "concurrent-promotion-decision",
            "--decided-at",
            "2026-07-30T19:06:00+08:00",
            "--confirmation-task-id",
            "T9003",
            "--confirmation-source",
            "user_decision",
            "--confirmation-at",
            confirmed_at,
            "--confirmed-by",
            "workflow-owner",
        )
        self.assertEqual(0, decision.returncode, decision.stderr)
        decision_payload = json.loads(decision.stdout)

        def command(slug: str) -> list[str]:
            return [
                "python3",
                str(ROOT / "scripts/promote-improvement-candidate.py"),
                "--record",
                "R9001",
                "--candidate-id",
                candidate_payload["candidate_id"],
                "--decision-id",
                decision_payload["decision_id"],
                "--slug",
                slug,
                "--title",
                "Concurrent promotion fixture",
                "--created-at",
                "2026-07-30T19:07:00+08:00",
                "--root",
                str(self.root),
            ]

        first = subprocess.Popen(command("0730-concurrent-a"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        second = subprocess.Popen(command("0730-concurrent-b"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        first_stdout, first_stderr = first.communicate()
        second_stdout, second_stderr = second.communicate()
        self.assertEqual(0, first.returncode, first_stderr)
        self.assertEqual(0, second.returncode, second_stderr)
        self.assertEqual(
            ["created", "unchanged"],
            sorted([json.loads(first_stdout)["status"], json.loads(second_stdout)["status"]]),
        )

        promoted = []
        for task_path in (self.root / "pdca/tasks/active").glob("**/task.json"):
            task = json.loads(task_path.read_text(encoding="utf-8"))
            if task.get("meta", {}).get("improvement_source", {}).get("candidate_id") == candidate_payload["candidate_id"]:
                promoted.append(task)
        self.assertEqual(1, len(promoted))

    def test_flow_issue_fixtures_report_pairing_and_context_bytes(self) -> None:
        completed = subprocess.run(
            ["python3", "scripts/run-flow-issue-fixtures.py", "--all"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(0, payload["failed"])
        self.assertGreater(payload["context_bytes"]["list"], 0)
        self.assertGreater(payload["context_bytes"]["show"], payload["context_bytes"]["list"])
        results = {item["id"]: item for item in payload["results"]}
        self.assertEqual("CUTOVER_MISSING", results["midphase-before-cutover"]["observed"])
        self.assertEqual("created", results["midphase-after-cutover"]["observed"])
        self.assertEqual("created", results["end-to-end-feedback-loop"]["observed"])


if __name__ == "__main__":
    unittest.main()
