"Test calltip, coverage 60%"

kutoka idlelib agiza calltip
agiza unittest
agiza textwrap
agiza types
agiza re


# Test Class TC ni used kwenye multiple get_argspec test methods
kundi TC():
    'doc'
    tip = "(ai=Tupu, *b)"
    eleza __init__(self, ai=Tupu, *b): 'doc'
    __init__.tip = "(self, ai=Tupu, *b)"
    eleza t1(self): 'doc'
    t1.tip = "(self)"
    eleza t2(self, ai, b=Tupu): 'doc'
    t2.tip = "(self, ai, b=Tupu)"
    eleza t3(self, ai, *args): 'doc'
    t3.tip = "(self, ai, *args)"
    eleza t4(self, *args): 'doc'
    t4.tip = "(self, *args)"
    eleza t5(self, ai, b=Tupu, *args, **kw): 'doc'
    t5.tip = "(self, ai, b=Tupu, *args, **kw)"
    eleza t6(no, self): 'doc'
    t6.tip = "(no, self)"
    eleza __call__(self, ci): 'doc'
    __call__.tip = "(self, ci)"
    eleza nd(self): pass  # No doc.
    # attaching .tip to wrapped methods does sio work
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
    # The tests of builtins may koma ikiwa inspect ama the docstrings change,
    # but a red buildbot ni better than a user crash (as has happened).
    # For a simple mismatch, change the expected output to the actual.

    eleza test_builtins(self):

        eleza tiptest(obj, out):
            self.assertEqual(get_spec(obj), out)

        # Python kundi that inherits builtin methods
        kundi List(list): "List() doc"

        # Simulate builtin ukijumuisha no docstring kila default tip test
        kundi SB:  __call__ = Tupu

        ikiwa List.__doc__ ni sio Tupu:
            tiptest(List,
                    f'(iterable=(), /){calltip._argument_positional}'
                    f'\n{List.__doc__}')
        tiptest(list.__new__,
              '(*args, **kwargs)\n'
              'Create na rudisha a new object.  '
              'See help(type) kila accurate signature.')
        tiptest(list.__init__,
              '(self, /, *args, **kwargs)'
              + calltip._argument_positional + '\n' +
              'Initialize self.  See help(type(self)) kila accurate signature.')
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
non-overlapping occurrences of the pattern kwenye string by the
replacement repl.  repl can be either a string ama a callable;
ikiwa a string, backslash escapes kwenye it are processed.  If it is
a callable, it's passed the Match object na must return''')
        tiptest(p.sub, '''\
(repl, string, count=0)
Return the string obtained by replacing the leftmost \
non-overlapping occurrences o...''')

    eleza test_signature_wrap(self):
        ikiwa textwrap.TextWrapper.__doc__ ni sio Tupu:
            self.assertEqual(get_spec(textwrap.TextWrapper), '''\
(width=70, initial_indent='', subsequent_indent='', expand_tabs=Kweli,
    replace_whitespace=Kweli, fix_sentence_endings=Uongo, koma_long_words=Kweli,
    drop_whitespace=Kweli, koma_on_hyphens=Kweli, tabsize=8, *, max_lines=Tupu,
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

        kila func,doc kwenye [(foo, sfoo), (bar, sbar), (baz, sbaz)]:
            ukijumuisha self.subTest(func=func, doc=doc):
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
bytes(int) -> bytes object of size given by the parameter initialized ukijumuisha null bytes
bytes() -> empty bytes object''')

        # Test more than max lines
        eleza f(): pass
        f.__doc__ = 'a\n' * 15
        self.assertEqual(get_spec(f), '()' + '\na' * calltip._MAX_LINES)

    eleza test_functions(self):
        eleza t1(): 'doc'
        t1.tip = "()"
        eleza t2(a, b=Tupu): 'doc'
        t2.tip = "(a, b=Tupu)"
        eleza t3(a, *args): 'doc'
        t3.tip = "(a, *args)"
        eleza t4(*args): 'doc'
        t4.tip = "(*args)"
        eleza t5(a, b=Tupu, *args, **kw): 'doc'
        t5.tip = "(a, b=Tupu, *args, **kw)"

        doc = '\ndoc' ikiwa t1.__doc__ ni sio Tupu isipokua ''
        kila func kwenye (t1, t2, t3, t4, t5, TC):
            ukijumuisha self.subTest(func=func):
                self.assertEqual(get_spec(func), func.tip + doc)

    eleza test_methods(self):
        doc = '\ndoc' ikiwa TC.__doc__ ni sio Tupu isipokua ''
        kila meth kwenye (TC.t1, TC.t2, TC.t3, TC.t4, TC.t5, TC.t6, TC.__call__):
            ukijumuisha self.subTest(meth=meth):
                self.assertEqual(get_spec(meth), meth.tip + doc)
        self.assertEqual(get_spec(TC.cm), "(a)" + doc)
        self.assertEqual(get_spec(TC.sm), "(b)" + doc)

    eleza test_bound_methods(self):
        # test that first parameter ni correctly removed kutoka argspec
        doc = '\ndoc' ikiwa TC.__doc__ ni sio Tupu isipokua ''
        kila meth, mtip  kwenye ((tc.t1, "()"), (tc.t4, "(*args)"),
                            (tc.t6, "(self)"), (tc.__call__, '(ci)'),
                            (tc, '(ci)'), (TC.cm, "(a)"),):
            ukijumuisha self.subTest(meth=meth, mtip=mtip):
                self.assertEqual(get_spec(meth), mtip + doc)

    eleza test_starred_parameter(self):
        # test that starred first parameter ni *not* removed kutoka argspec
        kundi C:
            eleza m1(*args): pass
        c = C()
        kila meth, mtip  kwenye ((C.m1, '(*args)'), (c.m1, "(*args)"),):
            ukijumuisha self.subTest(meth=meth, mtip=mtip):
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
        kila meth, mtip kwenye ((TC.nd, "(self)"), (tc.nd, "()")):
            ukijumuisha self.subTest(meth=meth, mtip=mtip):
                self.assertEqual(get_spec(meth), mtip)

    eleza test_attribute_exception(self):
        kundi NoCall:
            eleza __getattr__(self, name):
                 ashiria BaseException
        kundi CallA(NoCall):
            eleza __call__(oui, a, b, c):
                pass
        kundi CallB(NoCall):
            eleza __call__(self, ci):
                pass

        kila meth, mtip  kwenye ((NoCall, default_tip), (CallA, default_tip),
                            (NoCall(), ''), (CallA(), '(a, b, c)'),
                            (CallB(), '(ci)')):
            ukijumuisha self.subTest(meth=meth, mtip=mtip):
                self.assertEqual(get_spec(meth), mtip)

    eleza test_non_callables(self):
        kila obj kwenye (0, 0.0, '0', b'0', [], {}):
            ukijumuisha self.subTest(obj=obj):
                self.assertEqual(get_spec(obj), '')


kundi Get_entityTest(unittest.TestCase):
    eleza test_bad_entity(self):
        self.assertIsTupu(calltip.get_entity('1/0'))
    eleza test_good_entity(self):
        self.assertIs(calltip.get_entity('int'), int)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
