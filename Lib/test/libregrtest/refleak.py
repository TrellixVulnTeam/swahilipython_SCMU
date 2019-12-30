agiza os
agiza re
agiza sys
agiza warnings
kutoka inspect agiza isabstract
kutoka test agiza support
jaribu:
    kutoka _abc agiza _get_dump
tatizo ImportError:
    agiza weakref

    eleza _get_dump(cls):
        # Reimplement _get_dump() kila pure-Python implementation of
        # the abc module (Lib/_py_abc.py)
        registry_weakrefs = set(weakref.ref(obj) kila obj kwenye cls._abc_registry)
        rudisha (registry_weakrefs, cls._abc_cache,
                cls._abc_negative_cache, cls._abc_negative_cache_version)


eleza dash_R(ns, test_name, test_func):
    """Run a test multiple times, looking kila reference leaks.

    Returns:
        Uongo ikiwa the test didn't leak references; Kweli ikiwa we detected refleaks.
    """
    # This code ni hackish na inelegant, but it seems to do the job.
    agiza copyreg
    agiza collections.abc

    ikiwa sio hasattr(sys, 'gettotalrefcount'):
        ashiria Exception("Tracking reference leaks requires a debug build "
                        "of Python")

    # Avoid false positives due to various caches
    # filling slowly ukijumuisha random data:
    warm_caches()

    # Save current values kila dash_R_cleanup() to restore.
    fs = warnings.filters[:]
    ps = copyreg.dispatch_table.copy()
    pic = sys.path_importer_cache.copy()
    jaribu:
        agiza zipimport
    tatizo ImportError:
        zdc = Tupu # Run unmodified on platforms without zipagiza support
    isipokua:
        zdc = zipimport._zip_directory_cache.copy()
    abcs = {}
    kila abc kwenye [getattr(collections.abc, a) kila a kwenye collections.abc.__all__]:
        ikiwa sio isabstract(abc):
            endelea
        kila obj kwenye abc.__subclasses__() + [abc]:
            abcs[obj] = _get_dump(obj)[0]

    # bpo-31217: Integer pool to get a single integer object kila the same
    # value. The pool ni used to prevent false alarm when checking kila memory
    # block leaks. Fill the pool ukijumuisha values kwenye -1000..1000 which are the most
    # common (reference, memory block, file descriptor) differences.
    int_pool = {value: value kila value kwenye range(-1000, 1000)}
    eleza get_pooled_int(value):
        rudisha int_pool.setdefault(value, value)

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

    ikiwa sio ns.quiet:
        andika("beginning", repcount, "repetitions", file=sys.stderr)
        andika(("1234567890"*(repcount//10 + 1))[:repcount], file=sys.stderr,
              flush=Kweli)

    dash_R_cleanup(fs, ps, pic, zdc, abcs)

    kila i kwenye rep_range:
        test_func()
        dash_R_cleanup(fs, ps, pic, zdc, abcs)

        # dash_R_cleanup() ends ukijumuisha collecting cyclic trash:
        # read memory statistics immediately after.
        alloc_after = getallocatedblocks()
        rc_after = gettotalrefcount()
        fd_after = fd_count()

        ikiwa sio ns.quiet:
            andika('.', end='', file=sys.stderr, flush=Kweli)

        rc_deltas[i] = get_pooled_int(rc_after - rc_before)
        alloc_deltas[i] = get_pooled_int(alloc_after - alloc_before)
        fd_deltas[i] = get_pooled_int(fd_after - fd_before)

        alloc_before = alloc_after
        rc_before = rc_after
        fd_before = fd_after

    ikiwa sio ns.quiet:
        andika(file=sys.stderr)

    # These checkers rudisha Uongo on success, Kweli on failure
    eleza check_rc_deltas(deltas):
        # Checker kila reference counters na memomry blocks.
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
        rudisha all(delta >= 1 kila delta kwenye deltas)

    eleza check_fd_deltas(deltas):
        rudisha any(deltas)

    failed = Uongo
    kila deltas, item_name, checker kwenye [
        (rc_deltas, 'references', check_rc_deltas),
        (alloc_deltas, 'memory blocks', check_rc_deltas),
        (fd_deltas, 'file descriptors', check_fd_deltas)
    ]:
        # ignore warmup runs
        deltas = deltas[nwarmup:]
        ikiwa checker(deltas):
            msg = '%s leaked %s %s, sum=%s' % (
                test_name, deltas, item_name, sum(deltas))
            andika(msg, file=sys.stderr, flush=Kweli)
            ukijumuisha open(fname, "a") kama refrep:
                andika(msg, file=refrep)
                refrep.flush()
            failed = Kweli
    rudisha failed


eleza dash_R_cleanup(fs, ps, pic, zdc, abcs):
    agiza copyreg
    agiza collections.abc

    # Restore some original values.
    warnings.filters[:] = fs
    copyreg.dispatch_table.clear()
    copyreg.dispatch_table.update(ps)
    sys.path_importer_cache.clear()
    sys.path_importer_cache.update(pic)
    jaribu:
        agiza zipimport
    tatizo ImportError:
        pita # Run unmodified on platforms without zipagiza support
    isipokua:
        zipimport._zip_directory_cache.clear()
        zipimport._zip_directory_cache.update(zdc)

    # clear type cache
    sys._clear_type_cache()

    # Clear ABC registries, restoring previously saved ABC registries.
    abs_classes = [getattr(collections.abc, a) kila a kwenye collections.abc.__all__]
    abs_classes = filter(isabstract, abs_classes)
    kila abc kwenye abs_classes:
        kila obj kwenye abc.__subclasses__() + [abc]:
            kila ref kwenye abcs.get(obj, set()):
                ikiwa ref() ni sio Tupu:
                    obj.register(ref())
            obj._abc_caches_clear()

    clear_caches()


eleza clear_caches():
    # Clear the warnings registry, so they can be displayed again
    kila mod kwenye sys.modules.values():
        ikiwa hasattr(mod, '__warningregistry__'):
            toa mod.__warningregistry__

    # Flush standard output, so that buffered data ni sent to the OS na
    # associated Python objects are reclaimed.
    kila stream kwenye (sys.stdout, sys.stderr, sys.__stdout__, sys.__stderr__):
        ikiwa stream ni sio Tupu:
            stream.flush()

    # Clear assorted module caches.
    # Don't worry about resetting the cache ikiwa the module ni sio loaded
    jaribu:
        distutils_dir_util = sys.modules['distutils.dir_util']
    tatizo KeyError:
        pita
    isipokua:
        distutils_dir_util._path_created.clear()
    re.purge()

    jaribu:
        _strptime = sys.modules['_strptime']
    tatizo KeyError:
        pita
    isipokua:
        _strptime._regex_cache.clear()

    jaribu:
        urllib_parse = sys.modules['urllib.parse']
    tatizo KeyError:
        pita
    isipokua:
        urllib_parse.clear_cache()

    jaribu:
        urllib_request = sys.modules['urllib.request']
    tatizo KeyError:
        pita
    isipokua:
        urllib_request.urlcleanup()

    jaribu:
        linecache = sys.modules['linecache']
    tatizo KeyError:
        pita
    isipokua:
        linecache.clearcache()

    jaribu:
        mimetypes = sys.modules['mimetypes']
    tatizo KeyError:
        pita
    isipokua:
        mimetypes._default_mime_types()

    jaribu:
        filecmp = sys.modules['filecmp']
    tatizo KeyError:
        pita
    isipokua:
        filecmp._cache.clear()

    jaribu:
        struct = sys.modules['struct']
    tatizo KeyError:
        pita
    isipokua:
        struct._clearcache()

    jaribu:
        doctest = sys.modules['doctest']
    tatizo KeyError:
        pita
    isipokua:
        doctest.master = Tupu

    jaribu:
        ctypes = sys.modules['ctypes']
    tatizo KeyError:
        pita
    isipokua:
        ctypes._reset_cache()

    jaribu:
        typing = sys.modules['typing']
    tatizo KeyError:
        pita
    isipokua:
        kila f kwenye typing._cleanups:
            f()

    support.gc_collect()


eleza warm_caches():
    # char cache
    s = bytes(range(256))
    kila i kwenye range(256):
        s[i:i+1]
    # unicode cache
    [chr(i) kila i kwenye range(256)]
    # int cache
    list(range(-5, 257))
