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


@dataclass_validate()
@dataclass()
class SymbolEntry:
    month: int
    year: int
    close: float
    open: float
    low: float
    high: float
    volume: float
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

    # 256

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
    Header: int = 0
    Series: List[SymbolEntry] = field(default_factory=list)

    def append(self, entry: SymbolEntry):
        self.Series.append(entry)

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
        for el in self.Series:
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
            "Entries": [el.to_construct_dict() for el in self.Series],
        }
        return result

    def to_dataframe(self):
        return pd.DataFrame(self.to_dict())

    def write_to_file(self, file):
        binary = SymbolConstruct.build(self.to_construct_dict())
        file.write(binary)


@dataclass_validate()
@dataclass()
class MasterData:
    Header: int = 0
    Symbols: List[str] = field(default_factory=list)

    def write_to_file(self, file):
        Master.build()
