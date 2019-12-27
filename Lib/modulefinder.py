"""Find modules used by a script, using introspection."""

agiza dis
agiza importlib._bootstrap_external
agiza importlib.machinery
agiza marshal
agiza os
agiza sys
agiza types
agiza warnings


LOAD_CONST = dis.opmap['LOAD_CONST']
IMPORT_NAME = dis.opmap['IMPORT_NAME']
STORE_NAME = dis.opmap['STORE_NAME']
STORE_GLOBAL = dis.opmap['STORE_GLOBAL']
STORE_OPS = STORE_NAME, STORE_GLOBAL
EXTENDED_ARG = dis.EXTENDED_ARG

# Old imp constants:

_SEARCH_ERROR = 0
_PY_SOURCE = 1
_PY_COMPILED = 2
_C_EXTENSION = 3
_PKG_DIRECTORY = 5
_C_BUILTIN = 6
_PY_FROZEN = 7

# Modulefinder does a good job at simulating Python's, but it can not
# handle __path__ modifications packages make at runtime.  Therefore there
# is a mechanism whereby you can register extra paths in this map for a
# package, and it will be honored.

# Note this is a mapping is lists of paths.
packagePathMap = {}

# A Public interface
eleza AddPackagePath(packagename, path):
    packagePathMap.setdefault(packagename, []).append(path)

replacePackageMap = {}

# This ReplacePackage mechanism allows modulefinder to work around
# situations in which a package injects itself under the name
# of another package into sys.modules at runtime by calling
# ReplacePackage("real_package_name", "faked_package_name")
# before running ModuleFinder.

eleza ReplacePackage(oldname, newname):
    replacePackageMap[oldname] = newname


eleza _find_module(name, path=None):
    """An importlib reimplementation of imp.find_module (for our purposes)."""

    # It's necessary to clear the caches for our Finder first, in case any
    # modules are being added/deleted/modified at runtime. In particular,
    # test_modulefinder.py changes file tree contents in a cache-breaking way:

    importlib.machinery.PathFinder.invalidate_caches()

    spec = importlib.machinery.PathFinder.find_spec(name, path)

    ikiwa spec is None:
        raise ImportError("No module named {name!r}".format(name=name), name=name)

    # Some special cases:

    ikiwa spec.loader is importlib.machinery.BuiltinImporter:
        rudisha None, None, ("", "", _C_BUILTIN)

    ikiwa spec.loader is importlib.machinery.FrozenImporter:
        rudisha None, None, ("", "", _PY_FROZEN)

    file_path = spec.origin

    ikiwa spec.loader.is_package(name):
        rudisha None, os.path.dirname(file_path), ("", "", _PKG_DIRECTORY)

    ikiwa isinstance(spec.loader, importlib.machinery.SourceFileLoader):
        kind = _PY_SOURCE
        mode = "r"

    elikiwa isinstance(spec.loader, importlib.machinery.ExtensionFileLoader):
        kind = _C_EXTENSION
        mode = "rb"

    elikiwa isinstance(spec.loader, importlib.machinery.SourcelessFileLoader):
        kind = _PY_COMPILED
        mode = "rb"

    else:  # Should never happen.
        rudisha None, None, ("", "", _SEARCH_ERROR)

    file = open(file_path, mode)
    suffix = os.path.splitext(file_path)[-1]

    rudisha file, file_path, (suffix, mode, kind)


kundi Module:

    eleza __init__(self, name, file=None, path=None):
        self.__name__ = name
        self.__file__ = file
        self.__path__ = path
        self.__code__ = None
        # The set of global names that are assigned to in the module.
        # This includes those names imported through staragizas of
        # Python modules.
        self.globalnames = {}
        # The set of staragizas this module did that could not be
        # resolved, ie. a staragiza kutoka a non-Python module.
        self.staragizas = {}

    eleza __repr__(self):
        s = "Module(%r" % (self.__name__,)
        ikiwa self.__file__ is not None:
            s = s + ", %r" % (self.__file__,)
        ikiwa self.__path__ is not None:
            s = s + ", %r" % (self.__path__,)
        s = s + ")"
        rudisha s

kundi ModuleFinder:

    eleza __init__(self, path=None, debug=0, excludes=None, replace_paths=None):
        ikiwa path is None:
            path = sys.path
        self.path = path
        self.modules = {}
        self.badmodules = {}
        self.debug = debug
        self.indent = 0
        self.excludes = excludes ikiwa excludes is not None else []
        self.replace_paths = replace_paths ikiwa replace_paths is not None else []
        self.processed_paths = []   # Used in debugging only

    eleza msg(self, level, str, *args):
        ikiwa level <= self.debug:
            for i in range(self.indent):
                andika("   ", end=' ')
            andika(str, end=' ')
            for arg in args:
                andika(repr(arg), end=' ')
            andika()

    eleza msgin(self, *args):
        level = args[0]
        ikiwa level <= self.debug:
            self.indent = self.indent + 1
            self.msg(*args)

    eleza msgout(self, *args):
        level = args[0]
        ikiwa level <= self.debug:
            self.indent = self.indent - 1
            self.msg(*args)

    eleza run_script(self, pathname):
        self.msg(2, "run_script", pathname)
        with open(pathname) as fp:
            stuff = ("", "r", _PY_SOURCE)
            self.load_module('__main__', fp, pathname, stuff)

    eleza load_file(self, pathname):
        dir, name = os.path.split(pathname)
        name, ext = os.path.splitext(name)
        with open(pathname) as fp:
            stuff = (ext, "r", _PY_SOURCE)
            self.load_module(name, fp, pathname, stuff)

    eleza import_hook(self, name, caller=None, kutokalist=None, level=-1):
        self.msg(3, "import_hook", name, caller, kutokalist, level)
        parent = self.determine_parent(caller, level=level)
        q, tail = self.find_head_package(parent, name)
        m = self.load_tail(q, tail)
        ikiwa not kutokalist:
            rudisha q
        ikiwa m.__path__:
            self.ensure_kutokalist(m, kutokalist)
        rudisha None

    eleza determine_parent(self, caller, level=-1):
        self.msgin(4, "determine_parent", caller, level)
        ikiwa not caller or level == 0:
            self.msgout(4, "determine_parent -> None")
            rudisha None
        pname = caller.__name__
        ikiwa level >= 1: # relative agiza
            ikiwa caller.__path__:
                level -= 1
            ikiwa level == 0:
                parent = self.modules[pname]
                assert parent is caller
                self.msgout(4, "determine_parent ->", parent)
                rudisha parent
            ikiwa pname.count(".") < level:
                raise ImportError("relative agizapath too deep")
            pname = ".".join(pname.split(".")[:-level])
            parent = self.modules[pname]
            self.msgout(4, "determine_parent ->", parent)
            rudisha parent
        ikiwa caller.__path__:
            parent = self.modules[pname]
            assert caller is parent
            self.msgout(4, "determine_parent ->", parent)
            rudisha parent
        ikiwa '.' in pname:
            i = pname.rfind('.')
            pname = pname[:i]
            parent = self.modules[pname]
            assert parent.__name__ == pname
            self.msgout(4, "determine_parent ->", parent)
            rudisha parent
        self.msgout(4, "determine_parent -> None")
        rudisha None

    eleza find_head_package(self, parent, name):
        self.msgin(4, "find_head_package", parent, name)
        ikiwa '.' in name:
            i = name.find('.')
            head = name[:i]
            tail = name[i+1:]
        else:
            head = name
            tail = ""
        ikiwa parent:
            qname = "%s.%s" % (parent.__name__, head)
        else:
            qname = head
        q = self.import_module(head, qname, parent)
        ikiwa q:
            self.msgout(4, "find_head_package ->", (q, tail))
            rudisha q, tail
        ikiwa parent:
            qname = head
            parent = None
            q = self.import_module(head, qname, parent)
            ikiwa q:
                self.msgout(4, "find_head_package ->", (q, tail))
                rudisha q, tail
        self.msgout(4, "raise ImportError: No module named", qname)
        raise ImportError("No module named " + qname)

    eleza load_tail(self, q, tail):
        self.msgin(4, "load_tail", q, tail)
        m = q
        while tail:
            i = tail.find('.')
            ikiwa i < 0: i = len(tail)
            head, tail = tail[:i], tail[i+1:]
            mname = "%s.%s" % (m.__name__, head)
            m = self.import_module(head, mname, m)
            ikiwa not m:
                self.msgout(4, "raise ImportError: No module named", mname)
                raise ImportError("No module named " + mname)
        self.msgout(4, "load_tail ->", m)
        rudisha m

    eleza ensure_kutokalist(self, m, kutokalist, recursive=0):
        self.msg(4, "ensure_kutokalist", m, kutokalist, recursive)
        for sub in kutokalist:
            ikiwa sub == "*":
                ikiwa not recursive:
                    all = self.find_all_submodules(m)
                    ikiwa all:
                        self.ensure_kutokalist(m, all, 1)
            elikiwa not hasattr(m, sub):
                subname = "%s.%s" % (m.__name__, sub)
                submod = self.import_module(sub, subname, m)
                ikiwa not submod:
                    raise ImportError("No module named " + subname)

    eleza find_all_submodules(self, m):
        ikiwa not m.__path__:
            return
        modules = {}
        # 'suffixes' used to be a list hardcoded to [".py", ".pyc"].
        # But we must also collect Python extension modules - although
        # we cannot separate normal dlls kutoka Python extensions.
        suffixes = []
        suffixes += importlib.machinery.EXTENSION_SUFFIXES[:]
        suffixes += importlib.machinery.SOURCE_SUFFIXES[:]
        suffixes += importlib.machinery.BYTECODE_SUFFIXES[:]
        for dir in m.__path__:
            try:
                names = os.listdir(dir)
            except OSError:
                self.msg(2, "can't list directory", dir)
                continue
            for name in names:
                mod = None
                for suff in suffixes:
                    n = len(suff)
                    ikiwa name[-n:] == suff:
                        mod = name[:-n]
                        break
                ikiwa mod and mod != "__init__":
                    modules[mod] = mod
        rudisha modules.keys()

    eleza import_module(self, partname, fqname, parent):
        self.msgin(3, "import_module", partname, fqname, parent)
        try:
            m = self.modules[fqname]
        except KeyError:
            pass
        else:
            self.msgout(3, "import_module ->", m)
            rudisha m
        ikiwa fqname in self.badmodules:
            self.msgout(3, "import_module -> None")
            rudisha None
        ikiwa parent and parent.__path__ is None:
            self.msgout(3, "import_module -> None")
            rudisha None
        try:
            fp, pathname, stuff = self.find_module(partname,
                                                   parent and parent.__path__, parent)
        except ImportError:
            self.msgout(3, "import_module ->", None)
            rudisha None
        try:
            m = self.load_module(fqname, fp, pathname, stuff)
        finally:
            ikiwa fp:
                fp.close()
        ikiwa parent:
            setattr(parent, partname, m)
        self.msgout(3, "import_module ->", m)
        rudisha m

    eleza load_module(self, fqname, fp, pathname, file_info):
        suffix, mode, type = file_info
        self.msgin(2, "load_module", fqname, fp and "fp", pathname)
        ikiwa type == _PKG_DIRECTORY:
            m = self.load_package(fqname, pathname)
            self.msgout(2, "load_module ->", m)
            rudisha m
        ikiwa type == _PY_SOURCE:
            co = compile(fp.read()+'\n', pathname, 'exec')
        elikiwa type == _PY_COMPILED:
            try:
                data = fp.read()
                importlib._bootstrap_external._classify_pyc(data, fqname, {})
            except ImportError as exc:
                self.msgout(2, "raise ImportError: " + str(exc), pathname)
                raise
            co = marshal.loads(memoryview(data)[16:])
        else:
            co = None
        m = self.add_module(fqname)
        m.__file__ = pathname
        ikiwa co:
            ikiwa self.replace_paths:
                co = self.replace_paths_in_code(co)
            m.__code__ = co
            self.scan_code(co, m)
        self.msgout(2, "load_module ->", m)
        rudisha m

    eleza _add_badmodule(self, name, caller):
        ikiwa name not in self.badmodules:
            self.badmodules[name] = {}
        ikiwa caller:
            self.badmodules[name][caller.__name__] = 1
        else:
            self.badmodules[name]["-"] = 1

    eleza _safe_import_hook(self, name, caller, kutokalist, level=-1):
        # wrapper for self.import_hook() that won't raise ImportError
        ikiwa name in self.badmodules:
            self._add_badmodule(name, caller)
            return
        try:
            self.import_hook(name, caller, level=level)
        except ImportError as msg:
            self.msg(2, "ImportError:", str(msg))
            self._add_badmodule(name, caller)
        except SyntaxError as msg:
            self.msg(2, "SyntaxError:", str(msg))
            self._add_badmodule(name, caller)
        else:
            ikiwa kutokalist:
                for sub in kutokalist:
                    fullname = name + "." + sub
                    ikiwa fullname in self.badmodules:
                        self._add_badmodule(fullname, caller)
                        continue
                    try:
                        self.import_hook(name, caller, [sub], level=level)
                    except ImportError as msg:
                        self.msg(2, "ImportError:", str(msg))
                        self._add_badmodule(fullname, caller)

    eleza scan_opcodes(self, co):
        # Scan the code, and yield 'interesting' opcode combinations
        code = co.co_code
        names = co.co_names
        consts = co.co_consts
        opargs = [(op, arg) for _, op, arg in dis._unpack_opargs(code)
                  ikiwa op != EXTENDED_ARG]
        for i, (op, oparg) in enumerate(opargs):
            ikiwa op in STORE_OPS:
                yield "store", (names[oparg],)
                continue
            ikiwa (op == IMPORT_NAME and i >= 2
                    and opargs[i-1][0] == opargs[i-2][0] == LOAD_CONST):
                level = consts[opargs[i-2][1]]
                kutokalist = consts[opargs[i-1][1]]
                ikiwa level == 0: # absolute agiza
                    yield "absolute_agiza", (kutokalist, names[oparg])
                else: # relative agiza
                    yield "relative_agiza", (level, kutokalist, names[oparg])
                continue

    eleza scan_code(self, co, m):
        code = co.co_code
        scanner = self.scan_opcodes
        for what, args in scanner(co):
            ikiwa what == "store":
                name, = args
                m.globalnames[name] = 1
            elikiwa what == "absolute_agiza":
                kutokalist, name = args
                have_star = 0
                ikiwa kutokalist is not None:
                    ikiwa "*" in kutokalist:
                        have_star = 1
                    kutokalist = [f for f in kutokalist ikiwa f != "*"]
                self._safe_import_hook(name, m, kutokalist, level=0)
                ikiwa have_star:
                    # We've encountered an "agiza *". If it is a Python module,
                    # the code has already been parsed and we can suck out the
                    # global names.
                    mm = None
                    ikiwa m.__path__:
                        # At this point we don't know whether 'name' is a
                        # submodule of 'm' or a global module. Let's just try
                        # the full name first.
                        mm = self.modules.get(m.__name__ + "." + name)
                    ikiwa mm is None:
                        mm = self.modules.get(name)
                    ikiwa mm is not None:
                        m.globalnames.update(mm.globalnames)
                        m.staragizas.update(mm.staragizas)
                        ikiwa mm.__code__ is None:
                            m.staragizas[name] = 1
                    else:
                        m.staragizas[name] = 1
            elikiwa what == "relative_agiza":
                level, kutokalist, name = args
                ikiwa name:
                    self._safe_import_hook(name, m, kutokalist, level=level)
                else:
                    parent = self.determine_parent(m, level=level)
                    self._safe_import_hook(parent.__name__, None, kutokalist, level=0)
            else:
                # We don't expect anything else kutoka the generator.
                raise RuntimeError(what)

        for c in co.co_consts:
            ikiwa isinstance(c, type(co)):
                self.scan_code(c, m)

    eleza load_package(self, fqname, pathname):
        self.msgin(2, "load_package", fqname, pathname)
        newname = replacePackageMap.get(fqname)
        ikiwa newname:
            fqname = newname
        m = self.add_module(fqname)
        m.__file__ = pathname
        m.__path__ = [pathname]

        # As per comment at top of file, simulate runtime __path__ additions.
        m.__path__ = m.__path__ + packagePathMap.get(fqname, [])

        fp, buf, stuff = self.find_module("__init__", m.__path__)
        try:
            self.load_module(fqname, fp, buf, stuff)
            self.msgout(2, "load_package ->", m)
            rudisha m
        finally:
            ikiwa fp:
                fp.close()

    eleza add_module(self, fqname):
        ikiwa fqname in self.modules:
            rudisha self.modules[fqname]
        self.modules[fqname] = m = Module(fqname)
        rudisha m

    eleza find_module(self, name, path, parent=None):
        ikiwa parent is not None:
            # assert path is not None
            fullname = parent.__name__+'.'+name
        else:
            fullname = name
        ikiwa fullname in self.excludes:
            self.msgout(3, "find_module -> Excluded", fullname)
            raise ImportError(name)

        ikiwa path is None:
            ikiwa name in sys.builtin_module_names:
                rudisha (None, None, ("", "", _C_BUILTIN))

            path = self.path

        rudisha _find_module(name, path)

    eleza report(self):
        """Print a report to stdout, listing the found modules with their
        paths, as well as modules that are missing, or seem to be missing.
        """
        andika()
        andika("  %-25s %s" % ("Name", "File"))
        andika("  %-25s %s" % ("----", "----"))
        # Print modules found
        keys = sorted(self.modules.keys())
        for key in keys:
            m = self.modules[key]
            ikiwa m.__path__:
                andika("P", end=' ')
            else:
                andika("m", end=' ')
            andika("%-25s" % key, m.__file__ or "")

        # Print missing modules
        missing, maybe = self.any_missing_maybe()
        ikiwa missing:
            andika()
            andika("Missing modules:")
            for name in missing:
                mods = sorted(self.badmodules[name].keys())
                andika("?", name, "imported kutoka", ', '.join(mods))
        # Print modules that may be missing, but then again, maybe not...
        ikiwa maybe:
            andika()
            andika("Submodules that appear to be missing, but could also be", end=' ')
            andika("global names in the parent package:")
            for name in maybe:
                mods = sorted(self.badmodules[name].keys())
                andika("?", name, "imported kutoka", ', '.join(mods))

    eleza any_missing(self):
        """Return a list of modules that appear to be missing. Use
        any_missing_maybe() ikiwa you want to know which modules are
        certain to be missing, and which *may* be missing.
        """
        missing, maybe = self.any_missing_maybe()
        rudisha missing + maybe

    eleza any_missing_maybe(self):
        """Return two lists, one with modules that are certainly missing
        and one with modules that *may* be missing. The latter names could
        either be submodules *or* just global names in the package.

        The reason it can't always be determined is that it's impossible to
        tell which names are imported when "kutoka module agiza *" is done
        with an extension module, short of actually agizaing it.
        """
        missing = []
        maybe = []
        for name in self.badmodules:
            ikiwa name in self.excludes:
                continue
            i = name.rfind(".")
            ikiwa i < 0:
                missing.append(name)
                continue
            subname = name[i+1:]
            pkgname = name[:i]
            pkg = self.modules.get(pkgname)
            ikiwa pkg is not None:
                ikiwa pkgname in self.badmodules[name]:
                    # The package tried to agiza this module itself and
                    # failed. It's definitely missing.
                    missing.append(name)
                elikiwa subname in pkg.globalnames:
                    # It's a global in the package: definitely not missing.
                    pass
                elikiwa pkg.staragizas:
                    # It could be missing, but the package did an "agiza *"
                    # kutoka a non-Python module, so we simply can't be sure.
                    maybe.append(name)
                else:
                    # It's not a global in the package, the package didn't
                    # do funny star agizas, it's very likely to be missing.
                    # The symbol could be inserted into the package kutoka the
                    # outside, but since that's not good style we simply list
                    # it missing.
                    missing.append(name)
            else:
                missing.append(name)
        missing.sort()
        maybe.sort()
        rudisha missing, maybe

    eleza replace_paths_in_code(self, co):
        new_filename = original_filename = os.path.normpath(co.co_filename)
        for f, r in self.replace_paths:
            ikiwa original_filename.startswith(f):
                new_filename = r + original_filename[len(f):]
                break

        ikiwa self.debug and original_filename not in self.processed_paths:
            ikiwa new_filename != original_filename:
                self.msgout(2, "co_filename %r changed to %r" \
                                    % (original_filename,new_filename,))
            else:
                self.msgout(2, "co_filename %r remains unchanged" \
                                    % (original_filename,))
            self.processed_paths.append(original_filename)

        consts = list(co.co_consts)
        for i in range(len(consts)):
            ikiwa isinstance(consts[i], type(co)):
                consts[i] = self.replace_paths_in_code(consts[i])

        rudisha co.replace(co_consts=tuple(consts), co_filename=new_filename)


eleza test():
    # Parse command line
    agiza getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dmp:qx:")
    except getopt.error as msg:
        andika(msg)
        return

    # Process options
    debug = 1
    domods = 0
    addpath = []
    exclude = []
    for o, a in opts:
        ikiwa o == '-d':
            debug = debug + 1
        ikiwa o == '-m':
            domods = 1
        ikiwa o == '-p':
            addpath = addpath + a.split(os.pathsep)
        ikiwa o == '-q':
            debug = 0
        ikiwa o == '-x':
            exclude.append(a)

    # Provide default arguments
    ikiwa not args:
        script = "hello.py"
    else:
        script = args[0]

    # Set the path based on sys.path and the script directory
    path = sys.path[:]
    path[0] = os.path.dirname(script)
    path = addpath + path
    ikiwa debug > 1:
        andika("path:")
        for item in path:
            andika("   ", repr(item))

    # Create the module finder and turn its crank
    mf = ModuleFinder(path, debug, exclude)
    for arg in args[1:]:
        ikiwa arg == '-m':
            domods = 1
            continue
        ikiwa domods:
            ikiwa arg[-2:] == '.*':
                mf.import_hook(arg[:-2], None, ["*"])
            else:
                mf.import_hook(arg)
        else:
            mf.load_file(arg)
    mf.run_script(script)
    mf.report()
    rudisha mf  # for -i debugging


ikiwa __name__ == '__main__':
    try:
        mf = test()
    except KeyboardInterrupt:
        andika("\n[interrupted]")
