"""Module browser.

XXX TO DO:

- reparse when source changed (maybe just a button would be OK?)
    (or recheck on window popup)
- add popup menu with more options (e.g. doc strings, base classes, agizas)
- add base classes to kundi browser tree
- finish removing limitation to x.py files (ModuleBrowserTreeItem)
"""

agiza os
agiza pyclbr
agiza sys

kutoka idlelib.config agiza idleConf
kutoka idlelib agiza pyshell
kutoka idlelib.tree agiza TreeNode, TreeItem, ScrolledCanvas
kutoka idlelib.window agiza ListedToplevel


file_open = None  # Method...Item and Class...Item use this.
# Normally pyshell.flist.open, but there is no pyshell.flist for htest.


eleza transform_children(child_dict, modname=None):
    """Transform a child dictionary to an ordered sequence of objects.

    The dictionary maps names to pyclbr information objects.
    Filter out imported objects.
    Augment kundi names with bases.
    The insertion order of the dictionary is assumed to have been in line
    number order, so sorting is not necessary.

    The current tree only calls this once per child_dict as it saves
    TreeItems once created.  A future tree and tests might violate this,
    so a check prevents multiple in-place augmentations.
    """
    obs = []  # Use list since values should already be sorted.
    for key, obj in child_dict.items():
        ikiwa modname is None or obj.module == modname:
            ikiwa hasattr(obj, 'super') and obj.super and obj.name == key:
                # If obj.name != key, it has already been suffixed.
                supers = []
                for sup in obj.super:
                    ikiwa type(sup) is type(''):
                        sname = sup
                    else:
                        sname = sup.name
                        ikiwa sup.module != obj.module:
                            sname = f'{sup.module}.{sname}'
                    supers.append(sname)
                obj.name += '({})'.format(', '.join(supers))
            obs.append(obj)
    rudisha obs


kundi ModuleBrowser:
    """Browse module classes and functions in IDLE.
    """
    # This kundi is also the base kundi for pathbrowser.PathBrowser.
    # Init and close are inherited, other methods are overridden.
    # PathBrowser.__init__ does not call __init__ below.

    eleza __init__(self, master, path, *, _htest=False, _utest=False):
        """Create a window for browsing a module's structure.

        Args:
            master: parent for widgets.
            path: full path of file to browse.
            _htest - bool; change box location when running htest.
            -utest - bool; suppress contents when running unittest.

        Global variables:
            file_open: Function used for opening a file.

        Instance variables:
            name: Module name.
            file: Full path and module with .py extension.  Used in
                creating ModuleBrowserTreeItem as the rootnode for
                the tree and subsequently in the children.
        """
        self.master = master
        self.path = path
        self._htest = _htest
        self._utest = _utest
        self.init()

    eleza close(self, event=None):
        "Dismiss the window and the tree nodes."
        self.top.destroy()
        self.node.destroy()

    eleza init(self):
        "Create browser tkinter widgets, including the tree."
        global file_open
        root = self.master
        flist = (pyshell.flist ikiwa not (self._htest or self._utest)
                 else pyshell.PyShellFileList(root))
        file_open = flist.open
        pyclbr._modules.clear()

        # create top
        self.top = top = ListedToplevel(root)
        top.protocol("WM_DELETE_WINDOW", self.close)
        top.bind("<Escape>", self.close)
        ikiwa self._htest: # place dialog below parent ikiwa running htest
            top.geometry("+%d+%d" %
                (root.winfo_rootx(), root.winfo_rooty() + 200))
        self.settitle()
        top.focus_set()

        # create scrolled canvas
        theme = idleConf.CurrentTheme()
        background = idleConf.GetHighlight(theme, 'normal')['background']
        sc = ScrolledCanvas(top, bg=background, highlightthickness=0,
                            takefocus=1)
        sc.frame.pack(expand=1, fill="both")
        item = self.rootnode()
        self.node = node = TreeNode(sc.canvas, None, item)
        ikiwa not self._utest:
            node.update()
            node.expand()

    eleza settitle(self):
        "Set the window title."
        self.top.wm_title("Module Browser - " + os.path.basename(self.path))
        self.top.wm_iconname("Module Browser")

    eleza rootnode(self):
        "Return a ModuleBrowserTreeItem as the root of the tree."
        rudisha ModuleBrowserTreeItem(self.path)


kundi ModuleBrowserTreeItem(TreeItem):
    """Browser tree for Python module.

    Uses TreeItem as the basis for the structure of the tree.
    Used by both browsers.
    """

    eleza __init__(self, file):
        """Create a TreeItem for the file.

        Args:
            file: Full path and module name.
        """
        self.file = file

    eleza GetText(self):
        "Return the module name as the text string to display."
        rudisha os.path.basename(self.file)

    eleza GetIconName(self):
        "Return the name of the icon to display."
        rudisha "python"

    eleza GetSubList(self):
        "Return ChildBrowserTreeItems for children."
        rudisha [ChildBrowserTreeItem(obj) for obj in self.listchildren()]

    eleza OnDoubleClick(self):
        "Open a module in an editor window when double clicked."
        ikiwa os.path.normcase(self.file[-3:]) != ".py":
            return
        ikiwa not os.path.exists(self.file):
            return
        file_open(self.file)

    eleza IsExpandable(self):
        "Return True ikiwa Python (.py) file."
        rudisha os.path.normcase(self.file[-3:]) == ".py"

    eleza listchildren(self):
        "Return sequenced classes and functions in the module."
        dir, base = os.path.split(self.file)
        name, ext = os.path.splitext(base)
        ikiwa os.path.normcase(ext) != ".py":
            rudisha []
        try:
            tree = pyclbr.readmodule_ex(name, [dir] + sys.path)
        except ImportError:
            rudisha []
        rudisha transform_children(tree, name)


kundi ChildBrowserTreeItem(TreeItem):
    """Browser tree for child nodes within the module.

    Uses TreeItem as the basis for the structure of the tree.
    """

    eleza __init__(self, obj):
        "Create a TreeItem for a pyclbr class/function object."
        self.obj = obj
        self.name = obj.name
        self.isfunction = isinstance(obj, pyclbr.Function)

    eleza GetText(self):
        "Return the name of the function/kundi to display."
        name = self.name
        ikiwa self.isfunction:
            rudisha "eleza " + name + "(...)"
        else:
            rudisha "kundi " + name

    eleza GetIconName(self):
        "Return the name of the icon to display."
        ikiwa self.isfunction:
            rudisha "python"
        else:
            rudisha "folder"

    eleza IsExpandable(self):
        "Return True ikiwa self.obj has nested objects."
        rudisha self.obj.children != {}

    eleza GetSubList(self):
        "Return ChildBrowserTreeItems for children."
        rudisha [ChildBrowserTreeItem(obj)
                for obj in transform_children(self.obj.children)]

    eleza OnDoubleClick(self):
        "Open module with file_open and position to lineno."
        try:
            edit = file_open(self.obj.file)
            edit.gotoline(self.obj.lineno)
        except (OSError, AttributeError):
            pass


eleza _module_browser(parent): # htest #
    ikiwa len(sys.argv) > 1:  # If pass file on command line.
        file = sys.argv[1]
    else:
        file = __file__
        # Add nested objects for htest.
        kundi Nested_in_func(TreeNode):
            eleza nested_in_class(): pass
        eleza closure():
            kundi Nested_in_closure: pass
    ModuleBrowser(parent, file, _htest=True)

ikiwa __name__ == "__main__":
    ikiwa len(sys.argv) == 1:  # If pass file on command line, unittest fails.
        kutoka unittest agiza main
        main('idlelib.idle_test.test_browser', verbosity=2, exit=False)
    kutoka idlelib.idle_test.htest agiza run
    run(_module_browser)
