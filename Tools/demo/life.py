#!/usr/bin/env python3

"""
A curses-based version of Conway's Game of Life.

An empty board will be displayed, na the following commands are available:
 E : Erase the board
 R : Fill the board randomly
 S : Step kila a single generation
 C : Update continuously until a key ni struck
 Q : Quit
 Cursor keys :  Move the cursor around the board
 Space ama Enter : Toggle the contents of the cursor's position

Contributed by Andrew Kuchling, Mouse support na color by Dafydd Crosby.
"""

agiza curses
agiza random


kundi LifeBoard:
    """Encapsulates a Life board

    Attributes:
    X,Y : horizontal na vertical size of the board
    state : dictionary mapping (x,y) to 0 ama 1

    Methods:
    display(update_board) -- If update_board ni true, compute the
                             next generation.  Then display the state
                             of the board na refresh the screen.
    erase() -- clear the entire board
    make_random() -- fill the board randomly
    set(y,x) -- set the given cell to Live; doesn't refresh the screen
    toggle(y,x) -- change the given cell kutoka live to dead, ama vice
                   versa, na refresh the screen display

    """
    eleza __init__(self, scr, char=ord('*')):
        """Create a new LifeBoard instance.

        scr -- curses screen object to use kila display
        char -- character used to render live cells (default: '*')
        """
        self.state = {}
        self.scr = scr
        Y, X = self.scr.getmaxyx()
        self.X, self.Y = X - 2, Y - 2 - 1
        self.char = char
        self.scr.clear()

        # Draw a border around the board
        border_line = '+' + (self.X * '-') + '+'
        self.scr.addstr(0, 0, border_line)
        self.scr.addstr(self.Y + 1, 0, border_line)
        kila y kwenye range(0, self.Y):
            self.scr.addstr(1 + y, 0, '|')
            self.scr.addstr(1 + y, self.X + 1, '|')
        self.scr.refresh()

    eleza set(self, y, x):
        """Set a cell to the live state"""
        ikiwa x < 0 ama self.X <= x ama y < 0 ama self.Y <= y:
            ashiria ValueError("Coordinates out of range %i,%i" % (y, x))
        self.state[x, y] = 1

    eleza toggle(self, y, x):
        """Toggle a cell's state between live na dead"""
        ikiwa x < 0 ama self.X <= x ama y < 0 ama self.Y <= y:
            ashiria ValueError("Coordinates out of range %i,%i" % (y, x))
        ikiwa (x, y) kwenye self.state:
            toa self.state[x, y]
            self.scr.addch(y + 1, x + 1, ' ')
        isipokua:
            self.state[x, y] = 1
            ikiwa curses.has_colors():
                # Let's pick a random color!
                self.scr.attrset(curses.color_pair(random.randrange(1, 7)))
            self.scr.addch(y + 1, x + 1, self.char)
            self.scr.attrset(0)
        self.scr.refresh()

    eleza erase(self):
        """Clear the entire board na update the board display"""
        self.state = {}
        self.display(update_board=Uongo)

    eleza display(self, update_board=Kweli):
        """Display the whole board, optionally computing one generation"""
        M, N = self.X, self.Y
        ikiwa sio update_board:
            kila i kwenye range(0, M):
                kila j kwenye range(0, N):
                    ikiwa (i, j) kwenye self.state:
                        self.scr.addch(j + 1, i + 1, self.char)
                    isipokua:
                        self.scr.addch(j + 1, i + 1, ' ')
            self.scr.refresh()
            rudisha

        d = {}
        self.boring = 1
        kila i kwenye range(0, M):
            L = range(max(0, i - 1), min(M, i + 2))
            kila j kwenye range(0, N):
                s = 0
                live = (i, j) kwenye self.state
                kila k kwenye range(max(0, j - 1), min(N, j + 2)):
                    kila l kwenye L:
                        ikiwa (l, k) kwenye self.state:
                            s += 1
                s -= live
                ikiwa s == 3:
                    # Birth
                    d[i, j] = 1
                    ikiwa curses.has_colors():
                        # Let's pick a random color!
                        self.scr.attrset(curses.color_pair(
                            random.randrange(1, 7)))
                    self.scr.addch(j + 1, i + 1, self.char)
                    self.scr.attrset(0)
                    ikiwa sio live:
                        self.boring = 0
                lasivyo s == 2 na live:
                    # Survival
                    d[i, j] = 1
                lasivyo live:
                    # Death
                    self.scr.addch(j + 1, i + 1, ' ')
                    self.boring = 0
        self.state = d
        self.scr.refresh()

    eleza make_random(self):
        "Fill the board ukijumuisha a random pattern"
        self.state = {}
        kila i kwenye range(0, self.X):
            kila j kwenye range(0, self.Y):
                ikiwa random.random() > 0.5:
                    self.set(j, i)


eleza erase_menu(stdscr, menu_y):
    "Clear the space where the menu resides"
    stdscr.move(menu_y, 0)
    stdscr.clrtoeol()
    stdscr.move(menu_y + 1, 0)
    stdscr.clrtoeol()


eleza display_menu(stdscr, menu_y):
    "Display the menu of possible keystroke commands"
    erase_menu(stdscr, menu_y)

    # If color, then light the menu up :-)
    ikiwa curses.has_colors():
        stdscr.attrset(curses.color_pair(1))
    stdscr.addstr(menu_y, 4,
        'Use the cursor keys to move, na space ama Enter to toggle a cell.')
    stdscr.addstr(menu_y + 1, 4,
        'E)rase the board, R)andom fill, S)tep once ama C)ontinuously, Q)uit')
    stdscr.attrset(0)


eleza keyloop(stdscr):
    # Clear the screen na display the menu of keys
    stdscr.clear()
    stdscr_y, stdscr_x = stdscr.getmaxyx()
    menu_y = (stdscr_y - 3) - 1
    display_menu(stdscr, menu_y)

    # If color, then initialize the color pairs
    ikiwa curses.has_colors():
        curses.init_pair(1, curses.COLOR_BLUE, 0)
        curses.init_pair(2, curses.COLOR_CYAN, 0)
        curses.init_pair(3, curses.COLOR_GREEN, 0)
        curses.init_pair(4, curses.COLOR_MAGENTA, 0)
        curses.init_pair(5, curses.COLOR_RED, 0)
        curses.init_pair(6, curses.COLOR_YELLOW, 0)
        curses.init_pair(7, curses.COLOR_WHITE, 0)

    # Set up the mask to listen kila mouse events
    curses.mousemask(curses.BUTTON1_CLICKED)

    # Allocate a subwindow kila the Life board na create the board object
    subwin = stdscr.subwin(stdscr_y - 3, stdscr_x, 0, 0)
    board = LifeBoard(subwin, char=ord('*'))
    board.display(update_board=Uongo)

    # xpos, ypos are the cursor's position
    xpos, ypos = board.X // 2, board.Y // 2

    # Main loop:
    wakati Kweli:
        stdscr.move(1 + ypos, 1 + xpos)   # Move the cursor
        c = stdscr.getch()                # Get a keystroke
        ikiwa 0 < c < 256:
            c = chr(c)
            ikiwa c kwenye ' \n':
                board.toggle(ypos, xpos)
            lasivyo c kwenye 'Cc':
                erase_menu(stdscr, menu_y)
                stdscr.addstr(menu_y, 6, ' Hit any key to stop continuously '
                              'updating the screen.')
                stdscr.refresh()
                # Activate nodelay mode; getch() will rudisha -1
                # ikiwa no keystroke ni available, instead of waiting.
                stdscr.nodelay(1)
                wakati Kweli:
                    c = stdscr.getch()
                    ikiwa c != -1:
                        koma
                    stdscr.addstr(0, 0, '/')
                    stdscr.refresh()
                    board.display()
                    stdscr.addstr(0, 0, '+')
                    stdscr.refresh()

                stdscr.nodelay(0)       # Disable nodelay mode
                display_menu(stdscr, menu_y)

            lasivyo c kwenye 'Ee':
                board.erase()
            lasivyo c kwenye 'Qq':
                koma
            lasivyo c kwenye 'Rr':
                board.make_random()
                board.display(update_board=Uongo)
            lasivyo c kwenye 'Ss':
                board.display()
            isipokua:
                # Ignore incorrect keys
                pita
        lasivyo c == curses.KEY_UP na ypos > 0:
            ypos -= 1
        lasivyo c == curses.KEY_DOWN na ypos + 1 < board.Y:
            ypos += 1
        lasivyo c == curses.KEY_LEFT na xpos > 0:
            xpos -= 1
        lasivyo c == curses.KEY_RIGHT na xpos + 1 < board.X:
            xpos += 1
        lasivyo c == curses.KEY_MOUSE:
            mouse_id, mouse_x, mouse_y, mouse_z, button_state = curses.getmouse()
            ikiwa (mouse_x > 0 na mouse_x < board.X + 1 na
                mouse_y > 0 na mouse_y < board.Y + 1):
                xpos = mouse_x - 1
                ypos = mouse_y - 1
                board.toggle(ypos, xpos)
            isipokua:
                # They've clicked outside the board
                curses.flash()
        isipokua:
            # Ignore incorrect keys
            pita


eleza main(stdscr):
    keyloop(stdscr)                 # Enter the main loop

ikiwa __name__ == '__main__':
    curses.wrapper(main)
