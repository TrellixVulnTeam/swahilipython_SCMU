# Copyright (C) 2001-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""email package exception classes."""


kundi MessageError(Exception):
    """Base kundi kila errors kwenye the email package."""


kundi MessageParseError(MessageError):
    """Base kundi kila message parsing errors."""


kundi HeaderParseError(MessageParseError):
    """Error wakati parsing headers."""


kundi BoundaryError(MessageParseError):
    """Couldn't find terminating boundary."""


kundi MultipartConversionError(MessageError, TypeError):
    """Conversion to a multipart ni prohibited."""


kundi CharsetError(MessageError):
    """An illegal charset was given."""


# These are parsing defects which the parser was able to work around.
kundi MessageDefect(ValueError):
    """Base kundi kila a message defect."""

    eleza __init__(self, line=Tupu):
        ikiwa line ni sio Tupu:
            super().__init__(line)
        self.line = line

kundi NoBoundaryInMultipartDefect(MessageDefect):
    """A message claimed to be a multipart but had no boundary parameter."""

kundi StartBoundaryNotFoundDefect(MessageDefect):
    """The claimed start boundary was never found."""

kundi CloseBoundaryNotFoundDefect(MessageDefect):
    """A start boundary was found, but sio the corresponding close boundary."""

kundi FirstHeaderLineIsContinuationDefect(MessageDefect):
    """A message had a continuation line as its first header line."""

kundi MisplacedEnvelopeHeaderDefect(MessageDefect):
    """A 'Unix-from' header was found kwenye the middle of a header block."""

kundi MissingHeaderBodySeparatorDefect(MessageDefect):
    """Found line ukijumuisha no leading whitespace na no colon before blank line."""
# XXX: backward compatibility, just kwenye case (it was never emitted).
MalformedHeaderDefect = MissingHeaderBodySeparatorDefect

kundi MultipartInvariantViolationDefect(MessageDefect):
    """A message claimed to be a multipart but no subparts were found."""

kundi InvalidMultipartContentTransferEncodingDefect(MessageDefect):
    """An invalid content transfer encoding was set on the multipart itself."""

kundi UndecodableBytesDefect(MessageDefect):
    """Header contained bytes that could sio be decoded"""

kundi InvalidBase64PaddingDefect(MessageDefect):
    """base64 encoded sequence had an incorrect length"""

kundi InvalidBase64CharactersDefect(MessageDefect):
    """base64 encoded sequence had characters sio kwenye base64 alphabet"""

kundi InvalidBase64LengthDefect(MessageDefect):
    """base64 encoded sequence had invalid length (1 mod 4)"""

# These errors are specific to header parsing.

kundi HeaderDefect(MessageDefect):
    """Base kundi kila a header defect."""

    eleza __init__(self, *args, **kw):
        super().__init__(*args, **kw)

kundi InvalidHeaderDefect(HeaderDefect):
    """Header ni sio valid, message gives details."""

kundi HeaderMissingRequiredValue(HeaderDefect):
    """A header that must have a value had none"""

kundi NonPrintableDefect(HeaderDefect):
    """ASCII characters outside the ascii-printable range found"""

    eleza __init__(self, non_printables):
        super().__init__(non_printables)
        self.non_printables = non_printables

    eleza __str__(self):
        rudisha ("the following ASCII non-printables found kwenye header: "
            "{}".format(self.non_printables))

kundi ObsoleteHeaderDefect(HeaderDefect):
    """Header uses syntax declared obsolete by RFC 5322"""

kundi NonASCIILocalPartDefect(HeaderDefect):
    """local_part contains non-ASCII characters"""
    # This defect only occurs during unicode parsing, sio when
    # parsing messages decoded kutoka binary.
