"""Editor window that can serve as an output file.
"""

agiza re

kutoka tkinter agiza messagebox

kutoka idlelib.editor agiza EditorWindow
kutoka idlelib agiza iomenu


file_line_pats = [
    # order of patterns matters
    r'file "([^"]*)", line (\d+)',
    r'([^\s]+)\((\d+)\)',
    r'^(\s*\S.*?):\s*(\d+):',  # Win filename, maybe starting with spaces
    r'([^\s]+):\s*(\d+):',     # filename or path, ltrim
    r'^\s*(\S.*?):\s*(\d+):',  # Win abs path with embedded spaces, ltrim
]

file_line_progs = None


eleza compile_progs():
    "Compile the patterns for matching to file name and line number."
    global file_line_progs
    file_line_progs = [re.compile(pat, re.IGNORECASE)
                       for pat in file_line_pats]


eleza file_line_helper(line):
    """Extract file name and line number kutoka line of text.

    Check ikiwa line of text contains one of the file/line patterns.
    If it does and ikiwa the file and line are valid, return
    a tuple of the file name and line number.  If it doesn't match
    or ikiwa the file or line is invalid, rudisha None.
    """
    ikiwa not file_line_progs:
        compile_progs()
    for prog in file_line_progs:
        match = prog.search(line)
        ikiwa match:
            filename, lineno = match.group(1, 2)
            try:
                f = open(filename, "r")
                f.close()
                break
            except OSError:
                continue
    else:
        rudisha None
    try:
        rudisha filename, int(lineno)
    except TypeError:
        rudisha None


kundi OutputWindow(EditorWindow):
    """An editor window that can serve as an output file.

    Also the future base kundi for the Python shell window.
    This kundi has no input facilities.

    Adds binding to open a file at a line to the text widget.
    """

    # Our own right-button menu
    rmenu_specs = [
        ("Cut", "<<cut>>", "rmenu_check_cut"),
        ("Copy", "<<copy>>", "rmenu_check_copy"),
        ("Paste", "<<paste>>", "rmenu_check_paste"),
        (None, None, None),
        ("Go to file/line", "<<goto-file-line>>", None),
    ]

    allow_code_context = False

    eleza __init__(self, *args):
        EditorWindow.__init__(self, *args)
        self.text.bind("<<goto-file-line>>", self.goto_file_line)

    # Customize EditorWindow
    eleza ispythonsource(self, filename):
        "Python source is only part of output: do not colorize."
        rudisha False

    eleza short_title(self):
        "Customize EditorWindow title."
        rudisha "Output"

    eleza maybesave(self):
        "Customize EditorWindow to not display save file messagebox."
        rudisha 'yes' ikiwa self.get_saved() else 'no'

    # Act as output file
    eleza write(self, s, tags=(), mark="insert"):
        """Write text to text widget.

        The text is inserted at the given index with the provided
        tags.  The text widget is then scrolled to make it visible
        and updated to display it, giving the effect of seeing each
        line as it is added.

        Args:
            s: Text to insert into text widget.
            tags: Tuple of tag strings to apply on the insert.
            mark: Index for the insert.

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
        "Write each item in lines iterable."
        for line in lines:
            self.write(line)

    eleza flush(self):
        "No flushing needed as write() directly writes to widget."
        pass

    eleza showerror(self, *args, **kwargs):
        messagebox.showerror(*args, **kwargs)

    eleza goto_file_line(self, event=None):
        """Handle request to open file/line.

        If the selected or previous line in the output window
        contains a file name and line number, then open that file
        name in a new window and position on the line number.

        Otherwise, display an error messagebox.
        """
        line = self.text.get("insert linestart", "insert lineend")
        result = file_line_helper(line)
        ikiwa not result:
            # Try the previous line.  This is handy e.g. in tracebacks,
            # where you tend to right-click on the displayed source line
            line = self.text.get("insert -1line linestart",
                                 "insert -1line lineend")
            result = file_line_helper(line)
            ikiwa not result:
                self.showerror(
                    "No special line",
                    "The line you point at doesn't look like "
                    "a valid file name followed by a line number.",
                    parent=self.text)
                return
        filename, lineno = result
        self.flist.gotofileline(filename, lineno)


# These classes are currently not used but might come in handy
kundi OnDemandOutputWindow:

    tagdefs = {
        # XXX Should use IdlePrefs.ColorPrefs
        "stdout":  {"foreground": "blue"},
        "stderr":  {"foreground": "#007700"},
    }

    eleza __init__(self, flist):
        self.flist = flist
        self.owin = None

    eleza write(self, s, tags, mark):
        ikiwa not self.owin:
            self.setup()
        self.owin.write(s, tags, mark)

    eleza setup(self):
        self.owin = owin = OutputWindow(self.flist)
        text = owin.text
        for tag, cnf in self.tagdefs.items():
            ikiwa cnf:
                text.tag_configure(tag, **cnf)
        text.tag_raise('sel')
        self.write = self.owin.write

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_outwin', verbosity=2, exit=False)
