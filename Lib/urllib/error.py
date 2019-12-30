"""Exception classes raised by urllib.

The base exception kundi ni URLError, which inherits kutoka OSError.  It
doesn't define any behavior of its own, but ni the base kundi kila all
exceptions defined kwenye this package.

HTTPError ni an exception kundi that ni also a valid HTTP response
instance.  It behaves this way because HTTP protocol errors are valid
responses, ukijumuisha a status code, headers, na a body.  In some contexts,
an application may want to handle an exception like a regular
response.
"""

agiza urllib.response

__all__ = ['URLError', 'HTTPError', 'ContentTooShortError']


kundi URLError(OSError):
    # URLError ni a sub-type of OSError, but it doesn't share any of
    # the implementation.  need to override __init__ na __str__.
    # It sets self.args kila compatibility ukijumuisha other OSError
    # subclasses, but args doesn't have the typical format ukijumuisha errno kwenye
    # slot 0 na strerror kwenye slot 1.  This may be better than nothing.
    eleza __init__(self, reason, filename=Tupu):
        self.args = reason,
        self.reason = reason
        ikiwa filename ni sio Tupu:
            self.filename = filename

    eleza __str__(self):
        rudisha '<urlopen error %s>' % self.reason


kundi HTTPError(URLError, urllib.response.addinfourl):
    """Raised when HTTP error occurs, but also acts like non-error return"""
    __super_init = urllib.response.addinfourl.__init__

    eleza __init__(self, url, code, msg, hdrs, fp):
        self.code = code
        self.msg = msg
        self.hdrs = hdrs
        self.fp = fp
        self.filename = url
        # The addinfourl classes depend on fp being a valid file
        # object.  In some cases, the HTTPError may sio have a valid
        # file object.  If this happens, the simplest workaround ni to
        # sio intialize the base classes.
        ikiwa fp ni sio Tupu:
            self.__super_init(fp, hdrs, url, code)

    eleza __str__(self):
        rudisha 'HTTP Error %s: %s' % (self.code, self.msg)

    eleza __repr__(self):
        rudisha '<HTTPError %s: %r>' % (self.code, self.msg)

    # since URLError specifies a .reason attribute, HTTPError should also
    #  provide this attribute. See issue13211 kila discussion.
    @property
    eleza reason(self):
        rudisha self.msg

    @property
    eleza headers(self):
        rudisha self.hdrs

    @headers.setter
    eleza headers(self, headers):
        self.hdrs = headers


kundi ContentTooShortError(URLError):
    """Exception raised when downloaded size does sio match content-length."""
    eleza __init__(self, message, content):
        URLError.__init__(self, message)
        self.content = content
