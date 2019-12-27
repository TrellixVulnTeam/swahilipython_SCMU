"""Cache lines kutoka Python source files.

This is intended to read lines kutoka modules imported -- hence ikiwa a filename
is not found, it will look down the module search path for a file by
that name.
"""

agiza functools
agiza sys
agiza os
agiza tokenize

__all__ = ["getline", "clearcache", "checkcache"]

eleza getline(filename, lineno, module_globals=None):
    lines = getlines(filename, module_globals)
    ikiwa 1 <= lineno <= len(lines):
        rudisha lines[lineno-1]
    else:
        rudisha ''


# The cache

# The cache. Maps filenames to either a thunk which will provide source code,
# or a tuple (size, mtime, lines, fullname) once loaded.
cache = {}


eleza clearcache():
    """Clear the cache entirely."""

    global cache
    cache = {}


eleza getlines(filename, module_globals=None):
    """Get the lines for a Python source file kutoka the cache.
    Update the cache ikiwa it doesn't contain an entry for this file already."""

    ikiwa filename in cache:
        entry = cache[filename]
        ikiwa len(entry) != 1:
            rudisha cache[filename][2]

    try:
        rudisha updatecache(filename, module_globals)
    except MemoryError:
        clearcache()
        rudisha []


eleza checkcache(filename=None):
    """Discard cache entries that are out of date.
    (This is not checked upon each call!)"""

    ikiwa filename is None:
        filenames = list(cache.keys())
    else:
        ikiwa filename in cache:
            filenames = [filename]
        else:
            return

    for filename in filenames:
        entry = cache[filename]
        ikiwa len(entry) == 1:
            # lazy cache entry, leave it lazy.
            continue
        size, mtime, lines, fullname = entry
        ikiwa mtime is None:
            continue   # no-op for files loaded via a __loader__
        try:
            stat = os.stat(fullname)
        except OSError:
            del cache[filename]
            continue
        ikiwa size != stat.st_size or mtime != stat.st_mtime:
            del cache[filename]


eleza updatecache(filename, module_globals=None):
    """Update a cache entry and rudisha its list of lines.
    If something's wrong, print a message, discard the cache entry,
    and rudisha an empty list."""

    ikiwa filename in cache:
        ikiwa len(cache[filename]) != 1:
            del cache[filename]
    ikiwa not filename or (filename.startswith('<') and filename.endswith('>')):
        rudisha []

    fullname = filename
    try:
        stat = os.stat(fullname)
    except OSError:
        basename = filename

        # Realise a lazy loader based lookup ikiwa there is one
        # otherwise try to lookup right now.
        ikiwa lazycache(filename, module_globals):
            try:
                data = cache[filename][0]()
            except (ImportError, OSError):
                pass
            else:
                ikiwa data is None:
                    # No luck, the PEP302 loader cannot find the source
                    # for this module.
                    rudisha []
                cache[filename] = (
                    len(data), None,
                    [line+'\n' for line in data.splitlines()], fullname
                )
                rudisha cache[filename][2]

        # Try looking through the module search path, which is only useful
        # when handling a relative filename.
        ikiwa os.path.isabs(filename):
            rudisha []

        for dirname in sys.path:
            try:
                fullname = os.path.join(dirname, basename)
            except (TypeError, AttributeError):
                # Not sufficiently string-like to do anything useful with.
                continue
            try:
                stat = os.stat(fullname)
                break
            except OSError:
                pass
        else:
            rudisha []
    try:
        with tokenize.open(fullname) as fp:
            lines = fp.readlines()
    except OSError:
        rudisha []
    ikiwa lines and not lines[-1].endswith('\n'):
        lines[-1] += '\n'
    size, mtime = stat.st_size, stat.st_mtime
    cache[filename] = size, mtime, lines, fullname
    rudisha lines


eleza lazycache(filename, module_globals):
    """Seed the cache for filename with module_globals.

    The module loader will be asked for the source only when getlines is
    called, not immediately.

    If there is an entry in the cache already, it is not altered.

    :return: True ikiwa a lazy load is registered in the cache,
        otherwise False. To register such a load a module loader with a
        get_source method must be found, the filename must be a cachable
        filename, and the filename must not be already cached.
    """
    ikiwa filename in cache:
        ikiwa len(cache[filename]) == 1:
            rudisha True
        else:
            rudisha False
    ikiwa not filename or (filename.startswith('<') and filename.endswith('>')):
        rudisha False
    # Try for a __loader__, ikiwa available
    ikiwa module_globals and '__loader__' in module_globals:
        name = module_globals.get('__name__')
        loader = module_globals['__loader__']
        get_source = getattr(loader, 'get_source', None)

        ikiwa name and get_source:
            get_lines = functools.partial(get_source, name)
            cache[filename] = (get_lines,)
            rudisha True
    rudisha False
