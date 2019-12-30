agiza re
agiza types
agiza unittest
agiza weakref

kutoka test agiza support


kundi ClearTest(unittest.TestCase):
    """
    Tests kila frame.clear().
    """

    eleza inner(self, x=5, **kwargs):
        1/0

    eleza outer(self, **kwargs):
        jaribu:
            self.inner(**kwargs)
        tatizo ZeroDivisionError kama e:
            exc = e
        rudisha exc

    eleza clear_traceback_frames(self, tb):
        """
        Clear all frames kwenye a traceback.
        """
        wakati tb ni sio Tupu:
            tb.tb_frame.clear()
            tb = tb.tb_next

    eleza test_clear_locals(self):
        kundi C:
            pita
        c = C()
        wr = weakref.ref(c)
        exc = self.outer(c=c)
        toa c
        support.gc_collect()
        # A reference to c ni held through the frames
        self.assertIsNot(Tupu, wr())
        self.clear_traceback_frames(exc.__traceback__)
        support.gc_collect()
        # The reference was released by .clear()
        self.assertIs(Tupu, wr())

    eleza test_clear_generator(self):
        endly = Uongo
        eleza g():
            nonlocal endly
            jaribu:
                tuma
                inner()
            mwishowe:
                endly = Kweli
        gen = g()
        next(gen)
        self.assertUongo(endly)
        # Clearing the frame closes the generator
        gen.gi_frame.clear()
        self.assertKweli(endly)

    eleza test_clear_executing(self):
        # Attempting to clear an executing frame ni forbidden.
        jaribu:
            1/0
        tatizo ZeroDivisionError kama e:
            f = e.__traceback__.tb_frame
        ukijumuisha self.assertRaises(RuntimeError):
            f.clear()
        ukijumuisha self.assertRaises(RuntimeError):
            f.f_back.clear()

    eleza test_clear_executing_generator(self):
        # Attempting to clear an executing generator frame ni forbidden.
        endly = Uongo
        eleza g():
            nonlocal endly
            jaribu:
                1/0
            tatizo ZeroDivisionError kama e:
                f = e.__traceback__.tb_frame
                ukijumuisha self.assertRaises(RuntimeError):
                    f.clear()
                ukijumuisha self.assertRaises(RuntimeError):
                    f.f_back.clear()
                tuma f
            mwishowe:
                endly = Kweli
        gen = g()
        f = next(gen)
        self.assertUongo(endly)
        # Clearing the frame closes the generator
        f.clear()
        self.assertKweli(endly)

    @support.cpython_only
    eleza test_clear_refcycles(self):
        # .clear() doesn't leave any refcycle behind
        ukijumuisha support.disable_gc():
            kundi C:
                pita
            c = C()
            wr = weakref.ref(c)
            exc = self.outer(c=c)
            toa c
            self.assertIsNot(Tupu, wr())
            self.clear_traceback_frames(exc.__traceback__)
            self.assertIs(Tupu, wr())


kundi FrameAttrsTest(unittest.TestCase):

    eleza make_frames(self):
        eleza outer():
            x = 5
            y = 6
            eleza inner():
                z = x + 2
                1/0
                t = 9
            rudisha inner()
        jaribu:
            outer()
        tatizo ZeroDivisionError kama e:
            tb = e.__traceback__
            frames = []
            wakati tb:
                frames.append(tb.tb_frame)
                tb = tb.tb_next
        rudisha frames

    eleza test_locals(self):
        f, outer, inner = self.make_frames()
        outer_locals = outer.f_locals
        self.assertIsInstance(outer_locals.pop('inner'), types.FunctionType)
        self.assertEqual(outer_locals, {'x': 5, 'y': 6})
        inner_locals = inner.f_locals
        self.assertEqual(inner_locals, {'x': 5, 'z': 7})

    eleza test_clear_locals(self):
        # Test f_locals after clear() (issue #21897)
        f, outer, inner = self.make_frames()
        outer.clear()
        inner.clear()
        self.assertEqual(outer.f_locals, {})
        self.assertEqual(inner.f_locals, {})

    eleza test_locals_clear_locals(self):
        # Test f_locals before na after clear() (to exercise caching)
        f, outer, inner = self.make_frames()
        outer.f_locals
        inner.f_locals
        outer.clear()
        inner.clear()
        self.assertEqual(outer.f_locals, {})
        self.assertEqual(inner.f_locals, {})

    eleza test_f_lineno_del_segfault(self):
        f, _, _ = self.make_frames()
        ukijumuisha self.assertRaises(AttributeError):
            toa f.f_lineno


kundi ReprTest(unittest.TestCase):
    """
    Tests kila repr(frame).
    """

    eleza test_repr(self):
        eleza outer():
            x = 5
            y = 6
            eleza inner():
                z = x + 2
                1/0
                t = 9
            rudisha inner()

        offset = outer.__code__.co_firstlineno
        jaribu:
            outer()
        tatizo ZeroDivisionError kama e:
            tb = e.__traceback__
            frames = []
            wakati tb:
                frames.append(tb.tb_frame)
                tb = tb.tb_next
        isipokua:
            self.fail("should have raised")

        f_this, f_outer, f_inner = frames
        file_repr = re.escape(repr(__file__))
        self.assertRegex(repr(f_this),
                         r"^<frame at 0x[0-9a-fA-F]+, file %s, line %d, code test_repr>$"
                         % (file_repr, offset + 23))
        self.assertRegex(repr(f_outer),
                         r"^<frame at 0x[0-9a-fA-F]+, file %s, line %d, code outer>$"
                         % (file_repr, offset + 7))
        self.assertRegex(repr(f_inner),
                         r"^<frame at 0x[0-9a-fA-F]+, file %s, line %d, code inner>$"
                         % (file_repr, offset + 5))


ikiwa __name__ == "__main__":
    unittest.main()
