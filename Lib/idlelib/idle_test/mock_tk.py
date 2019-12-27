"""Classes that replace tkinter gui objects used by an object being tested.

A gui object is anything with a master or parent parameter, which is
typically required in spite of what the doc strings say.
"""

kundi Event:
    '''Minimal mock with attributes for testing event handlers.

    This is not a gui object, but is used as an argument for callbacks
    that access attributes of the event passed. If a callback ignores
    the event, other than the fact that is happened, pass 'event'.

    Keyboard, mouse, window, and other sources generate Event instances.
    Event instances have the following attributes: serial (number of
    event), time (of event), type (of event as number), widget (in which
    event occurred), and x,y (position of mouse). There are other
    attributes for specific events, such as keycode for key events.
    tkinter.Event.__doc__ has more but is still not complete.
    '''
    eleza __init__(self, **kwds):
        "Create event with attributes needed for test"
        self.__dict__.update(kwds)

kundi Var:
    "Use for String/Int/BooleanVar: incomplete"
    eleza __init__(self, master=None, value=None, name=None):
        self.master = master
        self.value = value
        self.name = name
    eleza set(self, value):
        self.value = value
    eleza get(self):
        rudisha self.value

kundi Mbox_func:
    """Generic mock for messagebox functions, which all have the same signature.

    Instead of displaying a message box, the mock's call method saves the
    arguments as instance attributes, which test functions can then examine.
    The test can set the result returned to ask function
    """
    eleza __init__(self, result=None):
        self.result = result  # Return None for all show funcs
    eleza __call__(self, title, message, *args, **kwds):
        # Save all args for possible examination by tester
        self.title = title
        self.message = message
        self.args = args
        self.kwds = kwds
        rudisha self.result  # Set by tester for ask functions

kundi Mbox:
    """Mock for tkinter.messagebox with an Mbox_func for each function.

    This module was 'tkMessageBox' in 2.x; hence the 'agiza as' in  3.x.
    Example usage in test_module.py for testing functions in module.py:
    ---
kutoka idlelib.idle_test.mock_tk agiza Mbox
agiza module

orig_mbox = module.tkMessageBox
showerror = Mbox.showerror  # example, for attribute access in test methods

kundi Test(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        module.tkMessageBox = Mbox

    @classmethod
    eleza tearDownClass(cls):
        module.tkMessageBox = orig_mbox
    ---
    For 'ask' functions, set func.result rudisha value before calling the method
    that uses the message function. When tkMessageBox functions are the
    only gui alls in a method, this replacement makes the method gui-free,
    """
    askokcancel = Mbox_func()     # True or False
    askquestion = Mbox_func()     # 'yes' or 'no'
    askretrycancel = Mbox_func()  # True or False
    askyesno = Mbox_func()        # True or False
    askyesnocancel = Mbox_func()  # True, False, or None
    showerror = Mbox_func()    # None
    showinfo = Mbox_func()     # None
    showwarning = Mbox_func()  # None

kutoka _tkinter agiza TclError

kundi Text:
    """A semi-functional non-gui replacement for tkinter.Text text editors.

    The mock's data model is that a text is a list of \n-terminated lines.
    The mock adds an empty string at  the beginning of the list so that the
    index of actual lines start at 1, as with Tk. The methods never see this.
    Tk initializes files with a terminal \n that cannot be deleted. It is
    invisible in the sense that one cannot move the cursor beyond it.

    This kundi is only tested (and valid) with strings of ascii chars.
    For testing, we are not concerned with Tk Text's treatment of,
    for instance, 0-width characters or character + accent.
   """
    eleza __init__(self, master=None, cnf={}, **kw):
        '''Initialize mock, non-gui, text-only Text widget.

        At present, all args are ignored. Almost all affect visual behavior.
        There are just a few Text-only options that affect text behavior.
        '''
        self.data = ['', '\n']

    eleza index(self, index):
        "Return string version of index decoded according to current text."
        rudisha "%s.%s" % self._decode(index, endflag=1)

    eleza _decode(self, index, endflag=0):
        """Return a (line, char) tuple of int indexes into self.data.

        This implements .index without converting the result back to a string.
        The result is constrained by the number of lines and linelengths of
        self.data. For many indexes, the result is initially (1, 0).

        The input index may have any of several possible forms:
        * line.char float: converted to 'line.char' string;
        * 'line.char' string, where line and char are decimal integers;
        * 'line.char lineend', where lineend='lineend' (and char is ignored);
        * 'line.end', where end='end' (same as above);
        * 'insert', the positions before terminal \n;
        * 'end', whose meaning depends on the endflag passed to ._endex.
        * 'sel.first' or 'sel.last', where sel is a tag -- not implemented.
        """
        ikiwa isinstance(index, (float, bytes)):
            index = str(index)
        try:
            index=index.lower()
        except AttributeError:
            raise TclError('bad text index "%s"' % index) kutoka None

        lastline =  len(self.data) - 1  # same as number of text lines
        ikiwa index == 'insert':
            rudisha lastline, len(self.data[lastline]) - 1
        elikiwa index == 'end':
            rudisha self._endex(endflag)

        line, char = index.split('.')
        line = int(line)

        # Out of bounds line becomes first or last ('end') index
        ikiwa line < 1:
            rudisha 1, 0
        elikiwa line > lastline:
            rudisha self._endex(endflag)

        linelength = len(self.data[line])  -1  # position before/at \n
        ikiwa char.endswith(' lineend') or char == 'end':
            rudisha line, linelength
            # Tk requires that ignored chars before ' lineend' be valid int

        # Out of bounds char becomes first or last index of line
        char = int(char)
        ikiwa char < 0:
            char = 0
        elikiwa char > linelength:
            char = linelength
        rudisha line, char

    eleza _endex(self, endflag):
        '''Return position for 'end' or line overflow corresponding to endflag.

       -1: position before terminal \n; for .insert(), .delete
       0: position after terminal \n; for .get, .delete index 1
       1: same viewed as beginning of non-existent next line (for .index)
       '''
        n = len(self.data)
        ikiwa endflag == 1:
            rudisha n, 0
        else:
            n -= 1
            rudisha n, len(self.data[n]) + endflag


    eleza insert(self, index, chars):
        "Insert chars before the character at index."

        ikiwa not chars:  # ''.splitlines() is [], not ['']
            return
        chars = chars.splitlines(True)
        ikiwa chars[-1][-1] == '\n':
            chars.append('')
        line, char = self._decode(index, -1)
        before = self.data[line][:char]
        after = self.data[line][char:]
        self.data[line] = before + chars[0]
        self.data[line+1:line+1] = chars[1:]
        self.data[line+len(chars)-1] += after


    eleza get(self, index1, index2=None):
        "Return slice kutoka index1 to index2 (default is 'index1+1')."

        startline, startchar = self._decode(index1)
        ikiwa index2 is None:
            endline, endchar = startline, startchar+1
        else:
            endline, endchar = self._decode(index2)

        ikiwa startline == endline:
            rudisha self.data[startline][startchar:endchar]
        else:
            lines = [self.data[startline][startchar:]]
            for i in range(startline+1, endline):
                lines.append(self.data[i])
            lines.append(self.data[endline][:endchar])
            rudisha ''.join(lines)


    eleza delete(self, index1, index2=None):
        '''Delete slice kutoka index1 to index2 (default is 'index1+1').

        Adjust default index2 ('index+1) for line ends.
        Do not delete the terminal \n at the very end of self.data ([-1][-1]).
        '''
        startline, startchar = self._decode(index1, -1)
        ikiwa index2 is None:
            ikiwa startchar < len(self.data[startline])-1:
                # not deleting \n
                endline, endchar = startline, startchar+1
            elikiwa startline < len(self.data) - 1:
                # deleting non-terminal \n, convert 'index1+1 to start of next line
                endline, endchar = startline+1, 0
            else:
                # do not delete terminal \n ikiwa index1 == 'insert'
                return
        else:
            endline, endchar = self._decode(index2, -1)
            # restricting end position to insert position excludes terminal \n

        ikiwa startline == endline and startchar < endchar:
            self.data[startline] = self.data[startline][:startchar] + \
                                             self.data[startline][endchar:]
        elikiwa startline < endline:
            self.data[startline] = self.data[startline][:startchar] + \
                                   self.data[endline][endchar:]
            startline += 1
            for i in range(startline, endline+1):
                del self.data[startline]

    eleza compare(self, index1, op, index2):
        line1, char1 = self._decode(index1)
        line2, char2 = self._decode(index2)
        ikiwa op == '<':
            rudisha line1 < line2 or line1 == line2 and char1 < char2
        elikiwa op == '<=':
            rudisha line1 < line2 or line1 == line2 and char1 <= char2
        elikiwa op == '>':
            rudisha line1 > line2 or line1 == line2 and char1 > char2
        elikiwa op == '>=':
            rudisha line1 > line2 or line1 == line2 and char1 >= char2
        elikiwa op == '==':
            rudisha line1 == line2 and char1 == char2
        elikiwa op == '!=':
            rudisha line1 != line2 or  char1 != char2
        else:
            raise TclError('''bad comparison operator "%s": '''
                                  '''must be <, <=, ==, >=, >, or !=''' % op)

    # The following Text methods normally do something and rudisha None.
    # Whether doing nothing is sufficient for a test will depend on the test.

    eleza mark_set(self, name, index):
        "Set mark *name* before the character at index."
        pass

    eleza mark_unset(self, *markNames):
        "Delete all marks in markNames."

    eleza tag_remove(self, tagName, index1, index2=None):
        "Remove tag tagName kutoka all characters between index1 and index2."
        pass

    # The following Text methods affect the graphics screen and rudisha None.
    # Doing nothing should always be sufficient for tests.

    eleza scan_dragto(self, x, y):
        "Adjust the view of the text according to scan_mark"

    eleza scan_mark(self, x, y):
        "Remember the current X, Y coordinates."

    eleza see(self, index):
        "Scroll screen to make the character at INDEX is visible."
        pass

    #  The following is a Misc method inherited by Text.
    # It should properly go in a Misc mock, but is included here for now.

    eleza bind(sequence=None, func=None, add=None):
        "Bind to this widget at event sequence a call to function func."
        pass

kundi Entry:
    "Mock for tkinter.Entry."
    eleza focus_set(self):
        pass
