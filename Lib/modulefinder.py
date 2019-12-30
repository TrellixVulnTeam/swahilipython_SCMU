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
# ni a mechanism whereby you can register extra paths kwenye this map kila a
# package, na it will be honored.

# Note this ni a mapping ni lists of paths.
packagePathMap = {}

# A Public interface
eleza AddPackagePath(packagename, path):
    packagePathMap.setdefault(packagename, []).append(path)

replacePackageMap = {}

# This ReplacePackage mechanism allows modulefinder to work around
# situations kwenye which a package injects itself under the name
# of another package into sys.modules at runtime by calling
# ReplacePackage("real_package_name", "faked_package_name")
# before running ModuleFinder.

eleza ReplacePackage(oldname, newname):
    replacePackageMap[oldname] = newname


eleza _find_module(name, path=Tupu):
    """An importlib reimplementation of imp.find_module (kila our purposes)."""

    # It's necessary to clear the caches kila our Finder first, kwenye case any
    # modules are being added/deleted/modified at runtime. In particular,
    # test_modulefinder.py changes file tree contents kwenye a cache-komaing way:

    importlib.machinery.PathFinder.invalidate_caches()

    spec = importlib.machinery.PathFinder.find_spec(name, path)

    ikiwa spec ni Tupu:
         ashiria ImportError("No module named {name!r}".format(name=name), name=name)

    # Some special cases:

    ikiwa spec.loader ni importlib.machinery.BuiltinImporter:
        rudisha Tupu, Tupu, ("", "", _C_BUILTIN)

    ikiwa spec.loader ni importlib.machinery.FrozenImporter:
        rudisha Tupu, Tupu, ("", "", _PY_FROZEN)

    file_path = spec.origin

    ikiwa spec.loader.is_package(name):
        rudisha Tupu, os.path.dirname(file_path), ("", "", _PKG_DIRECTORY)

    ikiwa isinstance(spec.loader, importlib.machinery.SourceFileLoader):
        kind = _PY_SOURCE
        mode = "r"

    elikiwa isinstance(spec.loader, importlib.machinery.ExtensionFileLoader):
        kind = _C_EXTENSION
        mode = "rb"

    elikiwa isinstance(spec.loader, importlib.machinery.SourcelessFileLoader):
        kind = _PY_COMPILED
        mode = "rb"

    isipokua:  # Should never happen.
        rudisha Tupu, Tupu, ("", "", _SEARCH_ERROR)

    file = open(file_path, mode)
    suffix = os.path.splitext(file_path)[-1]

    rudisha file, file_path, (suffix, mode, kind)


kundi Module:

    eleza __init__(self, name, file=Tupu, path=Tupu):
        self.__name__ = name
        self.__file__ = file
        self.__path__ = path
        self.__code__ = Tupu
        # The set of global names that are assigned to kwenye the module.
        # This includes those names imported through starimports of
        # Python modules.
        self.globalnames = {}
        # The set of starimports this module did that could sio be
        # resolved, ie. a staragiza kutoka a non-Python module.
        self.starimports = {}

    eleza __repr__(self):
        s = "Module(%r" % (self.__name__,)
        ikiwa self.__file__ ni sio Tupu:
            s = s + ", %r" % (self.__file__,)
        ikiwa self.__path__ ni sio Tupu:
            s = s + ", %r" % (self.__path__,)
        s = s + ")"
        rudisha s

kundi ModuleFinder:

    eleza __init__(self, path=Tupu, debug=0, excludes=Tupu, replace_paths=Tupu):
        ikiwa path ni Tupu:
            path = sys.path
        self.path = path
        self.modules = {}
        self.badmodules = {}
        self.debug = debug
        self.indent = 0
        self.excludes = excludes ikiwa excludes ni sio Tupu isipokua []
        self.replace_paths = replace_paths ikiwa replace_paths ni sio Tupu isipokua []
        self.processed_paths = []   # Used kwenye debugging only

    eleza msg(self, level, str, *args):
        ikiwa level <= self.debug:
            kila i kwenye range(self.indent):
                andika("   ", end=' ')
            andika(str, end=' ')
            kila arg kwenye args:
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
        ukijumuisha open(pathname) as fp:
            stuff = ("", "r", _PY_SOURCE)
            self.load_module('__main__', fp, pathname, stuff)

    eleza load_file(self, pathname):
        dir, name = os.path.split(pathname)
        name, ext = os.path.splitext(name)
        ukijumuisha open(pathname) as fp:
            stuff = (ext, "r", _PY_SOURCE)
            self.load_module(name, fp, pathname, stuff)

    eleza import_hook(self, name, caller=Tupu, fromlist=Tupu, level=-1):
        self.msg(3, "import_hook", name, caller, fromlist, level)
        parent = self.determine_parent(caller, level=level)
        q, tail = self.find_head_package(parent, name)
        m = self.load_tail(q, tail)
        ikiwa sio fromlist:
            rudisha q
        ikiwa m.__path__:
            self.ensure_fromlist(m, fromlist)
        rudisha Tupu

    eleza determine_parent(self, caller, level=-1):
        self.msgin(4, "determine_parent", caller, level)
        ikiwa sio caller ama level == 0:
            self.msgout(4, "determine_parent -> Tupu")
            rudisha Tupu
        pname = caller.__name__
        ikiwa level >= 1: # relative import
            ikiwa caller.__path__:
                level -= 1
            ikiwa level == 0:
                parent = self.modules[pname]
                assert parent ni caller
                self.msgout(4, "determine_parent ->", parent)
                rudisha parent
            ikiwa pname.count(".") < level:
                 ashiria ImportError("relative importpath too deep")
            pname = ".".join(pname.split(".")[:-level])
            parent = self.modules[pname]
            self.msgout(4, "determine_parent ->", parent)
            rudisha parent
        ikiwa caller.__path__:
            parent = self.modules[pname]
            assert caller ni parent
            self.msgout(4, "determine_parent ->", parent)
            rudisha parent
        ikiwa '.' kwenye pname:
            i = pname.rfind('.')
            pname = pname[:i]
            parent = self.modules[pname]
            assert parent.__name__ == pname
            self.msgout(4, "determine_parent ->", parent)
            rudisha parent
        self.msgout(4, "determine_parent -> Tupu")
        rudisha Tupu

    eleza find_head_package(self, parent, name):
        self.msgin(4, "find_head_package", parent, name)
        ikiwa '.' kwenye name:
            i = name.find('.')
            head = name[:i]
            tail = name[i+1:]
        isipokua:
            head = name
            tail = ""
        ikiwa parent:
            qname = "%s.%s" % (parent.__name__, head)
        isipokua:
            qname = head
        q = self.import_module(head, qname, parent)
        ikiwa q:
            self.msgout(4, "find_head_package ->", (q, tail))
            rudisha q, tail
        ikiwa parent:
            qname = head
            parent = Tupu
            q = self.import_module(head, qname, parent)
            ikiwa q:
                self.msgout(4, "find_head_package ->", (q, tail))
                rudisha q, tail
        self.msgout(4, " ashiria ImportError: No module named", qname)
         ashiria ImportError("No module named " + qname)

    eleza load_tail(self, q, tail):
        self.msgin(4, "load_tail", q, tail)
        m = q
        wakati tail:
            i = tail.find('.')
            ikiwa i < 0: i = len(tail)
            head, tail = tail[:i], tail[i+1:]
            mname = "%s.%s" % (m.__name__, head)
            m = self.import_module(head, mname, m)
            ikiwa sio m:
                self.msgout(4, " ashiria ImportError: No module named", mname)
                 ashiria ImportError("No module named " + mname)
        self.msgout(4, "load_tail ->", m)
        rudisha m

    eleza ensure_fromlist(self, m, fromlist, recursive=0):
        self.msg(4, "ensure_fromlist", m, fromlist, recursive)
        kila sub kwenye fromlist:
            ikiwa sub == "*":
                ikiwa sio recursive:
                    all = self.find_all_submodules(m)
                    ikiwa all:
                        self.ensure_fromlist(m, all, 1)
            elikiwa sio hasattr(m, sub):
                subname = "%s.%s" % (m.__name__, sub)
                submod = self.import_module(sub, subname, m)
                ikiwa sio submod:
                     ashiria ImportError("No module named " + subname)

    eleza find_all_submodules(self, m):
        ikiwa sio m.__path__:
            return
        modules = {}
        # 'suffixes' used to be a list hardcoded to [".py", ".pyc"].
        # But we must also collect Python extension modules - although
        # we cannot separate normal dlls kutoka Python extensions.
        suffixes = []
        suffixes += importlib.machinery.EXTENSION_SUFFIXES[:]
        suffixes += importlib.machinery.SOURCE_SUFFIXES[:]
        suffixes += importlib.machinery.BYTECODE_SUFFIXES[:]
        kila dir kwenye m.__path__:
            jaribu:
                names = os.listdir(dir)
            except OSError:
                self.msg(2, "can't list directory", dir)
                endelea
            kila name kwenye names:
                mod = Tupu
                kila suff kwenye suffixes:
                    n = len(suff)
                    ikiwa name[-n:] == suff:
                        mod = name[:-n]
                        koma
                ikiwa mod na mod != "__init__":
                    modules[mod] = mod
        rudisha modules.keys()

    eleza import_module(self, partname, fqname, parent):
        self.msgin(3, "import_module", partname, fqname, parent)
        jaribu:
            m = self.modules[fqname]
        except KeyError:
            pass
        isipokua:
            self.msgout(3, "import_module ->", m)
            rudisha m
        ikiwa fqname kwenye self.badmodules:
            self.msgout(3, "import_module -> Tupu")
            rudisha Tupu
        ikiwa parent na parent.__path__ ni Tupu:
            self.msgout(3, "import_module -> Tupu")
            rudisha Tupu
        jaribu:
            fp, pathname, stuff = self.find_module(partname,
                                                   parent na parent.__path__, parent)
        except ImportError:
            self.msgout(3, "import_module ->", Tupu)
            rudisha Tupu
        jaribu:
            m = self.load_module(fqname, fp, pathname, stuff)
        mwishowe:
            ikiwa fp:
                fp.close()
        ikiwa parent:
            setattr(parent, partname, m)
        self.msgout(3, "import_module ->", m)
        rudisha m

    eleza load_module(self, fqname, fp, pathname, file_info):
        suffix, mode, type = file_info
        self.msgin(2, "load_module", fqname, fp na "fp", pathname)
        ikiwa type == _PKG_DIRECTORY:
            m = self.load_package(fqname, pathname)
            self.msgout(2, "load_module ->", m)
            rudisha m
        ikiwa type == _PY_SOURCE:
            co = compile(fp.read()+'\n', pathname, 'exec')
        elikiwa type == _PY_COMPILED:
            jaribu:
                data = fp.read()
                importlib._bootstrap_external._classify_pyc(data, fqname, {})
            except ImportError as exc:
                self.msgout(2, " ashiria ImportError: " + str(exc), pathname)
                raise
            co = marshal.loads(memoryview(data)[16:])
        isipokua:
            co = Tupu
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
        ikiwa name sio kwenye self.badmodules:
            self.badmodules[name] = {}
        ikiwa caller:
            self.badmodules[name][caller.__name__] = 1
        isipokua:
            self.badmodules[name]["-"] = 1

    eleza _safe_import_hook(self, name, caller, fromlist, level=-1):
        # wrapper kila self.import_hook() that won't  ashiria ImportError
        ikiwa name kwenye self.badmodules:
            self._add_badmodule(name, caller)
            return
        jaribu:
            self.import_hook(name, caller, level=level)
        except ImportError as msg:
            self.msg(2, "ImportError:", str(msg))
            self._add_badmodule(name, caller)
        except SyntaxError as msg:
            self.msg(2, "SyntaxError:", str(msg))
            self._add_badmodule(name, caller)
        isipokua:
            ikiwa fromlist:
                kila sub kwenye fromlist:
                    fullname = name + "." + sub
                    ikiwa fullname kwenye self.badmodules:
                        self._add_badmodule(fullname, caller)
                        endelea
                    jaribu:
                        self.import_hook(name, caller, [sub], level=level)
                    except ImportError as msg:
                        self.msg(2, "ImportError:", str(msg))
                        self._add_badmodule(fullname, caller)

    eleza scan_opcodes(self, co):
        # Scan the code, na tuma 'interesting' opcode combinations
        code = co.co_code
        names = co.co_names
        consts = co.co_consts
        opargs = [(op, arg) kila _, op, arg kwenye dis._unpack_opargs(code)
                  ikiwa op != EXTENDED_ARG]
        kila i, (op, oparg) kwenye enumerate(opargs):
            ikiwa op kwenye STORE_OPS:
                tuma "store", (names[oparg],)
                endelea
            ikiwa (op == IMPORT_NAME na i >= 2
                    na opargs[i-1][0] == opargs[i-2][0] == LOAD_CONST):
                level = consts[opargs[i-2][1]]
                fromlist = consts[opargs[i-1][1]]
                ikiwa level == 0: # absolute import
                    tuma "absolute_import", (fromlist, names[oparg])
                isipokua: # relative import
                    tuma "relative_import", (level, fromlist, names[oparg])
                endelea

    eleza scan_code(self, co, m):
        code = co.co_code
        scanner = self.scan_opcodes
        kila what, args kwenye scanner(co):
            ikiwa what == "store":
                name, = args
                m.globalnames[name] = 1
            elikiwa what == "absolute_import":
                fromlist, name = args
                have_star = 0
                ikiwa fromlist ni sio Tupu:
                    ikiwa "*" kwenye fromlist:
                        have_star = 1
                    fromlist = [f kila f kwenye fromlist ikiwa f != "*"]
                self._safe_import_hook(name, m, fromlist, level=0)
                ikiwa have_star:
                    # We've encountered an "agiza *". If it ni a Python module,
                    # the code has already been parsed na we can suck out the
                    # global names.
                    mm = Tupu
                    ikiwa m.__path__:
                        # At this point we don't know whether 'name' ni a
                        # submodule of 'm' ama a global module. Let's just try
                        # the full name first.
                        mm = self.modules.get(m.__name__ + "." + name)
                    ikiwa mm ni Tupu:
                        mm = self.modules.get(name)
                    ikiwa mm ni sio Tupu:
                        m.globalnames.update(mm.globalnames)
                        m.starimports.update(mm.starimports)
                        ikiwa mm.__code__ ni Tupu:
                            m.starimports[name] = 1
                    isipokua:
                        m.starimports[name] = 1
            elikiwa what == "relative_import":
                level, fromlist, name = args
                ikiwa name:
                    self._safe_import_hook(name, m, fromlist, level=level)
                isipokua:
                    parent = self.determine_parent(m, level=level)
                    self._safe_import_hook(parent.__name__, Tupu, fromlist, level=0)
            isipokua:
                # We don't expect anything isipokua kutoka the generator.
                 ashiria RuntimeError(what)

        kila c kwenye co.co_consts:
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
        jaribu:
            self.load_module(fqname, fp, buf, stuff)
            self.msgout(2, "load_package ->", m)
            rudisha m
        mwishowe:
            ikiwa fp:
                fp.close()

    eleza add_module(self, fqname):
        ikiwa fqname kwenye self.modules:
            rudisha self.modules[fqname]
        self.modules[fqname] = m = Module(fqname)
        rudisha m

    eleza find_module(self, name, path, parent=Tupu):
        ikiwa parent ni sio Tupu:
            # assert path ni sio Tupu
            fullname = parent.__name__+'.'+name
        isipokua:
            fullname = name
        ikiwa fullname kwenye self.excludes:
            self.msgout(3, "find_module -> Excluded", fullname)
             ashiria ImportError(name)

        ikiwa path ni Tupu:
            ikiwa name kwenye sys.builtin_module_names:
                rudisha (Tupu, Tupu, ("", "", _C_BUILTIN))

            path = self.path

        rudisha _find_module(name, path)

    eleza report(self):
        """Print a report to stdout, listing the found modules ukijumuisha their
        paths, as well as modules that are missing, ama seem to be missing.
        """
        andika()
        andika("  %-25s %s" % ("Name", "File"))
        andika("  %-25s %s" % ("----", "----"))
        # Print modules found
        keys = sorted(self.modules.keys())
        kila key kwenye keys:
            m = self.modules[key]
            ikiwa m.__path__:
                andika("P", end=' ')
            isipokua:
                andika("m", end=' ')
            andika("%-25s" % key, m.__file__ ama "")

        # Print missing modules
        missing, maybe = self.any_missing_maybe()
        ikiwa missing:
            andika()
            andika("Missing modules:")
            kila name kwenye missing:
                mods = sorted(self.badmodules[name].keys())
                andika("?", name, "imported from", ', '.join(mods))
        # Print modules that may be missing, but then again, maybe not...
        ikiwa maybe:
            andika()
            andika("Submodules that appear to be missing, but could also be", end=' ')
            andika("global names kwenye the parent package:")
            kila name kwenye maybe:
                mods = sorted(self.badmodules[name].keys())
                andika("?", name, "imported from", ', '.join(mods))

    eleza any_missing(self):
        """Return a list of modules that appear to be missing. Use
        any_missing_maybe() ikiwa you want to know which modules are
        certain to be missing, na which *may* be missing.
        """
        missing, maybe = self.any_missing_maybe()
        rudisha missing + maybe

    eleza any_missing_maybe(self):
        """Return two lists, one ukijumuisha modules that are certainly missing
        na one ukijumuisha modules that *may* be missing. The latter names could
        either be submodules *or* just global names kwenye the package.

        The reason it can't always be determined ni that it's impossible to
        tell which names are imported when "kutoka module agiza *" ni done
        ukijumuisha an extension module, short of actually importing it.
        """
        missing = []
        maybe = []
        kila name kwenye self.badmodules:
            ikiwa name kwenye self.excludes:
                endelea
            i = name.rfind(".")
            ikiwa i < 0:
                missing.append(name)
                endelea
            subname = name[i+1:]
            pkgname = name[:i]
            pkg = self.modules.get(pkgname)
            ikiwa pkg ni sio Tupu:
                ikiwa pkgname kwenye self.badmodules[name]:
                    # The package tried to agiza this module itself and
                    # failed. It's definitely missing.
                    missing.append(name)
                elikiwa subname kwenye pkg.globalnames:
                    # It's a global kwenye the package: definitely sio missing.
                    pass
                elikiwa pkg.starimports:
                    # It could be missing, but the package did an "agiza *"
                    # kutoka a non-Python module, so we simply can't be sure.
                    maybe.append(name)
                isipokua:
                    # It's sio a global kwenye the package, the package didn't
                    # do funny star imports, it's very likely to be missing.
                    # The symbol could be inserted into the package kutoka the
                    # outside, but since that's sio good style we simply list
                    # it missing.
                    missing.append(name)
            isipokua:
                missing.append(name)
        missing.sort()
        maybe.sort()
        rudisha missing, maybe

    eleza replace_paths_in_code(self, co):
        new_filename = original_filename = os.path.normpath(co.co_filename)
        kila f, r kwenye self.replace_paths:
            ikiwa original_filename.startswith(f):
                new_filename = r + original_filename[len(f):]
                koma

        ikiwa self.debug na original_filename sio kwenye self.processed_paths:
            ikiwa new_filename != original_filename:
                self.msgout(2, "co_filename %r changed to %r" \
                                    % (original_filename,new_filename,))
            isipokua:
                self.msgout(2, "co_filename %r remains unchanged" \
                                    % (original_filename,))
            self.processed_paths.append(original_filename)

        consts = list(co.co_consts)
        kila i kwenye range(len(consts)):
            ikiwa isinstance(consts[i], type(co)):
                consts[i] = self.replace_paths_in_code(consts[i])

        rudisha co.replace(co_consts=tuple(consts), co_filename=new_filename)


eleza test():
    # Parse command line
    agiza getopt
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], "dmp:qx:")
    except getopt.error as msg:
        andika(msg)
        return

    # Process options
    debug = 1
    domods = 0
    addpath = []
    exclude = []
    kila o, a kwenye opts:
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
    ikiwa sio args:
        script = "hello.py"
    isipokua:
        script = args[0]

    # Set the path based on sys.path na the script directory
    path = sys.path[:]
    path[0] = os.path.dirname(script)
    path = addpath + path
    ikiwa debug > 1:
        andika("path:")
        kila item kwenye path:
            andika("   ", repr(item))

    # Create the module finder na turn its crank
    mf = ModuleFinder(path, debug, exclude)
    kila arg kwenye args[1:]:
        ikiwa arg == '-m':
            domods = 1
            endelea
        ikiwa domods:
            ikiwa arg[-2:] == '.*':
                mf.import_hook(arg[:-2], Tupu, ["*"])
            isipokua:
                mf.import_hook(arg)
        isipokua:
            mf.load_file(arg)
    mf.run_script(script)
    mf.report()
    rudisha mf  # kila -i debugging


ikiwa __name__ == '__main__':
    jaribu:
        mf = test()
    except KeyboardInterrupt:
        andika("\n[interrupted]")
