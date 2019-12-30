#!/usr/bin/env python3

""" Compare the output of two codecs.

(c) Copyright 2005, Marc-Andre Lemburg (mal@lemburg.com).

    Licensed to PSF under a Contributor Agreement.

"""
agiza sys

eleza compare_codecs(encoding1, encoding2):

    andika('Comparing encoding/decoding of   %r na   %r' % (encoding1, encoding2))
    mismatch = 0
    # Check encoding
    kila i kwenye range(sys.maxunicode+1):
        u = chr(i)
        jaribu:
            c1 = u.encode(encoding1)
        tatizo UnicodeError kama reason:
            c1 = '<undefined>'
        jaribu:
            c2 = u.encode(encoding2)
        tatizo UnicodeError kama reason:
            c2 = '<undefined>'
        ikiwa c1 != c2:
            andika(' * encoding mismatch kila 0x%04X: %-14r != %r' % \
                  (i, c1, c2))
            mismatch += 1
    # Check decoding
    kila i kwenye range(256):
        c = bytes([i])
        jaribu:
            u1 = c.decode(encoding1)
        tatizo UnicodeError:
            u1 = '<undefined>'
        jaribu:
            u2 = c.decode(encoding2)
        tatizo UnicodeError:
            u2 = '<undefined>'
        ikiwa u1 != u2:
            andika(' * decoding mismatch kila 0x%04X: %-14r != %r' % \
                  (i, u1, u2))
            mismatch += 1
    ikiwa mismatch:
        andika()
        andika('Found %i mismatches' % mismatch)
    isipokua:
        andika('-> Codecs are identical.')

ikiwa __name__ == '__main__':
    compare_codecs(sys.argv[1], sys.argv[2])
