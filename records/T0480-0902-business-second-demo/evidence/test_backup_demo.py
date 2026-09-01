import importlib.util, pathlib
spec = importlib.util.spec_from_file_location("demo", "backup/src/demo.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
def test_backup():
    assert mod.get_demo() == {"backup": 1}
