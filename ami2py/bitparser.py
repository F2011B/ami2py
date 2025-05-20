import os

USE_RUST = os.environ.get("AMI2PY_USE_RUST", "0") == "1"

if USE_RUST:
    try:
        from . import rust_bitparser as _backend
    except Exception:  # pragma: no cover - rust module may not be built
        USE_RUST = False
        from . import py_bitparser as _backend
else:
    from . import py_bitparser as _backend

reverse_bits = _backend.reverse_bits
read_date = _backend.read_date
create_float = getattr(_backend, "create_float", None)
float_to_bin = getattr(_backend, "float_to_bin", None)
date_to_bin = getattr(_backend, "date_to_bin", None)
