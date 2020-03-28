from ami2py import create_entry_chunk, read_symbol_file_data_part
from ami2py import DATEPACKED
from ami2py import swapnibbleinbytes, AmiReader
from construct import swapbitsinbytes
from ami2py.ami_reader import extract_symbols_from_db
import os

# def test_revbits():
#     # data=b'c0ffffffffef197e'
#
#     data = bytearray(
#         b"\xc0\xff\xff\xff\xff\x9f\x42\x7e\x66\x66\x15\x42\x33\x33\x09\x42\x00\x00\x16\x42\x00\x00\x00\x42\x46\x0b\xa0\x4c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
#     )
#
#     data = swapbitsinbytes(data)
#     a = create_entry_chunk()
#     parsed = a.parse(data)
#     assert parsed[DATEPACKED]["Year"] == 2020
#     assert parsed[DATEPACKED]["Month"] == 2
#     assert parsed[DATEPACKED]["Day"] == 19


def test_load_pandas():
    test_data_folder = os.path.dirname(__file__)
    test_data_file = os.path.join(test_data_folder, "./TestData/SPCE")
    f = open(test_data_file, "rb")
    binfile = f.read()
    chunksize, data, values = read_symbol_file_data_part(binfile)
    assert len(values) < len(data) / chunksize


def test_broker_db():
    test_data_folder = os.path.dirname(__file__)
    test_data_file = os.path.join(test_data_folder, "./TestData/broker.master")
    f = open(test_data_file, "rb")
    binfile = f.read()
    symbols = extract_symbols_from_db(binfile)
    assert symbols[0] == "AA"
    assert symbols[1] == "AACC"


def test_AmiReader():
    test_data_folder = os.path.dirname(__file__)
    test_data_folder = os.path.join(test_data_folder, "./TestData")
    amireader=AmiReader(test_data_folder)
    symbols = amireader.get_symbols()
    assert symbols[0] == "AA"
    assert symbols[1] == "AACC"
    spce=amireader.get_symbol_data_pandas("SPCE")
    assert spce['Year'][0] == 2017
    assert spce['Month'][0] == 9
    assert spce['Day'][0] == 29



