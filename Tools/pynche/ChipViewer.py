"""Chip viewer na widget.

In the lower left corner of the main Pynche window, you will see two
ChipWidgets, one kila the selected color na one kila the nearest color.  The
selected color ni the actual RGB value expressed kama an X11 #COLOR name. The
nearest color ni the named color kutoka the X11 database that ni closest to the
selected color kwenye 3D space.  There may be other colors equally close, but the
nearest one ni the first one found.

Clicking on the nearest color chip selects that named color.

The ChipViewer kundi includes the entire lower left quandrant; i.e. both the
selected na nearest ChipWidgets.
"""

kutoka tkinter agiza *
agiza ColorDB


kundi ChipWidget:
    _WIDTH = 150
    _HEIGHT = 80

    eleza __init__(self,
                 master = Tupu,
                 width  = _WIDTH,
                 height = _HEIGHT,
                 text   = 'Color',
                 initialcolor = 'blue',
                 presscmd   = Tupu,
                 releasecmd = Tupu):
        # create the text label
        self.__label = Label(master, text=text)
        self.__label.grid(row=0, column=0)
        # create the color chip, implemented kama a frame
        self.__chip = Frame(master, relief=RAISED, borderwidth=2,
                            width=width,
                            height=height,
                            background=initialcolor)
        self.__chip.grid(row=1, column=0)
        # create the color name
        self.__namevar = StringVar()
        self.__namevar.set(initialcolor)
        self.__name = Entry(master, textvariable=self.__namevar,
                            relief=FLAT, justify=CENTER, state=DISABLED,
                            font=self.__label['font'])
        self.__name.grid(row=2, column=0)
        # create the message area
        self.__msgvar = StringVar()
        self.__name = Entry(master, textvariable=self.__msgvar,
                            relief=FLAT, justify=CENTER, state=DISABLED,
                            font=self.__label['font'])
        self.__name.grid(row=3, column=0)
        # set bindings
        ikiwa presscmd:
            self.__chip.bind('<ButtonPress-1>', presscmd)
        ikiwa releasecmd:
            self.__chip.bind('<ButtonRelease-1>', releasecmd)

    eleza set_color(self, color):
        self.__chip.config(background=color)

    eleza get_color(self):
        rudisha self.__chip['background']

    eleza set_name(self, colorname):
        self.__namevar.set(colorname)

    eleza set_message(self, message):
        self.__msgvar.set(message)

    eleza press(self):
        self.__chip.configure(relief=SUNKEN)

    eleza release(self):
        self.__chip.configure(relief=RAISED)



kundi ChipViewer:
    eleza __init__(self, switchboard, master=Tupu):
        self.__sb = switchboard
        self.__frame = Frame(master, relief=RAISED, borderwidth=1)
        self.__frame.grid(row=3, column=0, ipadx=5, sticky='NSEW')
        # create the chip that will display the currently selected color
        # exactly
        self.__sframe = Frame(self.__frame)
        self.__sframe.grid(row=0, column=0)
        self.__selected = ChipWidget(self.__sframe, text='Selected')
        # create the chip that will display the nearest real X11 color
        # database color name
        self.__nframe = Frame(self.__frame)
        self.__nframe.grid(row=0, column=1)
        self.__nearest = ChipWidget(self.__nframe, text='Nearest',
                                    presscmd = self.__buttonpress,
                                    releasecmd = self.__buttonrelease)

    eleza update_yourself(self, red, green, blue):
        # Selected always shows the #rrggbb name of the color, nearest always
        # shows the name of the nearest color kwenye the database.  BAW: should
        # an exact match be indicated kwenye some way?
        #
        # Always use the #rrggbb style to actually set the color, since we may
        # sio be using X color names (e.g. "web-safe" names)
        colordb = self.__sb.colordb()
        rgbtuple = (red, green, blue)
        rrggbb = ColorDB.triplet_to_rrggbb(rgbtuple)
        # find the nearest
        nearest = colordb.nearest(red, green, blue)
        nearest_tuple = colordb.find_byname(nearest)
        nearest_rrggbb = ColorDB.triplet_to_rrggbb(nearest_tuple)
        self.__selected.set_color(rrggbb)
        self.__nearest.set_color(nearest_rrggbb)
        # set the name na messages areas
        self.__selected.set_name(rrggbb)
        ikiwa rrggbb == nearest_rrggbb:
            self.__selected.set_message(nearest)
        isipokua:
            self.__selected.set_message('')
        self.__nearest.set_name(nearest_rrggbb)
        self.__nearest.set_message(nearest)

    eleza __buttonpress(self, event=Tupu):
        self.__nearest.press()

    eleza __buttonrelease(self, event=Tupu):
        self.__nearest.release()
        rrggbb = self.__nearest.get_color()
        red, green, blue = ColorDB.rrggbb_to_triplet(rrggbb)
        self.__sb.update_views(red, green, blue)
