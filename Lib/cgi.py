#! /usr/local/bin/python

# NOTE: the above "/usr/local/bin/python" is NOT a mistake.  It is
# intentionally NOT "/usr/bin/env python".  On many systems
# (e.g. Solaris), /usr/local/bin is not in $PATH as passed to CGI
# scripts, and /usr/local/bin is the default directory where Python is
# installed, so /usr/bin/env would be unable to find python.  Granted,
# binary installations by Linux vendors often install Python in
# /usr/bin.  So let those vendors patch cgi.py to match their choice
# of installation.

"""Support module for CGI (Common Gateway Interface) scripts.

This module defines a number of utilities for use by CGI scripts
written in Python.
"""

# History
# -------
#
# Michael McLay started this module.  Steve Majewski changed the
# interface to SvFormContentDict and FormContentDict.  The multipart
# parsing was inspired by code submitted by Andreas Paepcke.  Guido van
# Rossum rewrote, reformatted and documented the module and is currently
# responsible for its maintenance.
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

logfile = ""            # Filename to log to, ikiwa not empty
logfp = None            # File object to log to, ikiwa not None

eleza initlog(*allargs):
    """Write a log message, ikiwa there is a log file.

    Even though this function is called initlog(), you should always
    use log(); log is a variable that is set either to initlog
    (initially), to dolog (once the log file has been opened), or to
    nolog (when logging is disabled).

    The first argument is a format string; the remaining arguments (if
    any) are arguments to the % operator, so e.g.
        log("%s: %s", "a", "b")
    will write "a: b" to the log file, followed by a newline.

    If the global logfp is not None, it should be a file object to
    which log data is written.

    If the global logfp is None, the global logfile may be a string
    giving a filename to open, in append mode.  This file should be
    world writable!!!  If the file can't be opened, logging is
    silently disabled (since there is no safe place where we could
    send an error message).

    """
    global log, logfile, logfp
    ikiwa logfile and not logfp:
        try:
            logfp = open(logfile, "a")
        except OSError:
            pass
    ikiwa not logfp:
        log = nolog
    else:
        log = dolog
    log(*allargs)

eleza dolog(fmt, *args):
    """Write a log message to the log file.  See initlog() for docs."""
    logfp.write(fmt%args + "\n")

eleza nolog(*allargs):
    """Dummy function, assigned to log when logging is disabled."""
    pass

eleza closelog():
    """Close the log file."""
    global log, logfile, logfp
    logfile = ''
    ikiwa logfp:
        logfp.close()
        logfp = None
    log = initlog

log = initlog           # The current logging function


# Parsing functions
# =================

# Maximum input we will accept when REQUEST_METHOD is POST
# 0 ==> unlimited input
maxlen = 0

eleza parse(fp=None, environ=os.environ, keep_blank_values=0, strict_parsing=0):
    """Parse a query in the environment or kutoka a file (default stdin)

        Arguments, all optional:

        fp              : file pointer; default: sys.stdin.buffer

        environ         : environment dictionary; default: os.environ

        keep_blank_values: flag indicating whether blank values in
            percent-encoded forms should be treated as blank strings.
            A true value indicates that blanks should be retained as
            blank strings.  The default false value indicates that
            blank values are to be ignored and treated as ikiwa they were
            not included.

        strict_parsing: flag indicating what to do with parsing errors.
            If false (the default), errors are silently ignored.
            If true, errors raise a ValueError exception.
    """
    ikiwa fp is None:
        fp = sys.stdin

    # field keys and values (except for files) are returned as strings
    # an encoding is required to decode the bytes read kutoka self.fp
    ikiwa hasattr(fp,'encoding'):
        encoding = fp.encoding
    else:
        encoding = 'latin-1'

    # fp.read() must rudisha bytes
    ikiwa isinstance(fp, TextIOWrapper):
        fp = fp.buffer

    ikiwa not 'REQUEST_METHOD' in environ:
        environ['REQUEST_METHOD'] = 'GET'       # For testing stand-alone
    ikiwa environ['REQUEST_METHOD'] == 'POST':
        ctype, pdict = parse_header(environ['CONTENT_TYPE'])
        ikiwa ctype == 'multipart/form-data':
            rudisha parse_multipart(fp, pdict)
        elikiwa ctype == 'application/x-www-form-urlencoded':
            clength = int(environ['CONTENT_LENGTH'])
            ikiwa maxlen and clength > maxlen:
                raise ValueError('Maximum content length exceeded')
            qs = fp.read(clength).decode(encoding)
        else:
            qs = ''                     # Unknown content-type
        ikiwa 'QUERY_STRING' in environ:
            ikiwa qs: qs = qs + '&'
            qs = qs + environ['QUERY_STRING']
        elikiwa sys.argv[1:]:
            ikiwa qs: qs = qs + '&'
            qs = qs + sys.argv[1]
        environ['QUERY_STRING'] = qs    # XXX Shouldn't, really
    elikiwa 'QUERY_STRING' in environ:
        qs = environ['QUERY_STRING']
    else:
        ikiwa sys.argv[1:]:
            qs = sys.argv[1]
        else:
            qs = ""
        environ['QUERY_STRING'] = qs    # XXX Shouldn't, really
    rudisha urllib.parse.parse_qs(qs, keep_blank_values, strict_parsing,
                                 encoding=encoding)


eleza parse_multipart(fp, pdict, encoding="utf-8", errors="replace"):
    """Parse multipart input.

    Arguments:
    fp   : input file
    pdict: dictionary containing other parameters of content-type header
    encoding, errors: request encoding and error handler, passed to
        FieldStorage

    Returns a dictionary just like parse_qs(): keys are the field names, each
    value is a list of values for that field. For non-file fields, the value
    is a list of strings.
    """
    # RFC 2026, Section 5.1 : The "multipart" boundary delimiters are always
    # represented as 7bit US-ASCII.
    boundary = pdict['boundary'].decode('ascii')
    ctype = "multipart/form-data; boundary={}".format(boundary)
    headers = Message()
    headers.set_type(ctype)
    headers['Content-Length'] = pdict['CONTENT-LENGTH']
    fs = FieldStorage(fp, headers=headers, encoding=encoding, errors=errors,
        environ={'REQUEST_METHOD': 'POST'})
    rudisha {k: fs.getlist(k) for k in fs}

eleza _parseparam(s):
    while s[:1] == ';':
        s = s[1:]
        end = s.find(';')
        while end > 0 and (s.count('"', 0, end) - s.count('\\"', 0, end)) % 2:
            end = s.find(';', end + 1)
        ikiwa end < 0:
            end = len(s)
        f = s[:end]
        yield f.strip()
        s = s[end:]

eleza parse_header(line):
    """Parse a Content-type like header.

    Return the main content-type and a dictionary of options.

    """
    parts = _parseparam(';' + line)
    key = parts.__next__()
    pdict = {}
    for p in parts:
        i = p.find('=')
        ikiwa i >= 0:
            name = p[:i].strip().lower()
            value = p[i+1:].strip()
            ikiwa len(value) >= 2 and value[0] == value[-1] == '"':
                value = value[1:-1]
                value = value.replace('\\\\', '\\').replace('\\"', '"')
            pdict[name] = value
    rudisha key, pdict


# Classes for field storage
# =========================

kundi MiniFieldStorage:

    """Like FieldStorage, for use when no file uploads are possible."""

    # Dummy attributes
    filename = None
    list = None
    type = None
    file = None
    type_options = {}
    disposition = None
    disposition_options = {}
    headers = {}

    eleza __init__(self, name, value):
        """Constructor kutoka field name and value."""
        self.name = name
        self.value = value
        # self.file = StringIO(value)

    eleza __repr__(self):
        """Return printable representation."""
        rudisha "MiniFieldStorage(%r, %r)" % (self.name, self.value)


kundi FieldStorage:

    """Store a sequence of fields, reading multipart/form-data.

    This kundi provides naming, typing, files stored on disk, and
    more.  At the top level, it is accessible like a dictionary, whose
    keys are the field names.  (Note: None can occur as a field name.)
    The items are either a Python list (ikiwa there's multiple values) or
    another FieldStorage or MiniFieldStorage object.  If it's a single
    object, it has the following attributes:

    name: the field name, ikiwa specified; otherwise None

    filename: the filename, ikiwa specified; otherwise None; this is the
        client side filename, *not* the file name on which it is
        stored (that's a temporary file you don't deal with)

    value: the value as a *string*; for file uploads, this
        transparently reads the file every time you request the value
        and returns *bytes*

    file: the file(-like) object kutoka which you can read the data *as
        bytes* ; None ikiwa the data is stored a simple string

    type: the content-type, or None ikiwa not specified

    type_options: dictionary of options specified on the content-type
        line

    disposition: content-disposition, or None ikiwa not specified

    disposition_options: dictionary of corresponding options

    headers: a dictionary(-like) object (sometimes email.message.Message or a
        subkundi thereof) containing *all* headers

    The kundi is subclassable, mostly for the purpose of overriding
    the make_file() method, which is called internally to come up with
    a file open for reading and writing.  This makes it possible to
    override the default choice of storing all files in a temporary
    directory and unlinking them as soon as they have been opened.

    """
    eleza __init__(self, fp=None, headers=None, outerboundary=b'',
                 environ=os.environ, keep_blank_values=0, strict_parsing=0,
                 limit=None, encoding='utf-8', errors='replace',
                 max_num_fields=None):
        """Constructor.  Read multipart/* until last part.

        Arguments, all optional:

        fp              : file pointer; default: sys.stdin.buffer
            (not used when the request method is GET)
            Can be :
            1. a TextIOWrapper object
            2. an object whose read() and readline() methods rudisha bytes

        headers         : header dictionary-like object; default:
            taken kutoka environ as per CGI spec

        outerboundary   : terminating multipart boundary
            (for internal use only)

        environ         : environment dictionary; default: os.environ

        keep_blank_values: flag indicating whether blank values in
            percent-encoded forms should be treated as blank strings.
            A true value indicates that blanks should be retained as
            blank strings.  The default false value indicates that
            blank values are to be ignored and treated as ikiwa they were
            not included.

        strict_parsing: flag indicating what to do with parsing errors.
            If false (the default), errors are silently ignored.
            If true, errors raise a ValueError exception.

        limit : used internally to read parts of multipart/form-data forms,
            to exit kutoka the reading loop when reached. It is the difference
            between the form content-length and the number of bytes already
            read

        encoding, errors : the encoding and error handler used to decode the
            binary stream to strings. Must be the same as the charset defined
            for the page sending the form (content-type : meta http-equiv or
            header)

        max_num_fields: int. If set, then __init__ throws a ValueError
            ikiwa there are more than n fields read by parse_qsl().

        """
        method = 'GET'
        self.keep_blank_values = keep_blank_values
        self.strict_parsing = strict_parsing
        self.max_num_fields = max_num_fields
        ikiwa 'REQUEST_METHOD' in environ:
            method = environ['REQUEST_METHOD'].upper()
        self.qs_on_post = None
        ikiwa method == 'GET' or method == 'HEAD':
            ikiwa 'QUERY_STRING' in environ:
                qs = environ['QUERY_STRING']
            elikiwa sys.argv[1:]:
                qs = sys.argv[1]
            else:
                qs = ""
            qs = qs.encode(locale.getpreferredencoding(), 'surrogateescape')
            fp = BytesIO(qs)
            ikiwa headers is None:
                headers = {'content-type':
                           "application/x-www-form-urlencoded"}
        ikiwa headers is None:
            headers = {}
            ikiwa method == 'POST':
                # Set default content-type for POST to what's traditional
                headers['content-type'] = "application/x-www-form-urlencoded"
            ikiwa 'CONTENT_TYPE' in environ:
                headers['content-type'] = environ['CONTENT_TYPE']
            ikiwa 'QUERY_STRING' in environ:
                self.qs_on_post = environ['QUERY_STRING']
            ikiwa 'CONTENT_LENGTH' in environ:
                headers['content-length'] = environ['CONTENT_LENGTH']
        else:
            ikiwa not (isinstance(headers, (Mapping, Message))):
                raise TypeError("headers must be mapping or an instance of "
                                "email.message.Message")
        self.headers = headers
        ikiwa fp is None:
            self.fp = sys.stdin.buffer
        # self.fp.read() must rudisha bytes
        elikiwa isinstance(fp, TextIOWrapper):
            self.fp = fp.buffer
        else:
            ikiwa not (hasattr(fp, 'read') and hasattr(fp, 'readline')):
                raise TypeError("fp must be file pointer")
            self.fp = fp

        self.encoding = encoding
        self.errors = errors

        ikiwa not isinstance(outerboundary, bytes):
            raise TypeError('outerboundary must be bytes, not %s'
                            % type(outerboundary).__name__)
        self.outerboundary = outerboundary

        self.bytes_read = 0
        self.limit = limit

        # Process content-disposition header
        cdisp, pdict = "", {}
        ikiwa 'content-disposition' in self.headers:
            cdisp, pdict = parse_header(self.headers['content-disposition'])
        self.disposition = cdisp
        self.disposition_options = pdict
        self.name = None
        ikiwa 'name' in pdict:
            self.name = pdict['name']
        self.filename = None
        ikiwa 'filename' in pdict:
            self.filename = pdict['filename']
        self._binary_file = self.filename is not None

        # Process content-type header
        #
        # Honor any existing content-type header.  But ikiwa there is no
        # content-type header, use some sensible defaults.  Assume
        # outerboundary is "" at the outer level, but something non-false
        # inside a multi-part.  The default for an inner part is text/plain,
        # but for an outer part it should be urlencoded.  This should catch
        # bogus clients which erroneously forget to include a content-type
        # header.
        #
        # See below for what we do ikiwa there does exist a content-type header,
        # but it happens to be something we don't understand.
        ikiwa 'content-type' in self.headers:
            ctype, pdict = parse_header(self.headers['content-type'])
        elikiwa self.outerboundary or method != 'POST':
            ctype, pdict = "text/plain", {}
        else:
            ctype, pdict = 'application/x-www-form-urlencoded', {}
        self.type = ctype
        self.type_options = pdict
        ikiwa 'boundary' in pdict:
            self.innerboundary = pdict['boundary'].encode(self.encoding,
                                                          self.errors)
        else:
            self.innerboundary = b""

        clen = -1
        ikiwa 'content-length' in self.headers:
            try:
                clen = int(self.headers['content-length'])
            except ValueError:
                pass
            ikiwa maxlen and clen > maxlen:
                raise ValueError('Maximum content length exceeded')
        self.length = clen
        ikiwa self.limit is None and clen >= 0:
            self.limit = clen

        self.list = self.file = None
        self.done = 0
        ikiwa ctype == 'application/x-www-form-urlencoded':
            self.read_urlencoded()
        elikiwa ctype[:10] == 'multipart/':
            self.read_multi(environ, keep_blank_values, strict_parsing)
        else:
            self.read_single()

    eleza __del__(self):
        try:
            self.file.close()
        except AttributeError:
            pass

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
            raise AttributeError(name)
        ikiwa self.file:
            self.file.seek(0)
            value = self.file.read()
            self.file.seek(0)
        elikiwa self.list is not None:
            value = self.list
        else:
            value = None
        rudisha value

    eleza __getitem__(self, key):
        """Dictionary style indexing."""
        ikiwa self.list is None:
            raise TypeError("not indexable")
        found = []
        for item in self.list:
            ikiwa item.name == key: found.append(item)
        ikiwa not found:
            raise KeyError(key)
        ikiwa len(found) == 1:
            rudisha found[0]
        else:
            rudisha found

    eleza getvalue(self, key, default=None):
        """Dictionary style get() method, including 'value' lookup."""
        ikiwa key in self:
            value = self[key]
            ikiwa isinstance(value, list):
                rudisha [x.value for x in value]
            else:
                rudisha value.value
        else:
            rudisha default

    eleza getfirst(self, key, default=None):
        """ Return the first value received."""
        ikiwa key in self:
            value = self[key]
            ikiwa isinstance(value, list):
                rudisha value[0].value
            else:
                rudisha value.value
        else:
            rudisha default

    eleza getlist(self, key):
        """ Return list of received values."""
        ikiwa key in self:
            value = self[key]
            ikiwa isinstance(value, list):
                rudisha [x.value for x in value]
            else:
                rudisha [value.value]
        else:
            rudisha []

    eleza keys(self):
        """Dictionary style keys() method."""
        ikiwa self.list is None:
            raise TypeError("not indexable")
        rudisha list(set(item.name for item in self.list))

    eleza __contains__(self, key):
        """Dictionary style __contains__ method."""
        ikiwa self.list is None:
            raise TypeError("not indexable")
        rudisha any(item.name == key for item in self.list)

    eleza __len__(self):
        """Dictionary style len(x) support."""
        rudisha len(self.keys())

    eleza __bool__(self):
        ikiwa self.list is None:
            raise TypeError("Cannot be converted to bool.")
        rudisha bool(self.list)

    eleza read_urlencoded(self):
        """Internal: read data in query string format."""
        qs = self.fp.read(self.length)
        ikiwa not isinstance(qs, bytes):
            raise ValueError("%s should rudisha bytes, got %s" \
                             % (self.fp, type(qs).__name__))
        qs = qs.decode(self.encoding, self.errors)
        ikiwa self.qs_on_post:
            qs += '&' + self.qs_on_post
        query = urllib.parse.parse_qsl(
            qs, self.keep_blank_values, self.strict_parsing,
            encoding=self.encoding, errors=self.errors,
            max_num_fields=self.max_num_fields)
        self.list = [MiniFieldStorage(key, value) for key, value in query]
        self.skip_lines()

    FieldStorageClass = None

    eleza read_multi(self, environ, keep_blank_values, strict_parsing):
        """Internal: read a part that is itself multipart."""
        ib = self.innerboundary
        ikiwa not valid_boundary(ib):
            raise ValueError('Invalid boundary in multipart form: %r' % (ib,))
        self.list = []
        ikiwa self.qs_on_post:
            query = urllib.parse.parse_qsl(
                self.qs_on_post, self.keep_blank_values, self.strict_parsing,
                encoding=self.encoding, errors=self.errors,
                max_num_fields=self.max_num_fields)
            self.list.extend(MiniFieldStorage(key, value) for key, value in query)

        klass = self.FieldStorageClass or self.__class__
        first_line = self.fp.readline() # bytes
        ikiwa not isinstance(first_line, bytes):
            raise ValueError("%s should rudisha bytes, got %s" \
                             % (self.fp, type(first_line).__name__))
        self.bytes_read += len(first_line)

        # Ensure that we consume the file until we've hit our inner boundary
        while (first_line.strip() != (b"--" + self.innerboundary) and
                first_line):
            first_line = self.fp.readline()
            self.bytes_read += len(first_line)

        # Propagate max_num_fields into the sub kundi appropriately
        max_num_fields = self.max_num_fields
        ikiwa max_num_fields is not None:
            max_num_fields -= len(self.list)

        while True:
            parser = FeedParser()
            hdr_text = b""
            while True:
                data = self.fp.readline()
                hdr_text += data
                ikiwa not data.strip():
                    break
            ikiwa not hdr_text:
                break
            # parser takes strings, not bytes
            self.bytes_read += len(hdr_text)
            parser.feed(hdr_text.decode(self.encoding, self.errors))
            headers = parser.close()

            # Some clients add Content-Length for part headers, ignore them
            ikiwa 'content-length' in headers:
                del headers['content-length']

            limit = None ikiwa self.limit is None \
                else self.limit - self.bytes_read
            part = klass(self.fp, headers, ib, environ, keep_blank_values,
                         strict_parsing, limit,
                         self.encoding, self.errors, max_num_fields)

            ikiwa max_num_fields is not None:
                max_num_fields -= 1
                ikiwa part.list:
                    max_num_fields -= len(part.list)
                ikiwa max_num_fields < 0:
                    raise ValueError('Max number of fields exceeded')

            self.bytes_read += part.bytes_read
            self.list.append(part)
            ikiwa part.done or self.bytes_read >= self.length > 0:
                break
        self.skip_lines()

    eleza read_single(self):
        """Internal: read an atomic part."""
        ikiwa self.length >= 0:
            self.read_binary()
            self.skip_lines()
        else:
            self.read_lines()
        self.file.seek(0)

    bufsize = 8*1024            # I/O buffering size for copy to file

    eleza read_binary(self):
        """Internal: read binary data."""
        self.file = self.make_file()
        todo = self.length
        ikiwa todo >= 0:
            while todo > 0:
                data = self.fp.read(min(todo, self.bufsize)) # bytes
                ikiwa not isinstance(data, bytes):
                    raise ValueError("%s should rudisha bytes, got %s"
                                     % (self.fp, type(data).__name__))
                self.bytes_read += len(data)
                ikiwa not data:
                    self.done = -1
                    break
                self.file.write(data)
                todo = todo - len(data)

    eleza read_lines(self):
        """Internal: read lines until EOF or outerboundary."""
        ikiwa self._binary_file:
            self.file = self.__file = BytesIO() # store data as bytes for files
        else:
            self.file = self.__file = StringIO() # as strings for other fields
        ikiwa self.outerboundary:
            self.read_lines_to_outerboundary()
        else:
            self.read_lines_to_eof()

    eleza __write(self, line):
        """line is always bytes, not string"""
        ikiwa self.__file is not None:
            ikiwa self.__file.tell() + len(line) > 1000:
                self.file = self.make_file()
                data = self.__file.getvalue()
                self.file.write(data)
                self.__file = None
        ikiwa self._binary_file:
            # keep bytes
            self.file.write(line)
        else:
            # decode to string
            self.file.write(line.decode(self.encoding, self.errors))

    eleza read_lines_to_eof(self):
        """Internal: read lines until EOF."""
        while 1:
            line = self.fp.readline(1<<16) # bytes
            self.bytes_read += len(line)
            ikiwa not line:
                self.done = -1
                break
            self.__write(line)

    eleza read_lines_to_outerboundary(self):
        """Internal: read lines until outerboundary.
        Data is read as bytes: boundaries and line ends must be converted
        to bytes for comparisons.
        """
        next_boundary = b"--" + self.outerboundary
        last_boundary = next_boundary + b"--"
        delim = b""
        last_line_lfend = True
        _read = 0
        while 1:
            ikiwa self.limit is not None and _read >= self.limit:
                break
            line = self.fp.readline(1<<16) # bytes
            self.bytes_read += len(line)
            _read += len(line)
            ikiwa not line:
                self.done = -1
                break
            ikiwa delim == b"\r":
                line = delim + line
                delim = b""
            ikiwa line.startswith(b"--") and last_line_lfend:
                strippedline = line.rstrip()
                ikiwa strippedline == next_boundary:
                    break
                ikiwa strippedline == last_boundary:
                    self.done = 1
                    break
            odelim = delim
            ikiwa line.endswith(b"\r\n"):
                delim = b"\r\n"
                line = line[:-2]
                last_line_lfend = True
            elikiwa line.endswith(b"\n"):
                delim = b"\n"
                line = line[:-1]
                last_line_lfend = True
            elikiwa line.endswith(b"\r"):
                # We may interrupt \r\n sequences ikiwa they span the 2**16
                # byte boundary
                delim = b"\r"
                line = line[:-1]
                last_line_lfend = False
            else:
                delim = b""
                last_line_lfend = False
            self.__write(odelim + line)

    eleza skip_lines(self):
        """Internal: skip lines until outer boundary ikiwa defined."""
        ikiwa not self.outerboundary or self.done:
            return
        next_boundary = b"--" + self.outerboundary
        last_boundary = next_boundary + b"--"
        last_line_lfend = True
        while True:
            line = self.fp.readline(1<<16)
            self.bytes_read += len(line)
            ikiwa not line:
                self.done = -1
                break
            ikiwa line.endswith(b"--") and last_line_lfend:
                strippedline = line.strip()
                ikiwa strippedline == next_boundary:
                    break
                ikiwa strippedline == last_boundary:
                    self.done = 1
                    break
            last_line_lfend = line.endswith(b'\n')

    eleza make_file(self):
        """Overridable: rudisha a readable & writable file.

        The file will be used as follows:
        - data is written to it
        - seek(0)
        - data is read kutoka it

        The file is opened in binary mode for files, in text mode
        for other fields

        This version opens a temporary file for reading and writing,
        and immediately deletes (unlinks) it.  The trick (on Unix!) is
        that the file can still be used, but it can't be opened by
        another process, and it will automatically be deleted when it
        is closed or when the current process terminates.

        If you want a more permanent file, you derive a kundi which
        overrides this method.  If you want a visible temporary file
        that is nevertheless automatically deleted when the script
        terminates, try defining a __del__ method in a derived class
        which unlinks the temporary files you have created.

        """
        ikiwa self._binary_file:
            rudisha tempfile.TemporaryFile("wb+")
        else:
            rudisha tempfile.TemporaryFile("w+",
                encoding=self.encoding, newline = '\n')


# Test/debug code
# ===============

eleza test(environ=os.environ):
    """Robust test CGI script, usable as main program.

    Write minimal HTTP headers and dump all information provided to
    the script in HTML form.

    """
    andika("Content-type: text/html")
    andika()
    sys.stderr = sys.stdout
    try:
        form = FieldStorage()   # Replace with other classes to test those
        print_directory()
        print_arguments()
        print_form(form)
        print_environ(environ)
        print_environ_usage()
        eleza f():
            exec("testing print_exception() -- <I>italics?</I>")
        eleza g(f=f):
            f()
        andika("<H3>What follows is a test, not an actual exception:</H3>")
        g()
    except:
        print_exception()

    andika("<H1>Second try with a small maxlen...</H1>")

    global maxlen
    maxlen = 50
    try:
        form = FieldStorage()   # Replace with other classes to test those
        print_directory()
        print_arguments()
        print_form(form)
        print_environ(environ)
    except:
        print_exception()

eleza print_exception(type=None, value=None, tb=None, limit=None):
    ikiwa type is None:
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
    del tb

eleza print_environ(environ=os.environ):
    """Dump the shell environment as HTML."""
    keys = sorted(environ.keys())
    andika()
    andika("<H3>Shell Environment:</H3>")
    andika("<DL>")
    for key in keys:
        andika("<DT>", html.escape(key), "<DD>", html.escape(environ[key]))
    andika("</DL>")
    andika()

eleza print_form(form):
    """Dump the contents of a form as HTML."""
    keys = sorted(form.keys())
    andika()
    andika("<H3>Form Contents:</H3>")
    ikiwa not keys:
        andika("<P>No form fields.")
    andika("<DL>")
    for key in keys:
        andika("<DT>" + html.escape(key) + ":", end=' ')
        value = form[key]
        andika("<i>" + html.escape(repr(type(value))) + "</i>")
        andika("<DD>" + html.escape(repr(value)))
    andika("</DL>")
    andika()

eleza print_directory():
    """Dump the current directory as HTML."""
    andika()
    andika("<H3>Current Working Directory:</H3>")
    try:
        pwd = os.getcwd()
    except OSError as msg:
        andika("OSError:", html.escape(str(msg)))
    else:
        andika(html.escape(pwd))
    andika()

eleza print_arguments():
    andika()
    andika("<H3>Command Line Arguments:</H3>")
    andika()
    andika(sys.argv)
    andika()

eleza print_environ_usage():
    """Dump a list of environment variables used by CGI as HTML."""
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
In addition, HTTP headers sent by the server may be passed in the
environment as well.  Here are some common variable names:
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
    else:
        _vb_pattern = "^[ -~]{0,200}[!-~]$"
    rudisha re.match(_vb_pattern, s)

# Invoke mainline
# ===============

# Call test() when this file is run as a script (not imported as a module)
ikiwa __name__ == '__main__':
    test()
