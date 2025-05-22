from construct import Struct, Bytes, GreedyRange
from .ami_dataclasses import SymbolEntry, SymbolData, MasterData
from .ami_construct import Master, SymbolConstruct
from .ami_symbol_facade import AmiSymbolDataFacade
# from .ami_symbol import compiled as SymbolConstruct
from .consts import YEAR, DAY, MONTH, CLOSE, OPEN, HIGH, LOW, VOLUME, DATEPACKED
import os
import mmap
from .ami_database_folder_layout import AmiDbFolderLayout

ERROR_RETURNED = True

VALUE_INDEX = 2
BROKER_MASTER = "broker.master"


class AmiReader(AmiDbFolderLayout):
    def __init__(self, folder, use_compiled=False):
        self.__folder = folder
        self.__symbol = SymbolConstruct
        self.__master = Master
        if use_compiled:
            self.__symbol = SymbolConstruct.compile(
                filename=os.path.join(os.path.dirname(__file__), "SymbolConstruct.py")
            )
            self.__master = Master.compile(
                filename=os.path.join(os.path.dirname(__file__), "Master.py")
            )

        self.__master = self._read_master()
        self.__symbols = self.__read_symbols()

    def get_master(self):
        return self.__master

    def _read_master(self):
        binarry, errorstate, errmsg = self.__get_binarry(BROKER_MASTER)
        if errorstate:
            return MasterData()

        parsed = Master.parse(binarry)
        if hasattr(binarry, "close"):
            binarry.close()
        return MasterData().set_by_construct(parsed)

    def __read_symbols(self):
        return self.__master.get_symbols()

    def __get_binarry(self, symbol_name):
        """

        :param filename:
        :return: binarray, error state, errormsg
        """
        filename=self._get_symbol_path(self.__folder, symbol_name)
        if not os.path.isfile(filename):
            return [], ERROR_RETURNED, f"{filename} is not a file"
        with open(filename, "rb") as f:
            binarry = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        return binarry, False, ""

    def get_symbols(self):
        return self.__symbols.copy()

    def get_fast_symbol_data(self, symbol_name):
        binarry, errorstate, errmsg = self.__get_binarry(
            symbol_name
        )
        if errorstate:
            return AmiSymbolDataFacade()
        facade = AmiSymbolDataFacade(binarry)
        if hasattr(binarry, "close"):
            binarry.close()
        return facade

    def get_symbol_data_raw(self, symbol_name):
        binarry, errorstate, errmsg = self.__get_binarry(symbol_name)
        if errorstate:
            return []
        data = self.__symbol.parse(binarry)
        if hasattr(binarry, "close"):
            binarry.close()
        return data

    def get_symbol_data_dictionary(self, symbol_name):
        symbdata = self.get_symbol_data_raw(symbol_name)
        if type(symbdata) == dict:
            return {}
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
        if errorstate == ERROR_RETURNED:
            return SymbolData()

        data = self.__symbol.parse(binarry)
        if hasattr(binarry, "close"):
            binarry.close()
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
