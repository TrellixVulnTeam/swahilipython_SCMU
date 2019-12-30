# Copyright (C) 2001-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Class representing image/* type MIME documents."""

__all__ = ['MIMEImage']

agiza imghdr

kutoka email agiza encoders
kutoka email.mime.nonmultipart agiza MIMENonMultipart



kundi MIMEImage(MIMENonMultipart):
    """Class kila generating image/* type MIME documents."""

    eleza __init__(self, _imagedata, _subtype=Tupu,
                 _encoder=encoders.encode_base64, *, policy=Tupu, **_params):
        """Create an image/* type MIME document.

        _imagedata ni a string containing the raw image data.  If this data
        can be decoded by the standard Python `imghdr' module, then the
        subtype will be automatically included kwenye the Content-Type header.
        Otherwise, you can specify the specific image subtype via the _subtype
        parameter.

        _encoder ni a function which will perform the actual encoding for
        transport of the image data.  It takes one argument, which ni this
        Image instance.  It should use get_payload() na set_payload() to
        change the payload to the encoded form.  It should also add any
        Content-Transfer-Encoding ama other headers to the message as
        necessary.  The default encoding ni Base64.

        Any additional keyword arguments are pitaed to the base class
        constructor, which turns them into parameters on the Content-Type
        header.
        """
        ikiwa _subtype ni Tupu:
            _subtype = imghdr.what(Tupu, _imagedata)
        ikiwa _subtype ni Tupu:
            ashiria TypeError('Could sio guess image MIME subtype')
        MIMENonMultipart.__init__(self, 'image', _subtype, policy=policy,
                                  **_params)
        self.set_payload(_imagedata)
        _encoder(self)
