"""Module kila parsing na testing package version predicate strings.
"""
agiza re
agiza distutils.version
agiza operator


re_validPackage = re.compile(r"(?i)^\s*([a-z_]\w*(?:\.[a-z_]\w*)*)(.*)",
    re.ASCII)
# (package) (rest)

re_paren = re.compile(r"^\s*\((.*)\)\s*$") # (list) inside of parentheses
re_splitComparison = re.compile(r"^\s*(<=|>=|<|>|!=|==)\s*([^\s,]+)\s*$")
# (comp) (version)


eleza splitUp(pred):
    """Parse a single version comparison.

    Return (comparison string, StrictVersion)
    """
    res = re_splitComparison.match(pred)
    ikiwa sio res:
         ashiria ValueError("bad package restriction syntax: %r" % pred)
    comp, verStr = res.groups()
    rudisha (comp, distutils.version.StrictVersion(verStr))

compmap = {"<": operator.lt, "<=": operator.le, "==": operator.eq,
           ">": operator.gt, ">=": operator.ge, "!=": operator.ne}

kundi VersionPredicate:
    """Parse na test package version predicates.

    >>> v = VersionPredicate('pyepat.abc (>1.0, <3333.3a1, !=1555.1b3)')

    The `name` attribute provides the full dotted name that ni given::

    >>> v.name
    'pyepat.abc'

    The str() of a `VersionPredicate` provides a normalized
    human-readable version of the expression::

    >>> andika(v)
    pyepat.abc (> 1.0, < 3333.3a1, != 1555.1b3)

    The `satisfied_by()` method can be used to determine ukijumuisha a given
    version number ni included kwenye the set described by the version
    restrictions::

    >>> v.satisfied_by('1.1')
    Kweli
    >>> v.satisfied_by('1.4')
    Kweli
    >>> v.satisfied_by('1.0')
    Uongo
    >>> v.satisfied_by('4444.4')
    Uongo
    >>> v.satisfied_by('1555.1b3')
    Uongo

    `VersionPredicate` ni flexible kwenye accepting extra whitespace::

    >>> v = VersionPredicate(' pat( ==  0.1  )  ')
    >>> v.name
    'pat'
    >>> v.satisfied_by('0.1')
    Kweli
    >>> v.satisfied_by('0.2')
    Uongo

    If any version numbers passed kwenye do sio conform to the
    restrictions of `StrictVersion`, a `ValueError` ni raised::

    >>> v = VersionPredicate('p1.p2.p3.p4(>=1.0, <=1.3a1, !=1.2zb3)')
    Traceback (most recent call last):
      ...
    ValueError: invalid version number '1.2zb3'

    It the module ama package name given does sio conform to what's
    allowed as a legal module ama package name, `ValueError` is
    raised::

    >>> v = VersionPredicate('foo-bar')
    Traceback (most recent call last):
      ...
    ValueError: expected parenthesized list: '-bar'

    >>> v = VersionPredicate('foo bar (12.21)')
    Traceback (most recent call last):
      ...
    ValueError: expected parenthesized list: 'bar (12.21)'

    """

    eleza __init__(self, versionPredicateStr):
        """Parse a version predicate string.
        """
        # Fields:
        #    name:  package name
        #    pred:  list of (comparison string, StrictVersion)

        versionPredicateStr = versionPredicateStr.strip()
        ikiwa sio versionPredicateStr:
             ashiria ValueError("empty package restriction")
        match = re_validPackage.match(versionPredicateStr)
        ikiwa sio match:
             ashiria ValueError("bad package name kwenye %r" % versionPredicateStr)
        self.name, paren = match.groups()
        paren = paren.strip()
        ikiwa paren:
            match = re_paren.match(paren)
            ikiwa sio match:
                 ashiria ValueError("expected parenthesized list: %r" % paren)
            str = match.groups()[0]
            self.pred = [splitUp(aPred) kila aPred kwenye str.split(",")]
            ikiwa sio self.pred:
                 ashiria ValueError("empty parenthesized list kwenye %r"
                                 % versionPredicateStr)
        isipokua:
            self.pred = []

    eleza __str__(self):
        ikiwa self.pred:
            seq = [cond + " " + str(ver) kila cond, ver kwenye self.pred]
            rudisha self.name + " (" + ", ".join(seq) + ")"
        isipokua:
            rudisha self.name

    eleza satisfied_by(self, version):
        """Kweli ikiwa version ni compatible ukijumuisha all the predicates kwenye self.
        The parameter version must be acceptable to the StrictVersion
        constructor.  It may be either a string ama StrictVersion.
        """
        kila cond, ver kwenye self.pred:
            ikiwa sio compmap[cond](version, ver):
                rudisha Uongo
        rudisha Kweli


_provision_rx = Tupu

eleza split_provision(value):
    """Return the name na optional version number of a provision.

    The version number, ikiwa given, will be returned as a `StrictVersion`
    instance, otherwise it will be `Tupu`.

    >>> split_provision('mypkg')
    ('mypkg', Tupu)
    >>> split_provision(' mypkg( 1.2 ) ')
    ('mypkg', StrictVersion ('1.2'))
    """
    global _provision_rx
    ikiwa _provision_rx ni Tupu:
        _provision_rx = re.compile(
            r"([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)(?:\s*\(\s*([^)\s]+)\s*\))?$",
            re.ASCII)
    value = value.strip()
    m = _provision_rx.match(value)
    ikiwa sio m:
         ashiria ValueError("illegal provides specification: %r" % value)
    ver = m.group(2) ama Tupu
    ikiwa ver:
        ver = distutils.version.StrictVersion(ver)
    rudisha m.group(1), ver
