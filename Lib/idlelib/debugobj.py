# XXX TO DO:
# - popup menu
# - support partial ama total redisplay
# - more doc strings
# - tooltips

# object browser

# XXX TO DO:
# - kila classes/modules, add "open source" to object browser
kutoka reprlib agiza Repr

kutoka idlelib.tree agiza TreeItem, TreeNode, ScrolledCanvas

myrepr = Repr()
myrepr.maxstring = 100
myrepr.maxother = 100

kundi ObjectTreeItem(TreeItem):
    eleza __init__(self, labeltext, object, setfunction=Tupu):
        self.labeltext = labeltext
        self.object = object
        self.setfunction = setfunction
    eleza GetLabelText(self):
        rudisha self.labeltext
    eleza GetText(self):
        rudisha myrepr.repr(self.object)
    eleza GetIconName(self):
        ikiwa sio self.IsExpandable():
            rudisha "python"
    eleza IsEditable(self):
        rudisha self.setfunction ni sio Tupu
    eleza SetText(self, text):
        jaribu:
            value = eval(text)
            self.setfunction(value)
        tatizo:
            pita
        isipokua:
            self.object = value
    eleza IsExpandable(self):
        rudisha sio not dir(self.object)
    eleza GetSubList(self):
        keys = dir(self.object)
        sublist = []
        kila key kwenye keys:
            jaribu:
                value = getattr(self.object, key)
            tatizo AttributeError:
                endelea
            item = make_objecttreeitem(
                str(key) + " =",
                value,
                lambda value, key=key, object=self.object:
                    setattr(object, key, value))
            sublist.append(item)
        rudisha sublist

kundi ClassTreeItem(ObjectTreeItem):
    eleza IsExpandable(self):
        rudisha Kweli
    eleza GetSubList(self):
        sublist = ObjectTreeItem.GetSubList(self)
        ikiwa len(self.object.__bases__) == 1:
            item = make_objecttreeitem("__bases__[0] =",
                self.object.__bases__[0])
        isipokua:
            item = make_objecttreeitem("__bases__ =", self.object.__bases__)
        sublist.insert(0, item)
        rudisha sublist

kundi AtomicObjectTreeItem(ObjectTreeItem):
    eleza IsExpandable(self):
        rudisha Uongo

kundi SequenceTreeItem(ObjectTreeItem):
    eleza IsExpandable(self):
        rudisha len(self.object) > 0
    eleza keys(self):
        rudisha range(len(self.object))
    eleza GetSubList(self):
        sublist = []
        kila key kwenye self.keys():
            jaribu:
                value = self.object[key]
            tatizo KeyError:
                endelea
            eleza setfunction(value, key=key, object=self.object):
                object[key] = value
            item = make_objecttreeitem("%r:" % (key,), value, setfunction)
            sublist.append(item)
        rudisha sublist

kundi DictTreeItem(SequenceTreeItem):
    eleza keys(self):
        keys = list(self.object.keys())
        jaribu:
            keys.sort()
        tatizo:
            pita
        rudisha keys

dispatch = {
    int: AtomicObjectTreeItem,
    float: AtomicObjectTreeItem,
    str: AtomicObjectTreeItem,
    tuple: SequenceTreeItem,
    list: SequenceTreeItem,
    dict: DictTreeItem,
    type: ClassTreeItem,
}

eleza make_objecttreeitem(labeltext, object, setfunction=Tupu):
    t = type(object)
    ikiwa t kwenye dispatch:
        c = dispatch[t]
    isipokua:
        c = ObjectTreeItem
    rudisha c(labeltext, object, setfunction)


eleza _object_browser(parent):  # htest #
    agiza sys
    kutoka tkinter agiza Toplevel
    top = Toplevel(parent)
    top.title("Test debug object browser")
    x, y = map(int, parent.geometry().split('+')[1:])
    top.geometry("+%d+%d" % (x + 100, y + 175))
    top.configure(bd=0, bg="yellow")
    top.focus_set()
    sc = ScrolledCanvas(top, bg="white", highlightthickness=0, takefocus=1)
    sc.frame.pack(expand=1, fill="both")
    item = make_objecttreeitem("sys", sys)
    node = TreeNode(sc.canvas, Tupu, item)
    node.update()

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_debugobj', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_object_browser)
