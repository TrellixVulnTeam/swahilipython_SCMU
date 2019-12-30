"""Miscellaneous WSGI-related Utilities"""

agiza posixpath

__all__ = [
    'FileWrapper', 'guess_scheme', 'application_uri', 'request_uri',
    'shift_path_info', 'setup_testing_defaults',
]


kundi FileWrapper:
    """Wrapper to convert file-like objects to iterables"""

    eleza __init__(self, filelike, blksize=8192):
        self.filelike = filelike
        self.blksize = blksize
        ikiwa hasattr(filelike,'close'):
            self.close = filelike.close

    eleza __getitem__(self,key):
        agiza warnings
        warnings.warn(
            "FileWrapper's __getitem__ method ignores 'key' parameter. "
            "Use iterator protocol instead.",
            DeprecationWarning,
            stacklevel=2
        )
        data = self.filelike.read(self.blksize)
        ikiwa data:
            rudisha data
        ashiria IndexError

    eleza __iter__(self):
        rudisha self

    eleza __next__(self):
        data = self.filelike.read(self.blksize)
        ikiwa data:
            rudisha data
        ashiria StopIteration

eleza guess_scheme(environ):
    """Return a guess kila whether 'wsgi.url_scheme' should be 'http' ama 'https'
    """
    ikiwa environ.get("HTTPS") kwenye ('yes','on','1'):
        rudisha 'https'
    isipokua:
        rudisha 'http'

eleza application_uri(environ):
    """Return the application's base URI (no PATH_INFO ama QUERY_STRING)"""
    url = environ['wsgi.url_scheme']+'://'
    kutoka urllib.parse agiza quote

    ikiwa environ.get('HTTP_HOST'):
        url += environ['HTTP_HOST']
    isipokua:
        url += environ['SERVER_NAME']

        ikiwa environ['wsgi.url_scheme'] == 'https':
            ikiwa environ['SERVER_PORT'] != '443':
                url += ':' + environ['SERVER_PORT']
        isipokua:
            ikiwa environ['SERVER_PORT'] != '80':
                url += ':' + environ['SERVER_PORT']

    url += quote(environ.get('SCRIPT_NAME') ama '/', encoding='latin1')
    rudisha url

eleza request_uri(environ, include_query=Kweli):
    """Return the full request URI, optionally including the query string"""
    url = application_uri(environ)
    kutoka urllib.parse agiza quote
    path_info = quote(environ.get('PATH_INFO',''), safe='/;=,', encoding='latin1')
    ikiwa sio environ.get('SCRIPT_NAME'):
        url += path_info[1:]
    isipokua:
        url += path_info
    ikiwa include_query na environ.get('QUERY_STRING'):
        url += '?' + environ['QUERY_STRING']
    rudisha url

eleza shift_path_info(environ):
    """Shift a name kutoka PATH_INFO to SCRIPT_NAME, returning it

    If there are no remaining path segments kwenye PATH_INFO, rudisha Tupu.
    Note: 'environ' ni modified in-place; use a copy ikiwa you need to keep
    the original PATH_INFO ama SCRIPT_NAME.

    Note: when PATH_INFO ni just a '/', this returns '' na appends a trailing
    '/' to SCRIPT_NAME, even though empty path segments are normally ignored,
    na SCRIPT_NAME doesn't normally end kwenye a '/'.  This ni intentional
    behavior, to ensure that an application can tell the difference between
    '/x' na '/x/' when traversing to objects.
    """
    path_info = environ.get('PATH_INFO','')
    ikiwa sio path_info:
        rudisha Tupu

    path_parts = path_info.split('/')
    path_parts[1:-1] = [p kila p kwenye path_parts[1:-1] ikiwa p na p != '.']
    name = path_parts[1]
    toa path_parts[1]

    script_name = environ.get('SCRIPT_NAME','')
    script_name = posixpath.normpath(script_name+'/'+name)
    ikiwa script_name.endswith('/'):
        script_name = script_name[:-1]
    ikiwa sio name na sio script_name.endswith('/'):
        script_name += '/'

    environ['SCRIPT_NAME'] = script_name
    environ['PATH_INFO']   = '/'.join(path_parts)

    # Special case: '/.' on PATH_INFO doesn't get stripped,
    # because we don't strip the last element of PATH_INFO
    # ikiwa there's only one path part left.  Instead of fixing this
    # above, we fix it here so that PATH_INFO gets normalized to
    # an empty string kwenye the environ.
    ikiwa name=='.':
        name = Tupu
    rudisha name

eleza setup_testing_defaults(environ):
    """Update 'environ' ukijumuisha trivial defaults kila testing purposes

    This adds various parameters required kila WSGI, including HTTP_HOST,
    SERVER_NAME, SERVER_PORT, REQUEST_METHOD, SCRIPT_NAME, PATH_INFO,
    na all of the wsgi.* variables.  It only supplies default values,
    na does sio replace any existing settings kila these variables.

    This routine ni intended to make it easier kila unit tests of WSGI
    servers na applications to set up dummy environments.  It should *not*
    be used by actual WSGI servers ama applications, since the data ni fake!
    """

    environ.setdefault('SERVER_NAME','127.0.0.1')
    environ.setdefault('SERVER_PROTOCOL','HTTP/1.0')

    environ.setdefault('HTTP_HOST',environ['SERVER_NAME'])
    environ.setdefault('REQUEST_METHOD','GET')

    ikiwa 'SCRIPT_NAME' haiko kwenye environ na 'PATH_INFO' haiko kwenye environ:
        environ.setdefault('SCRIPT_NAME','')
        environ.setdefault('PATH_INFO','/')

    environ.setdefault('wsgi.version', (1,0))
    environ.setdefault('wsgi.run_once', 0)
    environ.setdefault('wsgi.multithread', 0)
    environ.setdefault('wsgi.multiprocess', 0)

    kutoka io agiza StringIO, BytesIO
    environ.setdefault('wsgi.input', BytesIO())
    environ.setdefault('wsgi.errors', StringIO())
    environ.setdefault('wsgi.url_scheme',guess_scheme(environ))

    ikiwa environ['wsgi.url_scheme']=='http':
        environ.setdefault('SERVER_PORT', '80')
    lasivyo environ['wsgi.url_scheme']=='https':
        environ.setdefault('SERVER_PORT', '443')



_hoppish = {
    'connection', 'keep-alive', 'proxy-authenticate',
    'proxy-authorization', 'te', 'trailers', 'transfer-encoding',
    'upgrade'
}.__contains__

eleza is_hop_by_hop(header_name):
    """Return true ikiwa 'header_name' ni an HTTP/1.1 "Hop-by-Hop" header"""
    rudisha _hoppish(header_name.lower())
