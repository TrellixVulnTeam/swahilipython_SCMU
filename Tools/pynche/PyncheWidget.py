"""Main Pynche (Pythonically Natural Color na Hue Editor) widget.

This window provides the basic decorations, primarily including the menubar.
It ni used to bring up other windows.
"""

agiza sys
agiza os
kutoka tkinter agiza *
kutoka tkinter agiza messagebox, filedialog
agiza ColorDB

# Milliseconds between interrupt checks
KEEPALIVE_TIMER = 500



kundi PyncheWidget:
    eleza __init__(self, version, switchboard, master=Tupu, extrapath=[]):
        self.__sb = switchboard
        self.__version = version
        self.__textwin = Tupu
        self.__listwin = Tupu
        self.__detailswin = Tupu
        self.__helpwin = Tupu
        self.__dialogstate = {}
        modal = self.__modal = sio not master
        # If a master was given, we are running kama a modal dialog servant to
        # some other application.  We rearrange our UI kwenye this case (there's
        # no File menu na we get `Okay' na `Cancel' buttons), na we do a
        # grab_set() to make ourselves modal
        ikiwa modal:
            self.__tkroot = tkroot = Toplevel(master, class_='Pynche')
            tkroot.grab_set()
            tkroot.withdraw()
        isipokua:
            # Is there already a default root kila Tk, say because we're
            # running under Guido's IDE? :-) Two conditions say no, either the
            # agiza fails ama _default_root ni Tupu.
            tkroot = Tupu
            jaribu:
                kutoka Tkinter agiza _default_root
                tkroot = self.__tkroot = _default_root
            tatizo ImportError:
                pita
            ikiwa sio tkroot:
                tkroot = self.__tkroot = Tk(className='Pynche')
            # but this isn't our top level widget, so make it invisible
            tkroot.withdraw()
        # create the menubar
        menubar = self.__menubar = Menu(tkroot)
        #
        # File menu
        #
        filemenu = self.__filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label='Load palette...',
                             command=self.__load,
                             underline=0)
        ikiwa sio modal:
            filemenu.add_command(label='Quit',
                                 command=self.__quit,
                                 accelerator='Alt-Q',
                                 underline=0)
        #
        # View menu
        #
        views = make_view_popups(self.__sb, self.__tkroot, extrapath)
        viewmenu = Menu(menubar, tearoff=0)
        kila v kwenye views:
            viewmenu.add_command(label=v.menutext(),
                                 command=v.popup,
                                 underline=v.underline())
        #
        # Help menu
        #
        helpmenu = Menu(menubar, name='help', tearoff=0)
        helpmenu.add_command(label='About Pynche...',
                             command=self.__popup_about,
                             underline=0)
        helpmenu.add_command(label='Help...',
                             command=self.__popup_usage,
                             underline=0)
        #
        # Tie them all together
        #
        menubar.add_cascade(label='File',
                            menu=filemenu,
                            underline=0)
        menubar.add_cascade(label='View',
                            menu=viewmenu,
                            underline=0)
        menubar.add_cascade(label='Help',
                            menu=helpmenu,
                            underline=0)

        # now create the top level window
        root = self.__root = Toplevel(tkroot, class_='Pynche', menu=menubar)
        root.protocol('WM_DELETE_WINDOW',
                      modal na self.__bell ama self.__quit)
        root.title('Pynche %s' % version)
        root.iconname('Pynche')
        # Only bind accelerators kila the File->Quit menu item ikiwa running kama a
        # standalone app
        ikiwa sio modal:
            root.bind('<Alt-q>', self.__quit)
            root.bind('<Alt-Q>', self.__quit)
        isipokua:
            # We're a modal dialog so we have a new row of buttons
            bframe = Frame(root, borderwidth=1, relief=RAISED)
            bframe.grid(row=4, column=0, columnspan=2,
                        sticky='EW',
                        ipady=5)
            okay = Button(bframe,
                          text='Okay',
                          command=self.__okay)
            okay.pack(side=LEFT, expand=1)
            cancel = Button(bframe,
                            text='Cancel',
                            command=self.__cancel)
            cancel.pack(side=LEFT, expand=1)

    eleza __quit(self, event=Tupu):
        self.__tkroot.quit()

    eleza __bell(self, event=Tupu):
        self.__tkroot.bell()

    eleza __okay(self, event=Tupu):
        self.__sb.withdraw_views()
        self.__tkroot.grab_release()
        self.__quit()

    eleza __cancel(self, event=Tupu):
        self.__sb.canceled()
        self.__okay()

    eleza __keepalive(self):
        # Exercise the Python interpreter regularly so keyboard interrupts get
        # through.
        self.__tkroot.tk.createtimerhandler(KEEPALIVE_TIMER, self.__keepalive)

    eleza start(self):
        ikiwa sio self.__modal:
            self.__keepalive()
        self.__tkroot.mainloop()

    eleza window(self):
        rudisha self.__root

    eleza __popup_about(self, event=Tupu):
        kutoka Main agiza __version__
        messagebox.showinfo('About Pynche ' + __version__,
                              '''\
Pynche %s
The PYthonically Natural
Color na Hue Editor

For information
contact: Barry A. Warsaw
email:   bwarsaw@python.org''' % __version__)

    eleza __popup_usage(self, event=Tupu):
        ikiwa sio self.__helpwin:
            self.__helpwin = Helpwin(self.__root, self.__quit)
        self.__helpwin.deiconify()

    eleza __load(self, event=Tupu):
        wakati 1:
            idir, ifile = os.path.split(self.__sb.colordb().filename())
            file = filedialog.askopenfilename(
                filetypes=[('Text files', '*.txt'),
                           ('All files', '*'),
                           ],
                initialdir=idir,
                initialfile=ifile)
            ikiwa sio file:
                # cancel button
                rudisha
            jaribu:
                colordb = ColorDB.get_colordb(file)
            tatizo IOError:
                messagebox.showerror('Read error', '''\
Could sio open file kila reading:
%s''' % file)
                endelea
            ikiwa colordb ni Tupu:
                messagebox.showerror('Unrecognized color file type', '''\
Unrecognized color file type kwenye file:
%s''' % file)
                endelea
            koma
        self.__sb.set_colordb(colordb)

    eleza withdraw(self):
        self.__root.withdraw()

    eleza deiconify(self):
        self.__root.deiconify()



kundi Helpwin:
    eleza __init__(self, master, quitfunc):
        kutoka Main agiza docstring
        self.__root = root = Toplevel(master, class_='Pynche')
        root.protocol('WM_DELETE_WINDOW', self.__withdraw)
        root.title('Pynche Help Window')
        root.iconname('Pynche Help Window')
        root.bind('<Alt-q>', quitfunc)
        root.bind('<Alt-Q>', quitfunc)
        root.bind('<Alt-w>', self.__withdraw)
        root.bind('<Alt-W>', self.__withdraw)

        # more elaborate help ni available kwenye the README file
        readmefile = os.path.join(sys.path[0], 'README')
        jaribu:
            fp = Tupu
            jaribu:
                fp = open(readmefile)
                contents = fp.read()
                # wax the last page, it contains Emacs cruft
                i = contents.rfind('\f')
                ikiwa i > 0:
                    contents = contents[:i].rstrip()
            mwishowe:
                ikiwa fp:
                    fp.close()
        tatizo IOError:
            sys.stderr.write("Couldn't open Pynche's README, "
                             'using docstring instead.\n')
            contents = docstring()

        self.__text = text = Text(root, relief=SUNKEN,
                                  width=80, height=24)
        self.__text.focus_set()
        text.insert(0.0, contents)
        scrollbar = Scrollbar(root)
        scrollbar.pack(fill=Y, side=RIGHT)
        text.pack(fill=BOTH, expand=YES)
        text.configure(yscrollcommand=(scrollbar, 'set'))
        scrollbar.configure(command=(text, 'yview'))

    eleza __withdraw(self, event=Tupu):
        self.__root.withdraw()

    eleza deiconify(self):
        self.__root.deiconify()



agiza functools
@functools.total_ordering
kundi PopupViewer:
    eleza __init__(self, module, name, switchboard, root):
        self.__m = module
        self.__name = name
        self.__sb = switchboard
        self.__root = root
        self.__menutext = module.ADDTOVIEW
        # find the underline character
        underline = module.ADDTOVIEW.find('%')
        ikiwa underline == -1:
            underline = 0
        isipokua:
            self.__menutext = module.ADDTOVIEW.replace('%', '', 1)
        self.__underline = underline
        self.__window = Tupu

    eleza menutext(self):
        rudisha self.__menutext

    eleza underline(self):
        rudisha self.__underline

    eleza popup(self, event=Tupu):
        ikiwa sio self.__window:
            # kundi na module must have the same name
            class_ = getattr(self.__m, self.__name)
            self.__window = class_(self.__sb, self.__root)
            self.__sb.add_view(self.__window)
        self.__window.deiconify()

    eleza __eq__(self, other):
        rudisha self.__menutext == other.__menutext

    eleza __lt__(self, other):
        rudisha self.__menutext < other.__menutext


eleza make_view_popups(switchboard, root, extrapath):
    viewers = []
    # where we are kwenye the file system
    dirs = [os.path.dirname(__file__)] + extrapath
    kila dir kwenye dirs:
        ikiwa dir == '':
            dir = '.'
        kila file kwenye os.listdir(dir):
            ikiwa file[-9:] == 'Viewer.py':
                name = file[:-3]
                jaribu:
                    module = __import__(name)
                tatizo ImportError:
                    # Pynche ni running kutoka inside a package, so get the
                    # module using the explicit path.
                    pkg = __import__('pynche.'+name)
                    module = getattr(pkg, name)
                ikiwa hasattr(module, 'ADDTOVIEW') na module.ADDTOVIEW:
                    # this ni an external viewer
                    v = PopupViewer(module, name, switchboard, root)
                    viewers.append(v)
    # sort alphabetically
    viewers.sort()
    rudisha viewers
