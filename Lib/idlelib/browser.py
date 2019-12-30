"""Module browser.

XXX TO DO:

- reparse when source changed (maybe just a button would be OK?)
    (or recheck on window popup)
- add popup menu ukijumuisha more options (e.g. doc strings, base classes, imports)
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


file_open = Tupu  # Method...Item na Class...Item use this.
# Normally pyshell.flist.open, but there ni no pyshell.flist kila htest.


eleza transform_children(child_dict, modname=Tupu):
    """Transform a child dictionary to an ordered sequence of objects.

    The dictionary maps names to pyclbr information objects.
    Filter out imported objects.
    Augment kundi names ukijumuisha bases.
    The insertion order of the dictionary ni assumed to have been kwenye line
    number order, so sorting ni sio necessary.

    The current tree only calls this once per child_dict kama it saves
    TreeItems once created.  A future tree na tests might violate this,
    so a check prevents multiple in-place augmentations.
    """
    obs = []  # Use list since values should already be sorted.
    kila key, obj kwenye child_dict.items():
        ikiwa modname ni Tupu ama obj.module == modname:
            ikiwa hasattr(obj, 'super') na obj.super na obj.name == key:
                # If obj.name != key, it has already been suffixed.
                supers = []
                kila sup kwenye obj.super:
                    ikiwa type(sup) ni type(''):
                        sname = sup
                    isipokua:
                        sname = sup.name
                        ikiwa sup.module != obj.module:
                            sname = f'{sup.module}.{sname}'
                    supers.append(sname)
                obj.name += '({})'.format(', '.join(supers))
            obs.append(obj)
    rudisha obs


kundi ModuleBrowser:
    """Browse module classes na functions kwenye IDLE.
    """
    # This kundi ni also the base kundi kila pathbrowser.PathBrowser.
    # Init na close are inherited, other methods are overridden.
    # PathBrowser.__init__ does sio call __init__ below.

    eleza __init__(self, master, path, *, _htest=Uongo, _utest=Uongo):
        """Create a window kila browsing a module's structure.

        Args:
            master: parent kila widgets.
            path: full path of file to browse.
            _htest - bool; change box location when running htest.
            -utest - bool; suppress contents when running unittest.

        Global variables:
            file_open: Function used kila opening a file.

        Instance variables:
            name: Module name.
            file: Full path na module ukijumuisha .py extension.  Used in
                creating ModuleBrowserTreeItem kama the rootnode for
                the tree na subsequently kwenye the children.
        """
        self.master = master
        self.path = path
        self._htest = _htest
        self._utest = _utest
        self.init()

    eleza close(self, event=Tupu):
        "Dismiss the window na the tree nodes."
        self.top.destroy()
        self.node.destroy()

    eleza init(self):
        "Create browser tkinter widgets, including the tree."
        global file_open
        root = self.master
        flist = (pyshell.flist ikiwa sio (self._htest ama self._utest)
                 isipokua pyshell.PyShellFileList(root))
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
        self.node = node = TreeNode(sc.canvas, Tupu, item)
        ikiwa sio self._utest:
            node.update()
            node.expand()

    eleza settitle(self):
        "Set the window title."
        self.top.wm_title("Module Browser - " + os.path.basename(self.path))
        self.top.wm_iconname("Module Browser")

    eleza rootnode(self):
        "Return a ModuleBrowserTreeItem kama the root of the tree."
        rudisha ModuleBrowserTreeItem(self.path)


kundi ModuleBrowserTreeItem(TreeItem):
    """Browser tree kila Python module.

    Uses TreeItem kama the basis kila the structure of the tree.
    Used by both browsers.
    """

    eleza __init__(self, file):
        """Create a TreeItem kila the file.

        Args:
            file: Full path na module name.
        """
        self.file = file

    eleza GetText(self):
        "Return the module name kama the text string to display."
        rudisha os.path.basename(self.file)

    eleza GetIconName(self):
        "Return the name of the icon to display."
        rudisha "python"

    eleza GetSubList(self):
        "Return ChildBrowserTreeItems kila children."
        rudisha [ChildBrowserTreeItem(obj) kila obj kwenye self.listchildren()]

    eleza OnDoubleClick(self):
        "Open a module kwenye an editor window when double clicked."
        ikiwa os.path.normcase(self.file[-3:]) != ".py":
            rudisha
        ikiwa sio os.path.exists(self.file):
            rudisha
        file_open(self.file)

    eleza IsExpandable(self):
        "Return Kweli ikiwa Python (.py) file."
        rudisha os.path.normcase(self.file[-3:]) == ".py"

    eleza listchildren(self):
        "Return sequenced classes na functions kwenye the module."
        dir, base = os.path.split(self.file)
        name, ext = os.path.splitext(base)
        ikiwa os.path.normcase(ext) != ".py":
            rudisha []
        jaribu:
            tree = pyclbr.readmodule_ex(name, [dir] + sys.path)
        tatizo ImportError:
            rudisha []
        rudisha transform_children(tree, name)


kundi ChildBrowserTreeItem(TreeItem):
    """Browser tree kila child nodes within the module.

    Uses TreeItem kama the basis kila the structure of the tree.
    """

    eleza __init__(self, obj):
        "Create a TreeItem kila a pyclbr class/function object."
        self.obj = obj
        self.name = obj.name
        self.isfunction = isinstance(obj, pyclbr.Function)

    eleza GetText(self):
        "Return the name of the function/kundi to display."
        name = self.name
        ikiwa self.isfunction:
            rudisha "eleza " + name + "(...)"
        isipokua:
            rudisha "kundi " + name

    eleza GetIconName(self):
        "Return the name of the icon to display."
        ikiwa self.isfunction:
            rudisha "python"
        isipokua:
            rudisha "folder"

    eleza IsExpandable(self):
        "Return Kweli ikiwa self.obj has nested objects."
        rudisha self.obj.children != {}

    eleza GetSubList(self):
        "Return ChildBrowserTreeItems kila children."
        rudisha [ChildBrowserTreeItem(obj)
                kila obj kwenye transform_children(self.obj.children)]

    eleza OnDoubleClick(self):
        "Open module ukijumuisha file_open na position to lineno."
        jaribu:
            edit = file_open(self.obj.file)
            edit.gotoline(self.obj.lineno)
        tatizo (OSError, AttributeError):
            pita


eleza _module_browser(parent): # htest #
    ikiwa len(sys.argv) > 1:  # If pita file on command line.
        file = sys.argv[1]
    isipokua:
        file = __file__
        # Add nested objects kila htest.
        kundi Nested_in_func(TreeNode):
            eleza nested_in_class(): pita
        eleza closure():
            kundi Nested_in_closure: pita
    ModuleBrowser(parent, file, _htest=Kweli)

ikiwa __name__ == "__main__":
    ikiwa len(sys.argv) == 1:  # If pita file on command line, unittest fails.
        kutoka unittest agiza main
        main('idlelib.idle_test.test_browser', verbosity=2, exit=Uongo)
    kutoka idlelib.idle_test.htest agiza run
    run(_module_browser)
