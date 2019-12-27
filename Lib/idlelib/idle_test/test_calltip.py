"Test calltip, coverage 60%"

kutoka idlelib agiza calltip
agiza unittest
agiza textwrap
agiza types
agiza re


# Test Class TC is used in multiple get_argspec test methods
kundi TC():
    'doc'
    tip = "(ai=None, *b)"
    eleza __init__(self, ai=None, *b): 'doc'
    __init__.tip = "(self, ai=None, *b)"
    eleza t1(self): 'doc'
    t1.tip = "(self)"
    eleza t2(self, ai, b=None): 'doc'
    t2.tip = "(self, ai, b=None)"
    eleza t3(self, ai, *args): 'doc'
    t3.tip = "(self, ai, *args)"
    eleza t4(self, *args): 'doc'
    t4.tip = "(self, *args)"
    eleza t5(self, ai, b=None, *args, **kw): 'doc'
    t5.tip = "(self, ai, b=None, *args, **kw)"
    eleza t6(no, self): 'doc'
    t6.tip = "(no, self)"
    eleza __call__(self, ci): 'doc'
    __call__.tip = "(self, ci)"
    eleza nd(self): pass  # No doc.
    # attaching .tip to wrapped methods does not work
    @classmethod
    eleza cm(cls, a): 'doc'
    @staticmethod
    eleza sm(b): 'doc'


tc = TC()
default_tip = calltip._default_callable_argspec
get_spec = calltip.get_argspec


kundi Get_argspecTest(unittest.TestCase):
    # The get_spec function must rudisha a string, even ikiwa blank.
    # Test a variety of objects to be sure that none cause it to raise
    # (quite aside kutoka getting as correct an answer as possible).
    # The tests of builtins may break ikiwa inspect or the docstrings change,
    # but a red buildbot is better than a user crash (as has happened).
    # For a simple mismatch, change the expected output to the actual.

    eleza test_builtins(self):

        eleza tiptest(obj, out):
            self.assertEqual(get_spec(obj), out)

        # Python kundi that inherits builtin methods
        kundi List(list): "List() doc"

        # Simulate builtin with no docstring for default tip test
        kundi SB:  __call__ = None

        ikiwa List.__doc__ is not None:
            tiptest(List,
                    f'(iterable=(), /){calltip._argument_positional}'
                    f'\n{List.__doc__}')
        tiptest(list.__new__,
              '(*args, **kwargs)\n'
              'Create and rudisha a new object.  '
              'See help(type) for accurate signature.')
        tiptest(list.__init__,
              '(self, /, *args, **kwargs)'
              + calltip._argument_positional + '\n' +
              'Initialize self.  See help(type(self)) for accurate signature.')
        append_doc = (calltip._argument_positional
                      + "\nAppend object to the end of the list.")
        tiptest(list.append, '(self, object, /)' + append_doc)
        tiptest(List.append, '(self, object, /)' + append_doc)
        tiptest([].append, '(object, /)' + append_doc)

        tiptest(types.MethodType, "method(function, instance)")
        tiptest(SB(), default_tip)

        p = re.compile('')
        tiptest(re.sub, '''\
(pattern, repl, string, count=0, flags=0)
Return the string obtained by replacing the leftmost
non-overlapping occurrences of the pattern in string by the
replacement repl.  repl can be either a string or a callable;
ikiwa a string, backslash escapes in it are processed.  If it is
a callable, it's passed the Match object and must return''')
        tiptest(p.sub, '''\
(repl, string, count=0)
Return the string obtained by replacing the leftmost \
non-overlapping occurrences o...''')

    eleza test_signature_wrap(self):
        ikiwa textwrap.TextWrapper.__doc__ is not None:
            self.assertEqual(get_spec(textwrap.TextWrapper), '''\
(width=70, initial_indent='', subsequent_indent='', expand_tabs=True,
    replace_whitespace=True, fix_sentence_endings=False, break_long_words=True,
    drop_whitespace=True, break_on_hyphens=True, tabsize=8, *, max_lines=None,
    placeholder=' [...]')''')

    eleza test_properly_formated(self):

        eleza foo(s='a'*100):
            pass

        eleza bar(s='a'*100):
            """Hello Guido"""
            pass

        eleza baz(s='a'*100, z='b'*100):
            pass

        indent = calltip._INDENT

        sfoo = "(s='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\
               "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n" + indent + "aaaaaaaaa"\
               "aaaaaaaaaa')"
        sbar = "(s='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\
               "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n" + indent + "aaaaaaaaa"\
               "aaaaaaaaaa')\nHello Guido"
        sbaz = "(s='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\
               "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n" + indent + "aaaaaaaaa"\
               "aaaaaaaaaa', z='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"\
               "bbbbbbbbbbbbbbbbb\n" + indent + "bbbbbbbbbbbbbbbbbbbbbb"\
               "bbbbbbbbbbbbbbbbbbbbbb')"

        for func,doc in [(foo, sfoo), (bar, sbar), (baz, sbaz)]:
            with self.subTest(func=func, doc=doc):
                self.assertEqual(get_spec(func), doc)

    eleza test_docline_truncation(self):
        eleza f(): pass
        f.__doc__ = 'a'*300
        self.assertEqual(get_spec(f), f"()\n{'a'*(calltip._MAX_COLS-3) + '...'}")

    eleza test_multiline_docstring(self):
        # Test fewer lines than max.
        self.assertEqual(get_spec(range),
                "range(stop) -> range object\n"
                "range(start, stop[, step]) -> range object")

        # Test max lines
        self.assertEqual(get_spec(bytes), '''\
bytes(iterable_of_ints) -> bytes
bytes(string, encoding[, errors]) -> bytes
bytes(bytes_or_buffer) -> immutable copy of bytes_or_buffer
bytes(int) -> bytes object of size given by the parameter initialized with null bytes
bytes() -> empty bytes object''')

        # Test more than max lines
        eleza f(): pass
        f.__doc__ = 'a\n' * 15
        self.assertEqual(get_spec(f), '()' + '\na' * calltip._MAX_LINES)

    eleza test_functions(self):
        eleza t1(): 'doc'
        t1.tip = "()"
        eleza t2(a, b=None): 'doc'
        t2.tip = "(a, b=None)"
        eleza t3(a, *args): 'doc'
        t3.tip = "(a, *args)"
        eleza t4(*args): 'doc'
        t4.tip = "(*args)"
        eleza t5(a, b=None, *args, **kw): 'doc'
        t5.tip = "(a, b=None, *args, **kw)"

        doc = '\ndoc' ikiwa t1.__doc__ is not None else ''
        for func in (t1, t2, t3, t4, t5, TC):
            with self.subTest(func=func):
                self.assertEqual(get_spec(func), func.tip + doc)

    eleza test_methods(self):
        doc = '\ndoc' ikiwa TC.__doc__ is not None else ''
        for meth in (TC.t1, TC.t2, TC.t3, TC.t4, TC.t5, TC.t6, TC.__call__):
            with self.subTest(meth=meth):
                self.assertEqual(get_spec(meth), meth.tip + doc)
        self.assertEqual(get_spec(TC.cm), "(a)" + doc)
        self.assertEqual(get_spec(TC.sm), "(b)" + doc)

    eleza test_bound_methods(self):
        # test that first parameter is correctly removed kutoka argspec
        doc = '\ndoc' ikiwa TC.__doc__ is not None else ''
        for meth, mtip  in ((tc.t1, "()"), (tc.t4, "(*args)"),
                            (tc.t6, "(self)"), (tc.__call__, '(ci)'),
                            (tc, '(ci)'), (TC.cm, "(a)"),):
            with self.subTest(meth=meth, mtip=mtip):
                self.assertEqual(get_spec(meth), mtip + doc)

    eleza test_starred_parameter(self):
        # test that starred first parameter is *not* removed kutoka argspec
        kundi C:
            eleza m1(*args): pass
        c = C()
        for meth, mtip  in ((C.m1, '(*args)'), (c.m1, "(*args)"),):
            with self.subTest(meth=meth, mtip=mtip):
                self.assertEqual(get_spec(meth), mtip)

    eleza test_invalid_method_get_spec(self):
        kundi C:
            eleza m2(**kwargs): pass
        kundi Test:
            eleza __call__(*, a): pass

        mtip = calltip._invalid_method
        self.assertEqual(get_spec(C().m2), mtip)
        self.assertEqual(get_spec(Test()), mtip)

    eleza test_non_ascii_name(self):
        # test that re works to delete a first parameter name that
        # includes non-ascii chars, such as various forms of A.
        uni = "(A\u0391\u0410\u05d0\u0627\u0905\u1e00\u3042, a)"
        assert calltip._first_param.sub('', uni) == '(a)'

    eleza test_no_docstring(self):
        for meth, mtip in ((TC.nd, "(self)"), (tc.nd, "()")):
            with self.subTest(meth=meth, mtip=mtip):
                self.assertEqual(get_spec(meth), mtip)

    eleza test_attribute_exception(self):
        kundi NoCall:
            eleza __getattr__(self, name):
                raise BaseException
        kundi CallA(NoCall):
            eleza __call__(oui, a, b, c):
                pass
        kundi CallB(NoCall):
            eleza __call__(self, ci):
                pass

        for meth, mtip  in ((NoCall, default_tip), (CallA, default_tip),
                            (NoCall(), ''), (CallA(), '(a, b, c)'),
                            (CallB(), '(ci)')):
            with self.subTest(meth=meth, mtip=mtip):
                self.assertEqual(get_spec(meth), mtip)

    eleza test_non_callables(self):
        for obj in (0, 0.0, '0', b'0', [], {}):
            with self.subTest(obj=obj):
                self.assertEqual(get_spec(obj), '')


kundi Get_entityTest(unittest.TestCase):
    eleza test_bad_entity(self):
        self.assertIsNone(calltip.get_entity('1/0'))
    eleza test_good_entity(self):
        self.assertIs(calltip.get_entity('int'), int)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
