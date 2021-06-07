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
    values = int.from_bytes(swapbitsinbytes(bytes(reversed(date_tuple))), "little")
    return {
        # Reversed
        # YEAR: values >>52,# This does not work ??
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
    pass


class AmiSymbolDataFacade:
    def __init__(self, binary=None):
        self.binary=binary
        self._empty = False
        self.stride = OVERALL_ENTRY_BYTES
        self.default_header=b'BROKDAt5SPCE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00X\x02\x00\x00'
        self.default_header=bytearray(self.default_header)
        if (not binary):
            self._empty = True
            self.binary=self.default_header+bytearray(
                TERMINATOR_DOUBLE_WORD_LENGTH
            )
            self.binentries = self.binary[NUM_HEADER_BYTES:]
            self.length = 0
            self.set_length_in_header()
            return

        enough_bytes = len(binary) >= (NUM_HEADER_BYTES + TERMINATOR_DOUBLE_WORD_LENGTH)
        if not enough_bytes:
            self._empty = True
            self.length = 0
            self.set_length_in_header()
            self.binary=self.default_header+bytearray(
                                  TERMINATOR_DOUBLE_WORD_LENGTH
                                  )
            self.binentries = self.binary[NUM_HEADER_BYTES:]
            return
        self.binary=bytearray(self.binary)
        self.binentries = bytearray(binary[NUM_HEADER_BYTES:])
        self.length = (
            len(self.binentries) - TERMINATOR_DOUBLE_WORD_LENGTH
        ) // OVERALL_ENTRY_BYTES
        self.set_length_in_header()

    def set_length_in_header(self):
        self.default_header[-4] = self.length & 0x00ff
        self.default_header[-3] = (self.length & 0xff00) >> 8
        self.default_header[-2] = (self.length & 0xff0000) >> 16
        self.default_header[-1] = (self.length & 0xff000000) >> 24

    def _create_blank_header(self):
        pass

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
        pass

    def __iadd__(self, other):
        # assert all (k in entry_map for k in other)
        minute, hour, second, micro_second, milli_second = 0, 0, 0, 0, 0
        if MINUTE in other:
            minute = other[MINUTE]
        if HOUR in other:
            hour = other[HOUR]
        if SECOND in other:
            second = other[SECOND]
        if MICRO_SEC in other:
            micro_second = other[MICRO_SEC]
        if MILLI_SEC in other:
            milli_second = other[MILLI_SEC]

        append_bin = date_to_bin(
            other[DAY],
            other[MONTH],
            other[YEAR],
            hour,
            minute,
            second,
            micro_second,
            milli_second,
        )
        append_bin += float_to_bin(other[CLOSE])
        append_bin += float_to_bin(other[OPEN])
        append_bin += float_to_bin(other[HIGH])
        append_bin += float_to_bin(other[LOW])
        if VOLUME in other:
            append_bin += float_to_bin(other[VOLUME])
        else:
            append_bin += float_to_bin(0)
        if AUX_1 in other:
            append_bin += float_to_bin(other[AUX_1])
        else:
            append_bin += float_to_bin(0)
        if AUX_2 in other:
            append_bin += float_to_bin(other[AUX_2])
        else:
            append_bin += float_to_bin(0)
        if TERMINATOR in other:
            append_bin += float_to_bin(other[TERMINATOR])
        else:
            append_bin += float_to_bin(0)
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
