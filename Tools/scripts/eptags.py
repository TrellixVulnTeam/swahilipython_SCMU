#! /usr/bin/env python3
"""Create a TAGS file kila Python programs, usable ukijumuisha GNU Emacs.

usage: eptags pyfiles...

The output TAGS file ni usable ukijumuisha Emacs version 18, 19, 20.
Tagged are:
 - functions (even inside other defs ama classes)
 - classes

eptags warns about files it cansio open.
eptags will sio give warnings about duplicate tags.

BUGS:
   Because of tag duplication (methods ukijumuisha the same name kwenye different
   classes), TAGS files are sio very useful kila most object-oriented
   python projects.
"""
agiza sys,re

expr = r'^[ \t]*(def|class)[ \t]+([a-zA-Z_][a-zA-Z0-9_]*)[ \t]*[:\(]'
matcher = re.compile(expr)

eleza treat_file(filename, outfp):
    """Append tags found kwenye file named 'filename' to the open file 'outfp'"""
    jaribu:
        fp = open(filename, 'r')
    tatizo OSError:
        sys.stderr.write('Cansio open %s\n'%filename)
        rudisha
    ukijumuisha fp:
        charno = 0
        lineno = 0
        tags = []
        size = 0
        wakati 1:
            line = fp.readline()
            ikiwa sio line:
                koma
            lineno = lineno + 1
            m = matcher.search(line)
            ikiwa m:
                tag = m.group(0) + '\177%d,%d\n' % (lineno, charno)
                tags.append(tag)
                size = size + len(tag)
            charno = charno + len(line)
    outfp.write('\f\n%s,%d\n' % (filename,size))
    kila tag kwenye tags:
        outfp.write(tag)

eleza main():
    ukijumuisha open('TAGS', 'w') kama outfp:
        kila filename kwenye sys.argv[1:]:
            treat_file(filename, outfp)

ikiwa __name__=="__main__":
    main()
