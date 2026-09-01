# T0477 本体证明：既有领域树补齐
import pathlib, subprocess, json, yaml
def test_t0477_report_center_tree():
    fm = yaml.safe_load(pathlib.Path("ontology/entity/report-center-system.md").read_text().split("---",2)[1])
    assert fm["id"]=="ontology:entity/report-center-system"
    assert len(fm["relations"]["composed_of"])==2
    assert "ontology:entity/report-center-web-entity" in fm["relations"]["composed_of"]
def test_t0477_backup_tree():
    fm = yaml.safe_load(pathlib.Path("ontology/entity/backup-system.md").read_text().split("---",2)[1])
    assert len(fm["relations"]["composed_of"])==2
def test_t0477_validate_and_islands():
    r = subprocess.run(["python3","scripts/ontology-validate.py","--ontology-dir","ontology"], capture_output=True, text=True)
    assert r.returncode==0
    r2 = subprocess.run(["python3","scripts/ontology_graph.py","--format","summary"], capture_output=True, text=True)
    assert "islands: 0" in r2.stdout
    assert "nodes: 363" in r2.stdout
def test_t0477_tree_split_and_frontier():
    # 对新父节点可调度
    import json, subprocess
    # 模拟 PRD 含 report-center-system 映射
    p = pathlib.Path("/tmp/t0477_prd.md")
    p.write_text("# t\n## 验收标准\n- [ ] AC-1 x\n## 拆分映射\n- ReportCenter -> ontology:entity/report-center-system\n- Backup -> ontology:entity/backup-system\n")
    r = subprocess.run(["python3","scripts/ontology_tree_split.py","--ontology-dir","ontology","--prd",str(p)], capture_output=True, text=True)
    data = json.loads(r.stdout)
    assert any(c["ontology_node_id"]=="ontology:entity/report-center-system" for c in data["candidates"])
    # frontier
    dag = '{"report-center-web-entity":[],"report-center-collection-entity":[],"report-center-system":["report-center-web-entity","report-center-collection-entity"]}'
    r2 = subprocess.run(["python3","scripts/compute-frontier.py"], input=dag, capture_output=True, text=True)
    assert json.loads(r2.stdout)["valid"] is True
