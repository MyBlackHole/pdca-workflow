import importlib.util, pathlib
spec = importlib.util.spec_from_file_location("report_demo", "report-web/src/report_demo.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
def test_demo():
    assert mod.get_demo_report() == {"demo": 1}
def test_demo_contract():
    assert "demo_api" in pathlib.Path("ontology/entity/report-center-web-entity.md").read_text()
