"""ListViewer class.

This kundi implements an input/output view on the color model.  It lists every
unique color (e.g. unique r/g/b value) found kwenye the color database.  Each
color ni shown by small swatch na primary color name.  Some colors have
aliases -- more than one name kila the same r/g/b value.  These aliases are
displayed kwenye the small listbox at the bottom of the screen.

Clicking on a color name ama swatch selects that color na updates all other
windows.  When a color ni selected kwenye a different viewer, the color list is
scrolled to the selected color na it ni highlighted.  If the selected color
is an r/g/b value without a name, no scrolling occurs.

You can turn off Update On Click ikiwa all you want to see ni the alias kila a
given name, without selecting the color.
"""

kutoka tkinter agiza *
agiza ColorDB

ADDTOVIEW = 'Color %List Window...'

kundi ListViewer:
    eleza __init__(self, switchboard, master=Tupu):
        self.__sb = switchboard
        optiondb = switchboard.optiondb()
        self.__lastbox = Tupu
        self.__dontcenter = 0
        # GUI
        root = self.__root = Toplevel(master, class_='Pynche')
        root.protocol('WM_DELETE_WINDOW', self.withdraw)
        root.title('Pynche Color List')
        root.iconname('Pynche Color List')
        root.bind('<Alt-q>', self.__quit)
        root.bind('<Alt-Q>', self.__quit)
        root.bind('<Alt-w>', self.withdraw)
        root.bind('<Alt-W>', self.withdraw)
        #
        # create the canvas which holds everything, na its scrollbar
        #
        frame = self.__frame = Frame(root)
        frame.pack()
        canvas = self.__canvas = Canvas(frame, width=160, height=300,
                                        borderwidth=2, relief=SUNKEN)
        self.__scrollbar = Scrollbar(frame)
        self.__scrollbar.pack(fill=Y, side=RIGHT)
        canvas.pack(fill=BOTH, expand=1)
        canvas.configure(yscrollcommand=(self.__scrollbar, 'set'))
        self.__scrollbar.configure(command=(canvas, 'yview'))
        self.__populate()
        #
        # Update on click
        self.__uoc = BooleanVar()
        self.__uoc.set(optiondb.get('UPONCLICK', 1))
        self.__uocbtn = Checkbutton(root,
                                    text='Update on Click',
                                    variable=self.__uoc,
                                    command=self.__toggleupdate)
        self.__uocbtn.pack(expand=1, fill=BOTH)
        #
        # alias list
        self.__alabel = Label(root, text='Aliases:')
        self.__alabel.pack()
        self.__aliases = Listbox(root, height=5,
                                 selectmode=BROWSE)
        self.__aliases.pack(expand=1, fill=BOTH)

    eleza __populate(self):
        #
        # create all the buttons
        colordb = self.__sb.colordb()
        canvas = self.__canvas
        row = 0
        widest = 0
        bboxes = self.__bboxes = []
        kila name kwenye colordb.unique_names():
            exactcolor = ColorDB.triplet_to_rrggbb(colordb.find_byname(name))
            canvas.create_rectangle(5, row*20 + 5,
                                    20, row*20 + 20,
                                    fill=exactcolor)
            textid = canvas.create_text(25, row*20 + 13,
                                        text=name,
                                        anchor=W)
            x1, y1, textend, y2 = canvas.bbox(textid)
            boxid = canvas.create_rectangle(3, row*20+3,
                                            textend+3, row*20 + 23,
                                            outline='',
                                            tags=(exactcolor, 'all'))
            canvas.bind('<ButtonRelease>', self.__onrelease)
            bboxes.append(boxid)
            ikiwa textend+3 > widest:
                widest = textend+3
            row += 1
        canvheight = (row-1)*20 + 25
        canvas.config(scrollregion=(0, 0, 150, canvheight))
        kila box kwenye bboxes:
            x1, y1, x2, y2 = canvas.coords(box)
            canvas.coords(box, x1, y1, widest, y2)

    eleza __onrelease(self, event=Tupu):
        canvas = self.__canvas
        # find the current box
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        ids = canvas.find_overlapping(x, y, x, y)
        kila boxid kwenye ids:
            ikiwa boxid kwenye self.__bboxes:
                koma
        isipokua:
##            print 'No box found!'
            rudisha
        tags = self.__canvas.gettags(boxid)
        kila t kwenye tags:
            ikiwa t[0] == '#':
                koma
        isipokua:
##            print 'No color tag found!'
            rudisha
        red, green, blue = ColorDB.rrggbb_to_triplet(t)
        self.__dontcenter = 1
        ikiwa self.__uoc.get():
            self.__sb.update_views(red, green, blue)
        isipokua:
            self.update_yourself(red, green, blue)
            self.__red, self.__green, self.__blue = red, green, blue

    eleza __toggleupdate(self, event=Tupu):
        ikiwa self.__uoc.get():
            self.__sb.update_views(self.__red, self.__green, self.__blue)

    eleza __quit(self, event=Tupu):
        self.__root.quit()

    eleza withdraw(self, event=Tupu):
        self.__root.withdraw()

    eleza deiconify(self, event=Tupu):
        self.__root.deiconify()

    eleza update_yourself(self, red, green, blue):
        canvas = self.__canvas
        # turn off the last box
        ikiwa self.__lastbox:
            canvas.itemconfigure(self.__lastbox, outline='')
        # turn on the current box
        colortag = ColorDB.triplet_to_rrggbb((red, green, blue))
        canvas.itemconfigure(colortag, outline='black')
        self.__lastbox = colortag
        # fill the aliases
        self.__aliases.delete(0, END)
        jaribu:
            aliases = self.__sb.colordb().aliases_of(red, green, blue)[1:]
        tatizo ColorDB.BadColor:
            self.__aliases.insert(END, '<no matching color>')
            rudisha
        ikiwa sio aliases:
            self.__aliases.insert(END, '<no aliases>')
        isipokua:
            kila name kwenye aliases:
                self.__aliases.insert(END, name)
        # maybe scroll the canvas so that the item ni visible
        ikiwa self.__dontcenter:
            self.__dontcenter = 0
        isipokua:
            ig, ig, ig, y1 = canvas.coords(colortag)
            ig, ig, ig, y2 = canvas.coords(self.__bboxes[-1])
            h = int(canvas['height']) * 0.5
            canvas.yview('moveto', (y1-h) / y2)

    eleza save_options(self, optiondb):
        optiondb['UPONCLICK'] = self.__uoc.get()

    eleza colordb_changed(self, colordb):
        self.__canvas.delete('all')
        self.__populate()
