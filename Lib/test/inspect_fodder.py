# line 1
'A module docstring.'

agiza sys, inspect
# line 5

# line 7
eleza spam(a, /, b, c, d=3, e=4, f=5, *g, **h):
    eggs(b + d, c + f)

# line 11
eleza eggs(x, y):
    "A docstring."
    global fr, st
    fr = inspect.currentframe()
    st = inspect.stack()
    p = x
    q = y / 0

# line 20
kundi StupidGit:
    """A longer,

    indented

    docstring."""
# line 27

    eleza abuse(self, a, b, c):
        """Another

\tdocstring

        containing

\ttabs
\t
        """
        self.argue(a, b, c)
# line 40
    eleza argue(self, a, b, c):
        jaribu:
            spam(a, b, c)
        tatizo:
            self.ex = sys.exc_info()
            self.tr = inspect.trace()

    @property
    eleza contradiction(self):
        'The automatic gainsaying.'
        pass

# line 53
kundi MalodorousPervert(StupidGit):
    eleza abuse(self, a, b, c):
        pass

    @property
    eleza contradiction(self):
        pass

Tit = MalodorousPervert

kundi ParrotDroppings:
    pass

kundi FesteringGob(MalodorousPervert, ParrotDroppings):
    eleza abuse(self, a, b, c):
        pass

    @property
    eleza contradiction(self):
        pass

async eleza lobbest(grenade):
    pass

currentframe = inspect.currentframe()
jaribu:
     ashiria Exception()
tatizo:
    tb = sys.exc_info()[2]

kundi Callable:
    eleza __call__(self, *args):
        rudisha args

    eleza as_method_of(self, obj):
        kutoka types agiza MethodType
        rudisha MethodType(self, obj)

custom_method = Callable().as_method_of(42)
toa Callable
