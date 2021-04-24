from ami2py import SymbolEntry, SymbolData
from dataclass_type_validator import TypeValidationError

def test_SymbolEntry():
    entry = SymbolEntry(
        close=10.0, low=10.0, high=12.0, open=10.0, volume=0.0, day=10, month=11, year=2020
    )
    assert entry.day == 10


def test_SymbolData():
    entry = SymbolEntry(
        close=10.0, low=10.0, high=12.0, open=10.0, volume=0.0, day=10, month=11, year=2020
    )
    try:
        data = SymbolData(entry)
        assert False
    except TypeValidationError as e:
        assert True

    data = SymbolData([entry])
    entry = SymbolEntry(
        close=10.0, low=10.0, high=12.0, open=10.0, volume=0.0, day=11, month=11, year=2020
    )
    data.append(entry)
    assert len(data.Series) == 2

    df = data.to_dataframe()
    assert len(df["Close"]) == 2
