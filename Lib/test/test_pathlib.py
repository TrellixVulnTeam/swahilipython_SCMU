agiza collections.abc
agiza io
agiza os
agiza sys
agiza errno
agiza pathlib
agiza pickle
agiza socket
agiza stat
agiza tempfile
agiza unittest
kutoka unittest agiza mock

kutoka test agiza support
kutoka test.support agiza TESTFN, FakePath

jaribu:
    agiza grp, pwd
tatizo ImportError:
    grp = pwd = Tupu


kundi _BaseFlavourTest(object):

    eleza _check_parse_parts(self, arg, expected):
        f = self.flavour.parse_parts
        sep = self.flavour.sep
        altsep = self.flavour.altsep
        actual = f([x.replace('/', sep) kila x kwenye arg])
        self.assertEqual(actual, expected)
        ikiwa altsep:
            actual = f([x.replace('/', altsep) kila x kwenye arg])
            self.assertEqual(actual, expected)

    eleza test_parse_parts_common(self):
        check = self._check_parse_parts
        sep = self.flavour.sep
        # Unanchored parts.
        check([],                   ('', '', []))
        check(['a'],                ('', '', ['a']))
        check(['a/'],               ('', '', ['a']))
        check(['a', 'b'],           ('', '', ['a', 'b']))
        # Expansion.
        check(['a/b'],              ('', '', ['a', 'b']))
        check(['a/b/'],             ('', '', ['a', 'b']))
        check(['a', 'b/c', 'd'],    ('', '', ['a', 'b', 'c', 'd']))
        # Collapsing na stripping excess slashes.
        check(['a', 'b//c', 'd'],   ('', '', ['a', 'b', 'c', 'd']))
        check(['a', 'b/c/', 'd'],   ('', '', ['a', 'b', 'c', 'd']))
        # Eliminating standalone dots.
        check(['.'],                ('', '', []))
        check(['.', '.', 'b'],      ('', '', ['b']))
        check(['a', '.', 'b'],      ('', '', ['a', 'b']))
        check(['a', '.', '.'],      ('', '', ['a']))
        # The first part ni anchored.
        check(['/a/b'],             ('', sep, [sep, 'a', 'b']))
        check(['/a', 'b'],          ('', sep, [sep, 'a', 'b']))
        check(['/a/', 'b'],         ('', sep, [sep, 'a', 'b']))
        # Ignoring parts before an anchored part.
        check(['a', '/b', 'c'],     ('', sep, [sep, 'b', 'c']))
        check(['a', '/b', '/c'],    ('', sep, [sep, 'c']))


kundi PosixFlavourTest(_BaseFlavourTest, unittest.TestCase):
    flavour = pathlib._posix_flavour

    eleza test_parse_parts(self):
        check = self._check_parse_parts
        # Collapsing of excess leading slashes, tatizo kila the double-slash
        # special case.
        check(['//a', 'b'],             ('', '//', ['//', 'a', 'b']))
        check(['///a', 'b'],            ('', '/', ['/', 'a', 'b']))
        check(['////a', 'b'],           ('', '/', ['/', 'a', 'b']))
        # Paths which look like NT paths aren't treated specially.
        check(['c:a'],                  ('', '', ['c:a']))
        check(['c:\\a'],                ('', '', ['c:\\a']))
        check(['\\a'],                  ('', '', ['\\a']))

    eleza test_splitroot(self):
        f = self.flavour.splitroot
        self.assertEqual(f(''), ('', '', ''))
        self.assertEqual(f('a'), ('', '', 'a'))
        self.assertEqual(f('a/b'), ('', '', 'a/b'))
        self.assertEqual(f('a/b/'), ('', '', 'a/b/'))
        self.assertEqual(f('/a'), ('', '/', 'a'))
        self.assertEqual(f('/a/b'), ('', '/', 'a/b'))
        self.assertEqual(f('/a/b/'), ('', '/', 'a/b/'))
        # The root ni collapsed when there are redundant slashes
        # tatizo when there are exactly two leading slashes, which
        # ni a special case kwenye POSIX.
        self.assertEqual(f('//a'), ('', '//', 'a'))
        self.assertEqual(f('///a'), ('', '/', 'a'))
        self.assertEqual(f('///a/b'), ('', '/', 'a/b'))
        # Paths which look like NT paths aren't treated specially.
        self.assertEqual(f('c:/a/b'), ('', '', 'c:/a/b'))
        self.assertEqual(f('\\/a/b'), ('', '', '\\/a/b'))
        self.assertEqual(f('\\a\\b'), ('', '', '\\a\\b'))


kundi NTFlavourTest(_BaseFlavourTest, unittest.TestCase):
    flavour = pathlib._windows_flavour

    eleza test_parse_parts(self):
        check = self._check_parse_parts
        # First part ni anchored.
        check(['c:'],                   ('c:', '', ['c:']))
        check(['c:/'],                  ('c:', '\\', ['c:\\']))
        check(['/'],                    ('', '\\', ['\\']))
        check(['c:a'],                  ('c:', '', ['c:', 'a']))
        check(['c:/a'],                 ('c:', '\\', ['c:\\', 'a']))
        check(['/a'],                   ('', '\\', ['\\', 'a']))
        # UNC paths.
        check(['//a/b'],                ('\\\\a\\b', '\\', ['\\\\a\\b\\']))
        check(['//a/b/'],               ('\\\\a\\b', '\\', ['\\\\a\\b\\']))
        check(['//a/b/c'],              ('\\\\a\\b', '\\', ['\\\\a\\b\\', 'c']))
        # Second part ni anchored, so that the first part ni ignored.
        check(['a', 'Z:b', 'c'],        ('Z:', '', ['Z:', 'b', 'c']))
        check(['a', 'Z:/b', 'c'],       ('Z:', '\\', ['Z:\\', 'b', 'c']))
        # UNC paths.
        check(['a', '//b/c', 'd'],      ('\\\\b\\c', '\\', ['\\\\b\\c\\', 'd']))
        # Collapsing na stripping excess slashes.
        check(['a', 'Z://b//c/', 'd/'], ('Z:', '\\', ['Z:\\', 'b', 'c', 'd']))
        # UNC paths.
        check(['a', '//b/c//', 'd'],    ('\\\\b\\c', '\\', ['\\\\b\\c\\', 'd']))
        # Extended paths.
        check(['//?/c:/'],              ('\\\\?\\c:', '\\', ['\\\\?\\c:\\']))
        check(['//?/c:/a'],             ('\\\\?\\c:', '\\', ['\\\\?\\c:\\', 'a']))
        check(['//?/c:/a', '/b'],       ('\\\\?\\c:', '\\', ['\\\\?\\c:\\', 'b']))
        # Extended UNC paths (format ni "\\?\UNC\server\share").
        check(['//?/UNC/b/c'],          ('\\\\?\\UNC\\b\\c', '\\', ['\\\\?\\UNC\\b\\c\\']))
        check(['//?/UNC/b/c/d'],        ('\\\\?\\UNC\\b\\c', '\\', ['\\\\?\\UNC\\b\\c\\', 'd']))
        # Second part has a root but sio drive.
        check(['a', '/b', 'c'],         ('', '\\', ['\\', 'b', 'c']))
        check(['Z:/a', '/b', 'c'],      ('Z:', '\\', ['Z:\\', 'b', 'c']))
        check(['//?/Z:/a', '/b', 'c'],  ('\\\\?\\Z:', '\\', ['\\\\?\\Z:\\', 'b', 'c']))

    eleza test_splitroot(self):
        f = self.flavour.splitroot
        self.assertEqual(f(''), ('', '', ''))
        self.assertEqual(f('a'), ('', '', 'a'))
        self.assertEqual(f('a\\b'), ('', '', 'a\\b'))
        self.assertEqual(f('\\a'), ('', '\\', 'a'))
        self.assertEqual(f('\\a\\b'), ('', '\\', 'a\\b'))
        self.assertEqual(f('c:a\\b'), ('c:', '', 'a\\b'))
        self.assertEqual(f('c:\\a\\b'), ('c:', '\\', 'a\\b'))
        # Redundant slashes kwenye the root are collapsed.
        self.assertEqual(f('\\\\a'), ('', '\\', 'a'))
        self.assertEqual(f('\\\\\\a/b'), ('', '\\', 'a/b'))
        self.assertEqual(f('c:\\\\a'), ('c:', '\\', 'a'))
        self.assertEqual(f('c:\\\\\\a/b'), ('c:', '\\', 'a/b'))
        # Valid UNC paths.
        self.assertEqual(f('\\\\a\\b'), ('\\\\a\\b', '\\', ''))
        self.assertEqual(f('\\\\a\\b\\'), ('\\\\a\\b', '\\', ''))
        self.assertEqual(f('\\\\a\\b\\c\\d'), ('\\\\a\\b', '\\', 'c\\d'))
        # These are non-UNC paths (according to ntpath.py na test_ntpath).
        # However, command.com says such paths are invalid, so it's
        # difficult to know what the right semantics are.
        self.assertEqual(f('\\\\\\a\\b'), ('', '\\', 'a\\b'))
        self.assertEqual(f('\\\\a'), ('', '\\', 'a'))


#
# Tests kila the pure classes.
#

kundi _BasePurePathTest(object):

    # Keys are canonical paths, values are list of tuples of arguments
    # supposed to produce equal paths.
    equivalences = {
        'a/b': [
            ('a', 'b'), ('a/', 'b'), ('a', 'b/'), ('a/', 'b/'),
            ('a/b/',), ('a//b',), ('a//b//',),
            # Empty components get removed.
            ('', 'a', 'b'), ('a', '', 'b'), ('a', 'b', ''),
            ],
        '/b/c/d': [
            ('a', '/b/c', 'd'), ('a', '///b//c', 'd/'),
            ('/a', '/b/c', 'd'),
            # Empty components get removed.
            ('/', 'b', '', 'c/d'), ('/', '', 'b/c/d'), ('', '/b/c/d'),
            ],
    }

    eleza setUp(self):
        p = self.cls('a')
        self.flavour = p._flavour
        self.sep = self.flavour.sep
        self.altsep = self.flavour.altsep

    eleza test_constructor_common(self):
        P = self.cls
        p = P('a')
        self.assertIsInstance(p, P)
        P('a', 'b', 'c')
        P('/a', 'b', 'c')
        P('a/b/c')
        P('/a/b/c')
        P(FakePath("a/b/c"))
        self.assertEqual(P(P('a')), P('a'))
        self.assertEqual(P(P('a'), 'b'), P('a/b'))
        self.assertEqual(P(P('a'), P('b')), P('a/b'))
        self.assertEqual(P(P('a'), P('b'), P('c')), P(FakePath("a/b/c")))

    eleza _check_str_subclass(self, *args):
        # Issue #21127: it should be possible to construct a PurePath object
        # kutoka a str subkundi instance, na it then gets converted to
        # a pure str object.
        kundi StrSubclass(str):
            pita
        P = self.cls
        p = P(*(StrSubclass(x) kila x kwenye args))
        self.assertEqual(p, P(*args))
        kila part kwenye p.parts:
            self.assertIs(type(part), str)

    eleza test_str_subclass_common(self):
        self._check_str_subclass('')
        self._check_str_subclass('.')
        self._check_str_subclass('a')
        self._check_str_subclass('a/b.txt')
        self._check_str_subclass('/a/b.txt')

    eleza test_join_common(self):
        P = self.cls
        p = P('a/b')
        pp = p.joinpath('c')
        self.assertEqual(pp, P('a/b/c'))
        self.assertIs(type(pp), type(p))
        pp = p.joinpath('c', 'd')
        self.assertEqual(pp, P('a/b/c/d'))
        pp = p.joinpath(P('c'))
        self.assertEqual(pp, P('a/b/c'))
        pp = p.joinpath('/c')
        self.assertEqual(pp, P('/c'))

    eleza test_div_common(self):
        # Basically the same kama joinpath().
        P = self.cls
        p = P('a/b')
        pp = p / 'c'
        self.assertEqual(pp, P('a/b/c'))
        self.assertIs(type(pp), type(p))
        pp = p / 'c/d'
        self.assertEqual(pp, P('a/b/c/d'))
        pp = p / 'c' / 'd'
        self.assertEqual(pp, P('a/b/c/d'))
        pp = 'c' / p / 'd'
        self.assertEqual(pp, P('c/a/b/d'))
        pp = p / P('c')
        self.assertEqual(pp, P('a/b/c'))
        pp = p/ '/c'
        self.assertEqual(pp, P('/c'))

    eleza _check_str(self, expected, args):
        p = self.cls(*args)
        self.assertEqual(str(p), expected.replace('/', self.sep))

    eleza test_str_common(self):
        # Canonicalized paths roundtrip.
        kila pathstr kwenye ('a', 'a/b', 'a/b/c', '/', '/a/b', '/a/b/c'):
            self._check_str(pathstr, (pathstr,))
        # Special case kila the empty path.
        self._check_str('.', ('',))
        # Other tests kila str() are kwenye test_equivalences().

    eleza test_as_posix_common(self):
        P = self.cls
        kila pathstr kwenye ('a', 'a/b', 'a/b/c', '/', '/a/b', '/a/b/c'):
            self.assertEqual(P(pathstr).as_posix(), pathstr)
        # Other tests kila as_posix() are kwenye test_equivalences().

    eleza test_as_bytes_common(self):
        sep = os.fsencode(self.sep)
        P = self.cls
        self.assertEqual(bytes(P('a/b')), b'a' + sep + b'b')

    eleza test_as_uri_common(self):
        P = self.cls
        ukijumuisha self.assertRaises(ValueError):
            P('a').as_uri()
        ukijumuisha self.assertRaises(ValueError):
            P().as_uri()

    eleza test_repr_common(self):
        kila pathstr kwenye ('a', 'a/b', 'a/b/c', '/', '/a/b', '/a/b/c'):
            p = self.cls(pathstr)
            clsname = p.__class__.__name__
            r = repr(p)
            # The repr() ni kwenye the form ClassName("forward-slashes path").
            self.assertKweli(r.startswith(clsname + '('), r)
            self.assertKweli(r.endswith(')'), r)
            inner = r[len(clsname) + 1 : -1]
            self.assertEqual(eval(inner), p.as_posix())
            # The repr() roundtrips.
            q = eval(r, pathlib.__dict__)
            self.assertIs(q.__class__, p.__class__)
            self.assertEqual(q, p)
            self.assertEqual(repr(q), r)

    eleza test_eq_common(self):
        P = self.cls
        self.assertEqual(P('a/b'), P('a/b'))
        self.assertEqual(P('a/b'), P('a', 'b'))
        self.assertNotEqual(P('a/b'), P('a'))
        self.assertNotEqual(P('a/b'), P('/a/b'))
        self.assertNotEqual(P('a/b'), P())
        self.assertNotEqual(P('/a/b'), P('/'))
        self.assertNotEqual(P(), P('/'))
        self.assertNotEqual(P(), "")
        self.assertNotEqual(P(), {})
        self.assertNotEqual(P(), int)

    eleza test_match_common(self):
        P = self.cls
        self.assertRaises(ValueError, P('a').match, '')
        self.assertRaises(ValueError, P('a').match, '.')
        # Simple relative pattern.
        self.assertKweli(P('b.py').match('b.py'))
        self.assertKweli(P('a/b.py').match('b.py'))
        self.assertKweli(P('/a/b.py').match('b.py'))
        self.assertUongo(P('a.py').match('b.py'))
        self.assertUongo(P('b/py').match('b.py'))
        self.assertUongo(P('/a.py').match('b.py'))
        self.assertUongo(P('b.py/c').match('b.py'))
        # Wilcard relative pattern.
        self.assertKweli(P('b.py').match('*.py'))
        self.assertKweli(P('a/b.py').match('*.py'))
        self.assertKweli(P('/a/b.py').match('*.py'))
        self.assertUongo(P('b.pyc').match('*.py'))
        self.assertUongo(P('b./py').match('*.py'))
        self.assertUongo(P('b.py/c').match('*.py'))
        # Multi-part relative pattern.
        self.assertKweli(P('ab/c.py').match('a*/*.py'))
        self.assertKweli(P('/d/ab/c.py').match('a*/*.py'))
        self.assertUongo(P('a.py').match('a*/*.py'))
        self.assertUongo(P('/dab/c.py').match('a*/*.py'))
        self.assertUongo(P('ab/c.py/d').match('a*/*.py'))
        # Absolute pattern.
        self.assertKweli(P('/b.py').match('/*.py'))
        self.assertUongo(P('b.py').match('/*.py'))
        self.assertUongo(P('a/b.py').match('/*.py'))
        self.assertUongo(P('/a/b.py').match('/*.py'))
        # Multi-part absolute pattern.
        self.assertKweli(P('/a/b.py').match('/a/*.py'))
        self.assertUongo(P('/ab.py').match('/a/*.py'))
        self.assertUongo(P('/a/b/c.py').match('/a/*.py'))
        # Multi-part glob-style pattern.
        self.assertUongo(P('/a/b/c.py').match('/**/*.py'))
        self.assertKweli(P('/a/b/c.py').match('/a/**/*.py'))

    eleza test_ordering_common(self):
        # Ordering ni tuple-alike.
        eleza assertLess(a, b):
            self.assertLess(a, b)
            self.assertGreater(b, a)
        P = self.cls
        a = P('a')
        b = P('a/b')
        c = P('abc')
        d = P('b')
        assertLess(a, b)
        assertLess(a, c)
        assertLess(a, d)
        assertLess(b, c)
        assertLess(c, d)
        P = self.cls
        a = P('/a')
        b = P('/a/b')
        c = P('/abc')
        d = P('/b')
        assertLess(a, b)
        assertLess(a, c)
        assertLess(a, d)
        assertLess(b, c)
        assertLess(c, d)
        ukijumuisha self.assertRaises(TypeError):
            P() < {}

    eleza test_parts_common(self):
        # `parts` returns a tuple.
        sep = self.sep
        P = self.cls
        p = P('a/b')
        parts = p.parts
        self.assertEqual(parts, ('a', 'b'))
        # The object gets reused.
        self.assertIs(parts, p.parts)
        # When the path ni absolute, the anchor ni a separate part.
        p = P('/a/b')
        parts = p.parts
        self.assertEqual(parts, (sep, 'a', 'b'))

    eleza test_fspath_common(self):
        P = self.cls
        p = P('a/b')
        self._check_str(p.__fspath__(), ('a/b',))
        self._check_str(os.fspath(p), ('a/b',))

    eleza test_equivalences(self):
        kila k, tuples kwenye self.equivalences.items():
            canon = k.replace('/', self.sep)
            posix = k.replace(self.sep, '/')
            ikiwa canon != posix:
                tuples = tuples + [
                    tuple(part.replace('/', self.sep) kila part kwenye t)
                    kila t kwenye tuples
                    ]
                tuples.append((posix, ))
            pcanon = self.cls(canon)
            kila t kwenye tuples:
                p = self.cls(*t)
                self.assertEqual(p, pcanon, "failed ukijumuisha args {}".format(t))
                self.assertEqual(hash(p), hash(pcanon))
                self.assertEqual(str(p), canon)
                self.assertEqual(p.as_posix(), posix)

    eleza test_parent_common(self):
        # Relative
        P = self.cls
        p = P('a/b/c')
        self.assertEqual(p.parent, P('a/b'))
        self.assertEqual(p.parent.parent, P('a'))
        self.assertEqual(p.parent.parent.parent, P())
        self.assertEqual(p.parent.parent.parent.parent, P())
        # Anchored
        p = P('/a/b/c')
        self.assertEqual(p.parent, P('/a/b'))
        self.assertEqual(p.parent.parent, P('/a'))
        self.assertEqual(p.parent.parent.parent, P('/'))
        self.assertEqual(p.parent.parent.parent.parent, P('/'))

    eleza test_parents_common(self):
        # Relative
        P = self.cls
        p = P('a/b/c')
        par = p.parents
        self.assertEqual(len(par), 3)
        self.assertEqual(par[0], P('a/b'))
        self.assertEqual(par[1], P('a'))
        self.assertEqual(par[2], P('.'))
        self.assertEqual(list(par), [P('a/b'), P('a'), P('.')])
        ukijumuisha self.assertRaises(IndexError):
            par[-1]
        ukijumuisha self.assertRaises(IndexError):
            par[3]
        ukijumuisha self.assertRaises(TypeError):
            par[0] = p
        # Anchored
        p = P('/a/b/c')
        par = p.parents
        self.assertEqual(len(par), 3)
        self.assertEqual(par[0], P('/a/b'))
        self.assertEqual(par[1], P('/a'))
        self.assertEqual(par[2], P('/'))
        self.assertEqual(list(par), [P('/a/b'), P('/a'), P('/')])
        ukijumuisha self.assertRaises(IndexError):
            par[3]

    eleza test_drive_common(self):
        P = self.cls
        self.assertEqual(P('a/b').drive, '')
        self.assertEqual(P('/a/b').drive, '')
        self.assertEqual(P('').drive, '')

    eleza test_root_common(self):
        P = self.cls
        sep = self.sep
        self.assertEqual(P('').root, '')
        self.assertEqual(P('a/b').root, '')
        self.assertEqual(P('/').root, sep)
        self.assertEqual(P('/a/b').root, sep)

    eleza test_anchor_common(self):
        P = self.cls
        sep = self.sep
        self.assertEqual(P('').anchor, '')
        self.assertEqual(P('a/b').anchor, '')
        self.assertEqual(P('/').anchor, sep)
        self.assertEqual(P('/a/b').anchor, sep)

    eleza test_name_common(self):
        P = self.cls
        self.assertEqual(P('').name, '')
        self.assertEqual(P('.').name, '')
        self.assertEqual(P('/').name, '')
        self.assertEqual(P('a/b').name, 'b')
        self.assertEqual(P('/a/b').name, 'b')
        self.assertEqual(P('/a/b/.').name, 'b')
        self.assertEqual(P('a/b.py').name, 'b.py')
        self.assertEqual(P('/a/b.py').name, 'b.py')

    eleza test_suffix_common(self):
        P = self.cls
        self.assertEqual(P('').suffix, '')
        self.assertEqual(P('.').suffix, '')
        self.assertEqual(P('..').suffix, '')
        self.assertEqual(P('/').suffix, '')
        self.assertEqual(P('a/b').suffix, '')
        self.assertEqual(P('/a/b').suffix, '')
        self.assertEqual(P('/a/b/.').suffix, '')
        self.assertEqual(P('a/b.py').suffix, '.py')
        self.assertEqual(P('/a/b.py').suffix, '.py')
        self.assertEqual(P('a/.hgrc').suffix, '')
        self.assertEqual(P('/a/.hgrc').suffix, '')
        self.assertEqual(P('a/.hg.rc').suffix, '.rc')
        self.assertEqual(P('/a/.hg.rc').suffix, '.rc')
        self.assertEqual(P('a/b.tar.gz').suffix, '.gz')
        self.assertEqual(P('/a/b.tar.gz').suffix, '.gz')
        self.assertEqual(P('a/Some name. Ending ukijumuisha a dot.').suffix, '')
        self.assertEqual(P('/a/Some name. Ending ukijumuisha a dot.').suffix, '')

    eleza test_suffixes_common(self):
        P = self.cls
        self.assertEqual(P('').suffixes, [])
        self.assertEqual(P('.').suffixes, [])
        self.assertEqual(P('/').suffixes, [])
        self.assertEqual(P('a/b').suffixes, [])
        self.assertEqual(P('/a/b').suffixes, [])
        self.assertEqual(P('/a/b/.').suffixes, [])
        self.assertEqual(P('a/b.py').suffixes, ['.py'])
        self.assertEqual(P('/a/b.py').suffixes, ['.py'])
        self.assertEqual(P('a/.hgrc').suffixes, [])
        self.assertEqual(P('/a/.hgrc').suffixes, [])
        self.assertEqual(P('a/.hg.rc').suffixes, ['.rc'])
        self.assertEqual(P('/a/.hg.rc').suffixes, ['.rc'])
        self.assertEqual(P('a/b.tar.gz').suffixes, ['.tar', '.gz'])
        self.assertEqual(P('/a/b.tar.gz').suffixes, ['.tar', '.gz'])
        self.assertEqual(P('a/Some name. Ending ukijumuisha a dot.').suffixes, [])
        self.assertEqual(P('/a/Some name. Ending ukijumuisha a dot.').suffixes, [])

    eleza test_stem_common(self):
        P = self.cls
        self.assertEqual(P('').stem, '')
        self.assertEqual(P('.').stem, '')
        self.assertEqual(P('..').stem, '..')
        self.assertEqual(P('/').stem, '')
        self.assertEqual(P('a/b').stem, 'b')
        self.assertEqual(P('a/b.py').stem, 'b')
        self.assertEqual(P('a/.hgrc').stem, '.hgrc')
        self.assertEqual(P('a/.hg.rc').stem, '.hg')
        self.assertEqual(P('a/b.tar.gz').stem, 'b.tar')
        self.assertEqual(P('a/Some name. Ending ukijumuisha a dot.').stem,
                         'Some name. Ending ukijumuisha a dot.')

    eleza test_with_name_common(self):
        P = self.cls
        self.assertEqual(P('a/b').with_name('d.xml'), P('a/d.xml'))
        self.assertEqual(P('/a/b').with_name('d.xml'), P('/a/d.xml'))
        self.assertEqual(P('a/b.py').with_name('d.xml'), P('a/d.xml'))
        self.assertEqual(P('/a/b.py').with_name('d.xml'), P('/a/d.xml'))
        self.assertEqual(P('a/Dot ending.').with_name('d.xml'), P('a/d.xml'))
        self.assertEqual(P('/a/Dot ending.').with_name('d.xml'), P('/a/d.xml'))
        self.assertRaises(ValueError, P('').with_name, 'd.xml')
        self.assertRaises(ValueError, P('.').with_name, 'd.xml')
        self.assertRaises(ValueError, P('/').with_name, 'd.xml')
        self.assertRaises(ValueError, P('a/b').with_name, '')
        self.assertRaises(ValueError, P('a/b').with_name, '/c')
        self.assertRaises(ValueError, P('a/b').with_name, 'c/')
        self.assertRaises(ValueError, P('a/b').with_name, 'c/d')

    eleza test_with_suffix_common(self):
        P = self.cls
        self.assertEqual(P('a/b').with_suffix('.gz'), P('a/b.gz'))
        self.assertEqual(P('/a/b').with_suffix('.gz'), P('/a/b.gz'))
        self.assertEqual(P('a/b.py').with_suffix('.gz'), P('a/b.gz'))
        self.assertEqual(P('/a/b.py').with_suffix('.gz'), P('/a/b.gz'))
        # Stripping suffix.
        self.assertEqual(P('a/b.py').with_suffix(''), P('a/b'))
        self.assertEqual(P('/a/b').with_suffix(''), P('/a/b'))
        # Path doesn't have a "filename" component.
        self.assertRaises(ValueError, P('').with_suffix, '.gz')
        self.assertRaises(ValueError, P('.').with_suffix, '.gz')
        self.assertRaises(ValueError, P('/').with_suffix, '.gz')
        # Invalid suffix.
        self.assertRaises(ValueError, P('a/b').with_suffix, 'gz')
        self.assertRaises(ValueError, P('a/b').with_suffix, '/')
        self.assertRaises(ValueError, P('a/b').with_suffix, '.')
        self.assertRaises(ValueError, P('a/b').with_suffix, '/.gz')
        self.assertRaises(ValueError, P('a/b').with_suffix, 'c/d')
        self.assertRaises(ValueError, P('a/b').with_suffix, '.c/.d')
        self.assertRaises(ValueError, P('a/b').with_suffix, './.d')
        self.assertRaises(ValueError, P('a/b').with_suffix, '.d/.')
        self.assertRaises(ValueError, P('a/b').with_suffix,
                          (self.flavour.sep, 'd'))

    eleza test_relative_to_common(self):
        P = self.cls
        p = P('a/b')
        self.assertRaises(TypeError, p.relative_to)
        self.assertRaises(TypeError, p.relative_to, b'a')
        self.assertEqual(p.relative_to(P()), P('a/b'))
        self.assertEqual(p.relative_to(''), P('a/b'))
        self.assertEqual(p.relative_to(P('a')), P('b'))
        self.assertEqual(p.relative_to('a'), P('b'))
        self.assertEqual(p.relative_to('a/'), P('b'))
        self.assertEqual(p.relative_to(P('a/b')), P())
        self.assertEqual(p.relative_to('a/b'), P())
        # With several args.
        self.assertEqual(p.relative_to('a', 'b'), P())
        # Unrelated paths.
        self.assertRaises(ValueError, p.relative_to, P('c'))
        self.assertRaises(ValueError, p.relative_to, P('a/b/c'))
        self.assertRaises(ValueError, p.relative_to, P('a/c'))
        self.assertRaises(ValueError, p.relative_to, P('/a'))
        p = P('/a/b')
        self.assertEqual(p.relative_to(P('/')), P('a/b'))
        self.assertEqual(p.relative_to('/'), P('a/b'))
        self.assertEqual(p.relative_to(P('/a')), P('b'))
        self.assertEqual(p.relative_to('/a'), P('b'))
        self.assertEqual(p.relative_to('/a/'), P('b'))
        self.assertEqual(p.relative_to(P('/a/b')), P())
        self.assertEqual(p.relative_to('/a/b'), P())
        # Unrelated paths.
        self.assertRaises(ValueError, p.relative_to, P('/c'))
        self.assertRaises(ValueError, p.relative_to, P('/a/b/c'))
        self.assertRaises(ValueError, p.relative_to, P('/a/c'))
        self.assertRaises(ValueError, p.relative_to, P())
        self.assertRaises(ValueError, p.relative_to, '')
        self.assertRaises(ValueError, p.relative_to, P('a'))

    eleza test_pickling_common(self):
        P = self.cls
        p = P('/a/b')
        kila proto kwenye range(0, pickle.HIGHEST_PROTOCOL + 1):
            dumped = pickle.dumps(p, proto)
            pp = pickle.loads(dumped)
            self.assertIs(pp.__class__, p.__class__)
            self.assertEqual(pp, p)
            self.assertEqual(hash(pp), hash(p))
            self.assertEqual(str(pp), str(p))


kundi PurePosixPathTest(_BasePurePathTest, unittest.TestCase):
    cls = pathlib.PurePosixPath

    eleza test_root(self):
        P = self.cls
        self.assertEqual(P('/a/b').root, '/')
        self.assertEqual(P('///a/b').root, '/')
        # POSIX special case kila two leading slashes.
        self.assertEqual(P('//a/b').root, '//')

    eleza test_eq(self):
        P = self.cls
        self.assertNotEqual(P('a/b'), P('A/b'))
        self.assertEqual(P('/a'), P('///a'))
        self.assertNotEqual(P('/a'), P('//a'))

    eleza test_as_uri(self):
        P = self.cls
        self.assertEqual(P('/').as_uri(), 'file:///')
        self.assertEqual(P('/a/b.c').as_uri(), 'file:///a/b.c')
        self.assertEqual(P('/a/b%#c').as_uri(), 'file:///a/b%25%23c')

    eleza test_as_uri_non_ascii(self):
        kutoka urllib.parse agiza quote_from_bytes
        P = self.cls
        jaribu:
            os.fsencode('\xe9')
        tatizo UnicodeEncodeError:
            self.skipTest("\\xe9 cannot be encoded to the filesystem encoding")
        self.assertEqual(P('/a/b\xe9').as_uri(),
                         'file:///a/b' + quote_from_bytes(os.fsencode('\xe9')))

    eleza test_match(self):
        P = self.cls
        self.assertUongo(P('A.py').match('a.PY'))

    eleza test_is_absolute(self):
        P = self.cls
        self.assertUongo(P().is_absolute())
        self.assertUongo(P('a').is_absolute())
        self.assertUongo(P('a/b/').is_absolute())
        self.assertKweli(P('/').is_absolute())
        self.assertKweli(P('/a').is_absolute())
        self.assertKweli(P('/a/b/').is_absolute())
        self.assertKweli(P('//a').is_absolute())
        self.assertKweli(P('//a/b').is_absolute())

    eleza test_is_reserved(self):
        P = self.cls
        self.assertIs(Uongo, P('').is_reserved())
        self.assertIs(Uongo, P('/').is_reserved())
        self.assertIs(Uongo, P('/foo/bar').is_reserved())
        self.assertIs(Uongo, P('/dev/con/PRN/NUL').is_reserved())

    eleza test_join(self):
        P = self.cls
        p = P('//a')
        pp = p.joinpath('b')
        self.assertEqual(pp, P('//a/b'))
        pp = P('/a').joinpath('//c')
        self.assertEqual(pp, P('//c'))
        pp = P('//a').joinpath('/c')
        self.assertEqual(pp, P('/c'))

    eleza test_div(self):
        # Basically the same kama joinpath().
        P = self.cls
        p = P('//a')
        pp = p / 'b'
        self.assertEqual(pp, P('//a/b'))
        pp = P('/a') / '//c'
        self.assertEqual(pp, P('//c'))
        pp = P('//a') / '/c'
        self.assertEqual(pp, P('/c'))


kundi PureWindowsPathTest(_BasePurePathTest, unittest.TestCase):
    cls = pathlib.PureWindowsPath

    equivalences = _BasePurePathTest.equivalences.copy()
    equivalences.update({
        'c:a': [ ('c:', 'a'), ('c:', 'a/'), ('/', 'c:', 'a') ],
        'c:/a': [
            ('c:/', 'a'), ('c:', '/', 'a'), ('c:', '/a'),
            ('/z', 'c:/', 'a'), ('//x/y', 'c:/', 'a'),
            ],
        '//a/b/': [ ('//a/b',) ],
        '//a/b/c': [
            ('//a/b', 'c'), ('//a/b/', 'c'),
            ],
    })

    eleza test_str(self):
        p = self.cls('a/b/c')
        self.assertEqual(str(p), 'a\\b\\c')
        p = self.cls('c:/a/b/c')
        self.assertEqual(str(p), 'c:\\a\\b\\c')
        p = self.cls('//a/b')
        self.assertEqual(str(p), '\\\\a\\b\\')
        p = self.cls('//a/b/c')
        self.assertEqual(str(p), '\\\\a\\b\\c')
        p = self.cls('//a/b/c/d')
        self.assertEqual(str(p), '\\\\a\\b\\c\\d')

    eleza test_str_subclass(self):
        self._check_str_subclass('c:')
        self._check_str_subclass('c:a')
        self._check_str_subclass('c:a\\b.txt')
        self._check_str_subclass('c:\\')
        self._check_str_subclass('c:\\a')
        self._check_str_subclass('c:\\a\\b.txt')
        self._check_str_subclass('\\\\some\\share')
        self._check_str_subclass('\\\\some\\share\\a')
        self._check_str_subclass('\\\\some\\share\\a\\b.txt')

    eleza test_eq(self):
        P = self.cls
        self.assertEqual(P('c:a/b'), P('c:a/b'))
        self.assertEqual(P('c:a/b'), P('c:', 'a', 'b'))
        self.assertNotEqual(P('c:a/b'), P('d:a/b'))
        self.assertNotEqual(P('c:a/b'), P('c:/a/b'))
        self.assertNotEqual(P('/a/b'), P('c:/a/b'))
        # Case-insensitivity.
        self.assertEqual(P('a/B'), P('A/b'))
        self.assertEqual(P('C:a/B'), P('c:A/b'))
        self.assertEqual(P('//Some/SHARE/a/B'), P('//somE/share/A/b'))

    eleza test_as_uri(self):
        P = self.cls
        ukijumuisha self.assertRaises(ValueError):
            P('/a/b').as_uri()
        ukijumuisha self.assertRaises(ValueError):
            P('c:a/b').as_uri()
        self.assertEqual(P('c:/').as_uri(), 'file:///c:/')
        self.assertEqual(P('c:/a/b.c').as_uri(), 'file:///c:/a/b.c')
        self.assertEqual(P('c:/a/b%#c').as_uri(), 'file:///c:/a/b%25%23c')
        self.assertEqual(P('c:/a/b\xe9').as_uri(), 'file:///c:/a/b%C3%A9')
        self.assertEqual(P('//some/share/').as_uri(), 'file://some/share/')
        self.assertEqual(P('//some/share/a/b.c').as_uri(),
                         'file://some/share/a/b.c')
        self.assertEqual(P('//some/share/a/b%#c\xe9').as_uri(),
                         'file://some/share/a/b%25%23c%C3%A9')

    eleza test_match_common(self):
        P = self.cls
        # Absolute patterns.
        self.assertKweli(P('c:/b.py').match('/*.py'))
        self.assertKweli(P('c:/b.py').match('c:*.py'))
        self.assertKweli(P('c:/b.py').match('c:/*.py'))
        self.assertUongo(P('d:/b.py').match('c:/*.py'))  # wrong drive
        self.assertUongo(P('b.py').match('/*.py'))
        self.assertUongo(P('b.py').match('c:*.py'))
        self.assertUongo(P('b.py').match('c:/*.py'))
        self.assertUongo(P('c:b.py').match('/*.py'))
        self.assertUongo(P('c:b.py').match('c:/*.py'))
        self.assertUongo(P('/b.py').match('c:*.py'))
        self.assertUongo(P('/b.py').match('c:/*.py'))
        # UNC patterns.
        self.assertKweli(P('//some/share/a.py').match('/*.py'))
        self.assertKweli(P('//some/share/a.py').match('//some/share/*.py'))
        self.assertUongo(P('//other/share/a.py').match('//some/share/*.py'))
        self.assertUongo(P('//some/share/a/b.py').match('//some/share/*.py'))
        # Case-insensitivity.
        self.assertKweli(P('B.py').match('b.PY'))
        self.assertKweli(P('c:/a/B.Py').match('C:/A/*.pY'))
        self.assertKweli(P('//Some/Share/B.Py').match('//somE/sharE/*.pY'))

    eleza test_ordering_common(self):
        # Case-insensitivity.
        eleza assertOrderedEqual(a, b):
            self.assertLessEqual(a, b)
            self.assertGreaterEqual(b, a)
        P = self.cls
        p = P('c:A/b')
        q = P('C:a/B')
        assertOrderedEqual(p, q)
        self.assertUongo(p < q)
        self.assertUongo(p > q)
        p = P('//some/Share/A/b')
        q = P('//Some/SHARE/a/B')
        assertOrderedEqual(p, q)
        self.assertUongo(p < q)
        self.assertUongo(p > q)

    eleza test_parts(self):
        P = self.cls
        p = P('c:a/b')
        parts = p.parts
        self.assertEqual(parts, ('c:', 'a', 'b'))
        p = P('c:/a/b')
        parts = p.parts
        self.assertEqual(parts, ('c:\\', 'a', 'b'))
        p = P('//a/b/c/d')
        parts = p.parts
        self.assertEqual(parts, ('\\\\a\\b\\', 'c', 'd'))

    eleza test_parent(self):
        # Anchored
        P = self.cls
        p = P('z:a/b/c')
        self.assertEqual(p.parent, P('z:a/b'))
        self.assertEqual(p.parent.parent, P('z:a'))
        self.assertEqual(p.parent.parent.parent, P('z:'))
        self.assertEqual(p.parent.parent.parent.parent, P('z:'))
        p = P('z:/a/b/c')
        self.assertEqual(p.parent, P('z:/a/b'))
        self.assertEqual(p.parent.parent, P('z:/a'))
        self.assertEqual(p.parent.parent.parent, P('z:/'))
        self.assertEqual(p.parent.parent.parent.parent, P('z:/'))
        p = P('//a/b/c/d')
        self.assertEqual(p.parent, P('//a/b/c'))
        self.assertEqual(p.parent.parent, P('//a/b'))
        self.assertEqual(p.parent.parent.parent, P('//a/b'))

    eleza test_parents(self):
        # Anchored
        P = self.cls
        p = P('z:a/b/')
        par = p.parents
        self.assertEqual(len(par), 2)
        self.assertEqual(par[0], P('z:a'))
        self.assertEqual(par[1], P('z:'))
        self.assertEqual(list(par), [P('z:a'), P('z:')])
        ukijumuisha self.assertRaises(IndexError):
            par[2]
        p = P('z:/a/b/')
        par = p.parents
        self.assertEqual(len(par), 2)
        self.assertEqual(par[0], P('z:/a'))
        self.assertEqual(par[1], P('z:/'))
        self.assertEqual(list(par), [P('z:/a'), P('z:/')])
        ukijumuisha self.assertRaises(IndexError):
            par[2]
        p = P('//a/b/c/d')
        par = p.parents
        self.assertEqual(len(par), 2)
        self.assertEqual(par[0], P('//a/b/c'))
        self.assertEqual(par[1], P('//a/b'))
        self.assertEqual(list(par), [P('//a/b/c'), P('//a/b')])
        ukijumuisha self.assertRaises(IndexError):
            par[2]

    eleza test_drive(self):
        P = self.cls
        self.assertEqual(P('c:').drive, 'c:')
        self.assertEqual(P('c:a/b').drive, 'c:')
        self.assertEqual(P('c:/').drive, 'c:')
        self.assertEqual(P('c:/a/b/').drive, 'c:')
        self.assertEqual(P('//a/b').drive, '\\\\a\\b')
        self.assertEqual(P('//a/b/').drive, '\\\\a\\b')
        self.assertEqual(P('//a/b/c/d').drive, '\\\\a\\b')

    eleza test_root(self):
        P = self.cls
        self.assertEqual(P('c:').root, '')
        self.assertEqual(P('c:a/b').root, '')
        self.assertEqual(P('c:/').root, '\\')
        self.assertEqual(P('c:/a/b/').root, '\\')
        self.assertEqual(P('//a/b').root, '\\')
        self.assertEqual(P('//a/b/').root, '\\')
        self.assertEqual(P('//a/b/c/d').root, '\\')

    eleza test_anchor(self):
        P = self.cls
        self.assertEqual(P('c:').anchor, 'c:')
        self.assertEqual(P('c:a/b').anchor, 'c:')
        self.assertEqual(P('c:/').anchor, 'c:\\')
        self.assertEqual(P('c:/a/b/').anchor, 'c:\\')
        self.assertEqual(P('//a/b').anchor, '\\\\a\\b\\')
        self.assertEqual(P('//a/b/').anchor, '\\\\a\\b\\')
        self.assertEqual(P('//a/b/c/d').anchor, '\\\\a\\b\\')

    eleza test_name(self):
        P = self.cls
        self.assertEqual(P('c:').name, '')
        self.assertEqual(P('c:/').name, '')
        self.assertEqual(P('c:a/b').name, 'b')
        self.assertEqual(P('c:/a/b').name, 'b')
        self.assertEqual(P('c:a/b.py').name, 'b.py')
        self.assertEqual(P('c:/a/b.py').name, 'b.py')
        self.assertEqual(P('//My.py/Share.php').name, '')
        self.assertEqual(P('//My.py/Share.php/a/b').name, 'b')

    eleza test_suffix(self):
        P = self.cls
        self.assertEqual(P('c:').suffix, '')
        self.assertEqual(P('c:/').suffix, '')
        self.assertEqual(P('c:a/b').suffix, '')
        self.assertEqual(P('c:/a/b').suffix, '')
        self.assertEqual(P('c:a/b.py').suffix, '.py')
        self.assertEqual(P('c:/a/b.py').suffix, '.py')
        self.assertEqual(P('c:a/.hgrc').suffix, '')
        self.assertEqual(P('c:/a/.hgrc').suffix, '')
        self.assertEqual(P('c:a/.hg.rc').suffix, '.rc')
        self.assertEqual(P('c:/a/.hg.rc').suffix, '.rc')
        self.assertEqual(P('c:a/b.tar.gz').suffix, '.gz')
        self.assertEqual(P('c:/a/b.tar.gz').suffix, '.gz')
        self.assertEqual(P('c:a/Some name. Ending ukijumuisha a dot.').suffix, '')
        self.assertEqual(P('c:/a/Some name. Ending ukijumuisha a dot.').suffix, '')
        self.assertEqual(P('//My.py/Share.php').suffix, '')
        self.assertEqual(P('//My.py/Share.php/a/b').suffix, '')

    eleza test_suffixes(self):
        P = self.cls
        self.assertEqual(P('c:').suffixes, [])
        self.assertEqual(P('c:/').suffixes, [])
        self.assertEqual(P('c:a/b').suffixes, [])
        self.assertEqual(P('c:/a/b').suffixes, [])
        self.assertEqual(P('c:a/b.py').suffixes, ['.py'])
        self.assertEqual(P('c:/a/b.py').suffixes, ['.py'])
        self.assertEqual(P('c:a/.hgrc').suffixes, [])
        self.assertEqual(P('c:/a/.hgrc').suffixes, [])
        self.assertEqual(P('c:a/.hg.rc').suffixes, ['.rc'])
        self.assertEqual(P('c:/a/.hg.rc').suffixes, ['.rc'])
        self.assertEqual(P('c:a/b.tar.gz').suffixes, ['.tar', '.gz'])
        self.assertEqual(P('c:/a/b.tar.gz').suffixes, ['.tar', '.gz'])
        self.assertEqual(P('//My.py/Share.php').suffixes, [])
        self.assertEqual(P('//My.py/Share.php/a/b').suffixes, [])
        self.assertEqual(P('c:a/Some name. Ending ukijumuisha a dot.').suffixes, [])
        self.assertEqual(P('c:/a/Some name. Ending ukijumuisha a dot.').suffixes, [])

    eleza test_stem(self):
        P = self.cls
        self.assertEqual(P('c:').stem, '')
        self.assertEqual(P('c:.').stem, '')
        self.assertEqual(P('c:..').stem, '..')
        self.assertEqual(P('c:/').stem, '')
        self.assertEqual(P('c:a/b').stem, 'b')
        self.assertEqual(P('c:a/b.py').stem, 'b')
        self.assertEqual(P('c:a/.hgrc').stem, '.hgrc')
        self.assertEqual(P('c:a/.hg.rc').stem, '.hg')
        self.assertEqual(P('c:a/b.tar.gz').stem, 'b.tar')
        self.assertEqual(P('c:a/Some name. Ending ukijumuisha a dot.').stem,
                         'Some name. Ending ukijumuisha a dot.')

    eleza test_with_name(self):
        P = self.cls
        self.assertEqual(P('c:a/b').with_name('d.xml'), P('c:a/d.xml'))
        self.assertEqual(P('c:/a/b').with_name('d.xml'), P('c:/a/d.xml'))
        self.assertEqual(P('c:a/Dot ending.').with_name('d.xml'), P('c:a/d.xml'))
        self.assertEqual(P('c:/a/Dot ending.').with_name('d.xml'), P('c:/a/d.xml'))
        self.assertRaises(ValueError, P('c:').with_name, 'd.xml')
        self.assertRaises(ValueError, P('c:/').with_name, 'd.xml')
        self.assertRaises(ValueError, P('//My/Share').with_name, 'd.xml')
        self.assertRaises(ValueError, P('c:a/b').with_name, 'd:')
        self.assertRaises(ValueError, P('c:a/b').with_name, 'd:e')
        self.assertRaises(ValueError, P('c:a/b').with_name, 'd:/e')
        self.assertRaises(ValueError, P('c:a/b').with_name, '//My/Share')

    eleza test_with_suffix(self):
        P = self.cls
        self.assertEqual(P('c:a/b').with_suffix('.gz'), P('c:a/b.gz'))
        self.assertEqual(P('c:/a/b').with_suffix('.gz'), P('c:/a/b.gz'))
        self.assertEqual(P('c:a/b.py').with_suffix('.gz'), P('c:a/b.gz'))
        self.assertEqual(P('c:/a/b.py').with_suffix('.gz'), P('c:/a/b.gz'))
        # Path doesn't have a "filename" component.
        self.assertRaises(ValueError, P('').with_suffix, '.gz')
        self.assertRaises(ValueError, P('.').with_suffix, '.gz')
        self.assertRaises(ValueError, P('/').with_suffix, '.gz')
        self.assertRaises(ValueError, P('//My/Share').with_suffix, '.gz')
        # Invalid suffix.
        self.assertRaises(ValueError, P('c:a/b').with_suffix, 'gz')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, '/')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, '\\')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, 'c:')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, '/.gz')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, '\\.gz')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, 'c:.gz')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, 'c/d')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, 'c\\d')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, '.c/d')
        self.assertRaises(ValueError, P('c:a/b').with_suffix, '.c\\d')

    eleza test_relative_to(self):
        P = self.cls
        p = P('C:Foo/Bar')
        self.assertEqual(p.relative_to(P('c:')), P('Foo/Bar'))
        self.assertEqual(p.relative_to('c:'), P('Foo/Bar'))
        self.assertEqual(p.relative_to(P('c:foO')), P('Bar'))
        self.assertEqual(p.relative_to('c:foO'), P('Bar'))
        self.assertEqual(p.relative_to('c:foO/'), P('Bar'))
        self.assertEqual(p.relative_to(P('c:foO/baR')), P())
        self.assertEqual(p.relative_to('c:foO/baR'), P())
        # Unrelated paths.
        self.assertRaises(ValueError, p.relative_to, P())
        self.assertRaises(ValueError, p.relative_to, '')
        self.assertRaises(ValueError, p.relative_to, P('d:'))
        self.assertRaises(ValueError, p.relative_to, P('/'))
        self.assertRaises(ValueError, p.relative_to, P('Foo'))
        self.assertRaises(ValueError, p.relative_to, P('/Foo'))
        self.assertRaises(ValueError, p.relative_to, P('C:/Foo'))
        self.assertRaises(ValueError, p.relative_to, P('C:Foo/Bar/Baz'))
        self.assertRaises(ValueError, p.relative_to, P('C:Foo/Baz'))
        p = P('C:/Foo/Bar')
        self.assertEqual(p.relative_to(P('c:')), P('/Foo/Bar'))
        self.assertEqual(p.relative_to('c:'), P('/Foo/Bar'))
        self.assertEqual(str(p.relative_to(P('c:'))), '\\Foo\\Bar')
        self.assertEqual(str(p.relative_to('c:')), '\\Foo\\Bar')
        self.assertEqual(p.relative_to(P('c:/')), P('Foo/Bar'))
        self.assertEqual(p.relative_to('c:/'), P('Foo/Bar'))
        self.assertEqual(p.relative_to(P('c:/foO')), P('Bar'))
        self.assertEqual(p.relative_to('c:/foO'), P('Bar'))
        self.assertEqual(p.relative_to('c:/foO/'), P('Bar'))
        self.assertEqual(p.relative_to(P('c:/foO/baR')), P())
        self.assertEqual(p.relative_to('c:/foO/baR'), P())
        # Unrelated paths.
        self.assertRaises(ValueError, p.relative_to, P('C:/Baz'))
        self.assertRaises(ValueError, p.relative_to, P('C:/Foo/Bar/Baz'))
        self.assertRaises(ValueError, p.relative_to, P('C:/Foo/Baz'))
        self.assertRaises(ValueError, p.relative_to, P('C:Foo'))
        self.assertRaises(ValueError, p.relative_to, P('d:'))
        self.assertRaises(ValueError, p.relative_to, P('d:/'))
        self.assertRaises(ValueError, p.relative_to, P('/'))
        self.assertRaises(ValueError, p.relative_to, P('/Foo'))
        self.assertRaises(ValueError, p.relative_to, P('//C/Foo'))
        # UNC paths.
        p = P('//Server/Share/Foo/Bar')
        self.assertEqual(p.relative_to(P('//sErver/sHare')), P('Foo/Bar'))
        self.assertEqual(p.relative_to('//sErver/sHare'), P('Foo/Bar'))
        self.assertEqual(p.relative_to('//sErver/sHare/'), P('Foo/Bar'))
        self.assertEqual(p.relative_to(P('//sErver/sHare/Foo')), P('Bar'))
        self.assertEqual(p.relative_to('//sErver/sHare/Foo'), P('Bar'))
        self.assertEqual(p.relative_to('//sErver/sHare/Foo/'), P('Bar'))
        self.assertEqual(p.relative_to(P('//sErver/sHare/Foo/Bar')), P())
        self.assertEqual(p.relative_to('//sErver/sHare/Foo/Bar'), P())
        # Unrelated paths.
        self.assertRaises(ValueError, p.relative_to, P('/Server/Share/Foo'))
        self.assertRaises(ValueError, p.relative_to, P('c:/Server/Share/Foo'))
        self.assertRaises(ValueError, p.relative_to, P('//z/Share/Foo'))
        self.assertRaises(ValueError, p.relative_to, P('//Server/z/Foo'))

    eleza test_is_absolute(self):
        P = self.cls
        # Under NT, only paths ukijumuisha both a drive na a root are absolute.
        self.assertUongo(P().is_absolute())
        self.assertUongo(P('a').is_absolute())
        self.assertUongo(P('a/b/').is_absolute())
        self.assertUongo(P('/').is_absolute())
        self.assertUongo(P('/a').is_absolute())
        self.assertUongo(P('/a/b/').is_absolute())
        self.assertUongo(P('c:').is_absolute())
        self.assertUongo(P('c:a').is_absolute())
        self.assertUongo(P('c:a/b/').is_absolute())
        self.assertKweli(P('c:/').is_absolute())
        self.assertKweli(P('c:/a').is_absolute())
        self.assertKweli(P('c:/a/b/').is_absolute())
        # UNC paths are absolute by definition.
        self.assertKweli(P('//a/b').is_absolute())
        self.assertKweli(P('//a/b/').is_absolute())
        self.assertKweli(P('//a/b/c').is_absolute())
        self.assertKweli(P('//a/b/c/d').is_absolute())

    eleza test_join(self):
        P = self.cls
        p = P('C:/a/b')
        pp = p.joinpath('x/y')
        self.assertEqual(pp, P('C:/a/b/x/y'))
        pp = p.joinpath('/x/y')
        self.assertEqual(pp, P('C:/x/y'))
        # Joining ukijumuisha a different drive => the first path ni ignored, even
        # ikiwa the second path ni relative.
        pp = p.joinpath('D:x/y')
        self.assertEqual(pp, P('D:x/y'))
        pp = p.joinpath('D:/x/y')
        self.assertEqual(pp, P('D:/x/y'))
        pp = p.joinpath('//host/share/x/y')
        self.assertEqual(pp, P('//host/share/x/y'))
        # Joining ukijumuisha the same drive => the first path ni appended to if
        # the second path ni relative.
        pp = p.joinpath('c:x/y')
        self.assertEqual(pp, P('C:/a/b/x/y'))
        pp = p.joinpath('c:/x/y')
        self.assertEqual(pp, P('C:/x/y'))

    eleza test_div(self):
        # Basically the same kama joinpath().
        P = self.cls
        p = P('C:/a/b')
        self.assertEqual(p / 'x/y', P('C:/a/b/x/y'))
        self.assertEqual(p / 'x' / 'y', P('C:/a/b/x/y'))
        self.assertEqual(p / '/x/y', P('C:/x/y'))
        self.assertEqual(p / '/x' / 'y', P('C:/x/y'))
        # Joining ukijumuisha a different drive => the first path ni ignored, even
        # ikiwa the second path ni relative.
        self.assertEqual(p / 'D:x/y', P('D:x/y'))
        self.assertEqual(p / 'D:' / 'x/y', P('D:x/y'))
        self.assertEqual(p / 'D:/x/y', P('D:/x/y'))
        self.assertEqual(p / 'D:' / '/x/y', P('D:/x/y'))
        self.assertEqual(p / '//host/share/x/y', P('//host/share/x/y'))
        # Joining ukijumuisha the same drive => the first path ni appended to if
        # the second path ni relative.
        self.assertEqual(p / 'c:x/y', P('C:/a/b/x/y'))
        self.assertEqual(p / 'c:/x/y', P('C:/x/y'))

    eleza test_is_reserved(self):
        P = self.cls
        self.assertIs(Uongo, P('').is_reserved())
        self.assertIs(Uongo, P('/').is_reserved())
        self.assertIs(Uongo, P('/foo/bar').is_reserved())
        self.assertIs(Kweli, P('con').is_reserved())
        self.assertIs(Kweli, P('NUL').is_reserved())
        self.assertIs(Kweli, P('NUL.txt').is_reserved())
        self.assertIs(Kweli, P('com1').is_reserved())
        self.assertIs(Kweli, P('com9.bar').is_reserved())
        self.assertIs(Uongo, P('bar.com9').is_reserved())
        self.assertIs(Kweli, P('lpt1').is_reserved())
        self.assertIs(Kweli, P('lpt9.bar').is_reserved())
        self.assertIs(Uongo, P('bar.lpt9').is_reserved())
        # Only the last component matters.
        self.assertIs(Uongo, P('c:/NUL/con/baz').is_reserved())
        # UNC paths are never reserved.
        self.assertIs(Uongo, P('//my/share/nul/con/aux').is_reserved())

kundi PurePathTest(_BasePurePathTest, unittest.TestCase):
    cls = pathlib.PurePath

    eleza test_concrete_class(self):
        p = self.cls('a')
        self.assertIs(type(p),
            pathlib.PureWindowsPath ikiwa os.name == 'nt' isipokua pathlib.PurePosixPath)

    eleza test_different_flavours_unequal(self):
        p = pathlib.PurePosixPath('a')
        q = pathlib.PureWindowsPath('a')
        self.assertNotEqual(p, q)

    eleza test_different_flavours_unordered(self):
        p = pathlib.PurePosixPath('a')
        q = pathlib.PureWindowsPath('a')
        ukijumuisha self.assertRaises(TypeError):
            p < q
        ukijumuisha self.assertRaises(TypeError):
            p <= q
        ukijumuisha self.assertRaises(TypeError):
            p > q
        ukijumuisha self.assertRaises(TypeError):
            p >= q


#
# Tests kila the concrete classes.
#

# Make sure any symbolic links kwenye the base test path are resolved.
BASE = os.path.realpath(TESTFN)
join = lambda *x: os.path.join(BASE, *x)
rel_join = lambda *x: os.path.join(TESTFN, *x)

only_nt = unittest.skipIf(os.name != 'nt',
                          'test requires a Windows-compatible system')
only_posix = unittest.skipIf(os.name == 'nt',
                             'test requires a POSIX-compatible system')

@only_posix
kundi PosixPathAsPureTest(PurePosixPathTest):
    cls = pathlib.PosixPath

@only_nt
kundi WindowsPathAsPureTest(PureWindowsPathTest):
    cls = pathlib.WindowsPath

    eleza test_owner(self):
        P = self.cls
        ukijumuisha self.assertRaises(NotImplementedError):
            P('c:/').owner()

    eleza test_group(self):
        P = self.cls
        ukijumuisha self.assertRaises(NotImplementedError):
            P('c:/').group()


kundi _BasePathTest(object):
    """Tests kila the FS-accessing functionalities of the Path classes."""

    # (BASE)
    #  |
    #  |-- brokenLink -> non-existing
    #  |-- dirA
    #  |   `-- linkC -> ../dirB
    #  |-- dirB
    #  |   |-- fileB
    #  |   `-- linkD -> ../dirB
    #  |-- dirC
    #  |   |-- dirD
    #  |   |   `-- fileD
    #  |   `-- fileC
    #  |-- dirE  # No permissions
    #  |-- fileA
    #  |-- linkA -> fileA
    #  |-- linkB -> dirB
    #  `-- brokenLinkLoop -> brokenLinkLoop
    #

    eleza setUp(self):
        eleza cleanup():
            os.chmod(join('dirE'), 0o777)
            support.rmtree(BASE)
        self.addCleanup(cleanup)
        os.mkdir(BASE)
        os.mkdir(join('dirA'))
        os.mkdir(join('dirB'))
        os.mkdir(join('dirC'))
        os.mkdir(join('dirC', 'dirD'))
        os.mkdir(join('dirE'))
        ukijumuisha open(join('fileA'), 'wb') kama f:
            f.write(b"this ni file A\n")
        ukijumuisha open(join('dirB', 'fileB'), 'wb') kama f:
            f.write(b"this ni file B\n")
        ukijumuisha open(join('dirC', 'fileC'), 'wb') kama f:
            f.write(b"this ni file C\n")
        ukijumuisha open(join('dirC', 'dirD', 'fileD'), 'wb') kama f:
            f.write(b"this ni file D\n")
        os.chmod(join('dirE'), 0)
        ikiwa support.can_symlink():
            # Relative symlinks.
            os.symlink('fileA', join('linkA'))
            os.symlink('non-existing', join('brokenLink'))
            self.dirlink('dirB', join('linkB'))
            self.dirlink(os.path.join('..', 'dirB'), join('dirA', 'linkC'))
            # This one goes upwards, creating a loop.
            self.dirlink(os.path.join('..', 'dirB'), join('dirB', 'linkD'))
            # Broken symlink (pointing to itself).
            os.symlink('brokenLinkLoop',  join('brokenLinkLoop'))

    ikiwa os.name == 'nt':
        # Workaround kila http://bugs.python.org/issue13772.
        eleza dirlink(self, src, dest):
            os.symlink(src, dest, target_is_directory=Kweli)
    isipokua:
        eleza dirlink(self, src, dest):
            os.symlink(src, dest)

    eleza assertSame(self, path_a, path_b):
        self.assertKweli(os.path.samefile(str(path_a), str(path_b)),
                        "%r na %r don't point to the same file" %
                        (path_a, path_b))

    eleza assertFileNotFound(self, func, *args, **kwargs):
        ukijumuisha self.assertRaises(FileNotFoundError) kama cm:
            func(*args, **kwargs)
        self.assertEqual(cm.exception.errno, errno.ENOENT)

    eleza assertEqualNormCase(self, path_a, path_b):
        self.assertEqual(os.path.normcase(path_a), os.path.normcase(path_b))

    eleza _test_cwd(self, p):
        q = self.cls(os.getcwd())
        self.assertEqual(p, q)
        self.assertEqualNormCase(str(p), str(q))
        self.assertIs(type(p), type(q))
        self.assertKweli(p.is_absolute())

    eleza test_cwd(self):
        p = self.cls.cwd()
        self._test_cwd(p)

    eleza _test_home(self, p):
        q = self.cls(os.path.expanduser('~'))
        self.assertEqual(p, q)
        self.assertEqualNormCase(str(p), str(q))
        self.assertIs(type(p), type(q))
        self.assertKweli(p.is_absolute())

    eleza test_home(self):
        p = self.cls.home()
        self._test_home(p)

    eleza test_samefile(self):
        fileA_path = os.path.join(BASE, 'fileA')
        fileB_path = os.path.join(BASE, 'dirB', 'fileB')
        p = self.cls(fileA_path)
        pp = self.cls(fileA_path)
        q = self.cls(fileB_path)
        self.assertKweli(p.samefile(fileA_path))
        self.assertKweli(p.samefile(pp))
        self.assertUongo(p.samefile(fileB_path))
        self.assertUongo(p.samefile(q))
        # Test the non-existent file case
        non_existent = os.path.join(BASE, 'foo')
        r = self.cls(non_existent)
        self.assertRaises(FileNotFoundError, p.samefile, r)
        self.assertRaises(FileNotFoundError, p.samefile, non_existent)
        self.assertRaises(FileNotFoundError, r.samefile, p)
        self.assertRaises(FileNotFoundError, r.samefile, non_existent)
        self.assertRaises(FileNotFoundError, r.samefile, r)
        self.assertRaises(FileNotFoundError, r.samefile, non_existent)

    eleza test_empty_path(self):
        # The empty path points to '.'
        p = self.cls('')
        self.assertEqual(p.stat(), os.stat('.'))

    eleza test_expanduser_common(self):
        P = self.cls
        p = P('~')
        self.assertEqual(p.expanduser(), P(os.path.expanduser('~')))
        p = P('foo')
        self.assertEqual(p.expanduser(), p)
        p = P('/~')
        self.assertEqual(p.expanduser(), p)
        p = P('../~')
        self.assertEqual(p.expanduser(), p)
        p = P(P('').absolute().anchor) / '~'
        self.assertEqual(p.expanduser(), p)

    eleza test_exists(self):
        P = self.cls
        p = P(BASE)
        self.assertIs(Kweli, p.exists())
        self.assertIs(Kweli, (p / 'dirA').exists())
        self.assertIs(Kweli, (p / 'fileA').exists())
        self.assertIs(Uongo, (p / 'fileA' / 'bah').exists())
        ikiwa support.can_symlink():
            self.assertIs(Kweli, (p / 'linkA').exists())
            self.assertIs(Kweli, (p / 'linkB').exists())
            self.assertIs(Kweli, (p / 'linkB' / 'fileB').exists())
            self.assertIs(Uongo, (p / 'linkA' / 'bah').exists())
        self.assertIs(Uongo, (p / 'foo').exists())
        self.assertIs(Uongo, P('/xyzzy').exists())
        self.assertIs(Uongo, P(BASE + '\udfff').exists())
        self.assertIs(Uongo, P(BASE + '\x00').exists())

    eleza test_open_common(self):
        p = self.cls(BASE)
        ukijumuisha (p / 'fileA').open('r') kama f:
            self.assertIsInstance(f, io.TextIOBase)
            self.assertEqual(f.read(), "this ni file A\n")
        ukijumuisha (p / 'fileA').open('rb') kama f:
            self.assertIsInstance(f, io.BufferedIOBase)
            self.assertEqual(f.read().strip(), b"this ni file A")
        ukijumuisha (p / 'fileA').open('rb', buffering=0) kama f:
            self.assertIsInstance(f, io.RawIOBase)
            self.assertEqual(f.read().strip(), b"this ni file A")

    eleza test_read_write_bytes(self):
        p = self.cls(BASE)
        (p / 'fileA').write_bytes(b'abcdefg')
        self.assertEqual((p / 'fileA').read_bytes(), b'abcdefg')
        # Check that trying to write str does sio truncate the file.
        self.assertRaises(TypeError, (p / 'fileA').write_bytes, 'somestr')
        self.assertEqual((p / 'fileA').read_bytes(), b'abcdefg')

    eleza test_read_write_text(self):
        p = self.cls(BASE)
        (p / 'fileA').write_text('äbcdefg', encoding='latin-1')
        self.assertEqual((p / 'fileA').read_text(
            encoding='utf-8', errors='ignore'), 'bcdefg')
        # Check that trying to write bytes does sio truncate the file.
        self.assertRaises(TypeError, (p / 'fileA').write_text, b'somebytes')
        self.assertEqual((p / 'fileA').read_text(encoding='latin-1'), 'äbcdefg')

    eleza test_iterdir(self):
        P = self.cls
        p = P(BASE)
        it = p.iterdir()
        paths = set(it)
        expected = ['dirA', 'dirB', 'dirC', 'dirE', 'fileA']
        ikiwa support.can_symlink():
            expected += ['linkA', 'linkB', 'brokenLink', 'brokenLinkLoop']
        self.assertEqual(paths, { P(BASE, q) kila q kwenye expected })

    @support.skip_unless_symlink
    eleza test_iterdir_symlink(self):
        # __iter__ on a symlink to a directory.
        P = self.cls
        p = P(BASE, 'linkB')
        paths = set(p.iterdir())
        expected = { P(BASE, 'linkB', q) kila q kwenye ['fileB', 'linkD'] }
        self.assertEqual(paths, expected)

    eleza test_iterdir_nodir(self):
        # __iter__ on something that ni sio a directory.
        p = self.cls(BASE, 'fileA')
        ukijumuisha self.assertRaises(OSError) kama cm:
            next(p.iterdir())
        # ENOENT ama EINVAL under Windows, ENOTDIR otherwise
        # (see issue #12802).
        self.assertIn(cm.exception.errno, (errno.ENOTDIR,
                                           errno.ENOENT, errno.EINVAL))

    eleza test_glob_common(self):
        eleza _check(glob, expected):
            self.assertEqual(set(glob), { P(BASE, q) kila q kwenye expected })
        P = self.cls
        p = P(BASE)
        it = p.glob("fileA")
        self.assertIsInstance(it, collections.abc.Iterator)
        _check(it, ["fileA"])
        _check(p.glob("fileB"), [])
        _check(p.glob("dir*/file*"), ["dirB/fileB", "dirC/fileC"])
        ikiwa sio support.can_symlink():
            _check(p.glob("*A"), ['dirA', 'fileA'])
        isipokua:
            _check(p.glob("*A"), ['dirA', 'fileA', 'linkA'])
        ikiwa sio support.can_symlink():
            _check(p.glob("*B/*"), ['dirB/fileB'])
        isipokua:
            _check(p.glob("*B/*"), ['dirB/fileB', 'dirB/linkD',
                                    'linkB/fileB', 'linkB/linkD'])
        ikiwa sio support.can_symlink():
            _check(p.glob("*/fileB"), ['dirB/fileB'])
        isipokua:
            _check(p.glob("*/fileB"), ['dirB/fileB', 'linkB/fileB'])

    eleza test_rglob_common(self):
        eleza _check(glob, expected):
            self.assertEqual(set(glob), { P(BASE, q) kila q kwenye expected })
        P = self.cls
        p = P(BASE)
        it = p.rglob("fileA")
        self.assertIsInstance(it, collections.abc.Iterator)
        _check(it, ["fileA"])
        _check(p.rglob("fileB"), ["dirB/fileB"])
        _check(p.rglob("*/fileA"), [])
        ikiwa sio support.can_symlink():
            _check(p.rglob("*/fileB"), ["dirB/fileB"])
        isipokua:
            _check(p.rglob("*/fileB"), ["dirB/fileB", "dirB/linkD/fileB",
                                        "linkB/fileB", "dirA/linkC/fileB"])
        _check(p.rglob("file*"), ["fileA", "dirB/fileB",
                                  "dirC/fileC", "dirC/dirD/fileD"])
        p = P(BASE, "dirC")
        _check(p.rglob("file*"), ["dirC/fileC", "dirC/dirD/fileD"])
        _check(p.rglob("*/*"), ["dirC/dirD/fileD"])

    @support.skip_unless_symlink
    eleza test_rglob_symlink_loop(self):
        # Don't get fooled by symlink loops (Issue #26012).
        P = self.cls
        p = P(BASE)
        given = set(p.rglob('*'))
        expect = {'brokenLink',
                  'dirA', 'dirA/linkC',
                  'dirB', 'dirB/fileB', 'dirB/linkD',
                  'dirC', 'dirC/dirD', 'dirC/dirD/fileD', 'dirC/fileC',
                  'dirE',
                  'fileA',
                  'linkA',
                  'linkB',
                  'brokenLinkLoop',
                  }
        self.assertEqual(given, {p / x kila x kwenye expect})

    eleza test_glob_many_open_files(self):
        depth = 30
        P = self.cls
        base = P(BASE) / 'deep'
        p = P(base, *(['d']*depth))
        p.mkdir(parents=Kweli)
        pattern = '/'.join(['*'] * depth)
        iters = [base.glob(pattern) kila j kwenye range(100)]
        kila it kwenye iters:
            self.assertEqual(next(it), p)
        iters = [base.rglob('d') kila j kwenye range(100)]
        p = base
        kila i kwenye range(depth):
            p = p / 'd'
            kila it kwenye iters:
                self.assertEqual(next(it), p)

    eleza test_glob_dotdot(self):
        # ".." ni sio special kwenye globs.
        P = self.cls
        p = P(BASE)
        self.assertEqual(set(p.glob("..")), { P(BASE, "..") })
        self.assertEqual(set(p.glob("dirA/../file*")), { P(BASE, "dirA/../fileA") })
        self.assertEqual(set(p.glob("../xyzzy")), set())


    eleza _check_resolve(self, p, expected, strict=Kweli):
        q = p.resolve(strict)
        self.assertEqual(q, expected)

    # This can be used to check both relative na absolute resolutions.
    _check_resolve_relative = _check_resolve_absolute = _check_resolve

    @support.skip_unless_symlink
    eleza test_resolve_common(self):
        P = self.cls
        p = P(BASE, 'foo')
        ukijumuisha self.assertRaises(OSError) kama cm:
            p.resolve(strict=Kweli)
        self.assertEqual(cm.exception.errno, errno.ENOENT)
        # Non-strict
        self.assertEqualNormCase(str(p.resolve(strict=Uongo)),
                                 os.path.join(BASE, 'foo'))
        p = P(BASE, 'foo', 'in', 'spam')
        self.assertEqualNormCase(str(p.resolve(strict=Uongo)),
                                 os.path.join(BASE, 'foo', 'in', 'spam'))
        p = P(BASE, '..', 'foo', 'in', 'spam')
        self.assertEqualNormCase(str(p.resolve(strict=Uongo)),
                                 os.path.abspath(os.path.join('foo', 'in', 'spam')))
        # These are all relative symlinks.
        p = P(BASE, 'dirB', 'fileB')
        self._check_resolve_relative(p, p)
        p = P(BASE, 'linkA')
        self._check_resolve_relative(p, P(BASE, 'fileA'))
        p = P(BASE, 'dirA', 'linkC', 'fileB')
        self._check_resolve_relative(p, P(BASE, 'dirB', 'fileB'))
        p = P(BASE, 'dirB', 'linkD', 'fileB')
        self._check_resolve_relative(p, P(BASE, 'dirB', 'fileB'))
        # Non-strict
        p = P(BASE, 'dirA', 'linkC', 'fileB', 'foo', 'in', 'spam')
        self._check_resolve_relative(p, P(BASE, 'dirB', 'fileB', 'foo', 'in',
                                          'spam'), Uongo)
        p = P(BASE, 'dirA', 'linkC', '..', 'foo', 'in', 'spam')
        ikiwa os.name == 'nt':
            # In Windows, ikiwa linkY points to dirB, 'dirA\linkY\..'
            # resolves to 'dirA' without resolving linkY first.
            self._check_resolve_relative(p, P(BASE, 'dirA', 'foo', 'in',
                                              'spam'), Uongo)
        isipokua:
            # In Posix, ikiwa linkY points to dirB, 'dirA/linkY/..'
            # resolves to 'dirB/..' first before resolving to parent of dirB.
            self._check_resolve_relative(p, P(BASE, 'foo', 'in', 'spam'), Uongo)
        # Now create absolute symlinks.
        d = support._longpath(tempfile.mkdtemp(suffix='-dirD', dir=os.getcwd()))
        self.addCleanup(support.rmtree, d)
        os.symlink(os.path.join(d), join('dirA', 'linkX'))
        os.symlink(join('dirB'), os.path.join(d, 'linkY'))
        p = P(BASE, 'dirA', 'linkX', 'linkY', 'fileB')
        self._check_resolve_absolute(p, P(BASE, 'dirB', 'fileB'))
        # Non-strict
        p = P(BASE, 'dirA', 'linkX', 'linkY', 'foo', 'in', 'spam')
        self._check_resolve_relative(p, P(BASE, 'dirB', 'foo', 'in', 'spam'),
                                     Uongo)
        p = P(BASE, 'dirA', 'linkX', 'linkY', '..', 'foo', 'in', 'spam')
        ikiwa os.name == 'nt':
            # In Windows, ikiwa linkY points to dirB, 'dirA\linkY\..'
            # resolves to 'dirA' without resolving linkY first.
            self._check_resolve_relative(p, P(d, 'foo', 'in', 'spam'), Uongo)
        isipokua:
            # In Posix, ikiwa linkY points to dirB, 'dirA/linkY/..'
            # resolves to 'dirB/..' first before resolving to parent of dirB.
            self._check_resolve_relative(p, P(BASE, 'foo', 'in', 'spam'), Uongo)

    @support.skip_unless_symlink
    eleza test_resolve_dot(self):
        # See https://bitbucket.org/pitrou/pathlib/issue/9/pathresolve-fails-on-complex-symlinks
        p = self.cls(BASE)
        self.dirlink('.', join('0'))
        self.dirlink(os.path.join('0', '0'), join('1'))
        self.dirlink(os.path.join('1', '1'), join('2'))
        q = p / '2'
        self.assertEqual(q.resolve(strict=Kweli), p)
        r = q / '3' / '4'
        self.assertRaises(FileNotFoundError, r.resolve, strict=Kweli)
        # Non-strict
        self.assertEqual(r.resolve(strict=Uongo), p / '3' / '4')

    eleza test_with(self):
        p = self.cls(BASE)
        it = p.iterdir()
        it2 = p.iterdir()
        next(it2)
        ukijumuisha p:
            pita
        # I/O operation on closed path.
        self.assertRaises(ValueError, next, it)
        self.assertRaises(ValueError, next, it2)
        self.assertRaises(ValueError, p.open)
        self.assertRaises(ValueError, p.resolve)
        self.assertRaises(ValueError, p.absolute)
        self.assertRaises(ValueError, p.__enter__)

    eleza test_chmod(self):
        p = self.cls(BASE) / 'fileA'
        mode = p.stat().st_mode
        # Clear writable bit.
        new_mode = mode & ~0o222
        p.chmod(new_mode)
        self.assertEqual(p.stat().st_mode, new_mode)
        # Set writable bit.
        new_mode = mode | 0o222
        p.chmod(new_mode)
        self.assertEqual(p.stat().st_mode, new_mode)

    # XXX also need a test kila lchmod.

    eleza test_stat(self):
        p = self.cls(BASE) / 'fileA'
        st = p.stat()
        self.assertEqual(p.stat(), st)
        # Change file mode by flipping write bit.
        p.chmod(st.st_mode ^ 0o222)
        self.addCleanup(p.chmod, st.st_mode)
        self.assertNotEqual(p.stat(), st)

    @support.skip_unless_symlink
    eleza test_lstat(self):
        p = self.cls(BASE)/ 'linkA'
        st = p.stat()
        self.assertNotEqual(st, p.lstat())

    eleza test_lstat_nosymlink(self):
        p = self.cls(BASE) / 'fileA'
        st = p.stat()
        self.assertEqual(st, p.lstat())

    @unittest.skipUnless(pwd, "the pwd module ni needed kila this test")
    eleza test_owner(self):
        p = self.cls(BASE) / 'fileA'
        uid = p.stat().st_uid
        jaribu:
            name = pwd.getpwuid(uid).pw_name
        tatizo KeyError:
            self.skipTest(
                "user %d doesn't have an entry kwenye the system database" % uid)
        self.assertEqual(name, p.owner())

    @unittest.skipUnless(grp, "the grp module ni needed kila this test")
    eleza test_group(self):
        p = self.cls(BASE) / 'fileA'
        gid = p.stat().st_gid
        jaribu:
            name = grp.getgrgid(gid).gr_name
        tatizo KeyError:
            self.skipTest(
                "group %d doesn't have an entry kwenye the system database" % gid)
        self.assertEqual(name, p.group())

    eleza test_unlink(self):
        p = self.cls(BASE) / 'fileA'
        p.unlink()
        self.assertFileNotFound(p.stat)
        self.assertFileNotFound(p.unlink)

    eleza test_unlink_missing_ok(self):
        p = self.cls(BASE) / 'fileAAA'
        self.assertFileNotFound(p.unlink)
        p.unlink(missing_ok=Kweli)

    eleza test_rmdir(self):
        p = self.cls(BASE) / 'dirA'
        kila q kwenye p.iterdir():
            q.unlink()
        p.rmdir()
        self.assertFileNotFound(p.stat)
        self.assertFileNotFound(p.unlink)

    eleza test_link_to(self):
        P = self.cls(BASE)
        p = P / 'fileA'
        size = p.stat().st_size
        # linking to another path.
        q = P / 'dirA' / 'fileAA'
        jaribu:
            p.link_to(q)
        tatizo PermissionError kama e:
            self.skipTest('os.link(): %s' % e)
        self.assertEqual(q.stat().st_size, size)
        self.assertEqual(os.path.samefile(p, q), Kweli)
        self.assertKweli(p.stat)
        # Linking to a str of a relative path.
        r = rel_join('fileAAA')
        q.link_to(r)
        self.assertEqual(os.stat(r).st_size, size)
        self.assertKweli(q.stat)

    eleza test_rename(self):
        P = self.cls(BASE)
        p = P / 'fileA'
        size = p.stat().st_size
        # Renaming to another path.
        q = P / 'dirA' / 'fileAA'
        renamed_p = p.rename(q)
        self.assertEqual(renamed_p, q)
        self.assertEqual(q.stat().st_size, size)
        self.assertFileNotFound(p.stat)
        # Renaming to a str of a relative path.
        r = rel_join('fileAAA')
        renamed_q = q.rename(r)
        self.assertEqual(renamed_q, self.cls(r))
        self.assertEqual(os.stat(r).st_size, size)
        self.assertFileNotFound(q.stat)

    eleza test_replace(self):
        P = self.cls(BASE)
        p = P / 'fileA'
        size = p.stat().st_size
        # Replacing a non-existing path.
        q = P / 'dirA' / 'fileAA'
        replaced_p = p.replace(q)
        self.assertEqual(replaced_p, q)
        self.assertEqual(q.stat().st_size, size)
        self.assertFileNotFound(p.stat)
        # Replacing another (existing) path.
        r = rel_join('dirB', 'fileB')
        replaced_q = q.replace(r)
        self.assertEqual(replaced_q, self.cls(r))
        self.assertEqual(os.stat(r).st_size, size)
        self.assertFileNotFound(q.stat)

    eleza test_touch_common(self):
        P = self.cls(BASE)
        p = P / 'newfileA'
        self.assertUongo(p.exists())
        p.touch()
        self.assertKweli(p.exists())
        st = p.stat()
        old_mtime = st.st_mtime
        old_mtime_ns = st.st_mtime_ns
        # Rewind the mtime sufficiently far kwenye the past to work around
        # filesystem-specific timestamp granularity.
        os.utime(str(p), (old_mtime - 10, old_mtime - 10))
        # The file mtime should be refreshed by calling touch() again.
        p.touch()
        st = p.stat()
        self.assertGreaterEqual(st.st_mtime_ns, old_mtime_ns)
        self.assertGreaterEqual(st.st_mtime, old_mtime)
        # Now ukijumuisha exist_ok=Uongo.
        p = P / 'newfileB'
        self.assertUongo(p.exists())
        p.touch(mode=0o700, exist_ok=Uongo)
        self.assertKweli(p.exists())
        self.assertRaises(OSError, p.touch, exist_ok=Uongo)

    eleza test_touch_nochange(self):
        P = self.cls(BASE)
        p = P / 'fileA'
        p.touch()
        ukijumuisha p.open('rb') kama f:
            self.assertEqual(f.read().strip(), b"this ni file A")

    eleza test_mkdir(self):
        P = self.cls(BASE)
        p = P / 'newdirA'
        self.assertUongo(p.exists())
        p.mkdir()
        self.assertKweli(p.exists())
        self.assertKweli(p.is_dir())
        ukijumuisha self.assertRaises(OSError) kama cm:
            p.mkdir()
        self.assertEqual(cm.exception.errno, errno.EEXIST)

    eleza test_mkdir_parents(self):
        # Creating a chain of directories.
        p = self.cls(BASE, 'newdirB', 'newdirC')
        self.assertUongo(p.exists())
        ukijumuisha self.assertRaises(OSError) kama cm:
            p.mkdir()
        self.assertEqual(cm.exception.errno, errno.ENOENT)
        p.mkdir(parents=Kweli)
        self.assertKweli(p.exists())
        self.assertKweli(p.is_dir())
        ukijumuisha self.assertRaises(OSError) kama cm:
            p.mkdir(parents=Kweli)
        self.assertEqual(cm.exception.errno, errno.EEXIST)
        # Test `mode` arg.
        mode = stat.S_IMODE(p.stat().st_mode)  # Default mode.
        p = self.cls(BASE, 'newdirD', 'newdirE')
        p.mkdir(0o555, parents=Kweli)
        self.assertKweli(p.exists())
        self.assertKweli(p.is_dir())
        ikiwa os.name != 'nt':
            # The directory's permissions follow the mode argument.
            self.assertEqual(stat.S_IMODE(p.stat().st_mode), 0o7555 & mode)
        # The parent's permissions follow the default process settings.
        self.assertEqual(stat.S_IMODE(p.parent.stat().st_mode), mode)

    eleza test_mkdir_exist_ok(self):
        p = self.cls(BASE, 'dirB')
        st_ctime_first = p.stat().st_ctime
        self.assertKweli(p.exists())
        self.assertKweli(p.is_dir())
        ukijumuisha self.assertRaises(FileExistsError) kama cm:
            p.mkdir()
        self.assertEqual(cm.exception.errno, errno.EEXIST)
        p.mkdir(exist_ok=Kweli)
        self.assertKweli(p.exists())
        self.assertEqual(p.stat().st_ctime, st_ctime_first)

    eleza test_mkdir_exist_ok_with_parent(self):
        p = self.cls(BASE, 'dirC')
        self.assertKweli(p.exists())
        ukijumuisha self.assertRaises(FileExistsError) kama cm:
            p.mkdir()
        self.assertEqual(cm.exception.errno, errno.EEXIST)
        p = p / 'newdirC'
        p.mkdir(parents=Kweli)
        st_ctime_first = p.stat().st_ctime
        self.assertKweli(p.exists())
        ukijumuisha self.assertRaises(FileExistsError) kama cm:
            p.mkdir(parents=Kweli)
        self.assertEqual(cm.exception.errno, errno.EEXIST)
        p.mkdir(parents=Kweli, exist_ok=Kweli)
        self.assertKweli(p.exists())
        self.assertEqual(p.stat().st_ctime, st_ctime_first)

    eleza test_mkdir_exist_ok_root(self):
        # Issue #25803: A drive root could ashiria PermissionError on Windows.
        self.cls('/').resolve().mkdir(exist_ok=Kweli)
        self.cls('/').resolve().mkdir(parents=Kweli, exist_ok=Kweli)

    @only_nt  # XXX: sio sure how to test this on POSIX.
    eleza test_mkdir_with_unknown_drive(self):
        kila d kwenye 'ZYXWVUTSRQPONMLKJIHGFEDCBA':
            p = self.cls(d + ':\\')
            ikiwa sio p.is_dir():
                koma
        isipokua:
            self.skipTest("cannot find a drive that doesn't exist")
        ukijumuisha self.assertRaises(OSError):
            (p / 'child' / 'path').mkdir(parents=Kweli)

    eleza test_mkdir_with_child_file(self):
        p = self.cls(BASE, 'dirB', 'fileB')
        self.assertKweli(p.exists())
        # An exception ni raised when the last path component ni an existing
        # regular file, regardless of whether exist_ok ni true ama not.
        ukijumuisha self.assertRaises(FileExistsError) kama cm:
            p.mkdir(parents=Kweli)
        self.assertEqual(cm.exception.errno, errno.EEXIST)
        ukijumuisha self.assertRaises(FileExistsError) kama cm:
            p.mkdir(parents=Kweli, exist_ok=Kweli)
        self.assertEqual(cm.exception.errno, errno.EEXIST)

    eleza test_mkdir_no_parents_file(self):
        p = self.cls(BASE, 'fileA')
        self.assertKweli(p.exists())
        # An exception ni raised when the last path component ni an existing
        # regular file, regardless of whether exist_ok ni true ama not.
        ukijumuisha self.assertRaises(FileExistsError) kama cm:
            p.mkdir()
        self.assertEqual(cm.exception.errno, errno.EEXIST)
        ukijumuisha self.assertRaises(FileExistsError) kama cm:
            p.mkdir(exist_ok=Kweli)
        self.assertEqual(cm.exception.errno, errno.EEXIST)

    eleza test_mkdir_concurrent_parent_creation(self):
        kila pattern_num kwenye range(32):
            p = self.cls(BASE, 'dirCPC%d' % pattern_num)
            self.assertUongo(p.exists())

            eleza my_mkdir(path, mode=0o777):
                path = str(path)
                # Emulate another process that would create the directory
                # just before we try to create it ourselves.  We do it
                # kwenye all possible pattern combinations, assuming that this
                # function ni called at most 5 times (dirCPC/dir1/dir2,
                # dirCPC/dir1, dirCPC, dirCPC/dir1, dirCPC/dir1/dir2).
                ikiwa pattern.pop():
                    os.mkdir(path, mode)  # From another process.
                    concurrently_created.add(path)
                os.mkdir(path, mode)  # Our real call.

            pattern = [bool(pattern_num & (1 << n)) kila n kwenye range(5)]
            concurrently_created = set()
            p12 = p / 'dir1' / 'dir2'
            jaribu:
                ukijumuisha mock.patch("pathlib._normal_accessor.mkdir", my_mkdir):
                    p12.mkdir(parents=Kweli, exist_ok=Uongo)
            tatizo FileExistsError:
                self.assertIn(str(p12), concurrently_created)
            isipokua:
                self.assertNotIn(str(p12), concurrently_created)
            self.assertKweli(p.exists())

    @support.skip_unless_symlink
    eleza test_symlink_to(self):
        P = self.cls(BASE)
        target = P / 'fileA'
        # Symlinking a path target.
        link = P / 'dirA' / 'linkAA'
        link.symlink_to(target)
        self.assertEqual(link.stat(), target.stat())
        self.assertNotEqual(link.lstat(), target.stat())
        # Symlinking a str target.
        link = P / 'dirA' / 'linkAAA'
        link.symlink_to(str(target))
        self.assertEqual(link.stat(), target.stat())
        self.assertNotEqual(link.lstat(), target.stat())
        self.assertUongo(link.is_dir())
        # Symlinking to a directory.
        target = P / 'dirB'
        link = P / 'dirA' / 'linkAAAA'
        link.symlink_to(target, target_is_directory=Kweli)
        self.assertEqual(link.stat(), target.stat())
        self.assertNotEqual(link.lstat(), target.stat())
        self.assertKweli(link.is_dir())
        self.assertKweli(list(link.iterdir()))

    eleza test_is_dir(self):
        P = self.cls(BASE)
        self.assertKweli((P / 'dirA').is_dir())
        self.assertUongo((P / 'fileA').is_dir())
        self.assertUongo((P / 'non-existing').is_dir())
        self.assertUongo((P / 'fileA' / 'bah').is_dir())
        ikiwa support.can_symlink():
            self.assertUongo((P / 'linkA').is_dir())
            self.assertKweli((P / 'linkB').is_dir())
            self.assertUongo((P/ 'brokenLink').is_dir(), Uongo)
        self.assertIs((P / 'dirA\udfff').is_dir(), Uongo)
        self.assertIs((P / 'dirA\x00').is_dir(), Uongo)

    eleza test_is_file(self):
        P = self.cls(BASE)
        self.assertKweli((P / 'fileA').is_file())
        self.assertUongo((P / 'dirA').is_file())
        self.assertUongo((P / 'non-existing').is_file())
        self.assertUongo((P / 'fileA' / 'bah').is_file())
        ikiwa support.can_symlink():
            self.assertKweli((P / 'linkA').is_file())
            self.assertUongo((P / 'linkB').is_file())
            self.assertUongo((P/ 'brokenLink').is_file())
        self.assertIs((P / 'fileA\udfff').is_file(), Uongo)
        self.assertIs((P / 'fileA\x00').is_file(), Uongo)

    @only_posix
    eleza test_is_mount(self):
        P = self.cls(BASE)
        R = self.cls('/')  # TODO: Work out Windows.
        self.assertUongo((P / 'fileA').is_mount())
        self.assertUongo((P / 'dirA').is_mount())
        self.assertUongo((P / 'non-existing').is_mount())
        self.assertUongo((P / 'fileA' / 'bah').is_mount())
        self.assertKweli(R.is_mount())
        ikiwa support.can_symlink():
            self.assertUongo((P / 'linkA').is_mount())
        self.assertIs(self.cls('/\udfff').is_mount(), Uongo)
        self.assertIs(self.cls('/\x00').is_mount(), Uongo)

    eleza test_is_symlink(self):
        P = self.cls(BASE)
        self.assertUongo((P / 'fileA').is_symlink())
        self.assertUongo((P / 'dirA').is_symlink())
        self.assertUongo((P / 'non-existing').is_symlink())
        self.assertUongo((P / 'fileA' / 'bah').is_symlink())
        ikiwa support.can_symlink():
            self.assertKweli((P / 'linkA').is_symlink())
            self.assertKweli((P / 'linkB').is_symlink())
            self.assertKweli((P/ 'brokenLink').is_symlink())
        self.assertIs((P / 'fileA\udfff').is_file(), Uongo)
        self.assertIs((P / 'fileA\x00').is_file(), Uongo)
        ikiwa support.can_symlink():
            self.assertIs((P / 'linkA\udfff').is_file(), Uongo)
            self.assertIs((P / 'linkA\x00').is_file(), Uongo)

    eleza test_is_fifo_false(self):
        P = self.cls(BASE)
        self.assertUongo((P / 'fileA').is_fifo())
        self.assertUongo((P / 'dirA').is_fifo())
        self.assertUongo((P / 'non-existing').is_fifo())
        self.assertUongo((P / 'fileA' / 'bah').is_fifo())
        self.assertIs((P / 'fileA\udfff').is_fifo(), Uongo)
        self.assertIs((P / 'fileA\x00').is_fifo(), Uongo)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "os.mkfifo() required")
    eleza test_is_fifo_true(self):
        P = self.cls(BASE, 'myfifo')
        jaribu:
            os.mkfifo(str(P))
        tatizo PermissionError kama e:
            self.skipTest('os.mkfifo(): %s' % e)
        self.assertKweli(P.is_fifo())
        self.assertUongo(P.is_socket())
        self.assertUongo(P.is_file())
        self.assertIs(self.cls(BASE, 'myfifo\udfff').is_fifo(), Uongo)
        self.assertIs(self.cls(BASE, 'myfifo\x00').is_fifo(), Uongo)

    eleza test_is_socket_false(self):
        P = self.cls(BASE)
        self.assertUongo((P / 'fileA').is_socket())
        self.assertUongo((P / 'dirA').is_socket())
        self.assertUongo((P / 'non-existing').is_socket())
        self.assertUongo((P / 'fileA' / 'bah').is_socket())
        self.assertIs((P / 'fileA\udfff').is_socket(), Uongo)
        self.assertIs((P / 'fileA\x00').is_socket(), Uongo)

    @unittest.skipUnless(hasattr(socket, "AF_UNIX"), "Unix sockets required")
    eleza test_is_socket_true(self):
        P = self.cls(BASE, 'mysock')
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.addCleanup(sock.close)
        jaribu:
            sock.bind(str(P))
        tatizo OSError kama e:
            ikiwa (isinstance(e, PermissionError) ama
                    "AF_UNIX path too long" kwenye str(e)):
                self.skipTest("cannot bind Unix socket: " + str(e))
        self.assertKweli(P.is_socket())
        self.assertUongo(P.is_fifo())
        self.assertUongo(P.is_file())
        self.assertIs(self.cls(BASE, 'mysock\udfff').is_socket(), Uongo)
        self.assertIs(self.cls(BASE, 'mysock\x00').is_socket(), Uongo)

    eleza test_is_block_device_false(self):
        P = self.cls(BASE)
        self.assertUongo((P / 'fileA').is_block_device())
        self.assertUongo((P / 'dirA').is_block_device())
        self.assertUongo((P / 'non-existing').is_block_device())
        self.assertUongo((P / 'fileA' / 'bah').is_block_device())
        self.assertIs((P / 'fileA\udfff').is_block_device(), Uongo)
        self.assertIs((P / 'fileA\x00').is_block_device(), Uongo)

    eleza test_is_char_device_false(self):
        P = self.cls(BASE)
        self.assertUongo((P / 'fileA').is_char_device())
        self.assertUongo((P / 'dirA').is_char_device())
        self.assertUongo((P / 'non-existing').is_char_device())
        self.assertUongo((P / 'fileA' / 'bah').is_char_device())
        self.assertIs((P / 'fileA\udfff').is_char_device(), Uongo)
        self.assertIs((P / 'fileA\x00').is_char_device(), Uongo)

    eleza test_is_char_device_true(self):
        # Under Unix, /dev/null should generally be a char device.
        P = self.cls('/dev/null')
        ikiwa sio P.exists():
            self.skipTest("/dev/null required")
        self.assertKweli(P.is_char_device())
        self.assertUongo(P.is_block_device())
        self.assertUongo(P.is_file())
        self.assertIs(self.cls('/dev/null\udfff').is_char_device(), Uongo)
        self.assertIs(self.cls('/dev/null\x00').is_char_device(), Uongo)

    eleza test_pickling_common(self):
        p = self.cls(BASE, 'fileA')
        kila proto kwenye range(0, pickle.HIGHEST_PROTOCOL + 1):
            dumped = pickle.dumps(p, proto)
            pp = pickle.loads(dumped)
            self.assertEqual(pp.stat(), p.stat())

    eleza test_parts_interning(self):
        P = self.cls
        p = P('/usr/bin/foo')
        q = P('/usr/local/bin')
        # 'usr'
        self.assertIs(p.parts[1], q.parts[1])
        # 'bin'
        self.assertIs(p.parts[2], q.parts[3])

    eleza _check_complex_symlinks(self, link0_target):
        # Test solving a non-looping chain of symlinks (issue #19887).
        P = self.cls(BASE)
        self.dirlink(os.path.join('link0', 'link0'), join('link1'))
        self.dirlink(os.path.join('link1', 'link1'), join('link2'))
        self.dirlink(os.path.join('link2', 'link2'), join('link3'))
        self.dirlink(link0_target, join('link0'))

        # Resolve absolute paths.
        p = (P / 'link0').resolve()
        self.assertEqual(p, P)
        self.assertEqualNormCase(str(p), BASE)
        p = (P / 'link1').resolve()
        self.assertEqual(p, P)
        self.assertEqualNormCase(str(p), BASE)
        p = (P / 'link2').resolve()
        self.assertEqual(p, P)
        self.assertEqualNormCase(str(p), BASE)
        p = (P / 'link3').resolve()
        self.assertEqual(p, P)
        self.assertEqualNormCase(str(p), BASE)

        # Resolve relative paths.
        old_path = os.getcwd()
        os.chdir(BASE)
        jaribu:
            p = self.cls('link0').resolve()
            self.assertEqual(p, P)
            self.assertEqualNormCase(str(p), BASE)
            p = self.cls('link1').resolve()
            self.assertEqual(p, P)
            self.assertEqualNormCase(str(p), BASE)
            p = self.cls('link2').resolve()
            self.assertEqual(p, P)
            self.assertEqualNormCase(str(p), BASE)
            p = self.cls('link3').resolve()
            self.assertEqual(p, P)
            self.assertEqualNormCase(str(p), BASE)
        mwishowe:
            os.chdir(old_path)

    @support.skip_unless_symlink
    eleza test_complex_symlinks_absolute(self):
        self._check_complex_symlinks(BASE)

    @support.skip_unless_symlink
    eleza test_complex_symlinks_relative(self):
        self._check_complex_symlinks('.')

    @support.skip_unless_symlink
    eleza test_complex_symlinks_relative_dot_dot(self):
        self._check_complex_symlinks(os.path.join('dirA', '..'))


kundi PathTest(_BasePathTest, unittest.TestCase):
    cls = pathlib.Path

    eleza test_concrete_class(self):
        p = self.cls('a')
        self.assertIs(type(p),
            pathlib.WindowsPath ikiwa os.name == 'nt' isipokua pathlib.PosixPath)

    eleza test_unsupported_flavour(self):
        ikiwa os.name == 'nt':
            self.assertRaises(NotImplementedError, pathlib.PosixPath)
        isipokua:
            self.assertRaises(NotImplementedError, pathlib.WindowsPath)

    eleza test_glob_empty_pattern(self):
        p = self.cls()
        ukijumuisha self.assertRaisesRegex(ValueError, 'Unacceptable pattern'):
            list(p.glob(''))


@only_posix
kundi PosixPathTest(_BasePathTest, unittest.TestCase):
    cls = pathlib.PosixPath

    eleza _check_symlink_loop(self, *args, strict=Kweli):
        path = self.cls(*args)
        ukijumuisha self.assertRaises(RuntimeError):
            andika(path.resolve(strict))

    eleza test_open_mode(self):
        old_mask = os.umask(0)
        self.addCleanup(os.umask, old_mask)
        p = self.cls(BASE)
        ukijumuisha (p / 'new_file').open('wb'):
            pita
        st = os.stat(join('new_file'))
        self.assertEqual(stat.S_IMODE(st.st_mode), 0o666)
        os.umask(0o022)
        ukijumuisha (p / 'other_new_file').open('wb'):
            pita
        st = os.stat(join('other_new_file'))
        self.assertEqual(stat.S_IMODE(st.st_mode), 0o644)

    eleza test_touch_mode(self):
        old_mask = os.umask(0)
        self.addCleanup(os.umask, old_mask)
        p = self.cls(BASE)
        (p / 'new_file').touch()
        st = os.stat(join('new_file'))
        self.assertEqual(stat.S_IMODE(st.st_mode), 0o666)
        os.umask(0o022)
        (p / 'other_new_file').touch()
        st = os.stat(join('other_new_file'))
        self.assertEqual(stat.S_IMODE(st.st_mode), 0o644)
        (p / 'masked_new_file').touch(mode=0o750)
        st = os.stat(join('masked_new_file'))
        self.assertEqual(stat.S_IMODE(st.st_mode), 0o750)

    @support.skip_unless_symlink
    eleza test_resolve_loop(self):
        # Loops ukijumuisha relative symlinks.
        os.symlink('linkX/inside', join('linkX'))
        self._check_symlink_loop(BASE, 'linkX')
        os.symlink('linkY', join('linkY'))
        self._check_symlink_loop(BASE, 'linkY')
        os.symlink('linkZ/../linkZ', join('linkZ'))
        self._check_symlink_loop(BASE, 'linkZ')
        # Non-strict
        self._check_symlink_loop(BASE, 'linkZ', 'foo', strict=Uongo)
        # Loops ukijumuisha absolute symlinks.
        os.symlink(join('linkU/inside'), join('linkU'))
        self._check_symlink_loop(BASE, 'linkU')
        os.symlink(join('linkV'), join('linkV'))
        self._check_symlink_loop(BASE, 'linkV')
        os.symlink(join('linkW/../linkW'), join('linkW'))
        self._check_symlink_loop(BASE, 'linkW')
        # Non-strict
        self._check_symlink_loop(BASE, 'linkW', 'foo', strict=Uongo)

    eleza test_glob(self):
        P = self.cls
        p = P(BASE)
        given = set(p.glob("FILEa"))
        expect = set() ikiwa sio support.fs_is_case_insensitive(BASE) isipokua given
        self.assertEqual(given, expect)
        self.assertEqual(set(p.glob("FILEa*")), set())

    eleza test_rglob(self):
        P = self.cls
        p = P(BASE, "dirC")
        given = set(p.rglob("FILEd"))
        expect = set() ikiwa sio support.fs_is_case_insensitive(BASE) isipokua given
        self.assertEqual(given, expect)
        self.assertEqual(set(p.rglob("FILEd*")), set())

    @unittest.skipUnless(hasattr(pwd, 'getpwall'),
                         'pwd module does sio expose getpwall()')
    eleza test_expanduser(self):
        P = self.cls
        support.import_module('pwd')
        agiza pwd
        pwdent = pwd.getpwuid(os.getuid())
        username = pwdent.pw_name
        userhome = pwdent.pw_dir.rstrip('/') ama '/'
        # Find arbitrary different user (ikiwa exists).
        kila pwdent kwenye pwd.getpwall():
            othername = pwdent.pw_name
            otherhome = pwdent.pw_dir.rstrip('/')
            ikiwa othername != username na otherhome:
                koma
        isipokua:
            othername = username
            otherhome = userhome

        p1 = P('~/Documents')
        p2 = P('~' + username + '/Documents')
        p3 = P('~' + othername + '/Documents')
        p4 = P('../~' + username + '/Documents')
        p5 = P('/~' + username + '/Documents')
        p6 = P('')
        p7 = P('~fakeuser/Documents')

        ukijumuisha support.EnvironmentVarGuard() kama env:
            env.pop('HOME', Tupu)

            self.assertEqual(p1.expanduser(), P(userhome) / 'Documents')
            self.assertEqual(p2.expanduser(), P(userhome) / 'Documents')
            self.assertEqual(p3.expanduser(), P(otherhome) / 'Documents')
            self.assertEqual(p4.expanduser(), p4)
            self.assertEqual(p5.expanduser(), p5)
            self.assertEqual(p6.expanduser(), p6)
            self.assertRaises(RuntimeError, p7.expanduser)

            env['HOME'] = '/tmp'
            self.assertEqual(p1.expanduser(), P('/tmp/Documents'))
            self.assertEqual(p2.expanduser(), P(userhome) / 'Documents')
            self.assertEqual(p3.expanduser(), P(otherhome) / 'Documents')
            self.assertEqual(p4.expanduser(), p4)
            self.assertEqual(p5.expanduser(), p5)
            self.assertEqual(p6.expanduser(), p6)
            self.assertRaises(RuntimeError, p7.expanduser)

    @unittest.skipIf(sys.platform != "darwin",
                     "Bad file descriptor kwenye /dev/fd affects only macOS")
    eleza test_handling_bad_descriptor(self):
        jaribu:
            file_descriptors = list(pathlib.Path('/dev/fd').rglob("*"))[3:]
            ikiwa sio file_descriptors:
                self.skipTest("no file descriptors - issue was sio reproduced")
            # Checking all file descriptors because there ni no guarantee
            # which one will fail.
            kila f kwenye file_descriptors:
                f.exists()
                f.is_dir()
                f.is_file()
                f.is_symlink()
                f.is_block_device()
                f.is_char_device()
                f.is_fifo()
                f.is_socket()
        tatizo OSError kama e:
            ikiwa e.errno == errno.EBADF:
                self.fail("Bad file descriptor sio handled.")
            raise


@only_nt
kundi WindowsPathTest(_BasePathTest, unittest.TestCase):
    cls = pathlib.WindowsPath

    eleza test_glob(self):
        P = self.cls
        p = P(BASE)
        self.assertEqual(set(p.glob("FILEa")), { P(BASE, "fileA") })

    eleza test_rglob(self):
        P = self.cls
        p = P(BASE, "dirC")
        self.assertEqual(set(p.rglob("FILEd")), { P(BASE, "dirC/dirD/fileD") })

    eleza test_expanduser(self):
        P = self.cls
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env.pop('HOME', Tupu)
            env.pop('USERPROFILE', Tupu)
            env.pop('HOMEPATH', Tupu)
            env.pop('HOMEDRIVE', Tupu)
            env['USERNAME'] = 'alice'

            # test that the path returns unchanged
            p1 = P('~/My Documents')
            p2 = P('~alice/My Documents')
            p3 = P('~bob/My Documents')
            p4 = P('/~/My Documents')
            p5 = P('d:~/My Documents')
            p6 = P('')
            self.assertRaises(RuntimeError, p1.expanduser)
            self.assertRaises(RuntimeError, p2.expanduser)
            self.assertRaises(RuntimeError, p3.expanduser)
            self.assertEqual(p4.expanduser(), p4)
            self.assertEqual(p5.expanduser(), p5)
            self.assertEqual(p6.expanduser(), p6)

            eleza check():
                env.pop('USERNAME', Tupu)
                self.assertEqual(p1.expanduser(),
                                 P('C:/Users/alice/My Documents'))
                self.assertRaises(KeyError, p2.expanduser)
                env['USERNAME'] = 'alice'
                self.assertEqual(p2.expanduser(),
                                 P('C:/Users/alice/My Documents'))
                self.assertEqual(p3.expanduser(),
                                 P('C:/Users/bob/My Documents'))
                self.assertEqual(p4.expanduser(), p4)
                self.assertEqual(p5.expanduser(), p5)
                self.assertEqual(p6.expanduser(), p6)

            # Test the first lookup key kwenye the env vars.
            env['HOME'] = 'C:\\Users\\alice'
            check()

            # Test that HOMEPATH ni available instead.
            env.pop('HOME', Tupu)
            env['HOMEPATH'] = 'C:\\Users\\alice'
            check()

            env['HOMEDRIVE'] = 'C:\\'
            env['HOMEPATH'] = 'Users\\alice'
            check()

            env.pop('HOMEDRIVE', Tupu)
            env.pop('HOMEPATH', Tupu)
            env['USERPROFILE'] = 'C:\\Users\\alice'
            check()


kundi CompatiblePathTest(unittest.TestCase):
    """
    Test that a type can be made compatible ukijumuisha PurePath
    derivatives by implementing division operator overloads.
    """

    kundi CompatPath:
        """
        Minimum viable kundi to test PurePath compatibility.
        Simply uses the division operator to join a given
        string na the string value of another object with
        a forward slash.
        """
        eleza __init__(self, string):
            self.string = string

        eleza __truediv__(self, other):
            rudisha type(self)(f"{self.string}/{other}")

        eleza __rtruediv__(self, other):
            rudisha type(self)(f"{other}/{self.string}")

    eleza test_truediv(self):
        result = pathlib.PurePath("test") / self.CompatPath("right")
        self.assertIsInstance(result, self.CompatPath)
        self.assertEqual(result.string, "test/right")

        ukijumuisha self.assertRaises(TypeError):
            # Verify improper operations still ashiria a TypeError
            pathlib.PurePath("test") / 10

    eleza test_rtruediv(self):
        result = self.CompatPath("left") / pathlib.PurePath("test")
        self.assertIsInstance(result, self.CompatPath)
        self.assertEqual(result.string, "left/test")

        ukijumuisha self.assertRaises(TypeError):
            # Verify improper operations still ashiria a TypeError
            10 / pathlib.PurePath("test")


ikiwa __name__ == "__main__":
    unittest.main()
