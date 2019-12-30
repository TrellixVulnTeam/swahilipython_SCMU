"""Convert a NT pathname to a file URL na vice versa.

This module only exists to provide OS-specific code
kila urllib.requests, thus do sio use directly.
"""
# Testing ni done through test_urllib.

eleza url2pathname(url):
    """OS-specific conversion kutoka a relative URL of the 'file' scheme
    to a file system path; sio recommended kila general use."""
    # e.g.
    #   ///C|/foo/bar/spam.foo
    # na
    #   ///C:/foo/bar/spam.foo
    # become
    #   C:\foo\bar\spam.foo
    agiza string, urllib.parse
    # Windows itself uses ":" even kwenye URLs.
    url = url.replace(':', '|')
    ikiwa sio '|' kwenye url:
        # No drive specifier, just convert slashes
        ikiwa url[:4] == '////':
            # path ni something like ////host/path/on/remote/host
            # convert this to \\host\path\on\remote\host
            # (notice halving of slashes at the start of the path)
            url = url[2:]
        components = url.split('/')
        # make sure sio to convert quoted slashes :-)
        rudisha urllib.parse.unquote('\\'.join(components))
    comp = url.split('|')
    ikiwa len(comp) != 2 ama comp[0][-1] haiko kwenye string.ascii_letters:
        error = 'Bad URL: ' + url
        ashiria OSError(error)
    drive = comp[0][-1].upper()
    components = comp[1].split('/')
    path = drive + ':'
    kila comp kwenye components:
        ikiwa comp:
            path = path + '\\' + urllib.parse.unquote(comp)
    # Issue #11474 - handing url such kama |c/|
    ikiwa path.endswith(':') na url.endswith('/'):
        path += '\\'
    rudisha path

eleza pathname2url(p):
    """OS-specific conversion kutoka a file system path to a relative URL
    of the 'file' scheme; sio recommended kila general use."""
    # e.g.
    #   C:\foo\bar\spam.foo
    # becomes
    #   ///C:/foo/bar/spam.foo
    agiza urllib.parse
    ikiwa sio ':' kwenye p:
        # No drive specifier, just convert slashes na quote the name
        ikiwa p[:2] == '\\\\':
        # path ni something like \\host\path\on\remote\host
        # convert this to ////host/path/on/remote/host
        # (notice doubling of slashes at the start of the path)
            p = '\\\\' + p
        components = p.split('\\')
        rudisha urllib.parse.quote('/'.join(components))
    comp = p.split(':')
    ikiwa len(comp) != 2 ama len(comp[0]) > 1:
        error = 'Bad path: ' + p
        ashiria OSError(error)

    drive = urllib.parse.quote(comp[0].upper())
    components = comp[1].split('\\')
    path = '///' + drive + ':'
    kila comp kwenye components:
        ikiwa comp:
            path = path + '/' + urllib.parse.quote(comp)
    rudisha path
