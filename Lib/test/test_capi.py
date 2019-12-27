# Run the _testcapi module tests (tests for the Python/C API):  by defn,
# these are all functions _testcapi exports whose name begins with 'test_'.

kutoka collections agiza OrderedDict
agiza os
agiza pickle
agiza random
agiza re
agiza subprocess
agiza sys
agiza textwrap
agiza threading
agiza time
agiza unittest
kutoka test agiza support
kutoka test.support agiza MISSING_C_DOCSTRINGS
kutoka test.support.script_helper agiza assert_python_failure, assert_python_ok
try:
    agiza _posixsubprocess
except ImportError:
    _posixsubprocess = None

# Skip this test ikiwa the _testcapi module isn't available.
_testcapi = support.import_module('_testcapi')

# Were we compiled --with-pydebug or with #define Py_DEBUG?
Py_DEBUG = hasattr(sys, 'gettotalrefcount')


eleza testfunction(self):
    """some doc"""
    rudisha self


kundi InstanceMethod:
    id = _testcapi.instancemethod(id)
    testfunction = _testcapi.instancemethod(testfunction)

kundi CAPITest(unittest.TestCase):

    eleza test_instancemethod(self):
        inst = InstanceMethod()
        self.assertEqual(id(inst), inst.id())
        self.assertTrue(inst.testfunction() is inst)
        self.assertEqual(inst.testfunction.__doc__, testfunction.__doc__)
        self.assertEqual(InstanceMethod.testfunction.__doc__, testfunction.__doc__)

        InstanceMethod.testfunction.attribute = "test"
        self.assertEqual(testfunction.attribute, "test")
        self.assertRaises(AttributeError, setattr, inst.testfunction, "attribute", "test")

    eleza test_no_FatalError_infinite_loop(self):
        with support.SuppressCrashReport():
            p = subprocess.Popen([sys.executable, "-c",
                                  'agiza _testcapi;'
                                  '_testcapi.crash_no_current_thread()'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        (out, err) = p.communicate()
        self.assertEqual(out, b'')
        # This used to cause an infinite loop.
        self.assertTrue(err.rstrip().startswith(
                         b'Fatal Python error:'
                         b' PyThreadState_Get: no current thread'))

    eleza test_memoryview_kutoka_NULL_pointer(self):
        self.assertRaises(ValueError, _testcapi.make_memoryview_kutoka_NULL_pointer)

    eleza test_exc_info(self):
        raised_exception = ValueError("5")
        new_exc = TypeError("TEST")
        try:
            raise raised_exception
        except ValueError as e:
            tb = e.__traceback__
            orig_sys_exc_info = sys.exc_info()
            orig_exc_info = _testcapi.set_exc_info(new_exc.__class__, new_exc, None)
            new_sys_exc_info = sys.exc_info()
            new_exc_info = _testcapi.set_exc_info(*orig_exc_info)
            reset_sys_exc_info = sys.exc_info()

            self.assertEqual(orig_exc_info[1], e)

            self.assertSequenceEqual(orig_exc_info, (raised_exception.__class__, raised_exception, tb))
            self.assertSequenceEqual(orig_sys_exc_info, orig_exc_info)
            self.assertSequenceEqual(reset_sys_exc_info, orig_exc_info)
            self.assertSequenceEqual(new_exc_info, (new_exc.__class__, new_exc, None))
            self.assertSequenceEqual(new_sys_exc_info, new_exc_info)
        else:
            self.assertTrue(False)

    @unittest.skipUnless(_posixsubprocess, '_posixsubprocess required for this test.')
    eleza test_seq_bytes_to_charp_array(self):
        # Issue #15732: crash in _PySequence_BytesToCharpArray()
        kundi Z(object):
            eleza __len__(self):
                rudisha 1
        self.assertRaises(TypeError, _posixsubprocess.fork_exec,
                          1,Z(),3,(1, 2),5,6,7,8,9,10,11,12,13,14,15,16,17)
        # Issue #15736: overflow in _PySequence_BytesToCharpArray()
        kundi Z(object):
            eleza __len__(self):
                rudisha sys.maxsize
            eleza __getitem__(self, i):
                rudisha b'x'
        self.assertRaises(MemoryError, _posixsubprocess.fork_exec,
                          1,Z(),3,(1, 2),5,6,7,8,9,10,11,12,13,14,15,16,17)

    @unittest.skipUnless(_posixsubprocess, '_posixsubprocess required for this test.')
    eleza test_subprocess_fork_exec(self):
        kundi Z(object):
            eleza __len__(self):
                rudisha 1

        # Issue #15738: crash in subprocess_fork_exec()
        self.assertRaises(TypeError, _posixsubprocess.fork_exec,
                          Z(),[b'1'],3,(1, 2),5,6,7,8,9,10,11,12,13,14,15,16,17)

    @unittest.skipIf(MISSING_C_DOCSTRINGS,
                     "Signature information for builtins requires docstrings")
    eleza test_docstring_signature_parsing(self):

        self.assertEqual(_testcapi.no_docstring.__doc__, None)
        self.assertEqual(_testcapi.no_docstring.__text_signature__, None)

        self.assertEqual(_testcapi.docstring_empty.__doc__, None)
        self.assertEqual(_testcapi.docstring_empty.__text_signature__, None)

        self.assertEqual(_testcapi.docstring_no_signature.__doc__,
            "This docstring has no signature.")
        self.assertEqual(_testcapi.docstring_no_signature.__text_signature__, None)

        self.assertEqual(_testcapi.docstring_with_invalid_signature.__doc__,
            "docstring_with_invalid_signature($module, /, boo)\n"
            "\n"
            "This docstring has an invalid signature."
            )
        self.assertEqual(_testcapi.docstring_with_invalid_signature.__text_signature__, None)

        self.assertEqual(_testcapi.docstring_with_invalid_signature2.__doc__,
            "docstring_with_invalid_signature2($module, /, boo)\n"
            "\n"
            "--\n"
            "\n"
            "This docstring also has an invalid signature."
            )
        self.assertEqual(_testcapi.docstring_with_invalid_signature2.__text_signature__, None)

        self.assertEqual(_testcapi.docstring_with_signature.__doc__,
            "This docstring has a valid signature.")
        self.assertEqual(_testcapi.docstring_with_signature.__text_signature__, "($module, /, sig)")

        self.assertEqual(_testcapi.docstring_with_signature_but_no_doc.__doc__, None)
        self.assertEqual(_testcapi.docstring_with_signature_but_no_doc.__text_signature__,
            "($module, /, sig)")

        self.assertEqual(_testcapi.docstring_with_signature_and_extra_newlines.__doc__,
            "\nThis docstring has a valid signature and some extra newlines.")
        self.assertEqual(_testcapi.docstring_with_signature_and_extra_newlines.__text_signature__,
            "($module, /, parameter)")

    eleza test_c_type_with_matrix_multiplication(self):
        M = _testcapi.matmulType
        m1 = M()
        m2 = M()
        self.assertEqual(m1 @ m2, ("matmul", m1, m2))
        self.assertEqual(m1 @ 42, ("matmul", m1, 42))
        self.assertEqual(42 @ m1, ("matmul", 42, m1))
        o = m1
        o @= m2
        self.assertEqual(o, ("imatmul", m1, m2))
        o = m1
        o @= 42
        self.assertEqual(o, ("imatmul", m1, 42))
        o = 42
        o @= m1
        self.assertEqual(o, ("matmul", 42, m1))

    eleza test_c_type_with_ipow(self):
        # When the __ipow__ method of a type was implemented in C, using the
        # modulo param would cause segfaults.
        o = _testcapi.ipowType()
        self.assertEqual(o.__ipow__(1), (1, None))
        self.assertEqual(o.__ipow__(2, 2), (2, 2))

    eleza test_return_null_without_error(self):
        # Issue #23571: A function must not rudisha NULL without setting an
        # error
        ikiwa Py_DEBUG:
            code = textwrap.dedent("""
                agiza _testcapi
                kutoka test agiza support

                with support.SuppressCrashReport():
                    _testcapi.return_null_without_error()
            """)
            rc, out, err = assert_python_failure('-c', code)
            self.assertRegex(err.replace(b'\r', b''),
                             br'Fatal Python error: a function returned NULL '
                                br'without setting an error\n'
                             br'Python runtime state: initialized\n'
                             br'SystemError: <built-in function '
                                 br'return_null_without_error> returned NULL '
                                 br'without setting an error\n'
                             br'\n'
                             br'Current thread.*:\n'
                             br'  File .*", line 6 in <module>')
        else:
            with self.assertRaises(SystemError) as cm:
                _testcapi.return_null_without_error()
            self.assertRegex(str(cm.exception),
                             'return_null_without_error.* '
                             'returned NULL without setting an error')

    eleza test_return_result_with_error(self):
        # Issue #23571: A function must not rudisha a result with an error set
        ikiwa Py_DEBUG:
            code = textwrap.dedent("""
                agiza _testcapi
                kutoka test agiza support

                with support.SuppressCrashReport():
                    _testcapi.return_result_with_error()
            """)
            rc, out, err = assert_python_failure('-c', code)
            self.assertRegex(err.replace(b'\r', b''),
                             br'Fatal Python error: a function returned a '
                                br'result with an error set\n'
                             br'Python runtime state: initialized\n'
                             br'ValueError\n'
                             br'\n'
                             br'The above exception was the direct cause '
                                br'of the following exception:\n'
                             br'\n'
                             br'SystemError: <built-in '
                                br'function return_result_with_error> '
                                br'returned a result with an error set\n'
                             br'\n'
                             br'Current thread.*:\n'
                             br'  File .*, line 6 in <module>')
        else:
            with self.assertRaises(SystemError) as cm:
                _testcapi.return_result_with_error()
            self.assertRegex(str(cm.exception),
                             'return_result_with_error.* '
                             'returned a result with an error set')

    eleza test_buildvalue_N(self):
        _testcapi.test_buildvalue_N()

    eleza test_set_nomemory(self):
        code = """ikiwa 1:
            agiza _testcapi

            kundi C(): pass

            # The first loop tests both functions and that remove_mem_hooks()
            # can be called twice in a row. The second loop checks a call to
            # set_nomemory() after a call to remove_mem_hooks(). The third
            # loop checks the start and stop arguments of set_nomemory().
            for outer_cnt in range(1, 4):
                start = 10 * outer_cnt
                for j in range(100):
                    ikiwa j == 0:
                        ikiwa outer_cnt != 3:
                            _testcapi.set_nomemory(start)
                        else:
                            _testcapi.set_nomemory(start, start + 1)
                    try:
                        C()
                    except MemoryError as e:
                        ikiwa outer_cnt != 3:
                            _testcapi.remove_mem_hooks()
                        andika('MemoryError', outer_cnt, j)
                        _testcapi.remove_mem_hooks()
                        break
        """
        rc, out, err = assert_python_ok('-c', code)
        self.assertIn(b'MemoryError 1 10', out)
        self.assertIn(b'MemoryError 2 20', out)
        self.assertIn(b'MemoryError 3 30', out)

    eleza test_mapping_keys_values_items(self):
        kundi Mapping1(dict):
            eleza keys(self):
                rudisha list(super().keys())
            eleza values(self):
                rudisha list(super().values())
            eleza items(self):
                rudisha list(super().items())
        kundi Mapping2(dict):
            eleza keys(self):
                rudisha tuple(super().keys())
            eleza values(self):
                rudisha tuple(super().values())
            eleza items(self):
                rudisha tuple(super().items())
        dict_obj = {'foo': 1, 'bar': 2, 'spam': 3}

        for mapping in [{}, OrderedDict(), Mapping1(), Mapping2(),
                        dict_obj, OrderedDict(dict_obj),
                        Mapping1(dict_obj), Mapping2(dict_obj)]:
            self.assertListEqual(_testcapi.get_mapping_keys(mapping),
                                 list(mapping.keys()))
            self.assertListEqual(_testcapi.get_mapping_values(mapping),
                                 list(mapping.values()))
            self.assertListEqual(_testcapi.get_mapping_items(mapping),
                                 list(mapping.items()))

    eleza test_mapping_keys_values_items_bad_arg(self):
        self.assertRaises(AttributeError, _testcapi.get_mapping_keys, None)
        self.assertRaises(AttributeError, _testcapi.get_mapping_values, None)
        self.assertRaises(AttributeError, _testcapi.get_mapping_items, None)

        kundi BadMapping:
            eleza keys(self):
                rudisha None
            eleza values(self):
                rudisha None
            eleza items(self):
                rudisha None
        bad_mapping = BadMapping()
        self.assertRaises(TypeError, _testcapi.get_mapping_keys, bad_mapping)
        self.assertRaises(TypeError, _testcapi.get_mapping_values, bad_mapping)
        self.assertRaises(TypeError, _testcapi.get_mapping_items, bad_mapping)

    @unittest.skipUnless(hasattr(_testcapi, 'negative_refcount'),
                         'need _testcapi.negative_refcount')
    eleza test_negative_refcount(self):
        # bpo-35059: Check that Py_DECREF() reports the correct filename
        # when calling _Py_NegativeRefcount() to abort Python.
        code = textwrap.dedent("""
            agiza _testcapi
            kutoka test agiza support

            with support.SuppressCrashReport():
                _testcapi.negative_refcount()
        """)
        rc, out, err = assert_python_failure('-c', code)
        self.assertRegex(err,
                         br'_testcapimodule\.c:[0-9]+: '
                         br'_Py_NegativeRefcount: Assertion failed: '
                         br'object has negative ref count')

    eleza test_trashcan_subclass(self):
        # bpo-35983: Check that the trashcan mechanism for "list" is NOT
        # activated when its tp_dealloc is being called by a subclass
        kutoka _testcapi agiza MyList
        L = None
        for i in range(1000):
            L = MyList((L,))

    eleza test_trashcan_python_class1(self):
        self.do_test_trashcan_python_class(list)

    eleza test_trashcan_python_class2(self):
        kutoka _testcapi agiza MyList
        self.do_test_trashcan_python_class(MyList)

    eleza do_test_trashcan_python_class(self, base):
        # Check that the trashcan mechanism works properly for a Python
        # subkundi of a kundi using the trashcan (this specific test assumes
        # that the base kundi "base" behaves like list)
        kundi PyList(base):
            # Count the number of PyList instances to verify that there is
            # no memory leak
            num = 0
            eleza __init__(self, *args):
                __class__.num += 1
                super().__init__(*args)
            eleza __del__(self):
                __class__.num -= 1

        for parity in (0, 1):
            L = None
            # We need in the order of 2**20 iterations here such that a
            # typical 8MB stack would overflow without the trashcan.
            for i in range(2**20):
                L = PyList((L,))
                L.attr = i
            ikiwa parity:
                # Add one additional nesting layer
                L = (L,)
            self.assertGreater(PyList.num, 0)
            del L
            self.assertEqual(PyList.num, 0)

    eleza test_subclass_of_heap_gc_ctype_with_tpdealloc_decrefs_once(self):
        kundi HeapGcCTypeSubclass(_testcapi.HeapGcCType):
            eleza __init__(self):
                self.value2 = 20
                super().__init__()

        subclass_instance = HeapGcCTypeSubclass()
        type_refcnt = sys.getrefcount(HeapGcCTypeSubclass)

        # Test that subkundi instance was fully created
        self.assertEqual(subclass_instance.value, 10)
        self.assertEqual(subclass_instance.value2, 20)

        # Test that the type reference count is only decremented once
        del subclass_instance
        self.assertEqual(type_refcnt - 1, sys.getrefcount(HeapGcCTypeSubclass))

    eleza test_subclass_of_heap_gc_ctype_with_del_modifying_dunder_class_only_decrefs_once(self):
        kundi A(_testcapi.HeapGcCType):
            eleza __init__(self):
                self.value2 = 20
                super().__init__()

        kundi B(A):
            eleza __init__(self):
                super().__init__()

            eleza __del__(self):
                self.__class__ = A
                A.refcnt_in_del = sys.getrefcount(A)
                B.refcnt_in_del = sys.getrefcount(B)

        subclass_instance = B()
        type_refcnt = sys.getrefcount(B)
        new_type_refcnt = sys.getrefcount(A)

        # Test that subkundi instance was fully created
        self.assertEqual(subclass_instance.value, 10)
        self.assertEqual(subclass_instance.value2, 20)

        del subclass_instance

        # Test that setting __class__ modified the reference counts of the types
        self.assertEqual(type_refcnt - 1, B.refcnt_in_del)
        self.assertEqual(new_type_refcnt + 1, A.refcnt_in_del)

        # Test that the original type already has decreased its refcnt
        self.assertEqual(type_refcnt - 1, sys.getrefcount(B))

        # Test that subtype_dealloc decref the newly assigned __class__ only once
        self.assertEqual(new_type_refcnt, sys.getrefcount(A))

    eleza test_c_subclass_of_heap_ctype_with_tpdealloc_decrefs_once(self):
        subclass_instance = _testcapi.HeapCTypeSubclass()
        type_refcnt = sys.getrefcount(_testcapi.HeapCTypeSubclass)

        # Test that subkundi instance was fully created
        self.assertEqual(subclass_instance.value, 10)
        self.assertEqual(subclass_instance.value2, 20)

        # Test that the type reference count is only decremented once
        del subclass_instance
        self.assertEqual(type_refcnt - 1, sys.getrefcount(_testcapi.HeapCTypeSubclass))

    eleza test_c_subclass_of_heap_ctype_with_del_modifying_dunder_class_only_decrefs_once(self):
        subclass_instance = _testcapi.HeapCTypeSubclassWithFinalizer()
        type_refcnt = sys.getrefcount(_testcapi.HeapCTypeSubclassWithFinalizer)
        new_type_refcnt = sys.getrefcount(_testcapi.HeapCTypeSubclass)

        # Test that subkundi instance was fully created
        self.assertEqual(subclass_instance.value, 10)
        self.assertEqual(subclass_instance.value2, 20)

        # The tp_finalize slot will set __class__ to HeapCTypeSubclass
        del subclass_instance

        # Test that setting __class__ modified the reference counts of the types
        self.assertEqual(type_refcnt - 1, _testcapi.HeapCTypeSubclassWithFinalizer.refcnt_in_del)
        self.assertEqual(new_type_refcnt + 1, _testcapi.HeapCTypeSubclass.refcnt_in_del)

        # Test that the original type already has decreased its refcnt
        self.assertEqual(type_refcnt - 1, sys.getrefcount(_testcapi.HeapCTypeSubclassWithFinalizer))

        # Test that subtype_dealloc decref the newly assigned __class__ only once
        self.assertEqual(new_type_refcnt, sys.getrefcount(_testcapi.HeapCTypeSubclass))


kundi TestPendingCalls(unittest.TestCase):

    eleza pendingcalls_submit(self, l, n):
        eleza callback():
            #this function can be interrupted by thread switching so let's
            #use an atomic operation
            l.append(None)

        for i in range(n):
            time.sleep(random.random()*0.02) #0.01 secs on average
            #try submitting callback until successful.
            #rely on regular interrupt to flush queue ikiwa we are
            #unsuccessful.
            while True:
                ikiwa _testcapi._pending_threadfunc(callback):
                    break;

    eleza pendingcalls_wait(self, l, n, context = None):
        #now, stick around until l[0] has grown to 10
        count = 0;
        while len(l) != n:
            #this busy loop is where we expect to be interrupted to
            #run our callbacks.  Note that callbacks are only run on the
            #main thread
            ikiwa False and support.verbose:
                andika("(%i)"%(len(l),),)
            for i in range(1000):
                a = i*i
            ikiwa context and not context.event.is_set():
                continue
            count += 1
            self.assertTrue(count < 10000,
                "timeout waiting for %i callbacks, got %i"%(n, len(l)))
        ikiwa False and support.verbose:
            andika("(%i)"%(len(l),))

    eleza test_pendingcalls_threaded(self):

        #do every callback on a separate thread
        n = 32 #total callbacks
        threads = []
        kundi foo(object):pass
        context = foo()
        context.l = []
        context.n = 2 #submits per thread
        context.nThreads = n // context.n
        context.nFinished = 0
        context.lock = threading.Lock()
        context.event = threading.Event()

        threads = [threading.Thread(target=self.pendingcalls_thread,
                                    args=(context,))
                   for i in range(context.nThreads)]
        with support.start_threads(threads):
            self.pendingcalls_wait(context.l, n, context)

    eleza pendingcalls_thread(self, context):
        try:
            self.pendingcalls_submit(context.l, context.n)
        finally:
            with context.lock:
                context.nFinished += 1
                nFinished = context.nFinished
                ikiwa False and support.verbose:
                    andika("finished threads: ", nFinished)
            ikiwa nFinished == context.nThreads:
                context.event.set()

    eleza test_pendingcalls_non_threaded(self):
        #again, just using the main thread, likely they will all be dispatched at
        #once.  It is ok to ask for too many, because we loop until we find a slot.
        #the loop can be interrupted to dispatch.
        #there are only 32 dispatch slots, so we go for twice that!
        l = []
        n = 64
        self.pendingcalls_submit(l, n)
        self.pendingcalls_wait(l, n)


kundi SubinterpreterTest(unittest.TestCase):

    eleza test_subinterps(self):
        agiza builtins
        r, w = os.pipe()
        code = """ikiwa 1:
            agiza sys, builtins, pickle
            with open({:d}, "wb") as f:
                pickle.dump(id(sys.modules), f)
                pickle.dump(id(builtins), f)
            """.format(w)
        with open(r, "rb") as f:
            ret = support.run_in_subinterp(code)
            self.assertEqual(ret, 0)
            self.assertNotEqual(pickle.load(f), id(sys.modules))
            self.assertNotEqual(pickle.load(f), id(builtins))

    eleza test_mutate_exception(self):
        """
        Exceptions saved in global module state get shared between
        individual module instances. This test checks whether or not
        a change in one interpreter's module gets reflected into the
        other ones.
        """
        agiza binascii

        support.run_in_subinterp("agiza binascii; binascii.Error.foobar = 'foobar'")

        self.assertFalse(hasattr(binascii.Error, "foobar"))


kundi TestThreadState(unittest.TestCase):

    @support.reap_threads
    eleza test_thread_state(self):
        # some extra thread-state tests driven via _testcapi
        eleza target():
            idents = []

            eleza callback():
                idents.append(threading.get_ident())

            _testcapi._test_thread_state(callback)
            a = b = callback
            time.sleep(1)
            # Check our main thread is in the list exactly 3 times.
            self.assertEqual(idents.count(threading.get_ident()), 3,
                             "Couldn't find main thread correctly in the list")

        target()
        t = threading.Thread(target=target)
        t.start()
        t.join()


kundi Test_testcapi(unittest.TestCase):
    locals().update((name, getattr(_testcapi, name))
                    for name in dir(_testcapi)
                    ikiwa name.startswith('test_') and not name.endswith('_code'))


kundi PyMemDebugTests(unittest.TestCase):
    PYTHONMALLOC = 'debug'
    # '0x04c06e0' or '04C06E0'
    PTR_REGEX = r'(?:0x)?[0-9a-fA-F]+'

    eleza check(self, code):
        with support.SuppressCrashReport():
            out = assert_python_failure('-c', code,
                                        PYTHONMALLOC=self.PYTHONMALLOC)
        stderr = out.err
        rudisha stderr.decode('ascii', 'replace')

    eleza test_buffer_overflow(self):
        out = self.check('agiza _testcapi; _testcapi.pymem_buffer_overflow()')
        regex = (r"Debug memory block at address p={ptr}: API 'm'\n"
                 r"    16 bytes originally requested\n"
                 r"    The [0-9] pad bytes at p-[0-9] are FORBIDDENBYTE, as expected.\n"
                 r"    The [0-9] pad bytes at tail={ptr} are not all FORBIDDENBYTE \(0x[0-9a-f]{{2}}\):\n"
                 r"        at tail\+0: 0x78 \*\*\* OUCH\n"
                 r"        at tail\+1: 0xfd\n"
                 r"        at tail\+2: 0xfd\n"
                 r"        .*\n"
                 r"(    The block was made by call #[0-9]+ to debug malloc/realloc.\n)?"
                 r"    Data at p: cd cd cd .*\n"
                 r"\n"
                 r"Enable tracemalloc to get the memory block allocation traceback\n"
                 r"\n"
                 r"Fatal Python error: bad trailing pad byte")
        regex = regex.format(ptr=self.PTR_REGEX)
        regex = re.compile(regex, flags=re.DOTALL)
        self.assertRegex(out, regex)

    eleza test_api_misuse(self):
        out = self.check('agiza _testcapi; _testcapi.pymem_api_misuse()')
        regex = (r"Debug memory block at address p={ptr}: API 'm'\n"
                 r"    16 bytes originally requested\n"
                 r"    The [0-9] pad bytes at p-[0-9] are FORBIDDENBYTE, as expected.\n"
                 r"    The [0-9] pad bytes at tail={ptr} are FORBIDDENBYTE, as expected.\n"
                 r"(    The block was made by call #[0-9]+ to debug malloc/realloc.\n)?"
                 r"    Data at p: cd cd cd .*\n"
                 r"\n"
                 r"Enable tracemalloc to get the memory block allocation traceback\n"
                 r"\n"
                 r"Fatal Python error: bad ID: Allocated using API 'm', verified using API 'r'\n")
        regex = regex.format(ptr=self.PTR_REGEX)
        self.assertRegex(out, regex)

    eleza check_malloc_without_gil(self, code):
        out = self.check(code)
        expected = ('Fatal Python error: Python memory allocator called '
                    'without holding the GIL')
        self.assertIn(expected, out)

    eleza test_pymem_malloc_without_gil(self):
        # Debug hooks must raise an error ikiwa PyMem_Malloc() is called
        # without holding the GIL
        code = 'agiza _testcapi; _testcapi.pymem_malloc_without_gil()'
        self.check_malloc_without_gil(code)

    eleza test_pyobject_malloc_without_gil(self):
        # Debug hooks must raise an error ikiwa PyObject_Malloc() is called
        # without holding the GIL
        code = 'agiza _testcapi; _testcapi.pyobject_malloc_without_gil()'
        self.check_malloc_without_gil(code)

    eleza check_pyobject_is_freed(self, func_name):
        code = textwrap.dedent(f'''
            agiza gc, os, sys, _testcapi
            # Disable the GC to avoid crash on GC collection
            gc.disable()
            try:
                _testcapi.{func_name}()
                # Exit immediately to avoid a crash while deallocating
                # the invalid object
                os._exit(0)
            except _testcapi.error:
                os._exit(1)
        ''')
        assert_python_ok('-c', code, PYTHONMALLOC=self.PYTHONMALLOC)

    eleza test_pyobject_uninitialized_is_freed(self):
        self.check_pyobject_is_freed('check_pyobject_uninitialized_is_freed')

    eleza test_pyobject_forbidden_bytes_is_freed(self):
        self.check_pyobject_is_freed('check_pyobject_forbidden_bytes_is_freed')

    eleza test_pyobject_freed_is_freed(self):
        self.check_pyobject_is_freed('check_pyobject_freed_is_freed')


kundi PyMemMallocDebugTests(PyMemDebugTests):
    PYTHONMALLOC = 'malloc_debug'


@unittest.skipUnless(support.with_pymalloc(), 'need pymalloc')
kundi PyMemPymallocDebugTests(PyMemDebugTests):
    PYTHONMALLOC = 'pymalloc_debug'


@unittest.skipUnless(Py_DEBUG, 'need Py_DEBUG')
kundi PyMemDefaultTests(PyMemDebugTests):
    # test default allocator of Python compiled in debug mode
    PYTHONMALLOC = ''


ikiwa __name__ == "__main__":
    unittest.main()
