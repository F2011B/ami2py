from ami2py import AmiDataBase
from ami2py import SymbolEntry
import os
import shutil

test_data_folder = os.path.dirname(__file__)


def test_AmiDataBase_should_get_symbols():
    test_database_folder = os.path.join(test_data_folder, "./TestData")
    db = AmiDataBase(test_database_folder)
    symbols = db.get_symbols()
    assert "AAP" in symbols
    assert "AAPL" in symbols


def test_AmiDataBase_should_get_dict_for_symbol():
    test_database_folder = os.path.join(test_data_folder, "./TestData")
    db = AmiDataBase(test_database_folder)
    # Only data for the symbol SPCE is contained in the TestData folder !!
    aapl = db.get_dict_for_symbol("SPCE")
    assert len(aapl["Close"]) > 10
    assert aapl["Day"][0] == 29
    assert aapl["Month"][0] == 9
    assert aapl["Year"][0] == 2017


def test_AmiDataBase_should_append_symbol_entry():
    test_database_folder = os.path.join(test_data_folder, "./TestData")
    db = AmiDataBase(test_database_folder)
    # Only data for the symbol SPCE is contained in the TestData folder !!
    try:
        db.append_symbole_entry(
            "AAPL",
            SymbolEntry(
                Close=200.0,
                High=230.0,
                Low=190.0,
                Open=210.0,
                Volume=200003122.0,
                Month=12,
                Year=2020,
                Day=17,
            ),
        )
        db.append_symbole_entry(
            "AAPL",
            SymbolEntry(
                Close=200,
                High=230.0,
                Low=190,
                Open=210.0,
                Volume=200003122.0,
                Month=12,
                Year=2020,
                Day=18,
            ),
        )
    except:
        assert False
    assert True
    aapl = db.get_dict_for_symbol("AAPL")
    assert len(aapl["Close"]) == 2
    assert aapl["Day"][0] == 17
    assert aapl["Day"][1] == 18


def test_AmiDataBase_should_append_symbol_data():
    test_database_folder = os.path.join(test_data_folder, "./TestData")
    db = AmiDataBase(test_database_folder)
    # Only data for the symbol SPCE is contained in the TestData folder !!
    try:
        db.append_symbol_data(
            {
                "AAPL": {
                    "Close": [200.0, 201.0],
                    "High": [202, 203],
                    "Low": [199, 199.1],
                    "Open": [200, 200],
                    "Volume": [200001212.0, 213001311],
                    "Month": [12, 12],
                    "Year": [2020, 2020],
                    "Day": [17, 18],
                },
            }
        )
    except:
        assert False
    assert True
    aapl = db.get_dict_for_symbol("AAPL")
    assert len(aapl["Day"]) == 2


def test_AmiDataBase_should_create_new_db():
    # Setup folders
    test_database_folder = os.path.join(test_data_folder, "./NewData")
    if os.path.exists(test_database_folder):
        shutil.rmtree(test_database_folder)
    os.mkdir(test_database_folder)
    # Create Amibroker Database
    db = AmiDataBase(test_database_folder)
    db.add_symbol("AAPL")
    try:
        db.append_symbole_entry(
            "AAPL",
            SymbolEntry(
                Close=200.0,
                High=230.0,
                Low=190.0,
                Open=210.0,
                Volume=200003122.0,
                Month=12,
                Year=2020,
                Day=17,
            ),
        )
    except:
        assert False
    db.write_database()
    assert os.path.exists(os.path.join(test_database_folder, "a\\AAPL"))
    assert os.path.exists(os.path.join(test_database_folder, "broker.master"))
