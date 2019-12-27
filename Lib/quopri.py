#! /usr/bin/env python3

"""Conversions to/kutoka quoted-printable transport encoding as per RFC 1521."""

# (Dec 1991 version).

__all__ = ["encode", "decode", "encodestring", "decodestring"]

ESCAPE = b'='
MAXLINESIZE = 76
HEX = b'0123456789ABCDEF'
EMPTYSTRING = b''

try:
    kutoka binascii agiza a2b_qp, b2a_qp
except ImportError:
    a2b_qp = None
    b2a_qp = None


eleza needsquoting(c, quotetabs, header):
    """Decide whether a particular byte ordinal needs to be quoted.

    The 'quotetabs' flag indicates whether embedded tabs and spaces should be
    quoted.  Note that line-ending tabs and spaces are always encoded, as per
    RFC 1521.
    """
    assert isinstance(c, bytes)
    ikiwa c in b' \t':
        rudisha quotetabs
    # ikiwa header, we have to escape _ because _ is used to escape space
    ikiwa c == b'_':
        rudisha header
    rudisha c == ESCAPE or not (b' ' <= c <= b'~')

eleza quote(c):
    """Quote a single character."""
    assert isinstance(c, bytes) and len(c)==1
    c = ord(c)
    rudisha ESCAPE + bytes((HEX[c//16], HEX[c%16]))



eleza encode(input, output, quotetabs, header=False):
    """Read 'input', apply quoted-printable encoding, and write to 'output'.

    'input' and 'output' are binary file objects. The 'quotetabs' flag
    indicates whether embedded tabs and spaces should be quoted. Note that
    line-ending tabs and spaces are always encoded, as per RFC 1521.
    The 'header' flag indicates whether we are encoding spaces as _ as per RFC
    1522."""

    ikiwa b2a_qp is not None:
        data = input.read()
        odata = b2a_qp(data, quotetabs=quotetabs, header=header)
        output.write(odata)
        return

    eleza write(s, output=output, lineEnd=b'\n'):
        # RFC 1521 requires that the line ending in a space or tab must have
        # that trailing character encoded.
        ikiwa s and s[-1:] in b' \t':
            output.write(s[:-1] + quote(s[-1:]) + lineEnd)
        elikiwa s == b'.':
            output.write(quote(s) + lineEnd)
        else:
            output.write(s + lineEnd)

    prevline = None
    while 1:
        line = input.readline()
        ikiwa not line:
            break
        outline = []
        # Strip off any readline induced trailing newline
        stripped = b''
        ikiwa line[-1:] == b'\n':
            line = line[:-1]
            stripped = b'\n'
        # Calculate the un-length-limited encoded line
        for c in line:
            c = bytes((c,))
            ikiwa needsquoting(c, quotetabs, header):
                c = quote(c)
            ikiwa header and c == b' ':
                outline.append(b'_')
            else:
                outline.append(c)
        # First, write out the previous line
        ikiwa prevline is not None:
            write(prevline)
        # Now see ikiwa we need any soft line breaks because of RFC-imposed
        # length limitations.  Then do the thisline->prevline dance.
        thisline = EMPTYSTRING.join(outline)
        while len(thisline) > MAXLINESIZE:
            # Don't forget to include the soft line break `=' sign in the
            # length calculation!
            write(thisline[:MAXLINESIZE-1], lineEnd=b'=\n')
            thisline = thisline[MAXLINESIZE-1:]
        # Write out the current line
        prevline = thisline
    # Write out the last line, without a trailing newline
    ikiwa prevline is not None:
        write(prevline, lineEnd=stripped)

eleza encodestring(s, quotetabs=False, header=False):
    ikiwa b2a_qp is not None:
        rudisha b2a_qp(s, quotetabs=quotetabs, header=header)
    kutoka io agiza BytesIO
    infp = BytesIO(s)
    outfp = BytesIO()
    encode(infp, outfp, quotetabs, header)
    rudisha outfp.getvalue()



eleza decode(input, output, header=False):
    """Read 'input', apply quoted-printable decoding, and write to 'output'.
    'input' and 'output' are binary file objects.
    If 'header' is true, decode underscore as space (per RFC 1522)."""

    ikiwa a2b_qp is not None:
        data = input.read()
        odata = a2b_qp(data, header=header)
        output.write(odata)
        return

    new = b''
    while 1:
        line = input.readline()
        ikiwa not line: break
        i, n = 0, len(line)
        ikiwa n > 0 and line[n-1:n] == b'\n':
            partial = 0; n = n-1
            # Strip trailing whitespace
            while n > 0 and line[n-1:n] in b" \t\r":
                n = n-1
        else:
            partial = 1
        while i < n:
            c = line[i:i+1]
            ikiwa c == b'_' and header:
                new = new + b' '; i = i+1
            elikiwa c != ESCAPE:
                new = new + c; i = i+1
            elikiwa i+1 == n and not partial:
                partial = 1; break
            elikiwa i+1 < n and line[i+1:i+2] == ESCAPE:
                new = new + ESCAPE; i = i+2
            elikiwa i+2 < n and ishex(line[i+1:i+2]) and ishex(line[i+2:i+3]):
                new = new + bytes((unhex(line[i+1:i+3]),)); i = i+3
            else: # Bad escape sequence -- leave it in
                new = new + c; i = i+1
        ikiwa not partial:
            output.write(new + b'\n')
            new = b''
    ikiwa new:
        output.write(new)

eleza decodestring(s, header=False):
    ikiwa a2b_qp is not None:
        rudisha a2b_qp(s, header=header)
    kutoka io agiza BytesIO
    infp = BytesIO(s)
    outfp = BytesIO()
    decode(infp, outfp, header=header)
    rudisha outfp.getvalue()



# Other helper functions
eleza ishex(c):
    """Return true ikiwa the byte ordinal 'c' is a hexadecimal digit in ASCII."""
    assert isinstance(c, bytes)
    rudisha b'0' <= c <= b'9' or b'a' <= c <= b'f' or b'A' <= c <= b'F'

eleza unhex(s):
    """Get the integer value of a hexadecimal number."""
    bits = 0
    for c in s:
        c = bytes((c,))
        ikiwa b'0' <= c <= b'9':
            i = ord('0')
        elikiwa b'a' <= c <= b'f':
            i = ord('a')-10
        elikiwa b'A' <= c <= b'F':
            i = ord(b'A')-10
        else:
            assert False, "non-hex digit "+repr(c)
        bits = bits*16 + (ord(c) - i)
    rudisha bits



eleza main():
    agiza sys
    agiza getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'td')
    except getopt.error as msg:
        sys.stdout = sys.stderr
        andika(msg)
        andika("usage: quopri [-t | -d] [file] ...")
        andika("-t: quote tabs")
        andika("-d: decode; default encode")
        sys.exit(2)
    deco = 0
    tabs = 0
    for o, a in opts:
        ikiwa o == '-t': tabs = 1
        ikiwa o == '-d': deco = 1
    ikiwa tabs and deco:
        sys.stdout = sys.stderr
        andika("-t and -d are mutually exclusive")
        sys.exit(2)
    ikiwa not args: args = ['-']
    sts = 0
    for file in args:
        ikiwa file == '-':
            fp = sys.stdin.buffer
        else:
            try:
                fp = open(file, "rb")
            except OSError as msg:
                sys.stderr.write("%s: can't open (%s)\n" % (file, msg))
                sts = 1
                continue
        try:
            ikiwa deco:
                decode(fp, sys.stdout.buffer)
            else:
                encode(fp, sys.stdout.buffer, tabs)
        finally:
            ikiwa file != '-':
                fp.close()
    ikiwa sts:
        sys.exit(sts)



ikiwa __name__ == '__main__':
    main()
