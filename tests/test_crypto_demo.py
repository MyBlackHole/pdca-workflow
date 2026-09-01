import importlib.util
spec = importlib.util.spec_from_file_location("crypto_demo", "backup/src/crypto_demo.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
def test_crypto():
    assert mod.get_demo() == {"crypto": 1}
