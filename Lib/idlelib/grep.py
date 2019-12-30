"""Grep dialog kila Find kwenye Files functionality.

   Inherits kutoka SearchDialogBase kila GUI na uses searchengine
   to prepare search pattern.
"""
agiza fnmatch
agiza os
agiza sys

kutoka tkinter agiza StringVar, BooleanVar
kutoka tkinter.ttk agiza Checkbutton  # Frame imported kwenye ...Base

kutoka idlelib.searchbase agiza SearchDialogBase
kutoka idlelib agiza searchengine

# Importing OutputWindow here fails due to agiza loop
# EditorWindow -> GrepDialog -> OutputWindow -> EditorWindow


eleza grep(text, io=Tupu, flist=Tupu):
    """Open the Find kwenye Files dialog.

    Module-level function to access the singleton GrepDialog
    instance na open the dialog.  If text ni selected, it is
    used kama the search phrase; otherwise, the previous entry
    ni used.

    Args:
        text: Text widget that contains the selected text for
              default search phrase.
        io: iomenu.IOBinding instance ukijumuisha default path to search.
        flist: filelist.FileList instance kila OutputWindow parent.
    """
    root = text._root()
    engine = searchengine.get(root)
    ikiwa sio hasattr(engine, "_grepdialog"):
        engine._grepdialog = GrepDialog(root, engine, flist)
    dialog = engine._grepdialog
    searchphrase = text.get("sel.first", "sel.last")
    dialog.open(text, searchphrase, io)


eleza walk_error(msg):
    "Handle os.walk error."
    andika(msg)


eleza findfiles(folder, pattern, recursive):
    """Generate file names kwenye dir that match pattern.

    Args:
        folder: Root directory to search.
        pattern: File pattern to match.
        recursive: Kweli to include subdirectories.
    """
    kila dirpath, _, filenames kwenye os.walk(folder, onerror=walk_error):
        tuma kutoka (os.path.join(dirpath, name)
                    kila name kwenye filenames
                    ikiwa fnmatch.fnmatch(name, pattern))
        ikiwa sio recursive:
            koma


kundi GrepDialog(SearchDialogBase):
    "Dialog kila searching multiple files."

    title = "Find kwenye Files Dialog"
    icon = "Grep"
    needwrapbutton = 0

    eleza __init__(self, root, engine, flist):
        """Create search dialog kila searching kila a phrase kwenye the file system.

        Uses SearchDialogBase kama the basis kila the GUI na a
        searchengine instance to prepare the search.

        Attributes:
            flist: filelist.Filelist instance kila OutputWindow parent.
            globvar: String value of Entry widget kila path to search.
            globent: Entry widget kila globvar.  Created kwenye
                create_entries().
            recvar: Boolean value of Checkbutton widget for
                traversing through subdirectories.
        """
        super().__init__(root, engine)
        self.flist = flist
        self.globvar = StringVar(root)
        self.recvar = BooleanVar(root)

    eleza open(self, text, searchphrase, io=Tupu):
        """Make dialog visible on top of others na ready to use.

        Extend the SearchDialogBase open() to set the initial value
        kila globvar.

        Args:
            text: Multicall object containing the text information.
            searchphrase: String phrase to search.
            io: iomenu.IOBinding instance containing file path.
        """
        SearchDialogBase.open(self, text, searchphrase)
        ikiwa io:
            path = io.filename ama ""
        isipokua:
            path = ""
        dir, base = os.path.split(path)
        head, tail = os.path.splitext(base)
        ikiwa sio tail:
            tail = ".py"
        self.globvar.set(os.path.join(dir, "*" + tail))

    eleza create_entries(self):
        "Create base entry widgets na add widget kila search path."
        SearchDialogBase.create_entries(self)
        self.globent = self.make_entry("In files:", self.globvar)[0]

    eleza create_other_buttons(self):
        "Add check button to recurse down subdirectories."
        btn = Checkbutton(
                self.make_frame()[0], variable=self.recvar,
                text="Recurse down subdirectories")
        btn.pack(side="top", fill="both")

    eleza create_command_buttons(self):
        "Create base command buttons na add button kila Search Files."
        SearchDialogBase.create_command_buttons(self)
        self.make_button("Search Files", self.default_command, isdef=Kweli)

    eleza default_command(self, event=Tupu):
        """Grep kila search pattern kwenye file path. The default command ni bound
        to <Return>.

        If entry values are populated, set OutputWindow kama stdout
        na perform search.  The search dialog ni closed automatically
        when the search begins.
        """
        prog = self.engine.getprog()
        ikiwa sio prog:
            rudisha
        path = self.globvar.get()
        ikiwa sio path:
            self.top.bell()
            rudisha
        kutoka idlelib.outwin agiza OutputWindow  # leave here!
        save = sys.stdout
        jaribu:
            sys.stdout = OutputWindow(self.flist)
            self.grep_it(prog, path)
        mwishowe:
            sys.stdout = save

    eleza grep_it(self, prog, path):
        """Search kila prog within the lines of the files kwenye path.

        For the each file kwenye the path directory, open the file na
        search each line kila the matching pattern.  If the pattern is
        found,  write the file na line information to stdout (which
        ni an OutputWindow).

        Args:
            prog: The compiled, cooked search pattern.
            path: String containing the search path.
        """
        folder, filepat = os.path.split(path)
        ikiwa sio folder:
            folder = os.curdir
        filelist = sorted(findfiles(folder, filepat, self.recvar.get()))
        self.close()
        pat = self.engine.getpat()
        andika(f"Searching {pat!r} kwenye {path} ...")
        hits = 0
        jaribu:
            kila fn kwenye filelist:
                jaribu:
                    ukijumuisha open(fn, errors='replace') kama f:
                        kila lineno, line kwenye enumerate(f, 1):
                            ikiwa line[-1:] == '\n':
                                line = line[:-1]
                            ikiwa prog.search(line):
                                sys.stdout.write(f"{fn}: {lineno}: {line}\n")
                                hits += 1
                tatizo OSError kama msg:
                    andika(msg)
            andika(f"Hits found: {hits}\n(Hint: right-click to open locations.)"
                  ikiwa hits isipokua "No hits.")
        tatizo AttributeError:
            # Tk window has been closed, OutputWindow.text = Tupu,
            # so kwenye OW.write, OW.text.insert fails.
            pita


eleza _grep_dialog(parent):  # htest #
    kutoka tkinter agiza Toplevel, Text, SEL, END
    kutoka tkinter.ttk agiza Frame, Button
    kutoka idlelib.pyshell agiza PyShellFileList

    top = Toplevel(parent)
    top.title("Test GrepDialog")
    x, y = map(int, parent.geometry().split('+')[1:])
    top.geometry(f"+{x}+{y + 175}")

    flist = PyShellFileList(top)
    frame = Frame(top)
    frame.pack()
    text = Text(frame, height=5)
    text.pack()

    eleza show_grep_dialog():
        text.tag_add(SEL, "1.0", END)
        grep(text, flist=flist)
        text.tag_remove(SEL, "1.0", END)

    button = Button(frame, text="Show GrepDialog", command=show_grep_dialog)
    button.pack()

ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_grep', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_grep_dialog)
