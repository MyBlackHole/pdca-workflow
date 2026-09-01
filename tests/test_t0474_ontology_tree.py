# T0474 本体证明：树形执行叶→根
import pathlib, subprocess, json, yaml
def test_t0474_composed_of():
    fm = yaml.safe_load(pathlib.Path("ontology/entity/ontology-deep-integration.md").read_text().split("---",2)[1])
    com = fm["relations"]["composed_of"]
    assert len(com)==4
    assert "ontology:entity/ontology-deep-integration-split" in com
def test_t0474_graph_islands_and_dot():
    r = subprocess.run(["python3","scripts/ontology_graph.py","--format","summary"], capture_output=True, text=True)
    assert "islands: 0" in r.stdout
    r2 = subprocess.run(["python3","scripts/ontology_graph.py","--format","dot","--root","ontology"], capture_output=True, text=True)
    assert "ontology-deep-integration" in r2.stdout and "ontology-deep-integration-split" in r2.stdout
def test_t0474_frontier_batches():
    dag = '{"T0472":[],"T0473":[],"T0474":[],"T0475":[],"T0476":["T0472","T0473","T0474","T0475"]}'
    r = subprocess.run(["python3","scripts/compute-frontier.py"], input=dag, capture_output=True, text=True)
    data = json.loads(r.stdout)
    assert data["valid"] is True
    assert data["batches"] == [["T0472","T0473","T0474","T0475"],["T0476"]]
def test_t0474_tree_split_candidates():
    r = subprocess.run(["python3","scripts/ontology_tree_split.py","--ontology-dir","ontology","--prd","pdca/tasks/0901-ontology-deep-integration/prd.md"], capture_output=True, text=True)
    data = json.loads(r.stdout)
    assert len(data["candidates"])==5
    root = [c for c in data["candidates"] if c["ontology_node_id"]=="ontology:entity/ontology-deep-integration"][0]
    assert set(root["dependencies"])=={"ontology-deep-integration-split","ontology-deep-integration-test","ontology-deep-integration-tree","ontology-deep-integration-knowledge"}
