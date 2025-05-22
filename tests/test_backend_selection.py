import ami2py
from ami2py import bitparser


def test_backend_selection(backend):
    if backend == "rust":
        assert ami2py.USE_RUST is True
        assert bitparser.USE_RUST is True
        assert ami2py.AmiDataBase.__module__ == "builtins"
        assert bitparser._backend.__name__ == "ami2py.rust_bitparser"
    else:
        assert ami2py.USE_RUST is False
        assert bitparser.USE_RUST is False
        assert ami2py.AmiDataBase.__module__ == "ami2py.ami_database"
        assert bitparser._backend.__name__ == "ami2py.py_bitparser"
