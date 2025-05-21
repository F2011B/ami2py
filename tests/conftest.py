import os
import sys
import importlib
import pytest



test_data_folder = os.path.dirname(__file__)


@pytest.fixture(autouse=True, params=["python", "rust"], ids=["python", "rust"])
def backend(request, monkeypatch):
    """Reload ami2py modules for python and rust backends."""
    use_rust = request.param == "rust"
    monkeypatch.setenv("AMI2PY_USE_RUST", "1" if use_rust else "0")

    modules = [
        "ami2py.bitparser",
        "ami2py.ami_symbol_facade",
        "ami2py.ami_reader",
        "ami2py.ami_database",
        "ami2py",
    ]
    for mod in modules:
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])

    import ami2py
    if use_rust and not ami2py.bitparser.USE_RUST:
        pytest.skip("Rust backend not available")

    test_mod = request.module
    names = [
        "AmiDataBase",
        "AmiReader",
        "SymbolEntry",
        "SymbolData",
        "Master",
        "MasterData",
        "MasterEntry",
        "SymbolConstruct",
    ]
    for name in names:
        if hasattr(test_mod, name):
            monkeypatch.setattr(test_mod, name, getattr(ami2py, name), raising=False)

    if hasattr(test_mod, "AmiSymbolDataFacade"):
        from ami2py.ami_symbol_facade import AmiSymbolDataFacade
        monkeypatch.setattr(test_mod, "AmiSymbolDataFacade", AmiSymbolDataFacade, raising=False)

    yield request.param

def pytest_configure():
    pytest.TEST_DATABASE_FOLDER = os.path.join(test_data_folder, "./TestData")

@pytest.fixture
def master_data():
    test_data_file = os.path.join(test_data_folder, "./TestData/broker.master")
    try:
        f = open(test_data_file, "rb")
        binfile = f.read()
    finally:
        f.close()
    return binfile

@pytest.fixture
def index_db():
    return os.path.join(test_data_folder, "./TestDB")


@pytest.fixture
def symbol_spce():
    test_data_file = os.path.join(test_data_folder, "./TestData/s/SPCE")
    try:
        f = open(test_data_file, "rb")
        binfile = f.read()
    finally:
        f.close()
    return binfile





