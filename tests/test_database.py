from ami2py import AmiDataBase
from ami2py import SymbolEntry
import os
import shutil
import pytest

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

def test_AmiDataBase_should_get_fastdata_for_symbol():
    test_database_folder = os.path.join(test_data_folder, "./TestData")
    db = AmiDataBase(test_database_folder)
    symbol = db.get_fast_symbol_data("SPCE")
    assert len(symbol) > 10
    assert symbol[0]["Day"] == 29
    assert symbol[0]["Month"] == 9
    assert symbol[0]["Year"] == 2017
    assert len(symbol[0:10]) == 10

def test_AmiDataBase_should_get_fastdata_for_symbol_negative_indexed():
    test_database_folder = os.path.join(test_data_folder, "./TestData")
    db = AmiDataBase(test_database_folder)
    symbol = db.get_fast_symbol_data("SPCE")
    assert len(symbol) > 10
    assert symbol[-1]["Day"] == 19
    assert symbol[-1]["Month"] == 2
    assert symbol[-1]["Year"] == 2020
    assert round(symbol[-1]["Open"],2) == 34.3
    assert round(symbol[-1]["Close"], 2) == 37.35
    assert round(symbol[-1]["High"], 2) == 37.5
    assert round(symbol[-1]["Low"], 2) == 32

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


def test_append_symbol_data_twice_increases_entries():
    test_database_folder = os.path.join(test_data_folder, "./TestData")
    db = AmiDataBase(test_database_folder)
    first = {
        "AAPL": {
            "Close": [200.0, 201.0],
            "High": [202, 203],
            "Low": [199, 199.1],
            "Open": [200, 200],
            "Volume": [200001212.0, 213001311],
            "Month": [12, 12],
            "Year": [2020, 2020],
            "Day": [17, 18],
        }
    }
    second = {
        "AAPL": {
            "Close": [202.0, 203.0],
            "High": [204, 205],
            "Low": [200, 200.1],
            "Open": [202, 203],
            "Volume": [220001212.0, 230001311],
            "Month": [12, 12],
            "Year": [2020, 2020],
            "Day": [19, 20],
        }
    }
    db.append_symbol_data(first)
    db.append_symbol_data(second)
    aapl = db.get_dict_for_symbol("AAPL")
    assert len(aapl["Day"]) == 4


def test_AmiDataBase_should_create_new_db():
    # Setup folders
    test_database_folder = os.path.join(test_data_folder, "./NewData")
    if os.path.exists(test_database_folder):
        shutil.rmtree(test_database_folder)
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

    assert os.path.exists(os.path.join(test_database_folder, f"a/AAPL"))
    assert os.path.exists(os.path.join(test_database_folder, "broker.master"))


def test_AmiDataBase_should_create_new_db_and_add_fast_symbol_data():
    # Setup folders
    test_database_folder = os.path.join(test_data_folder, "./NewData")
    if os.path.exists(test_database_folder):
        shutil.rmtree(test_database_folder)
    # Create Amibroker Database
    db = AmiDataBase(test_database_folder)
    db.add_new_symbol(
        "AAPL",
        {
            "Day": 1,
            "Month": 10,
            "Year": 2017,
            "Close": 0.12,
            "Open": 0.3,
            "High": 0.5,
            "Low": 0.1,
            "Volume": 200121,
        },
    )
    fast_data = db.get_fast_symbol_data("AAPL")
    assert fast_data.length == 1
    db.append_to_symbol(
        "AAPL",
        [
            {
                "Day": 2,
                "Month": 10,
                "Year": 2017,
                "Close": 0.12,
                "Open": 0.3,
                "High": 0.5,
                "Low": 0.1,
                "Volume": 2001,
            },
            {
                "Day": 3,
                "Month": 10,
                "Year": 2017,
                "Close": 0.12,
                "Open": 0.3,
                "High": 0.5,
                "Low": 0.1,
                "Volume": 2001121,
            },
            {
                "Day": 4,
                "Month": 10,
                "Year": 2017,
                "Close": 0.12,
                "Open": 0.09,
                "High": 0.5,
                "Low": 0.09,
                "Volume": 2001121,
            },
        ],
    )

    assert fast_data.length == 4
    db.write_database()
    assert os.path.exists(os.path.join(test_database_folder, "a/AAPL"))


def test_AmiDataBase_should_create_new_db_and_add_fast_symbol_data_and_avoiding_windows_piping_conflicts():
    # Setup folders
    test_database_folder = os.path.join(test_data_folder, "./NewData")
    if os.path.exists(test_database_folder):
        shutil.rmtree(test_database_folder)
    # Create Amibroker Database
    db = AmiDataBase(test_database_folder)
    db.add_new_symbol(
        "CON.DE",
        {
            "Day": 1,
            "Month": 10,
            "Year": 2017,
            "Close": 0.12,
            "Open": 0.3,
            "High": 0.5,
            "Low": 0.1,
            "Volume": 200121,
        },
    )
    fast_data = db.get_fast_symbol_data("C_O_N.DE")
    assert fast_data.length == 1
    db.append_to_symbol(
        "C_O_N.DE",
        [
            {
                "Day": 2,
                "Month": 10,
                "Year": 2017,
                "Close": 0.12,
                "Open": 0.3,
                "High": 0.5,
                "Low": 0.1,
                "Volume": 2001,
            },
            {
                "Day": 3,
                "Month": 10,
                "Year": 2017,
                "Close": 0.12,
                "Open": 0.3,
                "High": 0.5,
                "Low": 0.1,
                "Volume": 2001121,
            },
            {
                "Day": 4,
                "Month": 10,
                "Year": 2017,
                "Close": 0.12,
                "Open": 0.09,
                "High": 0.5,
                "Low": 0.09,
                "Volume": 2001121,
            },
        ],
    )

    assert fast_data.length == 4
    db.write_database()
    assert os.path.exists(os.path.join(test_database_folder, "c/C_O_N.DE"))


@pytest.mark.parametrize("symbol", ["^GSPC", "@ES_C", "~~~EQUITY"])
def test_AmiDataBase_should_create_new_db_and_add_hat_containing_symbol(
    tmp_path, symbol
):
    # Setup folders
    test_database_folder = tmp_path / "NewData"
    if os.path.exists(test_database_folder):
        shutil.rmtree(test_database_folder)
    # Create Amibroker Database
    db = AmiDataBase(test_database_folder)
    db.add_new_symbol(
        symbol,
        {
            "Day": 1,
            "Month": 10,
            "Year": 2017,
            "Close": 0.12,
            "Open": 0.3,
            "High": 0.5,
            "Low": 0.1,
            "Volume": 200121,
        },
    )
    fast_data = db.get_fast_symbol_data(symbol)
    assert fast_data.length == 1
    db.append_to_symbol(
        symbol,
        [
            {
                "Day": 2,
                "Month": 10,
                "Year": 2017,
                "Close": 0.12,
                "Open": 0.3,
                "High": 0.5,
                "Low": 0.1,
                "Volume": 2001,
            },
            {
                "Day": 3,
                "Month": 10,
                "Year": 2017,
                "Close": 0.12,
                "Open": 0.3,
                "High": 0.5,
                "Low": 0.1,
                "Volume": 2001121,
            },
            {
                "Day": 4,
                "Month": 10,
                "Year": 2017,
                "Close": 0.12,
                "Open": 0.09,
                "High": 0.5,
                "Low": 0.09,
                "Volume": 2001121,
            },
        ],
    )

    assert fast_data.length == 4
    db.write_database()
    assert os.path.exists(os.path.join(test_database_folder, f"_/{symbol}"))


def test_AmiDataBase_can_read_index_symbol(index_db):
    db = AmiDataBase(index_db)
    gdaxi = db.get_dict_for_symbol("^GDAXI")
    assert gdaxi["Day"][0] == 3
    assert gdaxi["Month"][0] == 1
    assert gdaxi["Month"][-1] == 11
    assert gdaxi["Close"][0] == 6750.759765625


def test_AmiDataBase_can_read_tilde_symbol(index_db):
    db = AmiDataBase(index_db)
    equity = db.get_dict_for_symbol("~~~EQUITY")
    assert equity["Day"][0] == 2
    assert equity["Month"][0] == 1
    assert equity["Year"][0] == 1996


def test_AmiDataBase_can_read_at_symbol(index_db):
    db = AmiDataBase(index_db)
    equity = db.get_dict_for_symbol("@ES_C")
    assert equity["Day"][0] == 29
    assert equity["Month"][0] == 8
    assert equity["Year"][0] == 2003