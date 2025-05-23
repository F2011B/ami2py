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
from .ami_construct import SymbolHeader
from .bitparser import read_date, reverse_bits
from .errors import InvalidAmiHeaderError
import struct

entry_map = [
    DAY,
    MONTH,
    YEAR,
    MICRO_SEC,
    MILLI_SEC,
    SECOND,
    MINUTE,
    HOUR,
    VOLUME,
    AUX_1,
    AUX_2,
    TERMINATOR,
    CLOSE,
    OPEN,
    HIGH,
    LOW,
    FUT,
]

NUM_HEADER_BYTES = 0x4A0

OVERALL_ENTRY_BYTES = 40

TERMINATOR_DOUBLE_WORD_LENGTH = 4

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
        ...

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


def float_to_bin(data):
    return bytearray(struct.pack("<f", data))


def date_to_bin(day, month, year, hour=0, minute=0, second=0, mic_sec=0, milli_sec=0):
    result = bytearray(8)
    result[7] = year >> 4
    result[6] = (result[6] & 0x0F) + (year << 4) & 0xF0
    result[6] = (result[6] & 0xF0) + month
    result[5] = (day << 3) + result[5] & 0xF8
    return result
    # Currently reading intraday data is very difficult
    # YEAR: (date_tuple[7] << 4) + ((date_tuple[6] & 0xF0) >> 4),
    # MONTH: date_tuple[6] & 0x0F,
    # DAY: (date_tuple[5] & 0xF8) >> 3,
    # # Unreversed !!!
    # HOUR: (reverse_bits(date_tuple[5]) & 0x7)
    # + ((reverse_bits(date_tuple[4]) & 0xC0) >> 6),
    # MINUTE: (reverse_bits(date_tuple[4]) & 0x3F),
    # SECOND: (reverse_bits(date_tuple[3]) & 0xFC) >> 2,
    # MILLI_SEC: (reverse_bits(date_tuple[3]) & 0x3)
    # + (reverse_bits(date_tuple[2]) & 0xFF),
    # MICRO_SEC: (reverse_bits(date_tuple[1]) & 0xFF)
    # + ((reverse_bits(date_tuple[0]) & 0xC0) >> 6),
    # RESERVED: ((reverse_bits(date_tuple[0]) & 0x1E) >> 1),
    # FUT: (reverse_bits(date_tuple[0]) & 0x1),
    ...


class AmiSymbolDataFacade:
    def __init__(self, binary=None):
        self.binary = binary
        self._empty = False
        self.stride = OVERALL_ENTRY_BYTES
        self.default_header = b"BROKDAt5SPCE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00X\x02\x00\x00"
        self.header = SymbolHeader.parse(self.default_header)
        self.default_header = bytearray(self.default_header)
        if not binary:
            self._empty = True
            self.binary = self.default_header + bytearray(TERMINATOR_DOUBLE_WORD_LENGTH)
            self.binentries = self.binary[NUM_HEADER_BYTES:]
            self.length = 0
            self.set_length_in_header()
            return

        enough_bytes = len(binary) >= (NUM_HEADER_BYTES + TERMINATOR_DOUBLE_WORD_LENGTH)
        if not enough_bytes:
            raise InvalidAmiHeaderError("Symbol file is too short")
        self.binary = bytearray(self.binary)
        self.header = SymbolHeader.parse(self.binary)
        self.default_header = SymbolHeader.build(self.header)
        self.binentries = bytearray(binary[NUM_HEADER_BYTES:])
        self.length = (
            len(self.binentries) - TERMINATOR_DOUBLE_WORD_LENGTH
        ) // OVERALL_ENTRY_BYTES
        self.set_length_in_header()

    def set_length_in_header(self):
        self.header["Length"] = self.length
        self.default_header = SymbolHeader.build(self.header)
        # self.default_header[-4] = self.length & 0x00ff
        # self.default_header[-3] = (self.length & 0xff00) >> 8
        # self.default_header[-2] = (self.length & 0xff0000) >> 16
        # self.default_header[-1] = (self.length & 0xff000000) >> 24

    def __len__(self):
        return self.length

    def __getitem__(self, item):
        if self._empty:
            return []
        if type(item) == int:
            return self._get_item_by_index(item)
        if type(item) == slice:
            result = []
        start = self._convert_to_index(item.start)
        stop = self._convert_to_index(item.stop)
        step = item.step
        if item.step == None:
            step = 1
        for i in range(start, stop, step):
            result.append(self._get_item_by_index(i))

        return result

    def _convert_to_index(self, index):
        if index >= 0:
            return index
        if index < 0:
            return self.length + index

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
        for i in range(self.length):
            yield self._get_item_by_index(i)

    def __iadd__(self, other):
        # assert all (k in entry_map for k in other)
        minute = other.get(MINUTE, 0)
        hour = other.get(HOUR, 0)
        second = other.get(SECOND, 0)
        micro_second = other.get(MICRO_SEC, 0)
        milli_second = other.get(MILLI_SEC, 0)
        reserved = other.get(RESERVED, 0)
        fut = other.get(FUT, 0)

        append_bin = bytearray(OVERALL_ENTRY_BYTES)

        date_value = (
            ((other[YEAR] & 0xFFF) << 52)
            | ((other[MONTH] & 0xF) << 48)
            | ((other[DAY] & 0x1F) << 43)
            | ((hour & 0x1F) << 38)
            | ((minute & 0x3F) << 32)
            | ((second & 0x3F) << 26)
            | ((milli_second & 0x3FF) << 16)
            | ((micro_second & 0x3FF) << 6)
            | ((reserved & 0x7) << 1)
            | (fut & 0x1)
        )
        struct.pack_into("<Q", append_bin, 0, date_value)

        struct.pack_into("<f", append_bin, 8, other[CLOSE])
        struct.pack_into("<f", append_bin, 12, other[OPEN])
        struct.pack_into("<f", append_bin, 16, other[HIGH])
        struct.pack_into("<f", append_bin, 20, other[LOW])
        struct.pack_into("<f", append_bin, 24, other.get(VOLUME, 0))
        struct.pack_into("<f", append_bin, 28, other.get(AUX_1, 0))
        struct.pack_into("<f", append_bin, 32, other.get(AUX_2, 0))
        struct.pack_into("<f", append_bin, 36, other.get(TERMINATOR, 0))
        self.binentries[
            -TERMINATOR_DOUBLE_WORD_LENGTH:-TERMINATOR_DOUBLE_WORD_LENGTH
        ] = append_bin
        self.length = (
            len(self.binentries) - TERMINATOR_DOUBLE_WORD_LENGTH
        ) // OVERALL_ENTRY_BYTES
        self.set_length_in_header()
        self.binary = self.default_header + self.binentries
        return self


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
            entries = []
            for offset_index in range(30):
                start_index = offset_index * i * 40
                entries.append(
                    self.entry_chunk.parse(entrybin[start_index : start_index + 40])
                )
            result["Entries"].append(entries)

        return result
