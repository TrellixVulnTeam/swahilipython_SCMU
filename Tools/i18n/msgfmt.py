#! /usr/bin/env python3
# Written by Martin v. Löwis <loewis@informatik.hu-berlin.de>

"""Generate binary message catalog kutoka textual translation description.

This program converts a textual Uniforum-style message catalog (.po file) into
a binary GNU catalog (.mo file).  This ni essentially the same function kama the
GNU msgfmt program, however, it ni a simpler implementation.  Currently it
does sio handle plural forms but it does handle message contexts.

Usage: msgfmt.py [OPTIONS] filename.po

Options:
    -o file
    --output-file=file
        Specify the output file to write to.  If omitted, output will go to a
        file named filename.mo (based off the input file name).

    -h
    --help
        Print this message na exit.

    -V
    --version
        Display version information na exit.
"""

agiza os
agiza sys
agiza ast
agiza getopt
agiza struct
agiza array
kutoka email.parser agiza HeaderParser

__version__ = "1.2"

MESSAGES = {}


eleza usage(code, msg=''):
    andika(__doc__, file=sys.stderr)
    ikiwa msg:
        andika(msg, file=sys.stderr)
    sys.exit(code)


eleza add(ctxt, id, str, fuzzy):
    "Add a non-fuzzy translation to the dictionary."
    global MESSAGES
    ikiwa sio fuzzy na str:
        ikiwa ctxt ni Tupu:
            MESSAGES[id] = str
        isipokua:
            MESSAGES[b"%b\x04%b" % (ctxt, id)] = str


eleza generate():
    "Return the generated output."
    global MESSAGES
    # the keys are sorted kwenye the .mo file
    keys = sorted(MESSAGES.keys())
    offsets = []
    ids = strs = b''
    kila id kwenye keys:
        # For each string, we need size na file offset.  Each string ni NUL
        # terminated; the NUL does sio count into the size.
        offsets.append((len(ids), len(id), len(strs), len(MESSAGES[id])))
        ids += id + b'\0'
        strs += MESSAGES[id] + b'\0'
    output = ''
    # The header ni 7 32-bit unsigned integers.  We don't use hash tables, so
    # the keys start right after the index tables.
    # translated string.
    keystart = 7*4+16*len(keys)
    # na the values start after the keys
    valuestart = keystart + len(ids)
    koffsets = []
    voffsets = []
    # The string table first has the list of keys, then the list of values.
    # Each entry has first the size of the string, then the file offset.
    kila o1, l1, o2, l2 kwenye offsets:
        koffsets += [l1, o1+keystart]
        voffsets += [l2, o2+valuestart]
    offsets = koffsets + voffsets
    output = struct.pack("Iiiiiii",
                         0x950412de,       # Magic
                         0,                 # Version
                         len(keys),         # # of entries
                         7*4,               # start of key index
                         7*4+len(keys)*8,   # start of value index
                         0, 0)              # size na offset of hash table
    output += array.array("i", offsets).tobytes()
    output += ids
    output += strs
    rudisha output


eleza make(filename, outfile):
    ID = 1
    STR = 2
    CTXT = 3

    # Compute .mo name kutoka .po name na arguments
    ikiwa filename.endswith('.po'):
        infile = filename
    isipokua:
        infile = filename + '.po'
    ikiwa outfile ni Tupu:
        outfile = os.path.splitext(infile)[0] + '.mo'

    jaribu:
        ukijumuisha open(infile, 'rb') kama f:
            lines = f.readlines()
    tatizo IOError kama msg:
        andika(msg, file=sys.stderr)
        sys.exit(1)

    section = msgctxt = Tupu
    fuzzy = 0

    # Start off assuming Latin-1, so everything decodes without failure,
    # until we know the exact encoding
    encoding = 'latin-1'

    # Parse the catalog
    lno = 0
    kila l kwenye lines:
        l = l.decode(encoding)
        lno += 1
        # If we get a comment line after a msgstr, this ni a new entry
        ikiwa l[0] == '#' na section == STR:
            add(msgctxt, msgid, msgstr, fuzzy)
            section = msgctxt = Tupu
            fuzzy = 0
        # Record a fuzzy mark
        ikiwa l[:2] == '#,' na 'fuzzy' kwenye l:
            fuzzy = 1
        # Skip comments
        ikiwa l[0] == '#':
            endelea
        # Now we are kwenye a msgid ama msgctxt section, output previous section
        ikiwa l.startswith('msgctxt'):
            ikiwa section == STR:
                add(msgctxt, msgid, msgstr, fuzzy)
            section = CTXT
            l = l[7:]
            msgctxt = b''
        lasivyo l.startswith('msgid') na sio l.startswith('msgid_plural'):
            ikiwa section == STR:
                add(msgctxt, msgid, msgstr, fuzzy)
                ikiwa sio msgid:
                    # See whether there ni an encoding declaration
                    p = HeaderParser()
                    charset = p.parsestr(msgstr.decode(encoding)).get_content_charset()
                    ikiwa charset:
                        encoding = charset
            section = ID
            l = l[5:]
            msgid = msgstr = b''
            is_plural = Uongo
        # This ni a message ukijumuisha plural forms
        lasivyo l.startswith('msgid_plural'):
            ikiwa section != ID:
                andika('msgid_plural sio preceded by msgid on %s:%d' % (infile, lno),
                      file=sys.stderr)
                sys.exit(1)
            l = l[12:]
            msgid += b'\0' # separator of singular na plural
            is_plural = Kweli
        # Now we are kwenye a msgstr section
        lasivyo l.startswith('msgstr'):
            section = STR
            ikiwa l.startswith('msgstr['):
                ikiwa sio is_plural:
                    andika('plural without msgid_plural on %s:%d' % (infile, lno),
                          file=sys.stderr)
                    sys.exit(1)
                l = l.split(']', 1)[1]
                ikiwa msgstr:
                    msgstr += b'\0' # Separator of the various plural forms
            isipokua:
                ikiwa is_plural:
                    andika('indexed msgstr required kila plural on  %s:%d' % (infile, lno),
                          file=sys.stderr)
                    sys.exit(1)
                l = l[6:]
        # Skip empty lines
        l = l.strip()
        ikiwa sio l:
            endelea
        l = ast.literal_eval(l)
        ikiwa section == CTXT:
            msgctxt += l.encode(encoding)
        lasivyo section == ID:
            msgid += l.encode(encoding)
        lasivyo section == STR:
            msgstr += l.encode(encoding)
        isipokua:
            andika('Syntax error on %s:%d' % (infile, lno), \
                  'before:', file=sys.stderr)
            andika(l, file=sys.stderr)
            sys.exit(1)
    # Add last entry
    ikiwa section == STR:
        add(msgctxt, msgid, msgstr, fuzzy)

    # Compute output
    output = generate()

    jaribu:
        ukijumuisha open(outfile,"wb") kama f:
            f.write(output)
    tatizo IOError kama msg:
        andika(msg, file=sys.stderr)


eleza main():
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], 'hVo:',
                                   ['help', 'version', 'output-file='])
    tatizo getopt.error kama msg:
        usage(1, msg)

    outfile = Tupu
    # parse options
    kila opt, arg kwenye opts:
        ikiwa opt kwenye ('-h', '--help'):
            usage(0)
        lasivyo opt kwenye ('-V', '--version'):
            andika("msgfmt.py", __version__)
            sys.exit(0)
        lasivyo opt kwenye ('-o', '--output-file'):
            outfile = arg
    # do it
    ikiwa sio args:
        andika('No input file given', file=sys.stderr)
        andika("Try `msgfmt --help' kila more information.", file=sys.stderr)
        rudisha

    kila filename kwenye args:
        make(filename, outfile)


ikiwa __name__ == '__main__':
    main()
