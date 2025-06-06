from .ami_reader import AmiReader
from .ami_dataclasses import SymbolEntry, SymbolData
from .ami_construct import Master, SymbolConstruct
from pathlib import Path
import os

from .ami_database_folder_layout import AmiDbFolderLayout


def symbolpath(root, symbol):
    return os.path.join(root, f"{symbol[0].lower()}/{symbol}")


class AmiDataBase(AmiDbFolderLayout):
    def __init__(self, folder, use_compiled=False, avoid_windows_file=True):
        if not os.path.exists(folder):
            os.mkdir(folder)
        self.avoid_windows_file = avoid_windows_file
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

    def add_new_symbol(self, symbol_name, symboldata=None):
        if self.avoid_windows_file:
            new_symbol_name = self._replace_windows_pipe_file(symbol_name)
            self._add_new_symbol(new_symbol_name, symboldata)
        else:
            self._add_new_symbol(symbol_name, symboldata)

    def _replace_windows_pipe_file(self, symbol_name):
        wfiles = ["CON", "AUX", "LST", "PRN", "NUL", "EOF", "INP", "OUT"]
        result = symbol_name
        if symbol_name[:3] in wfiles:
            result = symbol_name.replace(symbol_name[:3], "_".join(symbol_name[:3]))
        return result

    def _add_new_symbol(self, symbol_name, symboldata=None):
        self._master.append_symbol(symbol=symbol_name)
        self.read_fast_data_for_symbol(symbol_name)
        if isinstance(symboldata, dict):
            self._fast_symbol_cache[symbol_name] += symboldata
        if isinstance(symboldata, list):
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
        """Append data provided as dictionaries to the fast symbol cache.

        Parameters
        ----------
        input_dict : dict
            Mapping of symbol name to data. The data can either be a list of
            dictionaries describing the individual rows or a dictionary of
            column lists (as returned by ``get_symbol_data_dictionary``).
        """

        assert isinstance(input_dict, dict)

        for symbol, data in input_dict.items():
            if symbol not in self._fast_symbol_cache:
                self.read_fast_data_for_symbol(symbol)

            # data may be a list of dictionaries
            if isinstance(data, list):
                for entry in data:
                    self._fast_symbol_cache[symbol] += entry
                continue

            # or a dictionary with column lists
            if isinstance(data, dict):
                if all(isinstance(v, list) for v in data.values()):
                    if len(data) > 0:
                        length = len(next(iter(data.values())))
                        for i in range(length):
                            entry = {k: v[i] for k, v in data.items()}
                            self._fast_symbol_cache[symbol] += entry
                else:
                    self._fast_symbol_cache[symbol] += data

    def store_symbol(self, symbol_name):
        if symbol_name in self._symbol_cache:
            data = self._symbol_cache[symbol_name].to_construct_dict()
            newbin = SymbolConstruct.build(data)
            with open(os.path.join(self.folder, symbol_name), "wb") as f:
                f.write(newbin)

    def ensure_symbol_folder(self, symbol):
        symb_root = self.get_symbol_root_folder(symbol)
        Path(os.path.join(self.folder, symb_root)).mkdir(parents=True, exist_ok=True)

    def write_database(self):
        con_data = self._master.to_construct_dict()
        newbin = Master.build(con_data)
        with open(self._master_path, "wb") as f:
            f.write(newbin)
        for symbol in self._fast_symbol_cache:
            newbin = self._fast_symbol_cache[symbol].binary
            self.ensure_symbol_folder(symbol)
            with open(self._get_symbol_path(self.folder, symbol), "wb") as f:
                f.write(newbin)

        for symbol in self._symbol_cache:
            newbin = SymbolConstruct.build(
                self._symbol_cache[symbol].to_construct_dict()
            )
            self.ensure_symbol_folder(symbol)
            with open(self._get_symbol_path(self.folder, symbol), "wb") as f:
                f.write(newbin)

    def read_data_for_symbol(self, symbol_name):
        self._symbol_cache[symbol_name] = self.reader.get_symbol_data(symbol_name)

    def read_fast_data_for_symbol(self, symbol_name):
        self._fast_symbol_cache[symbol_name] = self.reader.get_fast_symbol_data(
            symbol_name
        )

    def read_raw_data_for_symbol(self, symbol_name):
        return self.reader.get_symbol_data_raw(symbol_name)

    def get_dict_for_symbol(self, symbol_name, force_refresh=False):
        if force_refresh or symbol_name not in self._symbol_cache:
            self.read_data_for_symbol(symbol_name)
        return self._symbol_cache[symbol_name].to_dict()

    def get_symbol_data(self, symbol_name, force_refresh=False):
        if force_refresh or symbol_name not in self._symbol_cache:
            self.read_data_for_symbol(symbol_name)
        return self._symbol_cache[symbol_name]

    def get_fast_symbol_data(self, symbol_name, force_refresh=False):
        if force_refresh or symbol_name not in self._fast_symbol_cache:
            self.read_fast_data_for_symbol(symbol_name)
        return self._fast_symbol_cache[symbol_name]

    def append_symbol_entry(self, symbol, data: SymbolEntry):
        """Append a :class:`SymbolEntry` to ``symbol``.

        This method supersedes the old :func:`append_symbole_entry` with the
        correct spelling and simply forwards to it for backwards
        compatibility.
        """
        return self.append_symbole_entry(symbol, data)

    def append_symbole_entry(self, symbol, data: SymbolEntry):
        """
        :param symbol: name of the symbol to which data should be appended
        :param data: Instance of SymbolEntry
        :return:
        """
        self._modified_symbols.append(symbol)
        if symbol not in self._symbol_cache:
            symbol_path = self._get_symbol_path(self.folder, symbol)
            if os.path.isfile(symbol_path):
                # load existing data so appending does not overwrite
                self.read_data_for_symbol(symbol)
            else:
                self._symbol_cache[symbol] = SymbolData()

        self._symbol_cache[symbol].append(data)

    def append_symbol_data(self, symbol_data):
        """

        :param symbol_data:
        :return:
        """

        assert type(symbol_data) == dict
        for symbol in symbol_data:
            assert type(symbol_data[symbol]) == dict
            assert all(
                el in symbol_data[symbol] for el in SymbolEntry.get_necessary_args()
            )
            symbol_lengths = [len(symbol_data[symbol][k]) for k in symbol_data[symbol]]
            assert min(symbol_lengths) == max(symbol_lengths)
            data = [
                SymbolEntry(
                    **{k: symbol_data[symbol][k][i] for k in symbol_data[symbol]}
                )
                for i in range(max(symbol_lengths))
            ]
            if symbol not in self._symbol_cache:
                symbol_path = self._get_symbol_path(self.folder, symbol)
                if os.path.isfile(symbol_path):
                    self.read_data_for_symbol(symbol)
                else:
                    self._symbol_cache[symbol] = SymbolData()
            for entry in data:
                self._symbol_cache[symbol].append(entry)
