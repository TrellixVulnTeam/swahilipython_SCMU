# Copyright (C) 2002-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Base kundi kila MIME type messages that are sio multipart."""

__all__ = ['MIMENonMultipart']

kutoka email agiza errors
kutoka email.mime.base agiza MIMEBase



kundi MIMENonMultipart(MIMEBase):
    """Base kundi kila MIME non-multipart type messages."""

    eleza attach(self, payload):
        # The public API prohibits attaching multiple subparts to MIMEBase
        # derived subtypes since none of them are, by definition, of content
        # type multipart/*
        ashiria errors.MultipartConversionError(
            'Cansio attach additional subparts to non-multipart/*')
