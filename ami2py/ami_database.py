from .ami_reader import AmiReader
from .ami_dataclasses import SymbolEntry, SymbolData
from .ami_construct import Master, SymbolConstruct
import os


class AmiDataBase:
    def __init__(self, folder):
        self.reader = AmiReader(folder)
        self._symbol_cache = {}
        self._symbols = []
        self._symbol_frames = {}
        self._modified_symbols = []
        self._master = self.reader.get_master()
        self.folder = folder
        self._master_path = os.path.join(folder, "broker.master")

    def get_symbols(self):
        if len(self._symbols) == 0:
            self._symbols = self.reader.get_symbols()
        return self._symbols

    def add_symbol(self, symbol_name):
        self._master.append_symbol(symbol=symbol_name)

    def add_symbol_data_dict(self, input_dict):
        pass

    def store_symbol(self, symbol_name):
        if symbol_name in self._symbol_cache:
            data = self._symbol_cache[symbol_name].to_construct_dict()
            newbin = SymbolConstruct.build(data)
            f = open(os.path.join(self.folder, symbol_name), "wb")
            try:
                f.write(newbin)
            finally:
                f.close()

    def write_database(self):
        con_data = self._master.to_construct_dict()
        newbin = Master.build(con_data)
        f = open(self._master_path, "wb")
        try:
            f.write(newbin)
        finally:
            f.close()
        for symbol in self._symbol_cache:
            newbin = SymbolConstruct.build(self._symbol_cache[symbol].to_construct_dict())
            f = open(os.path.join(self.folder, symbol), "wb")
            try:
                f.write(newbin)
            finally:
                f.close()

    def read_data_for_symbol(self, symbol_name):
        self._symbol_cache[symbol_name] = self.reader.get_symbol_data(symbol_name)

    def get_dataframe_for_symbol(self, symbol_name):
        if symbol_name in self._symbol_cache:
            return self._symbol_cache[symbol_name].to_dataframe()

        self.read_data_for_symbol(symbol_name)
        return self._symbol_cache[symbol_name].to_dataframe()

    def get_symbol_data(self, symbol_name):
        if symbol_name in self._symbol_cache:
            return self._symbol_cache[symbol_name]

        self.read_data_for_symbol(symbol_name)
        return self._symbol_cache[symbol_name]

    def append_data_to_symbol(self, symbol, data: SymbolEntry):
        """
        :param symbol: name of the symbol to which data should be appended
        :param data: Instance of SymbolEntry
        :return:
        """
        self._modified_symbols.append(symbol)
        if symbol not in self._symbol_cache:
            self._symbol_cache[symbol] = SymbolData(Entries=[data])
            return

        self._symbol_cache[symbol].append(data)
