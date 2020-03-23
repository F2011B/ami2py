from construct import Struct, BitStruct, BitsInteger, swapbitsinbytes, GreedyRange

from ami2py.revbitinteger import RevBitsInteger, RevFormatField
from ami2py.consts import DATEPACKED, DAY, MONTH, YEAR, VOLUME, CLOSE, OPEN, HIGH, LOW


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
            "Day" / RevBitsInteger(length=5),
            "Month" / RevBitsInteger(length=4),
            "Year" / RevBitsInteger(length=12),
        ),
        "Price" / RevFormatField("<", "f"),
        "Open" / RevFormatField("<", "f"),
        "High" / RevFormatField("<", "f"),
        "Low" / RevFormatField("<", "f"),
        "Volume" / RevFormatField("<", "f"),
    )
    return a


def read_symbol_file_data_part(binfile):
    datapart = binfile[0x4A0:]
    data = swapbitsinbytes(datapart)
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
    chunksize = 40
    parsed = a.parse(data[:chunksize])
    assert parsed["DatePacked"][YEAR] == 2017
    start = 0
    end = chunksize
    values = {
        DAY: [],
        MONTH: [],
        YEAR: [],
        CLOSE: [],
        OPEN: [],
        HIGH: [],
        LOW: [],
        VOLUME: [],
    }
    packed_map = {
        DAY: lambda x: x[DATEPACKED][DAY],
        MONTH: lambda x: x[DATEPACKED][MONTH],
        YEAR: lambda x: x[DATEPACKED][YEAR],
    }
    greedy_parser = GreedyRange(a)
    data_lines = greedy_parser.parse(data)
    values = [
        (
            packed_map[DAY](el),
            packed_map[MONTH](el),
            packed_map[YEAR](el),
            el[OPEN],
            el[HIGH],
            el[LOW],
            el[CLOSE],
            el[VOLUME],
        )
        for el in data_lines
    ]
    return chunksize, data, values