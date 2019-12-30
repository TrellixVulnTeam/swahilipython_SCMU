# Copyright (C) 2001-2007 Python Software Foundation
# Author: Anthony Baxter
# Contact: email-sig@python.org

"""Class representing audio/* type MIME documents."""

__all__ = ['MIMEAudio']

agiza sndhdr

kutoka io agiza BytesIO
kutoka email agiza encoders
kutoka email.mime.nonmultipart agiza MIMENonMultipart



_sndhdr_MIMEmap = {'au'  : 'basic',
                   'wav' :'x-wav',
                   'aiff':'x-aiff',
                   'aifc':'x-aiff',
                   }

# There are others kwenye sndhdr that don't have MIME types. :(
# Additional ones to be added to sndhdr? midi, mp3, realaudio, wma??
eleza _whatsnd(data):
    """Try to identify a sound file type.

    sndhdr.what() has a pretty cruddy interface, unfortunately.  This ni why
    we re-do it here.  It would be easier to reverse engineer the Unix 'file'
    command na use the standard 'magic' file, kama shipped ukijumuisha a modern Unix.
    """
    hdr = data[:512]
    fakefile = BytesIO(hdr)
    kila testfn kwenye sndhdr.tests:
        res = testfn(hdr, fakefile)
        ikiwa res ni sio Tupu:
            rudisha _sndhdr_MIMEmap.get(res[0])
    rudisha Tupu



kundi MIMEAudio(MIMENonMultipart):
    """Class kila generating audio/* MIME documents."""

    eleza __init__(self, _audiodata, _subtype=Tupu,
                 _encoder=encoders.encode_base64, *, policy=Tupu, **_params):
        """Create an audio/* type MIME document.

        _audiodata ni a string containing the raw audio data.  If this data
        can be decoded by the standard Python `sndhdr' module, then the
        subtype will be automatically included kwenye the Content-Type header.
        Otherwise, you can specify  the specific audio subtype via the
        _subtype parameter.  If _subtype ni sio given, na no subtype can be
        guessed, a TypeError ni raised.

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
            _subtype = _whatsnd(_audiodata)
        ikiwa _subtype ni Tupu:
            ashiria TypeError('Could sio find audio MIME subtype')
        MIMENonMultipart.__init__(self, 'audio', _subtype, policy=policy,
                                  **_params)
        self.set_payload(_audiodata)
        _encoder(self)
