# T0478 本体证明：CI 硬门禁
import pathlib, subprocess, json
def test_t0478_hook_exists():
    assert pathlib.Path("scripts/install-git-hook.sh").exists()
    assert pathlib.Path(".github/workflows/ontology-gate.yml").exists()
    assert "ci-ontology-gate.py" in pathlib.Path("scripts/install-git-hook.sh").read_text()
def test_t0478_ci_script():
    txt = pathlib.Path("scripts/ci-ontology-gate.py").read_text()
    assert "ontology-validate" in txt or "validate" in txt
def test_t0478_no_regress():
    r = subprocess.run(["python3","scripts/ontology-validate.py","--ontology-dir","ontology"], capture_output=True, text=True)
    assert r.returncode==0
