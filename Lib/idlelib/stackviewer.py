agiza linecache
agiza os
agiza sys

agiza tkinter as tk

kutoka idlelib.debugobj agiza ObjectTreeItem, make_objecttreeitem
kutoka idlelib.tree agiza TreeNode, TreeItem, ScrolledCanvas

eleza StackBrowser(root, flist=None, tb=None, top=None):
    global sc, item, node  # For testing.
    ikiwa top is None:
        top = tk.Toplevel(root)
    sc = ScrolledCanvas(top, bg="white", highlightthickness=0)
    sc.frame.pack(expand=1, fill="both")
    item = StackTreeItem(flist, tb)
    node = TreeNode(sc.canvas, None, item)
    node.expand()


kundi StackTreeItem(TreeItem):

    eleza __init__(self, flist=None, tb=None):
        self.flist = flist
        self.stack = self.get_stack(tb)
        self.text = self.get_exception()

    eleza get_stack(self, tb):
        ikiwa tb is None:
            tb = sys.last_traceback
        stack = []
        ikiwa tb and tb.tb_frame is None:
            tb = tb.tb_next
        while tb is not None:
            stack.append((tb.tb_frame, tb.tb_lineno))
            tb = tb.tb_next
        rudisha stack

    eleza get_exception(self):
        type = sys.last_type
        value = sys.last_value
        ikiwa hasattr(type, "__name__"):
            type = type.__name__
        s = str(type)
        ikiwa value is not None:
            s = s + ": " + str(value)
        rudisha s

    eleza GetText(self):
        rudisha self.text

    eleza GetSubList(self):
        sublist = []
        for info in self.stack:
            item = FrameTreeItem(info, self.flist)
            sublist.append(item)
        rudisha sublist


kundi FrameTreeItem(TreeItem):

    eleza __init__(self, info, flist):
        self.info = info
        self.flist = flist

    eleza GetText(self):
        frame, lineno = self.info
        try:
            modname = frame.f_globals["__name__"]
        except:
            modname = "?"
        code = frame.f_code
        filename = code.co_filename
        funcname = code.co_name
        sourceline = linecache.getline(filename, lineno)
        sourceline = sourceline.strip()
        ikiwa funcname in ("?", "", None):
            item = "%s, line %d: %s" % (modname, lineno, sourceline)
        else:
            item = "%s.%s(...), line %d: %s" % (modname, funcname,
                                             lineno, sourceline)
        rudisha item

    eleza GetSubList(self):
        frame, lineno = self.info
        sublist = []
        ikiwa frame.f_globals is not frame.f_locals:
            item = VariablesTreeItem("<locals>", frame.f_locals, self.flist)
            sublist.append(item)
        item = VariablesTreeItem("<globals>", frame.f_globals, self.flist)
        sublist.append(item)
        rudisha sublist

    eleza OnDoubleClick(self):
        ikiwa self.flist:
            frame, lineno = self.info
            filename = frame.f_code.co_filename
            ikiwa os.path.isfile(filename):
                self.flist.gotofileline(filename, lineno)


kundi VariablesTreeItem(ObjectTreeItem):

    eleza GetText(self):
        rudisha self.labeltext

    eleza GetLabelText(self):
        rudisha None

    eleza IsExpandable(self):
        rudisha len(self.object) > 0

    eleza GetSubList(self):
        sublist = []
        for key in self.object.keys():
            try:
                value = self.object[key]
            except KeyError:
                continue
            eleza setfunction(value, key=key, object=self.object):
                object[key] = value
            item = make_objecttreeitem(key + " =", value, setfunction)
            sublist.append(item)
        rudisha sublist


eleza _stack_viewer(parent):  # htest #
    kutoka idlelib.pyshell agiza PyShellFileList
    top = tk.Toplevel(parent)
    top.title("Test StackViewer")
    x, y = map(int, parent.geometry().split('+')[1:])
    top.geometry("+%d+%d" % (x + 50, y + 175))
    flist = PyShellFileList(top)
    try: # to obtain a traceback object
        intentional_name_error
    except NameError:
        exc_type, exc_value, exc_tb = sys.exc_info()
    # inject stack trace to sys
    sys.last_type = exc_type
    sys.last_value = exc_value
    sys.last_traceback = exc_tb

    StackBrowser(top, flist=flist, top=top, tb=exc_tb)

    # restore sys to original state
    del sys.last_type
    del sys.last_value
    del sys.last_traceback

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_stackviewer', verbosity=2, exit=False)

    kutoka idlelib.idle_test.htest agiza run
    run(_stack_viewer)
