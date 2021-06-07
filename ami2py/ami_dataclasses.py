from dataclasses import dataclass, field, fields
from dataclass_type_validator import dataclass_validate
from typing import List
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

SYMBOL_REST = b"\0" * (1172 - 5 - 16 - 490 + 3)
SYMBOL_SPACE = b"\0" * (495 - 5 - 3)
SYMBOL_STR = b"\0" * (497)


@dataclass()
class SymbolEntry:
    Month: int = 0
    Year: int = 0
    Close: float = 0.0
    Open: float = 0.0
    Low: float = 0.0
    High: float = 0.0
    Volume: float = 0.0
    Future: int = 0
    Reserved: int = 0
    Micro_second: int = 0
    Milli_sec: int = 0
    Second: int = 0
    Minute: int = 0
    Hour: int = 0
    Day: int = 0
    Aux_1: int = 0
    Aux_2: int = 0
    Terminator: int = 0

    # 256
    def __post_init__(self):
        current_fields = fields(self)
        for field in current_fields:
            field_name = field.name
            expected_type = field.type
            value = getattr(self, field_name)
            if expected_type == int:
                assert isinstance(value, int)

            if expected_type == float:
                if isinstance(value, int):
                    self.__setattr__(field_name, float(value))
                value = getattr(self, field_name)
                assert isinstance(value, float)

    @classmethod
    def get_necessary_args(self):
        return ["Month", "Year", "Day", "Close", "High", "Open", "Low", "Volume"]

    def set_by_construct(self, con_data):
        date_data = con_data[DATEPACKED]
        self.Future = date_data[FUT]
        self.Reserved = date_data[RESERVED]
        self.Micro_second = date_data[MICRO_SEC]
        self.Milli_sec = date_data[MILLI_SEC]
        self.Second = date_data[SECOND]
        self.Minute = date_data[MINUTE]
        self.Hour = date_data[HOUR]
        self.Day = date_data[DAY]
        self.Month = date_data[MONTH]
        self.Year = date_data[YEAR]

        self.Close = con_data[CLOSE]
        self.Open = con_data[OPEN]
        self.High = con_data[HIGH]
        self.Low = con_data[LOW]
        self.Volume = con_data[VOLUME]
        self.Aux_1 = con_data[AUX_1]
        self.Aux_2 = con_data[AUX_2]
        self.Terminator = con_data[TERMINATOR]
        return self

    def to_construct_dict(self):
        return {
            DATEPACKED: {
                FUT: self.Future,
                RESERVED: self.Reserved,
                MICRO_SEC: self.Micro_second,
                MILLI_SEC: self.Milli_sec,
                SECOND: self.Second,
                MINUTE: self.Minute,
                HOUR: self.Hour,
                DAY: self.Day,
                MONTH: self.Month,
                YEAR: self.Year,
            },
            CLOSE: self.Close,
            OPEN: self.Open,
            HIGH: self.High,
            LOW: self.Low,
            VOLUME: self.Volume,  # 160
            AUX_1: self.Aux_1,
            AUX_2: self.Aux_2,
            TERMINATOR: self.Terminator,
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
            result[DAY].append(el.Day)
            result[MONTH].append(el.Month)
            result[YEAR].append(el.Year)

            result[OPEN].append(el.Open)
            result[HIGH].append(el.High)
            result[LOW].append(el.Low)
            result[CLOSE].append(el.Close)
            result[VOLUME].append(el.Volume)
        return result

    def to_construct_dict(self):
        result = {
            "Header": self.Header,
            "Entries": [el.to_construct_dict() for el in self.Entries],
        }
        return result

    def write_to_file(self, file):
        binary = SymbolConstruct.build(self.to_construct_dict())
        file.write(binary)


@dataclass_validate()
@dataclass()
class MasterEntry:
    Symbol: str = ""
    # Space: bytes= SYMBOL_SPACE
    Rest: bytes = SYMBOL_REST

    def to_construct_dict(self):
        result = {"Symbol": self.Symbol, "Rest": self.Rest, "Const": None}
        return result

    def set_by_construct(self, con_data):
        if type(con_data["Symbol"]) != str:
            return self
        self.Symbol = con_data["Symbol"]
        self.Rest = con_data["Rest"]
        # self.Space = con_data["Space"]
        return self


@dataclass_validate()
@dataclass()
class MasterData:
    Header: bytes = b"BROKMAS2"
    NumSymbols: int = 0
    Symbols: List[MasterEntry] = field(default_factory=list)

    def write_to_file(self, file):
        Master.build()

    def append_symbol(self, symbol: str, rest: bytes = SYMBOL_REST):
        self.Symbols.append(MasterEntry(Symbol=symbol, Rest=rest))
        self.NumSymbols= len(self.Symbols)


    def get_symbols(self):
        return [el.Symbol for el in self.Symbols]

    def to_construct_dict(self):
        result = {
            "Header": self.Header,
            "NumSymbols": self.NumSymbols,
            "Symbols": [el.to_construct_dict() for el in self.Symbols],
        }
        return result

    def set_by_construct(self, con_data):
        self.Header = con_data["Header"]
        self.NumSymbols = con_data["NumSymbols"]
        self.Symbols = [
            MasterEntry().set_by_construct(el) for el in con_data["Symbols"]
        ]
        return self
