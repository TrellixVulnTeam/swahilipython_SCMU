"""
Tests for object finalization semantics, as outlined in PEP 442.
"""

agiza contextlib
agiza gc
agiza unittest
agiza weakref

try:
    kutoka _testcapi agiza with_tp_del
except ImportError:
    eleza with_tp_del(cls):
        kundi C(object):
            eleza __new__(cls, *args, **kwargs):
                raise TypeError('requires _testcapi.with_tp_del')
        rudisha C

kutoka test agiza support


kundi NonGCSimpleBase:
    """
    The base kundi for all the objects under test, equipped with various
    testing features.
    """

    survivors = []
    del_calls = []
    tp_del_calls = []
    errors = []

    _cleaning = False

    __slots__ = ()

    @classmethod
    eleza _cleanup(cls):
        cls.survivors.clear()
        cls.errors.clear()
        gc.garbage.clear()
        gc.collect()
        cls.del_calls.clear()
        cls.tp_del_calls.clear()

    @classmethod
    @contextlib.contextmanager
    eleza test(cls):
        """
        A context manager to use around all finalization tests.
        """
        with support.disable_gc():
            cls.del_calls.clear()
            cls.tp_del_calls.clear()
            NonGCSimpleBase._cleaning = False
            try:
                yield
                ikiwa cls.errors:
                    raise cls.errors[0]
            finally:
                NonGCSimpleBase._cleaning = True
                cls._cleanup()

    eleza check_sanity(self):
        """
        Check the object is sane (non-broken).
        """

    eleza __del__(self):
        """
        PEP 442 finalizer.  Record that this was called, check the
        object is in a sane state, and invoke a side effect.
        """
        try:
            ikiwa not self._cleaning:
                self.del_calls.append(id(self))
                self.check_sanity()
                self.side_effect()
        except Exception as e:
            self.errors.append(e)

    eleza side_effect(self):
        """
        A side effect called on destruction.
        """


kundi SimpleBase(NonGCSimpleBase):

    eleza __init__(self):
        self.id_ = id(self)

    eleza check_sanity(self):
        assert self.id_ == id(self)


kundi NonGC(NonGCSimpleBase):
    __slots__ = ()

kundi NonGCResurrector(NonGCSimpleBase):
    __slots__ = ()

    eleza side_effect(self):
        """
        Resurrect self by storing self in a class-wide list.
        """
        self.survivors.append(self)

kundi Simple(SimpleBase):
    pass

kundi SimpleResurrector(NonGCResurrector, SimpleBase):
    pass


kundi TestBase:

    eleza setUp(self):
        self.old_garbage = gc.garbage[:]
        gc.garbage[:] = []

    eleza tearDown(self):
        # None of the tests here should put anything in gc.garbage
        try:
            self.assertEqual(gc.garbage, [])
        finally:
            del self.old_garbage
            gc.collect()

    eleza assert_del_calls(self, ids):
        self.assertEqual(sorted(SimpleBase.del_calls), sorted(ids))

    eleza assert_tp_del_calls(self, ids):
        self.assertEqual(sorted(SimpleBase.tp_del_calls), sorted(ids))

    eleza assert_survivors(self, ids):
        self.assertEqual(sorted(id(x) for x in SimpleBase.survivors), sorted(ids))

    eleza assert_garbage(self, ids):
        self.assertEqual(sorted(id(x) for x in gc.garbage), sorted(ids))

    eleza clear_survivors(self):
        SimpleBase.survivors.clear()


kundi SimpleFinalizationTest(TestBase, unittest.TestCase):
    """
    Test finalization without refcycles.
    """

    eleza test_simple(self):
        with SimpleBase.test():
            s = Simple()
            ids = [id(s)]
            wr = weakref.ref(s)
            del s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), None)
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])

    eleza test_simple_resurrect(self):
        with SimpleBase.test():
            s = SimpleResurrector()
            ids = [id(s)]
            wr = weakref.ref(s)
            del s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors(ids)
            self.assertIsNot(wr(), None)
            self.clear_survivors()
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
        self.assertIs(wr(), None)

    eleza test_non_gc(self):
        with SimpleBase.test():
            s = NonGC()
            self.assertFalse(gc.is_tracked(s))
            ids = [id(s)]
            del s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])

    eleza test_non_gc_resurrect(self):
        with SimpleBase.test():
            s = NonGCResurrector()
            self.assertFalse(gc.is_tracked(s))
            ids = [id(s)]
            del s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors(ids)
            self.clear_survivors()
            gc.collect()
            self.assert_del_calls(ids * 2)
            self.assert_survivors(ids)


kundi SelfCycleBase:

    eleza __init__(self):
        super().__init__()
        self.ref = self

    eleza check_sanity(self):
        super().check_sanity()
        assert self.ref is self

kundi SimpleSelfCycle(SelfCycleBase, Simple):
    pass

kundi SelfCycleResurrector(SelfCycleBase, SimpleResurrector):
    pass

kundi SuicidalSelfCycle(SelfCycleBase, Simple):

    eleza side_effect(self):
        """
        Explicitly break the reference cycle.
        """
        self.ref = None


kundi SelfCycleFinalizationTest(TestBase, unittest.TestCase):
    """
    Test finalization of an object having a single cyclic reference to
    itself.
    """

    eleza test_simple(self):
        with SimpleBase.test():
            s = SimpleSelfCycle()
            ids = [id(s)]
            wr = weakref.ref(s)
            del s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), None)
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])

    eleza test_simple_resurrect(self):
        # Test that __del__ can resurrect the object being finalized.
        with SimpleBase.test():
            s = SelfCycleResurrector()
            ids = [id(s)]
            wr = weakref.ref(s)
            del s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors(ids)
            # XXX is this desirable?
            self.assertIs(wr(), None)
            # When trying to destroy the object a second time, __del__
            # isn't called anymore (and the object isn't resurrected).
            self.clear_survivors()
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), None)

    eleza test_simple_suicide(self):
        # Test the GC is able to deal with an object that kills its last
        # reference during __del__.
        with SimpleBase.test():
            s = SuicidalSelfCycle()
            ids = [id(s)]
            wr = weakref.ref(s)
            del s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), None)
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), None)


kundi ChainedBase:

    eleza chain(self, left):
        self.suicided = False
        self.left = left
        left.right = self

    eleza check_sanity(self):
        super().check_sanity()
        ikiwa self.suicided:
            assert self.left is None
            assert self.right is None
        else:
            left = self.left
            ikiwa left.suicided:
                assert left.right is None
            else:
                assert left.right is self
            right = self.right
            ikiwa right.suicided:
                assert right.left is None
            else:
                assert right.left is self

kundi SimpleChained(ChainedBase, Simple):
    pass

kundi ChainedResurrector(ChainedBase, SimpleResurrector):
    pass

kundi SuicidalChained(ChainedBase, Simple):

    eleza side_effect(self):
        """
        Explicitly break the reference cycle.
        """
        self.suicided = True
        self.left = None
        self.right = None


kundi CycleChainFinalizationTest(TestBase, unittest.TestCase):
    """
    Test finalization of a cyclic chain.  These tests are similar in
    spirit to the self-cycle tests above, but the collectable object
    graph isn't trivial anymore.
    """

    eleza build_chain(self, classes):
        nodes = [cls() for cls in classes]
        for i in range(len(nodes)):
            nodes[i].chain(nodes[i-1])
        rudisha nodes

    eleza check_non_resurrecting_chain(self, classes):
        N = len(classes)
        with SimpleBase.test():
            nodes = self.build_chain(classes)
            ids = [id(s) for s in nodes]
            wrs = [weakref.ref(s) for s in nodes]
            del nodes
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertEqual([wr() for wr in wrs], [None] * N)
            gc.collect()
            self.assert_del_calls(ids)

    eleza check_resurrecting_chain(self, classes):
        N = len(classes)
        with SimpleBase.test():
            nodes = self.build_chain(classes)
            N = len(nodes)
            ids = [id(s) for s in nodes]
            survivor_ids = [id(s) for s in nodes ikiwa isinstance(s, SimpleResurrector)]
            wrs = [weakref.ref(s) for s in nodes]
            del nodes
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors(survivor_ids)
            # XXX desirable?
            self.assertEqual([wr() for wr in wrs], [None] * N)
            self.clear_survivors()
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])

    eleza test_homogenous(self):
        self.check_non_resurrecting_chain([SimpleChained] * 3)

    eleza test_homogenous_resurrect(self):
        self.check_resurrecting_chain([ChainedResurrector] * 3)

    eleza test_homogenous_suicidal(self):
        self.check_non_resurrecting_chain([SuicidalChained] * 3)

    eleza test_heterogenous_suicidal_one(self):
        self.check_non_resurrecting_chain([SuicidalChained, SimpleChained] * 2)

    eleza test_heterogenous_suicidal_two(self):
        self.check_non_resurrecting_chain(
            [SuicidalChained] * 2 + [SimpleChained] * 2)

    eleza test_heterogenous_resurrect_one(self):
        self.check_resurrecting_chain([ChainedResurrector, SimpleChained] * 2)

    eleza test_heterogenous_resurrect_two(self):
        self.check_resurrecting_chain(
            [ChainedResurrector, SimpleChained, SuicidalChained] * 2)

    eleza test_heterogenous_resurrect_three(self):
        self.check_resurrecting_chain(
            [ChainedResurrector] * 2 + [SimpleChained] * 2 + [SuicidalChained] * 2)


# NOTE: the tp_del slot isn't automatically inherited, so we have to call
# with_tp_del() for each instantiated class.

kundi LegacyBase(SimpleBase):

    eleza __del__(self):
        try:
            # Do not invoke side_effect here, since we are now exercising
            # the tp_del slot.
            ikiwa not self._cleaning:
                self.del_calls.append(id(self))
                self.check_sanity()
        except Exception as e:
            self.errors.append(e)

    eleza __tp_del__(self):
        """
        Legacy (pre-PEP 442) finalizer, mapped to a tp_del slot.
        """
        try:
            ikiwa not self._cleaning:
                self.tp_del_calls.append(id(self))
                self.check_sanity()
                self.side_effect()
        except Exception as e:
            self.errors.append(e)

@with_tp_del
kundi Legacy(LegacyBase):
    pass

@with_tp_del
kundi LegacyResurrector(LegacyBase):

    eleza side_effect(self):
        """
        Resurrect self by storing self in a class-wide list.
        """
        self.survivors.append(self)

@with_tp_del
kundi LegacySelfCycle(SelfCycleBase, LegacyBase):
    pass


@support.cpython_only
kundi LegacyFinalizationTest(TestBase, unittest.TestCase):
    """
    Test finalization of objects with a tp_del.
    """

    eleza tearDown(self):
        # These tests need to clean up a bit more, since they create
        # uncollectable objects.
        gc.garbage.clear()
        gc.collect()
        super().tearDown()

    eleza test_legacy(self):
        with SimpleBase.test():
            s = Legacy()
            ids = [id(s)]
            wr = weakref.ref(s)
            del s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_tp_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), None)
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_tp_del_calls(ids)

    eleza test_legacy_resurrect(self):
        with SimpleBase.test():
            s = LegacyResurrector()
            ids = [id(s)]
            wr = weakref.ref(s)
            del s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_tp_del_calls(ids)
            self.assert_survivors(ids)
            # weakrefs are cleared before tp_del is called.
            self.assertIs(wr(), None)
            self.clear_survivors()
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_tp_del_calls(ids * 2)
            self.assert_survivors(ids)
        self.assertIs(wr(), None)

    eleza test_legacy_self_cycle(self):
        # Self-cycles with legacy finalizers end up in gc.garbage.
        with SimpleBase.test():
            s = LegacySelfCycle()
            ids = [id(s)]
            wr = weakref.ref(s)
            del s
            gc.collect()
            self.assert_del_calls([])
            self.assert_tp_del_calls([])
            self.assert_survivors([])
            self.assert_garbage(ids)
            self.assertIsNot(wr(), None)
            # Break the cycle to allow collection
            gc.garbage[0].ref = None
        self.assert_garbage([])
        self.assertIs(wr(), None)


ikiwa __name__ == "__main__":
    unittest.main()
