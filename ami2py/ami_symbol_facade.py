from construct import (
    Struct,
    Bytes,
    GreedyRange,
    PaddedString,
    swapbitsinbytes,
    BitsSwapped,
    bytes2bits,
    bits2bytes,
)
from .consts import (
    DATEPACKED,
    DAY,
    MONTH,
    YEAR,
    VOLUME,
    CLOSE,
    OPEN,
    HIGH,
    LOW,
    FUT,
    RESERVED,
    MICRO_SEC,
    MILLI_SEC,
    SECOND,
    MINUTE,
    HOUR,
    AUX_1,
    AUX_2,
    TERMINATOR,
)
from .ami_bitstructs import EntryChunk
import struct



Master = Struct(
    "Header" / Bytes(0x4A0),
    "Symbols"
    / GreedyRange(
        Struct("Symbol" / PaddedString(5, "ASCII"), "Rest" / Bytes(1172 - 5))
    ),
)


SymbolConstruct = Struct(
    "Header" / Bytes(0x4A0), "Entries" / GreedyRange(BitsSwapped(EntryChunk))
)


class AmiSymbolFacade:
    def __init__(self, binary):
        self.data = binary
        pass

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def pop(self, *args):
        return self.__dict__.pop(*args)

    def __cmp__(self, dict_):
        return self.__cmp__(self.__dict__, dict_)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    # def __unicode__(self):
    #     return unicode(repr(self.__dict__))


class AmiHeaderFacade:
    def __init__(self):
        pass


def reverse_bits(byte_data):
    return int("{:08b}".format(byte_data)[::-1], 2)


def read_date(date_tuple):
    values = int.from_bytes(swapbitsinbytes(bytes(date_tuple)), "little")
    return {
        # Reversed
        YEAR: (date_tuple[7] << 4) + ((date_tuple[6] & 0xF0) >> 4),
        MONTH: date_tuple[6] & 0x0F,
        DAY: (date_tuple[5] & 0xF8) >> 3,
        # Unreversed !!!
        HOUR: (reverse_bits(date_tuple[5]) & 0x7)
        + ((reverse_bits(date_tuple[4]) & 0xC0) >> 6),
        MINUTE: (reverse_bits(date_tuple[4]) & 0x3F),
        SECOND: (reverse_bits(date_tuple[3]) & 0xFC) >> 2,
        MILLI_SEC: (reverse_bits(date_tuple[3]) & 0x3)
        + (reverse_bits(date_tuple[2]) & 0xFF),
        MICRO_SEC: (reverse_bits(date_tuple[1]) & 0xFF)
        + ((reverse_bits(date_tuple[0]) & 0xC0) >> 6),
        RESERVED: ((reverse_bits(date_tuple[0]) & 0x1E) >> 1),
        FUT: (reverse_bits(date_tuple[0]) & 0x1),
    }


def read_date_data(entrybin):
    stride = 40
    start = 0
    datapackbytes = zip(
        entrybin[start::stride],
        entrybin[start + 1 :: stride],
        entrybin[start + 2 :: stride],
        entrybin[start + 3 :: stride],
        entrybin[start + 4 :: stride],
        entrybin[start + 5 :: stride],
        entrybin[start + 6 :: stride],
        entrybin[start + 7 :: stride],
    )
    result = [el for el in map(read_date, datapackbytes)]
    return result


def create_float(float_tuple):
    return struct.unpack("<f", bytes(float_tuple))[0]


class AmiSymbolDataFacade:
    def __init__(self, binary):
        self.binentries = binary[0x4A0:]
        self.length = (len(self.binentries) - 4) // 40
        self.stride = 40

    def __len__(self):
        return self.length

    def __getitem__(self, item):
        if type(item) == int:
            return self._get_item_by_index(item)
        if type(item) == slice:
            result = []
            if item.start >= 0:
                if item.step:
                    for i in range(item.start, item.stop, item.step):
                        result.append(self._get_item_by_index(i))
                else:
                    for i in range(item.start, item.stop):
                        result.append(self._get_item_by_index(i))
            else:
                start = self.length + item.start
                if item.step:
                    for i in range(start, item.stop, item.step):
                        result.append(self._get_item_by_index(i))
                else:
                    for i in range(start, item.stop, -1):
                        result.append(self._get_item_by_index(i))

            return result

    def _get_item_by_index(self, item):
        index = item
        if item < 0:
            index = self.length + item
        start = index * self.stride
        date_tuple = self.binentries[start : (start + 8)]
        return {
            **read_date(date_tuple),
            CLOSE: create_float(self.binentries[(start + 8) : (start + 12)]),
            OPEN: create_float(self.binentries[(start + 12) : (start + 16)]),
            HIGH: create_float(self.binentries[(start + 16) : (start + 20)]),
            LOW: create_float(self.binentries[(start + 20) : (start + 24)]),
            VOLUME: create_float(self.binentries[(start + 24) : (start + 28)]),
            AUX_1: create_float(self.binentries[(start + 28) : (start + 32)]),
            AUX_2: create_float(self.binentries[(start + 32) : (start + 36)]),
            TERMINATOR: create_float(self.binentries[(start + 36) : (start + 40)]),
        }

    def __iter__(self):
        pass


class SymbolConstructFast:
    header = "Header" / Bytes(0x4A0)
    entry_chunk = BitsSwapped(EntryChunk)

    @classmethod
    def parse(self, bin):
        binentries = bin[0x4A0:]
        num_bytes = len(binentries)
        numits, offset = divmod(num_bytes, 0x488)  # bytes
        result = {}
        result["Header"] = self.header.parse(bin[0:0x4A0])
        result["Entries"] = []
        start = 0x4A0 - offset
        numits = numits + 1
        result["Entries"].append(self.entry_chunk.parse(bin[0x4A0:]))
        entrybin = bin[start:]
        for i in range(numits):
            result["Entries"].append(
                [
                    self.entry_chunk.parse(entrybin[(i * 40) : (i * 40 + 40)]),
                    self.entry_chunk.parse(entrybin[(2 * i * 40) : (2 * i * 40 + 40)]),
                    self.entry_chunk.parse(entrybin[(3 * i * 40) : (3 * i * 40 + 40)]),
                    self.entry_chunk.parse(entrybin[(4 * i * 40) : (4 * i * 40 + 40)]),
                    self.entry_chunk.parse(entrybin[(5 * i * 40) : (5 * i * 40 + 40)]),
                    self.entry_chunk.parse(entrybin[(6 * i * 40) : (6 * i * 40 + 40)]),
                    self.entry_chunk.parse(entrybin[(7 * i * 40) : (7 * i * 40 + 40)]),
                    self.entry_chunk.parse(entrybin[(8 * i * 40) : (8 * i * 40 + 40)]),
                    self.entry_chunk.parse(entrybin[(9 * i * 40) : (9 * i * 40 + 40)]),
                    self.entry_chunk.parse(
                        entrybin[(10 * i * 40) : (10 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(11 * i * 40) : (11 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(12 * i * 40) : (12 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(13 * i * 40) : (13 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(14 * i * 40) : (14 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(15 * i * 40) : (15 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(16 * i * 40) : (16 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(17 * i * 40) : (17 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(18 * i * 40) : (18 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(19 * i * 40) : (19 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(20 * i * 40) : (20 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(21 * i * 40) : (21 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(22 * i * 40) : (22 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(23 * i * 40) : (23 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(24 * i * 40) : (24 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(25 * i * 40) : (25 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(26 * i * 40) : (26 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(27 * i * 40) : (27 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(28 * i * 40) : (28 * i * 40 + 40)]
                    ),
                    self.entry_chunk.parse(
                        entrybin[(29 * i * 40) : (29 * i * 40 + 40)]
                    ),
                ]
            )

        return result