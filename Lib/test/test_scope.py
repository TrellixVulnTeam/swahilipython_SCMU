agiza unittest
agiza weakref

kutoka test.support agiza check_syntax_error, cpython_only


kundi ScopeTests(unittest.TestCase):

    eleza testSimpleNesting(self):

        eleza make_adder(x):
            eleza adder(y):
                rudisha x + y
            rudisha adder

        inc = make_adder(1)
        plus10 = make_adder(10)

        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(-2), 8)

    eleza testExtraNesting(self):

        eleza make_adder2(x):
            eleza extra(): # check freevars passing through non-use scopes
                eleza adder(y):
                    rudisha x + y
                rudisha adder
            rudisha extra()

        inc = make_adder2(1)
        plus10 = make_adder2(10)

        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(-2), 8)

    eleza testSimpleAndRebinding(self):

        eleza make_adder3(x):
            eleza adder(y):
                rudisha x + y
            x = x + 1 # check tracking of assignment to x in defining scope
            rudisha adder

        inc = make_adder3(0)
        plus10 = make_adder3(9)

        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(-2), 8)

    eleza testNestingGlobalNoFree(self):

        eleza make_adder4(): # XXX add exta level of indirection
            eleza nest():
                eleza nest():
                    eleza adder(y):
                        rudisha global_x + y # check that plain old globals work
                    rudisha adder
                rudisha nest()
            rudisha nest()

        global_x = 1
        adder = make_adder4()
        self.assertEqual(adder(1), 2)

        global_x = 10
        self.assertEqual(adder(-2), 8)

    eleza testNestingThroughClass(self):

        eleza make_adder5(x):
            kundi Adder:
                eleza __call__(self, y):
                    rudisha x + y
            rudisha Adder()

        inc = make_adder5(1)
        plus10 = make_adder5(10)

        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(-2), 8)

    eleza testNestingPlusFreeRefToGlobal(self):

        eleza make_adder6(x):
            global global_nest_x
            eleza adder(y):
                rudisha global_nest_x + y
            global_nest_x = x
            rudisha adder

        inc = make_adder6(1)
        plus10 = make_adder6(10)

        self.assertEqual(inc(1), 11) # there's only one global
        self.assertEqual(plus10(-2), 8)

    eleza testNearestEnclosingScope(self):

        eleza f(x):
            eleza g(y):
                x = 42 # check that this masks binding in f()
                eleza h(z):
                    rudisha x + z
                rudisha h
            rudisha g(2)

        test_func = f(10)
        self.assertEqual(test_func(5), 47)

    eleza testMixedFreevarsAndCellvars(self):

        eleza identity(x):
            rudisha x

        eleza f(x, y, z):
            eleza g(a, b, c):
                a = a + x # 3
                eleza h():
                    # z * (4 + 9)
                    # 3 * 13
                    rudisha identity(z * (b + y))
                y = c + z # 9
                rudisha h
            rudisha g

        g = f(1, 2, 3)
        h = g(2, 4, 6)
        self.assertEqual(h(), 39)

    eleza testFreeVarInMethod(self):

        eleza test():
            method_and_var = "var"
            kundi Test:
                eleza method_and_var(self):
                    rudisha "method"
                eleza test(self):
                    rudisha method_and_var
                eleza actual_global(self):
                    rudisha str("global")
                eleza str(self):
                    rudisha str(self)
            rudisha Test()

        t = test()
        self.assertEqual(t.test(), "var")
        self.assertEqual(t.method_and_var(), "method")
        self.assertEqual(t.actual_global(), "global")

        method_and_var = "var"
        kundi Test:
            # this kundi is not nested, so the rules are different
            eleza method_and_var(self):
                rudisha "method"
            eleza test(self):
                rudisha method_and_var
            eleza actual_global(self):
                rudisha str("global")
            eleza str(self):
                rudisha str(self)

        t = Test()
        self.assertEqual(t.test(), "var")
        self.assertEqual(t.method_and_var(), "method")
        self.assertEqual(t.actual_global(), "global")

    eleza testCellIsKwonlyArg(self):
        # Issue 1409: Initialisation of a cell value,
        # when it comes kutoka a keyword-only parameter
        eleza foo(*, a=17):
            eleza bar():
                rudisha a + 5
            rudisha bar() + 3

        self.assertEqual(foo(a=42), 50)
        self.assertEqual(foo(), 25)

    eleza testRecursion(self):

        eleza f(x):
            eleza fact(n):
                ikiwa n == 0:
                    rudisha 1
                else:
                    rudisha n * fact(n - 1)
            ikiwa x >= 0:
                rudisha fact(x)
            else:
                raise ValueError("x must be >= 0")

        self.assertEqual(f(6), 720)


    eleza testUnoptimizedNamespaces(self):

        check_syntax_error(self, """ikiwa 1:
            eleza unoptimized_clash1(strip):
                eleza f(s):
                    kutoka sys agiza *
                    rudisha getrefcount(s) # ambiguity: free or local
                rudisha f
            """)

        check_syntax_error(self, """ikiwa 1:
            eleza unoptimized_clash2():
                kutoka sys agiza *
                eleza f(s):
                    rudisha getrefcount(s) # ambiguity: global or local
                rudisha f
            """)

        check_syntax_error(self, """ikiwa 1:
            eleza unoptimized_clash2():
                kutoka sys agiza *
                eleza g():
                    eleza f(s):
                        rudisha getrefcount(s) # ambiguity: global or local
                    rudisha f
            """)

        check_syntax_error(self, """ikiwa 1:
            eleza f():
                eleza g():
                    kutoka sys agiza *
                    rudisha getrefcount # global or local?
            """)

    eleza testLambdas(self):

        f1 = lambda x: lambda y: x + y
        inc = f1(1)
        plus10 = f1(10)
        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(5), 15)

        f2 = lambda x: (lambda : lambda y: x + y)()
        inc = f2(1)
        plus10 = f2(10)
        self.assertEqual(inc(1), 2)
        self.assertEqual(plus10(5), 15)

        f3 = lambda x: lambda y: global_x + y
        global_x = 1
        inc = f3(None)
        self.assertEqual(inc(2), 3)

        f8 = lambda x, y, z: lambda a, b, c: lambda : z * (b + y)
        g = f8(1, 2, 3)
        h = g(2, 4, 6)
        self.assertEqual(h(), 18)

    eleza testUnboundLocal(self):

        eleza errorInOuter():
            andika(y)
            eleza inner():
                rudisha y
            y = 1

        eleza errorInInner():
            eleza inner():
                rudisha y
            inner()
            y = 1

        self.assertRaises(UnboundLocalError, errorInOuter)
        self.assertRaises(NameError, errorInInner)

    eleza testUnboundLocal_AfterDel(self):
        # #4617: It is now legal to delete a cell variable.
        # The following functions must obviously compile,
        # and give the correct error when accessing the deleted name.
        eleza errorInOuter():
            y = 1
            del y
            andika(y)
            eleza inner():
                rudisha y

        eleza errorInInner():
            eleza inner():
                rudisha y
            y = 1
            del y
            inner()

        self.assertRaises(UnboundLocalError, errorInOuter)
        self.assertRaises(NameError, errorInInner)

    eleza testUnboundLocal_AugAssign(self):
        # test for bug #1501934: incorrect LOAD/STORE_GLOBAL generation
        exec("""ikiwa 1:
            global_x = 1
            eleza f():
                global_x += 1
            try:
                f()
            except UnboundLocalError:
                pass
            else:
                fail('scope of global_x not correctly determined')
            """, {'fail': self.fail})

    eleza testComplexDefinitions(self):

        eleza makeReturner(*lst):
            eleza returner():
                rudisha lst
            rudisha returner

        self.assertEqual(makeReturner(1,2,3)(), (1,2,3))

        eleza makeReturner2(**kwargs):
            eleza returner():
                rudisha kwargs
            rudisha returner

        self.assertEqual(makeReturner2(a=11)()['a'], 11)

    eleza testScopeOfGlobalStmt(self):
        # Examples posted by Samuele Pedroni to python-dev on 3/1/2001

        exec("""ikiwa 1:
            # I
            x = 7
            eleza f():
                x = 1
                eleza g():
                    global x
                    eleza i():
                        eleza h():
                            rudisha x
                        rudisha h()
                    rudisha i()
                rudisha g()
            self.assertEqual(f(), 7)
            self.assertEqual(x, 7)

            # II
            x = 7
            eleza f():
                x = 1
                eleza g():
                    x = 2
                    eleza i():
                        eleza h():
                            rudisha x
                        rudisha h()
                    rudisha i()
                rudisha g()
            self.assertEqual(f(), 2)
            self.assertEqual(x, 7)

            # III
            x = 7
            eleza f():
                x = 1
                eleza g():
                    global x
                    x = 2
                    eleza i():
                        eleza h():
                            rudisha x
                        rudisha h()
                    rudisha i()
                rudisha g()
            self.assertEqual(f(), 2)
            self.assertEqual(x, 2)

            # IV
            x = 7
            eleza f():
                x = 3
                eleza g():
                    global x
                    x = 2
                    eleza i():
                        eleza h():
                            rudisha x
                        rudisha h()
                    rudisha i()
                rudisha g()
            self.assertEqual(f(), 2)
            self.assertEqual(x, 2)

            # XXX what about global statements in kundi blocks?
            # do they affect methods?

            x = 12
            kundi Global:
                global x
                x = 13
                eleza set(self, val):
                    x = val
                eleza get(self):
                    rudisha x

            g = Global()
            self.assertEqual(g.get(), 13)
            g.set(15)
            self.assertEqual(g.get(), 13)
            """)

    eleza testLeaks(self):

        kundi Foo:
            count = 0

            eleza __init__(self):
                Foo.count += 1

            eleza __del__(self):
                Foo.count -= 1

        eleza f1():
            x = Foo()
            eleza f2():
                rudisha x
            f2()

        for i in range(100):
            f1()

        self.assertEqual(Foo.count, 0)

    eleza testClassAndGlobal(self):

        exec("""ikiwa 1:
            eleza test(x):
                kundi Foo:
                    global x
                    eleza __call__(self, y):
                        rudisha x + y
                rudisha Foo()

            x = 0
            self.assertEqual(test(6)(2), 8)
            x = -1
            self.assertEqual(test(3)(2), 5)

            looked_up_by_load_name = False
            kundi X:
                # Implicit globals inside classes are be looked up by LOAD_NAME, not
                # LOAD_GLOBAL.
                locals()['looked_up_by_load_name'] = True
                passed = looked_up_by_load_name

            self.assertTrue(X.passed)
            """)

    eleza testLocalsFunction(self):

        eleza f(x):
            eleza g(y):
                eleza h(z):
                    rudisha y + z
                w = x + y
                y += 3
                rudisha locals()
            rudisha g

        d = f(2)(4)
        self.assertIn('h', d)
        del d['h']
        self.assertEqual(d, {'x': 2, 'y': 7, 'w': 6})

    eleza testLocalsClass(self):
        # This test verifies that calling locals() does not pollute
        # the local namespace of the kundi with free variables.  Old
        # versions of Python had a bug, where a free variable being
        # passed through a kundi namespace would be inserted into
        # locals() by locals() or exec or a trace function.
        #
        # The real bug lies in frame code that copies variables
        # between fast locals and the locals dict, e.g. when executing
        # a trace function.

        eleza f(x):
            kundi C:
                x = 12
                eleza m(self):
                    rudisha x
                locals()
            rudisha C

        self.assertEqual(f(1).x, 12)

        eleza f(x):
            kundi C:
                y = x
                eleza m(self):
                    rudisha x
                z = list(locals())
            rudisha C

        varnames = f(1).z
        self.assertNotIn("x", varnames)
        self.assertIn("y", varnames)

    @cpython_only
    eleza testLocalsClass_WithTrace(self):
        # Issue23728: after the trace function returns, the locals()
        # dictionary is used to update all variables, this used to
        # include free variables. But in kundi statements, free
        # variables are not inserted...
        agiza sys
        self.addCleanup(sys.settrace, sys.gettrace())
        sys.settrace(lambda a,b,c:None)
        x = 12

        kundi C:
            eleza f(self):
                rudisha x

        self.assertEqual(x, 12) # Used to raise UnboundLocalError

    eleza testBoundAndFree(self):
        # var is bound and free in class

        eleza f(x):
            kundi C:
                eleza m(self):
                    rudisha x
                a = x
            rudisha C

        inst = f(3)()
        self.assertEqual(inst.a, inst.m())

    @cpython_only
    eleza testInteractionWithTraceFunc(self):

        agiza sys
        eleza tracer(a,b,c):
            rudisha tracer

        eleza adaptgetter(name, klass, getter):
            kind, des = getter
            ikiwa kind == 1:       # AV happens when stepping kutoka this line to next
                ikiwa des == "":
                    des = "_%s__%s" % (klass.__name__, name)
                rudisha lambda obj: getattr(obj, des)

        kundi TestClass:
            pass

        self.addCleanup(sys.settrace, sys.gettrace())
        sys.settrace(tracer)
        adaptgetter("foo", TestClass, (1, ""))
        sys.settrace(None)

        self.assertRaises(TypeError, sys.settrace)

    eleza testEvalExecFreeVars(self):

        eleza f(x):
            rudisha lambda: x + 1

        g = f(3)
        self.assertRaises(TypeError, eval, g.__code__)

        try:
            exec(g.__code__, {})
        except TypeError:
            pass
        else:
            self.fail("exec should have failed, because code contained free vars")

    eleza testListCompLocalVars(self):

        try:
            andika(bad)
        except NameError:
            pass
        else:
            andika("bad should not be defined")

        eleza x():
            [bad for s in 'a b' for bad in s.split()]

        x()
        try:
            andika(bad)
        except NameError:
            pass

    eleza testEvalFreeVars(self):

        eleza f(x):
            eleza g():
                x
                eval("x + 1")
            rudisha g

        f(4)()

    eleza testFreeingCell(self):
        # Test what happens when a finalizer accesses
        # the cell where the object was stored.
        kundi Special:
            eleza __del__(self):
                nestedcell_get()

    eleza testNonLocalFunction(self):

        eleza f(x):
            eleza inc():
                nonlocal x
                x += 1
                rudisha x
            eleza dec():
                nonlocal x
                x -= 1
                rudisha x
            rudisha inc, dec

        inc, dec = f(0)
        self.assertEqual(inc(), 1)
        self.assertEqual(inc(), 2)
        self.assertEqual(dec(), 1)
        self.assertEqual(dec(), 0)

    eleza testNonLocalMethod(self):
        eleza f(x):
            kundi c:
                eleza inc(self):
                    nonlocal x
                    x += 1
                    rudisha x
                eleza dec(self):
                    nonlocal x
                    x -= 1
                    rudisha x
            rudisha c()
        c = f(0)
        self.assertEqual(c.inc(), 1)
        self.assertEqual(c.inc(), 2)
        self.assertEqual(c.dec(), 1)
        self.assertEqual(c.dec(), 0)

    eleza testGlobalInParallelNestedFunctions(self):
        # A symbol table bug leaked the global statement kutoka one
        # function to other nested functions in the same block.
        # This test verifies that a global statement in the first
        # function does not affect the second function.
        local_ns = {}
        global_ns = {}
        exec("""ikiwa 1:
            eleza f():
                y = 1
                eleza g():
                    global y
                    rudisha y
                eleza h():
                    rudisha y + 1
                rudisha g, h
            y = 9
            g, h = f()
            result9 = g()
            result2 = h()
            """, local_ns, global_ns)
        self.assertEqual(2, global_ns["result2"])
        self.assertEqual(9, global_ns["result9"])

    eleza testNonLocalClass(self):

        eleza f(x):
            kundi c:
                nonlocal x
                x += 1
                eleza get(self):
                    rudisha x
            rudisha c()

        c = f(0)
        self.assertEqual(c.get(), 1)
        self.assertNotIn("x", c.__class__.__dict__)


    eleza testNonLocalGenerator(self):

        eleza f(x):
            eleza g(y):
                nonlocal x
                for i in range(y):
                    x += 1
                    yield x
            rudisha g

        g = f(0)
        self.assertEqual(list(g(5)), [1, 2, 3, 4, 5])

    eleza testNestedNonLocal(self):

        eleza f(x):
            eleza g():
                nonlocal x
                x -= 2
                eleza h():
                    nonlocal x
                    x += 4
                    rudisha x
                rudisha h
            rudisha g

        g = f(1)
        h = g()
        self.assertEqual(h(), 3)

    eleza testTopIsNotSignificant(self):
        # See #9997.
        eleza top(a):
            pass
        eleza b():
            global a

    eleza testClassNamespaceOverridesClosure(self):
        # See #17853.
        x = 42
        kundi X:
            locals()["x"] = 43
            y = x
        self.assertEqual(X.y, 43)
        kundi X:
            locals()["x"] = 43
            del x
        self.assertFalse(hasattr(X, "x"))
        self.assertEqual(x, 42)

    @cpython_only
    eleza testCellLeak(self):
        # Issue 17927.
        #
        # The issue was that ikiwa self was part of a cycle involving the
        # frame of a method call, *and* the method contained a nested
        # function referencing self, thereby forcing 'self' into a
        # cell, setting self to None would not be enough to break the
        # frame -- the frame had another reference to the instance,
        # which could not be cleared by the code running in the frame
        # (though it will be cleared when the frame is collected).
        # Without the lambda, setting self to None is enough to break
        # the cycle.
        kundi Tester:
            eleza dig(self):
                ikiwa 0:
                    lambda: self
                try:
                    1/0
                except Exception as exc:
                    self.exc = exc
                self = None  # Break the cycle
        tester = Tester()
        tester.dig()
        ref = weakref.ref(tester)
        del tester
        self.assertIsNone(ref())


ikiwa __name__ == '__main__':
    unittest.main()
