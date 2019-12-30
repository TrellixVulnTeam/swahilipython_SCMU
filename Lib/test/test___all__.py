agiza unittest
kutoka test agiza support
agiza os
agiza sys


kundi NoAll(RuntimeError):
    pita

kundi FailedImport(RuntimeError):
    pita


kundi AllTest(unittest.TestCase):

    eleza check_all(self, modname):
        names = {}
        ukijumuisha support.check_warnings(
            (".* (module|package)", DeprecationWarning),
            ("", ResourceWarning),
            quiet=Kweli):
            jaribu:
                exec("agiza %s" % modname, names)
            tatizo:
                # Silent fail here seems the best route since some modules
                # may sio be available ama sio initialize properly kwenye all
                # environments.
                ashiria FailedImport(modname)
        ikiwa sio hasattr(sys.modules[modname], "__all__"):
            ashiria NoAll(modname)
        names = {}
        ukijumuisha self.subTest(module=modname):
            ukijumuisha support.check_warnings(
                ("", DeprecationWarning),
                ("", ResourceWarning),
                quiet=Kweli):
                jaribu:
                    exec("kutoka %s agiza *" % modname, names)
                tatizo Exception kama e:
                    # Include the module name kwenye the exception string
                    self.fail("__all__ failure kwenye {}: {}: {}".format(
                              modname, e.__class__.__name__, e))
                ikiwa "__builtins__" kwenye names:
                    toa names["__builtins__"]
                ikiwa '__annotations__' kwenye names:
                    toa names['__annotations__']
                ikiwa "__warningregistry__" kwenye names:
                    toa names["__warningregistry__"]
                keys = set(names)
                all_list = sys.modules[modname].__all__
                all_set = set(all_list)
                self.assertCountEqual(all_set, all_list, "in module {}".format(modname))
                self.assertEqual(keys, all_set, "in module {}".format(modname))

    eleza walk_modules(self, basedir, modpath):
        kila fn kwenye sorted(os.listdir(basedir)):
            path = os.path.join(basedir, fn)
            ikiwa os.path.isdir(path):
                pkg_init = os.path.join(path, '__init__.py')
                ikiwa os.path.exists(pkg_init):
                    tuma pkg_init, modpath + fn
                    kila p, m kwenye self.walk_modules(path, modpath + fn + "."):
                        tuma p, m
                endelea
            ikiwa sio fn.endswith('.py') ama fn == '__init__.py':
                endelea
            tuma path, modpath + fn[:-3]

    eleza test_all(self):
        # Blacklisted modules na packages
        blacklist = set([
            # Will ashiria a SyntaxError when compiling the exec statement
            '__future__',
        ])

        ikiwa sio sys.platform.startswith('java'):
            # In case _socket fails to build, make this test fail more gracefully
            # than an AttributeError somewhere deep kwenye CGIHTTPServer.
            agiza _socket

        ignored = []
        failed_agizas = []
        lib_dir = os.path.dirname(os.path.dirname(__file__))
        kila path, modname kwenye self.walk_modules(lib_dir, ""):
            m = modname
            blacklisted = Uongo
            wakati m:
                ikiwa m kwenye blacklist:
                    blacklisted = Kweli
                    koma
                m = m.rpartition('.')[0]
            ikiwa blacklisted:
                endelea
            ikiwa support.verbose:
                andika(modname)
            jaribu:
                # This heuristic speeds up the process by removing, de facto,
                # most test modules (and avoiding the auto-executing ones).
                ukijumuisha open(path, "rb") kama f:
                    ikiwa b"__all__" haiko kwenye f.read():
                        ashiria NoAll(modname)
                    self.check_all(modname)
            tatizo NoAll:
                ignored.append(modname)
            tatizo FailedImport:
                failed_agizas.append(modname)

        ikiwa support.verbose:
            andika('Following modules have no __all__ na have been ignored:',
                  ignored)
            andika('Following modules failed to be imported:', failed_agizas)


ikiwa __name__ == "__main__":
    unittest.main()
