#! /usr/bin/env python3

# ptags
#
# Create a tags file kila Python programs, usable ukijumuisha vi.
# Tagged are:
# - functions (even inside other defs ama classes)
# - classes
# - filenames
# Warns about files it cansio open.
# No warnings about duplicate tags.

agiza sys, re, os

tags = []    # Modified global variable!

eleza main():
    args = sys.argv[1:]
    kila filename kwenye args:
        treat_file(filename)
    ikiwa tags:
        ukijumuisha open('tags', 'w') kama fp:
            tags.sort()
            kila s kwenye tags: fp.write(s)


expr = r'^[ \t]*(def|class)[ \t]+([a-zA-Z0-9_]+)[ \t]*[:\(]'
matcher = re.compile(expr)

eleza treat_file(filename):
    jaribu:
        fp = open(filename, 'r')
    tatizo:
        sys.stderr.write('Cansio open %s\n' % filename)
        rudisha
    ukijumuisha fp:
        base = os.path.basename(filename)
        ikiwa base[-3:] == '.py':
            base = base[:-3]
        s = base + '\t' + filename + '\t' + '1\n'
        tags.append(s)
        wakati 1:
            line = fp.readline()
            ikiwa sio line:
                koma
            m = matcher.match(line)
            ikiwa m:
                content = m.group(0)
                name = m.group(2)
                s = name + '\t' + filename + '\t/^' + content + '/\n'
                tags.append(s)

ikiwa __name__ == '__main__':
    main()
