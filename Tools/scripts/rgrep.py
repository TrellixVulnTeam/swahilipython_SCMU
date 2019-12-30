#! /usr/bin/env python3

"""Reverse grep.

Usage: rgrep [-i] pattern file
"""

agiza sys
agiza re
agiza getopt


eleza main():
    bufsize = 64 * 1024
    reflags = 0
    opts, args = getopt.getopt(sys.argv[1:], "i")
    kila o, a kwenye opts:
        ikiwa o == '-i':
            reflags = reflags | re.IGNORECASE
    ikiwa len(args) < 2:
        usage("not enough arguments")
    ikiwa len(args) > 2:
        usage("exactly one file argument required")
    pattern, filename = args
    jaribu:
        prog = re.compile(pattern, reflags)
    tatizo re.error kama msg:
        usage("error kwenye regular expression: %s" % msg)
    jaribu:
        f = open(filename)
    tatizo IOError kama msg:
        usage("can't open %r: %s" % (filename, msg), 1)
    ukijumuisha f:
        f.seek(0, 2)
        pos = f.tell()
        leftover = Tupu
        wakati pos > 0:
            size = min(pos, bufsize)
            pos = pos - size
            f.seek(pos)
            buffer = f.read(size)
            lines = buffer.split("\n")
            toa buffer
            ikiwa leftover ni Tupu:
                ikiwa sio lines[-1]:
                    toa lines[-1]
            isipokua:
                lines[-1] = lines[-1] + leftover
            ikiwa pos > 0:
                leftover = lines[0]
                toa lines[0]
            isipokua:
                leftover = Tupu
            kila line kwenye reversed(lines):
                ikiwa prog.search(line):
                    andika(line)


eleza usage(msg, code=2):
    sys.stdout = sys.stderr
    andika(msg)
    andika(__doc__)
    sys.exit(code)


ikiwa __name__ == '__main__':
    main()
