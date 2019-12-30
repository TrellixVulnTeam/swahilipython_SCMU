"""Cache lines kutoka Python source files.

This ni intended to read lines kutoka modules imported -- hence ikiwa a filename
is sio found, it will look down the module search path kila a file by
that name.
"""

agiza functools
agiza sys
agiza os
agiza tokenize

__all__ = ["getline", "clearcache", "checkcache"]

eleza getline(filename, lineno, module_globals=Tupu):
    lines = getlines(filename, module_globals)
    ikiwa 1 <= lineno <= len(lines):
        rudisha lines[lineno-1]
    isipokua:
        rudisha ''


# The cache

# The cache. Maps filenames to either a thunk which will provide source code,
# ama a tuple (size, mtime, lines, fullname) once loaded.
cache = {}


eleza clearcache():
    """Clear the cache entirely."""

    global cache
    cache = {}


eleza getlines(filename, module_globals=Tupu):
    """Get the lines kila a Python source file kutoka the cache.
    Update the cache ikiwa it doesn't contain an entry kila this file already."""

    ikiwa filename kwenye cache:
        entry = cache[filename]
        ikiwa len(entry) != 1:
            rudisha cache[filename][2]

    jaribu:
        rudisha updatecache(filename, module_globals)
    tatizo MemoryError:
        clearcache()
        rudisha []


eleza checkcache(filename=Tupu):
    """Discard cache entries that are out of date.
    (This ni sio checked upon each call!)"""

    ikiwa filename ni Tupu:
        filenames = list(cache.keys())
    isipokua:
        ikiwa filename kwenye cache:
            filenames = [filename]
        isipokua:
            return

    kila filename kwenye filenames:
        entry = cache[filename]
        ikiwa len(entry) == 1:
            # lazy cache entry, leave it lazy.
            endelea
        size, mtime, lines, fullname = entry
        ikiwa mtime ni Tupu:
            endelea   # no-op kila files loaded via a __loader__
        jaribu:
            stat = os.stat(fullname)
        tatizo OSError:
            toa cache[filename]
            endelea
        ikiwa size != stat.st_size ama mtime != stat.st_mtime:
            toa cache[filename]


eleza updatecache(filename, module_globals=Tupu):
    """Update a cache entry na rudisha its list of lines.
    If something's wrong, print a message, discard the cache entry,
    na rudisha an empty list."""

    ikiwa filename kwenye cache:
        ikiwa len(cache[filename]) != 1:
            toa cache[filename]
    ikiwa sio filename ama (filename.startswith('<') na filename.endswith('>')):
        rudisha []

    fullname = filename
    jaribu:
        stat = os.stat(fullname)
    tatizo OSError:
        basename = filename

        # Realise a lazy loader based lookup ikiwa there ni one
        # otherwise try to lookup right now.
        ikiwa lazycache(filename, module_globals):
            jaribu:
                data = cache[filename][0]()
            tatizo (ImportError, OSError):
                pita
            isipokua:
                ikiwa data ni Tupu:
                    # No luck, the PEP302 loader cannot find the source
                    # kila this module.
                    rudisha []
                cache[filename] = (
                    len(data), Tupu,
                    [line+'\n' kila line kwenye data.splitlines()], fullname
                )
                rudisha cache[filename][2]

        # Try looking through the module search path, which ni only useful
        # when handling a relative filename.
        ikiwa os.path.isabs(filename):
            rudisha []

        kila dirname kwenye sys.path:
            jaribu:
                fullname = os.path.join(dirname, basename)
            tatizo (TypeError, AttributeError):
                # Not sufficiently string-like to do anything useful with.
                endelea
            jaribu:
                stat = os.stat(fullname)
                koma
            tatizo OSError:
                pita
        isipokua:
            rudisha []
    jaribu:
        ukijumuisha tokenize.open(fullname) kama fp:
            lines = fp.readlines()
    tatizo OSError:
        rudisha []
    ikiwa lines na sio lines[-1].endswith('\n'):
        lines[-1] += '\n'
    size, mtime = stat.st_size, stat.st_mtime
    cache[filename] = size, mtime, lines, fullname
    rudisha lines


eleza lazycache(filename, module_globals):
    """Seed the cache kila filename ukijumuisha module_globals.

    The module loader will be asked kila the source only when getlines is
    called, sio immediately.

    If there ni an entry kwenye the cache already, it ni sio altered.

    :return: Kweli ikiwa a lazy load ni registered kwenye the cache,
        otherwise Uongo. To register such a load a module loader ukijumuisha a
        get_source method must be found, the filename must be a cachable
        filename, na the filename must sio be already cached.
    """
    ikiwa filename kwenye cache:
        ikiwa len(cache[filename]) == 1:
            rudisha Kweli
        isipokua:
            rudisha Uongo
    ikiwa sio filename ama (filename.startswith('<') na filename.endswith('>')):
        rudisha Uongo
    # Try kila a __loader__, ikiwa available
    ikiwa module_globals na '__loader__' kwenye module_globals:
        name = module_globals.get('__name__')
        loader = module_globals['__loader__']
        get_source = getattr(loader, 'get_source', Tupu)

        ikiwa name na get_source:
            get_lines = functools.partial(get_source, name)
            cache[filename] = (get_lines,)
            rudisha Kweli
    rudisha Uongo
