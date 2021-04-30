from construct import Struct, Bytes, GreedyRange
from .ami_dataclasses import SymbolEntry, SymbolData, MasterData
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
            return MasterData()

        parsed = Master.parse(binarry)
        return MasterData().set_by_construct(parsed)

    def __read_symbols(self):
        return self.__master.get_symbols()

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
        return data

    def get_symbol_data_dictionary(self, symbol_name):
        symbdata = self.get_symbol_data_raw(symbol_name)
        packed_map = {
            DAY: lambda x: x[DATEPACKED][DAY],
            MONTH: lambda x: x[DATEPACKED][MONTH],
            YEAR: lambda x: x[DATEPACKED][YEAR],
        }
        data_lines = symbdata["Entries"]
        result = {
            DAY: [],
            MONTH: [],
            YEAR: [],
            OPEN: [],
            HIGH: [],
            LOW: [],
            CLOSE: [],
            VOLUME: [],
        }
        for el in data_lines:
            for k in result:
                if k in [DAY, MONTH, YEAR]:
                    result[k].append(el[DATEPACKED][k])
                else:
                    result[k].append(el[k])

        return result

    def get_symbol_data(self, symbol_name):
        binarry, errorstate, errmsg = self.__get_binarry(symbol_name)
        data = SymbolConstruct.parse(binarry)
        values = [
            SymbolEntry(
                Open=el[OPEN],
                Low=el[LOW],
                High=el[HIGH],
                Close=el[CLOSE],
                Volume=el[VOLUME],
                Day=el[DATEPACKED][DAY],
                Month=el[DATEPACKED][MONTH],
                Year=el[DATEPACKED][YEAR],
            )
            for el in data["Entries"]
        ]
        return SymbolData(Header=data["Header"], Entries=values)
