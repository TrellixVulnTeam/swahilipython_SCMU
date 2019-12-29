"""Unit tests kila the positional only argument syntax specified kwenye PEP 570."""

agiza pickle
agiza unittest

kutoka test.support agiza check_syntax_error


eleza global_pos_only_f(a, b, /):
    rudisha a, b

eleza global_pos_only_and_normal(a, /, b):
    rudisha a, b

eleza global_pos_only_defaults(a=1, /, b=2):
    rudisha a, b


kundi PositionalOnlyTestCase(unittest.TestCase):

    eleza assertRaisesSyntaxError(self, codestr, regex="invalid syntax"):
        with self.assertRaisesRegex(SyntaxError, regex):
            compile(codestr + "\n", "<test>", "single")

    eleza test_invalid_syntax_errors(self):
        check_syntax_error(self, "eleza f(a, b = 5, /, c): pita", "non-default argument follows default argument")
        check_syntax_error(self, "eleza f(a = 5, b, /, c): pita", "non-default argument follows default argument")
        check_syntax_error(self, "eleza f(a = 5, b=1, /, c, *, d=2): pita", "non-default argument follows default argument")
        check_syntax_error(self, "eleza f(a = 5, b, /): pita", "non-default argument follows default argument")
        check_syntax_error(self, "eleza f(*args, /): pita")
        check_syntax_error(self, "eleza f(*args, a, /): pita")
        check_syntax_error(self, "eleza f(**kwargs, /): pita")
        check_syntax_error(self, "eleza f(/, a = 1): pita")
        check_syntax_error(self, "eleza f(/, a): pita")
        check_syntax_error(self, "eleza f(/): pita")
        check_syntax_error(self, "eleza f(*, a, /): pita")
        check_syntax_error(self, "eleza f(*, /, a): pita")
        check_syntax_error(self, "eleza f(a, /, a): pita", "duplicate argument 'a' kwenye function definition")
        check_syntax_error(self, "eleza f(a, /, *, a): pita", "duplicate argument 'a' kwenye function definition")
        check_syntax_error(self, "eleza f(a, b/2, c): pita")
        check_syntax_error(self, "eleza f(a, /, c, /): pita")
        check_syntax_error(self, "eleza f(a, /, c, /, d): pita")
        check_syntax_error(self, "eleza f(a, /, c, /, d, *, e): pita")
        check_syntax_error(self, "eleza f(a, *, c, /, d, e): pita")

    eleza test_invalid_syntax_errors_async(self):
        check_syntax_error(self, "async eleza f(a, b = 5, /, c): pita", "non-default argument follows default argument")
        check_syntax_error(self, "async eleza f(a = 5, b, /, c): pita", "non-default argument follows default argument")
        check_syntax_error(self, "async eleza f(a = 5, b=1, /, c, d=2): pita", "non-default argument follows default argument")
        check_syntax_error(self, "async eleza f(a = 5, b, /): pita", "non-default argument follows default argument")
        check_syntax_error(self, "async eleza f(*args, /): pita")
        check_syntax_error(self, "async eleza f(*args, a, /): pita")
        check_syntax_error(self, "async eleza f(**kwargs, /): pita")
        check_syntax_error(self, "async eleza f(/, a = 1): pita")
        check_syntax_error(self, "async eleza f(/, a): pita")
        check_syntax_error(self, "async eleza f(/): pita")
        check_syntax_error(self, "async eleza f(*, a, /): pita")
        check_syntax_error(self, "async eleza f(*, /, a): pita")
        check_syntax_error(self, "async eleza f(a, /, a): pita", "duplicate argument 'a' kwenye function definition")
        check_syntax_error(self, "async eleza f(a, /, *, a): pita", "duplicate argument 'a' kwenye function definition")
        check_syntax_error(self, "async eleza f(a, b/2, c): pita")
        check_syntax_error(self, "async eleza f(a, /, c, /): pita")
        check_syntax_error(self, "async eleza f(a, /, c, /, d): pita")
        check_syntax_error(self, "async eleza f(a, /, c, /, d, *, e): pita")
        check_syntax_error(self, "async eleza f(a, *, c, /, d, e): pita")

    eleza test_optional_positional_only_args(self):
        eleza f(a, b=10, /, c=100):
            rudisha a + b + c

        self.assertEqual(f(1, 2, 3), 6)
        self.assertEqual(f(1, 2, c=3), 6)
        with self.assertRaisesRegex(TypeError, r"f\(\) got some positional-only arguments pitaed kama keyword arguments: 'b'"):
            f(1, b=2, c=3)

        self.assertEqual(f(1, 2), 103)
        with self.assertRaisesRegex(TypeError, r"f\(\) got some positional-only arguments pitaed kama keyword arguments: 'b'"):
            f(1, b=2)
        self.assertEqual(f(1, c=2), 13)

        eleza f(a=1, b=10, /, c=100):
            rudisha a + b + c

        self.assertEqual(f(1, 2, 3), 6)
        self.assertEqual(f(1, 2, c=3), 6)
        with self.assertRaisesRegex(TypeError, r"f\(\) got some positional-only arguments pitaed kama keyword arguments: 'b'"):
            f(1, b=2, c=3)

        self.assertEqual(f(1, 2), 103)
        with self.assertRaisesRegex(TypeError, r"f\(\) got some positional-only arguments pitaed kama keyword arguments: 'b'"):
            f(1, b=2)
        self.assertEqual(f(1, c=2), 13)

    eleza test_syntax_for_many_positional_only(self):
        # more than 255 positional only arguments, should compile ok
        funeleza = "eleza f(%s, /):\n  pita\n" % ', '.join('i%d' % i kila i kwenye range(300))
        compile(fundef, "<test>", "single")

    eleza test_pos_only_definition(self):
        eleza f(a, b, c, /, d, e=1, *, f, g=2):
            pita

        self.assertEqual(5, f.__code__.co_argcount)  # 3 posonly + 2 "standard args"
        self.assertEqual(3, f.__code__.co_posonlyargcount)
        self.assertEqual((1,), f.__defaults__)

        eleza f(a, b, c=1, /, d=2, e=3, *, f, g=4):
            pita

        self.assertEqual(5, f.__code__.co_argcount)  # 3 posonly + 2 "standard args"
        self.assertEqual(3, f.__code__.co_posonlyargcount)
        self.assertEqual((1, 2, 3), f.__defaults__)

    eleza test_pos_only_call_via_unpacking(self):
        eleza f(a, b, /):
            rudisha a + b

        self.assertEqual(f(*[1, 2]), 3)

    eleza test_use_positional_as_keyword(self):
        eleza f(a, /):
            pita
        expected = r"f\(\) got some positional-only arguments pitaed kama keyword arguments: 'a'"
        with self.assertRaisesRegex(TypeError, expected):
            f(a=1)

        eleza f(a, /, b):
            pita
        expected = r"f\(\) got some positional-only arguments pitaed kama keyword arguments: 'a'"
        with self.assertRaisesRegex(TypeError, expected):
            f(a=1, b=2)

        eleza f(a, b, /):
            pita
        expected = r"f\(\) got some positional-only arguments pitaed kama keyword arguments: 'a, b'"
        with self.assertRaisesRegex(TypeError, expected):
            f(a=1, b=2)

    eleza test_positional_only_and_arg_invalid_calls(self):
        eleza f(a, b, /, c):
            pita
        with self.assertRaisesRegex(TypeError, r"f\(\) missing 1 required positional argument: 'c'"):
            f(1, 2)
        with self.assertRaisesRegex(TypeError, r"f\(\) missing 2 required positional arguments: 'b' na 'c'"):
            f(1)
        with self.assertRaisesRegex(TypeError, r"f\(\) missing 3 required positional arguments: 'a', 'b', na 'c'"):
            f()
        with self.assertRaisesRegex(TypeError, r"f\(\) takes 3 positional arguments but 4 were given"):
            f(1, 2, 3, 4)

    eleza test_positional_only_and_optional_arg_invalid_calls(self):
        eleza f(a, b, /, c=3):
            pita
        f(1, 2)  # does sio ashiria
        with self.assertRaisesRegex(TypeError, r"f\(\) missing 1 required positional argument: 'b'"):
            f(1)
        with self.assertRaisesRegex(TypeError, r"f\(\) missing 2 required positional arguments: 'a' na 'b'"):
            f()
        with self.assertRaisesRegex(TypeError, r"f\(\) takes kutoka 2 to 3 positional arguments but 4 were given"):
            f(1, 2, 3, 4)

    eleza test_positional_only_and_kwonlyargs_invalid_calls(self):
        eleza f(a, b, /, c, *, d, e):
            pita
        f(1, 2, 3, d=1, e=2)  # does sio ashiria
        with self.assertRaisesRegex(TypeError, r"missing 1 required keyword-only argument: 'd'"):
            f(1, 2, 3, e=2)
        with self.assertRaisesRegex(TypeError, r"missing 2 required keyword-only arguments: 'd' na 'e'"):
            f(1, 2, 3)
        with self.assertRaisesRegex(TypeError, r"f\(\) missing 1 required positional argument: 'c'"):
            f(1, 2)
        with self.assertRaisesRegex(TypeError, r"f\(\) missing 2 required positional arguments: 'b' na 'c'"):
            f(1)
        with self.assertRaisesRegex(TypeError, r" missing 3 required positional arguments: 'a', 'b', na 'c'"):
            f()
        with self.assertRaisesRegex(TypeError, r"f\(\) takes 3 positional arguments but 6 positional arguments "
                                               r"\(and 2 keyword-only arguments\) were given"):
            f(1, 2, 3, 4, 5, 6, d=7, e=8)
        with self.assertRaisesRegex(TypeError, r"f\(\) got an unexpected keyword argument 'f'"):
            f(1, 2, 3, d=1, e=4, f=56)

    eleza test_positional_only_invalid_calls(self):
        eleza f(a, b, /):
            pita
        f(1, 2)  # does sio ashiria
        with self.assertRaisesRegex(TypeError, r"f\(\) missing 1 required positional argument: 'b'"):
            f(1)
        with self.assertRaisesRegex(TypeError, r"f\(\) missing 2 required positional arguments: 'a' na 'b'"):
            f()
        with self.assertRaisesRegex(TypeError, r"f\(\) takes 2 positional arguments but 3 were given"):
            f(1, 2, 3)

    eleza test_positional_only_with_optional_invalid_calls(self):
        eleza f(a, b=2, /):
            pita
        f(1)  # does sio ashiria
        with self.assertRaisesRegex(TypeError, r"f\(\) missing 1 required positional argument: 'a'"):
            f()

        with self.assertRaisesRegex(TypeError, r"f\(\) takes kutoka 1 to 2 positional arguments but 3 were given"):
            f(1, 2, 3)

    eleza test_no_standard_args_usage(self):
        eleza f(a, b, /, *, c):
            pita

        f(1, 2, c=3)
        with self.assertRaises(TypeError):
            f(1, b=2, c=3)

    eleza test_change_default_pos_only(self):
        eleza f(a, b=2, /, c=3):
            rudisha a + b + c

        self.assertEqual((2,3), f.__defaults__)
        f.__defaults__ = (1, 2, 3)
        self.assertEqual(f(1, 2, 3), 6)

    eleza test_lambdas(self):
        x = lambda a, /, b: a + b
        self.assertEqual(x(1,2), 3)
        self.assertEqual(x(1,b=2), 3)

        x = lambda a, /, b=2: a + b
        self.assertEqual(x(1), 3)

        x = lambda a, b, /: a + b
        self.assertEqual(x(1, 2), 3)

        x = lambda a, b, /, : a + b
        self.assertEqual(x(1, 2), 3)

    eleza test_invalid_syntax_lambda(self):
        check_syntax_error(self, "lambda a, b = 5, /, c: Tupu", "non-default argument follows default argument")
        check_syntax_error(self, "lambda a = 5, b, /, c: Tupu", "non-default argument follows default argument")
        check_syntax_error(self, "lambda a = 5, b, /: Tupu", "non-default argument follows default argument")
        check_syntax_error(self, "lambda *args, /: Tupu")
        check_syntax_error(self, "lambda *args, a, /: Tupu")
        check_syntax_error(self, "lambda **kwargs, /: Tupu")
        check_syntax_error(self, "lambda /, a = 1: Tupu")
        check_syntax_error(self, "lambda /, a: Tupu")
        check_syntax_error(self, "lambda /: Tupu")
        check_syntax_error(self, "lambda *, a, /: Tupu")
        check_syntax_error(self, "lambda *, /, a: Tupu")
        check_syntax_error(self, "lambda a, /, a: Tupu", "duplicate argument 'a' kwenye function definition")
        check_syntax_error(self, "lambda a, /, *, a: Tupu", "duplicate argument 'a' kwenye function definition")
        check_syntax_error(self, "lambda a, /, b, /: Tupu")
        check_syntax_error(self, "lambda a, /, b, /, c: Tupu")
        check_syntax_error(self, "lambda a, /, b, /, c, *, d: Tupu")
        check_syntax_error(self, "lambda a, *, b, /, c: Tupu")

    eleza test_posonly_methods(self):
        kundi Example:
            eleza f(self, a, b, /):
                rudisha a, b

        self.assertEqual(Example().f(1, 2), (1, 2))
        self.assertEqual(Example.f(Example(), 1, 2), (1, 2))
        self.assertRaises(TypeError, Example.f, 1, 2)
        expected = r"f\(\) got some positional-only arguments pitaed kama keyword arguments: 'b'"
        with self.assertRaisesRegex(TypeError, expected):
            Example().f(1, b=2)

    eleza test_mangling(self):
        kundi X:
            eleza f(self, *, __a=42):
                rudisha __a
        self.assertEqual(X().f(), 42)

    eleza test_module_function(self):
        with self.assertRaisesRegex(TypeError, r"f\(\) missing 2 required positional arguments: 'a' na 'b'"):
            global_pos_only_f()


    eleza test_closures(self):
        eleza f(x,y):
            eleza g(x2,/,y2):
                rudisha x + y + x2 + y2
            rudisha g

        self.assertEqual(f(1,2)(3,4), 10)
        with self.assertRaisesRegex(TypeError, r"g\(\) missing 1 required positional argument: 'y2'"):
            f(1,2)(3)
        with self.assertRaisesRegex(TypeError, r"g\(\) takes 2 positional arguments but 3 were given"):
            f(1,2)(3,4,5)

        eleza f(x,/,y):
            eleza g(x2,y2):
                rudisha x + y + x2 + y2
            rudisha g

        self.assertEqual(f(1,2)(3,4), 10)

        eleza f(x,/,y):
            eleza g(x2,/,y2):
                rudisha x + y + x2 + y2
            rudisha g

        self.assertEqual(f(1,2)(3,4), 10)
        with self.assertRaisesRegex(TypeError, r"g\(\) missing 1 required positional argument: 'y2'"):
            f(1,2)(3)
        with self.assertRaisesRegex(TypeError, r"g\(\) takes 2 positional arguments but 3 were given"):
            f(1,2)(3,4,5)

    eleza test_same_keyword_as_positional_with_kwargs(self):
        eleza f(something,/,**kwargs):
            rudisha (something, kwargs)

        self.assertEqual(f(42, something=42), (42, {'something': 42}))

        with self.assertRaisesRegex(TypeError, r"f\(\) missing 1 required positional argument: 'something'"):
            f(something=42)

        self.assertEqual(f(42), (42, {}))

    eleza test_mangling(self):
        kundi X:
            eleza f(self, __a=42, /):
                rudisha __a

            eleza f2(self, __a=42, /, __b=43):
                rudisha (__a, __b)

            eleza f3(self, __a=42, /, __b=43, *, __c=44):
                rudisha (__a, __b, __c)

        self.assertEqual(X().f(), 42)
        self.assertEqual(X().f2(), (42, 43))
        self.assertEqual(X().f3(), (42, 43, 44))

    eleza test_too_many_arguments(self):
        # more than 255 positional-only arguments, should compile ok
        funeleza = "eleza f(%s, /):\n  pita\n" % ', '.join('i%d' % i kila i kwenye range(300))
        compile(fundef, "<test>", "single")

    eleza test_serialization(self):
        pickled_posonly = pickle.dumps(global_pos_only_f)
        pickled_optional = pickle.dumps(global_pos_only_and_normal)
        pickled_defaults = pickle.dumps(global_pos_only_defaults)

        unpickled_posonly = pickle.loads(pickled_posonly)
        unpickled_optional = pickle.loads(pickled_optional)
        unpickled_defaults = pickle.loads(pickled_defaults)

        self.assertEqual(unpickled_posonly(1,2), (1,2))
        expected = r"global_pos_only_f\(\) got some positional-only arguments "\
                   r"pitaed kama keyword arguments: 'a, b'"
        with self.assertRaisesRegex(TypeError, expected):
            unpickled_posonly(a=1,b=2)

        self.assertEqual(unpickled_optional(1,2), (1,2))
        expected = r"global_pos_only_and_normal\(\) got some positional-only arguments "\
                   r"pitaed kama keyword arguments: 'a'"
        with self.assertRaisesRegex(TypeError, expected):
            unpickled_optional(a=1,b=2)

        self.assertEqual(unpickled_defaults(), (1,2))
        expected = r"global_pos_only_defaults\(\) got some positional-only arguments "\
                   r"pitaed kama keyword arguments: 'a'"
        with self.assertRaisesRegex(TypeError, expected):
            unpickled_defaults(a=1,b=2)

    eleza test_async(self):

        async eleza f(a=1, /, b=2):
            rudisha a, b

        with self.assertRaisesRegex(TypeError, r"f\(\) got some positional-only arguments pitaed kama keyword arguments: 'a'"):
            f(a=1, b=2)

        eleza _check_call(*args, **kwargs):
            jaribu:
                coro = f(*args, **kwargs)
                coro.send(Tupu)
            tatizo StopIteration kama e:
                result = e.value
            self.assertEqual(result, (1, 2))

        _check_call(1, 2)
        _check_call(1, b=2)
        _check_call(1)
        _check_call()

    eleza test_generator(self):

        eleza f(a=1, /, b=2):
            tuma a, b

        with self.assertRaisesRegex(TypeError, r"f\(\) got some positional-only arguments pitaed kama keyword arguments: 'a'"):
            f(a=1, b=2)

        gen = f(1, 2)
        self.assertEqual(next(gen), (1, 2))
        gen = f(1, b=2)
        self.assertEqual(next(gen), (1, 2))
        gen = f(1)
        self.assertEqual(next(gen), (1, 2))
        gen = f()
        self.assertEqual(next(gen), (1, 2))

    eleza test_super(self):

        sentinel = object()

        kundi A:
            eleza method(self):
                rudisha sentinel

        kundi C(A):
            eleza method(self, /):
                rudisha super().method()

        self.assertEqual(C().method(), sentinel)


ikiwa __name__ == "__main__":
    unittest.main()
