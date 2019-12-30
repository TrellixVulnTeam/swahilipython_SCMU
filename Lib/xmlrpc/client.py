#
# XML-RPC CLIENT LIBRARY
# $Id$
#
# an XML-RPC client interface kila Python.
#
# the marshalling na response parser code can also be used to
# implement XML-RPC servers.
#
# Notes:
# this version ni designed to work ukijumuisha Python 2.1 ama newer.
#
# History:
# 1999-01-14 fl  Created
# 1999-01-15 fl  Changed dateTime to use localtime
# 1999-01-16 fl  Added Binary/base64 element, default to RPC2 service
# 1999-01-19 fl  Fixed array data element (kutoka Skip Montanaro)
# 1999-01-21 fl  Fixed dateTime constructor, etc.
# 1999-02-02 fl  Added fault handling, handle empty sequences, etc.
# 1999-02-10 fl  Fixed problem ukijumuisha empty responses (kutoka Skip Montanaro)
# 1999-06-20 fl  Speed improvements, pluggable parsers/transports (0.9.8)
# 2000-11-28 fl  Changed boolean to check the truth value of its argument
# 2001-02-24 fl  Added encoding/Unicode/SafeTransport patches
# 2001-02-26 fl  Added compare support to wrappers (0.9.9/1.0b1)
# 2001-03-28 fl  Make sure response tuple ni a singleton
# 2001-03-29 fl  Don't require empty params element (kutoka Nicholas Riley)
# 2001-06-10 fl  Folded kwenye _xmlrpclib accelerator support (1.0b2)
# 2001-08-20 fl  Base xmlrpclib.Error on built-in Exception (kutoka Paul Prescod)
# 2001-09-03 fl  Allow Transport subkundi to override getparser
# 2001-09-10 fl  Lazy agiza of urllib, cgi, xmllib (20x agiza speedup)
# 2001-10-01 fl  Remove containers kutoka memo cache when done ukijumuisha them
# 2001-10-01 fl  Use faster escape method (80% dumps speedup)
# 2001-10-02 fl  More dumps microtuning
# 2001-10-04 fl  Make sure agiza expat gets a parser (kutoka Guido van Rossum)
# 2001-10-10 sm  Allow long ints to be passed as ints ikiwa they don't overflow
# 2001-10-17 sm  Test kila int na long overflow (allows use on 64-bit systems)
# 2001-11-12 fl  Use repr() to marshal doubles (kutoka Paul Felix)
# 2002-03-17 fl  Avoid buffered read when possible (kutoka James Rucker)
# 2002-04-07 fl  Added pythondoc comments
# 2002-04-16 fl  Added __str__ methods to datetime/binary wrappers
# 2002-05-15 fl  Added error constants (kutoka Andrew Kuchling)
# 2002-06-27 fl  Merged ukijumuisha Python CVS version
# 2002-10-22 fl  Added basic authentication (based on code kutoka Phillip Eby)
# 2003-01-22 sm  Add support kila the bool type
# 2003-02-27 gvr Remove apply calls
# 2003-04-24 sm  Use cStringIO ikiwa available
# 2003-04-25 ak  Add support kila nil
# 2003-06-15 gn  Add support kila time.struct_time
# 2003-07-12 gp  Correct marshalling of Faults
# 2003-10-31 mvl Add multicall support
# 2004-08-20 mvl Bump minimum supported Python version to 2.1
# 2014-12-02 ch/doko  Add workaround kila gzip bomb vulnerability
#
# Copyright (c) 1999-2002 by Secret Labs AB.
# Copyright (c) 1999-2002 by Fredrik Lundh.
#
# info@pythonware.com
# http://www.pythonware.com
#
# --------------------------------------------------------------------
# The XML-RPC client interface is
#
# Copyright (c) 1999-2002 by Secret Labs AB
# Copyright (c) 1999-2002 by Fredrik Lundh
#
# By obtaining, using, and/or copying this software and/or its
# associated documentation, you agree that you have read, understood,
# na will comply ukijumuisha the following terms na conditions:
#
# Permission to use, copy, modify, na distribute this software and
# its associated documentation kila any purpose na without fee is
# hereby granted, provided that the above copyright notice appears in
# all copies, na that both that copyright notice na this permission
# notice appear kwenye supporting documentation, na that the name of
# Secret Labs AB ama the author sio be used kwenye advertising ama publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANT-
# ABILITY AND FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR
# BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
# --------------------------------------------------------------------

"""
An XML-RPC client interface kila Python.

The marshalling na response parser code can also be used to
implement XML-RPC servers.

Exported exceptions:

  Error          Base kundi kila client errors
  ProtocolError  Indicates an HTTP protocol error
  ResponseError  Indicates a broken response package
  Fault          Indicates an XML-RPC fault package

Exported classes:

  ServerProxy    Represents a logical connection to an XML-RPC server

  MultiCall      Executor of boxcared xmlrpc requests
  DateTime       dateTime wrapper kila an ISO 8601 string ama time tuple or
                 localtime integer value to generate a "dateTime.iso8601"
                 XML-RPC value
  Binary         binary data wrapper

  Marshaller     Generate an XML-RPC params chunk kutoka a Python data structure
  Unmarshaller   Unmarshal an XML-RPC response kutoka incoming XML event message
  Transport      Handles an HTTP transaction to an XML-RPC server
  SafeTransport  Handles an HTTPS transaction to an XML-RPC server

Exported constants:

  (none)

Exported functions:

  getparser      Create instance of the fastest available parser & attach
                 to an unmarshalling object
  dumps          Convert an argument tuple ama a Fault instance to an XML-RPC
                 request (or response, ikiwa the methodresponse option ni used).
  loads          Convert an XML-RPC packet to unmarshalled data plus a method
                 name (Tupu ikiwa sio present).
"""

agiza base64
agiza sys
agiza time
kutoka datetime agiza datetime
kutoka decimal agiza Decimal
agiza http.client
agiza urllib.parse
kutoka xml.parsers agiza expat
agiza errno
kutoka io agiza BytesIO
jaribu:
    agiza gzip
except ImportError:
    gzip = Tupu #python can be built without zlib/gzip support

# --------------------------------------------------------------------
# Internal stuff

eleza escape(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    rudisha s.replace(">", "&gt;",)

# used kwenye User-Agent header sent
__version__ = '%d.%d' % sys.version_info[:2]

# xmlrpc integer limits
MAXINT =  2**31-1
MININT = -2**31

# --------------------------------------------------------------------
# Error constants (kutoka Dan Libby's specification at
# http://xmlrpc-epi.sourceforge.net/specs/rfc.fault_codes.php)

# Ranges of errors
PARSE_ERROR       = -32700
SERVER_ERROR      = -32600
APPLICATION_ERROR = -32500
SYSTEM_ERROR      = -32400
TRANSPORT_ERROR   = -32300

# Specific errors
NOT_WELLFORMED_ERROR  = -32700
UNSUPPORTED_ENCODING  = -32701
INVALID_ENCODING_CHAR = -32702
INVALID_XMLRPC        = -32600
METHOD_NOT_FOUND      = -32601
INVALID_METHOD_PARAMS = -32602
INTERNAL_ERROR        = -32603

# --------------------------------------------------------------------
# Exceptions

##
# Base kundi kila all kinds of client-side errors.

kundi Error(Exception):
    """Base kundi kila client errors."""
    __str__ = object.__str__

##
# Indicates an HTTP-level protocol error.  This ni raised by the HTTP
# transport layer, ikiwa the server returns an error code other than 200
# (OK).
#
# @param url The target URL.
# @param errcode The HTTP error code.
# @param errmsg The HTTP error message.
# @param headers The HTTP header dictionary.

kundi ProtocolError(Error):
    """Indicates an HTTP protocol error."""
    eleza __init__(self, url, errcode, errmsg, headers):
        Error.__init__(self)
        self.url = url
        self.errcode = errcode
        self.errmsg = errmsg
        self.headers = headers
    eleza __repr__(self):
        rudisha (
            "<%s kila %s: %s %s>" %
            (self.__class__.__name__, self.url, self.errcode, self.errmsg)
            )

##
# Indicates a broken XML-RPC response package.  This exception is
# raised by the unmarshalling layer, ikiwa the XML-RPC response is
# malformed.

kundi ResponseError(Error):
    """Indicates a broken response package."""
    pass

##
# Indicates an XML-RPC fault response package.  This exception is
# raised by the unmarshalling layer, ikiwa the XML-RPC response contains
# a fault string.  This exception can also be used as a class, to
# generate a fault XML-RPC message.
#
# @param faultCode The XML-RPC fault code.
# @param faultString The XML-RPC fault string.

kundi Fault(Error):
    """Indicates an XML-RPC fault package."""
    eleza __init__(self, faultCode, faultString, **extra):
        Error.__init__(self)
        self.faultCode = faultCode
        self.faultString = faultString
    eleza __repr__(self):
        rudisha "<%s %s: %r>" % (self.__class__.__name__,
                                self.faultCode, self.faultString)

# --------------------------------------------------------------------
# Special values

##
# Backwards compatibility

boolean = Boolean = bool

##
# Wrapper kila XML-RPC DateTime values.  This converts a time value to
# the format used by XML-RPC.
# <p>
# The value can be given as a datetime object, as a string kwenye the
# format "yyyymmddThh:mm:ss", as a 9-item time tuple (as returned by
# time.localtime()), ama an integer value (as returned by time.time()).
# The wrapper uses time.localtime() to convert an integer to a time
# tuple.
#
# @param value The time, given as a datetime object, an ISO 8601 string,
#              a time tuple, ama an integer time value.


# Issue #13305: different format codes across platforms
_day0 = datetime(1, 1, 1)
ikiwa _day0.strftime('%Y') == '0001':      # Mac OS X
    eleza _iso8601_format(value):
        rudisha value.strftime("%Y%m%dT%H:%M:%S")
elikiwa _day0.strftime('%4Y') == '0001':   # Linux
    eleza _iso8601_format(value):
        rudisha value.strftime("%4Y%m%dT%H:%M:%S")
isipokua:
    eleza _iso8601_format(value):
        rudisha value.strftime("%Y%m%dT%H:%M:%S").zfill(17)
toa _day0


eleza _strftime(value):
    ikiwa isinstance(value, datetime):
        rudisha _iso8601_format(value)

    ikiwa sio isinstance(value, (tuple, time.struct_time)):
        ikiwa value == 0:
            value = time.time()
        value = time.localtime(value)

    rudisha "%04d%02d%02dT%02d:%02d:%02d" % value[:6]

kundi DateTime:
    """DateTime wrapper kila an ISO 8601 string ama time tuple or
    localtime integer value to generate 'dateTime.iso8601' XML-RPC
    value.
    """

    eleza __init__(self, value=0):
        ikiwa isinstance(value, str):
            self.value = value
        isipokua:
            self.value = _strftime(value)

    eleza make_comparable(self, other):
        ikiwa isinstance(other, DateTime):
            s = self.value
            o = other.value
        elikiwa isinstance(other, datetime):
            s = self.value
            o = _iso8601_format(other)
        elikiwa isinstance(other, str):
            s = self.value
            o = other
        elikiwa hasattr(other, "timetuple"):
            s = self.timetuple()
            o = other.timetuple()
        isipokua:
            otype = (hasattr(other, "__class__")
                     na other.__class__.__name__
                     ama type(other))
             ashiria TypeError("Can't compare %s na %s" %
                            (self.__class__.__name__, otype))
        rudisha s, o

    eleza __lt__(self, other):
        s, o = self.make_comparable(other)
        rudisha s < o

    eleza __le__(self, other):
        s, o = self.make_comparable(other)
        rudisha s <= o

    eleza __gt__(self, other):
        s, o = self.make_comparable(other)
        rudisha s > o

    eleza __ge__(self, other):
        s, o = self.make_comparable(other)
        rudisha s >= o

    eleza __eq__(self, other):
        s, o = self.make_comparable(other)
        rudisha s == o

    eleza timetuple(self):
        rudisha time.strptime(self.value, "%Y%m%dT%H:%M:%S")

    ##
    # Get date/time value.
    #
    # @rudisha Date/time value, as an ISO 8601 string.

    eleza __str__(self):
        rudisha self.value

    eleza __repr__(self):
        rudisha "<%s %r at %#x>" % (self.__class__.__name__, self.value, id(self))

    eleza decode(self, data):
        self.value = str(data).strip()

    eleza encode(self, out):
        out.write("<value><dateTime.iso8601>")
        out.write(self.value)
        out.write("</dateTime.iso8601></value>\n")

eleza _datetime(data):
    # decode xml element contents into a DateTime structure.
    value = DateTime()
    value.decode(data)
    rudisha value

eleza _datetime_type(data):
    rudisha datetime.strptime(data, "%Y%m%dT%H:%M:%S")

##
# Wrapper kila binary data.  This can be used to transport any kind
# of binary data over XML-RPC, using BASE64 encoding.
#
# @param data An 8-bit string containing arbitrary data.

kundi Binary:
    """Wrapper kila binary data."""

    eleza __init__(self, data=Tupu):
        ikiwa data ni Tupu:
            data = b""
        isipokua:
            ikiwa sio isinstance(data, (bytes, bytearray)):
                 ashiria TypeError("expected bytes ama bytearray, sio %s" %
                                data.__class__.__name__)
            data = bytes(data)  # Make a copy of the bytes!
        self.data = data

    ##
    # Get buffer contents.
    #
    # @rudisha Buffer contents, as an 8-bit string.

    eleza __str__(self):
        rudisha str(self.data, "latin-1")  # XXX encoding?!

    eleza __eq__(self, other):
        ikiwa isinstance(other, Binary):
            other = other.data
        rudisha self.data == other

    eleza decode(self, data):
        self.data = base64.decodebytes(data)

    eleza encode(self, out):
        out.write("<value><base64>\n")
        encoded = base64.encodebytes(self.data)
        out.write(encoded.decode('ascii'))
        out.write("</base64></value>\n")

eleza _binary(data):
    # decode xml element contents into a Binary structure
    value = Binary()
    value.decode(data)
    rudisha value

WRAPPERS = (DateTime, Binary)

# --------------------------------------------------------------------
# XML parsers

kundi ExpatParser:
    # fast expat parser kila Python 2.0 na later.
    eleza __init__(self, target):
        self._parser = parser = expat.ParserCreate(Tupu, Tupu)
        self._target = target
        parser.StartElementHandler = target.start
        parser.EndElementHandler = target.end
        parser.CharacterDataHandler = target.data
        encoding = Tupu
        target.xml(encoding, Tupu)

    eleza feed(self, data):
        self._parser.Parse(data, 0)

    eleza close(self):
        jaribu:
            parser = self._parser
        except AttributeError:
            pass
        isipokua:
            toa self._target, self._parser # get rid of circular references
            parser.Parse(b"", Kweli) # end of data

# --------------------------------------------------------------------
# XML-RPC marshalling na unmarshalling code

##
# XML-RPC marshaller.
#
# @param encoding Default encoding kila 8-bit strings.  The default
#     value ni Tupu (interpreted as UTF-8).
# @see dumps

kundi Marshaller:
    """Generate an XML-RPC params chunk kutoka a Python data structure.

    Create a Marshaller instance kila each set of parameters, na use
    the "dumps" method to convert your data (represented as a tuple)
    to an XML-RPC params chunk.  To write a fault response, pass a
    Fault instance instead.  You may prefer to use the "dumps" module
    function kila this purpose.
    """

    # by the way, ikiwa you don't understand what's going on kwenye here,
    # that's perfectly ok.

    eleza __init__(self, encoding=Tupu, allow_none=Uongo):
        self.memo = {}
        self.data = Tupu
        self.encoding = encoding
        self.allow_none = allow_none

    dispatch = {}

    eleza dumps(self, values):
        out = []
        write = out.append
        dump = self.__dump
        ikiwa isinstance(values, Fault):
            # fault instance
            write("<fault>\n")
            dump({'faultCode': values.faultCode,
                  'faultString': values.faultString},
                 write)
            write("</fault>\n")
        isipokua:
            # parameter block
            # FIXME: the xml-rpc specification allows us to leave out
            # the entire <params> block ikiwa there are no parameters.
            # however, changing this may koma older code (including
            # old versions of xmlrpclib.py), so this ni better left as
            # ni kila now.  See @XMLRPC3 kila more information. /F
            write("<params>\n")
            kila v kwenye values:
                write("<param>\n")
                dump(v, write)
                write("</param>\n")
            write("</params>\n")
        result = "".join(out)
        rudisha result

    eleza __dump(self, value, write):
        jaribu:
            f = self.dispatch[type(value)]
        except KeyError:
            # check ikiwa this object can be marshalled as a structure
            ikiwa sio hasattr(value, '__dict__'):
                 ashiria TypeError("cannot marshal %s objects" % type(value))
            # check ikiwa this kundi ni a sub-kundi of a basic type,
            # because we don't know how to marshal these types
            # (e.g. a string sub-class)
            kila type_ kwenye type(value).__mro__:
                ikiwa type_ kwenye self.dispatch.keys():
                     ashiria TypeError("cannot marshal %s objects" % type(value))
            # XXX(twouters): using "_arbitrary_instance" as key as a quick-fix
            # kila the p3yk merge, this should probably be fixed more neatly.
            f = self.dispatch["_arbitrary_instance"]
        f(self, value, write)

    eleza dump_nil (self, value, write):
        ikiwa sio self.allow_none:
             ashiria TypeError("cannot marshal Tupu unless allow_none ni enabled")
        write("<value><nil/></value>")
    dispatch[type(Tupu)] = dump_nil

    eleza dump_bool(self, value, write):
        write("<value><boolean>")
        write(value na "1" ama "0")
        write("</boolean></value>\n")
    dispatch[bool] = dump_bool

    eleza dump_long(self, value, write):
        ikiwa value > MAXINT ama value < MININT:
             ashiria OverflowError("int exceeds XML-RPC limits")
        write("<value><int>")
        write(str(int(value)))
        write("</int></value>\n")
    dispatch[int] = dump_long

    # backward compatible
    dump_int = dump_long

    eleza dump_double(self, value, write):
        write("<value><double>")
        write(repr(value))
        write("</double></value>\n")
    dispatch[float] = dump_double

    eleza dump_unicode(self, value, write, escape=escape):
        write("<value><string>")
        write(escape(value))
        write("</string></value>\n")
    dispatch[str] = dump_unicode

    eleza dump_bytes(self, value, write):
        write("<value><base64>\n")
        encoded = base64.encodebytes(value)
        write(encoded.decode('ascii'))
        write("</base64></value>\n")
    dispatch[bytes] = dump_bytes
    dispatch[bytearray] = dump_bytes

    eleza dump_array(self, value, write):
        i = id(value)
        ikiwa i kwenye self.memo:
             ashiria TypeError("cannot marshal recursive sequences")
        self.memo[i] = Tupu
        dump = self.__dump
        write("<value><array><data>\n")
        kila v kwenye value:
            dump(v, write)
        write("</data></array></value>\n")
        toa self.memo[i]
    dispatch[tuple] = dump_array
    dispatch[list] = dump_array

    eleza dump_struct(self, value, write, escape=escape):
        i = id(value)
        ikiwa i kwenye self.memo:
             ashiria TypeError("cannot marshal recursive dictionaries")
        self.memo[i] = Tupu
        dump = self.__dump
        write("<value><struct>\n")
        kila k, v kwenye value.items():
            write("<member>\n")
            ikiwa sio isinstance(k, str):
                 ashiria TypeError("dictionary key must be string")
            write("<name>%s</name>\n" % escape(k))
            dump(v, write)
            write("</member>\n")
        write("</struct></value>\n")
        toa self.memo[i]
    dispatch[dict] = dump_struct

    eleza dump_datetime(self, value, write):
        write("<value><dateTime.iso8601>")
        write(_strftime(value))
        write("</dateTime.iso8601></value>\n")
    dispatch[datetime] = dump_datetime

    eleza dump_instance(self, value, write):
        # check kila special wrappers
        ikiwa value.__class__ kwenye WRAPPERS:
            self.write = write
            value.encode(self)
            toa self.write
        isipokua:
            # store instance attributes as a struct (really?)
            self.dump_struct(value.__dict__, write)
    dispatch[DateTime] = dump_instance
    dispatch[Binary] = dump_instance
    # XXX(twouters): using "_arbitrary_instance" as key as a quick-fix
    # kila the p3yk merge, this should probably be fixed more neatly.
    dispatch["_arbitrary_instance"] = dump_instance

##
# XML-RPC unmarshaller.
#
# @see loads

kundi Unmarshaller:
    """Unmarshal an XML-RPC response, based on incoming XML event
    messages (start, data, end).  Call close() to get the resulting
    data structure.

    Note that this reader ni fairly tolerant, na gladly accepts bogus
    XML-RPC data without complaining (but sio bogus XML).
    """

    # na again, ikiwa you don't understand what's going on kwenye here,
    # that's perfectly ok.

    eleza __init__(self, use_datetime=Uongo, use_builtin_types=Uongo):
        self._type = Tupu
        self._stack = []
        self._marks = []
        self._data = []
        self._value = Uongo
        self._methodname = Tupu
        self._encoding = "utf-8"
        self.append = self._stack.append
        self._use_datetime = use_builtin_types ama use_datetime
        self._use_bytes = use_builtin_types

    eleza close(self):
        # rudisha response tuple na target method
        ikiwa self._type ni Tupu ama self._marks:
             ashiria ResponseError()
        ikiwa self._type == "fault":
             ashiria Fault(**self._stack[0])
        rudisha tuple(self._stack)

    eleza getmethodname(self):
        rudisha self._methodname

    #
    # event handlers

    eleza xml(self, encoding, standalone):
        self._encoding = encoding
        # FIXME: assert standalone == 1 ???

    eleza start(self, tag, attrs):
        # prepare to handle this element
        ikiwa ':' kwenye tag:
            tag = tag.split(':')[-1]
        ikiwa tag == "array" ama tag == "struct":
            self._marks.append(len(self._stack))
        self._data = []
        ikiwa self._value na tag sio kwenye self.dispatch:
             ashiria ResponseError("unknown tag %r" % tag)
        self._value = (tag == "value")

    eleza data(self, text):
        self._data.append(text)

    eleza end(self, tag):
        # call the appropriate end tag handler
        jaribu:
            f = self.dispatch[tag]
        except KeyError:
            ikiwa ':' sio kwenye tag:
                rudisha # unknown tag ?
            jaribu:
                f = self.dispatch[tag.split(':')[-1]]
            except KeyError:
                rudisha # unknown tag ?
        rudisha f(self, "".join(self._data))

    #
    # accelerator support

    eleza end_dispatch(self, tag, data):
        # dispatch data
        jaribu:
            f = self.dispatch[tag]
        except KeyError:
            ikiwa ':' sio kwenye tag:
                rudisha # unknown tag ?
            jaribu:
                f = self.dispatch[tag.split(':')[-1]]
            except KeyError:
                rudisha # unknown tag ?
        rudisha f(self, data)

    #
    # element decoders

    dispatch = {}

    eleza end_nil (self, data):
        self.append(Tupu)
        self._value = 0
    dispatch["nil"] = end_nil

    eleza end_boolean(self, data):
        ikiwa data == "0":
            self.append(Uongo)
        elikiwa data == "1":
            self.append(Kweli)
        isipokua:
             ashiria TypeError("bad boolean value")
        self._value = 0
    dispatch["boolean"] = end_boolean

    eleza end_int(self, data):
        self.append(int(data))
        self._value = 0
    dispatch["i1"] = end_int
    dispatch["i2"] = end_int
    dispatch["i4"] = end_int
    dispatch["i8"] = end_int
    dispatch["int"] = end_int
    dispatch["biginteger"] = end_int

    eleza end_double(self, data):
        self.append(float(data))
        self._value = 0
    dispatch["double"] = end_double
    dispatch["float"] = end_double

    eleza end_bigdecimal(self, data):
        self.append(Decimal(data))
        self._value = 0
    dispatch["bigdecimal"] = end_bigdecimal

    eleza end_string(self, data):
        ikiwa self._encoding:
            data = data.decode(self._encoding)
        self.append(data)
        self._value = 0
    dispatch["string"] = end_string
    dispatch["name"] = end_string # struct keys are always strings

    eleza end_array(self, data):
        mark = self._marks.pop()
        # map arrays to Python lists
        self._stack[mark:] = [self._stack[mark:]]
        self._value = 0
    dispatch["array"] = end_array

    eleza end_struct(self, data):
        mark = self._marks.pop()
        # map structs to Python dictionaries
        dict = {}
        items = self._stack[mark:]
        kila i kwenye range(0, len(items), 2):
            dict[items[i]] = items[i+1]
        self._stack[mark:] = [dict]
        self._value = 0
    dispatch["struct"] = end_struct

    eleza end_base64(self, data):
        value = Binary()
        value.decode(data.encode("ascii"))
        ikiwa self._use_bytes:
            value = value.data
        self.append(value)
        self._value = 0
    dispatch["base64"] = end_base64

    eleza end_dateTime(self, data):
        value = DateTime()
        value.decode(data)
        ikiwa self._use_datetime:
            value = _datetime_type(data)
        self.append(value)
    dispatch["dateTime.iso8601"] = end_dateTime

    eleza end_value(self, data):
        # ikiwa we stumble upon a value element ukijumuisha no internal
        # elements, treat it as a string element
        ikiwa self._value:
            self.end_string(data)
    dispatch["value"] = end_value

    eleza end_params(self, data):
        self._type = "params"
    dispatch["params"] = end_params

    eleza end_fault(self, data):
        self._type = "fault"
    dispatch["fault"] = end_fault

    eleza end_methodName(self, data):
        ikiwa self._encoding:
            data = data.decode(self._encoding)
        self._methodname = data
        self._type = "methodName" # no params
    dispatch["methodName"] = end_methodName

## Multicall support
#

kundi _MultiCallMethod:
    # some lesser magic to store calls made to a MultiCall object
    # kila batch execution
    eleza __init__(self, call_list, name):
        self.__call_list = call_list
        self.__name = name
    eleza __getattr__(self, name):
        rudisha _MultiCallMethod(self.__call_list, "%s.%s" % (self.__name, name))
    eleza __call__(self, *args):
        self.__call_list.append((self.__name, args))

kundi MultiCallIterator:
    """Iterates over the results of a multicall. Exceptions are
    raised kwenye response to xmlrpc faults."""

    eleza __init__(self, results):
        self.results = results

    eleza __getitem__(self, i):
        item = self.results[i]
        ikiwa type(item) == type({}):
             ashiria Fault(item['faultCode'], item['faultString'])
        elikiwa type(item) == type([]):
            rudisha item[0]
        isipokua:
             ashiria ValueError("unexpected type kwenye multicall result")

kundi MultiCall:
    """server -> an object used to boxcar method calls

    server should be a ServerProxy object.

    Methods can be added to the MultiCall using normal
    method call syntax e.g.:

    multicall = MultiCall(server_proxy)
    multicall.add(2,3)
    multicall.get_address("Guido")

    To execute the multicall, call the MultiCall object e.g.:

    add_result, address = multicall()
    """

    eleza __init__(self, server):
        self.__server = server
        self.__call_list = []

    eleza __repr__(self):
        rudisha "<%s at %#x>" % (self.__class__.__name__, id(self))

    eleza __getattr__(self, name):
        rudisha _MultiCallMethod(self.__call_list, name)

    eleza __call__(self):
        marshalled_list = []
        kila name, args kwenye self.__call_list:
            marshalled_list.append({'methodName' : name, 'params' : args})

        rudisha MultiCallIterator(self.__server.system.multicall(marshalled_list))

# --------------------------------------------------------------------
# convenience functions

FastMarshaller = FastParser = FastUnmarshaller = Tupu

##
# Create a parser object, na connect it to an unmarshalling instance.
# This function picks the fastest available XML parser.
#
# rudisha A (parser, unmarshaller) tuple.

eleza getparser(use_datetime=Uongo, use_builtin_types=Uongo):
    """getparser() -> parser, unmarshaller

    Create an instance of the fastest available parser, na attach it
    to an unmarshalling object.  Return both objects.
    """
    ikiwa FastParser na FastUnmarshaller:
        ikiwa use_builtin_types:
            mkdatetime = _datetime_type
            mkbytes = base64.decodebytes
        elikiwa use_datetime:
            mkdatetime = _datetime_type
            mkbytes = _binary
        isipokua:
            mkdatetime = _datetime
            mkbytes = _binary
        target = FastUnmarshaller(Kweli, Uongo, mkbytes, mkdatetime, Fault)
        parser = FastParser(target)
    isipokua:
        target = Unmarshaller(use_datetime=use_datetime, use_builtin_types=use_builtin_types)
        ikiwa FastParser:
            parser = FastParser(target)
        isipokua:
            parser = ExpatParser(target)
    rudisha parser, target

##
# Convert a Python tuple ama a Fault instance to an XML-RPC packet.
#
# @eleza dumps(params, **options)
# @param params A tuple ama Fault instance.
# @keyparam methodname If given, create a methodCall request for
#     this method name.
# @keyparam methodresponse If given, create a methodResponse packet.
#     If used ukijumuisha a tuple, the tuple must be a singleton (that is,
#     it must contain exactly one element).
# @keyparam encoding The packet encoding.
# @rudisha A string containing marshalled data.

eleza dumps(params, methodname=Tupu, methodresponse=Tupu, encoding=Tupu,
          allow_none=Uongo):
    """data [,options] -> marshalled data

    Convert an argument tuple ama a Fault instance to an XML-RPC
    request (or response, ikiwa the methodresponse option ni used).

    In addition to the data object, the following options can be given
    as keyword arguments:

        methodname: the method name kila a methodCall packet

        methodresponse: true to create a methodResponse packet.
        If this option ni used ukijumuisha a tuple, the tuple must be
        a singleton (i.e. it can contain only one element).

        encoding: the packet encoding (default ni UTF-8)

    All byte strings kwenye the data structure are assumed to use the
    packet encoding.  Unicode strings are automatically converted,
    where necessary.
    """

    assert isinstance(params, (tuple, Fault)), "argument must be tuple ama Fault instance"
    ikiwa isinstance(params, Fault):
        methodresponse = 1
    elikiwa methodresponse na isinstance(params, tuple):
        assert len(params) == 1, "response tuple must be a singleton"

    ikiwa sio encoding:
        encoding = "utf-8"

    ikiwa FastMarshaller:
        m = FastMarshaller(encoding)
    isipokua:
        m = Marshaller(encoding, allow_none)

    data = m.dumps(params)

    ikiwa encoding != "utf-8":
        xmlheader = "<?xml version='1.0' encoding='%s'?>\n" % str(encoding)
    isipokua:
        xmlheader = "<?xml version='1.0'?>\n" # utf-8 ni default

    # standard XML-RPC wrappings
    ikiwa methodname:
        # a method call
        data = (
            xmlheader,
            "<methodCall>\n"
            "<methodName>", methodname, "</methodName>\n",
            data,
            "</methodCall>\n"
            )
    elikiwa methodresponse:
        # a method response, ama a fault structure
        data = (
            xmlheader,
            "<methodResponse>\n",
            data,
            "</methodResponse>\n"
            )
    isipokua:
        rudisha data # rudisha as is
    rudisha "".join(data)

##
# Convert an XML-RPC packet to a Python object.  If the XML-RPC packet
# represents a fault condition, this function raises a Fault exception.
#
# @param data An XML-RPC packet, given as an 8-bit string.
# @rudisha A tuple containing the unpacked data, na the method name
#     (Tupu ikiwa sio present).
# @see Fault

eleza loads(data, use_datetime=Uongo, use_builtin_types=Uongo):
    """data -> unmarshalled data, method name

    Convert an XML-RPC packet to unmarshalled data plus a method
    name (Tupu ikiwa sio present).

    If the XML-RPC packet represents a fault condition, this function
    raises a Fault exception.
    """
    p, u = getparser(use_datetime=use_datetime, use_builtin_types=use_builtin_types)
    p.feed(data)
    p.close()
    rudisha u.close(), u.getmethodname()

##
# Encode a string using the gzip content encoding such as specified by the
# Content-Encoding: gzip
# kwenye the HTTP header, as described kwenye RFC 1952
#
# @param data the unencoded data
# @rudisha the encoded data

eleza gzip_encode(data):
    """data -> gzip encoded data

    Encode data using the gzip content encoding as described kwenye RFC 1952
    """
    ikiwa sio gzip:
         ashiria NotImplementedError
    f = BytesIO()
    ukijumuisha gzip.GzipFile(mode="wb", fileobj=f, compresslevel=1) as gzf:
        gzf.write(data)
    rudisha f.getvalue()

##
# Decode a string using the gzip content encoding such as specified by the
# Content-Encoding: gzip
# kwenye the HTTP header, as described kwenye RFC 1952
#
# @param data The encoded data
# @keyparam max_decode Maximum bytes to decode (20 MiB default), use negative
#    values kila unlimited decoding
# @rudisha the unencoded data
# @raises ValueError ikiwa data ni sio correctly coded.
# @raises ValueError ikiwa max gzipped payload length exceeded

eleza gzip_decode(data, max_decode=20971520):
    """gzip encoded data -> unencoded data

    Decode data using the gzip content encoding as described kwenye RFC 1952
    """
    ikiwa sio gzip:
         ashiria NotImplementedError
    ukijumuisha gzip.GzipFile(mode="rb", fileobj=BytesIO(data)) as gzf:
        jaribu:
            ikiwa max_decode < 0: # no limit
                decoded = gzf.read()
            isipokua:
                decoded = gzf.read(max_decode + 1)
        except OSError:
             ashiria ValueError("invalid data")
    ikiwa max_decode >= 0 na len(decoded) > max_decode:
         ashiria ValueError("max gzipped payload length exceeded")
    rudisha decoded

##
# Return a decoded file-like object kila the gzip encoding
# as described kwenye RFC 1952.
#
# @param response A stream supporting a read() method
# @rudisha a file-like object that the decoded data can be read() from

kundi GzipDecodedResponse(gzip.GzipFile ikiwa gzip isipokua object):
    """a file-like object to decode a response encoded ukijumuisha the gzip
    method, as described kwenye RFC 1952.
    """
    eleza __init__(self, response):
        #response doesn't support tell() na read(), required by
        #GzipFile
        ikiwa sio gzip:
             ashiria NotImplementedError
        self.io = BytesIO(response.read())
        gzip.GzipFile.__init__(self, mode="rb", fileobj=self.io)

    eleza close(self):
        jaribu:
            gzip.GzipFile.close(self)
        mwishowe:
            self.io.close()


# --------------------------------------------------------------------
# request dispatcher

kundi _Method:
    # some magic to bind an XML-RPC method to an RPC server.
    # supports "nested" methods (e.g. examples.getStateName)
    eleza __init__(self, send, name):
        self.__send = send
        self.__name = name
    eleza __getattr__(self, name):
        rudisha _Method(self.__send, "%s.%s" % (self.__name, name))
    eleza __call__(self, *args):
        rudisha self.__send(self.__name, args)

##
# Standard transport kundi kila XML-RPC over HTTP.
# <p>
# You can create custom transports by subclassing this method, and
# overriding selected methods.

kundi Transport:
    """Handles an HTTP transaction to an XML-RPC server."""

    # client identifier (may be overridden)
    user_agent = "Python-xmlrpc/%s" % __version__

    #ikiwa true, we'll request gzip encoding
    accept_gzip_encoding = Kweli

    # ikiwa positive, encode request using gzip ikiwa it exceeds this threshold
    # note that many servers will get confused, so only use it ikiwa you know
    # that they can decode such a request
    encode_threshold = Tupu #Tupu = don't encode

    eleza __init__(self, use_datetime=Uongo, use_builtin_types=Uongo,
                 *, headers=()):
        self._use_datetime = use_datetime
        self._use_builtin_types = use_builtin_types
        self._connection = (Tupu, Tupu)
        self._headers = list(headers)
        self._extra_headers = []

    ##
    # Send a complete request, na parse the response.
    # Retry request ikiwa a cached connection has disconnected.
    #
    # @param host Target host.
    # @param handler Target PRC handler.
    # @param request_body XML-RPC request body.
    # @param verbose Debugging flag.
    # @rudisha Parsed response.

    eleza request(self, host, handler, request_body, verbose=Uongo):
        #retry request once ikiwa cached connection has gone cold
        kila i kwenye (0, 1):
            jaribu:
                rudisha self.single_request(host, handler, request_body, verbose)
            except http.client.RemoteDisconnected:
                ikiwa i:
                    raise
            except OSError as e:
                ikiwa i ama e.errno sio kwenye (errno.ECONNRESET, errno.ECONNABORTED,
                                        errno.EPIPE):
                    raise

    eleza single_request(self, host, handler, request_body, verbose=Uongo):
        # issue XML-RPC request
        jaribu:
            http_conn = self.send_request(host, handler, request_body, verbose)
            resp = http_conn.getresponse()
            ikiwa resp.status == 200:
                self.verbose = verbose
                rudisha self.parse_response(resp)

        except Fault:
            raise
        except Exception:
            #All unexpected errors leave connection in
            # a strange state, so we clear it.
            self.close()
            raise

        #We got an error response.
        #Discard any response data na  ashiria exception
        ikiwa resp.getheader("content-length", ""):
            resp.read()
         ashiria ProtocolError(
            host + handler,
            resp.status, resp.reason,
            dict(resp.getheaders())
            )


    ##
    # Create parser.
    #
    # @rudisha A 2-tuple containing a parser na an unmarshaller.

    eleza getparser(self):
        # get parser na unmarshaller
        rudisha getparser(use_datetime=self._use_datetime,
                         use_builtin_types=self._use_builtin_types)

    ##
    # Get authorization info kutoka host parameter
    # Host may be a string, ama a (host, x509-dict) tuple; ikiwa a string,
    # it ni checked kila a "user:pw@host" format, na a "Basic
    # Authentication" header ni added ikiwa appropriate.
    #
    # @param host Host descriptor (URL ama (URL, x509 info) tuple).
    # @rudisha A 3-tuple containing (actual host, extra headers,
    #     x509 info).  The header na x509 fields may be Tupu.

    eleza get_host_info(self, host):

        x509 = {}
        ikiwa isinstance(host, tuple):
            host, x509 = host

        auth, host = urllib.parse._splituser(host)

        ikiwa auth:
            auth = urllib.parse.unquote_to_bytes(auth)
            auth = base64.encodebytes(auth).decode("utf-8")
            auth = "".join(auth.split()) # get rid of whitespace
            extra_headers = [
                ("Authorization", "Basic " + auth)
                ]
        isipokua:
            extra_headers = []

        rudisha host, extra_headers, x509

    ##
    # Connect to server.
    #
    # @param host Target host.
    # @rudisha An HTTPConnection object

    eleza make_connection(self, host):
        #rudisha an existing connection ikiwa possible.  This allows
        #HTTP/1.1 keep-alive.
        ikiwa self._connection na host == self._connection[0]:
            rudisha self._connection[1]
        # create a HTTP connection object kutoka a host descriptor
        chost, self._extra_headers, x509 = self.get_host_info(host)
        self._connection = host, http.client.HTTPConnection(chost)
        rudisha self._connection[1]

    ##
    # Clear any cached connection object.
    # Used kwenye the event of socket errors.
    #
    eleza close(self):
        host, connection = self._connection
        ikiwa connection:
            self._connection = (Tupu, Tupu)
            connection.close()

    ##
    # Send HTTP request.
    #
    # @param host Host descriptor (URL ama (URL, x509 info) tuple).
    # @param handler Target RPC handler (a path relative to host)
    # @param request_body The XML-RPC request body
    # @param debug Enable debugging ikiwa debug ni true.
    # @rudisha An HTTPConnection.

    eleza send_request(self, host, handler, request_body, debug):
        connection = self.make_connection(host)
        headers = self._headers + self._extra_headers
        ikiwa debug:
            connection.set_debuglevel(1)
        ikiwa self.accept_gzip_encoding na gzip:
            connection.putrequest("POST", handler, skip_accept_encoding=Kweli)
            headers.append(("Accept-Encoding", "gzip"))
        isipokua:
            connection.putrequest("POST", handler)
        headers.append(("Content-Type", "text/xml"))
        headers.append(("User-Agent", self.user_agent))
        self.send_headers(connection, headers)
        self.send_content(connection, request_body)
        rudisha connection

    ##
    # Send request headers.
    # This function provides a useful hook kila subclassing
    #
    # @param connection httpConnection.
    # @param headers list of key,value pairs kila HTTP headers

    eleza send_headers(self, connection, headers):
        kila key, val kwenye headers:
            connection.putheader(key, val)

    ##
    # Send request body.
    # This function provides a useful hook kila subclassing
    #
    # @param connection httpConnection.
    # @param request_body XML-RPC request body.

    eleza send_content(self, connection, request_body):
        #optionally encode the request
        ikiwa (self.encode_threshold ni sio Tupu and
            self.encode_threshold < len(request_body) and
            gzip):
            connection.putheader("Content-Encoding", "gzip")
            request_body = gzip_encode(request_body)

        connection.putheader("Content-Length", str(len(request_body)))
        connection.endheaders(request_body)

    ##
    # Parse response.
    #
    # @param file Stream.
    # @rudisha Response tuple na target method.

    eleza parse_response(self, response):
        # read response data kutoka httpresponse, na parse it
        # Check kila new http response object, otherwise it ni a file object.
        ikiwa hasattr(response, 'getheader'):
            ikiwa response.getheader("Content-Encoding", "") == "gzip":
                stream = GzipDecodedResponse(response)
            isipokua:
                stream = response
        isipokua:
            stream = response

        p, u = self.getparser()

        wakati 1:
            data = stream.read(1024)
            ikiwa sio data:
                koma
            ikiwa self.verbose:
                andika("body:", repr(data))
            p.feed(data)

        ikiwa stream ni sio response:
            stream.close()
        p.close()

        rudisha u.close()

##
# Standard transport kundi kila XML-RPC over HTTPS.

kundi SafeTransport(Transport):
    """Handles an HTTPS transaction to an XML-RPC server."""

    eleza __init__(self, use_datetime=Uongo, use_builtin_types=Uongo,
                 *, headers=(), context=Tupu):
        super().__init__(use_datetime=use_datetime,
                         use_builtin_types=use_builtin_types,
                         headers=headers)
        self.context = context

    # FIXME: mostly untested

    eleza make_connection(self, host):
        ikiwa self._connection na host == self._connection[0]:
            rudisha self._connection[1]

        ikiwa sio hasattr(http.client, "HTTPSConnection"):
             ashiria NotImplementedError(
            "your version of http.client doesn't support HTTPS")
        # create a HTTPS connection object kutoka a host descriptor
        # host may be a string, ama a (host, x509-dict) tuple
        chost, self._extra_headers, x509 = self.get_host_info(host)
        self._connection = host, http.client.HTTPSConnection(chost,
            Tupu, context=self.context, **(x509 ama {}))
        rudisha self._connection[1]

##
# Standard server proxy.  This kundi establishes a virtual connection
# to an XML-RPC server.
# <p>
# This kundi ni available as ServerProxy na Server.  New code should
# use ServerProxy, to avoid confusion.
#
# @eleza ServerProxy(uri, **options)
# @param uri The connection point on the server.
# @keyparam transport A transport factory, compatible ukijumuisha the
#    standard transport class.
# @keyparam encoding The default encoding used kila 8-bit strings
#    (default ni UTF-8).
# @keyparam verbose Use a true value to enable debugging output.
#    (printed to standard output).
# @see Transport

kundi ServerProxy:
    """uri [,options] -> a logical connection to an XML-RPC server

    uri ni the connection point on the server, given as
    scheme://host/target.

    The standard implementation always supports the "http" scheme.  If
    SSL socket support ni available (Python 2.0), it also supports
    "https".

    If the target part na the slash preceding it are both omitted,
    "/RPC2" ni assumed.

    The following options can be given as keyword arguments:

        transport: a transport factory
        encoding: the request encoding (default ni UTF-8)

    All 8-bit strings passed to the server proxy are assumed to use
    the given encoding.
    """

    eleza __init__(self, uri, transport=Tupu, encoding=Tupu, verbose=Uongo,
                 allow_none=Uongo, use_datetime=Uongo, use_builtin_types=Uongo,
                 *, headers=(), context=Tupu):
        # establish a "logical" server connection

        # get the url
        type, uri = urllib.parse._splittype(uri)
        ikiwa type sio kwenye ("http", "https"):
             ashiria OSError("unsupported XML-RPC protocol")
        self.__host, self.__handler = urllib.parse._splithost(uri)
        ikiwa sio self.__handler:
            self.__handler = "/RPC2"

        ikiwa transport ni Tupu:
            ikiwa type == "https":
                handler = SafeTransport
                extra_kwargs = {"context": context}
            isipokua:
                handler = Transport
                extra_kwargs = {}
            transport = handler(use_datetime=use_datetime,
                                use_builtin_types=use_builtin_types,
                                headers=headers,
                                **extra_kwargs)
        self.__transport = transport

        self.__encoding = encoding ama 'utf-8'
        self.__verbose = verbose
        self.__allow_none = allow_none

    eleza __close(self):
        self.__transport.close()

    eleza __request(self, methodname, params):
        # call a method on the remote server

        request = dumps(params, methodname, encoding=self.__encoding,
                        allow_none=self.__allow_none).encode(self.__encoding, 'xmlcharrefreplace')

        response = self.__transport.request(
            self.__host,
            self.__handler,
            request,
            verbose=self.__verbose
            )

        ikiwa len(response) == 1:
            response = response[0]

        rudisha response

    eleza __repr__(self):
        rudisha (
            "<%s kila %s%s>" %
            (self.__class__.__name__, self.__host, self.__handler)
            )

    eleza __getattr__(self, name):
        # magic method dispatcher
        rudisha _Method(self.__request, name)

    # note: to call a remote object ukijumuisha a non-standard name, use
    # result getattr(server, "strange-python-name")(args)

    eleza __call__(self, attr):
        """A workaround to get special attributes on the ServerProxy
           without interfering ukijumuisha the magic __getattr__
        """
        ikiwa attr == "close":
            rudisha self.__close
        elikiwa attr == "transport":
            rudisha self.__transport
         ashiria AttributeError("Attribute %r sio found" % (attr,))

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *args):
        self.__close()

# compatibility

Server = ServerProxy

# --------------------------------------------------------------------
# test code

ikiwa __name__ == "__main__":

    # simple test program (kutoka the XML-RPC specification)

    # local server, available kutoka Lib/xmlrpc/server.py
    server = ServerProxy("http://localhost:8000")

    jaribu:
        andika(server.currentTime.getCurrentTime())
    except Error as v:
        andika("ERROR", v)

    multi = MultiCall(server)
    multi.getData()
    multi.pow(2,9)
    multi.add(1,2)
    jaribu:
        kila response kwenye multi():
            andika(response)
    except Error as v:
        andika("ERROR", v)
