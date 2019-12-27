agiza re
agiza types
agiza unittest
agiza weakref

kutoka test agiza support


kundi ClearTest(unittest.TestCase):
    """
    Tests for frame.clear().
    """

    eleza inner(self, x=5, **kwargs):
        1/0

    eleza outer(self, **kwargs):
        try:
            self.inner(**kwargs)
        except ZeroDivisionError as e:
            exc = e
        rudisha exc

    eleza clear_traceback_frames(self, tb):
        """
        Clear all frames in a traceback.
        """
        while tb is not None:
            tb.tb_frame.clear()
            tb = tb.tb_next

    eleza test_clear_locals(self):
        kundi C:
            pass
        c = C()
        wr = weakref.ref(c)
        exc = self.outer(c=c)
        del c
        support.gc_collect()
        # A reference to c is held through the frames
        self.assertIsNot(None, wr())
        self.clear_traceback_frames(exc.__traceback__)
        support.gc_collect()
        # The reference was released by .clear()
        self.assertIs(None, wr())

    eleza test_clear_generator(self):
        endly = False
        eleza g():
            nonlocal endly
            try:
                yield
                inner()
            finally:
                endly = True
        gen = g()
        next(gen)
        self.assertFalse(endly)
        # Clearing the frame closes the generator
        gen.gi_frame.clear()
        self.assertTrue(endly)

    eleza test_clear_executing(self):
        # Attempting to clear an executing frame is forbidden.
        try:
            1/0
        except ZeroDivisionError as e:
            f = e.__traceback__.tb_frame
        with self.assertRaises(RuntimeError):
            f.clear()
        with self.assertRaises(RuntimeError):
            f.f_back.clear()

    eleza test_clear_executing_generator(self):
        # Attempting to clear an executing generator frame is forbidden.
        endly = False
        eleza g():
            nonlocal endly
            try:
                1/0
            except ZeroDivisionError as e:
                f = e.__traceback__.tb_frame
                with self.assertRaises(RuntimeError):
                    f.clear()
                with self.assertRaises(RuntimeError):
                    f.f_back.clear()
                yield f
            finally:
                endly = True
        gen = g()
        f = next(gen)
        self.assertFalse(endly)
        # Clearing the frame closes the generator
        f.clear()
        self.assertTrue(endly)

    @support.cpython_only
    eleza test_clear_refcycles(self):
        # .clear() doesn't leave any refcycle behind
        with support.disable_gc():
            kundi C:
                pass
            c = C()
            wr = weakref.ref(c)
            exc = self.outer(c=c)
            del c
            self.assertIsNot(None, wr())
            self.clear_traceback_frames(exc.__traceback__)
            self.assertIs(None, wr())


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
        try:
            outer()
        except ZeroDivisionError as e:
            tb = e.__traceback__
            frames = []
            while tb:
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
        # Test f_locals before and after clear() (to exercise caching)
        f, outer, inner = self.make_frames()
        outer.f_locals
        inner.f_locals
        outer.clear()
        inner.clear()
        self.assertEqual(outer.f_locals, {})
        self.assertEqual(inner.f_locals, {})

    eleza test_f_lineno_del_segfault(self):
        f, _, _ = self.make_frames()
        with self.assertRaises(AttributeError):
            del f.f_lineno


kundi ReprTest(unittest.TestCase):
    """
    Tests for repr(frame).
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
        try:
            outer()
        except ZeroDivisionError as e:
            tb = e.__traceback__
            frames = []
            while tb:
                frames.append(tb.tb_frame)
                tb = tb.tb_next
        else:
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
