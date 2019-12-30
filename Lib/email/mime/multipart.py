# Copyright (C) 2002-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Base kundi kila MIME multipart/* type messages."""

__all__ = ['MIMEMultipart']

kutoka email.mime.base agiza MIMEBase



kundi MIMEMultipart(MIMEBase):
    """Base kundi kila MIME multipart/* type messages."""

    eleza __init__(self, _subtype='mixed', boundary=Tupu, _subparts=Tupu,
                 *, policy=Tupu,
                 **_params):
        """Creates a multipart/* type message.

        By default, creates a multipart/mixed message, ukijumuisha proper
        Content-Type na MIME-Version headers.

        _subtype ni the subtype of the multipart content type, defaulting to
        `mixed'.

        boundary ni the multipart boundary string.  By default it is
        calculated kama needed.

        _subparts ni a sequence of initial subparts kila the payload.  It
        must be an iterable object, such kama a list.  You can always
        attach new subparts to the message by using the attach() method.

        Additional parameters kila the Content-Type header are taken kutoka the
        keyword arguments (or pitaed into the _params argument).
        """
        MIMEBase.__init__(self, 'multipart', _subtype, policy=policy, **_params)

        # Initialise _payload to an empty list kama the Message superclass's
        # implementation of is_multipart assumes that _payload ni a list for
        # multipart messages.
        self._payload = []

        ikiwa _subparts:
            kila p kwenye _subparts:
                self.attach(p)
        ikiwa boundary:
            self.set_boundary(boundary)
