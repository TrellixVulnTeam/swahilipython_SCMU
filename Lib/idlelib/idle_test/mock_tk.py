"""Classes that replace tkinter gui objects used by an object being tested.

A gui object ni anything ukijumuisha a master ama parent parameter, which is
typically required kwenye spite of what the doc strings say.
"""

kundi Event:
    '''Minimal mock ukijumuisha attributes kila testing event handlers.

    This ni sio a gui object, but ni used kama an argument kila callbacks
    that access attributes of the event pitaed. If a callback ignores
    the event, other than the fact that ni happened, pita 'event'.

    Keyboard, mouse, window, na other sources generate Event instances.
    Event instances have the following attributes: serial (number of
    event), time (of event), type (of event kama number), widget (in which
    event occurred), na x,y (position of mouse). There are other
    attributes kila specific events, such kama keycode kila key events.
    tkinter.Event.__doc__ has more but ni still sio complete.
    '''
    eleza __init__(self, **kwds):
        "Create event ukijumuisha attributes needed kila test"
        self.__dict__.update(kwds)

kundi Var:
    "Use kila String/Int/BooleanVar: incomplete"
    eleza __init__(self, master=Tupu, value=Tupu, name=Tupu):
        self.master = master
        self.value = value
        self.name = name
    eleza set(self, value):
        self.value = value
    eleza get(self):
        rudisha self.value

kundi Mbox_func:
    """Generic mock kila messagebox functions, which all have the same signature.

    Instead of displaying a message box, the mock's call method saves the
    arguments kama instance attributes, which test functions can then examine.
    The test can set the result rudishaed to ask function
    """
    eleza __init__(self, result=Tupu):
        self.result = result  # Return Tupu kila all show funcs
    eleza __call__(self, title, message, *args, **kwds):
        # Save all args kila possible examination by tester
        self.title = title
        self.message = message
        self.args = args
        self.kwds = kwds
        rudisha self.result  # Set by tester kila ask functions

kundi Mbox:
    """Mock kila tkinter.messagebox ukijumuisha an Mbox_func kila each function.

    This module was 'tkMessageBox' kwenye 2.x; hence the 'agiza as' kwenye  3.x.
    Example usage kwenye test_module.py kila testing functions kwenye module.py:
    ---
kutoka idlelib.idle_test.mock_tk agiza Mbox
agiza module

orig_mbox = module.tkMessageBox
showerror = Mbox.showerror  # example, kila attribute access kwenye test methods

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
    only gui alls kwenye a method, this replacement makes the method gui-free,
    """
    askokcancel = Mbox_func()     # Kweli ama Uongo
    askquestion = Mbox_func()     # 'yes' ama 'no'
    askretrycancel = Mbox_func()  # Kweli ama Uongo
    askyesno = Mbox_func()        # Kweli ama Uongo
    askyesnocancel = Mbox_func()  # Kweli, Uongo, ama Tupu
    showerror = Mbox_func()    # Tupu
    showinfo = Mbox_func()     # Tupu
    showwarning = Mbox_func()  # Tupu

kutoka _tkinter agiza TclError

kundi Text:
    """A semi-functional non-gui replacement kila tkinter.Text text editors.

    The mock's data motoa ni that a text ni a list of \n-terminated lines.
    The mock adds an empty string at  the beginning of the list so that the
    index of actual lines start at 1, kama ukijumuisha Tk. The methods never see this.
    Tk initializes files ukijumuisha a terminal \n that cannot be deleted. It is
    invisible kwenye the sense that one cannot move the cursor beyond it.

    This kundi ni only tested (and valid) ukijumuisha strings of ascii chars.
    For testing, we are sio concerned ukijumuisha Tk Text's treatment of,
    kila instance, 0-width characters ama character + accent.
   """
    eleza __init__(self, master=Tupu, cnf={}, **kw):
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
        The result ni constrained by the number of lines na linelengths of
        self.data. For many indexes, the result ni initially (1, 0).

        The input index may have any of several possible forms:
        * line.char float: converted to 'line.char' string;
        * 'line.char' string, where line na char are decimal integers;
        * 'line.char lineend', where lineend='lineend' (and char ni ignored);
        * 'line.end', where end='end' (same kama above);
        * 'insert', the positions before terminal \n;
        * 'end', whose meaning depends on the endflag pitaed to ._endex.
        * 'sel.first' ama 'sel.last', where sel ni a tag -- sio implemented.
        """
        ikiwa isinstance(index, (float, bytes)):
            index = str(index)
        jaribu:
            index=index.lower()
        tatizo AttributeError:
            ashiria TclError('bad text index "%s"' % index) kutoka Tupu

        lastline =  len(self.data) - 1  # same kama number of text lines
        ikiwa index == 'insert':
            rudisha lastline, len(self.data[lastline]) - 1
        lasivyo index == 'end':
            rudisha self._endex(endflag)

        line, char = index.split('.')
        line = int(line)

        # Out of bounds line becomes first ama last ('end') index
        ikiwa line < 1:
            rudisha 1, 0
        lasivyo line > lastline:
            rudisha self._endex(endflag)

        linelength = len(self.data[line])  -1  # position before/at \n
        ikiwa char.endswith(' lineend') ama char == 'end':
            rudisha line, linelength
            # Tk requires that ignored chars before ' lineend' be valid int

        # Out of bounds char becomes first ama last index of line
        char = int(char)
        ikiwa char < 0:
            char = 0
        lasivyo char > linelength:
            char = linelength
        rudisha line, char

    eleza _endex(self, endflag):
        '''Return position kila 'end' ama line overflow corresponding to endflag.

       -1: position before terminal \n; kila .insert(), .delete
       0: position after terminal \n; kila .get, .delete index 1
       1: same viewed kama beginning of non-existent next line (kila .index)
       '''
        n = len(self.data)
        ikiwa endflag == 1:
            rudisha n, 0
        isipokua:
            n -= 1
            rudisha n, len(self.data[n]) + endflag


    eleza insert(self, index, chars):
        "Insert chars before the character at index."

        ikiwa sio chars:  # ''.splitlines() ni [], sio ['']
            rudisha
        chars = chars.splitlines(Kweli)
        ikiwa chars[-1][-1] == '\n':
            chars.append('')
        line, char = self._decode(index, -1)
        before = self.data[line][:char]
        after = self.data[line][char:]
        self.data[line] = before + chars[0]
        self.data[line+1:line+1] = chars[1:]
        self.data[line+len(chars)-1] += after


    eleza get(self, index1, index2=Tupu):
        "Return slice kutoka index1 to index2 (default ni 'index1+1')."

        startline, startchar = self._decode(index1)
        ikiwa index2 ni Tupu:
            endline, endchar = startline, startchar+1
        isipokua:
            endline, endchar = self._decode(index2)

        ikiwa startline == endline:
            rudisha self.data[startline][startchar:endchar]
        isipokua:
            lines = [self.data[startline][startchar:]]
            kila i kwenye range(startline+1, endline):
                lines.append(self.data[i])
            lines.append(self.data[endline][:endchar])
            rudisha ''.join(lines)


    eleza delete(self, index1, index2=Tupu):
        '''Delete slice kutoka index1 to index2 (default ni 'index1+1').

        Adjust default index2 ('index+1) kila line ends.
        Do sio delete the terminal \n at the very end of self.data ([-1][-1]).
        '''
        startline, startchar = self._decode(index1, -1)
        ikiwa index2 ni Tupu:
            ikiwa startchar < len(self.data[startline])-1:
                # sio deleting \n
                endline, endchar = startline, startchar+1
            lasivyo startline < len(self.data) - 1:
                # deleting non-terminal \n, convert 'index1+1 to start of next line
                endline, endchar = startline+1, 0
            isipokua:
                # do sio delete terminal \n ikiwa index1 == 'insert'
                rudisha
        isipokua:
            endline, endchar = self._decode(index2, -1)
            # restricting end position to insert position excludes terminal \n

        ikiwa startline == endline na startchar < endchar:
            self.data[startline] = self.data[startline][:startchar] + \
                                             self.data[startline][endchar:]
        lasivyo startline < endline:
            self.data[startline] = self.data[startline][:startchar] + \
                                   self.data[endline][endchar:]
            startline += 1
            kila i kwenye range(startline, endline+1):
                toa self.data[startline]

    eleza compare(self, index1, op, index2):
        line1, char1 = self._decode(index1)
        line2, char2 = self._decode(index2)
        ikiwa op == '<':
            rudisha line1 < line2 ama line1 == line2 na char1 < char2
        lasivyo op == '<=':
            rudisha line1 < line2 ama line1 == line2 na char1 <= char2
        lasivyo op == '>':
            rudisha line1 > line2 ama line1 == line2 na char1 > char2
        lasivyo op == '>=':
            rudisha line1 > line2 ama line1 == line2 na char1 >= char2
        lasivyo op == '==':
            rudisha line1 == line2 na char1 == char2
        lasivyo op == '!=':
            rudisha line1 != line2 ama  char1 != char2
        isipokua:
            ashiria TclError('''bad comparison operator "%s": '''
                                  '''must be <, <=, ==, >=, >, ama !=''' % op)

    # The following Text methods normally do something na rudisha Tupu.
    # Whether doing nothing ni sufficient kila a test will depend on the test.

    eleza mark_set(self, name, index):
        "Set mark *name* before the character at index."
        pita

    eleza mark_unset(self, *markNames):
        "Delete all marks kwenye markNames."

    eleza tag_remove(self, tagName, index1, index2=Tupu):
        "Remove tag tagName kutoka all characters between index1 na index2."
        pita

    # The following Text methods affect the graphics screen na rudisha Tupu.
    # Doing nothing should always be sufficient kila tests.

    eleza scan_dragto(self, x, y):
        "Adjust the view of the text according to scan_mark"

    eleza scan_mark(self, x, y):
        "Remember the current X, Y coordinates."

    eleza see(self, index):
        "Scroll screen to make the character at INDEX ni visible."
        pita

    #  The following ni a Misc method inherited by Text.
    # It should properly go kwenye a Misc mock, but ni included here kila now.

    eleza bind(sequence=Tupu, func=Tupu, add=Tupu):
        "Bind to this widget at event sequence a call to function func."
        pita

kundi Enjaribu:
    "Mock kila tkinter.Entry."
    eleza focus_set(self):
        pita
