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
             ashiria e
        self.assertRaises(KeyError, _raise, KeyError)
        self.assertRaises(KeyError, _raise, KeyError("key"))
        jaribu:
            self.assertRaises(KeyError, lambda: Tupu)
        except self.failureException as e:
            self.assertIn("KeyError sio raised", str(e))
        isipokua:
            self.fail("assertRaises() didn't fail")
        jaribu:
            self.assertRaises(KeyError, _raise, ValueError)
        except ValueError:
            pass
        isipokua:
            self.fail("assertRaises() didn't let exception pass through")
        ukijumuisha self.assertRaises(KeyError) as cm:
            jaribu:
                 ashiria KeyError
            except Exception as e:
                exc = e
                raise
        self.assertIs(cm.exception, exc)

        ukijumuisha self.assertRaises(KeyError):
             ashiria KeyError("key")
        jaribu:
            ukijumuisha self.assertRaises(KeyError):
                pass
        except self.failureException as e:
            self.assertIn("KeyError sio raised", str(e))
        isipokua:
            self.fail("assertRaises() didn't fail")
        jaribu:
            ukijumuisha self.assertRaises(KeyError):
                 ashiria ValueError
        except ValueError:
            pass
        isipokua:
            self.fail("assertRaises() didn't let exception pass through")

    eleza test_assertRaises_frames_survival(self):
        # Issue #9815: assertRaises should avoid keeping local variables
        # kwenye a traceback alive.
        kundi A:
            pass
        wr = Tupu

        kundi Foo(unittest.TestCase):

            eleza foo(self):
                nonlocal wr
                a = A()
                wr = weakref.ref(a)
                jaribu:
                     ashiria OSError
                except OSError:
                     ashiria ValueError

            eleza test_functional(self):
                self.assertRaises(ValueError, self.foo)

            eleza test_with(self):
                ukijumuisha self.assertRaises(ValueError):
                    self.foo()

        Foo("test_functional").run()
        self.assertIsTupu(wr())
        Foo("test_with").run()
        self.assertIsTupu(wr())

    eleza testAssertNotRegex(self):
        self.assertNotRegex('Ala ma kota', r'r+')
        jaribu:
            self.assertNotRegex('Ala ma kota', r'k.t', 'Message')
        except self.failureException as e:
            self.assertIn('Message', e.args[0])
        isipokua:
            self.fail('assertNotRegex should have failed.')


kundi TestLongMessage(unittest.TestCase):
    """Test that the individual asserts honour longMessage.
    This actually tests all the message behaviour for
    asserts that use longMessage."""

    eleza setUp(self):
        kundi TestableTestUongo(unittest.TestCase):
            longMessage = Uongo
            failureException = self.failureException

            eleza testTest(self):
                pass

        kundi TestableTestKweli(unittest.TestCase):
            longMessage = Kweli
            failureException = self.failureException

            eleza testTest(self):
                pass

        self.testableKweli = TestableTestKweli('testTest')
        self.testableUongo = TestableTestUongo('testTest')

    eleza testDefault(self):
        self.assertKweli(unittest.TestCase.longMessage)

    eleza test_formatMsg(self):
        self.assertEqual(self.testableUongo._formatMessage(Tupu, "foo"), "foo")
        self.assertEqual(self.testableUongo._formatMessage("foo", "bar"), "foo")

        self.assertEqual(self.testableKweli._formatMessage(Tupu, "foo"), "foo")
        self.assertEqual(self.testableKweli._formatMessage("foo", "bar"), "bar : foo")

        # This blows up ikiwa _formatMessage uses string concatenation
        self.testableKweli._formatMessage(object(), 'foo')

    eleza test_formatMessage_unicode_error(self):
        one = ''.join(chr(i) kila i kwenye range(255))
        # this used to cause a UnicodeDecodeError constructing msg
        self.testableKweli._formatMessage(one, '\uFFFD')

    eleza assertMessages(self, methodName, args, errors):
        """
        Check that methodName(*args) raises the correct error messages.
        errors should be a list of 4 regex that match the error when:
          1) longMessage = Uongo na no msg passed;
          2) longMessage = Uongo na msg passed;
          3) longMessage = Kweli na no msg passed;
          4) longMessage = Kweli na msg passed;
        """
        eleza getMethod(i):
            useTestableUongo  = i < 2
            ikiwa useTestableUongo:
                test = self.testableUongo
            isipokua:
                test = self.testableKweli
            rudisha getattr(test, methodName)

        kila i, expected_regex kwenye enumerate(errors):
            testMethod = getMethod(i)
            kwargs = {}
            withMsg = i % 2
            ikiwa withMsg:
                kwargs = {"msg": "oops"}

            ukijumuisha self.assertRaisesRegex(self.failureException,
                                        expected_regex=expected_regex):
                testMethod(*args, **kwargs)

    eleza testAssertKweli(self):
        self.assertMessages('assertKweli', (Uongo,),
                            ["^Uongo ni sio true$", "^oops$", "^Uongo ni sio true$",
                             "^Uongo ni sio true : oops$"])

    eleza testAssertUongo(self):
        self.assertMessages('assertUongo', (Kweli,),
                            ["^Kweli ni sio false$", "^oops$", "^Kweli ni sio false$",
                             "^Kweli ni sio false : oops$"])

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
        # Error messages are multiline so sio testing on full message
        # assertTupleEqual na assertListEqual delegate to this method
        self.assertMessages('assertSequenceEqual', ([], [Tupu]),
                            [r"\+ \[Tupu\]$", "^oops$", r"\+ \[Tupu\]$",
                             r"\+ \[Tupu\] : oops$"])

    eleza testAssertSetEqual(self):
        self.assertMessages('assertSetEqual', (set(), set([Tupu])),
                            ["Tupu$", "^oops$", "Tupu$",
                             "Tupu : oops$"])

    eleza testAssertIn(self):
        self.assertMessages('assertIn', (Tupu, []),
                            [r'^Tupu sio found kwenye \[\]$', "^oops$",
                             r'^Tupu sio found kwenye \[\]$',
                             r'^Tupu sio found kwenye \[\] : oops$'])

    eleza testAssertNotIn(self):
        self.assertMessages('assertNotIn', (Tupu, [Tupu]),
                            [r'^Tupu unexpectedly found kwenye \[Tupu\]$', "^oops$",
                             r'^Tupu unexpectedly found kwenye \[Tupu\]$',
                             r'^Tupu unexpectedly found kwenye \[Tupu\] : oops$'])

    eleza testAssertDictEqual(self):
        self.assertMessages('assertDictEqual', ({}, {'key': 'value'}),
                            [r"\+ \{'key': 'value'\}$", "^oops$",
                             r"\+ \{'key': 'value'\}$",
                             r"\+ \{'key': 'value'\} : oops$"])

    eleza testAssertDictContainsSubset(self):
        ukijumuisha warnings.catch_warnings():
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
                            ["^2 sio less than 1$", "^oops$",
                             "^2 sio less than 1$", "^2 sio less than 1 : oops$"])

    eleza testAssertLessEqual(self):
        self.assertMessages('assertLessEqual', (2, 1),
                            ["^2 sio less than ama equal to 1$", "^oops$",
                             "^2 sio less than ama equal to 1$",
                             "^2 sio less than ama equal to 1 : oops$"])

    eleza testAssertGreater(self):
        self.assertMessages('assertGreater', (1, 2),
                            ["^1 sio greater than 2$", "^oops$",
                             "^1 sio greater than 2$",
                             "^1 sio greater than 2 : oops$"])

    eleza testAssertGreaterEqual(self):
        self.assertMessages('assertGreaterEqual', (1, 2),
                            ["^1 sio greater than ama equal to 2$", "^oops$",
                             "^1 sio greater than ama equal to 2$",
                             "^1 sio greater than ama equal to 2 : oops$"])

    eleza testAssertIsTupu(self):
        self.assertMessages('assertIsTupu', ('not Tupu',),
                            ["^'not Tupu' ni sio Tupu$", "^oops$",
                             "^'not Tupu' ni sio Tupu$",
                             "^'not Tupu' ni sio Tupu : oops$"])

    eleza testAssertIsNotTupu(self):
        self.assertMessages('assertIsNotTupu', (Tupu,),
                            ["^unexpectedly Tupu$", "^oops$",
                             "^unexpectedly Tupu$",
                             "^unexpectedly Tupu : oops$"])

    eleza testAssertIs(self):
        self.assertMessages('assertIs', (Tupu, 'foo'),
                            ["^Tupu ni sio 'foo'$", "^oops$",
                             "^Tupu ni sio 'foo'$",
                             "^Tupu ni sio 'foo' : oops$"])

    eleza testAssertIsNot(self):
        self.assertMessages('assertIsNot', (Tupu, Tupu),
                            ["^unexpectedly identical: Tupu$", "^oops$",
                             "^unexpectedly identical: Tupu$",
                             "^unexpectedly identical: Tupu : oops$"])

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
        Check that the correct error messages are raised wakati executing:
          ukijumuisha method(*args):
              func()
        *errors* should be a list of 4 regex that match the error when:
          1) longMessage = Uongo na no msg passed;
          2) longMessage = Uongo na msg passed;
          3) longMessage = Kweli na no msg passed;
          4) longMessage = Kweli na msg passed;
        """
        p = product((self.testableUongo, self.testableKweli),
                    ({}, {"msg": "oops"}))
        kila (cls, kwargs), err kwenye zip(p, errors):
            method = getattr(cls, methodName)
            ukijumuisha self.assertRaisesRegex(cls.failureException, err):
                ukijumuisha method(*args, **kwargs) as cm:
                    func()

    eleza testAssertRaises(self):
        self.assertMessagesCM('assertRaises', (TypeError,), lambda: Tupu,
                              ['^TypeError sio raised$', '^oops$',
                               '^TypeError sio raised$',
                               '^TypeError sio raised : oops$'])

    eleza testAssertRaisesRegex(self):
        # test error sio raised
        self.assertMessagesCM('assertRaisesRegex', (TypeError, 'unused regex'),
                              lambda: Tupu,
                              ['^TypeError sio raised$', '^oops$',
                               '^TypeError sio raised$',
                               '^TypeError sio raised : oops$'])
        # test error raised but ukijumuisha wrong message
        eleza raise_wrong_message():
             ashiria TypeError('foo')
        self.assertMessagesCM('assertRaisesRegex', (TypeError, 'regex'),
                              raise_wrong_message,
                              ['^"regex" does sio match "foo"$', '^oops$',
                               '^"regex" does sio match "foo"$',
                               '^"regex" does sio match "foo" : oops$'])

    eleza testAssertWarns(self):
        self.assertMessagesCM('assertWarns', (UserWarning,), lambda: Tupu,
                              ['^UserWarning sio triggered$', '^oops$',
                               '^UserWarning sio triggered$',
                               '^UserWarning sio triggered : oops$'])

    eleza testAssertWarnsRegex(self):
        # test error sio raised
        self.assertMessagesCM('assertWarnsRegex', (UserWarning, 'unused regex'),
                              lambda: Tupu,
                              ['^UserWarning sio triggered$', '^oops$',
                               '^UserWarning sio triggered$',
                               '^UserWarning sio triggered : oops$'])
        # test warning raised but ukijumuisha wrong message
        eleza raise_wrong_message():
            warnings.warn('foo')
        self.assertMessagesCM('assertWarnsRegex', (UserWarning, 'regex'),
                              raise_wrong_message,
                              ['^"regex" does sio match "foo"$', '^oops$',
                               '^"regex" does sio match "foo"$',
                               '^"regex" does sio match "foo" : oops$'])


ikiwa __name__ == "__main__":
    unittest.main()
