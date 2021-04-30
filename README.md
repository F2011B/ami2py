 ami2py
==========================

[![Build Status](https://travis-ci.org/F2011B/ami2py.svg?branch=master)](https://travis-ci.org/F2011B/ami2py)
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

Examples
---------

Creating a Database from scratch and adding symbol data to the database. 

    >>> from ami2py import AmiDataBase, SymbolEntry
    >>> db = AmiDataBase(db_folder)
    >>> db.add_symbol("AAPL")    
    >>> db.append_data_to_symbol(
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

Getting values for a symbol in a pandas compatible dicitonary format.

    >>> data = aapl = db.get_dict_for_symbol("SPCE")
    {
        "Open": [20.0,....],
        "Close": [200.0,....],
        "High": [230.0,.....],
        "Low": [190.0,.....],
        "Open": [210.0,.......],
        "Volume": [200003122.0,.....],
        "Month": [12,.......],
        "Year": [2020,.......],
        "Day": [17,........],
    }

Todos
--------------------
* Write tests for intraday data, currently data structures is able to handle intraday data. 
  But no tests had been written, until now. 
  This is considered mandatory to reach version 1.0.0  
* Add docstrings to the source code. This seems to be a minor task.
* Currently no real life performance measures have been done. 






