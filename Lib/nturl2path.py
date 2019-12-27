"""Convert a NT pathname to a file URL and vice versa.

This module only exists to provide OS-specific code
for urllib.requests, thus do not use directly.
"""
# Testing is done through test_urllib.

eleza url2pathname(url):
    """OS-specific conversion kutoka a relative URL of the 'file' scheme
    to a file system path; not recommended for general use."""
    # e.g.
    #   ///C|/foo/bar/spam.foo
    # and
    #   ///C:/foo/bar/spam.foo
    # become
    #   C:\foo\bar\spam.foo
    agiza string, urllib.parse
    # Windows itself uses ":" even in URLs.
    url = url.replace(':', '|')
    ikiwa not '|' in url:
        # No drive specifier, just convert slashes
        ikiwa url[:4] == '////':
            # path is something like ////host/path/on/remote/host
            # convert this to \\host\path\on\remote\host
            # (notice halving of slashes at the start of the path)
            url = url[2:]
        components = url.split('/')
        # make sure not to convert quoted slashes :-)
        rudisha urllib.parse.unquote('\\'.join(components))
    comp = url.split('|')
    ikiwa len(comp) != 2 or comp[0][-1] not in string.ascii_letters:
        error = 'Bad URL: ' + url
        raise OSError(error)
    drive = comp[0][-1].upper()
    components = comp[1].split('/')
    path = drive + ':'
    for comp in components:
        ikiwa comp:
            path = path + '\\' + urllib.parse.unquote(comp)
    # Issue #11474 - handing url such as |c/|
    ikiwa path.endswith(':') and url.endswith('/'):
        path += '\\'
    rudisha path

eleza pathname2url(p):
    """OS-specific conversion kutoka a file system path to a relative URL
    of the 'file' scheme; not recommended for general use."""
    # e.g.
    #   C:\foo\bar\spam.foo
    # becomes
    #   ///C:/foo/bar/spam.foo
    agiza urllib.parse
    ikiwa not ':' in p:
        # No drive specifier, just convert slashes and quote the name
        ikiwa p[:2] == '\\\\':
        # path is something like \\host\path\on\remote\host
        # convert this to ////host/path/on/remote/host
        # (notice doubling of slashes at the start of the path)
            p = '\\\\' + p
        components = p.split('\\')
        rudisha urllib.parse.quote('/'.join(components))
    comp = p.split(':')
    ikiwa len(comp) != 2 or len(comp[0]) > 1:
        error = 'Bad path: ' + p
        raise OSError(error)

    drive = urllib.parse.quote(comp[0].upper())
    components = comp[1].split('\\')
    path = '///' + drive + ':'
    for comp in components:
        ikiwa comp:
            path = path + '/' + urllib.parse.quote(comp)
    rudisha path
