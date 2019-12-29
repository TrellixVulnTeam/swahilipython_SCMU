"""
  Test cases kila the repr module
  Nick Mathewson
"""

agiza sys
agiza os
agiza shutil
agiza importlib
agiza importlib.util
agiza unittest

kutoka test.support agiza create_empty_file, verbose
kutoka reprlib agiza repr kama r # Don't shadow builtin repr
kutoka reprlib agiza Repr
kutoka reprlib agiza recursive_repr


eleza nestedTuple(nesting):
    t = ()
    kila i kwenye range(nesting):
        t = (t,)
    rudisha t

kundi ReprTests(unittest.TestCase):

    eleza test_string(self):
        eq = self.assertEqual
        eq(r("abc"), "'abc'")
        eq(r("abcdefghijklmnop"),"'abcdefghijklmnop'")

        s = "a"*30+"b"*30
        expected = repr(s)[:13] + "..." + repr(s)[-14:]
        eq(r(s), expected)

        eq(r("\"'"), repr("\"'"))
        s = "\""*30+"'"*100
        expected = repr(s)[:13] + "..." + repr(s)[-14:]
        eq(r(s), expected)

    eleza test_tuple(self):
        eq = self.assertEqual
        eq(r((1,)), "(1,)")

        t3 = (1, 2, 3)
        eq(r(t3), "(1, 2, 3)")

        r2 = Repr()
        r2.maxtuple = 2
        expected = repr(t3)[:-2] + "...)"
        eq(r2.repr(t3), expected)

    eleza test_container(self):
        kutoka array agiza array
        kutoka collections agiza deque

        eq = self.assertEqual
        # Tuples give up after 6 elements
        eq(r(()), "()")
        eq(r((1,)), "(1,)")
        eq(r((1, 2, 3)), "(1, 2, 3)")
        eq(r((1, 2, 3, 4, 5, 6)), "(1, 2, 3, 4, 5, 6)")
        eq(r((1, 2, 3, 4, 5, 6, 7)), "(1, 2, 3, 4, 5, 6, ...)")

        # Lists give up after 6 kama well
        eq(r([]), "[]")
        eq(r([1]), "[1]")
        eq(r([1, 2, 3]), "[1, 2, 3]")
        eq(r([1, 2, 3, 4, 5, 6]), "[1, 2, 3, 4, 5, 6]")
        eq(r([1, 2, 3, 4, 5, 6, 7]), "[1, 2, 3, 4, 5, 6, ...]")

        # Sets give up after 6 kama well
        eq(r(set([])), "set()")
        eq(r(set([1])), "{1}")
        eq(r(set([1, 2, 3])), "{1, 2, 3}")
        eq(r(set([1, 2, 3, 4, 5, 6])), "{1, 2, 3, 4, 5, 6}")
        eq(r(set([1, 2, 3, 4, 5, 6, 7])), "{1, 2, 3, 4, 5, 6, ...}")

        # Frozensets give up after 6 kama well
        eq(r(frozenset([])), "frozenset()")
        eq(r(frozenset([1])), "frozenset({1})")
        eq(r(frozenset([1, 2, 3])), "frozenset({1, 2, 3})")
        eq(r(frozenset([1, 2, 3, 4, 5, 6])), "frozenset({1, 2, 3, 4, 5, 6})")
        eq(r(frozenset([1, 2, 3, 4, 5, 6, 7])), "frozenset({1, 2, 3, 4, 5, 6, ...})")

        # collections.deque after 6
        eq(r(deque([1, 2, 3, 4, 5, 6, 7])), "deque([1, 2, 3, 4, 5, 6, ...])")

        # Dictionaries give up after 4.
        eq(r({}), "{}")
        d = {'alice': 1, 'bob': 2, 'charles': 3, 'dave': 4}
        eq(r(d), "{'alice': 1, 'bob': 2, 'charles': 3, 'dave': 4}")
        d['arthur'] = 1
        eq(r(d), "{'alice': 1, 'arthur': 1, 'bob': 2, 'charles': 3, ...}")

        # array.array after 5.
        eq(r(array('i')), "array('i')")
        eq(r(array('i', [1])), "array('i', [1])")
        eq(r(array('i', [1, 2])), "array('i', [1, 2])")
        eq(r(array('i', [1, 2, 3])), "array('i', [1, 2, 3])")
        eq(r(array('i', [1, 2, 3, 4])), "array('i', [1, 2, 3, 4])")
        eq(r(array('i', [1, 2, 3, 4, 5])), "array('i', [1, 2, 3, 4, 5])")
        eq(r(array('i', [1, 2, 3, 4, 5, 6])),
                   "array('i', [1, 2, 3, 4, 5, ...])")

    eleza test_set_literal(self):
        eq = self.assertEqual
        eq(r({1}), "{1}")
        eq(r({1, 2, 3}), "{1, 2, 3}")
        eq(r({1, 2, 3, 4, 5, 6}), "{1, 2, 3, 4, 5, 6}")
        eq(r({1, 2, 3, 4, 5, 6, 7}), "{1, 2, 3, 4, 5, 6, ...}")

    eleza test_frozenset(self):
        eq = self.assertEqual
        eq(r(frozenset({1})), "frozenset({1})")
        eq(r(frozenset({1, 2, 3})), "frozenset({1, 2, 3})")
        eq(r(frozenset({1, 2, 3, 4, 5, 6})), "frozenset({1, 2, 3, 4, 5, 6})")
        eq(r(frozenset({1, 2, 3, 4, 5, 6, 7})), "frozenset({1, 2, 3, 4, 5, 6, ...})")

    eleza test_numbers(self):
        eq = self.assertEqual
        eq(r(123), repr(123))
        eq(r(123), repr(123))
        eq(r(1.0/3), repr(1.0/3))

        n = 10**100
        expected = repr(n)[:18] + "..." + repr(n)[-19:]
        eq(r(n), expected)

    eleza test_instance(self):
        eq = self.assertEqual
        i1 = ClassWithRepr("a")
        eq(r(i1), repr(i1))

        i2 = ClassWithRepr("x"*1000)
        expected = repr(i2)[:13] + "..." + repr(i2)[-14:]
        eq(r(i2), expected)

        i3 = ClassWithFailingRepr()
        eq(r(i3), ("<ClassWithFailingRepr instance at %#x>"%id(i3)))

        s = r(ClassWithFailingRepr)
        self.assertKweli(s.startswith("<kundi "))
        self.assertKweli(s.endswith(">"))
        self.assertIn(s.find("..."), [12, 13])

    eleza test_lambda(self):
        r = repr(lambda x: x)
        self.assertKweli(r.startswith("<function ReprTests.test_lambda.<locals>.<lambda"), r)
        # XXX anonymous functions?  see func_repr

    eleza test_builtin_function(self):
        eq = self.assertEqual
        # Functions
        eq(repr(hash), '<built-in function hash>')
        # Methods
        self.assertKweli(repr(''.split).startswith(
            '<built-in method split of str object at 0x'))

    eleza test_range(self):
        eq = self.assertEqual
        eq(repr(range(1)), 'range(0, 1)')
        eq(repr(range(1, 2)), 'range(1, 2)')
        eq(repr(range(1, 4, 3)), 'range(1, 4, 3)')

    eleza test_nesting(self):
        eq = self.assertEqual
        # everything ni meant to give up after 6 levels.
        eq(r([[[[[[[]]]]]]]), "[[[[[[[]]]]]]]")
        eq(r([[[[[[[[]]]]]]]]), "[[[[[[[...]]]]]]]")

        eq(r(nestedTuple(6)), "(((((((),),),),),),)")
        eq(r(nestedTuple(7)), "(((((((...),),),),),),)")

        eq(r({ nestedTuple(5) : nestedTuple(5) }),
           "{((((((),),),),),): ((((((),),),),),)}")
        eq(r({ nestedTuple(6) : nestedTuple(6) }),
           "{((((((...),),),),),): ((((((...),),),),),)}")

        eq(r([[[[[[{}]]]]]]), "[[[[[[{}]]]]]]")
        eq(r([[[[[[[{}]]]]]]]), "[[[[[[[...]]]]]]]")

    eleza test_cell(self):
        eleza get_cell():
            x = 42
            eleza inner():
                rudisha x
            rudisha inner
        x = get_cell().__closure__[0]
        self.assertRegex(repr(x), r'<cell at 0x[0-9A-Fa-f]+: '
                                  r'int object at 0x[0-9A-Fa-f]+>')
        self.assertRegex(r(x), r'<cell at 0x.*\.\.\..*>')

    eleza test_descriptors(self):
        eq = self.assertEqual
        # method descriptors
        eq(repr(dict.items), "<method 'items' of 'dict' objects>")
        # XXX member descriptors
        # XXX attribute descriptors
        # XXX slot descriptors
        # static na kundi methods
        kundi C:
            eleza foo(cls): pita
        x = staticmethod(C.foo)
        self.assertKweli(repr(x).startswith('<staticmethod object at 0x'))
        x = classmethod(C.foo)
        self.assertKweli(repr(x).startswith('<classmethod object at 0x'))

    eleza test_unsortable(self):
        # Repr.repr() used to call sorted() on sets, frozensets na dicts
        # without taking into account that sio all objects are comparable
        x = set([1j, 2j, 3j])
        y = frozenset(x)
        z = {1j: 1, 2j: 2}
        r(x)
        r(y)
        r(z)

eleza write_file(path, text):
    with open(path, 'w', encoding='ASCII') kama fp:
        fp.write(text)

kundi LongReprTest(unittest.TestCase):
    longname = 'areallylongpackageandmodulenametotestreprtruncation'

    eleza setUp(self):
        self.pkgname = os.path.join(self.longname)
        self.subpkgname = os.path.join(self.longname, self.longname)
        # Make the package na subpackage
        shutil.rmtree(self.pkgname, ignore_errors=Kweli)
        os.mkdir(self.pkgname)
        create_empty_file(os.path.join(self.pkgname, '__init__.py'))
        shutil.rmtree(self.subpkgname, ignore_errors=Kweli)
        os.mkdir(self.subpkgname)
        create_empty_file(os.path.join(self.subpkgname, '__init__.py'))
        # Remember where we are
        self.here = os.getcwd()
        sys.path.insert(0, self.here)
        # When regrtest ni run with its -j option, this command alone ni not
        # enough.
        importlib.invalidate_caches()

    eleza tearDown(self):
        actions = []
        kila dirpath, dirnames, filenames kwenye os.walk(self.pkgname):
            kila name kwenye dirnames + filenames:
                actions.append(os.path.join(dirpath, name))
        actions.append(self.pkgname)
        actions.sort()
        actions.reverse()
        kila p kwenye actions:
            ikiwa os.path.isdir(p):
                os.rmdir(p)
            isipokua:
                os.remove(p)
        toa sys.path[0]

    eleza _check_path_limitations(self, module_name):
        # base directory
        source_path_len = len(self.here)
        # a path separator + `longname` (twice)
        source_path_len += 2 * (len(self.longname) + 1)
        # a path separator + `module_name` + ".py"
        source_path_len += len(module_name) + 1 + len(".py")
        cached_path_len = (source_path_len +
            len(importlib.util.cache_kutoka_source("x.py")) - len("x.py"))
        ikiwa os.name == 'nt' na cached_path_len >= 258:
            # Under Windows, the max path len ni 260 including C's terminating
            # NUL character.
            # (see http://msdn.microsoft.com/en-us/library/windows/desktop/aa365247%28v=vs.85%29.aspx#maxpath)
            self.skipTest("test paths too long (%d characters) kila Windows' 260 character limit"
                          % cached_path_len)
        elikiwa os.name == 'nt' na verbose:
            andika("cached_path_len =", cached_path_len)

    eleza test_module(self):
        self.maxDiff = Tupu
        self._check_path_limitations(self.pkgname)
        create_empty_file(os.path.join(self.subpkgname, self.pkgname + '.py'))
        importlib.invalidate_caches()
        kutoka areallylongpackageandmodulenametotestreprtruncation.areallylongpackageandmodulenametotestreprtruncation agiza areallylongpackageandmodulenametotestreprtruncation
        module = areallylongpackageandmodulenametotestreprtruncation
        self.assertEqual(repr(module), "<module %r kutoka %r>" % (module.__name__, module.__file__))
        self.assertEqual(repr(sys), "<module 'sys' (built-in)>")

    eleza test_type(self):
        self._check_path_limitations('foo')
        eq = self.assertEqual
        write_file(os.path.join(self.subpkgname, 'foo.py'), '''\
kundi foo(object):
    pita
''')
        importlib.invalidate_caches()
        kutoka areallylongpackageandmodulenametotestreprtruncation.areallylongpackageandmodulenametotestreprtruncation agiza foo
        eq(repr(foo.foo),
               "<kundi '%s.foo'>" % foo.__name__)

    @unittest.skip('need a suitable object')
    eleza test_object(self):
        # XXX Test the repr of a type with a really long tp_name but with no
        # tp_repr.  WIBNI we had ::Inline? :)
        pita

    eleza test_class(self):
        self._check_path_limitations('bar')
        write_file(os.path.join(self.subpkgname, 'bar.py'), '''\
kundi bar:
    pita
''')
        importlib.invalidate_caches()
        kutoka areallylongpackageandmodulenametotestreprtruncation.areallylongpackageandmodulenametotestreprtruncation agiza bar
        # Module name may be prefixed with "test.", depending on how run.
        self.assertEqual(repr(bar.bar), "<kundi '%s.bar'>" % bar.__name__)

    eleza test_instance(self):
        self._check_path_limitations('baz')
        write_file(os.path.join(self.subpkgname, 'baz.py'), '''\
kundi baz:
    pita
''')
        importlib.invalidate_caches()
        kutoka areallylongpackageandmodulenametotestreprtruncation.areallylongpackageandmodulenametotestreprtruncation agiza baz
        ibaz = baz.baz()
        self.assertKweli(repr(ibaz).startswith(
            "<%s.baz object at 0x" % baz.__name__))

    eleza test_method(self):
        self._check_path_limitations('qux')
        eq = self.assertEqual
        write_file(os.path.join(self.subpkgname, 'qux.py'), '''\
kundi aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:
    eleza amethod(self): pita
''')
        importlib.invalidate_caches()
        kutoka areallylongpackageandmodulenametotestreprtruncation.areallylongpackageandmodulenametotestreprtruncation agiza qux
        # Unbound methods first
        r = repr(qux.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.amethod)
        self.assertKweli(r.startswith('<function aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.amethod'), r)
        # Bound method next
        iqux = qux.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa()
        r = repr(iqux.amethod)
        self.assertKweli(r.startswith(
            '<bound method aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.amethod of <%s.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa object at 0x' \
            % (qux.__name__,) ), r)

    @unittest.skip('needs a built-in function with a really long name')
    eleza test_builtin_function(self):
        # XXX test built-in functions na methods with really long names
        pita

kundi ClassWithRepr:
    eleza __init__(self, s):
        self.s = s
    eleza __repr__(self):
        rudisha "ClassWithRepr(%r)" % self.s


kundi ClassWithFailingRepr:
    eleza __repr__(self):
        ashiria Exception("This should be caught by Repr.repr_instance")

kundi MyContainer:
    'Helper kundi kila TestRecursiveRepr'
    eleza __init__(self, values):
        self.values = list(values)
    eleza append(self, value):
        self.values.append(value)
    @recursive_repr()
    eleza __repr__(self):
        rudisha '<' + ', '.join(map(str, self.values)) + '>'

kundi MyContainer2(MyContainer):
    @recursive_repr('+++')
    eleza __repr__(self):
        rudisha '<' + ', '.join(map(str, self.values)) + '>'

kundi MyContainer3:
    eleza __repr__(self):
        'Test document content'
        pita
    wrapped = __repr__
    wrapper = recursive_repr()(wrapped)

kundi TestRecursiveRepr(unittest.TestCase):
    eleza test_recursive_repr(self):
        m = MyContainer(list('abcde'))
        m.append(m)
        m.append('x')
        m.append(m)
        self.assertEqual(repr(m), '<a, b, c, d, e, ..., x, ...>')
        m = MyContainer2(list('abcde'))
        m.append(m)
        m.append('x')
        m.append(m)
        self.assertEqual(repr(m), '<a, b, c, d, e, +++, x, +++>')

    eleza test_assigned_attributes(self):
        kutoka functools agiza WRAPPER_ASSIGNMENTS kama assigned
        wrapped = MyContainer3.wrapped
        wrapper = MyContainer3.wrapper
        kila name kwenye assigned:
            self.assertIs(getattr(wrapper, name), getattr(wrapped, name))

ikiwa __name__ == "__main__":
    unittest.main()
