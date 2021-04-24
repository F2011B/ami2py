from construct import (
    Struct,
    Bytes,
    GreedyRange,
    PaddedString,
    swapbitsinbytes,
    BitsSwapped,
)
from .consts import YEAR, DAY, MONTH, CLOSE, OPEN, HIGH, LOW, VOLUME, DATEPACKED
from .ami_bitstructs import EntryChunk


Master = Struct(
    "Header" / Bytes(0x4A0),
    "Symbols"
    / GreedyRange(
        Struct("Symbol" / PaddedString(5, "ASCII"), "Rest" / Bytes(1172 - 5))
    ),
)

SymbolConstruct = Struct(
    "Header" / Bytes(0x4A0), "Entries" / GreedyRange(BitsSwapped(EntryChunk))
)
