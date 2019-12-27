# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Tests for the raise statement."""

kutoka test agiza support
agiza sys
agiza types
agiza unittest


eleza get_tb():
    try:
        raise OSError()
    except:
        rudisha sys.exc_info()[2]


kundi Context:
    eleza __enter__(self):
        rudisha self
    eleza __exit__(self, exc_type, exc_value, exc_tb):
        rudisha True


kundi TestRaise(unittest.TestCase):
    eleza test_invalid_reraise(self):
        try:
            raise
        except RuntimeError as e:
            self.assertIn("No active exception", str(e))
        else:
            self.fail("No exception raised")

    eleza test_reraise(self):
        try:
            try:
                raise IndexError()
            except IndexError as e:
                exc1 = e
                raise
        except IndexError as exc2:
            self.assertIs(exc1, exc2)
        else:
            self.fail("No exception raised")

    eleza test_except_reraise(self):
        eleza reraise():
            try:
                raise TypeError("foo")
            except:
                try:
                    raise KeyError("caught")
                except KeyError:
                    pass
                raise
        self.assertRaises(TypeError, reraise)

    eleza test_finally_reraise(self):
        eleza reraise():
            try:
                raise TypeError("foo")
            except:
                try:
                    raise KeyError("caught")
                finally:
                    raise
        self.assertRaises(KeyError, reraise)

    eleza test_nested_reraise(self):
        eleza nested_reraise():
            raise
        eleza reraise():
            try:
                raise TypeError("foo")
            except:
                nested_reraise()
        self.assertRaises(TypeError, reraise)

    eleza test_raise_kutoka_None(self):
        try:
            try:
                raise TypeError("foo")
            except:
                raise ValueError() kutoka None
        except ValueError as e:
            self.assertIsInstance(e.__context__, TypeError)
            self.assertIsNone(e.__cause__)

    eleza test_with_reraise1(self):
        eleza reraise():
            try:
                raise TypeError("foo")
            except:
                with Context():
                    pass
                raise
        self.assertRaises(TypeError, reraise)

    eleza test_with_reraise2(self):
        eleza reraise():
            try:
                raise TypeError("foo")
            except:
                with Context():
                    raise KeyError("caught")
                raise
        self.assertRaises(TypeError, reraise)

    eleza test_yield_reraise(self):
        eleza reraise():
            try:
                raise TypeError("foo")
            except:
                yield 1
                raise
        g = reraise()
        next(g)
        self.assertRaises(TypeError, lambda: next(g))
        self.assertRaises(StopIteration, lambda: next(g))

    eleza test_erroneous_exception(self):
        kundi MyException(Exception):
            eleza __init__(self):
                raise RuntimeError()

        try:
            raise MyException
        except RuntimeError:
            pass
        else:
            self.fail("No exception raised")

    eleza test_new_returns_invalid_instance(self):
        # See issue #11627.
        kundi MyException(Exception):
            eleza __new__(cls, *args):
                rudisha object()

        with self.assertRaises(TypeError):
            raise MyException

    eleza test_assert_with_tuple_arg(self):
        try:
            assert False, (3,)
        except AssertionError as e:
            self.assertEqual(str(e), "(3,)")



kundi TestCause(unittest.TestCase):

    eleza testCauseSyntax(self):
        try:
            try:
                try:
                    raise TypeError
                except Exception:
                    raise ValueError kutoka None
            except ValueError as exc:
                self.assertIsNone(exc.__cause__)
                self.assertTrue(exc.__suppress_context__)
                exc.__suppress_context__ = False
                raise exc
        except ValueError as exc:
            e = exc

        self.assertIsNone(e.__cause__)
        self.assertFalse(e.__suppress_context__)
        self.assertIsInstance(e.__context__, TypeError)

    eleza test_invalid_cause(self):
        try:
            raise IndexError kutoka 5
        except TypeError as e:
            self.assertIn("exception cause", str(e))
        else:
            self.fail("No exception raised")

    eleza test_class_cause(self):
        try:
            raise IndexError kutoka KeyError
        except IndexError as e:
            self.assertIsInstance(e.__cause__, KeyError)
        else:
            self.fail("No exception raised")

    eleza test_instance_cause(self):
        cause = KeyError()
        try:
            raise IndexError kutoka cause
        except IndexError as e:
            self.assertIs(e.__cause__, cause)
        else:
            self.fail("No exception raised")

    eleza test_erroneous_cause(self):
        kundi MyException(Exception):
            eleza __init__(self):
                raise RuntimeError()

        try:
            raise IndexError kutoka MyException
        except RuntimeError:
            pass
        else:
            self.fail("No exception raised")


kundi TestTraceback(unittest.TestCase):

    eleza test_sets_traceback(self):
        try:
            raise IndexError()
        except IndexError as e:
            self.assertIsInstance(e.__traceback__, types.TracebackType)
        else:
            self.fail("No exception raised")

    eleza test_accepts_traceback(self):
        tb = get_tb()
        try:
            raise IndexError().with_traceback(tb)
        except IndexError as e:
            self.assertNotEqual(e.__traceback__, tb)
            self.assertEqual(e.__traceback__.tb_next, tb)
        else:
            self.fail("No exception raised")


kundi TestTracebackType(unittest.TestCase):

    eleza raiser(self):
        raise ValueError

    eleza test_attrs(self):
        try:
            self.raiser()
        except Exception as exc:
            tb = exc.__traceback__

        self.assertIsInstance(tb.tb_next, types.TracebackType)
        self.assertIs(tb.tb_frame, sys._getframe())
        self.assertIsInstance(tb.tb_lasti, int)
        self.assertIsInstance(tb.tb_lineno, int)

        self.assertIs(tb.tb_next.tb_next, None)

        # Invalid assignments
        with self.assertRaises(TypeError):
            del tb.tb_next

        with self.assertRaises(TypeError):
            tb.tb_next = "asdf"

        # Loops
        with self.assertRaises(ValueError):
            tb.tb_next = tb

        with self.assertRaises(ValueError):
            tb.tb_next.tb_next = tb

        # Valid assignments
        tb.tb_next = None
        self.assertIs(tb.tb_next, None)

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

        tb = types.TracebackType(None, frame, 1, 2)
        self.assertEqual(tb.tb_next, None)

        with self.assertRaises(TypeError):
            types.TracebackType("no", frame, 1, 2)

        with self.assertRaises(TypeError):
            types.TracebackType(other_tb, "no", 1, 2)

        with self.assertRaises(TypeError):
            types.TracebackType(other_tb, frame, "no", 2)

        with self.assertRaises(TypeError):
            types.TracebackType(other_tb, frame, 1, "nuh-uh")


kundi TestContext(unittest.TestCase):
    eleza test_instance_context_instance_raise(self):
        context = IndexError()
        try:
            try:
                raise context
            except:
                raise OSError()
        except OSError as e:
            self.assertEqual(e.__context__, context)
        else:
            self.fail("No exception raised")

    eleza test_class_context_instance_raise(self):
        context = IndexError
        try:
            try:
                raise context
            except:
                raise OSError()
        except OSError as e:
            self.assertNotEqual(e.__context__, context)
            self.assertIsInstance(e.__context__, context)
        else:
            self.fail("No exception raised")

    eleza test_class_context_class_raise(self):
        context = IndexError
        try:
            try:
                raise context
            except:
                raise OSError
        except OSError as e:
            self.assertNotEqual(e.__context__, context)
            self.assertIsInstance(e.__context__, context)
        else:
            self.fail("No exception raised")

    eleza test_c_exception_context(self):
        try:
            try:
                1/0
            except:
                raise OSError
        except OSError as e:
            self.assertIsInstance(e.__context__, ZeroDivisionError)
        else:
            self.fail("No exception raised")

    eleza test_c_exception_raise(self):
        try:
            try:
                1/0
            except:
                xyzzy
        except NameError as e:
            self.assertIsInstance(e.__context__, ZeroDivisionError)
        else:
            self.fail("No exception raised")

    eleza test_noraise_finally(self):
        try:
            try:
                pass
            finally:
                raise OSError
        except OSError as e:
            self.assertIsNone(e.__context__)
        else:
            self.fail("No exception raised")

    eleza test_raise_finally(self):
        try:
            try:
                1/0
            finally:
                raise OSError
        except OSError as e:
            self.assertIsInstance(e.__context__, ZeroDivisionError)
        else:
            self.fail("No exception raised")

    eleza test_context_manager(self):
        kundi ContextManager:
            eleza __enter__(self):
                pass
            eleza __exit__(self, t, v, tb):
                xyzzy
        try:
            with ContextManager():
                1/0
        except NameError as e:
            self.assertIsInstance(e.__context__, ZeroDivisionError)
        else:
            self.fail("No exception raised")

    eleza test_cycle_broken(self):
        # Self-cycles (when re-raising a caught exception) are broken
        try:
            try:
                1/0
            except ZeroDivisionError as e:
                raise e
        except ZeroDivisionError as e:
            self.assertIsNone(e.__context__)

    eleza test_reraise_cycle_broken(self):
        # Non-trivial context cycles (through re-raising a previous exception)
        # are broken too.
        try:
            try:
                xyzzy
            except NameError as a:
                try:
                    1/0
                except ZeroDivisionError:
                    raise a
        except NameError as e:
            self.assertIsNone(e.__context__.__context__)

    eleza test_3118(self):
        # deleting the generator caused the __context__ to be cleared
        eleza gen():
            try:
                yield 1
            finally:
                pass

        eleza f():
            g = gen()
            next(g)
            try:
                try:
                    raise ValueError
                except:
                    del g
                    raise KeyError
            except Exception as e:
                self.assertIsInstance(e.__context__, ValueError)

        f()

    eleza test_3611(self):
        # A re-raised exception in a __del__ caused the __context__
        # to be cleared
        kundi C:
            eleza __del__(self):
                try:
                    1/0
                except:
                    raise

        eleza f():
            x = C()
            try:
                try:
                    x.x
                except AttributeError:
                    del x
                    raise TypeError
            except Exception as e:
                self.assertNotEqual(e.__context__, None)
                self.assertIsInstance(e.__context__, AttributeError)

        with support.catch_unraisable_exception() as cm:
            f()

            self.assertEqual(ZeroDivisionError, cm.unraisable.exc_type)


kundi TestRemovedFunctionality(unittest.TestCase):
    eleza test_tuples(self):
        try:
            raise (IndexError, KeyError) # This should be a tuple!
        except TypeError:
            pass
        else:
            self.fail("No exception raised")

    eleza test_strings(self):
        try:
            raise "foo"
        except TypeError:
            pass
        else:
            self.fail("No exception raised")


ikiwa __name__ == "__main__":
    unittest.main()
