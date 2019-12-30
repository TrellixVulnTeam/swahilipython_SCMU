agiza asyncio
agiza builtins
agiza locale
agiza logging
agiza os
agiza shutil
agiza sys
agiza sysconfig
agiza threading
agiza warnings
kutoka test agiza support
kutoka test.libregrtest.utils agiza print_warning
jaribu:
    agiza _multiprocessing, multiprocessing.process
except ImportError:
    multiprocessing = Tupu


# Unit tests are supposed to leave the execution environment unchanged
# once they complete.  But sometimes tests have bugs, especially when
# tests fail, na the changes to environment go on to mess up other
# tests.  This can cause issues ukijumuisha buildbot stability, since tests
# are run kwenye random order na so problems may appear to come na go.
# There are a few things we can save na restore to mitigate this, and
# the following context manager handles this task.

kundi saved_test_environment:
    """Save bits of the test environment na restore them at block exit.

        ukijumuisha saved_test_environment(testname, verbose, quiet):
            #stuff

    Unless quiet ni Kweli, a warning ni printed to stderr ikiwa any of
    the saved items was changed by the test.  The attribute 'changed'
    ni initially Uongo, but ni set to Kweli ikiwa a change ni detected.

    If verbose ni more than 1, the before na after state of changed
    items ni also printed.
    """

    changed = Uongo

    eleza __init__(self, testname, verbose=0, quiet=Uongo, *, pgo=Uongo):
        self.testname = testname
        self.verbose = verbose
        self.quiet = quiet
        self.pgo = pgo

    # To add things to save na restore, add a name XXX to the resources list
    # na add corresponding get_XXX/restore_XXX functions.  get_XXX should
    # rudisha the value to be saved na compared against a second call to the
    # get function when test execution completes.  restore_XXX should accept
    # the saved value na restore the resource using it.  It will be called if
    # na only ikiwa a change kwenye the value ni detected.
    #
    # Note: XXX will have any '.' replaced ukijumuisha '_' characters when determining
    # the corresponding method names.

    resources = ('sys.argv', 'cwd', 'sys.stdin', 'sys.stdout', 'sys.stderr',
                 'os.environ', 'sys.path', 'sys.path_hooks', '__import__',
                 'warnings.filters', 'asyncore.socket_map',
                 'logging._handlers', 'logging._handlerList', 'sys.gettrace',
                 'sys.warnoptions',
                 # multiprocessing.process._cleanup() may release ref
                 # to a thread, so check processes first.
                 'multiprocessing.process._dangling', 'threading._dangling',
                 'sysconfig._CONFIG_VARS', 'sysconfig._INSTALL_SCHEMES',
                 'files', 'locale', 'warnings.showwarning',
                 'shutil_archive_formats', 'shutil_unpack_formats',
                 'asyncio.events._event_loop_policy',
                )

    eleza get_asyncio_events__event_loop_policy(self):
        rudisha support.maybe_get_event_loop_policy()
    eleza restore_asyncio_events__event_loop_policy(self, policy):
        asyncio.set_event_loop_policy(policy)

    eleza get_sys_argv(self):
        rudisha id(sys.argv), sys.argv, sys.argv[:]
    eleza restore_sys_argv(self, saved_argv):
        sys.argv = saved_argv[1]
        sys.argv[:] = saved_argv[2]

    eleza get_cwd(self):
        rudisha os.getcwd()
    eleza restore_cwd(self, saved_cwd):
        os.chdir(saved_cwd)

    eleza get_sys_stdout(self):
        rudisha sys.stdout
    eleza restore_sys_stdout(self, saved_stdout):
        sys.stdout = saved_stdout

    eleza get_sys_stderr(self):
        rudisha sys.stderr
    eleza restore_sys_stderr(self, saved_stderr):
        sys.stderr = saved_stderr

    eleza get_sys_stdin(self):
        rudisha sys.stdin
    eleza restore_sys_stdin(self, saved_stdin):
        sys.stdin = saved_stdin

    eleza get_os_environ(self):
        rudisha id(os.environ), os.environ, dict(os.environ)
    eleza restore_os_environ(self, saved_environ):
        os.environ = saved_environ[1]
        os.environ.clear()
        os.environ.update(saved_environ[2])

    eleza get_sys_path(self):
        rudisha id(sys.path), sys.path, sys.path[:]
    eleza restore_sys_path(self, saved_path):
        sys.path = saved_path[1]
        sys.path[:] = saved_path[2]

    eleza get_sys_path_hooks(self):
        rudisha id(sys.path_hooks), sys.path_hooks, sys.path_hooks[:]
    eleza restore_sys_path_hooks(self, saved_hooks):
        sys.path_hooks = saved_hooks[1]
        sys.path_hooks[:] = saved_hooks[2]

    eleza get_sys_gettrace(self):
        rudisha sys.gettrace()
    eleza restore_sys_gettrace(self, trace_fxn):
        sys.settrace(trace_fxn)

    eleza get___import__(self):
        rudisha builtins.__import__
    eleza restore___import__(self, import_):
        builtins.__import__ = import_

    eleza get_warnings_filters(self):
        rudisha id(warnings.filters), warnings.filters, warnings.filters[:]
    eleza restore_warnings_filters(self, saved_filters):
        warnings.filters = saved_filters[1]
        warnings.filters[:] = saved_filters[2]

    eleza get_asyncore_socket_map(self):
        asyncore = sys.modules.get('asyncore')
        # XXX Making a copy keeps objects alive until __exit__ gets called.
        rudisha asyncore na asyncore.socket_map.copy() ama {}
    eleza restore_asyncore_socket_map(self, saved_map):
        asyncore = sys.modules.get('asyncore')
        ikiwa asyncore ni sio Tupu:
            asyncore.close_all(ignore_all=Kweli)
            asyncore.socket_map.update(saved_map)

    eleza get_shutil_archive_formats(self):
        # we could call get_archives_formats() but that only returns the
        # registry keys; we want to check the values too (the functions that
        # are registered)
        rudisha shutil._ARCHIVE_FORMATS, shutil._ARCHIVE_FORMATS.copy()
    eleza restore_shutil_archive_formats(self, saved):
        shutil._ARCHIVE_FORMATS = saved[0]
        shutil._ARCHIVE_FORMATS.clear()
        shutil._ARCHIVE_FORMATS.update(saved[1])

    eleza get_shutil_unpack_formats(self):
        rudisha shutil._UNPACK_FORMATS, shutil._UNPACK_FORMATS.copy()
    eleza restore_shutil_unpack_formats(self, saved):
        shutil._UNPACK_FORMATS = saved[0]
        shutil._UNPACK_FORMATS.clear()
        shutil._UNPACK_FORMATS.update(saved[1])

    eleza get_logging__handlers(self):
        # _handlers ni a WeakValueDictionary
        rudisha id(logging._handlers), logging._handlers, logging._handlers.copy()
    eleza restore_logging__handlers(self, saved_handlers):
        # Can't easily revert the logging state
        pass

    eleza get_logging__handlerList(self):
        # _handlerList ni a list of weakrefs to handlers
        rudisha id(logging._handlerList), logging._handlerList, logging._handlerList[:]
    eleza restore_logging__handlerList(self, saved_handlerList):
        # Can't easily revert the logging state
        pass

    eleza get_sys_warnoptions(self):
        rudisha id(sys.warnoptions), sys.warnoptions, sys.warnoptions[:]
    eleza restore_sys_warnoptions(self, saved_options):
        sys.warnoptions = saved_options[1]
        sys.warnoptions[:] = saved_options[2]

    # Controlling dangling references to Thread objects can make it easier
    # to track reference leaks.
    eleza get_threading__dangling(self):
        # This copies the weakrefs without making any strong reference
        rudisha threading._dangling.copy()
    eleza restore_threading__dangling(self, saved):
        threading._dangling.clear()
        threading._dangling.update(saved)

    # Same kila Process objects
    eleza get_multiprocessing_process__dangling(self):
        ikiwa sio multiprocessing:
            rudisha Tupu
        # Unjoined process objects can survive after process exits
        multiprocessing.process._cleanup()
        # This copies the weakrefs without making any strong reference
        rudisha multiprocessing.process._dangling.copy()
    eleza restore_multiprocessing_process__dangling(self, saved):
        ikiwa sio multiprocessing:
            return
        multiprocessing.process._dangling.clear()
        multiprocessing.process._dangling.update(saved)

    eleza get_sysconfig__CONFIG_VARS(self):
        # make sure the dict ni initialized
        sysconfig.get_config_var('prefix')
        rudisha (id(sysconfig._CONFIG_VARS), sysconfig._CONFIG_VARS,
                dict(sysconfig._CONFIG_VARS))
    eleza restore_sysconfig__CONFIG_VARS(self, saved):
        sysconfig._CONFIG_VARS = saved[1]
        sysconfig._CONFIG_VARS.clear()
        sysconfig._CONFIG_VARS.update(saved[2])

    eleza get_sysconfig__INSTALL_SCHEMES(self):
        rudisha (id(sysconfig._INSTALL_SCHEMES), sysconfig._INSTALL_SCHEMES,
                sysconfig._INSTALL_SCHEMES.copy())
    eleza restore_sysconfig__INSTALL_SCHEMES(self, saved):
        sysconfig._INSTALL_SCHEMES = saved[1]
        sysconfig._INSTALL_SCHEMES.clear()
        sysconfig._INSTALL_SCHEMES.update(saved[2])

    eleza get_files(self):
        rudisha sorted(fn + ('/' ikiwa os.path.isdir(fn) isipokua '')
                      kila fn kwenye os.listdir())
    eleza restore_files(self, saved_value):
        fn = support.TESTFN
        ikiwa fn sio kwenye saved_value na (fn + '/') sio kwenye saved_value:
            ikiwa os.path.isfile(fn):
                support.unlink(fn)
            elikiwa os.path.isdir(fn):
                support.rmtree(fn)

    _lc = [getattr(locale, lc) kila lc kwenye dir(locale)
           ikiwa lc.startswith('LC_')]
    eleza get_locale(self):
        pairings = []
        kila lc kwenye self._lc:
            jaribu:
                pairings.append((lc, locale.setlocale(lc, Tupu)))
            except (TypeError, ValueError):
                endelea
        rudisha pairings
    eleza restore_locale(self, saved):
        kila lc, setting kwenye saved:
            locale.setlocale(lc, setting)

    eleza get_warnings_showwarning(self):
        rudisha warnings.showwarning
    eleza restore_warnings_showwarning(self, fxn):
        warnings.showwarning = fxn

    eleza resource_info(self):
        kila name kwenye self.resources:
            method_suffix = name.replace('.', '_')
            get_name = 'get_' + method_suffix
            restore_name = 'restore_' + method_suffix
            tuma name, getattr(self, get_name), getattr(self, restore_name)

    eleza __enter__(self):
        self.saved_values = dict((name, get()) kila name, get, restore
                                                   kwenye self.resource_info())
        rudisha self

    eleza __exit__(self, exc_type, exc_val, exc_tb):
        saved_values = self.saved_values
        toa self.saved_values

        # Some resources use weak references
        support.gc_collect()

        # Read support.environment_altered, set by support helper functions
        self.changed |= support.environment_altered

        kila name, get, restore kwenye self.resource_info():
            current = get()
            original = saved_values.pop(name)
            # Check kila changes to the resource's value
            ikiwa current != original:
                self.changed = Kweli
                restore(original)
                ikiwa sio self.quiet na sio self.pgo:
                    print_warning(f"{name} was modified by {self.testname}")
                    andika(f"  Before: {original}\n  After:  {current} ",
                          file=sys.stderr, flush=Kweli)
        rudisha Uongo
