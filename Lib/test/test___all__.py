agiza unittest
kutoka test agiza support
agiza os
agiza sys


kundi NoAll(RuntimeError):
    pass

kundi FailedImport(RuntimeError):
    pass


kundi AllTest(unittest.TestCase):

    eleza check_all(self, modname):
        names = {}
        with support.check_warnings(
            (".* (module|package)", DeprecationWarning),
            ("", ResourceWarning),
            quiet=True):
            try:
                exec("agiza %s" % modname, names)
            except:
                # Silent fail here seems the best route since some modules
                # may not be available or not initialize properly in all
                # environments.
                raise FailedImport(modname)
        ikiwa not hasattr(sys.modules[modname], "__all__"):
            raise NoAll(modname)
        names = {}
        with self.subTest(module=modname):
            with support.check_warnings(
                ("", DeprecationWarning),
                ("", ResourceWarning),
                quiet=True):
                try:
                    exec("kutoka %s agiza *" % modname, names)
                except Exception as e:
                    # Include the module name in the exception string
                    self.fail("__all__ failure in {}: {}: {}".format(
                              modname, e.__class__.__name__, e))
                ikiwa "__builtins__" in names:
                    del names["__builtins__"]
                ikiwa '__annotations__' in names:
                    del names['__annotations__']
                ikiwa "__warningregistry__" in names:
                    del names["__warningregistry__"]
                keys = set(names)
                all_list = sys.modules[modname].__all__
                all_set = set(all_list)
                self.assertCountEqual(all_set, all_list, "in module {}".format(modname))
                self.assertEqual(keys, all_set, "in module {}".format(modname))

    eleza walk_modules(self, basedir, modpath):
        for fn in sorted(os.listdir(basedir)):
            path = os.path.join(basedir, fn)
            ikiwa os.path.isdir(path):
                pkg_init = os.path.join(path, '__init__.py')
                ikiwa os.path.exists(pkg_init):
                    yield pkg_init, modpath + fn
                    for p, m in self.walk_modules(path, modpath + fn + "."):
                        yield p, m
                continue
            ikiwa not fn.endswith('.py') or fn == '__init__.py':
                continue
            yield path, modpath + fn[:-3]

    eleza test_all(self):
        # Blacklisted modules and packages
        blacklist = set([
            # Will raise a SyntaxError when compiling the exec statement
            '__future__',
        ])

        ikiwa not sys.platform.startswith('java'):
            # In case _socket fails to build, make this test fail more gracefully
            # than an AttributeError somewhere deep in CGIHTTPServer.
            agiza _socket

        ignored = []
        failed_agizas = []
        lib_dir = os.path.dirname(os.path.dirname(__file__))
        for path, modname in self.walk_modules(lib_dir, ""):
            m = modname
            blacklisted = False
            while m:
                ikiwa m in blacklist:
                    blacklisted = True
                    break
                m = m.rpartition('.')[0]
            ikiwa blacklisted:
                continue
            ikiwa support.verbose:
                andika(modname)
            try:
                # This heuristic speeds up the process by removing, de facto,
                # most test modules (and avoiding the auto-executing ones).
                with open(path, "rb") as f:
                    ikiwa b"__all__" not in f.read():
                        raise NoAll(modname)
                    self.check_all(modname)
            except NoAll:
                ignored.append(modname)
            except FailedImport:
                failed_agizas.append(modname)

        ikiwa support.verbose:
            andika('Following modules have no __all__ and have been ignored:',
                  ignored)
            andika('Following modules failed to be imported:', failed_agizas)


ikiwa __name__ == "__main__":
    unittest.main()
