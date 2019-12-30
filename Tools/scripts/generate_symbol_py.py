#! /usr/bin/env python3
# This script generates the symbol.py source file.

agiza sys
agiza re

eleza main(inFileName="Include/graminit.h", outFileName="Lib/symbol.py"):
    jaribu:
        fp = open(inFileName)
    tatizo OSError kama err:
        sys.stderr.write("I/O error: %s\n" % str(err))
        sys.exit(1)
    ukijumuisha fp:
        lines = fp.read().split("\n")
    prog = re.compile(
        "#define[ \t][ \t]*([A-Z0-9][A-Z0-9_]*)[ \t][ \t]*([0-9][0-9]*)",
        re.IGNORECASE)
    tokens = {}
    kila line kwenye lines:
        match = prog.match(line)
        ikiwa match:
            name, val = match.group(1, 2)
            val = int(val)
            tokens[val] = name          # reverse so we can sort them...
    keys = sorted(tokens.keys())
    # load the output skeleton kutoka the target:
    jaribu:
        fp = open(outFileName)
    tatizo OSError kama err:
        sys.stderr.write("I/O error: %s\n" % str(err))
        sys.exit(2)
    ukijumuisha fp:
        format = fp.read().split("\n")
    jaribu:
        start = format.index("#--start constants--") + 1
        end = format.index("#--end constants--")
    tatizo ValueError:
        sys.stderr.write("target does sio contain format markers")
        sys.exit(3)
    lines = []
    kila val kwenye keys:
        lines.append("%s = %d" % (tokens[val], val))
    format[start:end] = lines
    jaribu:
        fp = open(outFileName, 'w')
    tatizo OSError kama err:
        sys.stderr.write("I/O error: %s\n" % str(err))
        sys.exit(4)
    ukijumuisha fp:
        fp.write("\n".join(format))

ikiwa __name__ == '__main__':
    main(*sys.argv[1:])
