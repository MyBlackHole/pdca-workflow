# T0475 本体证明：全任务知识闭环
import pathlib, subprocess, json, yaml
def test_t0475_flow_act_hardened():
    txt = pathlib.Path("ontology/process/flow-act.md").read_text()
    assert "全任务强制" in txt
    assert "ontology:" in txt and "records-only" in txt
def test_t0475_disposition_gate():
    assert pathlib.Path("scripts/pdca_core.py").read_text().count("DISPOSITION_ONTOLOGY_MISSING")==1
def test_t0475_ontology_ready_any_scenario():
    r = subprocess.run(["python3","scripts/ontology-validate.py","--ontology-dir","ontology"], capture_output=True, text=True)
    assert r.returncode==0
    fm = yaml.safe_load(pathlib.Path("ontology/concept/pdca-task.md").read_text().split("---",2)[1])
    assert fm["id"]=="ontology:concept/pdca-task"
