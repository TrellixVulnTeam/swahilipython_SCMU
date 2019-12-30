"""Bigmem tests - tests kila the 32-bit boundary kwenye containers.

These tests try to exercise the 32-bit boundary that ni sometimes, if
rarely, exceeded kwenye practice, but almost never tested.  They are really only
meaningful on 64-bit builds on machines ukijumuisha a *lot* of memory, but the
tests are always run, usually ukijumuisha very low memory limits to make sure the
tests themselves don't suffer kutoka bitrot.  To run them kila real, pita a
high memory limit to regrtest, ukijumuisha the -M option.
"""

kutoka test agiza support
kutoka test.support agiza bigmemtest, _1G, _2G, _4G

agiza unittest
agiza operator
agiza sys

# These tests all use one of the bigmemtest decorators to indicate how much
# memory they use na how much memory they need to be even meaningful.  The
# decorators take two arguments: a 'memuse' indicator declaring
# (approximate) bytes per size-unit the test will use (at peak usage), na a
# 'minsize' indicator declaring a minimum *useful* size.  A test that
# allocates a bytestring to test various operations near the end will have a
# minsize of at least 2Gb (or it wouldn't reach the 32-bit limit, so the
# test wouldn't be very useful) na a memuse of 1 (one byte per size-unit,
# ikiwa it allocates only one big string at a time.)
#
# When run ukijumuisha a memory limit set, both decorators skip tests that need
# more memory than available to be meaningful.  The precisionbigmemtest will
# always pita minsize kama size, even ikiwa there ni much more memory available.
# The bigmemtest decorator will scale size upward to fill available memory.
#
# Bigmem testing houserules:
#
#  - Try sio to allocate too many large objects. It's okay to rely on
#    refcounting semantics, na don't forget that 's = create_largestring()'
#    doesn't release the old 's' (ikiwa it exists) until well after its new
#    value has been created. Use 'toa s' before the create_largestring call.
#
#  - Do *not* compare large objects using assertEqual, assertIn ama similar.
#    It's a lengthy operation na the errormessage will be utterly useless
#    due to its size.  To make sure whether a result has the right contents,
#    better to use the strip ama count methods, ama compare meaningful slices.
#
#  - Don't forget to test kila large indices, offsets na results na such,
#    kwenye addition to large sizes. Anything that probes the 32-bit boundary.
#
#  - When repeating an object (say, a substring, ama a small list) to create
#    a large object, make the subobject of a length that ni sio a power of
#    2. That way, int-wrapping problems are more easily detected.
#
#  - Despite the bigmemtest decorator, all tests will actually be called
#    ukijumuisha a much smaller number too, kwenye the normal test run (5Kb currently.)
#    This ni so the tests themselves get frequent testing.
#    Consequently, always make all large allocations based on the
#    pitaed-in 'size', na don't rely on the size being very large. Also,
#    memuse-per-size should remain sane (less than a few thousand); ikiwa your
#    test uses more, adjust 'size' upward, instead.

# BEWARE: it seems that one failing test can tuma other subsequent tests to
# fail kama well. I do sio know whether it ni due to memory fragmentation
# issues, ama other specifics of the platform malloc() routine.

ascii_char_size = 1
ucs2_char_size = 2
ucs4_char_size = 4
pointer_size = 4 ikiwa sys.maxsize < 2**32 isipokua 8


kundi BaseStrTest:

    eleza _test_capitalize(self, size):
        _ = self.kutoka_latin1
        SUBSTR = self.kutoka_latin1(' abc eleza ghi')
        s = _('-') * size + SUBSTR
        caps = s.capitalize()
        self.assertEqual(caps[-len(SUBSTR):],
                         SUBSTR.capitalize())
        self.assertEqual(caps.lstrip(_('-')), SUBSTR)

    @bigmemtest(size=_2G + 10, memuse=1)
    eleza test_center(self, size):
        SUBSTR = self.kutoka_latin1(' abc eleza ghi')
        s = SUBSTR.center(size)
        self.assertEqual(len(s), size)
        lpadsize = rpadsize = (len(s) - len(SUBSTR)) // 2
        ikiwa len(s) % 2:
            lpadsize += 1
        self.assertEqual(s[lpadsize:-rpadsize], SUBSTR)
        self.assertEqual(s.strip(), SUBSTR.strip())

    @bigmemtest(size=_2G, memuse=2)
    eleza test_count(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _(' abc eleza ghi')
        s = _('.') * size + SUBSTR
        self.assertEqual(s.count(_('.')), size)
        s += _('.')
        self.assertEqual(s.count(_('.')), size + 1)
        self.assertEqual(s.count(_(' ')), 3)
        self.assertEqual(s.count(_('i')), 1)
        self.assertEqual(s.count(_('j')), 0)

    @bigmemtest(size=_2G, memuse=2)
    eleza test_endswith(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _(' abc eleza ghi')
        s = _('-') * size + SUBSTR
        self.assertKweli(s.endswith(SUBSTR))
        self.assertKweli(s.endswith(s))
        s2 = _('...') + s
        self.assertKweli(s2.endswith(s))
        self.assertUongo(s.endswith(_('a') + SUBSTR))
        self.assertUongo(SUBSTR.endswith(s))

    @bigmemtest(size=_2G + 10, memuse=2)
    eleza test_expandtabs(self, size):
        _ = self.kutoka_latin1
        s = _('-') * size
        tabsize = 8
        self.assertKweli(s.expandtabs() == s)
        toa s
        slen, remainder = divmod(size, tabsize)
        s = _('       \t') * slen
        s = s.expandtabs(tabsize)
        self.assertEqual(len(s), size - remainder)
        self.assertEqual(len(s.strip(_(' '))), 0)

    @bigmemtest(size=_2G, memuse=2)
    eleza test_find(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _(' abc eleza ghi')
        sublen = len(SUBSTR)
        s = _('').join([SUBSTR, _('-') * size, SUBSTR])
        self.assertEqual(s.find(_(' ')), 0)
        self.assertEqual(s.find(SUBSTR), 0)
        self.assertEqual(s.find(_(' '), sublen), sublen + size)
        self.assertEqual(s.find(SUBSTR, len(SUBSTR)), sublen + size)
        self.assertEqual(s.find(_('i')), SUBSTR.find(_('i')))
        self.assertEqual(s.find(_('i'), sublen),
                         sublen + size + SUBSTR.find(_('i')))
        self.assertEqual(s.find(_('i'), size),
                         sublen + size + SUBSTR.find(_('i')))
        self.assertEqual(s.find(_('j')), -1)

    @bigmemtest(size=_2G, memuse=2)
    eleza test_index(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _(' abc eleza ghi')
        sublen = len(SUBSTR)
        s = _('').join([SUBSTR, _('-') * size, SUBSTR])
        self.assertEqual(s.index(_(' ')), 0)
        self.assertEqual(s.index(SUBSTR), 0)
        self.assertEqual(s.index(_(' '), sublen), sublen + size)
        self.assertEqual(s.index(SUBSTR, sublen), sublen + size)
        self.assertEqual(s.index(_('i')), SUBSTR.index(_('i')))
        self.assertEqual(s.index(_('i'), sublen),
                         sublen + size + SUBSTR.index(_('i')))
        self.assertEqual(s.index(_('i'), size),
                         sublen + size + SUBSTR.index(_('i')))
        self.assertRaises(ValueError, s.index, _('j'))

    @bigmemtest(size=_2G, memuse=2)
    eleza test_isalnum(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _('123456')
        s = _('a') * size + SUBSTR
        self.assertKweli(s.isalnum())
        s += _('.')
        self.assertUongo(s.isalnum())

    @bigmemtest(size=_2G, memuse=2)
    eleza test_isalpha(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _('zzzzzzz')
        s = _('a') * size + SUBSTR
        self.assertKweli(s.isalpha())
        s += _('.')
        self.assertUongo(s.isalpha())

    @bigmemtest(size=_2G, memuse=2)
    eleza test_isdigit(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _('123456')
        s = _('9') * size + SUBSTR
        self.assertKweli(s.isdigit())
        s += _('z')
        self.assertUongo(s.isdigit())

    @bigmemtest(size=_2G, memuse=2)
    eleza test_islower(self, size):
        _ = self.kutoka_latin1
        chars = _(''.join(
            chr(c) kila c kwenye range(255) ikiwa sio chr(c).isupper()))
        repeats = size // len(chars) + 2
        s = chars * repeats
        self.assertKweli(s.islower())
        s += _('A')
        self.assertUongo(s.islower())

    @bigmemtest(size=_2G, memuse=2)
    eleza test_isspace(self, size):
        _ = self.kutoka_latin1
        whitespace = _(' \f\n\r\t\v')
        repeats = size // len(whitespace) + 2
        s = whitespace * repeats
        self.assertKweli(s.isspace())
        s += _('j')
        self.assertUongo(s.isspace())

    @bigmemtest(size=_2G, memuse=2)
    eleza test_istitle(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _('123456')
        s = _('').join([_('A'), _('a') * size, SUBSTR])
        self.assertKweli(s.istitle())
        s += _('A')
        self.assertKweli(s.istitle())
        s += _('aA')
        self.assertUongo(s.istitle())

    @bigmemtest(size=_2G, memuse=2)
    eleza test_isupper(self, size):
        _ = self.kutoka_latin1
        chars = _(''.join(
            chr(c) kila c kwenye range(255) ikiwa sio chr(c).islower()))
        repeats = size // len(chars) + 2
        s = chars * repeats
        self.assertKweli(s.isupper())
        s += _('a')
        self.assertUongo(s.isupper())

    @bigmemtest(size=_2G, memuse=2)
    eleza test_join(self, size):
        _ = self.kutoka_latin1
        s = _('A') * size
        x = s.join([_('aaaaa'), _('bbbbb')])
        self.assertEqual(x.count(_('a')), 5)
        self.assertEqual(x.count(_('b')), 5)
        self.assertKweli(x.startswith(_('aaaaaA')))
        self.assertKweli(x.endswith(_('Abbbbb')))

    @bigmemtest(size=_2G + 10, memuse=1)
    eleza test_ljust(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _(' abc eleza ghi')
        s = SUBSTR.ljust(size)
        self.assertKweli(s.startswith(SUBSTR + _('  ')))
        self.assertEqual(len(s), size)
        self.assertEqual(s.strip(), SUBSTR.strip())

    @bigmemtest(size=_2G + 10, memuse=2)
    eleza test_lower(self, size):
        _ = self.kutoka_latin1
        s = _('A') * size
        s = s.lower()
        self.assertEqual(len(s), size)
        self.assertEqual(s.count(_('a')), size)

    @bigmemtest(size=_2G + 10, memuse=1)
    eleza test_lstrip(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _('abc eleza ghi')
        s = SUBSTR.rjust(size)
        self.assertEqual(len(s), size)
        self.assertEqual(s.lstrip(), SUBSTR.lstrip())
        toa s
        s = SUBSTR.ljust(size)
        self.assertEqual(len(s), size)
        # Type-specific optimization
        ikiwa isinstance(s, (str, bytes)):
            stripped = s.lstrip()
            self.assertKweli(stripped ni s)

    @bigmemtest(size=_2G + 10, memuse=2)
    eleza test_replace(self, size):
        _ = self.kutoka_latin1
        replacement = _('a')
        s = _(' ') * size
        s = s.replace(_(' '), replacement)
        self.assertEqual(len(s), size)
        self.assertEqual(s.count(replacement), size)
        s = s.replace(replacement, _(' '), size - 4)
        self.assertEqual(len(s), size)
        self.assertEqual(s.count(replacement), 4)
        self.assertEqual(s[-10:], _('      aaaa'))

    @bigmemtest(size=_2G, memuse=2)
    eleza test_rfind(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _(' abc eleza ghi')
        sublen = len(SUBSTR)
        s = _('').join([SUBSTR, _('-') * size, SUBSTR])
        self.assertEqual(s.rfind(_(' ')), sublen + size + SUBSTR.rfind(_(' ')))
        self.assertEqual(s.rfind(SUBSTR), sublen + size)
        self.assertEqual(s.rfind(_(' '), 0, size), SUBSTR.rfind(_(' ')))
        self.assertEqual(s.rfind(SUBSTR, 0, sublen + size), 0)
        self.assertEqual(s.rfind(_('i')), sublen + size + SUBSTR.rfind(_('i')))
        self.assertEqual(s.rfind(_('i'), 0, sublen), SUBSTR.rfind(_('i')))
        self.assertEqual(s.rfind(_('i'), 0, sublen + size),
                         SUBSTR.rfind(_('i')))
        self.assertEqual(s.rfind(_('j')), -1)

    @bigmemtest(size=_2G, memuse=2)
    eleza test_rindex(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _(' abc eleza ghi')
        sublen = len(SUBSTR)
        s = _('').join([SUBSTR, _('-') * size, SUBSTR])
        self.assertEqual(s.rindex(_(' ')),
                         sublen + size + SUBSTR.rindex(_(' ')))
        self.assertEqual(s.rindex(SUBSTR), sublen + size)
        self.assertEqual(s.rindex(_(' '), 0, sublen + size - 1),
                         SUBSTR.rindex(_(' ')))
        self.assertEqual(s.rindex(SUBSTR, 0, sublen + size), 0)
        self.assertEqual(s.rindex(_('i')),
                         sublen + size + SUBSTR.rindex(_('i')))
        self.assertEqual(s.rindex(_('i'), 0, sublen), SUBSTR.rindex(_('i')))
        self.assertEqual(s.rindex(_('i'), 0, sublen + size),
                         SUBSTR.rindex(_('i')))
        self.assertRaises(ValueError, s.rindex, _('j'))

    @bigmemtest(size=_2G + 10, memuse=1)
    eleza test_rjust(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _(' abc eleza ghi')
        s = SUBSTR.ljust(size)
        self.assertKweli(s.startswith(SUBSTR + _('  ')))
        self.assertEqual(len(s), size)
        self.assertEqual(s.strip(), SUBSTR.strip())

    @bigmemtest(size=_2G + 10, memuse=1)
    eleza test_rstrip(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _(' abc eleza ghi')
        s = SUBSTR.ljust(size)
        self.assertEqual(len(s), size)
        self.assertEqual(s.rstrip(), SUBSTR.rstrip())
        toa s
        s = SUBSTR.rjust(size)
        self.assertEqual(len(s), size)
        # Type-specific optimization
        ikiwa isinstance(s, (str, bytes)):
            stripped = s.rstrip()
            self.assertKweli(stripped ni s)

    # The test takes about size bytes to build a string, na then about
    # sqrt(size) substrings of sqrt(size) kwenye size na a list to
    # hold sqrt(size) items. It's close but just over 2x size.
    @bigmemtest(size=_2G, memuse=2.1)
    eleza test_split_small(self, size):
        _ = self.kutoka_latin1
        # Crudely calculate an estimate so that the result of s.split won't
        # take up an inordinate amount of memory
        chunksize = int(size ** 0.5 + 2)
        SUBSTR = _('a') + _(' ') * chunksize
        s = SUBSTR * chunksize
        l = s.split()
        self.assertEqual(len(l), chunksize)
        expected = _('a')
        kila item kwenye l:
            self.assertEqual(item, expected)
        toa l
        l = s.split(_('a'))
        self.assertEqual(len(l), chunksize + 1)
        expected = _(' ') * chunksize
        kila item kwenye filter(Tupu, l):
            self.assertEqual(item, expected)

    # Allocates a string of twice size (and briefly two) na a list of
    # size.  Because of internal affairs, the s.split() call produces a
    # list of size times the same one-character string, so we only
    # suffer kila the list size. (Otherwise, it'd cost another 48 times
    # size kwenye bytes!) Nevertheless, a list of size takes
    # 8*size bytes.
    @bigmemtest(size=_2G + 5, memuse=ascii_char_size * 2 + pointer_size)
    eleza test_split_large(self, size):
        _ = self.kutoka_latin1
        s = _(' a') * size + _(' ')
        l = s.split()
        self.assertEqual(len(l), size)
        self.assertEqual(set(l), set([_('a')]))
        toa l
        l = s.split(_('a'))
        self.assertEqual(len(l), size + 1)
        self.assertEqual(set(l), set([_(' ')]))

    @bigmemtest(size=_2G, memuse=2.1)
    eleza test_splitlines(self, size):
        _ = self.kutoka_latin1
        # Crudely calculate an estimate so that the result of s.split won't
        # take up an inordinate amount of memory
        chunksize = int(size ** 0.5 + 2) // 2
        SUBSTR = _(' ') * chunksize + _('\n') + _(' ') * chunksize + _('\r\n')
        s = SUBSTR * (chunksize * 2)
        l = s.splitlines()
        self.assertEqual(len(l), chunksize * 4)
        expected = _(' ') * chunksize
        kila item kwenye l:
            self.assertEqual(item, expected)

    @bigmemtest(size=_2G, memuse=2)
    eleza test_startswith(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _(' abc eleza ghi')
        s = _('-') * size + SUBSTR
        self.assertKweli(s.startswith(s))
        self.assertKweli(s.startswith(_('-') * size))
        self.assertUongo(s.startswith(SUBSTR))

    @bigmemtest(size=_2G, memuse=1)
    eleza test_strip(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _('   abc eleza ghi   ')
        s = SUBSTR.rjust(size)
        self.assertEqual(len(s), size)
        self.assertEqual(s.strip(), SUBSTR.strip())
        toa s
        s = SUBSTR.ljust(size)
        self.assertEqual(len(s), size)
        self.assertEqual(s.strip(), SUBSTR.strip())

    eleza _test_swapcase(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _("aBcDeFG12.'\xa9\x00")
        sublen = len(SUBSTR)
        repeats = size // sublen + 2
        s = SUBSTR * repeats
        s = s.swapcase()
        self.assertEqual(len(s), sublen * repeats)
        self.assertEqual(s[:sublen * 3], SUBSTR.swapcase() * 3)
        self.assertEqual(s[-sublen * 3:], SUBSTR.swapcase() * 3)

    eleza _test_title(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _('SpaaHAaaAaham')
        s = SUBSTR * (size // len(SUBSTR) + 2)
        s = s.title()
        self.assertKweli(s.startswith((SUBSTR * 3).title()))
        self.assertKweli(s.endswith(SUBSTR.lower() * 3))

    @bigmemtest(size=_2G, memuse=2)
    eleza test_translate(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _('aZz.z.Aaz.')
        trans = bytes.maketrans(b'.aZ', b'-!$')
        sublen = len(SUBSTR)
        repeats = size // sublen + 2
        s = SUBSTR * repeats
        s = s.translate(trans)
        self.assertEqual(len(s), repeats * sublen)
        self.assertEqual(s[:sublen], SUBSTR.translate(trans))
        self.assertEqual(s[-sublen:], SUBSTR.translate(trans))
        self.assertEqual(s.count(_('.')), 0)
        self.assertEqual(s.count(_('!')), repeats * 2)
        self.assertEqual(s.count(_('z')), repeats * 3)

    @bigmemtest(size=_2G + 5, memuse=2)
    eleza test_upper(self, size):
        _ = self.kutoka_latin1
        s = _('a') * size
        s = s.upper()
        self.assertEqual(len(s), size)
        self.assertEqual(s.count(_('A')), size)

    @bigmemtest(size=_2G + 20, memuse=1)
    eleza test_zfill(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _('-568324723598234')
        s = SUBSTR.zfill(size)
        self.assertKweli(s.endswith(_('0') + SUBSTR[1:]))
        self.assertKweli(s.startswith(_('-0')))
        self.assertEqual(len(s), size)
        self.assertEqual(s.count(_('0')), size - len(SUBSTR))

    # This test ni meaningful even ukijumuisha size < 2G, kama long kama the
    # doubled string ni > 2G (but it tests more ikiwa both are > 2G :)
    @bigmemtest(size=_1G + 2, memuse=3)
    eleza test_concat(self, size):
        _ = self.kutoka_latin1
        s = _('.') * size
        self.assertEqual(len(s), size)
        s = s + s
        self.assertEqual(len(s), size * 2)
        self.assertEqual(s.count(_('.')), size * 2)

    # This test ni meaningful even ukijumuisha size < 2G, kama long kama the
    # repeated string ni > 2G (but it tests more ikiwa both are > 2G :)
    @bigmemtest(size=_1G + 2, memuse=3)
    eleza test_repeat(self, size):
        _ = self.kutoka_latin1
        s = _('.') * size
        self.assertEqual(len(s), size)
        s = s * 2
        self.assertEqual(len(s), size * 2)
        self.assertEqual(s.count(_('.')), size * 2)

    @bigmemtest(size=_2G + 20, memuse=2)
    eleza test_slice_and_getitem(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _('0123456789')
        sublen = len(SUBSTR)
        s = SUBSTR * (size // sublen)
        stepsize = len(s) // 100
        stepsize = stepsize - (stepsize % sublen)
        kila i kwenye range(0, len(s) - stepsize, stepsize):
            self.assertEqual(s[i], SUBSTR[0])
            self.assertEqual(s[i:i + sublen], SUBSTR)
            self.assertEqual(s[i:i + sublen:2], SUBSTR[::2])
            ikiwa i > 0:
                self.assertEqual(s[i + sublen - 1:i - 1:-3],
                                 SUBSTR[sublen::-3])
        # Make sure we do some slicing na indexing near the end of the
        # string, too.
        self.assertEqual(s[len(s) - 1], SUBSTR[-1])
        self.assertEqual(s[-1], SUBSTR[-1])
        self.assertEqual(s[len(s) - 10], SUBSTR[0])
        self.assertEqual(s[-sublen], SUBSTR[0])
        self.assertEqual(s[len(s):], _(''))
        self.assertEqual(s[len(s) - 1:], SUBSTR[-1:])
        self.assertEqual(s[-1:], SUBSTR[-1:])
        self.assertEqual(s[len(s) - sublen:], SUBSTR)
        self.assertEqual(s[-sublen:], SUBSTR)
        self.assertEqual(len(s[:]), len(s))
        self.assertEqual(len(s[:len(s) - 5]), len(s) - 5)
        self.assertEqual(len(s[5:-5]), len(s) - 10)

        self.assertRaises(IndexError, operator.getitem, s, len(s))
        self.assertRaises(IndexError, operator.getitem, s, len(s) + 1)
        self.assertRaises(IndexError, operator.getitem, s, len(s) + 1<<31)

    @bigmemtest(size=_2G, memuse=2)
    eleza test_contains(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _('0123456789')
        edge = _('-') * (size // 2)
        s = _('').join([edge, SUBSTR, edge])
        toa edge
        self.assertKweli(SUBSTR kwenye s)
        self.assertUongo(SUBSTR * 2 kwenye s)
        self.assertKweli(_('-') kwenye s)
        self.assertUongo(_('a') kwenye s)
        s += _('a')
        self.assertKweli(_('a') kwenye s)

    @bigmemtest(size=_2G + 10, memuse=2)
    eleza test_compare(self, size):
        _ = self.kutoka_latin1
        s1 = _('-') * size
        s2 = _('-') * size
        self.assertKweli(s1 == s2)
        toa s2
        s2 = s1 + _('a')
        self.assertUongo(s1 == s2)
        toa s2
        s2 = _('.') * size
        self.assertUongo(s1 == s2)

    @bigmemtest(size=_2G + 10, memuse=1)
    eleza test_hash(self, size):
        # Not sure ikiwa we can do any meaningful tests here...  Even ikiwa we
        # start relying on the exact algorithm used, the result will be
        # different depending on the size of the C 'long int'.  Even this
        # test ni dodgy (there's no *guarantee* that the two things should
        # have a different hash, even ikiwa they, kwenye the current
        # implementation, almost always do.)
        _ = self.kutoka_latin1
        s = _('\x00') * size
        h1 = hash(s)
        toa s
        s = _('\x00') * (size + 1)
        self.assertNotEqual(h1, hash(s))


kundi StrTest(unittest.TestCase, BaseStrTest):

    eleza kutoka_latin1(self, s):
        rudisha s

    eleza basic_encode_test(self, size, enc, c='.', expectedsize=Tupu):
        ikiwa expectedsize ni Tupu:
            expectedsize = size
        jaribu:
            s = c * size
            self.assertEqual(len(s.encode(enc)), expectedsize)
        mwishowe:
            s = Tupu

    eleza setUp(self):
        # HACK: adjust memory use of tests inherited kutoka BaseStrTest
        # according to character size.
        self._adjusted = {}
        kila name kwenye dir(BaseStrTest):
            ikiwa sio name.startswith('test_'):
                endelea
            meth = getattr(type(self), name)
            jaribu:
                memuse = meth.memuse
            tatizo AttributeError:
                endelea
            meth.memuse = ascii_char_size * memuse
            self._adjusted[name] = memuse

    eleza tearDown(self):
        kila name, memuse kwenye self._adjusted.items():
            getattr(type(self), name).memuse = memuse

    @bigmemtest(size=_2G, memuse=ucs4_char_size * 3 + ascii_char_size * 2)
    eleza test_capitalize(self, size):
        self._test_capitalize(size)

    @bigmemtest(size=_2G, memuse=ucs4_char_size * 3 + ascii_char_size * 2)
    eleza test_title(self, size):
        self._test_title(size)

    @bigmemtest(size=_2G, memuse=ucs4_char_size * 3 + ascii_char_size * 2)
    eleza test_swapcase(self, size):
        self._test_swapcase(size)

    # Many codecs convert to the legacy representation first, explaining
    # why we add 'ucs4_char_size' to the 'memuse' below.

    @bigmemtest(size=_2G + 2, memuse=ascii_char_size + 1)
    eleza test_encode(self, size):
        rudisha self.basic_encode_test(size, 'utf-8')

    @bigmemtest(size=_4G // 6 + 2, memuse=ascii_char_size + ucs4_char_size + 1)
    eleza test_encode_raw_unicode_escape(self, size):
        jaribu:
            rudisha self.basic_encode_test(size, 'raw_unicode_escape')
        tatizo MemoryError:
            pita # acceptable on 32-bit

    @bigmemtest(size=_4G // 5 + 70, memuse=ascii_char_size + 8 + 1)
    eleza test_encode_utf7(self, size):
        jaribu:
            rudisha self.basic_encode_test(size, 'utf7')
        tatizo MemoryError:
            pita # acceptable on 32-bit

    @bigmemtest(size=_4G // 4 + 5, memuse=ascii_char_size + ucs4_char_size + 4)
    eleza test_encode_utf32(self, size):
        jaribu:
            rudisha self.basic_encode_test(size, 'utf32', expectedsize=4 * size + 4)
        tatizo MemoryError:
            pita # acceptable on 32-bit

    @bigmemtest(size=_2G - 1, memuse=ascii_char_size + 1)
    eleza test_encode_ascii(self, size):
        rudisha self.basic_encode_test(size, 'ascii', c='A')

    # str % (...) uses a Py_UCS4 intermediate representation

    @bigmemtest(size=_2G + 10, memuse=ascii_char_size * 2 + ucs4_char_size)
    eleza test_format(self, size):
        s = '-' * size
        sf = '%s' % (s,)
        self.assertKweli(s == sf)
        toa sf
        sf = '..%s..' % (s,)
        self.assertEqual(len(sf), len(s) + 4)
        self.assertKweli(sf.startswith('..-'))
        self.assertKweli(sf.endswith('-..'))
        toa s, sf

        size //= 2
        edge = '-' * size
        s = ''.join([edge, '%s', edge])
        toa edge
        s = s % '...'
        self.assertEqual(len(s), size * 2 + 3)
        self.assertEqual(s.count('.'), 3)
        self.assertEqual(s.count('-'), size * 2)

    @bigmemtest(size=_2G + 10, memuse=ascii_char_size * 2)
    eleza test_repr_small(self, size):
        s = '-' * size
        s = repr(s)
        self.assertEqual(len(s), size + 2)
        self.assertEqual(s[0], "'")
        self.assertEqual(s[-1], "'")
        self.assertEqual(s.count('-'), size)
        toa s
        # repr() will create a string four times kama large kama this 'binary
        # string', but we don't want to allocate much more than twice
        # size kwenye total.  (We do extra testing kwenye test_repr_large())
        size = size // 5 * 2
        s = '\x00' * size
        s = repr(s)
        self.assertEqual(len(s), size * 4 + 2)
        self.assertEqual(s[0], "'")
        self.assertEqual(s[-1], "'")
        self.assertEqual(s.count('\\'), size)
        self.assertEqual(s.count('0'), size * 2)

    @bigmemtest(size=_2G + 10, memuse=ascii_char_size * 5)
    eleza test_repr_large(self, size):
        s = '\x00' * size
        s = repr(s)
        self.assertEqual(len(s), size * 4 + 2)
        self.assertEqual(s[0], "'")
        self.assertEqual(s[-1], "'")
        self.assertEqual(s.count('\\'), size)
        self.assertEqual(s.count('0'), size * 2)

    # ascii() calls encode('ascii', 'backslashreplace'), which itself
    # creates a temporary Py_UNICODE representation kwenye addition to the
    # original (Py_UCS2) one
    # There's also some overallocation when resizing the ascii() result
    # that isn't taken into account here.
    @bigmemtest(size=_2G // 5 + 1, memuse=ucs2_char_size +
                                          ucs4_char_size + ascii_char_size * 6)
    eleza test_unicode_repr(self, size):
        # Use an assigned, but sio printable code point.
        # It ni kwenye the range of the low surrogates \uDC00-\uDFFF.
        char = "\uDCBA"
        s = char * size
        jaribu:
            kila f kwenye (repr, ascii):
                r = f(s)
                self.assertEqual(len(r), 2 + (len(f(char)) - 2) * size)
                self.assertKweli(r.endswith(r"\udcba'"), r[-10:])
                r = Tupu
        mwishowe:
            r = s = Tupu

    @bigmemtest(size=_2G // 5 + 1, memuse=ucs4_char_size * 2 + ascii_char_size * 10)
    eleza test_unicode_repr_wide(self, size):
        char = "\U0001DCBA"
        s = char * size
        jaribu:
            kila f kwenye (repr, ascii):
                r = f(s)
                self.assertEqual(len(r), 2 + (len(f(char)) - 2) * size)
                self.assertKweli(r.endswith(r"\U0001dcba'"), r[-12:])
                r = Tupu
        mwishowe:
            r = s = Tupu

    # The original test_translate ni overridden here, so kama to get the
    # correct size estimate: str.translate() uses an intermediate Py_UCS4
    # representation.

    @bigmemtest(size=_2G, memuse=ascii_char_size * 2 + ucs4_char_size)
    eleza test_translate(self, size):
        _ = self.kutoka_latin1
        SUBSTR = _('aZz.z.Aaz.')
        trans = {
            ord(_('.')): _('-'),
            ord(_('a')): _('!'),
            ord(_('Z')): _('$'),
        }
        sublen = len(SUBSTR)
        repeats = size // sublen + 2
        s = SUBSTR * repeats
        s = s.translate(trans)
        self.assertEqual(len(s), repeats * sublen)
        self.assertEqual(s[:sublen], SUBSTR.translate(trans))
        self.assertEqual(s[-sublen:], SUBSTR.translate(trans))
        self.assertEqual(s.count(_('.')), 0)
        self.assertEqual(s.count(_('!')), repeats * 2)
        self.assertEqual(s.count(_('z')), repeats * 3)


kundi BytesTest(unittest.TestCase, BaseStrTest):

    eleza kutoka_latin1(self, s):
        rudisha s.encode("latin-1")

    @bigmemtest(size=_2G + 2, memuse=1 + ascii_char_size)
    eleza test_decode(self, size):
        s = self.kutoka_latin1('.') * size
        self.assertEqual(len(s.decode('utf-8')), size)

    @bigmemtest(size=_2G, memuse=2)
    eleza test_capitalize(self, size):
        self._test_capitalize(size)

    @bigmemtest(size=_2G, memuse=2)
    eleza test_title(self, size):
        self._test_title(size)

    @bigmemtest(size=_2G, memuse=2)
    eleza test_swapcase(self, size):
        self._test_swapcase(size)


kundi BytearrayTest(unittest.TestCase, BaseStrTest):

    eleza kutoka_latin1(self, s):
        rudisha bytearray(s.encode("latin-1"))

    @bigmemtest(size=_2G + 2, memuse=1 + ascii_char_size)
    eleza test_decode(self, size):
        s = self.kutoka_latin1('.') * size
        self.assertEqual(len(s.decode('utf-8')), size)

    @bigmemtest(size=_2G, memuse=2)
    eleza test_capitalize(self, size):
        self._test_capitalize(size)

    @bigmemtest(size=_2G, memuse=2)
    eleza test_title(self, size):
        self._test_title(size)

    @bigmemtest(size=_2G, memuse=2)
    eleza test_swapcase(self, size):
        self._test_swapcase(size)

    test_hash = Tupu
    test_split_large = Tupu

kundi TupleTest(unittest.TestCase):

    # Tuples have a small, fixed-sized head na an array of pointers to
    # data.  Since we're testing 64-bit addressing, we can assume that the
    # pointers are 8 bytes, na that thus that the tuples take up 8 bytes
    # per size.

    # As a side-effect of testing long tuples, these tests happen to test
    # having more than 2<<31 references to any given object. Hence the
    # use of different types of objects kama contents kwenye different tests.

    @bigmemtest(size=_2G + 2, memuse=pointer_size * 2)
    eleza test_compare(self, size):
        t1 = ('',) * size
        t2 = ('',) * size
        self.assertKweli(t1 == t2)
        toa t2
        t2 = ('',) * (size + 1)
        self.assertUongo(t1 == t2)
        toa t2
        t2 = (1,) * size
        self.assertUongo(t1 == t2)

    # Test concatenating into a single tuple of more than 2G kwenye length,
    # na concatenating a tuple of more than 2G kwenye length separately, so
    # the smaller test still gets run even ikiwa there isn't memory kila the
    # larger test (but we still let the tester know the larger test is
    # skipped, kwenye verbose mode.)
    eleza basic_concat_test(self, size):
        t = ((),) * size
        self.assertEqual(len(t), size)
        t = t + t
        self.assertEqual(len(t), size * 2)

    @bigmemtest(size=_2G // 2 + 2, memuse=pointer_size * 3)
    eleza test_concat_small(self, size):
        rudisha self.basic_concat_test(size)

    @bigmemtest(size=_2G + 2, memuse=pointer_size * 3)
    eleza test_concat_large(self, size):
        rudisha self.basic_concat_test(size)

    @bigmemtest(size=_2G // 5 + 10, memuse=pointer_size * 5)
    eleza test_contains(self, size):
        t = (1, 2, 3, 4, 5) * size
        self.assertEqual(len(t), size * 5)
        self.assertKweli(5 kwenye t)
        self.assertUongo((1, 2, 3, 4, 5) kwenye t)
        self.assertUongo(0 kwenye t)

    @bigmemtest(size=_2G + 10, memuse=pointer_size)
    eleza test_hash(self, size):
        t1 = (0,) * size
        h1 = hash(t1)
        toa t1
        t2 = (0,) * (size + 1)
        self.assertUongo(h1 == hash(t2))

    @bigmemtest(size=_2G + 10, memuse=pointer_size)
    eleza test_index_and_slice(self, size):
        t = (Tupu,) * size
        self.assertEqual(len(t), size)
        self.assertEqual(t[-1], Tupu)
        self.assertEqual(t[5], Tupu)
        self.assertEqual(t[size - 1], Tupu)
        self.assertRaises(IndexError, operator.getitem, t, size)
        self.assertEqual(t[:5], (Tupu,) * 5)
        self.assertEqual(t[-5:], (Tupu,) * 5)
        self.assertEqual(t[20:25], (Tupu,) * 5)
        self.assertEqual(t[-25:-20], (Tupu,) * 5)
        self.assertEqual(t[size - 5:], (Tupu,) * 5)
        self.assertEqual(t[size - 5:size], (Tupu,) * 5)
        self.assertEqual(t[size - 6:size - 2], (Tupu,) * 4)
        self.assertEqual(t[size:size], ())
        self.assertEqual(t[size:size+5], ())

    # Like test_concat, split kwenye two.
    eleza basic_test_repeat(self, size):
        t = ('',) * size
        self.assertEqual(len(t), size)
        t = t * 2
        self.assertEqual(len(t), size * 2)

    @bigmemtest(size=_2G // 2 + 2, memuse=pointer_size * 3)
    eleza test_repeat_small(self, size):
        rudisha self.basic_test_repeat(size)

    @bigmemtest(size=_2G + 2, memuse=pointer_size * 3)
    eleza test_repeat_large(self, size):
        rudisha self.basic_test_repeat(size)

    @bigmemtest(size=_1G - 1, memuse=12)
    eleza test_repeat_large_2(self, size):
        rudisha self.basic_test_repeat(size)

    @bigmemtest(size=_1G - 1, memuse=pointer_size * 2)
    eleza test_from_2G_generator(self, size):
        jaribu:
            t = tuple(iter([42]*size))
        tatizo MemoryError:
            pita # acceptable on 32-bit
        isipokua:
            self.assertEqual(len(t), size)
            self.assertEqual(t[:10], (42,) * 10)
            self.assertEqual(t[-10:], (42,) * 10)

    @bigmemtest(size=_1G - 25, memuse=pointer_size * 2)
    eleza test_from_almost_2G_generator(self, size):
        jaribu:
            t = tuple(iter([42]*size))
        tatizo MemoryError:
            pita # acceptable on 32-bit
        isipokua:
            self.assertEqual(len(t), size)
            self.assertEqual(t[:10], (42,) * 10)
            self.assertEqual(t[-10:], (42,) * 10)

    # Like test_concat, split kwenye two.
    eleza basic_test_repr(self, size):
        t = (Uongo,) * size
        s = repr(t)
        # The repr of a tuple of Uongos ni exactly 7 times the tuple length.
        self.assertEqual(len(s), size * 7)
        self.assertEqual(s[:10], '(Uongo, Fa')
        self.assertEqual(s[-10:], 'se, Uongo)')

    @bigmemtest(size=_2G // 7 + 2, memuse=pointer_size + ascii_char_size * 7)
    eleza test_repr_small(self, size):
        rudisha self.basic_test_repr(size)

    @bigmemtest(size=_2G + 2, memuse=pointer_size + ascii_char_size * 7)
    eleza test_repr_large(self, size):
        rudisha self.basic_test_repr(size)

kundi ListTest(unittest.TestCase):

    # Like tuples, lists have a small, fixed-sized head na an array of
    # pointers to data, so 8 bytes per size. Also like tuples, we make the
    # lists hold references to various objects to test their refcount
    # limits.

    @bigmemtest(size=_2G + 2, memuse=pointer_size * 2)
    eleza test_compare(self, size):
        l1 = [''] * size
        l2 = [''] * size
        self.assertKweli(l1 == l2)
        toa l2
        l2 = [''] * (size + 1)
        self.assertUongo(l1 == l2)
        toa l2
        l2 = [2] * size
        self.assertUongo(l1 == l2)

    # Test concatenating into a single list of more than 2G kwenye length,
    # na concatenating a list of more than 2G kwenye length separately, so
    # the smaller test still gets run even ikiwa there isn't memory kila the
    # larger test (but we still let the tester know the larger test is
    # skipped, kwenye verbose mode.)
    eleza basic_test_concat(self, size):
        l = [[]] * size
        self.assertEqual(len(l), size)
        l = l + l
        self.assertEqual(len(l), size * 2)

    @bigmemtest(size=_2G // 2 + 2, memuse=pointer_size * 3)
    eleza test_concat_small(self, size):
        rudisha self.basic_test_concat(size)

    @bigmemtest(size=_2G + 2, memuse=pointer_size * 3)
    eleza test_concat_large(self, size):
        rudisha self.basic_test_concat(size)

    # XXX This tests suffers kutoka overallocation, just like test_append.
    # This should be fixed kwenye future.
    eleza basic_test_inplace_concat(self, size):
        l = [sys.stdout] * size
        l += l
        self.assertEqual(len(l), size * 2)
        self.assertKweli(l[0] ni l[-1])
        self.assertKweli(l[size - 1] ni l[size + 1])

    @bigmemtest(size=_2G // 2 + 2, memuse=pointer_size * 2 * 9/8)
    eleza test_inplace_concat_small(self, size):
        rudisha self.basic_test_inplace_concat(size)

    @bigmemtest(size=_2G + 2, memuse=pointer_size * 2 * 9/8)
    eleza test_inplace_concat_large(self, size):
        rudisha self.basic_test_inplace_concat(size)

    @bigmemtest(size=_2G // 5 + 10, memuse=pointer_size * 5)
    eleza test_contains(self, size):
        l = [1, 2, 3, 4, 5] * size
        self.assertEqual(len(l), size * 5)
        self.assertKweli(5 kwenye l)
        self.assertUongo([1, 2, 3, 4, 5] kwenye l)
        self.assertUongo(0 kwenye l)

    @bigmemtest(size=_2G + 10, memuse=pointer_size)
    eleza test_hash(self, size):
        l = [0] * size
        self.assertRaises(TypeError, hash, l)

    @bigmemtest(size=_2G + 10, memuse=pointer_size)
    eleza test_index_and_slice(self, size):
        l = [Tupu] * size
        self.assertEqual(len(l), size)
        self.assertEqual(l[-1], Tupu)
        self.assertEqual(l[5], Tupu)
        self.assertEqual(l[size - 1], Tupu)
        self.assertRaises(IndexError, operator.getitem, l, size)
        self.assertEqual(l[:5], [Tupu] * 5)
        self.assertEqual(l[-5:], [Tupu] * 5)
        self.assertEqual(l[20:25], [Tupu] * 5)
        self.assertEqual(l[-25:-20], [Tupu] * 5)
        self.assertEqual(l[size - 5:], [Tupu] * 5)
        self.assertEqual(l[size - 5:size], [Tupu] * 5)
        self.assertEqual(l[size - 6:size - 2], [Tupu] * 4)
        self.assertEqual(l[size:size], [])
        self.assertEqual(l[size:size+5], [])

        l[size - 2] = 5
        self.assertEqual(len(l), size)
        self.assertEqual(l[-3:], [Tupu, 5, Tupu])
        self.assertEqual(l.count(5), 1)
        self.assertRaises(IndexError, operator.setitem, l, size, 6)
        self.assertEqual(len(l), size)

        l[size - 7:] = [1, 2, 3, 4, 5]
        size -= 2
        self.assertEqual(len(l), size)
        self.assertEqual(l[-7:], [Tupu, Tupu, 1, 2, 3, 4, 5])

        l[:7] = [1, 2, 3, 4, 5]
        size -= 2
        self.assertEqual(len(l), size)
        self.assertEqual(l[:7], [1, 2, 3, 4, 5, Tupu, Tupu])

        toa l[size - 1]
        size -= 1
        self.assertEqual(len(l), size)
        self.assertEqual(l[-1], 4)

        toa l[-2:]
        size -= 2
        self.assertEqual(len(l), size)
        self.assertEqual(l[-1], 2)

        toa l[0]
        size -= 1
        self.assertEqual(len(l), size)
        self.assertEqual(l[0], 2)

        toa l[:2]
        size -= 2
        self.assertEqual(len(l), size)
        self.assertEqual(l[0], 4)

    # Like test_concat, split kwenye two.
    eleza basic_test_repeat(self, size):
        l = [] * size
        self.assertUongo(l)
        l = [''] * size
        self.assertEqual(len(l), size)
        l = l * 2
        self.assertEqual(len(l), size * 2)

    @bigmemtest(size=_2G // 2 + 2, memuse=pointer_size * 3)
    eleza test_repeat_small(self, size):
        rudisha self.basic_test_repeat(size)

    @bigmemtest(size=_2G + 2, memuse=pointer_size * 3)
    eleza test_repeat_large(self, size):
        rudisha self.basic_test_repeat(size)

    # XXX This tests suffers kutoka overallocation, just like test_append.
    # This should be fixed kwenye future.
    eleza basic_test_inplace_repeat(self, size):
        l = ['']
        l *= size
        self.assertEqual(len(l), size)
        self.assertKweli(l[0] ni l[-1])
        toa l

        l = [''] * size
        l *= 2
        self.assertEqual(len(l), size * 2)
        self.assertKweli(l[size - 1] ni l[-1])

    @bigmemtest(size=_2G // 2 + 2, memuse=pointer_size * 2 * 9/8)
    eleza test_inplace_repeat_small(self, size):
        rudisha self.basic_test_inplace_repeat(size)

    @bigmemtest(size=_2G + 2, memuse=pointer_size * 2 * 9/8)
    eleza test_inplace_repeat_large(self, size):
        rudisha self.basic_test_inplace_repeat(size)

    eleza basic_test_repr(self, size):
        l = [Uongo] * size
        s = repr(l)
        # The repr of a list of Uongos ni exactly 7 times the list length.
        self.assertEqual(len(s), size * 7)
        self.assertEqual(s[:10], '[Uongo, Fa')
        self.assertEqual(s[-10:], 'se, Uongo]')
        self.assertEqual(s.count('F'), size)

    @bigmemtest(size=_2G // 7 + 2, memuse=pointer_size + ascii_char_size * 7)
    eleza test_repr_small(self, size):
        rudisha self.basic_test_repr(size)

    @bigmemtest(size=_2G + 2, memuse=pointer_size + ascii_char_size * 7)
    eleza test_repr_large(self, size):
        rudisha self.basic_test_repr(size)

    # list overallocates ~1/8th of the total size (on first expansion) so
    # the single list.append call puts memuse at 9 bytes per size.
    @bigmemtest(size=_2G, memuse=pointer_size * 9/8)
    eleza test_append(self, size):
        l = [object()] * size
        l.append(object())
        self.assertEqual(len(l), size+1)
        self.assertKweli(l[-3] ni l[-2])
        self.assertUongo(l[-2] ni l[-1])

    @bigmemtest(size=_2G // 5 + 2, memuse=pointer_size * 5)
    eleza test_count(self, size):
        l = [1, 2, 3, 4, 5] * size
        self.assertEqual(l.count(1), size)
        self.assertEqual(l.count("1"), 0)

    # XXX This tests suffers kutoka overallocation, just like test_append.
    # This should be fixed kwenye future.
    eleza basic_test_extend(self, size):
        l = [object] * size
        l.extend(l)
        self.assertEqual(len(l), size * 2)
        self.assertKweli(l[0] ni l[-1])
        self.assertKweli(l[size - 1] ni l[size + 1])

    @bigmemtest(size=_2G // 2 + 2, memuse=pointer_size * 2 * 9/8)
    eleza test_extend_small(self, size):
        rudisha self.basic_test_extend(size)

    @bigmemtest(size=_2G + 2, memuse=pointer_size * 2 * 9/8)
    eleza test_extend_large(self, size):
        rudisha self.basic_test_extend(size)

    @bigmemtest(size=_2G // 5 + 2, memuse=pointer_size * 5)
    eleza test_index(self, size):
        l = [1, 2, 3, 4, 5] * size
        size *= 5
        self.assertEqual(l.index(1), 0)
        self.assertEqual(l.index(5, size - 5), size - 1)
        self.assertEqual(l.index(5, size - 5, size), size - 1)
        self.assertRaises(ValueError, l.index, 1, size - 4, size)
        self.assertRaises(ValueError, l.index, 6)

    # This tests suffers kutoka overallocation, just like test_append.
    @bigmemtest(size=_2G + 10, memuse=pointer_size * 9/8)
    eleza test_insert(self, size):
        l = [1.0] * size
        l.insert(size - 1, "A")
        size += 1
        self.assertEqual(len(l), size)
        self.assertEqual(l[-3:], [1.0, "A", 1.0])

        l.insert(size + 1, "B")
        size += 1
        self.assertEqual(len(l), size)
        self.assertEqual(l[-3:], ["A", 1.0, "B"])

        l.insert(1, "C")
        size += 1
        self.assertEqual(len(l), size)
        self.assertEqual(l[:3], [1.0, "C", 1.0])
        self.assertEqual(l[size - 3:], ["A", 1.0, "B"])

    @bigmemtest(size=_2G // 5 + 4, memuse=pointer_size * 5)
    eleza test_pop(self, size):
        l = ["a", "b", "c", "d", "e"] * size
        size *= 5
        self.assertEqual(len(l), size)

        item = l.pop()
        size -= 1
        self.assertEqual(len(l), size)
        self.assertEqual(item, "e")
        self.assertEqual(l[-2:], ["c", "d"])

        item = l.pop(0)
        size -= 1
        self.assertEqual(len(l), size)
        self.assertEqual(item, "a")
        self.assertEqual(l[:2], ["b", "c"])

        item = l.pop(size - 2)
        size -= 1
        self.assertEqual(len(l), size)
        self.assertEqual(item, "c")
        self.assertEqual(l[-2:], ["b", "d"])

    @bigmemtest(size=_2G + 10, memuse=pointer_size)
    eleza test_remove(self, size):
        l = [10] * size
        self.assertEqual(len(l), size)

        l.remove(10)
        size -= 1
        self.assertEqual(len(l), size)

        # Because of the earlier l.remove(), this append doesn't trigger
        # a resize.
        l.append(5)
        size += 1
        self.assertEqual(len(l), size)
        self.assertEqual(l[-2:], [10, 5])
        l.remove(5)
        size -= 1
        self.assertEqual(len(l), size)
        self.assertEqual(l[-2:], [10, 10])

    @bigmemtest(size=_2G // 5 + 2, memuse=pointer_size * 5)
    eleza test_reverse(self, size):
        l = [1, 2, 3, 4, 5] * size
        l.reverse()
        self.assertEqual(len(l), size * 5)
        self.assertEqual(l[-5:], [5, 4, 3, 2, 1])
        self.assertEqual(l[:5], [5, 4, 3, 2, 1])

    @bigmemtest(size=_2G // 5 + 2, memuse=pointer_size * 5 * 1.5)
    eleza test_sort(self, size):
        l = [1, 2, 3, 4, 5] * size
        l.sort()
        self.assertEqual(len(l), size * 5)
        self.assertEqual(l.count(1), size)
        self.assertEqual(l[:10], [1] * 10)
        self.assertEqual(l[-10:], [5] * 10)

eleza test_main():
    support.run_unittest(StrTest, BytesTest, BytearrayTest,
        TupleTest, ListTest)

ikiwa __name__ == '__main__':
    ikiwa len(sys.argv) > 1:
        support.set_memlimit(sys.argv[1])
    test_main()
