agiza unittest
kutoka test.support agiza (verbose, refcount_test, run_unittest,
                          strip_python_stderr, cpython_only, start_threads,
                          temp_dir, requires_type_collecting, TESTFN, unlink,
                          import_module)
kutoka test.support.script_helper agiza assert_python_ok, make_script

agiza gc
agiza sys
agiza sysconfig
agiza textwrap
agiza threading
agiza time
agiza weakref

jaribu:
    kutoka _testcapi agiza with_tp_del
tatizo ImportError:
    eleza with_tp_del(cls):
        kundi C(object):
            eleza __new__(cls, *args, **kwargs):
                ashiria TypeError('requires _testcapi.with_tp_del')
        rudisha C

### Support code
###############################################################################

# Bug 1055820 has several tests of longstanding bugs involving weakrefs na
# cyclic gc.

# An instance of C1055820 has a self-loop, so becomes cyclic trash when
# unreachable.
kundi C1055820(object):
    eleza __init__(self, i):
        self.i = i
        self.loop = self

kundi GC_Detector(object):
    # Create an instance I.  Then gc hasn't happened again so long as
    # I.gc_happened ni false.

    eleza __init__(self):
        self.gc_happened = Uongo

        eleza it_happened(ignored):
            self.gc_happened = Kweli

        # Create a piece of cyclic trash that triggers it_happened when
        # gc collects it.
        self.wr = weakref.ref(C1055820(666), it_happened)

@with_tp_del
kundi Uncollectable(object):
    """Create a reference cycle ukijumuisha multiple __del__ methods.

    An object kwenye a reference cycle will never have zero references,
    na so must be garbage collected.  If one ama more objects kwenye the
    cycle have __del__ methods, the gc refuses to guess an order,
    na leaves the cycle uncollected."""
    eleza __init__(self, partner=Tupu):
        ikiwa partner ni Tupu:
            self.partner = Uncollectable(partner=self)
        isipokua:
            self.partner = partner
    eleza __tp_del__(self):
        pita

ikiwa sysconfig.get_config_vars().get('PY_CFLAGS', ''):
    BUILD_WITH_NDEBUG = ('-DNDEBUG' kwenye sysconfig.get_config_vars()['PY_CFLAGS'])
isipokua:
    # Usually, sys.gettotalrefcount() ni only present ikiwa Python has been
    # compiled kwenye debug mode. If it's missing, expect that Python has
    # been released kwenye release mode: ukijumuisha NDEBUG defined.
    BUILD_WITH_NDEBUG = (sio hasattr(sys, 'gettotalrefcount'))

### Tests
###############################################################################

kundi GCTests(unittest.TestCase):
    eleza test_list(self):
        l = []
        l.append(l)
        gc.collect()
        toa l
        self.assertEqual(gc.collect(), 1)

    eleza test_dict(self):
        d = {}
        d[1] = d
        gc.collect()
        toa d
        self.assertEqual(gc.collect(), 1)

    eleza test_tuple(self):
        # since tuples are immutable we close the loop ukijumuisha a list
        l = []
        t = (l,)
        l.append(t)
        gc.collect()
        toa t
        toa l
        self.assertEqual(gc.collect(), 2)

    eleza test_class(self):
        kundi A:
            pita
        A.a = A
        gc.collect()
        toa A
        self.assertNotEqual(gc.collect(), 0)

    eleza test_newstyleclass(self):
        kundi A(object):
            pita
        gc.collect()
        toa A
        self.assertNotEqual(gc.collect(), 0)

    eleza test_instance(self):
        kundi A:
            pita
        a = A()
        a.a = a
        gc.collect()
        toa a
        self.assertNotEqual(gc.collect(), 0)

    @requires_type_collecting
    eleza test_newinstance(self):
        kundi A(object):
            pita
        a = A()
        a.a = a
        gc.collect()
        toa a
        self.assertNotEqual(gc.collect(), 0)
        kundi B(list):
            pita
        kundi C(B, A):
            pita
        a = C()
        a.a = a
        gc.collect()
        toa a
        self.assertNotEqual(gc.collect(), 0)
        toa B, C
        self.assertNotEqual(gc.collect(), 0)
        A.a = A()
        toa A
        self.assertNotEqual(gc.collect(), 0)
        self.assertEqual(gc.collect(), 0)

    eleza test_method(self):
        # Tricky: self.__init__ ni a bound method, it references the instance.
        kundi A:
            eleza __init__(self):
                self.init = self.__init__
        a = A()
        gc.collect()
        toa a
        self.assertNotEqual(gc.collect(), 0)

    @cpython_only
    eleza test_legacy_finalizer(self):
        # A() ni uncollectable ikiwa it ni part of a cycle, make sure it shows up
        # kwenye gc.garbage.
        @with_tp_del
        kundi A:
            eleza __tp_del__(self): pita
        kundi B:
            pita
        a = A()
        a.a = a
        id_a = id(a)
        b = B()
        b.b = b
        gc.collect()
        toa a
        toa b
        self.assertNotEqual(gc.collect(), 0)
        kila obj kwenye gc.garbage:
            ikiwa id(obj) == id_a:
                toa obj.a
                koma
        isipokua:
            self.fail("didn't find obj kwenye garbage (finalizer)")
        gc.garbage.remove(obj)

    @cpython_only
    eleza test_legacy_finalizer_newclass(self):
        # A() ni uncollectable ikiwa it ni part of a cycle, make sure it shows up
        # kwenye gc.garbage.
        @with_tp_del
        kundi A(object):
            eleza __tp_del__(self): pita
        kundi B(object):
            pita
        a = A()
        a.a = a
        id_a = id(a)
        b = B()
        b.b = b
        gc.collect()
        toa a
        toa b
        self.assertNotEqual(gc.collect(), 0)
        kila obj kwenye gc.garbage:
            ikiwa id(obj) == id_a:
                toa obj.a
                koma
        isipokua:
            self.fail("didn't find obj kwenye garbage (finalizer)")
        gc.garbage.remove(obj)

    eleza test_function(self):
        # Tricky: f -> d -> f, code should call d.clear() after the exec to
        # koma the cycle.
        d = {}
        exec("eleza f(): pita\n", d)
        gc.collect()
        toa d
        self.assertEqual(gc.collect(), 2)

    @refcount_test
    eleza test_frame(self):
        eleza f():
            frame = sys._getframe()
        gc.collect()
        f()
        self.assertEqual(gc.collect(), 1)

    eleza test_saveall(self):
        # Verify that cyclic garbage like lists show up kwenye gc.garbage ikiwa the
        # SAVEALL option ni enabled.

        # First make sure we don't save away other stuff that just happens to
        # be waiting kila collection.
        gc.collect()
        # ikiwa this fails, someone isipokua created immortal trash
        self.assertEqual(gc.garbage, [])

        L = []
        L.append(L)
        id_L = id(L)

        debug = gc.get_debug()
        gc.set_debug(debug | gc.DEBUG_SAVEALL)
        toa L
        gc.collect()
        gc.set_debug(debug)

        self.assertEqual(len(gc.garbage), 1)
        obj = gc.garbage.pop()
        self.assertEqual(id(obj), id_L)

    eleza test_del(self):
        # __del__ methods can trigger collection, make this to happen
        thresholds = gc.get_threshold()
        gc.enable()
        gc.set_threshold(1)

        kundi A:
            eleza __del__(self):
                dir(self)
        a = A()
        toa a

        gc.disable()
        gc.set_threshold(*thresholds)

    eleza test_del_newclass(self):
        # __del__ methods can trigger collection, make this to happen
        thresholds = gc.get_threshold()
        gc.enable()
        gc.set_threshold(1)

        kundi A(object):
            eleza __del__(self):
                dir(self)
        a = A()
        toa a

        gc.disable()
        gc.set_threshold(*thresholds)

    # The following two tests are fragile:
    # They precisely count the number of allocations,
    # which ni highly implementation-dependent.
    # For example, disposed tuples are sio freed, but reused.
    # To minimize variations, though, we first store the get_count() results
    # na check them at the end.
    @refcount_test
    eleza test_get_count(self):
        gc.collect()
        a, b, c = gc.get_count()
        x = []
        d, e, f = gc.get_count()
        self.assertEqual((b, c), (0, 0))
        self.assertEqual((e, f), (0, 0))
        # This ni less fragile than asserting that a equals 0.
        self.assertLess(a, 5)
        # Between the two calls to get_count(), at least one object was
        # created (the list).
        self.assertGreater(d, a)

    @refcount_test
    eleza test_collect_generations(self):
        gc.collect()
        # This object will "trickle" into generation N + 1 after
        # each call to collect(N)
        x = []
        gc.collect(0)
        # x ni now kwenye gen 1
        a, b, c = gc.get_count()
        gc.collect(1)
        # x ni now kwenye gen 2
        d, e, f = gc.get_count()
        gc.collect(2)
        # x ni now kwenye gen 3
        g, h, i = gc.get_count()
        # We don't check a, d, g since their exact values depends on
        # internal implementation details of the interpreter.
        self.assertEqual((b, c), (1, 0))
        self.assertEqual((e, f), (0, 1))
        self.assertEqual((h, i), (0, 0))

    eleza test_trashcan(self):
        kundi Ouch:
            n = 0
            eleza __del__(self):
                Ouch.n = Ouch.n + 1
                ikiwa Ouch.n % 17 == 0:
                    gc.collect()

        # "trashcan" ni a hack to prevent stack overflow when deallocating
        # very deeply nested tuples etc.  It works kwenye part by abusing the
        # type pointer na refcount fields, na that can tuma horrible
        # problems when gc tries to traverse the structures.
        # If this test fails (as it does kwenye 2.0, 2.1 na 2.2), it will
        # most likely die via segfault.

        # Note:  In 2.3 the possibility kila compiling without cyclic gc was
        # removed, na that kwenye turn allows the trashcan mechanism to work
        # via much simpler means (e.g., it never abuses the type pointer ama
        # refcount fields anymore).  Since it's much less likely to cause a
        # problem now, the various constants kwenye this expensive (we force a lot
        # of full collections) test are cut back kutoka the 2.2 version.
        gc.enable()
        N = 150
        kila count kwenye range(2):
            t = []
            kila i kwenye range(N):
                t = [t, Ouch()]
            u = []
            kila i kwenye range(N):
                u = [u, Ouch()]
            v = {}
            kila i kwenye range(N):
                v = {1: v, 2: Ouch()}
        gc.disable()

    eleza test_trashcan_threads(self):
        # Issue #13992: trashcan mechanism should be thread-safe
        NESTING = 60
        N_THREADS = 2

        eleza sleeper_gen():
            """A generator that releases the GIL when closed ama dealloc'ed."""
            jaribu:
                tuma
            mwishowe:
                time.sleep(0.000001)

        kundi C(list):
            # Appending to a list ni atomic, which avoids the use of a lock.
            inits = []
            dels = []
            eleza __init__(self, alist):
                self[:] = alist
                C.inits.append(Tupu)
            eleza __del__(self):
                # This __del__ ni called by subtype_dealloc().
                C.dels.append(Tupu)
                # `g` will release the GIL when garbage-collected.  This
                # helps assert subtype_dealloc's behaviour when threads
                # switch kwenye the middle of it.
                g = sleeper_gen()
                next(g)
                # Now that __del__ ni finished, subtype_dealloc will proceed
                # to call list_dealloc, which also uses the trashcan mechanism.

        eleza make_nested():
            """Create a sufficiently nested container object so that the
            trashcan mechanism ni invoked when deallocating it."""
            x = C([])
            kila i kwenye range(NESTING):
                x = [C([x])]
            toa x

        eleza run_thread():
            """Exercise make_nested() kwenye a loop."""
            wakati sio exit:
                make_nested()

        old_switchinterval = sys.getswitchinterval()
        sys.setswitchinterval(1e-5)
        jaribu:
            exit = []
            threads = []
            kila i kwenye range(N_THREADS):
                t = threading.Thread(target=run_thread)
                threads.append(t)
            ukijumuisha start_threads(threads, lambda: exit.append(1)):
                time.sleep(1.0)
        mwishowe:
            sys.setswitchinterval(old_switchinterval)
        gc.collect()
        self.assertEqual(len(C.inits), len(C.dels))

    eleza test_boom(self):
        kundi Boom:
            eleza __getattr__(self, someattribute):
                toa self.attr
                ashiria AttributeError

        a = Boom()
        b = Boom()
        a.attr = b
        b.attr = a

        gc.collect()
        garbagelen = len(gc.garbage)
        toa a, b
        # a<->b are kwenye a trash cycle now.  Collection will invoke
        # Boom.__getattr__ (to see whether a na b have __del__ methods), na
        # __getattr__ deletes the internal "attr" attributes kama a side effect.
        # That causes the trash cycle to get reclaimed via refcounts falling to
        # 0, thus mutating the trash graph kama a side effect of merely asking
        # whether __del__ exists.  This used to (before 2.3b1) crash Python.
        # Now __getattr__ isn't called.
        self.assertEqual(gc.collect(), 4)
        self.assertEqual(len(gc.garbage), garbagelen)

    eleza test_boom2(self):
        kundi Boom2:
            eleza __init__(self):
                self.x = 0

            eleza __getattr__(self, someattribute):
                self.x += 1
                ikiwa self.x > 1:
                    toa self.attr
                ashiria AttributeError

        a = Boom2()
        b = Boom2()
        a.attr = b
        b.attr = a

        gc.collect()
        garbagelen = len(gc.garbage)
        toa a, b
        # Much like test_boom(), tatizo that __getattr__ doesn't koma the
        # cycle until the second time gc checks kila __del__.  As of 2.3b1,
        # there isn't a second time, so this simply cleans up the trash cycle.
        # We expect a, b, a.__dict__ na b.__dict__ (4 objects) to get
        # reclaimed this way.
        self.assertEqual(gc.collect(), 4)
        self.assertEqual(len(gc.garbage), garbagelen)

    eleza test_boom_new(self):
        # boom__new na boom2_new are exactly like boom na boom2, tatizo use
        # new-style classes.

        kundi Boom_New(object):
            eleza __getattr__(self, someattribute):
                toa self.attr
                ashiria AttributeError

        a = Boom_New()
        b = Boom_New()
        a.attr = b
        b.attr = a

        gc.collect()
        garbagelen = len(gc.garbage)
        toa a, b
        self.assertEqual(gc.collect(), 4)
        self.assertEqual(len(gc.garbage), garbagelen)

    eleza test_boom2_new(self):
        kundi Boom2_New(object):
            eleza __init__(self):
                self.x = 0

            eleza __getattr__(self, someattribute):
                self.x += 1
                ikiwa self.x > 1:
                    toa self.attr
                ashiria AttributeError

        a = Boom2_New()
        b = Boom2_New()
        a.attr = b
        b.attr = a

        gc.collect()
        garbagelen = len(gc.garbage)
        toa a, b
        self.assertEqual(gc.collect(), 4)
        self.assertEqual(len(gc.garbage), garbagelen)

    eleza test_get_referents(self):
        alist = [1, 3, 5]
        got = gc.get_referents(alist)
        got.sort()
        self.assertEqual(got, alist)

        atuple = tuple(alist)
        got = gc.get_referents(atuple)
        got.sort()
        self.assertEqual(got, alist)

        adict = {1: 3, 5: 7}
        expected = [1, 3, 5, 7]
        got = gc.get_referents(adict)
        got.sort()
        self.assertEqual(got, expected)

        got = gc.get_referents([1, 2], {3: 4}, (0, 0, 0))
        got.sort()
        self.assertEqual(got, [0, 0] + list(range(5)))

        self.assertEqual(gc.get_referents(1, 'a', 4j), [])

    eleza test_is_tracked(self):
        # Atomic built-in types are sio tracked, user-defined objects na
        # mutable containers are.
        # NOTE: types ukijumuisha special optimizations (e.g. tuple) have tests
        # kwenye their own test files instead.
        self.assertUongo(gc.is_tracked(Tupu))
        self.assertUongo(gc.is_tracked(1))
        self.assertUongo(gc.is_tracked(1.0))
        self.assertUongo(gc.is_tracked(1.0 + 5.0j))
        self.assertUongo(gc.is_tracked(Kweli))
        self.assertUongo(gc.is_tracked(Uongo))
        self.assertUongo(gc.is_tracked(b"a"))
        self.assertUongo(gc.is_tracked("a"))
        self.assertUongo(gc.is_tracked(bytearray(b"a")))
        self.assertUongo(gc.is_tracked(type))
        self.assertUongo(gc.is_tracked(int))
        self.assertUongo(gc.is_tracked(object))
        self.assertUongo(gc.is_tracked(object()))

        kundi UserClass:
            pita

        kundi UserInt(int):
            pita

        # Base kundi ni object; no extra fields.
        kundi UserClassSlots:
            __slots__ = ()

        # Base kundi ni fixed size larger than object; no extra fields.
        kundi UserFloatSlots(float):
            __slots__ = ()

        # Base kundi ni variable size; no extra fields.
        kundi UserIntSlots(int):
            __slots__ = ()

        self.assertKweli(gc.is_tracked(gc))
        self.assertKweli(gc.is_tracked(UserClass))
        self.assertKweli(gc.is_tracked(UserClass()))
        self.assertKweli(gc.is_tracked(UserInt()))
        self.assertKweli(gc.is_tracked([]))
        self.assertKweli(gc.is_tracked(set()))
        self.assertUongo(gc.is_tracked(UserClassSlots()))
        self.assertUongo(gc.is_tracked(UserFloatSlots()))
        self.assertUongo(gc.is_tracked(UserIntSlots()))

    eleza test_bug1055820b(self):
        # Corresponds to temp2b.py kwenye the bug report.

        ouch = []
        eleza callback(ignored):
            ouch[:] = [wr() kila wr kwenye WRs]

        Cs = [C1055820(i) kila i kwenye range(2)]
        WRs = [weakref.ref(c, callback) kila c kwenye Cs]
        c = Tupu

        gc.collect()
        self.assertEqual(len(ouch), 0)
        # Make the two instances trash, na collect again.  The bug was that
        # the callback materialized a strong reference to an instance, but gc
        # cleared the instance's dict anyway.
        Cs = Tupu
        gc.collect()
        self.assertEqual(len(ouch), 2)  # isipokua the callbacks didn't run
        kila x kwenye ouch:
            # If the callback resurrected one of these guys, the instance
            # would be damaged, ukijumuisha an empty __dict__.
            self.assertEqual(x, Tupu)

    eleza test_bug21435(self):
        # This ni a poor test - its only virtue ni that it happened to
        # segfault on Tim's Windows box before the patch kila 21435 was
        # applied.  That's a nasty bug relying on specific pieces of cyclic
        # trash appearing kwenye exactly the right order kwenye finalize_garbage()'s
        # input list.
        # But there's no reliable way to force that order kutoka Python code,
        # so over time chances are good this test won't really be testing much
        # of anything anymore.  Still, ikiwa it blows up, there's _some_
        # problem ;-)
        gc.collect()

        kundi A:
            pita

        kundi B:
            eleza __init__(self, x):
                self.x = x

            eleza __del__(self):
                self.attr = Tupu

        eleza do_work():
            a = A()
            b = B(A())

            a.attr = b
            b.attr = a

        do_work()
        gc.collect() # this blows up (bad C pointer) when it fails

    @cpython_only
    eleza test_garbage_at_shutdown(self):
        agiza subprocess
        code = """ikiwa 1:
            agiza gc
            agiza _testcapi
            @_testcapi.with_tp_del
            kundi X:
                eleza __init__(self, name):
                    self.name = name
                eleza __repr__(self):
                    rudisha "<X %%r>" %% self.name
                eleza __tp_del__(self):
                    pita

            x = X('first')
            x.x = x
            x.y = X('second')
            toa x
            gc.set_debug(%s)
        """
        eleza run_command(code):
            p = subprocess.Popen([sys.executable, "-Wd", "-c", code],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            p.stdout.close()
            p.stderr.close()
            self.assertEqual(p.returncode, 0)
            self.assertEqual(stdout.strip(), b"")
            rudisha strip_python_stderr(stderr)

        stderr = run_command(code % "0")
        self.assertIn(b"ResourceWarning: gc: 2 uncollectable objects at "
                      b"shutdown; use", stderr)
        self.assertNotIn(b"<X 'first'>", stderr)
        # With DEBUG_UNCOLLECTABLE, the garbage list gets printed
        stderr = run_command(code % "gc.DEBUG_UNCOLLECTABLE")
        self.assertIn(b"ResourceWarning: gc: 2 uncollectable objects at "
                      b"shutdown", stderr)
        self.assertKweli(
            (b"[<X 'first'>, <X 'second'>]" kwenye stderr) ama
            (b"[<X 'second'>, <X 'first'>]" kwenye stderr), stderr)
        # With DEBUG_SAVEALL, no additional message should get printed
        # (because gc.garbage also contains normally reclaimable cyclic
        # references, na its elements get printed at runtime anyway).
        stderr = run_command(code % "gc.DEBUG_SAVEALL")
        self.assertNotIn(b"uncollectable objects at shutdown", stderr)

    @requires_type_collecting
    eleza test_gc_main_module_at_shutdown(self):
        # Create a reference cycle through the __main__ module na check
        # it gets collected at interpreter shutdown.
        code = """ikiwa 1:
            kundi C:
                eleza __del__(self):
                    andika('__del__ called')
            l = [C()]
            l.append(l)
            """
        rc, out, err = assert_python_ok('-c', code)
        self.assertEqual(out.strip(), b'__del__ called')

    @requires_type_collecting
    eleza test_gc_ordinary_module_at_shutdown(self):
        # Same kama above, but ukijumuisha a non-__main__ module.
        ukijumuisha temp_dir() kama script_dir:
            module = """ikiwa 1:
                kundi C:
                    eleza __del__(self):
                        andika('__del__ called')
                l = [C()]
                l.append(l)
                """
            code = """ikiwa 1:
                agiza sys
                sys.path.insert(0, %r)
                agiza gctest
                """ % (script_dir,)
            make_script(script_dir, 'gctest', module)
            rc, out, err = assert_python_ok('-c', code)
            self.assertEqual(out.strip(), b'__del__ called')

    @requires_type_collecting
    eleza test_global_del_SystemExit(self):
        code = """ikiwa 1:
            kundi ClassWithDel:
                eleza __del__(self):
                    andika('__del__ called')
            a = ClassWithDel()
            a.link = a
            ashiria SystemExit(0)"""
        self.addCleanup(unlink, TESTFN)
        ukijumuisha open(TESTFN, 'w') kama script:
            script.write(code)
        rc, out, err = assert_python_ok(TESTFN)
        self.assertEqual(out.strip(), b'__del__ called')

    eleza test_get_stats(self):
        stats = gc.get_stats()
        self.assertEqual(len(stats), 3)
        kila st kwenye stats:
            self.assertIsInstance(st, dict)
            self.assertEqual(set(st),
                             {"collected", "collections", "uncollectable"})
            self.assertGreaterEqual(st["collected"], 0)
            self.assertGreaterEqual(st["collections"], 0)
            self.assertGreaterEqual(st["uncollectable"], 0)
        # Check that collection counts are incremented correctly
        ikiwa gc.isenabled():
            self.addCleanup(gc.enable)
            gc.disable()
        old = gc.get_stats()
        gc.collect(0)
        new = gc.get_stats()
        self.assertEqual(new[0]["collections"], old[0]["collections"] + 1)
        self.assertEqual(new[1]["collections"], old[1]["collections"])
        self.assertEqual(new[2]["collections"], old[2]["collections"])
        gc.collect(2)
        new = gc.get_stats()
        self.assertEqual(new[0]["collections"], old[0]["collections"] + 1)
        self.assertEqual(new[1]["collections"], old[1]["collections"])
        self.assertEqual(new[2]["collections"], old[2]["collections"] + 1)

    eleza test_freeze(self):
        gc.freeze()
        self.assertGreater(gc.get_freeze_count(), 0)
        gc.unfreeze()
        self.assertEqual(gc.get_freeze_count(), 0)

    eleza test_get_objects(self):
        gc.collect()
        l = []
        l.append(l)
        self.assertKweli(
                any(l ni element kila element kwenye gc.get_objects(generation=0))
        )
        self.assertUongo(
                any(l ni element kila element kwenye  gc.get_objects(generation=1))
        )
        self.assertUongo(
                any(l ni element kila element kwenye gc.get_objects(generation=2))
        )
        gc.collect(generation=0)
        self.assertUongo(
                any(l ni element kila element kwenye gc.get_objects(generation=0))
        )
        self.assertKweli(
                any(l ni element kila element kwenye  gc.get_objects(generation=1))
        )
        self.assertUongo(
                any(l ni element kila element kwenye gc.get_objects(generation=2))
        )
        gc.collect(generation=1)
        self.assertUongo(
                any(l ni element kila element kwenye gc.get_objects(generation=0))
        )
        self.assertUongo(
                any(l ni element kila element kwenye  gc.get_objects(generation=1))
        )
        self.assertKweli(
                any(l ni element kila element kwenye gc.get_objects(generation=2))
        )
        gc.collect(generation=2)
        self.assertUongo(
                any(l ni element kila element kwenye gc.get_objects(generation=0))
        )
        self.assertUongo(
                any(l ni element kila element kwenye  gc.get_objects(generation=1))
        )
        self.assertKweli(
                any(l ni element kila element kwenye gc.get_objects(generation=2))
        )
        toa l
        gc.collect()

    eleza test_get_objects_arguments(self):
        gc.collect()
        self.assertEqual(len(gc.get_objects()),
                         len(gc.get_objects(generation=Tupu)))

        self.assertRaises(ValueError, gc.get_objects, 1000)
        self.assertRaises(ValueError, gc.get_objects, -1000)
        self.assertRaises(TypeError, gc.get_objects, "1")
        self.assertRaises(TypeError, gc.get_objects, 1.234)

    eleza test_38379(self):
        # When a finalizer resurrects objects, stats were reporting them as
        # having been collected.  This affected both collect()'s rudisha
        # value na the dicts returned by get_stats().
        N = 100

        kundi A:  # simple self-loop
            eleza __init__(self):
                self.me = self

        kundi Z(A):  # resurrecting __del__
            eleza __del__(self):
                zs.append(self)

        zs = []

        eleza getstats():
            d = gc.get_stats()[-1]
            rudisha d['collected'], d['uncollectable']

        gc.collect()
        gc.disable()

        # No problems ikiwa just collecting A() instances.
        oldc, oldnc = getstats()
        kila i kwenye range(N):
            A()
        t = gc.collect()
        c, nc = getstats()
        self.assertEqual(t, 2*N) # instance object & its dict
        self.assertEqual(c - oldc, 2*N)
        self.assertEqual(nc - oldnc, 0)

        # But Z() ni sio actually collected.
        oldc, oldnc = c, nc
        Z()
        # Nothing ni collected - Z() ni merely resurrected.
        t = gc.collect()
        c, nc = getstats()
        #self.assertEqual(t, 2)  # before
        self.assertEqual(t, 0)  # after
        #self.assertEqual(c - oldc, 2)   # before
        self.assertEqual(c - oldc, 0)   # after
        self.assertEqual(nc - oldnc, 0)

        # Unfortunately, a Z() prevents _anything_ kutoka being collected.
        # It should be possible to collect the A instances anyway, but
        # that will require non-trivial code changes.
        oldc, oldnc = c, nc
        kila i kwenye range(N):
            A()
        Z()
        # Z() prevents anything kutoka being collected.
        t = gc.collect()
        c, nc = getstats()
        #self.assertEqual(t, 2*N + 2)  # before
        self.assertEqual(t, 0)  # after
        #self.assertEqual(c - oldc, 2*N + 2)   # before
        self.assertEqual(c - oldc, 0)   # after
        self.assertEqual(nc - oldnc, 0)

        # But the A() trash ni reclaimed on the next run.
        oldc, oldnc = c, nc
        t = gc.collect()
        c, nc = getstats()
        self.assertEqual(t, 2*N)
        self.assertEqual(c - oldc, 2*N)
        self.assertEqual(nc - oldnc, 0)

        gc.enable()

kundi GCCallbackTests(unittest.TestCase):
    eleza setUp(self):
        # Save gc state na disable it.
        self.enabled = gc.isenabled()
        gc.disable()
        self.debug = gc.get_debug()
        gc.set_debug(0)
        gc.callbacks.append(self.cb1)
        gc.callbacks.append(self.cb2)
        self.othergarbage = []

    eleza tearDown(self):
        # Restore gc state
        toa self.visit
        gc.callbacks.remove(self.cb1)
        gc.callbacks.remove(self.cb2)
        gc.set_debug(self.debug)
        ikiwa self.enabled:
            gc.enable()
        # destroy any uncollectables
        gc.collect()
        kila obj kwenye gc.garbage:
            ikiwa isinstance(obj, Uncollectable):
                obj.partner = Tupu
        toa gc.garbage[:]
        toa self.othergarbage
        gc.collect()

    eleza preclean(self):
        # Remove all fluff kutoka the system.  Invoke this function
        # manually rather than through self.setUp() kila maximum
        # safety.
        self.visit = []
        gc.collect()
        garbage, gc.garbage[:] = gc.garbage[:], []
        self.othergarbage.append(garbage)
        self.visit = []

    eleza cb1(self, phase, info):
        self.visit.append((1, phase, dict(info)))

    eleza cb2(self, phase, info):
        self.visit.append((2, phase, dict(info)))
        ikiwa phase == "stop" na hasattr(self, "cleanup"):
            # Clean Uncollectable kutoka garbage
            uc = [e kila e kwenye gc.garbage ikiwa isinstance(e, Uncollectable)]
            gc.garbage[:] = [e kila e kwenye gc.garbage
                             ikiwa sio isinstance(e, Uncollectable)]
            kila e kwenye uc:
                e.partner = Tupu

    eleza test_collect(self):
        self.preclean()
        gc.collect()
        # Algorithmically verify the contents of self.visit
        # because it ni long na tortuous.

        # Count the number of visits to each callback
        n = [v[0] kila v kwenye self.visit]
        n1 = [i kila i kwenye n ikiwa i == 1]
        n2 = [i kila i kwenye n ikiwa i == 2]
        self.assertEqual(n1, [1]*2)
        self.assertEqual(n2, [2]*2)

        # Count that we got the right number of start na stop callbacks.
        n = [v[1] kila v kwenye self.visit]
        n1 = [i kila i kwenye n ikiwa i == "start"]
        n2 = [i kila i kwenye n ikiwa i == "stop"]
        self.assertEqual(n1, ["start"]*2)
        self.assertEqual(n2, ["stop"]*2)

        # Check that we got the right info dict kila all callbacks
        kila v kwenye self.visit:
            info = v[2]
            self.assertKweli("generation" kwenye info)
            self.assertKweli("collected" kwenye info)
            self.assertKweli("uncollectable" kwenye info)

    eleza test_collect_generation(self):
        self.preclean()
        gc.collect(2)
        kila v kwenye self.visit:
            info = v[2]
            self.assertEqual(info["generation"], 2)

    @cpython_only
    eleza test_collect_garbage(self):
        self.preclean()
        # Each of these cause four objects to be garbage: Two
        # Uncollectables na their instance dicts.
        Uncollectable()
        Uncollectable()
        C1055820(666)
        gc.collect()
        kila v kwenye self.visit:
            ikiwa v[1] != "stop":
                endelea
            info = v[2]
            self.assertEqual(info["collected"], 2)
            self.assertEqual(info["uncollectable"], 8)

        # We should now have the Uncollectables kwenye gc.garbage
        self.assertEqual(len(gc.garbage), 4)
        kila e kwenye gc.garbage:
            self.assertIsInstance(e, Uncollectable)

        # Now, let our callback handle the Uncollectable instances
        self.cleanup=Kweli
        self.visit = []
        gc.garbage[:] = []
        gc.collect()
        kila v kwenye self.visit:
            ikiwa v[1] != "stop":
                endelea
            info = v[2]
            self.assertEqual(info["collected"], 0)
            self.assertEqual(info["uncollectable"], 4)

        # Uncollectables should be gone
        self.assertEqual(len(gc.garbage), 0)


    @unittest.skipIf(BUILD_WITH_NDEBUG,
                     'built ukijumuisha -NDEBUG')
    eleza test_refcount_errors(self):
        self.preclean()
        # Verify the "handling" of objects ukijumuisha broken refcounts

        # Skip the test ikiwa ctypes ni sio available
        import_module("ctypes")

        agiza subprocess
        code = textwrap.dedent('''
            kutoka test.support agiza gc_collect, SuppressCrashReport

            a = [1, 2, 3]
            b = [a]

            # Avoid coredump when Py_FatalError() calls abort()
            SuppressCrashReport().__enter__()

            # Simulate the refcount of "a" being too low (compared to the
            # references held on it by live data), but keeping it above zero
            # (to avoid deallocating it):
            agiza ctypes
            ctypes.pythonapi.Py_DecRef(ctypes.py_object(a))

            # The garbage collector should now have a fatal error
            # when it reaches the broken object
            gc_collect()
        ''')
        p = subprocess.Popen([sys.executable, "-c", code],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        p.stdout.close()
        p.stderr.close()
        # Verify that stderr has a useful error message:
        self.assertRegex(stderr,
            br'gcmodule\.c:[0-9]+: gc_decref: Assertion "gc_get_refs\(g\) > 0" failed.')
        self.assertRegex(stderr,
            br'refcount ni too small')
        self.assertRegex(stderr,
            br'object  : \[1, 2, 3\]')
        self.assertRegex(stderr,
            br'type    : list')
        self.assertRegex(stderr,
            br'refcount: 1')
        # "address : 0x7fb5062efc18"
        # "address : 7FB5062EFC18"
        self.assertRegex(stderr,
            br'address : [0-9a-fA-Fx]+')


kundi GCTogglingTests(unittest.TestCase):
    eleza setUp(self):
        gc.enable()

    eleza tearDown(self):
        gc.disable()

    eleza test_bug1055820c(self):
        # Corresponds to temp2c.py kwenye the bug report.  This ni pretty
        # elaborate.

        c0 = C1055820(0)
        # Move c0 into generation 2.
        gc.collect()

        c1 = C1055820(1)
        c1.keep_c0_alive = c0
        toa c0.loop # now only c1 keeps c0 alive

        c2 = C1055820(2)
        c2wr = weakref.ref(c2) # no callback!

        ouch = []
        eleza callback(ignored):
            ouch[:] = [c2wr()]

        # The callback gets associated ukijumuisha a wr on an object kwenye generation 2.
        c0wr = weakref.ref(c0, callback)

        c0 = c1 = c2 = Tupu

        # What we've set up:  c0, c1, na c2 are all trash now.  c0 ni kwenye
        # generation 2.  The only thing keeping it alive ni that c1 points to
        # it. c1 na c2 are kwenye generation 0, na are kwenye self-loops.  There's a
        # global weakref to c2 (c2wr), but that weakref has no callback.
        # There's also a global weakref to c0 (c0wr), na that does have a
        # callback, na that callback references c2 via c2wr().
        #
        #               c0 has a wr ukijumuisha callback, which references c2wr
        #               ^
        #               |
        #               |     Generation 2 above dots
        #. . . . . . . .|. . . . . . . . . . . . . . . . . . . . . . . .
        #               |     Generation 0 below dots
        #               |
        #               |
        #            ^->c1   ^->c2 has a wr but no callback
        #            |  |    |  |
        #            <--v    <--v
        #
        # So this ni the nightmare:  when generation 0 gets collected, we see
        # that c2 has a callback-free weakref, na c1 doesn't even have a
        # weakref.  Collecting generation 0 doesn't see c0 at all, na c0 is
        # the only object that has a weakref ukijumuisha a callback.  gc clears c1
        # na c2.  Clearing c1 has the side effect of dropping the refcount on
        # c0 to 0, so c0 goes away (despite that it's kwenye an older generation)
        # na c0's wr callback triggers.  That kwenye turn materializes a reference
        # to c2 via c2wr(), but c2 gets cleared anyway by gc.

        # We want to let gc happen "naturally", to preserve the distinction
        # between generations.
        junk = []
        i = 0
        detector = GC_Detector()
        wakati sio detector.gc_happened:
            i += 1
            ikiwa i > 10000:
                self.fail("gc didn't happen after 10000 iterations")
            self.assertEqual(len(ouch), 0)
            junk.append([])  # this will eventually trigger gc

        self.assertEqual(len(ouch), 1)  # isipokua the callback wasn't invoked
        kila x kwenye ouch:
            # If the callback resurrected c2, the instance would be damaged,
            # ukijumuisha an empty __dict__.
            self.assertEqual(x, Tupu)

    eleza test_bug1055820d(self):
        # Corresponds to temp2d.py kwenye the bug report.  This ni very much like
        # test_bug1055820c, but uses a __del__ method instead of a weakref
        # callback to sneak kwenye a resurrection of cyclic trash.

        ouch = []
        kundi D(C1055820):
            eleza __del__(self):
                ouch[:] = [c2wr()]

        d0 = D(0)
        # Move all the above into generation 2.
        gc.collect()

        c1 = C1055820(1)
        c1.keep_d0_alive = d0
        toa d0.loop # now only c1 keeps d0 alive

        c2 = C1055820(2)
        c2wr = weakref.ref(c2) # no callback!

        d0 = c1 = c2 = Tupu

        # What we've set up:  d0, c1, na c2 are all trash now.  d0 ni kwenye
        # generation 2.  The only thing keeping it alive ni that c1 points to
        # it.  c1 na c2 are kwenye generation 0, na are kwenye self-loops.  There's
        # a global weakref to c2 (c2wr), but that weakref has no callback.
        # There are no other weakrefs.
        #
        #               d0 has a __del__ method that references c2wr
        #               ^
        #               |
        #               |     Generation 2 above dots
        #. . . . . . . .|. . . . . . . . . . . . . . . . . . . . . . . .
        #               |     Generation 0 below dots
        #               |
        #               |
        #            ^->c1   ^->c2 has a wr but no callback
        #            |  |    |  |
        #            <--v    <--v
        #
        # So this ni the nightmare:  when generation 0 gets collected, we see
        # that c2 has a callback-free weakref, na c1 doesn't even have a
        # weakref.  Collecting generation 0 doesn't see d0 at all.  gc clears
        # c1 na c2.  Clearing c1 has the side effect of dropping the refcount
        # on d0 to 0, so d0 goes away (despite that it's kwenye an older
        # generation) na d0's __del__ triggers.  That kwenye turn materializes
        # a reference to c2 via c2wr(), but c2 gets cleared anyway by gc.

        # We want to let gc happen "naturally", to preserve the distinction
        # between generations.
        detector = GC_Detector()
        junk = []
        i = 0
        wakati sio detector.gc_happened:
            i += 1
            ikiwa i > 10000:
                self.fail("gc didn't happen after 10000 iterations")
            self.assertEqual(len(ouch), 0)
            junk.append([])  # this will eventually trigger gc

        self.assertEqual(len(ouch), 1)  # isipokua __del__ wasn't invoked
        kila x kwenye ouch:
            # If __del__ resurrected c2, the instance would be damaged, ukijumuisha an
            # empty __dict__.
            self.assertEqual(x, Tupu)

eleza test_main():
    enabled = gc.isenabled()
    gc.disable()
    assert sio gc.isenabled()
    debug = gc.get_debug()
    gc.set_debug(debug & ~gc.DEBUG_LEAK) # this test ni supposed to leak

    jaribu:
        gc.collect() # Delete 2nd generation garbage
        run_unittest(GCTests, GCTogglingTests, GCCallbackTests)
    mwishowe:
        gc.set_debug(debug)
        # test gc.enable() even ikiwa GC ni disabled by default
        ikiwa verbose:
            andika("restoring automatic collection")
        # make sure to always test gc.enable()
        gc.enable()
        assert gc.isenabled()
        ikiwa sio enabled:
            gc.disable()

ikiwa __name__ == "__main__":
    test_main()
