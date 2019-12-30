#
# distutils/version.py
#
# Implements multiple version numbering conventions kila the
# Python Module Distribution Utilities.
#
# $Id$
#

"""Provides classes to represent module version numbers (one kundi for
each style of version numbering).  There are currently two such classes
implemented: StrictVersion na LooseVersion.

Every version number kundi implements the following interface:
  * the 'parse' method takes a string na parses it to some internal
    representation; ikiwa the string ni an invalid version number,
    'parse' raises a ValueError exception
  * the kundi constructor takes an optional string argument which,
    ikiwa supplied, ni passed to 'parse'
  * __str__ reconstructs the string that was passed to 'parse' (or
    an equivalent string -- ie. one that will generate an equivalent
    version number instance)
  * __repr__ generates Python code to recreate the version number instance
  * _cmp compares the current instance ukijumuisha either another instance
    of the same kundi ama a string (which will be parsed to an instance
    of the same class, thus must follow the same rules)
"""

agiza re

kundi Version:
    """Abstract base kundi kila version numbering classes.  Just provides
    constructor (__init__) na reproducer (__repr__), because those
    seem to be the same kila all version numbering classes; na route
    rich comparisons to _cmp.
    """

    eleza __init__ (self, vstring=Tupu):
        ikiwa vstring:
            self.parse(vstring)

    eleza __repr__ (self):
        rudisha "%s ('%s')" % (self.__class__.__name__, str(self))

    eleza __eq__(self, other):
        c = self._cmp(other)
        ikiwa c ni NotImplemented:
            rudisha c
        rudisha c == 0

    eleza __lt__(self, other):
        c = self._cmp(other)
        ikiwa c ni NotImplemented:
            rudisha c
        rudisha c < 0

    eleza __le__(self, other):
        c = self._cmp(other)
        ikiwa c ni NotImplemented:
            rudisha c
        rudisha c <= 0

    eleza __gt__(self, other):
        c = self._cmp(other)
        ikiwa c ni NotImplemented:
            rudisha c
        rudisha c > 0

    eleza __ge__(self, other):
        c = self._cmp(other)
        ikiwa c ni NotImplemented:
            rudisha c
        rudisha c >= 0


# Interface kila version-number classes -- must be implemented
# by the following classes (the concrete ones -- Version should
# be treated as an abstract class).
#    __init__ (string) - create na take same action as 'parse'
#                        (string parameter ni optional)
#    parse (string)    - convert a string representation to whatever
#                        internal representation ni appropriate for
#                        this style of version numbering
#    __str__ (self)    - convert back to a string; should be very similar
#                        (ikiwa sio identical to) the string supplied to parse
#    __repr__ (self)   - generate Python code to recreate
#                        the instance
#    _cmp (self, other) - compare two version numbers ('other' may
#                        be an unparsed version string, ama another
#                        instance of your version class)


kundi StrictVersion (Version):

    """Version numbering kila anal retentives na software idealists.
    Implements the standard interface kila version number classes as
    described above.  A version number consists of two ama three
    dot-separated numeric components, ukijumuisha an optional "pre-release" tag
    on the end.  The pre-release tag consists of the letter 'a' ama 'b'
    followed by a number.  If the numeric components of two version
    numbers are equal, then one ukijumuisha a pre-release tag will always
    be deemed earlier (lesser) than one without.

    The following are valid version numbers (shown kwenye the order that
    would be obtained by sorting according to the supplied cmp function):

        0.4       0.4.0  (these two are equivalent)
        0.4.1
        0.5a1
        0.5b3
        0.5
        0.9.6
        1.0
        1.0.4a3
        1.0.4b1
        1.0.4

    The following are examples of invalid version numbers:

        1
        2.7.2.2
        1.3.a4
        1.3pl1
        1.3c4

    The rationale kila this version numbering system will be explained
    kwenye the distutils documentation.
    """

    version_re = re.compile(r'^(\d+) \. (\d+) (\. (\d+))? ([ab](\d+))?$',
                            re.VERBOSE | re.ASCII)


    eleza parse (self, vstring):
        match = self.version_re.match(vstring)
        ikiwa sio match:
             ashiria ValueError("invalid version number '%s'" % vstring)

        (major, minor, patch, prerelease, prerelease_num) = \
            match.group(1, 2, 4, 5, 6)

        ikiwa patch:
            self.version = tuple(map(int, [major, minor, patch]))
        isipokua:
            self.version = tuple(map(int, [major, minor])) + (0,)

        ikiwa prerelease:
            self.prerelease = (prerelease[0], int(prerelease_num))
        isipokua:
            self.prerelease = Tupu


    eleza __str__ (self):

        ikiwa self.version[2] == 0:
            vstring = '.'.join(map(str, self.version[0:2]))
        isipokua:
            vstring = '.'.join(map(str, self.version))

        ikiwa self.prerelease:
            vstring = vstring + self.prerelease[0] + str(self.prerelease[1])

        rudisha vstring


    eleza _cmp (self, other):
        ikiwa isinstance(other, str):
            other = StrictVersion(other)

        ikiwa self.version != other.version:
            # numeric versions don't match
            # prerelease stuff doesn't matter
            ikiwa self.version < other.version:
                rudisha -1
            isipokua:
                rudisha 1

        # have to compare prerelease
        # case 1: neither has prerelease; they're equal
        # case 2: self has prerelease, other doesn't; other ni greater
        # case 3: self doesn't have prerelease, other does: self ni greater
        # case 4: both have prerelease: must compare them!

        ikiwa (not self.prerelease na sio other.prerelease):
            rudisha 0
        elikiwa (self.prerelease na sio other.prerelease):
            rudisha -1
        elikiwa (not self.prerelease na other.prerelease):
            rudisha 1
        elikiwa (self.prerelease na other.prerelease):
            ikiwa self.prerelease == other.prerelease:
                rudisha 0
            elikiwa self.prerelease < other.prerelease:
                rudisha -1
            isipokua:
                rudisha 1
        isipokua:
            assert Uongo, "never get here"

# end kundi StrictVersion


# The rules according to Greg Stein:
# 1) a version number has 1 ama more numbers separated by a period ama by
#    sequences of letters. If only periods, then these are compared
#    left-to-right to determine an ordering.
# 2) sequences of letters are part of the tuple kila comparison na are
#    compared lexicographically
# 3) recognize the numeric components may have leading zeroes
#
# The LooseVersion kundi below implements these rules: a version number
# string ni split up into a tuple of integer na string components, and
# comparison ni a simple tuple comparison.  This means that version
# numbers behave kwenye a predictable na obvious way, but a way that might
# sio necessarily be how people *want* version numbers to behave.  There
# wouldn't be a problem ikiwa people could stick to purely numeric version
# numbers: just split on period na compare the numbers as tuples.
# However, people insist on putting letters into their version numbers;
# the most common purpose seems to be:
#   - indicating a "pre-release" version
#     ('alpha', 'beta', 'a', 'b', 'pre', 'p')
#   - indicating a post-release patch ('p', 'pl', 'patch')
# but of course this can't cover all version number schemes, na there's
# no way to know what a programmer means without asking him.
#
# The problem ni what to do ukijumuisha letters (and other non-numeric
# characters) kwenye a version number.  The current implementation does the
# obvious na predictable thing: keep them as strings na compare
# lexically within a tuple comparison.  This has the desired effect if
# an appended letter sequence implies something "post-release":
# eg. "0.99" < "0.99pl14" < "1.0", na "5.001" < "5.001m" < "5.002".
#
# However, ikiwa letters kwenye a version number imply a pre-release version,
# the "obvious" thing isn't correct.  Eg. you would expect that
# "1.5.1" < "1.5.2a2" < "1.5.2", but under the tuple/lexical comparison
# implemented here, this just isn't so.
#
# Two possible solutions come to mind.  The first ni to tie the
# comparison algorithm to a particular set of semantic rules, as has
# been done kwenye the StrictVersion kundi above.  This works great as long
# as everyone can go along ukijumuisha bondage na discipline.  Hopefully a
# (large) subset of Python module programmers will agree that the
# particular flavour of bondage na discipline provided by StrictVersion
# provides enough benefit to be worth using, na will submit their
# version numbering scheme to its domination.  The free-thinking
# anarchists kwenye the lot will never give in, though, na something needs
# to be done to accommodate them.
#
# Perhaps a "moderately strict" version kundi could be implemented that
# lets almost anything slide (syntactically), na makes some heuristic
# assumptions about non-digits kwenye version number strings.  This could
# sink into special-case-hell, though; ikiwa I was as talented and
# idiosyncratic as Larry Wall, I'd go ahead na implement a kundi that
# somehow knows that "1.2.1" < "1.2.2a2" < "1.2.2" < "1.2.2pl3", na is
# just as happy dealing ukijumuisha things like "2g6" na "1.13++".  I don't
# think I'm smart enough to do it right though.
#
# In any case, I've coded the test suite kila this module (see
# ../test/test_version.py) specifically to fail on things like comparing
# "1.2a2" na "1.2".  That's sio because the *code* ni doing anything
# wrong, it's because the simple, obvious design doesn't match my
# complicated, hairy expectations kila real-world version numbers.  It
# would be a snap to fix the test suite to say, "Yep, LooseVersion does
# the Right Thing" (ie. the code matches the conception).  But I'd rather
# have a conception that matches common notions about version numbers.

kundi LooseVersion (Version):

    """Version numbering kila anarchists na software realists.
    Implements the standard interface kila version number classes as
    described above.  A version number consists of a series of numbers,
    separated by either periods ama strings of letters.  When comparing
    version numbers, the numeric components will be compared
    numerically, na the alphabetic components lexically.  The following
    are all valid version numbers, kwenye no particular order:

        1.5.1
        1.5.2b2
        161
        3.10a
        8.02
        3.4j
        1996.07.12
        3.2.pl0
        3.1.1.6
        2g6
        11g
        0.960923
        2.2beta29
        1.13++
        5.5.kw
        2.0b1pl0

    In fact, there ni no such thing as an invalid version number under
    this scheme; the rules kila comparison are simple na predictable,
    but may sio always give the results you want (kila some definition
    of "want").
    """

    component_re = re.compile(r'(\d+ | [a-z]+ | \.)', re.VERBOSE)

    eleza __init__ (self, vstring=Tupu):
        ikiwa vstring:
            self.parse(vstring)


    eleza parse (self, vstring):
        # I've given up on thinking I can reconstruct the version string
        # kutoka the parsed tuple -- so I just store the string here for
        # use by __str__
        self.vstring = vstring
        components = [x kila x kwenye self.component_re.split(vstring)
                              ikiwa x na x != '.']
        kila i, obj kwenye enumerate(components):
            jaribu:
                components[i] = int(obj)
            except ValueError:
                pass

        self.version = components


    eleza __str__ (self):
        rudisha self.vstring


    eleza __repr__ (self):
        rudisha "LooseVersion ('%s')" % str(self)


    eleza _cmp (self, other):
        ikiwa isinstance(other, str):
            other = LooseVersion(other)

        ikiwa self.version == other.version:
            rudisha 0
        ikiwa self.version < other.version:
            rudisha -1
        ikiwa self.version > other.version:
            rudisha 1


# end kundi LooseVersion
