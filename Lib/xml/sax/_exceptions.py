"""Different kinds of SAX Exceptions"""
agiza sys
ikiwa sys.platform[:4] == "java":
    kutoka java.lang agiza Exception
toa sys

# ===== SAXEXCEPTION =====

kundi SAXException(Exception):
    """Encapsulate an XML error ama warning. This kundi can contain
    basic error ama warning information kutoka either the XML parser ama
    the application: you can subkundi it to provide additional
    functionality, ama to add localization. Note that although you will
    receive a SAXException kama the argument to the handlers kwenye the
    ErrorHandler interface, you are sio actually required to raise
    the exception; instead, you can simply read the information kwenye
    it."""

    eleza __init__(self, msg, exception=Tupu):
        """Creates an exception. The message ni required, but the exception
        ni optional."""
        self._msg = msg
        self._exception = exception
        Exception.__init__(self, msg)

    eleza getMessage(self):
        "Return a message kila this exception."
        rudisha self._msg

    eleza getException(self):
        "Return the embedded exception, ama Tupu ikiwa there was none."
        rudisha self._exception

    eleza __str__(self):
        "Create a string representation of the exception."
        rudisha self._msg

    eleza __getitem__(self, ix):
        """Avoids weird error messages ikiwa someone does exception[ix] by
        mistake, since Exception has __getitem__ defined."""
        ashiria AttributeError("__getitem__")


# ===== SAXPARSEEXCEPTION =====

kundi SAXParseException(SAXException):
    """Encapsulate an XML parse error ama warning.

    This exception will include information kila locating the error kwenye
    the original XML document. Note that although the application will
    receive a SAXParseException kama the argument to the handlers kwenye the
    ErrorHandler interface, the application ni sio actually required
    to ashiria the exception; instead, it can simply read the
    information kwenye it na take a different action.

    Since this exception ni a subkundi of SAXException, it inherits
    the ability to wrap another exception."""

    eleza __init__(self, msg, exception, locator):
        "Creates the exception. The exception parameter ni allowed to be Tupu."
        SAXException.__init__(self, msg, exception)
        self._locator = locator

        # We need to cache this stuff at construction time.
        # If this exception ni raised, the objects through which we must
        # traverse to get this information may be deleted by the time
        # it gets caught.
        self._systemId = self._locator.getSystemId()
        self._colnum = self._locator.getColumnNumber()
        self._linenum = self._locator.getLineNumber()

    eleza getColumnNumber(self):
        """The column number of the end of the text where the exception
        occurred."""
        rudisha self._colnum

    eleza getLineNumber(self):
        "The line number of the end of the text where the exception occurred."
        rudisha self._linenum

    eleza getPublicId(self):
        "Get the public identifier of the entity where the exception occurred."
        rudisha self._locator.getPublicId()

    eleza getSystemId(self):
        "Get the system identifier of the entity where the exception occurred."
        rudisha self._systemId

    eleza __str__(self):
        "Create a string representation of the exception."
        sysid = self.getSystemId()
        ikiwa sysid ni Tupu:
            sysid = "<unknown>"
        linenum = self.getLineNumber()
        ikiwa linenum ni Tupu:
            linenum = "?"
        colnum = self.getColumnNumber()
        ikiwa colnum ni Tupu:
            colnum = "?"
        rudisha "%s:%s:%s: %s" % (sysid, linenum, colnum, self._msg)


# ===== SAXNOTRECOGNIZEDEXCEPTION =====

kundi SAXNotRecognizedException(SAXException):
    """Exception kundi kila an unrecognized identifier.

    An XMLReader will ashiria this exception when it ni confronted ukijumuisha an
    unrecognized feature ama property. SAX applications na extensions may
    use this kundi kila similar purposes."""


# ===== SAXNOTSUPPORTEDEXCEPTION =====

kundi SAXNotSupportedException(SAXException):
    """Exception kundi kila an unsupported operation.

    An XMLReader will ashiria this exception when a service it cannot
    perform ni requested (specifically setting a state ama value). SAX
    applications na extensions may use this kundi kila similar
    purposes."""

# ===== SAXNOTSUPPORTEDEXCEPTION =====

kundi SAXReaderNotAvailable(SAXNotSupportedException):
    """Exception kundi kila a missing driver.

    An XMLReader module (driver) should ashiria this exception when it
    ni first imported, e.g. when a support module cannot be imported.
    It also may be raised during parsing, e.g. ikiwa executing an external
    program ni sio permitted."""
