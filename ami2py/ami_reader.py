import pandas as pd
from construct import Struct, Bytes, GreedyRange, swapbitsinbytes
from .amibitstructs import create_entry_chunk
from .consts import YEAR, DAY, MONTH, CLOSE, OPEN, HIGH, LOW, VOLUME, DATEPACKED
import os

VALUE_INDEX = 2
BROKER_MASTER = "broker.master"


def extract_symbols_from_db(binarr):
    datapart = binarr[0x4A0:]
    # 494 bytes - 5bytes = 489
    a = Struct("Symbol" / Bytes(5), "Rest" / Bytes(1172 - 5))
    greedy_parser = GreedyRange(a)
    data_lines = greedy_parser.parse(datapart)
    return [data["Symbol"].decode("ascii").rstrip("\x00") for data in data_lines]


class AmiReader:
    def __init__(self, folder):
        self.__folder = folder
        self.__symbols = self.__read_symbols()

    def __read_symbols(self):
        binarry, errorstate, errmsg=self.__get_binarry(BROKER_MASTER)
        if errorstate:
            return []
        return extract_symbols_from_db(binarry)

    def __get_binarry(self, filename):
        '''

        :param filename:
        :return: binarray, error state, errormsg
        '''
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
        binarry, errorstate, errmsg=self.__get_binarry(symbol_name)
        if errorstate:
            return []
        return read_symbol_file_data_part(binarry)

    def get_symbol_data_pandas(self, symbol_name):
        symbdata = self.get_symbol_data_raw(symbol_name)
        return convert_to_data_frame(symbdata[VALUE_INDEX])



def read_symbol_file_data_part(binfile):
    datapart = binfile[0x4A0:]
    data = swapbitsinbytes(datapart)
    a = create_entry_chunk()
    chunksize = 40
    parsed = a.parse(data[:chunksize])
    assert parsed["DatePacked"][YEAR] == 2017
    start = 0
    end = chunksize
    values = {
        DAY: [],
        MONTH: [],
        YEAR: [],
        CLOSE: [],
        OPEN: [],
        HIGH: [],
        LOW: [],
        VOLUME: [],
    }
    packed_map = {
        DAY: lambda x: x[DATEPACKED][DAY],
        MONTH: lambda x: x[DATEPACKED][MONTH],
        YEAR: lambda x: x[DATEPACKED][YEAR],
    }
    greedy_parser = GreedyRange(a)
    data_lines = greedy_parser.parse(data)
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
    return chunksize, data, values


def convert_to_data_frame(values):
    df = pd.DataFrame(
        values, columns=[DAY, MONTH, YEAR, OPEN, HIGH, LOW, CLOSE, VOLUME]
    )
    df["Date"] = pd.to_datetime(df.loc[:, [DAY, MONTH, YEAR]])
    return df