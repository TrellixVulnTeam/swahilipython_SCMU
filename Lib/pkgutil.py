"""Utilities to support packages."""

kutoka collections agiza namedtuple
kutoka functools agiza singledispatch kama simplegeneric
agiza importlib
agiza importlib.util
agiza importlib.machinery
agiza os
agiza os.path
agiza sys
kutoka types agiza ModuleType
agiza warnings

__all__ = [
    'get_importer', 'iter_importers', 'get_loader', 'find_loader',
    'walk_packages', 'iter_modules', 'get_data',
    'ImpImporter', 'ImpLoader', 'read_code', 'extend_path',
    'ModuleInfo',
]


ModuleInfo = namedtuple('ModuleInfo', 'module_finder name ispkg')
ModuleInfo.__doc__ = 'A namedtuple ukijumuisha minimal info about a module.'


eleza _get_spec(finder, name):
    """Return the finder-specific module spec."""
    # Works ukijumuisha legacy finders.
    jaribu:
        find_spec = finder.find_spec
    tatizo AttributeError:
        loader = finder.find_module(name)
        ikiwa loader ni Tupu:
            rudisha Tupu
        rudisha importlib.util.spec_from_loader(name, loader)
    isipokua:
        rudisha find_spec(name)


eleza read_code(stream):
    # This helper ni needed kwenye order kila the PEP 302 emulation to
    # correctly handle compiled files
    agiza marshal

    magic = stream.read(4)
    ikiwa magic != importlib.util.MAGIC_NUMBER:
        rudisha Tupu

    stream.read(12) # Skip rest of the header
    rudisha marshal.load(stream)


eleza walk_packages(path=Tupu, prefix='', onerror=Tupu):
    """Yields ModuleInfo kila all modules recursively
    on path, or, ikiwa path ni Tupu, all accessible modules.

    'path' should be either Tupu ama a list of paths to look for
    modules in.

    'prefix' ni a string to output on the front of every module name
    on output.

    Note that this function must agiza all *packages* (NOT all
    modules!) on the given path, kwenye order to access the __path__
    attribute to find submodules.

    'onerror' ni a function which gets called ukijumuisha one argument (the
    name of the package which was being imported) ikiwa any exception
    occurs wakati trying to agiza a package.  If no onerror function is
    supplied, ImportErrors are caught na ignored, wakati all other
    exceptions are propagated, terminating the search.

    Examples:

    # list all modules python can access
    walk_packages()

    # list all submodules of ctypes
    walk_packages(ctypes.__path__, ctypes.__name__+'.')
    """

    eleza seen(p, m={}):
        ikiwa p kwenye m:
            rudisha Kweli
        m[p] = Kweli

    kila info kwenye iter_modules(path, prefix):
        tuma info

        ikiwa info.ispkg:
            jaribu:
                __import__(info.name)
            tatizo ImportError:
                ikiwa onerror ni sio Tupu:
                    onerror(info.name)
            tatizo Exception:
                ikiwa onerror ni sio Tupu:
                    onerror(info.name)
                isipokua:
                    raise
            isipokua:
                path = getattr(sys.modules[info.name], '__path__', Tupu) ama []

                # don't traverse path items we've seen before
                path = [p kila p kwenye path ikiwa sio seen(p)]

                tuma kutoka walk_packages(path, info.name+'.', onerror)


eleza iter_modules(path=Tupu, prefix=''):
    """Yields ModuleInfo kila all submodules on path,
    or, ikiwa path ni Tupu, all top-level modules on sys.path.

    'path' should be either Tupu ama a list of paths to look for
    modules in.

    'prefix' ni a string to output on the front of every module name
    on output.
    """
    ikiwa path ni Tupu:
        importers = iter_importers()
    lasivyo isinstance(path, str):
        ashiria ValueError("path must be Tupu ama list of paths to look kila "
                        "modules in")
    isipokua:
        importers = map(get_importer, path)

    tumaed = {}
    kila i kwenye importers:
        kila name, ispkg kwenye iter_importer_modules(i, prefix):
            ikiwa name haiko kwenye tumaed:
                tumaed[name] = 1
                tuma ModuleInfo(i, name, ispkg)


@simplegeneric
eleza iter_importer_modules(importer, prefix=''):
    ikiwa sio hasattr(importer, 'iter_modules'):
        rudisha []
    rudisha importer.iter_modules(prefix)


# Implement a file walker kila the normal importlib path hook
eleza _iter_file_finder_modules(importer, prefix=''):
    ikiwa importer.path ni Tupu ama sio os.path.isdir(importer.path):
        rudisha

    tumaed = {}
    agiza inspect
    jaribu:
        filenames = os.listdir(importer.path)
    tatizo OSError:
        # ignore unreadable directories like agiza does
        filenames = []
    filenames.sort()  # handle packages before same-named modules

    kila fn kwenye filenames:
        modname = inspect.getmodulename(fn)
        ikiwa modname=='__init__' ama modname kwenye tumaed:
            endelea

        path = os.path.join(importer.path, fn)
        ispkg = Uongo

        ikiwa sio modname na os.path.isdir(path) na '.' haiko kwenye fn:
            modname = fn
            jaribu:
                dircontents = os.listdir(path)
            tatizo OSError:
                # ignore unreadable directories like agiza does
                dircontents = []
            kila fn kwenye dircontents:
                subname = inspect.getmodulename(fn)
                ikiwa subname=='__init__':
                    ispkg = Kweli
                    koma
            isipokua:
                endelea    # sio a package

        ikiwa modname na '.' haiko kwenye modname:
            tumaed[modname] = 1
            tuma prefix + modname, ispkg

iter_importer_modules.register(
    importlib.machinery.FileFinder, _iter_file_finder_modules)


eleza _import_imp():
    global imp
    ukijumuisha warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        imp = importlib.import_module('imp')

kundi ImpImporter:
    """PEP 302 Finder that wraps Python's "classic" agiza algorithm

    ImpImporter(dirname) produces a PEP 302 finder that searches that
    directory.  ImpImporter(Tupu) produces a PEP 302 finder that searches
    the current sys.path, plus any modules that are frozen ama built-in.

    Note that ImpImporter does sio currently support being used by placement
    on sys.meta_path.
    """

    eleza __init__(self, path=Tupu):
        global imp
        warnings.warn("This emulation ni deprecated, use 'importlib' instead",
             DeprecationWarning)
        _import_imp()
        self.path = path

    eleza find_module(self, fullname, path=Tupu):
        # Note: we ignore 'path' argument since it ni only used via meta_path
        subname = fullname.split(".")[-1]
        ikiwa subname != fullname na self.path ni Tupu:
            rudisha Tupu
        ikiwa self.path ni Tupu:
            path = Tupu
        isipokua:
            path = [os.path.realpath(self.path)]
        jaribu:
            file, filename, etc = imp.find_module(subname, path)
        tatizo ImportError:
            rudisha Tupu
        rudisha ImpLoader(fullname, file, filename, etc)

    eleza iter_modules(self, prefix=''):
        ikiwa self.path ni Tupu ama sio os.path.isdir(self.path):
            rudisha

        tumaed = {}
        agiza inspect
        jaribu:
            filenames = os.listdir(self.path)
        tatizo OSError:
            # ignore unreadable directories like agiza does
            filenames = []
        filenames.sort()  # handle packages before same-named modules

        kila fn kwenye filenames:
            modname = inspect.getmodulename(fn)
            ikiwa modname=='__init__' ama modname kwenye tumaed:
                endelea

            path = os.path.join(self.path, fn)
            ispkg = Uongo

            ikiwa sio modname na os.path.isdir(path) na '.' haiko kwenye fn:
                modname = fn
                jaribu:
                    dircontents = os.listdir(path)
                tatizo OSError:
                    # ignore unreadable directories like agiza does
                    dircontents = []
                kila fn kwenye dircontents:
                    subname = inspect.getmodulename(fn)
                    ikiwa subname=='__init__':
                        ispkg = Kweli
                        koma
                isipokua:
                    endelea    # sio a package

            ikiwa modname na '.' haiko kwenye modname:
                tumaed[modname] = 1
                tuma prefix + modname, ispkg


kundi ImpLoader:
    """PEP 302 Loader that wraps Python's "classic" agiza algorithm
    """
    code = source = Tupu

    eleza __init__(self, fullname, file, filename, etc):
        warnings.warn("This emulation ni deprecated, use 'importlib' instead",
                      DeprecationWarning)
        _import_imp()
        self.file = file
        self.filename = filename
        self.fullname = fullname
        self.etc = etc

    eleza load_module(self, fullname):
        self._reopen()
        jaribu:
            mod = imp.load_module(fullname, self.file, self.filename, self.etc)
        mwishowe:
            ikiwa self.file:
                self.file.close()
        # Note: we don't set __loader__ because we want the module to look
        # normal; i.e. this ni just a wrapper kila standard agiza machinery
        rudisha mod

    eleza get_data(self, pathname):
        ukijumuisha open(pathname, "rb") kama file:
            rudisha file.read()

    eleza _reopen(self):
        ikiwa self.file na self.file.closed:
            mod_type = self.etc[2]
            ikiwa mod_type==imp.PY_SOURCE:
                self.file = open(self.filename, 'r')
            lasivyo mod_type kwenye (imp.PY_COMPILED, imp.C_EXTENSION):
                self.file = open(self.filename, 'rb')

    eleza _fix_name(self, fullname):
        ikiwa fullname ni Tupu:
            fullname = self.fullname
        lasivyo fullname != self.fullname:
            ashiria ImportError("Loader kila module %s cansio handle "
                              "module %s" % (self.fullname, fullname))
        rudisha fullname

    eleza is_package(self, fullname):
        fullname = self._fix_name(fullname)
        rudisha self.etc[2]==imp.PKG_DIRECTORY

    eleza get_code(self, fullname=Tupu):
        fullname = self._fix_name(fullname)
        ikiwa self.code ni Tupu:
            mod_type = self.etc[2]
            ikiwa mod_type==imp.PY_SOURCE:
                source = self.get_source(fullname)
                self.code = compile(source, self.filename, 'exec')
            lasivyo mod_type==imp.PY_COMPILED:
                self._reopen()
                jaribu:
                    self.code = read_code(self.file)
                mwishowe:
                    self.file.close()
            lasivyo mod_type==imp.PKG_DIRECTORY:
                self.code = self._get_delegate().get_code()
        rudisha self.code

    eleza get_source(self, fullname=Tupu):
        fullname = self._fix_name(fullname)
        ikiwa self.source ni Tupu:
            mod_type = self.etc[2]
            ikiwa mod_type==imp.PY_SOURCE:
                self._reopen()
                jaribu:
                    self.source = self.file.read()
                mwishowe:
                    self.file.close()
            lasivyo mod_type==imp.PY_COMPILED:
                ikiwa os.path.exists(self.filename[:-1]):
                    ukijumuisha open(self.filename[:-1], 'r') kama f:
                        self.source = f.read()
            lasivyo mod_type==imp.PKG_DIRECTORY:
                self.source = self._get_delegate().get_source()
        rudisha self.source

    eleza _get_delegate(self):
        finder = ImpImporter(self.filename)
        spec = _get_spec(finder, '__init__')
        rudisha spec.loader

    eleza get_filename(self, fullname=Tupu):
        fullname = self._fix_name(fullname)
        mod_type = self.etc[2]
        ikiwa mod_type==imp.PKG_DIRECTORY:
            rudisha self._get_delegate().get_filename()
        lasivyo mod_type kwenye (imp.PY_SOURCE, imp.PY_COMPILED, imp.C_EXTENSION):
            rudisha self.filename
        rudisha Tupu


jaribu:
    agiza zipimport
    kutoka zipagiza agiza zipimporter

    eleza iter_zipimport_modules(importer, prefix=''):
        dirlist = sorted(zipimport._zip_directory_cache[importer.archive])
        _prefix = importer.prefix
        plen = len(_prefix)
        tumaed = {}
        agiza inspect
        kila fn kwenye dirlist:
            ikiwa sio fn.startswith(_prefix):
                endelea

            fn = fn[plen:].split(os.sep)

            ikiwa len(fn)==2 na fn[1].startswith('__init__.py'):
                ikiwa fn[0] haiko kwenye tumaed:
                    tumaed[fn[0]] = 1
                    tuma prefix + fn[0], Kweli

            ikiwa len(fn)!=1:
                endelea

            modname = inspect.getmodulename(fn[0])
            ikiwa modname=='__init__':
                endelea

            ikiwa modname na '.' haiko kwenye modname na modname haiko kwenye tumaed:
                tumaed[modname] = 1
                tuma prefix + modname, Uongo

    iter_importer_modules.register(zipimporter, iter_zipimport_modules)

tatizo ImportError:
    pita


eleza get_importer(path_item):
    """Retrieve a finder kila the given path item

    The returned finder ni cached kwenye sys.path_importer_cache
    ikiwa it was newly created by a path hook.

    The cache (or part of it) can be cleared manually ikiwa a
    rescan of sys.path_hooks ni necessary.
    """
    jaribu:
        importer = sys.path_importer_cache[path_item]
    tatizo KeyError:
        kila path_hook kwenye sys.path_hooks:
            jaribu:
                importer = path_hook(path_item)
                sys.path_importer_cache.setdefault(path_item, importer)
                koma
            tatizo ImportError:
                pita
        isipokua:
            importer = Tupu
    rudisha importer


eleza iter_importers(fullname=""):
    """Yield finders kila the given module name

    If fullname contains a '.', the finders will be kila the package
    containing fullname, otherwise they will be all registered top level
    finders (i.e. those on both sys.meta_path na sys.path_hooks).

    If the named module ni kwenye a package, that package ni imported kama a side
    effect of invoking this function.

    If no module name ni specified, all top level finders are produced.
    """
    ikiwa fullname.startswith('.'):
        msg = "Relative module name {!r} sio supported".format(fullname)
        ashiria ImportError(msg)
    ikiwa '.' kwenye fullname:
        # Get the containing package's __path__
        pkg_name = fullname.rpartition(".")[0]
        pkg = importlib.import_module(pkg_name)
        path = getattr(pkg, '__path__', Tupu)
        ikiwa path ni Tupu:
            rudisha
    isipokua:
        tuma kutoka sys.meta_path
        path = sys.path
    kila item kwenye path:
        tuma get_importer(item)


eleza get_loader(module_or_name):
    """Get a "loader" object kila module_or_name

    Returns Tupu ikiwa the module cansio be found ama imported.
    If the named module ni sio already imported, its containing package
    (ikiwa any) ni imported, kwenye order to establish the package __path__.
    """
    ikiwa module_or_name kwenye sys.modules:
        module_or_name = sys.modules[module_or_name]
        ikiwa module_or_name ni Tupu:
            rudisha Tupu
    ikiwa isinstance(module_or_name, ModuleType):
        module = module_or_name
        loader = getattr(module, '__loader__', Tupu)
        ikiwa loader ni sio Tupu:
            rudisha loader
        ikiwa getattr(module, '__spec__', Tupu) ni Tupu:
            rudisha Tupu
        fullname = module.__name__
    isipokua:
        fullname = module_or_name
    rudisha find_loader(fullname)


eleza find_loader(fullname):
    """Find a "loader" object kila fullname

    This ni a backwards compatibility wrapper around
    importlib.util.find_spec that converts most failures to ImportError
    na only returns the loader rather than the full spec
    """
    ikiwa fullname.startswith('.'):
        msg = "Relative module name {!r} sio supported".format(fullname)
        ashiria ImportError(msg)
    jaribu:
        spec = importlib.util.find_spec(fullname)
    tatizo (ImportError, AttributeError, TypeError, ValueError) kama ex:
        # This hack fixes an impedance mismatch between pkgutil na
        # importlib, where the latter raises other errors kila cases where
        # pkgutil previously raised ImportError
        msg = "Error wakati finding loader kila {!r} ({}: {})"
        ashiria ImportError(msg.format(fullname, type(ex), ex)) kutoka ex
    rudisha spec.loader ikiwa spec ni sio Tupu isipokua Tupu


eleza extend_path(path, name):
    """Extend a package's path.

    Intended use ni to place the following code kwenye a package's __init__.py:

        kutoka pkgutil agiza extend_path
        __path__ = extend_path(__path__, __name__)

    This will add to the package's __path__ all subdirectories of
    directories on sys.path named after the package.  This ni useful
    ikiwa one wants to distribute different parts of a single logical
    package kama multiple directories.

    It also looks kila *.pkg files beginning where * matches the name
    argument.  This feature ni similar to *.pth files (see site.py),
    tatizo that it doesn't special-case lines starting ukijumuisha 'import'.
    A *.pkg file ni trusted at face value: apart kutoka checking for
    duplicates, all entries found kwenye a *.pkg file are added to the
    path, regardless of whether they are exist the filesystem.  (This
    ni a feature.)

    If the input path ni sio a list (as ni the case kila frozen
    packages) it ni returned unchanged.  The input path ni sio
    modified; an extended copy ni returned.  Items are only appended
    to the copy at the end.

    It ni assumed that sys.path ni a sequence.  Items of sys.path that
    are sio (unicode ama 8-bit) strings referring to existing
    directories are ignored.  Unicode items of sys.path that cause
    errors when used kama filenames may cause this function to ashiria an
    exception (in line ukijumuisha os.path.isdir() behavior).
    """

    ikiwa sio isinstance(path, list):
        # This could happen e.g. when this ni called kutoka inside a
        # frozen package.  Return the path unchanged kwenye that case.
        rudisha path

    sname_pkg = name + ".pkg"

    path = path[:] # Start ukijumuisha a copy of the existing path

    parent_package, _, final_name = name.rpartition('.')
    ikiwa parent_package:
        jaribu:
            search_path = sys.modules[parent_package].__path__
        tatizo (KeyError, AttributeError):
            # We can't do anything: find_loader() returns Tupu when
            # pitaed a dotted name.
            rudisha path
    isipokua:
        search_path = sys.path

    kila dir kwenye search_path:
        ikiwa sio isinstance(dir, str):
            endelea

        finder = get_importer(dir)
        ikiwa finder ni sio Tupu:
            portions = []
            ikiwa hasattr(finder, 'find_spec'):
                spec = finder.find_spec(final_name)
                ikiwa spec ni sio Tupu:
                    portions = spec.submodule_search_locations ama []
            # Is this finder PEP 420 compliant?
            lasivyo hasattr(finder, 'find_loader'):
                _, portions = finder.find_loader(final_name)

            kila portion kwenye portions:
                # XXX This may still add duplicate entries to path on
                # case-insensitive filesystems
                ikiwa portion haiko kwenye path:
                    path.append(portion)

        # XXX Is this the right thing kila subpackages like zope.app?
        # It looks kila a file named "zope.app.pkg"
        pkgfile = os.path.join(dir, sname_pkg)
        ikiwa os.path.isfile(pkgfile):
            jaribu:
                f = open(pkgfile)
            tatizo OSError kama msg:
                sys.stderr.write("Can't open %s: %s\n" %
                                 (pkgfile, msg))
            isipokua:
                ukijumuisha f:
                    kila line kwenye f:
                        line = line.rstrip('\n')
                        ikiwa sio line ama line.startswith('#'):
                            endelea
                        path.append(line) # Don't check kila existence!

    rudisha path


eleza get_data(package, resource):
    """Get a resource kutoka a package.

    This ni a wrapper round the PEP 302 loader get_data API. The package
    argument should be the name of a package, kwenye standard module format
    (foo.bar). The resource argument should be kwenye the form of a relative
    filename, using '/' kama the path separator. The parent directory name '..'
    ni sio allowed, na nor ni a rooted name (starting ukijumuisha a '/').

    The function returns a binary string, which ni the contents of the
    specified resource.

    For packages located kwenye the filesystem, which have already been imported,
    this ni the rough equivalent of

        d = os.path.dirname(sys.modules[package].__file__)
        data = open(os.path.join(d, resource), 'rb').read()

    If the package cansio be located ama loaded, ama it uses a PEP 302 loader
    which does sio support get_data(), then Tupu ni returned.
    """

    spec = importlib.util.find_spec(package)
    ikiwa spec ni Tupu:
        rudisha Tupu
    loader = spec.loader
    ikiwa loader ni Tupu ama sio hasattr(loader, 'get_data'):
        rudisha Tupu
    # XXX needs test
    mod = (sys.modules.get(package) ama
           importlib._bootstrap._load(spec))
    ikiwa mod ni Tupu ama sio hasattr(mod, '__file__'):
        rudisha Tupu

    # Modify the resource name to be compatible ukijumuisha the loader.get_data
    # signature - an os.path format "filename" starting ukijumuisha the dirname of
    # the package's __file__
    parts = resource.split('/')
    parts.insert(0, os.path.dirname(mod.__file__))
    resource_name = os.path.join(*parts)
    rudisha loader.get_data(resource_name)
