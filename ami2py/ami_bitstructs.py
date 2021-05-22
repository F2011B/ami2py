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

Date=BitStruct(
    FUT / BitsInteger(length=1),  # 1
    RESERVED / BitsInteger(length=5),  # 6
    MICRO_SEC / BitsInteger(length=10),  # Bit 16 byte 2
    MILLI_SEC / BitsInteger(length=10),  # 26
    SECOND / BitsInteger(length=6),  # Bit 32 Byte 4
    MINUTE / BitsInteger(length=6),  # 38
    HOUR / BitsInteger(length=5),  # 43
    DAY / RevBitsInteger(length=5),  # Bit 48 Byte 6
    MONTH / RevBitsInteger(length=4),  # 52
    YEAR / RevBitsInteger(length=12),  # Bit  64 Byte 8
)

EntryChunk = Struct(
    DATEPACKED
    / Date,
    CLOSE / SwappedField, # Byte 4
    OPEN / SwappedField,
    HIGH / SwappedField,
    LOW / SwappedField,
    VOLUME / SwappedField,  # 160
    AUX_1 / SwappedField,
    AUX_2 / SwappedField,
    TERMINATOR / SwappedField,  # 256 + 64
)


def create_entry_chunk():
    return EntryChunk
