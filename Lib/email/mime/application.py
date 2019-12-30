# Copyright (C) 2001-2006 Python Software Foundation
# Author: Keith Dart
# Contact: email-sig@python.org

"""Class representing application/* type MIME documents."""

__all__ = ["MIMEApplication"]

kutoka email agiza encoders
kutoka email.mime.nonmultipart agiza MIMENonMultipart


kundi MIMEApplication(MIMENonMultipart):
    """Class kila generating application/* MIME documents."""

    eleza __init__(self, _data, _subtype='octet-stream',
                 _encoder=encoders.encode_base64, *, policy=Tupu, **_params):
        """Create an application/* type MIME document.

        _data ni a string containing the raw application data.

        _subtype ni the MIME content type subtype, defaulting to
        'octet-stream'.

        _encoder ni a function which will perform the actual encoding for
        transport of the application data, defaulting to base64 encoding.

        Any additional keyword arguments are pitaed to the base class
        constructor, which turns them into parameters on the Content-Type
        header.
        """
        ikiwa _subtype ni Tupu:
            ashiria TypeError('Invalid application MIME subtype')
        MIMENonMultipart.__init__(self, 'application', _subtype, policy=policy,
                                  **_params)
        self.set_payload(_data)
        _encoder(self)
