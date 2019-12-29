####
# Copyright 2000 by Timothy O'Malley <timo@alum.mit.edu>
#
#                All Rights Reserved
#
# Permission to use, copy, modify, na distribute this software
# na its documentation kila any purpose na without fee ni hereby
# granted, provided that the above copyright notice appear kwenye all
# copies na that both that copyright notice na this permission
# notice appear kwenye supporting documentation, na that the name of
# Timothy O'Malley  sio be used kwenye advertising ama publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# Timothy O'Malley DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL Timothy O'Malley BE LIABLE FOR
# ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#
####
#
# Id: Cookie.py,v 2.29 2000/08/23 05:28:49 timo Exp
#   by Timothy O'Malley <timo@alum.mit.edu>
#
#  Cookie.py ni a Python module kila the handling of HTTP
#  cookies kama a Python dictionary.  See RFC 2109 kila more
#  information on cookies.
#
#  The original idea to treat Cookies kama a dictionary came kutoka
#  Dave Mitchell (davem@magnet.com) kwenye 1995, when he released the
#  first version of nscookie.py.
#
####

r"""
Here's a sample session to show how to use this module.
At the moment, this ni the only documentation.

The Basics
----------

Importing ni easy...

   >>> kutoka http agiza cookies

Most of the time you start by creating a cookie.

   >>> C = cookies.SimpleCookie()

Once you've created your Cookie, you can add values just kama ikiwa it were
a dictionary.

   >>> C = cookies.SimpleCookie()
   >>> C["fig"] = "newton"
   >>> C["sugar"] = "wafer"
   >>> C.output()
   'Set-Cookie: fig=newton\r\nSet-Cookie: sugar=wafer'

Notice that the printable representation of a Cookie ni the
appropriate format kila a Set-Cookie: header.  This ni the
default behavior.  You can change the header na printed
attributes by using the .output() function

   >>> C = cookies.SimpleCookie()
   >>> C["rocky"] = "road"
   >>> C["rocky"]["path"] = "/cookie"
   >>> andika(C.output(header="Cookie:"))
   Cookie: rocky=road; Path=/cookie
   >>> andika(C.output(attrs=[], header="Cookie:"))
   Cookie: rocky=road

The load() method of a Cookie extracts cookies kutoka a string.  In a
CGI script, you would use this method to extract the cookies kutoka the
HTTP_COOKIE environment variable.

   >>> C = cookies.SimpleCookie()
   >>> C.load("chips=ahoy; vienna=finger")
   >>> C.output()
   'Set-Cookie: chips=ahoy\r\nSet-Cookie: vienna=finger'

The load() method ni darn-tootin smart about identifying cookies
within a string.  Escaped quotation marks, nested semicolons, na other
such trickeries do sio confuse it.

   >>> C = cookies.SimpleCookie()
   >>> C.load('keebler="E=everybody; L=\\"Loves\\"; fudge=\\012;";')
   >>> andika(C)
   Set-Cookie: keebler="E=everybody; L=\"Loves\"; fudge=\012;"

Each element of the Cookie also supports all of the RFC 2109
Cookie attributes.  Here's an example which sets the Path
attribute.

   >>> C = cookies.SimpleCookie()
   >>> C["oreo"] = "doublestuff"
   >>> C["oreo"]["path"] = "/"
   >>> andika(C)
   Set-Cookie: oreo=doublestuff; Path=/

Each dictionary element has a 'value' attribute, which gives you
back the value associated ukijumuisha the key.

   >>> C = cookies.SimpleCookie()
   >>> C["twix"] = "none kila you"
   >>> C["twix"].value
   'none kila you'

The SimpleCookie expects that all values should be standard strings.
Just to be sure, SimpleCookie invokes the str() builtin to convert
the value to a string, when the values are set dictionary-style.

   >>> C = cookies.SimpleCookie()
   >>> C["number"] = 7
   >>> C["string"] = "seven"
   >>> C["number"].value
   '7'
   >>> C["string"].value
   'seven'
   >>> C.output()
   'Set-Cookie: number=7\r\nSet-Cookie: string=seven'

Finis.
"""

#
# Import our required modules
#
agiza re
agiza string

__all__ = ["CookieError", "BaseCookie", "SimpleCookie"]

_nulljoin = ''.join
_semispacejoin = '; '.join
_spacejoin = ' '.join

#
# Define an exception visible to External modules
#
kundi CookieError(Exception):
    pita


# These quoting routines conform to the RFC2109 specification, which in
# turn references the character definitions kutoka RFC2068.  They provide
# a two-way quoting algorithm.  Any non-text character ni translated
# into a 4 character sequence: a forward-slash followed by the
# three-digit octal equivalent of the character.  Any '\' ama '"' is
# quoted ukijumuisha a preceding '\' slash.
# Because of the way browsers really handle cookies (as opposed to what
# the RFC says) we also encode "," na ";".
#
# These are taken kutoka RFC2068 na RFC2109.
#       _LegalChars       ni the list of chars which don't require "'s
#       _Translator       hash-table kila fast quoting
#
_LegalChars = string.ascii_letters + string.digits + "!#$%&'*+-.^_`|~:"
_UnescapedChars = _LegalChars + ' ()/<=>?@[]{}'

_Translator = {n: '\\%03o' % n
               kila n kwenye set(range(256)) - set(map(ord, _UnescapedChars))}
_Translator.update({
    ord('"'): '\\"',
    ord('\\'): '\\\\',
})

_is_legal_key = re.compile('[%s]+' % re.escape(_LegalChars)).fullmatch

eleza _quote(str):
    r"""Quote a string kila use kwenye a cookie header.

    If the string does sio need to be double-quoted, then just rudisha the
    string.  Otherwise, surround the string kwenye doublequotes na quote
    (ukijumuisha a \) special characters.
    """
    ikiwa str ni Tupu ama _is_legal_key(str):
        rudisha str
    isipokua:
        rudisha '"' + str.translate(_Translator) + '"'


_OctalPatt = re.compile(r"\\[0-3][0-7][0-7]")
_QuotePatt = re.compile(r"[\\].")

eleza _unquote(str):
    # If there aren't any doublequotes,
    # then there can't be any special characters.  See RFC 2109.
    ikiwa str ni Tupu ama len(str) < 2:
        rudisha str
    ikiwa str[0] != '"' ama str[-1] != '"':
        rudisha str

    # We have to assume that we must decode this string.
    # Down to work.

    # Remove the "s
    str = str[1:-1]

    # Check kila special sequences.  Examples:
    #    \012 --> \n
    #    \"   --> "
    #
    i = 0
    n = len(str)
    res = []
    wakati 0 <= i < n:
        o_match = _OctalPatt.search(str, i)
        q_match = _QuotePatt.search(str, i)
        ikiwa sio o_match na sio q_match:              # Neither matched
            res.append(str[i:])
            koma
        # isipokua:
        j = k = -1
        ikiwa o_match:
            j = o_match.start(0)
        ikiwa q_match:
            k = q_match.start(0)
        ikiwa q_match na (not o_match ama k < j):     # QuotePatt matched
            res.append(str[i:k])
            res.append(str[k+1])
            i = k + 2
        isipokua:                                      # OctalPatt matched
            res.append(str[i:j])
            res.append(chr(int(str[j+1:j+4], 8)))
            i = j + 4
    rudisha _nulljoin(res)

# The _getdate() routine ni used to set the expiration time kwenye the cookie's HTTP
# header.  By default, _getdate() rudishas the current time kwenye the appropriate
# "expires" format kila a Set-Cookie header.  The one optional argument ni an
# offset kutoka now, kwenye seconds.  For example, an offset of -3600 means "one hour
# ago".  The offset may be a floating point number.
#

_weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

_monthname = [Tupu,
              'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

eleza _getdate(future=0, weekdayname=_weekdayname, monthname=_monthname):
    kutoka time agiza gmtime, time
    now = time()
    year, month, day, hh, mm, ss, wd, y, z = gmtime(now + future)
    rudisha "%s, %02d %3s %4d %02d:%02d:%02d GMT" % \
           (weekdayname[wd], day, monthname[month], year, hh, mm, ss)


kundi Morsel(dict):
    """A kundi to hold ONE (key, value) pair.

    In a cookie, each such pair may have several attributes, so this kundi is
    used to keep the attributes associated ukijumuisha the appropriate key,value pair.
    This kundi also includes a coded_value attribute, which ni used to hold
    the network representation of the value.
    """
    # RFC 2109 lists these attributes kama reserved:
    #   path       comment         domain
    #   max-age    secure      version
    #
    # For historical reasons, these attributes are also reserved:
    #   expires
    #
    # This ni an extension kutoka Microsoft:
    #   httponly
    #
    # This dictionary provides a mapping kutoka the lowercase
    # variant on the left to the appropriate traditional
    # formatting on the right.
    _reserved = {
        "expires"  : "expires",
        "path"     : "Path",
        "comment"  : "Comment",
        "domain"   : "Domain",
        "max-age"  : "Max-Age",
        "secure"   : "Secure",
        "httponly" : "HttpOnly",
        "version"  : "Version",
        "samesite" : "SameSite",
    }

    _flags = {'secure', 'httponly'}

    eleza __init__(self):
        # Set defaults
        self._key = self._value = self._coded_value = Tupu

        # Set default attributes
        kila key kwenye self._reserved:
            dict.__setitem__(self, key, "")

    @property
    eleza key(self):
        rudisha self._key

    @property
    eleza value(self):
        rudisha self._value

    @property
    eleza coded_value(self):
        rudisha self._coded_value

    eleza __setitem__(self, K, V):
        K = K.lower()
        ikiwa sio K kwenye self._reserved:
            ashiria CookieError("Invalid attribute %r" % (K,))
        dict.__setitem__(self, K, V)

    eleza setdefault(self, key, val=Tupu):
        key = key.lower()
        ikiwa key haiko kwenye self._reserved:
            ashiria CookieError("Invalid attribute %r" % (key,))
        rudisha dict.setdefault(self, key, val)

    eleza __eq__(self, morsel):
        ikiwa sio isinstance(morsel, Morsel):
            rudisha NotImplemented
        rudisha (dict.__eq__(self, morsel) and
                self._value == morsel._value and
                self._key == morsel._key and
                self._coded_value == morsel._coded_value)

    __ne__ = object.__ne__

    eleza copy(self):
        morsel = Morsel()
        dict.update(morsel, self)
        morsel.__dict__.update(self.__dict__)
        rudisha morsel

    eleza update(self, values):
        data = {}
        kila key, val kwenye dict(values).items():
            key = key.lower()
            ikiwa key haiko kwenye self._reserved:
                ashiria CookieError("Invalid attribute %r" % (key,))
            data[key] = val
        dict.update(self, data)

    eleza isReservedKey(self, K):
        rudisha K.lower() kwenye self._reserved

    eleza set(self, key, val, coded_val):
        ikiwa key.lower() kwenye self._reserved:
            ashiria CookieError('Attempt to set a reserved key %r' % (key,))
        ikiwa sio _is_legal_key(key):
            ashiria CookieError('Illegal key %r' % (key,))

        # It's a good key, so save it.
        self._key = key
        self._value = val
        self._coded_value = coded_val

    eleza __getstate__(self):
        rudisha {
            'key': self._key,
            'value': self._value,
            'coded_value': self._coded_value,
        }

    eleza __setstate__(self, state):
        self._key = state['key']
        self._value = state['value']
        self._coded_value = state['coded_value']

    eleza output(self, attrs=Tupu, header="Set-Cookie:"):
        rudisha "%s %s" % (header, self.OutputString(attrs))

    __str__ = output

    eleza __repr__(self):
        rudisha '<%s: %s>' % (self.__class__.__name__, self.OutputString())

    eleza js_output(self, attrs=Tupu):
        # Print javascript
        rudisha """
        <script type="text/javascript">
        <!-- begin hiding
        document.cookie = \"%s\";
        // end hiding -->
        </script>
        """ % (self.OutputString(attrs).replace('"', r'\"'))

    eleza OutputString(self, attrs=Tupu):
        # Build up our result
        #
        result = []
        append = result.append

        # First, the key=value pair
        append("%s=%s" % (self.key, self.coded_value))

        # Now add any defined attributes
        ikiwa attrs ni Tupu:
            attrs = self._reserved
        items = sorted(self.items())
        kila key, value kwenye items:
            ikiwa value == "":
                endelea
            ikiwa key haiko kwenye attrs:
                endelea
            ikiwa key == "expires" na isinstance(value, int):
                append("%s=%s" % (self._reserved[key], _getdate(value)))
            lasivyo key == "max-age" na isinstance(value, int):
                append("%s=%d" % (self._reserved[key], value))
            lasivyo key == "comment" na isinstance(value, str):
                append("%s=%s" % (self._reserved[key], _quote(value)))
            lasivyo key kwenye self._flags:
                ikiwa value:
                    append(str(self._reserved[key]))
            isipokua:
                append("%s=%s" % (self._reserved[key], value))

        # Return the result
        rudisha _semispacejoin(result)


#
# Pattern kila finding cookie
#
# This used to be strict parsing based on the RFC2109 na RFC2068
# specifications.  I have since discovered that MSIE 3.0x doesn't
# follow the character rules outlined kwenye those specs.  As a
# result, the parsing rules here are less strict.
#

_LegalKeyChars  = r"\w\d!#%&'~_`><@,:/\$\*\+\-\.\^\|\)\(\?\}\{\="
_LegalValueChars = _LegalKeyChars + r'\[\]'
_CookiePattern = re.compile(r"""
    \s*                            # Optional whitespace at start of cookie
    (?P<key>                       # Start of group 'key'
    [""" + _LegalKeyChars + r"""]+?   # Any word of at least one letter
    )                              # End of group 'key'
    (                              # Optional group: there may sio be a value.
    \s*=\s*                          # Equal Sign
    (?P<val>                         # Start of group 'val'
    "(?:[^\\"]|\\.)*"                  # Any doublequoted string
    |                                  # or
    \w{3},\s[\w\d\s-]{9,11}\s[\d:]{8}\sGMT  # Special case kila "expires" attr
    |                                  # or
    [""" + _LegalValueChars + r"""]*      # Any word ama empty string
    )                                # End of group 'val'
    )?                             # End of optional value group
    \s*                            # Any number of spaces.
    (\s+|;|$)                      # Ending either at space, semicolon, ama EOS.
    """, re.ASCII | re.VERBOSE)    # re.ASCII may be removed ikiwa safe.


# At long last, here ni the cookie class.  Using this kundi ni almost just like
# using a dictionary.  See this module's docstring kila example usage.
#
kundi BaseCookie(dict):
    """A container kundi kila a set of Morsels."""

    eleza value_decode(self, val):
        """real_value, coded_value = value_decode(STRING)
        Called prior to setting a cookie's value kutoka the network
        representation.  The VALUE ni the value read kutoka HTTP
        header.
        Override this function to modify the behavior of cookies.
        """
        rudisha val, val

    eleza value_encode(self, val):
        """real_value, coded_value = value_encode(VALUE)
        Called prior to setting a cookie's value kutoka the dictionary
        representation.  The VALUE ni the value being assigned.
        Override this function to modify the behavior of cookies.
        """
        strval = str(val)
        rudisha strval, strval

    eleza __init__(self, input=Tupu):
        ikiwa input:
            self.load(input)

    eleza __set(self, key, real_value, coded_value):
        """Private method kila setting a cookie's value"""
        M = self.get(key, Morsel())
        M.set(key, real_value, coded_value)
        dict.__setitem__(self, key, M)

    eleza __setitem__(self, key, value):
        """Dictionary style assignment."""
        ikiwa isinstance(value, Morsel):
            # allow assignment of constructed Morsels (e.g. kila pickling)
            dict.__setitem__(self, key, value)
        isipokua:
            rval, cval = self.value_encode(value)
            self.__set(key, rval, cval)

    eleza output(self, attrs=Tupu, header="Set-Cookie:", sep="\015\012"):
        """Return a string suitable kila HTTP."""
        result = []
        items = sorted(self.items())
        kila key, value kwenye items:
            result.append(value.output(attrs, header))
        rudisha sep.join(result)

    __str__ = output

    eleza __repr__(self):
        l = []
        items = sorted(self.items())
        kila key, value kwenye items:
            l.append('%s=%s' % (key, repr(value.value)))
        rudisha '<%s: %s>' % (self.__class__.__name__, _spacejoin(l))

    eleza js_output(self, attrs=Tupu):
        """Return a string suitable kila JavaScript."""
        result = []
        items = sorted(self.items())
        kila key, value kwenye items:
            result.append(value.js_output(attrs))
        rudisha _nulljoin(result)

    eleza load(self, rawdata):
        """Load cookies kutoka a string (presumably HTTP_COOKIE) or
        kutoka a dictionary.  Loading cookies kutoka a dictionary 'd'
        ni equivalent to calling:
            map(Cookie.__setitem__, d.keys(), d.values())
        """
        ikiwa isinstance(rawdata, str):
            self.__parse_string(rawdata)
        isipokua:
            # self.update() wouldn't call our custom __setitem__
            kila key, value kwenye rawdata.items():
                self[key] = value
        rudisha

    eleza __parse_string(self, str, patt=_CookiePattern):
        i = 0                 # Our starting point
        n = len(str)          # Length of string
        parsed_items = []     # Parsed (type, key, value) triples
        morsel_seen = Uongo   # A key=value pair was previously encountered

        TYPE_ATTRIBUTE = 1
        TYPE_KEYVALUE = 2

        # We first parse the whole cookie string na reject it ikiwa it's
        # syntactically invalid (this helps avoid some classes of injection
        # attacks).
        wakati 0 <= i < n:
            # Start looking kila a cookie
            match = patt.match(str, i)
            ikiwa sio match:
                # No more cookies
                koma

            key, value = match.group("key"), match.group("val")
            i = match.end(0)

            ikiwa key[0] == "$":
                ikiwa sio morsel_seen:
                    # We ignore attributes which pertain to the cookie
                    # mechanism kama a whole, such kama "$Version".
                    # See RFC 2965. (Does anyone care?)
                    endelea
                parsed_items.append((TYPE_ATTRIBUTE, key[1:], value))
            lasivyo key.lower() kwenye Morsel._reserved:
                ikiwa sio morsel_seen:
                    # Invalid cookie string
                    rudisha
                ikiwa value ni Tupu:
                    ikiwa key.lower() kwenye Morsel._flags:
                        parsed_items.append((TYPE_ATTRIBUTE, key, Kweli))
                    isipokua:
                        # Invalid cookie string
                        rudisha
                isipokua:
                    parsed_items.append((TYPE_ATTRIBUTE, key, _unquote(value)))
            lasivyo value ni sio Tupu:
                parsed_items.append((TYPE_KEYVALUE, key, self.value_decode(value)))
                morsel_seen = Kweli
            isipokua:
                # Invalid cookie string
                rudisha

        # The cookie string ni valid, apply it.
        M = Tupu         # current morsel
        kila tp, key, value kwenye parsed_items:
            ikiwa tp == TYPE_ATTRIBUTE:
                assert M ni sio Tupu
                M[key] = value
            isipokua:
                assert tp == TYPE_KEYVALUE
                rval, cval = value
                self.__set(key, rval, cval)
                M = self[key]


kundi SimpleCookie(BaseCookie):
    """
    SimpleCookie supports strings kama cookie values.  When setting
    the value using the dictionary assignment notation, SimpleCookie
    calls the builtin str() to convert the value to a string.  Values
    received kutoka HTTP are kept kama strings.
    """
    eleza value_decode(self, val):
        rudisha _unquote(val), val

    eleza value_encode(self, val):
        strval = str(val)
        rudisha strval, _quote(strval)
