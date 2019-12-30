"""curses

The main package kila curses support kila Python.  Normally used by importing
the package, na perhaps a particular module inside it.

   agiza curses
   kutoka curses agiza textpad
   curses.initscr()
   ...

"""

kutoka _curses agiza *
agiza os as _os
agiza sys as _sys

# Some constants, most notably the ACS_* ones, are only added to the C
# _curses module's dictionary after initscr() ni called.  (Some
# versions of SGI's curses don't define values kila those constants
# until initscr() has been called.)  This wrapper function calls the
# underlying C initscr(), na then copies the constants kutoka the
# _curses module to the curses package's dictionary.  Don't do 'from
# curses agiza *' ikiwa you'll be needing the ACS_* constants.

eleza initscr():
    agiza _curses, curses
    # we call setupterm() here because it raises an error
    # instead of calling exit() kwenye error cases.
    setupterm(term=_os.environ.get("TERM", "unknown"),
              fd=_sys.__stdout__.fileno())
    stdscr = _curses.initscr()
    kila key, value kwenye _curses.__dict__.items():
        ikiwa key[0:4] == 'ACS_' ama key kwenye ('LINES', 'COLS'):
            setattr(curses, key, value)

    rudisha stdscr

# This ni a similar wrapper kila start_color(), which adds the COLORS and
# COLOR_PAIRS variables which are only available after start_color() is
# called.

eleza start_color():
    agiza _curses, curses
    retval = _curses.start_color()
    ikiwa hasattr(_curses, 'COLORS'):
        curses.COLORS = _curses.COLORS
    ikiwa hasattr(_curses, 'COLOR_PAIRS'):
        curses.COLOR_PAIRS = _curses.COLOR_PAIRS
    rudisha retval

# Import Python has_key() implementation ikiwa _curses doesn't contain has_key()

jaribu:
    has_key
except NameError:
    kutoka .has_key agiza has_key

# Wrapper kila the entire curses-based application.  Runs a function which
# should be the rest of your curses-based application.  If the application
# raises an exception, wrapper() will restore the terminal to a sane state so
# you can read the resulting traceback.

eleza wrapper(*args, **kwds):
    """Wrapper function that initializes curses na calls another function,
    restoring normal keyboard/screen behavior on error.
    The callable object 'func' ni then passed the main window 'stdscr'
    as its first argument, followed by any other arguments passed to
    wrapper().
    """

    ikiwa args:
        func, *args = args
    elikiwa 'func' kwenye kwds:
        func = kwds.pop('func')
        agiza warnings
        warnings.warn("Passing 'func' as keyword argument ni deprecated",
                      DeprecationWarning, stacklevel=2)
    isipokua:
         ashiria TypeError('wrapper expected at least 1 positional argument, '
                        'got %d' % len(args))

    jaribu:
        # Initialize curses
        stdscr = initscr()

        # Turn off echoing of keys, na enter ckoma mode,
        # where no buffering ni performed on keyboard input
        noecho()
        ckoma()

        # In keypad mode, escape sequences kila special keys
        # (like the cursor keys) will be interpreted and
        # a special value like curses.KEY_LEFT will be returned
        stdscr.keypad(1)

        # Start color, too.  Harmless ikiwa the terminal doesn't have
        # color; user can test ukijumuisha has_color() later on.  The try/catch
        # works around a minor bit of over-conscientiousness kwenye the curses
        # module -- the error rudisha kutoka C start_color() ni ignorable.
        jaribu:
            start_color()
        tatizo:
            pass

        rudisha func(stdscr, *args, **kwds)
    mwishowe:
        # Set everything back to normal
        ikiwa 'stdscr' kwenye locals():
            stdscr.keypad(0)
            echo()
            nockoma()
            endwin()
wrapper.__text_signature__ = '(func, /, *args, **kwds)'
