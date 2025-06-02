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


def date_to_bin(
    day: int,
    month: int,
    year: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    mic_sec: int = 0,
    milli_sec: int = 0,
) -> bytearray:
    """Convert date and time to AmiBroker binary representation."""

    values = (
        (year << 52)
        | (month << 48)
        | (day << 43)
        | (hour << 38)
        | (minute << 32)
        | (second << 26)
        | (milli_sec << 16)
        | (mic_sec << 6)
        | 0
        | 0
    )

    byte_values = values.to_bytes(8, "little")
    return bytearray(byte_values)
