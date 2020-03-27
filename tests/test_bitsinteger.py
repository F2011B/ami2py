from ami2py import create_entry_chunk, read_symbol_file_data_part
from ami2py import DATEPACKED, DAY, MONTH, YEAR, VOLUME, CLOSE, OPEN, HIGH, LOW
from ami2py import swapnibbleinbytes
from construct import Struct
from construct import swapbitsinbytes, GreedyRange, Bytes
import os
import pandas as pd
import pytest

# unsigned int IsFuturePad:1;	// bit marking "future data"
# unsigned int Reserved:5;	// reserved set to zero
# unsigned int MicroSec:10;	// microseconds	0..999
# unsigned int MilliSec:10;	// milliseconds	0..999
# unsigned int Second: 6;		// 0..59
# // higher 32 bits
# unsigned int Minute : 6; // 0..59 63 is reserved as EOD marker
# unsigned int Hour : 5; // 0..23 31 is reserved as EOD marker
# unsigned int Day : 5; // 1..31
# unsigned int Month : 4; // 1..12
# unsigned int Year : 12;	// 0..4095


def test_fortrue():
    assert True


def test_revbits():
    # data=b'c0ffffffffef197e'
    data = b"\x19\xe7"
    data = b"\xc0\xff\xff\xff\xff\xef\x19\x7e"

    data = bytearray(b"\x19\x7e")
    data = swapnibbleinbytes(data)

    data = swapbitsinbytes(data)
    data = bytearray(
        b"\xc0\xff\xff\xff\xff\x9f\x42\x7e\x66\x66\x15\x42\x33\x33\x09\x42\x00\x00\x16\x42\x00\x00\x00\x42\x46\x0b\xa0\x4c"
    )
    # data[6] = swapNibbles(data[6])
    # data[5] = swapNibbles(data[5])
    data = swapbitsinbytes(data)
    a = create_entry_chunk()
    parsed = a.parse(data)
    assert parsed[DATEPACKED]["Year"] == 2020
    assert parsed[DATEPACKED]["Month"] == 2
    assert parsed[DATEPACKED]["Day"] == 19


def test_load_pandas():
    test_data_folder = os.path.dirname(__file__)
    test_data_file = os.path.join(test_data_folder, "./TestData/SPCE")
    f = open(test_data_file, "rb")
    binfile = f.read()
    chunksize, data, values = read_symbol_file_data_part(binfile)
    df = convert_to_data_frame(values)

    out_data_file = os.path.join(test_data_folder, "./TestData/SPCE.json")
    df.to_json(out_data_file)
    #df.plot(x="Date", y="Close")

    assert len(values) < len(data) / chunksize


def convert_to_data_frame(values):
    df = pd.DataFrame(
        values, columns=[DAY, MONTH, YEAR, OPEN, HIGH, LOW, CLOSE, VOLUME]
    )
    df["Date"] = pd.to_datetime(df.loc[:, [DAY, MONTH, YEAR]])
    return df


def test_broker_db():
    test_data_folder = os.path.dirname(__file__)
    test_data_file = os.path.join(test_data_folder, "./TestData/broker.master")
    f = open(test_data_file, "rb")
    binfile = f.read()
    datapart = binfile[0x4A0:]
    # 494 bytes - 5bytes = 489
    a = Struct("Symbol" / Bytes(5), "Rest" / Bytes(1172 - 5))
    greedy_parser = GreedyRange(a)
    data_lines = greedy_parser.parse(datapart)
    first = data_lines[0]["Symbol"].decode("ascii").rstrip('\x00')

    assert first == "AA"
    second = data_lines[1]["Symbol"].decode("utf-8").rstrip('\x00')
    assert second == "AACC"
