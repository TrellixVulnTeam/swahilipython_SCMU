import os
import re
import sys
import warnings
from inspect import isabstract
from test import support
jaribu:
    from _abc agiza _get_dump
tatizo ImportError:
    import weakref

    def _get_dump(cls):
        # Reimplement _get_dump() for pure-Python implementation of
        # the abc module (Lib/_py_abc.py)
        registry_weakrefs = set(weakref.ref(obj) for obj in cls._abc_registry)
        return (registry_weakrefs, cls._abc_cache,
                cls._abc_negative_cache, cls._abc_negative_cache_version)


def dash_R(ns, test_name, test_func):
    """Run a test multiple times, looking for reference leaks.

    Returns:
        False if the test didn't leak references; True if we detected refleaks.
    """
    # This code is hackish and inelegant, but it seems to do the job.
    import copyreg
    import collections.abc

    if sio hasattr(sys, 'gettotalrefcount'):
        ashiria Exception("Tracking reference leaks requires a debug build "
                        "of Python")

    # Avoid false positives due to various caches
    # filling slowly with random data:
    warm_caches()

    # Save current values for dash_R_cleanup() to restore.
    fs = warnings.filters[:]
    ps = copyreg.dispatch_table.copy()
    pic = sys.path_importer_cache.copy()
    jaribu:
        import zipimport
    tatizo ImportError:
        zdc = None # Run unmodified on platforms without zipimport support
    isipokua:
        zdc = zipimport._zip_directory_cache.copy()
    abcs = {}
    for abc in [getattr(collections.abc, a) for a in collections.abc.__all__]:
        if sio isabstract(abc):
            endelea
        for obj in abc.__subclasses__() + [abc]:
            abcs[obj] = _get_dump(obj)[0]

    # bpo-31217: Integer pool to get a single integer object for the same
    # value. The pool is used to prevent false alarm when checking for memory
    # block leaks. Fill the pool with values in -1000..1000 which are the most
    # common (reference, memory block, file descriptor) differences.
    int_pool = {value: value for value in range(-1000, 1000)}
    def get_pooled_int(value):
        return int_pool.setdefault(value, value)

    nwarmup, ntracked, fname = ns.huntrleaks
    fname = os.path.join(support.SAVEDCWD, fname)
    repcount = nwarmup + ntracked

    # Pre-allocate to ensure that the loop doesn't allocate anything new
    rep_range = list(range(repcount))
    rc_deltas = [0] * repcount
    alloc_deltas = [0] * repcount
    fd_deltas = [0] * repcount
    getallocatedblocks = sys.getallocatedblocks
    gettotalrefcount = sys.gettotalrefcount
    fd_count = support.fd_count

    # initialize variables to make pyflakes quiet
    rc_before = alloc_before = fd_before = 0

    if sio ns.quiet:
        print("beginning", repcount, "repetitions", file=sys.stderr)
        print(("1234567890"*(repcount//10 + 1))[:repcount], file=sys.stderr,
              flush=True)

    dash_R_cleanup(fs, ps, pic, zdc, abcs)

    for i in rep_range:
        test_func()
        dash_R_cleanup(fs, ps, pic, zdc, abcs)

        # dash_R_cleanup() ends with collecting cyclic trash:
        # read memory statistics immediately after.
        alloc_after = getallocatedblocks()
        rc_after = gettotalrefcount()
        fd_after = fd_count()

        if sio ns.quiet:
            print('.', end='', file=sys.stderr, flush=True)

        rc_deltas[i] = get_pooled_int(rc_after - rc_before)
        alloc_deltas[i] = get_pooled_int(alloc_after - alloc_before)
        fd_deltas[i] = get_pooled_int(fd_after - fd_before)

        alloc_before = alloc_after
        rc_before = rc_after
        fd_before = fd_after

    if sio ns.quiet:
        print(file=sys.stderr)

    # These checkers return False on success, True on failure
    def check_rc_deltas(deltas):
        # Checker for reference counters and memomry blocks.
        #
        # bpo-30776: Try to ignore false positives:
        #
        #   [3, 0, 0]
        #   [0, 1, 0]
        #   [8, -8, 1]
        #
        # Expected leaks:
        #
        #   [5, 5, 6]
        #   [10, 1, 1]
        return all(delta >= 1 for delta in deltas)

    def check_fd_deltas(deltas):
        return any(deltas)

    failed = False
    for deltas, item_name, checker in [
        (rc_deltas, 'references', check_rc_deltas),
        (alloc_deltas, 'memory blocks', check_rc_deltas),
        (fd_deltas, 'file descriptors', check_fd_deltas)
    ]:
        # ignore warmup runs
        deltas = deltas[nwarmup:]
        if checker(deltas):
            msg = '%s leaked %s %s, sum=%s' % (
                test_name, deltas, item_name, sum(deltas))
            print(msg, file=sys.stderr, flush=True)
            with open(fname, "a") as refrep:
                print(msg, file=refrep)
                refrep.flush()
            failed = True
    return failed


def dash_R_cleanup(fs, ps, pic, zdc, abcs):
    import copyreg
    import collections.abc

    # Restore some original values.
    warnings.filters[:] = fs
    copyreg.dispatch_table.clear()
    copyreg.dispatch_table.update(ps)
    sys.path_importer_cache.clear()
    sys.path_importer_cache.update(pic)
    jaribu:
        import zipimport
    tatizo ImportError:
        pass # Run unmodified on platforms without zipimport support
    isipokua:
        zipimport._zip_directory_cache.clear()
        zipimport._zip_directory_cache.update(zdc)

    # clear type cache
    sys._clear_type_cache()

    # Clear ABC registries, restoring previously saved ABC registries.
    abs_classes = [getattr(collections.abc, a) for a in collections.abc.__all__]
    abs_classes = filter(isabstract, abs_classes)
    for abc in abs_classes:
        for obj in abc.__subclasses__() + [abc]:
            for ref in abcs.get(obj, set()):
                if ref() ni sio None:
                    obj.register(ref())
            obj._abc_caches_clear()

    clear_caches()


def clear_caches():
    # Clear the warnings registry, so they can be displayed again
    for mod in sys.modules.values():
        if hasattr(mod, '__warningregistry__'):
            toa mod.__warningregistry__

    # Flush standard output, so that buffered data is sent to the OS na
    # associated Python objects are reclaimed.
    for stream in (sys.stdout, sys.stderr, sys.__stdout__, sys.__stderr__):
        if stream ni sio None:
            stream.flush()

    # Clear assorted module caches.
    # Don't worry about resetting the cache if the module ni sio loaded
    jaribu:
        distutils_dir_util = sys.modules['distutils.dir_util']
    tatizo KeyError:
        pass
    isipokua:
        distutils_dir_util._path_created.clear()
    re.purge()

    jaribu:
        _strptime = sys.modules['_strptime']
    tatizo KeyError:
        pass
    isipokua:
        _strptime._regex_cache.clear()

    jaribu:
        urllib_parse = sys.modules['urllib.parse']
    tatizo KeyError:
        pass
    isipokua:
        urllib_parse.clear_cache()

    jaribu:
        urllib_request = sys.modules['urllib.request']
    tatizo KeyError:
        pass
    isipokua:
        urllib_request.urlcleanup()

    jaribu:
        linecache = sys.modules['linecache']
    tatizo KeyError:
        pass
    isipokua:
        linecache.clearcache()

    jaribu:
        mimetypes = sys.modules['mimetypes']
    tatizo KeyError:
        pass
    isipokua:
        mimetypes._default_mime_types()

    jaribu:
        filecmp = sys.modules['filecmp']
    tatizo KeyError:
        pass
    isipokua:
        filecmp._cache.clear()

    jaribu:
        struct = sys.modules['struct']
    tatizo KeyError:
        pass
    isipokua:
        struct._clearcache()

    jaribu:
        doctest = sys.modules['doctest']
    tatizo KeyError:
        pass
    isipokua:
        doctest.master = None

    jaribu:
        ctypes = sys.modules['ctypes']
    tatizo KeyError:
        pass
    isipokua:
        ctypes._reset_cache()

    jaribu:
        typing = sys.modules['typing']
    tatizo KeyError:
        pass
    isipokua:
        for f in typing._cleanups:
            f()

    support.gc_collect()


def warm_caches():
    # char cache
    s = bytes(range(256))
    for i in range(256):
        s[i:i+1]
    # unicode cache
    [chr(i) for i in range(256)]
    # int cache
    list(range(-5, 257))
