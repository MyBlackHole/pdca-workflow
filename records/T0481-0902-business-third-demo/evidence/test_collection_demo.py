import importlib.util
spec = importlib.util.spec_from_file_location("demo", "collection/src/demo.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
def test_collection():
    assert mod.get_demo() == {"collection": 1}
