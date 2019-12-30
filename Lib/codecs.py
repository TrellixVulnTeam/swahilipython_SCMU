""" codecs -- Python Codec Registry, API na helpers.


Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""

agiza builtins
agiza sys

### Registry na builtin stateless codec functions

jaribu:
    kutoka _codecs agiza *
tatizo ImportError kama why:
    ashiria SystemError('Failed to load the builtin codecs: %s' % why)

__all__ = ["register", "lookup", "open", "EncodedFile", "BOM", "BOM_BE",
           "BOM_LE", "BOM32_BE", "BOM32_LE", "BOM64_BE", "BOM64_LE",
           "BOM_UTF8", "BOM_UTF16", "BOM_UTF16_LE", "BOM_UTF16_BE",
           "BOM_UTF32", "BOM_UTF32_LE", "BOM_UTF32_BE",
           "CodecInfo", "Codec", "IncrementalEncoder", "IncrementalDecoder",
           "StreamReader", "StreamWriter",
           "StreamReaderWriter", "StreamRecoder",
           "getencoder", "getdecoder", "getincrementalencoder",
           "getincrementaldecoder", "getreader", "getwriter",
           "encode", "decode", "iterencode", "iterdecode",
           "strict_errors", "ignore_errors", "replace_errors",
           "xmlcharrefreplace_errors",
           "backslashreplace_errors", "namereplace_errors",
           "register_error", "lookup_error"]

### Constants

#
# Byte Order Mark (BOM = ZERO WIDTH NO-BREAK SPACE = U+FEFF)
# na its possible byte string values
# kila UTF8/UTF16/UTF32 output na little/big endian machines
#

# UTF-8
BOM_UTF8 = b'\xef\xbb\xbf'

# UTF-16, little endian
BOM_LE = BOM_UTF16_LE = b'\xff\xfe'

# UTF-16, big endian
BOM_BE = BOM_UTF16_BE = b'\xfe\xff'

# UTF-32, little endian
BOM_UTF32_LE = b'\xff\xfe\x00\x00'

# UTF-32, big endian
BOM_UTF32_BE = b'\x00\x00\xfe\xff'

ikiwa sys.byteorder == 'little':

    # UTF-16, native endianness
    BOM = BOM_UTF16 = BOM_UTF16_LE

    # UTF-32, native endianness
    BOM_UTF32 = BOM_UTF32_LE

isipokua:

    # UTF-16, native endianness
    BOM = BOM_UTF16 = BOM_UTF16_BE

    # UTF-32, native endianness
    BOM_UTF32 = BOM_UTF32_BE

# Old broken names (don't use kwenye new code)
BOM32_LE = BOM_UTF16_LE
BOM32_BE = BOM_UTF16_BE
BOM64_LE = BOM_UTF32_LE
BOM64_BE = BOM_UTF32_BE


### Codec base classes (defining the API)

kundi CodecInfo(tuple):
    """Codec details when looking up the codec registry"""

    # Private API to allow Python 3.4 to blacklist the known non-Unicode
    # codecs kwenye the standard library. A more general mechanism to
    # reliably distinguish test encodings kutoka other codecs will hopefully
    # be defined kila Python 3.5
    #
    # See http://bugs.python.org/issue19619
    _is_text_encoding = Kweli # Assume codecs are text encodings by default

    eleza __new__(cls, encode, decode, streamreader=Tupu, streamwriter=Tupu,
        incrementalencoder=Tupu, incrementaldecoder=Tupu, name=Tupu,
        *, _is_text_encoding=Tupu):
        self = tuple.__new__(cls, (encode, decode, streamreader, streamwriter))
        self.name = name
        self.encode = encode
        self.decode = decode
        self.incrementalencoder = incrementalencoder
        self.incrementaldecoder = incrementaldecoder
        self.streamwriter = streamwriter
        self.streamreader = streamreader
        ikiwa _is_text_encoding ni sio Tupu:
            self._is_text_encoding = _is_text_encoding
        rudisha self

    eleza __repr__(self):
        rudisha "<%s.%s object kila encoding %s at %#x>" % \
                (self.__class__.__module__, self.__class__.__qualname__,
                 self.name, id(self))

kundi Codec:

    """ Defines the interface kila stateless encoders/decoders.

        The .encode()/.decode() methods may use different error
        handling schemes by providing the errors argument. These
        string values are predefined:

         'strict' - ashiria a ValueError error (or a subclass)
         'ignore' - ignore the character na endelea ukijumuisha the next
         'replace' - replace ukijumuisha a suitable replacement character;
                    Python will use the official U+FFFD REPLACEMENT
                    CHARACTER kila the builtin Unicode codecs on
                    decoding na '?' on encoding.
         'surrogateescape' - replace ukijumuisha private code points U+DCnn.
         'xmlcharrefreplace' - Replace ukijumuisha the appropriate XML
                               character reference (only kila encoding).
         'backslashreplace'  - Replace ukijumuisha backslashed escape sequences.
         'namereplace'       - Replace ukijumuisha \\N{...} escape sequences
                               (only kila encoding).

        The set of allowed values can be extended via register_error.

    """
    eleza encode(self, input, errors='strict'):

        """ Encodes the object input na rudishas a tuple (output
            object, length consumed).

            errors defines the error handling to apply. It defaults to
            'strict' handling.

            The method may sio store state kwenye the Codec instance. Use
            StreamWriter kila codecs which have to keep state kwenye order to
            make encoding efficient.

            The encoder must be able to handle zero length input na
            rudisha an empty object of the output object type kwenye this
            situation.

        """
        ashiria NotImplementedError

    eleza decode(self, input, errors='strict'):

        """ Decodes the object input na rudishas a tuple (output
            object, length consumed).

            input must be an object which provides the bf_getreadbuf
            buffer slot. Python strings, buffer objects na memory
            mapped files are examples of objects providing this slot.

            errors defines the error handling to apply. It defaults to
            'strict' handling.

            The method may sio store state kwenye the Codec instance. Use
            StreamReader kila codecs which have to keep state kwenye order to
            make decoding efficient.

            The decoder must be able to handle zero length input na
            rudisha an empty object of the output object type kwenye this
            situation.

        """
        ashiria NotImplementedError

kundi IncrementalEncoder(object):
    """
    An IncrementalEncoder encodes an input kwenye multiple steps. The input can
    be pitaed piece by piece to the encode() method. The IncrementalEncoder
    remembers the state of the encoding process between calls to encode().
    """
    eleza __init__(self, errors='strict'):
        """
        Creates an IncrementalEncoder instance.

        The IncrementalEncoder may use different error handling schemes by
        providing the errors keyword argument. See the module docstring
        kila a list of possible values.
        """
        self.errors = errors
        self.buffer = ""

    eleza encode(self, input, final=Uongo):
        """
        Encodes input na rudishas the resulting object.
        """
        ashiria NotImplementedError

    eleza reset(self):
        """
        Resets the encoder to the initial state.
        """

    eleza getstate(self):
        """
        Return the current state of the encoder.
        """
        rudisha 0

    eleza setstate(self, state):
        """
        Set the current state of the encoder. state must have been
        rudishaed by getstate().
        """

kundi BufferedIncrementalEncoder(IncrementalEncoder):
    """
    This subkundi of IncrementalEncoder can be used kama the basekundi kila an
    incremental encoder ikiwa the encoder must keep some of the output kwenye a
    buffer between calls to encode().
    """
    eleza __init__(self, errors='strict'):
        IncrementalEncoder.__init__(self, errors)
        # unencoded input that ni kept between calls to encode()
        self.buffer = ""

    eleza _buffer_encode(self, input, errors, final):
        # Overwrite this method kwenye subclasses: It must encode input
        # na rudisha an (output, length consumed) tuple
        ashiria NotImplementedError

    eleza encode(self, input, final=Uongo):
        # encode input (taking the buffer into account)
        data = self.buffer + input
        (result, consumed) = self._buffer_encode(data, self.errors, final)
        # keep unencoded input until the next call
        self.buffer = data[consumed:]
        rudisha result

    eleza reset(self):
        IncrementalEncoder.reset(self)
        self.buffer = ""

    eleza getstate(self):
        rudisha self.buffer ama 0

    eleza setstate(self, state):
        self.buffer = state ama ""

kundi IncrementalDecoder(object):
    """
    An IncrementalDecoder decodes an input kwenye multiple steps. The input can
    be pitaed piece by piece to the decode() method. The IncrementalDecoder
    remembers the state of the decoding process between calls to decode().
    """
    eleza __init__(self, errors='strict'):
        """
        Create an IncrementalDecoder instance.

        The IncrementalDecoder may use different error handling schemes by
        providing the errors keyword argument. See the module docstring
        kila a list of possible values.
        """
        self.errors = errors

    eleza decode(self, input, final=Uongo):
        """
        Decode input na rudishas the resulting object.
        """
        ashiria NotImplementedError

    eleza reset(self):
        """
        Reset the decoder to the initial state.
        """

    eleza getstate(self):
        """
        Return the current state of the decoder.

        This must be a (buffered_input, additional_state_info) tuple.
        buffered_input must be a bytes object containing bytes that
        were pitaed to decode() that have sio yet been converted.
        additional_state_info must be a non-negative integer
        representing the state of the decoder WITHOUT yet having
        processed the contents of buffered_input.  In the initial state
        na after reset(), getstate() must rudisha (b"", 0).
        """
        rudisha (b"", 0)

    eleza setstate(self, state):
        """
        Set the current state of the decoder.

        state must have been rudishaed by getstate().  The effect of
        setstate((b"", 0)) must be equivalent to reset().
        """

kundi BufferedIncrementalDecoder(IncrementalDecoder):
    """
    This subkundi of IncrementalDecoder can be used kama the basekundi kila an
    incremental decoder ikiwa the decoder must be able to handle incomplete
    byte sequences.
    """
    eleza __init__(self, errors='strict'):
        IncrementalDecoder.__init__(self, errors)
        # undecoded input that ni kept between calls to decode()
        self.buffer = b""

    eleza _buffer_decode(self, input, errors, final):
        # Overwrite this method kwenye subclasses: It must decode input
        # na rudisha an (output, length consumed) tuple
        ashiria NotImplementedError

    eleza decode(self, input, final=Uongo):
        # decode input (taking the buffer into account)
        data = self.buffer + input
        (result, consumed) = self._buffer_decode(data, self.errors, final)
        # keep undecoded input until the next call
        self.buffer = data[consumed:]
        rudisha result

    eleza reset(self):
        IncrementalDecoder.reset(self)
        self.buffer = b""

    eleza getstate(self):
        # additional state info ni always 0
        rudisha (self.buffer, 0)

    eleza setstate(self, state):
        # ignore additional state info
        self.buffer = state[0]

#
# The StreamWriter na StreamReader kundi provide generic working
# interfaces which can be used to implement new encoding submodules
# very easily. See encodings/utf_8.py kila an example on how this is
# done.
#

kundi StreamWriter(Codec):

    eleza __init__(self, stream, errors='strict'):

        """ Creates a StreamWriter instance.

            stream must be a file-like object open kila writing.

            The StreamWriter may use different error handling
            schemes by providing the errors keyword argument. These
            parameters are predefined:

             'strict' - ashiria a ValueError (or a subclass)
             'ignore' - ignore the character na endelea ukijumuisha the next
             'replace'- replace ukijumuisha a suitable replacement character
             'xmlcharrefreplace' - Replace ukijumuisha the appropriate XML
                                   character reference.
             'backslashreplace'  - Replace ukijumuisha backslashed escape
                                   sequences.
             'namereplace'       - Replace ukijumuisha \\N{...} escape sequences.

            The set of allowed parameter values can be extended via
            register_error.
        """
        self.stream = stream
        self.errors = errors

    eleza write(self, object):

        """ Writes the object's contents encoded to self.stream.
        """
        data, consumed = self.encode(object, self.errors)
        self.stream.write(data)

    eleza writelines(self, list):

        """ Writes the concatenated list of strings to the stream
            using .write().
        """
        self.write(''.join(list))

    eleza reset(self):

        """ Flushes na resets the codec buffers used kila keeping state.

            Calling this method should ensure that the data on the
            output ni put into a clean state, that allows appending
            of new fresh data without having to rescan the whole
            stream to recover state.

        """
        pita

    eleza seek(self, offset, whence=0):
        self.stream.seek(offset, whence)
        ikiwa whence == 0 na offset == 0:
            self.reset()

    eleza __getattr__(self, name,
                    getattr=getattr):

        """ Inherit all other methods kutoka the underlying stream.
        """
        rudisha getattr(self.stream, name)

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, type, value, tb):
        self.stream.close()

###

kundi StreamReader(Codec):

    charbuffertype = str

    eleza __init__(self, stream, errors='strict'):

        """ Creates a StreamReader instance.

            stream must be a file-like object open kila reading.

            The StreamReader may use different error handling
            schemes by providing the errors keyword argument. These
            parameters are predefined:

             'strict' - ashiria a ValueError (or a subclass)
             'ignore' - ignore the character na endelea ukijumuisha the next
             'replace'- replace ukijumuisha a suitable replacement character
             'backslashreplace' - Replace ukijumuisha backslashed escape sequences;

            The set of allowed parameter values can be extended via
            register_error.
        """
        self.stream = stream
        self.errors = errors
        self.bytebuffer = b""
        self._empty_charbuffer = self.charbuffertype()
        self.charbuffer = self._empty_charbuffer
        self.linebuffer = Tupu

    eleza decode(self, input, errors='strict'):
        ashiria NotImplementedError

    eleza read(self, size=-1, chars=-1, firstline=Uongo):

        """ Decodes data kutoka the stream self.stream na rudishas the
            resulting object.

            chars indicates the number of decoded code points ama bytes to
            rudisha. read() will never rudisha more data than requested,
            but it might rudisha less, ikiwa there ni sio enough available.

            size indicates the approximate maximum number of decoded
            bytes ama code points to read kila decoding. The decoder
            can modify this setting kama appropriate. The default value
            -1 indicates to read na decode kama much kama possible.  size
            ni intended to prevent having to decode huge files kwenye one
            step.

            If firstline ni true, na a UnicodeDecodeError happens
            after the first line terminator kwenye the input only the first line
            will be rudishaed, the rest of the input will be kept until the
            next call to read().

            The method should use a greedy read strategy, meaning that
            it should read kama much data kama ni allowed within the
            definition of the encoding na the given size, e.g.  if
            optional encoding endings ama state markers are available
            on the stream, these should be read too.
        """
        # If we have lines cached, first merge them back into characters
        ikiwa self.linebuffer:
            self.charbuffer = self._empty_charbuffer.join(self.linebuffer)
            self.linebuffer = Tupu

        ikiwa chars < 0:
            # For compatibility ukijumuisha other read() methods that take a
            # single argument
            chars = size

        # read until we get the required number of characters (ikiwa available)
        wakati Kweli:
            # can the request be satisfied kutoka the character buffer?
            ikiwa chars >= 0:
                ikiwa len(self.charbuffer) >= chars:
                    koma
            # we need more data
            ikiwa size < 0:
                newdata = self.stream.read()
            isipokua:
                newdata = self.stream.read(size)
            # decode bytes (those remaining kutoka the last call included)
            data = self.bytebuffer + newdata
            ikiwa sio data:
                koma
            jaribu:
                newchars, decodedbytes = self.decode(data, self.errors)
            tatizo UnicodeDecodeError kama exc:
                ikiwa firstline:
                    newchars, decodedbytes = \
                        self.decode(data[:exc.start], self.errors)
                    lines = newchars.splitlines(keepends=Kweli)
                    ikiwa len(lines)<=1:
                        ashiria
                isipokua:
                    ashiria
            # keep undecoded bytes until the next call
            self.bytebuffer = data[decodedbytes:]
            # put new characters kwenye the character buffer
            self.charbuffer += newchars
            # there was no data available
            ikiwa sio newdata:
                koma
        ikiwa chars < 0:
            # Return everything we've got
            result = self.charbuffer
            self.charbuffer = self._empty_charbuffer
        isipokua:
            # Return the first chars characters
            result = self.charbuffer[:chars]
            self.charbuffer = self.charbuffer[chars:]
        rudisha result

    eleza readline(self, size=Tupu, keepends=Kweli):

        """ Read one line kutoka the input stream na rudisha the
            decoded data.

            size, ikiwa given, ni pitaed kama size argument to the
            read() method.

        """
        # If we have lines cached kutoka an earlier read, rudisha
        # them unconditionally
        ikiwa self.linebuffer:
            line = self.linebuffer[0]
            toa self.linebuffer[0]
            ikiwa len(self.linebuffer) == 1:
                # revert to charbuffer mode; we might need more data
                # next time
                self.charbuffer = self.linebuffer[0]
                self.linebuffer = Tupu
            ikiwa sio keepends:
                line = line.splitlines(keepends=Uongo)[0]
            rudisha line

        readsize = size ama 72
        line = self._empty_charbuffer
        # If size ni given, we call read() only once
        wakati Kweli:
            data = self.read(readsize, firstline=Kweli)
            ikiwa data:
                # If we're at a "\r" read one extra character (which might
                # be a "\n") to get a proper line ending. If the stream is
                # temporarily exhausted we rudisha the wrong line ending.
                ikiwa (isinstance(data, str) na data.endswith("\r")) ama \
                   (isinstance(data, bytes) na data.endswith(b"\r")):
                    data += self.read(size=1, chars=1)

            line += data
            lines = line.splitlines(keepends=Kweli)
            ikiwa lines:
                ikiwa len(lines) > 1:
                    # More than one line result; the first line ni a full line
                    # to rudisha
                    line = lines[0]
                    toa lines[0]
                    ikiwa len(lines) > 1:
                        # cache the remaining lines
                        lines[-1] += self.charbuffer
                        self.linebuffer = lines
                        self.charbuffer = Tupu
                    isipokua:
                        # only one remaining line, put it back into charbuffer
                        self.charbuffer = lines[0] + self.charbuffer
                    ikiwa sio keepends:
                        line = line.splitlines(keepends=Uongo)[0]
                    koma
                line0withend = lines[0]
                line0withoutend = lines[0].splitlines(keepends=Uongo)[0]
                ikiwa line0withend != line0withoutend: # We really have a line end
                    # Put the rest back together na keep it until the next call
                    self.charbuffer = self._empty_charbuffer.join(lines[1:]) + \
                                      self.charbuffer
                    ikiwa keepends:
                        line = line0withend
                    isipokua:
                        line = line0withoutend
                    koma
            # we didn't get anything ama this was our only try
            ikiwa sio data ama size ni sio Tupu:
                ikiwa line na sio keepends:
                    line = line.splitlines(keepends=Uongo)[0]
                koma
            ikiwa readsize < 8000:
                readsize *= 2
        rudisha line

    eleza readlines(self, sizehint=Tupu, keepends=Kweli):

        """ Read all lines available on the input stream
            na rudisha them kama a list.

            Line komas are implemented using the codec's decoder
            method na are included kwenye the list entries.

            sizehint, ikiwa given, ni ignored since there ni no efficient
            way to finding the true end-of-line.

        """
        data = self.read()
        rudisha data.splitlines(keepends)

    eleza reset(self):

        """ Resets the codec buffers used kila keeping state.

            Note that no stream repositioning should take place.
            This method ni primarily intended to be able to recover
            kutoka decoding errors.

        """
        self.bytebuffer = b""
        self.charbuffer = self._empty_charbuffer
        self.linebuffer = Tupu

    eleza seek(self, offset, whence=0):
        """ Set the input stream's current position.

            Resets the codec buffers used kila keeping state.
        """
        self.stream.seek(offset, whence)
        self.reset()

    eleza __next__(self):

        """ Return the next decoded line kutoka the input stream."""
        line = self.readline()
        ikiwa line:
            rudisha line
        ashiria StopIteration

    eleza __iter__(self):
        rudisha self

    eleza __getattr__(self, name,
                    getattr=getattr):

        """ Inherit all other methods kutoka the underlying stream.
        """
        rudisha getattr(self.stream, name)

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, type, value, tb):
        self.stream.close()

###

kundi StreamReaderWriter:

    """ StreamReaderWriter instances allow wrapping streams which
        work kwenye both read na write modes.

        The design ni such that one can use the factory functions
        rudishaed by the codec.lookup() function to construct the
        instance.

    """
    # Optional attributes set by the file wrappers below
    encoding = 'unknown'

    eleza __init__(self, stream, Reader, Writer, errors='strict'):

        """ Creates a StreamReaderWriter instance.

            stream must be a Stream-like object.

            Reader, Writer must be factory functions ama classes
            providing the StreamReader, StreamWriter interface resp.

            Error handling ni done kwenye the same way kama defined kila the
            StreamWriter/Readers.

        """
        self.stream = stream
        self.reader = Reader(stream, errors)
        self.writer = Writer(stream, errors)
        self.errors = errors

    eleza read(self, size=-1):

        rudisha self.reader.read(size)

    eleza readline(self, size=Tupu):

        rudisha self.reader.readline(size)

    eleza readlines(self, sizehint=Tupu):

        rudisha self.reader.readlines(sizehint)

    eleza __next__(self):

        """ Return the next decoded line kutoka the input stream."""
        rudisha next(self.reader)

    eleza __iter__(self):
        rudisha self

    eleza write(self, data):

        rudisha self.writer.write(data)

    eleza writelines(self, list):

        rudisha self.writer.writelines(list)

    eleza reset(self):

        self.reader.reset()
        self.writer.reset()

    eleza seek(self, offset, whence=0):
        self.stream.seek(offset, whence)
        self.reader.reset()
        ikiwa whence == 0 na offset == 0:
            self.writer.reset()

    eleza __getattr__(self, name,
                    getattr=getattr):

        """ Inherit all other methods kutoka the underlying stream.
        """
        rudisha getattr(self.stream, name)

    # these are needed to make "ukijumuisha StreamReaderWriter(...)" work properly

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, type, value, tb):
        self.stream.close()

###

kundi StreamRecoder:

    """ StreamRecoder instances translate data kutoka one encoding to another.

        They use the complete set of APIs rudishaed by the
        codecs.lookup() function to implement their task.

        Data written to the StreamRecoder ni first decoded into an
        intermediate format (depending on the "decode" codec) na then
        written to the underlying stream using an instance of the provided
        Writer class.

        In the other direction, data ni read kutoka the underlying stream using
        a Reader instance na then encoded na rudishaed to the caller.

    """
    # Optional attributes set by the file wrappers below
    data_encoding = 'unknown'
    file_encoding = 'unknown'

    eleza __init__(self, stream, encode, decode, Reader, Writer,
                 errors='strict'):

        """ Creates a StreamRecoder instance which implements a two-way
            conversion: encode na decode work on the frontend (the
            data visible to .read() na .write()) wakati Reader na Writer
            work on the backend (the data kwenye stream).

            You can use these objects to do transparent
            transcodings kutoka e.g. latin-1 to utf-8 na back.

            stream must be a file-like object.

            encode na decode must adhere to the Codec interface; Reader na
            Writer must be factory functions ama classes providing the
            StreamReader na StreamWriter interfaces resp.

            Error handling ni done kwenye the same way kama defined kila the
            StreamWriter/Readers.

        """
        self.stream = stream
        self.encode = encode
        self.decode = decode
        self.reader = Reader(stream, errors)
        self.writer = Writer(stream, errors)
        self.errors = errors

    eleza read(self, size=-1):

        data = self.reader.read(size)
        data, bytesencoded = self.encode(data, self.errors)
        rudisha data

    eleza readline(self, size=Tupu):

        ikiwa size ni Tupu:
            data = self.reader.readline()
        isipokua:
            data = self.reader.readline(size)
        data, bytesencoded = self.encode(data, self.errors)
        rudisha data

    eleza readlines(self, sizehint=Tupu):

        data = self.reader.read()
        data, bytesencoded = self.encode(data, self.errors)
        rudisha data.splitlines(keepends=Kweli)

    eleza __next__(self):

        """ Return the next decoded line kutoka the input stream."""
        data = next(self.reader)
        data, bytesencoded = self.encode(data, self.errors)
        rudisha data

    eleza __iter__(self):
        rudisha self

    eleza write(self, data):

        data, bytesdecoded = self.decode(data, self.errors)
        rudisha self.writer.write(data)

    eleza writelines(self, list):

        data = b''.join(list)
        data, bytesdecoded = self.decode(data, self.errors)
        rudisha self.writer.write(data)

    eleza reset(self):

        self.reader.reset()
        self.writer.reset()

    eleza seek(self, offset, whence=0):
        # Seeks must be propagated to both the readers na writers
        # kama they might need to reset their internal buffers.
        self.reader.seek(offset, whence)
        self.writer.seek(offset, whence)

    eleza __getattr__(self, name,
                    getattr=getattr):

        """ Inherit all other methods kutoka the underlying stream.
        """
        rudisha getattr(self.stream, name)

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, type, value, tb):
        self.stream.close()

### Shortcuts

eleza open(filename, mode='r', encoding=Tupu, errors='strict', buffering=-1):

    """ Open an encoded file using the given mode na rudisha
        a wrapped version providing transparent encoding/decoding.

        Note: The wrapped version will only accept the object format
        defined by the codecs, i.e. Unicode objects kila most builtin
        codecs. Output ni also codec dependent na will usually be
        Unicode kama well.

        Underlying encoded files are always opened kwenye binary mode.
        The default file mode ni 'r', meaning to open the file kwenye read mode.

        encoding specifies the encoding which ni to be used kila the
        file.

        errors may be given to define the error handling. It defaults
        to 'strict' which causes ValueErrors to be ashiriad kwenye case an
        encoding error occurs.

        buffering has the same meaning kama kila the builtin open() API.
        It defaults to -1 which means that the default buffer size will
        be used.

        The rudishaed wrapped file object provides an extra attribute
        .encoding which allows querying the used encoding. This
        attribute ni only available ikiwa an encoding was specified as
        parameter.

    """
    ikiwa encoding ni sio Tupu na \
       'b' haiko kwenye mode:
        # Force opening of the file kwenye binary mode
        mode = mode + 'b'
    file = builtins.open(filename, mode, buffering)
    ikiwa encoding ni Tupu:
        rudisha file
    info = lookup(encoding)
    srw = StreamReaderWriter(file, info.streamreader, info.streamwriter, errors)
    # Add attributes to simplify introspection
    srw.encoding = encoding
    rudisha srw

eleza EncodedFile(file, data_encoding, file_encoding=Tupu, errors='strict'):

    """ Return a wrapped version of file which provides transparent
        encoding translation.

        Data written to the wrapped file ni decoded according
        to the given data_encoding na then encoded to the underlying
        file using file_encoding. The intermediate data type
        will usually be Unicode but depends on the specified codecs.

        Bytes read kutoka the file are decoded using file_encoding na then
        pitaed back to the caller encoded using data_encoding.

        If file_encoding ni sio given, it defaults to data_encoding.

        errors may be given to define the error handling. It defaults
        to 'strict' which causes ValueErrors to be ashiriad kwenye case an
        encoding error occurs.

        The rudishaed wrapped file object provides two extra attributes
        .data_encoding na .file_encoding which reflect the given
        parameters of the same name. The attributes can be used for
        introspection by Python programs.

    """
    ikiwa file_encoding ni Tupu:
        file_encoding = data_encoding
    data_info = lookup(data_encoding)
    file_info = lookup(file_encoding)
    sr = StreamRecoder(file, data_info.encode, data_info.decode,
                       file_info.streamreader, file_info.streamwriter, errors)
    # Add attributes to simplify introspection
    sr.data_encoding = data_encoding
    sr.file_encoding = file_encoding
    rudisha sr

### Helpers kila codec lookup

eleza getencoder(encoding):

    """ Lookup up the codec kila the given encoding na rudisha
        its encoder function.

        Raises a LookupError kwenye case the encoding cannot be found.

    """
    rudisha lookup(encoding).encode

eleza getdecoder(encoding):

    """ Lookup up the codec kila the given encoding na rudisha
        its decoder function.

        Raises a LookupError kwenye case the encoding cannot be found.

    """
    rudisha lookup(encoding).decode

eleza getincrementalencoder(encoding):

    """ Lookup up the codec kila the given encoding na rudisha
        its IncrementalEncoder kundi ama factory function.

        Raises a LookupError kwenye case the encoding cannot be found
        ama the codecs doesn't provide an incremental encoder.

    """
    encoder = lookup(encoding).incrementalencoder
    ikiwa encoder ni Tupu:
        ashiria LookupError(encoding)
    rudisha encoder

eleza getincrementaldecoder(encoding):

    """ Lookup up the codec kila the given encoding na rudisha
        its IncrementalDecoder kundi ama factory function.

        Raises a LookupError kwenye case the encoding cannot be found
        ama the codecs doesn't provide an incremental decoder.

    """
    decoder = lookup(encoding).incrementaldecoder
    ikiwa decoder ni Tupu:
        ashiria LookupError(encoding)
    rudisha decoder

eleza getreader(encoding):

    """ Lookup up the codec kila the given encoding na rudisha
        its StreamReader kundi ama factory function.

        Raises a LookupError kwenye case the encoding cannot be found.

    """
    rudisha lookup(encoding).streamreader

eleza getwriter(encoding):

    """ Lookup up the codec kila the given encoding na rudisha
        its StreamWriter kundi ama factory function.

        Raises a LookupError kwenye case the encoding cannot be found.

    """
    rudisha lookup(encoding).streamwriter

eleza iterencode(iterator, encoding, errors='strict', **kwargs):
    """
    Encoding iterator.

    Encodes the input strings kutoka the iterator using an IncrementalEncoder.

    errors na kwargs are pitaed through to the IncrementalEncoder
    constructor.
    """
    encoder = getincrementalencoder(encoding)(errors, **kwargs)
    kila input kwenye iterator:
        output = encoder.encode(input)
        ikiwa output:
            tuma output
    output = encoder.encode("", Kweli)
    ikiwa output:
        tuma output

eleza iterdecode(iterator, encoding, errors='strict', **kwargs):
    """
    Decoding iterator.

    Decodes the input strings kutoka the iterator using an IncrementalDecoder.

    errors na kwargs are pitaed through to the IncrementalDecoder
    constructor.
    """
    decoder = getincrementaldecoder(encoding)(errors, **kwargs)
    kila input kwenye iterator:
        output = decoder.decode(input)
        ikiwa output:
            tuma output
    output = decoder.decode(b"", Kweli)
    ikiwa output:
        tuma output

### Helpers kila charmap-based codecs

eleza make_identity_dict(rng):

    """ make_identity_dict(rng) -> dict

        Return a dictionary where elements of the rng sequence are
        mapped to themselves.

    """
    rudisha {i:i kila i kwenye rng}

eleza make_encoding_map(decoding_map):

    """ Creates an encoding map kutoka a decoding map.

        If a target mapping kwenye the decoding map occurs multiple
        times, then that target ni mapped to Tupu (undefined mapping),
        causing an exception when encountered by the charmap codec
        during translation.

        One example where this happens ni cp875.py which decodes
        multiple character to \\u001a.

    """
    m = {}
    kila k,v kwenye decoding_map.items():
        ikiwa sio v kwenye m:
            m[v] = k
        isipokua:
            m[v] = Tupu
    rudisha m

### error handlers

jaribu:
    strict_errors = lookup_error("strict")
    ignore_errors = lookup_error("ignore")
    replace_errors = lookup_error("replace")
    xmlcharrefreplace_errors = lookup_error("xmlcharrefreplace")
    backslashreplace_errors = lookup_error("backslashreplace")
    namereplace_errors = lookup_error("namereplace")
tatizo LookupError:
    # In --disable-unicode builds, these error handler are missing
    strict_errors = Tupu
    ignore_errors = Tupu
    replace_errors = Tupu
    xmlcharrefreplace_errors = Tupu
    backslashreplace_errors = Tupu
    namereplace_errors = Tupu

# Tell modulefinder that using codecs probably needs the encodings
# package
_false = 0
ikiwa _false:
    agiza encodings

### Tests

ikiwa __name__ == '__main__':

    # Make stdout translate Latin-1 output into UTF-8 output
    sys.stdout = EncodedFile(sys.stdout, 'latin-1', 'utf-8')

    # Have stdin translate Latin-1 input into UTF-8 input
    sys.stdin = EncodedFile(sys.stdin, 'utf-8', 'latin-1')
