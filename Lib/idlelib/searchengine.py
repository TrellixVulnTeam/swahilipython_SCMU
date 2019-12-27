'''Define SearchEngine for search dialogs.'''
agiza re

kutoka tkinter agiza StringVar, BooleanVar, TclError
agiza tkinter.messagebox as tkMessageBox

eleza get(root):
    '''Return the singleton SearchEngine instance for the process.

    The single SearchEngine saves settings between dialog instances.
    If there is not a SearchEngine already, make one.
    '''
    ikiwa not hasattr(root, "_searchengine"):
        root._searchengine = SearchEngine(root)
        # This creates a cycle that persists until root is deleted.
    rudisha root._searchengine


kundi SearchEngine:
    """Handles searching a text widget for Find, Replace, and Grep."""

    eleza __init__(self, root):
        '''Initialize Variables that save search state.

        The dialogs bind these to the UI elements present in the dialogs.
        '''
        self.root = root  # need for report_error()
        self.patvar = StringVar(root, '')   # search pattern
        self.revar = BooleanVar(root, False)   # regular expression?
        self.casevar = BooleanVar(root, False)   # match case?
        self.wordvar = BooleanVar(root, False)   # match whole word?
        self.wrapvar = BooleanVar(root, True)   # wrap around buffer?
        self.backvar = BooleanVar(root, False)   # search backwards?

    # Access methods

    eleza getpat(self):
        rudisha self.patvar.get()

    eleza setpat(self, pat):
        self.patvar.set(pat)

    eleza isre(self):
        rudisha self.revar.get()

    eleza iscase(self):
        rudisha self.casevar.get()

    eleza isword(self):
        rudisha self.wordvar.get()

    eleza iswrap(self):
        rudisha self.wrapvar.get()

    eleza isback(self):
        rudisha self.backvar.get()

    # Higher level access methods

    eleza setcookedpat(self, pat):
        "Set pattern after escaping ikiwa re."
        # called only in search.py: 66
        ikiwa self.isre():
            pat = re.escape(pat)
        self.setpat(pat)

    eleza getcookedpat(self):
        pat = self.getpat()
        ikiwa not self.isre():  # ikiwa True, see setcookedpat
            pat = re.escape(pat)
        ikiwa self.isword():
            pat = r"\b%s\b" % pat
        rudisha pat

    eleza getprog(self):
        "Return compiled cooked search pattern."
        pat = self.getpat()
        ikiwa not pat:
            self.report_error(pat, "Empty regular expression")
            rudisha None
        pat = self.getcookedpat()
        flags = 0
        ikiwa not self.iscase():
            flags = flags | re.IGNORECASE
        try:
            prog = re.compile(pat, flags)
        except re.error as what:
            args = what.args
            msg = args[0]
            col = args[1] ikiwa len(args) >= 2 else -1
            self.report_error(pat, msg, col)
            rudisha None
        rudisha prog

    eleza report_error(self, pat, msg, col=-1):
        # Derived kundi could override this with something fancier
        msg = "Error: " + str(msg)
        ikiwa pat:
            msg = msg + "\nPattern: " + str(pat)
        ikiwa col >= 0:
            msg = msg + "\nOffset: " + str(col)
        tkMessageBox.showerror("Regular expression error",
                               msg, master=self.root)

    eleza search_text(self, text, prog=None, ok=0):
        '''Return (lineno, matchobj) or None for forward/backward search.

        This function calls the right function with the right arguments.
        It directly rudisha the result of that call.

        Text is a text widget. Prog is a precompiled pattern.
        The ok parameter is a bit complicated as it has two effects.

        If there is a selection, the search begin at either end,
        depending on the direction setting and ok, with ok meaning that
        the search starts with the selection. Otherwise, search begins
        at the insert mark.

        To aid progress, the search functions do not rudisha an empty
        match at the starting position unless ok is True.
        '''

        ikiwa not prog:
            prog = self.getprog()
            ikiwa not prog:
                rudisha None # Compilation failed -- stop
        wrap = self.wrapvar.get()
        first, last = get_selection(text)
        ikiwa self.isback():
            ikiwa ok:
                start = last
            else:
                start = first
            line, col = get_line_col(start)
            res = self.search_backward(text, prog, line, col, wrap, ok)
        else:
            ikiwa ok:
                start = first
            else:
                start = last
            line, col = get_line_col(start)
            res = self.search_forward(text, prog, line, col, wrap, ok)
        rudisha res

    eleza search_forward(self, text, prog, line, col, wrap, ok=0):
        wrapped = 0
        startline = line
        chars = text.get("%d.0" % line, "%d.0" % (line+1))
        while chars:
            m = prog.search(chars[:-1], col)
            ikiwa m:
                ikiwa ok or m.end() > col:
                    rudisha line, m
            line = line + 1
            ikiwa wrapped and line > startline:
                break
            col = 0
            ok = 1
            chars = text.get("%d.0" % line, "%d.0" % (line+1))
            ikiwa not chars and wrap:
                wrapped = 1
                wrap = 0
                line = 1
                chars = text.get("1.0", "2.0")
        rudisha None

    eleza search_backward(self, text, prog, line, col, wrap, ok=0):
        wrapped = 0
        startline = line
        chars = text.get("%d.0" % line, "%d.0" % (line+1))
        while 1:
            m = search_reverse(prog, chars[:-1], col)
            ikiwa m:
                ikiwa ok or m.start() < col:
                    rudisha line, m
            line = line - 1
            ikiwa wrapped and line < startline:
                break
            ok = 1
            ikiwa line <= 0:
                ikiwa not wrap:
                    break
                wrapped = 1
                wrap = 0
                pos = text.index("end-1c")
                line, col = map(int, pos.split("."))
            chars = text.get("%d.0" % line, "%d.0" % (line+1))
            col = len(chars) - 1
        rudisha None


eleza search_reverse(prog, chars, col):
    '''Search backwards and rudisha an re match object or None.

    This is done by searching forwards until there is no match.
    Prog: compiled re object with a search method returning a match.
    Chars: line of text, without \\n.
    Col: stop index for the search; the limit for match.end().
    '''
    m = prog.search(chars)
    ikiwa not m:
        rudisha None
    found = None
    i, j = m.span()  # m.start(), m.end() == match slice indexes
    while i < col and j <= col:
        found = m
        ikiwa i == j:
            j = j+1
        m = prog.search(chars, j)
        ikiwa not m:
            break
        i, j = m.span()
    rudisha found

eleza get_selection(text):
    '''Return tuple of 'line.col' indexes kutoka selection or insert mark.
    '''
    try:
        first = text.index("sel.first")
        last = text.index("sel.last")
    except TclError:
        first = last = None
    ikiwa not first:
        first = text.index("insert")
    ikiwa not last:
        last = first
    rudisha first, last

eleza get_line_col(index):
    '''Return (line, col) tuple of ints kutoka 'line.col' string.'''
    line, col = map(int, index.split(".")) # Fails on invalid index
    rudisha line, col


ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_searchengine', verbosity=2)
