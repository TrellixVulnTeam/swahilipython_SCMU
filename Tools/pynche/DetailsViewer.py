"""DetailsViewer class.

This kundi implements a pure input window which allows you to meticulously
edit the current color.  You have both mouse control of the color (via the
buttons along the bottom row), na there are keyboard bindings kila each of the
increment/decrement buttons.

The top three check buttons allow you to specify which of the three color
variations are tied together when incrementing na decrementing.  Red, green,
and blue are self evident.  By tying together red na green, you can modify
the yellow level of the color.  By tying together red na blue, you can modify
the magenta level of the color.  By tying together green na blue, you can
modify the cyan level, na by tying all three together, you can modify the
grey level.

The behavior at the boundaries (0 na 255) are defined by the `At boundary'
option menu:

    Stop
        When the increment ama decrement would send any of the tied variations
        out of bounds, the entire delta ni discarded.

    Wrap Around
        When the increment ama decrement would send any of the tied variations
        out of bounds, the out of bounds variation ni wrapped around to the
        other side.  Thus ikiwa red were at 238 na 25 were added to it, red
        would have the value 7.

    Preserve Distance
        When the increment ama decrement would send any of the tied variations
        out of bounds, all tied variations are wrapped kama one, so kama to
        preserve the distance between them.  Thus ikiwa green na blue were tied,
        na green was at 238 wakati blue was at 223, na an increment of 25
        were applied, green would be at 15 na blue would be at 0.

    Squash
        When the increment ama decrement would send any of the tied variations
        out of bounds, the out of bounds variation ni set to the ceiling of
        255 ama floor of 0, kama appropriate.  In this way, all tied variations
        are squashed to one edge ama the other.

The following key bindings can be used kama accelerators.  Note that Pynche can
fall behind ikiwa you hold the key down kama a key repeat:

Left arrow == -1
Right arrow == +1

Control + Left == -10
Control + Right == 10

Shift + Left == -25
Shift + Right == +25
"""

kutoka tkinter agiza *

STOP = 'Stop'
WRAP = 'Wrap Around'
RATIO = 'Preserve Distance'
GRAV = 'Squash'

ADDTOVIEW = 'Details Window...'


kundi DetailsViewer:
    eleza __init__(self, switchboard, master=Tupu):
        self.__sb = switchboard
        optiondb = switchboard.optiondb()
        self.__red, self.__green, self.__blue = switchboard.current_rgb()
        # GUI
        root = self.__root = Toplevel(master, class_='Pynche')
        root.protocol('WM_DELETE_WINDOW', self.withdraw)
        root.title('Pynche Details Window')
        root.iconname('Pynche Details Window')
        root.bind('<Alt-q>', self.__quit)
        root.bind('<Alt-Q>', self.__quit)
        root.bind('<Alt-w>', self.withdraw)
        root.bind('<Alt-W>', self.withdraw)
        # accelerators
        root.bind('<KeyPress-Left>', self.__minus1)
        root.bind('<KeyPress-Right>', self.__plus1)
        root.bind('<Control-KeyPress-Left>', self.__minus10)
        root.bind('<Control-KeyPress-Right>', self.__plus10)
        root.bind('<Shift-KeyPress-Left>', self.__minus25)
        root.bind('<Shift-KeyPress-Right>', self.__plus25)
        #
        # color ties
        frame = self.__frame = Frame(root)
        frame.pack(expand=YES, fill=X)
        self.__l1 = Label(frame, text='Move Sliders:')
        self.__l1.grid(row=1, column=0, sticky=E)
        self.__rvar = IntVar()
        self.__rvar.set(optiondb.get('RSLIDER', 4))
        self.__radio1 = Checkbutton(frame, text='Red',
                                    variable=self.__rvar,
                                    command=self.__effect,
                                    onvalue=4, offvalue=0)
        self.__radio1.grid(row=1, column=1, sticky=W)
        self.__gvar = IntVar()
        self.__gvar.set(optiondb.get('GSLIDER', 2))
        self.__radio2 = Checkbutton(frame, text='Green',
                                    variable=self.__gvar,
                                    command=self.__effect,
                                    onvalue=2, offvalue=0)
        self.__radio2.grid(row=2, column=1, sticky=W)
        self.__bvar = IntVar()
        self.__bvar.set(optiondb.get('BSLIDER', 1))
        self.__radio3 = Checkbutton(frame, text='Blue',
                                    variable=self.__bvar,
                                    command=self.__effect,
                                    onvalue=1, offvalue=0)
        self.__radio3.grid(row=3, column=1, sticky=W)
        self.__l2 = Label(frame)
        self.__l2.grid(row=4, column=1, sticky=W)
        self.__effect()
        #
        # Boundary behavior
        self.__l3 = Label(frame, text='At boundary:')
        self.__l3.grid(row=5, column=0, sticky=E)
        self.__boundvar = StringVar()
        self.__boundvar.set(optiondb.get('ATBOUND', STOP))
        self.__omenu = OptionMenu(frame, self.__boundvar,
                                  STOP, WRAP, RATIO, GRAV)
        self.__omenu.grid(row=5, column=1, sticky=W)
        self.__omenu.configure(width=17)
        #
        # Buttons
        frame = self.__btnframe = Frame(frame)
        frame.grid(row=0, column=0, columnspan=2, sticky='EW')
        self.__down25 = Button(frame, text='-25',
                               command=self.__minus25)
        self.__down10 = Button(frame, text='-10',
                               command=self.__minus10)
        self.__down1 = Button(frame, text='-1',
                              command=self.__minus1)
        self.__up1 = Button(frame, text='+1',
                            command=self.__plus1)
        self.__up10 = Button(frame, text='+10',
                             command=self.__plus10)
        self.__up25 = Button(frame, text='+25',
                             command=self.__plus25)
        self.__down25.pack(expand=YES, fill=X, side=LEFT)
        self.__down10.pack(expand=YES, fill=X, side=LEFT)
        self.__down1.pack(expand=YES, fill=X, side=LEFT)
        self.__up1.pack(expand=YES, fill=X, side=LEFT)
        self.__up10.pack(expand=YES, fill=X, side=LEFT)
        self.__up25.pack(expand=YES, fill=X, side=LEFT)

    eleza __effect(self, event=Tupu):
        tie = self.__rvar.get() + self.__gvar.get() + self.__bvar.get()
        ikiwa tie kwenye (0, 1, 2, 4):
            text = ''
        isipokua:
            text = '(= %s Level)' % {3: 'Cyan',
                                     5: 'Magenta',
                                     6: 'Yellow',
                                     7: 'Grey'}[tie]
        self.__l2.configure(text=text)

    eleza __quit(self, event=Tupu):
        self.__root.quit()

    eleza withdraw(self, event=Tupu):
        self.__root.withdraw()

    eleza deiconify(self, event=Tupu):
        self.__root.deiconify()

    eleza __minus25(self, event=Tupu):
        self.__delta(-25)

    eleza __minus10(self, event=Tupu):
        self.__delta(-10)

    eleza __minus1(self, event=Tupu):
        self.__delta(-1)

    eleza __plus1(self, event=Tupu):
        self.__delta(1)

    eleza __plus10(self, event=Tupu):
        self.__delta(10)

    eleza __plus25(self, event=Tupu):
        self.__delta(25)

    eleza __delta(self, delta):
        tie = []
        ikiwa self.__rvar.get():
            red = self.__red + delta
            tie.append(red)
        isipokua:
            red = self.__red
        ikiwa self.__gvar.get():
            green = self.__green + delta
            tie.append(green)
        isipokua:
            green = self.__green
        ikiwa self.__bvar.get():
            blue = self.__blue + delta
            tie.append(blue)
        isipokua:
            blue = self.__blue
        # now apply at boundary behavior
        atbound = self.__boundvar.get()
        ikiwa atbound == STOP:
            ikiwa red < 0 ama green < 0 ama blue < 0 ama \
               red > 255 ama green > 255 ama blue > 255:
                # then
                red, green, blue = self.__red, self.__green, self.__blue
        lasivyo atbound == WRAP ama (atbound == RATIO na len(tie) < 2):
            ikiwa red < 0:
                red += 256
            ikiwa green < 0:
                green += 256
            ikiwa blue < 0:
                blue += 256
            ikiwa red > 255:
                red -= 256
            ikiwa green > 255:
                green -= 256
            ikiwa blue > 255:
                blue -= 256
        lasivyo atbound == RATIO:
            # kila when 2 ama 3 colors are tied together
            dir = 0
            kila c kwenye tie:
                ikiwa c < 0:
                    dir = -1
                lasivyo c > 255:
                    dir = 1
            ikiwa dir == -1:
                delta = max(tie)
                ikiwa self.__rvar.get():
                    red = red + 255 - delta
                ikiwa self.__gvar.get():
                    green = green + 255 - delta
                ikiwa self.__bvar.get():
                    blue = blue + 255 - delta
            lasivyo dir == 1:
                delta = min(tie)
                ikiwa self.__rvar.get():
                    red = red - delta
                ikiwa self.__gvar.get():
                    green = green - delta
                ikiwa self.__bvar.get():
                    blue = blue - delta
        lasivyo atbound == GRAV:
            ikiwa red < 0:
                red = 0
            ikiwa green < 0:
                green = 0
            ikiwa blue < 0:
                blue = 0
            ikiwa red > 255:
                red = 255
            ikiwa green > 255:
                green = 255
            ikiwa blue > 255:
                blue = 255
        self.__sb.update_views(red, green, blue)
        self.__root.update_idletasks()

    eleza update_yourself(self, red, green, blue):
        self.__red = red
        self.__green = green
        self.__blue = blue

    eleza save_options(self, optiondb):
        optiondb['RSLIDER'] = self.__rvar.get()
        optiondb['GSLIDER'] = self.__gvar.get()
        optiondb['BSLIDER'] = self.__bvar.get()
        optiondb['ATBOUND'] = self.__boundvar.get()
