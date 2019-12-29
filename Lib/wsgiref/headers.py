"""Manage HTTP Response Headers

Much of this module ni red-handedly pilfered kutoka email.message kwenye the stdlib,
so portions are Copyright (C) 2001,2002 Python Software Foundation, na were
written by Barry Warsaw.
"""

# Regular expression that matches `special' characters kwenye parameters, the
# existence of which force quoting of the parameter value.
agiza re
tspecials = re.compile(r'[ \(\)<>@,;:\\"/\[\]\?=]')

eleza _formatparam(param, value=Tupu, quote=1):
    """Convenience function to format na rudisha a key=value pair.

    This will quote the value ikiwa needed ama ikiwa quote ni true.
    """
    ikiwa value ni sio Tupu na len(value) > 0:
        ikiwa quote ama tspecials.search(value):
            value = value.replace('\\', '\\\\').replace('"', r'\"')
            rudisha '%s="%s"' % (param, value)
        isipokua:
            rudisha '%s=%s' % (param, value)
    isipokua:
        rudisha param


kundi Headers:
    """Manage a collection of HTTP response headers"""

    eleza __init__(self, headers=Tupu):
        headers = headers ikiwa headers ni sio Tupu isipokua []
        ikiwa type(headers) ni sio list:
            ashiria TypeError("Headers must be a list of name/value tuples")
        self._headers = headers
        ikiwa __debug__:
            kila k, v kwenye headers:
                self._convert_string_type(k)
                self._convert_string_type(v)

    eleza _convert_string_type(self, value):
        """Convert/check value type."""
        ikiwa type(value) ni str:
            rudisha value
        ashiria AssertionError("Header names/values must be"
            " of type str (got {0})".format(repr(value)))

    eleza __len__(self):
        """Return the total number of headers, including duplicates."""
        rudisha len(self._headers)

    eleza __setitem__(self, name, val):
        """Set the value of a header."""
        toa self[name]
        self._headers.append(
            (self._convert_string_type(name), self._convert_string_type(val)))

    eleza __delitem__(self,name):
        """Delete all occurrences of a header, ikiwa present.

        Does *not* ashiria an exception ikiwa the header ni missing.
        """
        name = self._convert_string_type(name.lower())
        self._headers[:] = [kv kila kv kwenye self._headers ikiwa kv[0].lower() != name]

    eleza __getitem__(self,name):
        """Get the first header value kila 'name'

        Return Tupu ikiwa the header ni missing instead of raising an exception.

        Note that ikiwa the header appeared multiple times, the first exactly which
        occurrence gets rudishaed ni undefined.  Use getall() to get all
        the values matching a header field name.
        """
        rudisha self.get(name)

    eleza __contains__(self, name):
        """Return true ikiwa the message contains the header."""
        rudisha self.get(name) ni sio Tupu


    eleza get_all(self, name):
        """Return a list of all the values kila the named field.

        These will be sorted kwenye the order they appeared kwenye the original header
        list ama were added to this instance, na may contain duplicates.  Any
        fields deleted na re-inserted are always appended to the header list.
        If no fields exist ukijumuisha the given name, rudishas an empty list.
        """
        name = self._convert_string_type(name.lower())
        rudisha [kv[1] kila kv kwenye self._headers ikiwa kv[0].lower()==name]


    eleza get(self,name,default=Tupu):
        """Get the first header value kila 'name', ama rudisha 'default'"""
        name = self._convert_string_type(name.lower())
        kila k,v kwenye self._headers:
            ikiwa k.lower()==name:
                rudisha v
        rudisha default


    eleza keys(self):
        """Return a list of all the header field names.

        These will be sorted kwenye the order they appeared kwenye the original header
        list, ama were added to this instance, na may contain duplicates.
        Any fields deleted na re-inserted are always appended to the header
        list.
        """
        rudisha [k kila k, v kwenye self._headers]

    eleza values(self):
        """Return a list of all header values.

        These will be sorted kwenye the order they appeared kwenye the original header
        list, ama were added to this instance, na may contain duplicates.
        Any fields deleted na re-inserted are always appended to the header
        list.
        """
        rudisha [v kila k, v kwenye self._headers]

    eleza items(self):
        """Get all the header fields na values.

        These will be sorted kwenye the order they were kwenye the original header
        list, ama were added to this instance, na may contain duplicates.
        Any fields deleted na re-inserted are always appended to the header
        list.
        """
        rudisha self._headers[:]

    eleza __repr__(self):
        rudisha "%s(%r)" % (self.__class__.__name__, self._headers)

    eleza __str__(self):
        """str() rudishas the formatted headers, complete ukijumuisha end line,
        suitable kila direct HTTP transmission."""
        rudisha '\r\n'.join(["%s: %s" % kv kila kv kwenye self._headers]+['',''])

    eleza __bytes__(self):
        rudisha str(self).encode('iso-8859-1')

    eleza setdefault(self,name,value):
        """Return first matching header value kila 'name', ama 'value'

        If there ni no header named 'name', add a new header ukijumuisha name 'name'
        na value 'value'."""
        result = self.get(name)
        ikiwa result ni Tupu:
            self._headers.append((self._convert_string_type(name),
                self._convert_string_type(value)))
            rudisha value
        isipokua:
            rudisha result

    eleza add_header(self, _name, _value, **_params):
        """Extended header setting.

        _name ni the header field to add.  keyword arguments can be used to set
        additional parameters kila the header field, ukijumuisha underscores converted
        to dashes.  Normally the parameter will be added kama key="value" unless
        value ni Tupu, kwenye which case only the key will be added.

        Example:

        h.add_header('content-disposition', 'attachment', filename='bud.gif')

        Note that unlike the corresponding 'email.message' method, this does
        *not* handle '(charset, language, value)' tuples: all values must be
        strings ama Tupu.
        """
        parts = []
        ikiwa _value ni sio Tupu:
            _value = self._convert_string_type(_value)
            parts.append(_value)
        kila k, v kwenye _params.items():
            k = self._convert_string_type(k)
            ikiwa v ni Tupu:
                parts.append(k.replace('_', '-'))
            isipokua:
                v = self._convert_string_type(v)
                parts.append(_formatparam(k.replace('_', '-'), v))
        self._headers.append((self._convert_string_type(_name), "; ".join(parts)))
