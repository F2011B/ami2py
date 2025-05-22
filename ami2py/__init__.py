import os

USE_RUST = os.environ.get("AMI2PY_USE_RUST", "0") == "1"

if USE_RUST:
    try:
        from .rust_amidatabase import AmiDataBase
    except Exception:  # pragma: no cover - rust module may not be built
        USE_RUST = False
        from .ami_database import AmiDataBase
else:
    from .ami_database import AmiDataBase

from .ami_bitstructs import create_entry_chunk
from .ami_reader import AmiReader
from .ami_dataclasses import (
    SymbolEntry,
    SymbolData,
    Master,
    MasterData,
    MasterEntry,
    SymbolConstruct,
)
from .consts import DATEPACKED, DAY, MONTH, YEAR, VOLUME, CLOSE, OPEN, HIGH, LOW

