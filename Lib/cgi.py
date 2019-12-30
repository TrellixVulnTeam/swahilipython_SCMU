#! /usr/local/bin/python

# NOTE: the above "/usr/local/bin/python" ni NOT a mistake.  It is
# intentionally NOT "/usr/bin/env python".  On many systems
# (e.g. Solaris), /usr/local/bin ni haiko kwenye $PATH kama pitaed to CGI
# scripts, na /usr/local/bin ni the default directory where Python is
# installed, so /usr/bin/env would be unable to find python.  Granted,
# binary installations by Linux vendors often install Python kwenye
# /usr/bin.  So let those vendors patch cgi.py to match their choice
# of installation.

"""Support module kila CGI (Common Gateway Interface) scripts.

This module defines a number of utilities kila use by CGI scripts
written kwenye Python.
"""

# History
# -------
#
# Michael McLay started this module.  Steve Majewski changed the
# interface to SvFormContentDict na FormContentDict.  The multipart
# parsing was inspired by code submitted by Andreas Paepcke.  Guido van
# Rossum rewrote, reformatted na documented the module na ni currently
# responsible kila its maintenance.
#

__version__ = "2.6"


# Imports
# =======

kutoka io agiza StringIO, BytesIO, TextIOWrapper
kutoka collections.abc agiza Mapping
agiza sys
agiza os
agiza urllib.parse
kutoka email.parser agiza FeedParser
kutoka email.message agiza Message
agiza html
agiza locale
agiza tempfile

__all__ = ["MiniFieldStorage", "FieldStorage", "parse", "parse_multipart",
           "parse_header", "test", "print_exception", "print_environ",
           "print_form", "print_directory", "print_arguments",
           "print_environ_usage"]

# Logging support
# ===============

logfile = ""            # Filename to log to, ikiwa sio empty
logfp = Tupu            # File object to log to, ikiwa sio Tupu

eleza initlog(*allargs):
    """Write a log message, ikiwa there ni a log file.

    Even though this function ni called initlog(), you should always
    use log(); log ni a variable that ni set either to initlog
    (initially), to dolog (once the log file has been opened), ama to
    nolog (when logging ni disabled).

    The first argument ni a format string; the remaining arguments (if
    any) are arguments to the % operator, so e.g.
        log("%s: %s", "a", "b")
    will write "a: b" to the log file, followed by a newline.

    If the global logfp ni sio Tupu, it should be a file object to
    which log data ni written.

    If the global logfp ni Tupu, the global logfile may be a string
    giving a filename to open, kwenye append mode.  This file should be
    world writable!!!  If the file can't be opened, logging is
    silently disabled (since there ni no safe place where we could
    send an error message).

    """
    global log, logfile, logfp
    ikiwa logfile na sio logfp:
        jaribu:
            logfp = open(logfile, "a")
        tatizo OSError:
            pita
    ikiwa sio logfp:
        log = nolog
    isipokua:
        log = dolog
    log(*allargs)

eleza dolog(fmt, *args):
    """Write a log message to the log file.  See initlog() kila docs."""
    logfp.write(fmt%args + "\n")

eleza nolog(*allargs):
    """Dummy function, assigned to log when logging ni disabled."""
    pita

eleza closelog():
    """Close the log file."""
    global log, logfile, logfp
    logfile = ''
    ikiwa logfp:
        logfp.close()
        logfp = Tupu
    log = initlog

log = initlog           # The current logging function


# Parsing functions
# =================

# Maximum input we will accept when REQUEST_METHOD ni POST
# 0 ==> unlimited input
maxlen = 0

eleza parse(fp=Tupu, environ=os.environ, keep_blank_values=0, strict_parsing=0):
    """Parse a query kwenye the environment ama kutoka a file (default stdin)

        Arguments, all optional:

        fp              : file pointer; default: sys.stdin.buffer

        environ         : environment dictionary; default: os.environ

        keep_blank_values: flag indicating whether blank values kwenye
            percent-encoded forms should be treated kama blank strings.
            A true value indicates that blanks should be retained as
            blank strings.  The default false value indicates that
            blank values are to be ignored na treated kama ikiwa they were
            sio inluded.

        strict_parsing: flag indicating what to do ukijumuisha parsing errors.
            If false (the default), errors are silently ignored.
            If true, errors ashiria a ValueError exception.
    """
    ikiwa fp ni Tupu:
        fp = sys.stdin

    # field keys na values (tatizo kila files) are returned kama strings
    # an encoding ni required to decode the bytes read kutoka self.fp
    ikiwa hasattr(fp,'encoding'):
        encoding = fp.encoding
    isipokua:
        encoding = 'latin-1'

    # fp.read() must rudisha bytes
    ikiwa isinstance(fp, TextIOWrapper):
        fp = fp.buffer

    ikiwa sio 'REQUEST_METHOD' kwenye environ:
        environ['REQUEST_METHOD'] = 'GET'       # For testing stand-alone
    ikiwa environ['REQUEST_METHOD'] == 'POST':
        ctype, pdict = parse_header(environ['CONTENT_TYPE'])
        ikiwa ctype == 'multipart/form-data':
            rudisha parse_multipart(fp, pdict)
        lasivyo ctype == 'application/x-www-form-urlencoded':
            clength = int(environ['CONTENT_LENGTH'])
            ikiwa maxlen na clength > maxlen:
                ashiria ValueError('Maximum content length exceeded')
            qs = fp.read(clength).decode(encoding)
        isipokua:
            qs = ''                     # Unknown content-type
        ikiwa 'QUERY_STRING' kwenye environ:
            ikiwa qs: qs = qs + '&'
            qs = qs + environ['QUERY_STRING']
        lasivyo sys.argv[1:]:
            ikiwa qs: qs = qs + '&'
            qs = qs + sys.argv[1]
        environ['QUERY_STRING'] = qs    # XXX Shouldn't, really
    lasivyo 'QUERY_STRING' kwenye environ:
        qs = environ['QUERY_STRING']
    isipokua:
        ikiwa sys.argv[1:]:
            qs = sys.argv[1]
        isipokua:
            qs = ""
        environ['QUERY_STRING'] = qs    # XXX Shouldn't, really
    rudisha urllib.parse.parse_qs(qs, keep_blank_values, strict_parsing,
                                 encoding=encoding)


eleza parse_multipart(fp, pdict, encoding="utf-8", errors="replace"):
    """Parse multipart input.

    Arguments:
    fp   : input file
    pdict: dictionary containing other parameters of content-type header
    encoding, errors: request encoding na error handler, pitaed to
        FieldStorage

    Returns a dictionary just like parse_qs(): keys are the field names, each
    value ni a list of values kila that field. For non-file fields, the value
    ni a list of strings.
    """
    # RFC 2026, Section 5.1 : The "multipart" boundary delimiters are always
    # represented kama 7bit US-ASCII.
    boundary = pdict['boundary'].decode('ascii')
    ctype = "multipart/form-data; boundary={}".format(boundary)
    headers = Message()
    headers.set_type(ctype)
    headers['Content-Length'] = pdict['CONTENT-LENGTH']
    fs = FieldStorage(fp, headers=headers, encoding=encoding, errors=errors,
        environ={'REQUEST_METHOD': 'POST'})
    rudisha {k: fs.getlist(k) kila k kwenye fs}

eleza _parseparam(s):
    wakati s[:1] == ';':
        s = s[1:]
        end = s.find(';')
        wakati end > 0 na (s.count('"', 0, end) - s.count('\\"', 0, end)) % 2:
            end = s.find(';', end + 1)
        ikiwa end < 0:
            end = len(s)
        f = s[:end]
        tuma f.strip()
        s = s[end:]

eleza parse_header(line):
    """Parse a Content-type like header.

    Return the main content-type na a dictionary of options.

    """
    parts = _parseparam(';' + line)
    key = parts.__next__()
    pdict = {}
    kila p kwenye parts:
        i = p.find('=')
        ikiwa i >= 0:
            name = p[:i].strip().lower()
            value = p[i+1:].strip()
            ikiwa len(value) >= 2 na value[0] == value[-1] == '"':
                value = value[1:-1]
                value = value.replace('\\\\', '\\').replace('\\"', '"')
            pdict[name] = value
    rudisha key, pdict


# Classes kila field storage
# =========================

kundi MiniFieldStorage:

    """Like FieldStorage, kila use when no file uploads are possible."""

    # Dummy attributes
    filename = Tupu
    list = Tupu
    type = Tupu
    file = Tupu
    type_options = {}
    disposition = Tupu
    disposition_options = {}
    headers = {}

    eleza __init__(self, name, value):
        """Constructor kutoka field name na value."""
        self.name = name
        self.value = value
        # self.file = StringIO(value)

    eleza __repr__(self):
        """Return printable representation."""
        rudisha "MiniFieldStorage(%r, %r)" % (self.name, self.value)


kundi FieldStorage:

    """Store a sequence of fields, reading multipart/form-data.

    This kundi provides naming, typing, files stored on disk, na
    more.  At the top level, it ni accessible like a dictionary, whose
    keys are the field names.  (Note: Tupu can occur kama a field name.)
    The items are either a Python list (ikiwa there's multiple values) ama
    another FieldStorage ama MiniFieldStorage object.  If it's a single
    object, it has the following attributes:

    name: the field name, ikiwa specified; otherwise Tupu

    filename: the filename, ikiwa specified; otherwise Tupu; this ni the
        client side filename, *not* the file name on which it is
        stored (that's a temporary file you don't deal with)

    value: the value kama a *string*; kila file uploads, this
        transparently reads the file every time you request the value
        na returns *bytes*

    file: the file(-like) object kutoka which you can read the data *as
        bytes* ; Tupu ikiwa the data ni stored a simple string

    type: the content-type, ama Tupu ikiwa sio specified

    type_options: dictionary of options specified on the content-type
        line

    disposition: content-disposition, ama Tupu ikiwa sio specified

    disposition_options: dictionary of corresponding options

    headers: a dictionary(-like) object (sometimes email.message.Message ama a
        subkundi thereof) containing *all* headers

    The kundi ni subclassable, mostly kila the purpose of overriding
    the make_file() method, which ni called internally to come up with
    a file open kila reading na writing.  This makes it possible to
    override the default choice of storing all files kwenye a temporary
    directory na unlinking them kama soon kama they have been opened.

    """
    eleza __init__(self, fp=Tupu, headers=Tupu, outerboundary=b'',
                 environ=os.environ, keep_blank_values=0, strict_parsing=0,
                 limit=Tupu, encoding='utf-8', errors='replace',
                 max_num_fields=Tupu):
        """Constructor.  Read multipart/* until last part.

        Arguments, all optional:

        fp              : file pointer; default: sys.stdin.buffer
            (sio used when the request method ni GET)
            Can be :
            1. a TextIOWrapper object
            2. an object whose read() na readline() methods rudisha bytes

        headers         : header dictionary-like object; default:
            taken kutoka environ kama per CGI spec

        outerboundary   : terminating multipart boundary
            (kila internal use only)

        environ         : environment dictionary; default: os.environ

        keep_blank_values: flag indicating whether blank values kwenye
            percent-encoded forms should be treated kama blank strings.
            A true value indicates that blanks should be retained as
            blank strings.  The default false value indicates that
            blank values are to be ignored na treated kama ikiwa they were
            sio inluded.

        strict_parsing: flag indicating what to do ukijumuisha parsing errors.
            If false (the default), errors are silently ignored.
            If true, errors ashiria a ValueError exception.

        limit : used internally to read parts of multipart/form-data forms,
            to exit kutoka the reading loop when reached. It ni the difference
            between the form content-length na the number of bytes already
            read

        encoding, errors : the encoding na error handler used to decode the
            binary stream to strings. Must be the same kama the charset defined
            kila the page sending the form (content-type : meta http-equiv ama
            header)

        max_num_fields: int. If set, then __init__ throws a ValueError
            ikiwa there are more than n fields read by parse_qsl().

        """
        method = 'GET'
        self.keep_blank_values = keep_blank_values
        self.strict_parsing = strict_parsing
        self.max_num_fields = max_num_fields
        ikiwa 'REQUEST_METHOD' kwenye environ:
            method = environ['REQUEST_METHOD'].upper()
        self.qs_on_post = Tupu
        ikiwa method == 'GET' ama method == 'HEAD':
            ikiwa 'QUERY_STRING' kwenye environ:
                qs = environ['QUERY_STRING']
            lasivyo sys.argv[1:]:
                qs = sys.argv[1]
            isipokua:
                qs = ""
            qs = qs.encode(locale.getpreferredencoding(), 'surrogateescape')
            fp = BytesIO(qs)
            ikiwa headers ni Tupu:
                headers = {'content-type':
                           "application/x-www-form-urlencoded"}
        ikiwa headers ni Tupu:
            headers = {}
            ikiwa method == 'POST':
                # Set default content-type kila POST to what's traditional
                headers['content-type'] = "application/x-www-form-urlencoded"
            ikiwa 'CONTENT_TYPE' kwenye environ:
                headers['content-type'] = environ['CONTENT_TYPE']
            ikiwa 'QUERY_STRING' kwenye environ:
                self.qs_on_post = environ['QUERY_STRING']
            ikiwa 'CONTENT_LENGTH' kwenye environ:
                headers['content-length'] = environ['CONTENT_LENGTH']
        isipokua:
            ikiwa sio (isinstance(headers, (Mapping, Message))):
                ashiria TypeError("headers must be mapping ama an instance of "
                                "email.message.Message")
        self.headers = headers
        ikiwa fp ni Tupu:
            self.fp = sys.stdin.buffer
        # self.fp.read() must rudisha bytes
        lasivyo isinstance(fp, TextIOWrapper):
            self.fp = fp.buffer
        isipokua:
            ikiwa sio (hasattr(fp, 'read') na hasattr(fp, 'readline')):
                ashiria TypeError("fp must be file pointer")
            self.fp = fp

        self.encoding = encoding
        self.errors = errors

        ikiwa sio isinstance(outerboundary, bytes):
            ashiria TypeError('outerboundary must be bytes, sio %s'
                            % type(outerboundary).__name__)
        self.outerboundary = outerboundary

        self.bytes_read = 0
        self.limit = limit

        # Process content-disposition header
        cdisp, pdict = "", {}
        ikiwa 'content-disposition' kwenye self.headers:
            cdisp, pdict = parse_header(self.headers['content-disposition'])
        self.disposition = cdisp
        self.disposition_options = pdict
        self.name = Tupu
        ikiwa 'name' kwenye pdict:
            self.name = pdict['name']
        self.filename = Tupu
        ikiwa 'filename' kwenye pdict:
            self.filename = pdict['filename']
        self._binary_file = self.filename ni sio Tupu

        # Process content-type header
        #
        # Honor any existing content-type header.  But ikiwa there ni no
        # content-type header, use some sensible defaults.  Assume
        # outerboundary ni "" at the outer level, but something non-false
        # inside a multi-part.  The default kila an inner part ni text/plain,
        # but kila an outer part it should be urlencoded.  This should catch
        # bogus clients which erroneously forget to include a content-type
        # header.
        #
        # See below kila what we do ikiwa there does exist a content-type header,
        # but it happens to be something we don't understand.
        ikiwa 'content-type' kwenye self.headers:
            ctype, pdict = parse_header(self.headers['content-type'])
        lasivyo self.outerboundary ama method != 'POST':
            ctype, pdict = "text/plain", {}
        isipokua:
            ctype, pdict = 'application/x-www-form-urlencoded', {}
        self.type = ctype
        self.type_options = pdict
        ikiwa 'boundary' kwenye pdict:
            self.innerboundary = pdict['boundary'].encode(self.encoding,
                                                          self.errors)
        isipokua:
            self.innerboundary = b""

        clen = -1
        ikiwa 'content-length' kwenye self.headers:
            jaribu:
                clen = int(self.headers['content-length'])
            tatizo ValueError:
                pita
            ikiwa maxlen na clen > maxlen:
                ashiria ValueError('Maximum content length exceeded')
        self.length = clen
        ikiwa self.limit ni Tupu na clen >= 0:
            self.limit = clen

        self.list = self.file = Tupu
        self.done = 0
        ikiwa ctype == 'application/x-www-form-urlencoded':
            self.read_urlencoded()
        lasivyo ctype[:10] == 'multipart/':
            self.read_multi(environ, keep_blank_values, strict_parsing)
        isipokua:
            self.read_single()

    eleza __del__(self):
        jaribu:
            self.file.close()
        tatizo AttributeError:
            pita

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        self.file.close()

    eleza __repr__(self):
        """Return a printable representation."""
        rudisha "FieldStorage(%r, %r, %r)" % (
                self.name, self.filename, self.value)

    eleza __iter__(self):
        rudisha iter(self.keys())

    eleza __getattr__(self, name):
        ikiwa name != 'value':
            ashiria AttributeError(name)
        ikiwa self.file:
            self.file.seek(0)
            value = self.file.read()
            self.file.seek(0)
        lasivyo self.list ni sio Tupu:
            value = self.list
        isipokua:
            value = Tupu
        rudisha value

    eleza __getitem__(self, key):
        """Dictionary style indexing."""
        ikiwa self.list ni Tupu:
            ashiria TypeError("sio indexable")
        found = []
        kila item kwenye self.list:
            ikiwa item.name == key: found.append(item)
        ikiwa sio found:
            ashiria KeyError(key)
        ikiwa len(found) == 1:
            rudisha found[0]
        isipokua:
            rudisha found

    eleza getvalue(self, key, default=Tupu):
        """Dictionary style get() method, including 'value' lookup."""
        ikiwa key kwenye self:
            value = self[key]
            ikiwa isinstance(value, list):
                rudisha [x.value kila x kwenye value]
            isipokua:
                rudisha value.value
        isipokua:
            rudisha default

    eleza getfirst(self, key, default=Tupu):
        """ Return the first value received."""
        ikiwa key kwenye self:
            value = self[key]
            ikiwa isinstance(value, list):
                rudisha value[0].value
            isipokua:
                rudisha value.value
        isipokua:
            rudisha default

    eleza getlist(self, key):
        """ Return list of received values."""
        ikiwa key kwenye self:
            value = self[key]
            ikiwa isinstance(value, list):
                rudisha [x.value kila x kwenye value]
            isipokua:
                rudisha [value.value]
        isipokua:
            rudisha []

    eleza keys(self):
        """Dictionary style keys() method."""
        ikiwa self.list ni Tupu:
            ashiria TypeError("sio indexable")
        rudisha list(set(item.name kila item kwenye self.list))

    eleza __contains__(self, key):
        """Dictionary style __contains__ method."""
        ikiwa self.list ni Tupu:
            ashiria TypeError("sio indexable")
        rudisha any(item.name == key kila item kwenye self.list)

    eleza __len__(self):
        """Dictionary style len(x) support."""
        rudisha len(self.keys())

    eleza __bool__(self):
        ikiwa self.list ni Tupu:
            ashiria TypeError("Cansio be converted to bool.")
        rudisha bool(self.list)

    eleza read_urlencoded(self):
        """Internal: read data kwenye query string format."""
        qs = self.fp.read(self.length)
        ikiwa sio isinstance(qs, bytes):
            ashiria ValueError("%s should rudisha bytes, got %s" \
                             % (self.fp, type(qs).__name__))
        qs = qs.decode(self.encoding, self.errors)
        ikiwa self.qs_on_post:
            qs += '&' + self.qs_on_post
        query = urllib.parse.parse_qsl(
            qs, self.keep_blank_values, self.strict_parsing,
            encoding=self.encoding, errors=self.errors,
            max_num_fields=self.max_num_fields)
        self.list = [MiniFieldStorage(key, value) kila key, value kwenye query]
        self.skip_lines()

    FieldStorageClass = Tupu

    eleza read_multi(self, environ, keep_blank_values, strict_parsing):
        """Internal: read a part that ni itself multipart."""
        ib = self.innerboundary
        ikiwa sio valid_boundary(ib):
            ashiria ValueError('Invalid boundary kwenye multipart form: %r' % (ib,))
        self.list = []
        ikiwa self.qs_on_post:
            query = urllib.parse.parse_qsl(
                self.qs_on_post, self.keep_blank_values, self.strict_parsing,
                encoding=self.encoding, errors=self.errors,
                max_num_fields=self.max_num_fields)
            self.list.extend(MiniFieldStorage(key, value) kila key, value kwenye query)

        klass = self.FieldStorageClass ama self.__class__
        first_line = self.fp.readline() # bytes
        ikiwa sio isinstance(first_line, bytes):
            ashiria ValueError("%s should rudisha bytes, got %s" \
                             % (self.fp, type(first_line).__name__))
        self.bytes_read += len(first_line)

        # Ensure that we consume the file until we've hit our inner boundary
        wakati (first_line.strip() != (b"--" + self.innerboundary) na
                first_line):
            first_line = self.fp.readline()
            self.bytes_read += len(first_line)

        # Propagate max_num_fields into the sub kundi appropriately
        max_num_fields = self.max_num_fields
        ikiwa max_num_fields ni sio Tupu:
            max_num_fields -= len(self.list)

        wakati Kweli:
            parser = FeedParser()
            hdr_text = b""
            wakati Kweli:
                data = self.fp.readline()
                hdr_text += data
                ikiwa sio data.strip():
                    koma
            ikiwa sio hdr_text:
                koma
            # parser takes strings, sio bytes
            self.bytes_read += len(hdr_text)
            parser.feed(hdr_text.decode(self.encoding, self.errors))
            headers = parser.close()

            # Some clients add Content-Length kila part headers, ignore them
            ikiwa 'content-length' kwenye headers:
                toa headers['content-length']

            limit = Tupu ikiwa self.limit ni Tupu \
                isipokua self.limit - self.bytes_read
            part = klass(self.fp, headers, ib, environ, keep_blank_values,
                         strict_parsing, limit,
                         self.encoding, self.errors, max_num_fields)

            ikiwa max_num_fields ni sio Tupu:
                max_num_fields -= 1
                ikiwa part.list:
                    max_num_fields -= len(part.list)
                ikiwa max_num_fields < 0:
                    ashiria ValueError('Max number of fields exceeded')

            self.bytes_read += part.bytes_read
            self.list.append(part)
            ikiwa part.done ama self.bytes_read >= self.length > 0:
                koma
        self.skip_lines()

    eleza read_single(self):
        """Internal: read an atomic part."""
        ikiwa self.length >= 0:
            self.read_binary()
            self.skip_lines()
        isipokua:
            self.read_lines()
        self.file.seek(0)

    bufsize = 8*1024            # I/O buffering size kila copy to file

    eleza read_binary(self):
        """Internal: read binary data."""
        self.file = self.make_file()
        todo = self.length
        ikiwa todo >= 0:
            wakati todo > 0:
                data = self.fp.read(min(todo, self.bufsize)) # bytes
                ikiwa sio isinstance(data, bytes):
                    ashiria ValueError("%s should rudisha bytes, got %s"
                                     % (self.fp, type(data).__name__))
                self.bytes_read += len(data)
                ikiwa sio data:
                    self.done = -1
                    koma
                self.file.write(data)
                todo = todo - len(data)

    eleza read_lines(self):
        """Internal: read lines until EOF ama outerboundary."""
        ikiwa self._binary_file:
            self.file = self.__file = BytesIO() # store data kama bytes kila files
        isipokua:
            self.file = self.__file = StringIO() # kama strings kila other fields
        ikiwa self.outerboundary:
            self.read_lines_to_outerboundary()
        isipokua:
            self.read_lines_to_eof()

    eleza __write(self, line):
        """line ni always bytes, sio string"""
        ikiwa self.__file ni sio Tupu:
            ikiwa self.__file.tell() + len(line) > 1000:
                self.file = self.make_file()
                data = self.__file.getvalue()
                self.file.write(data)
                self.__file = Tupu
        ikiwa self._binary_file:
            # keep bytes
            self.file.write(line)
        isipokua:
            # decode to string
            self.file.write(line.decode(self.encoding, self.errors))

    eleza read_lines_to_eof(self):
        """Internal: read lines until EOF."""
        wakati 1:
            line = self.fp.readline(1<<16) # bytes
            self.bytes_read += len(line)
            ikiwa sio line:
                self.done = -1
                koma
            self.__write(line)

    eleza read_lines_to_outerboundary(self):
        """Internal: read lines until outerboundary.
        Data ni read kama bytes: boundaries na line ends must be converted
        to bytes kila comparisons.
        """
        next_boundary = b"--" + self.outerboundary
        last_boundary = next_boundary + b"--"
        delim = b""
        last_line_lfend = Kweli
        _read = 0
        wakati 1:
            ikiwa self.limit ni sio Tupu na _read >= self.limit:
                koma
            line = self.fp.readline(1<<16) # bytes
            self.bytes_read += len(line)
            _read += len(line)
            ikiwa sio line:
                self.done = -1
                koma
            ikiwa delim == b"\r":
                line = delim + line
                delim = b""
            ikiwa line.startswith(b"--") na last_line_lfend:
                strippedline = line.rstrip()
                ikiwa strippedline == next_boundary:
                    koma
                ikiwa strippedline == last_boundary:
                    self.done = 1
                    koma
            odelim = delim
            ikiwa line.endswith(b"\r\n"):
                delim = b"\r\n"
                line = line[:-2]
                last_line_lfend = Kweli
            lasivyo line.endswith(b"\n"):
                delim = b"\n"
                line = line[:-1]
                last_line_lfend = Kweli
            lasivyo line.endswith(b"\r"):
                # We may interrupt \r\n sequences ikiwa they span the 2**16
                # byte boundary
                delim = b"\r"
                line = line[:-1]
                last_line_lfend = Uongo
            isipokua:
                delim = b""
                last_line_lfend = Uongo
            self.__write(odelim + line)

    eleza skip_lines(self):
        """Internal: skip lines until outer boundary ikiwa defined."""
        ikiwa sio self.outerboundary ama self.done:
            rudisha
        next_boundary = b"--" + self.outerboundary
        last_boundary = next_boundary + b"--"
        last_line_lfend = Kweli
        wakati Kweli:
            line = self.fp.readline(1<<16)
            self.bytes_read += len(line)
            ikiwa sio line:
                self.done = -1
                koma
            ikiwa line.endswith(b"--") na last_line_lfend:
                strippedline = line.strip()
                ikiwa strippedline == next_boundary:
                    koma
                ikiwa strippedline == last_boundary:
                    self.done = 1
                    koma
            last_line_lfend = line.endswith(b'\n')

    eleza make_file(self):
        """Overridable: rudisha a readable & writable file.

        The file will be used kama follows:
        - data ni written to it
        - seek(0)
        - data ni read kutoka it

        The file ni opened kwenye binary mode kila files, kwenye text mode
        kila other fields

        This version opens a temporary file kila reading na writing,
        na immediately deletes (unlinks) it.  The trick (on Unix!) is
        that the file can still be used, but it can't be opened by
        another process, na it will automatically be deleted when it
        ni closed ama when the current process terminates.

        If you want a more permanent file, you derive a kundi which
        overrides this method.  If you want a visible temporary file
        that ni nevertheless automatically deleted when the script
        terminates, try defining a __del__ method kwenye a derived class
        which unlinks the temporary files you have created.

        """
        ikiwa self._binary_file:
            rudisha tempfile.TemporaryFile("wb+")
        isipokua:
            rudisha tempfile.TemporaryFile("w+",
                encoding=self.encoding, newline = '\n')


# Test/debug code
# ===============

eleza test(environ=os.environ):
    """Robust test CGI script, usable kama main program.

    Write minimal HTTP headers na dump all information provided to
    the script kwenye HTML form.

    """
    andika("Content-type: text/html")
    andika()
    sys.stderr = sys.stdout
    jaribu:
        form = FieldStorage()   # Replace ukijumuisha other classes to test those
        print_directory()
        print_arguments()
        print_form(form)
        print_environ(environ)
        print_environ_usage()
        eleza f():
            exec("testing print_exception() -- <I>italics?</I>")
        eleza g(f=f):
            f()
        andika("<H3>What follows ni a test, sio an actual exception:</H3>")
        g()
    tatizo:
        print_exception()

    andika("<H1>Second try ukijumuisha a small maxlen...</H1>")

    global maxlen
    maxlen = 50
    jaribu:
        form = FieldStorage()   # Replace ukijumuisha other classes to test those
        print_directory()
        print_arguments()
        print_form(form)
        print_environ(environ)
    tatizo:
        print_exception()

eleza print_exception(type=Tupu, value=Tupu, tb=Tupu, limit=Tupu):
    ikiwa type ni Tupu:
        type, value, tb = sys.exc_info()
    agiza traceback
    andika()
    andika("<H3>Traceback (most recent call last):</H3>")
    list = traceback.format_tb(tb, limit) + \
           traceback.format_exception_only(type, value)
    andika("<PRE>%s<B>%s</B></PRE>" % (
        html.escape("".join(list[:-1])),
        html.escape(list[-1]),
        ))
    toa tb

eleza print_environ(environ=os.environ):
    """Dump the shell environment kama HTML."""
    keys = sorted(environ.keys())
    andika()
    andika("<H3>Shell Environment:</H3>")
    andika("<DL>")
    kila key kwenye keys:
        andika("<DT>", html.escape(key), "<DD>", html.escape(environ[key]))
    andika("</DL>")
    andika()

eleza print_form(form):
    """Dump the contents of a form kama HTML."""
    keys = sorted(form.keys())
    andika()
    andika("<H3>Form Contents:</H3>")
    ikiwa sio keys:
        andika("<P>No form fields.")
    andika("<DL>")
    kila key kwenye keys:
        andika("<DT>" + html.escape(key) + ":", end=' ')
        value = form[key]
        andika("<i>" + html.escape(repr(type(value))) + "</i>")
        andika("<DD>" + html.escape(repr(value)))
    andika("</DL>")
    andika()

eleza print_directory():
    """Dump the current directory kama HTML."""
    andika()
    andika("<H3>Current Working Directory:</H3>")
    jaribu:
        pwd = os.getcwd()
    tatizo OSError kama msg:
        andika("OSError:", html.escape(str(msg)))
    isipokua:
        andika(html.escape(pwd))
    andika()

eleza print_arguments():
    andika()
    andika("<H3>Command Line Arguments:</H3>")
    andika()
    andika(sys.argv)
    andika()

eleza print_environ_usage():
    """Dump a list of environment variables used by CGI kama HTML."""
    andika("""
<H3>These environment variables could have been set:</H3>
<UL>
<LI>AUTH_TYPE
<LI>CONTENT_LENGTH
<LI>CONTENT_TYPE
<LI>DATE_GMT
<LI>DATE_LOCAL
<LI>DOCUMENT_NAME
<LI>DOCUMENT_ROOT
<LI>DOCUMENT_URI
<LI>GATEWAY_INTERFACE
<LI>LAST_MODIFIED
<LI>PATH
<LI>PATH_INFO
<LI>PATH_TRANSLATED
<LI>QUERY_STRING
<LI>REMOTE_ADDR
<LI>REMOTE_HOST
<LI>REMOTE_IDENT
<LI>REMOTE_USER
<LI>REQUEST_METHOD
<LI>SCRIPT_NAME
<LI>SERVER_NAME
<LI>SERVER_PORT
<LI>SERVER_PROTOCOL
<LI>SERVER_ROOT
<LI>SERVER_SOFTWARE
</UL>
In addition, HTTP headers sent by the server may be pitaed kwenye the
environment kama well.  Here are some common variable names:
<UL>
<LI>HTTP_ACCEPT
<LI>HTTP_CONNECTION
<LI>HTTP_HOST
<LI>HTTP_PRAGMA
<LI>HTTP_REFERER
<LI>HTTP_USER_AGENT
</UL>
""")


# Utilities
# =========

eleza valid_boundary(s):
    agiza re
    ikiwa isinstance(s, bytes):
        _vb_pattern = b"^[ -~]{0,200}[!-~]$"
    isipokua:
        _vb_pattern = "^[ -~]{0,200}[!-~]$"
    rudisha re.match(_vb_pattern, s)

# Invoke mainline
# ===============

# Call test() when this file ni run kama a script (sio imported kama a module)
ikiwa __name__ == '__main__':
    test()
