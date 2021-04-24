from .ami_reader import AmiReader
from .ami_dataclasses import SymbolEntry


class AmiDataBase:
    def __init__(self, folder):
        self.reader = AmiReader(folder)
        self._symbol_cache = {}
        self._symbols = []
        self._symbol_frames = {}

    def get_symbols(self):
        if len(self._symbols) == 0:
            self._symbols = self.reader.get_symbols()
        return self._symbols

    def add_symbol(self, symbol_name):
        self._symbols.append(symbol_name)

    def store_symbol(self, symbol_name):
        pass

    def read_data_for_symbol(self, symbol_name):
        self._symbol_cache[symbol_name] = self.reader.get_symbol_data(symbol_name)

    def get_dataframe_for_symbol(self, symbol_name):
        if symbol_name in self._symbol_cache:
            return self._symbol_cache[symbol_name].to_dataframe()

        self.read_data_for_symbol(symbol_name)
        return self._symbol_cache[symbol_name].to_dataframe()

    def append_data_to_symbol(self, symbol, data: SymbolEntry):
        """
        :param symbol: name of the symbol to which data should be appended
        :param data: Instance of SymbolEntry
        :return:
        """
        if symbol not in self._symbol_cache:
            self._symbol_cache[symbol] = []
        self._symbol_cache[symbol].append(data)
