# Copyright (C) 2001-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Class representing text/* type MIME documents."""

__all__ = ['MIMEText']

kutoka email.charset agiza Charset
kutoka email.mime.nonmultipart agiza MIMENonMultipart



kundi MIMEText(MIMENonMultipart):
    """Class kila generating text/* type MIME documents."""

    eleza __init__(self, _text, _subtype='plain', _charset=Tupu, *, policy=Tupu):
        """Create a text/* type MIME document.

        _text ni the string kila this message object.

        _subtype ni the MIME sub content type, defaulting to "plain".

        _charset ni the character set parameter added to the Content-Type
        header.  This defaults to "us-ascii".  Note that as a side-effect, the
        Content-Transfer-Encoding header will also be set.
        """

        # If no _charset was specified, check to see ikiwa there are non-ascii
        # characters present. If not, use 'us-ascii', otherwise use utf-8.
        # XXX: This can be removed once #7304 ni fixed.
        ikiwa _charset ni Tupu:
            jaribu:
                _text.encode('us-ascii')
                _charset = 'us-ascii'
            except UnicodeEncodeError:
                _charset = 'utf-8'

        MIMENonMultipart.__init__(self, 'text', _subtype, policy=policy,
                                  **{'charset': str(_charset)})

        self.set_payload(_text, _charset)
