#
# turtle.py: a Tkinter based turtle graphics module kila Python
# Version 1.1b - 4. 5. 2009
#
# Copyright (C) 2006 - 2010  Gregor Lingl
# email: glingl@aon.at
#
# This software ni provided 'as-is', without any express ama implied
# warranty.  In no event will the authors be held liable kila any damages
# arising kutoka the use of this software.
#
# Permission ni granted to anyone to use this software kila any purpose,
# including commercial applications, na to alter it na redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must sio be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    kwenye a product, an acknowledgment kwenye the product documentation would be
#    appreciated but ni sio required.
# 2. Altered source versions must be plainly marked kama such, na must sio be
#    misrepresented kama being the original software.
# 3. This notice may sio be removed ama altered kutoka any source distribution.


"""
Turtle graphics ni a popular way kila introducing programming to
kids. It was part of the original Logo programming language developed
by Wally Feurzig na Seymour Papert kwenye 1966.

Imagine a robotic turtle starting at (0, 0) kwenye the x-y plane. After an ``agiza turtle``, give it
the command turtle.forward(15), na it moves (on-screen!) 15 pixels in
the direction it ni facing, drawing a line kama it moves. Give it the
command turtle.right(25), na it rotates in-place 25 degrees clockwise.

By combining together these na similar commands, intricate shapes na
pictures can easily be drawn.

----- turtle.py

This module ni an extended reimplementation of turtle.py kutoka the
Python standard distribution up to Python 2.5. (See: http://www.python.org)

It tries to keep the merits of turtle.py na to be (nearly) 100%
compatible ukijumuisha it. This means kwenye the first place to enable the
learning programmer to use all the commands, classes na methods
interactively when using the module kutoka within IDLE run with
the -n switch.

Roughly it has the following features added:

- Better animation of the turtle movements, especially of turning the
  turtle. So the turtles can more easily be used kama a visual feedback
  instrument by the (beginning) programmer.

- Different turtle shapes, gif-images kama turtle shapes, user defined
  na user controllable turtle shapes, among them compound
  (multicolored) shapes. Turtle shapes can be stretched na tilted, which
  makes turtles very versatile geometrical objects.

- Fine control over turtle movement na screen updates via delay(),
  na enhanced tracer() na speed() methods.

- Aliases kila the most commonly used commands, like fd kila forward etc.,
  following the early Logo traditions. This reduces the boring work of
  typing long sequences of commands, which often occur kwenye a natural way
  when kids try to program fancy pictures on their first encounter with
  turtle graphics.

- Turtles now have an undo()-method ukijumuisha configurable undo-buffer.

- Some simple commands/methods kila creating event driven programs
  (mouse-, key-, timer-events). Especially useful kila programming games.

- A scrollable Canvas class. The default scrollable Canvas can be
  extended interactively kama needed wakati playing around ukijumuisha the turtle(s).

- A TurtleScreen kundi ukijumuisha methods controlling background color ama
  background image, window na canvas size na other properties of the
  TurtleScreen.

- There ni a method, setworldcoordinates(), to install a user defined
  coordinate-system kila the TurtleScreen.

- The implementation uses a 2-vector kundi named Vec2D, derived kutoka tuple.
  This kundi ni public, so it can be imported by the application programmer,
  which makes certain types of computations very natural na compact.

- Appearance of the TurtleScreen na the Turtles at startup/agiza can be
  configured by means of a turtle.cfg configuration file.
  The default configuration mimics the appearance of the old turtle module.

- If configured appropriately the module reads kwenye docstrings kutoka a docstring
  dictionary kwenye some different language, supplied separately  na replaces
  the English ones by those read in. There ni a utility function
  write_docstringdict() to write a dictionary ukijumuisha the original (English)
  docstrings to disc, so it can serve kama a template kila translations.

Behind the scenes there are some features included ukijumuisha possible
extensions kwenye mind. These will be commented na documented elsewhere.

"""

_ver = "turtle 1.1b- - kila Python 3.1   -  4. 5. 2009"

# andika(_ver)

agiza tkinter kama TK
agiza types
agiza math
agiza time
agiza inspect
agiza sys

kutoka os.path agiza isfile, split, join
kutoka copy agiza deepcopy
kutoka tkinter agiza simpledialog

_tg_classes = ['ScrolledCanvas', 'TurtleScreen', 'Screen',
               'RawTurtle', 'Turtle', 'RawPen', 'Pen', 'Shape', 'Vec2D']
_tg_screen_functions = ['addshape', 'bgcolor', 'bgpic', 'bye',
        'clearscreen', 'colormode', 'delay', 'exitonclick', 'getcanvas',
        'getshapes', 'listen', 'mainloop', 'mode', 'numinput',
        'onkey', 'onkeypress', 'onkeyrelease', 'onscreenclick', 'ontimer',
        'register_shape', 'resetscreen', 'screensize', 'setup',
        'setworldcoordinates', 'textinput', 'title', 'tracer', 'turtles', 'update',
        'window_height', 'window_width']
_tg_turtle_functions = ['back', 'backward', 'begin_fill', 'begin_poly', 'bk',
        'circle', 'clear', 'clearstamp', 'clearstamps', 'clone', 'color',
        'degrees', 'distance', 'dot', 'down', 'end_fill', 'end_poly', 'fd',
        'fillcolor', 'filling', 'forward', 'get_poly', 'getpen', 'getscreen', 'get_shapepoly',
        'getturtle', 'goto', 'heading', 'hideturtle', 'home', 'ht', 'isdown',
        'isvisible', 'left', 'lt', 'onclick', 'ondrag', 'onrelease', 'pd',
        'pen', 'pencolor', 'pendown', 'pensize', 'penup', 'pos', 'position',
        'pu', 'radians', 'right', 'reset', 'resizemode', 'rt',
        'seth', 'setheading', 'setpos', 'setposition', 'settiltangle',
        'setundobuffer', 'setx', 'sety', 'shape', 'shapesize', 'shapetransform', 'shearfactor', 'showturtle',
        'speed', 'st', 'stamp', 'tilt', 'tiltangle', 'towards',
        'turtlesize', 'undo', 'undobufferentries', 'up', 'width',
        'write', 'xcor', 'ycor']
_tg_utilities = ['write_docstringdict', 'done']

__all__ = (_tg_classes + _tg_screen_functions + _tg_turtle_functions +
           _tg_utilities + ['Terminator']) # + _math_functions)

_alias_list = ['addshape', 'backward', 'bk', 'fd', 'ht', 'lt', 'pd', 'pos',
               'pu', 'rt', 'seth', 'setpos', 'setposition', 'st',
               'turtlesize', 'up', 'width']

_CFG = {"width" : 0.5,               # Screen
        "height" : 0.75,
        "canvwidth" : 400,
        "canvheight": 300,
        "leftright": Tupu,
        "topbottom": Tupu,
        "mode": "standard",          # TurtleScreen
        "colormode": 1.0,
        "delay": 10,
        "undobuffersize": 1000,      # RawTurtle
        "shape": "classic",
        "pencolor" : "black",
        "fillcolor" : "black",
        "resizemode" : "noresize",
        "visible" : Kweli,
        "language": "english",        # docstrings
        "exampleturtle": "turtle",
        "examplescreen": "screen",
        "title": "Python Turtle Graphics",
        "using_IDLE": Uongo
       }

eleza config_dict(filename):
    """Convert content of config-file into dictionary."""
    ukijumuisha open(filename, "r") kama f:
        cfglines = f.readlines()
    cfgdict = {}
    kila line kwenye cfglines:
        line = line.strip()
        ikiwa sio line ama line.startswith("#"):
            endelea
        jaribu:
            key, value = line.split("=")
        tatizo ValueError:
            andika("Bad line kwenye config-file %s:\n%s" % (filename,line))
            endelea
        key = key.strip()
        value = value.strip()
        ikiwa value kwenye ["Kweli", "Uongo", "Tupu", "''", '""']:
            value = eval(value)
        isipokua:
            jaribu:
                ikiwa "." kwenye value:
                    value = float(value)
                isipokua:
                    value = int(value)
            tatizo ValueError:
                pita # value need sio be converted
        cfgdict[key] = value
    rudisha cfgdict

eleza readconfig(cfgdict):
    """Read config-files, change configuration-dict accordingly.

    If there ni a turtle.cfg file kwenye the current working directory,
    read it kutoka there. If this contains an importconfig-value,
    say 'myway', construct filename turtle_mayway.cfg isipokua use
    turtle.cfg na read it kutoka the import-directory, where
    turtle.py ni located.
    Update configuration dictionary first according to config-file,
    kwenye the agiza directory, then according to config-file kwenye the
    current working directory.
    If no config-file ni found, the default configuration ni used.
    """
    default_cfg = "turtle.cfg"
    cfgdict1 = {}
    cfgdict2 = {}
    ikiwa isfile(default_cfg):
        cfgdict1 = config_dict(default_cfg)
    ikiwa "importconfig" kwenye cfgdict1:
        default_cfg = "turtle_%s.cfg" % cfgdict1["importconfig"]
    jaribu:
        head, tail = split(__file__)
        cfg_file2 = join(head, default_cfg)
    tatizo Exception:
        cfg_file2 = ""
    ikiwa isfile(cfg_file2):
        cfgdict2 = config_dict(cfg_file2)
    _CFG.update(cfgdict2)
    _CFG.update(cfgdict1)

jaribu:
    readconfig(_CFG)
tatizo Exception:
    print ("No configfile read, reason unknown")


kundi Vec2D(tuple):
    """A 2 dimensional vector class, used kama a helper class
    kila implementing turtle graphics.
    May be useful kila turtle graphics programs also.
    Derived kutoka tuple, so a vector ni a tuple!

    Provides (kila a, b vectors, k number):
       a+b vector addition
       a-b vector subtraction
       a*b inner product
       k*a na a*k multiplication ukijumuisha scalar
       |a| absolute value of a
       a.rotate(angle) rotation
    """
    eleza __new__(cls, x, y):
        rudisha tuple.__new__(cls, (x, y))
    eleza __add__(self, other):
        rudisha Vec2D(self[0]+other[0], self[1]+other[1])
    eleza __mul__(self, other):
        ikiwa isinstance(other, Vec2D):
            rudisha self[0]*other[0]+self[1]*other[1]
        rudisha Vec2D(self[0]*other, self[1]*other)
    eleza __rmul__(self, other):
        ikiwa isinstance(other, int) ama isinstance(other, float):
            rudisha Vec2D(self[0]*other, self[1]*other)
    eleza __sub__(self, other):
        rudisha Vec2D(self[0]-other[0], self[1]-other[1])
    eleza __neg__(self):
        rudisha Vec2D(-self[0], -self[1])
    eleza __abs__(self):
        rudisha (self[0]**2 + self[1]**2)**0.5
    eleza rotate(self, angle):
        """rotate self counterclockwise by angle
        """
        perp = Vec2D(-self[1], self[0])
        angle = angle * math.pi / 180.0
        c, s = math.cos(angle), math.sin(angle)
        rudisha Vec2D(self[0]*c+perp[0]*s, self[1]*c+perp[1]*s)
    eleza __getnewargs__(self):
        rudisha (self[0], self[1])
    eleza __repr__(self):
        rudisha "(%.2f,%.2f)" % self


##############################################################################
### From here up to line    : Tkinter - Interface kila turtle.py            ###
### May be replaced by an interface to some different graphics toolkit     ###
##############################################################################

## helper functions kila Scrolled Canvas, to forward Canvas-methods
## to ScrolledCanvas class

eleza __methodDict(cls, _dict):
    """helper function kila Scrolled Canvas"""
    baseList = list(cls.__bases__)
    baseList.reverse()
    kila _super kwenye baseList:
        __methodDict(_super, _dict)
    kila key, value kwenye cls.__dict__.items():
        ikiwa type(value) == types.FunctionType:
            _dict[key] = value

eleza __methods(cls):
    """helper function kila Scrolled Canvas"""
    _dict = {}
    __methodDict(cls, _dict)
    rudisha _dict.keys()

__stringBody = (
    'eleza %(method)s(self, *args, **kw): rudisha ' +
    'self.%(attribute)s.%(method)s(*args, **kw)')

eleza __forwardmethods(fromClass, toClass, toPart, exclude = ()):
    ### MANY CHANGES ###
    _dict_1 = {}
    __methodDict(toClass, _dict_1)
    _dict = {}
    mfc = __methods(fromClass)
    kila ex kwenye _dict_1.keys():
        ikiwa ex[:1] == '_' ama ex[-1:] == '_' ama ex kwenye exclude ama ex kwenye mfc:
            pita
        isipokua:
            _dict[ex] = _dict_1[ex]

    kila method, func kwenye _dict.items():
        d = {'method': method, 'func': func}
        ikiwa isinstance(toPart, str):
            execString = \
                __stringBody % {'method' : method, 'attribute' : toPart}
        exec(execString, d)
        setattr(fromClass, method, d[method])   ### NEWU!


kundi ScrolledCanvas(TK.Frame):
    """Modeled after the scrolled canvas kundi kutoka Grayons's Tkinter book.

    Used kama the default canvas, which pops up automatically when
    using turtle graphics functions ama the Turtle class.
    """
    eleza __init__(self, master, width=500, height=350,
                                          canvwidth=600, canvheight=500):
        TK.Frame.__init__(self, master, width=width, height=height)
        self._rootwindow = self.winfo_toplevel()
        self.width, self.height = width, height
        self.canvwidth, self.canvheight = canvwidth, canvheight
        self.bg = "white"
        self._canvas = TK.Canvas(master, width=width, height=height,
                                 bg=self.bg, relief=TK.SUNKEN, borderwidth=2)
        self.hscroll = TK.Scrollbar(master, command=self._canvas.xview,
                                    orient=TK.HORIZONTAL)
        self.vscroll = TK.Scrollbar(master, command=self._canvas.yview)
        self._canvas.configure(xscrollcommand=self.hscroll.set,
                               yscrollcommand=self.vscroll.set)
        self.rowconfigure(0, weight=1, minsize=0)
        self.columnconfigure(0, weight=1, minsize=0)
        self._canvas.grid(padx=1, in_ = self, pady=1, row=0,
                column=0, rowspan=1, columnspan=1, sticky='news')
        self.vscroll.grid(padx=1, in_ = self, pady=1, row=0,
                column=1, rowspan=1, columnspan=1, sticky='news')
        self.hscroll.grid(padx=1, in_ = self, pady=1, row=1,
                column=0, rowspan=1, columnspan=1, sticky='news')
        self.reset()
        self._rootwindow.bind('<Configure>', self.onResize)

    eleza reset(self, canvwidth=Tupu, canvheight=Tupu, bg = Tupu):
        """Adjust canvas na scrollbars according to given canvas size."""
        ikiwa canvwidth:
            self.canvwidth = canvwidth
        ikiwa canvheight:
            self.canvheight = canvheight
        ikiwa bg:
            self.bg = bg
        self._canvas.config(bg=bg,
                        scrollregion=(-self.canvwidth//2, -self.canvheight//2,
                                       self.canvwidth//2, self.canvheight//2))
        self._canvas.xview_moveto(0.5*(self.canvwidth - self.width + 30) /
                                                               self.canvwidth)
        self._canvas.yview_moveto(0.5*(self.canvheight- self.height + 30) /
                                                              self.canvheight)
        self.adjustScrolls()


    eleza adjustScrolls(self):
        """ Adjust scrollbars according to window- na canvas-size.
        """
        cwidth = self._canvas.winfo_width()
        cheight = self._canvas.winfo_height()
        self._canvas.xview_moveto(0.5*(self.canvwidth-cwidth)/self.canvwidth)
        self._canvas.yview_moveto(0.5*(self.canvheight-cheight)/self.canvheight)
        ikiwa cwidth < self.canvwidth ama cheight < self.canvheight:
            self.hscroll.grid(padx=1, in_ = self, pady=1, row=1,
                              column=0, rowspan=1, columnspan=1, sticky='news')
            self.vscroll.grid(padx=1, in_ = self, pady=1, row=0,
                              column=1, rowspan=1, columnspan=1, sticky='news')
        isipokua:
            self.hscroll.grid_forget()
            self.vscroll.grid_forget()

    eleza onResize(self, event):
        """self-explanatory"""
        self.adjustScrolls()

    eleza bbox(self, *args):
        """ 'forward' method, which canvas itself has inherited...
        """
        rudisha self._canvas.bbox(*args)

    eleza cget(self, *args, **kwargs):
        """ 'forward' method, which canvas itself has inherited...
        """
        rudisha self._canvas.cget(*args, **kwargs)

    eleza config(self, *args, **kwargs):
        """ 'forward' method, which canvas itself has inherited...
        """
        self._canvas.config(*args, **kwargs)

    eleza bind(self, *args, **kwargs):
        """ 'forward' method, which canvas itself has inherited...
        """
        self._canvas.bind(*args, **kwargs)

    eleza unbind(self, *args, **kwargs):
        """ 'forward' method, which canvas itself has inherited...
        """
        self._canvas.unbind(*args, **kwargs)

    eleza focus_force(self):
        """ 'forward' method, which canvas itself has inherited...
        """
        self._canvas.focus_force()

__forwardmethods(ScrolledCanvas, TK.Canvas, '_canvas')


kundi _Root(TK.Tk):
    """Root kundi kila Screen based on Tkinter."""
    eleza __init__(self):
        TK.Tk.__init__(self)

    eleza setupcanvas(self, width, height, cwidth, cheight):
        self._canvas = ScrolledCanvas(self, width, height, cwidth, cheight)
        self._canvas.pack(expand=1, fill="both")

    eleza _getcanvas(self):
        rudisha self._canvas

    eleza set_geometry(self, width, height, startx, starty):
        self.geometry("%dx%d%+d%+d"%(width, height, startx, starty))

    eleza ondestroy(self, destroy):
        self.wm_protocol("WM_DELETE_WINDOW", destroy)

    eleza win_width(self):
        rudisha self.winfo_screenwidth()

    eleza win_height(self):
        rudisha self.winfo_screenheight()

Canvas = TK.Canvas


kundi TurtleScreenBase(object):
    """Provide the basic graphics functionality.
       Interface between Tkinter na turtle.py.

       To port turtle.py to some different graphics toolkit
       a corresponding TurtleScreenBase kundi has to be implemented.
    """

    @staticmethod
    eleza _blankimage():
        """rudisha a blank image object
        """
        img = TK.PhotoImage(width=1, height=1)
        img.blank()
        rudisha img

    @staticmethod
    eleza _image(filename):
        """rudisha an image object containing the
        imagedata kutoka a gif-file named filename.
        """
        rudisha TK.PhotoImage(file=filename)

    eleza __init__(self, cv):
        self.cv = cv
        ikiwa isinstance(cv, ScrolledCanvas):
            w = self.cv.canvwidth
            h = self.cv.canvheight
        isipokua:  # expected: ordinary TK.Canvas
            w = int(self.cv.cget("width"))
            h = int(self.cv.cget("height"))
            self.cv.config(scrollregion = (-w//2, -h//2, w//2, h//2 ))
        self.canvwidth = w
        self.canvheight = h
        self.xscale = self.yscale = 1.0

    eleza _createpoly(self):
        """Create an invisible polygon item on canvas self.cv)
        """
        rudisha self.cv.create_polygon((0, 0, 0, 0, 0, 0), fill="", outline="")

    eleza _drawpoly(self, polyitem, coordlist, fill=Tupu,
                  outline=Tupu, width=Tupu, top=Uongo):
        """Configure polygonitem polyitem according to provided
        arguments:
        coordlist ni sequence of coordinates
        fill ni filling color
        outline ni outline color
        top ni a boolean value, which specifies ikiwa polyitem
        will be put on top of the canvas' displaylist so it
        will sio be covered by other items.
        """
        cl = []
        kila x, y kwenye coordlist:
            cl.append(x * self.xscale)
            cl.append(-y * self.yscale)
        self.cv.coords(polyitem, *cl)
        ikiwa fill ni sio Tupu:
            self.cv.itemconfigure(polyitem, fill=fill)
        ikiwa outline ni sio Tupu:
            self.cv.itemconfigure(polyitem, outline=outline)
        ikiwa width ni sio Tupu:
            self.cv.itemconfigure(polyitem, width=width)
        ikiwa top:
            self.cv.tag_raise(polyitem)

    eleza _createline(self):
        """Create an invisible line item on canvas self.cv)
        """
        rudisha self.cv.create_line(0, 0, 0, 0, fill="", width=2,
                                   capstyle = TK.ROUND)

    eleza _drawline(self, lineitem, coordlist=Tupu,
                  fill=Tupu, width=Tupu, top=Uongo):
        """Configure lineitem according to provided arguments:
        coordlist ni sequence of coordinates
        fill ni drawing color
        width ni width of drawn line.
        top ni a boolean value, which specifies ikiwa polyitem
        will be put on top of the canvas' displaylist so it
        will sio be covered by other items.
        """
        ikiwa coordlist ni sio Tupu:
            cl = []
            kila x, y kwenye coordlist:
                cl.append(x * self.xscale)
                cl.append(-y * self.yscale)
            self.cv.coords(lineitem, *cl)
        ikiwa fill ni sio Tupu:
            self.cv.itemconfigure(lineitem, fill=fill)
        ikiwa width ni sio Tupu:
            self.cv.itemconfigure(lineitem, width=width)
        ikiwa top:
            self.cv.tag_raise(lineitem)

    eleza _delete(self, item):
        """Delete graphics item kutoka canvas.
        If item is"all" delete all graphics items.
        """
        self.cv.delete(item)

    eleza _update(self):
        """Redraw graphics items on canvas
        """
        self.cv.update()

    eleza _delay(self, delay):
        """Delay subsequent canvas actions kila delay ms."""
        self.cv.after(delay)

    eleza _iscolorstring(self, color):
        """Check ikiwa the string color ni a legal Tkinter color string.
        """
        jaribu:
            rgb = self.cv.winfo_rgb(color)
            ok = Kweli
        tatizo TK.TclError:
            ok = Uongo
        rudisha ok

    eleza _bgcolor(self, color=Tupu):
        """Set canvas' backgroundcolor ikiwa color ni sio Tupu,
        isipokua rudisha backgroundcolor."""
        ikiwa color ni sio Tupu:
            self.cv.config(bg = color)
            self._update()
        isipokua:
            rudisha self.cv.cget("bg")

    eleza _write(self, pos, txt, align, font, pencolor):
        """Write txt at pos kwenye canvas ukijumuisha specified font
        na color.
        Return text item na x-coord of right bottom corner
        of text's bounding box."""
        x, y = pos
        x = x * self.xscale
        y = y * self.yscale
        anchor = {"left":"sw", "center":"s", "right":"se" }
        item = self.cv.create_text(x-1, -y, text = txt, anchor = anchor[align],
                                        fill = pencolor, font = font)
        x0, y0, x1, y1 = self.cv.bbox(item)
        self.cv.update()
        rudisha item, x1-1

##    eleza _dot(self, pos, size, color):
##        """may be implemented kila some other graphics toolkit"""

    eleza _onclick(self, item, fun, num=1, add=Tupu):
        """Bind fun to mouse-click event on turtle.
        fun must be a function ukijumuisha two arguments, the coordinates
        of the clicked point on the canvas.
        num, the number of the mouse-button defaults to 1
        """
        ikiwa fun ni Tupu:
            self.cv.tag_unbind(item, "<Button-%s>" % num)
        isipokua:
            eleza eventfun(event):
                x, y = (self.cv.canvasx(event.x)/self.xscale,
                        -self.cv.canvasy(event.y)/self.yscale)
                fun(x, y)
            self.cv.tag_bind(item, "<Button-%s>" % num, eventfun, add)

    eleza _onrelease(self, item, fun, num=1, add=Tupu):
        """Bind fun to mouse-button-release event on turtle.
        fun must be a function ukijumuisha two arguments, the coordinates
        of the point on the canvas where mouse button ni released.
        num, the number of the mouse-button defaults to 1

        If a turtle ni clicked, first _onclick-event will be performed,
        then _onscreensclick-event.
        """
        ikiwa fun ni Tupu:
            self.cv.tag_unbind(item, "<Button%s-ButtonRelease>" % num)
        isipokua:
            eleza eventfun(event):
                x, y = (self.cv.canvasx(event.x)/self.xscale,
                        -self.cv.canvasy(event.y)/self.yscale)
                fun(x, y)
            self.cv.tag_bind(item, "<Button%s-ButtonRelease>" % num,
                             eventfun, add)

    eleza _ondrag(self, item, fun, num=1, add=Tupu):
        """Bind fun to mouse-move-event (ukijumuisha pressed mouse button) on turtle.
        fun must be a function ukijumuisha two arguments, the coordinates of the
        actual mouse position on the canvas.
        num, the number of the mouse-button defaults to 1

        Every sequence of mouse-move-events on a turtle ni preceded by a
        mouse-click event on that turtle.
        """
        ikiwa fun ni Tupu:
            self.cv.tag_unbind(item, "<Button%s-Motion>" % num)
        isipokua:
            eleza eventfun(event):
                jaribu:
                    x, y = (self.cv.canvasx(event.x)/self.xscale,
                           -self.cv.canvasy(event.y)/self.yscale)
                    fun(x, y)
                tatizo Exception:
                    pita
            self.cv.tag_bind(item, "<Button%s-Motion>" % num, eventfun, add)

    eleza _onscreenclick(self, fun, num=1, add=Tupu):
        """Bind fun to mouse-click event on canvas.
        fun must be a function ukijumuisha two arguments, the coordinates
        of the clicked point on the canvas.
        num, the number of the mouse-button defaults to 1

        If a turtle ni clicked, first _onclick-event will be performed,
        then _onscreensclick-event.
        """
        ikiwa fun ni Tupu:
            self.cv.unbind("<Button-%s>" % num)
        isipokua:
            eleza eventfun(event):
                x, y = (self.cv.canvasx(event.x)/self.xscale,
                        -self.cv.canvasy(event.y)/self.yscale)
                fun(x, y)
            self.cv.bind("<Button-%s>" % num, eventfun, add)

    eleza _onkeyrelease(self, fun, key):
        """Bind fun to key-release event of key.
        Canvas must have focus. See method listen
        """
        ikiwa fun ni Tupu:
            self.cv.unbind("<KeyRelease-%s>" % key, Tupu)
        isipokua:
            eleza eventfun(event):
                fun()
            self.cv.bind("<KeyRelease-%s>" % key, eventfun)

    eleza _onkeypress(self, fun, key=Tupu):
        """If key ni given, bind fun to key-press event of key.
        Otherwise bind fun to any key-press.
        Canvas must have focus. See method listen.
        """
        ikiwa fun ni Tupu:
            ikiwa key ni Tupu:
                self.cv.unbind("<KeyPress>", Tupu)
            isipokua:
                self.cv.unbind("<KeyPress-%s>" % key, Tupu)
        isipokua:
            eleza eventfun(event):
                fun()
            ikiwa key ni Tupu:
                self.cv.bind("<KeyPress>", eventfun)
            isipokua:
                self.cv.bind("<KeyPress-%s>" % key, eventfun)

    eleza _listen(self):
        """Set focus on canvas (in order to collect key-events)
        """
        self.cv.focus_force()

    eleza _ontimer(self, fun, t):
        """Install a timer, which calls fun after t milliseconds.
        """
        ikiwa t == 0:
            self.cv.after_idle(fun)
        isipokua:
            self.cv.after(t, fun)

    eleza _createimage(self, image):
        """Create na rudisha image item on canvas.
        """
        rudisha self.cv.create_image(0, 0, image=image)

    eleza _drawimage(self, item, pos, image):
        """Configure image item kama to draw image object
        at position (x,y) on canvas)
        """
        x, y = pos
        self.cv.coords(item, (x * self.xscale, -y * self.yscale))
        self.cv.itemconfig(item, image=image)

    eleza _setbgpic(self, item, image):
        """Configure image item kama to draw image object
        at center of canvas. Set item to the first item
        kwenye the displaylist, so it will be drawn below
        any other item ."""
        self.cv.itemconfig(item, image=image)
        self.cv.tag_lower(item)

    eleza _type(self, item):
        """Return 'line' ama 'polygon' ama 'image' depending on
        type of item.
        """
        rudisha self.cv.type(item)

    eleza _pointlist(self, item):
        """returns list of coordinate-pairs of points of item
        Example (kila insiders):
        >>> kutoka turtle agiza *
        >>> getscreen()._pointlist(getturtle().turtle._item)
        [(0.0, 9.9999999999999982), (0.0, -9.9999999999999982),
        (9.9999999999999982, 0.0)]
        >>> """
        cl = self.cv.coords(item)
        pl = [(cl[i], -cl[i+1]) kila i kwenye range(0, len(cl), 2)]
        rudisha  pl

    eleza _setscrollregion(self, srx1, sry1, srx2, sry2):
        self.cv.config(scrollregion=(srx1, sry1, srx2, sry2))

    eleza _rescale(self, xscalefactor, yscalefactor):
        items = self.cv.find_all()
        kila item kwenye items:
            coordinates = list(self.cv.coords(item))
            newcoordlist = []
            wakati coordinates:
                x, y = coordinates[:2]
                newcoordlist.append(x * xscalefactor)
                newcoordlist.append(y * yscalefactor)
                coordinates = coordinates[2:]
            self.cv.coords(item, *newcoordlist)

    eleza _resize(self, canvwidth=Tupu, canvheight=Tupu, bg=Tupu):
        """Resize the canvas the turtles are drawing on. Does
        sio alter the drawing window.
        """
        # needs amendment
        ikiwa sio isinstance(self.cv, ScrolledCanvas):
            rudisha self.canvwidth, self.canvheight
        ikiwa canvwidth ni canvheight ni bg ni Tupu:
            rudisha self.cv.canvwidth, self.cv.canvheight
        ikiwa canvwidth ni sio Tupu:
            self.canvwidth = canvwidth
        ikiwa canvheight ni sio Tupu:
            self.canvheight = canvheight
        self.cv.reset(canvwidth, canvheight, bg)

    eleza _window_size(self):
        """ Return the width na height of the turtle window.
        """
        width = self.cv.winfo_width()
        ikiwa width <= 1:  # the window isn't managed by a geometry manager
            width = self.cv['width']
        height = self.cv.winfo_height()
        ikiwa height <= 1: # the window isn't managed by a geometry manager
            height = self.cv['height']
        rudisha width, height

    eleza mainloop(self):
        """Starts event loop - calling Tkinter's mainloop function.

        No argument.

        Must be last statement kwenye a turtle graphics program.
        Must NOT be used ikiwa a script ni run kutoka within IDLE kwenye -n mode
        (No subprocess) - kila interactive use of turtle graphics.

        Example (kila a TurtleScreen instance named screen):
        >>> screen.mainloop()

        """
        TK.mainloop()

    eleza textuliza(self, title, prompt):
        """Pop up a dialog window kila input of a string.

        Arguments: title ni the title of the dialog window,
        prompt ni a text mostly describing what information to input.

        Return the string input
        If the dialog ni canceled, rudisha Tupu.

        Example (kila a TurtleScreen instance named screen):
        >>> screen.textuliza("NIM", "Name of first player:")

        """
        rudisha simpledialog.askstring(title, prompt)

    eleza numuliza(self, title, prompt, default=Tupu, minval=Tupu, maxval=Tupu):
        """Pop up a dialog window kila input of a number.

        Arguments: title ni the title of the dialog window,
        prompt ni a text mostly describing what numerical information to input.
        default: default value
        minval: minimum value kila input
        maxval: maximum value kila input

        The number input must be kwenye the range minval .. maxval ikiwa these are
        given. If not, a hint ni issued na the dialog remains open for
        correction. Return the number input.
        If the dialog ni canceled,  rudisha Tupu.

        Example (kila a TurtleScreen instance named screen):
        >>> screen.numuliza("Poker", "Your stakes:", 1000, minval=10, maxval=10000)

        """
        rudisha simpledialog.askfloat(title, prompt, initialvalue=default,
                                     minvalue=minval, maxvalue=maxval)


##############################################################################
###                  End of Tkinter - interface                            ###
##############################################################################


kundi Terminator (Exception):
    """Will be raised kwenye TurtleScreen.update, ikiwa _RUNNING becomes Uongo.

    This stops execution of a turtle graphics script.
    Main purpose: use kwenye the Demo-Viewer turtle.Demo.py.
    """
    pita


kundi TurtleGraphicsError(Exception):
    """Some TurtleGraphics Error
    """


kundi Shape(object):
    """Data structure modeling shapes.

    attribute _type ni one of "polygon", "image", "compound"
    attribute _data ni - depending on _type a poygon-tuple,
    an image ama a list constructed using the addcomponent method.
    """
    eleza __init__(self, type_, data=Tupu):
        self._type = type_
        ikiwa type_ == "polygon":
            ikiwa isinstance(data, list):
                data = tuple(data)
        lasivyo type_ == "image":
            ikiwa isinstance(data, str):
                ikiwa data.lower().endswith(".gif") na isfile(data):
                    data = TurtleScreen._image(data)
                # isipokua data assumed to be Photoimage
        lasivyo type_ == "compound":
            data = []
        isipokua:
            ashiria TurtleGraphicsError("There ni no shape type %s" % type_)
        self._data = data

    eleza addcomponent(self, poly, fill, outline=Tupu):
        """Add component to a shape of type compound.

        Arguments: poly ni a polygon, i. e. a tuple of number pairs.
        fill ni the fillcolor of the component,
        outline ni the outline color of the component.

        call (kila a Shapeobject namend s):
        --   s.addcomponent(((0,0), (10,10), (-10,10)), "red", "blue")

        Example:
        >>> poly = ((0,0),(10,-5),(0,10),(-10,-5))
        >>> s = Shape("compound")
        >>> s.addcomponent(poly, "red", "blue")
        >>> # .. add more components na then use register_shape()
        """
        ikiwa self._type != "compound":
            ashiria TurtleGraphicsError("Cannot add component to %s Shape"
                                                                % self._type)
        ikiwa outline ni Tupu:
            outline = fill
        self._data.append([poly, fill, outline])


kundi Tbuffer(object):
    """Ring buffer used kama undobuffer kila RawTurtle objects."""
    eleza __init__(self, bufsize=10):
        self.bufsize = bufsize
        self.buffer = [[Tupu]] * bufsize
        self.ptr = -1
        self.cumulate = Uongo
    eleza reset(self, bufsize=Tupu):
        ikiwa bufsize ni Tupu:
            kila i kwenye range(self.bufsize):
                self.buffer[i] = [Tupu]
        isipokua:
            self.bufsize = bufsize
            self.buffer = [[Tupu]] * bufsize
        self.ptr = -1
    eleza push(self, item):
        ikiwa self.bufsize > 0:
            ikiwa sio self.cumulate:
                self.ptr = (self.ptr + 1) % self.bufsize
                self.buffer[self.ptr] = item
            isipokua:
                self.buffer[self.ptr].append(item)
    eleza pop(self):
        ikiwa self.bufsize > 0:
            item = self.buffer[self.ptr]
            ikiwa item ni Tupu:
                rudisha Tupu
            isipokua:
                self.buffer[self.ptr] = [Tupu]
                self.ptr = (self.ptr - 1) % self.bufsize
                rudisha (item)
    eleza nr_of_items(self):
        rudisha self.bufsize - self.buffer.count([Tupu])
    eleza __repr__(self):
        rudisha str(self.buffer) + " " + str(self.ptr)



kundi TurtleScreen(TurtleScreenBase):
    """Provides screen oriented methods like setbg etc.

    Only relies upon the methods of TurtleScreenBase na NOT
    upon components of the underlying graphics toolkit -
    which ni Tkinter kwenye this case.
    """
    _RUNNING = Kweli

    eleza __init__(self, cv, mode=_CFG["mode"],
                 colormode=_CFG["colormode"], delay=_CFG["delay"]):
        self._shapes = {
                   "arrow" : Shape("polygon", ((-10,0), (10,0), (0,10))),
                  "turtle" : Shape("polygon", ((0,16), (-2,14), (-1,10), (-4,7),
                              (-7,9), (-9,8), (-6,5), (-7,1), (-5,-3), (-8,-6),
                              (-6,-8), (-4,-5), (0,-7), (4,-5), (6,-8), (8,-6),
                              (5,-3), (7,1), (6,5), (9,8), (7,9), (4,7), (1,10),
                              (2,14))),
                  "circle" : Shape("polygon", ((10,0), (9.51,3.09), (8.09,5.88),
                              (5.88,8.09), (3.09,9.51), (0,10), (-3.09,9.51),
                              (-5.88,8.09), (-8.09,5.88), (-9.51,3.09), (-10,0),
                              (-9.51,-3.09), (-8.09,-5.88), (-5.88,-8.09),
                              (-3.09,-9.51), (-0.00,-10.00), (3.09,-9.51),
                              (5.88,-8.09), (8.09,-5.88), (9.51,-3.09))),
                  "square" : Shape("polygon", ((10,-10), (10,10), (-10,10),
                              (-10,-10))),
                "triangle" : Shape("polygon", ((10,-5.77), (0,11.55),
                              (-10,-5.77))),
                  "classic": Shape("polygon", ((0,0),(-5,-9),(0,-7),(5,-9))),
                   "blank" : Shape("image", self._blankimage())
                  }

        self._bgpics = {"nopic" : ""}

        TurtleScreenBase.__init__(self, cv)
        self._mode = mode
        self._delayvalue = delay
        self._colormode = _CFG["colormode"]
        self._keys = []
        self.clear()
        ikiwa sys.platform == 'darwin':
            # Force Turtle window to the front on OS X. This ni needed because
            # the Turtle window will show behind the Terminal window when you
            # start the demo kutoka the command line.
            rootwindow = cv.winfo_toplevel()
            rootwindow.call('wm', 'attributes', '.', '-topmost', '1')
            rootwindow.call('wm', 'attributes', '.', '-topmost', '0')

    eleza clear(self):
        """Delete all drawings na all turtles kutoka the TurtleScreen.

        No argument.

        Reset empty TurtleScreen to its initial state: white background,
        no backgroundimage, no eventbindings na tracing on.

        Example (kila a TurtleScreen instance named screen):
        >>> screen.clear()

        Note: this method ni sio available kama function.
        """
        self._delayvalue = _CFG["delay"]
        self._colormode = _CFG["colormode"]
        self._delete("all")
        self._bgpic = self._createimage("")
        self._bgpicname = "nopic"
        self._tracing = 1
        self._updatecounter = 0
        self._turtles = []
        self.bgcolor("white")
        kila btn kwenye 1, 2, 3:
            self.onclick(Tupu, btn)
        self.onkeypress(Tupu)
        kila key kwenye self._keys[:]:
            self.onkey(Tupu, key)
            self.onkeypress(Tupu, key)
        Turtle._pen = Tupu

    eleza mode(self, mode=Tupu):
        """Set turtle-mode ('standard', 'logo' ama 'world') na perform reset.

        Optional argument:
        mode -- one of the strings 'standard', 'logo' ama 'world'

        Mode 'standard' ni compatible ukijumuisha turtle.py.
        Mode 'logo' ni compatible ukijumuisha most Logo-Turtle-Graphics.
        Mode 'world' uses userdefined 'worldcoordinates'. *Attention*: in
        this mode angles appear distorted ikiwa x/y unit-ratio doesn't equal 1.
        If mode ni sio given, rudisha the current mode.

             Mode      Initial turtle heading     positive angles
         ------------|-------------------------|-------------------
          'standard'    to the right (east)       counterclockwise
            'logo'        upward    (north)         clockwise

        Examples:
        >>> mode('logo')   # resets turtle heading to north
        >>> mode()
        'logo'
        """
        ikiwa mode ni Tupu:
            rudisha self._mode
        mode = mode.lower()
        ikiwa mode haiko kwenye ["standard", "logo", "world"]:
            ashiria TurtleGraphicsError("No turtle-graphics-mode %s" % mode)
        self._mode = mode
        ikiwa mode kwenye ["standard", "logo"]:
            self._setscrollregion(-self.canvwidth//2, -self.canvheight//2,
                                       self.canvwidth//2, self.canvheight//2)
            self.xscale = self.yscale = 1.0
        self.reset()

    eleza setworldcoordinates(self, llx, lly, urx, ury):
        """Set up a user defined coordinate-system.

        Arguments:
        llx -- a number, x-coordinate of lower left corner of canvas
        lly -- a number, y-coordinate of lower left corner of canvas
        urx -- a number, x-coordinate of upper right corner of canvas
        ury -- a number, y-coordinate of upper right corner of canvas

        Set up user coodinat-system na switch to mode 'world' ikiwa necessary.
        This performs a screen.reset. If mode 'world' ni already active,
        all drawings are redrawn according to the new coordinates.

        But ATTENTION: kwenye user-defined coordinatesystems angles may appear
        distorted. (see Screen.mode())

        Example (kila a TurtleScreen instance named screen):
        >>> screen.setworldcoordinates(-10,-0.5,50,1.5)
        >>> kila _ kwenye range(36):
        ...     left(10)
        ...     forward(0.5)
        """
        ikiwa self.mode() != "world":
            self.mode("world")
        xspan = float(urx - llx)
        yspan = float(ury - lly)
        wx, wy = self._window_size()
        self.screensize(wx-20, wy-20)
        oldxscale, oldyscale = self.xscale, self.yscale
        self.xscale = self.canvwidth / xspan
        self.yscale = self.canvheight / yspan
        srx1 = llx * self.xscale
        sry1 = -ury * self.yscale
        srx2 = self.canvwidth + srx1
        sry2 = self.canvheight + sry1
        self._setscrollregion(srx1, sry1, srx2, sry2)
        self._rescale(self.xscale/oldxscale, self.yscale/oldyscale)
        self.update()

    eleza register_shape(self, name, shape=Tupu):
        """Adds a turtle shape to TurtleScreen's shapelist.

        Arguments:
        (1) name ni the name of a gif-file na shape ni Tupu.
            Installs the corresponding image shape.
            !! Image-shapes DO NOT rotate when turning the turtle,
            !! so they do sio display the heading of the turtle!
        (2) name ni an arbitrary string na shape ni a tuple
            of pairs of coordinates. Installs the corresponding
            polygon shape
        (3) name ni an arbitrary string na shape ni a
            (compound) Shape object. Installs the corresponding
            compound shape.
        To use a shape, you have to issue the command shape(shapename).

        call: register_shape("turtle.gif")
        --or: register_shape("tri", ((0,0), (10,10), (-10,10)))

        Example (kila a TurtleScreen instance named screen):
        >>> screen.register_shape("triangle", ((5,-3),(0,5),(-5,-3)))

        """
        ikiwa shape ni Tupu:
            # image
            ikiwa name.lower().endswith(".gif"):
                shape = Shape("image", self._image(name))
            isipokua:
                ashiria TurtleGraphicsError("Bad arguments kila register_shape.\n"
                                          + "Use  help(register_shape)" )
        lasivyo isinstance(shape, tuple):
            shape = Shape("polygon", shape)
        ## isipokua shape assumed to be Shape-instance
        self._shapes[name] = shape

    eleza _colorstr(self, color):
        """Return color string corresponding to args.

        Argument may be a string ama a tuple of three
        numbers corresponding to actual colormode,
        i.e. kwenye the range 0<=n<=colormode.

        If the argument doesn't represent a color,
        an error ni raised.
        """
        ikiwa len(color) == 1:
            color = color[0]
        ikiwa isinstance(color, str):
            ikiwa self._iscolorstring(color) ama color == "":
                rudisha color
            isipokua:
                ashiria TurtleGraphicsError("bad color string: %s" % str(color))
        jaribu:
            r, g, b = color
        tatizo (TypeError, ValueError):
            ashiria TurtleGraphicsError("bad color arguments: %s" % str(color))
        ikiwa self._colormode == 1.0:
            r, g, b = [round(255.0*x) kila x kwenye (r, g, b)]
        ikiwa sio ((0 <= r <= 255) na (0 <= g <= 255) na (0 <= b <= 255)):
            ashiria TurtleGraphicsError("bad color sequence: %s" % str(color))
        rudisha "#%02x%02x%02x" % (r, g, b)

    eleza _color(self, cstr):
        ikiwa sio cstr.startswith("#"):
            rudisha cstr
        ikiwa len(cstr) == 7:
            cl = [int(cstr[i:i+2], 16) kila i kwenye (1, 3, 5)]
        lasivyo len(cstr) == 4:
            cl = [16*int(cstr[h], 16) kila h kwenye cstr[1:]]
        isipokua:
            ashiria TurtleGraphicsError("bad colorstring: %s" % cstr)
        rudisha tuple(c * self._colormode/255 kila c kwenye cl)

    eleza colormode(self, cmode=Tupu):
        """Return the colormode ama set it to 1.0 ama 255.

        Optional argument:
        cmode -- one of the values 1.0 ama 255

        r, g, b values of colortriples have to be kwenye range 0..cmode.

        Example (kila a TurtleScreen instance named screen):
        >>> screen.colormode()
        1.0
        >>> screen.colormode(255)
        >>> pencolor(240,160,80)
        """
        ikiwa cmode ni Tupu:
            rudisha self._colormode
        ikiwa cmode == 1.0:
            self._colormode = float(cmode)
        lasivyo cmode == 255:
            self._colormode = int(cmode)

    eleza reset(self):
        """Reset all Turtles on the Screen to their initial state.

        No argument.

        Example (kila a TurtleScreen instance named screen):
        >>> screen.reset()
        """
        kila turtle kwenye self._turtles:
            turtle._setmode(self._mode)
            turtle.reset()

    eleza turtles(self):
        """Return the list of turtles on the screen.

        Example (kila a TurtleScreen instance named screen):
        >>> screen.turtles()
        [<turtle.Turtle object at 0x00E11FB0>]
        """
        rudisha self._turtles

    eleza bgcolor(self, *args):
        """Set ama rudisha backgroundcolor of the TurtleScreen.

        Arguments (ikiwa given): a color string ama three numbers
        kwenye the range 0..colormode ama a 3-tuple of such numbers.

        Example (kila a TurtleScreen instance named screen):
        >>> screen.bgcolor("orange")
        >>> screen.bgcolor()
        'orange'
        >>> screen.bgcolor(0.5,0,0.5)
        >>> screen.bgcolor()
        '#800080'
        """
        ikiwa args:
            color = self._colorstr(args)
        isipokua:
            color = Tupu
        color = self._bgcolor(color)
        ikiwa color ni sio Tupu:
            color = self._color(color)
        rudisha color

    eleza tracer(self, n=Tupu, delay=Tupu):
        """Turns turtle animation on/off na set delay kila update drawings.

        Optional arguments:
        n -- nonnegative  integer
        delay -- nonnegative  integer

        If n ni given, only each n-th regular screen update ni really performed.
        (Can be used to accelerate the drawing of complex graphics.)
        Second arguments sets delay value (see RawTurtle.delay())

        Example (kila a TurtleScreen instance named screen):
        >>> screen.tracer(8, 25)
        >>> dist = 2
        >>> kila i kwenye range(200):
        ...     fd(dist)
        ...     rt(90)
        ...     dist += 2
        """
        ikiwa n ni Tupu:
            rudisha self._tracing
        self._tracing = int(n)
        self._updatecounter = 0
        ikiwa delay ni sio Tupu:
            self._delayvalue = int(delay)
        ikiwa self._tracing:
            self.update()

    eleza delay(self, delay=Tupu):
        """ Return ama set the drawing delay kwenye milliseconds.

        Optional argument:
        delay -- positive integer

        Example (kila a TurtleScreen instance named screen):
        >>> screen.delay(15)
        >>> screen.delay()
        15
        """
        ikiwa delay ni Tupu:
            rudisha self._delayvalue
        self._delayvalue = int(delay)

    eleza _incrementudc(self):
        """Increment update counter."""
        ikiwa sio TurtleScreen._RUNNING:
            TurtleScreen._RUNNING = Kweli
            ashiria Terminator
        ikiwa self._tracing > 0:
            self._updatecounter += 1
            self._updatecounter %= self._tracing

    eleza update(self):
        """Perform a TurtleScreen update.
        """
        tracing = self._tracing
        self._tracing = Kweli
        kila t kwenye self.turtles():
            t._update_data()
            t._drawturtle()
        self._tracing = tracing
        self._update()

    eleza window_width(self):
        """ Return the width of the turtle window.

        Example (kila a TurtleScreen instance named screen):
        >>> screen.window_width()
        640
        """
        rudisha self._window_size()[0]

    eleza window_height(self):
        """ Return the height of the turtle window.

        Example (kila a TurtleScreen instance named screen):
        >>> screen.window_height()
        480
        """
        rudisha self._window_size()[1]

    eleza getcanvas(self):
        """Return the Canvas of this TurtleScreen.

        No argument.

        Example (kila a Screen instance named screen):
        >>> cv = screen.getcanvas()
        >>> cv
        <turtle.ScrolledCanvas instance at 0x010742D8>
        """
        rudisha self.cv

    eleza getshapes(self):
        """Return a list of names of all currently available turtle shapes.

        No argument.

        Example (kila a TurtleScreen instance named screen):
        >>> screen.getshapes()
        ['arrow', 'blank', 'circle', ... , 'turtle']
        """
        rudisha sorted(self._shapes.keys())

    eleza onclick(self, fun, btn=1, add=Tupu):
        """Bind fun to mouse-click event on canvas.

        Arguments:
        fun -- a function ukijumuisha two arguments, the coordinates of the
               clicked point on the canvas.
        btn -- the number of the mouse-button, defaults to 1

        Example (kila a TurtleScreen instance named screen)

        >>> screen.onclick(goto)
        >>> # Subsequently clicking into the TurtleScreen will
        >>> # make the turtle move to the clicked point.
        >>> screen.onclick(Tupu)
        """
        self._onscreenclick(fun, btn, add)

    eleza onkey(self, fun, key):
        """Bind fun to key-release event of key.

        Arguments:
        fun -- a function ukijumuisha no arguments
        key -- a string: key (e.g. "a") ama key-symbol (e.g. "space")

        In order to be able to register key-events, TurtleScreen
        must have focus. (See method listen.)

        Example (kila a TurtleScreen instance named screen):

        >>> eleza f():
        ...     fd(50)
        ...     lt(60)
        ...
        >>> screen.onkey(f, "Up")
        >>> screen.listen()

        Subsequently the turtle can be moved by repeatedly pressing
        the up-arrow key, consequently drawing a hexagon

        """
        ikiwa fun ni Tupu:
            ikiwa key kwenye self._keys:
                self._keys.remove(key)
        lasivyo key haiko kwenye self._keys:
            self._keys.append(key)
        self._onkeyrelease(fun, key)

    eleza onkeypress(self, fun, key=Tupu):
        """Bind fun to key-press event of key ikiwa key ni given,
        ama to any key-press-event ikiwa no key ni given.

        Arguments:
        fun -- a function ukijumuisha no arguments
        key -- a string: key (e.g. "a") ama key-symbol (e.g. "space")

        In order to be able to register key-events, TurtleScreen
        must have focus. (See method listen.)

        Example (kila a TurtleScreen instance named screen
        na a Turtle instance named turtle):

        >>> eleza f():
        ...     fd(50)
        ...     lt(60)
        ...
        >>> screen.onkeypress(f, "Up")
        >>> screen.listen()

        Subsequently the turtle can be moved by repeatedly pressing
        the up-arrow key, ama by keeping pressed the up-arrow key.
        consequently drawing a hexagon.
        """
        ikiwa fun ni Tupu:
            ikiwa key kwenye self._keys:
                self._keys.remove(key)
        lasivyo key ni sio Tupu na key haiko kwenye self._keys:
            self._keys.append(key)
        self._onkeypress(fun, key)

    eleza listen(self, xdummy=Tupu, ydummy=Tupu):
        """Set focus on TurtleScreen (in order to collect key-events)

        No arguments.
        Dummy arguments are provided kwenye order
        to be able to pita listen to the onclick method.

        Example (kila a TurtleScreen instance named screen):
        >>> screen.listen()
        """
        self._listen()

    eleza ontimer(self, fun, t=0):
        """Install a timer, which calls fun after t milliseconds.

        Arguments:
        fun -- a function ukijumuisha no arguments.
        t -- a number >= 0

        Example (kila a TurtleScreen instance named screen):

        >>> running = Kweli
        >>> eleza f():
        ...     ikiwa running:
        ...             fd(50)
        ...             lt(60)
        ...             screen.ontimer(f, 250)
        ...
        >>> f()   # makes the turtle marching around
        >>> running = Uongo
        """
        self._ontimer(fun, t)

    eleza bgpic(self, picname=Tupu):
        """Set background image ama rudisha name of current backgroundimage.

        Optional argument:
        picname -- a string, name of a gif-file ama "nopic".

        If picname ni a filename, set the corresponding image kama background.
        If picname ni "nopic", delete backgroundimage, ikiwa present.
        If picname ni Tupu, rudisha the filename of the current backgroundimage.

        Example (kila a TurtleScreen instance named screen):
        >>> screen.bgpic()
        'nopic'
        >>> screen.bgpic("landscape.gif")
        >>> screen.bgpic()
        'landscape.gif'
        """
        ikiwa picname ni Tupu:
            rudisha self._bgpicname
        ikiwa picname haiko kwenye self._bgpics:
            self._bgpics[picname] = self._image(picname)
        self._setbgpic(self._bgpic, self._bgpics[picname])
        self._bgpicname = picname

    eleza screensize(self, canvwidth=Tupu, canvheight=Tupu, bg=Tupu):
        """Resize the canvas the turtles are drawing on.

        Optional arguments:
        canvwidth -- positive integer, new width of canvas kwenye pixels
        canvheight --  positive integer, new height of canvas kwenye pixels
        bg -- colorstring ama color-tuple, new backgroundcolor
        If no arguments are given, rudisha current (canvaswidth, canvasheight)

        Do sio alter the drawing window. To observe hidden parts of
        the canvas use the scrollbars. (Can make visible those parts
        of a drawing, which were outside the canvas before!)

        Example (kila a Turtle instance named turtle):
        >>> turtle.screensize(2000,1500)
        >>> # e.g. to search kila an erroneously escaped turtle ;-)
        """
        rudisha self._resize(canvwidth, canvheight, bg)

    onscreenclick = onclick
    resetscreen = reset
    clearscreen = clear
    addshape = register_shape
    onkeyrelease = onkey

kundi TNavigator(object):
    """Navigation part of the RawTurtle.
    Implements methods kila turtle movement.
    """
    START_ORIENTATION = {
        "standard": Vec2D(1.0, 0.0),
        "world"   : Vec2D(1.0, 0.0),
        "logo"    : Vec2D(0.0, 1.0)  }
    DEFAULT_MODE = "standard"
    DEFAULT_ANGLEOFFSET = 0
    DEFAULT_ANGLEORIENT = 1

    eleza __init__(self, mode=DEFAULT_MODE):
        self._angleOffset = self.DEFAULT_ANGLEOFFSET
        self._angleOrient = self.DEFAULT_ANGLEORIENT
        self._mode = mode
        self.undobuffer = Tupu
        self.degrees()
        self._mode = Tupu
        self._setmode(mode)
        TNavigator.reset(self)

    eleza reset(self):
        """reset turtle to its initial values

        Will be overwritten by parent class
        """
        self._position = Vec2D(0.0, 0.0)
        self._orient =  TNavigator.START_ORIENTATION[self._mode]

    eleza _setmode(self, mode=Tupu):
        """Set turtle-mode to 'standard', 'world' ama 'logo'.
        """
        ikiwa mode ni Tupu:
            rudisha self._mode
        ikiwa mode haiko kwenye ["standard", "logo", "world"]:
            rudisha
        self._mode = mode
        ikiwa mode kwenye ["standard", "world"]:
            self._angleOffset = 0
            self._angleOrient = 1
        isipokua: # mode == "logo":
            self._angleOffset = self._fullcircle/4.
            self._angleOrient = -1

    eleza _setDegreesPerAU(self, fullcircle):
        """Helper function kila degrees() na radians()"""
        self._fullcircle = fullcircle
        self._degreesPerAU = 360/fullcircle
        ikiwa self._mode == "standard":
            self._angleOffset = 0
        isipokua:
            self._angleOffset = fullcircle/4.

    eleza degrees(self, fullcircle=360.0):
        """ Set angle measurement units to degrees.

        Optional argument:
        fullcircle -  a number

        Set angle measurement units, i. e. set number
        of 'degrees' kila a full circle. Default value is
        360 degrees.

        Example (kila a Turtle instance named turtle):
        >>> turtle.left(90)
        >>> turtle.heading()
        90

        Change angle measurement unit to grad (also known kama gon,
        grade, ama gradian na equals 1/100-th of the right angle.)
        >>> turtle.degrees(400.0)
        >>> turtle.heading()
        100

        """
        self._setDegreesPerAU(fullcircle)

    eleza radians(self):
        """ Set the angle measurement units to radians.

        No arguments.

        Example (kila a Turtle instance named turtle):
        >>> turtle.heading()
        90
        >>> turtle.radians()
        >>> turtle.heading()
        1.5707963267948966
        """
        self._setDegreesPerAU(2*math.pi)

    eleza _go(self, distance):
        """move turtle forward by specified distance"""
        ende = self._position + self._orient * distance
        self._goto(ende)

    eleza _rotate(self, angle):
        """Turn turtle counterclockwise by specified angle ikiwa angle > 0."""
        angle *= self._degreesPerAU
        self._orient = self._orient.rotate(angle)

    eleza _goto(self, end):
        """move turtle to position end."""
        self._position = end

    eleza forward(self, distance):
        """Move the turtle forward by the specified distance.

        Aliases: forward | fd

        Argument:
        distance -- a number (integer ama float)

        Move the turtle forward by the specified distance, kwenye the direction
        the turtle ni headed.

        Example (kila a Turtle instance named turtle):
        >>> turtle.position()
        (0.00, 0.00)
        >>> turtle.forward(25)
        >>> turtle.position()
        (25.00,0.00)
        >>> turtle.forward(-75)
        >>> turtle.position()
        (-50.00,0.00)
        """
        self._go(distance)

    eleza back(self, distance):
        """Move the turtle backward by distance.

        Aliases: back | backward | bk

        Argument:
        distance -- a number

        Move the turtle backward by distance ,opposite to the direction the
        turtle ni headed. Do sio change the turtle's heading.

        Example (kila a Turtle instance named turtle):
        >>> turtle.position()
        (0.00, 0.00)
        >>> turtle.backward(30)
        >>> turtle.position()
        (-30.00, 0.00)
        """
        self._go(-distance)

    eleza right(self, angle):
        """Turn turtle right by angle units.

        Aliases: right | rt

        Argument:
        angle -- a number (integer ama float)

        Turn turtle right by angle units. (Units are by default degrees,
        but can be set via the degrees() na radians() functions.)
        Angle orientation depends on mode. (See this.)

        Example (kila a Turtle instance named turtle):
        >>> turtle.heading()
        22.0
        >>> turtle.right(45)
        >>> turtle.heading()
        337.0
        """
        self._rotate(-angle)

    eleza left(self, angle):
        """Turn turtle left by angle units.

        Aliases: left | lt

        Argument:
        angle -- a number (integer ama float)

        Turn turtle left by angle units. (Units are by default degrees,
        but can be set via the degrees() na radians() functions.)
        Angle orientation depends on mode. (See this.)

        Example (kila a Turtle instance named turtle):
        >>> turtle.heading()
        22.0
        >>> turtle.left(45)
        >>> turtle.heading()
        67.0
        """
        self._rotate(angle)

    eleza pos(self):
        """Return the turtle's current location (x,y), kama a Vec2D-vector.

        Aliases: pos | position

        No arguments.

        Example (kila a Turtle instance named turtle):
        >>> turtle.pos()
        (0.00, 240.00)
        """
        rudisha self._position

    eleza xcor(self):
        """ Return the turtle's x coordinate.

        No arguments.

        Example (kila a Turtle instance named turtle):
        >>> reset()
        >>> turtle.left(60)
        >>> turtle.forward(100)
        >>> print turtle.xcor()
        50.0
        """
        rudisha self._position[0]

    eleza ycor(self):
        """ Return the turtle's y coordinate
        ---
        No arguments.

        Example (kila a Turtle instance named turtle):
        >>> reset()
        >>> turtle.left(60)
        >>> turtle.forward(100)
        >>> print turtle.ycor()
        86.6025403784
        """
        rudisha self._position[1]


    eleza goto(self, x, y=Tupu):
        """Move turtle to an absolute position.

        Aliases: setpos | setposition | goto:

        Arguments:
        x -- a number      ama     a pair/vector of numbers
        y -- a number             Tupu

        call: goto(x, y)         # two coordinates
        --or: goto((x, y))       # a pair (tuple) of coordinates
        --or: goto(vec)          # e.g. kama returned by pos()

        Move turtle to an absolute position. If the pen ni down,
        a line will be drawn. The turtle's orientation does sio change.

        Example (kila a Turtle instance named turtle):
        >>> tp = turtle.pos()
        >>> tp
        (0.00, 0.00)
        >>> turtle.setpos(60,30)
        >>> turtle.pos()
        (60.00,30.00)
        >>> turtle.setpos((20,80))
        >>> turtle.pos()
        (20.00,80.00)
        >>> turtle.setpos(tp)
        >>> turtle.pos()
        (0.00,0.00)
        """
        ikiwa y ni Tupu:
            self._goto(Vec2D(*x))
        isipokua:
            self._goto(Vec2D(x, y))

    eleza home(self):
        """Move turtle to the origin - coordinates (0,0).

        No arguments.

        Move turtle to the origin - coordinates (0,0) na set its
        heading to its start-orientation (which depends on mode).

        Example (kila a Turtle instance named turtle):
        >>> turtle.home()
        """
        self.goto(0, 0)
        self.setheading(0)

    eleza setx(self, x):
        """Set the turtle's first coordinate to x

        Argument:
        x -- a number (integer ama float)

        Set the turtle's first coordinate to x, leave second coordinate
        unchanged.

        Example (kila a Turtle instance named turtle):
        >>> turtle.position()
        (0.00, 240.00)
        >>> turtle.setx(10)
        >>> turtle.position()
        (10.00, 240.00)
        """
        self._goto(Vec2D(x, self._position[1]))

    eleza sety(self, y):
        """Set the turtle's second coordinate to y

        Argument:
        y -- a number (integer ama float)

        Set the turtle's first coordinate to x, second coordinate remains
        unchanged.

        Example (kila a Turtle instance named turtle):
        >>> turtle.position()
        (0.00, 40.00)
        >>> turtle.sety(-10)
        >>> turtle.position()
        (0.00, -10.00)
        """
        self._goto(Vec2D(self._position[0], y))

    eleza distance(self, x, y=Tupu):
        """Return the distance kutoka the turtle to (x,y) kwenye turtle step units.

        Arguments:
        x -- a number   ama  a pair/vector of numbers   ama   a turtle instance
        y -- a number       Tupu                            Tupu

        call: distance(x, y)         # two coordinates
        --or: distance((x, y))       # a pair (tuple) of coordinates
        --or: distance(vec)          # e.g. kama returned by pos()
        --or: distance(mypen)        # where mypen ni another turtle

        Example (kila a Turtle instance named turtle):
        >>> turtle.pos()
        (0.00, 0.00)
        >>> turtle.distance(30,40)
        50.0
        >>> pen = Turtle()
        >>> pen.forward(77)
        >>> turtle.distance(pen)
        77.0
        """
        ikiwa y ni sio Tupu:
            pos = Vec2D(x, y)
        ikiwa isinstance(x, Vec2D):
            pos = x
        lasivyo isinstance(x, tuple):
            pos = Vec2D(*x)
        lasivyo isinstance(x, TNavigator):
            pos = x._position
        rudisha abs(pos - self._position)

    eleza towards(self, x, y=Tupu):
        """Return the angle of the line kutoka the turtle's position to (x, y).

        Arguments:
        x -- a number   ama  a pair/vector of numbers   ama   a turtle instance
        y -- a number       Tupu                            Tupu

        call: distance(x, y)         # two coordinates
        --or: distance((x, y))       # a pair (tuple) of coordinates
        --or: distance(vec)          # e.g. kama returned by pos()
        --or: distance(mypen)        # where mypen ni another turtle

        Return the angle, between the line kutoka turtle-position to position
        specified by x, y na the turtle's start orientation. (Depends on
        modes - "standard" ama "logo")

        Example (kila a Turtle instance named turtle):
        >>> turtle.pos()
        (10.00, 10.00)
        >>> turtle.towards(0,0)
        225.0
        """
        ikiwa y ni sio Tupu:
            pos = Vec2D(x, y)
        ikiwa isinstance(x, Vec2D):
            pos = x
        lasivyo isinstance(x, tuple):
            pos = Vec2D(*x)
        lasivyo isinstance(x, TNavigator):
            pos = x._position
        x, y = pos - self._position
        result = round(math.atan2(y, x)*180.0/math.pi, 10) % 360.0
        result /= self._degreesPerAU
        rudisha (self._angleOffset + self._angleOrient*result) % self._fullcircle

    eleza heading(self):
        """ Return the turtle's current heading.

        No arguments.

        Example (kila a Turtle instance named turtle):
        >>> turtle.left(67)
        >>> turtle.heading()
        67.0
        """
        x, y = self._orient
        result = round(math.atan2(y, x)*180.0/math.pi, 10) % 360.0
        result /= self._degreesPerAU
        rudisha (self._angleOffset + self._angleOrient*result) % self._fullcircle

    eleza setheading(self, to_angle):
        """Set the orientation of the turtle to to_angle.

        Aliases:  setheading | seth

        Argument:
        to_angle -- a number (integer ama float)

        Set the orientation of the turtle to to_angle.
        Here are some common directions kwenye degrees:

         standard - mode:          logo-mode:
        -------------------|--------------------
           0 - east                0 - north
          90 - north              90 - east
         180 - west              180 - south
         270 - south             270 - west

        Example (kila a Turtle instance named turtle):
        >>> turtle.setheading(90)
        >>> turtle.heading()
        90
        """
        angle = (to_angle - self.heading())*self._angleOrient
        full = self._fullcircle
        angle = (angle+full/2.)%full - full/2.
        self._rotate(angle)

    eleza circle(self, radius, extent = Tupu, steps = Tupu):
        """ Draw a circle ukijumuisha given radius.

        Arguments:
        radius -- a number
        extent (optional) -- a number
        steps (optional) -- an integer

        Draw a circle ukijumuisha given radius. The center ni radius units left
        of the turtle; extent - an angle - determines which part of the
        circle ni drawn. If extent ni sio given, draw the entire circle.
        If extent ni sio a full circle, one endpoint of the arc ni the
        current pen position. Draw the arc kwenye counterclockwise direction
        ikiwa radius ni positive, otherwise kwenye clockwise direction. Finally
        the direction of the turtle ni changed by the amount of extent.

        As the circle ni approximated by an inscribed regular polygon,
        steps determines the number of steps to use. If sio given,
        it will be calculated automatically. Maybe used to draw regular
        polygons.

        call: circle(radius)                  # full circle
        --or: circle(radius, extent)          # arc
        --or: circle(radius, extent, steps)
        --or: circle(radius, steps=6)         # 6-sided polygon

        Example (kila a Turtle instance named turtle):
        >>> turtle.circle(50)
        >>> turtle.circle(120, 180)  # semicircle
        """
        ikiwa self.undobuffer:
            self.undobuffer.push(["seq"])
            self.undobuffer.cumulate = Kweli
        speed = self.speed()
        ikiwa extent ni Tupu:
            extent = self._fullcircle
        ikiwa steps ni Tupu:
            frac = abs(extent)/self._fullcircle
            steps = 1+int(min(11+abs(radius)/6.0, 59.0)*frac)
        w = 1.0 * extent / steps
        w2 = 0.5 * w
        l = 2.0 * radius * math.sin(w2*math.pi/180.0*self._degreesPerAU)
        ikiwa radius < 0:
            l, w, w2 = -l, -w, -w2
        tr = self._tracer()
        dl = self._delay()
        ikiwa speed == 0:
            self._tracer(0, 0)
        isipokua:
            self.speed(0)
        self._rotate(w2)
        kila i kwenye range(steps):
            self.speed(speed)
            self._go(l)
            self.speed(0)
            self._rotate(w)
        self._rotate(-w2)
        ikiwa speed == 0:
            self._tracer(tr, dl)
        self.speed(speed)
        ikiwa self.undobuffer:
            self.undobuffer.cumulate = Uongo

## three dummy methods to be implemented by child class:

    eleza speed(self, s=0):
        """dummy method - to be overwritten by child class"""
    eleza _tracer(self, a=Tupu, b=Tupu):
        """dummy method - to be overwritten by child class"""
    eleza _delay(self, n=Tupu):
        """dummy method - to be overwritten by child class"""

    fd = forward
    bk = back
    backward = back
    rt = right
    lt = left
    position = pos
    setpos = goto
    setposition = goto
    seth = setheading


kundi TPen(object):
    """Drawing part of the RawTurtle.
    Implements drawing properties.
    """
    eleza __init__(self, resizemode=_CFG["resizemode"]):
        self._resizemode = resizemode # ama "user" ama "noresize"
        self.undobuffer = Tupu
        TPen._reset(self)

    eleza _reset(self, pencolor=_CFG["pencolor"],
                     fillcolor=_CFG["fillcolor"]):
        self._pensize = 1
        self._shown = Kweli
        self._pencolor = pencolor
        self._fillcolor = fillcolor
        self._drawing = Kweli
        self._speed = 3
        self._stretchfactor = (1., 1.)
        self._shearfactor = 0.
        self._tilt = 0.
        self._shapetrafo = (1., 0., 0., 1.)
        self._outlinewidth = 1

    eleza resizemode(self, rmode=Tupu):
        """Set resizemode to one of the values: "auto", "user", "noresize".

        (Optional) Argument:
        rmode -- one of the strings "auto", "user", "noresize"

        Different resizemodes have the following effects:
          - "auto" adapts the appearance of the turtle
                   corresponding to the value of pensize.
          - "user" adapts the appearance of the turtle according to the
                   values of stretchfactor na outlinewidth (outline),
                   which are set by shapesize()
          - "noresize" no adaption of the turtle's appearance takes place.
        If no argument ni given, rudisha current resizemode.
        resizemode("user") ni called by a call of shapesize ukijumuisha arguments.


        Examples (kila a Turtle instance named turtle):
        >>> turtle.resizemode("noresize")
        >>> turtle.resizemode()
        'noresize'
        """
        ikiwa rmode ni Tupu:
            rudisha self._resizemode
        rmode = rmode.lower()
        ikiwa rmode kwenye ["auto", "user", "noresize"]:
            self.pen(resizemode=rmode)

    eleza pensize(self, width=Tupu):
        """Set ama rudisha the line thickness.

        Aliases:  pensize | width

        Argument:
        width -- positive number

        Set the line thickness to width ama rudisha it. If resizemode ni set
        to "auto" na turtleshape ni a polygon, that polygon ni drawn with
        the same line thickness. If no argument ni given, current pensize
        ni returned.

        Example (kila a Turtle instance named turtle):
        >>> turtle.pensize()
        1
        >>> turtle.pensize(10)   # kutoka here on lines of width 10 are drawn
        """
        ikiwa width ni Tupu:
            rudisha self._pensize
        self.pen(pensize=width)


    eleza penup(self):
        """Pull the pen up -- no drawing when moving.

        Aliases: penup | pu | up

        No argument

        Example (kila a Turtle instance named turtle):
        >>> turtle.penup()
        """
        ikiwa sio self._drawing:
            rudisha
        self.pen(pendown=Uongo)

    eleza pendown(self):
        """Pull the pen down -- drawing when moving.

        Aliases: pendown | pd | down

        No argument.

        Example (kila a Turtle instance named turtle):
        >>> turtle.pendown()
        """
        ikiwa self._drawing:
            rudisha
        self.pen(pendown=Kweli)

    eleza isdown(self):
        """Return Kweli ikiwa pen ni down, Uongo ikiwa it's up.

        No argument.

        Example (kila a Turtle instance named turtle):
        >>> turtle.penup()
        >>> turtle.isdown()
        Uongo
        >>> turtle.pendown()
        >>> turtle.isdown()
        Kweli
        """
        rudisha self._drawing

    eleza speed(self, speed=Tupu):
        """ Return ama set the turtle's speed.

        Optional argument:
        speed -- an integer kwenye the range 0..10 ama a speedstring (see below)

        Set the turtle's speed to an integer value kwenye the range 0 .. 10.
        If no argument ni given: rudisha current speed.

        If input ni a number greater than 10 ama smaller than 0.5,
        speed ni set to 0.
        Speedstrings  are mapped to speedvalues kwenye the following way:
            'fastest' :  0
            'fast'    :  10
            'normal'  :  6
            'slow'    :  3
            'slowest' :  1
        speeds kutoka 1 to 10 enforce increasingly faster animation of
        line drawing na turtle turning.

        Attention:
        speed = 0 : *no* animation takes place. forward/back makes turtle jump
        na likewise left/right make the turtle turn instantly.

        Example (kila a Turtle instance named turtle):
        >>> turtle.speed(3)
        """
        speeds = {'fastest':0, 'fast':10, 'normal':6, 'slow':3, 'slowest':1 }
        ikiwa speed ni Tupu:
            rudisha self._speed
        ikiwa speed kwenye speeds:
            speed = speeds[speed]
        lasivyo 0.5 < speed < 10.5:
            speed = int(round(speed))
        isipokua:
            speed = 0
        self.pen(speed=speed)

    eleza color(self, *args):
        """Return ama set the pencolor na fillcolor.

        Arguments:
        Several input formats are allowed.
        They use 0, 1, 2, ama 3 arguments kama follows:

        color()
            Return the current pencolor na the current fillcolor
            kama a pair of color specification strings kama are returned
            by pencolor na fillcolor.
        color(colorstring), color((r,g,b)), color(r,g,b)
            inputs kama kwenye pencolor, set both, fillcolor na pencolor,
            to the given value.
        color(colorstring1, colorstring2),
        color((r1,g1,b1), (r2,g2,b2))
            equivalent to pencolor(colorstring1) na fillcolor(colorstring2)
            na analogously, ikiwa the other input format ni used.

        If turtleshape ni a polygon, outline na interior of that polygon
        ni drawn ukijumuisha the newly set colors.
        For more info see: pencolor, fillcolor

        Example (kila a Turtle instance named turtle):
        >>> turtle.color('red', 'green')
        >>> turtle.color()
        ('red', 'green')
        >>> colormode(255)
        >>> color((40, 80, 120), (160, 200, 240))
        >>> color()
        ('#285078', '#a0c8f0')
        """
        ikiwa args:
            l = len(args)
            ikiwa l == 1:
                pcolor = fcolor = args[0]
            lasivyo l == 2:
                pcolor, fcolor = args
            lasivyo l == 3:
                pcolor = fcolor = args
            pcolor = self._colorstr(pcolor)
            fcolor = self._colorstr(fcolor)
            self.pen(pencolor=pcolor, fillcolor=fcolor)
        isipokua:
            rudisha self._color(self._pencolor), self._color(self._fillcolor)

    eleza pencolor(self, *args):
        """ Return ama set the pencolor.

        Arguments:
        Four input formats are allowed:
          - pencolor()
            Return the current pencolor kama color specification string,
            possibly kwenye hex-number format (see example).
            May be used kama input to another color/pencolor/fillcolor call.
          - pencolor(colorstring)
            s ni a Tk color specification string, such kama "red" ama "yellow"
          - pencolor((r, g, b))
            *a tuple* of r, g, na b, which represent, an RGB color,
            na each of r, g, na b are kwenye the range 0..colormode,
            where colormode ni either 1.0 ama 255
          - pencolor(r, g, b)
            r, g, na b represent an RGB color, na each of r, g, na b
            are kwenye the range 0..colormode

        If turtleshape ni a polygon, the outline of that polygon ni drawn
        ukijumuisha the newly set pencolor.

        Example (kila a Turtle instance named turtle):
        >>> turtle.pencolor('brown')
        >>> tup = (0.2, 0.8, 0.55)
        >>> turtle.pencolor(tup)
        >>> turtle.pencolor()
        '#33cc8c'
        """
        ikiwa args:
            color = self._colorstr(args)
            ikiwa color == self._pencolor:
                rudisha
            self.pen(pencolor=color)
        isipokua:
            rudisha self._color(self._pencolor)

    eleza fillcolor(self, *args):
        """ Return ama set the fillcolor.

        Arguments:
        Four input formats are allowed:
          - fillcolor()
            Return the current fillcolor kama color specification string,
            possibly kwenye hex-number format (see example).
            May be used kama input to another color/pencolor/fillcolor call.
          - fillcolor(colorstring)
            s ni a Tk color specification string, such kama "red" ama "yellow"
          - fillcolor((r, g, b))
            *a tuple* of r, g, na b, which represent, an RGB color,
            na each of r, g, na b are kwenye the range 0..colormode,
            where colormode ni either 1.0 ama 255
          - fillcolor(r, g, b)
            r, g, na b represent an RGB color, na each of r, g, na b
            are kwenye the range 0..colormode

        If turtleshape ni a polygon, the interior of that polygon ni drawn
        ukijumuisha the newly set fillcolor.

        Example (kila a Turtle instance named turtle):
        >>> turtle.fillcolor('violet')
        >>> col = turtle.pencolor()
        >>> turtle.fillcolor(col)
        >>> turtle.fillcolor(0, .5, 0)
        """
        ikiwa args:
            color = self._colorstr(args)
            ikiwa color == self._fillcolor:
                rudisha
            self.pen(fillcolor=color)
        isipokua:
            rudisha self._color(self._fillcolor)

    eleza showturtle(self):
        """Makes the turtle visible.

        Aliases: showturtle | st

        No argument.

        Example (kila a Turtle instance named turtle):
        >>> turtle.hideturtle()
        >>> turtle.showturtle()
        """
        self.pen(shown=Kweli)

    eleza hideturtle(self):
        """Makes the turtle invisible.

        Aliases: hideturtle | ht

        No argument.

        It's a good idea to do this wakati you're kwenye the
        middle of a complicated drawing, because hiding
        the turtle speeds up the drawing observably.

        Example (kila a Turtle instance named turtle):
        >>> turtle.hideturtle()
        """
        self.pen(shown=Uongo)

    eleza isvisible(self):
        """Return Kweli ikiwa the Turtle ni shown, Uongo ikiwa it's hidden.

        No argument.

        Example (kila a Turtle instance named turtle):
        >>> turtle.hideturtle()
        >>> print turtle.isvisible():
        Uongo
        """
        rudisha self._shown

    eleza pen(self, pen=Tupu, **pendict):
        """Return ama set the pen's attributes.

        Arguments:
            pen -- a dictionary ukijumuisha some ama all of the below listed keys.
            **pendict -- one ama more keyword-arguments ukijumuisha the below
                         listed keys kama keywords.

        Return ama set the pen's attributes kwenye a 'pen-dictionary'
        ukijumuisha the following key/value pairs:
           "shown"      :   Kweli/Uongo
           "pendown"    :   Kweli/Uongo
           "pencolor"   :   color-string ama color-tuple
           "fillcolor"  :   color-string ama color-tuple
           "pensize"    :   positive number
           "speed"      :   number kwenye range 0..10
           "resizemode" :   "auto" ama "user" ama "noresize"
           "stretchfactor": (positive number, positive number)
           "shearfactor":   number
           "outline"    :   positive number
           "tilt"       :   number

        This dictionary can be used kama argument kila a subsequent
        pen()-call to restore the former pen-state. Moreover one
        ama more of these attributes can be provided kama keyword-arguments.
        This can be used to set several pen attributes kwenye one statement.


        Examples (kila a Turtle instance named turtle):
        >>> turtle.pen(fillcolor="black", pencolor="red", pensize=10)
        >>> turtle.pen()
        {'pensize': 10, 'shown': Kweli, 'resizemode': 'auto', 'outline': 1,
        'pencolor': 'red', 'pendown': Kweli, 'fillcolor': 'black',
        'stretchfactor': (1,1), 'speed': 3, 'shearfactor': 0.0}
        >>> penstate=turtle.pen()
        >>> turtle.color("yellow","")
        >>> turtle.penup()
        >>> turtle.pen()
        {'pensize': 10, 'shown': Kweli, 'resizemode': 'auto', 'outline': 1,
        'pencolor': 'yellow', 'pendown': Uongo, 'fillcolor': '',
        'stretchfactor': (1,1), 'speed': 3, 'shearfactor': 0.0}
        >>> p.pen(penstate, fillcolor="green")
        >>> p.pen()
        {'pensize': 10, 'shown': Kweli, 'resizemode': 'auto', 'outline': 1,
        'pencolor': 'red', 'pendown': Kweli, 'fillcolor': 'green',
        'stretchfactor': (1,1), 'speed': 3, 'shearfactor': 0.0}
        """
        _pd =  {"shown"         : self._shown,
                "pendown"       : self._drawing,
                "pencolor"      : self._pencolor,
                "fillcolor"     : self._fillcolor,
                "pensize"       : self._pensize,
                "speed"         : self._speed,
                "resizemode"    : self._resizemode,
                "stretchfactor" : self._stretchfactor,
                "shearfactor"   : self._shearfactor,
                "outline"       : self._outlinewidth,
                "tilt"          : self._tilt
               }

        ikiwa sio (pen ama pendict):
            rudisha _pd

        ikiwa isinstance(pen, dict):
            p = pen
        isipokua:
            p = {}
        p.update(pendict)

        _p_buf = {}
        kila key kwenye p:
            _p_buf[key] = _pd[key]

        ikiwa self.undobuffer:
            self.undobuffer.push(("pen", _p_buf))

        newLine = Uongo
        ikiwa "pendown" kwenye p:
            ikiwa self._drawing != p["pendown"]:
                newLine = Kweli
        ikiwa "pencolor" kwenye p:
            ikiwa isinstance(p["pencolor"], tuple):
                p["pencolor"] = self._colorstr((p["pencolor"],))
            ikiwa self._pencolor != p["pencolor"]:
                newLine = Kweli
        ikiwa "pensize" kwenye p:
            ikiwa self._pensize != p["pensize"]:
                newLine = Kweli
        ikiwa newLine:
            self._newLine()
        ikiwa "pendown" kwenye p:
            self._drawing = p["pendown"]
        ikiwa "pencolor" kwenye p:
            self._pencolor = p["pencolor"]
        ikiwa "pensize" kwenye p:
            self._pensize = p["pensize"]
        ikiwa "fillcolor" kwenye p:
            ikiwa isinstance(p["fillcolor"], tuple):
                p["fillcolor"] = self._colorstr((p["fillcolor"],))
            self._fillcolor = p["fillcolor"]
        ikiwa "speed" kwenye p:
            self._speed = p["speed"]
        ikiwa "resizemode" kwenye p:
            self._resizemode = p["resizemode"]
        ikiwa "stretchfactor" kwenye p:
            sf = p["stretchfactor"]
            ikiwa isinstance(sf, (int, float)):
                sf = (sf, sf)
            self._stretchfactor = sf
        ikiwa "shearfactor" kwenye p:
            self._shearfactor = p["shearfactor"]
        ikiwa "outline" kwenye p:
            self._outlinewidth = p["outline"]
        ikiwa "shown" kwenye p:
            self._shown = p["shown"]
        ikiwa "tilt" kwenye p:
            self._tilt = p["tilt"]
        ikiwa "stretchfactor" kwenye p ama "tilt" kwenye p ama "shearfactor" kwenye p:
            scx, scy = self._stretchfactor
            shf = self._shearfactor
            sa, ca = math.sin(self._tilt), math.cos(self._tilt)
            self._shapetrafo = ( scx*ca, scy*(shf*ca + sa),
                                -scx*sa, scy*(ca - shf*sa))
        self._update()

## three dummy methods to be implemented by child class:

    eleza _newLine(self, usePos = Kweli):
        """dummy method - to be overwritten by child class"""
    eleza _update(self, count=Kweli, forced=Uongo):
        """dummy method - to be overwritten by child class"""
    eleza _color(self, args):
        """dummy method - to be overwritten by child class"""
    eleza _colorstr(self, args):
        """dummy method - to be overwritten by child class"""

    width = pensize
    up = penup
    pu = penup
    pd = pendown
    down = pendown
    st = showturtle
    ht = hideturtle


kundi _TurtleImage(object):
    """Helper class: Datatype to store Turtle attributes
    """

    eleza __init__(self, screen, shapeIndex):
        self.screen = screen
        self._type = Tupu
        self._setshape(shapeIndex)

    eleza _setshape(self, shapeIndex):
        screen = self.screen
        self.shapeIndex = shapeIndex
        ikiwa self._type == "polygon" == screen._shapes[shapeIndex]._type:
            rudisha
        ikiwa self._type == "image" == screen._shapes[shapeIndex]._type:
            rudisha
        ikiwa self._type kwenye ["image", "polygon"]:
            screen._delete(self._item)
        lasivyo self._type == "compound":
            kila item kwenye self._item:
                screen._delete(item)
        self._type = screen._shapes[shapeIndex]._type
        ikiwa self._type == "polygon":
            self._item = screen._createpoly()
        lasivyo self._type == "image":
            self._item = screen._createimage(screen._shapes["blank"]._data)
        lasivyo self._type == "compound":
            self._item = [screen._createpoly() kila item in
                                          screen._shapes[shapeIndex]._data]


kundi RawTurtle(TPen, TNavigator):
    """Animation part of the RawTurtle.
    Puts RawTurtle upon a TurtleScreen na provides tools for
    its animation.
    """
    screens = []

    eleza __init__(self, canvas=Tupu,
                 shape=_CFG["shape"],
                 undobuffersize=_CFG["undobuffersize"],
                 visible=_CFG["visible"]):
        ikiwa isinstance(canvas, _Screen):
            self.screen = canvas
        lasivyo isinstance(canvas, TurtleScreen):
            ikiwa canvas haiko kwenye RawTurtle.screens:
                RawTurtle.screens.append(canvas)
            self.screen = canvas
        lasivyo isinstance(canvas, (ScrolledCanvas, Canvas)):
            kila screen kwenye RawTurtle.screens:
                ikiwa screen.cv == canvas:
                    self.screen = screen
                    koma
            isipokua:
                self.screen = TurtleScreen(canvas)
                RawTurtle.screens.append(self.screen)
        isipokua:
            ashiria TurtleGraphicsError("bad canvas argument %s" % canvas)

        screen = self.screen
        TNavigator.__init__(self, screen.mode())
        TPen.__init__(self)
        screen._turtles.append(self)
        self.drawingLineItem = screen._createline()
        self.turtle = _TurtleImage(screen, shape)
        self._poly = Tupu
        self._creatingPoly = Uongo
        self._fillitem = self._fillpath = Tupu
        self._shown = visible
        self._hidden_from_screen = Uongo
        self.currentLineItem = screen._createline()
        self.currentLine = [self._position]
        self.items = [self.currentLineItem]
        self.stampItems = []
        self._undobuffersize = undobuffersize
        self.undobuffer = Tbuffer(undobuffersize)
        self._update()

    eleza reset(self):
        """Delete the turtle's drawings na restore its default values.

        No argument.

        Delete the turtle's drawings kutoka the screen, re-center the turtle
        na set variables to the default values.

        Example (kila a Turtle instance named turtle):
        >>> turtle.position()
        (0.00,-22.00)
        >>> turtle.heading()
        100.0
        >>> turtle.reset()
        >>> turtle.position()
        (0.00,0.00)
        >>> turtle.heading()
        0.0
        """
        TNavigator.reset(self)
        TPen._reset(self)
        self._clear()
        self._drawturtle()
        self._update()

    eleza setundobuffer(self, size):
        """Set ama disable undobuffer.

        Argument:
        size -- an integer ama Tupu

        If size ni an integer an empty undobuffer of given size ni installed.
        Size gives the maximum number of turtle-actions that can be undone
        by the undo() function.
        If size ni Tupu, no undobuffer ni present.

        Example (kila a Turtle instance named turtle):
        >>> turtle.setundobuffer(42)
        """
        ikiwa size ni Tupu ama size <= 0:
            self.undobuffer = Tupu
        isipokua:
            self.undobuffer = Tbuffer(size)

    eleza undobufferentries(self):
        """Return count of entries kwenye the undobuffer.

        No argument.

        Example (kila a Turtle instance named turtle):
        >>> wakati undobufferentries():
        ...     undo()
        """
        ikiwa self.undobuffer ni Tupu:
            rudisha 0
        rudisha self.undobuffer.nr_of_items()

    eleza _clear(self):
        """Delete all of pen's drawings"""
        self._fillitem = self._fillpath = Tupu
        kila item kwenye self.items:
            self.screen._delete(item)
        self.currentLineItem = self.screen._createline()
        self.currentLine = []
        ikiwa self._drawing:
            self.currentLine.append(self._position)
        self.items = [self.currentLineItem]
        self.clearstamps()
        self.setundobuffer(self._undobuffersize)


    eleza clear(self):
        """Delete the turtle's drawings kutoka the screen. Do sio move turtle.

        No arguments.

        Delete the turtle's drawings kutoka the screen. Do sio move turtle.
        State na position of the turtle kama well kama drawings of other
        turtles are sio affected.

        Examples (kila a Turtle instance named turtle):
        >>> turtle.clear()
        """
        self._clear()
        self._update()

    eleza _update_data(self):
        self.screen._incrementudc()
        ikiwa self.screen._updatecounter != 0:
            rudisha
        ikiwa len(self.currentLine)>1:
            self.screen._drawline(self.currentLineItem, self.currentLine,
                                  self._pencolor, self._pensize)

    eleza _update(self):
        """Perform a Turtle-data update.
        """
        screen = self.screen
        ikiwa screen._tracing == 0:
            rudisha
        lasivyo screen._tracing == 1:
            self._update_data()
            self._drawturtle()
            screen._update()                  # TurtleScreenBase
            screen._delay(screen._delayvalue) # TurtleScreenBase
        isipokua:
            self._update_data()
            ikiwa screen._updatecounter == 0:
                kila t kwenye screen.turtles():
                    t._drawturtle()
                screen._update()

    eleza _tracer(self, flag=Tupu, delay=Tupu):
        """Turns turtle animation on/off na set delay kila update drawings.

        Optional arguments:
        n -- nonnegative  integer
        delay -- nonnegative  integer

        If n ni given, only each n-th regular screen update ni really performed.
        (Can be used to accelerate the drawing of complex graphics.)
        Second arguments sets delay value (see RawTurtle.delay())

        Example (kila a Turtle instance named turtle):
        >>> turtle.tracer(8, 25)
        >>> dist = 2
        >>> kila i kwenye range(200):
        ...     turtle.fd(dist)
        ...     turtle.rt(90)
        ...     dist += 2
        """
        rudisha self.screen.tracer(flag, delay)

    eleza _color(self, args):
        rudisha self.screen._color(args)

    eleza _colorstr(self, args):
        rudisha self.screen._colorstr(args)

    eleza _cc(self, args):
        """Convert colortriples to hexstrings.
        """
        ikiwa isinstance(args, str):
            rudisha args
        jaribu:
            r, g, b = args
        tatizo (TypeError, ValueError):
            ashiria TurtleGraphicsError("bad color arguments: %s" % str(args))
        ikiwa self.screen._colormode == 1.0:
            r, g, b = [round(255.0*x) kila x kwenye (r, g, b)]
        ikiwa sio ((0 <= r <= 255) na (0 <= g <= 255) na (0 <= b <= 255)):
            ashiria TurtleGraphicsError("bad color sequence: %s" % str(args))
        rudisha "#%02x%02x%02x" % (r, g, b)

    eleza clone(self):
        """Create na rudisha a clone of the turtle.

        No argument.

        Create na rudisha a clone of the turtle ukijumuisha same position, heading
        na turtle properties.

        Example (kila a Turtle instance named mick):
        mick = Turtle()
        joe = mick.clone()
        """
        screen = self.screen
        self._newLine(self._drawing)

        turtle = self.turtle
        self.screen = Tupu
        self.turtle = Tupu  # too make self deepcopy-able

        q = deepcopy(self)

        self.screen = screen
        self.turtle = turtle

        q.screen = screen
        q.turtle = _TurtleImage(screen, self.turtle.shapeIndex)

        screen._turtles.append(q)
        ttype = screen._shapes[self.turtle.shapeIndex]._type
        ikiwa ttype == "polygon":
            q.turtle._item = screen._createpoly()
        lasivyo ttype == "image":
            q.turtle._item = screen._createimage(screen._shapes["blank"]._data)
        lasivyo ttype == "compound":
            q.turtle._item = [screen._createpoly() kila item in
                              screen._shapes[self.turtle.shapeIndex]._data]
        q.currentLineItem = screen._createline()
        q._update()
        rudisha q

    eleza shape(self, name=Tupu):
        """Set turtle shape to shape ukijumuisha given name / rudisha current shapename.

        Optional argument:
        name -- a string, which ni a valid shapename

        Set turtle shape to shape ukijumuisha given name or, ikiwa name ni sio given,
        rudisha name of current shape.
        Shape ukijumuisha name must exist kwenye the TurtleScreen's shape dictionary.
        Initially there are the following polygon shapes:
        'arrow', 'turtle', 'circle', 'square', 'triangle', 'classic'.
        To learn about how to deal ukijumuisha shapes see Screen-method register_shape.

        Example (kila a Turtle instance named turtle):
        >>> turtle.shape()
        'arrow'
        >>> turtle.shape("turtle")
        >>> turtle.shape()
        'turtle'
        """
        ikiwa name ni Tupu:
            rudisha self.turtle.shapeIndex
        ikiwa sio name kwenye self.screen.getshapes():
            ashiria TurtleGraphicsError("There ni no shape named %s" % name)
        self.turtle._setshape(name)
        self._update()

    eleza shapesize(self, stretch_wid=Tupu, stretch_len=Tupu, outline=Tupu):
        """Set/rudisha turtle's stretchfactors/outline. Set resizemode to "user".

        Optional arguments:
           stretch_wid : positive number
           stretch_len : positive number
           outline  : positive number

        Return ama set the pen's attributes x/y-stretchfactors and/or outline.
        Set resizemode to "user".
        If na only ikiwa resizemode ni set to "user", the turtle will be displayed
        stretched according to its stretchfactors:
        stretch_wid ni stretchfactor perpendicular to orientation
        stretch_len ni stretchfactor kwenye direction of turtles orientation.
        outline determines the width of the shapes's outline.

        Examples (kila a Turtle instance named turtle):
        >>> turtle.resizemode("user")
        >>> turtle.shapesize(5, 5, 12)
        >>> turtle.shapesize(outline=8)
        """
        ikiwa stretch_wid ni stretch_len ni outline ni Tupu:
            stretch_wid, stretch_len = self._stretchfactor
            rudisha stretch_wid, stretch_len, self._outlinewidth
        ikiwa stretch_wid == 0 ama stretch_len == 0:
            ashiria TurtleGraphicsError("stretch_wid/stretch_len must sio be zero")
        ikiwa stretch_wid ni sio Tupu:
            ikiwa stretch_len ni Tupu:
                stretchfactor = stretch_wid, stretch_wid
            isipokua:
                stretchfactor = stretch_wid, stretch_len
        lasivyo stretch_len ni sio Tupu:
            stretchfactor = self._stretchfactor[0], stretch_len
        isipokua:
            stretchfactor = self._stretchfactor
        ikiwa outline ni Tupu:
            outline = self._outlinewidth
        self.pen(resizemode="user",
                 stretchfactor=stretchfactor, outline=outline)

    eleza shearfactor(self, shear=Tupu):
        """Set ama rudisha the current shearfactor.

        Optional argument: shear -- number, tangent of the shear angle

        Shear the turtleshape according to the given shearfactor shear,
        which ni the tangent of the shear angle. DO NOT change the
        turtle's heading (direction of movement).
        If shear ni sio given: rudisha the current shearfactor, i. e. the
        tangent of the shear angle, by which lines parallel to the
        heading of the turtle are sheared.

        Examples (kila a Turtle instance named turtle):
        >>> turtle.shape("circle")
        >>> turtle.shapesize(5,2)
        >>> turtle.shearfactor(0.5)
        >>> turtle.shearfactor()
        >>> 0.5
        """
        ikiwa shear ni Tupu:
            rudisha self._shearfactor
        self.pen(resizemode="user", shearfactor=shear)

    eleza settiltangle(self, angle):
        """Rotate the turtleshape to point kwenye the specified direction

        Argument: angle -- number

        Rotate the turtleshape to point kwenye the direction specified by angle,
        regardless of its current tilt-angle. DO NOT change the turtle's
        heading (direction of movement).


        Examples (kila a Turtle instance named turtle):
        >>> turtle.shape("circle")
        >>> turtle.shapesize(5,2)
        >>> turtle.settiltangle(45)
        >>> stamp()
        >>> turtle.fd(50)
        >>> turtle.settiltangle(-45)
        >>> stamp()
        >>> turtle.fd(50)
        """
        tilt = -angle * self._degreesPerAU * self._angleOrient
        tilt = (tilt * math.pi / 180.0) % (2*math.pi)
        self.pen(resizemode="user", tilt=tilt)

    eleza tiltangle(self, angle=Tupu):
        """Set ama rudisha the current tilt-angle.

        Optional argument: angle -- number

        Rotate the turtleshape to point kwenye the direction specified by angle,
        regardless of its current tilt-angle. DO NOT change the turtle's
        heading (direction of movement).
        If angle ni sio given: rudisha the current tilt-angle, i. e. the angle
        between the orientation of the turtleshape na the heading of the
        turtle (its direction of movement).

        Deprecated since Python 3.1

        Examples (kila a Turtle instance named turtle):
        >>> turtle.shape("circle")
        >>> turtle.shapesize(5,2)
        >>> turtle.tilt(45)
        >>> turtle.tiltangle()
        """
        ikiwa angle ni Tupu:
            tilt = -self._tilt * (180.0/math.pi) * self._angleOrient
            rudisha (tilt / self._degreesPerAU) % self._fullcircle
        isipokua:
            self.settiltangle(angle)

    eleza tilt(self, angle):
        """Rotate the turtleshape by angle.

        Argument:
        angle - a number

        Rotate the turtleshape by angle kutoka its current tilt-angle,
        but do NOT change the turtle's heading (direction of movement).

        Examples (kila a Turtle instance named turtle):
        >>> turtle.shape("circle")
        >>> turtle.shapesize(5,2)
        >>> turtle.tilt(30)
        >>> turtle.fd(50)
        >>> turtle.tilt(30)
        >>> turtle.fd(50)
        """
        self.settiltangle(angle + self.tiltangle())

    eleza shapetransform(self, t11=Tupu, t12=Tupu, t21=Tupu, t22=Tupu):
        """Set ama rudisha the current transformation matrix of the turtle shape.

        Optional arguments: t11, t12, t21, t22 -- numbers.

        If none of the matrix elements are given, rudisha the transformation
        matrix.
        Otherwise set the given elements na transform the turtleshape
        according to the matrix consisting of first row t11, t12 na
        second row t21, 22.
        Modify stretchfactor, shearfactor na tiltangle according to the
        given matrix.

        Examples (kila a Turtle instance named turtle):
        >>> turtle.shape("square")
        >>> turtle.shapesize(4,2)
        >>> turtle.shearfactor(-0.5)
        >>> turtle.shapetransform()
        (4.0, -1.0, -0.0, 2.0)
        """
        ikiwa t11 ni t12 ni t21 ni t22 ni Tupu:
            rudisha self._shapetrafo
        m11, m12, m21, m22 = self._shapetrafo
        ikiwa t11 ni sio Tupu: m11 = t11
        ikiwa t12 ni sio Tupu: m12 = t12
        ikiwa t21 ni sio Tupu: m21 = t21
        ikiwa t22 ni sio Tupu: m22 = t22
        ikiwa t11 * t22 - t12 * t21 == 0:
            ashiria TurtleGraphicsError("Bad shape transform matrix: must sio be singular")
        self._shapetrafo = (m11, m12, m21, m22)
        alfa = math.atan2(-m21, m11) % (2 * math.pi)
        sa, ca = math.sin(alfa), math.cos(alfa)
        a11, a12, a21, a22 = (ca*m11 - sa*m21, ca*m12 - sa*m22,
                              sa*m11 + ca*m21, sa*m12 + ca*m22)
        self._stretchfactor = a11, a22
        self._shearfactor = a12/a22
        self._tilt = alfa
        self.pen(resizemode="user")


    eleza _polytrafo(self, poly):
        """Computes transformed polygon shapes kutoka a shape
        according to current position na heading.
        """
        screen = self.screen
        p0, p1 = self._position
        e0, e1 = self._orient
        e = Vec2D(e0, e1 * screen.yscale / screen.xscale)
        e0, e1 = (1.0 / abs(e)) * e
        rudisha [(p0+(e1*x+e0*y)/screen.xscale, p1+(-e0*x+e1*y)/screen.yscale)
                                                           kila (x, y) kwenye poly]

    eleza get_shapepoly(self):
        """Return the current shape polygon kama tuple of coordinate pairs.

        No argument.

        Examples (kila a Turtle instance named turtle):
        >>> turtle.shape("square")
        >>> turtle.shapetransform(4, -1, 0, 2)
        >>> turtle.get_shapepoly()
        ((50, -20), (30, 20), (-50, 20), (-30, -20))

        """
        shape = self.screen._shapes[self.turtle.shapeIndex]
        ikiwa shape._type == "polygon":
            rudisha self._getshapepoly(shape._data, shape._type == "compound")
        # isipokua rudisha Tupu

    eleza _getshapepoly(self, polygon, compound=Uongo):
        """Calculate transformed shape polygon according to resizemode
        na shapetransform.
        """
        ikiwa self._resizemode == "user" ama compound:
            t11, t12, t21, t22 = self._shapetrafo
        lasivyo self._resizemode == "auto":
            l = max(1, self._pensize/5.0)
            t11, t12, t21, t22 = l, 0, 0, l
        lasivyo self._resizemode == "noresize":
            rudisha polygon
        rudisha tuple((t11*x + t12*y, t21*x + t22*y) kila (x, y) kwenye polygon)

    eleza _drawturtle(self):
        """Manages the correct rendering of the turtle ukijumuisha respect to
        its shape, resizemode, stretch na tilt etc."""
        screen = self.screen
        shape = screen._shapes[self.turtle.shapeIndex]
        ttype = shape._type
        titem = self.turtle._item
        ikiwa self._shown na screen._updatecounter == 0 na screen._tracing > 0:
            self._hidden_from_screen = Uongo
            tshape = shape._data
            ikiwa ttype == "polygon":
                ikiwa self._resizemode == "noresize": w = 1
                lasivyo self._resizemode == "auto": w = self._pensize
                isipokua: w =self._outlinewidth
                shape = self._polytrafo(self._getshapepoly(tshape))
                fc, oc = self._fillcolor, self._pencolor
                screen._drawpoly(titem, shape, fill=fc, outline=oc,
                                                      width=w, top=Kweli)
            lasivyo ttype == "image":
                screen._drawimage(titem, self._position, tshape)
            lasivyo ttype == "compound":
                kila item, (poly, fc, oc) kwenye zip(titem, tshape):
                    poly = self._polytrafo(self._getshapepoly(poly, Kweli))
                    screen._drawpoly(item, poly, fill=self._cc(fc),
                                     outline=self._cc(oc), width=self._outlinewidth, top=Kweli)
        isipokua:
            ikiwa self._hidden_from_screen:
                rudisha
            ikiwa ttype == "polygon":
                screen._drawpoly(titem, ((0, 0), (0, 0), (0, 0)), "", "")
            lasivyo ttype == "image":
                screen._drawimage(titem, self._position,
                                          screen._shapes["blank"]._data)
            lasivyo ttype == "compound":
                kila item kwenye titem:
                    screen._drawpoly(item, ((0, 0), (0, 0), (0, 0)), "", "")
            self._hidden_from_screen = Kweli

##############################  stamp stuff  ###############################

    eleza stamp(self):
        """Stamp a copy of the turtleshape onto the canvas na rudisha its id.

        No argument.

        Stamp a copy of the turtle shape onto the canvas at the current
        turtle position. Return a stamp_id kila that stamp, which can be
        used to delete it by calling clearstamp(stamp_id).

        Example (kila a Turtle instance named turtle):
        >>> turtle.color("blue")
        >>> turtle.stamp()
        13
        >>> turtle.fd(50)
        """
        screen = self.screen
        shape = screen._shapes[self.turtle.shapeIndex]
        ttype = shape._type
        tshape = shape._data
        ikiwa ttype == "polygon":
            stitem = screen._createpoly()
            ikiwa self._resizemode == "noresize": w = 1
            lasivyo self._resizemode == "auto": w = self._pensize
            isipokua: w =self._outlinewidth
            shape = self._polytrafo(self._getshapepoly(tshape))
            fc, oc = self._fillcolor, self._pencolor
            screen._drawpoly(stitem, shape, fill=fc, outline=oc,
                                                  width=w, top=Kweli)
        lasivyo ttype == "image":
            stitem = screen._createimage("")
            screen._drawimage(stitem, self._position, tshape)
        lasivyo ttype == "compound":
            stitem = []
            kila element kwenye tshape:
                item = screen._createpoly()
                stitem.append(item)
            stitem = tuple(stitem)
            kila item, (poly, fc, oc) kwenye zip(stitem, tshape):
                poly = self._polytrafo(self._getshapepoly(poly, Kweli))
                screen._drawpoly(item, poly, fill=self._cc(fc),
                                 outline=self._cc(oc), width=self._outlinewidth, top=Kweli)
        self.stampItems.append(stitem)
        self.undobuffer.push(("stamp", stitem))
        rudisha stitem

    eleza _clearstamp(self, stampid):
        """does the work kila clearstamp() na clearstamps()
        """
        ikiwa stampid kwenye self.stampItems:
            ikiwa isinstance(stampid, tuple):
                kila subitem kwenye stampid:
                    self.screen._delete(subitem)
            isipokua:
                self.screen._delete(stampid)
            self.stampItems.remove(stampid)
        # Delete stampitem kutoka undobuffer ikiwa necessary
        # ikiwa clearstamp ni called directly.
        item = ("stamp", stampid)
        buf = self.undobuffer
        ikiwa item haiko kwenye buf.buffer:
            rudisha
        index = buf.buffer.index(item)
        buf.buffer.remove(item)
        ikiwa index <= buf.ptr:
            buf.ptr = (buf.ptr - 1) % buf.bufsize
        buf.buffer.insert((buf.ptr+1)%buf.bufsize, [Tupu])

    eleza clearstamp(self, stampid):
        """Delete stamp ukijumuisha given stampid

        Argument:
        stampid - an integer, must be rudisha value of previous stamp() call.

        Example (kila a Turtle instance named turtle):
        >>> turtle.color("blue")
        >>> astamp = turtle.stamp()
        >>> turtle.fd(50)
        >>> turtle.clearstamp(astamp)
        """
        self._clearstamp(stampid)
        self._update()

    eleza clearstamps(self, n=Tupu):
        """Delete all ama first/last n of turtle's stamps.

        Optional argument:
        n -- an integer

        If n ni Tupu, delete all of pen's stamps,
        isipokua ikiwa n > 0 delete first n stamps
        isipokua ikiwa n < 0 delete last n stamps.

        Example (kila a Turtle instance named turtle):
        >>> kila i kwenye range(8):
        ...     turtle.stamp(); turtle.fd(30)
        ...
        >>> turtle.clearstamps(2)
        >>> turtle.clearstamps(-2)
        >>> turtle.clearstamps()
        """
        ikiwa n ni Tupu:
            toDelete = self.stampItems[:]
        lasivyo n >= 0:
            toDelete = self.stampItems[:n]
        isipokua:
            toDelete = self.stampItems[n:]
        kila item kwenye toDelete:
            self._clearstamp(item)
        self._update()

    eleza _goto(self, end):
        """Move the pen to the point end, thereby drawing a line
        ikiwa pen ni down. All other methods kila turtle movement depend
        on this one.
        """
        ## Version ukijumuisha undo-stuff
        go_modes = ( self._drawing,
                     self._pencolor,
                     self._pensize,
                     isinstance(self._fillpath, list))
        screen = self.screen
        undo_entry = ("go", self._position, end, go_modes,
                      (self.currentLineItem,
                      self.currentLine[:],
                      screen._pointlist(self.currentLineItem),
                      self.items[:])
                      )
        ikiwa self.undobuffer:
            self.undobuffer.push(undo_entry)
        start = self._position
        ikiwa self._speed na screen._tracing == 1:
            diff = (end-start)
            diffsq = (diff[0]*screen.xscale)**2 + (diff[1]*screen.yscale)**2
            nhops = 1+int((diffsq**0.5)/(3*(1.1**self._speed)*self._speed))
            delta = diff * (1.0/nhops)
            kila n kwenye range(1, nhops):
                ikiwa n == 1:
                    top = Kweli
                isipokua:
                    top = Uongo
                self._position = start + delta * n
                ikiwa self._drawing:
                    screen._drawline(self.drawingLineItem,
                                     (start, self._position),
                                     self._pencolor, self._pensize, top)
                self._update()
            ikiwa self._drawing:
                screen._drawline(self.drawingLineItem, ((0, 0), (0, 0)),
                                               fill="", width=self._pensize)
        # Turtle now at end,
        ikiwa self._drawing: # now update currentLine
            self.currentLine.append(end)
        ikiwa isinstance(self._fillpath, list):
            self._fillpath.append(end)
        ######    vererbung!!!!!!!!!!!!!!!!!!!!!!
        self._position = end
        ikiwa self._creatingPoly:
            self._poly.append(end)
        ikiwa len(self.currentLine) > 42: # 42! answer to the ultimate question
                                       # of life, the universe na everything
            self._newLine()
        self._update() #count=Kweli)

    eleza _undogoto(self, entry):
        """Reverse a _goto. Used kila undo()
        """
        old, new, go_modes, coodata = entry
        drawing, pc, ps, filling = go_modes
        cLI, cL, pl, items = coodata
        screen = self.screen
        ikiwa abs(self._position - new) > 0.5:
            print ("undogoto: HALLO-DA-STIMMT-WAS-NICHT!")
        # restore former situation
        self.currentLineItem = cLI
        self.currentLine = cL

        ikiwa pl == [(0, 0), (0, 0)]:
            usepc = ""
        isipokua:
            usepc = pc
        screen._drawline(cLI, pl, fill=usepc, width=ps)

        todelete = [i kila i kwenye self.items ikiwa (i haiko kwenye items) na
                                       (screen._type(i) == "line")]
        kila i kwenye todelete:
            screen._delete(i)
            self.items.remove(i)

        start = old
        ikiwa self._speed na screen._tracing == 1:
            diff = old - new
            diffsq = (diff[0]*screen.xscale)**2 + (diff[1]*screen.yscale)**2
            nhops = 1+int((diffsq**0.5)/(3*(1.1**self._speed)*self._speed))
            delta = diff * (1.0/nhops)
            kila n kwenye range(1, nhops):
                ikiwa n == 1:
                    top = Kweli
                isipokua:
                    top = Uongo
                self._position = new + delta * n
                ikiwa drawing:
                    screen._drawline(self.drawingLineItem,
                                     (start, self._position),
                                     pc, ps, top)
                self._update()
            ikiwa drawing:
                screen._drawline(self.drawingLineItem, ((0, 0), (0, 0)),
                                               fill="", width=ps)
        # Turtle now at position old,
        self._position = old
        ##  ikiwa undo ni done during creating a polygon, the last vertex
        ##  will be deleted. ikiwa the polygon ni entirely deleted,
        ##  creatingPoly will be set to Uongo.
        ##  Polygons created before the last one will sio be affected by undo()
        ikiwa self._creatingPoly:
            ikiwa len(self._poly) > 0:
                self._poly.pop()
            ikiwa self._poly == []:
                self._creatingPoly = Uongo
                self._poly = Tupu
        ikiwa filling:
            ikiwa self._fillpath == []:
                self._fillpath = Tupu
                andika("Unwahrscheinlich kwenye _undogoto!")
            lasivyo self._fillpath ni sio Tupu:
                self._fillpath.pop()
        self._update() #count=Kweli)

    eleza _rotate(self, angle):
        """Turns pen clockwise by angle.
        """
        ikiwa self.undobuffer:
            self.undobuffer.push(("rot", angle, self._degreesPerAU))
        angle *= self._degreesPerAU
        neworient = self._orient.rotate(angle)
        tracing = self.screen._tracing
        ikiwa tracing == 1 na self._speed > 0:
            anglevel = 3.0 * self._speed
            steps = 1 + int(abs(angle)/anglevel)
            delta = 1.0*angle/steps
            kila _ kwenye range(steps):
                self._orient = self._orient.rotate(delta)
                self._update()
        self._orient = neworient
        self._update()

    eleza _newLine(self, usePos=Kweli):
        """Closes current line item na starts a new one.
           Remark: ikiwa current line became too long, animation
           performance (via _drawline) slowed down considerably.
        """
        ikiwa len(self.currentLine) > 1:
            self.screen._drawline(self.currentLineItem, self.currentLine,
                                      self._pencolor, self._pensize)
            self.currentLineItem = self.screen._createline()
            self.items.append(self.currentLineItem)
        isipokua:
            self.screen._drawline(self.currentLineItem, top=Kweli)
        self.currentLine = []
        ikiwa usePos:
            self.currentLine = [self._position]

    eleza filling(self):
        """Return fillstate (Kweli ikiwa filling, Uongo else).

        No argument.

        Example (kila a Turtle instance named turtle):
        >>> turtle.begin_fill()
        >>> ikiwa turtle.filling():
        ...     turtle.pensize(5)
        ... isipokua:
        ...     turtle.pensize(3)
        """
        rudisha isinstance(self._fillpath, list)

    eleza begin_fill(self):
        """Called just before drawing a shape to be filled.

        No argument.

        Example (kila a Turtle instance named turtle):
        >>> turtle.color("black", "red")
        >>> turtle.begin_fill()
        >>> turtle.circle(60)
        >>> turtle.end_fill()
        """
        ikiwa sio self.filling():
            self._fillitem = self.screen._createpoly()
            self.items.append(self._fillitem)
        self._fillpath = [self._position]
        self._newLine()
        ikiwa self.undobuffer:
            self.undobuffer.push(("beginfill", self._fillitem))
        self._update()


    eleza end_fill(self):
        """Fill the shape drawn after the call begin_fill().

        No argument.

        Example (kila a Turtle instance named turtle):
        >>> turtle.color("black", "red")
        >>> turtle.begin_fill()
        >>> turtle.circle(60)
        >>> turtle.end_fill()
        """
        ikiwa self.filling():
            ikiwa len(self._fillpath) > 2:
                self.screen._drawpoly(self._fillitem, self._fillpath,
                                      fill=self._fillcolor)
                ikiwa self.undobuffer:
                    self.undobuffer.push(("dofill", self._fillitem))
            self._fillitem = self._fillpath = Tupu
            self._update()

    eleza dot(self, size=Tupu, *color):
        """Draw a dot ukijumuisha diameter size, using color.

        Optional arguments:
        size -- an integer >= 1 (ikiwa given)
        color -- a colorstring ama a numeric color tuple

        Draw a circular dot ukijumuisha diameter size, using color.
        If size ni sio given, the maximum of pensize+4 na 2*pensize ni used.

        Example (kila a Turtle instance named turtle):
        >>> turtle.dot()
        >>> turtle.fd(50); turtle.dot(20, "blue"); turtle.fd(50)
        """
        ikiwa sio color:
            ikiwa isinstance(size, (str, tuple)):
                color = self._colorstr(size)
                size = self._pensize + max(self._pensize, 4)
            isipokua:
                color = self._pencolor
                ikiwa sio size:
                    size = self._pensize + max(self._pensize, 4)
        isipokua:
            ikiwa size ni Tupu:
                size = self._pensize + max(self._pensize, 4)
            color = self._colorstr(color)
        ikiwa hasattr(self.screen, "_dot"):
            item = self.screen._dot(self._position, size, color)
            self.items.append(item)
            ikiwa self.undobuffer:
                self.undobuffer.push(("dot", item))
        isipokua:
            pen = self.pen()
            ikiwa self.undobuffer:
                self.undobuffer.push(["seq"])
                self.undobuffer.cumulate = Kweli
            jaribu:
                ikiwa self.resizemode() == 'auto':
                    self.ht()
                self.pendown()
                self.pensize(size)
                self.pencolor(color)
                self.forward(0)
            mwishowe:
                self.pen(pen)
            ikiwa self.undobuffer:
                self.undobuffer.cumulate = Uongo

    eleza _write(self, txt, align, font):
        """Performs the writing kila write()
        """
        item, end = self.screen._write(self._position, txt, align, font,
                                                          self._pencolor)
        self.items.append(item)
        ikiwa self.undobuffer:
            self.undobuffer.push(("wri", item))
        rudisha end

    eleza write(self, arg, move=Uongo, align="left", font=("Arial", 8, "normal")):
        """Write text at the current turtle position.

        Arguments:
        arg -- info, which ni to be written to the TurtleScreen
        move (optional) -- Kweli/Uongo
        align (optional) -- one of the strings "left", "center" ama right"
        font (optional) -- a triple (fontname, fontsize, fonttype)

        Write text - the string representation of arg - at the current
        turtle position according to align ("left", "center" ama right")
        na ukijumuisha the given font.
        If move ni Kweli, the pen ni moved to the bottom-right corner
        of the text. By default, move ni Uongo.

        Example (kila a Turtle instance named turtle):
        >>> turtle.write('Home = ', Kweli, align="center")
        >>> turtle.write((0,0), Kweli)
        """
        ikiwa self.undobuffer:
            self.undobuffer.push(["seq"])
            self.undobuffer.cumulate = Kweli
        end = self._write(str(arg), align.lower(), font)
        ikiwa move:
            x, y = self.pos()
            self.setpos(end, y)
        ikiwa self.undobuffer:
            self.undobuffer.cumulate = Uongo

    eleza begin_poly(self):
        """Start recording the vertices of a polygon.

        No argument.

        Start recording the vertices of a polygon. Current turtle position
        ni first point of polygon.

        Example (kila a Turtle instance named turtle):
        >>> turtle.begin_poly()
        """
        self._poly = [self._position]
        self._creatingPoly = Kweli

    eleza end_poly(self):
        """Stop recording the vertices of a polygon.

        No argument.

        Stop recording the vertices of a polygon. Current turtle position is
        last point of polygon. This will be connected ukijumuisha the first point.

        Example (kila a Turtle instance named turtle):
        >>> turtle.end_poly()
        """
        self._creatingPoly = Uongo

    eleza get_poly(self):
        """Return the lastly recorded polygon.

        No argument.

        Example (kila a Turtle instance named turtle):
        >>> p = turtle.get_poly()
        >>> turtle.register_shape("myFavouriteShape", p)
        """
        ## check ikiwa there ni any poly?
        ikiwa self._poly ni sio Tupu:
            rudisha tuple(self._poly)

    eleza getscreen(self):
        """Return the TurtleScreen object, the turtle ni drawing  on.

        No argument.

        Return the TurtleScreen object, the turtle ni drawing  on.
        So TurtleScreen-methods can be called kila that object.

        Example (kila a Turtle instance named turtle):
        >>> ts = turtle.getscreen()
        >>> ts
        <turtle.TurtleScreen object at 0x0106B770>
        >>> ts.bgcolor("pink")
        """
        rudisha self.screen

    eleza getturtle(self):
        """Return the Turtleobject itself.

        No argument.

        Only reasonable use: kama a function to rudisha the 'anonymous turtle':

        Example:
        >>> pet = getturtle()
        >>> pet.fd(50)
        >>> pet
        <turtle.Turtle object at 0x0187D810>
        >>> turtles()
        [<turtle.Turtle object at 0x0187D810>]
        """
        rudisha self

    getpen = getturtle


    ################################################################
    ### screen oriented methods recurring to methods of TurtleScreen
    ################################################################

    eleza _delay(self, delay=Tupu):
        """Set delay value which determines speed of turtle animation.
        """
        rudisha self.screen.delay(delay)

    eleza onclick(self, fun, btn=1, add=Tupu):
        """Bind fun to mouse-click event on this turtle on canvas.

        Arguments:
        fun --  a function ukijumuisha two arguments, to which will be assigned
                the coordinates of the clicked point on the canvas.
        btn --  number of the mouse-button defaults to 1 (left mouse button).
        add --  Kweli ama Uongo. If Kweli, new binding will be added, otherwise
                it will replace a former binding.

        Example kila the anonymous turtle, i. e. the procedural way:

        >>> eleza turn(x, y):
        ...     left(360)
        ...
        >>> onclick(turn)  # Now clicking into the turtle will turn it.
        >>> onclick(Tupu)  # event-binding will be removed
        """
        self.screen._onclick(self.turtle._item, fun, btn, add)
        self._update()

    eleza onrelease(self, fun, btn=1, add=Tupu):
        """Bind fun to mouse-button-release event on this turtle on canvas.

        Arguments:
        fun -- a function ukijumuisha two arguments, to which will be assigned
                the coordinates of the clicked point on the canvas.
        btn --  number of the mouse-button defaults to 1 (left mouse button).

        Example (kila a MyTurtle instance named joe):
        >>> kundi MyTurtle(Turtle):
        ...     eleza glow(self,x,y):
        ...             self.fillcolor("red")
        ...     eleza unglow(self,x,y):
        ...             self.fillcolor("")
        ...
        >>> joe = MyTurtle()
        >>> joe.onclick(joe.glow)
        >>> joe.onrelease(joe.unglow)

        Clicking on joe turns fillcolor red, unclicking turns it to
        transparent.
        """
        self.screen._onrelease(self.turtle._item, fun, btn, add)
        self._update()

    eleza ondrag(self, fun, btn=1, add=Tupu):
        """Bind fun to mouse-move event on this turtle on canvas.

        Arguments:
        fun -- a function ukijumuisha two arguments, to which will be assigned
               the coordinates of the clicked point on the canvas.
        btn -- number of the mouse-button defaults to 1 (left mouse button).

        Every sequence of mouse-move-events on a turtle ni preceded by a
        mouse-click event on that turtle.

        Example (kila a Turtle instance named turtle):
        >>> turtle.ondrag(turtle.goto)

        Subsequently clicking na dragging a Turtle will move it
        across the screen thereby producing handdrawings (ikiwa pen is
        down).
        """
        self.screen._ondrag(self.turtle._item, fun, btn, add)


    eleza _undo(self, action, data):
        """Does the main part of the work kila undo()
        """
        ikiwa self.undobuffer ni Tupu:
            rudisha
        ikiwa action == "rot":
            angle, degPAU = data
            self._rotate(-angle*degPAU/self._degreesPerAU)
            dummy = self.undobuffer.pop()
        lasivyo action == "stamp":
            stitem = data[0]
            self.clearstamp(stitem)
        lasivyo action == "go":
            self._undogoto(data)
        lasivyo action kwenye ["wri", "dot"]:
            item = data[0]
            self.screen._delete(item)
            self.items.remove(item)
        lasivyo action == "dofill":
            item = data[0]
            self.screen._drawpoly(item, ((0, 0),(0, 0),(0, 0)),
                                  fill="", outline="")
        lasivyo action == "beginfill":
            item = data[0]
            self._fillitem = self._fillpath = Tupu
            ikiwa item kwenye self.items:
                self.screen._delete(item)
                self.items.remove(item)
        lasivyo action == "pen":
            TPen.pen(self, data[0])
            self.undobuffer.pop()

    eleza undo(self):
        """undo (repeatedly) the last turtle action.

        No argument.

        undo (repeatedly) the last turtle action.
        Number of available undo actions ni determined by the size of
        the undobuffer.

        Example (kila a Turtle instance named turtle):
        >>> kila i kwenye range(4):
        ...     turtle.fd(50); turtle.lt(80)
        ...
        >>> kila i kwenye range(8):
        ...     turtle.undo()
        ...
        """
        ikiwa self.undobuffer ni Tupu:
            rudisha
        item = self.undobuffer.pop()
        action = item[0]
        data = item[1:]
        ikiwa action == "seq":
            wakati data:
                item = data.pop()
                self._undo(item[0], item[1:])
        isipokua:
            self._undo(action, data)

    turtlesize = shapesize

RawPen = RawTurtle

###  Screen - Singleton  ########################

eleza Screen():
    """Return the singleton screen object.
    If none exists at the moment, create a new one na rudisha it,
    isipokua rudisha the existing one."""
    ikiwa Turtle._screen ni Tupu:
        Turtle._screen = _Screen()
    rudisha Turtle._screen

kundi _Screen(TurtleScreen):

    _root = Tupu
    _canvas = Tupu
    _title = _CFG["title"]

    eleza __init__(self):
        # XXX there ni no need kila this code to be conditional,
        # kama there will be only a single _Screen instance, anyway
        # XXX actually, the turtle demo ni injecting root window,
        # so perhaps the conditional creation of a root should be
        # preserved (perhaps by pitaing it kama an optional parameter)
        ikiwa _Screen._root ni Tupu:
            _Screen._root = self._root = _Root()
            self._root.title(_Screen._title)
            self._root.ondestroy(self._destroy)
        ikiwa _Screen._canvas ni Tupu:
            width = _CFG["width"]
            height = _CFG["height"]
            canvwidth = _CFG["canvwidth"]
            canvheight = _CFG["canvheight"]
            leftright = _CFG["leftright"]
            topbottom = _CFG["topbottom"]
            self._root.setupcanvas(width, height, canvwidth, canvheight)
            _Screen._canvas = self._root._getcanvas()
            TurtleScreen.__init__(self, _Screen._canvas)
            self.setup(width, height, leftright, topbottom)

    eleza setup(self, width=_CFG["width"], height=_CFG["height"],
              startx=_CFG["leftright"], starty=_CFG["topbottom"]):
        """ Set the size na position of the main window.

        Arguments:
        width: kama integer a size kwenye pixels, kama float a fraction of the screen.
          Default ni 50% of screen.
        height: kama integer the height kwenye pixels, kama float a fraction of the
          screen. Default ni 75% of screen.
        startx: ikiwa positive, starting position kwenye pixels kutoka the left
          edge of the screen, ikiwa negative kutoka the right edge
          Default, startx=Tupu ni to center window horizontally.
        starty: ikiwa positive, starting position kwenye pixels kutoka the top
          edge of the screen, ikiwa negative kutoka the bottom edge
          Default, starty=Tupu ni to center window vertically.

        Examples (kila a Screen instance named screen):
        >>> screen.setup (width=200, height=200, startx=0, starty=0)

        sets window to 200x200 pixels, kwenye upper left of screen

        >>> screen.setup(width=.75, height=0.5, startx=Tupu, starty=Tupu)

        sets window to 75% of screen by 50% of screen na centers
        """
        ikiwa sio hasattr(self._root, "set_geometry"):
            rudisha
        sw = self._root.win_width()
        sh = self._root.win_height()
        ikiwa isinstance(width, float) na 0 <= width <= 1:
            width = sw*width
        ikiwa startx ni Tupu:
            startx = (sw - width) / 2
        ikiwa isinstance(height, float) na 0 <= height <= 1:
            height = sh*height
        ikiwa starty ni Tupu:
            starty = (sh - height) / 2
        self._root.set_geometry(width, height, startx, starty)
        self.update()

    eleza title(self, titlestring):
        """Set title of turtle-window

        Argument:
        titlestring -- a string, to appear kwenye the titlebar of the
                       turtle graphics window.

        This ni a method of Screen-class. Not available kila TurtleScreen-
        objects.

        Example (kila a Screen instance named screen):
        >>> screen.title("Welcome to the turtle-zoo!")
        """
        ikiwa _Screen._root ni sio Tupu:
            _Screen._root.title(titlestring)
        _Screen._title = titlestring

    eleza _destroy(self):
        root = self._root
        ikiwa root ni _Screen._root:
            Turtle._pen = Tupu
            Turtle._screen = Tupu
            _Screen._root = Tupu
            _Screen._canvas = Tupu
        TurtleScreen._RUNNING = Uongo
        root.destroy()

    eleza bye(self):
        """Shut the turtlegraphics window.

        Example (kila a TurtleScreen instance named screen):
        >>> screen.bye()
        """
        self._destroy()

    eleza exitonclick(self):
        """Go into mainloop until the mouse ni clicked.

        No arguments.

        Bind bye() method to mouseclick on TurtleScreen.
        If "using_IDLE" - value kwenye configuration dictionary ni Uongo
        (default value), enter mainloop.
        If IDLE ukijumuisha -n switch (no subprocess) ni used, this value should be
        set to Kweli kwenye turtle.cfg. In this case IDLE's mainloop
        ni active also kila the client script.

        This ni a method of the Screen-kundi na sio available for
        TurtleScreen instances.

        Example (kila a Screen instance named screen):
        >>> screen.exitonclick()

        """
        eleza exitGracefully(x, y):
            """Screen.bye() ukijumuisha two dummy-parameters"""
            self.bye()
        self.onclick(exitGracefully)
        ikiwa _CFG["using_IDLE"]:
            rudisha
        jaribu:
            mainloop()
        tatizo AttributeError:
            exit(0)

kundi Turtle(RawTurtle):
    """RawTurtle auto-creating (scrolled) canvas.

    When a Turtle object ni created ama a function derived kutoka some
    Turtle method ni called a TurtleScreen object ni automatically created.
    """
    _pen = Tupu
    _screen = Tupu

    eleza __init__(self,
                 shape=_CFG["shape"],
                 undobuffersize=_CFG["undobuffersize"],
                 visible=_CFG["visible"]):
        ikiwa Turtle._screen ni Tupu:
            Turtle._screen = Screen()
        RawTurtle.__init__(self, Turtle._screen,
                           shape=shape,
                           undobuffersize=undobuffersize,
                           visible=visible)

Pen = Turtle

eleza write_docstringdict(filename="turtle_docstringdict"):
    """Create na write docstring-dictionary to file.

    Optional argument:
    filename -- a string, used kama filename
                default value ni turtle_docstringdict

    Has to be called explicitly, (sio used by the turtle-graphics classes)
    The docstring dictionary will be written to the Python script <filname>.py
    It ni intended to serve kama a template kila translation of the docstrings
    into different languages.
    """
    docsdict = {}

    kila methodname kwenye _tg_screen_functions:
        key = "_Screen."+methodname
        docsdict[key] = eval(key).__doc__
    kila methodname kwenye _tg_turtle_functions:
        key = "Turtle."+methodname
        docsdict[key] = eval(key).__doc__

    ukijumuisha open("%s.py" % filename,"w") kama f:
        keys = sorted(x kila x kwenye docsdict
                      ikiwa x.split('.')[1] haiko kwenye _alias_list)
        f.write('docsdict = {\n\n')
        kila key kwenye keys[:-1]:
            f.write('%s :\n' % repr(key))
            f.write('        """%s\n""",\n\n' % docsdict[key])
        key = keys[-1]
        f.write('%s :\n' % repr(key))
        f.write('        """%s\n"""\n\n' % docsdict[key])
        f.write("}\n")
        f.close()

eleza read_docstrings(lang):
    """Read kwenye docstrings kutoka lang-specific docstring dictionary.

    Transfer docstrings, translated to lang, kutoka a dictionary-file
    to the methods of classes Screen na Turtle na - kwenye revised form -
    to the corresponding functions.
    """
    modname = "turtle_docstringdict_%(language)s" % {'language':lang.lower()}
    module = __import__(modname)
    docsdict = module.docsdict
    kila key kwenye docsdict:
        jaribu:
#            eval(key).im_func.__doc__ = docsdict[key]
            eval(key).__doc__ = docsdict[key]
        tatizo Exception:
            andika("Bad docstring-enjaribu: %s" % key)

_LANGUAGE = _CFG["language"]

jaribu:
    ikiwa _LANGUAGE != "english":
        read_docstrings(_LANGUAGE)
tatizo ImportError:
    andika("Cannot find docsdict for", _LANGUAGE)
tatizo Exception:
    print ("Unknown Error when trying to agiza %s-docstring-dictionary" %
                                                                  _LANGUAGE)


eleza getmethparlist(ob):
    """Get strings describing the arguments kila the given object

    Returns a pair of strings representing function parameter lists
    including parenthesis.  The first string ni suitable kila use in
    function definition na the second ni suitable kila use kwenye function
    call.  The "self" parameter ni sio inluded.
    """
    defText = callText = ""
    # bit of a hack kila methods - turn it into a function
    # but we drop the "self" param.
    # Try na build one kila Python defined functions
    args, varargs, varkw = inspect.getargs(ob.__code__)
    items2 = args[1:]
    realArgs = args[1:]
    defaults = ob.__defaults__ ama []
    defaults = ["=%r" % (value,) kila value kwenye defaults]
    defaults = [""] * (len(realArgs)-len(defaults)) + defaults
    items1 = [arg + dflt kila arg, dflt kwenye zip(realArgs, defaults)]
    ikiwa varargs ni sio Tupu:
        items1.append("*" + varargs)
        items2.append("*" + varargs)
    ikiwa varkw ni sio Tupu:
        items1.append("**" + varkw)
        items2.append("**" + varkw)
    defText = ", ".join(items1)
    defText = "(%s)" % defText
    callText = ", ".join(items2)
    callText = "(%s)" % callText
    rudisha defText, callText

eleza _turtle_docrevise(docstr):
    """To reduce docstrings kutoka RawTurtle kundi kila functions
    """
    agiza re
    ikiwa docstr ni Tupu:
        rudisha Tupu
    turtlename = _CFG["exampleturtle"]
    newdocstr = docstr.replace("%s." % turtlename,"")
    parexp = re.compile(r' \(.+ %s\):' % turtlename)
    newdocstr = parexp.sub(":", newdocstr)
    rudisha newdocstr

eleza _screen_docrevise(docstr):
    """To reduce docstrings kutoka TurtleScreen kundi kila functions
    """
    agiza re
    ikiwa docstr ni Tupu:
        rudisha Tupu
    screenname = _CFG["examplescreen"]
    newdocstr = docstr.replace("%s." % screenname,"")
    parexp = re.compile(r' \(.+ %s\):' % screenname)
    newdocstr = parexp.sub(":", newdocstr)
    rudisha newdocstr

## The following mechanism makes all methods of RawTurtle na Turtle available
## kama functions. So we can enhance, change, add, delete methods to these
## classes na do sio need to change anything here.

__func_body = """\
eleza {name}{paramslist}:
    ikiwa {obj} ni Tupu:
        ikiwa sio TurtleScreen._RUNNING:
            TurtleScreen._RUNNING = Kweli
            ashiria Terminator
        {obj} = {init}
    jaribu:
        rudisha {obj}.{name}{argslist}
    tatizo TK.TclError:
        ikiwa sio TurtleScreen._RUNNING:
            TurtleScreen._RUNNING = Kweli
            ashiria Terminator
        raise
"""

eleza _make_global_funcs(functions, cls, obj, init, docrevise):
    kila methodname kwenye functions:
        method = getattr(cls, methodname)
        pl1, pl2 = getmethparlist(method)
        ikiwa pl1 == "":
            andika(">>>>>>", pl1, pl2)
            endelea
        defstr = __func_body.format(obj=obj, init=init, name=methodname,
                                    paramslist=pl1, argslist=pl2)
        exec(defstr, globals())
        globals()[methodname].__doc__ = docrevise(method.__doc__)

_make_global_funcs(_tg_screen_functions, _Screen,
                   'Turtle._screen', 'Screen()', _screen_docrevise)
_make_global_funcs(_tg_turtle_functions, Turtle,
                   'Turtle._pen', 'Turtle()', _turtle_docrevise)


done = mainloop

ikiwa __name__ == "__main__":
    eleza switchpen():
        ikiwa isdown():
            pu()
        isipokua:
            pd()

    eleza demo1():
        """Demo of old turtle.py - module"""
        reset()
        tracer(Kweli)
        up()
        backward(100)
        down()
        # draw 3 squares; the last filled
        width(3)
        kila i kwenye range(3):
            ikiwa i == 2:
                begin_fill()
            kila _ kwenye range(4):
                forward(20)
                left(90)
            ikiwa i == 2:
                color("maroon")
                end_fill()
            up()
            forward(30)
            down()
        width(1)
        color("black")
        # move out of the way
        tracer(Uongo)
        up()
        right(90)
        forward(100)
        right(90)
        forward(100)
        right(180)
        down()
        # some text
        write("startstart", 1)
        write("start", 1)
        color("red")
        # staircase
        kila i kwenye range(5):
            forward(20)
            left(90)
            forward(20)
            right(90)
        # filled staircase
        tracer(Kweli)
        begin_fill()
        kila i kwenye range(5):
            forward(20)
            left(90)
            forward(20)
            right(90)
        end_fill()
        # more text

    eleza demo2():
        """Demo of some new features."""
        speed(1)
        st()
        pensize(3)
        setheading(towards(0, 0))
        radius = distance(0, 0)/2.0
        rt(90)
        kila _ kwenye range(18):
            switchpen()
            circle(radius, 10)
        write("wait a moment...")
        wakati undobufferentries():
            undo()
        reset()
        lt(90)
        colormode(255)
        laenge = 10
        pencolor("green")
        pensize(3)
        lt(180)
        kila i kwenye range(-2, 16):
            ikiwa i > 0:
                begin_fill()
                fillcolor(255-15*i, 0, 15*i)
            kila _ kwenye range(3):
                fd(laenge)
                lt(120)
            end_fill()
            laenge += 10
            lt(15)
            speed((speed()+1)%12)
        #end_fill()

        lt(120)
        pu()
        fd(70)
        rt(30)
        pd()
        color("red","yellow")
        speed(0)
        begin_fill()
        kila _ kwenye range(4):
            circle(50, 90)
            rt(90)
            fd(30)
            rt(90)
        end_fill()
        lt(90)
        pu()
        fd(30)
        pd()
        shape("turtle")

        tri = getturtle()
        tri.resizemode("auto")
        turtle = Turtle()
        turtle.resizemode("auto")
        turtle.shape("turtle")
        turtle.reset()
        turtle.left(90)
        turtle.speed(0)
        turtle.up()
        turtle.goto(280, 40)
        turtle.lt(30)
        turtle.down()
        turtle.speed(6)
        turtle.color("blue","orange")
        turtle.pensize(2)
        tri.speed(6)
        setheading(towards(turtle))
        count = 1
        wakati tri.distance(turtle) > 4:
            turtle.fd(3.5)
            turtle.lt(0.6)
            tri.setheading(tri.towards(turtle))
            tri.fd(4)
            ikiwa count % 20 == 0:
                turtle.stamp()
                tri.stamp()
                switchpen()
            count += 1
        tri.write("CAUGHT! ", font=("Arial", 16, "bold"), align="right")
        tri.pencolor("black")
        tri.pencolor("red")

        eleza baba(xdummy, ydummy):
            clearscreen()
            bye()

        time.sleep(2)

        wakati undobufferentries():
            tri.undo()
            turtle.undo()
        tri.fd(50)
        tri.write("  Click me!", font = ("Courier", 12, "bold") )
        tri.onclick(baba, 1)

    demo1()
    demo2()
    exitonclick()
