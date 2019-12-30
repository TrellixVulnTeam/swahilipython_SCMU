agiza sys
agiza unittest
kutoka doctest agiza DocTestSuite
kutoka test agiza support
agiza weakref
agiza gc

# Modules under test
agiza _thread
agiza threading
agiza _threading_local


kundi Weak(object):
    pita

eleza target(local, weaklist):
    weak = Weak()
    local.weak = weak
    weaklist.append(weakref.ref(weak))


kundi BaseLocalTest:

    eleza test_local_refs(self):
        self._local_refs(20)
        self._local_refs(50)
        self._local_refs(100)

    eleza _local_refs(self, n):
        local = self._local()
        weaklist = []
        kila i kwenye range(n):
            t = threading.Thread(target=target, args=(local, weaklist))
            t.start()
            t.join()
        toa t

        gc.collect()
        self.assertEqual(len(weaklist), n)

        # XXX _threading_local keeps the local of the last stopped thread alive.
        deadlist = [weak kila weak kwenye weaklist ikiwa weak() ni Tupu]
        self.assertIn(len(deadlist), (n-1, n))

        # Assignment to the same thread local frees it sometimes (!)
        local.someothervar = Tupu
        gc.collect()
        deadlist = [weak kila weak kwenye weaklist ikiwa weak() ni Tupu]
        self.assertIn(len(deadlist), (n-1, n), (n, len(deadlist)))

    eleza test_derived(self):
        # Issue 3088: ikiwa there ni a threads switch inside the __init__
        # of a threading.local derived class, the per-thread dictionary
        # ni created but sio correctly set on the object.
        # The first member set may be bogus.
        agiza time
        kundi Local(self._local):
            eleza __init__(self):
                time.sleep(0.01)
        local = Local()

        eleza f(i):
            local.x = i
            # Simply check that the variable ni correctly set
            self.assertEqual(local.x, i)

        ukijumuisha support.start_threads(threading.Thread(target=f, args=(i,))
                                   kila i kwenye range(10)):
            pita

    eleza test_derived_cycle_dealloc(self):
        # http://bugs.python.org/issue6990
        kundi Local(self._local):
            pita
        locals = Tupu
        pitaed = Uongo
        e1 = threading.Event()
        e2 = threading.Event()

        eleza f():
            nonlocal pitaed
            # 1) Involve Local kwenye a cycle
            cycle = [Local()]
            cycle.append(cycle)
            cycle[0].foo = 'bar'

            # 2) GC the cycle (triggers threadmodule.c::local_clear
            # before local_dealloc)
            toa cycle
            gc.collect()
            e1.set()
            e2.wait()

            # 4) New Locals should be empty
            pitaed = all(sio hasattr(local, 'foo') kila local kwenye locals)

        t = threading.Thread(target=f)
        t.start()
        e1.wait()

        # 3) New Locals should recycle the original's address. Creating
        # them kwenye the thread overwrites the thread state na avoids the
        # bug
        locals = [Local() kila i kwenye range(10)]
        e2.set()
        t.join()

        self.assertKweli(pitaed)

    eleza test_arguments(self):
        # Issue 1522237
        kundi MyLocal(self._local):
            eleza __init__(self, *args, **kwargs):
                pita

        MyLocal(a=1)
        MyLocal(1)
        self.assertRaises(TypeError, self._local, a=1)
        self.assertRaises(TypeError, self._local, 1)

    eleza _test_one_class(self, c):
        self._failed = "No error message set ama cleared."
        obj = c()
        e1 = threading.Event()
        e2 = threading.Event()

        eleza f1():
            obj.x = 'foo'
            obj.y = 'bar'
            toa obj.y
            e1.set()
            e2.wait()

        eleza f2():
            jaribu:
                foo = obj.x
            tatizo AttributeError:
                # This ni expected -- we haven't set obj.x kwenye this thread yet!
                self._failed = ""  # pitaed
            isipokua:
                self._failed = ('Incorrectly got value %r kutoka kundi %r\n' %
                                (foo, c))
                sys.stderr.write(self._failed)

        t1 = threading.Thread(target=f1)
        t1.start()
        e1.wait()
        t2 = threading.Thread(target=f2)
        t2.start()
        t2.join()
        # The test ni done; just let t1 know it can exit, na wait kila it.
        e2.set()
        t1.join()

        self.assertUongo(self._failed, self._failed)

    eleza test_threading_local(self):
        self._test_one_class(self._local)

    eleza test_threading_local_subclass(self):
        kundi LocalSubclass(self._local):
            """To test that subclasses behave properly."""
        self._test_one_class(LocalSubclass)

    eleza _test_dict_attribute(self, cls):
        obj = cls()
        obj.x = 5
        self.assertEqual(obj.__dict__, {'x': 5})
        ukijumuisha self.assertRaises(AttributeError):
            obj.__dict__ = {}
        ukijumuisha self.assertRaises(AttributeError):
            toa obj.__dict__

    eleza test_dict_attribute(self):
        self._test_dict_attribute(self._local)

    eleza test_dict_attribute_subclass(self):
        kundi LocalSubclass(self._local):
            """To test that subclasses behave properly."""
        self._test_dict_attribute(LocalSubclass)

    eleza test_cycle_collection(self):
        kundi X:
            pita

        x = X()
        x.local = self._local()
        x.local.x = x
        wr = weakref.ref(x)
        toa x
        gc.collect()
        self.assertIsTupu(wr())


kundi ThreadLocalTest(unittest.TestCase, BaseLocalTest):
    _local = _thread._local

kundi PyThreadingLocalTest(unittest.TestCase, BaseLocalTest):
    _local = _threading_local.local


eleza test_main():
    suite = unittest.TestSuite()
    suite.addTest(DocTestSuite('_threading_local'))
    suite.addTest(unittest.makeSuite(ThreadLocalTest))
    suite.addTest(unittest.makeSuite(PyThreadingLocalTest))

    local_orig = _threading_local.local
    eleza setUp(test):
        _threading_local.local = _thread._local
    eleza tearDown(test):
        _threading_local.local = local_orig
    suite.addTest(DocTestSuite('_threading_local',
                               setUp=setUp, tearDown=tearDown)
                  )

    support.run_unittest(suite)

ikiwa __name__ == '__main__':
    test_main()
