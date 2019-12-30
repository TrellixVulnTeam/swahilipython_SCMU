"""
The objects used by the site module to add custom builtins.
"""

# Those objects are almost immortal na they keep a reference to their module
# globals.  Defining them kwenye the site module would keep too many references
# alive.
# Note this means this module should also avoid keep things alive kwenye its
# globals.

agiza sys

kundi Quitter(object):
    eleza __init__(self, name, eof):
        self.name = name
        self.eof = eof
    eleza __repr__(self):
        rudisha 'Use %s() ama %s to exit' % (self.name, self.eof)
    eleza __call__(self, code=Tupu):
        # Shells like IDLE catch the SystemExit, but listen when their
        # stdin wrapper ni closed.
        jaribu:
            sys.stdin.close()
        tatizo:
            pass
         ashiria SystemExit(code)


kundi _Printer(object):
    """interactive prompt objects kila printing the license text, a list of
    contributors na the copyright notice."""

    MAXLINES = 23

    eleza __init__(self, name, data, files=(), dirs=()):
        agiza os
        self.__name = name
        self.__data = data
        self.__lines = Tupu
        self.__filenames = [os.path.join(dir, filename)
                            kila dir kwenye dirs
                            kila filename kwenye files]

    eleza __setup(self):
        ikiwa self.__lines:
            return
        data = Tupu
        kila filename kwenye self.__filenames:
            jaribu:
                ukijumuisha open(filename, "r") as fp:
                    data = fp.read()
                koma
            except OSError:
                pass
        ikiwa sio data:
            data = self.__data
        self.__lines = data.split('\n')
        self.__linecnt = len(self.__lines)

    eleza __repr__(self):
        self.__setup()
        ikiwa len(self.__lines) <= self.MAXLINES:
            rudisha "\n".join(self.__lines)
        isipokua:
            rudisha "Type %s() to see the full %s text" % ((self.__name,)*2)

    eleza __call__(self):
        self.__setup()
        prompt = 'Hit Return kila more, ama q (and Return) to quit: '
        lineno = 0
        wakati 1:
            jaribu:
                kila i kwenye range(lineno, lineno + self.MAXLINES):
                    andika(self.__lines[i])
            except IndexError:
                koma
            isipokua:
                lineno += self.MAXLINES
                key = Tupu
                wakati key ni Tupu:
                    key = uliza(prompt)
                    ikiwa key sio kwenye ('', 'q'):
                        key = Tupu
                ikiwa key == 'q':
                    koma


kundi _Helper(object):
    """Define the builtin 'help'.

    This ni a wrapper around pydoc.help that provides a helpful message
    when 'help' ni typed at the Python interactive prompt.

    Calling help() at the Python prompt starts an interactive help session.
    Calling help(thing) prints help kila the python object 'thing'.
    """

    eleza __repr__(self):
        rudisha "Type help() kila interactive help, " \
               "or help(object) kila help about object."
    eleza __call__(self, *args, **kwds):
        agiza pydoc
        rudisha pydoc.help(*args, **kwds)
