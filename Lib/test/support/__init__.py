"""Supporting definitions kila the Python regression tests."""

ikiwa __name__ != 'test.support':
     ashiria ImportError('support must be imported kutoka the test package')

agiza asyncio.events
agiza collections.abc
agiza contextlib
agiza errno
agiza faulthandler
agiza fnmatch
agiza functools
agiza gc
agiza glob
agiza hashlib
agiza importlib
agiza importlib.util
agiza locale
agiza logging.handlers
agiza nntplib
agiza os
agiza platform
agiza re
agiza shutil
agiza socket
agiza stat
agiza struct
agiza subprocess
agiza sys
agiza sysconfig
agiza tempfile
agiza _thread
agiza threading
agiza time
agiza types
agiza unittest
agiza urllib.error
agiza warnings

kutoka .testresult agiza get_test_runner

jaribu:
    agiza multiprocessing.process
except ImportError:
    multiprocessing = Tupu

jaribu:
    agiza zlib
except ImportError:
    zlib = Tupu

jaribu:
    agiza gzip
except ImportError:
    gzip = Tupu

jaribu:
    agiza bz2
except ImportError:
    bz2 = Tupu

jaribu:
    agiza lzma
except ImportError:
    lzma = Tupu

jaribu:
    agiza resource
except ImportError:
    resource = Tupu

jaribu:
    agiza _hashlib
except ImportError:
    _hashlib = Tupu

__all__ = [
    # globals
    "PIPE_MAX_SIZE", "verbose", "max_memuse", "use_resources", "failfast",
    # exceptions
    "Error", "TestFailed", "TestDidNotRun", "ResourceDenied",
    # imports
    "import_module", "import_fresh_module", "CleanImport",
    # modules
    "unload", "forget",
    # io
    "record_original_stdout", "get_original_stdout", "captured_stdout",
    "captured_stdin", "captured_stderr",
    # filesystem
    "TESTFN", "SAVEDCWD", "unlink", "rmtree", "temp_cwd", "findfile",
    "create_empty_file", "can_symlink", "fs_is_case_insensitive",
    # unittest
    "is_resource_enabled", "requires", "requires_freebsd_version",
    "requires_linux_version", "requires_mac_ver", "requires_hashdigest",
    "check_syntax_error", "check_syntax_warning",
    "TransientResource", "time_out", "socket_peer_reset", "ioerror_peer_reset",
    "transient_internet", "BasicTestRunner", "run_unittest", "run_doctest",
    "skip_unless_symlink", "requires_gzip", "requires_bz2", "requires_lzma",
    "bigmemtest", "bigaddrspacetest", "cpython_only", "get_attribute",
    "requires_IEEE_754", "skip_unless_xattr", "requires_zlib",
    "anticipate_failure", "load_package_tests", "detect_api_mismatch",
    "check__all__", "skip_unless_bind_unix_socket", "skip_if_buggy_ucrt_strfptime",
    "ignore_warnings",
    # sys
    "is_jython", "is_android", "check_impl_detail", "unix_shell",
    "setswitchinterval",
    # network
    "HOST", "IPV6_ENABLED", "find_unused_port", "bind_port", "open_urlresource",
    "bind_unix_socket",
    # processes
    'temp_umask', "reap_children",
    # logging
    "TestHandler",
    # threads
    "threading_setup", "threading_cleanup", "reap_threads", "start_threads",
    # miscellaneous
    "check_warnings", "check_no_resource_warning", "check_no_warnings",
    "EnvironmentVarGuard",
    "run_with_locale", "swap_item",
    "swap_attr", "Matcher", "set_memlimit", "SuppressCrashReport", "sortdict",
    "run_with_tz", "PGO", "missing_compiler_executable", "fd_count",
    "ALWAYS_EQ", "LARGEST", "SMALLEST"
    ]

kundi Error(Exception):
    """Base kundi kila regression test exceptions."""

kundi TestFailed(Error):
    """Test failed."""

kundi TestDidNotRun(Error):
    """Test did sio run any subtests."""

kundi ResourceDenied(unittest.SkipTest):
    """Test skipped because it requested a disallowed resource.

    This ni raised when a test calls requires() kila a resource that
    has sio be enabled.  It ni used to distinguish between expected
    na unexpected skips.
    """

@contextlib.contextmanager
eleza _ignore_deprecated_imports(ignore=Kweli):
    """Context manager to suppress package na module deprecation
    warnings when importing them.

    If ignore ni Uongo, this context manager has no effect.
    """
    ikiwa ignore:
        ukijumuisha warnings.catch_warnings():
            warnings.filterwarnings("ignore", ".+ (module|package)",
                                    DeprecationWarning)
            yield
    isipokua:
        yield


eleza ignore_warnings(*, category):
    """Decorator to suppress deprecation warnings.

    Use of context managers to hide warnings make diffs
    more noisy na tools like 'git blame' less useful.
    """
    eleza decorator(test):
        @functools.wraps(test)
        eleza wrapper(self, *args, **kwargs):
            ukijumuisha warnings.catch_warnings():
                warnings.simplefilter('ignore', category=category)
                rudisha test(self, *args, **kwargs)
        rudisha wrapper
    rudisha decorator


eleza import_module(name, deprecated=Uongo, *, required_on=()):
    """Import na rudisha the module to be tested, raising SkipTest if
    it ni sio available.

    If deprecated ni Kweli, any module ama package deprecation messages
    will be suppressed. If a module ni required on a platform but optional for
    others, set required_on to an iterable of platform prefixes which will be
    compared against sys.platform.
    """
    ukijumuisha _ignore_deprecated_imports(deprecated):
        jaribu:
            rudisha importlib.import_module(name)
        except ImportError as msg:
            ikiwa sys.platform.startswith(tuple(required_on)):
                raise
             ashiria unittest.SkipTest(str(msg))


eleza _save_and_remove_module(name, orig_modules):
    """Helper function to save na remove a module kutoka sys.modules

    Raise ImportError ikiwa the module can't be imported.
    """
    # try to agiza the module na  ashiria an error ikiwa it can't be imported
    ikiwa name sio kwenye sys.modules:
        __import__(name)
        toa sys.modules[name]
    kila modname kwenye list(sys.modules):
        ikiwa modname == name ama modname.startswith(name + '.'):
            orig_modules[modname] = sys.modules[modname]
            toa sys.modules[modname]

eleza _save_and_block_module(name, orig_modules):
    """Helper function to save na block a module kwenye sys.modules

    Return Kweli ikiwa the module was kwenye sys.modules, Uongo otherwise.
    """
    saved = Kweli
    jaribu:
        orig_modules[name] = sys.modules[name]
    except KeyError:
        saved = Uongo
    sys.modules[name] = Tupu
    rudisha saved


eleza anticipate_failure(condition):
    """Decorator to mark a test that ni known to be broken kwenye some cases

       Any use of this decorator should have a comment identifying the
       associated tracker issue.
    """
    ikiwa condition:
        rudisha unittest.expectedFailure
    rudisha lambda f: f

eleza load_package_tests(pkg_dir, loader, standard_tests, pattern):
    """Generic load_tests implementation kila simple test packages.

    Most packages can implement load_tests using this function as follows:

       eleza load_tests(*args):
           rudisha load_package_tests(os.path.dirname(__file__), *args)
    """
    ikiwa pattern ni Tupu:
        pattern = "test*"
    top_dir = os.path.dirname(              # Lib
                  os.path.dirname(              # test
                      os.path.dirname(__file__)))   # support
    package_tests = loader.discover(start_dir=pkg_dir,
                                    top_level_dir=top_dir,
                                    pattern=pattern)
    standard_tests.addTests(package_tests)
    rudisha standard_tests


eleza import_fresh_module(name, fresh=(), blocked=(), deprecated=Uongo):
    """Import na rudisha a module, deliberately bypassing sys.modules.

    This function imports na returns a fresh copy of the named Python module
    by removing the named module kutoka sys.modules before doing the import.
    Note that unlike reload, the original module ni sio affected by
    this operation.

    *fresh* ni an iterable of additional module names that are also removed
    kutoka the sys.modules cache before doing the import.

    *blocked* ni an iterable of module names that are replaced ukijumuisha Tupu
    kwenye the module cache during the agiza to ensure that attempts to import
    them  ashiria ImportError.

    The named module na any modules named kwenye the *fresh* na *blocked*
    parameters are saved before starting the agiza na then reinserted into
    sys.modules when the fresh agiza ni complete.

    Module na package deprecation messages are suppressed during this import
    ikiwa *deprecated* ni Kweli.

    This function will  ashiria ImportError ikiwa the named module cannot be
    imported.
    """
    # NOTE: test_heapq, test_json na test_warnings include extra sanity checks
    # to make sure that this utility function ni working as expected
    ukijumuisha _ignore_deprecated_imports(deprecated):
        # Keep track of modules saved kila later restoration as well
        # as those which just need a blocking entry removed
        orig_modules = {}
        names_to_remove = []
        _save_and_remove_module(name, orig_modules)
        jaribu:
            kila fresh_name kwenye fresh:
                _save_and_remove_module(fresh_name, orig_modules)
            kila blocked_name kwenye blocked:
                ikiwa sio _save_and_block_module(blocked_name, orig_modules):
                    names_to_remove.append(blocked_name)
            fresh_module = importlib.import_module(name)
        except ImportError:
            fresh_module = Tupu
        mwishowe:
            kila orig_name, module kwenye orig_modules.items():
                sys.modules[orig_name] = module
            kila name_to_remove kwenye names_to_remove:
                toa sys.modules[name_to_remove]
        rudisha fresh_module


eleza get_attribute(obj, name):
    """Get an attribute, raising SkipTest ikiwa AttributeError ni raised."""
    jaribu:
        attribute = getattr(obj, name)
    except AttributeError:
         ashiria unittest.SkipTest("object %r has no attribute %r" % (obj, name))
    isipokua:
        rudisha attribute

verbose = 1              # Flag set to 0 by regrtest.py
use_resources = Tupu     # Flag set to [] by regrtest.py
max_memuse = 0           # Disable bigmem tests (they will still be run with
                         # small sizes, to make sure they work.)
real_max_memuse = 0
junit_xml_list = Tupu    # list of testsuite XML elements
failfast = Uongo

# _original_stdout ni meant to hold stdout at the time regrtest began.
# This may be "the real" stdout, ama IDLE's emulation of stdout, ama whatever.
# The point ni to have some flavor of stdout the user can actually see.
_original_stdout = Tupu
eleza record_original_stdout(stdout):
    global _original_stdout
    _original_stdout = stdout

eleza get_original_stdout():
    rudisha _original_stdout ama sys.stdout

eleza unload(name):
    jaribu:
        toa sys.modules[name]
    except KeyError:
        pass

eleza _force_run(path, func, *args):
    jaribu:
        rudisha func(*args)
    except OSError as err:
        ikiwa verbose >= 2:
            andika('%s: %s' % (err.__class__.__name__, err))
            andika('re-run %s%r' % (func.__name__, args))
        os.chmod(path, stat.S_IRWXU)
        rudisha func(*args)

ikiwa sys.platform.startswith("win"):
    eleza _waitfor(func, pathname, waitall=Uongo):
        # Perform the operation
        func(pathname)
        # Now setup the wait loop
        ikiwa waitall:
            dirname = pathname
        isipokua:
            dirname, name = os.path.split(pathname)
            dirname = dirname ama '.'
        # Check kila `pathname` to be removed kutoka the filesystem.
        # The exponential backoff of the timeout amounts to a total
        # of ~1 second after which the deletion ni probably an error
        # anyway.
        # Testing on an i7@4.3GHz shows that usually only 1 iteration is
        # required when contention occurs.
        timeout = 0.001
        wakati timeout < 1.0:
            # Note we are only testing kila the existence of the file(s) in
            # the contents of the directory regardless of any security or
            # access rights.  If we have made it this far, we have sufficient
            # permissions to do that much using Python's equivalent of the
            # Windows API FindFirstFile.
            # Other Windows APIs can fail ama give incorrect results when
            # dealing ukijumuisha files that are pending deletion.
            L = os.listdir(dirname)
            ikiwa sio (L ikiwa waitall isipokua name kwenye L):
                return
            # Increase the timeout na try again
            time.sleep(timeout)
            timeout *= 2
        warnings.warn('tests may fail, delete still pending kila ' + pathname,
                      RuntimeWarning, stacklevel=4)

    eleza _unlink(filename):
        _waitfor(os.unlink, filename)

    eleza _rmdir(dirname):
        _waitfor(os.rmdir, dirname)

    eleza _rmtree(path):
        eleza _rmtree_inner(path):
            kila name kwenye _force_run(path, os.listdir, path):
                fullname = os.path.join(path, name)
                jaribu:
                    mode = os.lstat(fullname).st_mode
                except OSError as exc:
                    andika("support.rmtree(): os.lstat(%r) failed ukijumuisha %s" % (fullname, exc),
                          file=sys.__stderr__)
                    mode = 0
                ikiwa stat.S_ISDIR(mode):
                    _waitfor(_rmtree_inner, fullname, waitall=Kweli)
                    _force_run(fullname, os.rmdir, fullname)
                isipokua:
                    _force_run(fullname, os.unlink, fullname)
        _waitfor(_rmtree_inner, path, waitall=Kweli)
        _waitfor(lambda p: _force_run(p, os.rmdir, p), path)

    eleza _longpath(path):
        jaribu:
            agiza ctypes
        except ImportError:
            # No ctypes means we can't expands paths.
            pass
        isipokua:
            buffer = ctypes.create_unicode_buffer(len(path) * 2)
            length = ctypes.windll.kernel32.GetLongPathNameW(path, buffer,
                                                             len(buffer))
            ikiwa length:
                rudisha buffer[:length]
        rudisha path
isipokua:
    _unlink = os.unlink
    _rmdir = os.rmdir

    eleza _rmtree(path):
        jaribu:
            shutil.rmtree(path)
            return
        except OSError:
            pass

        eleza _rmtree_inner(path):
            kila name kwenye _force_run(path, os.listdir, path):
                fullname = os.path.join(path, name)
                jaribu:
                    mode = os.lstat(fullname).st_mode
                except OSError:
                    mode = 0
                ikiwa stat.S_ISDIR(mode):
                    _rmtree_inner(fullname)
                    _force_run(path, os.rmdir, fullname)
                isipokua:
                    _force_run(path, os.unlink, fullname)
        _rmtree_inner(path)
        os.rmdir(path)

    eleza _longpath(path):
        rudisha path

eleza unlink(filename):
    jaribu:
        _unlink(filename)
    except (FileNotFoundError, NotADirectoryError):
        pass

eleza rmdir(dirname):
    jaribu:
        _rmdir(dirname)
    except FileNotFoundError:
        pass

eleza rmtree(path):
    jaribu:
        _rmtree(path)
    except FileNotFoundError:
        pass

eleza make_legacy_pyc(source):
    """Move a PEP 3147/488 pyc file to its legacy pyc location.

    :param source: The file system path to the source file.  The source file
        does sio need to exist, however the PEP 3147/488 pyc file must exist.
    :return: The file system path to the legacy pyc file.
    """
    pyc_file = importlib.util.cache_from_source(source)
    up_one = os.path.dirname(os.path.abspath(source))
    legacy_pyc = os.path.join(up_one, source + 'c')
    os.rename(pyc_file, legacy_pyc)
    rudisha legacy_pyc

eleza forget(modname):
    """'Forget' a module was ever imported.

    This removes the module kutoka sys.modules na deletes any PEP 3147/488 or
    legacy .pyc files.
    """
    unload(modname)
    kila dirname kwenye sys.path:
        source = os.path.join(dirname, modname + '.py')
        # It doesn't matter ikiwa they exist ama not, unlink all possible
        # combinations of PEP 3147/488 na legacy pyc files.
        unlink(source + 'c')
        kila opt kwenye ('', 1, 2):
            unlink(importlib.util.cache_from_source(source, optimization=opt))

# Check whether a gui ni actually available
eleza _is_gui_available():
    ikiwa hasattr(_is_gui_available, 'result'):
        rudisha _is_gui_available.result
    reason = Tupu
    ikiwa sys.platform.startswith('win'):
        # ikiwa Python ni running as a service (such as the buildbot service),
        # gui interaction may be disallowed
        agiza ctypes
        agiza ctypes.wintypes
        UOI_FLAGS = 1
        WSF_VISIBLE = 0x0001
        kundi USEROBJECTFLAGS(ctypes.Structure):
            _fields_ = [("fInherit", ctypes.wintypes.BOOL),
                        ("fReserved", ctypes.wintypes.BOOL),
                        ("dwFlags", ctypes.wintypes.DWORD)]
        dll = ctypes.windll.user32
        h = dll.GetProcessWindowStation()
        ikiwa sio h:
             ashiria ctypes.WinError()
        uof = USEROBJECTFLAGS()
        needed = ctypes.wintypes.DWORD()
        res = dll.GetUserObjectInformationW(h,
            UOI_FLAGS,
            ctypes.byref(uof),
            ctypes.sizeof(uof),
            ctypes.byref(needed))
        ikiwa sio res:
             ashiria ctypes.WinError()
        ikiwa sio bool(uof.dwFlags & WSF_VISIBLE):
            reason = "gui sio available (WSF_VISIBLE flag sio set)"
    elikiwa sys.platform == 'darwin':
        # The Aqua Tk implementations on OS X can abort the process if
        # being called kwenye an environment where a window server connection
        # cannot be made, kila instance when invoked by a buildbot ama ssh
        # process sio running under the same user id as the current console
        # user.  To avoid that,  ashiria an exception ikiwa the window manager
        # connection ni sio available.
        kutoka ctypes agiza cdll, c_int, pointer, Structure
        kutoka ctypes.util agiza find_library

        app_services = cdll.LoadLibrary(find_library("ApplicationServices"))

        ikiwa app_services.CGMainDisplayID() == 0:
            reason = "gui tests cannot run without OS X window manager"
        isipokua:
            kundi ProcessSerialNumber(Structure):
                _fields_ = [("highLongOfPSN", c_int),
                            ("lowLongOfPSN", c_int)]
            psn = ProcessSerialNumber()
            psn_p = pointer(psn)
            ikiwa (  (app_services.GetCurrentProcess(psn_p) < 0) or
                  (app_services.SetFrontProcess(psn_p) < 0) ):
                reason = "cannot run without OS X gui process"

    # check on every platform whether tkinter can actually do anything
    ikiwa sio reason:
        jaribu:
            kutoka tkinter agiza Tk
            root = Tk()
            root.withdraw()
            root.update()
            root.destroy()
        except Exception as e:
            err_string = str(e)
            ikiwa len(err_string) > 50:
                err_string = err_string[:50] + ' [...]'
            reason = 'Tk unavailable due to {}: {}'.format(type(e).__name__,
                                                           err_string)

    _is_gui_available.reason = reason
    _is_gui_available.result = sio reason

    rudisha _is_gui_available.result

eleza is_resource_enabled(resource):
    """Test whether a resource ni enabled.

    Known resources are set by regrtest.py.  If sio running under regrtest.py,
    all resources are assumed enabled unless use_resources has been set.
    """
    rudisha use_resources ni Tupu ama resource kwenye use_resources

eleza requires(resource, msg=Tupu):
    """Raise ResourceDenied ikiwa the specified resource ni sio available."""
    ikiwa sio is_resource_enabled(resource):
        ikiwa msg ni Tupu:
            msg = "Use of the %r resource sio enabled" % resource
         ashiria ResourceDenied(msg)
    ikiwa resource == 'gui' na sio _is_gui_available():
         ashiria ResourceDenied(_is_gui_available.reason)

eleza _requires_unix_version(sysname, min_version):
    """Decorator raising SkipTest ikiwa the OS ni `sysname` na the version ni less
    than `min_version`.

    For example, @_requires_unix_version('FreeBSD', (7, 2)) raises SkipTest if
    the FreeBSD version ni less than 7.2.
    """
    eleza decorator(func):
        @functools.wraps(func)
        eleza wrapper(*args, **kw):
            ikiwa platform.system() == sysname:
                version_txt = platform.release().split('-', 1)[0]
                jaribu:
                    version = tuple(map(int, version_txt.split('.')))
                except ValueError:
                    pass
                isipokua:
                    ikiwa version < min_version:
                        min_version_txt = '.'.join(map(str, min_version))
                         ashiria unittest.SkipTest(
                            "%s version %s ama higher required, sio %s"
                            % (sysname, min_version_txt, version_txt))
            rudisha func(*args, **kw)
        wrapper.min_version = min_version
        rudisha wrapper
    rudisha decorator

eleza requires_freebsd_version(*min_version):
    """Decorator raising SkipTest ikiwa the OS ni FreeBSD na the FreeBSD version is
    less than `min_version`.

    For example, @requires_freebsd_version(7, 2) raises SkipTest ikiwa the FreeBSD
    version ni less than 7.2.
    """
    rudisha _requires_unix_version('FreeBSD', min_version)

eleza requires_linux_version(*min_version):
    """Decorator raising SkipTest ikiwa the OS ni Linux na the Linux version is
    less than `min_version`.

    For example, @requires_linux_version(2, 6, 32) raises SkipTest ikiwa the Linux
    version ni less than 2.6.32.
    """
    rudisha _requires_unix_version('Linux', min_version)

eleza requires_mac_ver(*min_version):
    """Decorator raising SkipTest ikiwa the OS ni Mac OS X na the OS X
    version ikiwa less than min_version.

    For example, @requires_mac_ver(10, 5) raises SkipTest ikiwa the OS X version
    ni lesser than 10.5.
    """
    eleza decorator(func):
        @functools.wraps(func)
        eleza wrapper(*args, **kw):
            ikiwa sys.platform == 'darwin':
                version_txt = platform.mac_ver()[0]
                jaribu:
                    version = tuple(map(int, version_txt.split('.')))
                except ValueError:
                    pass
                isipokua:
                    ikiwa version < min_version:
                        min_version_txt = '.'.join(map(str, min_version))
                         ashiria unittest.SkipTest(
                            "Mac OS X %s ama higher required, sio %s"
                            % (min_version_txt, version_txt))
            rudisha func(*args, **kw)
        wrapper.min_version = min_version
        rudisha wrapper
    rudisha decorator


eleza requires_hashdigest(digestname, openssl=Tupu):
    """Decorator raising SkipTest ikiwa a hashing algorithm ni sio available

    The hashing algorithm could be missing ama blocked by a strict crypto
    policy.

    If 'openssl' ni Kweli, then the decorator checks that OpenSSL provides
    the algorithm. Otherwise the check falls back to built-in
    implementations.

    ValueError: [digital envelope routines: EVP_DigestInit_ex] disabled kila FIPS
    ValueError: unsupported hash type md4
    """
    eleza decorator(func):
        @functools.wraps(func)
        eleza wrapper(*args, **kwargs):
            jaribu:
                ikiwa openssl na _hashlib ni sio Tupu:
                    _hashlib.new(digestname)
                isipokua:
                    hashlib.new(digestname)
            except ValueError:
                 ashiria unittest.SkipTest(
                    f"hash digest '{digestname}' ni sio available."
                )
            rudisha func(*args, **kwargs)
        rudisha wrapper
    rudisha decorator


HOST = "localhost"
HOSTv4 = "127.0.0.1"
HOSTv6 = "::1"


eleza find_unused_port(family=socket.AF_INET, socktype=socket.SOCK_STREAM):
    """Returns an unused port that should be suitable kila binding.  This is
    achieved by creating a temporary socket ukijumuisha the same family na type as
    the 'sock' parameter (default ni AF_INET, SOCK_STREAM), na binding it to
    the specified host address (defaults to 0.0.0.0) ukijumuisha the port set to 0,
    eliciting an unused ephemeral port kutoka the OS.  The temporary socket is
    then closed na deleted, na the ephemeral port ni returned.

    Either this method ama bind_port() should be used kila any tests where a
    server socket needs to be bound to a particular port kila the duration of
    the test.  Which one to use depends on whether the calling code ni creating
    a python socket, ama ikiwa an unused port needs to be provided kwenye a constructor
    ama passed to an external program (i.e. the -accept argument to openssl's
    s_server mode).  Always prefer bind_port() over find_unused_port() where
    possible.  Hard coded ports should *NEVER* be used.  As soon as a server
    socket ni bound to a hard coded port, the ability to run multiple instances
    of the test simultaneously on the same host ni compromised, which makes the
    test a ticking time bomb kwenye a buildbot environment. On Unix buildbots, this
    may simply manifest as a failed test, which can be recovered kutoka without
    intervention kwenye most cases, but on Windows, the entire python process can
    completely na utterly wedge, requiring someone to log kwenye to the buildbot
    na manually kill the affected process.

    (This ni easy to reproduce on Windows, unfortunately, na can be traced to
    the SO_REUSEADDR socket option having different semantics on Windows versus
    Unix/Linux.  On Unix, you can't have two AF_INET SOCK_STREAM sockets bind,
    listen na then accept connections on identical host/ports.  An EADDRINUSE
    OSError will be raised at some point (depending on the platform and
    the order bind na listen were called on each socket).

    However, on Windows, ikiwa SO_REUSEADDR ni set on the sockets, no EADDRINUSE
    will ever be raised when attempting to bind two identical host/ports. When
    accept() ni called on each socket, the second caller's process will steal
    the port kutoka the first caller, leaving them both kwenye an awkwardly wedged
    state where they'll no longer respond to any signals ama graceful kills, and
    must be forcibly killed via OpenProcess()/TerminateProcess().

    The solution on Windows ni to use the SO_EXCLUSIVEADDRUSE socket option
    instead of SO_REUSEADDR, which effectively affords the same semantics as
    SO_REUSEADDR on Unix.  Given the propensity of Unix developers kwenye the Open
    Source world compared to Windows ones, this ni a common mistake.  A quick
    look over OpenSSL's 0.9.8g source shows that they use SO_REUSEADDR when
    openssl.exe ni called ukijumuisha the 's_server' option, kila example. See
    http://bugs.python.org/issue2550 kila more info.  The following site also
    has a very thorough description about the implications of both REUSEADDR
    na EXCLUSIVEADDRUSE on Windows:
    http://msdn2.microsoft.com/en-us/library/ms740621(VS.85).aspx)

    XXX: although this approach ni a vast improvement on previous attempts to
    elicit unused ports, it rests heavily on the assumption that the ephemeral
    port returned to us by the OS won't immediately be dished back out to some
    other process when we close na delete our temporary socket but before our
    calling code has a chance to bind the returned port.  We can deal ukijumuisha this
    issue if/when we come across it.
    """

    ukijumuisha socket.socket(family, socktype) as tempsock:
        port = bind_port(tempsock)
    toa tempsock
    rudisha port

eleza bind_port(sock, host=HOST):
    """Bind the socket to a free port na rudisha the port number.  Relies on
    ephemeral ports kwenye order to ensure we are using an unbound port.  This is
    important as many tests may be running simultaneously, especially kwenye a
    buildbot environment.  This method raises an exception ikiwa the sock.family
    ni AF_INET na sock.type ni SOCK_STREAM, *and* the socket has SO_REUSEADDR
    ama SO_REUSEPORT set on it.  Tests should *never* set these socket options
    kila TCP/IP sockets.  The only case kila setting these options ni testing
    multicasting via multiple UDP sockets.

    Additionally, ikiwa the SO_EXCLUSIVEADDRUSE socket option ni available (i.e.
    on Windows), it will be set on the socket.  This will prevent anyone else
    kutoka bind()'ing to our host/port kila the duration of the test.
    """

    ikiwa sock.family == socket.AF_INET na sock.type == socket.SOCK_STREAM:
        ikiwa hasattr(socket, 'SO_REUSEADDR'):
            ikiwa sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR) == 1:
                 ashiria TestFailed("tests should never set the SO_REUSEADDR "   \
                                 "socket option on TCP/IP sockets!")
        ikiwa hasattr(socket, 'SO_REUSEPORT'):
            jaribu:
                ikiwa sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT) == 1:
                     ashiria TestFailed("tests should never set the SO_REUSEPORT "   \
                                     "socket option on TCP/IP sockets!")
            except OSError:
                # Python's socket module was compiled using modern headers
                # thus defining SO_REUSEPORT but this process ni running
                # under an older kernel that does sio support SO_REUSEPORT.
                pass
        ikiwa hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)

    sock.bind((host, 0))
    port = sock.getsockname()[1]
    rudisha port

eleza bind_unix_socket(sock, addr):
    """Bind a unix socket, raising SkipTest ikiwa PermissionError ni raised."""
    assert sock.family == socket.AF_UNIX
    jaribu:
        sock.bind(addr)
    except PermissionError:
        sock.close()
         ashiria unittest.SkipTest('cannot bind AF_UNIX sockets')

eleza _is_ipv6_enabled():
    """Check whether IPv6 ni enabled on this host."""
    ikiwa socket.has_ipv6:
        sock = Tupu
        jaribu:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.bind((HOSTv6, 0))
            rudisha Kweli
        except OSError:
            pass
        mwishowe:
            ikiwa sock:
                sock.close()
    rudisha Uongo

IPV6_ENABLED = _is_ipv6_enabled()

eleza system_must_validate_cert(f):
    """Skip the test on TLS certificate validation failures."""
    @functools.wraps(f)
    eleza dec(*args, **kwargs):
        jaribu:
            f(*args, **kwargs)
        except OSError as e:
            ikiwa "CERTIFICATE_VERIFY_FAILED" kwenye str(e):
                 ashiria unittest.SkipTest("system does sio contain "
                                        "necessary certificates")
            raise
    rudisha dec

# A constant likely larger than the underlying OS pipe buffer size, to
# make writes blocking.
# Windows limit seems to be around 512 B, na many Unix kernels have a
# 64 KiB pipe buffer size ama 16 * PAGE_SIZE: take a few megs to be sure.
# (see issue #17835 kila a discussion of this number).
PIPE_MAX_SIZE = 4 * 1024 * 1024 + 1

# A constant likely larger than the underlying OS socket buffer size, to make
# writes blocking.
# The socket buffer sizes can usually be tuned system-wide (e.g. through sysctl
# on Linux), ama on a per-socket basis (SO_SNDBUF/SO_RCVBUF). See issue #18643
# kila a discussion of this number).
SOCK_MAX_SIZE = 16 * 1024 * 1024 + 1

# decorator kila skipping tests on non-IEEE 754 platforms
requires_IEEE_754 = unittest.skipUnless(
    float.__getformat__("double").startswith("IEEE"),
    "test requires IEEE 754 doubles")

requires_zlib = unittest.skipUnless(zlib, 'requires zlib')

requires_gzip = unittest.skipUnless(gzip, 'requires gzip')

requires_bz2 = unittest.skipUnless(bz2, 'requires bz2')

requires_lzma = unittest.skipUnless(lzma, 'requires lzma')

is_jython = sys.platform.startswith('java')

is_android = hasattr(sys, 'getandroidapilevel')

ikiwa sys.platform != 'win32':
    unix_shell = '/system/bin/sh' ikiwa is_android isipokua '/bin/sh'
isipokua:
    unix_shell = Tupu

# Filename used kila testing
ikiwa os.name == 'java':
    # Jython disallows @ kwenye module names
    TESTFN = '$test'
isipokua:
    TESTFN = '@test'

# Disambiguate TESTFN kila parallel testing, wakati letting it remain a valid
# module name.
TESTFN = "{}_{}_tmp".format(TESTFN, os.getpid())

# Define the URL of a dedicated HTTP server kila the network tests.
# The URL must use clear-text HTTP: no redirection to encrypted HTTPS.
TEST_HTTP_URL = "http://www.pythontest.net"

# FS_NONASCII: non-ASCII character encodable by os.fsencode(),
# ama Tupu ikiwa there ni no such character.
FS_NONASCII = Tupu
kila character kwenye (
    # First try printable na common characters to have a readable filename.
    # For each character, the encoding list are just example of encodings able
    # to encode the character (the list ni sio exhaustive).

    # U+00E6 (Latin Small Letter Ae): cp1252, iso-8859-1
    '\u00E6',
    # U+0130 (Latin Capital Letter I With Dot Above): cp1254, iso8859_3
    '\u0130',
    # U+0141 (Latin Capital Letter L With Stroke): cp1250, cp1257
    '\u0141',
    # U+03C6 (Greek Small Letter Phi): cp1253
    '\u03C6',
    # U+041A (Cyrillic Capital Letter Ka): cp1251
    '\u041A',
    # U+05D0 (Hebrew Letter Alef): Encodable to cp424
    '\u05D0',
    # U+060C (Arabic Comma): cp864, cp1006, iso8859_6, mac_arabic
    '\u060C',
    # U+062A (Arabic Letter Teh): cp720
    '\u062A',
    # U+0E01 (Thai Character Ko Kai): cp874
    '\u0E01',

    # Then try more "special" characters. "special" because they may be
    # interpreted ama displayed differently depending on the exact locale
    # encoding na the font.

    # U+00A0 (No-Break Space)
    '\u00A0',
    # U+20AC (Euro Sign)
    '\u20AC',
):
    jaribu:
        # If Python ni set up to use the legacy 'mbcs' kwenye Windows,
        # 'replace' error mode ni used, na encode() returns b'?'
        # kila characters missing kwenye the ANSI codepage
        ikiwa os.fsdecode(os.fsencode(character)) != character:
             ashiria UnicodeError
    except UnicodeError:
        pass
    isipokua:
        FS_NONASCII = character
        koma

# TESTFN_UNICODE ni a non-ascii filename
TESTFN_UNICODE = TESTFN + "-\xe0\xf2\u0258\u0141\u011f"
ikiwa sys.platform == 'darwin':
    # In Mac OS X's VFS API file names are, by definition, canonically
    # decomposed Unicode, encoded using UTF-8. See QA1173:
    # http://developer.apple.com/mac/library/qa/qa2001/qa1173.html
    agiza unicodedata
    TESTFN_UNICODE = unicodedata.normalize('NFD', TESTFN_UNICODE)
TESTFN_ENCODING = sys.getfilesystemencoding()

# TESTFN_UNENCODABLE ni a filename (str type) that should *not* be able to be
# encoded by the filesystem encoding (in strict mode). It can be Tupu ikiwa we
# cannot generate such filename.
TESTFN_UNENCODABLE = Tupu
ikiwa os.name == 'nt':
    # skip win32s (0) ama Windows 9x/ME (1)
    ikiwa sys.getwindowsversion().platform >= 2:
        # Different kinds of characters kutoka various languages to minimize the
        # probability that the whole name ni encodable to MBCS (issue #9819)
        TESTFN_UNENCODABLE = TESTFN + "-\u5171\u0141\u2661\u0363\uDC80"
        jaribu:
            TESTFN_UNENCODABLE.encode(TESTFN_ENCODING)
        except UnicodeEncodeError:
            pass
        isipokua:
            andika('WARNING: The filename %r CAN be encoded by the filesystem encoding (%s). '
                  'Unicode filename tests may sio be effective'
                  % (TESTFN_UNENCODABLE, TESTFN_ENCODING))
            TESTFN_UNENCODABLE = Tupu
# Mac OS X denies unencodable filenames (invalid utf-8)
elikiwa sys.platform != 'darwin':
    jaribu:
        # ascii na utf-8 cannot encode the byte 0xff
        b'\xff'.decode(TESTFN_ENCODING)
    except UnicodeDecodeError:
        # 0xff will be encoded using the surrogate character u+DCFF
        TESTFN_UNENCODABLE = TESTFN \
            + b'-\xff'.decode(TESTFN_ENCODING, 'surrogateescape')
    isipokua:
        # File system encoding (eg. ISO-8859-* encodings) can encode
        # the byte 0xff. Skip some unicode filename tests.
        pass

# TESTFN_UNDECODABLE ni a filename (bytes type) that should *not* be able to be
# decoded kutoka the filesystem encoding (in strict mode). It can be Tupu ikiwa we
# cannot generate such filename (ex: the latin1 encoding can decode any byte
# sequence). On UNIX, TESTFN_UNDECODABLE can be decoded by os.fsdecode() thanks
# to the surrogateescape error handler (PEP 383), but sio kutoka the filesystem
# encoding kwenye strict mode.
TESTFN_UNDECODABLE = Tupu
kila name kwenye (
    # b'\xff' ni sio decodable by os.fsdecode() ukijumuisha code page 932. Windows
    # accepts it to create a file ama a directory, ama don't accept to enter to
    # such directory (when the bytes name ni used). So test b'\xe7' first: it is
    # sio decodable kutoka cp932.
    b'\xe7w\xf0',
    # undecodable kutoka ASCII, UTF-8
    b'\xff',
    # undecodable kutoka iso8859-3, iso8859-6, iso8859-7, cp424, iso8859-8, cp856
    # na cp857
    b'\xae\xd5'
    # undecodable kutoka UTF-8 (UNIX na Mac OS X)
    b'\xed\xb2\x80', b'\xed\xb4\x80',
    # undecodable kutoka shift_jis, cp869, cp874, cp932, cp1250, cp1251, cp1252,
    # cp1253, cp1254, cp1255, cp1257, cp1258
    b'\x81\x98',
):
    jaribu:
        name.decode(TESTFN_ENCODING)
    except UnicodeDecodeError:
        TESTFN_UNDECODABLE = os.fsencode(TESTFN) + name
        koma

ikiwa FS_NONASCII:
    TESTFN_NONASCII = TESTFN + '-' + FS_NONASCII
isipokua:
    TESTFN_NONASCII = Tupu

# Save the initial cwd
SAVEDCWD = os.getcwd()

# Set by libregrtest/main.py so we can skip tests that are not
# useful kila PGO
PGO = Uongo

# Set by libregrtest/main.py ikiwa we are running the extended (time consuming)
# PGO task.  If this ni Kweli, PGO ni also Kweli.
PGO_EXTENDED = Uongo

@contextlib.contextmanager
eleza temp_dir(path=Tupu, quiet=Uongo):
    """Return a context manager that creates a temporary directory.

    Arguments:

      path: the directory to create temporarily.  If omitted ama Tupu,
        defaults to creating a temporary directory using tempfile.mkdtemp.

      quiet: ikiwa Uongo (the default), the context manager raises an exception
        on error.  Otherwise, ikiwa the path ni specified na cannot be
        created, only a warning ni issued.

    """
    dir_created = Uongo
    ikiwa path ni Tupu:
        path = tempfile.mkdtemp()
        dir_created = Kweli
        path = os.path.realpath(path)
    isipokua:
        jaribu:
            os.mkdir(path)
            dir_created = Kweli
        except OSError as exc:
            ikiwa sio quiet:
                raise
            warnings.warn(f'tests may fail, unable to create '
                          f'temporary directory {path!r}: {exc}',
                          RuntimeWarning, stacklevel=3)
    ikiwa dir_created:
        pid = os.getpid()
    jaribu:
        tuma path
    mwishowe:
        # In case the process forks, let only the parent remove the
        # directory. The child has a different process id. (bpo-30028)
        ikiwa dir_created na pid == os.getpid():
            rmtree(path)

@contextlib.contextmanager
eleza change_cwd(path, quiet=Uongo):
    """Return a context manager that changes the current working directory.

    Arguments:

      path: the directory to use as the temporary current working directory.

      quiet: ikiwa Uongo (the default), the context manager raises an exception
        on error.  Otherwise, it issues only a warning na keeps the current
        working directory the same.

    """
    saved_dir = os.getcwd()
    jaribu:
        os.chdir(path)
    except OSError as exc:
        ikiwa sio quiet:
            raise
        warnings.warn(f'tests may fail, unable to change the current working '
                      f'directory to {path!r}: {exc}',
                      RuntimeWarning, stacklevel=3)
    jaribu:
        tuma os.getcwd()
    mwishowe:
        os.chdir(saved_dir)


@contextlib.contextmanager
eleza temp_cwd(name='tempcwd', quiet=Uongo):
    """
    Context manager that temporarily creates na changes the CWD.

    The function temporarily changes the current working directory
    after creating a temporary directory kwenye the current directory with
    name *name*.  If *name* ni Tupu, the temporary directory is
    created using tempfile.mkdtemp.

    If *quiet* ni Uongo (default) na it ni sio possible to
    create ama change the CWD, an error ni raised.  If *quiet* ni Kweli,
    only a warning ni raised na the original CWD ni used.

    """
    ukijumuisha temp_dir(path=name, quiet=quiet) as temp_path:
        ukijumuisha change_cwd(temp_path, quiet=quiet) as cwd_dir:
            tuma cwd_dir

ikiwa hasattr(os, "umask"):
    @contextlib.contextmanager
    eleza temp_umask(umask):
        """Context manager that temporarily sets the process umask."""
        oldmask = os.umask(umask)
        jaribu:
            yield
        mwishowe:
            os.umask(oldmask)

# TEST_HOME_DIR refers to the top level directory of the "test" package
# that contains Python's regression test suite
TEST_SUPPORT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_HOME_DIR = os.path.dirname(TEST_SUPPORT_DIR)

# TEST_DATA_DIR ni used as a target download location kila remote resources
TEST_DATA_DIR = os.path.join(TEST_HOME_DIR, "data")

eleza findfile(filename, subdir=Tupu):
    """Try to find a file on sys.path ama kwenye the test directory.  If it ni not
    found the argument passed to the function ni returned (this does not
    necessarily signal failure; could still be the legitimate path).

    Setting *subdir* indicates a relative path to use to find the file
    rather than looking directly kwenye the path directories.
    """
    ikiwa os.path.isabs(filename):
        rudisha filename
    ikiwa subdir ni sio Tupu:
        filename = os.path.join(subdir, filename)
    path = [TEST_HOME_DIR] + sys.path
    kila dn kwenye path:
        fn = os.path.join(dn, filename)
        ikiwa os.path.exists(fn): rudisha fn
    rudisha filename

eleza create_empty_file(filename):
    """Create an empty file. If the file already exists, truncate it."""
    fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    os.close(fd)

eleza sortdict(dict):
    "Like repr(dict), but kwenye sorted order."
    items = sorted(dict.items())
    reprpairs = ["%r: %r" % pair kila pair kwenye items]
    withcommas = ", ".join(reprpairs)
    rudisha "{%s}" % withcommas

eleza make_bad_fd():
    """
    Create an invalid file descriptor by opening na closing a file na return
    its fd.
    """
    file = open(TESTFN, "wb")
    jaribu:
        rudisha file.fileno()
    mwishowe:
        file.close()
        unlink(TESTFN)


eleza check_syntax_error(testcase, statement, errtext='', *, lineno=Tupu, offset=Tupu):
    ukijumuisha testcase.assertRaisesRegex(SyntaxError, errtext) as cm:
        compile(statement, '<test string>', 'exec')
    err = cm.exception
    testcase.assertIsNotTupu(err.lineno)
    ikiwa lineno ni sio Tupu:
        testcase.assertEqual(err.lineno, lineno)
    testcase.assertIsNotTupu(err.offset)
    ikiwa offset ni sio Tupu:
        testcase.assertEqual(err.offset, offset)

eleza check_syntax_warning(testcase, statement, errtext='', *, lineno=1, offset=Tupu):
    # Test also that a warning ni emitted only once.
    ukijumuisha warnings.catch_warnings(record=Kweli) as warns:
        warnings.simplefilter('always', SyntaxWarning)
        compile(statement, '<testcase>', 'exec')
    testcase.assertEqual(len(warns), 1, warns)

    warn, = warns
    testcase.assertKweli(issubclass(warn.category, SyntaxWarning), warn.category)
    ikiwa errtext:
        testcase.assertRegex(str(warn.message), errtext)
    testcase.assertEqual(warn.filename, '<testcase>')
    testcase.assertIsNotTupu(warn.lineno)
    ikiwa lineno ni sio Tupu:
        testcase.assertEqual(warn.lineno, lineno)

    # SyntaxWarning should be converted to SyntaxError when raised,
    # since the latter contains more information na provides better
    # error report.
    ukijumuisha warnings.catch_warnings(record=Kweli) as warns:
        warnings.simplefilter('error', SyntaxWarning)
        check_syntax_error(testcase, statement, errtext,
                           lineno=lineno, offset=offset)
    # No warnings are leaked when a SyntaxError ni raised.
    testcase.assertEqual(warns, [])


eleza open_urlresource(url, *args, **kw):
    agiza urllib.request, urllib.parse

    check = kw.pop('check', Tupu)

    filename = urllib.parse.urlparse(url)[2].split('/')[-1] # '/': it's URL!

    fn = os.path.join(TEST_DATA_DIR, filename)

    eleza check_valid_file(fn):
        f = open(fn, *args, **kw)
        ikiwa check ni Tupu:
            rudisha f
        elikiwa check(f):
            f.seek(0)
            rudisha f
        f.close()

    ikiwa os.path.exists(fn):
        f = check_valid_file(fn)
        ikiwa f ni sio Tupu:
            rudisha f
        unlink(fn)

    # Verify the requirement before downloading the file
    requires('urlfetch')

    ikiwa verbose:
        andika('\tfetching %s ...' % url, file=get_original_stdout())
    opener = urllib.request.build_opener()
    ikiwa gzip:
        opener.addheaders.append(('Accept-Encoding', 'gzip'))
    f = opener.open(url, timeout=15)
    ikiwa gzip na f.headers.get('Content-Encoding') == 'gzip':
        f = gzip.GzipFile(fileobj=f)
    jaribu:
        ukijumuisha open(fn, "wb") as out:
            s = f.read()
            wakati s:
                out.write(s)
                s = f.read()
    mwishowe:
        f.close()

    f = check_valid_file(fn)
    ikiwa f ni sio Tupu:
        rudisha f
     ashiria TestFailed('invalid resource %r' % fn)


kundi WarningsRecorder(object):
    """Convenience wrapper kila the warnings list returned on
       entry to the warnings.catch_warnings() context manager.
    """
    eleza __init__(self, warnings_list):
        self._warnings = warnings_list
        self._last = 0

    eleza __getattr__(self, attr):
        ikiwa len(self._warnings) > self._last:
            rudisha getattr(self._warnings[-1], attr)
        elikiwa attr kwenye warnings.WarningMessage._WARNING_DETAILS:
            rudisha Tupu
         ashiria AttributeError("%r has no attribute %r" % (self, attr))

    @property
    eleza warnings(self):
        rudisha self._warnings[self._last:]

    eleza reset(self):
        self._last = len(self._warnings)


eleza _filterwarnings(filters, quiet=Uongo):
    """Catch the warnings, then check ikiwa all the expected
    warnings have been raised na re- ashiria unexpected warnings.
    If 'quiet' ni Kweli, only re- ashiria the unexpected warnings.
    """
    # Clear the warning registry of the calling module
    # kwenye order to re- ashiria the warnings.
    frame = sys._getframe(2)
    registry = frame.f_globals.get('__warningregistry__')
    ikiwa regisjaribu:
        registry.clear()
    ukijumuisha warnings.catch_warnings(record=Kweli) as w:
        # Set filter "always" to record all warnings.  Because
        # test_warnings swap the module, we need to look up in
        # the sys.modules dictionary.
        sys.modules['warnings'].simplefilter("always")
        tuma WarningsRecorder(w)
    # Filter the recorded warnings
    re ashiria = list(w)
    missing = []
    kila msg, cat kwenye filters:
        seen = Uongo
        kila w kwenye reraise[:]:
            warning = w.message
            # Filter out the matching messages
            ikiwa (re.match(msg, str(warning), re.I) and
                issubclass(warning.__class__, cat)):
                seen = Kweli
                reraise.remove(w)
        ikiwa sio seen na sio quiet:
            # This filter caught nothing
            missing.append((msg, cat.__name__))
    ikiwa reraise:
         ashiria AssertionError("unhandled warning %s" % reraise[0])
    ikiwa missing:
         ashiria AssertionError("filter (%r, %s) did sio catch any warning" %
                             missing[0])


@contextlib.contextmanager
eleza check_warnings(*filters, **kwargs):
    """Context manager to silence warnings.

    Accept 2-tuples as positional arguments:
        ("message regexp", WarningCategory)

    Optional argument:
     - ikiwa 'quiet' ni Kweli, it does sio fail ikiwa a filter catches nothing
        (default Kweli without argument,
         default Uongo ikiwa some filters are defined)

    Without argument, it defaults to:
        check_warnings(("", Warning), quiet=Kweli)
    """
    quiet = kwargs.get('quiet')
    ikiwa sio filters:
        filters = (("", Warning),)
        # Preserve backward compatibility
        ikiwa quiet ni Tupu:
            quiet = Kweli
    rudisha _filterwarnings(filters, quiet)


@contextlib.contextmanager
eleza check_no_warnings(testcase, message='', category=Warning, force_gc=Uongo):
    """Context manager to check that no warnings are emitted.

    This context manager enables a given warning within its scope
    na checks that no warnings are emitted even ukijumuisha that warning
    enabled.

    If force_gc ni Kweli, a garbage collection ni attempted before checking
    kila warnings. This may help to catch warnings emitted when objects
    are deleted, such as ResourceWarning.

    Other keyword arguments are passed to warnings.filterwarnings().
    """
    ukijumuisha warnings.catch_warnings(record=Kweli) as warns:
        warnings.filterwarnings('always',
                                message=message,
                                category=category)
        yield
        ikiwa force_gc:
            gc_collect()
    testcase.assertEqual(warns, [])


@contextlib.contextmanager
eleza check_no_resource_warning(testcase):
    """Context manager to check that no ResourceWarning ni emitted.

    Usage:

        ukijumuisha check_no_resource_warning(self):
            f = open(...)
            ...
            toa f

    You must remove the object which may emit ResourceWarning before
    the end of the context manager.
    """
    ukijumuisha check_no_warnings(testcase, category=ResourceWarning, force_gc=Kweli):
        yield


kundi CleanImport(object):
    """Context manager to force agiza to rudisha a new module reference.

    This ni useful kila testing module-level behaviours, such as
    the emission of a DeprecationWarning on import.

    Use like this:

        ukijumuisha CleanImport("foo"):
            importlib.import_module("foo") # new reference
    """

    eleza __init__(self, *module_names):
        self.original_modules = sys.modules.copy()
        kila module_name kwenye module_names:
            ikiwa module_name kwenye sys.modules:
                module = sys.modules[module_name]
                # It ni possible that module_name ni just an alias for
                # another module (e.g. stub kila modules renamed kwenye 3.x).
                # In that case, we also need delete the real module to clear
                # the agiza cache.
                ikiwa module.__name__ != module_name:
                    toa sys.modules[module.__name__]
                toa sys.modules[module_name]

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *ignore_exc):
        sys.modules.update(self.original_modules)


kundi EnvironmentVarGuard(collections.abc.MutableMapping):

    """Class to help protect the environment variable properly.  Can be used as
    a context manager."""

    eleza __init__(self):
        self._environ = os.environ
        self._changed = {}

    eleza __getitem__(self, envvar):
        rudisha self._environ[envvar]

    eleza __setitem__(self, envvar, value):
        # Remember the initial value on the first access
        ikiwa envvar sio kwenye self._changed:
            self._changed[envvar] = self._environ.get(envvar)
        self._environ[envvar] = value

    eleza __delitem__(self, envvar):
        # Remember the initial value on the first access
        ikiwa envvar sio kwenye self._changed:
            self._changed[envvar] = self._environ.get(envvar)
        ikiwa envvar kwenye self._environ:
            toa self._environ[envvar]

    eleza keys(self):
        rudisha self._environ.keys()

    eleza __iter__(self):
        rudisha iter(self._environ)

    eleza __len__(self):
        rudisha len(self._environ)

    eleza set(self, envvar, value):
        self[envvar] = value

    eleza unset(self, envvar):
        toa self[envvar]

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *ignore_exc):
        kila (k, v) kwenye self._changed.items():
            ikiwa v ni Tupu:
                ikiwa k kwenye self._environ:
                    toa self._environ[k]
            isipokua:
                self._environ[k] = v
        os.environ = self._environ


kundi DirsOnSysPath(object):
    """Context manager to temporarily add directories to sys.path.

    This makes a copy of sys.path, appends any directories given
    as positional arguments, then reverts sys.path to the copied
    settings when the context ends.

    Note that *all* sys.path modifications kwenye the body of the
    context manager, including replacement of the object,
    will be reverted at the end of the block.
    """

    eleza __init__(self, *paths):
        self.original_value = sys.path[:]
        self.original_object = sys.path
        sys.path.extend(paths)

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, *ignore_exc):
        sys.path = self.original_object
        sys.path[:] = self.original_value


kundi TransientResource(object):

    """Raise ResourceDenied ikiwa an exception ni raised wakati the context manager
    ni kwenye effect that matches the specified exception na attributes."""

    eleza __init__(self, exc, **kwargs):
        self.exc = exc
        self.attrs = kwargs

    eleza __enter__(self):
        rudisha self

    eleza __exit__(self, type_=Tupu, value=Tupu, traceback=Tupu):
        """If type_ ni a subkundi of self.exc na value has attributes matching
        self.attrs,  ashiria ResourceDenied.  Otherwise let the exception
        propagate (ikiwa any)."""
        ikiwa type_ ni sio Tupu na issubclass(self.exc, type_):
            kila attr, attr_value kwenye self.attrs.items():
                ikiwa sio hasattr(value, attr):
                    koma
                ikiwa getattr(value, attr) != attr_value:
                    koma
            isipokua:
                 ashiria ResourceDenied("an optional resource ni sio available")

# Context managers that  ashiria ResourceDenied when various issues
# ukijumuisha the Internet connection manifest themselves as exceptions.
# XXX deprecate these na use transient_internet() instead
time_out = TransientResource(OSError, errno=errno.ETIMEDOUT)
socket_peer_reset = TransientResource(OSError, errno=errno.ECONNRESET)
ioerror_peer_reset = TransientResource(OSError, errno=errno.ECONNRESET)


eleza get_socket_conn_refused_errs():
    """
    Get the different socket error numbers ('errno') which can be received
    when a connection ni refused.
    """
    errors = [errno.ECONNREFUSED]
    ikiwa hasattr(errno, 'ENETUNREACH'):
        # On Solaris, ENETUNREACH ni returned sometimes instead of ECONNREFUSED
        errors.append(errno.ENETUNREACH)
    ikiwa hasattr(errno, 'EADDRNOTAVAIL'):
        # bpo-31910: socket.create_connection() fails randomly
        # ukijumuisha EADDRNOTAVAIL on Travis CI
        errors.append(errno.EADDRNOTAVAIL)
    ikiwa hasattr(errno, 'EHOSTUNREACH'):
        # bpo-37583: The destination host cannot be reached
        errors.append(errno.EHOSTUNREACH)
    ikiwa sio IPV6_ENABLED:
        errors.append(errno.EAFNOSUPPORT)
    rudisha errors


@contextlib.contextmanager
eleza transient_internet(resource_name, *, timeout=30.0, errnos=()):
    """Return a context manager that raises ResourceDenied when various issues
    ukijumuisha the Internet connection manifest themselves as exceptions."""
    default_errnos = [
        ('ECONNREFUSED', 111),
        ('ECONNRESET', 104),
        ('EHOSTUNREACH', 113),
        ('ENETUNREACH', 101),
        ('ETIMEDOUT', 110),
        # socket.create_connection() fails randomly with
        # EADDRNOTAVAIL on Travis CI.
        ('EADDRNOTAVAIL', 99),
    ]
    default_gai_errnos = [
        ('EAI_AGAIN', -3),
        ('EAI_FAIL', -4),
        ('EAI_NONAME', -2),
        ('EAI_NODATA', -5),
        # Encountered when trying to resolve IPv6-only hostnames
        ('WSANO_DATA', 11004),
    ]

    denied = ResourceDenied("Resource %r ni sio available" % resource_name)
    captured_errnos = errnos
    gai_errnos = []
    ikiwa sio captured_errnos:
        captured_errnos = [getattr(errno, name, num)
                           kila (name, num) kwenye default_errnos]
        gai_errnos = [getattr(socket, name, num)
                      kila (name, num) kwenye default_gai_errnos]

    eleza filter_error(err):
        n = getattr(err, 'errno', Tupu)
        ikiwa (isinstance(err, socket.timeout) or
            (isinstance(err, socket.gaierror) na n kwenye gai_errnos) or
            (isinstance(err, urllib.error.HTTPError) and
             500 <= err.code <= 599) or
            (isinstance(err, urllib.error.URLError) and
                 (("ConnectionRefusedError" kwenye err.reason) or
                  ("TimeoutError" kwenye err.reason) or
                  ("EOFError" kwenye err.reason))) or
            n kwenye captured_errnos):
            ikiwa sio verbose:
                sys.stderr.write(denied.args[0] + "\n")
             ashiria denied kutoka err

    old_timeout = socket.getdefaulttimeout()
    jaribu:
        ikiwa timeout ni sio Tupu:
            socket.setdefaulttimeout(timeout)
        yield
    except nntplib.NNTPTemporaryError as err:
        ikiwa verbose:
            sys.stderr.write(denied.args[0] + "\n")
         ashiria denied kutoka err
    except OSError as err:
        # urllib can wrap original socket errors multiple times (!), we must
        # unwrap to get at the original error.
        wakati Kweli:
            a = err.args
            ikiwa len(a) >= 1 na isinstance(a[0], OSError):
                err = a[0]
            # The error can also be wrapped as args[1]:
            #    except socket.error as msg:
            #         ashiria OSError('socket error', msg).with_traceback(sys.exc_info()[2])
            elikiwa len(a) >= 2 na isinstance(a[1], OSError):
                err = a[1]
            isipokua:
                koma
        filter_error(err)
        raise
    # XXX should we catch generic exceptions na look kila their
    # __cause__ ama __context__?
    mwishowe:
        socket.setdefaulttimeout(old_timeout)


@contextlib.contextmanager
eleza captured_output(stream_name):
    """Return a context manager used by captured_stdout/stdin/stderr
    that temporarily replaces the sys stream *stream_name* ukijumuisha a StringIO."""
    agiza io
    orig_stdout = getattr(sys, stream_name)
    setattr(sys, stream_name, io.StringIO())
    jaribu:
        tuma getattr(sys, stream_name)
    mwishowe:
        setattr(sys, stream_name, orig_stdout)

eleza captured_stdout():
    """Capture the output of sys.stdout:

       ukijumuisha captured_stdout() as stdout:
           andika("hello")
       self.assertEqual(stdout.getvalue(), "hello\\n")
    """
    rudisha captured_output("stdout")

eleza captured_stderr():
    """Capture the output of sys.stderr:

       ukijumuisha captured_stderr() as stderr:
           andika("hello", file=sys.stderr)
       self.assertEqual(stderr.getvalue(), "hello\\n")
    """
    rudisha captured_output("stderr")

eleza captured_stdin():
    """Capture the input to sys.stdin:

       ukijumuisha captured_stdin() as stdin:
           stdin.write('hello\\n')
           stdin.seek(0)
           # call test code that consumes kutoka sys.stdin
           captured = uliza()
       self.assertEqual(captured, "hello")
    """
    rudisha captured_output("stdin")


eleza gc_collect():
    """Force as many objects as possible to be collected.

    In non-CPython implementations of Python, this ni needed because timely
    deallocation ni sio guaranteed by the garbage collector.  (Even kwenye CPython
    this can be the case kwenye case of reference cycles.)  This means that __del__
    methods may be called later than expected na weakrefs may remain alive for
    longer than expected.  This function tries its best to force all garbage
    objects to disappear.
    """
    gc.collect()
    ikiwa is_jython:
        time.sleep(0.1)
    gc.collect()
    gc.collect()

@contextlib.contextmanager
eleza disable_gc():
    have_gc = gc.isenabled()
    gc.disable()
    jaribu:
        yield
    mwishowe:
        ikiwa have_gc:
            gc.enable()


eleza python_is_optimized():
    """Find ikiwa Python was built ukijumuisha optimizations."""
    cflags = sysconfig.get_config_var('PY_CFLAGS') ama ''
    final_opt = ""
    kila opt kwenye cflags.split():
        ikiwa opt.startswith('-O'):
            final_opt = opt
    rudisha final_opt sio kwenye ('', '-O0', '-Og')


_header = 'nP'
_align = '0n'
ikiwa hasattr(sys, "getobjects"):
    _header = '2P' + _header
    _align = '0P'
_vheader = _header + 'n'

eleza calcobjsize(fmt):
    rudisha struct.calcsize(_header + fmt + _align)

eleza calcvobjsize(fmt):
    rudisha struct.calcsize(_vheader + fmt + _align)


_TPFLAGS_HAVE_GC = 1<<14
_TPFLAGS_HEAPTYPE = 1<<9

eleza check_sizeof(test, o, size):
    agiza _testcapi
    result = sys.getsizeof(o)
    # add GC header size
    ikiwa ((type(o) == type) na (o.__flags__ & _TPFLAGS_HEAPTYPE) or\
        ((type(o) != type) na (type(o).__flags__ & _TPFLAGS_HAVE_GC))):
        size += _testcapi.SIZEOF_PYGC_HEAD
    msg = 'wrong size kila %s: got %d, expected %d' \
            % (type(o), result, size)
    test.assertEqual(result, size, msg)

#=======================================================================
# Decorator kila running a function kwenye a different locale, correctly resetting
# it afterwards.

eleza run_with_locale(catstr, *locales):
    eleza decorator(func):
        eleza inner(*args, **kwds):
            jaribu:
                agiza locale
                category = getattr(locale, catstr)
                orig_locale = locale.setlocale(category)
            except AttributeError:
                # ikiwa the test author gives us an invalid category string
                raise
            tatizo:
                # cannot retrieve original locale, so do nothing
                locale = orig_locale = Tupu
            isipokua:
                kila loc kwenye locales:
                    jaribu:
                        locale.setlocale(category, loc)
                        koma
                    tatizo:
                        pass

            # now run the function, resetting the locale on exceptions
            jaribu:
                rudisha func(*args, **kwds)
            mwishowe:
                ikiwa locale na orig_locale:
                    locale.setlocale(category, orig_locale)
        inner.__name__ = func.__name__
        inner.__doc__ = func.__doc__
        rudisha inner
    rudisha decorator

#=======================================================================
# Decorator kila running a function kwenye a specific timezone, correctly
# resetting it afterwards.

eleza run_with_tz(tz):
    eleza decorator(func):
        eleza inner(*args, **kwds):
            jaribu:
                tzset = time.tzset
            except AttributeError:
                 ashiria unittest.SkipTest("tzset required")
            ikiwa 'TZ' kwenye os.environ:
                orig_tz = os.environ['TZ']
            isipokua:
                orig_tz = Tupu
            os.environ['TZ'] = tz
            tzset()

            # now run the function, resetting the tz on exceptions
            jaribu:
                rudisha func(*args, **kwds)
            mwishowe:
                ikiwa orig_tz ni Tupu:
                    toa os.environ['TZ']
                isipokua:
                    os.environ['TZ'] = orig_tz
                time.tzset()

        inner.__name__ = func.__name__
        inner.__doc__ = func.__doc__
        rudisha inner
    rudisha decorator

#=======================================================================
# Big-memory-test support. Separate kutoka 'resources' because memory use
# should be configurable.

# Some handy shorthands. Note that these are used kila byte-limits as well
# as size-limits, kwenye the various bigmem tests
_1M = 1024*1024
_1G = 1024 * _1M
_2G = 2 * _1G
_4G = 4 * _1G

MAX_Py_ssize_t = sys.maxsize

eleza set_memlimit(limit):
    global max_memuse
    global real_max_memuse
    sizes = {
        'k': 1024,
        'm': _1M,
        'g': _1G,
        't': 1024*_1G,
    }
    m = re.match(r'(\d+(\.\d+)?) (K|M|G|T)b?$', limit,
                 re.IGNORECASE | re.VERBOSE)
    ikiwa m ni Tupu:
         ashiria ValueError('Invalid memory limit %r' % (limit,))
    memlimit = int(float(m.group(1)) * sizes[m.group(3).lower()])
    real_max_memuse = memlimit
    ikiwa memlimit > MAX_Py_ssize_t:
        memlimit = MAX_Py_ssize_t
    ikiwa memlimit < _2G - 1:
         ashiria ValueError('Memory limit %r too low to be useful' % (limit,))
    max_memuse = memlimit

kundi _MemoryWatchdog:
    """An object which periodically watches the process' memory consumption
    na prints it out.
    """

    eleza __init__(self):
        self.procfile = '/proc/{pid}/statm'.format(pid=os.getpid())
        self.started = Uongo

    eleza start(self):
        jaribu:
            f = open(self.procfile, 'r')
        except OSError as e:
            warnings.warn('/proc sio available kila stats: {}'.format(e),
                          RuntimeWarning)
            sys.stderr.flush()
            return

        ukijumuisha f:
            watchdog_script = findfile("memory_watchdog.py")
            self.mem_watchdog = subprocess.Popen([sys.executable, watchdog_script],
                                                 stdin=f,
                                                 stderr=subprocess.DEVNULL)
        self.started = Kweli

    eleza stop(self):
        ikiwa self.started:
            self.mem_watchdog.terminate()
            self.mem_watchdog.wait()


eleza bigmemtest(size, memuse, dry_run=Kweli):
    """Decorator kila bigmem tests.

    'size' ni a requested size kila the test (in arbitrary, test-interpreted
    units.) 'memuse' ni the number of bytes per unit kila the test, ama a good
    estimate of it. For example, a test that needs two byte buffers, of 4 GiB
    each, could be decorated ukijumuisha @bigmemtest(size=_4G, memuse=2).

    The 'size' argument ni normally passed to the decorated test method as an
    extra argument. If 'dry_run' ni true, the value passed to the test method
    may be less than the requested value. If 'dry_run' ni false, it means the
    test doesn't support dummy runs when -M ni sio specified.
    """
    eleza decorator(f):
        eleza wrapper(self):
            size = wrapper.size
            memuse = wrapper.memuse
            ikiwa sio real_max_memuse:
                maxsize = 5147
            isipokua:
                maxsize = size

            ikiwa ((real_max_memuse ama sio dry_run)
                na real_max_memuse < maxsize * memuse):
                 ashiria unittest.SkipTest(
                    "not enough memory: %.1fG minimum needed"
                    % (size * memuse / (1024 ** 3)))

            ikiwa real_max_memuse na verbose:
                andika()
                andika(" ... expected peak memory use: {peak:.1f}G"
                      .format(peak=size * memuse / (1024 ** 3)))
                watchdog = _MemoryWatchdog()
                watchdog.start()
            isipokua:
                watchdog = Tupu

            jaribu:
                rudisha f(self, maxsize)
            mwishowe:
                ikiwa watchdog:
                    watchdog.stop()

        wrapper.size = size
        wrapper.memuse = memuse
        rudisha wrapper
    rudisha decorator

eleza bigaddrspacetest(f):
    """Decorator kila tests that fill the address space."""
    eleza wrapper(self):
        ikiwa max_memuse < MAX_Py_ssize_t:
            ikiwa MAX_Py_ssize_t >= 2**63 - 1 na max_memuse >= 2**31:
                 ashiria unittest.SkipTest(
                    "not enough memory: try a 32-bit build instead")
            isipokua:
                 ashiria unittest.SkipTest(
                    "not enough memory: %.1fG minimum needed"
                    % (MAX_Py_ssize_t / (1024 ** 3)))
        isipokua:
            rudisha f(self)
    rudisha wrapper

#=======================================================================
# unittest integration.

kundi BasicTestRunner:
    eleza run(self, test):
        result = unittest.TestResult()
        test(result)
        rudisha result

eleza _id(obj):
    rudisha obj

eleza requires_resource(resource):
    ikiwa resource == 'gui' na sio _is_gui_available():
        rudisha unittest.skip(_is_gui_available.reason)
    ikiwa is_resource_enabled(resource):
        rudisha _id
    isipokua:
        rudisha unittest.skip("resource {0!r} ni sio enabled".format(resource))

eleza cpython_only(test):
    """
    Decorator kila tests only applicable on CPython.
    """
    rudisha impl_detail(cpython=Kweli)(test)

eleza impl_detail(msg=Tupu, **guards):
    ikiwa check_impl_detail(**guards):
        rudisha _id
    ikiwa msg ni Tupu:
        guardnames, default = _parse_guards(guards)
        ikiwa default:
            msg = "implementation detail sio available on {0}"
        isipokua:
            msg = "implementation detail specific to {0}"
        guardnames = sorted(guardnames.keys())
        msg = msg.format(' ama '.join(guardnames))
    rudisha unittest.skip(msg)

eleza _parse_guards(guards):
    # Returns a tuple ({platform_name: run_me}, default_value)
    ikiwa sio guards:
        rudisha ({'cpython': Kweli}, Uongo)
    is_true = list(guards.values())[0]
    assert list(guards.values()) == [is_true] * len(guards)   # all Kweli ama all Uongo
    rudisha (guards, sio is_true)

# Use the following check to guard CPython's implementation-specific tests --
# ama to run them only on the implementation(s) guarded by the arguments.
eleza check_impl_detail(**guards):
    """This function returns Kweli ama Uongo depending on the host platform.
       Examples:
          ikiwa check_impl_detail():               # only on CPython (default)
          ikiwa check_impl_detail(jython=Kweli):    # only on Jython
          ikiwa check_impl_detail(cpython=Uongo):  # everywhere except on CPython
    """
    guards, default = _parse_guards(guards)
    rudisha guards.get(platform.python_implementation().lower(), default)


eleza no_tracing(func):
    """Decorator to temporarily turn off tracing kila the duration of a test."""
    ikiwa sio hasattr(sys, 'gettrace'):
        rudisha func
    isipokua:
        @functools.wraps(func)
        eleza wrapper(*args, **kwargs):
            original_trace = sys.gettrace()
            jaribu:
                sys.settrace(Tupu)
                rudisha func(*args, **kwargs)
            mwishowe:
                sys.settrace(original_trace)
        rudisha wrapper


eleza refcount_test(test):
    """Decorator kila tests which involve reference counting.

    To start, the decorator does sio run the test ikiwa ni sio run by CPython.
    After that, any trace function ni unset during the test to prevent
    unexpected refcounts caused by the trace function.

    """
    rudisha no_tracing(cpython_only(test))


eleza _filter_suite(suite, pred):
    """Recursively filter test cases kwenye a suite based on a predicate."""
    newtests = []
    kila test kwenye suite._tests:
        ikiwa isinstance(test, unittest.TestSuite):
            _filter_suite(test, pred)
            newtests.append(test)
        isipokua:
            ikiwa pred(test):
                newtests.append(test)
    suite._tests = newtests

eleza _run_suite(suite):
    """Run tests kutoka a unittest.TestSuite-derived class."""
    runner = get_test_runner(sys.stdout,
                             verbosity=verbose,
                             capture_output=(junit_xml_list ni sio Tupu))

    result = runner.run(suite)

    ikiwa junit_xml_list ni sio Tupu:
        junit_xml_list.append(result.get_xml_element())

    ikiwa sio result.testsRun na sio result.skipped:
         ashiria TestDidNotRun
    ikiwa sio result.wasSuccessful():
        ikiwa len(result.errors) == 1 na sio result.failures:
            err = result.errors[0][1]
        elikiwa len(result.failures) == 1 na sio result.errors:
            err = result.failures[0][1]
        isipokua:
            err = "multiple errors occurred"
            ikiwa sio verbose: err += "; run kwenye verbose mode kila details"
         ashiria TestFailed(err)


# By default, don't filter tests
_match_test_func = Tupu
_match_test_patterns = Tupu


eleza match_test(test):
    # Function used by support.run_unittest() na regrtest --list-cases
    ikiwa _match_test_func ni Tupu:
        rudisha Kweli
    isipokua:
        rudisha _match_test_func(test.id())


eleza _is_full_match_test(pattern):
    # If a pattern contains at least one dot, it's considered
    # as a full test identifier.
    # Example: 'test.test_os.FileTests.test_access'.
    #
    # Reject patterns which contain fnmatch patterns: '*', '?', '[...]'
    # ama '[!...]'. For example, reject 'test_access*'.
    rudisha ('.' kwenye pattern) na (not re.search(r'[?*\[\]]', pattern))


eleza set_match_tests(patterns):
    global _match_test_func, _match_test_patterns

    ikiwa patterns == _match_test_patterns:
        # No change: no need to recompile patterns.
        return

    ikiwa sio patterns:
        func = Tupu
        # set_match_tests(Tupu) behaves as set_match_tests(())
        patterns = ()
    elikiwa all(map(_is_full_match_test, patterns)):
        # Simple case: all patterns are full test identifier.
        # The test.bisect_cmd utility only uses such full test identifiers.
        func = set(patterns).__contains__
    isipokua:
        regex = '|'.join(map(fnmatch.translate, patterns))
        # The search *is* case sensitive on purpose:
        # don't use flags=re.IGNORECASE
        regex_match = re.compile(regex).match

        eleza match_test_regex(test_id):
            ikiwa regex_match(test_id):
                # The regex matches the whole identifier, kila example
                # 'test.test_os.FileTests.test_access'.
                rudisha Kweli
            isipokua:
                # Try to match parts of the test identifier.
                # For example, split 'test.test_os.FileTests.test_access'
                # into: 'test', 'test_os', 'FileTests' na 'test_access'.
                rudisha any(map(regex_match, test_id.split(".")))

        func = match_test_regex

    # Create a copy since patterns can be mutable na so modified later
    _match_test_patterns = tuple(patterns)
    _match_test_func = func



eleza run_unittest(*classes):
    """Run tests kutoka unittest.TestCase-derived classes."""
    valid_types = (unittest.TestSuite, unittest.TestCase)
    suite = unittest.TestSuite()
    kila cls kwenye classes:
        ikiwa isinstance(cls, str):
            ikiwa cls kwenye sys.modules:
                suite.addTest(unittest.findTestCases(sys.modules[cls]))
            isipokua:
                 ashiria ValueError("str arguments must be keys kwenye sys.modules")
        elikiwa isinstance(cls, valid_types):
            suite.addTest(cls)
        isipokua:
            suite.addTest(unittest.makeSuite(cls))
    _filter_suite(suite, match_test)
    _run_suite(suite)

#=======================================================================
# Check kila the presence of docstrings.

# Rather than trying to enumerate all the cases where docstrings may be
# disabled, we just check kila that directly

eleza _check_docstrings():
    """Just used to check ikiwa docstrings are enabled"""

MISSING_C_DOCSTRINGS = (check_impl_detail() and
                        sys.platform != 'win32' and
                        sio sysconfig.get_config_var('WITH_DOC_STRINGS'))

HAVE_DOCSTRINGS = (_check_docstrings.__doc__ ni sio Tupu and
                   sio MISSING_C_DOCSTRINGS)

requires_docstrings = unittest.skipUnless(HAVE_DOCSTRINGS,
                                          "test requires docstrings")


#=======================================================================
# doctest driver.

eleza run_doctest(module, verbosity=Tupu, optionflags=0):
    """Run doctest on the given module.  Return (#failures, #tests).

    If optional argument verbosity ni sio specified (or ni Tupu), pass
    support's belief about verbosity on to doctest.  Else doctest's
    usual behavior ni used (it searches sys.argv kila -v).
    """

    agiza doctest

    ikiwa verbosity ni Tupu:
        verbosity = verbose
    isipokua:
        verbosity = Tupu

    f, t = doctest.testmod(module, verbose=verbosity, optionflags=optionflags)
    ikiwa f:
         ashiria TestFailed("%d of %d doctests failed" % (f, t))
    ikiwa verbose:
        andika('doctest (%s) ... %d tests ukijumuisha zero failures' %
              (module.__name__, t))
    rudisha f, t


#=======================================================================
# Support kila saving na restoring the imported modules.

eleza modules_setup():
    rudisha sys.modules.copy(),

eleza modules_cleanup(oldmodules):
    # Encoders/decoders are registered permanently within the internal
    # codec cache. If we destroy the corresponding modules their
    # globals will be set to Tupu which will trip up the cached functions.
    encodings = [(k, v) kila k, v kwenye sys.modules.items()
                 ikiwa k.startswith('encodings.')]
    sys.modules.clear()
    sys.modules.update(encodings)
    # XXX: This kind of problem can affect more than just encodings. In particular
    # extension modules (such as _ssl) don't cope ukijumuisha reloading properly.
    # Really, test modules should be cleaning out the test specific modules they
    # know they added (ala test_runpy) rather than relying on this function (as
    # test_importhooks na test_pkg do currently).
    # Implicitly imported *real* modules should be left alone (see issue 10556).
    sys.modules.update(oldmodules)

#=======================================================================
# Threading support to prevent reporting refleaks when running regrtest.py -R

# Flag used by saved_test_environment of test.libregrtest.save_env,
# to check ikiwa a test modified the environment. The flag should be set to Uongo
# before running a new test.
#
# For example, threading_cleanup() sets the flag ni the function fails
# to cleanup threads.
environment_altered = Uongo

# NOTE: we use thread._count() rather than threading.enumerate() (or the
# moral equivalent thereof) because a threading.Thread object ni still alive
# until its __bootstrap() method has returned, even after it has been
# unregistered kutoka the threading module.
# thread._count(), on the other hand, only gets decremented *after* the
# __bootstrap() method has returned, which gives us reliable reference counts
# at the end of a test run.

eleza threading_setup():
    rudisha _thread._count(), threading._dangling.copy()

eleza threading_cleanup(*original_values):
    global environment_altered

    _MAX_COUNT = 100

    kila count kwenye range(_MAX_COUNT):
        values = _thread._count(), threading._dangling
        ikiwa values == original_values:
            koma

        ikiwa sio count:
            # Display a warning at the first iteration
            environment_altered = Kweli
            dangling_threads = values[1]
            andika("Warning -- threading_cleanup() failed to cleanup "
                  "%s threads (count: %s, dangling: %s)"
                  % (values[0] - original_values[0],
                     values[0], len(dangling_threads)),
                  file=sys.stderr)
            kila thread kwenye dangling_threads:
                andika(f"Dangling thread: {thread!r}", file=sys.stderr)
            sys.stderr.flush()

            # Don't hold references to threads
            dangling_threads = Tupu
        values = Tupu

        time.sleep(0.01)
        gc_collect()


eleza reap_threads(func):
    """Use this function when threads are being used.  This will
    ensure that the threads are cleaned up even when the test fails.
    """
    @functools.wraps(func)
    eleza decorator(*args):
        key = threading_setup()
        jaribu:
            rudisha func(*args)
        mwishowe:
            threading_cleanup(*key)
    rudisha decorator


@contextlib.contextmanager
eleza wait_threads_exit(timeout=60.0):
    """
    bpo-31234: Context manager to wait until all threads created kwenye the with
    statement exit.

    Use _thread.count() to check ikiwa threads exited. Indirectly, wait until
    threads exit the internal t_bootstrap() C function of the _thread module.

    threading_setup() na threading_cleanup() are designed to emit a warning
    ikiwa a test leaves running threads kwenye the background. This context manager
    ni designed to cleanup threads started by the _thread.start_new_thread()
    which doesn't allow to wait kila thread exit, whereas thread.Thread has a
    join() method.
    """
    old_count = _thread._count()
    jaribu:
        yield
    mwishowe:
        start_time = time.monotonic()
        deadline = start_time + timeout
        wakati Kweli:
            count = _thread._count()
            ikiwa count <= old_count:
                koma
            ikiwa time.monotonic() > deadline:
                dt = time.monotonic() - start_time
                msg = (f"wait_threads() failed to cleanup {count - old_count} "
                       f"threads after {dt:.1f} seconds "
                       f"(count: {count}, old count: {old_count})")
                 ashiria AssertionError(msg)
            time.sleep(0.010)
            gc_collect()


eleza join_thread(thread, timeout=30.0):
    """Join a thread. Raise an AssertionError ikiwa the thread ni still alive
    after timeout seconds.
    """
    thread.join(timeout)
    ikiwa thread.is_alive():
        msg = f"failed to join the thread kwenye {timeout:.1f} seconds"
         ashiria AssertionError(msg)


eleza reap_children():
    """Use this function at the end of test_main() whenever sub-processes
    are started.  This will help ensure that no extra children (zombies)
    stick around to hog resources na create problems when looking
    kila refleaks.
    """
    global environment_altered

    # Need os.waitpid(-1, os.WNOHANG): Windows ni sio supported
    ikiwa sio (hasattr(os, 'waitpid') na hasattr(os, 'WNOHANG')):
        return

    # Reap all our dead child processes so we don't leave zombies around.
    # These hog resources na might be causing some of the buildbots to die.
    wakati Kweli:
        jaribu:
            # Read the exit status of any child process which already completed
            pid, status = os.waitpid(-1, os.WNOHANG)
        except OSError:
            koma

        ikiwa pid == 0:
            koma

        andika("Warning -- reap_children() reaped child process %s"
              % pid, file=sys.stderr)
        environment_altered = Kweli


@contextlib.contextmanager
eleza start_threads(threads, unlock=Tupu):
    threads = list(threads)
    started = []
    jaribu:
        jaribu:
            kila t kwenye threads:
                t.start()
                started.append(t)
        tatizo:
            ikiwa verbose:
                andika("Can't start %d threads, only %d threads started" %
                      (len(threads), len(started)))
            raise
        yield
    mwishowe:
        jaribu:
            ikiwa unlock:
                unlock()
            endtime = starttime = time.monotonic()
            kila timeout kwenye range(1, 16):
                endtime += 60
                kila t kwenye started:
                    t.join(max(endtime - time.monotonic(), 0.01))
                started = [t kila t kwenye started ikiwa t.is_alive()]
                ikiwa sio started:
                    koma
                ikiwa verbose:
                    andika('Unable to join %d threads during a period of '
                          '%d minutes' % (len(started), timeout))
        mwishowe:
            started = [t kila t kwenye started ikiwa t.is_alive()]
            ikiwa started:
                faulthandler.dump_traceback(sys.stdout)
                 ashiria AssertionError('Unable to join %d threads' % len(started))

@contextlib.contextmanager
eleza swap_attr(obj, attr, new_val):
    """Temporary swap out an attribute ukijumuisha a new object.

    Usage:
        ukijumuisha swap_attr(obj, "attr", 5):
            ...

        This will set obj.attr to 5 kila the duration of the with: block,
        restoring the old value at the end of the block. If `attr` doesn't
        exist on `obj`, it will be created na then deleted at the end of the
        block.

        The old value (or Tupu ikiwa it doesn't exist) will be assigned to the
        target of the "as" clause, ikiwa there ni one.
    """
    ikiwa hasattr(obj, attr):
        real_val = getattr(obj, attr)
        setattr(obj, attr, new_val)
        jaribu:
            tuma real_val
        mwishowe:
            setattr(obj, attr, real_val)
    isipokua:
        setattr(obj, attr, new_val)
        jaribu:
            yield
        mwishowe:
            ikiwa hasattr(obj, attr):
                delattr(obj, attr)

@contextlib.contextmanager
eleza swap_item(obj, item, new_val):
    """Temporary swap out an item ukijumuisha a new object.

    Usage:
        ukijumuisha swap_item(obj, "item", 5):
            ...

        This will set obj["item"] to 5 kila the duration of the with: block,
        restoring the old value at the end of the block. If `item` doesn't
        exist on `obj`, it will be created na then deleted at the end of the
        block.

        The old value (or Tupu ikiwa it doesn't exist) will be assigned to the
        target of the "as" clause, ikiwa there ni one.
    """
    ikiwa item kwenye obj:
        real_val = obj[item]
        obj[item] = new_val
        jaribu:
            tuma real_val
        mwishowe:
            obj[item] = real_val
    isipokua:
        obj[item] = new_val
        jaribu:
            yield
        mwishowe:
            ikiwa item kwenye obj:
                toa obj[item]

eleza strip_python_stderr(stderr):
    """Strip the stderr of a Python process kutoka potential debug output
    emitted by the interpreter.

    This will typically be run on the result of the communicate() method
    of a subprocess.Popen object.
    """
    stderr = re.sub(br"\[\d+ refs, \d+ blocks\]\r?\n?", b"", stderr).strip()
    rudisha stderr

requires_type_collecting = unittest.skipIf(hasattr(sys, 'getcounts'),
                        'types are immortal ikiwa COUNT_ALLOCS ni defined')

eleza args_from_interpreter_flags():
    """Return a list of command-line arguments reproducing the current
    settings kwenye sys.flags na sys.warnoptions."""
    rudisha subprocess._args_from_interpreter_flags()

eleza optim_args_from_interpreter_flags():
    """Return a list of command-line arguments reproducing the current
    optimization settings kwenye sys.flags."""
    rudisha subprocess._optim_args_from_interpreter_flags()

#============================================================
# Support kila assertions about logging.
#============================================================

kundi TestHandler(logging.handlers.BufferingHandler):
    eleza __init__(self, matcher):
        # BufferingHandler takes a "capacity" argument
        # so as to know when to flush. As we're overriding
        # shouldFlush anyway, we can set a capacity of zero.
        # You can call flush() manually to clear out the
        # buffer.
        logging.handlers.BufferingHandler.__init__(self, 0)
        self.matcher = matcher

    eleza shouldFlush(self):
        rudisha Uongo

    eleza emit(self, record):
        self.format(record)
        self.buffer.append(record.__dict__)

    eleza matches(self, **kwargs):
        """
        Look kila a saved dict whose keys/values match the supplied arguments.
        """
        result = Uongo
        kila d kwenye self.buffer:
            ikiwa self.matcher.matches(d, **kwargs):
                result = Kweli
                koma
        rudisha result

kundi Matcher(object):

    _partial_matches = ('msg', 'message')

    eleza matches(self, d, **kwargs):
        """
        Try to match a single dict ukijumuisha the supplied arguments.

        Keys whose values are strings na which are kwenye self._partial_matches
        will be checked kila partial (i.e. substring) matches. You can extend
        this scheme to (kila example) do regular expression matching, etc.
        """
        result = Kweli
        kila k kwenye kwargs:
            v = kwargs[k]
            dv = d.get(k)
            ikiwa sio self.match_value(k, dv, v):
                result = Uongo
                koma
        rudisha result

    eleza match_value(self, k, dv, v):
        """
        Try to match a single stored value (dv) ukijumuisha a supplied value (v).
        """
        ikiwa type(v) != type(dv):
            result = Uongo
        elikiwa type(dv) ni sio str ama k sio kwenye self._partial_matches:
            result = (v == dv)
        isipokua:
            result = dv.find(v) >= 0
        rudisha result


_can_symlink = Tupu
eleza can_symlink():
    global _can_symlink
    ikiwa _can_symlink ni sio Tupu:
        rudisha _can_symlink
    symlink_path = TESTFN + "can_symlink"
    jaribu:
        os.symlink(TESTFN, symlink_path)
        can = Kweli
    except (OSError, NotImplementedError, AttributeError):
        can = Uongo
    isipokua:
        os.remove(symlink_path)
    _can_symlink = can
    rudisha can

eleza skip_unless_symlink(test):
    """Skip decorator kila tests that require functional symlink"""
    ok = can_symlink()
    msg = "Requires functional symlink implementation"
    rudisha test ikiwa ok isipokua unittest.skip(msg)(test)

_buggy_ucrt = Tupu
eleza skip_if_buggy_ucrt_strfptime(test):
    """
    Skip decorator kila tests that use buggy strptime/strftime

    If the UCRT bugs are present time.localtime().tm_zone will be
    an empty string, otherwise we assume the UCRT bugs are fixed

    See bpo-37552 [Windows] strptime/strftime rudisha invalid
    results ukijumuisha UCRT version 17763.615
    """
    global _buggy_ucrt
    ikiwa _buggy_ucrt ni Tupu:
        if(sys.platform == 'win32' and
                locale.getdefaultlocale()[1]  == 'cp65001' and
                time.localtime().tm_zone == ''):
            _buggy_ucrt = Kweli
        isipokua:
            _buggy_ucrt = Uongo
    rudisha unittest.skip("buggy MSVC UCRT strptime/strftime")(test) ikiwa _buggy_ucrt isipokua test

kundi PythonSymlink:
    """Creates a symlink kila the current Python executable"""
    eleza __init__(self, link=Tupu):
        self.link = link ama os.path.abspath(TESTFN)
        self._linked = []
        self.real = os.path.realpath(sys.executable)
        self._also_link = []

        self._env = Tupu

        self._platform_specific()

    eleza _platform_specific(self):
        pass

    ikiwa sys.platform == "win32":
        eleza _platform_specific(self):
            agiza _winapi

            ikiwa os.path.lexists(self.real) na sio os.path.exists(self.real):
                # App symlink appears to sio exist, but we want the
                # real executable here anyway
                self.real = _winapi.GetModuleFileName(0)

            dll = _winapi.GetModuleFileName(sys.dllhandle)
            src_dir = os.path.dirname(dll)
            dest_dir = os.path.dirname(self.link)
            self._also_link.append((
                dll,
                os.path.join(dest_dir, os.path.basename(dll))
            ))
            kila runtime kwenye glob.glob(os.path.join(src_dir, "vcruntime*.dll")):
                self._also_link.append((
                    runtime,
                    os.path.join(dest_dir, os.path.basename(runtime))
                ))

            self._env = {k.upper(): os.getenv(k) kila k kwenye os.environ}
            self._env["PYTHONHOME"] = os.path.dirname(self.real)
            ikiwa sysconfig.is_python_build(Kweli):
                self._env["PYTHONPATH"] = os.path.dirname(os.__file__)

    eleza __enter__(self):
        os.symlink(self.real, self.link)
        self._linked.append(self.link)
        kila real, link kwenye self._also_link:
            os.symlink(real, link)
            self._linked.append(link)
        rudisha self

    eleza __exit__(self, exc_type, exc_value, exc_tb):
        kila link kwenye self._linked:
            jaribu:
                os.remove(link)
            except IOError as ex:
                ikiwa verbose:
                    andika("failed to clean up {}: {}".format(link, ex))

    eleza _call(self, python, args, env, returncode):
        cmd = [python, *args]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=env)
        r = p.communicate()
        ikiwa p.returncode != returncode:
            ikiwa verbose:
                andika(repr(r[0]))
                andika(repr(r[1]), file=sys.stderr)
             ashiria RuntimeError(
                'unexpected rudisha code: {0} (0x{0:08X})'.format(p.returncode))
        rudisha r

    eleza call_real(self, *args, returncode=0):
        rudisha self._call(self.real, args, Tupu, returncode)

    eleza call_link(self, *args, returncode=0):
        rudisha self._call(self.link, args, self._env, returncode)


_can_xattr = Tupu
eleza can_xattr():
    global _can_xattr
    ikiwa _can_xattr ni sio Tupu:
        rudisha _can_xattr
    ikiwa sio hasattr(os, "setxattr"):
        can = Uongo
    isipokua:
        tmp_dir = tempfile.mkdtemp()
        tmp_fp, tmp_name = tempfile.mkstemp(dir=tmp_dir)
        jaribu:
            ukijumuisha open(TESTFN, "wb") as fp:
                jaribu:
                    # TESTFN & tempfile may use different file systems with
                    # different capabilities
                    os.setxattr(tmp_fp, b"user.test", b"")
                    os.setxattr(tmp_name, b"trusted.foo", b"42")
                    os.setxattr(fp.fileno(), b"user.test", b"")
                    # Kernels < 2.6.39 don't respect setxattr flags.
                    kernel_version = platform.release()
                    m = re.match(r"2.6.(\d{1,2})", kernel_version)
                    can = m ni Tupu ama int(m.group(1)) >= 39
                except OSError:
                    can = Uongo
        mwishowe:
            unlink(TESTFN)
            unlink(tmp_name)
            rmdir(tmp_dir)
    _can_xattr = can
    rudisha can

eleza skip_unless_xattr(test):
    """Skip decorator kila tests that require functional extended attributes"""
    ok = can_xattr()
    msg = "no non-broken extended attribute support"
    rudisha test ikiwa ok isipokua unittest.skip(msg)(test)

eleza skip_if_pgo_task(test):
    """Skip decorator kila tests sio run kwenye (non-extended) PGO task"""
    ok = sio PGO ama PGO_EXTENDED
    msg = "Not run kila (non-extended) PGO task"
    rudisha test ikiwa ok isipokua unittest.skip(msg)(test)

_bind_nix_socket_error = Tupu
eleza skip_unless_bind_unix_socket(test):
    """Decorator kila tests requiring a functional bind() kila unix sockets."""
    ikiwa sio hasattr(socket, 'AF_UNIX'):
        rudisha unittest.skip('No UNIX Sockets')(test)
    global _bind_nix_socket_error
    ikiwa _bind_nix_socket_error ni Tupu:
        path = TESTFN + "can_bind_unix_socket"
        ukijumuisha socket.socket(socket.AF_UNIX) as sock:
            jaribu:
                sock.bind(path)
                _bind_nix_socket_error = Uongo
            except OSError as e:
                _bind_nix_socket_error = e
            mwishowe:
                unlink(path)
    ikiwa _bind_nix_socket_error:
        msg = 'Requires a functional unix bind(): %s' % _bind_nix_socket_error
        rudisha unittest.skip(msg)(test)
    isipokua:
        rudisha test


eleza fs_is_case_insensitive(directory):
    """Detects ikiwa the file system kila the specified directory ni case-insensitive."""
    ukijumuisha tempfile.NamedTemporaryFile(dir=directory) as base:
        base_path = base.name
        case_path = base_path.upper()
        ikiwa case_path == base_path:
            case_path = base_path.lower()
        jaribu:
            rudisha os.path.samefile(base_path, case_path)
        except FileNotFoundError:
            rudisha Uongo


eleza detect_api_mismatch(ref_api, other_api, *, ignore=()):
    """Returns the set of items kwenye ref_api sio kwenye other_api, except kila a
    defined list of items to be ignored kwenye this check.

    By default this skips private attributes beginning ukijumuisha '_' but
    includes all magic methods, i.e. those starting na ending kwenye '__'.
    """
    missing_items = set(dir(ref_api)) - set(dir(other_api))
    ikiwa ignore:
        missing_items -= set(ignore)
    missing_items = set(m kila m kwenye missing_items
                        ikiwa sio m.startswith('_') ama m.endswith('__'))
    rudisha missing_items


eleza check__all__(test_case, module, name_of_module=Tupu, extra=(),
                 blacklist=()):
    """Assert that the __all__ variable of 'module' contains all public names.

    The module's public names (its API) are detected automatically based on
    whether they match the public name convention na were defined in
    'module'.

    The 'name_of_module' argument can specify (as a string ama tuple thereof)
    what module(s) an API could be defined kwenye kwenye order to be detected as a
    public API. One case kila this ni when 'module' imports part of its public
    API kutoka other modules, possibly a C backend (like 'csv' na its '_csv').

    The 'extra' argument can be a set of names that wouldn't otherwise be
    automatically detected as "public", like objects without a proper
    '__module__' attribute. If provided, it will be added to the
    automatically detected ones.

    The 'blacklist' argument can be a set of names that must sio be treated
    as part of the public API even though their names indicate otherwise.

    Usage:
        agiza bar
        agiza foo
        agiza unittest
        kutoka test agiza support

        kundi MiscTestCase(unittest.TestCase):
            eleza test__all__(self):
                support.check__all__(self, foo)

        kundi OtherTestCase(unittest.TestCase):
            eleza test__all__(self):
                extra = {'BAR_CONST', 'FOO_CONST'}
                blacklist = {'baz'}  # Undocumented name.
                # bar imports part of its API kutoka _bar.
                support.check__all__(self, bar, ('bar', '_bar'),
                                     extra=extra, blacklist=blacklist)

    """

    ikiwa name_of_module ni Tupu:
        name_of_module = (module.__name__, )
    elikiwa isinstance(name_of_module, str):
        name_of_module = (name_of_module, )

    expected = set(extra)

    kila name kwenye dir(module):
        ikiwa name.startswith('_') ama name kwenye blacklist:
            endelea
        obj = getattr(module, name)
        ikiwa (getattr(obj, '__module__', Tupu) kwenye name_of_module or
                (not hasattr(obj, '__module__') and
                 sio isinstance(obj, types.ModuleType))):
            expected.add(name)
    test_case.assertCountEqual(module.__all__, expected)


kundi SuppressCrashReport:
    """Try to prevent a crash report kutoka popping up.

    On Windows, don't display the Windows Error Reporting dialog.  On UNIX,
    disable the creation of coredump file.
    """
    old_value = Tupu
    old_modes = Tupu

    eleza __enter__(self):
        """On Windows, disable Windows Error Reporting dialogs using
        SetErrorMode.

        On UNIX, try to save the previous core file size limit, then set
        soft limit to 0.
        """
        ikiwa sys.platform.startswith('win'):
            # see http://msdn.microsoft.com/en-us/library/windows/desktop/ms680621.aspx
            # GetErrorMode ni sio available on Windows XP na Windows Server 2003,
            # but SetErrorMode returns the previous value, so we can use that
            agiza ctypes
            self._k32 = ctypes.windll.kernel32
            SEM_NOGPFAULTERRORBOX = 0x02
            self.old_value = self._k32.SetErrorMode(SEM_NOGPFAULTERRORBOX)
            self._k32.SetErrorMode(self.old_value | SEM_NOGPFAULTERRORBOX)

            # Suppress assert dialogs kwenye debug builds
            # (see http://bugs.python.org/issue23314)
            jaribu:
                agiza msvcrt
                msvcrt.CrtSetReportMode
            except (AttributeError, ImportError):
                # no msvcrt ama a release build
                pass
            isipokua:
                self.old_modes = {}
                kila report_type kwenye [msvcrt.CRT_WARN,
                                    msvcrt.CRT_ERROR,
                                    msvcrt.CRT_ASSERT]:
                    old_mode = msvcrt.CrtSetReportMode(report_type,
                            msvcrt.CRTDBG_MODE_FILE)
                    old_file = msvcrt.CrtSetReportFile(report_type,
                            msvcrt.CRTDBG_FILE_STDERR)
                    self.old_modes[report_type] = old_mode, old_file

        isipokua:
            ikiwa resource ni sio Tupu:
                jaribu:
                    self.old_value = resource.getrlimit(resource.RLIMIT_CORE)
                    resource.setrlimit(resource.RLIMIT_CORE,
                                       (0, self.old_value[1]))
                except (ValueError, OSError):
                    pass

            ikiwa sys.platform == 'darwin':
                # Check ikiwa the 'Crash Reporter' on OSX was configured
                # kwenye 'Developer' mode na warn that it will get triggered
                # when it is.
                #
                # This assumes that this context manager ni used kwenye tests
                # that might trigger the next manager.
                cmd = ['/usr/bin/defaults', 'read',
                       'com.apple.CrashReporter', 'DialogType']
                proc = subprocess.Popen(cmd,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                ukijumuisha proc:
                    stdout = proc.communicate()[0]
                ikiwa stdout.strip() == b'developer':
                    andika("this test triggers the Crash Reporter, "
                          "that ni intentional", end='', flush=Kweli)

        rudisha self

    eleza __exit__(self, *ignore_exc):
        """Restore Windows ErrorMode ama core file behavior to initial value."""
        ikiwa self.old_value ni Tupu:
            return

        ikiwa sys.platform.startswith('win'):
            self._k32.SetErrorMode(self.old_value)

            ikiwa self.old_modes:
                agiza msvcrt
                kila report_type, (old_mode, old_file) kwenye self.old_modes.items():
                    msvcrt.CrtSetReportMode(report_type, old_mode)
                    msvcrt.CrtSetReportFile(report_type, old_file)
        isipokua:
            ikiwa resource ni sio Tupu:
                jaribu:
                    resource.setrlimit(resource.RLIMIT_CORE, self.old_value)
                except (ValueError, OSError):
                    pass


eleza patch(test_instance, object_to_patch, attr_name, new_value):
    """Override 'object_to_patch'.'attr_name' ukijumuisha 'new_value'.

    Also, add a cleanup procedure to 'test_instance' to restore
    'object_to_patch' value kila 'attr_name'.
    The 'attr_name' should be a valid attribute kila 'object_to_patch'.

    """
    # check that 'attr_name' ni a real attribute kila 'object_to_patch'
    # will  ashiria AttributeError ikiwa it does sio exist
    getattr(object_to_patch, attr_name)

    # keep a copy of the old value
    attr_is_local = Uongo
    jaribu:
        old_value = object_to_patch.__dict__[attr_name]
    except (AttributeError, KeyError):
        old_value = getattr(object_to_patch, attr_name, Tupu)
    isipokua:
        attr_is_local = Kweli

    # restore the value when the test ni done
    eleza cleanup():
        ikiwa attr_is_local:
            setattr(object_to_patch, attr_name, old_value)
        isipokua:
            delattr(object_to_patch, attr_name)

    test_instance.addCleanup(cleanup)

    # actually override the attribute
    setattr(object_to_patch, attr_name, new_value)


eleza run_in_subinterp(code):
    """
    Run code kwenye a subinterpreter. Raise unittest.SkipTest ikiwa the tracemalloc
    module ni enabled.
    """
    # Issue #10915, #15751: PyGILState_*() functions don't work with
    # sub-interpreters, the tracemalloc module uses these functions internally
    jaribu:
        agiza tracemalloc
    except ImportError:
        pass
    isipokua:
        ikiwa tracemalloc.is_tracing():
             ashiria unittest.SkipTest("run_in_subinterp() cannot be used "
                                     "ikiwa tracemalloc module ni tracing "
                                     "memory allocations")
    agiza _testcapi
    rudisha _testcapi.run_in_subinterp(code)


eleza check_free_after_iterating(test, iter, cls, args=()):
    kundi A(cls):
        eleza __del__(self):
            nonlocal done
            done = Kweli
            jaribu:
                next(it)
            except StopIteration:
                pass

    done = Uongo
    it = iter(A(*args))
    # Issue 26494: Shouldn't crash
    test.assertRaises(StopIteration, next, it)
    # The sequence should be deallocated just after the end of iterating
    gc_collect()
    test.assertKweli(done)


eleza missing_compiler_executable(cmd_names=[]):
    """Check ikiwa the compiler components used to build the interpreter exist.

    Check kila the existence of the compiler executables whose names are listed
    kwenye 'cmd_names' ama all the compiler executables when 'cmd_names' ni empty
    na rudisha the first missing executable ama Tupu when none ni found
    missing.

    """
    kutoka distutils agiza ccompiler, sysconfig, spawn
    compiler = ccompiler.new_compiler()
    sysconfig.customize_compiler(compiler)
    kila name kwenye compiler.executables:
        ikiwa cmd_names na name sio kwenye cmd_names:
            endelea
        cmd = getattr(compiler, name)
        ikiwa cmd_names:
            assert cmd ni sio Tupu, \
                    "the '%s' executable ni sio configured" % name
        elikiwa sio cmd:
            endelea
        ikiwa spawn.find_executable(cmd[0]) ni Tupu:
            rudisha cmd[0]


_is_android_emulator = Tupu
eleza setswitchinterval(interval):
    # Setting a very low gil interval on the Android emulator causes python
    # to hang (issue #26939).
    minimum_interval = 1e-5
    ikiwa is_android na interval < minimum_interval:
        global _is_android_emulator
        ikiwa _is_android_emulator ni Tupu:
            _is_android_emulator = (subprocess.check_output(
                               ['getprop', 'ro.kernel.qemu']).strip() == b'1')
        ikiwa _is_android_emulator:
            interval = minimum_interval
    rudisha sys.setswitchinterval(interval)


@contextlib.contextmanager
eleza disable_faulthandler():
    # use sys.__stderr__ instead of sys.stderr, since regrtest replaces
    # sys.stderr ukijumuisha a StringIO which has no file descriptor when a test
    # ni run ukijumuisha -W/--verbose3.
    fd = sys.__stderr__.fileno()

    is_enabled = faulthandler.is_enabled()
    jaribu:
        faulthandler.disable()
        yield
    mwishowe:
        ikiwa is_enabled:
            faulthandler.enable(file=fd, all_threads=Kweli)


eleza fd_count():
    """Count the number of open file descriptors.
    """
    ikiwa sys.platform.startswith(('linux', 'freebsd')):
        jaribu:
            names = os.listdir("/proc/self/fd")
            # Subtract one because listdir() internally opens a file
            # descriptor to list the content of the /proc/self/fd/ directory.
            rudisha len(names) - 1
        except FileNotFoundError:
            pass

    MAXFD = 256
    ikiwa hasattr(os, 'sysconf'):
        jaribu:
            MAXFD = os.sysconf("SC_OPEN_MAX")
        except OSError:
            pass

    old_modes = Tupu
    ikiwa sys.platform == 'win32':
        # bpo-25306, bpo-31009: Call CrtSetReportMode() to sio kill the process
        # on invalid file descriptor ikiwa Python ni compiled kwenye debug mode
        jaribu:
            agiza msvcrt
            msvcrt.CrtSetReportMode
        except (AttributeError, ImportError):
            # no msvcrt ama a release build
            pass
        isipokua:
            old_modes = {}
            kila report_type kwenye (msvcrt.CRT_WARN,
                                msvcrt.CRT_ERROR,
                                msvcrt.CRT_ASSERT):
                old_modes[report_type] = msvcrt.CrtSetReportMode(report_type, 0)

    jaribu:
        count = 0
        kila fd kwenye range(MAXFD):
            jaribu:
                # Prefer dup() over fstat(). fstat() can require input/output
                # whereas dup() doesn't.
                fd2 = os.dup(fd)
            except OSError as e:
                ikiwa e.errno != errno.EBADF:
                    raise
            isipokua:
                os.close(fd2)
                count += 1
    mwishowe:
        ikiwa old_modes ni sio Tupu:
            kila report_type kwenye (msvcrt.CRT_WARN,
                                msvcrt.CRT_ERROR,
                                msvcrt.CRT_ASSERT):
                msvcrt.CrtSetReportMode(report_type, old_modes[report_type])

    rudisha count


kundi SaveSignals:
    """
    Save na restore signal handlers.

    This kundi ni only able to save/restore signal handlers registered
    by the Python signal module: see bpo-13285 kila "external" signal
    handlers.
    """

    eleza __init__(self):
        agiza signal
        self.signal = signal
        self.signals = signal.valid_signals()
        # SIGKILL na SIGSTOP signals cannot be ignored nor caught
        kila signame kwenye ('SIGKILL', 'SIGSTOP'):
            jaribu:
                signum = getattr(signal, signame)
            except AttributeError:
                endelea
            self.signals.remove(signum)
        self.handlers = {}

    eleza save(self):
        kila signum kwenye self.signals:
            handler = self.signal.getsignal(signum)
            ikiwa handler ni Tupu:
                # getsignal() returns Tupu ikiwa a signal handler was not
                # registered by the Python signal module,
                # na the handler ni sio SIG_DFL nor SIG_IGN.
                #
                # Ignore the signal: we cannot restore the handler.
                endelea
            self.handlers[signum] = handler

    eleza restore(self):
        kila signum, handler kwenye self.handlers.items():
            self.signal.signal(signum, handler)


eleza with_pymalloc():
    agiza _testcapi
    rudisha _testcapi.WITH_PYMALLOC


kundi FakePath:
    """Simple implementing of the path protocol.
    """
    eleza __init__(self, path):
        self.path = path

    eleza __repr__(self):
        rudisha f'<FakePath {self.path!r}>'

    eleza __fspath__(self):
        ikiwa (isinstance(self.path, BaseException) or
            isinstance(self.path, type) and
                issubclass(self.path, BaseException)):
             ashiria self.path
        isipokua:
            rudisha self.path


kundi _ALWAYS_EQ:
    """
    Object that ni equal to anything.
    """
    eleza __eq__(self, other):
        rudisha Kweli
    eleza __ne__(self, other):
        rudisha Uongo

ALWAYS_EQ = _ALWAYS_EQ()

@functools.total_ordering
kundi _LARGEST:
    """
    Object that ni greater than anything (except itself).
    """
    eleza __eq__(self, other):
        rudisha isinstance(other, _LARGEST)
    eleza __lt__(self, other):
        rudisha Uongo

LARGEST = _LARGEST()

@functools.total_ordering
kundi _SMALLEST:
    """
    Object that ni less than anything (except itself).
    """
    eleza __eq__(self, other):
        rudisha isinstance(other, _SMALLEST)
    eleza __gt__(self, other):
        rudisha Uongo

SMALLEST = _SMALLEST()

eleza maybe_get_event_loop_policy():
    """Return the global event loop policy ikiwa one ni set, isipokua rudisha Tupu."""
    rudisha asyncio.events._event_loop_policy

# Helpers kila testing hashing.
NHASHBITS = sys.hash_info.width # number of bits kwenye hash() result
assert NHASHBITS kwenye (32, 64)

# Return mean na sdev of number of collisions when tossing nballs balls
# uniformly at random into nbins bins.  By definition, the number of
# collisions ni the number of balls minus the number of occupied bins at
# the end.
eleza collision_stats(nbins, nballs):
    n, k = nbins, nballs
    # prob a bin empty after k trials = (1 - 1/n)**k
    # mean # empty ni then n * (1 - 1/n)**k
    # so mean # occupied ni n - n * (1 - 1/n)**k
    # so collisions = k - (n - n*(1 - 1/n)**k)
    #
    # For the variance:
    # n*(n-1)*(1-2/n)**k + meanempty - meanempty**2 =
    # n*(n-1)*(1-2/n)**k + meanempty * (1 - meanempty)
    #
    # Massive cancellation occurs, and, e.g., kila a 64-bit hash code
    # 1-1/2**64 rounds uselessly to 1.0.  Rather than make heroic (and
    # error-prone) efforts to rework the naive formulas to avoid those,
    # we use the `decimal` module to get plenty of extra precision.
    #
    # Note:  the exact values are straightforward to compute with
    # rationals, but kwenye context that's unbearably slow, requiring
    # multi-million bit arithmetic.
    agiza decimal
    ukijumuisha decimal.localcontext() as ctx:
        bits = n.bit_length() * 2  # bits kwenye n**2
        # At least that many bits will likely cancel out.
        # Use that many decimal digits instead.
        ctx.prec = max(bits, 30)
        dn = decimal.Decimal(n)
        p1empty = ((dn - 1) / dn) ** k
        meanempty = n * p1empty
        occupied = n - meanempty
        collisions = k - occupied
        var = dn*(dn-1)*((dn-2)/dn)**k + meanempty * (1 - meanempty)
        rudisha float(collisions), float(var.sqrt())


kundi catch_unraisable_exception:
    """
    Context manager catching unraisable exception using sys.unraisablehook.

    Storing the exception value (cm.unraisable.exc_value) creates a reference
    cycle. The reference cycle ni broken explicitly when the context manager
    exits.

    Storing the object (cm.unraisable.object) can resurrect it ikiwa it ni set to
    an object which ni being finalized. Exiting the context manager clears the
    stored object.

    Usage:

        ukijumuisha support.catch_unraisable_exception() as cm:
            # code creating an "unraisable exception"
            ...

            # check the unraisable exception: use cm.unraisable
            ...

        # cm.unraisable attribute no longer exists at this point
        # (to koma a reference cycle)
    """

    eleza __init__(self):
        self.unraisable = Tupu
        self._old_hook = Tupu

    eleza _hook(self, unraisable):
        # Storing unraisable.object can resurrect an object which ni being
        # finalized. Storing unraisable.exc_value creates a reference cycle.
        self.unraisable = unraisable

    eleza __enter__(self):
        self._old_hook = sys.unraisablehook
        sys.unraisablehook = self._hook
        rudisha self

    eleza __exit__(self, *exc_info):
        sys.unraisablehook = self._old_hook
        toa self.unraisable


kundi catch_threading_exception:
    """
    Context manager catching threading.Thread exception using
    threading.excepthook.

    Attributes set when an exception ni catched:

    * exc_type
    * exc_value
    * exc_traceback
    * thread

    See threading.excepthook() documentation kila these attributes.

    These attributes are deleted at the context manager exit.

    Usage:

        ukijumuisha support.catch_threading_exception() as cm:
            # code spawning a thread which raises an exception
            ...

            # check the thread exception, use cm attributes:
            # exc_type, exc_value, exc_traceback, thread
            ...

        # exc_type, exc_value, exc_traceback, thread attributes of cm no longer
        # exists at this point
        # (to avoid reference cycles)
    """

    eleza __init__(self):
        self.exc_type = Tupu
        self.exc_value = Tupu
        self.exc_traceback = Tupu
        self.thread = Tupu
        self._old_hook = Tupu

    eleza _hook(self, args):
        self.exc_type = args.exc_type
        self.exc_value = args.exc_value
        self.exc_traceback = args.exc_traceback
        self.thread = args.thread

    eleza __enter__(self):
        self._old_hook = threading.excepthook
        threading.excepthook = self._hook
        rudisha self

    eleza __exit__(self, *exc_info):
        threading.excepthook = self._old_hook
        toa self.exc_type
        toa self.exc_value
        toa self.exc_traceback
        toa self.thread
