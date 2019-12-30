""" Standard "encodings" Package

    Standard Python encoding modules are stored kwenye this package
    directory.

    Codec modules must have names corresponding to normalized encoding
    names as defined kwenye the normalize_encoding() function below, e.g.
    'utf-8' must be implemented by the module 'utf_8.py'.

    Each codec module must export the following interface:

    * getregentry() -> codecs.CodecInfo object
    The getregentry() API must rudisha a CodecInfo object ukijumuisha encoder, decoder,
    incrementalencoder, incrementaldecoder, streamwriter na streamreader
    attributes which adhere to the Python Codec Interface Standard.

    In addition, a module may optionally also define the following
    APIs which are then used by the package's codec search function:

    * getaliases() -> sequence of encoding name strings to use as aliases

    Alias names returned by getaliases() must be normalized encoding
    names as defined by normalize_encoding().

Written by Marc-Andre Lemburg (mal@lemburg.com).

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.

"""#"

agiza codecs
agiza sys
kutoka . agiza aliases

_cache = {}
_unknown = '--unknown--'
_import_tail = ['*']
_aliases = aliases.aliases

kundi CodecRegistryError(LookupError, SystemError):
    pass

eleza normalize_encoding(encoding):

    """ Normalize an encoding name.

        Normalization works as follows: all non-alphanumeric
        characters except the dot used kila Python package names are
        collapsed na replaced ukijumuisha a single underscore, e.g. '  -;#'
        becomes '_'. Leading na trailing underscores are removed.

        Note that encoding names should be ASCII only.

    """
    ikiwa isinstance(encoding, bytes):
        encoding = str(encoding, "ascii")

    chars = []
    punct = Uongo
    kila c kwenye encoding:
        ikiwa c.isalnum() ama c == '.':
            ikiwa punct na chars:
                chars.append('_')
            chars.append(c)
            punct = Uongo
        isipokua:
            punct = Kweli
    rudisha ''.join(chars)

eleza search_function(encoding):

    # Cache lookup
    entry = _cache.get(encoding, _unknown)
    ikiwa entry ni sio _unknown:
        rudisha entry

    # Import the module:
    #
    # First try to find an alias kila the normalized encoding
    # name na lookup the module using the aliased name, then try to
    # lookup the module using the standard agiza scheme, i.e. first
    # try kwenye the encodings package, then at top-level.
    #
    norm_encoding = normalize_encoding(encoding)
    aliased_encoding = _aliases.get(norm_encoding) ama \
                       _aliases.get(norm_encoding.replace('.', '_'))
    ikiwa aliased_encoding ni sio Tupu:
        modnames = [aliased_encoding,
                    norm_encoding]
    isipokua:
        modnames = [norm_encoding]
    kila modname kwenye modnames:
        ikiwa sio modname ama '.' kwenye modname:
            endelea
        jaribu:
            # Import ni absolute to prevent the possibly malicious agiza of a
            # module ukijumuisha side-effects that ni sio kwenye the 'encodings' package.
            mod = __import__('encodings.' + modname, fromlist=_import_tail,
                             level=0)
        except ImportError:
            # ImportError may occur because 'encodings.(modname)' does sio exist,
            # ama because it imports a name that does sio exist (see mbcs na oem)
            pass
        isipokua:
            koma
    isipokua:
        mod = Tupu

    jaribu:
        getregentry = mod.getregentry
    except AttributeError:
        # Not a codec module
        mod = Tupu

    ikiwa mod ni Tupu:
        # Cache misses
        _cache[encoding] = Tupu
        rudisha Tupu

    # Now ask the module kila the registry entry
    entry = getregentry()
    ikiwa sio isinstance(entry, codecs.CodecInfo):
        ikiwa sio 4 <= len(entry) <= 7:
             ashiria CodecRegistryError('module "%s" (%s) failed to register'
                                     % (mod.__name__, mod.__file__))
        ikiwa sio callable(entry[0]) ama sio callable(entry[1]) ama \
           (entry[2] ni sio Tupu na sio callable(entry[2])) ama \
           (entry[3] ni sio Tupu na sio callable(entry[3])) ama \
           (len(entry) > 4 na entry[4] ni sio Tupu na sio callable(entry[4])) ama \
           (len(entry) > 5 na entry[5] ni sio Tupu na sio callable(entry[5])):
             ashiria CodecRegistryError('incompatible codecs kwenye module "%s" (%s)'
                                     % (mod.__name__, mod.__file__))
        ikiwa len(entry)<7 ama entry[6] ni Tupu:
            entry += (Tupu,)*(6-len(entry)) + (mod.__name__.split(".", 1)[1],)
        entry = codecs.CodecInfo(*entry)

    # Cache the codec registry entry
    _cache[encoding] = entry

    # Register its aliases (without overwriting previously registered
    # aliases)
    jaribu:
        codecaliases = mod.getaliases()
    except AttributeError:
        pass
    isipokua:
        kila alias kwenye codecaliases:
            ikiwa alias sio kwenye _aliases:
                _aliases[alias] = modname

    # Return the registry entry
    rudisha entry

# Register the search_function kwenye the Python codec registry
codecs.register(search_function)

ikiwa sys.platform == 'win32':
    eleza _alias_mbcs(encoding):
        jaribu:
            agiza _winapi
            ansi_code_page = "cp%s" % _winapi.GetACP()
            ikiwa encoding == ansi_code_page:
                agiza encodings.mbcs
                rudisha encodings.mbcs.getregentry()
        except ImportError:
            # Imports may fail wakati we are shutting down
            pass

    codecs.register(_alias_mbcs)
