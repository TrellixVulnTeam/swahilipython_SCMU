# -*- coding: utf-8 -*-

"""
Test suite kila PEP 380 implementation

adapted kutoka original tests written by Greg Ewing
see <http://www.cosc.canterbury.ac.nz/greg.ewing/python/tuma-from/YieldFrom-Python3.1.2-rev5.zip>
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
            tuma kutoka g2()
            trace.append("Finishing g1")
        eleza g2():
            trace.append("Starting g2")
            tuma 42
            trace.append("Finishing g2")
        kila x kwenye g1():
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
        Test raising exception kwenye initial next() call
        """
        trace = []
        eleza g1():
            jaribu:
                trace.append("Starting g1")
                tuma kutoka g2()
            mwishowe:
                trace.append("Finishing g1")
        eleza g2():
            jaribu:
                trace.append("Starting g2")
                ashiria ValueError("spanish inquisition occurred")
            mwishowe:
                trace.append("Finishing g2")
        jaribu:
            kila x kwenye g1():
                trace.append("Yielded %s" % (x,))
        tatizo ValueError kama e:
            self.assertEqual(e.args[0], "spanish inquisition occurred")
        isipokua:
            self.fail("subgenerator failed to ashiria ValueError")
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
            tuma "g1 ham"
            tuma kutoka g2()
            tuma "g1 eggs"
            trace.append("Finishing g1")
        eleza g2():
            trace.append("Starting g2")
            tuma "g2 spam"
            tuma "g2 more spam"
            trace.append("Finishing g2")
        kila x kwenye g1():
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
        Test raising exception kwenye delegated next() call
        """
        trace = []
        eleza g1():
            jaribu:
                trace.append("Starting g1")
                tuma "g1 ham"
                tuma kutoka g2()
                tuma "g1 eggs"
            mwishowe:
                trace.append("Finishing g1")
        eleza g2():
            jaribu:
                trace.append("Starting g2")
                tuma "g2 spam"
                ashiria ValueError("hovercraft ni full of eels")
                tuma "g2 more spam"
            mwishowe:
                trace.append("Finishing g2")
        jaribu:
            kila x kwenye g1():
                trace.append("Yielded %s" % (x,))
        tatizo ValueError kama e:
            self.assertEqual(e.args[0], "hovercraft ni full of eels")
        isipokua:
            self.fail("subgenerator failed to ashiria ValueError")
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
            x = tuma "g1 ham"
            trace.append("g1 received %s" % (x,))
            tuma kutoka g2()
            x = tuma "g1 eggs"
            trace.append("g1 received %s" % (x,))
            trace.append("Finishing g1")
        eleza g2():
            trace.append("Starting g2")
            x = tuma "g2 spam"
            trace.append("g2 received %s" % (x,))
            x = tuma "g2 more spam"
            trace.append("g2 received %s" % (x,))
            trace.append("Finishing g2")
        g = g1()
        y = next(g)
        x = 1
        jaribu:
            wakati 1:
                y = g.send(x)
                trace.append("Yielded %s" % (y,))
                x += 1
        tatizo StopIteration:
            pita
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
        Test handling exception wakati delegating 'send'
        """
        trace = []
        eleza g1():
            trace.append("Starting g1")
            x = tuma "g1 ham"
            trace.append("g1 received %s" % (x,))
            tuma kutoka g2()
            x = tuma "g1 eggs"
            trace.append("g1 received %s" % (x,))
            trace.append("Finishing g1")
        eleza g2():
            trace.append("Starting g2")
            x = tuma "g2 spam"
            trace.append("g2 received %s" % (x,))
            ashiria ValueError("hovercraft ni full of eels")
            x = tuma "g2 more spam"
            trace.append("g2 received %s" % (x,))
            trace.append("Finishing g2")
        eleza run():
            g = g1()
            y = next(g)
            x = 1
            jaribu:
                wakati 1:
                    y = g.send(x)
                    trace.append("Yielded %s" % (y,))
                    x += 1
            tatizo StopIteration:
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
            jaribu:
                trace.append("Starting g1")
                tuma "g1 ham"
                tuma kutoka g2()
                tuma "g1 eggs"
            mwishowe:
                trace.append("Finishing g1")
        eleza g2():
            jaribu:
                trace.append("Starting g2")
                tuma "g2 spam"
                tuma "g2 more spam"
            mwishowe:
                trace.append("Finishing g2")
        g = g1()
        kila i kwenye range(2):
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
        Test handling exception wakati delegating 'close'
        """
        trace = []
        eleza g1():
            jaribu:
                trace.append("Starting g1")
                tuma "g1 ham"
                tuma kutoka g2()
                tuma "g1 eggs"
            mwishowe:
                trace.append("Finishing g1")
        eleza g2():
            jaribu:
                trace.append("Starting g2")
                tuma "g2 spam"
                tuma "g2 more spam"
            mwishowe:
                trace.append("Finishing g2")
                ashiria ValueError("nybbles have exploded ukijumuisha delight")
        jaribu:
            g = g1()
            kila i kwenye range(2):
                x = next(g)
                trace.append("Yielded %s" % (x,))
            g.close()
        tatizo ValueError kama e:
            self.assertEqual(e.args[0], "nybbles have exploded ukijumuisha delight")
            self.assertIsInstance(e.__context__, GeneratorExit)
        isipokua:
            self.fail("subgenerator failed to ashiria ValueError")
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
            jaribu:
                trace.append("Starting g1")
                tuma "g1 ham"
                tuma kutoka g2()
                tuma "g1 eggs"
            mwishowe:
                trace.append("Finishing g1")
        eleza g2():
            jaribu:
                trace.append("Starting g2")
                tuma "g2 spam"
                tuma "g2 more spam"
            mwishowe:
                trace.append("Finishing g2")
        jaribu:
            g = g1()
            kila i kwenye range(2):
                x = next(g)
                trace.append("Yielded %s" % (x,))
            e = ValueError("tomato ejected")
            g.throw(e)
        tatizo ValueError kama e:
            self.assertEqual(e.args[0], "tomato ejected")
        isipokua:
            self.fail("subgenerator failed to ashiria ValueError")
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
            "value = Tupu",
            "StopIteration: spam",
            "value = spam",
            "StopIteration: spam",
            "value = eggs",
        ])


    eleza test_exception_value_crash(self):
        # There used to be a refcount error when the rudisha value
        # stored kwenye the StopIteration has a refcount of 1.
        eleza g1():
            tuma kutoka g2()
        eleza g2():
            tuma "g2"
            rudisha [42]
        self.assertEqual(list(g1()), ["g2"])


    eleza test_generator_return_value(self):
        """
        Test generator rudisha value
        """
        trace = []
        eleza g1():
            trace.append("Starting g1")
            tuma "g1 ham"
            ret = tuma kutoka g2()
            trace.append("g2 returned %r" % (ret,))
            kila v kwenye 1, (2,), StopIteration(3):
                ret = tuma kutoka g2(v)
                trace.append("g2 returned %r" % (ret,))
            tuma "g1 eggs"
            trace.append("Finishing g1")
        eleza g2(v = Tupu):
            trace.append("Starting g2")
            tuma "g2 spam"
            tuma "g2 more spam"
            trace.append("Finishing g2")
            ikiwa v:
                rudisha v
        kila x kwenye g1():
            trace.append("Yielded %s" % (x,))
        self.assertEqual(trace,[
            "Starting g1",
            "Yielded g1 ham",
            "Starting g2",
            "Yielded g2 spam",
            "Yielded g2 more spam",
            "Finishing g2",
            "g2 returned Tupu",
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
            tuma kutoka range(3)
        kila x kwenye g():
            trace.append("Yielded %s" % (x,))
        self.assertEqual(trace,[
            "Yielded 0",
            "Yielded 1",
            "Yielded 2",
        ])


    eleza test_conversion_of_sendTupu_to_next(self):
        """
        Test conversion of send(Tupu) to next()
        """
        trace = []
        eleza g():
            tuma kutoka range(3)
        gi = g()
        kila x kwenye range(3):
            y = gi.send(Tupu)
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
            jaribu:
                trace.append("starting g")
                tuma kutoka range(3)
                trace.append("g should sio be here")
            mwishowe:
                trace.append("finishing g")
        gi = g()
        next(gi)
        ukijumuisha captured_stderr() kama output:
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
            jaribu:
                trace.append("Starting g")
                tuma kutoka range(10)
            mwishowe:
                trace.append("Finishing g")
        jaribu:
            gi = g()
            kila i kwenye range(5):
                x = next(gi)
                trace.append("Yielded %s" % (x,))
            e = ValueError("tomato ejected")
            gi.throw(e)
        tatizo ValueError kama e:
            self.assertEqual(e.args[0],"tomato ejected")
        isipokua:
            self.fail("subgenerator failed to ashiria ValueError")
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
            jaribu:
                trace.append("starting g")
                tuma kutoka range(3)
                trace.append("g should sio be here")
            mwishowe:
                trace.append("finishing g")
        jaribu:
            gi = g()
            next(gi)
            kila x kwenye range(3):
                y = gi.send(42)
                trace.append("Should sio have tumaed: %s" % (y,))
        tatizo AttributeError kama e:
            self.assertIn("send", e.args[0])
        isipokua:
            self.fail("was able to send into non-generator")
        self.assertEqual(trace,[
            "starting g",
            "finishing g",
        ])

    eleza test_broken_getattr_handling(self):
        """
        Test subiterator ukijumuisha a broken getattr implementation
        """
        kundi Broken:
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                rudisha 1
            eleza __getattr__(self, attr):
                1/0

        eleza g():
            tuma kutoka Broken()

        ukijumuisha self.assertRaises(ZeroDivisionError):
            gi = g()
            self.assertEqual(next(gi), 1)
            gi.send(1)

        ukijumuisha self.assertRaises(ZeroDivisionError):
            gi = g()
            self.assertEqual(next(gi), 1)
            gi.throw(AttributeError)

        ukijumuisha support.catch_unraisable_exception() kama cm:
            gi = g()
            self.assertEqual(next(gi), 1)
            gi.close()

            self.assertEqual(ZeroDivisionError, cm.unraisable.exc_type)

    eleza test_exception_in_initial_next_call(self):
        """
        Test exception kwenye initial next() call
        """
        trace = []
        eleza g1():
            trace.append("g1 about to tuma kutoka g2")
            tuma kutoka g2()
            trace.append("g1 should sio be here")
        eleza g2():
            tuma 1/0
        eleza run():
            gi = g1()
            next(gi)
        self.assertRaises(ZeroDivisionError,run)
        self.assertEqual(trace,[
            "g1 about to tuma kutoka g2"
        ])

    eleza test_attempted_tuma_from_loop(self):
        """
        Test attempted tuma-kutoka loop
        """
        trace = []
        eleza g1():
            trace.append("g1: starting")
            tuma "y1"
            trace.append("g1: about to tuma kutoka g2")
            tuma kutoka g2()
            trace.append("g1 should sio be here")

        eleza g2():
            trace.append("g2: starting")
            tuma "y2"
            trace.append("g2: about to tuma kutoka g1")
            tuma kutoka gi
            trace.append("g2 should sio be here")
        jaribu:
            gi = g1()
            kila y kwenye gi:
                trace.append("Yielded: %s" % (y,))
        tatizo ValueError kama e:
            self.assertEqual(e.args[0],"generator already executing")
        isipokua:
            self.fail("subgenerator didn't ashiria ValueError")
        self.assertEqual(trace,[
            "g1: starting",
            "Yielded: y1",
            "g1: about to tuma kutoka g2",
            "g2: starting",
            "Yielded: y2",
            "g2: about to tuma kutoka g1",
        ])

    eleza test_returning_value_from_delegated_throw(self):
        """
        Test returning value kutoka delegated 'throw'
        """
        trace = []
        eleza g1():
            jaribu:
                trace.append("Starting g1")
                tuma "g1 ham"
                tuma kutoka g2()
                tuma "g1 eggs"
            mwishowe:
                trace.append("Finishing g1")
        eleza g2():
            jaribu:
                trace.append("Starting g2")
                tuma "g2 spam"
                tuma "g2 more spam"
            tatizo LunchError:
                trace.append("Caught LunchError kwenye g2")
                tuma "g2 lunch saved"
                tuma "g2 yet more spam"
        kundi LunchError(Exception):
            pita
        g = g1()
        kila i kwenye range(2):
            x = next(g)
            trace.append("Yielded %s" % (x,))
        e = LunchError("tomato ejected")
        g.throw(e)
        kila x kwenye g:
            trace.append("Yielded %s" % (x,))
        self.assertEqual(trace,[
            "Starting g1",
            "Yielded g1 ham",
            "Starting g2",
            "Yielded g2 spam",
            "Caught LunchError kwenye g2",
            "Yielded g2 yet more spam",
            "Yielded g1 eggs",
            "Finishing g1",
        ])

    eleza test_next_and_return_with_value(self):
        """
        Test next na rudisha ukijumuisha value
        """
        trace = []
        eleza f(r):
            gi = g(r)
            next(gi)
            jaribu:
                trace.append("f resuming g")
                next(gi)
                trace.append("f SHOULD NOT BE HERE")
            tatizo StopIteration kama e:
                trace.append("f caught %r" % (e,))
        eleza g(r):
            trace.append("g starting")
            tuma
            trace.append("g returning %r" % (r,))
            rudisha r
        f(Tupu)
        f(1)
        f((2,))
        f(StopIteration(3))
        self.assertEqual(trace,[
            "g starting",
            "f resuming g",
            "g returning Tupu",
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
        Test send na rudisha ukijumuisha value
        """
        trace = []
        eleza f(r):
            gi = g(r)
            next(gi)
            jaribu:
                trace.append("f sending spam to g")
                gi.send("spam")
                trace.append("f SHOULD NOT BE HERE")
            tatizo StopIteration kama e:
                trace.append("f caught %r" % (e,))
        eleza g(r):
            trace.append("g starting")
            x = tuma
            trace.append("g received %r" % (x,))
            trace.append("g returning %r" % (r,))
            rudisha r
        f(Tupu)
        f(1)
        f((2,))
        f(StopIteration(3))
        self.assertEqual(trace, [
            "g starting",
            "f sending spam to g",
            "g received 'spam'",
            "g returning Tupu",
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

    eleza test_catching_exception_from_subgen_and_returning(self):
        """
        Test catching an exception thrown into a
        subgenerator na returning a value
        """
        eleza inner():
            jaribu:
                tuma 1
            tatizo ValueError:
                trace.append("inner caught ValueError")
            rudisha value

        eleza outer():
            v = tuma kutoka inner()
            trace.append("inner returned %r to outer" % (v,))
            tuma v

        kila value kwenye 2, (2,), StopIteration(2):
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
        catches it na returns normally.
        """
        trace = []
        eleza f():
            jaribu:
                trace.append("Enter f")
                tuma
                trace.append("Exit f")
            tatizo GeneratorExit:
                return
        eleza g():
            trace.append("Enter g")
            tuma kutoka f()
            trace.append("Exit g")
        jaribu:
            gi = g()
            next(gi)
            gi.throw(GeneratorExit)
        tatizo GeneratorExit:
            pita
        isipokua:
            self.fail("subgenerator failed to ashiria GeneratorExit")
        self.assertEqual(trace,[
            "Enter g",
            "Enter f",
        ])

    eleza test_throwing_GeneratorExit_into_subgenerator_that_tumas(self):
        """
        Test throwing GeneratorExit into a subgenerator that
        catches it na tumas.
        """
        trace = []
        eleza f():
            jaribu:
                trace.append("Enter f")
                tuma
                trace.append("Exit f")
            tatizo GeneratorExit:
                tuma
        eleza g():
            trace.append("Enter g")
            tuma kutoka f()
            trace.append("Exit g")
        jaribu:
            gi = g()
            next(gi)
            gi.throw(GeneratorExit)
        tatizo RuntimeError kama e:
            self.assertEqual(e.args[0], "generator ignored GeneratorExit")
        isipokua:
            self.fail("subgenerator failed to ashiria GeneratorExit")
        self.assertEqual(trace,[
            "Enter g",
            "Enter f",
        ])

    eleza test_throwing_GeneratorExit_into_subgen_that_raises(self):
        """
        Test throwing GeneratorExit into a subgenerator that
        catches it na raises a different exception.
        """
        trace = []
        eleza f():
            jaribu:
                trace.append("Enter f")
                tuma
                trace.append("Exit f")
            tatizo GeneratorExit:
                ashiria ValueError("Vorpal bunny encountered")
        eleza g():
            trace.append("Enter g")
            tuma kutoka f()
            trace.append("Exit g")
        jaribu:
            gi = g()
            next(gi)
            gi.throw(GeneratorExit)
        tatizo ValueError kama e:
            self.assertEqual(e.args[0], "Vorpal bunny encountered")
            self.assertIsInstance(e.__context__, GeneratorExit)
        isipokua:
            self.fail("subgenerator failed to ashiria ValueError")
        self.assertEqual(trace,[
            "Enter g",
            "Enter f",
        ])

    eleza test_tuma_from_empty(self):
        eleza g():
            tuma kutoka ()
        self.assertRaises(StopIteration, next, g())

    eleza test_delegating_generators_claim_to_be_running(self):
        # Check ukijumuisha basic iteration
        eleza one():
            tuma 0
            tuma kutoka two()
            tuma 3
        eleza two():
            tuma 1
            jaribu:
                tuma kutoka g1
            tatizo ValueError:
                pita
            tuma 2
        g1 = one()
        self.assertEqual(list(g1), [0, 1, 2, 3])
        # Check ukijumuisha send
        g1 = one()
        res = [next(g1)]
        jaribu:
            wakati Kweli:
                res.append(g1.send(42))
        tatizo StopIteration:
            pita
        self.assertEqual(res, [0, 1, 2, 3])
        # Check ukijumuisha throw
        kundi MyErr(Exception):
            pita
        eleza one():
            jaribu:
                tuma 0
            tatizo MyErr:
                pita
            tuma kutoka two()
            jaribu:
                tuma 3
            tatizo MyErr:
                pita
        eleza two():
            jaribu:
                tuma 1
            tatizo MyErr:
                pita
            jaribu:
                tuma kutoka g1
            tatizo ValueError:
                pita
            jaribu:
                tuma 2
            tatizo MyErr:
                pita
        g1 = one()
        res = [next(g1)]
        jaribu:
            wakati Kweli:
                res.append(g1.throw(MyErr))
        tatizo StopIteration:
            pita
        # Check ukijumuisha close
        kundi MyIt(object):
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                rudisha 42
            eleza close(self_):
                self.assertKweli(g1.gi_running)
                self.assertRaises(ValueError, next, g1)
        eleza one():
            tuma kutoka MyIt()
        g1 = one()
        next(g1)
        g1.close()

    eleza test_delegator_is_visible_to_debugger(self):
        eleza call_stack():
            rudisha [f[3] kila f kwenye inspect.stack()]

        eleza gen():
            tuma call_stack()
            tuma call_stack()
            tuma call_stack()

        eleza spam(g):
            tuma kutoka g

        eleza eggs(g):
            tuma kutoka g

        kila stack kwenye spam(gen()):
            self.assertKweli('spam' kwenye stack)

        kila stack kwenye spam(eggs(gen())):
            self.assertKweli('spam' kwenye stack na 'eggs' kwenye stack)

    eleza test_custom_iterator_return(self):
        # See issue #15568
        kundi MyIter:
            eleza __iter__(self):
                rudisha self
            eleza __next__(self):
                ashiria StopIteration(42)
        eleza gen():
            nonlocal ret
            ret = tuma kutoka MyIter()
        ret = Tupu
        list(gen())
        self.assertEqual(ret, 42)

    eleza test_close_with_cleared_frame(self):
        # See issue #17669.
        #
        # Create a stack of generators: outer() delegating to inner()
        # delegating to innermost(). The key point ni that the instance of
        # inner ni created first: this ensures that its frame appears before
        # the instance of outer kwenye the GC linked list.
        #
        # At the gc.collect call:
        #   - frame_clear ni called on the inner_gen frame.
        #   - gen_dealloc ni called on the outer_gen generator (the only
        #     reference ni kwenye the frame's locals).
        #   - gen_close ni called on the outer_gen generator.
        #   - gen_close_iter ni called to close the inner_gen generator, which
        #     kwenye turn calls gen_close, na gen_yf.
        #
        # Previously, gen_yf would crash since inner_gen's frame had been
        # cleared (and kwenye particular f_stacktop was NULL).

        eleza innermost():
            tuma
        eleza inner():
            outer_gen = tuma
            tuma kutoka innermost()
        eleza outer():
            inner_gen = tuma
            tuma kutoka inner_gen

        ukijumuisha disable_gc():
            inner_gen = inner()
            outer_gen = outer()
            outer_gen.send(Tupu)
            outer_gen.send(inner_gen)
            outer_gen.send(outer_gen)

            toa outer_gen
            toa inner_gen
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
                rudisha Tupu
        eleza outer():
            v = tuma kutoka MyGen()
        g = outer()
        next(g)
        v = Tupu
        g.send((1, 2, 3, 4))
        self.assertEqual(v, (1, 2, 3, 4))


ikiwa __name__ == '__main__':
    unittest.main()
