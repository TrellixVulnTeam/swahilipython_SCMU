"""Different kinds of SAX Exceptions"""
agiza sys
ikiwa sys.platform[:4] == "java":
    kutoka java.lang agiza Exception
del sys

# ===== SAXEXCEPTION =====

kundi SAXException(Exception):
    """Encapsulate an XML error or warning. This kundi can contain
    basic error or warning information kutoka either the XML parser or
    the application: you can subkundi it to provide additional
    functionality, or to add localization. Note that although you will
    receive a SAXException as the argument to the handlers in the
    ErrorHandler interface, you are not actually required to raise
    the exception; instead, you can simply read the information in
    it."""

    eleza __init__(self, msg, exception=None):
        """Creates an exception. The message is required, but the exception
        is optional."""
        self._msg = msg
        self._exception = exception
        Exception.__init__(self, msg)

    eleza getMessage(self):
        "Return a message for this exception."
        rudisha self._msg

    eleza getException(self):
        "Return the embedded exception, or None ikiwa there was none."
        rudisha self._exception

    eleza __str__(self):
        "Create a string representation of the exception."
        rudisha self._msg

    eleza __getitem__(self, ix):
        """Avoids weird error messages ikiwa someone does exception[ix] by
        mistake, since Exception has __getitem__ defined."""
        raise AttributeError("__getitem__")


# ===== SAXPARSEEXCEPTION =====

kundi SAXParseException(SAXException):
    """Encapsulate an XML parse error or warning.

    This exception will include information for locating the error in
    the original XML document. Note that although the application will
    receive a SAXParseException as the argument to the handlers in the
    ErrorHandler interface, the application is not actually required
    to raise the exception; instead, it can simply read the
    information in it and take a different action.

    Since this exception is a subkundi of SAXException, it inherits
    the ability to wrap another exception."""

    eleza __init__(self, msg, exception, locator):
        "Creates the exception. The exception parameter is allowed to be None."
        SAXException.__init__(self, msg, exception)
        self._locator = locator

        # We need to cache this stuff at construction time.
        # If this exception is raised, the objects through which we must
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
        ikiwa sysid is None:
            sysid = "<unknown>"
        linenum = self.getLineNumber()
        ikiwa linenum is None:
            linenum = "?"
        colnum = self.getColumnNumber()
        ikiwa colnum is None:
            colnum = "?"
        rudisha "%s:%s:%s: %s" % (sysid, linenum, colnum, self._msg)


# ===== SAXNOTRECOGNIZEDEXCEPTION =====

kundi SAXNotRecognizedException(SAXException):
    """Exception kundi for an unrecognized identifier.

    An XMLReader will raise this exception when it is confronted with an
    unrecognized feature or property. SAX applications and extensions may
    use this kundi for similar purposes."""


# ===== SAXNOTSUPPORTEDEXCEPTION =====

kundi SAXNotSupportedException(SAXException):
    """Exception kundi for an unsupported operation.

    An XMLReader will raise this exception when a service it cannot
    perform is requested (specifically setting a state or value). SAX
    applications and extensions may use this kundi for similar
    purposes."""

# ===== SAXNOTSUPPORTEDEXCEPTION =====

kundi SAXReaderNotAvailable(SAXNotSupportedException):
    """Exception kundi for a missing driver.

    An XMLReader module (driver) should raise this exception when it
    is first imported, e.g. when a support module cannot be imported.
    It also may be raised during parsing, e.g. ikiwa executing an external
    program is not permitted."""
