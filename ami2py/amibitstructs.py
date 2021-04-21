from construct import Struct, BitStruct, BitsInteger, FormatField, BitsSwapped
from .revbitinteger import RevBitsInteger
from .consts import DATEPACKED, DAY, MONTH, YEAR, VOLUME, CLOSE, OPEN, HIGH, LOW


SwappedField=BitsSwapped(FormatField("<", "f"))

EntryChunk = Struct(
    DATEPACKED
    / BitStruct(
        "Isfut" / BitsInteger(length=1),#1
        "Reserved" / BitsInteger(length=5),#6
        "MicroSec" / BitsInteger(length=10),#16
        "MilliSec" / BitsInteger(length=10),#26
        "Second" / BitsInteger(length=6),#32
        "Minute" / BitsInteger(length=6),#38
        "Hour" / BitsInteger(length=5),#43
        DAY / RevBitsInteger(length=5),#48
        MONTH / RevBitsInteger(length=4),#52
        YEAR / RevBitsInteger(length=12),  # 64bit
    ),
    CLOSE / SwappedField,
    OPEN / SwappedField,
    HIGH / SwappedField,
    LOW / SwappedField,
    VOLUME / SwappedField,  # 160
    "AUX1" / SwappedField,
    "AUX2" / SwappedField,
    "TERMINATOR" / SwappedField, #256
    )

def create_entry_chunk():
    return EntryChunk


