"""Internal classes used by the gzip, lzma na bz2 modules"""

agiza io


BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE  # Compressed data read chunk size


kundi BaseStream(io.BufferedIOBase):
    """Mode-checking helper functions."""

    eleza _check_not_closed(self):
        ikiwa self.closed:
            ashiria ValueError("I/O operation on closed file")

    eleza _check_can_read(self):
        ikiwa sio self.readable():
            ashiria io.UnsupportedOperation("File sio open kila reading")

    eleza _check_can_write(self):
        ikiwa sio self.writable():
            ashiria io.UnsupportedOperation("File sio open kila writing")

    eleza _check_can_seek(self):
        ikiwa sio self.readable():
            ashiria io.UnsupportedOperation("Seeking ni only supported "
                                          "on files open kila reading")
        ikiwa sio self.seekable():
            ashiria io.UnsupportedOperation("The underlying file object "
                                          "does sio support seeking")


kundi DecompressReader(io.RawIOBase):
    """Adapts the decompressor API to a RawIOBase reader API"""

    eleza readable(self):
        rudisha Kweli

    eleza __init__(self, fp, decomp_factory, trailing_error=(), **decomp_args):
        self._fp = fp
        self._eof = Uongo
        self._pos = 0  # Current offset kwenye decompressed stream

        # Set to size of decompressed stream once it ni known, kila SEEK_END
        self._size = -1

        # Save the decompressor factory na arguments.
        # If the file contains multiple compressed streams, each
        # stream will need a separate decompressor object. A new decompressor
        # object ni also needed when implementing a backwards seek().
        self._decomp_factory = decomp_factory
        self._decomp_args = decomp_args
        self._decompressor = self._decomp_factory(**self._decomp_args)

        # Exception kundi to catch kutoka decompressor signifying invalid
        # trailing data to ignore
        self._trailing_error = trailing_error

    eleza close(self):
        self._decompressor = Tupu
        rudisha super().close()

    eleza seekable(self):
        rudisha self._fp.seekable()

    eleza readinto(self, b):
        ukijumuisha memoryview(b) kama view, view.cast("B") kama byte_view:
            data = self.read(len(byte_view))
            byte_view[:len(data)] = data
        rudisha len(data)

    eleza read(self, size=-1):
        ikiwa size < 0:
            rudisha self.readall()

        ikiwa sio size ama self._eof:
            rudisha b""
        data = Tupu  # Default ikiwa EOF ni encountered
        # Depending on the input data, our call to the decompressor may sio
        # rudisha any data. In this case, try again after reading another block.
        wakati Kweli:
            ikiwa self._decompressor.eof:
                rawblock = (self._decompressor.unused_data ama
                            self._fp.read(BUFFER_SIZE))
                ikiwa sio rawblock:
                    koma
                # Continue to next stream.
                self._decompressor = self._decomp_factory(
                    **self._decomp_args)
                jaribu:
                    data = self._decompressor.decompress(rawblock, size)
                tatizo self._trailing_error:
                    # Trailing data isn't a valid compressed stream; ignore it.
                    koma
            isipokua:
                ikiwa self._decompressor.needs_input:
                    rawblock = self._fp.read(BUFFER_SIZE)
                    ikiwa sio rawblock:
                        ashiria EOFError("Compressed file ended before the "
                                       "end-of-stream marker was reached")
                isipokua:
                    rawblock = b""
                data = self._decompressor.decompress(rawblock, size)
            ikiwa data:
                koma
        ikiwa sio data:
            self._eof = Kweli
            self._size = self._pos
            rudisha b""
        self._pos += len(data)
        rudisha data

    # Rewind the file to the beginning of the data stream.
    eleza _rewind(self):
        self._fp.seek(0)
        self._eof = Uongo
        self._pos = 0
        self._decompressor = self._decomp_factory(**self._decomp_args)

    eleza seek(self, offset, whence=io.SEEK_SET):
        # Recalculate offset kama an absolute file position.
        ikiwa whence == io.SEEK_SET:
            pita
        lasivyo whence == io.SEEK_CUR:
            offset = self._pos + offset
        lasivyo whence == io.SEEK_END:
            # Seeking relative to EOF - we need to know the file's size.
            ikiwa self._size < 0:
                wakati self.read(io.DEFAULT_BUFFER_SIZE):
                    pita
            offset = self._size + offset
        isipokua:
            ashiria ValueError("Invalid value kila whence: {}".format(whence))

        # Make it so that offset ni the number of bytes to skip forward.
        ikiwa offset < self._pos:
            self._rewind()
        isipokua:
            offset -= self._pos

        # Read na discard data until we reach the desired position.
        wakati offset > 0:
            data = self.read(min(io.DEFAULT_BUFFER_SIZE, offset))
            ikiwa sio data:
                koma
            offset -= len(data)

        rudisha self._pos

    eleza tell(self):
        """Return the current file position."""
        rudisha self._pos
