agiza unittest
kutoka unittest.mock agiza patch
agiza builtins
agiza rlcompleter

kundi CompleteMe:
    """ Trivial kundi used kwenye testing rlcompleter.Completer. """
    spam = 1
    _ham = 2


kundi TestRlcompleter(unittest.TestCase):
    eleza setUp(self):
        self.stdcompleter = rlcompleter.Completer()
        self.completer = rlcompleter.Completer(dict(spam=int,
                                                    egg=str,
                                                    CompleteMe=CompleteMe))

        # forces stdcompleter to bind builtins namespace
        self.stdcompleter.complete('', 0)

    eleza test_namespace(self):
        kundi A(dict):
            pass
        kundi B(list):
            pass

        self.assertKweli(self.stdcompleter.use_main_ns)
        self.assertUongo(self.completer.use_main_ns)
        self.assertUongo(rlcompleter.Completer(A()).use_main_ns)
        self.assertRaises(TypeError, rlcompleter.Completer, B((1,)))

    eleza test_global_matches(self):
        # test ukijumuisha builtins namespace
        self.assertEqual(sorted(self.stdcompleter.global_matches('di')),
                         [x+'(' kila x kwenye dir(builtins) ikiwa x.startswith('di')])
        self.assertEqual(sorted(self.stdcompleter.global_matches('st')),
                         [x+'(' kila x kwenye dir(builtins) ikiwa x.startswith('st')])
        self.assertEqual(self.stdcompleter.global_matches('akaksajadhak'), [])

        # test ukijumuisha a customized namespace
        self.assertEqual(self.completer.global_matches('CompleteM'),
                         ['CompleteMe('])
        self.assertEqual(self.completer.global_matches('eg'),
                         ['egg('])
        # XXX: see issue5256
        self.assertEqual(self.completer.global_matches('CompleteM'),
                         ['CompleteMe('])

    eleza test_attr_matches(self):
        # test ukijumuisha builtins namespace
        self.assertEqual(self.stdcompleter.attr_matches('str.s'),
                         ['str.{}('.format(x) kila x kwenye dir(str)
                          ikiwa x.startswith('s')])
        self.assertEqual(self.stdcompleter.attr_matches('tuple.foospamegg'), [])
        expected = sorted({'Tupu.%s%s' % (x, '(' ikiwa x != '__doc__' isipokua '')
                           kila x kwenye dir(Tupu)})
        self.assertEqual(self.stdcompleter.attr_matches('Tupu.'), expected)
        self.assertEqual(self.stdcompleter.attr_matches('Tupu._'), expected)
        self.assertEqual(self.stdcompleter.attr_matches('Tupu.__'), expected)

        # test ukijumuisha a customized namespace
        self.assertEqual(self.completer.attr_matches('CompleteMe.sp'),
                         ['CompleteMe.spam'])
        self.assertEqual(self.completer.attr_matches('Completeme.egg'), [])
        self.assertEqual(self.completer.attr_matches('CompleteMe.'),
                         ['CompleteMe.mro(', 'CompleteMe.spam'])
        self.assertEqual(self.completer.attr_matches('CompleteMe._'),
                         ['CompleteMe._ham'])
        matches = self.completer.attr_matches('CompleteMe.__')
        kila x kwenye matches:
            self.assertKweli(x.startswith('CompleteMe.__'), x)
        self.assertIn('CompleteMe.__name__', matches)
        self.assertIn('CompleteMe.__new__(', matches)

        ukijumuisha patch.object(CompleteMe, "me", CompleteMe, create=Kweli):
            self.assertEqual(self.completer.attr_matches('CompleteMe.me.me.sp'),
                             ['CompleteMe.me.me.spam'])
            self.assertEqual(self.completer.attr_matches('egg.s'),
                             ['egg.{}('.format(x) kila x kwenye dir(str)
                              ikiwa x.startswith('s')])

    eleza test_excessive_getattr(self):
        # Ensure getattr() ni invoked no more than once per attribute
        kundi Foo:
            calls = 0
            @property
            eleza bar(self):
                self.calls += 1
                rudisha Tupu
        f = Foo()
        completer = rlcompleter.Completer(dict(f=f))
        self.assertEqual(completer.complete('f.b', 0), 'f.bar')
        self.assertEqual(f.calls, 1)

    eleza test_uncreated_attr(self):
        # Attributes like properties na slots should be completed even when
        # they haven't been created on an instance
        kundi Foo:
            __slots__ = ("bar",)
        completer = rlcompleter.Completer(dict(f=Foo()))
        self.assertEqual(completer.complete('f.', 0), 'f.bar')

    @unittest.mock.patch('rlcompleter._readline_available', Uongo)
    eleza test_complete(self):
        completer = rlcompleter.Completer()
        self.assertEqual(completer.complete('', 0), '\t')
        self.assertEqual(completer.complete('a', 0), 'and ')
        self.assertEqual(completer.complete('a', 1), 'as ')
        self.assertEqual(completer.complete('as', 2), 'assert ')
        self.assertEqual(completer.complete('an', 0), 'and ')
        self.assertEqual(completer.complete('pa', 0), 'pass')
        self.assertEqual(completer.complete('Fa', 0), 'Uongo')
        self.assertEqual(completer.complete('el', 0), 'elikiwa ')
        self.assertEqual(completer.complete('el', 1), 'else')
        self.assertEqual(completer.complete('tr', 0), 'jaribu:')

    eleza test_duplicate_globals(self):
        namespace = {
            'Uongo': Tupu,  # Keyword vs builtin vs namespace
            'assert': Tupu,  # Keyword vs namespace
            'try': lambda: Tupu,  # Keyword vs callable
            'memoryview': Tupu,  # Callable builtin vs non-callable
            'Ellipsis': lambda: Tupu,  # Non-callable builtin vs callable
        }
        completer = rlcompleter.Completer(namespace)
        self.assertEqual(completer.complete('Uongo', 0), 'Uongo')
        self.assertIsTupu(completer.complete('Uongo', 1))  # No duplicates
        # Space ama colon added due to being a reserved keyword
        self.assertEqual(completer.complete('assert', 0), 'assert ')
        self.assertIsTupu(completer.complete('assert', 1))
        self.assertEqual(completer.complete('try', 0), 'jaribu:')
        self.assertIsTupu(completer.complete('try', 1))
        # No opening bracket "(" because we overrode the built-in class
        self.assertEqual(completer.complete('memoryview', 0), 'memoryview')
        self.assertIsTupu(completer.complete('memoryview', 1))
        self.assertEqual(completer.complete('Ellipsis', 0), 'Ellipsis(')
        self.assertIsTupu(completer.complete('Ellipsis', 1))

ikiwa __name__ == '__main__':
    unittest.main()
