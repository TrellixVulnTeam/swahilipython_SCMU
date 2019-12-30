# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Tests kila the ashiria statement."""

kutoka test agiza support
agiza sys
agiza types
agiza unittest


eleza get_tb():
    jaribu:
        ashiria OSError()
    tatizo:
        rudisha sys.exc_info()[2]


kundi Context:
    eleza __enter__(self):
        rudisha self
    eleza __exit__(self, exc_type, exc_value, exc_tb):
        rudisha Kweli


kundi TestRaise(unittest.TestCase):
    eleza test_invalid_reraise(self):
        jaribu:
            raise
        tatizo RuntimeError kama e:
            self.assertIn("No active exception", str(e))
        isipokua:
            self.fail("No exception raised")

    eleza test_reraise(self):
        jaribu:
            jaribu:
                ashiria IndexError()
            tatizo IndexError kama e:
                exc1 = e
                raise
        tatizo IndexError kama exc2:
            self.assertIs(exc1, exc2)
        isipokua:
            self.fail("No exception raised")

    eleza test_except_reraise(self):
        eleza reraise():
            jaribu:
                ashiria TypeError("foo")
            tatizo:
                jaribu:
                    ashiria KeyError("caught")
                tatizo KeyError:
                    pita
                raise
        self.assertRaises(TypeError, reraise)

    eleza test_finally_reraise(self):
        eleza reraise():
            jaribu:
                ashiria TypeError("foo")
            tatizo:
                jaribu:
                    ashiria KeyError("caught")
                mwishowe:
                    raise
        self.assertRaises(KeyError, reraise)

    eleza test_nested_reraise(self):
        eleza nested_reraise():
            raise
        eleza reraise():
            jaribu:
                ashiria TypeError("foo")
            tatizo:
                nested_reraise()
        self.assertRaises(TypeError, reraise)

    eleza test_raise_from_Tupu(self):
        jaribu:
            jaribu:
                ashiria TypeError("foo")
            tatizo:
                ashiria ValueError() kutoka Tupu
        tatizo ValueError kama e:
            self.assertIsInstance(e.__context__, TypeError)
            self.assertIsTupu(e.__cause__)

    eleza test_with_reraise1(self):
        eleza reraise():
            jaribu:
                ashiria TypeError("foo")
            tatizo:
                ukijumuisha Context():
                    pita
                raise
        self.assertRaises(TypeError, reraise)

    eleza test_with_reraise2(self):
        eleza reraise():
            jaribu:
                ashiria TypeError("foo")
            tatizo:
                ukijumuisha Context():
                    ashiria KeyError("caught")
                raise
        self.assertRaises(TypeError, reraise)

    eleza test_tuma_reraise(self):
        eleza reraise():
            jaribu:
                ashiria TypeError("foo")
            tatizo:
                tuma 1
                raise
        g = reraise()
        next(g)
        self.assertRaises(TypeError, lambda: next(g))
        self.assertRaises(StopIteration, lambda: next(g))

    eleza test_erroneous_exception(self):
        kundi MyException(Exception):
            eleza __init__(self):
                ashiria RuntimeError()

        jaribu:
            ashiria MyException
        tatizo RuntimeError:
            pita
        isipokua:
            self.fail("No exception raised")

    eleza test_new_returns_invalid_instance(self):
        # See issue #11627.
        kundi MyException(Exception):
            eleza __new__(cls, *args):
                rudisha object()

        ukijumuisha self.assertRaises(TypeError):
            ashiria MyException

    eleza test_assert_with_tuple_arg(self):
        jaribu:
            assert Uongo, (3,)
        tatizo AssertionError kama e:
            self.assertEqual(str(e), "(3,)")



kundi TestCause(unittest.TestCase):

    eleza testCauseSyntax(self):
        jaribu:
            jaribu:
                jaribu:
                    ashiria TypeError
                tatizo Exception:
                    ashiria ValueError kutoka Tupu
            tatizo ValueError kama exc:
                self.assertIsTupu(exc.__cause__)
                self.assertKweli(exc.__suppress_context__)
                exc.__suppress_context__ = Uongo
                ashiria exc
        tatizo ValueError kama exc:
            e = exc

        self.assertIsTupu(e.__cause__)
        self.assertUongo(e.__suppress_context__)
        self.assertIsInstance(e.__context__, TypeError)

    eleza test_invalid_cause(self):
        jaribu:
            ashiria IndexError kutoka 5
        tatizo TypeError kama e:
            self.assertIn("exception cause", str(e))
        isipokua:
            self.fail("No exception raised")

    eleza test_class_cause(self):
        jaribu:
            ashiria IndexError kutoka KeyError
        tatizo IndexError kama e:
            self.assertIsInstance(e.__cause__, KeyError)
        isipokua:
            self.fail("No exception raised")

    eleza test_instance_cause(self):
        cause = KeyError()
        jaribu:
            ashiria IndexError kutoka cause
        tatizo IndexError kama e:
            self.assertIs(e.__cause__, cause)
        isipokua:
            self.fail("No exception raised")

    eleza test_erroneous_cause(self):
        kundi MyException(Exception):
            eleza __init__(self):
                ashiria RuntimeError()

        jaribu:
            ashiria IndexError kutoka MyException
        tatizo RuntimeError:
            pita
        isipokua:
            self.fail("No exception raised")


kundi TestTraceback(unittest.TestCase):

    eleza test_sets_traceback(self):
        jaribu:
            ashiria IndexError()
        tatizo IndexError kama e:
            self.assertIsInstance(e.__traceback__, types.TracebackType)
        isipokua:
            self.fail("No exception raised")

    eleza test_accepts_traceback(self):
        tb = get_tb()
        jaribu:
            ashiria IndexError().with_traceback(tb)
        tatizo IndexError kama e:
            self.assertNotEqual(e.__traceback__, tb)
            self.assertEqual(e.__traceback__.tb_next, tb)
        isipokua:
            self.fail("No exception raised")


kundi TestTracebackType(unittest.TestCase):

    eleza raiser(self):
        ashiria ValueError

    eleza test_attrs(self):
        jaribu:
            self.raiser()
        tatizo Exception kama exc:
            tb = exc.__traceback__

        self.assertIsInstance(tb.tb_next, types.TracebackType)
        self.assertIs(tb.tb_frame, sys._getframe())
        self.assertIsInstance(tb.tb_lasti, int)
        self.assertIsInstance(tb.tb_lineno, int)

        self.assertIs(tb.tb_next.tb_next, Tupu)

        # Invalid assignments
        ukijumuisha self.assertRaises(TypeError):
            toa tb.tb_next

        ukijumuisha self.assertRaises(TypeError):
            tb.tb_next = "asdf"

        # Loops
        ukijumuisha self.assertRaises(ValueError):
            tb.tb_next = tb

        ukijumuisha self.assertRaises(ValueError):
            tb.tb_next.tb_next = tb

        # Valid assignments
        tb.tb_next = Tupu
        self.assertIs(tb.tb_next, Tupu)

        new_tb = get_tb()
        tb.tb_next = new_tb
        self.assertIs(tb.tb_next, new_tb)

    eleza test_constructor(self):
        other_tb = get_tb()
        frame = sys._getframe()

        tb = types.TracebackType(other_tb, frame, 1, 2)
        self.assertEqual(tb.tb_next, other_tb)
        self.assertEqual(tb.tb_frame, frame)
        self.assertEqual(tb.tb_lasti, 1)
        self.assertEqual(tb.tb_lineno, 2)

        tb = types.TracebackType(Tupu, frame, 1, 2)
        self.assertEqual(tb.tb_next, Tupu)

        ukijumuisha self.assertRaises(TypeError):
            types.TracebackType("no", frame, 1, 2)

        ukijumuisha self.assertRaises(TypeError):
            types.TracebackType(other_tb, "no", 1, 2)

        ukijumuisha self.assertRaises(TypeError):
            types.TracebackType(other_tb, frame, "no", 2)

        ukijumuisha self.assertRaises(TypeError):
            types.TracebackType(other_tb, frame, 1, "nuh-uh")


kundi TestContext(unittest.TestCase):
    eleza test_instance_context_instance_raise(self):
        context = IndexError()
        jaribu:
            jaribu:
                ashiria context
            tatizo:
                ashiria OSError()
        tatizo OSError kama e:
            self.assertEqual(e.__context__, context)
        isipokua:
            self.fail("No exception raised")

    eleza test_class_context_instance_raise(self):
        context = IndexError
        jaribu:
            jaribu:
                ashiria context
            tatizo:
                ashiria OSError()
        tatizo OSError kama e:
            self.assertNotEqual(e.__context__, context)
            self.assertIsInstance(e.__context__, context)
        isipokua:
            self.fail("No exception raised")

    eleza test_class_context_class_raise(self):
        context = IndexError
        jaribu:
            jaribu:
                ashiria context
            tatizo:
                ashiria OSError
        tatizo OSError kama e:
            self.assertNotEqual(e.__context__, context)
            self.assertIsInstance(e.__context__, context)
        isipokua:
            self.fail("No exception raised")

    eleza test_c_exception_context(self):
        jaribu:
            jaribu:
                1/0
            tatizo:
                ashiria OSError
        tatizo OSError kama e:
            self.assertIsInstance(e.__context__, ZeroDivisionError)
        isipokua:
            self.fail("No exception raised")

    eleza test_c_exception_raise(self):
        jaribu:
            jaribu:
                1/0
            tatizo:
                xyzzy
        tatizo NameError kama e:
            self.assertIsInstance(e.__context__, ZeroDivisionError)
        isipokua:
            self.fail("No exception raised")

    eleza test_noraise_finally(self):
        jaribu:
            jaribu:
                pita
            mwishowe:
                ashiria OSError
        tatizo OSError kama e:
            self.assertIsTupu(e.__context__)
        isipokua:
            self.fail("No exception raised")

    eleza test_raise_finally(self):
        jaribu:
            jaribu:
                1/0
            mwishowe:
                ashiria OSError
        tatizo OSError kama e:
            self.assertIsInstance(e.__context__, ZeroDivisionError)
        isipokua:
            self.fail("No exception raised")

    eleza test_context_manager(self):
        kundi ContextManager:
            eleza __enter__(self):
                pita
            eleza __exit__(self, t, v, tb):
                xyzzy
        jaribu:
            ukijumuisha ContextManager():
                1/0
        tatizo NameError kama e:
            self.assertIsInstance(e.__context__, ZeroDivisionError)
        isipokua:
            self.fail("No exception raised")

    eleza test_cycle_broken(self):
        # Self-cycles (when re-raising a caught exception) are broken
        jaribu:
            jaribu:
                1/0
            tatizo ZeroDivisionError kama e:
                ashiria e
        tatizo ZeroDivisionError kama e:
            self.assertIsTupu(e.__context__)

    eleza test_reraise_cycle_broken(self):
        # Non-trivial context cycles (through re-raising a previous exception)
        # are broken too.
        jaribu:
            jaribu:
                xyzzy
            tatizo NameError kama a:
                jaribu:
                    1/0
                tatizo ZeroDivisionError:
                    ashiria a
        tatizo NameError kama e:
            self.assertIsTupu(e.__context__.__context__)

    eleza test_3118(self):
        # deleting the generator caused the __context__ to be cleared
        eleza gen():
            jaribu:
                tuma 1
            mwishowe:
                pita

        eleza f():
            g = gen()
            next(g)
            jaribu:
                jaribu:
                    ashiria ValueError
                tatizo:
                    toa g
                    ashiria KeyError
            tatizo Exception kama e:
                self.assertIsInstance(e.__context__, ValueError)

        f()

    eleza test_3611(self):
        # A re-raised exception kwenye a __del__ caused the __context__
        # to be cleared
        kundi C:
            eleza __del__(self):
                jaribu:
                    1/0
                tatizo:
                    raise

        eleza f():
            x = C()
            jaribu:
                jaribu:
                    x.x
                tatizo AttributeError:
                    toa x
                    ashiria TypeError
            tatizo Exception kama e:
                self.assertNotEqual(e.__context__, Tupu)
                self.assertIsInstance(e.__context__, AttributeError)

        ukijumuisha support.catch_unraisable_exception() kama cm:
            f()

            self.assertEqual(ZeroDivisionError, cm.unraisable.exc_type)


kundi TestRemovedFunctionality(unittest.TestCase):
    eleza test_tuples(self):
        jaribu:
            ashiria (IndexError, KeyError) # This should be a tuple!
        tatizo TypeError:
            pita
        isipokua:
            self.fail("No exception raised")

    eleza test_strings(self):
        jaribu:
            ashiria "foo"
        tatizo TypeError:
            pita
        isipokua:
            self.fail("No exception raised")


ikiwa __name__ == "__main__":
    unittest.main()
