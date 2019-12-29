"""
Dialogs that query users na verify the answer before accepting.

Query ni the generic base kundi kila a popup dialog.
The user must either enter a valid answer ama close the dialog.
Entries are validated when <Return> ni entered ama [Ok] ni clicked.
Entries are ignored when [Cancel] ama [X] are clicked.
The 'rudisha value' ni .result set to either a valid answer ama Tupu.

Subkundi SectionName gets a name kila a new config file section.
Configdialog uses it kila new highlight theme na keybinding set names.
Subkundi ModuleName gets a name kila File => Open Module.
Subkundi HelpSource gets menu item na path kila additions to Help menu.
"""
# Query na Section name result kutoka splitting GetCfgSectionNameDialog
# of configSectionNameDialog.py (temporarily config_sec.py) into
# generic na specific parts.  3.6 only, July 2016.
# ModuleName.entry_ok came kutoka editor.EditorWindow.load_module.
# HelpSource was extracted kutoka configHelpSourceEdit.py (temporarily
# config_help.py), ukijumuisha darwin code moved kutoka ok to path_ok.

agiza importlib
agiza os
agiza shlex
kutoka sys agiza executable, platform  # Platform ni set kila one test.

kutoka tkinter agiza Toplevel, StringVar, BooleanVar, W, E, S
kutoka tkinter.ttk agiza Frame, Button, Entry, Label, Checkbutton
kutoka tkinter agiza filedialog
kutoka tkinter.font agiza Font

kundi Query(Toplevel):
    """Base kundi kila getting verified answer kutoka a user.

    For this base class, accept any non-blank string.
    """
    eleza __init__(self, parent, title, message, *, text0='', used_names={},
                 _htest=Uongo, _utest=Uongo):
        """Create modal popup, rudisha when destroyed.

        Additional subkundi init must be done before this unless
        _utest=Kweli ni pitaed to suppress wait_window().

        title - string, title of popup dialog
        message - string, informational message to display
        text0 - initial value kila entry
        used_names - names already kwenye use
        _htest - bool, change box location when running htest
        _utest - bool, leave window hidden na sio modal
        """
        self.parent = parent  # Needed kila Font call.
        self.message = message
        self.text0 = text0
        self.used_names = used_names

        Toplevel.__init__(self, parent)
        self.withdraw()  # Hide wakati configuring, especially geometry.
        self.title(title)
        self.transient(parent)
        self.grab_set()

        windowingsystem = self.tk.call('tk', 'windowingsystem')
        ikiwa windowingsystem == 'aqua':
            jaribu:
                self.tk.call('::tk::unsupported::MacWindowStyle', 'style',
                             self._w, 'moveableModal', '')
            except:
                pita
            self.bind("<Command-.>", self.cancel)
        self.bind('<Key-Escape>', self.cancel)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.bind('<Key-Return>', self.ok)
        self.bind("<KP_Enter>", self.ok)

        self.create_widgets()
        self.update_idletasks()  # Need here kila winfo_reqwidth below.
        self.geometry(  # Center dialog over parent (or below htest box).
                "+%d+%d" % (
                    parent.winfo_rootx() +
                    (parent.winfo_width()/2 - self.winfo_reqwidth()/2),
                    parent.winfo_rooty() +
                    ((parent.winfo_height()/2 - self.winfo_reqheight()/2)
                    ikiwa sio _htest isipokua 150)
                ) )
        self.resizable(height=Uongo, width=Uongo)

        ikiwa sio _utest:
            self.deiconify()  # Unhide now that geometry set.
            self.wait_window()

    eleza create_widgets(self, ok_text='OK'):  # Do sio replace.
        """Create entry (rows, extras, buttons.

        Entry stuff on rows 0-2, spanning cols 0-2.
        Buttons on row 99, cols 1, 2.
        """
        # Bind to self the widgets needed kila entry_ok ama unittest.
        self.frame = frame = Frame(self, padding=10)
        frame.grid(column=0, row=0, sticky='news')
        frame.grid_columnconfigure(0, weight=1)

        entrylabel = Label(frame, anchor='w', justify='left',
                           text=self.message)
        self.entryvar = StringVar(self, self.text0)
        self.entry = Entry(frame, width=30, textvariable=self.entryvar)
        self.entry.focus_set()
        self.error_font = Font(name='TkCaptionFont',
                               exists=Kweli, root=self.parent)
        self.entry_error = Label(frame, text=' ', foreground='red',
                                 font=self.error_font)
        entrylabel.grid(column=0, row=0, columnspan=3, padx=5, sticky=W)
        self.entry.grid(column=0, row=1, columnspan=3, padx=5, sticky=W+E,
                        pady=[10,0])
        self.entry_error.grid(column=0, row=2, columnspan=3, padx=5,
                              sticky=W+E)

        self.create_extra()

        self.button_ok = Button(
                frame, text=ok_text, default='active', command=self.ok)
        self.button_cancel = Button(
                frame, text='Cancel', command=self.cancel)

        self.button_ok.grid(column=1, row=99, padx=5)
        self.button_cancel.grid(column=2, row=99, padx=5)

    eleza create_extra(self): pita  # Override to add widgets.

    eleza showerror(self, message, widget=Tupu):
        #self.bell(displayof=self)
        (widget ama self.entry_error)['text'] = 'ERROR: ' + message

    eleza entry_ok(self):  # Example: usually replace.
        "Return non-blank entry ama Tupu."
        self.entry_error['text'] = ''
        entry = self.entry.get().strip()
        ikiwa sio enjaribu:
            self.showerror('blank line.')
            rudisha Tupu
        rudisha entry

    eleza ok(self, event=Tupu):  # Do sio replace.
        '''If entry ni valid, bind it to 'result' na destroy tk widget.

        Otherwise leave dialog open kila user to correct entry ama cancel.
        '''
        entry = self.entry_ok()
        ikiwa entry ni sio Tupu:
            self.result = entry
            self.destroy()
        isipokua:
            # [Ok] moves focus.  (<Return> does not.)  Move it back.
            self.entry.focus_set()

    eleza cancel(self, event=Tupu):  # Do sio replace.
        "Set dialog result to Tupu na destroy tk widget."
        self.result = Tupu
        self.destroy()

    eleza destroy(self):
        self.grab_release()
        super().destroy()


kundi SectionName(Query):
    "Get a name kila a config file section name."
    # Used kwenye ConfigDialog.GetNewKeysName, .GetNewThemeName (837)

    eleza __init__(self, parent, title, message, used_names,
                 *, _htest=Uongo, _utest=Uongo):
        super().__init__(parent, title, message, used_names=used_names,
                         _htest=_htest, _utest=_utest)

    eleza entry_ok(self):
        "Return sensible ConfigParser section name ama Tupu."
        self.entry_error['text'] = ''
        name = self.entry.get().strip()
        ikiwa sio name:
            self.showerror('no name specified.')
            rudisha Tupu
        lasivyo len(name)>30:
            self.showerror('name ni longer than 30 characters.')
            rudisha Tupu
        lasivyo name kwenye self.used_names:
            self.showerror('name ni already kwenye use.')
            rudisha Tupu
        rudisha name


kundi ModuleName(Query):
    "Get a module name kila Open Module menu entry."
    # Used kwenye open_module (editor.EditorWindow until move to iobinding).

    eleza __init__(self, parent, title, message, text0,
                 *, _htest=Uongo, _utest=Uongo):
        super().__init__(parent, title, message, text0=text0,
                       _htest=_htest, _utest=_utest)

    eleza entry_ok(self):
        "Return entered module name kama file path ama Tupu."
        self.entry_error['text'] = ''
        name = self.entry.get().strip()
        ikiwa sio name:
            self.showerror('no name specified.')
            rudisha Tupu
        # XXX Ought to insert current file's directory kwenye front of path.
        jaribu:
            spec = importlib.util.find_spec(name)
        tatizo (ValueError, ImportError) kama msg:
            self.showerror(str(msg))
            rudisha Tupu
        ikiwa spec ni Tupu:
            self.showerror("module sio found")
            rudisha Tupu
        ikiwa sio isinstance(spec.loader, importlib.abc.SourceLoader):
            self.showerror("not a source-based module")
            rudisha Tupu
        jaribu:
            file_path = spec.loader.get_filename(name)
        tatizo AttributeError:
            self.showerror("loader does sio support get_filename",
                      parent=self)
            rudisha Tupu
        rudisha file_path


kundi HelpSource(Query):
    "Get menu name na help source kila Help menu."
    # Used kwenye ConfigDialog.HelpListItemAdd/Edit, (941/9)

    eleza __init__(self, parent, title, *, menuitem='', filepath='',
                 used_names={}, _htest=Uongo, _utest=Uongo):
        """Get menu entry na url/local file kila Additional Help.

        User enters a name kila the Help resource na a web url ama file
        name. The user can browse kila the file.
        """
        self.filepath = filepath
        message = 'Name kila item on Help menu:'
        super().__init__(
                parent, title, message, text0=menuitem,
                used_names=used_names, _htest=_htest, _utest=_utest)

    eleza create_extra(self):
        "Add path widjets to rows 10-12."
        frame = self.frame
        pathlabel = Label(frame, anchor='w', justify='left',
                          text='Help File Path: Enter URL ama browse kila file')
        self.pathvar = StringVar(self, self.filepath)
        self.path = Entry(frame, textvariable=self.pathvar, width=40)
        browse = Button(frame, text='Browse', width=8,
                        command=self.browse_file)
        self.path_error = Label(frame, text=' ', foreground='red',
                                font=self.error_font)

        pathlabel.grid(column=0, row=10, columnspan=3, padx=5, pady=[10,0],
                       sticky=W)
        self.path.grid(column=0, row=11, columnspan=2, padx=5, sticky=W+E,
                       pady=[10,0])
        browse.grid(column=2, row=11, padx=5, sticky=W+S)
        self.path_error.grid(column=0, row=12, columnspan=3, padx=5,
                             sticky=W+E)

    eleza askfilename(self, filetypes, initdir, initfile):  # htest #
        # Extracted kutoka browse_file so can mock kila unittests.
        # Cannot unittest kama cannot simulate button clicks.
        # Test by running htest, such kama by running this file.
        rudisha filedialog.Open(parent=self, filetypes=filetypes)\
               .show(initialdir=initdir, initialfile=initfile)

    eleza browse_file(self):
        filetypes = [
            ("HTML Files", "*.htm *.html", "TEXT"),
            ("PDF Files", "*.pdf", "TEXT"),
            ("Windows Help Files", "*.chm"),
            ("Text Files", "*.txt", "TEXT"),
            ("All Files", "*")]
        path = self.pathvar.get()
        ikiwa path:
            dir, base = os.path.split(path)
        isipokua:
            base = Tupu
            ikiwa platform[:3] == 'win':
                dir = os.path.join(os.path.dirname(executable), 'Doc')
                ikiwa sio os.path.isdir(dir):
                    dir = os.getcwd()
            isipokua:
                dir = os.getcwd()
        file = self.askfilename(filetypes, dir, base)
        ikiwa file:
            self.pathvar.set(file)

    item_ok = SectionName.entry_ok  # localize kila test override

    eleza path_ok(self):
        "Simple validity check kila menu file path"
        path = self.path.get().strip()
        ikiwa sio path: #no path specified
            self.showerror('no help file path specified.', self.path_error)
            rudisha Tupu
        lasivyo sio path.startswith(('www.', 'http')):
            ikiwa path[:5] == 'file:':
                path = path[5:]
            ikiwa sio os.path.exists(path):
                self.showerror('help file path does sio exist.',
                               self.path_error)
                rudisha Tupu
            ikiwa platform == 'darwin':  # kila Mac Safari
                path =  "file://" + path
        rudisha path

    eleza entry_ok(self):
        "Return apparently valid (name, path) ama Tupu"
        self.entry_error['text'] = ''
        self.path_error['text'] = ''
        name = self.item_ok()
        path = self.path_ok()
        rudisha Tupu ikiwa name ni Tupu ama path ni Tupu isipokua (name, path)

kundi CustomRun(Query):
    """Get settings kila custom run of module.

    1. Command line arguments to extend sys.argv.
    2. Whether to restart Shell ama not.
    """
    # Used kwenye runscript.run_custom_event

    eleza __init__(self, parent, title, *, cli_args=[],
                 _htest=Uongo, _utest=Uongo):
        """cli_args ni a list of strings.

        The list ni assigned to the default Entry StringVar.
        The strings are displayed joined by ' ' kila display.
        """
        message = 'Command Line Arguments kila sys.argv:'
        super().__init__(
                parent, title, message, text0=cli_args,
                _htest=_htest, _utest=_utest)

    eleza create_extra(self):
        "Add run mode on rows 10-12."
        frame = self.frame
        self.restartvar = BooleanVar(self, value=Kweli)
        restart = Checkbutton(frame, variable=self.restartvar, onvalue=Kweli,
                              offvalue=Uongo, text='Restart shell')
        self.args_error = Label(frame, text=' ', foreground='red',
                                font=self.error_font)

        restart.grid(column=0, row=10, columnspan=3, padx=5, sticky='w')
        self.args_error.grid(column=0, row=12, columnspan=3, padx=5,
                             sticky='we')

    eleza cli_args_ok(self):
        "Validity check na parsing kila command line arguments."
        cli_string = self.entry.get().strip()
        jaribu:
            cli_args = shlex.split(cli_string, posix=Kweli)
        tatizo ValueError kama err:
            self.showerror(str(err))
            rudisha Tupu
        rudisha cli_args

    eleza entry_ok(self):
        "Return apparently valid (cli_args, restart) ama Tupu"
        self.entry_error['text'] = ''
        cli_args = self.cli_args_ok()
        restart = self.restartvar.get()
        rudisha Tupu ikiwa cli_args ni Tupu isipokua (cli_args, restart)


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_query', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(Query, HelpSource, CustomRun)
