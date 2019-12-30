agiza linecache
agiza os
agiza sys

agiza tkinter as tk

kutoka idlelib.debugobj agiza ObjectTreeItem, make_objecttreeitem
kutoka idlelib.tree agiza TreeNode, TreeItem, ScrolledCanvas

eleza StackBrowser(root, flist=Tupu, tb=Tupu, top=Tupu):
    global sc, item, node  # For testing.
    ikiwa top ni Tupu:
        top = tk.Toplevel(root)
    sc = ScrolledCanvas(top, bg="white", highlightthickness=0)
    sc.frame.pack(expand=1, fill="both")
    item = StackTreeItem(flist, tb)
    node = TreeNode(sc.canvas, Tupu, item)
    node.expand()


kundi StackTreeItem(TreeItem):

    eleza __init__(self, flist=Tupu, tb=Tupu):
        self.flist = flist
        self.stack = self.get_stack(tb)
        self.text = self.get_exception()

    eleza get_stack(self, tb):
        ikiwa tb ni Tupu:
            tb = sys.last_traceback
        stack = []
        ikiwa tb na tb.tb_frame ni Tupu:
            tb = tb.tb_next
        wakati tb ni sio Tupu:
            stack.append((tb.tb_frame, tb.tb_lineno))
            tb = tb.tb_next
        rudisha stack

    eleza get_exception(self):
        type = sys.last_type
        value = sys.last_value
        ikiwa hasattr(type, "__name__"):
            type = type.__name__
        s = str(type)
        ikiwa value ni sio Tupu:
            s = s + ": " + str(value)
        rudisha s

    eleza GetText(self):
        rudisha self.text

    eleza GetSubList(self):
        sublist = []
        kila info kwenye self.stack:
            item = FrameTreeItem(info, self.flist)
            sublist.append(item)
        rudisha sublist


kundi FrameTreeItem(TreeItem):

    eleza __init__(self, info, flist):
        self.info = info
        self.flist = flist

    eleza GetText(self):
        frame, lineno = self.info
        jaribu:
            modname = frame.f_globals["__name__"]
        tatizo:
            modname = "?"
        code = frame.f_code
        filename = code.co_filename
        funcname = code.co_name
        sourceline = linecache.getline(filename, lineno)
        sourceline = sourceline.strip()
        ikiwa funcname kwenye ("?", "", Tupu):
            item = "%s, line %d: %s" % (modname, lineno, sourceline)
        isipokua:
            item = "%s.%s(...), line %d: %s" % (modname, funcname,
                                             lineno, sourceline)
        rudisha item

    eleza GetSubList(self):
        frame, lineno = self.info
        sublist = []
        ikiwa frame.f_globals ni sio frame.f_locals:
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
        rudisha Tupu

    eleza IsExpandable(self):
        rudisha len(self.object) > 0

    eleza GetSubList(self):
        sublist = []
        kila key kwenye self.object.keys():
            jaribu:
                value = self.object[key]
            except KeyError:
                endelea
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
    jaribu: # to obtain a traceback object
        intentional_name_error
    except NameError:
        exc_type, exc_value, exc_tb = sys.exc_info()
    # inject stack trace to sys
    sys.last_type = exc_type
    sys.last_value = exc_value
    sys.last_traceback = exc_tb

    StackBrowser(top, flist=flist, top=top, tb=exc_tb)

    # restore sys to original state
    toa sys.last_type
    toa sys.last_value
    toa sys.last_traceback

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_stackviewer', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_stack_viewer)
