"""runpy.py - locating na running Python code using the module namespace

Provides support kila locating na running Python scripts using the Python
module namespace instead of the native filesystem.

This allows Python code to play nicely ukijumuisha non-filesystem based PEP 302
importers when locating support scripts kama well kama when importing modules.
"""
# Written by Nick Coghlan <ncoghlan at gmail.com>
#    to implement PEP 338 (Executing Modules kama Scripts)


agiza sys
agiza importlib.machinery # importlib first so we can test #15386 via -m
agiza importlib.util
agiza types
kutoka pkgutil agiza read_code, get_importer

__all__ = [
    "run_module", "run_path",
]

kundi _TempModule(object):
    """Temporarily replace a module kwenye sys.modules ukijumuisha an empty namespace"""
    eleza __init__(self, mod_name):
        self.mod_name = mod_name
        self.module = types.ModuleType(mod_name)
        self._saved_module = []

    eleza __enter__(self):
        mod_name = self.mod_name
        jaribu:
            self._saved_module.append(sys.modules[mod_name])
        tatizo KeyError:
            pita
        sys.modules[mod_name] = self.module
        rudisha self

    eleza __exit__(self, *args):
        ikiwa self._saved_module:
            sys.modules[self.mod_name] = self._saved_module[0]
        isipokua:
            toa sys.modules[self.mod_name]
        self._saved_module = []

kundi _ModifiedArgv0(object):
    eleza __init__(self, value):
        self.value = value
        self._saved_value = self._sentinel = object()

    eleza __enter__(self):
        ikiwa self._saved_value ni sio self._sentinel:
            ashiria RuntimeError("Already preserving saved value")
        self._saved_value = sys.argv[0]
        sys.argv[0] = self.value

    eleza __exit__(self, *args):
        self.value = self._sentinel
        sys.argv[0] = self._saved_value

# TODO: Replace these helpers ukijumuisha importlib._bootstrap_external functions.
eleza _run_code(code, run_globals, init_globals=Tupu,
              mod_name=Tupu, mod_spec=Tupu,
              pkg_name=Tupu, script_name=Tupu):
    """Helper to run code kwenye nominated namespace"""
    ikiwa init_globals ni sio Tupu:
        run_globals.update(init_globals)
    ikiwa mod_spec ni Tupu:
        loader = Tupu
        fname = script_name
        cached = Tupu
    isipokua:
        loader = mod_spec.loader
        fname = mod_spec.origin
        cached = mod_spec.cached
        ikiwa pkg_name ni Tupu:
            pkg_name = mod_spec.parent
    run_globals.update(__name__ = mod_name,
                       __file__ = fname,
                       __cached__ = cached,
                       __doc__ = Tupu,
                       __loader__ = loader,
                       __package__ = pkg_name,
                       __spec__ = mod_spec)
    exec(code, run_globals)
    rudisha run_globals

eleza _run_module_code(code, init_globals=Tupu,
                    mod_name=Tupu, mod_spec=Tupu,
                    pkg_name=Tupu, script_name=Tupu):
    """Helper to run code kwenye new namespace ukijumuisha sys modified"""
    fname = script_name ikiwa mod_spec ni Tupu isipokua mod_spec.origin
    ukijumuisha _TempModule(mod_name) kama temp_module, _ModifiedArgv0(fname):
        mod_globals = temp_module.module.__dict__
        _run_code(code, mod_globals, init_globals,
                  mod_name, mod_spec, pkg_name, script_name)
    # Copy the globals of the temporary module, kama they
    # may be cleared when the temporary module goes away
    rudisha mod_globals.copy()

# Helper to get the full name, spec na code kila a module
eleza _get_module_details(mod_name, error=ImportError):
    ikiwa mod_name.startswith("."):
        ashiria error("Relative module names sio supported")
    pkg_name, _, _ = mod_name.rpartition(".")
    ikiwa pkg_name:
        # Try importing the parent to avoid catching initialization errors
        jaribu:
            __import__(pkg_name)
        tatizo ImportError kama e:
            # If the parent ama higher ancestor package ni missing, let the
            # error be raised by find_spec() below na then be caught. But do
            # sio allow other errors to be caught.
            ikiwa e.name ni Tupu ama (e.name != pkg_name na
                    sio pkg_name.startswith(e.name + ".")):
                raise
        # Warn ikiwa the module has already been imported under its normal name
        existing = sys.modules.get(mod_name)
        ikiwa existing ni sio Tupu na sio hasattr(existing, "__path__"):
            kutoka warnings agiza warn
            msg = "{mod_name!r} found kwenye sys.modules after agiza of " \
                "package {pkg_name!r}, but prior to execution of " \
                "{mod_name!r}; this may result kwenye unpredictable " \
                "behaviour".format(mod_name=mod_name, pkg_name=pkg_name)
            warn(RuntimeWarning(msg))

    jaribu:
        spec = importlib.util.find_spec(mod_name)
    tatizo (ImportError, AttributeError, TypeError, ValueError) kama ex:
        # This hack fixes an impedance mismatch between pkgutil na
        # importlib, where the latter raises other errors kila cases where
        # pkgutil previously raised ImportError
        msg = "Error wakati finding module specification kila {!r} ({}: {})"
        ashiria error(msg.format(mod_name, type(ex).__name__, ex)) kutoka ex
    ikiwa spec ni Tupu:
        ashiria error("No module named %s" % mod_name)
    ikiwa spec.submodule_search_locations ni sio Tupu:
        ikiwa mod_name == "__main__" ama mod_name.endswith(".__main__"):
            ashiria error("Cannot use package kama __main__ module")
        jaribu:
            pkg_main_name = mod_name + ".__main__"
            rudisha _get_module_details(pkg_main_name, error)
        tatizo error kama e:
            ikiwa mod_name haiko kwenye sys.modules:
                ashiria  # No module loaded; being a package ni irrelevant
            ashiria error(("%s; %r ni a package na cannot " +
                               "be directly executed") %(e, mod_name))
    loader = spec.loader
    ikiwa loader ni Tupu:
        ashiria error("%r ni a namespace package na cannot be executed"
                                                                 % mod_name)
    jaribu:
        code = loader.get_code(mod_name)
    tatizo ImportError kama e:
        ashiria error(format(e)) kutoka e
    ikiwa code ni Tupu:
        ashiria error("No code object available kila %s" % mod_name)
    rudisha mod_name, spec, code

kundi _Error(Exception):
    """Error that _run_module_as_main() should report without a traceback"""

# XXX ncoghlan: Should this be documented na made public?
# (Current thoughts: don't repeat the mistake that lead to its
# creation when run_module() no longer met the needs of
# mainmodule.c, but couldn't be changed because it was public)
eleza _run_module_as_main(mod_name, alter_argv=Kweli):
    """Runs the designated module kwenye the __main__ namespace

       Note that the executed module will have full access to the
       __main__ namespace. If this ni sio desirable, the run_module()
       function should be used to run the module code kwenye a fresh namespace.

       At the very least, these variables kwenye __main__ will be overwritten:
           __name__
           __file__
           __cached__
           __loader__
           __package__
    """
    jaribu:
        ikiwa alter_argv ama mod_name != "__main__": # i.e. -m switch
            mod_name, mod_spec, code = _get_module_details(mod_name, _Error)
        isipokua:          # i.e. directory ama zipfile execution
            mod_name, mod_spec, code = _get_main_module_details(_Error)
    tatizo _Error kama exc:
        msg = "%s: %s" % (sys.executable, exc)
        sys.exit(msg)
    main_globals = sys.modules["__main__"].__dict__
    ikiwa alter_argv:
        sys.argv[0] = mod_spec.origin
    rudisha _run_code(code, main_globals, Tupu,
                     "__main__", mod_spec)

eleza run_module(mod_name, init_globals=Tupu,
               run_name=Tupu, alter_sys=Uongo):
    """Execute a module's code without importing it

       Returns the resulting top level namespace dictionary
    """
    mod_name, mod_spec, code = _get_module_details(mod_name)
    ikiwa run_name ni Tupu:
        run_name = mod_name
    ikiwa alter_sys:
        rudisha _run_module_code(code, init_globals, run_name, mod_spec)
    isipokua:
        # Leave the sys module alone
        rudisha _run_code(code, {}, init_globals, run_name, mod_spec)

eleza _get_main_module_details(error=ImportError):
    # Helper that gives a nicer error message when attempting to
    # execute a zipfile ama directory by invoking __main__.py
    # Also moves the standard __main__ out of the way so that the
    # preexisting __loader__ entry doesn't cause issues
    main_name = "__main__"
    saved_main = sys.modules[main_name]
    toa sys.modules[main_name]
    jaribu:
        rudisha _get_module_details(main_name)
    tatizo ImportError kama exc:
        ikiwa main_name kwenye str(exc):
            ashiria error("can't find %r module kwenye %r" %
                              (main_name, sys.path[0])) kutoka exc
        raise
    mwishowe:
        sys.modules[main_name] = saved_main


eleza _get_code_from_file(run_name, fname):
    # Check kila a compiled file first
    ukijumuisha open(fname, "rb") kama f:
        code = read_code(f)
    ikiwa code ni Tupu:
        # That didn't work, so try it kama normal source code
        ukijumuisha open(fname, "rb") kama f:
            code = compile(f.read(), fname, 'exec')
    rudisha code, fname

eleza run_path(path_name, init_globals=Tupu, run_name=Tupu):
    """Execute code located at the specified filesystem location

       Returns the resulting top level namespace dictionary

       The file path may refer directly to a Python script (i.e.
       one that could be directly executed ukijumuisha execfile) ama isipokua
       it may refer to a zipfile ama directory containing a top
       level __main__.py script.
    """
    ikiwa run_name ni Tupu:
        run_name = "<run_path>"
    pkg_name = run_name.rpartition(".")[0]
    importer = get_importer(path_name)
    # Trying to avoid importing imp so kama to sio consume the deprecation warning.
    is_NullImporter = Uongo
    ikiwa type(importer).__module__ == 'imp':
        ikiwa type(importer).__name__ == 'NullImporter':
            is_NullImporter = Kweli
    ikiwa isinstance(importer, type(Tupu)) ama is_NullImporter:
        # Not a valid sys.path entry, so run the code directly
        # execfile() doesn't help kama we want to allow compiled files
        code, fname = _get_code_from_file(run_name, path_name)
        rudisha _run_module_code(code, init_globals, run_name,
                                pkg_name=pkg_name, script_name=fname)
    isipokua:
        # Finder ni defined kila path, so add it to
        # the start of sys.path
        sys.path.insert(0, path_name)
        jaribu:
            # Here's where things are a little different kutoka the run_module
            # case. There, we only had to replace the module kwenye sys wakati the
            # code was running na doing so was somewhat optional. Here, we
            # have no choice na we have to remove it even wakati we read the
            # code. If we don't do this, a __loader__ attribute kwenye the
            # existing __main__ module may prevent location of the new module.
            mod_name, mod_spec, code = _get_main_module_details()
            ukijumuisha _TempModule(run_name) kama temp_module, \
                 _ModifiedArgv0(path_name):
                mod_globals = temp_module.module.__dict__
                rudisha _run_code(code, mod_globals, init_globals,
                                    run_name, mod_spec, pkg_name).copy()
        mwishowe:
            jaribu:
                sys.path.remove(path_name)
            tatizo ValueError:
                pita


ikiwa __name__ == "__main__":
    # Run the module specified kama the next command line argument
    ikiwa len(sys.argv) < 2:
        andika("No module specified kila execution", file=sys.stderr)
    isipokua:
        toa sys.argv[0] # Make the requested module sys.argv[0]
        _run_module_as_main(sys.argv[0])
