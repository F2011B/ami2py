from ami2py import AmiDataBase
from ami2py import SymbolEntry
import os
import shutil

test_data_folder = os.path.dirname(__file__)

def test_get_symbols():
    test_database_folder = os.path.join(test_data_folder, "./TestData")
    db = AmiDataBase(test_database_folder)
    symbols = db.get_symbols()
    assert "AAP" in symbols
    assert "AAPL" in symbols


def test_get_symbol_data():
    test_database_folder = os.path.join(test_data_folder, "./TestData")
    db = AmiDataBase(test_database_folder)
    # Only data for the symbol SPCE is contained in the TestData folder !!
    aapl = db.get_dataframe_for_symbol("SPCE")
    assert len(aapl["Close"].tolist()) > 10
    assert aapl["Day"][0] == 29
    assert aapl["Month"][0] == 9
    assert aapl["Year"][0] == 2017


def test_append_symbol_data():
    test_database_folder = os.path.join(test_data_folder, "./TestData")
    db = AmiDataBase(test_database_folder)
    # Only data for the symbol SPCE is contained in the TestData folder !!
    try:
        db.append_data_to_symbol(
            "AAPL",
            SymbolEntry(
                close=200.0,
                high=230.0,
                low=190.0,
                open=210.0,
                volume=200003122.0,
                month=12,
                year=2020,
                day=17,
            ),
        )
    except:
        assert False
    assert True
    aapl = db.get_dataframe_for_symbol("AAPL")
    assert len(aapl) == 1


def test_create_new_db():
    # Setup folders
    test_database_folder = os.path.join(test_data_folder, "./NewData")
    if os.path.exists(test_database_folder):
        shutil.rmtree(test_database_folder)
    os.mkdir(test_database_folder)
    # Create Amibroker Database
    db = AmiDataBase(test_database_folder)
    db.add_symbol("AAPL")
    try:
        db.append_data_to_symbol(
            "AAPL",
            SymbolEntry(
                close=200.0,
                high=230.0,
                low=190.0,
                open=210.0,
                volume=200003122.0,
                month=12,
                year=2020,
                day=17,
            ),
        )
    except:
        assert False
    db.write_database()
    assert os.path.exists(os.path.join(test_database_folder, "AAPL"))
    assert os.path.exists(os.path.join(test_database_folder, "broker.master"))
