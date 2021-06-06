from construct import (
    Struct,
    Bytes,
    GreedyRange,
    PaddedString,
    swapbitsinbytes,
    BitsSwapped,
    bytes2bits,
    bits2bytes,
    Const,
)
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
from .ami_bitstructs import EntryChunk
import struct

# Const(b"\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x3F")
from construct import CString
ascii_str=CString('ascii')
Master = Struct(
    "Header" / Bytes(12),
    "Symbols"
    / GreedyRange(
        Struct(
            "Symbol" / Bytes(492),
            "CONST"
            / Const(
                b"\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x3F"
            ),
            "Rest" / Bytes(1172 - 5 - 16 - 490 + 3),
        )
    ),
)


SymbolConstruct = Struct(
    "Header" / Bytes(0x4A0), "Entries" / GreedyRange(BitsSwapped(EntryChunk))
)
