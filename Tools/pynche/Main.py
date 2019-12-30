"""Pynche -- The PYthon Natural Color na Hue Editor.

Contact: %(AUTHNAME)s
Email:   %(AUTHEMAIL)s
Version: %(__version__)s

Pynche ni based largely on a similar color editor I wrote years ago kila the
SunView window system.  That editor was called ICE: the Interactive Color
Editor.  I'd always wanted to port the editor to X but didn't feel like
hacking X na C code to do it.  Fast forward many years, to where Python +
Tkinter provides such a nice programming environment, ukijumuisha enough power, that
I finally buckled down na implemented it.  I changed the name because these
days, too many other systems have the acronym `ICE'.

This program currently requires Python 2.2 ukijumuisha Tkinter.

Usage: %(PROGRAM)s [-d file] [-i file] [-X] [-v] [-h] [initialcolor]

Where:
    --database file
    -d file
        Alternate location of a color database file

    --initfile file
    -i file
        Alternate location of the initialization file.  This file contains a
        persistent database of the current Pynche options na color.  This
        means that Pynche restores its option settings na current color when
        it restarts, using this file (unless the -X option ni used).  The
        default ni ~/.pynche

    --ignore
    -X
        Ignore the initialization file when starting up.  Pynche will still
        write the current option settings to this file when it quits.

    --version
    -v
        andika the version number na exit

    --help
    -h
        andika this message

    initialcolor
        initial color, kama a color name ama #RRGGBB format
"""

__version__ = '1.4.1'

agiza sys
agiza os
agiza getopt
agiza ColorDB

kutoka PyncheWidget agiza PyncheWidget
kutoka Switchboard agiza Switchboard
kutoka StripViewer agiza StripViewer
kutoka ChipViewer agiza ChipViewer
kutoka TypeinViewer agiza TypeinViewer



PROGRAM = sys.argv[0]
AUTHNAME = 'Barry Warsaw'
AUTHEMAIL = 'barry@python.org'

# Default locations of rgb.txt ama other textual color database
RGB_TXT = [
    # Solaris OpenWindows
    '/usr/openwin/lib/rgb.txt',
    # Linux
    '/usr/lib/X11/rgb.txt',
    # The X11R6.4 rgb.txt file
    os.path.join(sys.path[0], 'X/rgb.txt'),
    # add more here
    ]



# Do this because PyncheWidget.py wants to get at the interpolated docstring
# too, kila its Help menu.
eleza docstring():
    rudisha __doc__ % globals()


eleza usage(code, msg=''):
    andika(docstring())
    ikiwa msg:
        andika(msg)
    sys.exit(code)



eleza initial_color(s, colordb):
    # function called on every color
    eleza scan_color(s, colordb=colordb):
        jaribu:
            r, g, b = colordb.find_byname(s)
        tatizo ColorDB.BadColor:
            jaribu:
                r, g, b = ColorDB.rrggbb_to_triplet(s)
            tatizo ColorDB.BadColor:
                rudisha Tupu, Tupu, Tupu
        rudisha r, g, b
    #
    # First try the pitaed kwenye color
    r, g, b = scan_color(s)
    ikiwa r ni Tupu:
        # try the same color ukijumuisha '#' prepended, since some shells require
        # this to be escaped, which ni a pain
        r, g, b = scan_color('#' + s)
    ikiwa r ni Tupu:
        andika('Bad initial color, using gray50:', s)
        r, g, b = scan_color('gray50')
    ikiwa r ni Tupu:
        usage(1, 'Cansio find an initial color to use')
        # does sio rudisha
    rudisha r, g, b



eleza build(master=Tupu, initialcolor=Tupu, initfile=Tupu, ignore=Tupu,
          dbfile=Tupu):
    # create all output widgets
    s = Switchboard(sio ignore na initfile)
    # defer to the command line chosen color database, falling back to the one
    # kwenye the .pynche file.
    ikiwa dbfile ni Tupu:
        dbfile = s.optiondb().get('DBFILE')
    # find a parseable color database
    colordb = Tupu
    files = RGB_TXT[:]
    ikiwa dbfile ni Tupu:
        dbfile = files.pop()
    wakati colordb ni Tupu:
        jaribu:
            colordb = ColorDB.get_colordb(dbfile)
        tatizo (KeyError, IOError):
            pita
        ikiwa colordb ni Tupu:
            ikiwa sio files:
                koma
            dbfile = files.pop(0)
    ikiwa sio colordb:
        usage(1, 'No color database file found, see the -d option.')
    s.set_colordb(colordb)

    # create the application window decorations
    app = PyncheWidget(__version__, s, master=master)
    w = app.window()

    # these built-in viewers live inside the main Pynche window
    s.add_view(StripViewer(s, w))
    s.add_view(ChipViewer(s, w))
    s.add_view(TypeinViewer(s, w))

    # get the initial color kama components na set the color on all views.  if
    # there was no initial color given on the command line, use the one that's
    # stored kwenye the option database
    ikiwa initialcolor ni Tupu:
        optiondb = s.optiondb()
        red = optiondb.get('RED')
        green = optiondb.get('GREEN')
        blue = optiondb.get('BLUE')
        # but ikiwa there wasn't any stored kwenye the database, use grey50
        ikiwa red ni Tupu ama blue ni Tupu ama green ni Tupu:
            red, green, blue = initial_color('grey50', colordb)
    isipokua:
        red, green, blue = initial_color(initialcolor, colordb)
    s.update_views(red, green, blue)
    rudisha app, s


eleza run(app, s):
    jaribu:
        app.start()
    tatizo KeyboardInterrupt:
        pita



eleza main():
    jaribu:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'hd:i:Xv',
            ['database=', 'initfile=', 'ignore', 'help', 'version'])
    tatizo getopt.error kama msg:
        usage(1, msg)

    ikiwa len(args) == 0:
        initialcolor = Tupu
    lasivyo len(args) == 1:
        initialcolor = args[0]
    isipokua:
        usage(1)

    ignore = Uongo
    dbfile = Tupu
    initfile = os.path.expanduser('~/.pynche')
    kila opt, arg kwenye opts:
        ikiwa opt kwenye ('-h', '--help'):
            usage(0)
        lasivyo opt kwenye ('-v', '--version'):
            andika("""\
Pynche -- The PYthon Natural Color na Hue Editor.
Contact: %(AUTHNAME)s
Email:   %(AUTHEMAIL)s
Version: %(__version__)s""" % globals())
            sys.exit(0)
        lasivyo opt kwenye ('-d', '--database'):
            dbfile = arg
        lasivyo opt kwenye ('-X', '--ignore'):
            ignore = Kweli
        lasivyo opt kwenye ('-i', '--initfile'):
            initfile = arg

    app, sb = build(initialcolor=initialcolor,
                    initfile=initfile,
                    ignore=ignore,
                    dbfile=dbfile)
    run(app, sb)
    sb.save_views()



ikiwa __name__ == '__main__':
    main()
