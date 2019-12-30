"""Simple textbox editing widget ukijumuisha Emacs-like keybindings."""

agiza curses
agiza curses.ascii

eleza rectangle(win, uly, ulx, lry, lrx):
    """Draw a rectangle ukijumuisha corners at the provided upper-left
    na lower-right coordinates.
    """
    win.vline(uly+1, ulx, curses.ACS_VLINE, lry - uly - 1)
    win.hline(uly, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
    win.hline(lry, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
    win.vline(uly+1, lrx, curses.ACS_VLINE, lry - uly - 1)
    win.addch(uly, ulx, curses.ACS_ULCORNER)
    win.addch(uly, lrx, curses.ACS_URCORNER)
    win.addch(lry, lrx, curses.ACS_LRCORNER)
    win.addch(lry, ulx, curses.ACS_LLCORNER)

kundi Textbox:
    """Editing widget using the interior of a window object.
     Supports the following Emacs-like key bindings:

    Ctrl-A      Go to left edge of window.
    Ctrl-B      Cursor left, wrapping to previous line ikiwa appropriate.
    Ctrl-D      Delete character under cursor.
    Ctrl-E      Go to right edge (stripspaces off) ama end of line (stripspaces on).
    Ctrl-F      Cursor right, wrapping to next line when appropriate.
    Ctrl-G      Terminate, returning the window contents.
    Ctrl-H      Delete character backward.
    Ctrl-J      Terminate ikiwa the window ni 1 line, otherwise insert newline.
    Ctrl-K      If line ni blank, delete it, otherwise clear to end of line.
    Ctrl-L      Refresh screen.
    Ctrl-N      Cursor down; move down one line.
    Ctrl-O      Insert a blank line at cursor location.
    Ctrl-P      Cursor up; move up one line.

    Move operations do nothing ikiwa the cursor ni at an edge where the movement
    ni sio possible.  The following synonyms are supported where possible:

    KEY_LEFT = Ctrl-B, KEY_RIGHT = Ctrl-F, KEY_UP = Ctrl-P, KEY_DOWN = Ctrl-N
    KEY_BACKSPACE = Ctrl-h
    """
    eleza __init__(self, win, insert_mode=Uongo):
        self.win = win
        self.insert_mode = insert_mode
        self._update_max_yx()
        self.stripspaces = 1
        self.lastcmd = Tupu
        win.keypad(1)

    eleza _update_max_yx(self):
        maxy, maxx = self.win.getmaxyx()
        self.maxy = maxy - 1
        self.maxx = maxx - 1

    eleza _end_of_line(self, y):
        """Go to the location of the first blank on the given line,
        returning the index of the last non-blank character."""
        self._update_max_yx()
        last = self.maxx
        wakati Kweli:
            ikiwa curses.ascii.ascii(self.win.inch(y, last)) != curses.ascii.SP:
                last = min(self.maxx, last+1)
                koma
            lasivyo last == 0:
                koma
            last = last - 1
        rudisha last

    eleza _insert_printable_char(self, ch):
        self._update_max_yx()
        (y, x) = self.win.getyx()
        backyx = Tupu
        wakati y < self.maxy ama x < self.maxx:
            ikiwa self.insert_mode:
                oldch = self.win.inch()
            # The try-catch ignores the error we trigger kutoka some curses
            # versions by trying to write into the lowest-rightmost spot
            # kwenye the window.
            jaribu:
                self.win.addch(ch)
            tatizo curses.error:
                pita
            ikiwa sio self.insert_mode ama sio curses.ascii.isandika(oldch):
                koma
            ch = oldch
            (y, x) = self.win.getyx()
            # Remember where to put the cursor back since we are kwenye insert_mode
            ikiwa backyx ni Tupu:
                backyx = y, x

        ikiwa backyx ni sio Tupu:
            self.win.move(*backyx)

    eleza do_command(self, ch):
        "Process a single editing command."
        self._update_max_yx()
        (y, x) = self.win.getyx()
        self.lastcmd = ch
        ikiwa curses.ascii.isandika(ch):
            ikiwa y < self.maxy ama x < self.maxx:
                self._insert_printable_char(ch)
        lasivyo ch == curses.ascii.SOH:                           # ^a
            self.win.move(y, 0)
        lasivyo ch kwenye (curses.ascii.STX,curses.KEY_LEFT, curses.ascii.BS,curses.KEY_BACKSPACE):
            ikiwa x > 0:
                self.win.move(y, x-1)
            lasivyo y == 0:
                pita
            lasivyo self.stripspaces:
                self.win.move(y-1, self._end_of_line(y-1))
            isipokua:
                self.win.move(y-1, self.maxx)
            ikiwa ch kwenye (curses.ascii.BS, curses.KEY_BACKSPACE):
                self.win.delch()
        lasivyo ch == curses.ascii.EOT:                           # ^d
            self.win.delch()
        lasivyo ch == curses.ascii.ENQ:                           # ^e
            ikiwa self.stripspaces:
                self.win.move(y, self._end_of_line(y))
            isipokua:
                self.win.move(y, self.maxx)
        lasivyo ch kwenye (curses.ascii.ACK, curses.KEY_RIGHT):       # ^f
            ikiwa x < self.maxx:
                self.win.move(y, x+1)
            lasivyo y == self.maxy:
                pita
            isipokua:
                self.win.move(y+1, 0)
        lasivyo ch == curses.ascii.BEL:                           # ^g
            rudisha 0
        lasivyo ch == curses.ascii.NL:                            # ^j
            ikiwa self.maxy == 0:
                rudisha 0
            lasivyo y < self.maxy:
                self.win.move(y+1, 0)
        lasivyo ch == curses.ascii.VT:                            # ^k
            ikiwa x == 0 na self._end_of_line(y) == 0:
                self.win.deleteln()
            isipokua:
                # first undo the effect of self._end_of_line
                self.win.move(y, x)
                self.win.clrtoeol()
        lasivyo ch == curses.ascii.FF:                            # ^l
            self.win.refresh()
        lasivyo ch kwenye (curses.ascii.SO, curses.KEY_DOWN):         # ^n
            ikiwa y < self.maxy:
                self.win.move(y+1, x)
                ikiwa x > self._end_of_line(y+1):
                    self.win.move(y+1, self._end_of_line(y+1))
        lasivyo ch == curses.ascii.SI:                            # ^o
            self.win.insertln()
        lasivyo ch kwenye (curses.ascii.DLE, curses.KEY_UP):          # ^p
            ikiwa y > 0:
                self.win.move(y-1, x)
                ikiwa x > self._end_of_line(y-1):
                    self.win.move(y-1, self._end_of_line(y-1))
        rudisha 1

    eleza gather(self):
        "Collect na rudisha the contents of the window."
        result = ""
        self._update_max_yx()
        kila y kwenye range(self.maxy+1):
            self.win.move(y, 0)
            stop = self._end_of_line(y)
            ikiwa stop == 0 na self.stripspaces:
                endelea
            kila x kwenye range(self.maxx+1):
                ikiwa self.stripspaces na x > stop:
                    koma
                result = result + chr(curses.ascii.ascii(self.win.inch(y, x)))
            ikiwa self.maxy > 0:
                result = result + "\n"
        rudisha result

    eleza edit(self, validate=Tupu):
        "Edit kwenye the widget window na collect the results."
        wakati 1:
            ch = self.win.getch()
            ikiwa validate:
                ch = validate(ch)
            ikiwa sio ch:
                endelea
            ikiwa sio self.do_command(ch):
                koma
            self.win.refresh()
        rudisha self.gather()

ikiwa __name__ == '__main__':
    eleza test_editbox(stdscr):
        ncols, nlines = 9, 4
        uly, ulx = 15, 20
        stdscr.addstr(uly-2, ulx, "Use Ctrl-G to end editing.")
        win = curses.newwin(nlines, ncols, uly, ulx)
        rectangle(stdscr, uly-1, ulx-1, uly + nlines, ulx + ncols)
        stdscr.refresh()
        rudisha Textbox(win).edit()

    str = curses.wrapper(test_editbox)
    andika('Contents of text box:', repr(str))
