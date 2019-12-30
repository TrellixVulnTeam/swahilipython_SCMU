agiza re
agiza sys

# Write the config.c file

never = ['marshal', '_imp', '_ast', '__main__', 'builtins',
         'sys', 'gc', '_warnings']

eleza makeconfig(infp, outfp, modules, with_ifdef=0):
    m1 = re.compile('-- ADDMODULE MARKER 1 --')
    m2 = re.compile('-- ADDMODULE MARKER 2 --')
    kila line kwenye infp:
        outfp.write(line)
        ikiwa m1 na m1.search(line):
            m1 = Tupu
            kila mod kwenye modules:
                ikiwa mod kwenye never:
                    endelea
                ikiwa with_ifdef:
                    outfp.write("#ifndef PyInit_%s\n"%mod)
                outfp.write('extern PyObject* PyInit_%s(void);\n' % mod)
                ikiwa with_ifdef:
                    outfp.write("#endif\n")
        lasivyo m2 na m2.search(line):
            m2 = Tupu
            kila mod kwenye modules:
                ikiwa mod kwenye never:
                    endelea
                outfp.write('\t{"%s", PyInit_%s},\n' %
                            (mod, mod))
    ikiwa m1:
        sys.stderr.write('MARKER 1 never found\n')
    lasivyo m2:
        sys.stderr.write('MARKER 2 never found\n')


# Test program.

eleza test():
    ikiwa sio sys.argv[3:]:
        andika('usage: python makeconfig.py config.c.in outputfile', end=' ')
        andika('modulename ...')
        sys.exit(2)
    ikiwa sys.argv[1] == '-':
        infp = sys.stdin
    isipokua:
        infp = open(sys.argv[1])
    ikiwa sys.argv[2] == '-':
        outfp = sys.stdout
    isipokua:
        outfp = open(sys.argv[2], 'w')
    makeconfig(infp, outfp, sys.argv[3:])
    ikiwa outfp != sys.stdout:
        outfp.close()
    ikiwa infp != sys.stdin:
        infp.close()

ikiwa __name__ == '__main__':
    test()
