from construct import BitsInteger
from construct import (
    IntegerError,
    stream_read,
    swapbytes,
    bits2integer,
    integertypes,
    integer2bits,
    stream_write,
    bits2bytes,
    bytes2bits,
    int2byte,
    iterateints,
    FormatField,
    FormatFieldError,
    swapbitsinbytes,
)


def swapNibbles(x):
    return (x & 0x0F) << 4 | (x & 0xF0) >> 4


SWAPBITSINBYTES_CACHE = {
    i: bits2bytes(bytes2bits(int2byte(swapNibbles(i)))) for i in range(256)
}


def swapnibbleinbytes(data):
    r"""
    Performs a bit-reversal within a byte-string.

    Example:

        >>> swapbits(b'\xf0')
        b'\x0f'
    """
    return b"".join(SWAPBITSINBYTES_CACHE[b] for b in iterateints(data))


class RevBitsInteger(BitsInteger):
    def _parse(self, stream, context, path):
        length = self.length
        if callable(length):
            length = length(context)
        if length < 0:
            raise IntegerError("length must be non-negative")
        data = stream_read(stream, length, "WhateverPath")
        if self.swapped:
            if length & 7:
                raise IntegerError(
                    "little-endianness is only defined for multiples of 8 bits"
                )
            data = swapbytes(data)
        data = data[::-1]
        return bits2integer(data, self.signed)

    def _build(self, obj, stream, context, path):
        if not isinstance(obj, integertypes):
            raise IntegerError("value %r is not an integer" % (obj,))
        if obj < 0 and not self.signed:
            raise IntegerError("value %r is negative, but field is not signed" % (obj,))
        length = self.length
        if callable(length):
            length = length(context)
        if length < 0:
            raise IntegerError("length must be non-negative")
        data = integer2bits(obj, length)
        if self.swapped:
            if length & 7:
                raise IntegerError(
                    "little-endianness is only defined for multiples of 8 bits"
                )
            data = swapbytes(data)
        data = data[::-1]
        stream_write(stream, data, length)
        return obj


# def RevFloat32b(Float32b):
class RevFormatField(FormatField):
    def __init__(self, endianity, format):
        super().__init__(endianity, format)

    def _parse(self, stream, context, path):
        data = stream_read(stream, self.length, "WhateverPath")
        data = swapbitsinbytes(data)

        try:
            return self.packer.unpack(data)[0]
        except Exception:
            raise FormatFieldError("struct %r error during parsing" % self.fmtstr)

    def _build(self, obj, stream, context, path):
        try:
            data = self.packer.pack(obj)
        except Exception:
            raise FormatFieldError(
                "struct %r error during building, given value %r" % (self.fmtstr, obj)
            )
        data = swapbitsinbytes(data)
        stream_write(stream, data, self.length)
        return obj
