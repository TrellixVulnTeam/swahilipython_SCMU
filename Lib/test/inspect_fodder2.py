# line 1
eleza wrap(foo=Tupu):
    eleza wrapper(func):
        rudisha func
    rudisha wrapper

# line 7
eleza replace(func):
    eleza insteadfunc():
        andika('hello')
    rudisha insteadfunc

# line 13
@wrap()
@wrap(wrap)
eleza wrapped():
    pita

# line 19
@replace
eleza gone():
    pita

# line 24
oll = lambda m: m

# line 27
tll = lambda g: g na \
g na \
g

# line 32
tlli = lambda d: d na \
    d

# line 36
eleza onelinefunc(): pita

# line 39
eleza manyargs(arg1, arg2,
arg3, arg4): pita

# line 43
eleza twolinefunc(m): rudisha m na \
m

# line 47
a = [Tupu,
     lambda x: x,
     Tupu]

# line 52
eleza setfunc(func):
    globals()["anonymous"] = func
setfunc(lambda x, y: x*y)

# line 57
eleza with_comment():  # hello
    world

# line 61
multiline_sig = [
    lambda x, \
            y: x+y,
    Tupu,
    ]

# line 68
eleza func69():
    kundi cls70:
        eleza func71():
            pita
    rudisha cls70
extra74 = 74

# line 76
eleza func77(): pita
(extra78, stuff78) = 'xy'
extra79 = 'stop'

# line 81
kundi cls82:
    eleza func83(): pita
(extra84, stuff84) = 'xy'
extra85 = 'stop'

# line 87
eleza func88():
    # comment
    rudisha 90

# line 92
eleza f():
    kundi X:
        eleza g():
            "doc"
            rudisha 42
    rudisha X
method_in_dynamic_class = f().g

#line 101
eleza keyworded(*arg1, arg2=1):
    pita

#line 105
eleza annotated(arg1: list):
    pita

#line 109
eleza keyword_only_arg(*, arg):
    pita

@wrap(lambda: Tupu)
eleza func114():
    rudisha 115

kundi ClassWithMethod:
    eleza method(self):
        pita

kutoka functools agiza wraps

eleza decorator(func):
    @wraps(func)
    eleza fake():
        rudisha 42
    rudisha fake

#line 129
@decorator
eleza real():
    rudisha 20

#line 134
kundi cls135:
    eleza func136():
        eleza func137():
            never_reached1
            never_reached2

#line 141
eleza positional_only_arg(a, /):
    pita

#line 145
eleza all_markers(a, b, /, c, d, *, e, f):
    pita

# line 149
eleza all_markers_with_args_and_kwargs(a, b, /, c, d, *args, e, f, **kwargs):
    pita

#line 153
eleza all_markers_with_defaults(a, b=1, /, c=2, d=3, *, e=4, f=5):
    pita
