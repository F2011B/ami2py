from construct import Struct, BitStruct, BitsInteger, FormatField, BitsSwapped
from .revbitinteger import RevBitsInteger
from .consts import (
    DATEPACKED,
    DAY,
    MONTH,
    YEAR,
    VOLUME,
    CLOSE,
    OPEN,
    HIGH,
    LOW,
    FUT,
    RESERVED,
    MICRO_SEC,
    MILLI_SEC,
    SECOND,
    MINUTE,
    HOUR,
    AUX_1,
    AUX_2,
    TERMINATOR,
)


SwappedField = BitsSwapped(FormatField("<", "f"))

EntryChunk = Struct(
    DATEPACKED
    / BitStruct(
        FUT / BitsInteger(length=1),  # 1
        RESERVED / BitsInteger(length=5),  # 6
        MICRO_SEC / BitsInteger(length=10),  # 16
        MILLI_SEC / BitsInteger(length=10),  # 26
        SECOND / BitsInteger(length=6),  # 32
        MINUTE / BitsInteger(length=6),  # 38
        HOUR / BitsInteger(length=5),  # 43
        DAY / RevBitsInteger(length=5),  # 48
        MONTH / RevBitsInteger(length=4),  # 52
        YEAR / RevBitsInteger(length=12),  # 64bit
    ),
    CLOSE / SwappedField,
    OPEN / SwappedField,
    HIGH / SwappedField,
    LOW / SwappedField,
    VOLUME / SwappedField,  # 160
    AUX_1 / SwappedField,
    AUX_2 / SwappedField,
    TERMINATOR / SwappedField,  # 256
)


def create_entry_chunk():
    return EntryChunk
