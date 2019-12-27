agiza datetime
agiza warnings
agiza weakref
agiza unittest
kutoka itertools agiza product


kundi Test_Assertions(unittest.TestCase):
    eleza test_AlmostEqual(self):
        self.assertAlmostEqual(1.00000001, 1.0)
        self.assertNotAlmostEqual(1.0000001, 1.0)
        self.assertRaises(self.failureException,
                          self.assertAlmostEqual, 1.0000001, 1.0)
        self.assertRaises(self.failureException,
                          self.assertNotAlmostEqual, 1.00000001, 1.0)

        self.assertAlmostEqual(1.1, 1.0, places=0)
        self.assertRaises(self.failureException,
                          self.assertAlmostEqual, 1.1, 1.0, places=1)

        self.assertAlmostEqual(0, .1+.1j, places=0)
        self.assertNotAlmostEqual(0, .1+.1j, places=1)
        self.assertRaises(self.failureException,
                          self.assertAlmostEqual, 0, .1+.1j, places=1)
        self.assertRaises(self.failureException,
                          self.assertNotAlmostEqual, 0, .1+.1j, places=0)

        self.assertAlmostEqual(float('inf'), float('inf'))
        self.assertRaises(self.failureException, self.assertNotAlmostEqual,
                          float('inf'), float('inf'))

    eleza test_AmostEqualWithDelta(self):
        self.assertAlmostEqual(1.1, 1.0, delta=0.5)
        self.assertAlmostEqual(1.0, 1.1, delta=0.5)
        self.assertNotAlmostEqual(1.1, 1.0, delta=0.05)
        self.assertNotAlmostEqual(1.0, 1.1, delta=0.05)

        self.assertAlmostEqual(1.0, 1.0, delta=0.5)
        self.assertRaises(self.failureException, self.assertNotAlmostEqual,
                          1.0, 1.0, delta=0.5)

        self.assertRaises(self.failureException, self.assertAlmostEqual,
                          1.1, 1.0, delta=0.05)
        self.assertRaises(self.failureException, self.assertNotAlmostEqual,
                          1.1, 1.0, delta=0.5)

        self.assertRaises(TypeError, self.assertAlmostEqual,
                          1.1, 1.0, places=2, delta=2)
        self.assertRaises(TypeError, self.assertNotAlmostEqual,
                          1.1, 1.0, places=2, delta=2)

        first = datetime.datetime.now()
        second = first + datetime.timedelta(seconds=10)
        self.assertAlmostEqual(first, second,
                               delta=datetime.timedelta(seconds=20))
        self.assertNotAlmostEqual(first, second,
                                  delta=datetime.timedelta(seconds=5))

    eleza test_assertRaises(self):
        eleza _raise(e):
            raise e
        self.assertRaises(KeyError, _raise, KeyError)
        self.assertRaises(KeyError, _raise, KeyError("key"))
        try:
            self.assertRaises(KeyError, lambda: None)
        except self.failureException as e:
            self.assertIn("KeyError not raised", str(e))
        else:
            self.fail("assertRaises() didn't fail")
        try:
            self.assertRaises(KeyError, _raise, ValueError)
        except ValueError:
            pass
        else:
            self.fail("assertRaises() didn't let exception pass through")
        with self.assertRaises(KeyError) as cm:
            try:
                raise KeyError
            except Exception as e:
                exc = e
                raise
        self.assertIs(cm.exception, exc)

        with self.assertRaises(KeyError):
            raise KeyError("key")
        try:
            with self.assertRaises(KeyError):
                pass
        except self.failureException as e:
            self.assertIn("KeyError not raised", str(e))
        else:
            self.fail("assertRaises() didn't fail")
        try:
            with self.assertRaises(KeyError):
                raise ValueError
        except ValueError:
            pass
        else:
            self.fail("assertRaises() didn't let exception pass through")

    eleza test_assertRaises_frames_survival(self):
        # Issue #9815: assertRaises should avoid keeping local variables
        # in a traceback alive.
        kundi A:
            pass
        wr = None

        kundi Foo(unittest.TestCase):

            eleza foo(self):
                nonlocal wr
                a = A()
                wr = weakref.ref(a)
                try:
                    raise OSError
                except OSError:
                    raise ValueError

            eleza test_functional(self):
                self.assertRaises(ValueError, self.foo)

            eleza test_with(self):
                with self.assertRaises(ValueError):
                    self.foo()

        Foo("test_functional").run()
        self.assertIsNone(wr())
        Foo("test_with").run()
        self.assertIsNone(wr())

    eleza testAssertNotRegex(self):
        self.assertNotRegex('Ala ma kota', r'r+')
        try:
            self.assertNotRegex('Ala ma kota', r'k.t', 'Message')
        except self.failureException as e:
            self.assertIn('Message', e.args[0])
        else:
            self.fail('assertNotRegex should have failed.')


kundi TestLongMessage(unittest.TestCase):
    """Test that the individual asserts honour longMessage.
    This actually tests all the message behaviour for
    asserts that use longMessage."""

    eleza setUp(self):
        kundi TestableTestFalse(unittest.TestCase):
            longMessage = False
            failureException = self.failureException

            eleza testTest(self):
                pass

        kundi TestableTestTrue(unittest.TestCase):
            longMessage = True
            failureException = self.failureException

            eleza testTest(self):
                pass

        self.testableTrue = TestableTestTrue('testTest')
        self.testableFalse = TestableTestFalse('testTest')

    eleza testDefault(self):
        self.assertTrue(unittest.TestCase.longMessage)

    eleza test_formatMsg(self):
        self.assertEqual(self.testableFalse._formatMessage(None, "foo"), "foo")
        self.assertEqual(self.testableFalse._formatMessage("foo", "bar"), "foo")

        self.assertEqual(self.testableTrue._formatMessage(None, "foo"), "foo")
        self.assertEqual(self.testableTrue._formatMessage("foo", "bar"), "bar : foo")

        # This blows up ikiwa _formatMessage uses string concatenation
        self.testableTrue._formatMessage(object(), 'foo')

    eleza test_formatMessage_unicode_error(self):
        one = ''.join(chr(i) for i in range(255))
        # this used to cause a UnicodeDecodeError constructing msg
        self.testableTrue._formatMessage(one, '\uFFFD')

    eleza assertMessages(self, methodName, args, errors):
        """
        Check that methodName(*args) raises the correct error messages.
        errors should be a list of 4 regex that match the error when:
          1) longMessage = False and no msg passed;
          2) longMessage = False and msg passed;
          3) longMessage = True and no msg passed;
          4) longMessage = True and msg passed;
        """
        eleza getMethod(i):
            useTestableFalse  = i < 2
            ikiwa useTestableFalse:
                test = self.testableFalse
            else:
                test = self.testableTrue
            rudisha getattr(test, methodName)

        for i, expected_regex in enumerate(errors):
            testMethod = getMethod(i)
            kwargs = {}
            withMsg = i % 2
            ikiwa withMsg:
                kwargs = {"msg": "oops"}

            with self.assertRaisesRegex(self.failureException,
                                        expected_regex=expected_regex):
                testMethod(*args, **kwargs)

    eleza testAssertTrue(self):
        self.assertMessages('assertTrue', (False,),
                            ["^False is not true$", "^oops$", "^False is not true$",
                             "^False is not true : oops$"])

    eleza testAssertFalse(self):
        self.assertMessages('assertFalse', (True,),
                            ["^True is not false$", "^oops$", "^True is not false$",
                             "^True is not false : oops$"])

    eleza testNotEqual(self):
        self.assertMessages('assertNotEqual', (1, 1),
                            ["^1 == 1$", "^oops$", "^1 == 1$",
                             "^1 == 1 : oops$"])

    eleza testAlmostEqual(self):
        self.assertMessages(
            'assertAlmostEqual', (1, 2),
            [r"^1 != 2 within 7 places \(1 difference\)$", "^oops$",
             r"^1 != 2 within 7 places \(1 difference\)$",
             r"^1 != 2 within 7 places \(1 difference\) : oops$"])

    eleza testNotAlmostEqual(self):
        self.assertMessages('assertNotAlmostEqual', (1, 1),
                            ["^1 == 1 within 7 places$", "^oops$",
                             "^1 == 1 within 7 places$", "^1 == 1 within 7 places : oops$"])

    eleza test_baseAssertEqual(self):
        self.assertMessages('_baseAssertEqual', (1, 2),
                            ["^1 != 2$", "^oops$", "^1 != 2$", "^1 != 2 : oops$"])

    eleza testAssertSequenceEqual(self):
        # Error messages are multiline so not testing on full message
        # assertTupleEqual and assertListEqual delegate to this method
        self.assertMessages('assertSequenceEqual', ([], [None]),
                            [r"\+ \[None\]$", "^oops$", r"\+ \[None\]$",
                             r"\+ \[None\] : oops$"])

    eleza testAssertSetEqual(self):
        self.assertMessages('assertSetEqual', (set(), set([None])),
                            ["None$", "^oops$", "None$",
                             "None : oops$"])

    eleza testAssertIn(self):
        self.assertMessages('assertIn', (None, []),
                            [r'^None not found in \[\]$', "^oops$",
                             r'^None not found in \[\]$',
                             r'^None not found in \[\] : oops$'])

    eleza testAssertNotIn(self):
        self.assertMessages('assertNotIn', (None, [None]),
                            [r'^None unexpectedly found in \[None\]$', "^oops$",
                             r'^None unexpectedly found in \[None\]$',
                             r'^None unexpectedly found in \[None\] : oops$'])

    eleza testAssertDictEqual(self):
        self.assertMessages('assertDictEqual', ({}, {'key': 'value'}),
                            [r"\+ \{'key': 'value'\}$", "^oops$",
                             r"\+ \{'key': 'value'\}$",
                             r"\+ \{'key': 'value'\} : oops$"])

    eleza testAssertDictContainsSubset(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)

            self.assertMessages('assertDictContainsSubset', ({'key': 'value'}, {}),
                                ["^Missing: 'key'$", "^oops$",
                                 "^Missing: 'key'$",
                                 "^Missing: 'key' : oops$"])

    eleza testAssertMultiLineEqual(self):
        self.assertMessages('assertMultiLineEqual', ("", "foo"),
                            [r"\+ foo$", "^oops$",
                             r"\+ foo$",
                             r"\+ foo : oops$"])

    eleza testAssertLess(self):
        self.assertMessages('assertLess', (2, 1),
                            ["^2 not less than 1$", "^oops$",
                             "^2 not less than 1$", "^2 not less than 1 : oops$"])

    eleza testAssertLessEqual(self):
        self.assertMessages('assertLessEqual', (2, 1),
                            ["^2 not less than or equal to 1$", "^oops$",
                             "^2 not less than or equal to 1$",
                             "^2 not less than or equal to 1 : oops$"])

    eleza testAssertGreater(self):
        self.assertMessages('assertGreater', (1, 2),
                            ["^1 not greater than 2$", "^oops$",
                             "^1 not greater than 2$",
                             "^1 not greater than 2 : oops$"])

    eleza testAssertGreaterEqual(self):
        self.assertMessages('assertGreaterEqual', (1, 2),
                            ["^1 not greater than or equal to 2$", "^oops$",
                             "^1 not greater than or equal to 2$",
                             "^1 not greater than or equal to 2 : oops$"])

    eleza testAssertIsNone(self):
        self.assertMessages('assertIsNone', ('not None',),
                            ["^'not None' is not None$", "^oops$",
                             "^'not None' is not None$",
                             "^'not None' is not None : oops$"])

    eleza testAssertIsNotNone(self):
        self.assertMessages('assertIsNotNone', (None,),
                            ["^unexpectedly None$", "^oops$",
                             "^unexpectedly None$",
                             "^unexpectedly None : oops$"])

    eleza testAssertIs(self):
        self.assertMessages('assertIs', (None, 'foo'),
                            ["^None is not 'foo'$", "^oops$",
                             "^None is not 'foo'$",
                             "^None is not 'foo' : oops$"])

    eleza testAssertIsNot(self):
        self.assertMessages('assertIsNot', (None, None),
                            ["^unexpectedly identical: None$", "^oops$",
                             "^unexpectedly identical: None$",
                             "^unexpectedly identical: None : oops$"])

    eleza testAssertRegex(self):
        self.assertMessages('assertRegex', ('foo', 'bar'),
                            ["^Regex didn't match:",
                             "^oops$",
                             "^Regex didn't match:",
                             "^Regex didn't match: (.*) : oops$"])

    eleza testAssertNotRegex(self):
        self.assertMessages('assertNotRegex', ('foo', 'foo'),
                            ["^Regex matched:",
                             "^oops$",
                             "^Regex matched:",
                             "^Regex matched: (.*) : oops$"])


    eleza assertMessagesCM(self, methodName, args, func, errors):
        """
        Check that the correct error messages are raised while executing:
          with method(*args):
              func()
        *errors* should be a list of 4 regex that match the error when:
          1) longMessage = False and no msg passed;
          2) longMessage = False and msg passed;
          3) longMessage = True and no msg passed;
          4) longMessage = True and msg passed;
        """
        p = product((self.testableFalse, self.testableTrue),
                    ({}, {"msg": "oops"}))
        for (cls, kwargs), err in zip(p, errors):
            method = getattr(cls, methodName)
            with self.assertRaisesRegex(cls.failureException, err):
                with method(*args, **kwargs) as cm:
                    func()

    eleza testAssertRaises(self):
        self.assertMessagesCM('assertRaises', (TypeError,), lambda: None,
                              ['^TypeError not raised$', '^oops$',
                               '^TypeError not raised$',
                               '^TypeError not raised : oops$'])

    eleza testAssertRaisesRegex(self):
        # test error not raised
        self.assertMessagesCM('assertRaisesRegex', (TypeError, 'unused regex'),
                              lambda: None,
                              ['^TypeError not raised$', '^oops$',
                               '^TypeError not raised$',
                               '^TypeError not raised : oops$'])
        # test error raised but with wrong message
        eleza raise_wrong_message():
            raise TypeError('foo')
        self.assertMessagesCM('assertRaisesRegex', (TypeError, 'regex'),
                              raise_wrong_message,
                              ['^"regex" does not match "foo"$', '^oops$',
                               '^"regex" does not match "foo"$',
                               '^"regex" does not match "foo" : oops$'])

    eleza testAssertWarns(self):
        self.assertMessagesCM('assertWarns', (UserWarning,), lambda: None,
                              ['^UserWarning not triggered$', '^oops$',
                               '^UserWarning not triggered$',
                               '^UserWarning not triggered : oops$'])

    eleza testAssertWarnsRegex(self):
        # test error not raised
        self.assertMessagesCM('assertWarnsRegex', (UserWarning, 'unused regex'),
                              lambda: None,
                              ['^UserWarning not triggered$', '^oops$',
                               '^UserWarning not triggered$',
                               '^UserWarning not triggered : oops$'])
        # test warning raised but with wrong message
        eleza raise_wrong_message():
            warnings.warn('foo')
        self.assertMessagesCM('assertWarnsRegex', (UserWarning, 'regex'),
                              raise_wrong_message,
                              ['^"regex" does not match "foo"$', '^oops$',
                               '^"regex" does not match "foo"$',
                               '^"regex" does not match "foo" : oops$'])


ikiwa __name__ == "__main__":
    unittest.main()
