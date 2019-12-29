'''Define SearchDialogBase used by Search, Replace, na Grep dialogs.'''

kutoka tkinter agiza Toplevel
kutoka tkinter.ttk agiza Frame, Entry, Label, Button, Checkbutton, Radiobutton


kundi SearchDialogBase:
    '''Create most of a 3 ama 4 row, 3 column search dialog.

    The left na wide middle column contain:
    1 ama 2 labeled text entry lines (make_entry, create_entries);
    a row of standard Checkbuttons (make_frame, create_option_buttons),
    each of which corresponds to a search engine Variable;
    a row of dialog-specific Check/Radiobuttons (create_other_buttons).

    The narrow right column contains command buttons
    (make_button, create_command_buttons).
    These are bound to functions that execute the command.

    Except kila command buttons, this base kundi ni sio limited to items
    common to all three subclasses.  Rather, it ni the Find dialog minus
    the "Find Next" command, its execution function, na the
    default_command attribute needed kwenye create_widgets. The other
    dialogs override attributes na methods, the latter to replace and
    add widgets.
    '''

    title = "Search Dialog"  # replace kwenye subclasses
    icon = "Search"
    needwrapbutton = 1  # haiko kwenye Find kwenye Files

    eleza __init__(self, root, engine):
        '''Initialize root, engine, na top attributes.

        top (level widget): set kwenye create_widgets() called kutoka open().
        text (Text searched): set kwenye open(), only used kwenye subclasses().
        ent (ry): created kwenye make_entry() called kutoka create_entry().
        row (of grid): 0 kwenye create_widgets(), +1 kwenye make_entry/frame().
        default_command: set kwenye subclasses, used kwenye create_widgets().

        title (of dialog): kundi attribute, override kwenye subclasses.
        icon (of dialog): ditto, use unclear ikiwa cannot minimize dialog.
        '''
        self.root = root
        self.bell = root.bell
        self.engine = engine
        self.top = Tupu

    eleza open(self, text, searchphrase=Tupu):
        "Make dialog visible on top of others na ready to use."
        self.text = text
        ikiwa sio self.top:
            self.create_widgets()
        isipokua:
            self.top.deiconify()
            self.top.tkashiria()
        self.top.transient(text.winfo_toplevel())
        ikiwa searchphrase:
            self.ent.delete(0,"end")
            self.ent.insert("end",searchphrase)
        self.ent.focus_set()
        self.ent.selection_range(0, "end")
        self.ent.icursor(0)
        self.top.grab_set()

    eleza close(self, event=Tupu):
        "Put dialog away kila later use."
        ikiwa self.top:
            self.top.grab_release()
            self.top.transient('')
            self.top.withdraw()

    eleza create_widgets(self):
        '''Create basic 3 row x 3 col search (find) dialog.

        Other dialogs override subsidiary create_x methods kama needed.
        Replace na Find-in-Files add another entry row.
        '''
        top = Toplevel(self.root)
        top.bind("<Return>", self.default_command)
        top.bind("<Escape>", self.close)
        top.protocol("WM_DELETE_WINDOW", self.close)
        top.wm_title(self.title)
        top.wm_iconname(self.icon)
        self.top = top

        self.row = 0
        self.top.grid_columnconfigure(0, pad=2, weight=0)
        self.top.grid_columnconfigure(1, pad=2, minsize=100, weight=100)

        self.create_entries()  # row 0 (and maybe 1), cols 0, 1
        self.create_option_buttons()  # next row, cols 0, 1
        self.create_other_buttons()  # next row, cols 0, 1
        self.create_command_buttons()  # col 2, all rows

    eleza make_entry(self, label_text, var):
        '''Return (entry, label), .

        entry - gridded labeled Entry kila text entry.
        label - Label widget, rudishaed kila testing.
        '''
        label = Label(self.top, text=label_text)
        label.grid(row=self.row, column=0, sticky="nw")
        entry = Entry(self.top, textvariable=var, exportselection=0)
        entry.grid(row=self.row, column=1, sticky="nwe")
        self.row = self.row + 1
        rudisha entry, label

    eleza create_entries(self):
        "Create one ama more entry lines ukijumuisha make_entry."
        self.ent = self.make_entry("Find:", self.engine.patvar)[0]

    eleza make_frame(self,labeltext=Tupu):
        '''Return (frame, label).

        frame - gridded labeled Frame kila option ama other buttons.
        label - Label widget, rudishaed kila testing.
        '''
        ikiwa labeltext:
            label = Label(self.top, text=labeltext)
            label.grid(row=self.row, column=0, sticky="nw")
        isipokua:
            label = ''
        frame = Frame(self.top)
        frame.grid(row=self.row, column=1, columnspan=1, sticky="nwe")
        self.row = self.row + 1
        rudisha frame, label

    eleza create_option_buttons(self):
        '''Return (filled frame, options) kila testing.

        Options ni a list of searchengine booleanvar, label pairs.
        A gridded frame kutoka make_frame ni filled ukijumuisha a Checkbutton
        kila each pair, bound to the var, ukijumuisha the corresponding label.
        '''
        frame = self.make_frame("Options")[0]
        engine = self.engine
        options = [(engine.revar, "Regular expression"),
                   (engine.casevar, "Match case"),
                   (engine.wordvar, "Whole word")]
        ikiwa self.needwrapbutton:
            options.append((engine.wrapvar, "Wrap around"))
        kila var, label kwenye options:
            btn = Checkbutton(frame, variable=var, text=label)
            btn.pack(side="left", fill="both")
        rudisha frame, options

    eleza create_other_buttons(self):
        '''Return (frame, others) kila testing.

        Others ni a list of value, label pairs.
        A gridded frame kutoka make_frame ni filled ukijumuisha radio buttons.
        '''
        frame = self.make_frame("Direction")[0]
        var = self.engine.backvar
        others = [(1, 'Up'), (0, 'Down')]
        kila val, label kwenye others:
            btn = Radiobutton(frame, variable=var, value=val, text=label)
            btn.pack(side="left", fill="both")
        rudisha frame, others

    eleza make_button(self, label, command, isdef=0):
        "Return command button gridded kwenye command frame."
        b = Button(self.buttonframe,
                   text=label, command=command,
                   default=iseleza na "active" ama "normal")
        cols,rows=self.buttonframe.grid_size()
        b.grid(pady=1,row=rows,column=0,sticky="ew")
        self.buttonframe.grid(rowspan=rows+1)
        rudisha b

    eleza create_command_buttons(self):
        "Place buttons kwenye vertical command frame gridded on right."
        f = self.buttonframe = Frame(self.top)
        f.grid(row=0,column=2,padx=2,pady=2,ipadx=2,ipady=2)

        b = self.make_button("Close", self.close)
        b.lower()


kundi _searchbase(SearchDialogBase):  # htest #
    "Create auto-opening dialog ukijumuisha no text connection."

    eleza __init__(self, parent):
        agiza re
        kutoka idlelib agiza searchengine

        self.root = parent
        self.engine = searchengine.get(parent)
        self.create_widgets()
        andika(parent.geometry())
        width,height, x,y = list(map(int, re.split('[x+]', parent.geometry())))
        self.top.geometry("+%d+%d" % (x + 40, y + 175))

    eleza default_command(self, dummy): pita


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_searchbase', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_searchbase)
