from dataclasses import dataclass, field
from dataclass_type_validator import dataclass_validate
from typing import List
import pandas as pd
from .consts import (
    DAY,
    MONTH,
    CLOSE,
    OPEN,
    HIGH,
    LOW,
    VOLUME,
    YEAR,
    DATEPACKED,
    FUT,
    RESERVED,
    MICRO_SEC,
    AUX_1,
    AUX_2,
    TERMINATOR,
    MILLI_SEC,
    SECOND,
    MINUTE,
    HOUR,
)
from .ami_construct import SymbolConstruct, Master

SYMBOL_REST = b"\0" * (1172 - 5)


@dataclass_validate()
@dataclass()
class SymbolEntry:
    month: int = 0
    year: int = 0
    close: float = 0.0
    open: float = 0.0
    low: float = 0.0
    high: float = 0.0
    volume: float = 0.0
    future: int = 0
    reserved: int = 0
    micro_second: int = 0
    milli_sec: int = 0
    second: int = 0
    minute: int = 0
    hour: int = 0
    day: int = 0
    aux_1: int = 0
    aux_2: int = 0
    terminator: int = 0

    # 256

    def set_by_construct(self, con_data):
        date_data = con_data[DATEPACKED]
        self.future = date_data[FUT]
        self.reserved = date_data[RESERVED]
        self.micro_second = date_data[MICRO_SEC]
        self.milli_sec = date_data[MILLI_SEC]
        self.second = date_data[SECOND]
        self.minute = date_data[MINUTE]
        self.hour = date_data[HOUR]
        self.day = date_data[DAY]
        self.month = date_data[MONTH]
        self.year = date_data[YEAR]

        self.close = con_data[CLOSE]
        self.open = con_data[OPEN]
        self.high = con_data[HIGH]
        self.low = con_data[LOW]
        self.volume = con_data[VOLUME]
        self.aux_1 = con_data[AUX_1]
        self.aux_2 = con_data[AUX_2]
        self.terminator = con_data[TERMINATOR]
        return self

    def to_construct_dict(self):
        return {
            DATEPACKED: {
                FUT: self.future,
                RESERVED: self.reserved,
                MICRO_SEC: self.micro_second,
                MILLI_SEC: self.milli_sec,
                SECOND: self.second,
                MINUTE: self.minute,
                HOUR: self.hour,
                DAY: self.day,
                MONTH: self.month,
                YEAR: self.year,
            },
            CLOSE: self.close,
            OPEN: self.open,
            HIGH: self.high,
            LOW: self.low,
            VOLUME: self.volume,  # 160
            AUX_1: self.aux_1,
            AUX_2: self.aux_2,
            TERMINATOR: self.terminator,
        }

        pass


@dataclass_validate()
@dataclass()
class SymbolData:
    Header: bytes = b"\0" * 0x4A0
    Entries: List[SymbolEntry] = field(default_factory=list)

    def append(self, entry: SymbolEntry):
        self.Entries.append(entry)

    def set_by_construct(self, con_data):
        self.Header = con_data["Header"]
        self.Entries = [
            SymbolEntry().set_by_construct(el) for el in con_data["Entries"]
        ]
        return self

    def to_dict(self):
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
        for el in self.Entries:
            result[DAY].append(el.day)
            result[MONTH].append(el.month)
            result[YEAR].append(el.year)

            result[OPEN].append(el.open)
            result[HIGH].append(el.high)
            result[LOW].append(el.low)
            result[CLOSE].append(el.close)
            result[VOLUME].append(el.volume)
        return result

    def to_construct_dict(self):
        result = {
            "Header": self.Header,
            "Entries": [el.to_construct_dict() for el in self.Entries],
        }
        return result

    def to_dataframe(self):
        return pd.DataFrame(self.to_dict())

    def write_to_file(self, file):
        binary = SymbolConstruct.build(self.to_construct_dict())
        file.write(binary)


@dataclass_validate()
@dataclass()
class MasterEntry:
    Symbol: str = ""
    Rest: bytes = SYMBOL_REST

    def to_construct_dict(self):
        result = {"Symbol": self.Symbol, "Rest": self.Rest}
        return result

    def set_by_construct(self, con_data):
        if type(con_data["Symbol"]) != str:
            return self

        self.Symbol = con_data["Symbol"]
        self.Rest = con_data["Rest"]
        return self


@dataclass_validate()
@dataclass()
class MasterData:
    Header: bytes = b"\0" * 0x4A0
    Symbols: List[MasterEntry] = field(default_factory=list)

    def write_to_file(self, file):
        Master.build()

    def append_symbol(self, symbol: str, rest: bytes = SYMBOL_REST):
        self.Symbols.append(MasterEntry(Symbol=symbol, Rest=rest))

    def get_symbols(self):
        return [el.Symbol for el in self.Symbols]

    def to_construct_dict(self):
        result = {
            "Header": self.Header,
            "Symbols": [el.to_construct_dict() for el in self.Symbols],
        }
        return result

    def set_by_construct(self, con_data):
        self.Header = con_data["Header"]
        self.Symbols = [
            MasterEntry().set_by_construct(el) for el in con_data["Symbols"]
        ]
        return self
