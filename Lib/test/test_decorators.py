agiza unittest

eleza funcattrs(**kwds):
    eleza decorate(func):
        func.__dict__.update(kwds)
        rudisha func
    rudisha decorate

kundi MiscDecorators (object):
    @staticmethod
    eleza author(name):
        eleza decorate(func):
            func.__dict__['author'] = name
            rudisha func
        rudisha decorate

# -----------------------------------------------

kundi DbcheckError (Exception):
    eleza __init__(self, exprstr, func, args, kwds):
        # A real version of this would set attributes here
        Exception.__init__(self, "dbcheck %r failed (func=%s args=%s kwds=%s)" %
                           (exprstr, func, args, kwds))


eleza dbcheck(exprstr, globals=None, locals=None):
    "Decorator to implement debugging assertions"
    eleza decorate(func):
        expr = compile(exprstr, "dbcheck-%s" % func.__name__, "eval")
        eleza check(*args, **kwds):
            ikiwa not eval(expr, globals, locals):
                raise DbcheckError(exprstr, func, args, kwds)
            rudisha func(*args, **kwds)
        rudisha check
    rudisha decorate

# -----------------------------------------------

eleza countcalls(counts):
    "Decorator to count calls to a function"
    eleza decorate(func):
        func_name = func.__name__
        counts[func_name] = 0
        eleza call(*args, **kwds):
            counts[func_name] += 1
            rudisha func(*args, **kwds)
        call.__name__ = func_name
        rudisha call
    rudisha decorate

# -----------------------------------------------

eleza memoize(func):
    saved = {}
    eleza call(*args):
        try:
            rudisha saved[args]
        except KeyError:
            res = func(*args)
            saved[args] = res
            rudisha res
        except TypeError:
            # Unhashable argument
            rudisha func(*args)
    call.__name__ = func.__name__
    rudisha call

# -----------------------------------------------

kundi TestDecorators(unittest.TestCase):

    eleza test_single(self):
        kundi C(object):
            @staticmethod
            eleza foo(): rudisha 42
        self.assertEqual(C.foo(), 42)
        self.assertEqual(C().foo(), 42)

    eleza test_staticmethod_function(self):
        @staticmethod
        eleza notamethod(x):
            rudisha x
        self.assertRaises(TypeError, notamethod, 1)

    eleza test_dotted(self):
        decorators = MiscDecorators()
        @decorators.author('Cleese')
        eleza foo(): rudisha 42
        self.assertEqual(foo(), 42)
        self.assertEqual(foo.author, 'Cleese')

    eleza test_argforms(self):
        # A few tests of argument passing, as we use restricted form
        # of expressions for decorators.

        eleza noteargs(*args, **kwds):
            eleza decorate(func):
                setattr(func, 'dbval', (args, kwds))
                rudisha func
            rudisha decorate

        args = ( 'Now', 'is', 'the', 'time' )
        kwds = dict(one=1, two=2)
        @noteargs(*args, **kwds)
        eleza f1(): rudisha 42
        self.assertEqual(f1(), 42)
        self.assertEqual(f1.dbval, (args, kwds))

        @noteargs('terry', 'gilliam', eric='idle', john='cleese')
        eleza f2(): rudisha 84
        self.assertEqual(f2(), 84)
        self.assertEqual(f2.dbval, (('terry', 'gilliam'),
                                     dict(eric='idle', john='cleese')))

        @noteargs(1, 2,)
        eleza f3(): pass
        self.assertEqual(f3.dbval, ((1, 2), {}))

    eleza test_dbcheck(self):
        @dbcheck('args[1] is not None')
        eleza f(a, b):
            rudisha a + b
        self.assertEqual(f(1, 2), 3)
        self.assertRaises(DbcheckError, f, 1, None)

    eleza test_memoize(self):
        counts = {}

        @memoize
        @countcalls(counts)
        eleza double(x):
            rudisha x * 2
        self.assertEqual(double.__name__, 'double')

        self.assertEqual(counts, dict(double=0))

        # Only the first call with a given argument bumps the call count:
        #
        self.assertEqual(double(2), 4)
        self.assertEqual(counts['double'], 1)
        self.assertEqual(double(2), 4)
        self.assertEqual(counts['double'], 1)
        self.assertEqual(double(3), 6)
        self.assertEqual(counts['double'], 2)

        # Unhashable arguments do not get memoized:
        #
        self.assertEqual(double([10]), [10, 10])
        self.assertEqual(counts['double'], 3)
        self.assertEqual(double([10]), [10, 10])
        self.assertEqual(counts['double'], 4)

    eleza test_errors(self):
        # Test syntax restrictions - these are all compile-time errors:
        #
        for expr in [ "1+2", "x[3]", "(1, 2)" ]:
            # Sanity check: is expr is a valid expression by itself?
            compile(expr, "testexpr", "exec")

            codestr = "@%s\neleza f(): pass" % expr
            self.assertRaises(SyntaxError, compile, codestr, "test", "exec")

        # You can't put multiple decorators on a single line:
        #
        self.assertRaises(SyntaxError, compile,
                          "@f1 @f2\neleza f(): pass", "test", "exec")

        # Test runtime errors

        eleza unimp(func):
            raise NotImplementedError
        context = dict(nullval=None, unimp=unimp)

        for expr, exc in [ ("undef", NameError),
                           ("nullval", TypeError),
                           ("nullval.attr", AttributeError),
                           ("unimp", NotImplementedError)]:
            codestr = "@%s\neleza f(): pass\nassert f() is None" % expr
            code = compile(codestr, "test", "exec")
            self.assertRaises(exc, eval, code, context)

    eleza test_double(self):
        kundi C(object):
            @funcattrs(abc=1, xyz="haha")
            @funcattrs(booh=42)
            eleza foo(self): rudisha 42
        self.assertEqual(C().foo(), 42)
        self.assertEqual(C.foo.abc, 1)
        self.assertEqual(C.foo.xyz, "haha")
        self.assertEqual(C.foo.booh, 42)

    eleza test_order(self):
        # Test that decorators are applied in the proper order to the function
        # they are decorating.
        eleza callnum(num):
            """Decorator factory that returns a decorator that replaces the
            passed-in function with one that returns the value of 'num'"""
            eleza deco(func):
                rudisha lambda: num
            rudisha deco
        @callnum(2)
        @callnum(1)
        eleza foo(): rudisha 42
        self.assertEqual(foo(), 2,
                            "Application order of decorators is incorrect")

    eleza test_eval_order(self):
        # Evaluating a decorated function involves four steps for each
        # decorator-maker (the function that returns a decorator):
        #
        #    1: Evaluate the decorator-maker name
        #    2: Evaluate the decorator-maker arguments (ikiwa any)
        #    3: Call the decorator-maker to make a decorator
        #    4: Call the decorator
        #
        # When there are multiple decorators, these steps should be
        # performed in the above order for each decorator, but we should
        # iterate through the decorators in the reverse of the order they
        # appear in the source.

        actions = []

        eleza make_decorator(tag):
            actions.append('makedec' + tag)
            eleza decorate(func):
                actions.append('calldec' + tag)
                rudisha func
            rudisha decorate

        kundi NameLookupTracer (object):
            eleza __init__(self, index):
                self.index = index

            eleza __getattr__(self, fname):
                ikiwa fname == 'make_decorator':
                    opname, res = ('evalname', make_decorator)
                elikiwa fname == 'arg':
                    opname, res = ('evalargs', str(self.index))
                else:
                    assert False, "Unknown attrname %s" % fname
                actions.append('%s%d' % (opname, self.index))
                rudisha res

        c1, c2, c3 = map(NameLookupTracer, [ 1, 2, 3 ])

        expected_actions = [ 'evalname1', 'evalargs1', 'makedec1',
                             'evalname2', 'evalargs2', 'makedec2',
                             'evalname3', 'evalargs3', 'makedec3',
                             'calldec3', 'calldec2', 'calldec1' ]

        actions = []
        @c1.make_decorator(c1.arg)
        @c2.make_decorator(c2.arg)
        @c3.make_decorator(c3.arg)
        eleza foo(): rudisha 42
        self.assertEqual(foo(), 42)

        self.assertEqual(actions, expected_actions)

        # Test the equivalence claim in chapter 7 of the reference manual.
        #
        actions = []
        eleza bar(): rudisha 42
        bar = c1.make_decorator(c1.arg)(c2.make_decorator(c2.arg)(c3.make_decorator(c3.arg)(bar)))
        self.assertEqual(bar(), 42)
        self.assertEqual(actions, expected_actions)

kundi TestClassDecorators(unittest.TestCase):

    eleza test_simple(self):
        eleza plain(x):
            x.extra = 'Hello'
            rudisha x
        @plain
        kundi C(object): pass
        self.assertEqual(C.extra, 'Hello')

    eleza test_double(self):
        eleza ten(x):
            x.extra = 10
            rudisha x
        eleza add_five(x):
            x.extra += 5
            rudisha x

        @add_five
        @ten
        kundi C(object): pass
        self.assertEqual(C.extra, 15)

    eleza test_order(self):
        eleza applied_first(x):
            x.extra = 'first'
            rudisha x
        eleza applied_second(x):
            x.extra = 'second'
            rudisha x
        @applied_second
        @applied_first
        kundi C(object): pass
        self.assertEqual(C.extra, 'second')

ikiwa __name__ == "__main__":
    unittest.main()
