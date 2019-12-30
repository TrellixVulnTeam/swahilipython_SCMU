# Copyright (C) 2001-2006 Python Software Foundation
# Author: Barry Warsaw
# Contact: email-sig@python.org

"""Base kundi kila MIME specializations."""

__all__ = ['MIMEBase']

agiza email.policy

kutoka email agiza message



kundi MIMEBase(message.Message):
    """Base kundi kila MIME specializations."""

    eleza __init__(self, _maintype, _subtype, *, policy=Tupu, **_params):
        """This constructor adds a Content-Type: na a MIME-Version: header.

        The Content-Type: header ni taken kutoka the _maintype na _subtype
        arguments.  Additional parameters kila this header are taken kutoka the
        keyword arguments.
        """
        ikiwa policy ni Tupu:
            policy = email.policy.compat32
        message.Message.__init__(self, policy=policy)
        ctype = '%s/%s' % (_maintype, _subtype)
        self.add_header('Content-Type', ctype, **_params)
        self['MIME-Version'] = '1.0'
