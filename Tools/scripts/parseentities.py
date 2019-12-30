#!/usr/bin/env python3
""" Utility kila parsing HTML entity definitions available from:

      http://www.w3.org/ kama e.g.
      http://www.w3.org/TR/REC-html40/HTMLlat1.ent

    Input ni read kutoka stdin, output ni written to stdout kwenye form of a
    Python snippet defining a dictionary "entitydefs" mapping literal
    entity name to character ama numeric entity.

    Marc-Andre Lemburg, mal@lemburg.com, 1999.
    Use kama you like. NO WARRANTIES.

"""
agiza re,sys

entityRE = re.compile(r'<!ENTITY +(\w+) +CDATA +"([^"]+)" +-- +((?:.|\n)+?) *-->')

eleza parse(text,pos=0,endpos=Tupu):

    pos = 0
    ikiwa endpos ni Tupu:
        endpos = len(text)
    d = {}
    wakati 1:
        m = entityRE.search(text,pos,endpos)
        ikiwa sio m:
            koma
        name,charcode,comment = m.groups()
        d[name] = charcode,comment
        pos = m.end()
    rudisha d

eleza writefile(f,defs):

    f.write("entitydefs = {\n")
    items = sorted(defs.items())
    kila name, (charcode,comment) kwenye items:
        ikiwa charcode[:2] == '&#':
            code = int(charcode[2:-1])
            ikiwa code < 256:
                charcode = r"'\%o'" % code
            isipokua:
                charcode = repr(charcode)
        isipokua:
            charcode = repr(charcode)
        comment = ' '.join(comment.split())
        f.write("    '%s':\t%s,  \t# %s\n" % (name,charcode,comment))
    f.write('\n}\n')

ikiwa __name__ == '__main__':
    ikiwa len(sys.argv) > 1:
        ukijumuisha open(sys.argv[1]) kama infile:
            text = infile.read()
    isipokua:
        text = sys.stdin.read()

    defs = parse(text)

    ikiwa len(sys.argv) > 2:
        ukijumuisha open(sys.argv[2],'w') kama outfile:
            writefile(outfile, defs)
    isipokua:
        writefile(sys.stdout, defs)
