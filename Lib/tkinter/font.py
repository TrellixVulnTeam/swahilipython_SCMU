# Tkinter font wrapper
#
# written by Fredrik Lundh, February 1998
#

__version__ = "0.9"

agiza itertools
agiza tkinter


# weight/slant
NORMAL = "normal"
ROMAN = "roman"
BOLD   = "bold"
ITALIC = "italic"


eleza nametofont(name):
    """Given the name of a tk named font, returns a Font representation.
    """
    rudisha Font(name=name, exists=Kweli)


kundi Font:
    """Represents a named font.

    Constructor options are:

    font -- font specifier (name, system font, ama (family, size, style)-tuple)
    name -- name to use kila this font configuration (defaults to a unique name)
    exists -- does a named font by this name already exist?
       Creates a new named font ikiwa Uongo, points to the existing font ikiwa Kweli.
       Raises _tkinter.TclError ikiwa the assertion ni false.

       the following are ignored ikiwa font ni specified:

    family -- font 'family', e.g. Courier, Times, Helvetica
    size -- font size kwenye points
    weight -- font thickness: NORMAL, BOLD
    slant -- font slant: ROMAN, ITALIC
    underline -- font underlining: false (0), true (1)
    overstrike -- font strikeout: false (0), true (1)

    """

    counter = itertools.count(1)

    eleza _set(self, kw):
        options = []
        kila k, v kwenye kw.items():
            options.append("-"+k)
            options.append(str(v))
        rudisha tuple(options)

    eleza _get(self, args):
        options = []
        kila k kwenye args:
            options.append("-"+k)
        rudisha tuple(options)

    eleza _mkdict(self, args):
        options = {}
        kila i kwenye range(0, len(args), 2):
            options[args[i][1:]] = args[i+1]
        rudisha options

    eleza __init__(self, root=Tupu, font=Tupu, name=Tupu, exists=Uongo,
                 **options):
        ikiwa sio root:
            root = tkinter._default_root
        tk = getattr(root, 'tk', root)
        ikiwa font:
            # get actual settings corresponding to the given font
            font = tk.splitlist(tk.call("font", "actual", font))
        isipokua:
            font = self._set(options)
        ikiwa sio name:
            name = "font" + str(next(self.counter))
        self.name = name

        ikiwa exists:
            self.delete_font = Uongo
            # confirm font exists
            ikiwa self.name haiko kwenye tk.splitlist(tk.call("font", "names")):
                ashiria tkinter._tkinter.TclError(
                    "named font %s does sio already exist" % (self.name,))
            # ikiwa font config info supplied, apply it
            ikiwa font:
                tk.call("font", "configure", self.name, *font)
        isipokua:
            # create new font (raises TclError ikiwa the font exists)
            tk.call("font", "create", self.name, *font)
            self.delete_font = Kweli
        self._tk = tk
        self._split = tk.splitlist
        self._call  = tk.call

    eleza __str__(self):
        rudisha self.name

    eleza __eq__(self, other):
        rudisha isinstance(other, Font) na self.name == other.name

    eleza __getitem__(self, key):
        rudisha self.cget(key)

    eleza __setitem__(self, key, value):
        self.configure(**{key: value})

    eleza __del__(self):
        jaribu:
            ikiwa self.delete_font:
                self._call("font", "delete", self.name)
        tatizo Exception:
            pita

    eleza copy(self):
        "Return a distinct copy of the current font"
        rudisha Font(self._tk, **self.actual())

    eleza actual(self, option=Tupu, displayof=Tupu):
        "Return actual font attributes"
        args = ()
        ikiwa displayof:
            args = ('-displayof', displayof)
        ikiwa option:
            args = args + ('-' + option, )
            rudisha self._call("font", "actual", self.name, *args)
        isipokua:
            rudisha self._mkdict(
                self._split(self._call("font", "actual", self.name, *args)))

    eleza cget(self, option):
        "Get font attribute"
        rudisha self._call("font", "config", self.name, "-"+option)

    eleza config(self, **options):
        "Modify font attributes"
        ikiwa options:
            self._call("font", "config", self.name,
                  *self._set(options))
        isipokua:
            rudisha self._mkdict(
                self._split(self._call("font", "config", self.name)))

    configure = config

    eleza measure(self, text, displayof=Tupu):
        "Return text width"
        args = (text,)
        ikiwa displayof:
            args = ('-displayof', displayof, text)
        rudisha self._tk.getint(self._call("font", "measure", self.name, *args))

    eleza metrics(self, *options, **kw):
        """Return font metrics.

        For best performance, create a dummy widget
        using this font before calling this method."""
        args = ()
        displayof = kw.pop('displayof', Tupu)
        ikiwa displayof:
            args = ('-displayof', displayof)
        ikiwa options:
            args = args + self._get(options)
            rudisha self._tk.getint(
                self._call("font", "metrics", self.name, *args))
        isipokua:
            res = self._split(self._call("font", "metrics", self.name, *args))
            options = {}
            kila i kwenye range(0, len(res), 2):
                options[res[i][1:]] = self._tk.getint(res[i+1])
            rudisha options


eleza families(root=Tupu, displayof=Tupu):
    "Get font families (as a tuple)"
    ikiwa sio root:
        root = tkinter._default_root
    args = ()
    ikiwa displayof:
        args = ('-displayof', displayof)
    rudisha root.tk.splitlist(root.tk.call("font", "families", *args))


eleza names(root=Tupu):
    "Get names of defined fonts (as a tuple)"
    ikiwa sio root:
        root = tkinter._default_root
    rudisha root.tk.splitlist(root.tk.call("font", "names"))


# --------------------------------------------------------------------
# test stuff

ikiwa __name__ == "__main__":

    root = tkinter.Tk()

    # create a font
    f = Font(family="times", size=30, weight=NORMAL)

    andika(f.actual())
    andika(f.actual("family"))
    andika(f.actual("weight"))

    andika(f.config())
    andika(f.cget("family"))
    andika(f.cget("weight"))

    andika(names())

    andika(f.measure("hello"), f.metrics("linespace"))

    andika(f.metrics(displayof=root))

    f = Font(font=("Courier", 20, "bold"))
    andika(f.measure("hello"), f.metrics("linespace", displayof=root))

    w = tkinter.Label(root, text="Hello, world", font=f)
    w.pack()

    w = tkinter.Button(root, text="Quit!", command=root.destroy)
    w.pack()

    fb = Font(font=w["font"]).copy()
    fb.config(weight=BOLD)

    w.config(font=fb)

    tkinter.mainloop()
