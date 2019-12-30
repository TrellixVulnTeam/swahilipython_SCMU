""" Test suite kila the fixer modules """

# Python agizas
agiza os
kutoka itertools agiza chain
kutoka operator agiza itemgetter

# Local agizas
kutoka lib2to3 agiza pygram, fixer_util
kutoka lib2to3.tests agiza support


kundi FixerTestCase(support.TestCase):

    # Other test cases can subkundi this kundi na replace "fixer_pkg" with
    # their own.
    eleza setUp(self, fix_list=Tupu, fixer_pkg="lib2to3", options=Tupu):
        ikiwa fix_list ni Tupu:
            fix_list = [self.fixer]
        self.refactor = support.get_refactorer(fixer_pkg, fix_list, options)
        self.fixer_log = []
        self.filename = "<string>"

        kila fixer kwenye chain(self.refactor.pre_order,
                           self.refactor.post_order):
            fixer.log = self.fixer_log

    eleza _check(self, before, after):
        before = support.reformat(before)
        after = support.reformat(after)
        tree = self.refactor.refactor_string(before, self.filename)
        self.assertEqual(after, str(tree))
        rudisha tree

    eleza check(self, before, after, ignore_warnings=Uongo):
        tree = self._check(before, after)
        self.assertKweli(tree.was_changed)
        ikiwa sio ignore_warnings:
            self.assertEqual(self.fixer_log, [])

    eleza warns(self, before, after, message, unchanged=Uongo):
        tree = self._check(before, after)
        self.assertIn(message, "".join(self.fixer_log))
        ikiwa sio unchanged:
            self.assertKweli(tree.was_changed)

    eleza warns_unchanged(self, before, message):
        self.warns(before, before, message, unchanged=Kweli)

    eleza unchanged(self, before, ignore_warnings=Uongo):
        self._check(before, before)
        ikiwa sio ignore_warnings:
            self.assertEqual(self.fixer_log, [])

    eleza assert_runs_after(self, *names):
        fixes = [self.fixer]
        fixes.extend(names)
        r = support.get_refactorer("lib2to3", fixes)
        (pre, post) = r.get_fixers()
        n = "fix_" + self.fixer
        ikiwa post na post[-1].__class__.__module__.endswith(n):
            # We're the last fixer to run
            rudisha
        ikiwa pre na pre[-1].__class__.__module__.endswith(n) na sio post:
            # We're the last kwenye pre na post ni empty
            rudisha
        self.fail("Fixer run order (%s) ni incorrect; %s should be last."\
               %(", ".join([x.__class__.__module__ kila x kwenye (pre+post)]), n))

kundi Test_ne(FixerTestCase):
    fixer = "ne"

    eleza test_basic(self):
        b = """ikiwa x <> y:
            pita"""

        a = """ikiwa x != y:
            pita"""
        self.check(b, a)

    eleza test_no_spaces(self):
        b = """ikiwa x<>y:
            pita"""

        a = """ikiwa x!=y:
            pita"""
        self.check(b, a)

    eleza test_chained(self):
        b = """ikiwa x<>y<>z:
            pita"""

        a = """ikiwa x!=y!=z:
            pita"""
        self.check(b, a)

kundi Test_has_key(FixerTestCase):
    fixer = "has_key"

    eleza test_1(self):
        b = """x = d.has_key("x") ama d.has_key("y")"""
        a = """x = "x" kwenye d ama "y" kwenye d"""
        self.check(b, a)

    eleza test_2(self):
        b = """x = a.b.c.d.has_key("x") ** 3"""
        a = """x = ("x" kwenye a.b.c.d) ** 3"""
        self.check(b, a)

    eleza test_3(self):
        b = """x = a.b.has_key(1 + 2).__repr__()"""
        a = """x = (1 + 2 kwenye a.b).__repr__()"""
        self.check(b, a)

    eleza test_4(self):
        b = """x = a.b.has_key(1 + 2).__repr__() ** -3 ** 4"""
        a = """x = (1 + 2 kwenye a.b).__repr__() ** -3 ** 4"""
        self.check(b, a)

    eleza test_5(self):
        b = """x = a.has_key(f ama g)"""
        a = """x = (f ama g) kwenye a"""
        self.check(b, a)

    eleza test_6(self):
        b = """x = a + b.has_key(c)"""
        a = """x = a + (c kwenye b)"""
        self.check(b, a)

    eleza test_7(self):
        b = """x = a.has_key(lambda: 12)"""
        a = """x = (lambda: 12) kwenye a"""
        self.check(b, a)

    eleza test_8(self):
        b = """x = a.has_key(a kila a kwenye b)"""
        a = """x = (a kila a kwenye b) kwenye a"""
        self.check(b, a)

    eleza test_9(self):
        b = """ikiwa sio a.has_key(b): pita"""
        a = """ikiwa b haiko kwenye a: pita"""
        self.check(b, a)

    eleza test_10(self):
        b = """ikiwa sio a.has_key(b).__repr__(): pita"""
        a = """ikiwa sio (b kwenye a).__repr__(): pita"""
        self.check(b, a)

    eleza test_11(self):
        b = """ikiwa sio a.has_key(b) ** 2: pita"""
        a = """ikiwa sio (b kwenye a) ** 2: pita"""
        self.check(b, a)

kundi Test_apply(FixerTestCase):
    fixer = "apply"

    eleza test_1(self):
        b = """x = apply(f, g + h)"""
        a = """x = f(*g + h)"""
        self.check(b, a)

    eleza test_2(self):
        b = """y = apply(f, g, h)"""
        a = """y = f(*g, **h)"""
        self.check(b, a)

    eleza test_3(self):
        b = """z = apply(fs[0], g ama h, h ama g)"""
        a = """z = fs[0](*g ama h, **h ama g)"""
        self.check(b, a)

    eleza test_4(self):
        b = """apply(f, (x, y) + t)"""
        a = """f(*(x, y) + t)"""
        self.check(b, a)

    eleza test_5(self):
        b = """apply(f, args,)"""
        a = """f(*args)"""
        self.check(b, a)

    eleza test_6(self):
        b = """apply(f, args, kwds,)"""
        a = """f(*args, **kwds)"""
        self.check(b, a)

    # Test that complex functions are parenthesized

    eleza test_complex_1(self):
        b = """x = apply(f+g, args)"""
        a = """x = (f+g)(*args)"""
        self.check(b, a)

    eleza test_complex_2(self):
        b = """x = apply(f*g, args)"""
        a = """x = (f*g)(*args)"""
        self.check(b, a)

    eleza test_complex_3(self):
        b = """x = apply(f**g, args)"""
        a = """x = (f**g)(*args)"""
        self.check(b, a)

    # But dotted names etc. not

    eleza test_dotted_name(self):
        b = """x = apply(f.g, args)"""
        a = """x = f.g(*args)"""
        self.check(b, a)

    eleza test_subscript(self):
        b = """x = apply(f[x], args)"""
        a = """x = f[x](*args)"""
        self.check(b, a)

    eleza test_call(self):
        b = """x = apply(f(), args)"""
        a = """x = f()(*args)"""
        self.check(b, a)

    # Extreme case
    eleza test_extreme(self):
        b = """x = apply(a.b.c.d.e.f, args, kwds)"""
        a = """x = a.b.c.d.e.f(*args, **kwds)"""
        self.check(b, a)

    # XXX Comments kwenye weird places still get lost
    eleza test_weird_comments(self):
        b = """apply(   # foo
          f, # bar
          args)"""
        a = """f(*args)"""
        self.check(b, a)

    # These should *not* be touched

    eleza test_unchanged_1(self):
        s = """apply()"""
        self.unchanged(s)

    eleza test_unchanged_2(self):
        s = """apply(f)"""
        self.unchanged(s)

    eleza test_unchanged_3(self):
        s = """apply(f,)"""
        self.unchanged(s)

    eleza test_unchanged_4(self):
        s = """apply(f, args, kwds, extras)"""
        self.unchanged(s)

    eleza test_unchanged_5(self):
        s = """apply(f, *args, **kwds)"""
        self.unchanged(s)

    eleza test_unchanged_6(self):
        s = """apply(f, *args)"""
        self.unchanged(s)

    eleza test_unchanged_6b(self):
        s = """apply(f, **kwds)"""
        self.unchanged(s)

    eleza test_unchanged_7(self):
        s = """apply(func=f, args=args, kwds=kwds)"""
        self.unchanged(s)

    eleza test_unchanged_8(self):
        s = """apply(f, args=args, kwds=kwds)"""
        self.unchanged(s)

    eleza test_unchanged_9(self):
        s = """apply(f, args, kwds=kwds)"""
        self.unchanged(s)

    eleza test_space_1(self):
        a = """apply(  f,  args,   kwds)"""
        b = """f(*args, **kwds)"""
        self.check(a, b)

    eleza test_space_2(self):
        a = """apply(  f  ,args,kwds   )"""
        b = """f(*args, **kwds)"""
        self.check(a, b)

kundi Test_reload(FixerTestCase):
    fixer = "reload"

    eleza test(self):
        b = """reload(a)"""
        a = """agiza importlib\nimportlib.reload(a)"""
        self.check(b, a)

    eleza test_comment(self):
        b = """reload( a ) # comment"""
        a = """agiza importlib\nimportlib.reload( a ) # comment"""
        self.check(b, a)

        # PEP 8 comments
        b = """reload( a )  # comment"""
        a = """agiza importlib\nimportlib.reload( a )  # comment"""
        self.check(b, a)

    eleza test_space(self):
        b = """reload( a )"""
        a = """agiza importlib\nimportlib.reload( a )"""
        self.check(b, a)

        b = """reload( a)"""
        a = """agiza importlib\nimportlib.reload( a)"""
        self.check(b, a)

        b = """reload(a )"""
        a = """agiza importlib\nimportlib.reload(a )"""
        self.check(b, a)

    eleza test_unchanged(self):
        s = """reload(a=1)"""
        self.unchanged(s)

        s = """reload(f, g)"""
        self.unchanged(s)

        s = """reload(f, *h)"""
        self.unchanged(s)

        s = """reload(f, *h, **i)"""
        self.unchanged(s)

        s = """reload(f, **i)"""
        self.unchanged(s)

        s = """reload(*h, **i)"""
        self.unchanged(s)

        s = """reload(*h)"""
        self.unchanged(s)

        s = """reload(**i)"""
        self.unchanged(s)

        s = """reload()"""
        self.unchanged(s)

kundi Test_intern(FixerTestCase):
    fixer = "intern"

    eleza test_prefix_preservation(self):
        b = """x =   intern(  a  )"""
        a = """agiza sys\nx =   sys.intern(  a  )"""
        self.check(b, a)

        b = """y = intern("b" # test
              )"""
        a = """agiza sys\ny = sys.intern("b" # test
              )"""
        self.check(b, a)

        b = """z = intern(a+b+c.d,   )"""
        a = """agiza sys\nz = sys.intern(a+b+c.d,   )"""
        self.check(b, a)

    eleza test(self):
        b = """x = intern(a)"""
        a = """agiza sys\nx = sys.intern(a)"""
        self.check(b, a)

        b = """z = intern(a+b+c.d,)"""
        a = """agiza sys\nz = sys.intern(a+b+c.d,)"""
        self.check(b, a)

        b = """intern("y%s" % 5).replace("y", "")"""
        a = """agiza sys\nsys.intern("y%s" % 5).replace("y", "")"""
        self.check(b, a)

    # These should sio be refactored

    eleza test_unchanged(self):
        s = """intern(a=1)"""
        self.unchanged(s)

        s = """intern(f, g)"""
        self.unchanged(s)

        s = """intern(*h)"""
        self.unchanged(s)

        s = """intern(**i)"""
        self.unchanged(s)

        s = """intern()"""
        self.unchanged(s)

kundi Test_reduce(FixerTestCase):
    fixer = "reduce"

    eleza test_simple_call(self):
        b = "reduce(a, b, c)"
        a = "kutoka functools agiza reduce\nreduce(a, b, c)"
        self.check(b, a)

    eleza test_bug_7253(self):
        # fix_tuple_params was being bad na orphaning nodes kwenye the tree.
        b = "eleza x(arg): reduce(sum, [])"
        a = "kutoka functools agiza reduce\neleza x(arg): reduce(sum, [])"
        self.check(b, a)

    eleza test_call_with_lambda(self):
        b = "reduce(lambda x, y: x + y, seq)"
        a = "kutoka functools agiza reduce\nreduce(lambda x, y: x + y, seq)"
        self.check(b, a)

    eleza test_unchanged(self):
        s = "reduce(a)"
        self.unchanged(s)

        s = "reduce(a, b=42)"
        self.unchanged(s)

        s = "reduce(a, b, c, d)"
        self.unchanged(s)

        s = "reduce(**c)"
        self.unchanged(s)

        s = "reduce()"
        self.unchanged(s)

kundi Test_andika(FixerTestCase):
    fixer = "print"

    eleza test_prefix_preservation(self):
        b = """print 1,   1+1,   1+1+1"""
        a = """andika(1,   1+1,   1+1+1)"""
        self.check(b, a)

    eleza test_idempotency(self):
        s = """andika()"""
        self.unchanged(s)

        s = """andika('')"""
        self.unchanged(s)

    eleza test_idempotency_print_as_function(self):
        self.refactor.driver.grammar = pygram.python_grammar_no_print_statement
        s = """andika(1, 1+1, 1+1+1)"""
        self.unchanged(s)

        s = """andika()"""
        self.unchanged(s)

        s = """andika('')"""
        self.unchanged(s)

    eleza test_1(self):
        b = """print 1, 1+1, 1+1+1"""
        a = """andika(1, 1+1, 1+1+1)"""
        self.check(b, a)

    eleza test_2(self):
        b = """print 1, 2"""
        a = """andika(1, 2)"""
        self.check(b, a)

    eleza test_3(self):
        b = """print"""
        a = """andika()"""
        self.check(b, a)

    eleza test_4(self):
        # kutoka bug 3000
        b = """print whatever; print"""
        a = """andika(whatever); andika()"""
        self.check(b, a)

    eleza test_5(self):
        b = """print; print whatever;"""
        a = """andika(); andika(whatever);"""
        self.check(b, a)

    eleza test_tuple(self):
        b = """print (a, b, c)"""
        a = """andika((a, b, c))"""
        self.check(b, a)

    # trailing commas

    eleza test_trailing_comma_1(self):
        b = """print 1, 2, 3,"""
        a = """andika(1, 2, 3, end=' ')"""
        self.check(b, a)

    eleza test_trailing_comma_2(self):
        b = """print 1, 2,"""
        a = """andika(1, 2, end=' ')"""
        self.check(b, a)

    eleza test_trailing_comma_3(self):
        b = """print 1,"""
        a = """andika(1, end=' ')"""
        self.check(b, a)

    # >> stuff

    eleza test_vargs_without_trailing_comma(self):
        b = """print >>sys.stderr, 1, 2, 3"""
        a = """andika(1, 2, 3, file=sys.stderr)"""
        self.check(b, a)

    eleza test_with_trailing_comma(self):
        b = """print >>sys.stderr, 1, 2,"""
        a = """andika(1, 2, end=' ', file=sys.stderr)"""
        self.check(b, a)

    eleza test_no_trailing_comma(self):
        b = """print >>sys.stderr, 1+1"""
        a = """andika(1+1, file=sys.stderr)"""
        self.check(b, a)

    eleza test_spaces_before_file(self):
        b = """print >>  sys.stderr"""
        a = """andika(file=sys.stderr)"""
        self.check(b, a)

    eleza test_with_future_print_function(self):
        s = "kutoka __future__ agiza print_function\n" \
            "andika('Hai!', end=' ')"
        self.unchanged(s)

        b = "print 'Hello, world!'"
        a = "andika('Hello, world!')"
        self.check(b, a)


kundi Test_exec(FixerTestCase):
    fixer = "exec"

    eleza test_prefix_preservation(self):
        b = """  exec code kwenye ns1,   ns2"""
        a = """  exec(code, ns1,   ns2)"""
        self.check(b, a)

    eleza test_basic(self):
        b = """exec code"""
        a = """exec(code)"""
        self.check(b, a)

    eleza test_with_globals(self):
        b = """exec code kwenye ns"""
        a = """exec(code, ns)"""
        self.check(b, a)

    eleza test_with_globals_locals(self):
        b = """exec code kwenye ns1, ns2"""
        a = """exec(code, ns1, ns2)"""
        self.check(b, a)

    eleza test_complex_1(self):
        b = """exec (a.b()) kwenye ns"""
        a = """exec((a.b()), ns)"""
        self.check(b, a)

    eleza test_complex_2(self):
        b = """exec a.b() + c kwenye ns"""
        a = """exec(a.b() + c, ns)"""
        self.check(b, a)

    # These should sio be touched

    eleza test_unchanged_1(self):
        s = """exec(code)"""
        self.unchanged(s)

    eleza test_unchanged_2(self):
        s = """exec (code)"""
        self.unchanged(s)

    eleza test_unchanged_3(self):
        s = """exec(code, ns)"""
        self.unchanged(s)

    eleza test_unchanged_4(self):
        s = """exec(code, ns1, ns2)"""
        self.unchanged(s)

kundi Test_repr(FixerTestCase):
    fixer = "repr"

    eleza test_prefix_preservation(self):
        b = """x =   `1 + 2`"""
        a = """x =   repr(1 + 2)"""
        self.check(b, a)

    eleza test_simple_1(self):
        b = """x = `1 + 2`"""
        a = """x = repr(1 + 2)"""
        self.check(b, a)

    eleza test_simple_2(self):
        b = """y = `x`"""
        a = """y = repr(x)"""
        self.check(b, a)

    eleza test_complex(self):
        b = """z = `y`.__repr__()"""
        a = """z = repr(y).__repr__()"""
        self.check(b, a)

    eleza test_tuple(self):
        b = """x = `1, 2, 3`"""
        a = """x = repr((1, 2, 3))"""
        self.check(b, a)

    eleza test_nested(self):
        b = """x = `1 + `2``"""
        a = """x = repr(1 + repr(2))"""
        self.check(b, a)

    eleza test_nested_tuples(self):
        b = """x = `1, 2 + `3, 4``"""
        a = """x = repr((1, 2 + repr((3, 4))))"""
        self.check(b, a)

kundi Test_except(FixerTestCase):
    fixer = "except"

    eleza test_prefix_preservation(self):
        b = """
            jaribu:
                pita
            tatizo (RuntimeError, ImportError),    e:
                pita"""
        a = """
            jaribu:
                pita
            tatizo (RuntimeError, ImportError) kama    e:
                pita"""
        self.check(b, a)

    eleza test_simple(self):
        b = """
            jaribu:
                pita
            tatizo Foo, e:
                pita"""
        a = """
            jaribu:
                pita
            tatizo Foo kama e:
                pita"""
        self.check(b, a)

    eleza test_simple_no_space_before_target(self):
        b = """
            jaribu:
                pita
            tatizo Foo,e:
                pita"""
        a = """
            jaribu:
                pita
            tatizo Foo kama e:
                pita"""
        self.check(b, a)

    eleza test_tuple_unpack(self):
        b = """
            eleza foo():
                jaribu:
                    pita
                tatizo Exception, (f, e):
                    pita
                tatizo ImportError, e:
                    pita"""

        a = """
            eleza foo():
                jaribu:
                    pita
                tatizo Exception kama xxx_todo_changeme:
                    (f, e) = xxx_todo_changeme.args
                    pita
                tatizo ImportError kama e:
                    pita"""
        self.check(b, a)

    eleza test_multi_class(self):
        b = """
            jaribu:
                pita
            tatizo (RuntimeError, ImportError), e:
                pita"""

        a = """
            jaribu:
                pita
            tatizo (RuntimeError, ImportError) kama e:
                pita"""
        self.check(b, a)

    eleza test_list_unpack(self):
        b = """
            jaribu:
                pita
            tatizo Exception, [a, b]:
                pita"""

        a = """
            jaribu:
                pita
            tatizo Exception kama xxx_todo_changeme:
                [a, b] = xxx_todo_changeme.args
                pita"""
        self.check(b, a)

    eleza test_weird_target_1(self):
        b = """
            jaribu:
                pita
            tatizo Exception, d[5]:
                pita"""

        a = """
            jaribu:
                pita
            tatizo Exception kama xxx_todo_changeme:
                d[5] = xxx_todo_changeme
                pita"""
        self.check(b, a)

    eleza test_weird_target_2(self):
        b = """
            jaribu:
                pita
            tatizo Exception, a.foo:
                pita"""

        a = """
            jaribu:
                pita
            tatizo Exception kama xxx_todo_changeme:
                a.foo = xxx_todo_changeme
                pita"""
        self.check(b, a)

    eleza test_weird_target_3(self):
        b = """
            jaribu:
                pita
            tatizo Exception, a().foo:
                pita"""

        a = """
            jaribu:
                pita
            tatizo Exception kama xxx_todo_changeme:
                a().foo = xxx_todo_changeme
                pita"""
        self.check(b, a)

    eleza test_bare_except(self):
        b = """
            jaribu:
                pita
            tatizo Exception, a:
                pita
            tatizo:
                pita"""

        a = """
            jaribu:
                pita
            tatizo Exception kama a:
                pita
            tatizo:
                pita"""
        self.check(b, a)

    eleza test_bare_except_and_else_finally(self):
        b = """
            jaribu:
                pita
            tatizo Exception, a:
                pita
            tatizo:
                pita
            isipokua:
                pita
            mwishowe:
                pita"""

        a = """
            jaribu:
                pita
            tatizo Exception kama a:
                pita
            tatizo:
                pita
            isipokua:
                pita
            mwishowe:
                pita"""
        self.check(b, a)

    eleza test_multi_fixed_excepts_before_bare_except(self):
        b = """
            jaribu:
                pita
            tatizo TypeError, b:
                pita
            tatizo Exception, a:
                pita
            tatizo:
                pita"""

        a = """
            jaribu:
                pita
            tatizo TypeError kama b:
                pita
            tatizo Exception kama a:
                pita
            tatizo:
                pita"""
        self.check(b, a)

    eleza test_one_line_suites(self):
        b = """
            jaribu: ashiria TypeError
            tatizo TypeError, e:
                pita
            """
        a = """
            jaribu: ashiria TypeError
            tatizo TypeError kama e:
                pita
            """
        self.check(b, a)
        b = """
            jaribu:
                ashiria TypeError
            tatizo TypeError, e: pita
            """
        a = """
            jaribu:
                ashiria TypeError
            tatizo TypeError kama e: pita
            """
        self.check(b, a)
        b = """
            jaribu: ashiria TypeError
            tatizo TypeError, e: pita
            """
        a = """
            jaribu: ashiria TypeError
            tatizo TypeError kama e: pita
            """
        self.check(b, a)
        b = """
            jaribu: ashiria TypeError
            tatizo TypeError, e: pita
            isipokua: function()
            mwishowe: done()
            """
        a = """
            jaribu: ashiria TypeError
            tatizo TypeError kama e: pita
            isipokua: function()
            mwishowe: done()
            """
        self.check(b, a)

    # These should sio be touched:

    eleza test_unchanged_1(self):
        s = """
            jaribu:
                pita
            tatizo:
                pita"""
        self.unchanged(s)

    eleza test_unchanged_2(self):
        s = """
            jaribu:
                pita
            tatizo Exception:
                pita"""
        self.unchanged(s)

    eleza test_unchanged_3(self):
        s = """
            jaribu:
                pita
            tatizo (Exception, SystemExit):
                pita"""
        self.unchanged(s)

kundi Test_ashiria(FixerTestCase):
    fixer = "ashiria"

    eleza test_basic(self):
        b = """ashiria Exception, 5"""
        a = """ashiria Exception(5)"""
        self.check(b, a)

    eleza test_prefix_preservation(self):
        b = """ashiria Exception,5"""
        a = """ashiria Exception(5)"""
        self.check(b, a)

        b = """ashiria   Exception,    5"""
        a = """ashiria   Exception(5)"""
        self.check(b, a)

    eleza test_with_comments(self):
        b = """ashiria Exception, 5 # foo"""
        a = """ashiria Exception(5) # foo"""
        self.check(b, a)

        b = """ashiria E, (5, 6) % (a, b) # foo"""
        a = """ashiria E((5, 6) % (a, b)) # foo"""
        self.check(b, a)

        b = """eleza foo():
                    ashiria Exception, 5, 6 # foo"""
        a = """eleza foo():
                    ashiria Exception(5).with_traceback(6) # foo"""
        self.check(b, a)

    eleza test_Tupu_value(self):
        b = """ashiria Exception(5), Tupu, tb"""
        a = """ashiria Exception(5).with_traceback(tb)"""
        self.check(b, a)

    eleza test_tuple_value(self):
        b = """ashiria Exception, (5, 6, 7)"""
        a = """ashiria Exception(5, 6, 7)"""
        self.check(b, a)

    eleza test_tuple_detection(self):
        b = """ashiria E, (5, 6) % (a, b)"""
        a = """ashiria E((5, 6) % (a, b))"""
        self.check(b, a)

    eleza test_tuple_exc_1(self):
        b = """ashiria (((E1, E2), E3), E4), V"""
        a = """ashiria E1(V)"""
        self.check(b, a)

    eleza test_tuple_exc_2(self):
        b = """ashiria (E1, (E2, E3), E4), V"""
        a = """ashiria E1(V)"""
        self.check(b, a)

    # These should produce a warning

    eleza test_string_exc(self):
        s = """ashiria 'foo'"""
        self.warns_unchanged(s, "Python 3 does sio support string exceptions")

    eleza test_string_exc_val(self):
        s = """ashiria "foo", 5"""
        self.warns_unchanged(s, "Python 3 does sio support string exceptions")

    eleza test_string_exc_val_tb(self):
        s = """ashiria "foo", 5, 6"""
        self.warns_unchanged(s, "Python 3 does sio support string exceptions")

    # These should result kwenye traceback-assignment

    eleza test_tb_1(self):
        b = """eleza foo():
                    ashiria Exception, 5, 6"""
        a = """eleza foo():
                    ashiria Exception(5).with_traceback(6)"""
        self.check(b, a)

    eleza test_tb_2(self):
        b = """eleza foo():
                    a = 5
                    ashiria Exception, 5, 6
                    b = 6"""
        a = """eleza foo():
                    a = 5
                    ashiria Exception(5).with_traceback(6)
                    b = 6"""
        self.check(b, a)

    eleza test_tb_3(self):
        b = """eleza foo():
                    ashiria Exception,5,6"""
        a = """eleza foo():
                    ashiria Exception(5).with_traceback(6)"""
        self.check(b, a)

    eleza test_tb_4(self):
        b = """eleza foo():
                    a = 5
                    ashiria Exception,5,6
                    b = 6"""
        a = """eleza foo():
                    a = 5
                    ashiria Exception(5).with_traceback(6)
                    b = 6"""
        self.check(b, a)

    eleza test_tb_5(self):
        b = """eleza foo():
                    ashiria Exception, (5, 6, 7), 6"""
        a = """eleza foo():
                    ashiria Exception(5, 6, 7).with_traceback(6)"""
        self.check(b, a)

    eleza test_tb_6(self):
        b = """eleza foo():
                    a = 5
                    ashiria Exception, (5, 6, 7), 6
                    b = 6"""
        a = """eleza foo():
                    a = 5
                    ashiria Exception(5, 6, 7).with_traceback(6)
                    b = 6"""
        self.check(b, a)

kundi Test_throw(FixerTestCase):
    fixer = "throw"

    eleza test_1(self):
        b = """g.throw(Exception, 5)"""
        a = """g.throw(Exception(5))"""
        self.check(b, a)

    eleza test_2(self):
        b = """g.throw(Exception,5)"""
        a = """g.throw(Exception(5))"""
        self.check(b, a)

    eleza test_3(self):
        b = """g.throw(Exception, (5, 6, 7))"""
        a = """g.throw(Exception(5, 6, 7))"""
        self.check(b, a)

    eleza test_4(self):
        b = """5 + g.throw(Exception, 5)"""
        a = """5 + g.throw(Exception(5))"""
        self.check(b, a)

    # These should produce warnings

    eleza test_warn_1(self):
        s = """g.throw("foo")"""
        self.warns_unchanged(s, "Python 3 does sio support string exceptions")

    eleza test_warn_2(self):
        s = """g.throw("foo", 5)"""
        self.warns_unchanged(s, "Python 3 does sio support string exceptions")

    eleza test_warn_3(self):
        s = """g.throw("foo", 5, 6)"""
        self.warns_unchanged(s, "Python 3 does sio support string exceptions")

    # These should sio be touched

    eleza test_untouched_1(self):
        s = """g.throw(Exception)"""
        self.unchanged(s)

    eleza test_untouched_2(self):
        s = """g.throw(Exception(5, 6))"""
        self.unchanged(s)

    eleza test_untouched_3(self):
        s = """5 + g.throw(Exception(5, 6))"""
        self.unchanged(s)

    # These should result kwenye traceback-assignment

    eleza test_tb_1(self):
        b = """eleza foo():
                    g.throw(Exception, 5, 6)"""
        a = """eleza foo():
                    g.throw(Exception(5).with_traceback(6))"""
        self.check(b, a)

    eleza test_tb_2(self):
        b = """eleza foo():
                    a = 5
                    g.throw(Exception, 5, 6)
                    b = 6"""
        a = """eleza foo():
                    a = 5
                    g.throw(Exception(5).with_traceback(6))
                    b = 6"""
        self.check(b, a)

    eleza test_tb_3(self):
        b = """eleza foo():
                    g.throw(Exception,5,6)"""
        a = """eleza foo():
                    g.throw(Exception(5).with_traceback(6))"""
        self.check(b, a)

    eleza test_tb_4(self):
        b = """eleza foo():
                    a = 5
                    g.throw(Exception,5,6)
                    b = 6"""
        a = """eleza foo():
                    a = 5
                    g.throw(Exception(5).with_traceback(6))
                    b = 6"""
        self.check(b, a)

    eleza test_tb_5(self):
        b = """eleza foo():
                    g.throw(Exception, (5, 6, 7), 6)"""
        a = """eleza foo():
                    g.throw(Exception(5, 6, 7).with_traceback(6))"""
        self.check(b, a)

    eleza test_tb_6(self):
        b = """eleza foo():
                    a = 5
                    g.throw(Exception, (5, 6, 7), 6)
                    b = 6"""
        a = """eleza foo():
                    a = 5
                    g.throw(Exception(5, 6, 7).with_traceback(6))
                    b = 6"""
        self.check(b, a)

    eleza test_tb_7(self):
        b = """eleza foo():
                    a + g.throw(Exception, 5, 6)"""
        a = """eleza foo():
                    a + g.throw(Exception(5).with_traceback(6))"""
        self.check(b, a)

    eleza test_tb_8(self):
        b = """eleza foo():
                    a = 5
                    a + g.throw(Exception, 5, 6)
                    b = 6"""
        a = """eleza foo():
                    a = 5
                    a + g.throw(Exception(5).with_traceback(6))
                    b = 6"""
        self.check(b, a)

kundi Test_long(FixerTestCase):
    fixer = "long"

    eleza test_1(self):
        b = """x = long(x)"""
        a = """x = int(x)"""
        self.check(b, a)

    eleza test_2(self):
        b = """y = isinstance(x, long)"""
        a = """y = isinstance(x, int)"""
        self.check(b, a)

    eleza test_3(self):
        b = """z = type(x) kwenye (int, long)"""
        a = """z = type(x) kwenye (int, int)"""
        self.check(b, a)

    eleza test_unchanged(self):
        s = """long = Kweli"""
        self.unchanged(s)

        s = """s.long = Kweli"""
        self.unchanged(s)

        s = """eleza long(): pita"""
        self.unchanged(s)

        s = """kundi long(): pita"""
        self.unchanged(s)

        s = """eleza f(long): pita"""
        self.unchanged(s)

        s = """eleza f(g, long): pita"""
        self.unchanged(s)

        s = """eleza f(x, long=Kweli): pita"""
        self.unchanged(s)

    eleza test_prefix_preservation(self):
        b = """x =   long(  x  )"""
        a = """x =   int(  x  )"""
        self.check(b, a)


kundi Test_execfile(FixerTestCase):
    fixer = "execfile"

    eleza test_conversion(self):
        b = """execfile("fn")"""
        a = """exec(compile(open("fn", "rb").read(), "fn", 'exec'))"""
        self.check(b, a)

        b = """execfile("fn", glob)"""
        a = """exec(compile(open("fn", "rb").read(), "fn", 'exec'), glob)"""
        self.check(b, a)

        b = """execfile("fn", glob, loc)"""
        a = """exec(compile(open("fn", "rb").read(), "fn", 'exec'), glob, loc)"""
        self.check(b, a)

        b = """execfile("fn", globals=glob)"""
        a = """exec(compile(open("fn", "rb").read(), "fn", 'exec'), globals=glob)"""
        self.check(b, a)

        b = """execfile("fn", locals=loc)"""
        a = """exec(compile(open("fn", "rb").read(), "fn", 'exec'), locals=loc)"""
        self.check(b, a)

        b = """execfile("fn", globals=glob, locals=loc)"""
        a = """exec(compile(open("fn", "rb").read(), "fn", 'exec'), globals=glob, locals=loc)"""
        self.check(b, a)

    eleza test_spacing(self):
        b = """execfile( "fn" )"""
        a = """exec(compile(open( "fn", "rb" ).read(), "fn", 'exec'))"""
        self.check(b, a)

        b = """execfile("fn",  globals = glob)"""
        a = """exec(compile(open("fn", "rb").read(), "fn", 'exec'),  globals = glob)"""
        self.check(b, a)


kundi Test_isinstance(FixerTestCase):
    fixer = "isinstance"

    eleza test_remove_multiple_items(self):
        b = """isinstance(x, (int, int, int))"""
        a = """isinstance(x, int)"""
        self.check(b, a)

        b = """isinstance(x, (int, float, int, int, float))"""
        a = """isinstance(x, (int, float))"""
        self.check(b, a)

        b = """isinstance(x, (int, float, int, int, float, str))"""
        a = """isinstance(x, (int, float, str))"""
        self.check(b, a)

        b = """isinstance(foo() + bar(), (x(), y(), x(), int, int))"""
        a = """isinstance(foo() + bar(), (x(), y(), x(), int))"""
        self.check(b, a)

    eleza test_prefix_preservation(self):
        b = """ikiwa    isinstance(  foo(), (  bar, bar, baz )) : pita"""
        a = """ikiwa    isinstance(  foo(), (  bar, baz )) : pita"""
        self.check(b, a)

    eleza test_unchanged(self):
        self.unchanged("isinstance(x, (str, int))")

kundi Test_dict(FixerTestCase):
    fixer = "dict"

    eleza test_prefix_preservation(self):
        b = "ikiwa   d. keys  (  )  : pita"
        a = "ikiwa   list(d. keys  (  ))  : pita"
        self.check(b, a)

        b = "ikiwa   d. items  (  )  : pita"
        a = "ikiwa   list(d. items  (  ))  : pita"
        self.check(b, a)

        b = "ikiwa   d. iterkeys  ( )  : pita"
        a = "ikiwa   iter(d. keys  ( ))  : pita"
        self.check(b, a)

        b = "[i kila i kwenye    d.  iterkeys(  )  ]"
        a = "[i kila i kwenye    d.  keys(  )  ]"
        self.check(b, a)

        b = "ikiwa   d. viewkeys  ( )  : pita"
        a = "ikiwa   d. keys  ( )  : pita"
        self.check(b, a)

        b = "[i kila i kwenye    d.  viewkeys(  )  ]"
        a = "[i kila i kwenye    d.  keys(  )  ]"
        self.check(b, a)

    eleza test_trailing_comment(self):
        b = "d.keys() # foo"
        a = "list(d.keys()) # foo"
        self.check(b, a)

        b = "d.items()  # foo"
        a = "list(d.items())  # foo"
        self.check(b, a)

        b = "d.iterkeys()  # foo"
        a = "iter(d.keys())  # foo"
        self.check(b, a)

        b = """[i kila i kwenye d.iterkeys() # foo
               ]"""
        a = """[i kila i kwenye d.keys() # foo
               ]"""
        self.check(b, a)

        b = """[i kila i kwenye d.iterkeys() # foo
               ]"""
        a = """[i kila i kwenye d.keys() # foo
               ]"""
        self.check(b, a)

        b = "d.viewitems()  # foo"
        a = "d.items()  # foo"
        self.check(b, a)

    eleza test_unchanged(self):
        kila wrapper kwenye fixer_util.consuming_calls:
            s = "s = %s(d.keys())" % wrapper
            self.unchanged(s)

            s = "s = %s(d.values())" % wrapper
            self.unchanged(s)

            s = "s = %s(d.items())" % wrapper
            self.unchanged(s)

    eleza test_01(self):
        b = "d.keys()"
        a = "list(d.keys())"
        self.check(b, a)

        b = "a[0].foo().keys()"
        a = "list(a[0].foo().keys())"
        self.check(b, a)

    eleza test_02(self):
        b = "d.items()"
        a = "list(d.items())"
        self.check(b, a)

    eleza test_03(self):
        b = "d.values()"
        a = "list(d.values())"
        self.check(b, a)

    eleza test_04(self):
        b = "d.iterkeys()"
        a = "iter(d.keys())"
        self.check(b, a)

    eleza test_05(self):
        b = "d.iteritems()"
        a = "iter(d.items())"
        self.check(b, a)

    eleza test_06(self):
        b = "d.itervalues()"
        a = "iter(d.values())"
        self.check(b, a)

    eleza test_07(self):
        s = "list(d.keys())"
        self.unchanged(s)

    eleza test_08(self):
        s = "sorted(d.keys())"
        self.unchanged(s)

    eleza test_09(self):
        b = "iter(d.keys())"
        a = "iter(list(d.keys()))"
        self.check(b, a)

    eleza test_10(self):
        b = "foo(d.keys())"
        a = "foo(list(d.keys()))"
        self.check(b, a)

    eleza test_11(self):
        b = "kila i kwenye d.keys(): print i"
        a = "kila i kwenye list(d.keys()): print i"
        self.check(b, a)

    eleza test_12(self):
        b = "kila i kwenye d.iterkeys(): print i"
        a = "kila i kwenye d.keys(): print i"
        self.check(b, a)

    eleza test_13(self):
        b = "[i kila i kwenye d.keys()]"
        a = "[i kila i kwenye list(d.keys())]"
        self.check(b, a)

    eleza test_14(self):
        b = "[i kila i kwenye d.iterkeys()]"
        a = "[i kila i kwenye d.keys()]"
        self.check(b, a)

    eleza test_15(self):
        b = "(i kila i kwenye d.keys())"
        a = "(i kila i kwenye list(d.keys()))"
        self.check(b, a)

    eleza test_16(self):
        b = "(i kila i kwenye d.iterkeys())"
        a = "(i kila i kwenye d.keys())"
        self.check(b, a)

    eleza test_17(self):
        b = "iter(d.iterkeys())"
        a = "iter(d.keys())"
        self.check(b, a)

    eleza test_18(self):
        b = "list(d.iterkeys())"
        a = "list(d.keys())"
        self.check(b, a)

    eleza test_19(self):
        b = "sorted(d.iterkeys())"
        a = "sorted(d.keys())"
        self.check(b, a)

    eleza test_20(self):
        b = "foo(d.iterkeys())"
        a = "foo(iter(d.keys()))"
        self.check(b, a)

    eleza test_21(self):
        b = "print h.iterkeys().next()"
        a = "print iter(h.keys()).next()"
        self.check(b, a)

    eleza test_22(self):
        b = "print h.keys()[0]"
        a = "print list(h.keys())[0]"
        self.check(b, a)

    eleza test_23(self):
        b = "print list(h.iterkeys().next())"
        a = "print list(iter(h.keys()).next())"
        self.check(b, a)

    eleza test_24(self):
        b = "kila x kwenye h.keys()[0]: print x"
        a = "kila x kwenye list(h.keys())[0]: print x"
        self.check(b, a)

    eleza test_25(self):
        b = "d.viewkeys()"
        a = "d.keys()"
        self.check(b, a)

    eleza test_26(self):
        b = "d.viewitems()"
        a = "d.items()"
        self.check(b, a)

    eleza test_27(self):
        b = "d.viewvalues()"
        a = "d.values()"
        self.check(b, a)

    eleza test_28(self):
        b = "[i kila i kwenye d.viewkeys()]"
        a = "[i kila i kwenye d.keys()]"
        self.check(b, a)

    eleza test_29(self):
        b = "(i kila i kwenye d.viewkeys())"
        a = "(i kila i kwenye d.keys())"
        self.check(b, a)

    eleza test_30(self):
        b = "iter(d.viewkeys())"
        a = "iter(d.keys())"
        self.check(b, a)

    eleza test_31(self):
        b = "list(d.viewkeys())"
        a = "list(d.keys())"
        self.check(b, a)

    eleza test_32(self):
        b = "sorted(d.viewkeys())"
        a = "sorted(d.keys())"
        self.check(b, a)

kundi Test_xrange(FixerTestCase):
    fixer = "xrange"

    eleza test_prefix_preservation(self):
        b = """x =    xrange(  10  )"""
        a = """x =    range(  10  )"""
        self.check(b, a)

        b = """x = xrange(  1  ,  10   )"""
        a = """x = range(  1  ,  10   )"""
        self.check(b, a)

        b = """x = xrange(  0  ,  10 ,  2 )"""
        a = """x = range(  0  ,  10 ,  2 )"""
        self.check(b, a)

    eleza test_single_arg(self):
        b = """x = xrange(10)"""
        a = """x = range(10)"""
        self.check(b, a)

    eleza test_two_args(self):
        b = """x = xrange(1, 10)"""
        a = """x = range(1, 10)"""
        self.check(b, a)

    eleza test_three_args(self):
        b = """x = xrange(0, 10, 2)"""
        a = """x = range(0, 10, 2)"""
        self.check(b, a)

    eleza test_wrap_in_list(self):
        b = """x = range(10, 3, 9)"""
        a = """x = list(range(10, 3, 9))"""
        self.check(b, a)

        b = """x = foo(range(10, 3, 9))"""
        a = """x = foo(list(range(10, 3, 9)))"""
        self.check(b, a)

        b = """x = range(10, 3, 9) + [4]"""
        a = """x = list(range(10, 3, 9)) + [4]"""
        self.check(b, a)

        b = """x = range(10)[::-1]"""
        a = """x = list(range(10))[::-1]"""
        self.check(b, a)

        b = """x = range(10)  [3]"""
        a = """x = list(range(10))  [3]"""
        self.check(b, a)

    eleza test_xrange_in_for(self):
        b = """kila i kwenye xrange(10):\n    j=i"""
        a = """kila i kwenye range(10):\n    j=i"""
        self.check(b, a)

        b = """[i kila i kwenye xrange(10)]"""
        a = """[i kila i kwenye range(10)]"""
        self.check(b, a)

    eleza test_range_in_for(self):
        self.unchanged("kila i kwenye range(10): pita")
        self.unchanged("[i kila i kwenye range(10)]")

    eleza test_in_contains_test(self):
        self.unchanged("x kwenye range(10, 3, 9)")

    eleza test_in_consuming_context(self):
        kila call kwenye fixer_util.consuming_calls:
            self.unchanged("a = %s(range(10))" % call)

kundi Test_xrange_with_reduce(FixerTestCase):

    eleza setUp(self):
        super(Test_xrange_with_reduce, self).setUp(["xrange", "reduce"])

    eleza test_double_transform(self):
        b = """reduce(x, xrange(5))"""
        a = """kutoka functools agiza reduce
reduce(x, range(5))"""
        self.check(b, a)

kundi Test_raw_input(FixerTestCase):
    fixer = "raw_input"

    eleza test_prefix_preservation(self):
        b = """x =    raw_input(   )"""
        a = """x =    input(   )"""
        self.check(b, a)

        b = """x = raw_input(   ''   )"""
        a = """x = input(   ''   )"""
        self.check(b, a)

    eleza test_1(self):
        b = """x = raw_input()"""
        a = """x = input()"""
        self.check(b, a)

    eleza test_2(self):
        b = """x = raw_input('')"""
        a = """x = input('')"""
        self.check(b, a)

    eleza test_3(self):
        b = """x = raw_input('prompt')"""
        a = """x = input('prompt')"""
        self.check(b, a)

    eleza test_4(self):
        b = """x = raw_input(foo(a) + 6)"""
        a = """x = input(foo(a) + 6)"""
        self.check(b, a)

    eleza test_5(self):
        b = """x = raw_input(invite).split()"""
        a = """x = input(invite).split()"""
        self.check(b, a)

    eleza test_6(self):
        b = """x = raw_input(invite) . split ()"""
        a = """x = input(invite) . split ()"""
        self.check(b, a)

    eleza test_8(self):
        b = "x = int(raw_input())"
        a = "x = int(input())"
        self.check(b, a)

kundi Test_funcattrs(FixerTestCase):
    fixer = "funcattrs"

    attrs = ["closure", "doc", "name", "defaults", "code", "globals", "dict"]

    eleza test(self):
        kila attr kwenye self.attrs:
            b = "a.func_%s" % attr
            a = "a.__%s__" % attr
            self.check(b, a)

            b = "self.foo.func_%s.foo_bar" % attr
            a = "self.foo.__%s__.foo_bar" % attr
            self.check(b, a)

    eleza test_unchanged(self):
        kila attr kwenye self.attrs:
            s = "foo(func_%s + 5)" % attr
            self.unchanged(s)

            s = "f(foo.__%s__)" % attr
            self.unchanged(s)

            s = "f(foo.__%s__.foo)" % attr
            self.unchanged(s)

kundi Test_xreadlines(FixerTestCase):
    fixer = "xreadlines"

    eleza test_call(self):
        b = "kila x kwenye f.xreadlines(): pita"
        a = "kila x kwenye f: pita"
        self.check(b, a)

        b = "kila x kwenye foo().xreadlines(): pita"
        a = "kila x kwenye foo(): pita"
        self.check(b, a)

        b = "kila x kwenye (5 + foo()).xreadlines(): pita"
        a = "kila x kwenye (5 + foo()): pita"
        self.check(b, a)

    eleza test_attr_ref(self):
        b = "foo(f.xreadlines + 5)"
        a = "foo(f.__iter__ + 5)"
        self.check(b, a)

        b = "foo(f().xreadlines + 5)"
        a = "foo(f().__iter__ + 5)"
        self.check(b, a)

        b = "foo((5 + f()).xreadlines + 5)"
        a = "foo((5 + f()).__iter__ + 5)"
        self.check(b, a)

    eleza test_unchanged(self):
        s = "kila x kwenye f.xreadlines(5): pita"
        self.unchanged(s)

        s = "kila x kwenye f.xreadlines(k=5): pita"
        self.unchanged(s)

        s = "kila x kwenye f.xreadlines(*k, **v): pita"
        self.unchanged(s)

        s = "foo(xreadlines)"
        self.unchanged(s)


kundi ImportsFixerTests:

    eleza test_import_module(self):
        kila old, new kwenye self.modules.items():
            b = "agiza %s" % old
            a = "agiza %s" % new
            self.check(b, a)

            b = "agiza foo, %s, bar" % old
            a = "agiza foo, %s, bar" % new
            self.check(b, a)

    eleza test_import_kutoka(self):
        kila old, new kwenye self.modules.items():
            b = "kutoka %s agiza foo" % old
            a = "kutoka %s agiza foo" % new
            self.check(b, a)

            b = "kutoka %s agiza foo, bar" % old
            a = "kutoka %s agiza foo, bar" % new
            self.check(b, a)

            b = "kutoka %s agiza (yes, no)" % old
            a = "kutoka %s agiza (yes, no)" % new
            self.check(b, a)

    eleza test_import_module_as(self):
        kila old, new kwenye self.modules.items():
            b = "agiza %s kama foo_bar" % old
            a = "agiza %s kama foo_bar" % new
            self.check(b, a)

            b = "agiza %s kama foo_bar" % old
            a = "agiza %s kama foo_bar" % new
            self.check(b, a)

    eleza test_import_from_as(self):
        kila old, new kwenye self.modules.items():
            b = "kutoka %s agiza foo kama bar" % old
            a = "kutoka %s agiza foo kama bar" % new
            self.check(b, a)

    eleza test_star(self):
        kila old, new kwenye self.modules.items():
            b = "kutoka %s agiza *" % old
            a = "kutoka %s agiza *" % new
            self.check(b, a)

    eleza test_import_module_usage(self):
        kila old, new kwenye self.modules.items():
            b = """
                agiza %s
                foo(%s.bar)
                """ % (old, old)
            a = """
                agiza %s
                foo(%s.bar)
                """ % (new, new)
            self.check(b, a)

            b = """
                kutoka %s agiza x
                %s = 23
                """ % (old, old)
            a = """
                kutoka %s agiza x
                %s = 23
                """ % (new, old)
            self.check(b, a)

            s = """
                eleza f():
                    %s.method()
                """ % (old,)
            self.unchanged(s)

            # test nested usage
            b = """
                agiza %s
                %s.bar(%s.foo)
                """ % (old, old, old)
            a = """
                agiza %s
                %s.bar(%s.foo)
                """ % (new, new, new)
            self.check(b, a)

            b = """
                agiza %s
                x.%s
                """ % (old, old)
            a = """
                agiza %s
                x.%s
                """ % (new, old)
            self.check(b, a)


kundi Test_agizas(FixerTestCase, ImportsFixerTests):
    fixer = "agizas"
    kutoka ..fixes.fix_agizas agiza MAPPING kama modules

    eleza test_multiple_agizas(self):
        b = """agiza urlparse, cStringIO"""
        a = """agiza urllib.parse, io"""
        self.check(b, a)

    eleza test_multiple_agizas_as(self):
        b = """
            agiza copy_reg kama bar, HTMLParser kama foo, urlparse
            s = urlparse.spam(bar.foo())
            """
        a = """
            agiza copyreg kama bar, html.parser kama foo, urllib.parse
            s = urllib.parse.spam(bar.foo())
            """
        self.check(b, a)


kundi Test_agizas2(FixerTestCase, ImportsFixerTests):
    fixer = "agizas2"
    kutoka ..fixes.fix_agizas2 agiza MAPPING kama modules


kundi Test_agizas_fixer_order(FixerTestCase, ImportsFixerTests):

    eleza setUp(self):
        super(Test_agizas_fixer_order, self).setUp(['agizas', 'agizas2'])
        kutoka ..fixes.fix_agizas2 agiza MAPPING kama mapping2
        self.modules = mapping2.copy()
        kutoka ..fixes.fix_agizas agiza MAPPING kama mapping1
        kila key kwenye ('dbhash', 'dumbdbm', 'dbm', 'gdbm'):
            self.modules[key] = mapping1[key]

    eleza test_after_local_agizas_refactoring(self):
        kila fix kwenye ("agizas", "agizas2"):
            self.fixer = fix
            self.assert_runs_after("agiza")


kundi Test_urllib(FixerTestCase):
    fixer = "urllib"
    kutoka ..fixes.fix_urllib agiza MAPPING kama modules

    eleza test_import_module(self):
        kila old, changes kwenye self.modules.items():
            b = "agiza %s" % old
            a = "agiza %s" % ", ".join(map(itemgetter(0), changes))
            self.check(b, a)

    eleza test_import_kutoka(self):
        kila old, changes kwenye self.modules.items():
            all_members = []
            kila new, members kwenye changes:
                kila member kwenye members:
                    all_members.append(member)
                    b = "kutoka %s agiza %s" % (old, member)
                    a = "kutoka %s agiza %s" % (new, member)
                    self.check(b, a)

                    s = "kutoka foo agiza %s" % member
                    self.unchanged(s)

                b = "kutoka %s agiza %s" % (old, ", ".join(members))
                a = "kutoka %s agiza %s" % (new, ", ".join(members))
                self.check(b, a)

                s = "kutoka foo agiza %s" % ", ".join(members)
                self.unchanged(s)

            # test the komaing of a module into multiple replacements
            b = "kutoka %s agiza %s" % (old, ", ".join(all_members))
            a = "\n".join(["kutoka %s agiza %s" % (new, ", ".join(members))
                            kila (new, members) kwenye changes])
            self.check(b, a)

    eleza test_import_module_as(self):
        kila old kwenye self.modules:
            s = "agiza %s kama foo" % old
            self.warns_unchanged(s, "This module ni now multiple modules")

    eleza test_import_from_as(self):
        kila old, changes kwenye self.modules.items():
            kila new, members kwenye changes:
                kila member kwenye members:
                    b = "kutoka %s agiza %s kama foo_bar" % (old, member)
                    a = "kutoka %s agiza %s kama foo_bar" % (new, member)
                    self.check(b, a)
                    b = "kutoka %s agiza %s kama blah, %s" % (old, member, member)
                    a = "kutoka %s agiza %s kama blah, %s" % (new, member, member)
                    self.check(b, a)

    eleza test_star(self):
        kila old kwenye self.modules:
            s = "kutoka %s agiza *" % old
            self.warns_unchanged(s, "Cannot handle star agizas")

    eleza test_indented(self):
        b = """
eleza foo():
    kutoka urllib agiza urlencode, urlopen
"""
        a = """
eleza foo():
    kutoka urllib.parse agiza urlencode
    kutoka urllib.request agiza urlopen
"""
        self.check(b, a)

        b = """
eleza foo():
    other()
    kutoka urllib agiza urlencode, urlopen
"""
        a = """
eleza foo():
    other()
    kutoka urllib.parse agiza urlencode
    kutoka urllib.request agiza urlopen
"""
        self.check(b, a)



    eleza test_import_module_usage(self):
        kila old, changes kwenye self.modules.items():
            kila new, members kwenye changes:
                kila member kwenye members:
                    new_agiza = ", ".join([n kila (n, mems)
                                            kwenye self.modules[old]])
                    b = """
                        agiza %s
                        foo(%s.%s)
                        """ % (old, old, member)
                    a = """
                        agiza %s
                        foo(%s.%s)
                        """ % (new_agiza, new, member)
                    self.check(b, a)
                    b = """
                        agiza %s
                        %s.%s(%s.%s)
                        """ % (old, old, member, old, member)
                    a = """
                        agiza %s
                        %s.%s(%s.%s)
                        """ % (new_agiza, new, member, new, member)
                    self.check(b, a)


kundi Test_input(FixerTestCase):
    fixer = "input"

    eleza test_prefix_preservation(self):
        b = """x =   input(   )"""
        a = """x =   eval(input(   ))"""
        self.check(b, a)

        b = """x = input(   ''   )"""
        a = """x = eval(input(   ''   ))"""
        self.check(b, a)

    eleza test_trailing_comment(self):
        b = """x = input()  #  foo"""
        a = """x = eval(input())  #  foo"""
        self.check(b, a)

    eleza test_idempotency(self):
        s = """x = eval(input())"""
        self.unchanged(s)

        s = """x = eval(input(''))"""
        self.unchanged(s)

        s = """x = eval(input(foo(5) + 9))"""
        self.unchanged(s)

    eleza test_1(self):
        b = """x = input()"""
        a = """x = eval(input())"""
        self.check(b, a)

    eleza test_2(self):
        b = """x = input('')"""
        a = """x = eval(input(''))"""
        self.check(b, a)

    eleza test_3(self):
        b = """x = input('prompt')"""
        a = """x = eval(input('prompt'))"""
        self.check(b, a)

    eleza test_4(self):
        b = """x = input(foo(5) + 9)"""
        a = """x = eval(input(foo(5) + 9))"""
        self.check(b, a)

kundi Test_tuple_params(FixerTestCase):
    fixer = "tuple_params"

    eleza test_unchanged_1(self):
        s = """eleza foo(): pita"""
        self.unchanged(s)

    eleza test_unchanged_2(self):
        s = """eleza foo(a, b, c): pita"""
        self.unchanged(s)

    eleza test_unchanged_3(self):
        s = """eleza foo(a=3, b=4, c=5): pita"""
        self.unchanged(s)

    eleza test_1(self):
        b = """
            eleza foo(((a, b), c)):
                x = 5"""

        a = """
            eleza foo(xxx_todo_changeme):
                ((a, b), c) = xxx_todo_changeme
                x = 5"""
        self.check(b, a)

    eleza test_2(self):
        b = """
            eleza foo(((a, b), c), d):
                x = 5"""

        a = """
            eleza foo(xxx_todo_changeme, d):
                ((a, b), c) = xxx_todo_changeme
                x = 5"""
        self.check(b, a)

    eleza test_3(self):
        b = """
            eleza foo(((a, b), c), d) -> e:
                x = 5"""

        a = """
            eleza foo(xxx_todo_changeme, d) -> e:
                ((a, b), c) = xxx_todo_changeme
                x = 5"""
        self.check(b, a)

    eleza test_semicolon(self):
        b = """
            eleza foo(((a, b), c)): x = 5; y = 7"""

        a = """
            eleza foo(xxx_todo_changeme): ((a, b), c) = xxx_todo_changeme; x = 5; y = 7"""
        self.check(b, a)

    eleza test_keywords(self):
        b = """
            eleza foo(((a, b), c), d, e=5) -> z:
                x = 5"""

        a = """
            eleza foo(xxx_todo_changeme, d, e=5) -> z:
                ((a, b), c) = xxx_todo_changeme
                x = 5"""
        self.check(b, a)

    eleza test_varargs(self):
        b = """
            eleza foo(((a, b), c), d, *vargs, **kwargs) -> z:
                x = 5"""

        a = """
            eleza foo(xxx_todo_changeme, d, *vargs, **kwargs) -> z:
                ((a, b), c) = xxx_todo_changeme
                x = 5"""
        self.check(b, a)

    eleza test_multi_1(self):
        b = """
            eleza foo(((a, b), c), (d, e, f)) -> z:
                x = 5"""

        a = """
            eleza foo(xxx_todo_changeme, xxx_todo_changeme1) -> z:
                ((a, b), c) = xxx_todo_changeme
                (d, e, f) = xxx_todo_changeme1
                x = 5"""
        self.check(b, a)

    eleza test_multi_2(self):
        b = """
            eleza foo(x, ((a, b), c), d, (e, f, g), y) -> z:
                x = 5"""

        a = """
            eleza foo(x, xxx_todo_changeme, d, xxx_todo_changeme1, y) -> z:
                ((a, b), c) = xxx_todo_changeme
                (e, f, g) = xxx_todo_changeme1
                x = 5"""
        self.check(b, a)

    eleza test_docstring(self):
        b = """
            eleza foo(((a, b), c), (d, e, f)) -> z:
                "foo foo foo foo"
                x = 5"""

        a = """
            eleza foo(xxx_todo_changeme, xxx_todo_changeme1) -> z:
                "foo foo foo foo"
                ((a, b), c) = xxx_todo_changeme
                (d, e, f) = xxx_todo_changeme1
                x = 5"""
        self.check(b, a)

    eleza test_lambda_no_change(self):
        s = """lambda x: x + 5"""
        self.unchanged(s)

    eleza test_lambda_parens_single_arg(self):
        b = """lambda (x): x + 5"""
        a = """lambda x: x + 5"""
        self.check(b, a)

        b = """lambda(x): x + 5"""
        a = """lambda x: x + 5"""
        self.check(b, a)

        b = """lambda ((((x)))): x + 5"""
        a = """lambda x: x + 5"""
        self.check(b, a)

        b = """lambda((((x)))): x + 5"""
        a = """lambda x: x + 5"""
        self.check(b, a)

    eleza test_lambda_simple(self):
        b = """lambda (x, y): x + f(y)"""
        a = """lambda x_y: x_y[0] + f(x_y[1])"""
        self.check(b, a)

        b = """lambda(x, y): x + f(y)"""
        a = """lambda x_y: x_y[0] + f(x_y[1])"""
        self.check(b, a)

        b = """lambda (((x, y))): x + f(y)"""
        a = """lambda x_y: x_y[0] + f(x_y[1])"""
        self.check(b, a)

        b = """lambda(((x, y))): x + f(y)"""
        a = """lambda x_y: x_y[0] + f(x_y[1])"""
        self.check(b, a)

    eleza test_lambda_one_tuple(self):
        b = """lambda (x,): x + f(x)"""
        a = """lambda x1: x1[0] + f(x1[0])"""
        self.check(b, a)

        b = """lambda (((x,))): x + f(x)"""
        a = """lambda x1: x1[0] + f(x1[0])"""
        self.check(b, a)

    eleza test_lambda_simple_multi_use(self):
        b = """lambda (x, y): x + x + f(x) + x"""
        a = """lambda x_y: x_y[0] + x_y[0] + f(x_y[0]) + x_y[0]"""
        self.check(b, a)

    eleza test_lambda_simple_reverse(self):
        b = """lambda (x, y): y + x"""
        a = """lambda x_y: x_y[1] + x_y[0]"""
        self.check(b, a)

    eleza test_lambda_nested(self):
        b = """lambda (x, (y, z)): x + y + z"""
        a = """lambda x_y_z: x_y_z[0] + x_y_z[1][0] + x_y_z[1][1]"""
        self.check(b, a)

        b = """lambda (((x, (y, z)))): x + y + z"""
        a = """lambda x_y_z: x_y_z[0] + x_y_z[1][0] + x_y_z[1][1]"""
        self.check(b, a)

    eleza test_lambda_nested_multi_use(self):
        b = """lambda (x, (y, z)): x + y + f(y)"""
        a = """lambda x_y_z: x_y_z[0] + x_y_z[1][0] + f(x_y_z[1][0])"""
        self.check(b, a)

kundi Test_methodattrs(FixerTestCase):
    fixer = "methodattrs"

    attrs = ["func", "self", "class"]

    eleza test(self):
        kila attr kwenye self.attrs:
            b = "a.im_%s" % attr
            ikiwa attr == "class":
                a = "a.__self__.__class__"
            isipokua:
                a = "a.__%s__" % attr
            self.check(b, a)

            b = "self.foo.im_%s.foo_bar" % attr
            ikiwa attr == "class":
                a = "self.foo.__self__.__class__.foo_bar"
            isipokua:
                a = "self.foo.__%s__.foo_bar" % attr
            self.check(b, a)

    eleza test_unchanged(self):
        kila attr kwenye self.attrs:
            s = "foo(im_%s + 5)" % attr
            self.unchanged(s)

            s = "f(foo.__%s__)" % attr
            self.unchanged(s)

            s = "f(foo.__%s__.foo)" % attr
            self.unchanged(s)

kundi Test_next(FixerTestCase):
    fixer = "next"

    eleza test_1(self):
        b = """it.next()"""
        a = """next(it)"""
        self.check(b, a)

    eleza test_2(self):
        b = """a.b.c.d.next()"""
        a = """next(a.b.c.d)"""
        self.check(b, a)

    eleza test_3(self):
        b = """(a + b).next()"""
        a = """next((a + b))"""
        self.check(b, a)

    eleza test_4(self):
        b = """a().next()"""
        a = """next(a())"""
        self.check(b, a)

    eleza test_5(self):
        b = """a().next() + b"""
        a = """next(a()) + b"""
        self.check(b, a)

    eleza test_6(self):
        b = """c(      a().next() + b)"""
        a = """c(      next(a()) + b)"""
        self.check(b, a)

    eleza test_prefix_preservation_1(self):
        b = """
            kila a kwenye b:
                foo(a)
                a.next()
            """
        a = """
            kila a kwenye b:
                foo(a)
                next(a)
            """
        self.check(b, a)

    eleza test_prefix_preservation_2(self):
        b = """
            kila a kwenye b:
                foo(a) # abc
                # def
                a.next()
            """
        a = """
            kila a kwenye b:
                foo(a) # abc
                # def
                next(a)
            """
        self.check(b, a)

    eleza test_prefix_preservation_3(self):
        b = """
            next = 5
            kila a kwenye b:
                foo(a)
                a.next()
            """
        a = """
            next = 5
            kila a kwenye b:
                foo(a)
                a.__next__()
            """
        self.check(b, a, ignore_warnings=Kweli)

    eleza test_prefix_preservation_4(self):
        b = """
            next = 5
            kila a kwenye b:
                foo(a) # abc
                # def
                a.next()
            """
        a = """
            next = 5
            kila a kwenye b:
                foo(a) # abc
                # def
                a.__next__()
            """
        self.check(b, a, ignore_warnings=Kweli)

    eleza test_prefix_preservation_5(self):
        b = """
            next = 5
            kila a kwenye b:
                foo(foo(a), # abc
                    a.next())
            """
        a = """
            next = 5
            kila a kwenye b:
                foo(foo(a), # abc
                    a.__next__())
            """
        self.check(b, a, ignore_warnings=Kweli)

    eleza test_prefix_preservation_6(self):
        b = """
            kila a kwenye b:
                foo(foo(a), # abc
                    a.next())
            """
        a = """
            kila a kwenye b:
                foo(foo(a), # abc
                    next(a))
            """
        self.check(b, a)

    eleza test_method_1(self):
        b = """
            kundi A:
                eleza next(self):
                    pita
            """
        a = """
            kundi A:
                eleza __next__(self):
                    pita
            """
        self.check(b, a)

    eleza test_method_2(self):
        b = """
            kundi A(object):
                eleza next(self):
                    pita
            """
        a = """
            kundi A(object):
                eleza __next__(self):
                    pita
            """
        self.check(b, a)

    eleza test_method_3(self):
        b = """
            kundi A:
                eleza next(x):
                    pita
            """
        a = """
            kundi A:
                eleza __next__(x):
                    pita
            """
        self.check(b, a)

    eleza test_method_4(self):
        b = """
            kundi A:
                eleza __init__(self, foo):
                    self.foo = foo

                eleza next(self):
                    pita

                eleza __iter__(self):
                    rudisha self
            """
        a = """
            kundi A:
                eleza __init__(self, foo):
                    self.foo = foo

                eleza __next__(self):
                    pita

                eleza __iter__(self):
                    rudisha self
            """
        self.check(b, a)

    eleza test_method_unchanged(self):
        s = """
            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.unchanged(s)

    eleza test_shadowing_assign_simple(self):
        s = """
            next = foo

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_assign_tuple_1(self):
        s = """
            (next, a) = foo

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_assign_tuple_2(self):
        s = """
            (a, (b, (next, c)), a) = foo

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_assign_list_1(self):
        s = """
            [next, a] = foo

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_assign_list_2(self):
        s = """
            [a, [b, [next, c]], a] = foo

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_builtin_assign(self):
        s = """
            eleza foo():
                __builtin__.next = foo

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_builtin_assign_in_tuple(self):
        s = """
            eleza foo():
                (a, __builtin__.next) = foo

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_builtin_assign_in_list(self):
        s = """
            eleza foo():
                [a, __builtin__.next] = foo

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_assign_to_next(self):
        s = """
            eleza foo():
                A.next = foo

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.unchanged(s)

    eleza test_assign_to_next_in_tuple(self):
        s = """
            eleza foo():
                (a, A.next) = foo

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.unchanged(s)

    eleza test_assign_to_next_in_list(self):
        s = """
            eleza foo():
                [a, A.next] = foo

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.unchanged(s)

    eleza test_shadowing_import_1(self):
        s = """
            agiza foo.bar kama next

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_import_2(self):
        s = """
            agiza bar, bar.foo kama next

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_import_3(self):
        s = """
            agiza bar, bar.foo kama next, baz

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_import_from_1(self):
        s = """
            kutoka x agiza next

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_import_from_2(self):
        s = """
            kutoka x.a agiza next

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_import_from_3(self):
        s = """
            kutoka x agiza a, next, b

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_import_from_4(self):
        s = """
            kutoka x.a agiza a, next, b

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_funcdef_1(self):
        s = """
            eleza next(a):
                pita

            kundi A:
                eleza next(self, a, b):
                    pita
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_funcdef_2(self):
        b = """
            eleza next(a):
                pita

            kundi A:
                eleza next(self):
                    pita

            it.next()
            """
        a = """
            eleza next(a):
                pita

            kundi A:
                eleza __next__(self):
                    pita

            it.__next__()
            """
        self.warns(b, a, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_global_1(self):
        s = """
            eleza f():
                global next
                next = 5
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_global_2(self):
        s = """
            eleza f():
                global a, next, b
                next = 5
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_for_simple(self):
        s = """
            kila next kwenye it():
                pita

            b = 5
            c = 6
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_for_tuple_1(self):
        s = """
            kila next, b kwenye it():
                pita

            b = 5
            c = 6
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_shadowing_for_tuple_2(self):
        s = """
            kila a, (next, c), b kwenye it():
                pita

            b = 5
            c = 6
            """
        self.warns_unchanged(s, "Calls to builtin next() possibly shadowed")

    eleza test_noncall_access_1(self):
        b = """gnext = g.next"""
        a = """gnext = g.__next__"""
        self.check(b, a)

    eleza test_noncall_access_2(self):
        b = """f(g.next + 5)"""
        a = """f(g.__next__ + 5)"""
        self.check(b, a)

    eleza test_noncall_access_3(self):
        b = """f(g().next + 5)"""
        a = """f(g().__next__ + 5)"""
        self.check(b, a)

kundi Test_nonzero(FixerTestCase):
    fixer = "nonzero"

    eleza test_1(self):
        b = """
            kundi A:
                eleza __nonzero__(self):
                    pita
            """
        a = """
            kundi A:
                eleza __bool__(self):
                    pita
            """
        self.check(b, a)

    eleza test_2(self):
        b = """
            kundi A(object):
                eleza __nonzero__(self):
                    pita
            """
        a = """
            kundi A(object):
                eleza __bool__(self):
                    pita
            """
        self.check(b, a)

    eleza test_unchanged_1(self):
        s = """
            kundi A(object):
                eleza __bool__(self):
                    pita
            """
        self.unchanged(s)

    eleza test_unchanged_2(self):
        s = """
            kundi A(object):
                eleza __nonzero__(self, a):
                    pita
            """
        self.unchanged(s)

    eleza test_unchanged_func(self):
        s = """
            eleza __nonzero__(self):
                pita
            """
        self.unchanged(s)

kundi Test_numliterals(FixerTestCase):
    fixer = "numliterals"

    eleza test_octal_1(self):
        b = """0755"""
        a = """0o755"""
        self.check(b, a)

    eleza test_long_int_1(self):
        b = """a = 12L"""
        a = """a = 12"""
        self.check(b, a)

    eleza test_long_int_2(self):
        b = """a = 12l"""
        a = """a = 12"""
        self.check(b, a)

    eleza test_long_hex(self):
        b = """b = 0x12l"""
        a = """b = 0x12"""
        self.check(b, a)

    eleza test_comments_and_spacing(self):
        b = """b =   0x12L"""
        a = """b =   0x12"""
        self.check(b, a)

        b = """b = 0755 # spam"""
        a = """b = 0o755 # spam"""
        self.check(b, a)

    eleza test_unchanged_int(self):
        s = """5"""
        self.unchanged(s)

    eleza test_unchanged_float(self):
        s = """5.0"""
        self.unchanged(s)

    eleza test_unchanged_octal(self):
        s = """0o755"""
        self.unchanged(s)

    eleza test_unchanged_hex(self):
        s = """0xABC"""
        self.unchanged(s)

    eleza test_unchanged_exp(self):
        s = """5.0e10"""
        self.unchanged(s)

    eleza test_unchanged_complex_int(self):
        s = """5 + 4j"""
        self.unchanged(s)

    eleza test_unchanged_complex_float(self):
        s = """5.4 + 4.9j"""
        self.unchanged(s)

    eleza test_unchanged_complex_bare(self):
        s = """4j"""
        self.unchanged(s)
        s = """4.4j"""
        self.unchanged(s)

kundi Test_renames(FixerTestCase):
    fixer = "renames"

    modules = {"sys":  ("maxint", "maxsize"),
              }

    eleza test_import_kutoka(self):
        kila mod, (old, new) kwenye list(self.modules.items()):
            b = "kutoka %s agiza %s" % (mod, old)
            a = "kutoka %s agiza %s" % (mod, new)
            self.check(b, a)

            s = "kutoka foo agiza %s" % old
            self.unchanged(s)

    eleza test_import_from_as(self):
        kila mod, (old, new) kwenye list(self.modules.items()):
            b = "kutoka %s agiza %s kama foo_bar" % (mod, old)
            a = "kutoka %s agiza %s kama foo_bar" % (mod, new)
            self.check(b, a)

    eleza test_import_module_usage(self):
        kila mod, (old, new) kwenye list(self.modules.items()):
            b = """
                agiza %s
                foo(%s, %s.%s)
                """ % (mod, mod, mod, old)
            a = """
                agiza %s
                foo(%s, %s.%s)
                """ % (mod, mod, mod, new)
            self.check(b, a)

    eleza XXX_test_from_import_usage(self):
        # sio implemented yet
        kila mod, (old, new) kwenye list(self.modules.items()):
            b = """
                kutoka %s agiza %s
                foo(%s, %s)
                """ % (mod, old, mod, old)
            a = """
                kutoka %s agiza %s
                foo(%s, %s)
                """ % (mod, new, mod, new)
            self.check(b, a)

kundi Test_unicode(FixerTestCase):
    fixer = "unicode"

    eleza test_whitespace(self):
        b = """unicode( x)"""
        a = """str( x)"""
        self.check(b, a)

        b = """ unicode(x )"""
        a = """ str(x )"""
        self.check(b, a)

        b = """ u'h'"""
        a = """ 'h'"""
        self.check(b, a)

    eleza test_unicode_call(self):
        b = """unicode(x, y, z)"""
        a = """str(x, y, z)"""
        self.check(b, a)

    eleza test_unichr(self):
        b = """unichr(u'h')"""
        a = """chr('h')"""
        self.check(b, a)

    eleza test_unicode_literal_1(self):
        b = '''u"x"'''
        a = '''"x"'''
        self.check(b, a)

    eleza test_unicode_literal_2(self):
        b = """ur'x'"""
        a = """r'x'"""
        self.check(b, a)

    eleza test_unicode_literal_3(self):
        b = """UR'''x''' """
        a = """R'''x''' """
        self.check(b, a)

    eleza test_native_literal_escape_u(self):
        b = r"""'\\\u20ac\U0001d121\\u20ac'"""
        a = r"""'\\\\u20ac\\U0001d121\\u20ac'"""
        self.check(b, a)

        b = r"""r'\\\u20ac\U0001d121\\u20ac'"""
        a = r"""r'\\\u20ac\U0001d121\\u20ac'"""
        self.check(b, a)

    eleza test_bytes_literal_escape_u(self):
        b = r"""b'\\\u20ac\U0001d121\\u20ac'"""
        a = r"""b'\\\u20ac\U0001d121\\u20ac'"""
        self.check(b, a)

        b = r"""br'\\\u20ac\U0001d121\\u20ac'"""
        a = r"""br'\\\u20ac\U0001d121\\u20ac'"""
        self.check(b, a)

    eleza test_unicode_literal_escape_u(self):
        b = r"""u'\\\u20ac\U0001d121\\u20ac'"""
        a = r"""'\\\u20ac\U0001d121\\u20ac'"""
        self.check(b, a)

        b = r"""ur'\\\u20ac\U0001d121\\u20ac'"""
        a = r"""r'\\\u20ac\U0001d121\\u20ac'"""
        self.check(b, a)

    eleza test_native_unicode_literal_escape_u(self):
        f = 'kutoka __future__ agiza unicode_literals\n'
        b = f + r"""'\\\u20ac\U0001d121\\u20ac'"""
        a = f + r"""'\\\u20ac\U0001d121\\u20ac'"""
        self.check(b, a)

        b = f + r"""r'\\\u20ac\U0001d121\\u20ac'"""
        a = f + r"""r'\\\u20ac\U0001d121\\u20ac'"""
        self.check(b, a)


kundi Test_filter(FixerTestCase):
    fixer = "filter"

    eleza test_prefix_preservation(self):
        b = """x =   filter(    foo,     'abc'   )"""
        a = """x =   list(filter(    foo,     'abc'   ))"""
        self.check(b, a)

        b = """x =   filter(  Tupu , 'abc'  )"""
        a = """x =   [_f kila _f kwenye 'abc' ikiwa _f]"""
        self.check(b, a)

    eleza test_filter_basic(self):
        b = """x = filter(Tupu, 'abc')"""
        a = """x = [_f kila _f kwenye 'abc' ikiwa _f]"""
        self.check(b, a)

        b = """x = len(filter(f, 'abc'))"""
        a = """x = len(list(filter(f, 'abc')))"""
        self.check(b, a)

        b = """x = filter(lambda x: x%2 == 0, range(10))"""
        a = """x = [x kila x kwenye range(10) ikiwa x%2 == 0]"""
        self.check(b, a)

        # Note the parens around x
        b = """x = filter(lambda (x): x%2 == 0, range(10))"""
        a = """x = [x kila x kwenye range(10) ikiwa x%2 == 0]"""
        self.check(b, a)

    eleza test_filter_trailers(self):
        b = """x = filter(Tupu, 'abc')[0]"""
        a = """x = [_f kila _f kwenye 'abc' ikiwa _f][0]"""
        self.check(b, a)

        b = """x = len(filter(f, 'abc')[0])"""
        a = """x = len(list(filter(f, 'abc'))[0])"""
        self.check(b, a)

        b = """x = filter(lambda x: x%2 == 0, range(10))[0]"""
        a = """x = [x kila x kwenye range(10) ikiwa x%2 == 0][0]"""
        self.check(b, a)

        # Note the parens around x
        b = """x = filter(lambda (x): x%2 == 0, range(10))[0]"""
        a = """x = [x kila x kwenye range(10) ikiwa x%2 == 0][0]"""
        self.check(b, a)

    eleza test_filter_nochange(self):
        a = """b.join(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """(a + foo(5)).join(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """iter(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """list(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """list(filter(f, 'abc'))[0]"""
        self.unchanged(a)
        a = """set(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """set(filter(f, 'abc')).pop()"""
        self.unchanged(a)
        a = """tuple(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """any(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """all(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """sum(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """sorted(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """sorted(filter(f, 'abc'), key=blah)"""
        self.unchanged(a)
        a = """sorted(filter(f, 'abc'), key=blah)[0]"""
        self.unchanged(a)
        a = """enumerate(filter(f, 'abc'))"""
        self.unchanged(a)
        a = """enumerate(filter(f, 'abc'), start=1)"""
        self.unchanged(a)
        a = """kila i kwenye filter(f, 'abc'): pita"""
        self.unchanged(a)
        a = """[x kila x kwenye filter(f, 'abc')]"""
        self.unchanged(a)
        a = """(x kila x kwenye filter(f, 'abc'))"""
        self.unchanged(a)

    eleza test_future_builtins(self):
        a = "kutoka future_builtins agiza spam, filter; filter(f, 'ham')"
        self.unchanged(a)

        b = """kutoka future_builtins agiza spam; x = filter(f, 'abc')"""
        a = """kutoka future_builtins agiza spam; x = list(filter(f, 'abc'))"""
        self.check(b, a)

        a = "kutoka future_builtins agiza *; filter(f, 'ham')"
        self.unchanged(a)

kundi Test_map(FixerTestCase):
    fixer = "map"

    eleza check(self, b, a):
        self.unchanged("kutoka future_builtins agiza map; " + b, a)
        super(Test_map, self).check(b, a)

    eleza test_prefix_preservation(self):
        b = """x =    map(   f,    'abc'   )"""
        a = """x =    list(map(   f,    'abc'   ))"""
        self.check(b, a)

    eleza test_map_trailers(self):
        b = """x = map(f, 'abc')[0]"""
        a = """x = list(map(f, 'abc'))[0]"""
        self.check(b, a)

        b = """x = map(Tupu, l)[0]"""
        a = """x = list(l)[0]"""
        self.check(b, a)

        b = """x = map(lambda x:x, l)[0]"""
        a = """x = [x kila x kwenye l][0]"""
        self.check(b, a)

        b = """x = map(f, 'abc')[0][1]"""
        a = """x = list(map(f, 'abc'))[0][1]"""
        self.check(b, a)

    eleza test_trailing_comment(self):
        b = """x = map(f, 'abc')   #   foo"""
        a = """x = list(map(f, 'abc'))   #   foo"""
        self.check(b, a)

    eleza test_Tupu_with_multiple_arguments(self):
        s = """x = map(Tupu, a, b, c)"""
        self.warns_unchanged(s, "cannot convert map(Tupu, ...) ukijumuisha "
                             "multiple arguments")

    eleza test_map_basic(self):
        b = """x = map(f, 'abc')"""
        a = """x = list(map(f, 'abc'))"""
        self.check(b, a)

        b = """x = len(map(f, 'abc', 'def'))"""
        a = """x = len(list(map(f, 'abc', 'def')))"""
        self.check(b, a)

        b = """x = map(Tupu, 'abc')"""
        a = """x = list('abc')"""
        self.check(b, a)

        b = """x = map(lambda x: x+1, range(4))"""
        a = """x = [x+1 kila x kwenye range(4)]"""
        self.check(b, a)

        # Note the parens around x
        b = """x = map(lambda (x): x+1, range(4))"""
        a = """x = [x+1 kila x kwenye range(4)]"""
        self.check(b, a)

        b = """
            foo()
            # foo
            map(f, x)
            """
        a = """
            foo()
            # foo
            list(map(f, x))
            """
        self.warns(b, a, "You should use a kila loop here")

    eleza test_map_nochange(self):
        a = """b.join(map(f, 'abc'))"""
        self.unchanged(a)
        a = """(a + foo(5)).join(map(f, 'abc'))"""
        self.unchanged(a)
        a = """iter(map(f, 'abc'))"""
        self.unchanged(a)
        a = """list(map(f, 'abc'))"""
        self.unchanged(a)
        a = """list(map(f, 'abc'))[0]"""
        self.unchanged(a)
        a = """set(map(f, 'abc'))"""
        self.unchanged(a)
        a = """set(map(f, 'abc')).pop()"""
        self.unchanged(a)
        a = """tuple(map(f, 'abc'))"""
        self.unchanged(a)
        a = """any(map(f, 'abc'))"""
        self.unchanged(a)
        a = """all(map(f, 'abc'))"""
        self.unchanged(a)
        a = """sum(map(f, 'abc'))"""
        self.unchanged(a)
        a = """sorted(map(f, 'abc'))"""
        self.unchanged(a)
        a = """sorted(map(f, 'abc'), key=blah)"""
        self.unchanged(a)
        a = """sorted(map(f, 'abc'), key=blah)[0]"""
        self.unchanged(a)
        a = """enumerate(map(f, 'abc'))"""
        self.unchanged(a)
        a = """enumerate(map(f, 'abc'), start=1)"""
        self.unchanged(a)
        a = """kila i kwenye map(f, 'abc'): pita"""
        self.unchanged(a)
        a = """[x kila x kwenye map(f, 'abc')]"""
        self.unchanged(a)
        a = """(x kila x kwenye map(f, 'abc'))"""
        self.unchanged(a)

    eleza test_future_builtins(self):
        a = "kutoka future_builtins agiza spam, map, eggs; map(f, 'ham')"
        self.unchanged(a)

        b = """kutoka future_builtins agiza spam, eggs; x = map(f, 'abc')"""
        a = """kutoka future_builtins agiza spam, eggs; x = list(map(f, 'abc'))"""
        self.check(b, a)

        a = "kutoka future_builtins agiza *; map(f, 'ham')"
        self.unchanged(a)

kundi Test_zip(FixerTestCase):
    fixer = "zip"

    eleza check(self, b, a):
        self.unchanged("kutoka future_builtins agiza zip; " + b, a)
        super(Test_zip, self).check(b, a)

    eleza test_zip_basic(self):
        b = """x = zip()"""
        a = """x = list(zip())"""
        self.check(b, a)

        b = """x = zip(a, b, c)"""
        a = """x = list(zip(a, b, c))"""
        self.check(b, a)

        b = """x = len(zip(a, b))"""
        a = """x = len(list(zip(a, b)))"""
        self.check(b, a)

    eleza test_zip_trailers(self):
        b = """x = zip(a, b, c)[0]"""
        a = """x = list(zip(a, b, c))[0]"""
        self.check(b, a)

        b = """x = zip(a, b, c)[0][1]"""
        a = """x = list(zip(a, b, c))[0][1]"""
        self.check(b, a)

    eleza test_zip_nochange(self):
        a = """b.join(zip(a, b))"""
        self.unchanged(a)
        a = """(a + foo(5)).join(zip(a, b))"""
        self.unchanged(a)
        a = """iter(zip(a, b))"""
        self.unchanged(a)
        a = """list(zip(a, b))"""
        self.unchanged(a)
        a = """list(zip(a, b))[0]"""
        self.unchanged(a)
        a = """set(zip(a, b))"""
        self.unchanged(a)
        a = """set(zip(a, b)).pop()"""
        self.unchanged(a)
        a = """tuple(zip(a, b))"""
        self.unchanged(a)
        a = """any(zip(a, b))"""
        self.unchanged(a)
        a = """all(zip(a, b))"""
        self.unchanged(a)
        a = """sum(zip(a, b))"""
        self.unchanged(a)
        a = """sorted(zip(a, b))"""
        self.unchanged(a)
        a = """sorted(zip(a, b), key=blah)"""
        self.unchanged(a)
        a = """sorted(zip(a, b), key=blah)[0]"""
        self.unchanged(a)
        a = """enumerate(zip(a, b))"""
        self.unchanged(a)
        a = """enumerate(zip(a, b), start=1)"""
        self.unchanged(a)
        a = """kila i kwenye zip(a, b): pita"""
        self.unchanged(a)
        a = """[x kila x kwenye zip(a, b)]"""
        self.unchanged(a)
        a = """(x kila x kwenye zip(a, b))"""
        self.unchanged(a)

    eleza test_future_builtins(self):
        a = "kutoka future_builtins agiza spam, zip, eggs; zip(a, b)"
        self.unchanged(a)

        b = """kutoka future_builtins agiza spam, eggs; x = zip(a, b)"""
        a = """kutoka future_builtins agiza spam, eggs; x = list(zip(a, b))"""
        self.check(b, a)

        a = "kutoka future_builtins agiza *; zip(a, b)"
        self.unchanged(a)

kundi Test_standarderror(FixerTestCase):
    fixer = "standarderror"

    eleza test(self):
        b = """x =    StandardError()"""
        a = """x =    Exception()"""
        self.check(b, a)

        b = """x = StandardError(a, b, c)"""
        a = """x = Exception(a, b, c)"""
        self.check(b, a)

        b = """f(2 + StandardError(a, b, c))"""
        a = """f(2 + Exception(a, b, c))"""
        self.check(b, a)

kundi Test_types(FixerTestCase):
    fixer = "types"

    eleza test_basic_types_convert(self):
        b = """types.StringType"""
        a = """bytes"""
        self.check(b, a)

        b = """types.DictType"""
        a = """dict"""
        self.check(b, a)

        b = """types . IntType"""
        a = """int"""
        self.check(b, a)

        b = """types.ListType"""
        a = """list"""
        self.check(b, a)

        b = """types.LongType"""
        a = """int"""
        self.check(b, a)

        b = """types.TupuType"""
        a = """type(Tupu)"""
        self.check(b, a)

        b = "types.StringTypes"
        a = "(str,)"
        self.check(b, a)

kundi Test_idioms(FixerTestCase):
    fixer = "idioms"

    eleza test_while(self):
        b = """wakati 1: foo()"""
        a = """wakati Kweli: foo()"""
        self.check(b, a)

        b = """wakati   1: foo()"""
        a = """wakati   Kweli: foo()"""
        self.check(b, a)

        b = """
            wakati 1:
                foo()
            """
        a = """
            wakati Kweli:
                foo()
            """
        self.check(b, a)

    eleza test_while_unchanged(self):
        s = """wakati 11: foo()"""
        self.unchanged(s)

        s = """wakati 0: foo()"""
        self.unchanged(s)

        s = """wakati foo(): foo()"""
        self.unchanged(s)

        s = """wakati []: foo()"""
        self.unchanged(s)

    eleza test_eq_simple(self):
        b = """type(x) == T"""
        a = """isinstance(x, T)"""
        self.check(b, a)

        b = """ikiwa   type(x) == T: pita"""
        a = """ikiwa   isinstance(x, T): pita"""
        self.check(b, a)

    eleza test_eq_reverse(self):
        b = """T == type(x)"""
        a = """isinstance(x, T)"""
        self.check(b, a)

        b = """ikiwa   T == type(x): pita"""
        a = """ikiwa   isinstance(x, T): pita"""
        self.check(b, a)

    eleza test_eq_expression(self):
        b = """type(x+y) == d.get('T')"""
        a = """isinstance(x+y, d.get('T'))"""
        self.check(b, a)

        b = """type(   x  +  y) == d.get('T')"""
        a = """isinstance(x  +  y, d.get('T'))"""
        self.check(b, a)

    eleza test_is_simple(self):
        b = """type(x) ni T"""
        a = """isinstance(x, T)"""
        self.check(b, a)

        b = """ikiwa   type(x) ni T: pita"""
        a = """ikiwa   isinstance(x, T): pita"""
        self.check(b, a)

    eleza test_is_reverse(self):
        b = """T ni type(x)"""
        a = """isinstance(x, T)"""
        self.check(b, a)

        b = """ikiwa   T ni type(x): pita"""
        a = """ikiwa   isinstance(x, T): pita"""
        self.check(b, a)

    eleza test_is_expression(self):
        b = """type(x+y) ni d.get('T')"""
        a = """isinstance(x+y, d.get('T'))"""
        self.check(b, a)

        b = """type(   x  +  y) ni d.get('T')"""
        a = """isinstance(x  +  y, d.get('T'))"""
        self.check(b, a)

    eleza test_is_not_simple(self):
        b = """type(x) ni sio T"""
        a = """not isinstance(x, T)"""
        self.check(b, a)

        b = """ikiwa   type(x) ni sio T: pita"""
        a = """ikiwa   sio isinstance(x, T): pita"""
        self.check(b, a)

    eleza test_is_not_reverse(self):
        b = """T ni sio type(x)"""
        a = """not isinstance(x, T)"""
        self.check(b, a)

        b = """ikiwa   T ni sio type(x): pita"""
        a = """ikiwa   sio isinstance(x, T): pita"""
        self.check(b, a)

    eleza test_is_not_expression(self):
        b = """type(x+y) ni sio d.get('T')"""
        a = """not isinstance(x+y, d.get('T'))"""
        self.check(b, a)

        b = """type(   x  +  y) ni sio d.get('T')"""
        a = """not isinstance(x  +  y, d.get('T'))"""
        self.check(b, a)

    eleza test_ne_simple(self):
        b = """type(x) != T"""
        a = """not isinstance(x, T)"""
        self.check(b, a)

        b = """ikiwa   type(x) != T: pita"""
        a = """ikiwa   sio isinstance(x, T): pita"""
        self.check(b, a)

    eleza test_ne_reverse(self):
        b = """T != type(x)"""
        a = """not isinstance(x, T)"""
        self.check(b, a)

        b = """ikiwa   T != type(x): pita"""
        a = """ikiwa   sio isinstance(x, T): pita"""
        self.check(b, a)

    eleza test_ne_expression(self):
        b = """type(x+y) != d.get('T')"""
        a = """not isinstance(x+y, d.get('T'))"""
        self.check(b, a)

        b = """type(   x  +  y) != d.get('T')"""
        a = """not isinstance(x  +  y, d.get('T'))"""
        self.check(b, a)

    eleza test_type_unchanged(self):
        a = """type(x).__name__"""
        self.unchanged(a)

    eleza test_sort_list_call(self):
        b = """
            v = list(t)
            v.sort()
            foo(v)
            """
        a = """
            v = sorted(t)
            foo(v)
            """
        self.check(b, a)

        b = """
            v = list(foo(b) + d)
            v.sort()
            foo(v)
            """
        a = """
            v = sorted(foo(b) + d)
            foo(v)
            """
        self.check(b, a)

        b = """
            wakati x:
                v = list(t)
                v.sort()
                foo(v)
            """
        a = """
            wakati x:
                v = sorted(t)
                foo(v)
            """
        self.check(b, a)

        b = """
            v = list(t)
            # foo
            v.sort()
            foo(v)
            """
        a = """
            v = sorted(t)
            # foo
            foo(v)
            """
        self.check(b, a)

        b = r"""
            v = list(   t)
            v.sort()
            foo(v)
            """
        a = r"""
            v = sorted(   t)
            foo(v)
            """
        self.check(b, a)

        b = r"""
            jaribu:
                m = list(s)
                m.sort()
            tatizo: pita
            """

        a = r"""
            jaribu:
                m = sorted(s)
            tatizo: pita
            """
        self.check(b, a)

        b = r"""
            jaribu:
                m = list(s)
                # foo
                m.sort()
            tatizo: pita
            """

        a = r"""
            jaribu:
                m = sorted(s)
                # foo
            tatizo: pita
            """
        self.check(b, a)

        b = r"""
            m = list(s)
            # more comments
            m.sort()"""

        a = r"""
            m = sorted(s)
            # more comments"""
        self.check(b, a)

    eleza test_sort_simple_expr(self):
        b = """
            v = t
            v.sort()
            foo(v)
            """
        a = """
            v = sorted(t)
            foo(v)
            """
        self.check(b, a)

        b = """
            v = foo(b)
            v.sort()
            foo(v)
            """
        a = """
            v = sorted(foo(b))
            foo(v)
            """
        self.check(b, a)

        b = """
            v = b.keys()
            v.sort()
            foo(v)
            """
        a = """
            v = sorted(b.keys())
            foo(v)
            """
        self.check(b, a)

        b = """
            v = foo(b) + d
            v.sort()
            foo(v)
            """
        a = """
            v = sorted(foo(b) + d)
            foo(v)
            """
        self.check(b, a)

        b = """
            wakati x:
                v = t
                v.sort()
                foo(v)
            """
        a = """
            wakati x:
                v = sorted(t)
                foo(v)
            """
        self.check(b, a)

        b = """
            v = t
            # foo
            v.sort()
            foo(v)
            """
        a = """
            v = sorted(t)
            # foo
            foo(v)
            """
        self.check(b, a)

        b = r"""
            v =   t
            v.sort()
            foo(v)
            """
        a = r"""
            v =   sorted(t)
            foo(v)
            """
        self.check(b, a)

    eleza test_sort_unchanged(self):
        s = """
            v = list(t)
            w.sort()
            foo(w)
            """
        self.unchanged(s)

        s = """
            v = list(t)
            v.sort(u)
            foo(v)
            """
        self.unchanged(s)

kundi Test_basestring(FixerTestCase):
    fixer = "basestring"

    eleza test_basestring(self):
        b = """isinstance(x, basestring)"""
        a = """isinstance(x, str)"""
        self.check(b, a)

kundi Test_buffer(FixerTestCase):
    fixer = "buffer"

    eleza test_buffer(self):
        b = """x = buffer(y)"""
        a = """x = memoryview(y)"""
        self.check(b, a)

    eleza test_slicing(self):
        b = """buffer(y)[4:5]"""
        a = """memoryview(y)[4:5]"""
        self.check(b, a)

kundi Test_future(FixerTestCase):
    fixer = "future"

    eleza test_future(self):
        b = """kutoka __future__ agiza braces"""
        a = """"""
        self.check(b, a)

        b = """# comment\nkutoka __future__ agiza braces"""
        a = """# comment\n"""
        self.check(b, a)

        b = """kutoka __future__ agiza braces\n# comment"""
        a = """\n# comment"""
        self.check(b, a)

    eleza test_run_order(self):
        self.assert_runs_after('print')

kundi Test_itertools(FixerTestCase):
    fixer = "itertools"

    eleza checkall(self, before, after):
        # Because we need to check ukijumuisha na without the itertools prefix
        # na on each of the three functions, these loops make it all
        # much easier
        kila i kwenye ('itertools.', ''):
            kila f kwenye ('map', 'filter', 'zip'):
                b = before %(i+'i'+f)
                a = after %(f)
                self.check(b, a)

    eleza test_0(self):
        # A simple example -- test_1 covers exactly the same thing,
        # but it's sio quite kama clear.
        b = "itertools.izip(a, b)"
        a = "zip(a, b)"
        self.check(b, a)

    eleza test_1(self):
        b = """%s(f, a)"""
        a = """%s(f, a)"""
        self.checkall(b, a)

    eleza test_qualified(self):
        b = """itertools.ifilterfalse(a, b)"""
        a = """itertools.filterfalse(a, b)"""
        self.check(b, a)

        b = """itertools.izip_longest(a, b)"""
        a = """itertools.zip_longest(a, b)"""
        self.check(b, a)

    eleza test_2(self):
        b = """ifilterfalse(a, b)"""
        a = """filterfalse(a, b)"""
        self.check(b, a)

        b = """izip_longest(a, b)"""
        a = """zip_longest(a, b)"""
        self.check(b, a)

    eleza test_space_1(self):
        b = """    %s(f, a)"""
        a = """    %s(f, a)"""
        self.checkall(b, a)

    eleza test_space_2(self):
        b = """    itertools.ifilterfalse(a, b)"""
        a = """    itertools.filterfalse(a, b)"""
        self.check(b, a)

        b = """    itertools.izip_longest(a, b)"""
        a = """    itertools.zip_longest(a, b)"""
        self.check(b, a)

    eleza test_run_order(self):
        self.assert_runs_after('map', 'zip', 'filter')


kundi Test_itertools_agizas(FixerTestCase):
    fixer = 'itertools_agizas'

    eleza test_reduced(self):
        b = "kutoka itertools agiza imap, izip, foo"
        a = "kutoka itertools agiza foo"
        self.check(b, a)

        b = "kutoka itertools agiza bar, imap, izip, foo"
        a = "kutoka itertools agiza bar, foo"
        self.check(b, a)

        b = "kutoka itertools agiza chain, imap, izip"
        a = "kutoka itertools agiza chain"
        self.check(b, a)

    eleza test_comments(self):
        b = "#foo\nkutoka itertools agiza imap, izip"
        a = "#foo\n"
        self.check(b, a)

    eleza test_none(self):
        b = "kutoka itertools agiza imap, izip"
        a = ""
        self.check(b, a)

        b = "kutoka itertools agiza izip"
        a = ""
        self.check(b, a)

    eleza test_import_as(self):
        b = "kutoka itertools agiza izip, bar kama bang, imap"
        a = "kutoka itertools agiza bar kama bang"
        self.check(b, a)

        b = "kutoka itertools agiza izip kama _zip, imap, bar"
        a = "kutoka itertools agiza bar"
        self.check(b, a)

        b = "kutoka itertools agiza imap kama _map"
        a = ""
        self.check(b, a)

        b = "kutoka itertools agiza imap kama _map, izip kama _zip"
        a = ""
        self.check(b, a)

        s = "kutoka itertools agiza bar kama bang"
        self.unchanged(s)

    eleza test_ifilter_and_zip_longest(self):
        kila name kwenye "filterfalse", "zip_longest":
            b = "kutoka itertools agiza i%s" % (name,)
            a = "kutoka itertools agiza %s" % (name,)
            self.check(b, a)

            b = "kutoka itertools agiza imap, i%s, foo" % (name,)
            a = "kutoka itertools agiza %s, foo" % (name,)
            self.check(b, a)

            b = "kutoka itertools agiza bar, i%s, foo" % (name,)
            a = "kutoka itertools agiza bar, %s, foo" % (name,)
            self.check(b, a)

    eleza test_import_star(self):
        s = "kutoka itertools agiza *"
        self.unchanged(s)


    eleza test_unchanged(self):
        s = "kutoka itertools agiza foo"
        self.unchanged(s)


kundi Test_agiza(FixerTestCase):
    fixer = "agiza"

    eleza setUp(self):
        super(Test_agiza, self).setUp()
        # Need to replace fix_agiza's exists method
        # so we can check that it's doing the right thing
        self.files_checked = []
        self.present_files = set()
        self.always_exists = Kweli
        eleza fake_exists(name):
            self.files_checked.append(name)
            rudisha self.always_exists ama (name kwenye self.present_files)

        kutoka lib2to3.fixes agiza fix_agiza
        fix_agiza.exists = fake_exists

    eleza tearDown(self):
        kutoka lib2to3.fixes agiza fix_agiza
        fix_agiza.exists = os.path.exists

    eleza check_both(self, b, a):
        self.always_exists = Kweli
        super(Test_agiza, self).check(b, a)
        self.always_exists = Uongo
        super(Test_agiza, self).unchanged(b)

    eleza test_files_checked(self):
        eleza p(path):
            # Takes a unix path na rudishas a path ukijumuisha correct separators
            rudisha os.path.pathsep.join(path.split("/"))

        self.always_exists = Uongo
        self.present_files = set(['__init__.py'])
        expected_extensions = ('.py', os.path.sep, '.pyc', '.so', '.sl', '.pyd')
        names_to_test = (p("/spam/eggs.py"), "ni.py", p("../../shrubbery.py"))

        kila name kwenye names_to_test:
            self.files_checked = []
            self.filename = name
            self.unchanged("agiza jam")

            ikiwa os.path.dirname(name):
                name = os.path.dirname(name) + '/jam'
            isipokua:
                name = 'jam'
            expected_checks = set(name + ext kila ext kwenye expected_extensions)
            expected_checks.add("__init__.py")

            self.assertEqual(set(self.files_checked), expected_checks)

    eleza test_not_in_package(self):
        s = "agiza bar"
        self.always_exists = Uongo
        self.present_files = set(["bar.py"])
        self.unchanged(s)

    eleza test_with_absolute_import_enabled(self):
        s = "kutoka __future__ agiza absolute_agiza\nagiza bar"
        self.always_exists = Uongo
        self.present_files = set(["__init__.py", "bar.py"])
        self.unchanged(s)

    eleza test_in_package(self):
        b = "agiza bar"
        a = "kutoka . agiza bar"
        self.always_exists = Uongo
        self.present_files = set(["__init__.py", "bar.py"])
        self.check(b, a)

    eleza test_import_from_package(self):
        b = "agiza bar"
        a = "kutoka . agiza bar"
        self.always_exists = Uongo
        self.present_files = set(["__init__.py", "bar" + os.path.sep])
        self.check(b, a)

    eleza test_already_relative_agiza(self):
        s = "kutoka . agiza bar"
        self.unchanged(s)

    eleza test_comments_and_indent(self):
        b = "agiza bar # Foo"
        a = "kutoka . agiza bar # Foo"
        self.check(b, a)

    eleza test_kutoka(self):
        b = "kutoka foo agiza bar, baz"
        a = "kutoka .foo agiza bar, baz"
        self.check_both(b, a)

        b = "kutoka foo agiza bar"
        a = "kutoka .foo agiza bar"
        self.check_both(b, a)

        b = "kutoka foo agiza (bar, baz)"
        a = "kutoka .foo agiza (bar, baz)"
        self.check_both(b, a)

    eleza test_dotted_kutoka(self):
        b = "kutoka green.eggs agiza ham"
        a = "kutoka .green.eggs agiza ham"
        self.check_both(b, a)

    eleza test_from_as(self):
        b = "kutoka green.eggs agiza ham kama spam"
        a = "kutoka .green.eggs agiza ham kama spam"
        self.check_both(b, a)

    eleza test_agiza(self):
        b = "agiza foo"
        a = "kutoka . agiza foo"
        self.check_both(b, a)

        b = "agiza foo, bar"
        a = "kutoka . agiza foo, bar"
        self.check_both(b, a)

        b = "agiza foo, bar, x"
        a = "kutoka . agiza foo, bar, x"
        self.check_both(b, a)

        b = "agiza x, y, z"
        a = "kutoka . agiza x, y, z"
        self.check_both(b, a)

    eleza test_import_as(self):
        b = "agiza foo kama x"
        a = "kutoka . agiza foo kama x"
        self.check_both(b, a)

        b = "agiza a kama b, b kama c, c kama d"
        a = "kutoka . agiza a kama b, b kama c, c kama d"
        self.check_both(b, a)

    eleza test_local_and_absolute(self):
        self.always_exists = Uongo
        self.present_files = set(["foo.py", "__init__.py"])

        s = "agiza foo, bar"
        self.warns_unchanged(s, "absolute na local agizas together")

    eleza test_dotted_agiza(self):
        b = "agiza foo.bar"
        a = "kutoka . agiza foo.bar"
        self.check_both(b, a)

    eleza test_dotted_import_as(self):
        b = "agiza foo.bar kama bang"
        a = "kutoka . agiza foo.bar kama bang"
        self.check_both(b, a)

    eleza test_prefix(self):
        b = """
        # prefix
        agiza foo.bar
        """
        a = """
        # prefix
        kutoka . agiza foo.bar
        """
        self.check_both(b, a)


kundi Test_set_literal(FixerTestCase):

    fixer = "set_literal"

    eleza test_basic(self):
        b = """set([1, 2, 3])"""
        a = """{1, 2, 3}"""
        self.check(b, a)

        b = """set((1, 2, 3))"""
        a = """{1, 2, 3}"""
        self.check(b, a)

        b = """set((1,))"""
        a = """{1}"""
        self.check(b, a)

        b = """set([1])"""
        self.check(b, a)

        b = """set((a, b))"""
        a = """{a, b}"""
        self.check(b, a)

        b = """set([a, b])"""
        self.check(b, a)

        b = """set((a*234, f(args=23)))"""
        a = """{a*234, f(args=23)}"""
        self.check(b, a)

        b = """set([a*23, f(23)])"""
        a = """{a*23, f(23)}"""
        self.check(b, a)

        b = """set([a-234**23])"""
        a = """{a-234**23}"""
        self.check(b, a)

    eleza test_listcomps(self):
        b = """set([x kila x kwenye y])"""
        a = """{x kila x kwenye y}"""
        self.check(b, a)

        b = """set([x kila x kwenye y ikiwa x == m])"""
        a = """{x kila x kwenye y ikiwa x == m}"""
        self.check(b, a)

        b = """set([x kila x kwenye y kila a kwenye b])"""
        a = """{x kila x kwenye y kila a kwenye b}"""
        self.check(b, a)

        b = """set([f(x) - 23 kila x kwenye y])"""
        a = """{f(x) - 23 kila x kwenye y}"""
        self.check(b, a)

    eleza test_whitespace(self):
        b = """set( [1, 2])"""
        a = """{1, 2}"""
        self.check(b, a)

        b = """set([1 ,  2])"""
        a = """{1 ,  2}"""
        self.check(b, a)

        b = """set([ 1 ])"""
        a = """{ 1 }"""
        self.check(b, a)

        b = """set( [1] )"""
        a = """{1}"""
        self.check(b, a)

        b = """set([  1,  2  ])"""
        a = """{  1,  2  }"""
        self.check(b, a)

        b = """set([x  kila x kwenye y ])"""
        a = """{x  kila x kwenye y }"""
        self.check(b, a)

        b = """set(
                   [1, 2]
               )
            """
        a = """{1, 2}\n"""
        self.check(b, a)

    eleza test_comments(self):
        b = """set((1, 2)) # Hi"""
        a = """{1, 2} # Hi"""
        self.check(b, a)

        # This isn't optimal behavior, but the fixer ni optional.
        b = """
            # Foo
            set( # Bar
               (1, 2)
            )
            """
        a = """
            # Foo
            {1, 2}
            """
        self.check(b, a)

    eleza test_unchanged(self):
        s = """set()"""
        self.unchanged(s)

        s = """set(a)"""
        self.unchanged(s)

        s = """set(a, b, c)"""
        self.unchanged(s)

        # Don't transform generators because they might have to be lazy.
        s = """set(x kila x kwenye y)"""
        self.unchanged(s)

        s = """set(x kila x kwenye y ikiwa z)"""
        self.unchanged(s)

        s = """set(a*823-23**2 + f(23))"""
        self.unchanged(s)


kundi Test_sys_exc(FixerTestCase):
    fixer = "sys_exc"

    eleza test_0(self):
        b = "sys.exc_type"
        a = "sys.exc_info()[0]"
        self.check(b, a)

    eleza test_1(self):
        b = "sys.exc_value"
        a = "sys.exc_info()[1]"
        self.check(b, a)

    eleza test_2(self):
        b = "sys.exc_traceback"
        a = "sys.exc_info()[2]"
        self.check(b, a)

    eleza test_3(self):
        b = "sys.exc_type # Foo"
        a = "sys.exc_info()[0] # Foo"
        self.check(b, a)

    eleza test_4(self):
        b = "sys.  exc_type"
        a = "sys.  exc_info()[0]"
        self.check(b, a)

    eleza test_5(self):
        b = "sys  .exc_type"
        a = "sys  .exc_info()[0]"
        self.check(b, a)


kundi Test_paren(FixerTestCase):
    fixer = "paren"

    eleza test_0(self):
        b = """[i kila i kwenye 1, 2 ]"""
        a = """[i kila i kwenye (1, 2) ]"""
        self.check(b, a)

    eleza test_1(self):
        b = """[i kila i kwenye 1, 2, ]"""
        a = """[i kila i kwenye (1, 2,) ]"""
        self.check(b, a)

    eleza test_2(self):
        b = """[i kila i  kwenye     1, 2 ]"""
        a = """[i kila i  kwenye     (1, 2) ]"""
        self.check(b, a)

    eleza test_3(self):
        b = """[i kila i kwenye 1, 2 ikiwa i]"""
        a = """[i kila i kwenye (1, 2) ikiwa i]"""
        self.check(b, a)

    eleza test_4(self):
        b = """[i kila i kwenye 1,    2    ]"""
        a = """[i kila i kwenye (1,    2)    ]"""
        self.check(b, a)

    eleza test_5(self):
        b = """(i kila i kwenye 1, 2)"""
        a = """(i kila i kwenye (1, 2))"""
        self.check(b, a)

    eleza test_6(self):
        b = """(i kila i kwenye 1   ,2   ikiwa i)"""
        a = """(i kila i kwenye (1   ,2)   ikiwa i)"""
        self.check(b, a)

    eleza test_unchanged_0(self):
        s = """[i kila i kwenye (1, 2)]"""
        self.unchanged(s)

    eleza test_unchanged_1(self):
        s = """[i kila i kwenye foo()]"""
        self.unchanged(s)

    eleza test_unchanged_2(self):
        s = """[i kila i kwenye (1, 2) ikiwa nothing]"""
        self.unchanged(s)

    eleza test_unchanged_3(self):
        s = """(i kila i kwenye (1, 2))"""
        self.unchanged(s)

    eleza test_unchanged_4(self):
        s = """[i kila i kwenye m]"""
        self.unchanged(s)

kundi Test_metaclass(FixerTestCase):

    fixer = 'metaclass'

    eleza test_unchanged(self):
        self.unchanged("kundi X(): pita")
        self.unchanged("kundi X(object): pita")
        self.unchanged("kundi X(object1, object2): pita")
        self.unchanged("kundi X(object1, object2, object3): pita")
        self.unchanged("kundi X(metaclass=Meta): pita")
        self.unchanged("kundi X(b, arg=23, metclass=Meta): pita")
        self.unchanged("kundi X(b, arg=23, metaclass=Meta, other=42): pita")

        s = """
        kundi X:
            eleza __metaclass__(self): pita
        """
        self.unchanged(s)

        s = """
        kundi X:
            a[23] = 74
        """
        self.unchanged(s)

    eleza test_comments(self):
        b = """
        kundi X:
            # hi
            __metaclass__ = AppleMeta
        """
        a = """
        kundi X(metaclass=AppleMeta):
            # hi
            pita
        """
        self.check(b, a)

        b = """
        kundi X:
            __metaclass__ = Meta
            # Bedtime!
        """
        a = """
        kundi X(metaclass=Meta):
            pita
            # Bedtime!
        """
        self.check(b, a)

    eleza test_meta(self):
        # no-parent class, odd body
        b = """
        kundi X():
            __metaclass__ = Q
            pita
        """
        a = """
        kundi X(metaclass=Q):
            pita
        """
        self.check(b, a)

        # one parent class, no body
        b = """kundi X(object): __metaclass__ = Q"""
        a = """kundi X(object, metaclass=Q): pita"""
        self.check(b, a)


        # one parent, simple body
        b = """
        kundi X(object):
            __metaclass__ = Meta
            bar = 7
        """
        a = """
        kundi X(object, metaclass=Meta):
            bar = 7
        """
        self.check(b, a)

        b = """
        kundi X:
            __metaclass__ = Meta; x = 4; g = 23
        """
        a = """
        kundi X(metaclass=Meta):
            x = 4; g = 23
        """
        self.check(b, a)

        # one parent, simple body, __metaclass__ last
        b = """
        kundi X(object):
            bar = 7
            __metaclass__ = Meta
        """
        a = """
        kundi X(object, metaclass=Meta):
            bar = 7
        """
        self.check(b, a)

        # redefining __metaclass__
        b = """
        kundi X():
            __metaclass__ = A
            __metaclass__ = B
            bar = 7
        """
        a = """
        kundi X(metaclass=B):
            bar = 7
        """
        self.check(b, a)

        # multiple inheritance, simple body
        b = """
        kundi X(clsA, clsB):
            __metaclass__ = Meta
            bar = 7
        """
        a = """
        kundi X(clsA, clsB, metaclass=Meta):
            bar = 7
        """
        self.check(b, a)

        # keywords kwenye the kundi statement
        b = """kundi m(a, arg=23): __metaclass__ = Meta"""
        a = """kundi m(a, arg=23, metaclass=Meta): pita"""
        self.check(b, a)

        b = """
        kundi X(expression(2 + 4)):
            __metaclass__ = Meta
        """
        a = """
        kundi X(expression(2 + 4), metaclass=Meta):
            pita
        """
        self.check(b, a)

        b = """
        kundi X(expression(2 + 4), x**4):
            __metaclass__ = Meta
        """
        a = """
        kundi X(expression(2 + 4), x**4, metaclass=Meta):
            pita
        """
        self.check(b, a)

        b = """
        kundi X:
            __metaclass__ = Meta
            save.py = 23
        """
        a = """
        kundi X(metaclass=Meta):
            save.py = 23
        """
        self.check(b, a)


kundi Test_getcwdu(FixerTestCase):

    fixer = 'getcwdu'

    eleza test_basic(self):
        b = """os.getcwdu"""
        a = """os.getcwd"""
        self.check(b, a)

        b = """os.getcwdu()"""
        a = """os.getcwd()"""
        self.check(b, a)

        b = """meth = os.getcwdu"""
        a = """meth = os.getcwd"""
        self.check(b, a)

        b = """os.getcwdu(args)"""
        a = """os.getcwd(args)"""
        self.check(b, a)

    eleza test_comment(self):
        b = """os.getcwdu() # Foo"""
        a = """os.getcwd() # Foo"""
        self.check(b, a)

    eleza test_unchanged(self):
        s = """os.getcwd()"""
        self.unchanged(s)

        s = """getcwdu()"""
        self.unchanged(s)

        s = """os.getcwdb()"""
        self.unchanged(s)

    eleza test_indentation(self):
        b = """
            ikiwa 1:
                os.getcwdu()
            """
        a = """
            ikiwa 1:
                os.getcwd()
            """
        self.check(b, a)

    eleza test_multilation(self):
        b = """os .getcwdu()"""
        a = """os .getcwd()"""
        self.check(b, a)

        b = """os.  getcwdu"""
        a = """os.  getcwd"""
        self.check(b, a)

        b = """os.getcwdu (  )"""
        a = """os.getcwd (  )"""
        self.check(b, a)


kundi Test_operator(FixerTestCase):

    fixer = "operator"

    eleza test_operator_isCallable(self):
        b = "operator.isCallable(x)"
        a = "callable(x)"
        self.check(b, a)

    eleza test_operator_sequenceIncludes(self):
        b = "operator.sequenceIncludes(x, y)"
        a = "operator.contains(x, y)"
        self.check(b, a)

        b = "operator .sequenceIncludes(x, y)"
        a = "operator .contains(x, y)"
        self.check(b, a)

        b = "operator.  sequenceIncludes(x, y)"
        a = "operator.  contains(x, y)"
        self.check(b, a)

    eleza test_operator_isSequenceType(self):
        b = "operator.isSequenceType(x)"
        a = "agiza collections.abc\nisinstance(x, collections.abc.Sequence)"
        self.check(b, a)

    eleza test_operator_isMappingType(self):
        b = "operator.isMappingType(x)"
        a = "agiza collections.abc\nisinstance(x, collections.abc.Mapping)"
        self.check(b, a)

    eleza test_operator_isNumberType(self):
        b = "operator.isNumberType(x)"
        a = "agiza numbers\nisinstance(x, numbers.Number)"
        self.check(b, a)

    eleza test_operator_repeat(self):
        b = "operator.repeat(x, n)"
        a = "operator.mul(x, n)"
        self.check(b, a)

        b = "operator .repeat(x, n)"
        a = "operator .mul(x, n)"
        self.check(b, a)

        b = "operator.  repeat(x, n)"
        a = "operator.  mul(x, n)"
        self.check(b, a)

    eleza test_operator_irepeat(self):
        b = "operator.irepeat(x, n)"
        a = "operator.imul(x, n)"
        self.check(b, a)

        b = "operator .irepeat(x, n)"
        a = "operator .imul(x, n)"
        self.check(b, a)

        b = "operator.  irepeat(x, n)"
        a = "operator.  imul(x, n)"
        self.check(b, a)

    eleza test_bare_isCallable(self):
        s = "isCallable(x)"
        t = "You should use 'callable(x)' here."
        self.warns_unchanged(s, t)

    eleza test_bare_sequenceIncludes(self):
        s = "sequenceIncludes(x, y)"
        t = "You should use 'operator.contains(x, y)' here."
        self.warns_unchanged(s, t)

    eleza test_bare_operator_isSequenceType(self):
        s = "isSequenceType(z)"
        t = "You should use 'isinstance(z, collections.abc.Sequence)' here."
        self.warns_unchanged(s, t)

    eleza test_bare_operator_isMappingType(self):
        s = "isMappingType(x)"
        t = "You should use 'isinstance(x, collections.abc.Mapping)' here."
        self.warns_unchanged(s, t)

    eleza test_bare_operator_isNumberType(self):
        s = "isNumberType(y)"
        t = "You should use 'isinstance(y, numbers.Number)' here."
        self.warns_unchanged(s, t)

    eleza test_bare_operator_repeat(self):
        s = "repeat(x, n)"
        t = "You should use 'operator.mul(x, n)' here."
        self.warns_unchanged(s, t)

    eleza test_bare_operator_irepeat(self):
        s = "irepeat(y, 187)"
        t = "You should use 'operator.imul(y, 187)' here."
        self.warns_unchanged(s, t)


kundi Test_exitfunc(FixerTestCase):

    fixer = "exitfunc"

    eleza test_simple(self):
        b = """
            agiza sys
            sys.exitfunc = my_atexit
            """
        a = """
            agiza sys
            agiza atexit
            atexit.register(my_atexit)
            """
        self.check(b, a)

    eleza test_names_agiza(self):
        b = """
            agiza sys, crumbs
            sys.exitfunc = my_func
            """
        a = """
            agiza sys, crumbs, atexit
            atexit.register(my_func)
            """
        self.check(b, a)

    eleza test_complex_expression(self):
        b = """
            agiza sys
            sys.exitfunc = do(d)/a()+complex(f=23, g=23)*expression
            """
        a = """
            agiza sys
            agiza atexit
            atexit.register(do(d)/a()+complex(f=23, g=23)*expression)
            """
        self.check(b, a)

    eleza test_comments(self):
        b = """
            agiza sys # Foo
            sys.exitfunc = f # Blah
            """
        a = """
            agiza sys
            agiza atexit # Foo
            atexit.register(f) # Blah
            """
        self.check(b, a)

        b = """
            agiza apples, sys, crumbs, larry # Pleasant comments
            sys.exitfunc = func
            """
        a = """
            agiza apples, sys, crumbs, larry, atexit # Pleasant comments
            atexit.register(func)
            """
        self.check(b, a)

    eleza test_in_a_function(self):
        b = """
            agiza sys
            eleza f():
                sys.exitfunc = func
            """
        a = """
            agiza sys
            agiza atexit
            eleza f():
                atexit.register(func)
             """
        self.check(b, a)

    eleza test_no_sys_agiza(self):
        b = """sys.exitfunc = f"""
        a = """atexit.register(f)"""
        msg = ("Can't find sys agiza; Please add an atexit agiza at the "
            "top of your file.")
        self.warns(b, a, msg)


    eleza test_unchanged(self):
        s = """f(sys.exitfunc)"""
        self.unchanged(s)


kundi Test_asserts(FixerTestCase):

    fixer = "asserts"

    eleza test_deprecated_names(self):
        tests = [
            ('self.assert_(Kweli)', 'self.assertKweli(Kweli)'),
            ('self.assertEquals(2, 2)', 'self.assertEqual(2, 2)'),
            ('self.assertNotEquals(2, 3)', 'self.assertNotEqual(2, 3)'),
            ('self.assertAlmostEquals(2, 3)', 'self.assertAlmostEqual(2, 3)'),
            ('self.assertNotAlmostEquals(2, 8)', 'self.assertNotAlmostEqual(2, 8)'),
            ('self.failUnlessEqual(2, 2)', 'self.assertEqual(2, 2)'),
            ('self.failIfEqual(2, 3)', 'self.assertNotEqual(2, 3)'),
            ('self.failUnlessAlmostEqual(2, 3)', 'self.assertAlmostEqual(2, 3)'),
            ('self.failIfAlmostEqual(2, 8)', 'self.assertNotAlmostEqual(2, 8)'),
            ('self.failUnless(Kweli)', 'self.assertKweli(Kweli)'),
            ('self.failUnlessRaises(foo)', 'self.assertRaises(foo)'),
            ('self.failIf(Uongo)', 'self.assertUongo(Uongo)'),
        ]
        kila b, a kwenye tests:
            self.check(b, a)

    eleza test_variants(self):
        b = 'eq = self.assertEquals'
        a = 'eq = self.assertEqual'
        self.check(b, a)
        b = 'self.assertEquals(2, 3, msg="fail")'
        a = 'self.assertEqual(2, 3, msg="fail")'
        self.check(b, a)
        b = 'self.assertEquals(2, 3, msg="fail") # foo'
        a = 'self.assertEqual(2, 3, msg="fail") # foo'
        self.check(b, a)
        b = 'self.assertEquals (2, 3)'
        a = 'self.assertEqual (2, 3)'
        self.check(b, a)
        b = '  self.assertEquals (2, 3)'
        a = '  self.assertEqual (2, 3)'
        self.check(b, a)
        b = 'ukijumuisha self.failUnlessRaises(Explosion): explode()'
        a = 'ukijumuisha self.assertRaises(Explosion): explode()'
        self.check(b, a)
        b = 'ukijumuisha self.failUnlessRaises(Explosion) kama cm: explode()'
        a = 'ukijumuisha self.assertRaises(Explosion) kama cm: explode()'
        self.check(b, a)

    eleza test_unchanged(self):
        self.unchanged('self.assertEqualsOnSaturday')
        self.unchanged('self.assertEqualsOnSaturday(3, 5)')
