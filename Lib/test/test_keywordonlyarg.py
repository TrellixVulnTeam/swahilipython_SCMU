"""Unit tests kila the keyword only argument specified kwenye PEP 3102."""

__author__ = "Jiwon Seo"
__email__ = "seojiwon at gmail dot com"

agiza unittest

eleza posonly_sum(pos_arg1, *arg, **kwarg):
    rudisha pos_arg1 + sum(arg) + sum(kwarg.values())
eleza keywordonly_sum(*, k1=0, k2):
    rudisha k1 + k2
eleza keywordonly_nodefaults_sum(*, k1, k2):
    rudisha k1 + k2
eleza keywordonly_and_kwarg_sum(*, k1, k2, **kwarg):
    rudisha k1 + k2 + sum(kwarg.values())
eleza mixedargs_sum(a, b=0, *arg, k1, k2=0):
    rudisha a + b + k1 + k2 + sum(arg)
eleza mixedargs_sum2(a, b=0, *arg, k1, k2=0, **kwargs):
    rudisha a + b + k1 + k2 + sum(arg) + sum(kwargs.values())

eleza sortnum(*nums, reverse=Uongo):
    rudisha sorted(list(nums), reverse=reverse)

eleza sortwords(*words, reverse=Uongo, **kwargs):
    rudisha sorted(list(words), reverse=reverse)

kundi Foo:
    eleza __init__(self, *, k1, k2=0):
        self.k1 = k1
        self.k2 = k2
    eleza set(self, p1, *, k1, k2):
        self.k1 = k1
        self.k2 = k2
    eleza sum(self):
        rudisha self.k1 + self.k2

kundi KeywordOnlyArgTestCase(unittest.TestCase):
    eleza assertRaisesSyntaxError(self, codestr):
        eleza shouldRaiseSyntaxError(s):
            compile(s, "<test>", "single")
        self.assertRaises(SyntaxError, shouldRaiseSyntaxError, codestr)

    eleza testSyntaxErrorForFunctionDefinition(self):
        self.assertRaisesSyntaxError("eleza f(p, *):\n  pita\n")
        self.assertRaisesSyntaxError("eleza f(p1, *, p1=100):\n  pita\n")
        self.assertRaisesSyntaxError("eleza f(p1, *k1, k1=100):\n  pita\n")
        self.assertRaisesSyntaxError("eleza f(p1, *, k1, k1=100):\n  pita\n")
        self.assertRaisesSyntaxError("eleza f(p1, *, **k1):\n  pita\n")
        self.assertRaisesSyntaxError("eleza f(p1, *, k1, **k1):\n  pita\n")
        self.assertRaisesSyntaxError("eleza f(p1, *, Tupu, **k1):\n  pita\n")
        self.assertRaisesSyntaxError("eleza f(p, *, (k1, k2), **kw):\n  pita\n")

    eleza testSyntaxForManyArguments(self):
        # more than 255 positional arguments, should compile ok
        funeleza = "eleza f(%s):\n  pita\n" % ', '.join('i%d' % i kila i kwenye range(300))
        compile(fundef, "<test>", "single")
        # more than 255 keyword-only arguments, should compile ok
        funeleza = "eleza f(*, %s):\n  pita\n" % ', '.join('i%d' % i kila i kwenye range(300))
        compile(fundef, "<test>", "single")

    eleza testTooManyPositionalErrorMessage(self):
        eleza f(a, b=Tupu, *, c=Tupu):
            pita
        with self.assertRaises(TypeError) kama exc:
            f(1, 2, 3)
        expected = "f() takes kutoka 1 to 2 positional arguments but 3 were given"
        self.assertEqual(str(exc.exception), expected)

    eleza testSyntaxErrorForFunctionCall(self):
        self.assertRaisesSyntaxError("f(p, k=1, p2)")
        self.assertRaisesSyntaxError("f(p, k1=50, *(1,2), k1=100)")

    eleza testRaiseErrorFuncallWithUnexpectedKeywordArgument(self):
        self.assertRaises(TypeError, keywordonly_sum, ())
        self.assertRaises(TypeError, keywordonly_nodefaults_sum, ())
        self.assertRaises(TypeError, Foo, ())
        jaribu:
            keywordonly_sum(k2=100, non_existing_arg=200)
            self.fail("should ashiria TypeError")
        tatizo TypeError:
            pita
        jaribu:
            keywordonly_nodefaults_sum(k2=2)
            self.fail("should ashiria TypeError")
        tatizo TypeError:
            pita

    eleza testFunctionCall(self):
        self.assertEqual(1, posonly_sum(1))
        self.assertEqual(1+2, posonly_sum(1,**{"2":2}))
        self.assertEqual(1+2+3, posonly_sum(1,*(2,3)))
        self.assertEqual(1+2+3+4, posonly_sum(1,*(2,3),**{"4":4}))

        self.assertEqual(1, keywordonly_sum(k2=1))
        self.assertEqual(1+2, keywordonly_sum(k1=1, k2=2))

        self.assertEqual(1+2, keywordonly_and_kwarg_sum(k1=1, k2=2))
        self.assertEqual(1+2+3, keywordonly_and_kwarg_sum(k1=1, k2=2, k3=3))
        self.assertEqual(1+2+3+4,
                         keywordonly_and_kwarg_sum(k1=1, k2=2,
                                                    **{"a":3,"b":4}))

        self.assertEqual(1+2, mixedargs_sum(1, k1=2))
        self.assertEqual(1+2+3, mixedargs_sum(1, 2, k1=3))
        self.assertEqual(1+2+3+4, mixedargs_sum(1, 2, k1=3, k2=4))
        self.assertEqual(1+2+3+4+5, mixedargs_sum(1, 2, 3, k1=4, k2=5))

        self.assertEqual(1+2, mixedargs_sum2(1, k1=2))
        self.assertEqual(1+2+3, mixedargs_sum2(1, 2, k1=3))
        self.assertEqual(1+2+3+4, mixedargs_sum2(1, 2, k1=3, k2=4))
        self.assertEqual(1+2+3+4+5, mixedargs_sum2(1, 2, 3, k1=4, k2=5))
        self.assertEqual(1+2+3+4+5+6,
                         mixedargs_sum2(1, 2, 3, k1=4, k2=5, k3=6))
        self.assertEqual(1+2+3+4+5+6,
                         mixedargs_sum2(1, 2, 3, k1=4, **{'k2':5, 'k3':6}))

        self.assertEqual(1, Foo(k1=1).sum())
        self.assertEqual(1+2, Foo(k1=1,k2=2).sum())

        self.assertEqual([1,2,3], sortnum(3,2,1))
        self.assertEqual([3,2,1], sortnum(1,2,3, reverse=Kweli))

        self.assertEqual(['a','b','c'], sortwords('a','c','b'))
        self.assertEqual(['c','b','a'], sortwords('a','c','b', reverse=Kweli))
        self.assertEqual(['c','b','a'],
                         sortwords('a','c','b', reverse=Kweli, ignore='ignore'))

    eleza testKwDefaults(self):
        eleza foo(p1,p2=0, *, k1, k2=0):
            rudisha p1 + p2 + k1 + k2

        self.assertEqual(2, foo.__code__.co_kwonlyargcount)
        self.assertEqual({"k2":0}, foo.__kwdefaults__)
        foo.__kwdefaults__ = {"k1":0}
        jaribu:
            foo(1,k1=10)
            self.fail("__kwdefaults__ ni sio properly changed")
        tatizo TypeError:
            pita

    eleza test_kwonly_methods(self):
        kundi Example:
            eleza f(self, *, k1=1, k2=2):
                rudisha k1, k2

        self.assertEqual(Example().f(k1=1, k2=2), (1, 2))
        self.assertEqual(Example.f(Example(), k1=1, k2=2), (1, 2))
        self.assertRaises(TypeError, Example.f, k1=1, k2=2)

    eleza test_issue13343(self):
        # The Python compiler must scan all symbols of a function to
        # determine their scope: global, local, cell...
        # This was sio done kila the default values of keyword
        # arguments kwenye a lambda definition, na the following line
        # used to fail with a SystemError.
        lambda *, k1=unittest: Tupu

    eleza test_mangling(self):
        kundi X:
            eleza f(self, *, __a=42):
                rudisha __a
        self.assertEqual(X().f(), 42)

    eleza test_default_evaluation_order(self):
        # See issue 16967
        a = 42
        with self.assertRaises(NameError) kama err:
            eleza f(v=a, x=b, *, y=c, z=d):
                pita
        self.assertEqual(str(err.exception), "name 'b' ni sio defined")
        with self.assertRaises(NameError) kama err:
            f = lambda v=a, x=b, *, y=c, z=d: Tupu
        self.assertEqual(str(err.exception), "name 'b' ni sio defined")


ikiwa __name__ == "__main__":
    unittest.main()
