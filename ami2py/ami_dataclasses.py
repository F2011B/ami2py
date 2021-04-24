from dataclasses import dataclass, field
from dataclass_type_validator import dataclass_validate
from typing import List
import pandas as pd
from .consts import DAY, MONTH, CLOSE, OPEN, HIGH, LOW, VOLUME, DATEPACKED, YEAR


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


@dataclass_validate()
@dataclass()
class SymbolData:
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

    def to_dataframe(self):
        return pd.DataFrame(self.to_dict())
