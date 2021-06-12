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
    CString,
    Padded,
    BitsInteger,
    Int32ul,
    FormatField
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
from .ami_bitstructs import EntryChunk,DateShort
import struct
SwappedField = FormatField("<", "f")

# Const(b"\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x3F")
from construct import CString

ascii_str = CString("ascii")
Master = Struct(
    "Header" / Bytes(8),
    "NumSymbols" / Int32ul,
    "Symbols"
    / GreedyRange(
        Struct(
            "Symbol" / Padded(492, CString("ascii")),
            "CONST"
            / Const(
                b"\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x3F"
            ),
            "Rest" / Bytes(1172 - 5 - 16 - 490 + 3),
        )
    ),
)

# Symbol 7-151
# FullName Byte 152- 499
# 22C- 22F Schares Float
SymbolHeader = Struct(
    "Start" / Const(b"BROKDAt5"),# 8
    "SymbolName" / Padded(144, CString("ascii")), #144 + 8 = 152
    "FullName" / Padded(348, CString("ascii")), # 152+349 =501
    #"Const"/Bytes(16),# 16 +501 =517
    "First_Const"/DateShort,
    "Second_Const"/SwappedField,
    "Third_Const"/SwappedField,
    "Fourth_Const"/SwappedField,
    "Round Lot Size"/SwappedField,
    "Tick size"/SwappedField,
    "Filler_3"/SwappedField,
    "Filler_4"/SwappedField,
    "Filler_5"/SwappedField,
    "Last Split Date"/DateShort,
    "Filler_7"/SwappedField,
    "Delisting Date"/DateShort,
    "Filler_9"/SwappedField,
    "Ex-Dividend Date"/DateShort,
    "Shares Float"/SwappedField,
    "Shares Out"/SwappedField,
    "Dividend"/SwappedField,
    "Book Value(p.s.)"/SwappedField,
    "PEG Ratio"/SwappedField,
    "Profit Margin"/SwappedField,
    "Operating Margin"/SwappedField,
    "1yr target price"/SwappedField,
    "Return on Assets (ttm)"/SwappedField,
    "Return on Equity (ttm)"/SwappedField,
    "Qtrly Rev. Growth"/SwappedField,
    "Gross Profit (p.s)"/SwappedField,
    "Sales Per Share"/SwappedField,
    "EBITDA (p.s)"/SwappedField,
    "Qtrly Earnings Growth"/SwappedField,
    "% Held by Insiders"/SwappedField,
    "% Held by Institutions"/SwappedField,
    "Shares Short"/SwappedField,
    "Shares Short Prior Month"/SwappedField,
    "Forward EPS"/SwappedField,
    "EPS"/SwappedField,
    "EPS Est. Current Year"/SwappedField,
    "EPS Est. Next Year"/SwappedField,
    "EPS Est. Next Quarter"/SwappedField,
    "Forward Dividend"/SwappedField,
    "Beta"/SwappedField,
    "Operating Cash Flow"/SwappedField,
    "Levered Free Cash Flow"/SwappedField,
    "Filler_39"/SwappedField,
    "Filler_40"/SwappedField,
    "Filler_41"/SwappedField,
    "Filler_42"/SwappedField, # 685
    "Filler_43"/SwappedField,
    "Filler_44"/SwappedField,
    "Filler_45"/SwappedField,
    "Filler_46"/SwappedField,
    "Filler_47"/SwappedField,
    "Filler_48"/SwappedField,
    "Filler_49"/SwappedField,
    "Filler_50"/SwappedField,
    "Filler_51"/SwappedField,
    "Filler_52"/SwappedField,
    "Space"/Bytes(456),
    "Length"/Int32ul
)
SymbolConstruct = Struct(
    "Header" / Bytes(0x4A0), "Entries" / GreedyRange(BitsSwapped(EntryChunk))
)
