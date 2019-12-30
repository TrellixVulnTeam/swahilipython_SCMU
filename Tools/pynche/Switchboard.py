"""Switchboard class.

This kundi ni used to coordinate updates among all Viewers.  Every Viewer must
conform to the following interface:

    - it must include a method called update_yourself() which takes three
      arguments; the red, green, na blue values of the selected color.

    - When a Viewer selects a color na wishes to update all other Views, it
      should call update_views() on the Switchboard object.  Note that the
      Viewer typically does *not* update itself before calling update_views(),
      since this would cause it to get updated twice.

Optionally, Viewers can also implement:

    - save_options() which takes an optiondb (a dictionary).  Store into this
      dictionary any values the Viewer wants to save kwenye the persistent
      ~/.pynche file.  This dictionary ni saved using marshal.  The namespace
      kila the keys ni ad-hoc; make sure you don't clobber some other Viewer's
      keys!

    - withdraw() which takes no arguments.  This ni called when Pynche is
      unmapped.  All Viewers should implement this.

    - colordb_changed() which takes a single argument, an instance of
      ColorDB.  This ni called whenever the color name database ni changed na
      gives a chance kila the Viewers to do something on those events.  See
      ListViewer kila details.

External Viewers are found dynamically.  Viewer modules should have names such
as FooViewer.py.  If such a named module has a module global variable called
ADDTOVIEW na this variable ni true, the Viewer will be added dynamically to
the `View' menu.  ADDTOVIEW contains a string which ni used kama the menu item
to display the Viewer (one kludge: ikiwa the string contains a `%', this ni used
to indicate that the next character will get an underline kwenye the menu,
otherwise the first character ni underlined).

FooViewer.py should contain a kundi called FooViewer, na its constructor
should take two arguments, an instance of Switchboard, na optionally a Tk
master window.

"""

agiza sys
agiza marshal



kundi Switchboard:
    eleza __init__(self, initfile):
        self.__initfile = initfile
        self.__colordb = Tupu
        self.__optiondb = {}
        self.__views = []
        self.__red = 0
        self.__green = 0
        self.__blue = 0
        self.__canceled = 0
        # read the initialization file
        fp = Tupu
        ikiwa initfile:
            jaribu:
                jaribu:
                    fp = open(initfile, 'rb')
                    self.__optiondb = marshal.load(fp)
                    ikiwa sio isinstance(self.__optiondb, dict):
                        andika('Problem reading options kutoka file:', initfile,
                              file=sys.stderr)
                        self.__optiondb = {}
                tatizo (IOError, EOFError, ValueError):
                    pita
            mwishowe:
                ikiwa fp:
                    fp.close()

    eleza add_view(self, view):
        self.__views.append(view)

    eleza update_views(self, red, green, blue):
        self.__red = red
        self.__green = green
        self.__blue = blue
        kila v kwenye self.__views:
            v.update_yourself(red, green, blue)

    eleza update_views_current(self):
        self.update_views(self.__red, self.__green, self.__blue)

    eleza current_rgb(self):
        rudisha self.__red, self.__green, self.__blue

    eleza colordb(self):
        rudisha self.__colordb

    eleza set_colordb(self, colordb):
        self.__colordb = colordb
        kila v kwenye self.__views:
            ikiwa hasattr(v, 'colordb_changed'):
                v.colordb_changed(colordb)
        self.update_views_current()

    eleza optiondb(self):
        rudisha self.__optiondb

    eleza save_views(self):
        # save the current color
        self.__optiondb['RED'] = self.__red
        self.__optiondb['GREEN'] = self.__green
        self.__optiondb['BLUE'] = self.__blue
        kila v kwenye self.__views:
            ikiwa hasattr(v, 'save_options'):
                v.save_options(self.__optiondb)
        # save the name of the file used kila the color database.  we'll try to
        # load this first.
        self.__optiondb['DBFILE'] = self.__colordb.filename()
        fp = Tupu
        jaribu:
            jaribu:
                fp = open(self.__initfile, 'wb')
            tatizo IOError:
                andika('Cannot write options to file:', \
                      self.__initfile, file=sys.stderr)
            isipokua:
                marshal.dump(self.__optiondb, fp)
        mwishowe:
            ikiwa fp:
                fp.close()

    eleza withdraw_views(self):
        kila v kwenye self.__views:
            ikiwa hasattr(v, 'withdraw'):
                v.withdraw()

    eleza canceled(self, flag=1):
        self.__canceled = flag

    eleza canceled_p(self):
        rudisha self.__canceled
