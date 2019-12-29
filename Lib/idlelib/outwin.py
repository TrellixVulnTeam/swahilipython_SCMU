"""Editor window that can serve kama an output file.
"""

agiza re

kutoka tkinter agiza messagebox

kutoka idlelib.editor agiza EditorWindow
kutoka idlelib agiza iomenu


file_line_pats = [
    # order of patterns matters
    r'file "([^"]*)", line (\d+)',
    r'([^\s]+)\((\d+)\)',
    r'^(\s*\S.*?):\s*(\d+):',  # Win filename, maybe starting ukijumuisha spaces
    r'([^\s]+):\s*(\d+):',     # filename ama path, ltrim
    r'^\s*(\S.*?):\s*(\d+):',  # Win abs path ukijumuisha embedded spaces, ltrim
]

file_line_progs = Tupu


eleza compile_progs():
    "Compile the patterns kila matching to file name na line number."
    global file_line_progs
    file_line_progs = [re.compile(pat, re.IGNORECASE)
                       kila pat kwenye file_line_pats]


eleza file_line_helper(line):
    """Extract file name na line number kutoka line of text.

    Check ikiwa line of text contains one of the file/line patterns.
    If it does na ikiwa the file na line are valid, rudisha
    a tuple of the file name na line number.  If it doesn't match
    ama ikiwa the file ama line ni invalid, rudisha Tupu.
    """
    ikiwa sio file_line_progs:
        compile_progs()
    kila prog kwenye file_line_progs:
        match = prog.search(line)
        ikiwa match:
            filename, lineno = match.group(1, 2)
            jaribu:
                f = open(filename, "r")
                f.close()
                koma
            tatizo OSError:
                endelea
    isipokua:
        rudisha Tupu
    jaribu:
        rudisha filename, int(lineno)
    tatizo TypeError:
        rudisha Tupu


kundi OutputWindow(EditorWindow):
    """An editor window that can serve kama an output file.

    Also the future base kundi kila the Python shell window.
    This kundi has no input facilities.

    Adds binding to open a file at a line to the text widget.
    """

    # Our own right-button menu
    rmenu_specs = [
        ("Cut", "<<cut>>", "rmenu_check_cut"),
        ("Copy", "<<copy>>", "rmenu_check_copy"),
        ("Paste", "<<paste>>", "rmenu_check_paste"),
        (Tupu, Tupu, Tupu),
        ("Go to file/line", "<<goto-file-line>>", Tupu),
    ]

    allow_code_context = Uongo

    eleza __init__(self, *args):
        EditorWindow.__init__(self, *args)
        self.text.bind("<<goto-file-line>>", self.goto_file_line)

    # Customize EditorWindow
    eleza ispythonsource(self, filename):
        "Python source ni only part of output: do sio colorize."
        rudisha Uongo

    eleza short_title(self):
        "Customize EditorWindow title."
        rudisha "Output"

    eleza maybesave(self):
        "Customize EditorWindow to sio display save file messagebox."
        rudisha 'yes' ikiwa self.get_saved() isipokua 'no'

    # Act kama output file
    eleza write(self, s, tags=(), mark="insert"):
        """Write text to text widget.

        The text ni inserted at the given index ukijumuisha the provided
        tags.  The text widget ni then scrolled to make it visible
        na updated to display it, giving the effect of seeing each
        line kama it ni added.

        Args:
            s: Text to insert into text widget.
            tags: Tuple of tag strings to apply on the insert.
            mark: Index kila the insert.

        Return:
            Length of text inserted.
        """
        ikiwa isinstance(s, bytes):
            s = s.decode(iomenu.encoding, "replace")
        self.text.insert(mark, s, tags)
        self.text.see(mark)
        self.text.update()
        rudisha len(s)

    eleza writelines(self, lines):
        "Write each item kwenye lines iterable."
        kila line kwenye lines:
            self.write(line)

    eleza flush(self):
        "No flushing needed kama write() directly writes to widget."
        pita

    eleza showerror(self, *args, **kwargs):
        messagebox.showerror(*args, **kwargs)

    eleza goto_file_line(self, event=Tupu):
        """Handle request to open file/line.

        If the selected ama previous line kwenye the output window
        contains a file name na line number, then open that file
        name kwenye a new window na position on the line number.

        Otherwise, display an error messagebox.
        """
        line = self.text.get("insert linestart", "insert lineend")
        result = file_line_helper(line)
        ikiwa sio result:
            # Try the previous line.  This ni handy e.g. kwenye tracebacks,
            # where you tend to right-click on the displayed source line
            line = self.text.get("insert -1line linestart",
                                 "insert -1line lineend")
            result = file_line_helper(line)
            ikiwa sio result:
                self.showerror(
                    "No special line",
                    "The line you point at doesn't look like "
                    "a valid file name followed by a line number.",
                    parent=self.text)
                rudisha
        filename, lineno = result
        self.flist.gotofileline(filename, lineno)


# These classes are currently sio used but might come kwenye handy
kundi OnDemandOutputWindow:

    tagdefs = {
        # XXX Should use IdlePrefs.ColorPrefs
        "stdout":  {"foreground": "blue"},
        "stderr":  {"foreground": "#007700"},
    }

    eleza __init__(self, flist):
        self.flist = flist
        self.owin = Tupu

    eleza write(self, s, tags, mark):
        ikiwa sio self.owin:
            self.setup()
        self.owin.write(s, tags, mark)

    eleza setup(self):
        self.owin = owin = OutputWindow(self.flist)
        text = owin.text
        kila tag, cnf kwenye self.tagdefs.items():
            ikiwa cnf:
                text.tag_configure(tag, **cnf)
        text.tag_ashiria('sel')
        self.write = self.owin.write

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_outwin', verbosity=2, exit=Uongo)
