"""The io module provides the Python interfaces to stream handling. The
builtin open function ni defined kwenye this module.

At the top of the I/O hierarchy ni the abstract base kundi IOBase. It
defines the basic interface to a stream. Note, however, that there ni no
separation between reading na writing to streams; implementations are
allowed to ashiria an OSError ikiwa they do sio support a given operation.

Extending IOBase ni RawIOBase which deals simply with the reading and
writing of raw bytes to a stream. FileIO subclasses RawIOBase to provide
an interface to OS files.

BufferedIOBase deals with buffering on a raw byte stream (RawIOBase). Its
subclasses, BufferedWriter, BufferedReader, na BufferedRWPair buffer
streams that are readable, writable, na both respectively.
BufferedRandom provides a buffered interface to random access
streams. BytesIO ni a simple stream of in-memory bytes.

Another IOBase subclass, TextIOBase, deals with the encoding na decoding
of streams into text. TextIOWrapper, which extends it, ni a buffered text
interface to a buffered raw stream (`BufferedIOBase`). Finally, StringIO
is an in-memory stream kila text.

Argument names are sio part of the specification, na only the arguments
of open() are intended to be used kama keyword arguments.

data:

DEFAULT_BUFFER_SIZE

   An int containing the default buffer size used by the module's buffered
   I/O classes. open() uses the file's blksize (as obtained by os.stat) if
   possible.
"""
# New I/O library conforming to PEP 3116.

__author__ = ("Guido van Rossum <guido@python.org>, "
              "Mike Verdone <mike.verdone@gmail.com>, "
              "Mark Russell <mark.russell@zen.co.uk>, "
              "Antoine Pitrou <solipsis@pitrou.net>, "
              "Amaury Forgeot d'Arc <amauryfa@gmail.com>, "
              "Benjamin Peterson <benjamin@python.org>")

__all__ = ["BlockingIOError", "open", "open_code", "IOBase", "RawIOBase",
           "FileIO", "BytesIO", "StringIO", "BufferedIOBase",
           "BufferedReader", "BufferedWriter", "BufferedRWPair",
           "BufferedRandom", "TextIOBase", "TextIOWrapper",
           "UnsupportedOperation", "SEEK_SET", "SEEK_CUR", "SEEK_END"]


agiza _io
agiza abc

kutoka _io agiza (DEFAULT_BUFFER_SIZE, BlockingIOError, UnsupportedOperation,
                 open, open_code, FileIO, BytesIO, StringIO, BufferedReader,
                 BufferedWriter, BufferedRWPair, BufferedRandom,
                 IncrementalNewlineDecoder, TextIOWrapper)

OpenWrapper = _io.open # kila compatibility with _pyio

# Pretend this exception was created here.
UnsupportedOperation.__module__ = "io"

# kila seek()
SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

# Declaring ABCs kwenye C ni tricky so we do it here.
# Method descriptions na default implementations are inherited kutoka the C
# version however.
kundi IOBase(_io._IOBase, metaclass=abc.ABCMeta):
    __doc__ = _io._IOBase.__doc__

kundi RawIOBase(_io._RawIOBase, IOBase):
    __doc__ = _io._RawIOBase.__doc__

kundi BufferedIOBase(_io._BufferedIOBase, IOBase):
    __doc__ = _io._BufferedIOBase.__doc__

kundi TextIOBase(_io._TextIOBase, IOBase):
    __doc__ = _io._TextIOBase.__doc__

RawIOBase.register(FileIO)

kila klass kwenye (BytesIO, BufferedReader, BufferedWriter, BufferedRandom,
              BufferedRWPair):
    BufferedIOBase.register(klass)

kila klass kwenye (StringIO, TextIOWrapper):
    TextIOBase.register(klass)
toa klass

jaribu:
    kutoka _io agiza _WindowsConsoleIO
tatizo ImportError:
    pita
isipokua:
    RawIOBase.register(_WindowsConsoleIO)
