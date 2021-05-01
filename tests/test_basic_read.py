from ami2py import AmiReader
from ami2py.ami_construct import Master, SymbolConstruct
from ami2py.consts import DATEPACKED, OPEN
import os


def test_load_pandas():
    test_data_folder = os.path.dirname(__file__)
    test_data_file = os.path.join(test_data_folder, "./TestData/s/SPCE")
    f = open(test_data_file, "rb")
    binfile = f.read()
    data = SymbolConstruct.parse(binfile)
    assert len(data["Entries"]) == 600


def test_amistruct_master(master_data):
    parsed = Master.parse(master_data)
    assert parsed["Symbols"][0]["Symbol"] == "AA"
    assert parsed["Symbols"][1]["Symbol"] == "AACC"


def test_write_master(master_data):
    parsed = Master.parse(master_data)
    parsed["Symbols"][0]["Symbol"] = "JD"
    newbin = Master.build(parsed)
    newparsed = Master.parse(newbin)
    assert newparsed["Symbols"][0]["Symbol"] == "JD"


def test_read_symbol_construct(symbol_spce):
    space = SymbolConstruct.parse(symbol_spce)
    assert space["Entries"][0][DATEPACKED]["Year"] == 2017


def test_write_symbol_construct(symbol_spce):
    space = SymbolConstruct.parse(symbol_spce)
    newbin = SymbolConstruct.build(space)
    space["Entries"][0][DATEPACKED]["Year"] = 2016
    space["Entries"][0][OPEN] = -25
    newbin = SymbolConstruct.build(space)
    newparsed = SymbolConstruct.parse(newbin)
    assert newparsed["Entries"][0][DATEPACKED]["Year"] == 2016
    assert newparsed["Entries"][0][OPEN] == -25


def test_AmiReader():
    test_data_folder = os.path.dirname(__file__)
    test_data_folder = os.path.join(test_data_folder, "./TestData")
    amireader = AmiReader(test_data_folder)
    symbols = amireader.get_symbols()
    assert symbols[0] == "AA"
    assert symbols[1] == "AACC"
    spce = amireader.get_symbol_data_dictionary("SPCE")
    assert spce["Year"][0] == 2017
    assert spce["Month"][0] == 9
    assert spce["Day"][0] == 29


def test_reader_SymbolData():
    test_data_folder = os.path.dirname(__file__)
    test_data_folder = os.path.join(test_data_folder, "./TestData")
    amireader = AmiReader(test_data_folder)
    spce = amireader.get_symbol_data("SPCE")
    data = spce.to_dict()
    assert len(data["Close"]) > 20
