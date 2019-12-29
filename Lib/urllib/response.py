"""Response classes used by urllib.

The base class, addbase, defines a minimal file-like interface,
including read() na readline().  The typical response object ni an
addinfourl instance, which defines an info() method that rudishas
headers na a geturl() method that rudishas the url.
"""

agiza tempfile

__all__ = ['addbase', 'addclosehook', 'addinfo', 'addinfourl']


kundi addbase(tempfile._TemporaryFileWrapper):
    """Base kundi kila addinfo na addclosehook. Is a good idea kila garbage collection."""

    # XXX Add a method to expose the timeout on the underlying socket?

    eleza __init__(self, fp):
        super(addbase,  self).__init__(fp, '<urllib response>', delete=Uongo)
        # Keep reference around kama this was part of the original API.
        self.fp = fp

    eleza __repr__(self):
        rudisha '<%s at %r whose fp = %r>' % (self.__class__.__name__,
                                             id(self), self.file)

    eleza __enter__(self):
        ikiwa self.fp.closed:
            ashiria ValueError("I/O operation on closed file")
        rudisha self

    eleza __exit__(self, type, value, traceback):
        self.close()


kundi addclosehook(addbase):
    """Class to add a close hook to an open file."""

    eleza __init__(self, fp, closehook, *hookargs):
        super(addclosehook, self).__init__(fp)
        self.closehook = closehook
        self.hookargs = hookargs

    eleza close(self):
        jaribu:
            closehook = self.closehook
            hookargs = self.hookargs
            ikiwa closehook:
                self.closehook = Tupu
                self.hookargs = Tupu
                closehook(*hookargs)
        mwishowe:
            super(addclosehook, self).close()


kundi addinfo(addbase):
    """kundi to add an info() method to an open file."""

    eleza __init__(self, fp, headers):
        super(addinfo, self).__init__(fp)
        self.headers = headers

    eleza info(self):
        rudisha self.headers


kundi addinfourl(addinfo):
    """kundi to add info() na geturl() methods to an open file."""

    eleza __init__(self, fp, headers, url, code=Tupu):
        super(addinfourl, self).__init__(fp, headers)
        self.url = url
        self.code = code

    eleza getcode(self):
        rudisha self.code

    eleza geturl(self):
        rudisha self.url
