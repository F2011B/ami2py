from .ami_reader import AmiReader
from .ami_dataclasses import SymbolEntry, SymbolData
from .ami_construct import Master, SymbolConstruct
from pathlib import Path
import os


def symbolpath(root, symbol):
    return os.path.join(root, f"{symbol[0].lower()}/{symbol}")


class AmiDataBase:
    def __init__(self, folder, use_compiled=False):
        if not os.path.exists(folder):
            os.mkdir(folder)
        self.reader = AmiReader(folder, use_compiled=use_compiled)
        self._symbol_cache = {}
        self._fast_symbol_cache = {}
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


    def add_new_symbol(self, symbol_name, symboldata):
        self._master.append_symbol(symbol=symbol_name)
        self.read_fast_data_for_symbol(symbol_name)
        if type(symboldata) == dict:
            self._fast_symbol_cache[symbol_name] += symboldata
        if type(symboldata) == list:
            for el in symboldata:
                self._fast_symbol_cache[symbol_name] += el

    def append_to_symbol(self, symbol_name, symboldata):
        if symbol_name not in self._fast_symbol_cache:
            self.read_fast_data_for_symbol(symbol_name)
        if type(symboldata) == dict:
            self._fast_symbol_cache[symbol_name] += symboldata
        if type(symboldata) == list:
            for el in symboldata:
                self._fast_symbol_cache[symbol_name] += el

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

    def ensure_symbol_folder(self, symbol):
        Path(os.path.join(self.folder, symbol[0].lower())).mkdir(
            parents=True, exist_ok=True
        )

    def write_database(self):
        con_data = self._master.to_construct_dict()
        newbin = Master.build(con_data)
        f = open(self._master_path, "wb")
        try:
            f.write(newbin)
        finally:
            f.close()
        for symbol in self._fast_symbol_cache:
            newbin = self._fast_symbol_cache[symbol].binary
            self.ensure_symbol_folder(symbol)
            f = open(symbolpath(self.folder, symbol), "wb")
            try:
                f.write(newbin)
            finally:
                f.close()

        for symbol in self._symbol_cache:
            newbin = SymbolConstruct.build(
                self._symbol_cache[symbol].to_construct_dict()
            )
            self.ensure_symbol_folder(symbol)
            f = open(symbolpath(self.folder, symbol), "wb")
            try:
                f.write(newbin)
            finally:
                f.close()

    def read_data_for_symbol(self, symbol_name):
        self._symbol_cache[symbol_name] = self.reader.get_symbol_data(symbol_name)

    def read_fast_data_for_symbol(self, symbol_name):
        self._fast_symbol_cache[symbol_name] = self.reader.get_fast_symbol_data(
            symbol_name
        )

    def read_raw_data_for_symbol(self, symbol_name):
        return self.reader.get_symbol_data_raw(symbol_name)

    def get_dict_for_symbol(self, symbol_name):
        if symbol_name in self._symbol_cache:
            return self._symbol_cache[symbol_name].to_dict()

        self.read_data_for_symbol(symbol_name)
        return self._symbol_cache[symbol_name].to_dict()

    def get_symbol_data(self, symbol_name):
        if symbol_name in self._symbol_cache:
            return self._symbol_cache[symbol_name]

        self.read_data_for_symbol(symbol_name)
        return self._symbol_cache[symbol_name]

    def get_fast_symbol_data(self, symbol_name):
        if symbol_name in self._fast_symbol_cache:
            return self._fast_symbol_cache[symbol_name]

        self.read_fast_data_for_symbol(symbol_name)
        return self._fast_symbol_cache[symbol_name]

    def append_symbole_entry(self, symbol, data: SymbolEntry):
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

    def append_symbol_data(self, symbol_data):
        """

        :param symbol_data:
        :return:
        """

        assert type(symbol_data) == dict
        for symbol in symbol_data:
            assert type(symbol_data[symbol]) == dict
            all(el in symbol_data[symbol] for el in SymbolEntry.get_necessary_args())
            symbol_lengths = [len(symbol_data[symbol][k]) for k in symbol_data[symbol]]
            assert min(symbol_lengths) == max(symbol_lengths)
            data = [
                SymbolEntry(
                    **{k: symbol_data[symbol][k][i] for k in symbol_data[symbol]}
                )
                for i in range(max(symbol_lengths))
            ]
            if symbol not in self._symbol_cache:
                self._symbol_cache[symbol] = SymbolData(Entries=data)
            else:
                self._symbol_cache[symbol].append(data)
