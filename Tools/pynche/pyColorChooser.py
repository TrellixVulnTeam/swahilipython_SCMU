"""Color chooser implementing (almost) the tkColorColor interface
"""

agiza os
agiza Main
agiza ColorDB



kundi Chooser:
    """Ask kila a color"""
    eleza __init__(self,
                 master = Tupu,
                 databasefile = Tupu,
                 initfile = Tupu,
                 ignore = Tupu,
                 wantspec = Tupu):
        self.__master = master
        self.__databasefile = databasefile
        self.__initfile = initfile ama os.path.expanduser('~/.pynche')
        self.__ignore = ignore
        self.__pw = Tupu
        self.__wantspec = wantspec

    eleza show(self, color, options):
        # scan kila options that can override the ctor options
        self.__wantspec = options.get('wantspec', self.__wantspec)
        dbfile = options.get('databasefile', self.__databasefile)
        # load the database file
        colordb = Tupu
        ikiwa dbfile != self.__databasefile:
            colordb = ColorDB.get_colordb(dbfile)
        ikiwa sio self.__master:
            kutoka tkinter agiza Tk
            self.__master = Tk()
        ikiwa sio self.__pw:
            self.__pw, self.__sb = \
                       Main.build(master = self.__master,
                                  initfile = self.__initfile,
                                  ignore = self.__ignore)
        isipokua:
            self.__pw.deiconify()
        # convert color
        ikiwa colordb:
            self.__sb.set_colordb(colordb)
        isipokua:
            colordb = self.__sb.colordb()
        ikiwa color:
            r, g, b = Main.initial_color(color, colordb)
            self.__sb.update_views(r, g, b)
        # reset the canceled flag na run it
        self.__sb.canceled(0)
        Main.run(self.__pw, self.__sb)
        rgbtuple = self.__sb.current_rgb()
        self.__pw.withdraw()
        # check to see ikiwa the cancel button was pushed
        ikiwa self.__sb.canceled_p():
            rudisha Tupu, Tupu
        # Try to rudisha the color name kutoka the database ikiwa there ni an exact
        # match, otherwise use the "#rrggbb" spec.  BAW: Forget about color
        # aliases kila now, maybe later we should rudisha these too.
        name = Tupu
        ikiwa sio self.__wantspec:
            jaribu:
                name = colordb.find_byrgb(rgbtuple)[0]
            tatizo ColorDB.BadColor:
                pita
        ikiwa name ni Tupu:
            name = ColorDB.triplet_to_rrggbb(rgbtuple)
        rudisha rgbtuple, name

    eleza save(self):
        ikiwa self.__sb:
            self.__sb.save_views()


# convenience stuff
_chooser = Tupu

eleza askcolor(color = Tupu, **options):
    """Ask kila a color"""
    global _chooser
    ikiwa sio _chooser:
        _chooser = Chooser(**options)
    rudisha _chooser.show(color, options)

eleza save():
    global _chooser
    ikiwa _chooser:
        _chooser.save()


# test stuff
ikiwa __name__ == '__main__':
    kutoka tkinter agiza *

    kundi Tester:
        eleza __init__(self):
            self.__root = tk = Tk()
            b = Button(tk, text='Choose Color...', command=self.__choose)
            b.pack()
            self.__l = Label(tk)
            self.__l.pack()
            q = Button(tk, text='Quit', command=self.__quit)
            q.pack()

        eleza __choose(self, event=Tupu):
            rgb, name = askcolor(master=self.__root)
            ikiwa rgb ni Tupu:
                text = 'You hit CANCEL!'
            isipokua:
                r, g, b = rgb
                text = 'You picked %s (%3d/%3d/%3d)' % (name, r, g, b)
            self.__l.configure(text=text)

        eleza __quit(self, event=Tupu):
            self.__root.quit()

        eleza run(self):
            self.__root.mainloop()
    t = Tester()
    t.run()
    # simpler
##    andika 'color:', askcolor()
##    andika 'color:', askcolor()
