 ami2py
==========================

[![CI](https://github.com/F2011B/ami2py/actions/workflows/tests.yml/badge.svg)](https://github.com/F2011B/ami2py/actions/workflows/tests.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPi version](https://pypip.in/v/ami2py/badge.png)](https://crate.io/packages/ami2py/)
[![PyPi downloads](https://pypip.in/d/ami2py/badge.png)](https://crate.io/packages/ami2py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ami2py](https://snyk.io/advisor/python/ami2py/badge.svg)](https://snyk.io/advisor/python/ami2py)

Python Package for reading and writing from and to an amibroker database.<br/>
This package is using construct for defining the binary structures used to access the amibroker database, 
see [Construct documentation](https://construct.readthedocs.io/en/latest/). <br/>
The specification of the binary structure was taken from the official amibroker C++ sdk api documentation.

However, this is not an official amibroker database api. <br/> 
Therefore, no warranty is given and handle with care. <br/>
Improvement requests are always welcome.<br/>
This module can be used to create a database and write symbol data to that. <br/> 
However, it seems to be a good idea to use the official quote downloader program for productive usage.<br/>
__________________________________________________

Unofficial Resource
-------------------
A community-written overview is available at
[deepwiki.com/F2011B/ami2py](https://deepwiki.com/F2011B/ami2py). This
guide is unofficial and may become outdated.

Important
---------
On Windows there are special file names, e.g. "CON"
In case such a file is opened and data is written into every data written 
is printed to the console.
Therefore, by default the command add_new_symbol renames symbol names like CON.DE into C_O_N.DE.

Examples
---------

Creating a Database from scratch and adding symbol data to the database.
To use the underlying constructs in compiled form, use_compiled can be set to True within the  
AmiDataBase constructor. This is a more or less experimental feature.

    >>> from ami2py import AmiDataBase, SymbolEntry
    >>> db = AmiDataBase(db_folder)
    >>> db.add_symbol("AAPL")    
    >>> db.append_symbol_entry(
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
    >>> db.write_database()

Reading a list of symbols contained in the database.

    >>> symbols = db.get_symbols()
    >>> symbols
    ["AAPL"]

Getting values for a symbol in a pandas compatible dictionary format.

    >>> db.get_dict_for_symbol("SPCE")
    {
        "Open": [20.0,....],
        "Close": [200.0,....],
        "High": [230.0,.....],
        "Low": [190.0,.....],
        "Volume": [200003122.0,.....],
        "Month": [12,.......],
        "Year": [2020,.......],
        "Day": [17,........],
    }

`get_dict_for_symbol` caches the returned data for subsequent calls. If the
underlying database has changed, pass `force_refresh=True` to reload the latest
values from disk:

```python
>>> db.get_dict_for_symbol("SPCE", force_refresh=True)
```

Reading index data
------------------

Index files in an AmiBroker database use symbol names beginning with ``^``.
These can be accessed like any other symbol:

```python
>>> db.get_dict_for_symbol("^GDAXI")
```

Using a list container facade for fast reading of symbol data. 
The previous mentioned methods to read symbol data from the database use construct to 
convert the binary array into a hierarchical object structure. 
Creating those objects during the load process, causes high delay during loading. 
Therefore a symbol facade called AmiSymbolDataFacade was created to read data only in case 
it is necessary.

     >>> data = db.get_fast_symbol_data("SPCE")
     >>> data[0]
     {'Year': 2017, 
      'Month': 9, 
      'Day': 29, 
      'Hour': 10, 
      'Minute': 63, 
      'Second': 63, 
      'MilliSec': 258, 
      'MicroSec': 255, 
      'Reserved': 1,  
      'Isfut': 1,  
      'Close': 10.100000381469727, 
      'Open': 10.5, 
      'High': 10.5, 
      'Low': 10.0, 
      'Volume': 212769.0, 
      'AUX1': 0.0, 
      'AUX2': 0.0,  
      'TERMINATOR': 0.0
     }
     >>> newslice=data[0:10] 
     >>> newslice[0]
     {'Year': 2017,
      'Month': 9,
      ......
     }
     >>> newslice[1]
     {'Year': 2017,
      'Month': 10,
       ......
     }
Updating a database from Yahoo
------------------------------

A helper script ``scripts/update_yahoo_db.py`` can download new daily data from Yahoo Finance for all symbols already present in a database. The script reads the last stored date for each symbol and only fetches the missing days before appending them to the database.

```bash
python scripts/update_yahoo_db.py /path/to/db
```

Command Line Interface
----------------------

The `ami_cli` directory contains a small command line tool written in Rust
that wraps the Python API via PyO3. Build it using
`cargo build --manifest-path ami_cli/Cargo.toml --release` and use it like:

```bash
ami_cli <command> [args]
  create <db_path> <symbol1> [symbol2 ...]
  add-symbol <db_path> <symbol1> [symbol2 ...]
  list-symbols <db_path>
```

On Windows you can use the helper script `scripts\build_cli_windows.bat` to
compile `ami_cli.exe` in release mode. The resulting executable can be found
under `ami_cli\target\release\ami_cli.exe`.

Todos
--------------------
* Write tests for intraday data, currently data structures is able to handle intraday data. 
  But no tests had been written, until now. 
  This is considered mandatory to reach version 1.0.0  
* Add docstrings to the source code. This seems to be a minor task.

FAQs
--------------------
This section collects frequently asked questions about ami2py.

Codebase Overview
-----------------
The **ami2py** library is used to read from and write to AmiBroker databases
with Python. The README explains that `construct` is used for the binary
structures and that the project does not represent an official AmiBroker API.

* `ami2py/`
  * `ami_bitstructs.py` – defines bit structures for individual data entries.
  * `ami_construct.py` – assembles the complete structures (master file,
    symbol file).
  * `ami_dataclasses.py` – dataclasses for symbol and master data.
  * `ami_database.py` – central `AmiDataBase` class for reading and writing a
    database; uses `AmiReader`.
  * `ami_reader.py` – reads existing databases and returns dataclasses or
    faster "facade" objects.
  * `ami_symbol_facade.py` – fast access to symbol data without full parsing.
  * `consts.py` – constants such as `DAY`, `MONTH` etc.
* `tests/` – contains unit tests and test data.

The README shows an example in which a database is created, a symbol is added
and data is appended. Afterwards the database can be written to disk and later
read again.

Key Points
----------
1. **Construct structures** – the binary formats of AmiBroker files are defined
   using `construct`. Anyone working with the project should get familiar with
   this package.
2. **Dataclasses** – Python dataclasses exist for symbol data (`SymbolEntry`,
   `SymbolData`) and the master file (`MasterData`) with validation.
3. **Fast data access** – `AmiSymbolDataFacade` offers slicing and appending on
   the binary level to handle large data volumes efficiently.
4. **Database folder layout** – `AmiDbFolderLayout` specifies in which subfolder
   symbols are stored (e.g. `a/AAPL`).


### Optional Rust Backend

The bit parsing logic can optionally be executed using a Rust implementation. Set
`AMI2PY_USE_RUST=1` in the environment to activate the Rust backend (requires the
`rust_bitparser` extension to be built). If the extension is not available, the
library falls back to the pure Python implementation.

The included `run_tests.sh` script automatically compiles the Rust extension before running the tests. It uses an offline build by default but switches to an online build when the `CIRCLECI` environment variable is present. In this case the script also sets `CARGO_NET_OFFLINE=false` to override any offline Cargo configuration. If you want to build it manually, execute:

```bash
cargo build --manifest-path rust_bitparser/Cargo.toml --release --offline
# Linux/macOS
cp rust_bitparser/target/release/librust_bitparser.so ami2py/rust_bitparser.so
# Windows
cp rust_bitparser/target/release/rust_bitparser.dll ami2py/rust_bitparser.pyd
```

This will make the Rust backend available when `AMI2PY_USE_RUST=1` is set.
