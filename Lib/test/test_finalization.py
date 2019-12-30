"""
Tests kila object finalization semantics, kama outlined kwenye PEP 442.
"""

agiza contextlib
agiza gc
agiza unittest
agiza weakref

jaribu:
    kutoka _testcapi agiza with_tp_del
tatizo ImportError:
    eleza with_tp_del(cls):
        kundi C(object):
            eleza __new__(cls, *args, **kwargs):
                ashiria TypeError('requires _testcapi.with_tp_del')
        rudisha C

kutoka test agiza support


kundi NonGCSimpleBase:
    """
    The base kundi kila all the objects under test, equipped ukijumuisha various
    testing features.
    """

    survivors = []
    del_calls = []
    tp_del_calls = []
    errors = []

    _cleaning = Uongo

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
        ukijumuisha support.disable_gc():
            cls.del_calls.clear()
            cls.tp_del_calls.clear()
            NonGCSimpleBase._cleaning = Uongo
            jaribu:
                tuma
                ikiwa cls.errors:
                    ashiria cls.errors[0]
            mwishowe:
                NonGCSimpleBase._cleaning = Kweli
                cls._cleanup()

    eleza check_sanity(self):
        """
        Check the object ni sane (non-broken).
        """

    eleza __del__(self):
        """
        PEP 442 finalizer.  Record that this was called, check the
        object ni kwenye a sane state, na invoke a side effect.
        """
        jaribu:
            ikiwa sio self._cleaning:
                self.del_calls.append(id(self))
                self.check_sanity()
                self.side_effect()
        tatizo Exception kama e:
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
        Resurrect self by storing self kwenye a class-wide list.
        """
        self.survivors.append(self)

kundi Simple(SimpleBase):
    pita

kundi SimpleResurrector(NonGCResurrector, SimpleBase):
    pita


kundi TestBase:

    eleza setUp(self):
        self.old_garbage = gc.garbage[:]
        gc.garbage[:] = []

    eleza tearDown(self):
        # Tupu of the tests here should put anything kwenye gc.garbage
        jaribu:
            self.assertEqual(gc.garbage, [])
        mwishowe:
            toa self.old_garbage
            gc.collect()

    eleza assert_del_calls(self, ids):
        self.assertEqual(sorted(SimpleBase.del_calls), sorted(ids))

    eleza assert_tp_del_calls(self, ids):
        self.assertEqual(sorted(SimpleBase.tp_del_calls), sorted(ids))

    eleza assert_survivors(self, ids):
        self.assertEqual(sorted(id(x) kila x kwenye SimpleBase.survivors), sorted(ids))

    eleza assert_garbage(self, ids):
        self.assertEqual(sorted(id(x) kila x kwenye gc.garbage), sorted(ids))

    eleza clear_survivors(self):
        SimpleBase.survivors.clear()


kundi SimpleFinalizationTest(TestBase, unittest.TestCase):
    """
    Test finalization without refcycles.
    """

    eleza test_simple(self):
        ukijumuisha SimpleBase.test():
            s = Simple()
            ids = [id(s)]
            wr = weakref.ref(s)
            toa s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), Tupu)
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])

    eleza test_simple_resurrect(self):
        ukijumuisha SimpleBase.test():
            s = SimpleResurrector()
            ids = [id(s)]
            wr = weakref.ref(s)
            toa s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors(ids)
            self.assertIsNot(wr(), Tupu)
            self.clear_survivors()
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
        self.assertIs(wr(), Tupu)

    eleza test_non_gc(self):
        ukijumuisha SimpleBase.test():
            s = NonGC()
            self.assertUongo(gc.is_tracked(s))
            ids = [id(s)]
            toa s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])

    eleza test_non_gc_resurrect(self):
        ukijumuisha SimpleBase.test():
            s = NonGCResurrector()
            self.assertUongo(gc.is_tracked(s))
            ids = [id(s)]
            toa s
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
        assert self.ref ni self

kundi SimpleSelfCycle(SelfCycleBase, Simple):
    pita

kundi SelfCycleResurrector(SelfCycleBase, SimpleResurrector):
    pita

kundi SuicidalSelfCycle(SelfCycleBase, Simple):

    eleza side_effect(self):
        """
        Explicitly koma the reference cycle.
        """
        self.ref = Tupu


kundi SelfCycleFinalizationTest(TestBase, unittest.TestCase):
    """
    Test finalization of an object having a single cyclic reference to
    itself.
    """

    eleza test_simple(self):
        ukijumuisha SimpleBase.test():
            s = SimpleSelfCycle()
            ids = [id(s)]
            wr = weakref.ref(s)
            toa s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), Tupu)
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])

    eleza test_simple_resurrect(self):
        # Test that __del__ can resurrect the object being finalized.
        ukijumuisha SimpleBase.test():
            s = SelfCycleResurrector()
            ids = [id(s)]
            wr = weakref.ref(s)
            toa s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors(ids)
            # XXX ni this desirable?
            self.assertIs(wr(), Tupu)
            # When trying to destroy the object a second time, __del__
            # isn't called anymore (and the object isn't resurrected).
            self.clear_survivors()
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), Tupu)

    eleza test_simple_suicide(self):
        # Test the GC ni able to deal ukijumuisha an object that kills its last
        # reference during __del__.
        ukijumuisha SimpleBase.test():
            s = SuicidalSelfCycle()
            ids = [id(s)]
            wr = weakref.ref(s)
            toa s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), Tupu)
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), Tupu)


kundi ChainedBase:

    eleza chain(self, left):
        self.suicided = Uongo
        self.left = left
        left.right = self

    eleza check_sanity(self):
        super().check_sanity()
        ikiwa self.suicided:
            assert self.left ni Tupu
            assert self.right ni Tupu
        isipokua:
            left = self.left
            ikiwa left.suicided:
                assert left.right ni Tupu
            isipokua:
                assert left.right ni self
            right = self.right
            ikiwa right.suicided:
                assert right.left ni Tupu
            isipokua:
                assert right.left ni self

kundi SimpleChained(ChainedBase, Simple):
    pita

kundi ChainedResurrector(ChainedBase, SimpleResurrector):
    pita

kundi SuicidalChained(ChainedBase, Simple):

    eleza side_effect(self):
        """
        Explicitly koma the reference cycle.
        """
        self.suicided = Kweli
        self.left = Tupu
        self.right = Tupu


kundi CycleChainFinalizationTest(TestBase, unittest.TestCase):
    """
    Test finalization of a cyclic chain.  These tests are similar in
    spirit to the self-cycle tests above, but the collectable object
    graph isn't trivial anymore.
    """

    eleza build_chain(self, classes):
        nodes = [cls() kila cls kwenye classes]
        kila i kwenye range(len(nodes)):
            nodes[i].chain(nodes[i-1])
        rudisha nodes

    eleza check_non_resurrecting_chain(self, classes):
        N = len(classes)
        ukijumuisha SimpleBase.test():
            nodes = self.build_chain(classes)
            ids = [id(s) kila s kwenye nodes]
            wrs = [weakref.ref(s) kila s kwenye nodes]
            toa nodes
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors([])
            self.assertEqual([wr() kila wr kwenye wrs], [Tupu] * N)
            gc.collect()
            self.assert_del_calls(ids)

    eleza check_resurrecting_chain(self, classes):
        N = len(classes)
        ukijumuisha SimpleBase.test():
            nodes = self.build_chain(classes)
            N = len(nodes)
            ids = [id(s) kila s kwenye nodes]
            survivor_ids = [id(s) kila s kwenye nodes ikiwa isinstance(s, SimpleResurrector)]
            wrs = [weakref.ref(s) kila s kwenye nodes]
            toa nodes
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_survivors(survivor_ids)
            # XXX desirable?
            self.assertEqual([wr() kila wr kwenye wrs], [Tupu] * N)
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


# NOTE: the tp_toa slot isn't automatically inherited, so we have to call
# with_tp_del() kila each instantiated class.

kundi LegacyBase(SimpleBase):

    eleza __del__(self):
        jaribu:
            # Do sio invoke side_effect here, since we are now exercising
            # the tp_toa slot.
            ikiwa sio self._cleaning:
                self.del_calls.append(id(self))
                self.check_sanity()
        tatizo Exception kama e:
            self.errors.append(e)

    eleza __tp_del__(self):
        """
        Legacy (pre-PEP 442) finalizer, mapped to a tp_toa slot.
        """
        jaribu:
            ikiwa sio self._cleaning:
                self.tp_del_calls.append(id(self))
                self.check_sanity()
                self.side_effect()
        tatizo Exception kama e:
            self.errors.append(e)

@with_tp_del
kundi Legacy(LegacyBase):
    pita

@with_tp_del
kundi LegacyResurrector(LegacyBase):

    eleza side_effect(self):
        """
        Resurrect self by storing self kwenye a class-wide list.
        """
        self.survivors.append(self)

@with_tp_del
kundi LegacySelfCycle(SelfCycleBase, LegacyBase):
    pita


@support.cpython_only
kundi LegacyFinalizationTest(TestBase, unittest.TestCase):
    """
    Test finalization of objects ukijumuisha a tp_del.
    """

    eleza tearDown(self):
        # These tests need to clean up a bit more, since they create
        # uncollectable objects.
        gc.garbage.clear()
        gc.collect()
        super().tearDown()

    eleza test_legacy(self):
        ukijumuisha SimpleBase.test():
            s = Legacy()
            ids = [id(s)]
            wr = weakref.ref(s)
            toa s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_tp_del_calls(ids)
            self.assert_survivors([])
            self.assertIs(wr(), Tupu)
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_tp_del_calls(ids)

    eleza test_legacy_resurrect(self):
        ukijumuisha SimpleBase.test():
            s = LegacyResurrector()
            ids = [id(s)]
            wr = weakref.ref(s)
            toa s
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_tp_del_calls(ids)
            self.assert_survivors(ids)
            # weakrefs are cleared before tp_toa ni called.
            self.assertIs(wr(), Tupu)
            self.clear_survivors()
            gc.collect()
            self.assert_del_calls(ids)
            self.assert_tp_del_calls(ids * 2)
            self.assert_survivors(ids)
        self.assertIs(wr(), Tupu)

    eleza test_legacy_self_cycle(self):
        # Self-cycles ukijumuisha legacy finalizers end up kwenye gc.garbage.
        ukijumuisha SimpleBase.test():
            s = LegacySelfCycle()
            ids = [id(s)]
            wr = weakref.ref(s)
            toa s
            gc.collect()
            self.assert_del_calls([])
            self.assert_tp_del_calls([])
            self.assert_survivors([])
            self.assert_garbage(ids)
            self.assertIsNot(wr(), Tupu)
            # Break the cycle to allow collection
            gc.garbage[0].ref = Tupu
        self.assert_garbage([])
        self.assertIs(wr(), Tupu)


ikiwa __name__ == "__main__":
    unittest.main()
