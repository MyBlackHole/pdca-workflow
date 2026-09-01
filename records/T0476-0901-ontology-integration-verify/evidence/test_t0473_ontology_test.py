# T0473 本体证明：测试三模式派生
import pathlib, subprocess, json, yaml
NODE = "ontology:pattern/testable-signal-to-test-derivation"
def test_t0473_scaffold_exists():
    assert pathlib.Path("scripts/ontology_test_scaffold.py").exists()
    assert pathlib.Path("ontology/pattern/testable-signal-to-test-derivation.md").exists()
def test_t0473_three_modes_classify():
    import importlib.util
    import pathlib as pl
    spec = importlib.util.spec_from_file_location("scaffold", "scripts/ontology_test_scaffold.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert m.classify_signal("检查 X 是否满足 Y") == "assertion"
    assert m.classify_signal("对比声明与实际一致 契约") == "contract"
    assert m.classify_signal("回链 AC 覆盖 convergence") == "convergence"
def test_t0473_scaffold_generates():
    r = subprocess.run(["python3","scripts/ontology_test_scaffold.py","--node","ontology:pattern/testable-signal-to-test-derivation","--out","/tmp/t0473_test.py"], capture_output=True, text=True)
    assert r.returncode == 0
    txt = pathlib.Path("/tmp/t0473_test.py").read_text()
    assert "test_attr_" in txt and "test_contract_" in txt and "test_convergence_" in txt
    mp = pathlib.Path("/tmp/scaffold-map-testable_signal_to_test_derivation.json")
    assert mp.exists()
    data = json.loads(mp.read_text())
    assert data["node_id"] == NODE
def test_t0473_strategy_linked():
    txt = pathlib.Path("ontology/domain/skill-testing-strategy.md").read_text()
    assert "ontology_test_scaffold.py" in txt
    assert "testable-signal-to-test-derivation" in txt
