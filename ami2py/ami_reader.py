import pandas as pd
from construct import Struct, Bytes, GreedyRange
from .ami_dataclasses import SymbolEntry, SymbolData
from .ami_construct import SymbolConstruct, Master
from .consts import YEAR, DAY, MONTH, CLOSE, OPEN, HIGH, LOW, VOLUME, DATEPACKED
import os

VALUE_INDEX = 2
BROKER_MASTER = "broker.master"

class AmiReader:
    def __init__(self, folder):
        self.__folder = folder
        self.__master = self._read_master()
        self.__symbols = self.__read_symbols()

    def get_master(self):
        return self.__master

    def _read_master(self):
        binarry, errorstate, errmsg = self.__get_binarry(BROKER_MASTER)
        if errorstate:
            return []
        return Master.parse(binarry)

    def __read_symbols(self):
        return [el["Symbol"] for el in self.__master["Symbols"]]

    def __get_binarry(self, filename):
        """

        :param filename:
        :return: binarray, error state, errormsg
        """
        if not os.path.isdir(self.__folder):
            return [], True, f"{self.__folder} is not a directory"
        brokerfile = os.path.join(self.__folder, filename)

        if not os.path.isfile(brokerfile):
            return [], True, f"{brokerfile} is not a file"
        binarry = open(brokerfile, "rb").read()
        return binarry, False, ""

    def get_symbols(self):
        return self.__symbols.copy()

    def get_symbol_data_raw(self, symbol_name):
        binarry, errorstate, errmsg = self.__get_binarry(symbol_name)
        if errorstate:
            return []
        data = SymbolConstruct.parse(binarry)
        return read_symbol_file_data_part(data)

    def get_symbol_data_pandas(self, symbol_name):
        symbdata = self.get_symbol_data_raw(symbol_name)
        return convert_to_data_frame(symbdata)

    def get_symbol_data(self, symbol_name):
        binarry, errorstate, errmsg = self.__get_binarry(symbol_name)
        data = SymbolConstruct.parse(binarry)
        values = [
            SymbolEntry(
                open=el[OPEN],
                low=el[LOW],
                high=el[HIGH],
                close=el[CLOSE],
                volume=el[VOLUME],
                day=el[DATEPACKED][DAY],
                month=el[DATEPACKED][MONTH],
                year=el[DATEPACKED][YEAR],
            )
            for el in data["Entries"]
        ]
        return SymbolData(values)


def read_symbol_file_data_part(data):
    packed_map = {
        DAY: lambda x: x[DATEPACKED][DAY],
        MONTH: lambda x: x[DATEPACKED][MONTH],
        YEAR: lambda x: x[DATEPACKED][YEAR],
    }
    data_lines = data["Entries"]
    values = [
        (
            packed_map[DAY](el),
            packed_map[MONTH](el),
            packed_map[YEAR](el),
            el[OPEN],
            el[HIGH],
            el[LOW],
            el[CLOSE],
            el[VOLUME],
        )
        for el in data_lines
    ]
    return values

def convert_to_data_frame(values):
    df = pd.DataFrame(
        values, columns=[DAY, MONTH, YEAR, OPEN, HIGH, LOW, CLOSE, VOLUME]
    )
    df["Date"] = pd.to_datetime(df.loc[:, [DAY, MONTH, YEAR]])
    return df

