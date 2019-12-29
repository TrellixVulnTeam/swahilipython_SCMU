agiza contextlib
agiza os
agiza sys
agiza tracemalloc
agiza unittest
kutoka unittest.mock agiza patch
kutoka test.support.script_helper agiza (assert_python_ok, assert_python_failure,
                                        interpreter_requires_environment)
kutoka test agiza support

jaribu:
    agiza _testcapi
tatizo ImportError:
    _testcapi = Tupu


EMPTY_STRING_SIZE = sys.getsizeof(b'')
INVALID_NFRAME = (-1, 2**30)


eleza get_frames(nframe, lineno_delta):
    frames = []
    frame = sys._getframe(1)
    kila index kwenye range(nframe):
        code = frame.f_code
        lineno = frame.f_lineno + lineno_delta
        frames.append((code.co_filename, lineno))
        lineno_delta = 0
        frame = frame.f_back
        ikiwa frame ni Tupu:
            koma
    rudisha tuple(frames)

eleza allocate_bytes(size):
    nframe = tracemalloc.get_traceback_limit()
    bytes_len = (size - EMPTY_STRING_SIZE)
    frames = get_frames(nframe, 1)
    data = b'x' * bytes_len
    rudisha data, tracemalloc.Traceback(frames)

eleza create_snapshots():
    traceback_limit = 2

    # _tracemalloc._get_traces() rudishas a list of (domain, size,
    # traceback_frames) tuples. traceback_frames ni a tuple of (filename,
    # line_number) tuples.
    raw_traces = [
        (0, 10, (('a.py', 2), ('b.py', 4))),
        (0, 10, (('a.py', 2), ('b.py', 4))),
        (0, 10, (('a.py', 2), ('b.py', 4))),

        (1, 2, (('a.py', 5), ('b.py', 4))),

        (2, 66, (('b.py', 1),)),

        (3, 7, (('<unknown>', 0),)),
    ]
    snapshot = tracemalloc.Snapshot(raw_traces, traceback_limit)

    raw_traces2 = [
        (0, 10, (('a.py', 2), ('b.py', 4))),
        (0, 10, (('a.py', 2), ('b.py', 4))),
        (0, 10, (('a.py', 2), ('b.py', 4))),

        (2, 2, (('a.py', 5), ('b.py', 4))),
        (2, 5000, (('a.py', 5), ('b.py', 4))),

        (4, 400, (('c.py', 578),)),
    ]
    snapshot2 = tracemalloc.Snapshot(raw_traces2, traceback_limit)

    rudisha (snapshot, snapshot2)

eleza frame(filename, lineno):
    rudisha tracemalloc._Frame((filename, lineno))

eleza traceback(*frames):
    rudisha tracemalloc.Traceback(frames)

eleza traceback_lineno(filename, lineno):
    rudisha traceback((filename, lineno))

eleza traceback_filename(filename):
    rudisha traceback_lineno(filename, 0)


kundi TestTracemallocEnabled(unittest.TestCase):
    eleza setUp(self):
        ikiwa tracemalloc.is_tracing():
            self.skipTest("tracemalloc must be stopped before the test")

        tracemalloc.start(1)

    eleza tearDown(self):
        tracemalloc.stop()

    eleza test_get_tracemalloc_memory(self):
        data = [allocate_bytes(123) kila count kwenye range(1000)]
        size = tracemalloc.get_tracemalloc_memory()
        self.assertGreaterEqual(size, 0)

        tracemalloc.clear_traces()
        size2 = tracemalloc.get_tracemalloc_memory()
        self.assertGreaterEqual(size2, 0)
        self.assertLessEqual(size2, size)

    eleza test_get_object_traceback(self):
        tracemalloc.clear_traces()
        obj_size = 12345
        obj, obj_traceback = allocate_bytes(obj_size)
        traceback = tracemalloc.get_object_traceback(obj)
        self.assertEqual(traceback, obj_traceback)

    eleza test_new_reference(self):
        tracemalloc.clear_traces()
        # gc.collect() indirectly calls PyList_ClearFreeList()
        support.gc_collect()

        # Create a list na "destroy it": put it kwenye the PyListObject free list
        obj = []
        obj = Tupu

        # Create a list which should reuse the previously created empty list
        obj = []

        nframe = tracemalloc.get_traceback_limit()
        frames = get_frames(nframe, -3)
        obj_traceback = tracemalloc.Traceback(frames)

        traceback = tracemalloc.get_object_traceback(obj)
        self.assertIsNotTupu(traceback)
        self.assertEqual(traceback, obj_traceback)

    eleza test_set_traceback_limit(self):
        obj_size = 10

        tracemalloc.stop()
        self.assertRaises(ValueError, tracemalloc.start, -1)

        tracemalloc.stop()
        tracemalloc.start(10)
        obj2, obj2_traceback = allocate_bytes(obj_size)
        traceback = tracemalloc.get_object_traceback(obj2)
        self.assertEqual(len(traceback), 10)
        self.assertEqual(traceback, obj2_traceback)

        tracemalloc.stop()
        tracemalloc.start(1)
        obj, obj_traceback = allocate_bytes(obj_size)
        traceback = tracemalloc.get_object_traceback(obj)
        self.assertEqual(len(traceback), 1)
        self.assertEqual(traceback, obj_traceback)

    eleza find_trace(self, traces, traceback):
        kila trace kwenye traces:
            ikiwa trace[2] == traceback._frames:
                rudisha trace

        self.fail("trace sio found")

    eleza test_get_traces(self):
        tracemalloc.clear_traces()
        obj_size = 12345
        obj, obj_traceback = allocate_bytes(obj_size)

        traces = tracemalloc._get_traces()
        trace = self.find_trace(traces, obj_traceback)

        self.assertIsInstance(trace, tuple)
        domain, size, traceback = trace
        self.assertEqual(size, obj_size)
        self.assertEqual(traceback, obj_traceback._frames)

        tracemalloc.stop()
        self.assertEqual(tracemalloc._get_traces(), [])

    eleza test_get_traces_intern_traceback(self):
        # dummy wrappers to get more useful na identical frames kwenye the traceback
        eleza allocate_bytes2(size):
            rudisha allocate_bytes(size)
        eleza allocate_bytes3(size):
            rudisha allocate_bytes2(size)
        eleza allocate_bytes4(size):
            rudisha allocate_bytes3(size)

        # Ensure that two identical tracebacks are sio duplicated
        tracemalloc.stop()
        tracemalloc.start(4)
        obj_size = 123
        obj1, obj1_traceback = allocate_bytes4(obj_size)
        obj2, obj2_traceback = allocate_bytes4(obj_size)

        traces = tracemalloc._get_traces()

        obj1_traceback._frames = tuple(reversed(obj1_traceback._frames))
        obj2_traceback._frames = tuple(reversed(obj2_traceback._frames))

        trace1 = self.find_trace(traces, obj1_traceback)
        trace2 = self.find_trace(traces, obj2_traceback)
        domain1, size1, traceback1 = trace1
        domain2, size2, traceback2 = trace2
        self.assertIs(traceback2, traceback1)

    eleza test_get_traced_memory(self):
        # Python allocates some internals objects, so the test must tolerate
        # a small difference between the expected size na the real usage
        max_error = 2048

        # allocate one object
        obj_size = 1024 * 1024
        tracemalloc.clear_traces()
        obj, obj_traceback = allocate_bytes(obj_size)
        size, peak_size = tracemalloc.get_traced_memory()
        self.assertGreaterEqual(size, obj_size)
        self.assertGreaterEqual(peak_size, size)

        self.assertLessEqual(size - obj_size, max_error)
        self.assertLessEqual(peak_size - size, max_error)

        # destroy the object
        obj = Tupu
        size2, peak_size2 = tracemalloc.get_traced_memory()
        self.assertLess(size2, size)
        self.assertGreaterEqual(size - size2, obj_size - max_error)
        self.assertGreaterEqual(peak_size2, peak_size)

        # clear_traces() must reset traced memory counters
        tracemalloc.clear_traces()
        self.assertEqual(tracemalloc.get_traced_memory(), (0, 0))

        # allocate another object
        obj, obj_traceback = allocate_bytes(obj_size)
        size, peak_size = tracemalloc.get_traced_memory()
        self.assertGreaterEqual(size, obj_size)

        # stop() also resets traced memory counters
        tracemalloc.stop()
        self.assertEqual(tracemalloc.get_traced_memory(), (0, 0))

    eleza test_clear_traces(self):
        obj, obj_traceback = allocate_bytes(123)
        traceback = tracemalloc.get_object_traceback(obj)
        self.assertIsNotTupu(traceback)

        tracemalloc.clear_traces()
        traceback2 = tracemalloc.get_object_traceback(obj)
        self.assertIsTupu(traceback2)

    eleza test_is_tracing(self):
        tracemalloc.stop()
        self.assertUongo(tracemalloc.is_tracing())

        tracemalloc.start()
        self.assertKweli(tracemalloc.is_tracing())

    eleza test_snapshot(self):
        obj, source = allocate_bytes(123)

        # take a snapshot
        snapshot = tracemalloc.take_snapshot()

        # write on disk
        snapshot.dump(support.TESTFN)
        self.addCleanup(support.unlink, support.TESTFN)

        # load kutoka disk
        snapshot2 = tracemalloc.Snapshot.load(support.TESTFN)
        self.assertEqual(snapshot2.traces, snapshot.traces)

        # tracemalloc must be tracing memory allocations to take a snapshot
        tracemalloc.stop()
        ukijumuisha self.assertRaises(RuntimeError) kama cm:
            tracemalloc.take_snapshot()
        self.assertEqual(str(cm.exception),
                         "the tracemalloc module must be tracing memory "
                         "allocations to take a snapshot")

    eleza test_snapshot_save_attr(self):
        # take a snapshot ukijumuisha a new attribute
        snapshot = tracemalloc.take_snapshot()
        snapshot.test_attr = "new"
        snapshot.dump(support.TESTFN)
        self.addCleanup(support.unlink, support.TESTFN)

        # load() should recreate the attribute
        snapshot2 = tracemalloc.Snapshot.load(support.TESTFN)
        self.assertEqual(snapshot2.test_attr, "new")

    eleza fork_child(self):
        ikiwa sio tracemalloc.is_tracing():
            rudisha 2

        obj_size = 12345
        obj, obj_traceback = allocate_bytes(obj_size)
        traceback = tracemalloc.get_object_traceback(obj)
        ikiwa traceback ni Tupu:
            rudisha 3

        # everything ni fine
        rudisha 0

    @unittest.skipUnless(hasattr(os, 'fork'), 'need os.fork()')
    eleza test_fork(self):
        # check that tracemalloc ni still working after fork
        pid = os.fork()
        ikiwa sio pid:
            # child
            exitcode = 1
            jaribu:
                exitcode = self.fork_child()
            mwishowe:
                os._exit(exitcode)
        isipokua:
            pid2, status = os.waitpid(pid, 0)
            self.assertKweli(os.WIFEXITED(status))
            exitcode = os.WEXITSTATUS(status)
            self.assertEqual(exitcode, 0)


kundi TestSnapshot(unittest.TestCase):
    maxDiff = 4000

    eleza test_create_snapshot(self):
        raw_traces = [(0, 5, (('a.py', 2),))]

        ukijumuisha contextlib.ExitStack() kama stack:
            stack.enter_context(patch.object(tracemalloc, 'is_tracing',
                                             rudisha_value=Kweli))
            stack.enter_context(patch.object(tracemalloc, 'get_traceback_limit',
                                             rudisha_value=5))
            stack.enter_context(patch.object(tracemalloc, '_get_traces',
                                             rudisha_value=raw_traces))

            snapshot = tracemalloc.take_snapshot()
            self.assertEqual(snapshot.traceback_limit, 5)
            self.assertEqual(len(snapshot.traces), 1)
            trace = snapshot.traces[0]
            self.assertEqual(trace.size, 5)
            self.assertEqual(len(trace.traceback), 1)
            self.assertEqual(trace.traceback[0].filename, 'a.py')
            self.assertEqual(trace.traceback[0].lineno, 2)

    eleza test_filter_traces(self):
        snapshot, snapshot2 = create_snapshots()
        filter1 = tracemalloc.Filter(Uongo, "b.py")
        filter2 = tracemalloc.Filter(Kweli, "a.py", 2)
        filter3 = tracemalloc.Filter(Kweli, "a.py", 5)

        original_traces = list(snapshot.traces._traces)

        # exclude b.py
        snapshot3 = snapshot.filter_traces((filter1,))
        self.assertEqual(snapshot3.traces._traces, [
            (0, 10, (('a.py', 2), ('b.py', 4))),
            (0, 10, (('a.py', 2), ('b.py', 4))),
            (0, 10, (('a.py', 2), ('b.py', 4))),
            (1, 2, (('a.py', 5), ('b.py', 4))),
            (3, 7, (('<unknown>', 0),)),
        ])

        # filter_traces() must sio touch the original snapshot
        self.assertEqual(snapshot.traces._traces, original_traces)

        # only include two lines of a.py
        snapshot4 = snapshot3.filter_traces((filter2, filter3))
        self.assertEqual(snapshot4.traces._traces, [
            (0, 10, (('a.py', 2), ('b.py', 4))),
            (0, 10, (('a.py', 2), ('b.py', 4))),
            (0, 10, (('a.py', 2), ('b.py', 4))),
            (1, 2, (('a.py', 5), ('b.py', 4))),
        ])

        # No filter: just duplicate the snapshot
        snapshot5 = snapshot.filter_traces(())
        self.assertIsNot(snapshot5, snapshot)
        self.assertIsNot(snapshot5.traces, snapshot.traces)
        self.assertEqual(snapshot5.traces, snapshot.traces)

        self.assertRaises(TypeError, snapshot.filter_traces, filter1)

    eleza test_filter_traces_domain(self):
        snapshot, snapshot2 = create_snapshots()
        filter1 = tracemalloc.Filter(Uongo, "a.py", domain=1)
        filter2 = tracemalloc.Filter(Kweli, "a.py", domain=1)

        original_traces = list(snapshot.traces._traces)

        # exclude a.py of domain 1
        snapshot3 = snapshot.filter_traces((filter1,))
        self.assertEqual(snapshot3.traces._traces, [
            (0, 10, (('a.py', 2), ('b.py', 4))),
            (0, 10, (('a.py', 2), ('b.py', 4))),
            (0, 10, (('a.py', 2), ('b.py', 4))),
            (2, 66, (('b.py', 1),)),
            (3, 7, (('<unknown>', 0),)),
        ])

        # include domain 1
        snapshot3 = snapshot.filter_traces((filter1,))
        self.assertEqual(snapshot3.traces._traces, [
            (0, 10, (('a.py', 2), ('b.py', 4))),
            (0, 10, (('a.py', 2), ('b.py', 4))),
            (0, 10, (('a.py', 2), ('b.py', 4))),
            (2, 66, (('b.py', 1),)),
            (3, 7, (('<unknown>', 0),)),
        ])

    eleza test_filter_traces_domain_filter(self):
        snapshot, snapshot2 = create_snapshots()
        filter1 = tracemalloc.DomainFilter(Uongo, domain=3)
        filter2 = tracemalloc.DomainFilter(Kweli, domain=3)

        # exclude domain 2
        snapshot3 = snapshot.filter_traces((filter1,))
        self.assertEqual(snapshot3.traces._traces, [
            (0, 10, (('a.py', 2), ('b.py', 4))),
            (0, 10, (('a.py', 2), ('b.py', 4))),
            (0, 10, (('a.py', 2), ('b.py', 4))),
            (1, 2, (('a.py', 5), ('b.py', 4))),
            (2, 66, (('b.py', 1),)),
        ])

        # include domain 2
        snapshot3 = snapshot.filter_traces((filter2,))
        self.assertEqual(snapshot3.traces._traces, [
            (3, 7, (('<unknown>', 0),)),
        ])

    eleza test_snapshot_group_by_line(self):
        snapshot, snapshot2 = create_snapshots()
        tb_0 = traceback_lineno('<unknown>', 0)
        tb_a_2 = traceback_lineno('a.py', 2)
        tb_a_5 = traceback_lineno('a.py', 5)
        tb_b_1 = traceback_lineno('b.py', 1)
        tb_c_578 = traceback_lineno('c.py', 578)

        # stats per file na line
        stats1 = snapshot.statistics('lineno')
        self.assertEqual(stats1, [
            tracemalloc.Statistic(tb_b_1, 66, 1),
            tracemalloc.Statistic(tb_a_2, 30, 3),
            tracemalloc.Statistic(tb_0, 7, 1),
            tracemalloc.Statistic(tb_a_5, 2, 1),
        ])

        # stats per file na line (2)
        stats2 = snapshot2.statistics('lineno')
        self.assertEqual(stats2, [
            tracemalloc.Statistic(tb_a_5, 5002, 2),
            tracemalloc.Statistic(tb_c_578, 400, 1),
            tracemalloc.Statistic(tb_a_2, 30, 3),
        ])

        # stats diff per file na line
        statistics = snapshot2.compare_to(snapshot, 'lineno')
        self.assertEqual(statistics, [
            tracemalloc.StatisticDiff(tb_a_5, 5002, 5000, 2, 1),
            tracemalloc.StatisticDiff(tb_c_578, 400, 400, 1, 1),
            tracemalloc.StatisticDiff(tb_b_1, 0, -66, 0, -1),
            tracemalloc.StatisticDiff(tb_0, 0, -7, 0, -1),
            tracemalloc.StatisticDiff(tb_a_2, 30, 0, 3, 0),
        ])

    eleza test_snapshot_group_by_file(self):
        snapshot, snapshot2 = create_snapshots()
        tb_0 = traceback_filename('<unknown>')
        tb_a = traceback_filename('a.py')
        tb_b = traceback_filename('b.py')
        tb_c = traceback_filename('c.py')

        # stats per file
        stats1 = snapshot.statistics('filename')
        self.assertEqual(stats1, [
            tracemalloc.Statistic(tb_b, 66, 1),
            tracemalloc.Statistic(tb_a, 32, 4),
            tracemalloc.Statistic(tb_0, 7, 1),
        ])

        # stats per file (2)
        stats2 = snapshot2.statistics('filename')
        self.assertEqual(stats2, [
            tracemalloc.Statistic(tb_a, 5032, 5),
            tracemalloc.Statistic(tb_c, 400, 1),
        ])

        # stats diff per file
        diff = snapshot2.compare_to(snapshot, 'filename')
        self.assertEqual(diff, [
            tracemalloc.StatisticDiff(tb_a, 5032, 5000, 5, 1),
            tracemalloc.StatisticDiff(tb_c, 400, 400, 1, 1),
            tracemalloc.StatisticDiff(tb_b, 0, -66, 0, -1),
            tracemalloc.StatisticDiff(tb_0, 0, -7, 0, -1),
        ])

    eleza test_snapshot_group_by_traceback(self):
        snapshot, snapshot2 = create_snapshots()

        # stats per file
        tb1 = traceback(('a.py', 2), ('b.py', 4))
        tb2 = traceback(('a.py', 5), ('b.py', 4))
        tb3 = traceback(('b.py', 1))
        tb4 = traceback(('<unknown>', 0))
        stats1 = snapshot.statistics('traceback')
        self.assertEqual(stats1, [
            tracemalloc.Statistic(tb3, 66, 1),
            tracemalloc.Statistic(tb1, 30, 3),
            tracemalloc.Statistic(tb4, 7, 1),
            tracemalloc.Statistic(tb2, 2, 1),
        ])

        # stats per file (2)
        tb5 = traceback(('c.py', 578))
        stats2 = snapshot2.statistics('traceback')
        self.assertEqual(stats2, [
            tracemalloc.Statistic(tb2, 5002, 2),
            tracemalloc.Statistic(tb5, 400, 1),
            tracemalloc.Statistic(tb1, 30, 3),
        ])

        # stats diff per file
        diff = snapshot2.compare_to(snapshot, 'traceback')
        self.assertEqual(diff, [
            tracemalloc.StatisticDiff(tb2, 5002, 5000, 2, 1),
            tracemalloc.StatisticDiff(tb5, 400, 400, 1, 1),
            tracemalloc.StatisticDiff(tb3, 0, -66, 0, -1),
            tracemalloc.StatisticDiff(tb4, 0, -7, 0, -1),
            tracemalloc.StatisticDiff(tb1, 30, 0, 3, 0),
        ])

        self.assertRaises(ValueError,
                          snapshot.statistics, 'traceback', cumulative=Kweli)

    eleza test_snapshot_group_by_cumulative(self):
        snapshot, snapshot2 = create_snapshots()
        tb_0 = traceback_filename('<unknown>')
        tb_a = traceback_filename('a.py')
        tb_b = traceback_filename('b.py')
        tb_a_2 = traceback_lineno('a.py', 2)
        tb_a_5 = traceback_lineno('a.py', 5)
        tb_b_1 = traceback_lineno('b.py', 1)
        tb_b_4 = traceback_lineno('b.py', 4)

        # per file
        stats = snapshot.statistics('filename', Kweli)
        self.assertEqual(stats, [
            tracemalloc.Statistic(tb_b, 98, 5),
            tracemalloc.Statistic(tb_a, 32, 4),
            tracemalloc.Statistic(tb_0, 7, 1),
        ])

        # per line
        stats = snapshot.statistics('lineno', Kweli)
        self.assertEqual(stats, [
            tracemalloc.Statistic(tb_b_1, 66, 1),
            tracemalloc.Statistic(tb_b_4, 32, 4),
            tracemalloc.Statistic(tb_a_2, 30, 3),
            tracemalloc.Statistic(tb_0, 7, 1),
            tracemalloc.Statistic(tb_a_5, 2, 1),
        ])

    eleza test_trace_format(self):
        snapshot, snapshot2 = create_snapshots()
        trace = snapshot.traces[0]
        self.assertEqual(str(trace), 'b.py:4: 10 B')
        traceback = trace.traceback
        self.assertEqual(str(traceback), 'b.py:4')
        frame = traceback[0]
        self.assertEqual(str(frame), 'b.py:4')

    eleza test_statistic_format(self):
        snapshot, snapshot2 = create_snapshots()
        stats = snapshot.statistics('lineno')
        stat = stats[0]
        self.assertEqual(str(stat),
                         'b.py:1: size=66 B, count=1, average=66 B')

    eleza test_statistic_diff_format(self):
        snapshot, snapshot2 = create_snapshots()
        stats = snapshot2.compare_to(snapshot, 'lineno')
        stat = stats[0]
        self.assertEqual(str(stat),
                         'a.py:5: size=5002 B (+5000 B), count=2 (+1), average=2501 B')

    eleza test_slices(self):
        snapshot, snapshot2 = create_snapshots()
        self.assertEqual(snapshot.traces[:2],
                         (snapshot.traces[0], snapshot.traces[1]))

        traceback = snapshot.traces[0].traceback
        self.assertEqual(traceback[:2],
                         (traceback[0], traceback[1]))

    eleza test_format_traceback(self):
        snapshot, snapshot2 = create_snapshots()
        eleza getline(filename, lineno):
            rudisha '  <%s, %s>' % (filename, lineno)
        ukijumuisha unittest.mock.patch('tracemalloc.linecache.getline',
                                 side_effect=getline):
            tb = snapshot.traces[0].traceback
            self.assertEqual(tb.format(),
                             ['  File "b.py", line 4',
                              '    <b.py, 4>',
                              '  File "a.py", line 2',
                              '    <a.py, 2>'])

            self.assertEqual(tb.format(limit=1),
                             ['  File "a.py", line 2',
                              '    <a.py, 2>'])

            self.assertEqual(tb.format(limit=-1),
                             ['  File "b.py", line 4',
                              '    <b.py, 4>'])

            self.assertEqual(tb.format(most_recent_first=Kweli),
                             ['  File "a.py", line 2',
                              '    <a.py, 2>',
                              '  File "b.py", line 4',
                              '    <b.py, 4>'])

            self.assertEqual(tb.format(limit=1, most_recent_first=Kweli),
                             ['  File "a.py", line 2',
                              '    <a.py, 2>'])

            self.assertEqual(tb.format(limit=-1, most_recent_first=Kweli),
                             ['  File "b.py", line 4',
                              '    <b.py, 4>'])


kundi TestFilters(unittest.TestCase):
    maxDiff = 2048

    eleza test_filter_attributes(self):
        # test default values
        f = tracemalloc.Filter(Kweli, "abc")
        self.assertEqual(f.inclusive, Kweli)
        self.assertEqual(f.filename_pattern, "abc")
        self.assertIsTupu(f.lineno)
        self.assertEqual(f.all_frames, Uongo)

        # test custom values
        f = tracemalloc.Filter(Uongo, "test.py", 123, Kweli)
        self.assertEqual(f.inclusive, Uongo)
        self.assertEqual(f.filename_pattern, "test.py")
        self.assertEqual(f.lineno, 123)
        self.assertEqual(f.all_frames, Kweli)

        # parameters pitaed by keyword
        f = tracemalloc.Filter(inclusive=Uongo, filename_pattern="test.py", lineno=123, all_frames=Kweli)
        self.assertEqual(f.inclusive, Uongo)
        self.assertEqual(f.filename_pattern, "test.py")
        self.assertEqual(f.lineno, 123)
        self.assertEqual(f.all_frames, Kweli)

        # read-only attribute
        self.assertRaises(AttributeError, setattr, f, "filename_pattern", "abc")

    eleza test_filter_match(self):
        # filter without line number
        f = tracemalloc.Filter(Kweli, "abc")
        self.assertKweli(f._match_frame("abc", 0))
        self.assertKweli(f._match_frame("abc", 5))
        self.assertKweli(f._match_frame("abc", 10))
        self.assertUongo(f._match_frame("12356", 0))
        self.assertUongo(f._match_frame("12356", 5))
        self.assertUongo(f._match_frame("12356", 10))

        f = tracemalloc.Filter(Uongo, "abc")
        self.assertUongo(f._match_frame("abc", 0))
        self.assertUongo(f._match_frame("abc", 5))
        self.assertUongo(f._match_frame("abc", 10))
        self.assertKweli(f._match_frame("12356", 0))
        self.assertKweli(f._match_frame("12356", 5))
        self.assertKweli(f._match_frame("12356", 10))

        # filter ukijumuisha line number > 0
        f = tracemalloc.Filter(Kweli, "abc", 5)
        self.assertUongo(f._match_frame("abc", 0))
        self.assertKweli(f._match_frame("abc", 5))
        self.assertUongo(f._match_frame("abc", 10))
        self.assertUongo(f._match_frame("12356", 0))
        self.assertUongo(f._match_frame("12356", 5))
        self.assertUongo(f._match_frame("12356", 10))

        f = tracemalloc.Filter(Uongo, "abc", 5)
        self.assertKweli(f._match_frame("abc", 0))
        self.assertUongo(f._match_frame("abc", 5))
        self.assertKweli(f._match_frame("abc", 10))
        self.assertKweli(f._match_frame("12356", 0))
        self.assertKweli(f._match_frame("12356", 5))
        self.assertKweli(f._match_frame("12356", 10))

        # filter ukijumuisha line number 0
        f = tracemalloc.Filter(Kweli, "abc", 0)
        self.assertKweli(f._match_frame("abc", 0))
        self.assertUongo(f._match_frame("abc", 5))
        self.assertUongo(f._match_frame("abc", 10))
        self.assertUongo(f._match_frame("12356", 0))
        self.assertUongo(f._match_frame("12356", 5))
        self.assertUongo(f._match_frame("12356", 10))

        f = tracemalloc.Filter(Uongo, "abc", 0)
        self.assertUongo(f._match_frame("abc", 0))
        self.assertKweli(f._match_frame("abc", 5))
        self.assertKweli(f._match_frame("abc", 10))
        self.assertKweli(f._match_frame("12356", 0))
        self.assertKweli(f._match_frame("12356", 5))
        self.assertKweli(f._match_frame("12356", 10))

    eleza test_filter_match_filename(self):
        eleza fnmatch(inclusive, filename, pattern):
            f = tracemalloc.Filter(inclusive, pattern)
            rudisha f._match_frame(filename, 0)

        self.assertKweli(fnmatch(Kweli, "abc", "abc"))
        self.assertUongo(fnmatch(Kweli, "12356", "abc"))
        self.assertUongo(fnmatch(Kweli, "<unknown>", "abc"))

        self.assertUongo(fnmatch(Uongo, "abc", "abc"))
        self.assertKweli(fnmatch(Uongo, "12356", "abc"))
        self.assertKweli(fnmatch(Uongo, "<unknown>", "abc"))

    eleza test_filter_match_filename_joker(self):
        eleza fnmatch(filename, pattern):
            filter = tracemalloc.Filter(Kweli, pattern)
            rudisha filter._match_frame(filename, 0)

        # empty string
        self.assertUongo(fnmatch('abc', ''))
        self.assertUongo(fnmatch('', 'abc'))
        self.assertKweli(fnmatch('', ''))
        self.assertKweli(fnmatch('', '*'))

        # no *
        self.assertKweli(fnmatch('abc', 'abc'))
        self.assertUongo(fnmatch('abc', 'abcd'))
        self.assertUongo(fnmatch('abc', 'def'))

        # a*
        self.assertKweli(fnmatch('abc', 'a*'))
        self.assertKweli(fnmatch('abc', 'abc*'))
        self.assertUongo(fnmatch('abc', 'b*'))
        self.assertUongo(fnmatch('abc', 'abcd*'))

        # a*b
        self.assertKweli(fnmatch('abc', 'a*c'))
        self.assertKweli(fnmatch('abcdcx', 'a*cx'))
        self.assertUongo(fnmatch('abb', 'a*c'))
        self.assertUongo(fnmatch('abcdce', 'a*cx'))

        # a*b*c
        self.assertKweli(fnmatch('abcde', 'a*c*e'))
        self.assertKweli(fnmatch('abcbdefeg', 'a*bd*eg'))
        self.assertUongo(fnmatch('abcdd', 'a*c*e'))
        self.assertUongo(fnmatch('abcbdefef', 'a*bd*eg'))

        # replace .pyc suffix ukijumuisha .py
        self.assertKweli(fnmatch('a.pyc', 'a.py'))
        self.assertKweli(fnmatch('a.py', 'a.pyc'))

        ikiwa os.name == 'nt':
            # case insensitive
            self.assertKweli(fnmatch('aBC', 'ABc'))
            self.assertKweli(fnmatch('aBcDe', 'Ab*dE'))

            self.assertKweli(fnmatch('a.pyc', 'a.PY'))
            self.assertKweli(fnmatch('a.py', 'a.PYC'))
        isipokua:
            # case sensitive
            self.assertUongo(fnmatch('aBC', 'ABc'))
            self.assertUongo(fnmatch('aBcDe', 'Ab*dE'))

            self.assertUongo(fnmatch('a.pyc', 'a.PY'))
            self.assertUongo(fnmatch('a.py', 'a.PYC'))

        ikiwa os.name == 'nt':
            # normalize alternate separator "/" to the standard separator "\"
            self.assertKweli(fnmatch(r'a/b', r'a\b'))
            self.assertKweli(fnmatch(r'a\b', r'a/b'))
            self.assertKweli(fnmatch(r'a/b\c', r'a\b/c'))
            self.assertKweli(fnmatch(r'a/b/c', r'a\b\c'))
        isipokua:
            # there ni no alternate separator
            self.assertUongo(fnmatch(r'a/b', r'a\b'))
            self.assertUongo(fnmatch(r'a\b', r'a/b'))
            self.assertUongo(fnmatch(r'a/b\c', r'a\b/c'))
            self.assertUongo(fnmatch(r'a/b/c', r'a\b\c'))

        # kama of 3.5, .pyo ni no longer munged to .py
        self.assertUongo(fnmatch('a.pyo', 'a.py'))

    eleza test_filter_match_trace(self):
        t1 = (("a.py", 2), ("b.py", 3))
        t2 = (("b.py", 4), ("b.py", 5))
        t3 = (("c.py", 5), ('<unknown>', 0))
        unknown = (('<unknown>', 0),)

        f = tracemalloc.Filter(Kweli, "b.py", all_frames=Kweli)
        self.assertKweli(f._match_traceback(t1))
        self.assertKweli(f._match_traceback(t2))
        self.assertUongo(f._match_traceback(t3))
        self.assertUongo(f._match_traceback(unknown))

        f = tracemalloc.Filter(Kweli, "b.py", all_frames=Uongo)
        self.assertUongo(f._match_traceback(t1))
        self.assertKweli(f._match_traceback(t2))
        self.assertUongo(f._match_traceback(t3))
        self.assertUongo(f._match_traceback(unknown))

        f = tracemalloc.Filter(Uongo, "b.py", all_frames=Kweli)
        self.assertUongo(f._match_traceback(t1))
        self.assertUongo(f._match_traceback(t2))
        self.assertKweli(f._match_traceback(t3))
        self.assertKweli(f._match_traceback(unknown))

        f = tracemalloc.Filter(Uongo, "b.py", all_frames=Uongo)
        self.assertKweli(f._match_traceback(t1))
        self.assertUongo(f._match_traceback(t2))
        self.assertKweli(f._match_traceback(t3))
        self.assertKweli(f._match_traceback(unknown))

        f = tracemalloc.Filter(Uongo, "<unknown>", all_frames=Uongo)
        self.assertKweli(f._match_traceback(t1))
        self.assertKweli(f._match_traceback(t2))
        self.assertKweli(f._match_traceback(t3))
        self.assertUongo(f._match_traceback(unknown))

        f = tracemalloc.Filter(Kweli, "<unknown>", all_frames=Kweli)
        self.assertUongo(f._match_traceback(t1))
        self.assertUongo(f._match_traceback(t2))
        self.assertKweli(f._match_traceback(t3))
        self.assertKweli(f._match_traceback(unknown))

        f = tracemalloc.Filter(Uongo, "<unknown>", all_frames=Kweli)
        self.assertKweli(f._match_traceback(t1))
        self.assertKweli(f._match_traceback(t2))
        self.assertUongo(f._match_traceback(t3))
        self.assertUongo(f._match_traceback(unknown))


kundi TestCommandLine(unittest.TestCase):
    eleza test_env_var_disabled_by_default(self):
        # sio tracing by default
        code = 'agiza tracemalloc; andika(tracemalloc.is_tracing())'
        ok, stdout, stderr = assert_python_ok('-c', code)
        stdout = stdout.rstrip()
        self.assertEqual(stdout, b'Uongo')

    @unittest.skipIf(interpreter_requires_environment(),
                     'Cannot run -E tests when PYTHON env vars are required.')
    eleza test_env_var_ignored_with_E(self):
        """PYTHON* environment variables must be ignored when -E ni present."""
        code = 'agiza tracemalloc; andika(tracemalloc.is_tracing())'
        ok, stdout, stderr = assert_python_ok('-E', '-c', code, PYTHONTRACEMALLOC='1')
        stdout = stdout.rstrip()
        self.assertEqual(stdout, b'Uongo')

    eleza test_env_var_disabled(self):
        # tracing at startup
        code = 'agiza tracemalloc; andika(tracemalloc.is_tracing())'
        ok, stdout, stderr = assert_python_ok('-c', code, PYTHONTRACEMALLOC='0')
        stdout = stdout.rstrip()
        self.assertEqual(stdout, b'Uongo')

    eleza test_env_var_enabled_at_startup(self):
        # tracing at startup
        code = 'agiza tracemalloc; andika(tracemalloc.is_tracing())'
        ok, stdout, stderr = assert_python_ok('-c', code, PYTHONTRACEMALLOC='1')
        stdout = stdout.rstrip()
        self.assertEqual(stdout, b'Kweli')

    eleza test_env_limit(self):
        # start na set the number of frames
        code = 'agiza tracemalloc; andika(tracemalloc.get_traceback_limit())'
        ok, stdout, stderr = assert_python_ok('-c', code, PYTHONTRACEMALLOC='10')
        stdout = stdout.rstrip()
        self.assertEqual(stdout, b'10')

    eleza check_env_var_invalid(self, nframe):
        ukijumuisha support.SuppressCrashReport():
            ok, stdout, stderr = assert_python_failure(
                '-c', 'pita',
                PYTHONTRACEMALLOC=str(nframe))

        ikiwa b'ValueError: the number of frames must be kwenye range' kwenye stderr:
            rudisha
        ikiwa b'PYTHONTRACEMALLOC: invalid number of frames' kwenye stderr:
            rudisha
        self.fail(f"unexpected output: {stderr!a}")


    eleza test_env_var_invalid(self):
        kila nframe kwenye INVALID_NFRAME:
            ukijumuisha self.subTest(nframe=nframe):
                self.check_env_var_invalid(nframe)

    eleza test_sys_xoptions(self):
        kila xoptions, nframe kwenye (
            ('tracemalloc', 1),
            ('tracemalloc=1', 1),
            ('tracemalloc=15', 15),
        ):
            ukijumuisha self.subTest(xoptions=xoptions, nframe=nframe):
                code = 'agiza tracemalloc; andika(tracemalloc.get_traceback_limit())'
                ok, stdout, stderr = assert_python_ok('-X', xoptions, '-c', code)
                stdout = stdout.rstrip()
                self.assertEqual(stdout, str(nframe).encode('ascii'))

    eleza check_sys_xoptions_invalid(self, nframe):
        args = ('-X', 'tracemalloc=%s' % nframe, '-c', 'pita')
        ukijumuisha support.SuppressCrashReport():
            ok, stdout, stderr = assert_python_failure(*args)

        ikiwa b'ValueError: the number of frames must be kwenye range' kwenye stderr:
            rudisha
        ikiwa b'-X tracemalloc=NFRAME: invalid number of frames' kwenye stderr:
            rudisha
        self.fail(f"unexpected output: {stderr!a}")

    eleza test_sys_xoptions_invalid(self):
        kila nframe kwenye INVALID_NFRAME:
            ukijumuisha self.subTest(nframe=nframe):
                self.check_sys_xoptions_invalid(nframe)

    @unittest.skipIf(_testcapi ni Tupu, 'need _testcapi')
    eleza test_pymem_alloc0(self):
        # Issue #21639: Check that PyMem_Malloc(0) ukijumuisha tracemalloc enabled
        # does sio crash.
        code = 'agiza _testcapi; _testcapi.test_pymem_alloc0(); 1'
        assert_python_ok('-X', 'tracemalloc', '-c', code)


@unittest.skipIf(_testcapi ni Tupu, 'need _testcapi')
kundi TestCAPI(unittest.TestCase):
    maxDiff = 80 * 20

    eleza setUp(self):
        ikiwa tracemalloc.is_tracing():
            self.skipTest("tracemalloc must be stopped before the test")

        self.domain = 5
        self.size = 123
        self.obj = allocate_bytes(self.size)[0]

        # kila the type "object", id(obj) ni the address of its memory block.
        # This type ni sio tracked by the garbage collector
        self.ptr = id(self.obj)

    eleza tearDown(self):
        tracemalloc.stop()

    eleza get_traceback(self):
        frames = _testcapi.tracemalloc_get_traceback(self.domain, self.ptr)
        ikiwa frames ni sio Tupu:
            rudisha tracemalloc.Traceback(frames)
        isipokua:
            rudisha Tupu

    eleza track(self, release_gil=Uongo, nframe=1):
        frames = get_frames(nframe, 1)
        _testcapi.tracemalloc_track(self.domain, self.ptr, self.size,
                                    release_gil)
        rudisha frames

    eleza untrack(self):
        _testcapi.tracemalloc_untrack(self.domain, self.ptr)

    eleza get_traced_memory(self):
        # Get the traced size kwenye the domain
        snapshot = tracemalloc.take_snapshot()
        domain_filter = tracemalloc.DomainFilter(Kweli, self.domain)
        snapshot = snapshot.filter_traces([domain_filter])
        rudisha sum(trace.size kila trace kwenye snapshot.traces)

    eleza check_track(self, release_gil):
        nframe = 5
        tracemalloc.start(nframe)

        size = tracemalloc.get_traced_memory()[0]

        frames = self.track(release_gil, nframe)
        self.assertEqual(self.get_traceback(),
                         tracemalloc.Traceback(frames))

        self.assertEqual(self.get_traced_memory(), self.size)

    eleza test_track(self):
        self.check_track(Uongo)

    eleza test_track_without_gil(self):
        # check that calling _PyTraceMalloc_Track() without holding the GIL
        # works too
        self.check_track(Kweli)

    eleza test_track_already_tracked(self):
        nframe = 5
        tracemalloc.start(nframe)

        # track a first time
        self.track()

        # calling _PyTraceMalloc_Track() must remove the old trace na add
        # a new trace ukijumuisha the new traceback
        frames = self.track(nframe=nframe)
        self.assertEqual(self.get_traceback(),
                         tracemalloc.Traceback(frames))

    eleza test_untrack(self):
        tracemalloc.start()

        self.track()
        self.assertIsNotTupu(self.get_traceback())
        self.assertEqual(self.get_traced_memory(), self.size)

        # untrack must remove the trace
        self.untrack()
        self.assertIsTupu(self.get_traceback())
        self.assertEqual(self.get_traced_memory(), 0)

        # calling _PyTraceMalloc_Untrack() multiple times must sio crash
        self.untrack()
        self.untrack()

    eleza test_stop_track(self):
        tracemalloc.start()
        tracemalloc.stop()

        ukijumuisha self.assertRaises(RuntimeError):
            self.track()
        self.assertIsTupu(self.get_traceback())

    eleza test_stop_untrack(self):
        tracemalloc.start()
        self.track()

        tracemalloc.stop()
        ukijumuisha self.assertRaises(RuntimeError):
            self.untrack()


eleza test_main():
    support.run_unittest(
        TestTracemallocEnabled,
        TestSnapshot,
        TestFilters,
        TestCommandLine,
        TestCAPI,
    )

ikiwa __name__ == "__main__":
    test_main()
