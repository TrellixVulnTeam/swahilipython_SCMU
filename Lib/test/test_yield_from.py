# -*- coding: utf-8 -*-

"""
Test suite for PEP 380 implementation

adapted kutoka original tests written by Greg Ewing
see <http://www.cosc.canterbury.ac.nz/greg.ewing/python/yield-kutoka/YieldFrom-Python3.1.2-rev5.zip>
"""

agiza unittest
agiza inspect

kutoka test.support agiza captured_stderr, disable_gc, gc_collect
kutoka test agiza support

kundi TestPEP380Operation(unittest.TestCase):
    """
    Test semantics.
    """

    eleza test_delegation_of_initial_next_to_subgenerator(self):
        """
        Test delegation of initial next() call to subgenerator
        """
        trace = []
        eleza g1():
            trace.append("Starting g1")
            yield kutoka g2()
            trace.append("Finishing g1")
        eleza g2():
            trace.append("Starting g2")
            yield 42
            trace.append("Finishing g2")
        for x in g1():
            trace.append("Yielded %s" % (x,))
        self.assertEqual(trace,[
            "Starting g1",
            "Starting g2",
            "Yielded 42",
            "Finishing g2",
            "Finishing g1",
        ])

    eleza test_raising_exception_in_initial_next_call(self):
        """
        Test raising exception in initial next() call
        """
        trace = []
        eleza g1():
            try:
                trace.append("Starting g1")
                yield kutoka g2()
            finally:
                trace.append("Finishing g1")
        eleza g2():
            try:
                trace.append("Starting g2")
                raise ValueError("spanish inquisition occurred")
            finally:
                trace.append("Finishing g2")
        try:
            for x in g1():
                trace.append("Yielded %s" % (x,))
        except ValueError as e:
            self.assertEqual(e.args[0], "spanish inquisition occurred")
        else:
            self.fail("subgenerator failed to raise ValueError")
        self.assertEqual(trace,[
            "Starting g1",
            "Starting g2",
            "Finishing g2",
            "Finishing g1",
        ])

    eleza test_delegation_of_next_call_to_subgenerator(self):
        """
        Test delegation of next() call to subgenerator
        """
        trace = []
        eleza g1():
            trace.append("Starting g1")
            yield "g1 ham"
            yield kutoka g2()
            yield "g1 eggs"
            trace.append("Finishing g1")
        eleza g2():
            trace.append("Starting g2")
            yield "g2 spam"
            yield "g2 more spam"
            trace.append("Finishing g2")
        for x in g1():
            trace.append("Yielded %s" % (x,))
        self.assertEqual(trace,[
            "Starting g1",
            "Yielded g1 ham",
            "Starting g2",
            "Yielded g2 spam",
            "Yielded g2 more spam",
            "Finishing g2",
            "Yielded g1 eggs",
            "Finishing g1",
        ])

    eleza test_raising_exception_in_delegated_next_call(self):
        """
        Test raising exception in delegated next() call
        """
        trace = []
        eleza g1():
            try:
                trace.append("Starting g1")
                yield "g1 ham"
                yield kutoka g2()
                yield "g1 eggs"
            finally:
                trace.append("Finishing g1")
        eleza g2():
            try:
                trace.append("Starting g2")
                yield "g2 spam"
                raise ValueError("hovercraft is full of eels")
                yield "g2 more spam"
            finally:
                trace.append("Finishing g2")
        try:
            for x in g1():
                trace.append("Yielded %s" % (x,))
        except ValueError as e:
            self.assertEqual(e.args[0], "hovercraft is full of eels")
        else:
            self.fail("subgenerator failed to raise ValueError")
        self.assertEqual(trace,[
            "Starting g1",
            "Yielded g1 ham",
            "Starting g2",
            "Yielded g2 spam",
            "Finishing g2",
            "Finishing g1",
        ])

    eleza test_delegation_of_send(self):
        """
        Test delegation of send()
        """
        trace = []
        eleza g1():
            trace.append("Starting g1")
            x = yield "g1 ham"
            trace.append("g1 received %s" % (x,))
            yield kutoka g2()
            x = yield "g1 eggs"
            trace.append("g1 received %s" % (x,))
            trace.append("Finishing g1")
        eleza g2():
            trace.append("Starting g2")
            x = yield "g2 spam"
            trace.append("g2 received %s" % (x,))
            x = yield "g2 more spam"
            trace.append("g2 received %s" % (x,))
            trace.append("Finishing g2")
        g = g1()
        y = next(g)
        x = 1
        try:
            while 1:
                y = g.send(x)
                trace.append("Yielded %s" % (y,))
                x += 1
        except StopIteration:
            pass
        self.assertEqual(trace,[
            "Starting g1",
            "g1 received 1",
            "Starting g2",
            "Yielded g2 spam",
            "g2 received 2",
            "Yielded g2 more spam",
            "g2 received 3",
            "Finishing g2",
            "Yielded g1 eggs",
            "g1 received 4",
            "Finishing g1",
        ])

    eleza test_handling_exception_while_delegating_send(self):
        """
        Test handling exception while delegating 'send'
        """
        trace = []
        eleza g1():
            trace.append("Starting g1")
            x = yield "g1 ham"
            trace.append("g1 received %s" % (x,))
            yield kutoka g2()
            x = yield "g1 eggs"
            trace.append("g1 received %s" % (x,))
            trace.append("Finishing g1")
        eleza g2():
            trace.append("Starting g2")
            x = yield "g2 spam"
            trace.append("g2 received %s" % (x,))
            raise ValueError("hovercraft is full of eels")
            x = yield "g2 more spam"
            trace.append("g2 received %s" % (x,))
            trace.append("Finishing g2")
        eleza run():
            g = g1()
            y = next(g)
            x = 1
            try:
                while 1:
                    y = g.send(x)
                    trace.append("Yielded %s" % (y,))
                    x += 1
            except StopIteration:
                trace.append("StopIteration")
        self.assertRaises(ValueError,run)
        self.assertEqual(trace,[
            "Starting g1",
            "g1 received 1",
            "Starting g2",
            "Yielded g2 spam",
            "g2 received 2",
        ])

    eleza test_delegating_close(self):
        """
        Test delegating 'close'
        """
        trace = []
        eleza g1():
            try:
                trace.append("Starting g1")
                yield "g1 ham"
                yield kutoka g2()
                yield "g1 eggs"
            finally:
                trace.append("Finishing g1")
        eleza g2():
            try:
                trace.append("Starting g2")
                yield "g2 spam"
                yield "g2 more spam"
            finally:
                trace.append("Finishing g2")
        g = g1()
        for i in range(2):
            x = next(g)
            trace.append("Yielded %s" % (x,))
        g.close()
        self.assertEqual(trace,[
            "Starting g1",
            "Yielded g1 ham",
            "Starting g2",
            "Yielded g2 spam",
            "Finishing g2",
            "Finishing g1"
        ])

    eleza test_handing_exception_while_delegating_close(self):
        """
        Test handling exception while delegating 'close'
        """
        trace = []
        eleza g1():
            try:
                trace.append("Starting g1")
                yield "g1 ham"
                yield kutoka g2()
                yield "g1 eggs"
            finally:
                trace.append("Finishing g1")
        eleza g2():
            try:
                trace.append("Starting g2")
                yield "g2 spam"
                yield "g2 more spam"
            finally:
                trace.append("Finishing g2")
                raise ValueError("nybbles have exploded with delight")
        try:
            g = g1()
            for i in range(2):
                x = next(g)
                trace.append("Yielded %s" % (x,))
            g.close()
        except ValueError as e:
            self.assertEqual(e.args[0], "nybbles have exploded with delight")
            self.assertIsInstance(e.__context__, GeneratorExit)
        else:
            self.fail("subgenerator failed to raise ValueError")
        self.assertEqual(trace,[
            "Starting g1",
            "Yielded g1 ham",
            "Starting g2",
            "Yielded g2 spam",
            "Finishing g2",
            "Finishing g1",
        ])

    eleza test_delegating_throw(self):
        """
        Test delegating 'throw'
        """
        trace = []
        eleza g1():
            try:
                trace.append("Starting g1")
                yield "g1 ham"
                yield kutoka g2()
                yield "g1 eggs"
            finally:
                trace.append("Finishing g1")
        eleza g2():
            try:
                trace.append("Starting g2")
                yield "g2 spam"
                yield "g2 more spam"
            finally:
                trace.append("Finishing g2")
        try:
            g = g1()
            for i in range(2):
                x = next(g)
                trace.append("Yielded %s" % (x,))
            e = ValueError("tomato ejected")
            g.throw(e)
        except ValueError as e:
            self.assertEqual(e.args[0], "tomato ejected")
        else:
            self.fail("subgenerator failed to raise ValueError")
        self.assertEqual(trace,[
            "Starting g1",
            "Yielded g1 ham",
            "Starting g2",
            "Yielded g2 spam",
            "Finishing g2",
            "Finishing g1",
        ])

    eleza test_value_attribute_of_StopIteration_exception(self):
        """
        Test 'value' attribute of StopIteration exception
        """
        trace = []
        eleza pex(e):
            trace.append("%s: %s" % (e.__class__.__name__, e))
            trace.append("value = %s" % (e.value,))
        e = StopIteration()
        pex(e)
        e = StopIteration("spam")
        pex(e)
        e.value = "eggs"
        pex(e)
        self.assertEqual(trace,[
            "StopIteration: ",
            "value = None",
            "StopIteration: spam",
            "value = spam",
            "StopIteration: spam",
            "value = eggs",
        ])


    eleza test_exception_value_crash(self):
        # There used to be a refcount error when the rudisha value
        # stored in the StopIteration has a refcount of 1.
        eleza g1():
            yield kutoka g2()
        eleza g2():
            yield "g2"
            rudisha [42]
        self.assertEqual(list(g1()), ["g2"])


    eleza test_generator_return_value(self):
        """
        Test generator rudisha value
        """
        trace = []
        eleza g1():
            trace.append("Starting g1")
            yield "g1 ham"
            ret = yield kutoka g2()
            trace.append("g2 returned %r" % (ret,))
            for v in 1, (2,), StopIteration(3):
                ret = yield kutoka g2(v)
                trace.append("g2 returned %r" % (ret,))
            yield "g1 eggs"
            trace.append("Finishing g1")
        eleza g2(v = None):
            trace.append("Starting g2")
            yield "g2 spam"
            yield "g2 more spam"
            trace.append("Finishing g2")
            ikiwa v:
                rudisha v
        for x in g1():
            trace.append("Yielded %s" % (x,))
        self.assertEqual(trace,[
            "Starting g1",
            "Yielded g1 ham",
            "Starting g2",
            "Yielded g2 spam",
            "Yielded g2 more spam",
            "Finishing g2",
            "g2 returned None",
            "Starting g2",
            "Yielded g2 spam",
            "Yielded g2 more spam",
            "Finishing g2",
            "g2 returned 1",
            "Starting g2",
            "Yielded g2 spam",
            "Yielded g2 more spam",
            "Finishing g2",
            "g2 returned (2,)",
            "Starting g2",
            "Yielded g2 spam",
            "Yielded g2 more spam",
            "Finishing g2",
            "g2 returned StopIteration(3)",
            "Yielded g1 eggs",
            "Finishing g1",
        ])

    eleza test_delegation_of_next_to_non_generator(self):
        """
        Test delegation of next() to non-generator
        """
        trace = []
        eleza g():
            yield kutoka range(3)
        for x in g():
            trace.append("Yielded %s" % (x,))
        self.assertEqual(trace,[
            "Yielded 0",
            "Yielded 1",
            "Yielded 2",
        ])


    eleza test_conversion_of_sendNone_to_next(self):
        """
        Test conversion of send(None) to next()
        """
        trace = []
        eleza g():
            yield kutoka range(3)
        gi = g()
        for x in range(3):
            y = gi.send(None)
            trace.append("Yielded: %s" % (y,))
        self.assertEqual(trace,[
            "Yielded: 0",
            "Yielded: 1",
            "Yielded: 2",
        ])

    eleza test_delegation_of_close_to_non_generator(self):
        """
        Test delegation of close() to non-generator
        """
        trace = []
        eleza g():
            try:
                trace.append("starting g")
                yield kutoka range(3)
                trace.append("g should not be here")
            finally:
                trace.append("finishing g")
        gi = g()
        next(gi)
        with captured_stderr() as output:
            gi.close()
        self.assertEqual(output.getvalue(), '')
        self.assertEqual(trace,[
            "starting g",
            "finishing g",
        ])

    eleza test_delegating_throw_to_non_generator(self):
        """
        Test delegating 'throw' to non-generator
        """
        trace = []
        eleza g():
            try:
                trace.append("Starting g")
                yield kutoka range(10)
            finally:
                trace.append("Finishing g")
        try:
            gi = g()
            for i in range(5):
                x = next(gi)
                trace.append("Yielded %s" % (x,))
            e = ValueError("tomato ejected")
            gi.throw(e)
        except ValueError as e:
            self.assertEqual(e.args[0],"tomato ejected")
        else:
            self.fail("subgenerator failed to raise ValueError")
        self.assertEqual(trace,[
            "Starting g",
            "Yielded 0",
            "Yielded 1",
            "Yielded 2",
            "Yielded 3",
            "Yielded 4",
            "Finishing g",
        ])

    eleza test_attempting_to_send_to_non_generator(self):
        """
        Test attempting to send to non-generator
        """
        trace = []
        eleza g():
            try:
                trace.append("starting g")
                yield kutoka range(3)
                trace.append("g should not be here")
            finally:
                trace.append("finishing g")
        try:
            gi = g()
            next(gi)
            for x in range(3):
                y = gi.send(42)
                trace.append("Should not have yielded: %s" % (y,))
        except AttributeError as e:
            self.assertIn("send", e.args[0])
        else:
            self.fail("was able to send into non-generator")
        self.assertEqual(trace,[
            "starting g",
            "finishing g",
        ])

    eleza test_broken_getattr_handling(self):
        """
        Test subiterator with a broken getattr implementation
        """
        kundi Broken:
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                rudisha 1
            eleza __getattr__(self, attr):
                1/0

        eleza g():
            yield kutoka Broken()

        with self.assertRaises(ZeroDivisionError):
            gi = g()
            self.assertEqual(next(gi), 1)
            gi.send(1)

        with self.assertRaises(ZeroDivisionError):
            gi = g()
            self.assertEqual(next(gi), 1)
            gi.throw(AttributeError)

        with support.catch_unraisable_exception() as cm:
            gi = g()
            self.assertEqual(next(gi), 1)
            gi.close()

            self.assertEqual(ZeroDivisionError, cm.unraisable.exc_type)

    eleza test_exception_in_initial_next_call(self):
        """
        Test exception in initial next() call
        """
        trace = []
        eleza g1():
            trace.append("g1 about to yield kutoka g2")
            yield kutoka g2()
            trace.append("g1 should not be here")
        eleza g2():
            yield 1/0
        eleza run():
            gi = g1()
            next(gi)
        self.assertRaises(ZeroDivisionError,run)
        self.assertEqual(trace,[
            "g1 about to yield kutoka g2"
        ])

    eleza test_attempted_yield_kutoka_loop(self):
        """
        Test attempted yield-kutoka loop
        """
        trace = []
        eleza g1():
            trace.append("g1: starting")
            yield "y1"
            trace.append("g1: about to yield kutoka g2")
            yield kutoka g2()
            trace.append("g1 should not be here")

        eleza g2():
            trace.append("g2: starting")
            yield "y2"
            trace.append("g2: about to yield kutoka g1")
            yield kutoka gi
            trace.append("g2 should not be here")
        try:
            gi = g1()
            for y in gi:
                trace.append("Yielded: %s" % (y,))
        except ValueError as e:
            self.assertEqual(e.args[0],"generator already executing")
        else:
            self.fail("subgenerator didn't raise ValueError")
        self.assertEqual(trace,[
            "g1: starting",
            "Yielded: y1",
            "g1: about to yield kutoka g2",
            "g2: starting",
            "Yielded: y2",
            "g2: about to yield kutoka g1",
        ])

    eleza test_returning_value_kutoka_delegated_throw(self):
        """
        Test returning value kutoka delegated 'throw'
        """
        trace = []
        eleza g1():
            try:
                trace.append("Starting g1")
                yield "g1 ham"
                yield kutoka g2()
                yield "g1 eggs"
            finally:
                trace.append("Finishing g1")
        eleza g2():
            try:
                trace.append("Starting g2")
                yield "g2 spam"
                yield "g2 more spam"
            except LunchError:
                trace.append("Caught LunchError in g2")
                yield "g2 lunch saved"
                yield "g2 yet more spam"
        kundi LunchError(Exception):
            pass
        g = g1()
        for i in range(2):
            x = next(g)
            trace.append("Yielded %s" % (x,))
        e = LunchError("tomato ejected")
        g.throw(e)
        for x in g:
            trace.append("Yielded %s" % (x,))
        self.assertEqual(trace,[
            "Starting g1",
            "Yielded g1 ham",
            "Starting g2",
            "Yielded g2 spam",
            "Caught LunchError in g2",
            "Yielded g2 yet more spam",
            "Yielded g1 eggs",
            "Finishing g1",
        ])

    eleza test_next_and_return_with_value(self):
        """
        Test next and rudisha with value
        """
        trace = []
        eleza f(r):
            gi = g(r)
            next(gi)
            try:
                trace.append("f resuming g")
                next(gi)
                trace.append("f SHOULD NOT BE HERE")
            except StopIteration as e:
                trace.append("f caught %r" % (e,))
        eleza g(r):
            trace.append("g starting")
            yield
            trace.append("g returning %r" % (r,))
            rudisha r
        f(None)
        f(1)
        f((2,))
        f(StopIteration(3))
        self.assertEqual(trace,[
            "g starting",
            "f resuming g",
            "g returning None",
            "f caught StopIteration()",
            "g starting",
            "f resuming g",
            "g returning 1",
            "f caught StopIteration(1)",
            "g starting",
            "f resuming g",
            "g returning (2,)",
            "f caught StopIteration((2,))",
            "g starting",
            "f resuming g",
            "g returning StopIteration(3)",
            "f caught StopIteration(StopIteration(3))",
        ])

    eleza test_send_and_return_with_value(self):
        """
        Test send and rudisha with value
        """
        trace = []
        eleza f(r):
            gi = g(r)
            next(gi)
            try:
                trace.append("f sending spam to g")
                gi.send("spam")
                trace.append("f SHOULD NOT BE HERE")
            except StopIteration as e:
                trace.append("f caught %r" % (e,))
        eleza g(r):
            trace.append("g starting")
            x = yield
            trace.append("g received %r" % (x,))
            trace.append("g returning %r" % (r,))
            rudisha r
        f(None)
        f(1)
        f((2,))
        f(StopIteration(3))
        self.assertEqual(trace, [
            "g starting",
            "f sending spam to g",
            "g received 'spam'",
            "g returning None",
            "f caught StopIteration()",
            "g starting",
            "f sending spam to g",
            "g received 'spam'",
            "g returning 1",
            'f caught StopIteration(1)',
            'g starting',
            'f sending spam to g',
            "g received 'spam'",
            'g returning (2,)',
            'f caught StopIteration((2,))',
            'g starting',
            'f sending spam to g',
            "g received 'spam'",
            'g returning StopIteration(3)',
            'f caught StopIteration(StopIteration(3))'
        ])

    eleza test_catching_exception_kutoka_subgen_and_returning(self):
        """
        Test catching an exception thrown into a
        subgenerator and returning a value
        """
        eleza inner():
            try:
                yield 1
            except ValueError:
                trace.append("inner caught ValueError")
            rudisha value

        eleza outer():
            v = yield kutoka inner()
            trace.append("inner returned %r to outer" % (v,))
            yield v

        for value in 2, (2,), StopIteration(2):
            trace = []
            g = outer()
            trace.append(next(g))
            trace.append(repr(g.throw(ValueError)))
            self.assertEqual(trace, [
                1,
                "inner caught ValueError",
                "inner returned %r to outer" % (value,),
                repr(value),
            ])

    eleza test_throwing_GeneratorExit_into_subgen_that_returns(self):
        """
        Test throwing GeneratorExit into a subgenerator that
        catches it and returns normally.
        """
        trace = []
        eleza f():
            try:
                trace.append("Enter f")
                yield
                trace.append("Exit f")
            except GeneratorExit:
                return
        eleza g():
            trace.append("Enter g")
            yield kutoka f()
            trace.append("Exit g")
        try:
            gi = g()
            next(gi)
            gi.throw(GeneratorExit)
        except GeneratorExit:
            pass
        else:
            self.fail("subgenerator failed to raise GeneratorExit")
        self.assertEqual(trace,[
            "Enter g",
            "Enter f",
        ])

    eleza test_throwing_GeneratorExit_into_subgenerator_that_yields(self):
        """
        Test throwing GeneratorExit into a subgenerator that
        catches it and yields.
        """
        trace = []
        eleza f():
            try:
                trace.append("Enter f")
                yield
                trace.append("Exit f")
            except GeneratorExit:
                yield
        eleza g():
            trace.append("Enter g")
            yield kutoka f()
            trace.append("Exit g")
        try:
            gi = g()
            next(gi)
            gi.throw(GeneratorExit)
        except RuntimeError as e:
            self.assertEqual(e.args[0], "generator ignored GeneratorExit")
        else:
            self.fail("subgenerator failed to raise GeneratorExit")
        self.assertEqual(trace,[
            "Enter g",
            "Enter f",
        ])

    eleza test_throwing_GeneratorExit_into_subgen_that_raises(self):
        """
        Test throwing GeneratorExit into a subgenerator that
        catches it and raises a different exception.
        """
        trace = []
        eleza f():
            try:
                trace.append("Enter f")
                yield
                trace.append("Exit f")
            except GeneratorExit:
                raise ValueError("Vorpal bunny encountered")
        eleza g():
            trace.append("Enter g")
            yield kutoka f()
            trace.append("Exit g")
        try:
            gi = g()
            next(gi)
            gi.throw(GeneratorExit)
        except ValueError as e:
            self.assertEqual(e.args[0], "Vorpal bunny encountered")
            self.assertIsInstance(e.__context__, GeneratorExit)
        else:
            self.fail("subgenerator failed to raise ValueError")
        self.assertEqual(trace,[
            "Enter g",
            "Enter f",
        ])

    eleza test_yield_kutoka_empty(self):
        eleza g():
            yield kutoka ()
        self.assertRaises(StopIteration, next, g())

    eleza test_delegating_generators_claim_to_be_running(self):
        # Check with basic iteration
        eleza one():
            yield 0
            yield kutoka two()
            yield 3
        eleza two():
            yield 1
            try:
                yield kutoka g1
            except ValueError:
                pass
            yield 2
        g1 = one()
        self.assertEqual(list(g1), [0, 1, 2, 3])
        # Check with send
        g1 = one()
        res = [next(g1)]
        try:
            while True:
                res.append(g1.send(42))
        except StopIteration:
            pass
        self.assertEqual(res, [0, 1, 2, 3])
        # Check with throw
        kundi MyErr(Exception):
            pass
        eleza one():
            try:
                yield 0
            except MyErr:
                pass
            yield kutoka two()
            try:
                yield 3
            except MyErr:
                pass
        eleza two():
            try:
                yield 1
            except MyErr:
                pass
            try:
                yield kutoka g1
            except ValueError:
                pass
            try:
                yield 2
            except MyErr:
                pass
        g1 = one()
        res = [next(g1)]
        try:
            while True:
                res.append(g1.throw(MyErr))
        except StopIteration:
            pass
        # Check with close
        kundi MyIt(object):
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                rudisha 42
            eleza close(self_):
                self.assertTrue(g1.gi_running)
                self.assertRaises(ValueError, next, g1)
        eleza one():
            yield kutoka MyIt()
        g1 = one()
        next(g1)
        g1.close()

    eleza test_delegator_is_visible_to_debugger(self):
        eleza call_stack():
            rudisha [f[3] for f in inspect.stack()]

        eleza gen():
            yield call_stack()
            yield call_stack()
            yield call_stack()

        eleza spam(g):
            yield kutoka g

        eleza eggs(g):
            yield kutoka g

        for stack in spam(gen()):
            self.assertTrue('spam' in stack)

        for stack in spam(eggs(gen())):
            self.assertTrue('spam' in stack and 'eggs' in stack)

    eleza test_custom_iterator_return(self):
        # See issue #15568
        kundi MyIter:
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                raise StopIteration(42)
        eleza gen():
            nonlocal ret
            ret = yield kutoka MyIter()
        ret = None
        list(gen())
        self.assertEqual(ret, 42)

    eleza test_close_with_cleared_frame(self):
        # See issue #17669.
        #
        # Create a stack of generators: outer() delegating to inner()
        # delegating to innermost(). The key point is that the instance of
        # inner is created first: this ensures that its frame appears before
        # the instance of outer in the GC linked list.
        #
        # At the gc.collect call:
        #   - frame_clear is called on the inner_gen frame.
        #   - gen_dealloc is called on the outer_gen generator (the only
        #     reference is in the frame's locals).
        #   - gen_close is called on the outer_gen generator.
        #   - gen_close_iter is called to close the inner_gen generator, which
        #     in turn calls gen_close, and gen_yf.
        #
        # Previously, gen_yf would crash since inner_gen's frame had been
        # cleared (and in particular f_stacktop was NULL).

        eleza innermost():
            yield
        eleza inner():
            outer_gen = yield
            yield kutoka innermost()
        eleza outer():
            inner_gen = yield
            yield kutoka inner_gen

        with disable_gc():
            inner_gen = inner()
            outer_gen = outer()
            outer_gen.send(None)
            outer_gen.send(inner_gen)
            outer_gen.send(outer_gen)

            del outer_gen
            del inner_gen
            gc_collect()

    eleza test_send_tuple_with_custom_generator(self):
        # See issue #21209.
        kundi MyGen:
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                rudisha 42
            eleza send(self, what):
                nonlocal v
                v = what
                rudisha None
        eleza outer():
            v = yield kutoka MyGen()
        g = outer()
        next(g)
        v = None
        g.send((1, 2, 3, 4))
        self.assertEqual(v, (1, 2, 3, 4))


ikiwa __name__ == '__main__':
    unittest.main()
