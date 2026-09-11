from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from pdca_runtime import RuntimeContractError, build_projection_manifest, verify_projection_manifest
from pdca_runtime.task import load_executable_task
from pdca_runtime.tests.runtime_fixtures import make_runtime_root, runtime_materials


class OntologyProjectionRuntimeTest(unittest.TestCase):
    def test_three_layer_projection_is_content_addressed_and_traceable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir = make_runtime_root(Path(temporary))
            task, manifest, *_ = runtime_materials(root, task_dir)
            self.assertEqual(
                {
                    "authoritative_ontology_graph",
                    "bounded_task_subgraph",
                    "execution_tree_or_dag",
                },
                set(manifest["layers"]),
            )
            leaves = manifest["layers"]["execution_tree_or_dag"]["leaves"]
            self.assertEqual(list(task.required_actions), [leaf["required_action"] for leaf in leaves])
            self.assertTrue(all(leaf["ontology_node"] and leaf["completion_criterion"] for leaf in leaves))
            self.assertGreater(
                len(manifest["layers"]["authoritative_ontology_graph"]["nodes"]),
                len(manifest["layers"]["bounded_task_subgraph"]["nodes"]),
            )
            self.assertEqual("passed", verify_projection_manifest(task, manifest)["status"])

    def test_projection_rejects_missing_action_and_cycles(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir = make_runtime_root(Path(temporary))
            task, manifest, *_ = runtime_materials(root, task_dir)
            selected = [node["id"] for node in manifest["layers"]["bounded_task_subgraph"]["nodes"]]
            bindings = [
                {
                    "action_index": 1,
                    "step_name": "project",
                    "ontology_id": task.ontology_anchor,
                    "depends_on": [],
                }
            ]
            with self.assertRaises(RuntimeContractError) as missing:
                build_projection_manifest(task, selected, bindings)
            self.assertEqual("ACTION_BINDING_INCOMPLETE", missing.exception.code)

            bindings.append(
                {
                    "action_index": 2,
                    "step_name": "verify",
                    "ontology_id": task.ontology_anchor,
                    "depends_on": ["action-002"],
                }
            )
            with self.assertRaises(RuntimeContractError) as cycle:
                build_projection_manifest(task, selected, bindings)
            self.assertEqual("EXECUTION_DAG_CYCLE", cycle.exception.code)

    def test_authority_source_drift_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir = make_runtime_root(Path(temporary))
            task, manifest, *_ = runtime_materials(root, task_dir)
            source = root / "ontology/concept/executor-adapter.md"
            source.write_text(source.read_text(encoding="utf-8") + "drift\n", encoding="utf-8")
            with self.assertRaises(RuntimeContractError) as caught:
                verify_projection_manifest(task, manifest)
            self.assertEqual("ONTOLOGY_SOURCE_DRIFT", caught.exception.code)

    def test_projection_rejects_caller_omission_from_authority_layer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir = make_runtime_root(Path(temporary))
            task, manifest, *_ = runtime_materials(root, task_dir)
            manifest["layers"]["authoritative_ontology_graph"]["nodes"].pop()
            from pdca_runtime.io import digest_value

            manifest["digest"] = digest_value({key: value for key, value in manifest.items() if key != "digest"})
            with self.assertRaises(RuntimeContractError) as caught:
                verify_projection_manifest(task, manifest)
            self.assertEqual("ONTOLOGY_AUTHORITY_GRAPH_DRIFT", caught.exception.code)

    def test_relation_selection_is_derived_from_active_rule(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, task_dir = make_runtime_root(Path(temporary))
            rule_path = root / "ontology/concept/ontology-rule-non-dangling.md"
            text = rule_path.read_text(encoding="utf-8")
            metadata = yaml.safe_load(text.split("---", 2)[1])
            metadata["rule_spec"]["reference_relation_keys"].append("governs")
            rule_path.write_text(
                "---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---\n# rule\n",
                encoding="utf-8",
            )
            source = root / "ontology/concept/unrelated-authority.md"
            source_text = source.read_text(encoding="utf-8")
            source.write_text(
                source_text.replace(
                    "relations:\n",
                    "relations:\n  governs:\n    - ontology:concept/pdca-task\n",
                ),
                encoding="utf-8",
            )
            _, manifest, *_ = runtime_materials(root, task_dir)
            authority = manifest["layers"]["authoritative_ontology_graph"]
            self.assertIn("governs", authority["relation_vocabulary"]["relation_keys"])
            self.assertIn(
                {
                    "source": "ontology:concept/unrelated-authority",
                    "relation": "governs",
                    "target": "ontology:concept/pdca-task",
                },
                authority["edges"],
            )

    def test_projection_fails_closed_without_valid_relation_rule(self) -> None:
        for invalid in ("missing", "empty"):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as temporary:
                root, task_dir = make_runtime_root(Path(temporary))
                rule_path = root / "ontology/concept/ontology-rule-non-dangling.md"
                if invalid == "missing":
                    rule_path.unlink()
                    expected = "ONTOLOGY_RELATION_RULE_MISSING"
                else:
                    rule_path.write_text(
                        rule_path.read_text(encoding="utf-8").replace(
                            "  reference_relation_keys:\n"
                            "    - specializes\n"
                            "    - instance_of\n"
                            "    - composed_of\n"
                            "    - configured_by\n"
                            "    - part_of\n"
                            "    - guides\n"
                            "    - relates_to\n",
                            "  reference_relation_keys: []\n",
                        ),
                        encoding="utf-8",
                    )
                    expected = "ONTOLOGY_RELATION_RULE_INVALID"
                with self.assertRaises(RuntimeContractError) as caught:
                    build_projection_manifest(load_executable_task(root, task_dir), [], [])
                self.assertEqual(expected, caught.exception.code)


if __name__ == "__main__":
    unittest.main()
