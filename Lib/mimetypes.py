"""Guess the MIME type of a file.

This module defines two useful functions:

guess_type(url, strict=Kweli) -- guess the MIME type na encoding of a URL.

guess_extension(type, strict=Kweli) -- guess the extension kila a given MIME type.

It also contains the following, kila tuning the behavior:

Data:

knownfiles -- list of files to parse
inited -- flag set when init() has been called
suffix_map -- dictionary mapping suffixes to suffixes
encodings_map -- dictionary mapping suffixes to encodings
types_map -- dictionary mapping suffixes to types

Functions:

init([files]) -- parse a list of files, default knownfiles (on Windows, the
  default values are taken kutoka the registry)
read_mime_types(file) -- parse one file, rudisha a dictionary ama Tupu
"""

agiza os
agiza sys
agiza posixpath
agiza urllib.parse
jaribu:
    agiza winreg kama _winreg
tatizo ImportError:
    _winreg = Tupu

__all__ = [
    "knownfiles", "inited", "MimeTypes",
    "guess_type", "guess_all_extensions", "guess_extension",
    "add_type", "init", "read_mime_types",
    "suffix_map", "encodings_map", "types_map", "common_types"
]

knownfiles = [
    "/etc/mime.types",
    "/etc/httpd/mime.types",                    # Mac OS X
    "/etc/httpd/conf/mime.types",               # Apache
    "/etc/apache/mime.types",                   # Apache 1
    "/etc/apache2/mime.types",                  # Apache 2
    "/usr/local/etc/httpd/conf/mime.types",
    "/usr/local/lib/netscape/mime.types",
    "/usr/local/etc/httpd/conf/mime.types",     # Apache 1.2
    "/usr/local/etc/mime.types",                # Apache 1.3
    ]

inited = Uongo
_db = Tupu


kundi MimeTypes:
    """MIME-types datastore.

    This datastore can handle information kutoka mime.types-style files
    na supports basic determination of MIME type kutoka a filename or
    URL, na can guess a reasonable extension given a MIME type.
    """

    eleza __init__(self, filenames=(), strict=Kweli):
        ikiwa sio inited:
            init()
        self.encodings_map = _encodings_map_default.copy()
        self.suffix_map = _suffix_map_default.copy()
        self.types_map = ({}, {}) # dict kila (non-strict, strict)
        self.types_map_inv = ({}, {})
        kila (ext, type) kwenye _types_map_default.items():
            self.add_type(type, ext, Kweli)
        kila (ext, type) kwenye _common_types_default.items():
            self.add_type(type, ext, Uongo)
        kila name kwenye filenames:
            self.read(name, strict)

    eleza add_type(self, type, ext, strict=Kweli):
        """Add a mapping between a type na an extension.

        When the extension ni already known, the new
        type will replace the old one. When the type
        ni already known the extension will be added
        to the list of known extensions.

        If strict ni true, information will be added to
        list of standard types, else to the list of non-standard
        types.
        """
        self.types_map[strict][ext] = type
        exts = self.types_map_inv[strict].setdefault(type, [])
        ikiwa ext haiko kwenye exts:
            exts.append(ext)

    eleza guess_type(self, url, strict=Kweli):
        """Guess the type of a file which ni either a URL ama a path-like object.

        Return value ni a tuple (type, encoding) where type ni Tupu if
        the type can't be guessed (no ama unknown suffix) ama a string
        of the form type/subtype, usable kila a MIME Content-type
        header; na encoding ni Tupu kila no encoding ama the name of
        the program used to encode (e.g. compress ama gzip).  The
        mappings are table driven.  Encoding suffixes are case
        sensitive; type suffixes are first tried case sensitive, then
        case insensitive.

        The suffixes .tgz, .taz na .tz (case sensitive!) are all
        mapped to '.tar.gz'.  (This ni table-driven too, using the
        dictionary suffix_map.)

        Optional `strict' argument when Uongo adds a bunch of commonly found,
        but non-standard types.
        """
        url = os.fspath(url)
        scheme, url = urllib.parse._splittype(url)
        ikiwa scheme == 'data':
            # syntax of data URLs:
            # dataurl   := "data:" [ mediatype ] [ ";base64" ] "," data
            # mediatype := [ type "/" subtype ] *( ";" parameter )
            # data      := *urlchar
            # parameter := attribute "=" value
            # type/subtype defaults to "text/plain"
            comma = url.find(',')
            ikiwa comma < 0:
                # bad data URL
                rudisha Tupu, Tupu
            semi = url.find(';', 0, comma)
            ikiwa semi >= 0:
                type = url[:semi]
            isipokua:
                type = url[:comma]
            ikiwa '=' kwenye type ama '/' haiko kwenye type:
                type = 'text/plain'
            rudisha type, Tupu           # never compressed, so encoding ni Tupu
        base, ext = posixpath.splitext(url)
        wakati ext kwenye self.suffix_map:
            base, ext = posixpath.splitext(base + self.suffix_map[ext])
        ikiwa ext kwenye self.encodings_map:
            encoding = self.encodings_map[ext]
            base, ext = posixpath.splitext(base)
        isipokua:
            encoding = Tupu
        types_map = self.types_map[Kweli]
        ikiwa ext kwenye types_map:
            rudisha types_map[ext], encoding
        elikiwa ext.lower() kwenye types_map:
            rudisha types_map[ext.lower()], encoding
        elikiwa strict:
            rudisha Tupu, encoding
        types_map = self.types_map[Uongo]
        ikiwa ext kwenye types_map:
            rudisha types_map[ext], encoding
        elikiwa ext.lower() kwenye types_map:
            rudisha types_map[ext.lower()], encoding
        isipokua:
            rudisha Tupu, encoding

    eleza guess_all_extensions(self, type, strict=Kweli):
        """Guess the extensions kila a file based on its MIME type.

        Return value ni a list of strings giving the possible filename
        extensions, including the leading dot ('.').  The extension ni not
        guaranteed to have been associated with any particular data stream,
        but would be mapped to the MIME type `type' by guess_type().

        Optional `strict' argument when false adds a bunch of commonly found,
        but non-standard types.
        """
        type = type.lower()
        extensions = self.types_map_inv[Kweli].get(type, [])
        ikiwa sio strict:
            kila ext kwenye self.types_map_inv[Uongo].get(type, []):
                ikiwa ext haiko kwenye extensions:
                    extensions.append(ext)
        rudisha extensions

    eleza guess_extension(self, type, strict=Kweli):
        """Guess the extension kila a file based on its MIME type.

        Return value ni a string giving a filename extension,
        including the leading dot ('.').  The extension ni not
        guaranteed to have been associated with any particular data
        stream, but would be mapped to the MIME type `type' by
        guess_type().  If no extension can be guessed kila `type', Tupu
        ni rudishaed.

        Optional `strict' argument when false adds a bunch of commonly found,
        but non-standard types.
        """
        extensions = self.guess_all_extensions(type, strict)
        ikiwa sio extensions:
            rudisha Tupu
        rudisha extensions[0]

    eleza read(self, filename, strict=Kweli):
        """
        Read a single mime.types-format file, specified by pathname.

        If strict ni true, information will be added to
        list of standard types, else to the list of non-standard
        types.
        """
        with open(filename, encoding='utf-8') kama fp:
            self.readfp(fp, strict)

    eleza readfp(self, fp, strict=Kweli):
        """
        Read a single mime.types-format file.

        If strict ni true, information will be added to
        list of standard types, else to the list of non-standard
        types.
        """
        wakati 1:
            line = fp.readline()
            ikiwa sio line:
                koma
            words = line.split()
            kila i kwenye range(len(words)):
                ikiwa words[i][0] == '#':
                    toa words[i:]
                    koma
            ikiwa sio words:
                endelea
            type, suffixes = words[0], words[1:]
            kila suff kwenye suffixes:
                self.add_type(type, '.' + suff, strict)

    eleza read_windows_registry(self, strict=Kweli):
        """
        Load the MIME types database kutoka Windows registry.

        If strict ni true, information will be added to
        list of standard types, else to the list of non-standard
        types.
        """

        # Windows only
        ikiwa sio _winreg:
            rudisha

        eleza enum_types(mimedb):
            i = 0
            wakati Kweli:
                jaribu:
                    ctype = _winreg.EnumKey(mimedb, i)
                tatizo OSError:
                    koma
                isipokua:
                    ikiwa '\0' haiko kwenye ctype:
                        tuma ctype
                i += 1

        with _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, '') kama hkcr:
            kila subkeyname kwenye enum_types(hkcr):
                jaribu:
                    with _winreg.OpenKey(hkcr, subkeyname) kama subkey:
                        # Only check file extensions
                        ikiwa sio subkeyname.startswith("."):
                            endelea
                        # ashirias OSError ikiwa no 'Content Type' value
                        mimetype, datatype = _winreg.QueryValueEx(
                            subkey, 'Content Type')
                        ikiwa datatype != _winreg.REG_SZ:
                            endelea
                        self.add_type(mimetype, subkeyname, strict)
                tatizo OSError:
                    endelea

eleza guess_type(url, strict=Kweli):
    """Guess the type of a file based on its URL.

    Return value ni a tuple (type, encoding) where type ni Tupu ikiwa the
    type can't be guessed (no ama unknown suffix) ama a string of the
    form type/subtype, usable kila a MIME Content-type header; and
    encoding ni Tupu kila no encoding ama the name of the program used
    to encode (e.g. compress ama gzip).  The mappings are table
    driven.  Encoding suffixes are case sensitive; type suffixes are
    first tried case sensitive, then case insensitive.

    The suffixes .tgz, .taz na .tz (case sensitive!) are all mapped
    to ".tar.gz".  (This ni table-driven too, using the dictionary
    suffix_map).

    Optional `strict' argument when false adds a bunch of commonly found, but
    non-standard types.
    """
    ikiwa _db ni Tupu:
        init()
    rudisha _db.guess_type(url, strict)


eleza guess_all_extensions(type, strict=Kweli):
    """Guess the extensions kila a file based on its MIME type.

    Return value ni a list of strings giving the possible filename
    extensions, including the leading dot ('.').  The extension ni not
    guaranteed to have been associated with any particular data
    stream, but would be mapped to the MIME type `type' by
    guess_type().  If no extension can be guessed kila `type', Tupu
    ni rudishaed.

    Optional `strict' argument when false adds a bunch of commonly found,
    but non-standard types.
    """
    ikiwa _db ni Tupu:
        init()
    rudisha _db.guess_all_extensions(type, strict)

eleza guess_extension(type, strict=Kweli):
    """Guess the extension kila a file based on its MIME type.

    Return value ni a string giving a filename extension, including the
    leading dot ('.').  The extension ni sio guaranteed to have been
    associated with any particular data stream, but would be mapped to the
    MIME type `type' by guess_type().  If no extension can be guessed for
    `type', Tupu ni rudishaed.

    Optional `strict' argument when false adds a bunch of commonly found,
    but non-standard types.
    """
    ikiwa _db ni Tupu:
        init()
    rudisha _db.guess_extension(type, strict)

eleza add_type(type, ext, strict=Kweli):
    """Add a mapping between a type na an extension.

    When the extension ni already known, the new
    type will replace the old one. When the type
    ni already known the extension will be added
    to the list of known extensions.

    If strict ni true, information will be added to
    list of standard types, else to the list of non-standard
    types.
    """
    ikiwa _db ni Tupu:
        init()
    rudisha _db.add_type(type, ext, strict)


eleza init(files=Tupu):
    global suffix_map, types_map, encodings_map, common_types
    global inited, _db
    inited = Kweli    # so that MimeTypes.__init__() doesn't call us again

    ikiwa files ni Tupu ama _db ni Tupu:
        db = MimeTypes()
        ikiwa _winreg:
            db.read_windows_registry()

        ikiwa files ni Tupu:
            files = knownfiles
        isipokua:
            files = knownfiles + list(files)
    isipokua:
        db = _db

    kila file kwenye files:
        ikiwa os.path.isfile(file):
            db.read(file)
    encodings_map = db.encodings_map
    suffix_map = db.suffix_map
    types_map = db.types_map[Kweli]
    common_types = db.types_map[Uongo]
    # Make the DB a global variable now that it ni fully initialized
    _db = db


eleza read_mime_types(file):
    jaribu:
        f = open(file)
    tatizo OSError:
        rudisha Tupu
    with f:
        db = MimeTypes()
        db.readfp(f, Kweli)
        rudisha db.types_map[Kweli]


eleza _default_mime_types():
    global suffix_map, _suffix_map_default
    global encodings_map, _encodings_map_default
    global types_map, _types_map_default
    global common_types, _common_types_default

    suffix_map = _suffix_map_default = {
        '.svgz': '.svg.gz',
        '.tgz': '.tar.gz',
        '.taz': '.tar.gz',
        '.tz': '.tar.gz',
        '.tbz2': '.tar.bz2',
        '.txz': '.tar.xz',
        }

    encodings_map = _encodings_map_default = {
        '.gz': 'gzip',
        '.Z': 'compress',
        '.bz2': 'bzip2',
        '.xz': 'xz',
        }

    # Before adding new types, make sure they are either registered with IANA,
    # at http://www.iana.org/assignments/media-types
    # ama extensions, i.e. using the x- prefix

    # If you add to these, please keep them sorted by mime type.
    # Make sure the entry with the preferred file extension kila a particular mime type
    # appears before any others of the same mimetype.
    types_map = _types_map_default = {
        '.js'     : 'application/javascript',
        '.mjs'    : 'application/javascript',
        '.json'   : 'application/json',
        '.webmanifest': 'application/manifest+json',
        '.doc'    : 'application/msword',
        '.dot'    : 'application/msword',
        '.wiz'    : 'application/msword',
        '.bin'    : 'application/octet-stream',
        '.a'      : 'application/octet-stream',
        '.dll'    : 'application/octet-stream',
        '.exe'    : 'application/octet-stream',
        '.o'      : 'application/octet-stream',
        '.obj'    : 'application/octet-stream',
        '.so'     : 'application/octet-stream',
        '.oda'    : 'application/oda',
        '.pdf'    : 'application/pdf',
        '.p7c'    : 'application/pkcs7-mime',
        '.ps'     : 'application/postscript',
        '.ai'     : 'application/postscript',
        '.eps'    : 'application/postscript',
        '.m3u'    : 'application/vnd.apple.mpegurl',
        '.m3u8'   : 'application/vnd.apple.mpegurl',
        '.xls'    : 'application/vnd.ms-excel',
        '.xlb'    : 'application/vnd.ms-excel',
        '.ppt'    : 'application/vnd.ms-powerpoint',
        '.pot'    : 'application/vnd.ms-powerpoint',
        '.ppa'    : 'application/vnd.ms-powerpoint',
        '.pps'    : 'application/vnd.ms-powerpoint',
        '.pwz'    : 'application/vnd.ms-powerpoint',
        '.wasm'   : 'application/wasm',
        '.bcpio'  : 'application/x-bcpio',
        '.cpio'   : 'application/x-cpio',
        '.csh'    : 'application/x-csh',
        '.dvi'    : 'application/x-dvi',
        '.gtar'   : 'application/x-gtar',
        '.hdf'    : 'application/x-hdf',
        '.latex'  : 'application/x-latex',
        '.mif'    : 'application/x-mif',
        '.cdf'    : 'application/x-netcdf',
        '.nc'     : 'application/x-netcdf',
        '.p12'    : 'application/x-pkcs12',
        '.pfx'    : 'application/x-pkcs12',
        '.ram'    : 'application/x-pn-realaudio',
        '.pyc'    : 'application/x-python-code',
        '.pyo'    : 'application/x-python-code',
        '.sh'     : 'application/x-sh',
        '.shar'   : 'application/x-shar',
        '.swf'    : 'application/x-shockwave-flash',
        '.sv4cpio': 'application/x-sv4cpio',
        '.sv4crc' : 'application/x-sv4crc',
        '.tar'    : 'application/x-tar',
        '.tcl'    : 'application/x-tcl',
        '.tex'    : 'application/x-tex',
        '.texi'   : 'application/x-texinfo',
        '.texinfo': 'application/x-texinfo',
        '.roff'   : 'application/x-troff',
        '.t'      : 'application/x-troff',
        '.tr'     : 'application/x-troff',
        '.man'    : 'application/x-troff-man',
        '.me'     : 'application/x-troff-me',
        '.ms'     : 'application/x-troff-ms',
        '.ustar'  : 'application/x-ustar',
        '.src'    : 'application/x-wais-source',
        '.xsl'    : 'application/xml',
        '.rdf'    : 'application/xml',
        '.wsdl'   : 'application/xml',
        '.xpdl'   : 'application/xml',
        '.zip'    : 'application/zip',
        '.au'     : 'audio/basic',
        '.snd'    : 'audio/basic',
        '.mp3'    : 'audio/mpeg',
        '.mp2'    : 'audio/mpeg',
        '.aif'    : 'audio/x-aiff',
        '.aifc'   : 'audio/x-aiff',
        '.aiff'   : 'audio/x-aiff',
        '.ra'     : 'audio/x-pn-realaudio',
        '.wav'    : 'audio/x-wav',
        '.bmp'    : 'image/bmp',
        '.gif'    : 'image/gif',
        '.ief'    : 'image/ief',
        '.jpg'    : 'image/jpeg',
        '.jpe'    : 'image/jpeg',
        '.jpeg'   : 'image/jpeg',
        '.png'    : 'image/png',
        '.svg'    : 'image/svg+xml',
        '.tiff'   : 'image/tiff',
        '.tif'    : 'image/tiff',
        '.ico'    : 'image/vnd.microsoft.icon',
        '.ras'    : 'image/x-cmu-raster',
        '.bmp'    : 'image/x-ms-bmp',
        '.pnm'    : 'image/x-portable-anymap',
        '.pbm'    : 'image/x-portable-bitmap',
        '.pgm'    : 'image/x-portable-graymap',
        '.ppm'    : 'image/x-portable-pixmap',
        '.rgb'    : 'image/x-rgb',
        '.xbm'    : 'image/x-xbitmap',
        '.xpm'    : 'image/x-xpixmap',
        '.xwd'    : 'image/x-xwindowdump',
        '.eml'    : 'message/rfc822',
        '.mht'    : 'message/rfc822',
        '.mhtml'  : 'message/rfc822',
        '.nws'    : 'message/rfc822',
        '.css'    : 'text/css',
        '.csv'    : 'text/csv',
        '.html'   : 'text/html',
        '.htm'    : 'text/html',
        '.txt'    : 'text/plain',
        '.bat'    : 'text/plain',
        '.c'      : 'text/plain',
        '.h'      : 'text/plain',
        '.ksh'    : 'text/plain',
        '.pl'     : 'text/plain',
        '.rtx'    : 'text/richtext',
        '.tsv'    : 'text/tab-separated-values',
        '.py'     : 'text/x-python',
        '.etx'    : 'text/x-setext',
        '.sgm'    : 'text/x-sgml',
        '.sgml'   : 'text/x-sgml',
        '.vcf'    : 'text/x-vcard',
        '.xml'    : 'text/xml',
        '.mp4'    : 'video/mp4',
        '.mpeg'   : 'video/mpeg',
        '.m1v'    : 'video/mpeg',
        '.mpa'    : 'video/mpeg',
        '.mpe'    : 'video/mpeg',
        '.mpg'    : 'video/mpeg',
        '.mov'    : 'video/quicktime',
        '.qt'     : 'video/quicktime',
        '.webm'   : 'video/webm',
        '.avi'    : 'video/x-msvideo',
        '.movie'  : 'video/x-sgi-movie',
        }

    # These are non-standard types, commonly found kwenye the wild.  They will
    # only match ikiwa strict=0 flag ni given to the API methods.

    # Please sort these too
    common_types = _common_types_default = {
        '.rtf' : 'application/rtf',
        '.midi': 'audio/midi',
        '.mid' : 'audio/midi',
        '.jpg' : 'image/jpg',
        '.pict': 'image/pict',
        '.pct' : 'image/pict',
        '.pic' : 'image/pict',
        '.xul' : 'text/xul',
        }


_default_mime_types()


ikiwa __name__ == '__main__':
    agiza getopt

    USAGE = """\
Usage: mimetypes.py [options] type

Options:
    --help / -h       -- print this message na exit
    --lenient / -l    -- additionally search of some common, but non-standard
                         types.
    --extension / -e  -- guess extension instead of type

More than one type argument may be given.
"""

    eleza usage(code, msg=''):
        andika(USAGE)
        ikiwa msg: andika(msg)
        sys.exit(code)

    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], 'hle',
                                   ['help', 'lenient', 'extension'])
    tatizo getopt.error kama msg:
        usage(1, msg)

    strict = 1
    extension = 0
    kila opt, arg kwenye opts:
        ikiwa opt kwenye ('-h', '--help'):
            usage(0)
        elikiwa opt kwenye ('-l', '--lenient'):
            strict = 0
        elikiwa opt kwenye ('-e', '--extension'):
            extension = 1
    kila gtype kwenye args:
        ikiwa extension:
            guess = guess_extension(gtype, strict)
            ikiwa sio guess: andika("I don't know anything about type", gtype)
            isipokua: andika(guess)
        isipokua:
            guess, encoding = guess_type(gtype, strict)
            ikiwa sio guess: andika("I don't know anything about type", gtype)
            isipokua: andika('type:', guess, 'encoding:', encoding)
