from construct import BitsInteger
from construct import (
    IntegerError,
    stream_read,
    swapbytes,
    bits2integer,
    integertypes,
    integer2bits,
    stream_write,
)


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
        stream_write(stream, data, length, path)
        return obj
