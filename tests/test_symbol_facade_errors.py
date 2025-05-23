import pytest
from ami2py.ami_symbol_facade import AmiSymbolDataFacade
from ami2py.errors import InvalidAmiHeaderError


def test_invalid_header_raises():
    bad = b"\x00\x01\x02"
    with pytest.raises(InvalidAmiHeaderError):
        AmiSymbolDataFacade(bad)
