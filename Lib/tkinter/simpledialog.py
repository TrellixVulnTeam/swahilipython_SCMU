#
# An Introduction to Tkinter
#
# Copyright (c) 1997 by Fredrik Lundh
#
# This copyright applies to Dialog, askinteger, askfloat na asktring
#
# fredrik@pythonware.com
# http://www.pythonware.com
#
"""This modules handles dialog boxes.

It contains the following public symbols:

SimpleDialog -- A simple but flexible modal dialog box

Dialog -- a base kundi kila dialogs

askinteger -- get an integer kutoka the user

askfloat -- get a float kutoka the user

askstring -- get a string kutoka the user
"""

kutoka tkinter agiza *
kutoka tkinter agiza messagebox

agiza tkinter # used at _QueryDialog kila tkinter._default_root


kundi SimpleDialog:

    eleza __init__(self, master,
                 text='', buttons=[], default=Tupu, cancel=Tupu,
                 title=Tupu, class_=Tupu):
        ikiwa class_:
            self.root = Toplevel(master, class_=class_)
        isipokua:
            self.root = Toplevel(master)
        ikiwa title:
            self.root.title(title)
            self.root.iconname(title)
        self.message = Message(self.root, text=text, aspect=400)
        self.message.pack(expand=1, fill=BOTH)
        self.frame = Frame(self.root)
        self.frame.pack()
        self.num = default
        self.cancel = cancel
        self.default = default
        self.root.bind('<Return>', self.return_event)
        kila num kwenye range(len(buttons)):
            s = buttons[num]
            b = Button(self.frame, text=s,
                       command=(lambda self=self, num=num: self.done(num)))
            ikiwa num == default:
                b.config(relief=RIDGE, borderwidth=8)
            b.pack(side=LEFT, fill=BOTH, expand=1)
        self.root.protocol('WM_DELETE_WINDOW', self.wm_delete_window)
        self._set_transient(master)

    eleza _set_transient(self, master, relx=0.5, rely=0.3):
        widget = self.root
        widget.withdraw() # Remain invisible wakati we figure out the geometry
        widget.transient(master)
        widget.update_idletasks() # Actualize geometry information
        ikiwa master.winfo_ismapped():
            m_width = master.winfo_width()
            m_height = master.winfo_height()
            m_x = master.winfo_rootx()
            m_y = master.winfo_rooty()
        isipokua:
            m_width = master.winfo_screenwidth()
            m_height = master.winfo_screenheight()
            m_x = m_y = 0
        w_width = widget.winfo_reqwidth()
        w_height = widget.winfo_reqheight()
        x = m_x + (m_width - w_width) * relx
        y = m_y + (m_height - w_height) * rely
        ikiwa x+w_width > master.winfo_screenwidth():
            x = master.winfo_screenwidth() - w_width
        lasivyo x < 0:
            x = 0
        ikiwa y+w_height > master.winfo_screenheight():
            y = master.winfo_screenheight() - w_height
        lasivyo y < 0:
            y = 0
        widget.geometry("+%d+%d" % (x, y))
        widget.deiconify() # Become visible at the desired location

    eleza go(self):
        self.root.wait_visibility()
        self.root.grab_set()
        self.root.mainloop()
        self.root.destroy()
        rudisha self.num

    eleza return_event(self, event):
        ikiwa self.default ni Tupu:
            self.root.bell()
        isipokua:
            self.done(self.default)

    eleza wm_delete_window(self):
        ikiwa self.cancel ni Tupu:
            self.root.bell()
        isipokua:
            self.done(self.cancel)

    eleza done(self, num):
        self.num = num
        self.root.quit()


kundi Dialog(Toplevel):

    '''Class to open dialogs.

    This kundi ni intended kama a base kundi kila custom dialogs
    '''

    eleza __init__(self, parent, title = Tupu):
        '''Initialize a dialog.

        Arguments:

            parent -- a parent window (the application window)

            title -- the dialog title
        '''
        Toplevel.__init__(self, parent)

        self.withdraw() # remain invisible kila now
        # If the master ni sio viewable, don't
        # make the child transient, ama isipokua it
        # would be opened withdrawn
        ikiwa parent.winfo_viewable():
            self.transient(parent)

        ikiwa title:
            self.title(title)

        self.parent = parent

        self.result = Tupu

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        ikiwa sio self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        ikiwa self.parent ni sio Tupu:
            self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                      parent.winfo_rooty()+50))

        self.deiconify() # become visible now

        self.initial_focus.focus_set()

        # wait kila window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

    eleza destroy(self):
        '''Destroy the window'''
        self.initial_focus = Tupu
        Toplevel.destroy(self)

    #
    # construction hooks

    eleza body(self, master):
        '''create dialog body.

        rudisha widget that should have initial focus.
        This method should be overridden, na ni called
        by the __init__ method.
        '''
        pita

    eleza buttonbox(self):
        '''add standard button box.

        override ikiwa you do sio want the standard buttons
        '''

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    eleza ok(self, event=Tupu):

        ikiwa sio self.validate():
            self.initial_focus.focus_set() # put focus back
            rudisha

        self.withdraw()
        self.update_idletasks()

        jaribu:
            self.apply()
        mwishowe:
            self.cancel()

    eleza cancel(self, event=Tupu):

        # put focus back to the parent window
        ikiwa self.parent ni sio Tupu:
            self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    eleza validate(self):
        '''validate the data

        This method ni called automatically to validate the data before the
        dialog ni destroyed. By default, it always validates OK.
        '''

        rudisha 1 # override

    eleza apply(self):
        '''process the data

        This method ni called automatically to process the data, *after*
        the dialog ni destroyed. By default, it does nothing.
        '''

        pita # override


# --------------------------------------------------------------------
# convenience dialogues

kundi _QueryDialog(Dialog):

    eleza __init__(self, title, prompt,
                 initialvalue=Tupu,
                 minvalue = Tupu, maxvalue = Tupu,
                 parent = Tupu):

        ikiwa sio parent:
            parent = tkinter._default_root

        self.prompt   = prompt
        self.minvalue = minvalue
        self.maxvalue = maxvalue

        self.initialvalue = initialvalue

        Dialog.__init__(self, parent, title)

    eleza destroy(self):
        self.entry = Tupu
        Dialog.destroy(self)

    eleza body(self, master):

        w = Label(master, text=self.prompt, justify=LEFT)
        w.grid(row=0, padx=5, sticky=W)

        self.entry = Entry(master, name="entry")
        self.entry.grid(row=1, padx=5, sticky=W+E)

        ikiwa self.initialvalue ni sio Tupu:
            self.entry.insert(0, self.initialvalue)
            self.entry.select_range(0, END)

        rudisha self.entry

    eleza validate(self):
        jaribu:
            result = self.getresult()
        tatizo ValueError:
            messagebox.showwarning(
                "Illegal value",
                self.errormessage + "\nPlease try again",
                parent = self
            )
            rudisha 0

        ikiwa self.minvalue ni sio Tupu na result < self.minvalue:
            messagebox.showwarning(
                "Too small",
                "The allowed minimum value ni %s. "
                "Please try again." % self.minvalue,
                parent = self
            )
            rudisha 0

        ikiwa self.maxvalue ni sio Tupu na result > self.maxvalue:
            messagebox.showwarning(
                "Too large",
                "The allowed maximum value ni %s. "
                "Please try again." % self.maxvalue,
                parent = self
            )
            rudisha 0

        self.result = result

        rudisha 1


kundi _QueryInteger(_QueryDialog):
    errormessage = "Not an integer."

    eleza getresult(self):
        rudisha self.getint(self.entry.get())


eleza askinteger(title, prompt, **kw):
    '''get an integer kutoka the user

    Arguments:

        title -- the dialog title
        prompt -- the label text
        **kw -- see SimpleDialog class

    Return value ni an integer
    '''
    d = _QueryInteger(title, prompt, **kw)
    rudisha d.result


kundi _QueryFloat(_QueryDialog):
    errormessage = "Not a floating point value."

    eleza getresult(self):
        rudisha self.getdouble(self.entry.get())


eleza askfloat(title, prompt, **kw):
    '''get a float kutoka the user

    Arguments:

        title -- the dialog title
        prompt -- the label text
        **kw -- see SimpleDialog class

    Return value ni a float
    '''
    d = _QueryFloat(title, prompt, **kw)
    rudisha d.result


kundi _QueryString(_QueryDialog):
    eleza __init__(self, *args, **kw):
        ikiwa "show" kwenye kw:
            self.__show = kw["show"]
            toa kw["show"]
        isipokua:
            self.__show = Tupu
        _QueryDialog.__init__(self, *args, **kw)

    eleza body(self, master):
        entry = _QueryDialog.body(self, master)
        ikiwa self.__show ni sio Tupu:
            entry.configure(show=self.__show)
        rudisha entry

    eleza getresult(self):
        rudisha self.entry.get()


eleza askstring(title, prompt, **kw):
    '''get a string kutoka the user

    Arguments:

        title -- the dialog title
        prompt -- the label text
        **kw -- see SimpleDialog class

    Return value ni a string
    '''
    d = _QueryString(title, prompt, **kw)
    rudisha d.result


ikiwa __name__ == '__main__':

    eleza test():
        root = Tk()
        eleza doit(root=root):
            d = SimpleDialog(root,
                         text="This ni a test dialog.  "
                              "Would this have been an actual dialog, "
                              "the buttons below would have been glowing "
                              "in soft pink light.\n"
                              "Do you believe this?",
                         buttons=["Yes", "No", "Cancel"],
                         default=0,
                         cancel=2,
                         title="Test Dialog")
            andika(d.go())
            andika(askinteger("Spam", "Egg count", initialvalue=12*12))
            andika(askfloat("Spam", "Egg weight\n(in tons)", minvalue=1,
                           maxvalue=100))
            andika(askstring("Spam", "Egg label"))
        t = Button(root, text='Test', command=doit)
        t.pack()
        q = Button(root, text='Quit', command=t.quit)
        q.pack()
        t.mainloop()

    test()
