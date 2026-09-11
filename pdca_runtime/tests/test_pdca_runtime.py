from __future__ import annotations

import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pdca_runtime import (
    ONTOLOGY_ROLES,
    RuntimeContractError,
    bind_agent,
    build_context_manifest,
    derive_execution_state,
    prepare_dispatch_request,
    record_conformance_decision,
    record_agent_result,
    record_user_confirmation,
    resume_for_conformance,
)
from pdca_runtime.cli import build_parser, run
from pdca_runtime.io import digest_file, digest_value
from pdca_runtime.lifecycle import _load_receipts
from pdca_runtime.task import load_executable_task
from pdca_runtime.tests.runtime_fixtures import make_runtime_root, runtime_materials, write_json


def adapter_receipt(task_id: str, request_digest: str, agent_id: str = "agent-fresh-1") -> dict:
    return {
        "task_id": task_id,
        "request_digest": request_digest,
        "agent_id": agent_id,
        "adapter": "native-test-adapter",
        "fresh_context": True,
        "fork_context": False,
    }


def register_fixture_evidence(root: Path, record_id: str) -> str:
    evidence_dir = root / "records" / record_id / "evidence"
    evidence_dir.mkdir(parents=True)
    rows = []
    for index, criterion in enumerate(("AC-1", "AC-2"), 1):
        artifact = evidence_dir / f"runtime-result-{index}.txt"
        artifact.write_text("passed\n", encoding="utf-8")
        rows.append(
            {
                "id": f"runtime-{index}",
                "file": artifact.name,
                "kind": "test",
                "size": artifact.stat().st_size,
                "digest": digest_file(artifact),
                "at": "2026-09-11T10:02:00+08:00",
                "criteria": [criterion],
            }
        )
    manifest = evidence_dir / "manifest.jsonl"
    manifest.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    return manifest.relative_to(root).as_posix()


class PdcaRuntimeLifecycleTest(unittest.TestCase):
    def _bound(self, temporary: str, role: str = "ontology_projection"):
        root, task_dir = make_runtime_root(Path(temporary), role)
        task, projection, projection_path, context, context_path, request = runtime_materials(root, task_dir)
        result = bind_agent(
            root,
            task_dir,
            request,
            adapter_receipt(task.task_id, request["request_digest"]),
            projection,
            context,
        )
        return root, task_dir, task, projection_path, context_path, request, result

    def _pending_review(self, temporary: str):
        root, task_dir, task, projection_path, _, request, _ = self._bound(temporary)
        product = task_dir / "agent-result.md"
        product.write_text("completed\n", encoding="utf-8")
        evidence = register_fixture_evidence(root, task.record_id)
        record_agent_result(
            root,
            task_dir,
            status="completed",
            agent_id="agent-fresh-1",
            request_digest=request["request_digest"],
            artifacts=[projection_path.relative_to(root).as_posix(), product.relative_to(root).as_posix()],
            evidence_manifest=evidence,
        )
        review = resume_for_conformance(root, task_dir)
        return root, task_dir, task, projection_path, product, Path(evidence), review

    def test_each_role_dispatches_and_suspends(self) -> None:
        for role in ONTOLOGY_ROLES:
            with self.subTest(role=role), tempfile.TemporaryDirectory() as temporary:
                root, task_dir, task, _, _, _, result = self._bound(temporary, role)
                self.assertEqual("suspended_waiting_agent", result["status"])
                self.assertEqual("suspended_waiting_agent", derive_execution_state(_load_receipts(task)))
                self.assertEqual(2, len((task_dir / "agent-execution-receipts.jsonl").read_text().splitlines()))

    def test_missing_spawn_fails_without_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir = make_runtime_root(Path(temporary))
            task, projection, _, context, _, _ = runtime_materials(root, task_dir)
            with self.assertRaises(RuntimeContractError) as caught:
                prepare_dispatch_request(task, projection, context, spawn_status="missing")
            self.assertEqual("SPAWN_CAPABILITY_MISSING", caught.exception.code)
            self.assertFalse((task_dir / "agent-execution-receipts.jsonl").exists())

    def test_adapter_attestation_and_stale_request_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir = make_runtime_root(Path(temporary))
            task, projection, _, context, _, request = runtime_materials(root, task_dir)
            bad = adapter_receipt(task.task_id, request["request_digest"])
            bad["fresh_context"] = False
            with self.assertRaises(RuntimeContractError) as caught:
                bind_agent(root, task_dir, request, bad, projection, context)
            self.assertEqual("ADAPTER_CONTEXT_NOT_FRESH", caught.exception.code)
            self.assertFalse((task_dir / "agent-execution-receipts.jsonl").exists())

    def test_context_drift_is_rejected_at_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir = make_runtime_root(Path(temporary))
            task, projection, _, context, _, request = runtime_materials(root, task_dir)
            (task_dir / "prd.md").write_text("changed after request\n", encoding="utf-8")
            with self.assertRaises(RuntimeContractError) as caught:
                bind_agent(
                    root,
                    task_dir,
                    request,
                    adapter_receipt(task.task_id, request["request_digest"]),
                    projection,
                    context,
                )
            self.assertEqual("CONTEXT_FILE_DRIFT", caught.exception.code)
            self.assertFalse((task_dir / "agent-execution-receipts.jsonl").exists())

            stale = dict(request)
            stale["task_id"] = "T9999"
            with self.assertRaises(RuntimeContractError):
                bind_agent(root, task_dir, stale, adapter_receipt("T9999", stale["request_digest"]), projection, context)
            self.assertFalse((task_dir / "agent-execution-receipts.jsonl").exists())

    def test_lock_and_cas_allow_one_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir = make_runtime_root(Path(temporary))
            task, projection, _, context, _, request = runtime_materials(root, task_dir)
            barrier = threading.Barrier(2)

            def attempt(agent_id: str) -> str:
                barrier.wait()
                try:
                    bind_agent(
                        root,
                        task_dir,
                        request,
                        adapter_receipt(task.task_id, request["request_digest"], agent_id),
                        projection,
                        context,
                    )
                    return "bound"
                except RuntimeContractError as exc:
                    return exc.code

            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = sorted(pool.map(attempt, ("agent-a", "agent-b")))
            self.assertEqual(["DISPATCH_CAS_REJECTED", "bound"], outcomes)
            self.assertEqual(2, len((task_dir / "agent-execution-receipts.jsonl").read_text().splitlines()))

    def test_result_binding_confirmation_and_tamper_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir, task, _, _, request, _ = self._bound(temporary)
            waiting = record_agent_result(
                root,
                task_dir,
                status="awaiting_confirmation",
                agent_id="agent-fresh-1",
                request_digest=request["request_digest"],
                message="user decision required",
            )
            self.assertEqual("awaiting_confirmation", waiting["status"])
            with self.assertRaises(RuntimeContractError) as unresolved:
                record_agent_result(
                    root,
                    task_dir,
                    status="completed",
                    agent_id="agent-fresh-1",
                    request_digest=request["request_digest"],
                    artifacts=[f"{task.relative_dir}/projection-manifest.json"],
                    evidence_manifest=f"records/{task.record_id}/evidence/manifest.jsonl",
                )
            self.assertEqual("AGENT_RESULT_STATE_INVALID", unresolved.exception.code)
            with self.assertRaises(RuntimeContractError) as missing:
                record_user_confirmation(root, task_dir, clarification_digest=digest_value({"missing": True}))
            self.assertEqual("USER_CONFIRMATION_MISSING", missing.exception.code)

            non_confirmation = {
                "source": "grilling",
                "answer": "not a confirmation",
                "at": "2026-09-11T11:59:00+08:00",
            }
            (task_dir / "clarifications.jsonl").write_text(
                json.dumps(non_confirmation, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(RuntimeContractError) as invalid_entry:
                record_user_confirmation(root, task_dir, clarification_digest=digest_value(non_confirmation))
            self.assertEqual("USER_CONFIRMATION_ENTRY_INVALID", invalid_entry.exception.code)

            clarification = {
                "source": "fix_confirmation",
                "summary": "user selected the bounded correction",
                "response": "confirmed",
                "at": "2026-09-11T12:00:00+08:00",
            }
            (task_dir / "clarifications.jsonl").write_text(
                json.dumps(non_confirmation, ensure_ascii=False)
                + "\n"
                + json.dumps(clarification, ensure_ascii=False)
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(RuntimeContractError) as forged:
                record_user_confirmation(root, task_dir, clarification_digest=digest_value({"forged": True}))
            self.assertEqual("USER_CONFIRMATION_DIGEST_INVALID", forged.exception.code)
            recorded = record_user_confirmation(root, task_dir, clarification_digest=digest_value(clarification))
            self.assertEqual("suspended_waiting_agent", recorded["status"])
            self.assertEqual("agent-fresh-1", recorded["receipt"]["payload"]["agent_id"])
            with self.assertRaises(RuntimeContractError) as caught:
                record_agent_result(
                    root,
                    task_dir,
                    status="failed",
                    agent_id="another-agent",
                    request_digest=request["request_digest"],
                    message="bad binding",
                )
            self.assertEqual("AGENT_RESULT_BINDING_MISMATCH", caught.exception.code)

    def test_agent_failure_is_terminal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir, task, _, _, request, _ = self._bound(temporary)
            failed = record_agent_result(
                root,
                task_dir,
                status="failed",
                agent_id="agent-fresh-1",
                request_digest=request["request_digest"],
                message="agent reported a bounded failure",
            )
            self.assertEqual("failed", failed["status"])
            self.assertEqual("failed", derive_execution_state(_load_receipts(task)))
            with self.assertRaises(RuntimeContractError):
                record_agent_result(
                    root,
                    task_dir,
                    status="failed",
                    agent_id="agent-fresh-1",
                    request_digest=request["request_digest"],
                    message="duplicate terminal result",
                )

    def test_recorded_confirmation_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir, _, _, _, request, _ = self._bound(temporary)
            record_agent_result(
                root,
                task_dir,
                status="awaiting_confirmation",
                agent_id="agent-fresh-1",
                request_digest=request["request_digest"],
                message="user decision required",
            )
            clarification = {
                "source": "fix_confirmation",
                "summary": "original response",
                "response": "confirmed",
                "at": "2026-09-11T12:00:00+08:00",
            }
            (task_dir / "clarifications.jsonl").write_text(json.dumps(clarification) + "\n", encoding="utf-8")
            record_user_confirmation(root, task_dir, clarification_digest=digest_value(clarification))
            clarification["response"] = "rejected"
            (task_dir / "clarifications.jsonl").write_text(json.dumps(clarification) + "\n", encoding="utf-8")
            with self.assertRaises(RuntimeContractError) as caught:
                record_agent_result(
                    root,
                    task_dir,
                    status="failed",
                    agent_id="agent-fresh-1",
                    request_digest=request["request_digest"],
                    message="must not continue after clarification drift",
                )
            self.assertEqual("CLARIFICATION_DRIFT", caught.exception.code)

    def test_result_rejects_cross_task_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir, task, _, _, request, _ = self._bound(temporary)
            other = root / "pdca/tasks/0911-other/result.txt"
            other.parent.mkdir(parents=True)
            other.write_text("not current task\n", encoding="utf-8")
            evidence = register_fixture_evidence(root, task.record_id)
            with self.assertRaises(RuntimeContractError) as caught:
                record_agent_result(
                    root,
                    task_dir,
                    status="completed",
                    agent_id="agent-fresh-1",
                    request_digest=request["request_digest"],
                    artifacts=[other.relative_to(root).as_posix()],
                    evidence_manifest=evidence,
                )
            self.assertEqual("CROSS_TASK_ARTIFACT_FORBIDDEN", caught.exception.code)

    def test_completion_and_current_task_resume(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir, task, projection_path, _, request, _ = self._bound(temporary)
            product = task_dir / "agent-result.md"
            product.write_text("completed\n", encoding="utf-8")
            evidence = register_fixture_evidence(root, task.record_id)
            completed = record_agent_result(
                root,
                task_dir,
                status="completed",
                agent_id="agent-fresh-1",
                request_digest=request["request_digest"],
                artifacts=[projection_path.relative_to(root).as_posix(), product.relative_to(root).as_posix()],
                evidence_manifest=evidence,
            )
            self.assertEqual("awaiting_conformance_verification", completed["status"])
            resumed = resume_for_conformance(root, task_dir)
            self.assertEqual("awaiting_conformance_verification", resumed["status"])
            review = json.loads((root / resumed["review_bundle"]).read_text(encoding="utf-8"))
            self.assertEqual("pending", review["result"])
            self.assertEqual(task.ontology_role, review["ontology_role"])
            self.assertEqual("ontology_conformance_verification", review["review_action"])
            self.assertEqual("awaiting_conformance_verification", derive_execution_state(_load_receipts(task)))
            with self.assertRaises(RuntimeContractError) as forged:
                record_conformance_decision(
                    root,
                    task_dir,
                    decision="confirmed",
                    reason="reviewed semantic traceability",
                    review_digest=digest_value({"forged": True}),
                )
            self.assertEqual("CONFORMANCE_REVIEW_DIGEST_MISMATCH", forged.exception.code)
            decided = record_conformance_decision(
                root,
                task_dir,
                decision="confirmed",
                reason="coordinator reviewed the semantic ontology-to-evidence chain",
                review_digest=resumed["review_digest"],
            )
            self.assertEqual("completed", decided["status"])
            paths = json.dumps(review["inputs"], ensure_ascii=False)
            self.assertNotIn("T9998", paths)
            self.assertNotIn("T9999", paths)
            self.assertNotIn("T9997", paths)

    def test_resume_rejects_artifact_and_evidence_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir, task, projection_path, _, request, _ = self._bound(temporary)
            evidence = register_fixture_evidence(root, task.record_id)
            record_agent_result(
                root,
                task_dir,
                status="completed",
                agent_id="agent-fresh-1",
                request_digest=request["request_digest"],
                artifacts=[projection_path.relative_to(root).as_posix()],
                evidence_manifest=evidence,
            )
            projection_path.write_text(projection_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
            with self.assertRaises(RuntimeContractError) as caught:
                resume_for_conformance(root, task_dir)
            self.assertEqual("RESULT_ARTIFACT_DRIFT", caught.exception.code)

    def test_decision_rejects_work_product_drift_after_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir, task, _, product, _, review = self._pending_review(temporary)
            product.write_text("changed after review\n", encoding="utf-8")
            with self.assertRaises(RuntimeContractError) as caught:
                record_conformance_decision(
                    root,
                    task_dir,
                    decision="confirmed",
                    reason="must not accept stale work products",
                    review_digest=review["review_digest"],
                )
            self.assertEqual("CONFORMANCE_WORK_PRODUCT_DRIFT", caught.exception.code)
            self.assertEqual("awaiting_conformance_verification", derive_execution_state(_load_receipts(task)))

    def test_decision_rejects_evidence_drift_after_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir, task, _, _, evidence, review = self._pending_review(temporary)
            manifest = root / evidence
            manifest.write_text(manifest.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaises(RuntimeContractError) as caught:
                record_conformance_decision(
                    root,
                    task_dir,
                    decision="confirmed",
                    reason="must not accept stale evidence",
                    review_digest=review["review_digest"],
                )
            self.assertEqual("CONFORMANCE_EVIDENCE_DRIFT", caught.exception.code)
            self.assertEqual("awaiting_conformance_verification", derive_execution_state(_load_receipts(task)))

    def test_decision_rejects_all_other_review_input_drift(self) -> None:
        mutators = {
            "task": lambda root, task_dir, projection: self._mutate_task_title(task_dir),
            "receipt": lambda root, task_dir, projection: self._mutate_receipt_log(task_dir),
            "transition": lambda root, task_dir, projection: write_json(
                task_dir / "transition-receipts/late.json", {"late": True}
            ),
            "projection": lambda root, task_dir, projection: projection.write_text(
                projection.read_text(encoding="utf-8") + " ", encoding="utf-8"
            ),
            "authority-source": lambda root, task_dir, projection: (
                root / "ontology/concept/executor-adapter.md"
            ).write_text(
                (root / "ontology/concept/executor-adapter.md").read_text(encoding="utf-8") + "drift\n",
                encoding="utf-8",
            ),
        }
        expected_codes = {
            "task": "CONFORMANCE_TASK_DRIFT",
            "receipt": "CONFORMANCE_RECEIPT_DRIFT",
            "transition": "CONFORMANCE_TRANSITION_DRIFT",
            "projection": "CONFORMANCE_WORK_PRODUCT_DRIFT",
            "authority-source": "ONTOLOGY_SOURCE_DRIFT",
        }
        for identity, mutate in mutators.items():
            with self.subTest(identity=identity), tempfile.TemporaryDirectory() as temporary:
                root, task_dir, task, projection, _, _, review = self._pending_review(temporary)
                mutate(root, task_dir, projection)
                with self.assertRaises(RuntimeContractError) as caught:
                    record_conformance_decision(
                        root,
                        task_dir,
                        decision="confirmed",
                        reason="all reviewed inputs must remain current",
                        review_digest=review["review_digest"],
                    )
                self.assertEqual(expected_codes[identity], caught.exception.code)
                current_task = task if identity != "task" else load_executable_task(root, task_dir)
                self.assertEqual(
                    "awaiting_conformance_verification",
                    derive_execution_state(_load_receipts(current_task)),
                )

    @staticmethod
    def _mutate_task_title(task_dir: Path) -> None:
        value = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
        value["title"] = "changed after review"
        write_json(task_dir / "task.json", value)

    @staticmethod
    def _mutate_receipt_log(task_dir: Path) -> None:
        path = task_dir / "agent-execution-receipts.jsonl"
        receipts = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        receipts[-1]["recorded_at"] = "2026-09-11T10:03:00+08:00"
        receipts[-1]["receipt_digest"] = digest_value(
            {key: value for key, value in receipts[-1].items() if key != "receipt_digest"}
        )
        path.write_text(
            "".join(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n" for receipt in receipts),
            encoding="utf-8",
        )

    def test_context_rejects_another_task(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir = make_runtime_root(Path(temporary))
            other = root / "pdca/tasks/0911-other/task.json"
            write_json(other, {"id": "T9999"})
            task, *_ = runtime_materials(root, task_dir)
            with self.assertRaises(RuntimeContractError) as caught:
                build_context_manifest(task, [other.relative_to(root).as_posix()])
            self.assertEqual("CROSS_TASK_CONTEXT_FORBIDDEN", caught.exception.code)

    def test_context_rejects_other_record_archive_and_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir = make_runtime_root(Path(temporary))
            task, *_ = runtime_materials(root, task_dir)
            forbidden = [
                root / "records/T9999-other/evidence/result.txt",
                root / "pdca/tasks/archive/0901-old/task.json",
                root / "pdca_runtime/__pycache__/module.pyc",
                root / "outside-context.txt",
            ]
            for path in forbidden:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("forbidden\n", encoding="utf-8")
                with self.subTest(path=path), self.assertRaises(RuntimeContractError):
                    build_context_manifest(task, [path.relative_to(root).as_posix()])

    def test_cli_confines_binding_input_and_generated_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir = make_runtime_root(Path(temporary))
            outside_bindings = root / "outside-bindings.json"
            outside_bindings.write_text("[]\n", encoding="utf-8")
            parser = build_parser()
            args = parser.parse_args(
                [
                    "--root", str(root), "--task-dir", str(task_dir), "project",
                    "--selected-id", "ontology:concept/executor-adapter",
                    "--bindings", str(outside_bindings),
                    "--output", str(task_dir / "projection.json"),
                ]
            )
            with self.assertRaises(RuntimeContractError) as binding_error:
                run(args)
            self.assertEqual("TASK_ARTIFACT_SCOPE_INVALID", binding_error.exception.code)

            current_bindings = task_dir / "bindings.json"
            current_bindings.write_text("[]\n", encoding="utf-8")
            args = parser.parse_args(
                [
                    "--root", str(root), "--task-dir", str(task_dir), "project",
                    "--selected-id", "ontology:concept/executor-adapter",
                    "--bindings", str(current_bindings),
                    "--output", str(root / "outside-projection.json"),
                ]
            )
            with self.assertRaises(RuntimeContractError) as output_error:
                run(args)
            self.assertEqual("TASK_ARTIFACT_SCOPE_INVALID", output_error.exception.code)

    def test_conformance_decision_requires_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir, task, projection_path, _, request, _ = self._bound(temporary)
            evidence = register_fixture_evidence(root, task.record_id)
            record_agent_result(
                root,
                task_dir,
                status="completed",
                agent_id="agent-fresh-1",
                request_digest=request["request_digest"],
                artifacts=[projection_path.relative_to(root).as_posix()],
                evidence_manifest=evidence,
            )
            review = resume_for_conformance(root, task_dir)
            with self.assertRaises(RuntimeContractError) as caught:
                record_conformance_decision(
                    root,
                    task_dir,
                    decision="confirmed",
                    reason="",
                    review_digest=review["review_digest"],
                )
            self.assertEqual("CONFORMANCE_DECISION_INVALID", caught.exception.code)

    def test_public_cli_has_no_control_or_polling_entrypoints(self) -> None:
        parser = build_parser()
        help_text = parser.format_help()
        self.assertNotIn("scenario", help_text)
        self.assertNotIn("poll", help_text)
        self.assertNotIn("wait", help_text)
        self.assertNotIn("main-session", help_text)

    def test_validation_report_does_not_claim_unregistered_pytest_baseline(self) -> None:
        report = (
            Path(__file__).resolve().parents[2]
            / "pdca/tasks/0911-pdca-runtime-contract-projection/validation-report.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("strict subset of the pre-edit", report)
        self.assertNotIn("Pre-edit observed baseline: `70 failed", report)
        self.assertIn("python3 -m unittest discover -s tests", report)


if __name__ == "__main__":
    unittest.main()
