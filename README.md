ami2py
==========================
<p align="center">
  <img src="logo.png" alt="ami2py logo" width="50%" height="50%" />
</p>

[![CI](https://github.com/F2011B/ami2py/actions/workflows/tests.yml/badge.svg)](https://github.com/F2011B/ami2py/actions/workflows/tests.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPi version](https://pypip.in/v/ami2py/badge.png)](https://crate.io/packages/ami2py/)
[![PyPi downloads](https://pypip.in/d/ami2py/badge.png)](https://crate.io/packages/ami2py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ami2py](https://snyk.io/advisor/python/ami2py/badge.svg)](https://snyk.io/advisor/python/ami2py)

## Index
- [Short Introduction](#short-introduction)
- [Python Package API](#python-package-api)
- [Examples](#examples)
- [RUST Backend](#rust-backend)
- [ami_cli](#ami_cli)
- [Examples](#examples-1)
- [Architecture Overview](#architecture-overview)
- [FAQs](#faqs)

## Short Introduction

Python package for reading and writing AmiBroker databases. The binary structures
are defined using [`construct`](https://construct.readthedocs.io/en/latest/) and
are based on the official AmiBroker C++ SDK. This project is **not** an official
AmiBroker API and comes without any warranty. Improvement requests are welcome,
but for production usage the official quote downloader might still be the better
choice.

Unofficial Resource
-------------------
A community-written overview is available at
[deepwiki.com/F2011B/ami2py](https://deepwiki.com/F2011B/ami2py). This guide is
unofficial and may become outdated.

Important
---------
On Windows there are reserved file names such as `CON`. If such a file is opened
and data is written, the output is printed to the console. Therefore the command
`add_new_symbol` renames symbols like `CON.DE` to `C_O_N.DE` by default.

## Python Package API

The Python module allows you to create new databases and read or append quote
information. `ami2py` exposes dataclasses for the master file and individual
symbol records and supports a fast facade for large data volumes.

### Examples

Creating a database from scratch and adding symbol data:

```python
from ami2py import AmiDataBase, SymbolEntry

db = AmiDataBase(db_folder)
db.add_symbol("AAPL")
db.append_symbol_entry(
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
db.write_database()
```

Read a list of symbols stored in the database:

```python
symbols = db.get_symbols()
print(symbols)
```

Get values for a symbol in a pandas compatible dictionary format:

```python
db.get_dict_for_symbol("SPCE")
```

`get_dict_for_symbol` caches the returned data. Pass
`force_refresh=True` to reload the latest values from disk:

```python
db.get_dict_for_symbol("SPCE", force_refresh=True)
```

Reading index data:

```python
db.get_dict_for_symbol("^GDAXI")
```

Using a list container facade for fast reading of symbol data:

```python
data = db.get_fast_symbol_data("SPCE")
newslice = data[0:10]
```

Updating a database from Yahoo:

```bash
python scripts/update_yahoo_db.py /path/to/db
```

## RUST Backend

The parsing logic can optionally be executed using a Rust implementation.
Set the environment variable `AMI2PY_USE_RUST=1` to activate it (requires the
`rust_bitparser` extension to be built). The included `run_tests.sh` script
builds the extension automatically. Manual build is possible with:

```bash
cargo build --manifest-path rust/rust_bitparser/Cargo.toml --release --offline
```

## ami_cli

The `rust/ami_cli` directory contains a small command line tool written in Rust
that wraps the Python API via PyO3. Build it using
`cargo build --manifest-path rust/ami_cli/Cargo.toml --release`.

### Examples

```bash
ami_cli <command> [args]
  create <db_path> <symbol1> [symbol2 ...]
  add-symbol <db_path> <symbol1> [symbol2 ...]
  list-symbols <db_path>
  list-quotes <db_path> <symbol> [start YYYY-MM-DD end YYYY-MM-DD]
  add-quotes <db_path> <symbol> <csv_file>
```

On Windows use `scripts\build_cli_windows.bat` to compile `ami_cli.exe`. The
executable will be found under `rust\ami_cli\target\release\ami_cli.exe`.

## Architecture Overview

The **ami2py** library is used to read from and write to AmiBroker databases
with Python. Important parts of the code base are:

* `ami_bitstructs.py` – bit structures for individual data entries
* `ami_construct.py` – assembled binary structures
* `ami_dataclasses.py` – dataclasses for symbol and master data
* `ami_database.py` – central `AmiDataBase` class
* `ami_reader.py` – reads existing databases
* `ami_symbol_facade.py` – fast access to symbol data
* `consts.py` – various constants
* `tests/` – unit tests and test data

Key Points
----------
1. **Construct structures** – the binary formats are defined using `construct`.
2. **Dataclasses** – Python dataclasses exist for symbol data and the master
   file with validation.
3. **Fast data access** – `AmiSymbolDataFacade` allows slicing and appending at
   the binary level to handle large data volumes efficiently.
4. **Database folder layout** – `AmiDbFolderLayout` specifies in which subfolder
   symbols are stored (e.g. `a/AAPL`).

## FAQs
This section collects frequently asked questions about ami2py.

