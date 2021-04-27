from ami2py import SymbolEntry, SymbolData, Master, MasterData, MasterEntry
from dataclass_type_validator import TypeValidationError
from ami2py.ami_construct import SymbolConstruct
from ami2py import DATEPACKED, OPEN


def test_SymbolEntry():
    entry = SymbolEntry(
        close=10.0,
        low=10.0,
        high=12.0,
        open=10.0,
        volume=0.0,
        day=10,
        month=11,
        year=2020,
    )
    assert entry.day == 10


def test_SymbolData():
    entry = SymbolEntry(
        close=10.0,
        low=10.0,
        high=12.0,
        open=10.0,
        volume=0.0,
        day=10,
        month=11,
        year=2020,
    )
    try:
        data = SymbolData(Entries=entry)
        assert False
    except TypeValidationError as e:
        assert True

    data = SymbolData(Entries=[entry])
    entry = SymbolEntry(
        close=10.0,
        low=10.0,
        high=12.0,
        open=10.0,
        volume=0.0,
        day=11,
        month=11,
        year=2020,
    )
    data.append(entry)
    assert len(data.Entries) == 2

    df = data.to_dataframe()
    assert len(df["Close"]) == 2


def test_Master(master_data):
    parsed = Master.parse(master_data)
    assert parsed["Symbols"][0]["Symbol"] == "AA"
    assert parsed["Symbols"][1]["Symbol"] == "AACC"
    master_instance = MasterData(Header=parsed["Header"])
    master_instance.Symbols = [
        MasterEntry(Symbol=el["Symbol"], Rest=el["Rest"]) for el in parsed["Symbols"]
    ]
    data = master_instance.to_construct_dict()
    assert master_data == Master.build(data)

    master_instance = MasterData()
    master_instance.set_by_construct(parsed)
    newbin=Master.build(master_instance.to_construct_dict())
    newparsed=Master.parse(newbin)
    assert newparsed["Symbols"][0]["Symbol"] == "AA"
    assert newparsed["Symbols"][1]["Symbol"] == "AACC"



def test_SymbolData(symbol_spce):
    space = SymbolConstruct.parse(symbol_spce)
    symbdata = SymbolData().set_by_construct(space)
    newbin = SymbolConstruct.build(symbdata.to_construct_dict())
    newparsed = SymbolConstruct.parse(newbin)

    assert newparsed["Entries"][0][DATEPACKED]["Year"] == 2017
    assert newparsed["Entries"][0][OPEN] == 10.5



