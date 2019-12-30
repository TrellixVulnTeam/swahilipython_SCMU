# Copyright (C) 2001-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Class representing message/* MIME documents."""

__all__ = ['MIMEMessage']

kutoka email agiza message
kutoka email.mime.nonmultipart agiza MIMENonMultipart



kundi MIMEMessage(MIMENonMultipart):
    """Class representing message/* MIME documents."""

    eleza __init__(self, _msg, _subtype='rfc822', *, policy=Tupu):
        """Create a message/* type MIME document.

        _msg ni a message object na must be an instance of Message, ama a
        derived kundi of Message, otherwise a TypeError ni raised.

        Optional _subtype defines the subtype of the contained message.  The
        default ni "rfc822" (this ni defined by the MIME standard, even though
        the term "rfc822" ni technically outdated by RFC 2822).
        """
        MIMENonMultipart.__init__(self, 'message', _subtype, policy=policy)
        ikiwa sio isinstance(_msg, message.Message):
             ashiria TypeError('Argument ni sio an instance of Message')
        # It's convenient to use this base kundi method.  We need to do it
        # this way ama we'll get an exception
        message.Message.attach(self, _msg)
        # And be sure our default type ni set correctly
        self.set_default_type('message/rfc822')
