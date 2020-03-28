from construct import Struct, BitStruct, BitsInteger
from .revbitinteger import RevBitsInteger, RevFormatField
from .consts import DATEPACKED, DAY, MONTH, YEAR, VOLUME, CLOSE, OPEN, HIGH, LOW


def create_entry_chunk():
    a = Struct(
        DATEPACKED
        / BitStruct(
            "Isfut" / BitsInteger(length=1),
            "Reserved" / BitsInteger(length=5),
            "MicroSec" / BitsInteger(length=10),
            "MilliSec" / BitsInteger(length=10),
            "Second" / BitsInteger(length=6),
            "Minute" / BitsInteger(length=6),
            "Hour" / BitsInteger(length=5),
            DAY / RevBitsInteger(length=5),
            MONTH / RevBitsInteger(length=4),
            YEAR / RevBitsInteger(length=12),  # 64bit
        ),
        CLOSE / RevFormatField("<", "f"),
        OPEN / RevFormatField("<", "f"),
        HIGH / RevFormatField("<", "f"),
        LOW / RevFormatField("<", "f"),
        VOLUME / RevFormatField("<", "f"),  # 160
        "AUX1" / RevFormatField("<", "f"),
        "AUX2" / RevFormatField("<", "f"),
        "TERMINATOR" / RevFormatField("<", "f"),
    )
    return a


