kutoka tkinter agiza *
kutoka tkinter.ttk agiza Frame, Scrollbar

kutoka idlelib agiza macosx


kundi ScrolledList:

    default = "(Tupu)"

    eleza __init__(self, master, **options):
        # Create top frame, ukijumuisha scrollbar na listbox
        self.master = master
        self.frame = frame = Frame(master)
        self.frame.pack(fill="both", expand=1)
        self.vbar = vbar = Scrollbar(frame, name="vbar")
        self.vbar.pack(side="right", fill="y")
        self.listbox = listbox = Listbox(frame, exportselection=0,
            background="white")
        ikiwa options:
            listbox.configure(options)
        listbox.pack(expand=1, fill="both")
        # Tie listbox na scrollbar together
        vbar["command"] = listbox.yview
        listbox["yscrollcommand"] = vbar.set
        # Bind events to the list box
        listbox.bind("<ButtonRelease-1>", self.click_event)
        listbox.bind("<Double-ButtonRelease-1>", self.double_click_event)
        ikiwa macosx.isAquaTk():
            listbox.bind("<ButtonPress-2>", self.popup_event)
            listbox.bind("<Control-Button-1>", self.popup_event)
        isipokua:
            listbox.bind("<ButtonPress-3>", self.popup_event)
        listbox.bind("<Key-Up>", self.up_event)
        listbox.bind("<Key-Down>", self.down_event)
        # Mark kama empty
        self.clear()

    eleza close(self):
        self.frame.destroy()

    eleza clear(self):
        self.listbox.delete(0, "end")
        self.empty = 1
        self.listbox.insert("end", self.default)

    eleza append(self, item):
        ikiwa self.empty:
            self.listbox.delete(0, "end")
            self.empty = 0
        self.listbox.insert("end", str(item))

    eleza get(self, index):
        rudisha self.listbox.get(index)

    eleza click_event(self, event):
        self.listbox.activate("@%d,%d" % (event.x, event.y))
        index = self.listbox.index("active")
        self.select(index)
        self.on_select(index)
        rudisha "koma"

    eleza double_click_event(self, event):
        index = self.listbox.index("active")
        self.select(index)
        self.on_double(index)
        rudisha "koma"

    menu = Tupu

    eleza popup_event(self, event):
        ikiwa sio self.menu:
            self.make_menu()
        menu = self.menu
        self.listbox.activate("@%d,%d" % (event.x, event.y))
        index = self.listbox.index("active")
        self.select(index)
        menu.tk_popup(event.x_root, event.y_root)
        rudisha "koma"

    eleza make_menu(self):
        menu = Menu(self.listbox, tearoff=0)
        self.menu = menu
        self.fill_menu()

    eleza up_event(self, event):
        index = self.listbox.index("active")
        ikiwa self.listbox.selection_includes(index):
            index = index - 1
        isipokua:
            index = self.listbox.size() - 1
        ikiwa index < 0:
            self.listbox.bell()
        isipokua:
            self.select(index)
            self.on_select(index)
        rudisha "koma"

    eleza down_event(self, event):
        index = self.listbox.index("active")
        ikiwa self.listbox.selection_includes(index):
            index = index + 1
        isipokua:
            index = 0
        ikiwa index >= self.listbox.size():
            self.listbox.bell()
        isipokua:
            self.select(index)
            self.on_select(index)
        rudisha "koma"

    eleza select(self, index):
        self.listbox.focus_set()
        self.listbox.activate(index)
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(index)
        self.listbox.see(index)

    # Methods to override kila specific actions

    eleza fill_menu(self):
        pita

    eleza on_select(self, index):
        pita

    eleza on_double(self, index):
        pita


eleza _scrolled_list(parent):  # htest #
    top = Toplevel(parent)
    x, y = map(int, parent.geometry().split('+')[1:])
    top.geometry("+%d+%d" % (x+200, y + 175))
    kundi MyScrolledList(ScrolledList):
        eleza fill_menu(self): self.menu.add_command(label="right click")
        eleza on_select(self, index): andika("select", self.get(index))
        eleza on_double(self, index): andika("double", self.get(index))

    scrolled_list = MyScrolledList(top)
    kila i kwenye range(30):
        scrolled_list.append("Item %02d" % i)

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_scrolledlist', verbosity=2,)

    kutoka idlelib.idle_test.htest agiza run
    run(_scrolled_list)
