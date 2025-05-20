import struct
from .consts import (
    YEAR,
    MONTH,
    DAY,
    HOUR,
    MINUTE,
    SECOND,
    MILLI_SEC,
    MICRO_SEC,
    RESERVED,
    FUT,
)

def reverse_bits(byte_data: int) -> int:
    return int("{:08b}".format(byte_data)[::-1], 2)


def read_date(date_tuple):
    values = int.from_bytes(bytes(date_tuple), "little")
    return {
        YEAR: values >> 52,
        MONTH: (values >> 48) & 0x0F,
        DAY: (values >> 43) & 0x1F,
        HOUR: (values >> 38) & 0x1F,
        MINUTE: (values >> 32) & 0x3F,
        SECOND: (values >> 26) & 0x3F,
        MILLI_SEC: (values >> 16) & 0x3FF,
        MICRO_SEC: (values >> 6) & 0x3FF,
        RESERVED: values & 0xE,
        FUT: values & 0x1,
    }


def create_float(float_tuple):
    return struct.unpack("<f", bytes(float_tuple))[0]


def float_to_bin(data: float) -> bytearray:
    return bytearray(struct.pack("<f", data))


def date_to_bin(day, month, year, hour=0, minute=0, second=0, mic_sec=0, milli_sec=0):
    result = bytearray(8)
    result[7] = year >> 4
    result[6] = (result[6] & 0x0F) + (year << 4) & 0xF0
    result[6] = (result[6] & 0xF0) + month
    result[5] = (day << 3) + result[5] & 0xF8
    return result
