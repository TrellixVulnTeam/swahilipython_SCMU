agiza atexit
agiza faulthandler
agiza os
agiza signal
agiza sys
agiza unittest
kutoka test agiza support
jaribu:
    agiza gc
tatizo ImportError:
    gc = Tupu


eleza setup_tests(ns):
    jaribu:
        stderr_fd = sys.__stderr__.fileno()
    tatizo (ValueError, AttributeError):
        # Catch ValueError to catch io.UnsupportedOperation on TextIOBase
        # na ValueError on a closed stream.
        #
        # Catch AttributeError kila stderr being Tupu.
        stderr_fd = Tupu
    isipokua:
        # Display the Python traceback on fatal errors (e.g. segfault)
        faulthandler.enable(all_threads=Kweli, file=stderr_fd)

        # Display the Python traceback on SIGALRM ama SIGUSR1 signal
        signals = []
        ikiwa hasattr(signal, 'SIGALRM'):
            signals.append(signal.SIGALRM)
        ikiwa hasattr(signal, 'SIGUSR1'):
            signals.append(signal.SIGUSR1)
        kila signum kwenye signals:
            faulthandler.register(signum, chain=Kweli, file=stderr_fd)

    replace_stdout()
    support.record_original_stdout(sys.stdout)

    ikiwa ns.testdir:
        # Prepend test directory to sys.path, so runtest() will be able
        # to locate tests
        sys.path.insert(0, os.path.abspath(ns.testdir))

    # Some times __path__ na __file__ are sio absolute (e.g. wakati running from
    # Lib/) and, ikiwa we change the CWD to run the tests kwenye a temporary dir, some
    # imports might fail.  This affects only the modules imported before os.chdir().
    # These modules are searched first kwenye sys.path[0] (so '' -- the CWD) na if
    # they are found kwenye the CWD their __file__ na __path__ will be relative (this
    # happens before the chdir).  All the modules imported after the chdir, are
    # sio found kwenye the CWD, na since the other paths kwenye sys.path[1:] are absolute
    # (site.py absolutize them), the __file__ na __path__ will be absolute too.
    # Therefore it ni necessary to absolutize manually the __file__ na __path__ of
    # the packages to prevent later imports to fail when the CWD ni different.
    kila module kwenye sys.modules.values():
        ikiwa hasattr(module, '__path__'):
            kila index, path kwenye enumerate(module.__path__):
                module.__path__[index] = os.path.abspath(path)
        ikiwa getattr(module, '__file__', Tupu):
            module.__file__ = os.path.abspath(module.__file__)

    ikiwa ns.huntrleaks:
        unittest.BaseTestSuite._cleanup = Uongo

    ikiwa ns.memlimit ni sio Tupu:
        support.set_memlimit(ns.memlimit)

    ikiwa ns.threshold ni sio Tupu:
        gc.set_threshold(ns.threshold)

    suppress_msvcrt_asserts(ns.verbose na ns.verbose >= 2)

    support.use_resources = ns.use_resources

    ikiwa hasattr(sys, 'addaudithook'):
        # Add an auditing hook kila all tests to ensure PySys_Audit ni tested
        eleza _test_audit_hook(name, args):
            pita
        sys.addaudithook(_test_audit_hook)


eleza suppress_msvcrt_asserts(verbose):
    jaribu:
        agiza msvcrt
    tatizo ImportError:
        return

    msvcrt.SetErrorMode(msvcrt.SEM_FAILCRITICALERRORS|
                        msvcrt.SEM_NOALIGNMENTFAULTEXCEPT|
                        msvcrt.SEM_NOGPFAULTERRORBOX|
                        msvcrt.SEM_NOOPENFILEERRORBOX)
    jaribu:
        msvcrt.CrtSetReportMode
    tatizo AttributeError:
        # release build
        return

    kila m kwenye [msvcrt.CRT_WARN, msvcrt.CRT_ERROR, msvcrt.CRT_ASSERT]:
        ikiwa verbose:
            msvcrt.CrtSetReportMode(m, msvcrt.CRTDBG_MODE_FILE)
            msvcrt.CrtSetReportFile(m, msvcrt.CRTDBG_FILE_STDERR)
        isipokua:
            msvcrt.CrtSetReportMode(m, 0)



eleza replace_stdout():
    """Set stdout encoder error handler to backslashreplace (as stderr error
    handler) to avoid UnicodeEncodeError when printing a traceback"""
    stdout = sys.stdout
    jaribu:
        fd = stdout.fileno()
    tatizo ValueError:
        # On IDLE, sys.stdout has no file descriptor na ni sio a TextIOWrapper
        # object. Leaving sys.stdout unchanged.
        #
        # Catch ValueError to catch io.UnsupportedOperation on TextIOBase
        # na ValueError on a closed stream.
        return

    sys.stdout = open(fd, 'w',
        encoding=stdout.encoding,
        errors="backslashreplace",
        closefd=Uongo,
        newline='\n')

    eleza restore_stdout():
        sys.stdout.close()
        sys.stdout = stdout
    atexit.register(restore_stdout)
