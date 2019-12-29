kutoka idlelib.delegator agiza Delegator
kutoka idlelib.redirector agiza WidgetRedirector


kundi Percolator:

    eleza __init__(self, text):
        # XXX would be nice to inherit kutoka Delegator
        self.text = text
        self.redir = WidgetRedirector(text)
        self.top = self.bottom = Delegator(text)
        self.bottom.insert = self.redir.register("insert", self.insert)
        self.bottom.delete = self.redir.register("delete", self.delete)
        self.filters = []

    eleza close(self):
        wakati self.top ni sio self.bottom:
            self.removefilter(self.top)
        self.top = Tupu
        self.bottom.setdelegate(Tupu)
        self.bottom = Tupu
        self.redir.close()
        self.redir = Tupu
        self.text = Tupu

    eleza insert(self, index, chars, tags=Tupu):
        # Could go away ikiwa inheriting kutoka Delegator
        self.top.insert(index, chars, tags)

    eleza delete(self, index1, index2=Tupu):
        # Could go away ikiwa inheriting kutoka Delegator
        self.top.delete(index1, index2)

    eleza insertfilter(self, filter):
        # Perhaps rename to pushfilter()?
        assert isinstance(filter, Delegator)
        assert filter.delegate ni Tupu
        filter.setdelegate(self.top)
        self.top = filter

    eleza removefilter(self, filter):
        # XXX Perhaps should only support popfilter()?
        assert isinstance(filter, Delegator)
        assert filter.delegate ni sio Tupu
        f = self.top
        ikiwa f ni filter:
            self.top = filter.delegate
            filter.setdelegate(Tupu)
        isipokua:
            wakati f.delegate ni sio filter:
                assert f ni sio self.bottom
                f.resetcache()
                f = f.delegate
            f.setdelegate(filter.delegate)
            filter.setdelegate(Tupu)


eleza _percolator(parent):  # htest #
    agiza tkinter kama tk

    kundi Tracer(Delegator):
        eleza __init__(self, name):
            self.name = name
            Delegator.__init__(self, Tupu)

        eleza insert(self, *args):
            andika(self.name, ": insert", args)
            self.delegate.insert(*args)

        eleza delete(self, *args):
            andika(self.name, ": delete", args)
            self.delegate.delete(*args)

    box = tk.Toplevel(parent)
    box.title("Test Percolator")
    x, y = map(int, parent.geometry().split('+')[1:])
    box.geometry("+%d+%d" % (x, y + 175))
    text = tk.Text(box)
    p = Percolator(text)
    pin = p.insertfilter
    pout = p.removefilter
    t1 = Tracer("t1")
    t2 = Tracer("t2")

    eleza toggle1():
        (pin ikiwa var1.get() else pout)(t1)
    eleza toggle2():
        (pin ikiwa var2.get() else pout)(t2)

    text.pack()
    var1 = tk.IntVar(parent)
    cb1 = tk.Checkbutton(box, text="Tracer1", command=toggle1, variable=var1)
    cb1.pack()
    var2 = tk.IntVar(parent)
    cb2 = tk.Checkbutton(box, text="Tracer2", command=toggle2, variable=var2)
    cb2.pack()

ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_percolator', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_percolator)
