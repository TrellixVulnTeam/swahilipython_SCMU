'''Define SearchEngine kila search dialogs.'''
agiza re

kutoka tkinter agiza StringVar, BooleanVar, TclError
agiza tkinter.messagebox kama tkMessageBox

eleza get(root):
    '''Return the singleton SearchEngine instance kila the process.

    The single SearchEngine saves settings between dialog instances.
    If there ni sio a SearchEngine already, make one.
    '''
    ikiwa sio hasattr(root, "_searchengine"):
        root._searchengine = SearchEngine(root)
        # This creates a cycle that persists until root ni deleted.
    rudisha root._searchengine


kundi SearchEngine:
    """Handles searching a text widget kila Find, Replace, na Grep."""

    eleza __init__(self, root):
        '''Initialize Variables that save search state.

        The dialogs bind these to the UI elements present kwenye the dialogs.
        '''
        self.root = root  # need kila report_error()
        self.patvar = StringVar(root, '')   # search pattern
        self.revar = BooleanVar(root, Uongo)   # regular expression?
        self.casevar = BooleanVar(root, Uongo)   # match case?
        self.wordvar = BooleanVar(root, Uongo)   # match whole word?
        self.wrapvar = BooleanVar(root, Kweli)   # wrap around buffer?
        self.backvar = BooleanVar(root, Uongo)   # search backwards?

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
        # called only kwenye search.py: 66
        ikiwa self.isre():
            pat = re.escape(pat)
        self.setpat(pat)

    eleza getcookedpat(self):
        pat = self.getpat()
        ikiwa sio self.isre():  # ikiwa Kweli, see setcookedpat
            pat = re.escape(pat)
        ikiwa self.isword():
            pat = r"\b%s\b" % pat
        rudisha pat

    eleza getprog(self):
        "Return compiled cooked search pattern."
        pat = self.getpat()
        ikiwa sio pat:
            self.report_error(pat, "Empty regular expression")
            rudisha Tupu
        pat = self.getcookedpat()
        flags = 0
        ikiwa sio self.iscase():
            flags = flags | re.IGNORECASE
        jaribu:
            prog = re.compile(pat, flags)
        tatizo re.error kama what:
            args = what.args
            msg = args[0]
            col = args[1] ikiwa len(args) >= 2 isipokua -1
            self.report_error(pat, msg, col)
            rudisha Tupu
        rudisha prog

    eleza report_error(self, pat, msg, col=-1):
        # Derived kundi could override this ukijumuisha something fancier
        msg = "Error: " + str(msg)
        ikiwa pat:
            msg = msg + "\nPattern: " + str(pat)
        ikiwa col >= 0:
            msg = msg + "\nOffset: " + str(col)
        tkMessageBox.showerror("Regular expression error",
                               msg, master=self.root)

    eleza search_text(self, text, prog=Tupu, ok=0):
        '''Return (lineno, matchobj) ama Tupu kila forward/backward search.

        This function calls the right function ukijumuisha the right arguments.
        It directly rudisha the result of that call.

        Text ni a text widget. Prog ni a precompiled pattern.
        The ok parameter ni a bit complicated kama it has two effects.

        If there ni a selection, the search begin at either end,
        depending on the direction setting na ok, ukijumuisha ok meaning that
        the search starts ukijumuisha the selection. Otherwise, search begins
        at the insert mark.

        To aid progress, the search functions do sio rudisha an empty
        match at the starting position unless ok ni Kweli.
        '''

        ikiwa sio prog:
            prog = self.getprog()
            ikiwa sio prog:
                rudisha Tupu # Compilation failed -- stop
        wrap = self.wrapvar.get()
        first, last = get_selection(text)
        ikiwa self.isback():
            ikiwa ok:
                start = last
            isipokua:
                start = first
            line, col = get_line_col(start)
            res = self.search_backward(text, prog, line, col, wrap, ok)
        isipokua:
            ikiwa ok:
                start = first
            isipokua:
                start = last
            line, col = get_line_col(start)
            res = self.search_forward(text, prog, line, col, wrap, ok)
        rudisha res

    eleza search_forward(self, text, prog, line, col, wrap, ok=0):
        wrapped = 0
        startline = line
        chars = text.get("%d.0" % line, "%d.0" % (line+1))
        wakati chars:
            m = prog.search(chars[:-1], col)
            ikiwa m:
                ikiwa ok ama m.end() > col:
                    rudisha line, m
            line = line + 1
            ikiwa wrapped na line > startline:
                koma
            col = 0
            ok = 1
            chars = text.get("%d.0" % line, "%d.0" % (line+1))
            ikiwa sio chars na wrap:
                wrapped = 1
                wrap = 0
                line = 1
                chars = text.get("1.0", "2.0")
        rudisha Tupu

    eleza search_backward(self, text, prog, line, col, wrap, ok=0):
        wrapped = 0
        startline = line
        chars = text.get("%d.0" % line, "%d.0" % (line+1))
        wakati 1:
            m = search_reverse(prog, chars[:-1], col)
            ikiwa m:
                ikiwa ok ama m.start() < col:
                    rudisha line, m
            line = line - 1
            ikiwa wrapped na line < startline:
                koma
            ok = 1
            ikiwa line <= 0:
                ikiwa sio wrap:
                    koma
                wrapped = 1
                wrap = 0
                pos = text.index("end-1c")
                line, col = map(int, pos.split("."))
            chars = text.get("%d.0" % line, "%d.0" % (line+1))
            col = len(chars) - 1
        rudisha Tupu


eleza search_reverse(prog, chars, col):
    '''Search backwards na rudisha an re match object ama Tupu.

    This ni done by searching forwards until there ni no match.
    Prog: compiled re object ukijumuisha a search method rudishaing a match.
    Chars: line of text, without \\n.
    Col: stop index kila the search; the limit kila match.end().
    '''
    m = prog.search(chars)
    ikiwa sio m:
        rudisha Tupu
    found = Tupu
    i, j = m.span()  # m.start(), m.end() == match slice indexes
    wakati i < col na j <= col:
        found = m
        ikiwa i == j:
            j = j+1
        m = prog.search(chars, j)
        ikiwa sio m:
            koma
        i, j = m.span()
    rudisha found

eleza get_selection(text):
    '''Return tuple of 'line.col' indexes kutoka selection ama insert mark.
    '''
    jaribu:
        first = text.index("sel.first")
        last = text.index("sel.last")
    tatizo TclError:
        first = last = Tupu
    ikiwa sio first:
        first = text.index("insert")
    ikiwa sio last:
        last = first
    rudisha first, last

eleza get_line_col(index):
    '''Return (line, col) tuple of ints kutoka 'line.col' string.'''
    line, col = map(int, index.split(".")) # Fails on invalid index
    rudisha line, col


ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_searchengine', verbosity=2)
