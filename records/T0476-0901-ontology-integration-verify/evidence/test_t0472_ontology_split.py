# T0472 本体证明：拆分门禁硬化 ontology:entity/ontology-deep-integration-split
import pathlib, subprocess, json
NODE = "ontology:entity/ontology-deep-integration-split"
def test_t0472_node_exists_and_validate():
    r = subprocess.run(["python3","scripts/ontology-validate.py","--ontology-dir","ontology"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout+r.stderr
    assert "OK" in r.stdout
def test_t0472_node_specializes():
    import yaml
    fm = yaml.safe_load(pathlib.Path("ontology/entity/ontology-deep-integration-split.md").read_text().split("---",2)[1])
    assert fm["id"] == NODE
    assert fm["type"] == "entity"
    assert "ontology:concept/domain-entity" in fm["relations"]["specializes"]
def test_t0472_skill_default_tree():
    txt = pathlib.Path("ontology/domain/skill-to-tickets.md").read_text()
    assert "关系树驱动拆分（默认，叶→根）" in txt
    assert "默认启用" in txt
    assert "告警并回退" in txt
def test_t0472_inherit_and_clash():
    assert pathlib.Path("scripts/task_identity.py").read_text().count("ontology_fragment") >= 2
