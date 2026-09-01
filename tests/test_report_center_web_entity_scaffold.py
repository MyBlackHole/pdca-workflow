# 自动生成：ontology:entity/report-center-web-entity 的 testable_signal 测试骨架
# 三模式：属性断言 / 契约测试 / 收敛验证（见 ontology:pattern/testable-signal-to-test-derivation）
# 运行: pytest test_report_center_web_entity_scaffold.py -v
import pathlib, subprocess, json, re

NODE_ID = "ontology:entity/report-center-web-entity"
NODE_TYPE = "entity"
ONT_DIR = pathlib.Path("ontology")

def test_attr_report_center_web_entity_signals_non_generic():
    """属性断言：testable_signal 非空且非泛化（AC-4 补充）"""
    import yaml
    fm = yaml.safe_load(pathlib.Path("ontology/entity/report-center-web-entity.md").read_text().split("---")[1])
    for attr in (fm.get("attributes") or []):
        sig = str(attr.get("testable_signal",""))
        assert sig.strip(), f"{attr.get('name')} 缺 testable_signal"
        assert "由领域实践与测试验证" not in sig, f"{attr.get('name')} 为泛化信号"
        assert any(v in sig for v in ["检查","校验","运行","断言","验证","对比","回链","覆盖"]), f"{attr.get('name')} 无动词+判定"

def test_contract_report_center_web_entity_exists():
    """契约测试示例：声明 vs 实际一致性（按需精化）"""
    # 示例：校验本体节点存在且可被 ontology-validate
    ret = subprocess.run(["python3", "scripts/ontology-validate.py", "--ontology-dir", str(ONT_DIR)], capture_output=True, text=True)
    assert ret.returncode == 0, ret.stdout + ret.stderr

def test_convergence_report_center_web_entity_map():
    """收敛验证示例：convergence 需回链 AC 与 evidence（按需接入真实任务）"""
    # 本骨架仅示范结构；真实收敛验证由 scripts/validate-convergence.py --task-dir 承载
    assert NODE_ID.startswith("ontology:"), "node_id 须为本体 id"


def test_assertion_report_center_web_entity_demo_api():
    """assertion: 运行 python3 -m pytest tests/test_report_demo.py -v 检查桩接口返回 {demo:1}，且经 scaffold 生"""
    assert True  # TODO: 按 testable_signal 精化断言
