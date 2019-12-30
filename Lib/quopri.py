#! /usr/bin/env python3

"""Conversions to/kutoka quoted-printable transport encoding as per RFC 1521."""

# (Dec 1991 version).

__all__ = ["encode", "decode", "encodestring", "decodestring"]

ESCAPE = b'='
MAXLINESIZE = 76
HEX = b'0123456789ABCDEF'
EMPTYSTRING = b''

jaribu:
    kutoka binascii agiza a2b_qp, b2a_qp
except ImportError:
    a2b_qp = Tupu
    b2a_qp = Tupu


eleza needsquoting(c, quotetabs, header):
    """Decide whether a particular byte ordinal needs to be quoted.

    The 'quotetabs' flag indicates whether embedded tabs na spaces should be
    quoted.  Note that line-ending tabs na spaces are always encoded, as per
    RFC 1521.
    """
    assert isinstance(c, bytes)
    ikiwa c kwenye b' \t':
        rudisha quotetabs
    # ikiwa header, we have to escape _ because _ ni used to escape space
    ikiwa c == b'_':
        rudisha header
    rudisha c == ESCAPE ama sio (b' ' <= c <= b'~')

eleza quote(c):
    """Quote a single character."""
    assert isinstance(c, bytes) na len(c)==1
    c = ord(c)
    rudisha ESCAPE + bytes((HEX[c//16], HEX[c%16]))



eleza encode(input, output, quotetabs, header=Uongo):
    """Read 'input', apply quoted-printable encoding, na write to 'output'.

    'input' na 'output' are binary file objects. The 'quotetabs' flag
    indicates whether embedded tabs na spaces should be quoted. Note that
    line-ending tabs na spaces are always encoded, as per RFC 1521.
    The 'header' flag indicates whether we are encoding spaces as _ as per RFC
    1522."""

    ikiwa b2a_qp ni sio Tupu:
        data = input.read()
        odata = b2a_qp(data, quotetabs=quotetabs, header=header)
        output.write(odata)
        return

    eleza write(s, output=output, lineEnd=b'\n'):
        # RFC 1521 requires that the line ending kwenye a space ama tab must have
        # that trailing character encoded.
        ikiwa s na s[-1:] kwenye b' \t':
            output.write(s[:-1] + quote(s[-1:]) + lineEnd)
        elikiwa s == b'.':
            output.write(quote(s) + lineEnd)
        isipokua:
            output.write(s + lineEnd)

    prevline = Tupu
    wakati 1:
        line = input.readline()
        ikiwa sio line:
            koma
        outline = []
        # Strip off any readline induced trailing newline
        stripped = b''
        ikiwa line[-1:] == b'\n':
            line = line[:-1]
            stripped = b'\n'
        # Calculate the un-length-limited encoded line
        kila c kwenye line:
            c = bytes((c,))
            ikiwa needsquoting(c, quotetabs, header):
                c = quote(c)
            ikiwa header na c == b' ':
                outline.append(b'_')
            isipokua:
                outline.append(c)
        # First, write out the previous line
        ikiwa prevline ni sio Tupu:
            write(prevline)
        # Now see ikiwa we need any soft line komas because of RFC-imposed
        # length limitations.  Then do the thisline->prevline dance.
        thisline = EMPTYSTRING.join(outline)
        wakati len(thisline) > MAXLINESIZE:
            # Don't forget to include the soft line koma `=' sign kwenye the
            # length calculation!
            write(thisline[:MAXLINESIZE-1], lineEnd=b'=\n')
            thisline = thisline[MAXLINESIZE-1:]
        # Write out the current line
        prevline = thisline
    # Write out the last line, without a trailing newline
    ikiwa prevline ni sio Tupu:
        write(prevline, lineEnd=stripped)

eleza encodestring(s, quotetabs=Uongo, header=Uongo):
    ikiwa b2a_qp ni sio Tupu:
        rudisha b2a_qp(s, quotetabs=quotetabs, header=header)
    kutoka io agiza BytesIO
    infp = BytesIO(s)
    outfp = BytesIO()
    encode(infp, outfp, quotetabs, header)
    rudisha outfp.getvalue()



eleza decode(input, output, header=Uongo):
    """Read 'input', apply quoted-printable decoding, na write to 'output'.
    'input' na 'output' are binary file objects.
    If 'header' ni true, decode underscore as space (per RFC 1522)."""

    ikiwa a2b_qp ni sio Tupu:
        data = input.read()
        odata = a2b_qp(data, header=header)
        output.write(odata)
        return

    new = b''
    wakati 1:
        line = input.readline()
        ikiwa sio line: koma
        i, n = 0, len(line)
        ikiwa n > 0 na line[n-1:n] == b'\n':
            partial = 0; n = n-1
            # Strip trailing whitespace
            wakati n > 0 na line[n-1:n] kwenye b" \t\r":
                n = n-1
        isipokua:
            partial = 1
        wakati i < n:
            c = line[i:i+1]
            ikiwa c == b'_' na header:
                new = new + b' '; i = i+1
            elikiwa c != ESCAPE:
                new = new + c; i = i+1
            elikiwa i+1 == n na sio partial:
                partial = 1; koma
            elikiwa i+1 < n na line[i+1:i+2] == ESCAPE:
                new = new + ESCAPE; i = i+2
            elikiwa i+2 < n na ishex(line[i+1:i+2]) na ishex(line[i+2:i+3]):
                new = new + bytes((unhex(line[i+1:i+3]),)); i = i+3
            isipokua: # Bad escape sequence -- leave it in
                new = new + c; i = i+1
        ikiwa sio partial:
            output.write(new + b'\n')
            new = b''
    ikiwa new:
        output.write(new)

eleza decodestring(s, header=Uongo):
    ikiwa a2b_qp ni sio Tupu:
        rudisha a2b_qp(s, header=header)
    kutoka io agiza BytesIO
    infp = BytesIO(s)
    outfp = BytesIO()
    decode(infp, outfp, header=header)
    rudisha outfp.getvalue()



# Other helper functions
eleza ishex(c):
    """Return true ikiwa the byte ordinal 'c' ni a hexadecimal digit kwenye ASCII."""
    assert isinstance(c, bytes)
    rudisha b'0' <= c <= b'9' ama b'a' <= c <= b'f' ama b'A' <= c <= b'F'

eleza unhex(s):
    """Get the integer value of a hexadecimal number."""
    bits = 0
    kila c kwenye s:
        c = bytes((c,))
        ikiwa b'0' <= c <= b'9':
            i = ord('0')
        elikiwa b'a' <= c <= b'f':
            i = ord('a')-10
        elikiwa b'A' <= c <= b'F':
            i = ord(b'A')-10
        isipokua:
            assert Uongo, "non-hex digit "+repr(c)
        bits = bits*16 + (ord(c) - i)
    rudisha bits



eleza main():
    agiza sys
    agiza getopt
    jaribu:
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
    kila o, a kwenye opts:
        ikiwa o == '-t': tabs = 1
        ikiwa o == '-d': deco = 1
    ikiwa tabs na deco:
        sys.stdout = sys.stderr
        andika("-t na -d are mutually exclusive")
        sys.exit(2)
    ikiwa sio args: args = ['-']
    sts = 0
    kila file kwenye args:
        ikiwa file == '-':
            fp = sys.stdin.buffer
        isipokua:
            jaribu:
                fp = open(file, "rb")
            except OSError as msg:
                sys.stderr.write("%s: can't open (%s)\n" % (file, msg))
                sts = 1
                endelea
        jaribu:
            ikiwa deco:
                decode(fp, sys.stdout.buffer)
            isipokua:
                encode(fp, sys.stdout.buffer, tabs)
        mwishowe:
            ikiwa file != '-':
                fp.close()
    ikiwa sts:
        sys.exit(sts)



ikiwa __name__ == '__main__':
    main()
