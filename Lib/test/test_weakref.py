agiza gc
agiza sys
agiza unittest
agiza collections
agiza weakref
agiza operator
agiza contextlib
agiza copy
agiza threading
agiza time
agiza random

kutoka test agiza support
kutoka test.support agiza script_helper

# Used kwenye ReferencesTestCase.test_ref_created_during_del() .
ref_kutoka_toa = Tupu

# Used by FinalizeTestCase kama a global that may be replaced by Tupu
# when the interpreter shuts down.
_global_var = 'foobar'

kundi C:
    eleza method(self):
        pita


kundi Callable:
    bar = Tupu

    eleza __call__(self, x):
        self.bar = x


eleza create_function():
    eleza f(): pita
    rudisha f

eleza create_bound_method():
    rudisha C().method


kundi Object:
    eleza __init__(self, arg):
        self.arg = arg
    eleza __repr__(self):
        rudisha "<Object %r>" % self.arg
    eleza __eq__(self, other):
        ikiwa isinstance(other, Object):
            rudisha self.arg == other.arg
        rudisha NotImplemented
    eleza __lt__(self, other):
        ikiwa isinstance(other, Object):
            rudisha self.arg < other.arg
        rudisha NotImplemented
    eleza __hash__(self):
        rudisha hash(self.arg)
    eleza some_method(self):
        rudisha 4
    eleza other_method(self):
        rudisha 5


kundi RefCycle:
    eleza __init__(self):
        self.cycle = self


kundi TestBase(unittest.TestCase):

    eleza setUp(self):
        self.cbcalled = 0

    eleza callback(self, ref):
        self.cbcalled += 1


@contextlib.contextmanager
eleza collect_in_thread(period=0.0001):
    """
    Ensure GC collections happen kwenye a different thread, at a high frequency.
    """
    please_stop = Uongo

    eleza collect():
        wakati sio please_stop:
            time.sleep(period)
            gc.collect()

    with support.disable_gc():
        t = threading.Thread(target=collect)
        t.start()
        jaribu:
            tuma
        mwishowe:
            please_stop = Kweli
            t.join()


kundi ReferencesTestCase(TestBase):

    eleza test_basic_ref(self):
        self.check_basic_ref(C)
        self.check_basic_ref(create_function)
        self.check_basic_ref(create_bound_method)

        # Just make sure the tp_repr handler doesn't ashiria an exception.
        # Live reference:
        o = C()
        wr = weakref.ref(o)
        repr(wr)
        # Dead reference:
        toa o
        repr(wr)

    eleza test_basic_callback(self):
        self.check_basic_callback(C)
        self.check_basic_callback(create_function)
        self.check_basic_callback(create_bound_method)

    @support.cpython_only
    eleza test_cfunction(self):
        agiza _testcapi
        create_cfunction = _testcapi.create_cfunction
        f = create_cfunction()
        wr = weakref.ref(f)
        self.assertIs(wr(), f)
        toa f
        self.assertIsTupu(wr())
        self.check_basic_ref(create_cfunction)
        self.check_basic_callback(create_cfunction)

    eleza test_multiple_callbacks(self):
        o = C()
        ref1 = weakref.ref(o, self.callback)
        ref2 = weakref.ref(o, self.callback)
        toa o
        self.assertIsTupu(ref1(), "expected reference to be invalidated")
        self.assertIsTupu(ref2(), "expected reference to be invalidated")
        self.assertEqual(self.cbcalled, 2,
                     "callback sio called the right number of times")

    eleza test_multiple_selfref_callbacks(self):
        # Make sure all references are invalidated before callbacks are called
        #
        # What's agizaant here ni that we're using the first
        # reference kwenye the callback invoked on the second reference
        # (the most recently created ref ni cleaned up first).  This
        # tests that all references to the object are invalidated
        # before any of the callbacks are invoked, so that we only
        # have one invocation of _weakref.c:cleanup_helper() active
        # kila a particular object at a time.
        #
        eleza callback(object, self=self):
            self.ref()
        c = C()
        self.ref = weakref.ref(c, callback)
        ref1 = weakref.ref(c, callback)
        toa c

    eleza test_constructor_kwargs(self):
        c = C()
        self.assertRaises(TypeError, weakref.ref, c, callback=Tupu)

    eleza test_proxy_ref(self):
        o = C()
        o.bar = 1
        ref1 = weakref.proxy(o, self.callback)
        ref2 = weakref.proxy(o, self.callback)
        toa o

        eleza check(proxy):
            proxy.bar

        self.assertRaises(ReferenceError, check, ref1)
        self.assertRaises(ReferenceError, check, ref2)
        self.assertRaises(ReferenceError, bool, weakref.proxy(C()))
        self.assertEqual(self.cbcalled, 2)

    eleza check_basic_ref(self, factory):
        o = factory()
        ref = weakref.ref(o)
        self.assertIsNotTupu(ref(),
                     "weak reference to live object should be live")
        o2 = ref()
        self.assertIs(o, o2,
                     "<ref>() should rudisha original object ikiwa live")

    eleza check_basic_callback(self, factory):
        self.cbcalled = 0
        o = factory()
        ref = weakref.ref(o, self.callback)
        toa o
        self.assertEqual(self.cbcalled, 1,
                     "callback did sio properly set 'cbcalled'")
        self.assertIsTupu(ref(),
                     "ref2 should be dead after deleting object reference")

    eleza test_ref_reuse(self):
        o = C()
        ref1 = weakref.ref(o)
        # create a proxy to make sure that there's an intervening creation
        # between these two; it should make no difference
        proxy = weakref.proxy(o)
        ref2 = weakref.ref(o)
        self.assertIs(ref1, ref2,
                     "reference object w/out callback should be re-used")

        o = C()
        proxy = weakref.proxy(o)
        ref1 = weakref.ref(o)
        ref2 = weakref.ref(o)
        self.assertIs(ref1, ref2,
                     "reference object w/out callback should be re-used")
        self.assertEqual(weakref.getweakrefcount(o), 2,
                     "wrong weak ref count kila object")
        toa proxy
        self.assertEqual(weakref.getweakrefcount(o), 1,
                     "wrong weak ref count kila object after deleting proxy")

    eleza test_proxy_reuse(self):
        o = C()
        proxy1 = weakref.proxy(o)
        ref = weakref.ref(o)
        proxy2 = weakref.proxy(o)
        self.assertIs(proxy1, proxy2,
                     "proxy object w/out callback should have been re-used")

    eleza test_basic_proxy(self):
        o = C()
        self.check_proxy(o, weakref.proxy(o))

        L = collections.UserList()
        p = weakref.proxy(L)
        self.assertUongo(p, "proxy kila empty UserList should be false")
        p.append(12)
        self.assertEqual(len(L), 1)
        self.assertKweli(p, "proxy kila non-empty UserList should be true")
        p[:] = [2, 3]
        self.assertEqual(len(L), 2)
        self.assertEqual(len(p), 2)
        self.assertIn(3, p, "proxy didn't support __contains__() properly")
        p[1] = 5
        self.assertEqual(L[1], 5)
        self.assertEqual(p[1], 5)
        L2 = collections.UserList(L)
        p2 = weakref.proxy(L2)
        self.assertEqual(p, p2)
        ## self.assertEqual(repr(L2), repr(p2))
        L3 = collections.UserList(range(10))
        p3 = weakref.proxy(L3)
        self.assertEqual(L3[:], p3[:])
        self.assertEqual(L3[5:], p3[5:])
        self.assertEqual(L3[:5], p3[:5])
        self.assertEqual(L3[2:5], p3[2:5])

    eleza test_proxy_unicode(self):
        # See bug 5037
        kundi C(object):
            eleza __str__(self):
                rudisha "string"
            eleza __bytes__(self):
                rudisha b"bytes"
        instance = C()
        self.assertIn("__bytes__", dir(weakref.proxy(instance)))
        self.assertEqual(bytes(weakref.proxy(instance)), b"bytes")

    eleza test_proxy_index(self):
        kundi C:
            eleza __index__(self):
                rudisha 10
        o = C()
        p = weakref.proxy(o)
        self.assertEqual(operator.index(p), 10)

    eleza test_proxy_div(self):
        kundi C:
            eleza __floordiv__(self, other):
                rudisha 42
            eleza __ifloordiv__(self, other):
                rudisha 21
        o = C()
        p = weakref.proxy(o)
        self.assertEqual(p // 5, 42)
        p //= 5
        self.assertEqual(p, 21)

    eleza test_proxy_matmul(self):
        kundi C:
            eleza __matmul__(self, other):
                rudisha 1729
            eleza __rmatmul__(self, other):
                rudisha -163
            eleza __imatmul__(self, other):
                rudisha 561
        o = C()
        p = weakref.proxy(o)
        self.assertEqual(p @ 5, 1729)
        self.assertEqual(5 @ p, -163)
        p @= 5
        self.assertEqual(p, 561)

    # The PyWeakref_* C API ni documented kama allowing either NULL or
    # Tupu kama the value kila the callback, where either means "no
    # callback".  The "no callback" ref na proxy objects are supposed
    # to be shared so long kama they exist by all callers so long as
    # they are active.  In Python 2.3.3 na earlier, this guarantee
    # was sio honored, na was broken kwenye different ways for
    # PyWeakref_NewRef() na PyWeakref_NewProxy().  (Two tests.)

    eleza test_shared_ref_without_callback(self):
        self.check_shared_without_callback(weakref.ref)

    eleza test_shared_proxy_without_callback(self):
        self.check_shared_without_callback(weakref.proxy)

    eleza check_shared_without_callback(self, makeref):
        o = Object(1)
        p1 = makeref(o, Tupu)
        p2 = makeref(o, Tupu)
        self.assertIs(p1, p2, "both callbacks were Tupu kwenye the C API")
        toa p1, p2
        p1 = makeref(o)
        p2 = makeref(o, Tupu)
        self.assertIs(p1, p2, "callbacks were NULL, Tupu kwenye the C API")
        toa p1, p2
        p1 = makeref(o)
        p2 = makeref(o)
        self.assertIs(p1, p2, "both callbacks were NULL kwenye the C API")
        toa p1, p2
        p1 = makeref(o, Tupu)
        p2 = makeref(o)
        self.assertIs(p1, p2, "callbacks were Tupu, NULL kwenye the C API")

    eleza test_callable_proxy(self):
        o = Callable()
        ref1 = weakref.proxy(o)

        self.check_proxy(o, ref1)

        self.assertIs(type(ref1), weakref.CallableProxyType,
                     "proxy ni sio of callable type")
        ref1('twinkies!')
        self.assertEqual(o.bar, 'twinkies!',
                     "call through proxy sio pitaed through to original")
        ref1(x='Splat.')
        self.assertEqual(o.bar, 'Splat.',
                     "call through proxy sio pitaed through to original")

        # expect due to too few args
        self.assertRaises(TypeError, ref1)

        # expect due to too many args
        self.assertRaises(TypeError, ref1, 1, 2, 3)

    eleza check_proxy(self, o, proxy):
        o.foo = 1
        self.assertEqual(proxy.foo, 1,
                     "proxy does sio reflect attribute addition")
        o.foo = 2
        self.assertEqual(proxy.foo, 2,
                     "proxy does sio reflect attribute modification")
        toa o.foo
        self.assertUongo(hasattr(proxy, 'foo'),
                     "proxy does sio reflect attribute removal")

        proxy.foo = 1
        self.assertEqual(o.foo, 1,
                     "object does sio reflect attribute addition via proxy")
        proxy.foo = 2
        self.assertEqual(o.foo, 2,
            "object does sio reflect attribute modification via proxy")
        toa proxy.foo
        self.assertUongo(hasattr(o, 'foo'),
                     "object does sio reflect attribute removal via proxy")

    eleza test_proxy_deletion(self):
        # Test clearing of SF bug #762891
        kundi Foo:
            result = Tupu
            eleza __delitem__(self, accessor):
                self.result = accessor
        g = Foo()
        f = weakref.proxy(g)
        toa f[0]
        self.assertEqual(f.result, 0)

    eleza test_proxy_bool(self):
        # Test clearing of SF bug #1170766
        kundi List(list): pita
        lyst = List()
        self.assertEqual(bool(weakref.proxy(lyst)), bool(lyst))

    eleza test_proxy_iter(self):
        # Test fails with a debug build of the interpreter
        # (see bpo-38395).

        obj = Tupu

        kundi MyObj:
            eleza __iter__(self):
                nonlocal obj
                toa obj
                rudisha NotImplemented

        obj = MyObj()
        p = weakref.proxy(obj)
        with self.assertRaises(TypeError):
            # "blech" kwenye p calls MyObj.__iter__ through the proxy,
            # without keeping a reference to the real object, so it
            # can be killed kwenye the middle of the call
            "blech" kwenye p

    eleza test_getweakrefcount(self):
        o = C()
        ref1 = weakref.ref(o)
        ref2 = weakref.ref(o, self.callback)
        self.assertEqual(weakref.getweakrefcount(o), 2,
                     "got wrong number of weak reference objects")

        proxy1 = weakref.proxy(o)
        proxy2 = weakref.proxy(o, self.callback)
        self.assertEqual(weakref.getweakrefcount(o), 4,
                     "got wrong number of weak reference objects")

        toa ref1, ref2, proxy1, proxy2
        self.assertEqual(weakref.getweakrefcount(o), 0,
                     "weak reference objects sio unlinked kutoka"
                     " referent when discarded.")

        # assumes ints do sio support weakrefs
        self.assertEqual(weakref.getweakrefcount(1), 0,
                     "got wrong number of weak reference objects kila int")

    eleza test_getweakrefs(self):
        o = C()
        ref1 = weakref.ref(o, self.callback)
        ref2 = weakref.ref(o, self.callback)
        toa ref1
        self.assertEqual(weakref.getweakrefs(o), [ref2],
                     "list of refs does sio match")

        o = C()
        ref1 = weakref.ref(o, self.callback)
        ref2 = weakref.ref(o, self.callback)
        toa ref2
        self.assertEqual(weakref.getweakrefs(o), [ref1],
                     "list of refs does sio match")

        toa ref1
        self.assertEqual(weakref.getweakrefs(o), [],
                     "list of refs sio cleared")

        # assumes ints do sio support weakrefs
        self.assertEqual(weakref.getweakrefs(1), [],
                     "list of refs does sio match kila int")

    eleza test_newstyle_number_ops(self):
        kundi F(float):
            pita
        f = F(2.0)
        p = weakref.proxy(f)
        self.assertEqual(p + 1.0, 3.0)
        self.assertEqual(1.0 + p, 3.0)  # this used to SEGV

    eleza test_callbacks_protected(self):
        # Callbacks protected kutoka already-set exceptions?
        # Regression test kila SF bug #478534.
        kundi BogusError(Exception):
            pita
        data = {}
        eleza remove(k):
            toa data[k]
        eleza encapsulate():
            f = lambda : ()
            data[weakref.ref(f, remove)] = Tupu
            ashiria BogusError
        jaribu:
            encapsulate()
        tatizo BogusError:
            pita
        isipokua:
            self.fail("exception sio properly restored")
        jaribu:
            encapsulate()
        tatizo BogusError:
            pita
        isipokua:
            self.fail("exception sio properly restored")

    eleza test_sf_bug_840829(self):
        # "weakref callbacks na gc corrupt memory"
        # subtype_dealloc erroneously exposed a new-style instance
        # already kwenye the process of getting deallocated to gc,
        # causing double-deallocation ikiwa the instance had a weakref
        # callback that triggered gc.
        # If the bug exists, there probably won't be an obvious symptom
        # kwenye a release build.  In a debug build, a segfault will occur
        # when the second attempt to remove the instance kutoka the "list
        # of all objects" occurs.

        agiza gc

        kundi C(object):
            pita

        c = C()
        wr = weakref.ref(c, lambda ignore: gc.collect())
        toa c

        # There endeth the first part.  It gets worse.
        toa wr

        c1 = C()
        c1.i = C()
        wr = weakref.ref(c1.i, lambda ignore: gc.collect())

        c2 = C()
        c2.c1 = c1
        toa c1  # still alive because c2 points to it

        # Now when subtype_dealloc gets called on c2, it's sio enough just
        # that c2 ni immune kutoka gc wakati the weakref callbacks associated
        # with c2 execute (there are none kwenye this 2nd half of the test, btw).
        # subtype_dealloc goes on to call the base classes' deallocs too,
        # so any gc triggered by weakref callbacks associated with anything
        # torn down by a base kundi dealloc can also trigger double
        # deallocation of c2.
        toa c2

    eleza test_callback_in_cycle_1(self):
        agiza gc

        kundi J(object):
            pita

        kundi II(object):
            eleza acallback(self, ignore):
                self.J

        I = II()
        I.J = J
        I.wr = weakref.ref(J, I.acallback)

        # Now J na II are each kwenye a self-cycle (as all new-style class
        # objects are, since their __mro__ points back to them).  I holds
        # both a weak reference (I.wr) na a strong reference (I.J) to class
        # J.  I ni also kwenye a cycle (I.wr points to a weakref that references
        # I.acallback).  When we toa these three, they all become trash, but
        # the cycles prevent any of them kutoka getting cleaned up immediately.
        # Instead they have to wait kila cyclic gc to deduce that they're
        # trash.
        #
        # gc used to call tp_clear on all of them, na the order kwenye which
        # it does that ni pretty accidental.  The exact order kwenye which we
        # built up these things manages to provoke gc into running tp_clear
        # kwenye just the right order (I last).  Calling tp_clear on II leaves
        # behind an insane kundi object (its __mro__ becomes NULL).  Calling
        # tp_clear on J komas its self-cycle, but J doesn't get deleted
        # just then because of the strong reference kutoka I.J.  Calling
        # tp_clear on I starts to clear I's __dict__, na just happens to
        # clear I.J first -- I.wr ni still intact.  That removes the last
        # reference to J, which triggers the weakref callback.  The callback
        # tries to do "self.J", na instances of new-style classes look up
        # attributes ("J") kwenye the kundi dict first.  The kundi (II) wants to
        # search II.__mro__, but that's NULL.   The result was a segfault in
        # a release build, na an assert failure kwenye a debug build.
        toa I, J, II
        gc.collect()

    eleza test_callback_in_cycle_2(self):
        agiza gc

        # This ni just like test_callback_in_cycle_1, tatizo that II ni an
        # old-style class.  The symptom ni different then:  an instance of an
        # old-style kundi looks kwenye its own __dict__ first.  'J' happens to
        # get cleared kutoka I.__dict__ before 'wr', na 'J' was never kwenye II's
        # __dict__, so the attribute isn't found.  The difference ni that
        # the old-style II doesn't have a NULL __mro__ (it doesn't have any
        # __mro__), so no segfault occurs.  Instead it got:
        #    test_callback_in_cycle_2 (__main__.ReferencesTestCase) ...
        #    Exception exceptions.AttributeError:
        #   "II instance has no attribute 'J'" kwenye <bound method II.acallback
        #       of <?.II instance at 0x00B9B4B8>> ignored

        kundi J(object):
            pita

        kundi II:
            eleza acallback(self, ignore):
                self.J

        I = II()
        I.J = J
        I.wr = weakref.ref(J, I.acallback)

        toa I, J, II
        gc.collect()

    eleza test_callback_in_cycle_3(self):
        agiza gc

        # This one broke the first patch that fixed the last two.  In this
        # case, the objects reachable kutoka the callback aren't also reachable
        # kutoka the object (c1) *triggering* the callback:  you can get to
        # c1 kutoka c2, but sio vice-versa.  The result was that c2's __dict__
        # got tp_clear'ed by the time the c2.cb callback got invoked.

        kundi C:
            eleza cb(self, ignore):
                self.me
                self.c1
                self.wr

        c1, c2 = C(), C()

        c2.me = c2
        c2.c1 = c1
        c2.wr = weakref.ref(c1, c2.cb)

        toa c1, c2
        gc.collect()

    eleza test_callback_in_cycle_4(self):
        agiza gc

        # Like test_callback_in_cycle_3, tatizo c2 na c1 have different
        # classes.  c2's kundi (C) isn't reachable kutoka c1 then, so protecting
        # objects reachable kutoka the dying object (c1) isn't enough to stop
        # c2's kundi (C) kutoka getting tp_clear'ed before c2.cb ni invoked.
        # The result was a segfault (C.__mro__ was NULL when the callback
        # tried to look up self.me).

        kundi C(object):
            eleza cb(self, ignore):
                self.me
                self.c1
                self.wr

        kundi D:
            pita

        c1, c2 = D(), C()

        c2.me = c2
        c2.c1 = c1
        c2.wr = weakref.ref(c1, c2.cb)

        toa c1, c2, C, D
        gc.collect()

    @support.requires_type_collecting
    eleza test_callback_in_cycle_resurrection(self):
        agiza gc

        # Do something nasty kwenye a weakref callback:  resurrect objects
        # kutoka dead cycles.  For this to be attempted, the weakref and
        # its callback must also be part of the cyclic trash (else the
        # objects reachable via the callback couldn't be kwenye cyclic trash
        # to begin with -- the callback would act like an external root).
        # But gc clears trash weakrefs with callbacks early now, which
        # disables the callbacks, so the callbacks shouldn't get called
        # at all (and so nothing actually gets resurrected).

        alist = []
        kundi C(object):
            eleza __init__(self, value):
                self.attribute = value

            eleza acallback(self, ignore):
                alist.append(self.c)

        c1, c2 = C(1), C(2)
        c1.c = c2
        c2.c = c1
        c1.wr = weakref.ref(c2, c1.acallback)
        c2.wr = weakref.ref(c1, c2.acallback)

        eleza C_went_away(ignore):
            alist.append("C went away")
        wr = weakref.ref(C, C_went_away)

        toa c1, c2, C   # make them all trash
        self.assertEqual(alist, [])  # toa isn't enough to reclaim anything

        gc.collect()
        # c1.wr na c2.wr were part of the cyclic trash, so should have
        # been cleared without their callbacks executing.  OTOH, the weakref
        # to C ni bound to a function local (wr), na wasn't trash, so that
        # callback should have been invoked when C went away.
        self.assertEqual(alist, ["C went away"])
        # The remaining weakref should be dead now (its callback ran).
        self.assertEqual(wr(), Tupu)

        toa alist[:]
        gc.collect()
        self.assertEqual(alist, [])

    eleza test_callbacks_on_callback(self):
        agiza gc

        # Set up weakref callbacks *on* weakref callbacks.
        alist = []
        eleza safe_callback(ignore):
            alist.append("safe_callback called")

        kundi C(object):
            eleza cb(self, ignore):
                alist.append("cb called")

        c, d = C(), C()
        c.other = d
        d.other = c
        callback = c.cb
        c.wr = weakref.ref(d, callback)     # this won't trigger
        d.wr = weakref.ref(callback, d.cb)  # ditto
        external_wr = weakref.ref(callback, safe_callback)  # but this will
        self.assertIs(external_wr(), callback)

        # The weakrefs attached to c na d should get cleared, so that
        # C.cb ni never called.  But external_wr isn't part of the cyclic
        # trash, na no cyclic trash ni reachable kutoka it, so safe_callback
        # should get invoked when the bound method object callback (c.cb)
        # -- which ni itself a callback, na also part of the cyclic trash --
        # gets reclaimed at the end of gc.

        toa callback, c, d, C
        self.assertEqual(alist, [])  # toa isn't enough to clean up cycles
        gc.collect()
        self.assertEqual(alist, ["safe_callback called"])
        self.assertEqual(external_wr(), Tupu)

        toa alist[:]
        gc.collect()
        self.assertEqual(alist, [])

    eleza test_gc_during_ref_creation(self):
        self.check_gc_during_creation(weakref.ref)

    eleza test_gc_during_proxy_creation(self):
        self.check_gc_during_creation(weakref.proxy)

    eleza check_gc_during_creation(self, makeref):
        thresholds = gc.get_threshold()
        gc.set_threshold(1, 1, 1)
        gc.collect()
        kundi A:
            pita

        eleza callback(*args):
            pita

        referenced = A()

        a = A()
        a.a = a
        a.wr = makeref(referenced)

        jaribu:
            # now make sure the object na the ref get labeled as
            # cyclic trash:
            a = A()
            weakref.ref(referenced, callback)

        mwishowe:
            gc.set_threshold(*thresholds)

    eleza test_ref_created_during_del(self):
        # Bug #1377858
        # A weakref created kwenye an object's __del__() would crash the
        # interpreter when the weakref was cleaned up since it would refer to
        # non-existent memory.  This test should sio segfault the interpreter.
        kundi Target(object):
            eleza __del__(self):
                global ref_kutoka_del
                ref_kutoka_toa = weakref.ref(self)

        w = Target()

    eleza test_init(self):
        # Issue 3634
        # <weakref to class>.__init__() doesn't check errors correctly
        r = weakref.ref(Exception)
        self.assertRaises(TypeError, r.__init__, 0, 0, 0, 0, 0)
        # No exception should be ashiriad here
        gc.collect()

    eleza test_classes(self):
        # Check that classes are weakrefable.
        kundi A(object):
            pita
        l = []
        weakref.ref(int)
        a = weakref.ref(A, l.append)
        A = Tupu
        gc.collect()
        self.assertEqual(a(), Tupu)
        self.assertEqual(l, [a])

    eleza test_equality(self):
        # Alive weakrefs defer equality testing to their underlying object.
        x = Object(1)
        y = Object(1)
        z = Object(2)
        a = weakref.ref(x)
        b = weakref.ref(y)
        c = weakref.ref(z)
        d = weakref.ref(x)
        # Note how we directly test the operators here, to stress both
        # __eq__ na __ne__.
        self.assertKweli(a == b)
        self.assertUongo(a != b)
        self.assertUongo(a == c)
        self.assertKweli(a != c)
        self.assertKweli(a == d)
        self.assertUongo(a != d)
        toa x, y, z
        gc.collect()
        kila r kwenye a, b, c:
            # Sanity check
            self.assertIs(r(), Tupu)
        # Dead weakrefs compare by identity: whether `a` na `d` are the
        # same weakref object ni an implementation detail, since they pointed
        # to the same original object na didn't have a callback.
        # (see issue #16453).
        self.assertUongo(a == b)
        self.assertKweli(a != b)
        self.assertUongo(a == c)
        self.assertKweli(a != c)
        self.assertEqual(a == d, a ni d)
        self.assertEqual(a != d, a ni sio d)

    eleza test_ordering(self):
        # weakrefs cannot be ordered, even ikiwa the underlying objects can.
        ops = [operator.lt, operator.gt, operator.le, operator.ge]
        x = Object(1)
        y = Object(1)
        a = weakref.ref(x)
        b = weakref.ref(y)
        kila op kwenye ops:
            self.assertRaises(TypeError, op, a, b)
        # Same when dead.
        toa x, y
        gc.collect()
        kila op kwenye ops:
            self.assertRaises(TypeError, op, a, b)

    eleza test_hashing(self):
        # Alive weakrefs hash the same kama the underlying object
        x = Object(42)
        y = Object(42)
        a = weakref.ref(x)
        b = weakref.ref(y)
        self.assertEqual(hash(a), hash(42))
        toa x, y
        gc.collect()
        # Dead weakrefs:
        # - retain their hash ni they were hashed when alive;
        # - otherwise, cannot be hashed.
        self.assertEqual(hash(a), hash(42))
        self.assertRaises(TypeError, hash, b)

    eleza test_trashcan_16602(self):
        # Issue #16602: when a weakref's target was part of a long
        # deallocation chain, the trashcan mechanism could delay clearing
        # of the weakref na make the target object visible kutoka outside
        # code even though its refcount had dropped to 0.  A crash ensued.
        kundi C:
            eleza __init__(self, parent):
                ikiwa sio parent:
                    rudisha
                wself = weakref.ref(self)
                eleza cb(wparent):
                    o = wself()
                self.wparent = weakref.ref(parent, cb)

        d = weakref.WeakKeyDictionary()
        root = c = C(Tupu)
        kila n kwenye range(100):
            d[c] = c = C(c)
        toa root
        gc.collect()

    eleza test_callback_attribute(self):
        x = Object(1)
        callback = lambda ref: Tupu
        ref1 = weakref.ref(x, callback)
        self.assertIs(ref1.__callback__, callback)

        ref2 = weakref.ref(x)
        self.assertIsTupu(ref2.__callback__)

    eleza test_callback_attribute_after_deletion(self):
        x = Object(1)
        ref = weakref.ref(x, self.callback)
        self.assertIsNotTupu(ref.__callback__)
        toa x
        support.gc_collect()
        self.assertIsTupu(ref.__callback__)

    eleza test_set_callback_attribute(self):
        x = Object(1)
        callback = lambda ref: Tupu
        ref1 = weakref.ref(x, callback)
        with self.assertRaises(AttributeError):
            ref1.__callback__ = lambda ref: Tupu

    eleza test_callback_gcs(self):
        kundi ObjectWithDel(Object):
            eleza __del__(self): pita
        x = ObjectWithDel(1)
        ref1 = weakref.ref(x, lambda ref: support.gc_collect())
        toa x
        support.gc_collect()


kundi SubclassableWeakrefTestCase(TestBase):

    eleza test_subclass_refs(self):
        kundi MyRef(weakref.ref):
            eleza __init__(self, ob, callback=Tupu, value=42):
                self.value = value
                super().__init__(ob, callback)
            eleza __call__(self):
                self.called = Kweli
                rudisha super().__call__()
        o = Object("foo")
        mr = MyRef(o, value=24)
        self.assertIs(mr(), o)
        self.assertKweli(mr.called)
        self.assertEqual(mr.value, 24)
        toa o
        self.assertIsTupu(mr())
        self.assertKweli(mr.called)

    eleza test_subclass_refs_dont_replace_standard_refs(self):
        kundi MyRef(weakref.ref):
            pita
        o = Object(42)
        r1 = MyRef(o)
        r2 = weakref.ref(o)
        self.assertIsNot(r1, r2)
        self.assertEqual(weakref.getweakrefs(o), [r2, r1])
        self.assertEqual(weakref.getweakrefcount(o), 2)
        r3 = MyRef(o)
        self.assertEqual(weakref.getweakrefcount(o), 3)
        refs = weakref.getweakrefs(o)
        self.assertEqual(len(refs), 3)
        self.assertIs(r2, refs[0])
        self.assertIn(r1, refs[1:])
        self.assertIn(r3, refs[1:])

    eleza test_subclass_refs_dont_conflate_callbacks(self):
        kundi MyRef(weakref.ref):
            pita
        o = Object(42)
        r1 = MyRef(o, id)
        r2 = MyRef(o, str)
        self.assertIsNot(r1, r2)
        refs = weakref.getweakrefs(o)
        self.assertIn(r1, refs)
        self.assertIn(r2, refs)

    eleza test_subclass_refs_with_slots(self):
        kundi MyRef(weakref.ref):
            __slots__ = "slot1", "slot2"
            eleza __new__(type, ob, callback, slot1, slot2):
                rudisha weakref.ref.__new__(type, ob, callback)
            eleza __init__(self, ob, callback, slot1, slot2):
                self.slot1 = slot1
                self.slot2 = slot2
            eleza meth(self):
                rudisha self.slot1 + self.slot2
        o = Object(42)
        r = MyRef(o, Tupu, "abc", "def")
        self.assertEqual(r.slot1, "abc")
        self.assertEqual(r.slot2, "def")
        self.assertEqual(r.meth(), "abcdef")
        self.assertUongo(hasattr(r, "__dict__"))

    eleza test_subclass_refs_with_cycle(self):
        """Confirm https://bugs.python.org/issue3100 ni fixed."""
        # An instance of a weakref subkundi can have attributes.
        # If such a weakref holds the only strong reference to the object,
        # deleting the weakref will delete the object. In this case,
        # the callback must sio be called, because the ref object is
        # being deleted.
        kundi MyRef(weakref.ref):
            pita

        # Use a local callback, kila "regrtest -R::"
        # to detect refcounting problems
        eleza callback(w):
            self.cbcalled += 1

        o = C()
        r1 = MyRef(o, callback)
        r1.o = o
        toa o

        toa r1 # Used to crash here

        self.assertEqual(self.cbcalled, 0)

        # Same test, with two weakrefs to the same object
        # (since code paths are different)
        o = C()
        r1 = MyRef(o, callback)
        r2 = MyRef(o, callback)
        r1.r = r2
        r2.o = o
        toa o
        toa r2

        toa r1 # Used to crash here

        self.assertEqual(self.cbcalled, 0)


kundi WeakMethodTestCase(unittest.TestCase):

    eleza _subclass(self):
        """Return an Object subkundi overriding `some_method`."""
        kundi C(Object):
            eleza some_method(self):
                rudisha 6
        rudisha C

    eleza test_alive(self):
        o = Object(1)
        r = weakref.WeakMethod(o.some_method)
        self.assertIsInstance(r, weakref.ReferenceType)
        self.assertIsInstance(r(), type(o.some_method))
        self.assertIs(r().__self__, o)
        self.assertIs(r().__func__, o.some_method.__func__)
        self.assertEqual(r()(), 4)

    eleza test_object_dead(self):
        o = Object(1)
        r = weakref.WeakMethod(o.some_method)
        toa o
        gc.collect()
        self.assertIs(r(), Tupu)

    eleza test_method_dead(self):
        C = self._subclass()
        o = C(1)
        r = weakref.WeakMethod(o.some_method)
        toa C.some_method
        gc.collect()
        self.assertIs(r(), Tupu)

    eleza test_callback_when_object_dead(self):
        # Test callback behaviour when object dies first.
        C = self._subclass()
        calls = []
        eleza cb(arg):
            calls.append(arg)
        o = C(1)
        r = weakref.WeakMethod(o.some_method, cb)
        toa o
        gc.collect()
        self.assertEqual(calls, [r])
        # Callback ni only called once.
        C.some_method = Object.some_method
        gc.collect()
        self.assertEqual(calls, [r])

    eleza test_callback_when_method_dead(self):
        # Test callback behaviour when method dies first.
        C = self._subclass()
        calls = []
        eleza cb(arg):
            calls.append(arg)
        o = C(1)
        r = weakref.WeakMethod(o.some_method, cb)
        toa C.some_method
        gc.collect()
        self.assertEqual(calls, [r])
        # Callback ni only called once.
        toa o
        gc.collect()
        self.assertEqual(calls, [r])

    @support.cpython_only
    eleza test_no_cycles(self):
        # A WeakMethod doesn't create any reference cycle to itself.
        o = Object(1)
        eleza cb(_):
            pita
        r = weakref.WeakMethod(o.some_method, cb)
        wr = weakref.ref(r)
        toa r
        self.assertIs(wr(), Tupu)

    eleza test_equality(self):
        eleza _eq(a, b):
            self.assertKweli(a == b)
            self.assertUongo(a != b)
        eleza _ne(a, b):
            self.assertKweli(a != b)
            self.assertUongo(a == b)
        x = Object(1)
        y = Object(1)
        a = weakref.WeakMethod(x.some_method)
        b = weakref.WeakMethod(y.some_method)
        c = weakref.WeakMethod(x.other_method)
        d = weakref.WeakMethod(y.other_method)
        # Objects equal, same method
        _eq(a, b)
        _eq(c, d)
        # Objects equal, different method
        _ne(a, c)
        _ne(a, d)
        _ne(b, c)
        _ne(b, d)
        # Objects unequal, same ama different method
        z = Object(2)
        e = weakref.WeakMethod(z.some_method)
        f = weakref.WeakMethod(z.other_method)
        _ne(a, e)
        _ne(a, f)
        _ne(b, e)
        _ne(b, f)
        toa x, y, z
        gc.collect()
        # Dead WeakMethods compare by identity
        refs = a, b, c, d, e, f
        kila q kwenye refs:
            kila r kwenye refs:
                self.assertEqual(q == r, q ni r)
                self.assertEqual(q != r, q ni sio r)

    eleza test_hashing(self):
        # Alive WeakMethods are hashable ikiwa the underlying object is
        # hashable.
        x = Object(1)
        y = Object(1)
        a = weakref.WeakMethod(x.some_method)
        b = weakref.WeakMethod(y.some_method)
        c = weakref.WeakMethod(y.other_method)
        # Since WeakMethod objects are equal, the hashes should be equal.
        self.assertEqual(hash(a), hash(b))
        ha = hash(a)
        # Dead WeakMethods retain their old hash value
        toa x, y
        gc.collect()
        self.assertEqual(hash(a), ha)
        self.assertEqual(hash(b), ha)
        # If it wasn't hashed when alive, a dead WeakMethod cannot be hashed.
        self.assertRaises(TypeError, hash, c)


kundi MappingTestCase(TestBase):

    COUNT = 10

    eleza check_len_cycles(self, dict_type, cons):
        N = 20
        items = [RefCycle() kila i kwenye range(N)]
        dct = dict_type(cons(o) kila o kwenye items)
        # Keep an iterator alive
        it = dct.items()
        jaribu:
            next(it)
        tatizo StopIteration:
            pita
        toa items
        gc.collect()
        n1 = len(dct)
        toa it
        gc.collect()
        n2 = len(dct)
        # one item may be kept alive inside the iterator
        self.assertIn(n1, (0, 1))
        self.assertEqual(n2, 0)

    eleza test_weak_keyed_len_cycles(self):
        self.check_len_cycles(weakref.WeakKeyDictionary, lambda k: (k, 1))

    eleza test_weak_valued_len_cycles(self):
        self.check_len_cycles(weakref.WeakValueDictionary, lambda k: (1, k))

    eleza check_len_race(self, dict_type, cons):
        # Extended sanity checks kila len() kwenye the face of cyclic collection
        self.addCleanup(gc.set_threshold, *gc.get_threshold())
        kila th kwenye range(1, 100):
            N = 20
            gc.collect(0)
            gc.set_threshold(th, th, th)
            items = [RefCycle() kila i kwenye range(N)]
            dct = dict_type(cons(o) kila o kwenye items)
            toa items
            # All items will be collected at next garbage collection pita
            it = dct.items()
            jaribu:
                next(it)
            tatizo StopIteration:
                pita
            n1 = len(dct)
            toa it
            n2 = len(dct)
            self.assertGreaterEqual(n1, 0)
            self.assertLessEqual(n1, N)
            self.assertGreaterEqual(n2, 0)
            self.assertLessEqual(n2, n1)

    eleza test_weak_keyed_len_race(self):
        self.check_len_race(weakref.WeakKeyDictionary, lambda k: (k, 1))

    eleza test_weak_valued_len_race(self):
        self.check_len_race(weakref.WeakValueDictionary, lambda k: (1, k))

    eleza test_weak_values(self):
        #
        #  This exercises d.copy(), d.items(), d[], toa d[], len(d).
        #
        dict, objects = self.make_weak_valued_dict()
        kila o kwenye objects:
            self.assertEqual(weakref.getweakrefcount(o), 1)
            self.assertIs(o, dict[o.arg],
                         "wrong object rudishaed by weak dict!")
        items1 = list(dict.items())
        items2 = list(dict.copy().items())
        items1.sort()
        items2.sort()
        self.assertEqual(items1, items2,
                     "cloning of weak-valued dictionary did sio work!")
        toa items1, items2
        self.assertEqual(len(dict), self.COUNT)
        toa objects[0]
        self.assertEqual(len(dict), self.COUNT - 1,
                     "deleting object did sio cause dictionary update")
        toa objects, o
        self.assertEqual(len(dict), 0,
                     "deleting the values did sio clear the dictionary")
        # regression on SF bug #447152:
        dict = weakref.WeakValueDictionary()
        self.assertRaises(KeyError, dict.__getitem__, 1)
        dict[2] = C()
        self.assertRaises(KeyError, dict.__getitem__, 2)

    eleza test_weak_keys(self):
        #
        #  This exercises d.copy(), d.items(), d[] = v, d[], toa d[],
        #  len(d), k kwenye d.
        #
        dict, objects = self.make_weak_keyed_dict()
        kila o kwenye objects:
            self.assertEqual(weakref.getweakrefcount(o), 1,
                         "wrong number of weak references to %r!" % o)
            self.assertIs(o.arg, dict[o],
                         "wrong object rudishaed by weak dict!")
        items1 = dict.items()
        items2 = dict.copy().items()
        self.assertEqual(set(items1), set(items2),
                     "cloning of weak-keyed dictionary did sio work!")
        toa items1, items2
        self.assertEqual(len(dict), self.COUNT)
        toa objects[0]
        self.assertEqual(len(dict), (self.COUNT - 1),
                     "deleting object did sio cause dictionary update")
        toa objects, o
        self.assertEqual(len(dict), 0,
                     "deleting the keys did sio clear the dictionary")
        o = Object(42)
        dict[o] = "What ni the meaning of the universe?"
        self.assertIn(o, dict)
        self.assertNotIn(34, dict)

    eleza test_weak_keyed_iters(self):
        dict, objects = self.make_weak_keyed_dict()
        self.check_iters(dict)

        # Test keyrefs()
        refs = dict.keyrefs()
        self.assertEqual(len(refs), len(objects))
        objects2 = list(objects)
        kila wr kwenye refs:
            ob = wr()
            self.assertIn(ob, dict)
            self.assertIn(ob, dict)
            self.assertEqual(ob.arg, dict[ob])
            objects2.remove(ob)
        self.assertEqual(len(objects2), 0)

        # Test iterkeyrefs()
        objects2 = list(objects)
        self.assertEqual(len(list(dict.keyrefs())), len(objects))
        kila wr kwenye dict.keyrefs():
            ob = wr()
            self.assertIn(ob, dict)
            self.assertIn(ob, dict)
            self.assertEqual(ob.arg, dict[ob])
            objects2.remove(ob)
        self.assertEqual(len(objects2), 0)

    eleza test_weak_valued_iters(self):
        dict, objects = self.make_weak_valued_dict()
        self.check_iters(dict)

        # Test valuerefs()
        refs = dict.valuerefs()
        self.assertEqual(len(refs), len(objects))
        objects2 = list(objects)
        kila wr kwenye refs:
            ob = wr()
            self.assertEqual(ob, dict[ob.arg])
            self.assertEqual(ob.arg, dict[ob.arg].arg)
            objects2.remove(ob)
        self.assertEqual(len(objects2), 0)

        # Test itervaluerefs()
        objects2 = list(objects)
        self.assertEqual(len(list(dict.itervaluerefs())), len(objects))
        kila wr kwenye dict.itervaluerefs():
            ob = wr()
            self.assertEqual(ob, dict[ob.arg])
            self.assertEqual(ob.arg, dict[ob.arg].arg)
            objects2.remove(ob)
        self.assertEqual(len(objects2), 0)

    eleza check_iters(self, dict):
        # item iterator:
        items = list(dict.items())
        kila item kwenye dict.items():
            items.remove(item)
        self.assertUongo(items, "items() did sio touch all items")

        # key iterator, via __iter__():
        keys = list(dict.keys())
        kila k kwenye dict:
            keys.remove(k)
        self.assertUongo(keys, "__iter__() did sio touch all keys")

        # key iterator, via iterkeys():
        keys = list(dict.keys())
        kila k kwenye dict.keys():
            keys.remove(k)
        self.assertUongo(keys, "iterkeys() did sio touch all keys")

        # value iterator:
        values = list(dict.values())
        kila v kwenye dict.values():
            values.remove(v)
        self.assertUongo(values,
                     "itervalues() did sio touch all values")

    eleza check_weak_destroy_while_iterating(self, dict, objects, iter_name):
        n = len(dict)
        it = iter(getattr(dict, iter_name)())
        next(it)             # Trigger internal iteration
        # Destroy an object
        toa objects[-1]
        gc.collect()    # just kwenye case
        # We have removed either the first consumed object, ama another one
        self.assertIn(len(list(it)), [len(objects), len(objects) - 1])
        toa it
        # The removal has been committed
        self.assertEqual(len(dict), n - 1)

    eleza check_weak_destroy_and_mutate_while_iterating(self, dict, testcontext):
        # Check that we can explicitly mutate the weak dict without
        # interfering with delayed removal.
        # `testcontext` should create an iterator, destroy one of the
        # weakref'ed objects na then rudisha a new key/value pair corresponding
        # to the destroyed object.
        with testcontext() kama (k, v):
            self.assertNotIn(k, dict)
        with testcontext() kama (k, v):
            self.assertRaises(KeyError, dict.__delitem__, k)
        self.assertNotIn(k, dict)
        with testcontext() kama (k, v):
            self.assertRaises(KeyError, dict.pop, k)
        self.assertNotIn(k, dict)
        with testcontext() kama (k, v):
            dict[k] = v
        self.assertEqual(dict[k], v)
        ddict = copy.copy(dict)
        with testcontext() kama (k, v):
            dict.update(ddict)
        self.assertEqual(dict, ddict)
        with testcontext() kama (k, v):
            dict.clear()
        self.assertEqual(len(dict), 0)

    eleza check_weak_del_and_len_while_iterating(self, dict, testcontext):
        # Check that len() works when both iterating na removing keys
        # explicitly through various means (.pop(), .clear()...), while
        # implicit mutation ni deferred because an iterator ni alive.
        # (each call to testcontext() should schedule one item kila removal
        #  kila this test to work properly)
        o = Object(123456)
        with testcontext():
            n = len(dict)
            # Since underlaying dict ni ordered, first item ni popped
            dict.pop(next(dict.keys()))
            self.assertEqual(len(dict), n - 1)
            dict[o] = o
            self.assertEqual(len(dict), n)
        # last item kwenye objects ni removed kutoka dict kwenye context shutdown
        with testcontext():
            self.assertEqual(len(dict), n - 1)
            # Then, (o, o) ni popped
            dict.popitem()
            self.assertEqual(len(dict), n - 2)
        with testcontext():
            self.assertEqual(len(dict), n - 3)
            toa dict[next(dict.keys())]
            self.assertEqual(len(dict), n - 4)
        with testcontext():
            self.assertEqual(len(dict), n - 5)
            dict.popitem()
            self.assertEqual(len(dict), n - 6)
        with testcontext():
            dict.clear()
            self.assertEqual(len(dict), 0)
        self.assertEqual(len(dict), 0)

    eleza test_weak_keys_destroy_while_iterating(self):
        # Issue #7105: iterators shouldn't crash when a key ni implicitly removed
        dict, objects = self.make_weak_keyed_dict()
        self.check_weak_destroy_while_iterating(dict, objects, 'keys')
        self.check_weak_destroy_while_iterating(dict, objects, 'items')
        self.check_weak_destroy_while_iterating(dict, objects, 'values')
        self.check_weak_destroy_while_iterating(dict, objects, 'keyrefs')
        dict, objects = self.make_weak_keyed_dict()
        @contextlib.contextmanager
        eleza testcontext():
            jaribu:
                it = iter(dict.items())
                next(it)
                # Schedule a key/value kila removal na recreate it
                v = objects.pop().arg
                gc.collect()      # just kwenye case
                tuma Object(v), v
            mwishowe:
                it = Tupu           # should commit all removals
                gc.collect()
        self.check_weak_destroy_and_mutate_while_iterating(dict, testcontext)
        # Issue #21173: len() fragile when keys are both implicitly and
        # explicitly removed.
        dict, objects = self.make_weak_keyed_dict()
        self.check_weak_del_and_len_while_iterating(dict, testcontext)

    eleza test_weak_values_destroy_while_iterating(self):
        # Issue #7105: iterators shouldn't crash when a key ni implicitly removed
        dict, objects = self.make_weak_valued_dict()
        self.check_weak_destroy_while_iterating(dict, objects, 'keys')
        self.check_weak_destroy_while_iterating(dict, objects, 'items')
        self.check_weak_destroy_while_iterating(dict, objects, 'values')
        self.check_weak_destroy_while_iterating(dict, objects, 'itervaluerefs')
        self.check_weak_destroy_while_iterating(dict, objects, 'valuerefs')
        dict, objects = self.make_weak_valued_dict()
        @contextlib.contextmanager
        eleza testcontext():
            jaribu:
                it = iter(dict.items())
                next(it)
                # Schedule a key/value kila removal na recreate it
                k = objects.pop().arg
                gc.collect()      # just kwenye case
                tuma k, Object(k)
            mwishowe:
                it = Tupu           # should commit all removals
                gc.collect()
        self.check_weak_destroy_and_mutate_while_iterating(dict, testcontext)
        dict, objects = self.make_weak_valued_dict()
        self.check_weak_del_and_len_while_iterating(dict, testcontext)

    eleza test_make_weak_keyed_dict_kutoka_dict(self):
        o = Object(3)
        dict = weakref.WeakKeyDictionary({o:364})
        self.assertEqual(dict[o], 364)

    eleza test_make_weak_keyed_dict_kutoka_weak_keyed_dict(self):
        o = Object(3)
        dict = weakref.WeakKeyDictionary({o:364})
        dict2 = weakref.WeakKeyDictionary(dict)
        self.assertEqual(dict[o], 364)

    eleza make_weak_keyed_dict(self):
        dict = weakref.WeakKeyDictionary()
        objects = list(map(Object, range(self.COUNT)))
        kila o kwenye objects:
            dict[o] = o.arg
        rudisha dict, objects

    eleza test_make_weak_valued_dict_kutoka_dict(self):
        o = Object(3)
        dict = weakref.WeakValueDictionary({364:o})
        self.assertEqual(dict[364], o)

    eleza test_make_weak_valued_dict_kutoka_weak_valued_dict(self):
        o = Object(3)
        dict = weakref.WeakValueDictionary({364:o})
        dict2 = weakref.WeakValueDictionary(dict)
        self.assertEqual(dict[364], o)

    eleza test_make_weak_valued_dict_misc(self):
        # errors
        self.assertRaises(TypeError, weakref.WeakValueDictionary.__init__)
        self.assertRaises(TypeError, weakref.WeakValueDictionary, {}, {})
        self.assertRaises(TypeError, weakref.WeakValueDictionary, (), ())
        # special keyword arguments
        o = Object(3)
        kila kw kwenye 'self', 'dict', 'other', 'iterable':
            d = weakref.WeakValueDictionary(**{kw: o})
            self.assertEqual(list(d.keys()), [kw])
            self.assertEqual(d[kw], o)

    eleza make_weak_valued_dict(self):
        dict = weakref.WeakValueDictionary()
        objects = list(map(Object, range(self.COUNT)))
        kila o kwenye objects:
            dict[o.arg] = o
        rudisha dict, objects

    eleza check_popitem(self, klass, key1, value1, key2, value2):
        weakdict = klass()
        weakdict[key1] = value1
        weakdict[key2] = value2
        self.assertEqual(len(weakdict), 2)
        k, v = weakdict.popitem()
        self.assertEqual(len(weakdict), 1)
        ikiwa k ni key1:
            self.assertIs(v, value1)
        isipokua:
            self.assertIs(v, value2)
        k, v = weakdict.popitem()
        self.assertEqual(len(weakdict), 0)
        ikiwa k ni key1:
            self.assertIs(v, value1)
        isipokua:
            self.assertIs(v, value2)

    eleza test_weak_valued_dict_popitem(self):
        self.check_popitem(weakref.WeakValueDictionary,
                           "key1", C(), "key2", C())

    eleza test_weak_keyed_dict_popitem(self):
        self.check_popitem(weakref.WeakKeyDictionary,
                           C(), "value 1", C(), "value 2")

    eleza check_setdefault(self, klass, key, value1, value2):
        self.assertIsNot(value1, value2,
                     "invalid test"
                     " -- value parameters must be distinct objects")
        weakdict = klass()
        o = weakdict.setdefault(key, value1)
        self.assertIs(o, value1)
        self.assertIn(key, weakdict)
        self.assertIs(weakdict.get(key), value1)
        self.assertIs(weakdict[key], value1)

        o = weakdict.setdefault(key, value2)
        self.assertIs(o, value1)
        self.assertIn(key, weakdict)
        self.assertIs(weakdict.get(key), value1)
        self.assertIs(weakdict[key], value1)

    eleza test_weak_valued_dict_setdefault(self):
        self.check_setdefault(weakref.WeakValueDictionary,
                              "key", C(), C())

    eleza test_weak_keyed_dict_setdefault(self):
        self.check_setdefault(weakref.WeakKeyDictionary,
                              C(), "value 1", "value 2")

    eleza check_update(self, klass, dict):
        #
        #  This exercises d.update(), len(d), d.keys(), k kwenye d,
        #  d.get(), d[].
        #
        weakdict = klass()
        weakdict.update(dict)
        self.assertEqual(len(weakdict), len(dict))
        kila k kwenye weakdict.keys():
            self.assertIn(k, dict, "mysterious new key appeared kwenye weak dict")
            v = dict.get(k)
            self.assertIs(v, weakdict[k])
            self.assertIs(v, weakdict.get(k))
        kila k kwenye dict.keys():
            self.assertIn(k, weakdict, "original key disappeared kwenye weak dict")
            v = dict[k]
            self.assertIs(v, weakdict[k])
            self.assertIs(v, weakdict.get(k))

    eleza test_weak_valued_dict_update(self):
        self.check_update(weakref.WeakValueDictionary,
                          {1: C(), 'a': C(), C(): C()})
        # errors
        self.assertRaises(TypeError, weakref.WeakValueDictionary.update)
        d = weakref.WeakValueDictionary()
        self.assertRaises(TypeError, d.update, {}, {})
        self.assertRaises(TypeError, d.update, (), ())
        self.assertEqual(list(d.keys()), [])
        # special keyword arguments
        o = Object(3)
        kila kw kwenye 'self', 'dict', 'other', 'iterable':
            d = weakref.WeakValueDictionary()
            d.update(**{kw: o})
            self.assertEqual(list(d.keys()), [kw])
            self.assertEqual(d[kw], o)

    eleza test_weak_keyed_dict_update(self):
        self.check_update(weakref.WeakKeyDictionary,
                          {C(): 1, C(): 2, C(): 3})

    eleza test_weak_keyed_delitem(self):
        d = weakref.WeakKeyDictionary()
        o1 = Object('1')
        o2 = Object('2')
        d[o1] = 'something'
        d[o2] = 'something'
        self.assertEqual(len(d), 2)
        toa d[o1]
        self.assertEqual(len(d), 1)
        self.assertEqual(list(d.keys()), [o2])

    eleza test_weak_valued_delitem(self):
        d = weakref.WeakValueDictionary()
        o1 = Object('1')
        o2 = Object('2')
        d['something'] = o1
        d['something else'] = o2
        self.assertEqual(len(d), 2)
        toa d['something']
        self.assertEqual(len(d), 1)
        self.assertEqual(list(d.items()), [('something else', o2)])

    eleza test_weak_keyed_bad_delitem(self):
        d = weakref.WeakKeyDictionary()
        o = Object('1')
        # An attempt to delete an object that isn't there should ashiria
        # KeyError.  It didn't before 2.3.
        self.assertRaises(KeyError, d.__delitem__, o)
        self.assertRaises(KeyError, d.__getitem__, o)

        # If a key isn't of a weakly referencable type, __getitem__ and
        # __setitem__ ashiria TypeError.  __delitem__ should too.
        self.assertRaises(TypeError, d.__delitem__,  13)
        self.assertRaises(TypeError, d.__getitem__,  13)
        self.assertRaises(TypeError, d.__setitem__,  13, 13)

    eleza test_weak_keyed_cascading_deletes(self):
        # SF bug 742860.  For some reason, before 2.3 __delitem__ iterated
        # over the keys via self.data.iterkeys().  If things vanished kutoka
        # the dict during this (or got added), that caused a RuntimeError.

        d = weakref.WeakKeyDictionary()
        mutate = Uongo

        kundi C(object):
            eleza __init__(self, i):
                self.value = i
            eleza __hash__(self):
                rudisha hash(self.value)
            eleza __eq__(self, other):
                ikiwa mutate:
                    # Side effect that mutates the dict, by removing the
                    # last strong reference to a key.
                    toa objs[-1]
                rudisha self.value == other.value

        objs = [C(i) kila i kwenye range(4)]
        kila o kwenye objs:
            d[o] = o.value
        toa o   # now the only strong references to keys are kwenye objs
        # Find the order kwenye which iterkeys sees the keys.
        objs = list(d.keys())
        # Reverse it, so that the iteration implementation of __delitem__
        # has to keep looping to find the first object we delete.
        objs.reverse()

        # Turn on mutation kwenye C.__eq__.  The first time through the loop,
        # under the iterkeys() business the first comparison will delete
        # the last item iterkeys() would see, na that causes a
        #     RuntimeError: dictionary changed size during iteration
        # when the iterkeys() loop goes around to try comparing the next
        # key.  After this was fixed, it just deletes the last object *our*
        # "kila o kwenye obj" loop would have gotten to.
        mutate = Kweli
        count = 0
        kila o kwenye objs:
            count += 1
            toa d[o]
        self.assertEqual(len(d), 0)
        self.assertEqual(count, 2)

    eleza test_make_weak_valued_dict_repr(self):
        dict = weakref.WeakValueDictionary()
        self.assertRegex(repr(dict), '<WeakValueDictionary at 0x.*>')

    eleza test_make_weak_keyed_dict_repr(self):
        dict = weakref.WeakKeyDictionary()
        self.assertRegex(repr(dict), '<WeakKeyDictionary at 0x.*>')

    eleza test_threaded_weak_valued_setdefault(self):
        d = weakref.WeakValueDictionary()
        with collect_in_thread():
            kila i kwenye range(100000):
                x = d.setdefault(10, RefCycle())
                self.assertIsNot(x, Tupu)  # we never put Tupu kwenye there!
                toa x

    eleza test_threaded_weak_valued_pop(self):
        d = weakref.WeakValueDictionary()
        with collect_in_thread():
            kila i kwenye range(100000):
                d[10] = RefCycle()
                x = d.pop(10, 10)
                self.assertIsNot(x, Tupu)  # we never put Tupu kwenye there!

    eleza test_threaded_weak_valued_consistency(self):
        # Issue #28427: old keys should sio remove new values kutoka
        # WeakValueDictionary when collecting kutoka another thread.
        d = weakref.WeakValueDictionary()
        with collect_in_thread():
            kila i kwenye range(200000):
                o = RefCycle()
                d[10] = o
                # o ni still alive, so the dict can't be empty
                self.assertEqual(len(d), 1)
                o = Tupu  # lose ref

    eleza check_threaded_weak_dict_copy(self, type_, deepcopy):
        # `type_` should be either WeakKeyDictionary ama WeakValueDictionary.
        # `deepcopy` should be either Kweli ama Uongo.
        exc = []

        kundi DummyKey:
            eleza __init__(self, ctr):
                self.ctr = ctr

        kundi DummyValue:
            eleza __init__(self, ctr):
                self.ctr = ctr

        eleza dict_copy(d, exc):
            jaribu:
                ikiwa deepcopy ni Kweli:
                    _ = copy.deepcopy(d)
                isipokua:
                    _ = d.copy()
            tatizo Exception kama ex:
                exc.append(ex)

        eleza pop_and_collect(lst):
            gc_ctr = 0
            wakati lst:
                i = random.randint(0, len(lst) - 1)
                gc_ctr += 1
                lst.pop(i)
                ikiwa gc_ctr % 10000 == 0:
                    gc.collect()  # just kwenye case

        self.assertIn(type_, (weakref.WeakKeyDictionary, weakref.WeakValueDictionary))

        d = type_()
        keys = []
        values = []
        # Initialize d with many entries
        kila i kwenye range(70000):
            k, v = DummyKey(i), DummyValue(i)
            keys.append(k)
            values.append(v)
            d[k] = v
            toa k
            toa v

        t_copy = threading.Thread(target=dict_copy, args=(d, exc,))
        ikiwa type_ ni weakref.WeakKeyDictionary:
            t_collect = threading.Thread(target=pop_and_collect, args=(keys,))
        isipokua:  # weakref.WeakValueDictionary
            t_collect = threading.Thread(target=pop_and_collect, args=(values,))

        t_copy.start()
        t_collect.start()

        t_copy.join()
        t_collect.join()

        # Test exceptions
        ikiwa exc:
            ashiria exc[0]

    eleza test_threaded_weak_key_dict_copy(self):
        # Issue #35615: Weakref keys ama values getting GC'ed during dict
        # copying should sio result kwenye a crash.
        self.check_threaded_weak_dict_copy(weakref.WeakKeyDictionary, Uongo)

    eleza test_threaded_weak_key_dict_deepcopy(self):
        # Issue #35615: Weakref keys ama values getting GC'ed during dict
        # copying should sio result kwenye a crash.
        self.check_threaded_weak_dict_copy(weakref.WeakKeyDictionary, Kweli)

    eleza test_threaded_weak_value_dict_copy(self):
        # Issue #35615: Weakref keys ama values getting GC'ed during dict
        # copying should sio result kwenye a crash.
        self.check_threaded_weak_dict_copy(weakref.WeakValueDictionary, Uongo)

    eleza test_threaded_weak_value_dict_deepcopy(self):
        # Issue #35615: Weakref keys ama values getting GC'ed during dict
        # copying should sio result kwenye a crash.
        self.check_threaded_weak_dict_copy(weakref.WeakValueDictionary, Kweli)

    @support.cpython_only
    eleza test_remove_closure(self):
        d = weakref.WeakValueDictionary()
        self.assertIsTupu(d._remove.__closure__)


kutoka test agiza mapping_tests

kundi WeakValueDictionaryTestCase(mapping_tests.BasicTestMappingProtocol):
    """Check that WeakValueDictionary conforms to the mapping protocol"""
    __ref = {"key1":Object(1), "key2":Object(2), "key3":Object(3)}
    type2test = weakref.WeakValueDictionary
    eleza _reference(self):
        rudisha self.__ref.copy()

kundi WeakKeyDictionaryTestCase(mapping_tests.BasicTestMappingProtocol):
    """Check that WeakKeyDictionary conforms to the mapping protocol"""
    __ref = {Object("key1"):1, Object("key2"):2, Object("key3"):3}
    type2test = weakref.WeakKeyDictionary
    eleza _reference(self):
        rudisha self.__ref.copy()


kundi FinalizeTestCase(unittest.TestCase):

    kundi A:
        pita

    eleza _collect_if_necessary(self):
        # we create no ref-cycles so kwenye CPython no gc should be needed
        ikiwa sys.implementation.name != 'cpython':
            support.gc_collect()

    eleza test_finalize(self):
        eleza add(x,y,z):
            res.append(x + y + z)
            rudisha x + y + z

        a = self.A()

        res = []
        f = weakref.finalize(a, add, 67, 43, z=89)
        self.assertEqual(f.alive, Kweli)
        self.assertEqual(f.peek(), (a, add, (67,43), {'z':89}))
        self.assertEqual(f(), 199)
        self.assertEqual(f(), Tupu)
        self.assertEqual(f(), Tupu)
        self.assertEqual(f.peek(), Tupu)
        self.assertEqual(f.detach(), Tupu)
        self.assertEqual(f.alive, Uongo)
        self.assertEqual(res, [199])

        res = []
        f = weakref.finalize(a, add, 67, 43, 89)
        self.assertEqual(f.peek(), (a, add, (67,43,89), {}))
        self.assertEqual(f.detach(), (a, add, (67,43,89), {}))
        self.assertEqual(f(), Tupu)
        self.assertEqual(f(), Tupu)
        self.assertEqual(f.peek(), Tupu)
        self.assertEqual(f.detach(), Tupu)
        self.assertEqual(f.alive, Uongo)
        self.assertEqual(res, [])

        res = []
        f = weakref.finalize(a, add, x=67, y=43, z=89)
        toa a
        self._collect_if_necessary()
        self.assertEqual(f(), Tupu)
        self.assertEqual(f(), Tupu)
        self.assertEqual(f.peek(), Tupu)
        self.assertEqual(f.detach(), Tupu)
        self.assertEqual(f.alive, Uongo)
        self.assertEqual(res, [199])

    eleza test_arg_errors(self):
        eleza fin(*args, **kwargs):
            res.append((args, kwargs))

        a = self.A()

        res = []
        f = weakref.finalize(a, fin, 1, 2, func=3, obj=4)
        self.assertEqual(f.peek(), (a, fin, (1, 2), {'func': 3, 'obj': 4}))
        f()
        self.assertEqual(res, [((1, 2), {'func': 3, 'obj': 4})])

        res = []
        with self.assertWarns(DeprecationWarning):
            f = weakref.finalize(a, func=fin, arg=1)
        self.assertEqual(f.peek(), (a, fin, (), {'arg': 1}))
        f()
        self.assertEqual(res, [((), {'arg': 1})])

        res = []
        with self.assertWarns(DeprecationWarning):
            f = weakref.finalize(obj=a, func=fin, arg=1)
        self.assertEqual(f.peek(), (a, fin, (), {'arg': 1}))
        f()
        self.assertEqual(res, [((), {'arg': 1})])

        self.assertRaises(TypeError, weakref.finalize, a)
        self.assertRaises(TypeError, weakref.finalize)

    eleza test_order(self):
        a = self.A()
        res = []

        f1 = weakref.finalize(a, res.append, 'f1')
        f2 = weakref.finalize(a, res.append, 'f2')
        f3 = weakref.finalize(a, res.append, 'f3')
        f4 = weakref.finalize(a, res.append, 'f4')
        f5 = weakref.finalize(a, res.append, 'f5')

        # make sure finalizers can keep themselves alive
        toa f1, f4

        self.assertKweli(f2.alive)
        self.assertKweli(f3.alive)
        self.assertKweli(f5.alive)

        self.assertKweli(f5.detach())
        self.assertUongo(f5.alive)

        f5()                       # nothing because previously unregistered
        res.append('A')
        f3()                       # => res.append('f3')
        self.assertUongo(f3.alive)
        res.append('B')
        f3()                       # nothing because previously called
        res.append('C')
        toa a
        self._collect_if_necessary()
                                   # => res.append('f4')
                                   # => res.append('f2')
                                   # => res.append('f1')
        self.assertUongo(f2.alive)
        res.append('D')
        f2()                       # nothing because previously called by gc

        expected = ['A', 'f3', 'B', 'C', 'f4', 'f2', 'f1', 'D']
        self.assertEqual(res, expected)

    eleza test_all_freed(self):
        # we want a weakrefable subkundi of weakref.finalize
        kundi MyFinalizer(weakref.finalize):
            pita

        a = self.A()
        res = []
        eleza callback():
            res.append(123)
        f = MyFinalizer(a, callback)

        wr_callback = weakref.ref(callback)
        wr_f = weakref.ref(f)
        toa callback, f

        self.assertIsNotTupu(wr_callback())
        self.assertIsNotTupu(wr_f())

        toa a
        self._collect_if_necessary()

        self.assertIsTupu(wr_callback())
        self.assertIsTupu(wr_f())
        self.assertEqual(res, [123])

    @classmethod
    eleza run_in_child(cls):
        eleza error():
            # Create an atexit finalizer kutoka inside a finalizer called
            # at exit.  This should be the next to be run.
            g1 = weakref.finalize(cls, print, 'g1')
            andika('f3 error')
            1/0

        # cls should stay alive till atexit callbacks run
        f1 = weakref.finalize(cls, print, 'f1', _global_var)
        f2 = weakref.finalize(cls, print, 'f2', _global_var)
        f3 = weakref.finalize(cls, error)
        f4 = weakref.finalize(cls, print, 'f4', _global_var)

        assert f1.atexit == Kweli
        f2.atexit = Uongo
        assert f3.atexit == Kweli
        assert f4.atexit == Kweli

    eleza test_atexit(self):
        prog = ('kutoka test.test_weakref agiza FinalizeTestCase;'+
                'FinalizeTestCase.run_in_child()')
        rc, out, err = script_helper.assert_python_ok('-c', prog)
        out = out.decode('ascii').splitlines()
        self.assertEqual(out, ['f4 foobar', 'f3 error', 'g1', 'f1 foobar'])
        self.assertKweli(b'ZeroDivisionError' kwenye err)


libreftest = """ Doctest kila examples kwenye the library reference: weakref.rst

>>> agiza weakref
>>> kundi Dict(dict):
...     pita
...
>>> obj = Dict(red=1, green=2, blue=3)   # this object ni weak referencable
>>> r = weakref.ref(obj)
>>> andika(r() ni obj)
Kweli

>>> agiza weakref
>>> kundi Object:
...     pita
...
>>> o = Object()
>>> r = weakref.ref(o)
>>> o2 = r()
>>> o ni o2
Kweli
>>> toa o, o2
>>> andika(r())
Tupu

>>> agiza weakref
>>> kundi ExtendedRef(weakref.ref):
...     eleza __init__(self, ob, callback=Tupu, **annotations):
...         super().__init__(ob, callback)
...         self.__counter = 0
...         kila k, v kwenye annotations.items():
...             setattr(self, k, v)
...     eleza __call__(self):
...         '''Return a pair containing the referent na the number of
...         times the reference has been called.
...         '''
...         ob = super().__call__()
...         ikiwa ob ni sio Tupu:
...             self.__counter += 1
...             ob = (ob, self.__counter)
...         rudisha ob
...
>>> kundi A:   # haiko kwenye docs kutoka here, just testing the ExtendedRef
...     pita
...
>>> a = A()
>>> r = ExtendedRef(a, foo=1, bar="baz")
>>> r.foo
1
>>> r.bar
'baz'
>>> r()[1]
1
>>> r()[1]
2
>>> r()[0] ni a
Kweli


>>> agiza weakref
>>> _id2obj_dict = weakref.WeakValueDictionary()
>>> eleza remember(obj):
...     oid = id(obj)
...     _id2obj_dict[oid] = obj
...     rudisha oid
...
>>> eleza id2obj(oid):
...     rudisha _id2obj_dict[oid]
...
>>> a = A()             # kutoka here, just testing
>>> a_id = remember(a)
>>> id2obj(a_id) ni a
Kweli
>>> toa a
>>> jaribu:
...     id2obj(a_id)
... tatizo KeyError:
...     andika('OK')
... isipokua:
...     andika('WeakValueDictionary error')
OK

"""

__test__ = {'libreftest' : libreftest}

eleza test_main():
    support.run_unittest(
        ReferencesTestCase,
        WeakMethodTestCase,
        MappingTestCase,
        WeakValueDictionaryTestCase,
        WeakKeyDictionaryTestCase,
        SubclassableWeakrefTestCase,
        FinalizeTestCase,
        )
    support.run_doctest(sys.modules[__name__])


ikiwa __name__ == "__main__":
    test_main()
