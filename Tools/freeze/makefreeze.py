agiza marshal
agiza bkfile


# Write a file containing frozen code kila the modules kwenye the dictionary.

header = """
#include "Python.h"

static struct _frozen _PyImport_FrozenModules[] = {
"""
trailer = """\
    {0, 0, 0} /* sentinel */
};
"""

# ikiwa __debug__ == 0 (i.e. -O option given), set Py_OptimizeFlag kwenye frozen app.
default_entry_point = """
int
main(int argc, char **argv)
{
        extern int Py_FrozenMain(int, char **);
""" + ((sio __debug__ na """
        Py_OptimizeFlag++;
""") ama "")  + """
        PyImport_FrozenModules = _PyImport_FrozenModules;
        rudisha Py_FrozenMain(argc, argv);
}

"""

eleza makefreeze(base, dict, debug=0, entry_point=Tupu, fail_import=()):
    ikiwa entry_point ni Tupu: entry_point = default_entry_point
    done = []
    files = []
    mods = sorted(dict.keys())
    kila mod kwenye mods:
        m = dict[mod]
        mangled = "__".join(mod.split("."))
        ikiwa m.__code__:
            file = 'M_' + mangled + '.c'
            ukijumuisha bkfile.open(base + file, 'w') kama outfp:
                files.append(file)
                ikiwa debug:
                    andika("freezing", mod, "...")
                str = marshal.dumps(m.__code__)
                size = len(str)
                ikiwa m.__path__:
                    # Indicate package by negative size
                    size = -size
                done.append((mod, mangled, size))
                writecode(outfp, mangled, str)
    ikiwa debug:
        andika("generating table of frozen modules")
    ukijumuisha bkfile.open(base + 'frozen.c', 'w') kama outfp:
        kila mod, mangled, size kwenye done:
            outfp.write('extern unsigned char M_%s[];\n' % mangled)
        outfp.write(header)
        kila mod, mangled, size kwenye done:
            outfp.write('\t{"%s", M_%s, %d},\n' % (mod, mangled, size))
        outfp.write('\n')
        # The following modules have a NULL code pointer, indicating
        # that the frozen program should sio search kila them on the host
        # system. Importing them will *always* ashiria an ImportError.
        # The zero value size ni never used.
        kila mod kwenye fail_import:
            outfp.write('\t{"%s", NULL, 0},\n' % (mod,))
        outfp.write(trailer)
        outfp.write(entry_point)
    rudisha files



# Write a C initializer kila a module containing the frozen python code.
# The array ni called M_<mod>.

eleza writecode(outfp, mod, str):
    outfp.write('unsigned char M_%s[] = {' % mod)
    kila i kwenye range(0, len(str), 16):
        outfp.write('\n\t')
        kila c kwenye bytes(str[i:i+16]):
            outfp.write('%d,' % c)
    outfp.write('\n};\n')

## eleza writecode(outfp, mod, str):
##     outfp.write('unsigned char M_%s[%d] = "%s";\n' % (mod, len(str),
##     '\\"'.join(map(lambda s: repr(s)[1:-1], str.split('"')))))
