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
To use the underlying constructs in compiled form, use_compiled can be set to True within the  
AmiDataBase constructor. This is a more or less experimental feature.

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

    >>> db.get_dict_for_symbol("SPCE")
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

Todos
--------------------
* Write tests for intraday data, currently data structures is able to handle intraday data. 
  But no tests had been written, until now. 
  This is considered mandatory to reach version 1.0.0  
* Add docstrings to the source code. This seems to be a minor task.






