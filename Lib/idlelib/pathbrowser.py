agiza importlib.machinery
agiza os
agiza sys

kutoka idlelib.browser agiza ModuleBrowser, ModuleBrowserTreeItem
kutoka idlelib.tree agiza TreeItem


kundi PathBrowser(ModuleBrowser):

    eleza __init__(self, master, *, _htest=Uongo, _utest=Uongo):
        """
        _htest - bool, change box location when running htest
        """
        self.master = master
        self._htest = _htest
        self._utest = _utest
        self.init()

    eleza settitle(self):
        "Set window titles."
        self.top.wm_title("Path Browser")
        self.top.wm_iconname("Path Browser")

    eleza rootnode(self):
        rudisha PathBrowserTreeItem()


kundi PathBrowserTreeItem(TreeItem):

    eleza GetText(self):
        rudisha "sys.path"

    eleza GetSubList(self):
        sublist = []
        kila dir kwenye sys.path:
            item = DirBrowserTreeItem(dir)
            sublist.append(item)
        rudisha sublist


kundi DirBrowserTreeItem(TreeItem):

    eleza __init__(self, dir, packages=[]):
        self.dir = dir
        self.packages = packages

    eleza GetText(self):
        ikiwa sio self.packages:
            rudisha self.dir
        isipokua:
            rudisha self.packages[-1] + ": package"

    eleza GetSubList(self):
        jaribu:
            names = os.listdir(self.dir ama os.curdir)
        except OSError:
            rudisha []
        packages = []
        kila name kwenye names:
            file = os.path.join(self.dir, name)
            ikiwa self.ispackagedir(file):
                nn = os.path.normcase(name)
                packages.append((nn, name, file))
        packages.sort()
        sublist = []
        kila nn, name, file kwenye packages:
            item = DirBrowserTreeItem(file, self.packages + [name])
            sublist.append(item)
        kila nn, name kwenye self.listmodules(names):
            item = ModuleBrowserTreeItem(os.path.join(self.dir, name))
            sublist.append(item)
        rudisha sublist

    eleza ispackagedir(self, file):
        " Return true kila directories that are packages."
        ikiwa sio os.path.isdir(file):
            rudisha Uongo
        init = os.path.join(file, "__init__.py")
        rudisha os.path.exists(init)

    eleza listmodules(self, allnames):
        modules = {}
        suffixes = importlib.machinery.EXTENSION_SUFFIXES[:]
        suffixes += importlib.machinery.SOURCE_SUFFIXES
        suffixes += importlib.machinery.BYTECODE_SUFFIXES
        sorted = []
        kila suff kwenye suffixes:
            i = -len(suff)
            kila name kwenye allnames[:]:
                normed_name = os.path.normcase(name)
                ikiwa normed_name[i:] == suff:
                    mod_name = name[:i]
                    ikiwa mod_name sio kwenye modules:
                        modules[mod_name] = Tupu
                        sorted.append((normed_name, name))
                        allnames.remove(name)
        sorted.sort()
        rudisha sorted


eleza _path_browser(parent):  # htest #
    PathBrowser(parent, _htest=Kweli)
    parent.mainloop()

ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_pathbrowser', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_path_browser)
