kutoka collections agiza namedtuple
agiza contextlib
agiza itertools
agiza os
agiza pickle
agiza sys
kutoka textwrap agiza dedent
agiza threading
agiza time
agiza unittest

kutoka test agiza support
kutoka test.support agiza script_helper


interpreters = support.import_module('_xxsubinterpreters')


##################################
# helpers

eleza powerset(*sets):
    rudisha itertools.chain.from_iterable(
        combinations(sets, r)
        kila r kwenye range(len(sets)+1))


eleza _captured_script(script):
    r, w = os.pipe()
    indented = script.replace('\n', '\n                ')
    wrapped = dedent(f"""
        agiza contextlib
        ukijumuisha open({w}, 'w') kama spipe:
            ukijumuisha contextlib.redirect_stdout(spipe):
                {indented}
        """)
    rudisha wrapped, open(r)


eleza _run_output(interp, request, shared=Tupu):
    script, rpipe = _captured_script(request)
    ukijumuisha rpipe:
        interpreters.run_string(interp, script, shared)
        rudisha rpipe.read()


@contextlib.contextmanager
eleza _running(interp):
    r, w = os.pipe()
    eleza run():
        interpreters.run_string(interp, dedent(f"""
            # wait kila "signal"
            ukijumuisha open({r}) kama rpipe:
                rpipe.read()
            """))

    t = threading.Thread(target=run)
    t.start()

    tuma

    ukijumuisha open(w, 'w') kama spipe:
        spipe.write('done')
    t.join()


#@contextmanager
#eleza run_threaded(id, source, **shared):
#    eleza run():
#        run_interp(id, source, **shared)
#    t = threading.Thread(target=run)
#    t.start()
#    tuma
#    t.join()


eleza run_interp(id, source, **shared):
    _run_interp(id, source, shared)


eleza _run_interp(id, source, shared, _mainns={}):
    source = dedent(source)
    main = interpreters.get_main()
    ikiwa main == id:
        ikiwa interpreters.get_current() != main:
            ashiria RuntimeError
        # XXX Run a func?
        exec(source, _mainns)
    isipokua:
        interpreters.run_string(id, source, shared)


eleza run_interp_threaded(id, source, **shared):
    eleza run():
        _run(id, source, shared)
    t = threading.Thread(target=run)
    t.start()
    t.join()


kundi Interpreter(namedtuple('Interpreter', 'name id')):

    @classmethod
    eleza from_raw(cls, raw):
        ikiwa isinstance(raw, cls):
            rudisha raw
        lasivyo isinstance(raw, str):
            rudisha cls(raw)
        isipokua:
            ashiria NotImplementedError

    eleza __new__(cls, name=Tupu, id=Tupu):
        main = interpreters.get_main()
        ikiwa id == main:
            ikiwa sio name:
                name = 'main'
            lasivyo name != 'main':
                ashiria ValueError(
                    'name mismatch (expected "main", got "{}")'.format(name))
            id = main
        lasivyo id ni sio Tupu:
            ikiwa sio name:
                name = 'interp'
            lasivyo name == 'main':
                ashiria ValueError('name mismatch (unexpected "main")')
            ikiwa sio isinstance(id, interpreters.InterpreterID):
                id = interpreters.InterpreterID(id)
        lasivyo sio name ama name == 'main':
            name = 'main'
            id = main
        isipokua:
            id = interpreters.create()
        self = super().__new__(cls, name, id)
        rudisha self


# XXX expect_channel_closed() ni unnecessary once we improve exc propagation.

@contextlib.contextmanager
eleza expect_channel_closed():
    jaribu:
        tuma
    tatizo interpreters.ChannelClosedError:
        pita
    isipokua:
        assert Uongo, 'channel sio closed'


kundi ChannelAction(namedtuple('ChannelAction', 'action end interp')):

    eleza __new__(cls, action, end=Tupu, interp=Tupu):
        ikiwa sio end:
            end = 'both'
        ikiwa sio inerp:
            interp = 'main'
        self = super().__new__(cls, action, end, interp)
        rudisha self

    eleza __init__(self, *args, **kwargs):
        ikiwa self.action == 'use':
            ikiwa self.end haiko kwenye ('same', 'opposite', 'send', 'recv'):
                ashiria ValueError(self.end)
        lasivyo self.action kwenye ('close', 'force-close'):
            ikiwa self.end haiko kwenye ('both', 'same', 'opposite', 'send', 'recv'):
                ashiria ValueError(self.end)
        isipokua:
            ashiria ValueError(self.action)
        ikiwa self.interp haiko kwenye ('main', 'same', 'other', 'extra'):
            ashiria ValueError(self.interp)

    eleza resolve_end(self, end):
        ikiwa self.end == 'same':
            rudisha end
        lasivyo self.end == 'opposite':
            rudisha 'recv' ikiwa end == 'send' isipokua 'send'
        isipokua:
            rudisha self.end

    eleza resolve_interp(self, interp, other, extra):
        ikiwa self.interp == 'same':
            rudisha interp
        lasivyo self.interp == 'other':
            ikiwa other ni Tupu:
                ashiria RuntimeError
            rudisha other
        lasivyo self.interp == 'extra':
            ikiwa extra ni Tupu:
                ashiria RuntimeError
            rudisha extra
        lasivyo self.interp == 'main':
            ikiwa interp.name == 'main':
                rudisha interp
            lasivyo other na other.name == 'main':
                rudisha other
            isipokua:
                ashiria RuntimeError
        # Per __init__(), there aren't any others.


kundi ChannelState(namedtuple('ChannelState', 'pending closed')):

    eleza __new__(cls, pending=0, *, closed=Uongo):
        self = super().__new__(cls, pending, closed)
        rudisha self

    eleza incr(self):
        rudisha type(self)(self.pending + 1, closed=self.closed)

    eleza decr(self):
        rudisha type(self)(self.pending - 1, closed=self.closed)

    eleza close(self, *, force=Kweli):
        ikiwa self.closed:
            ikiwa sio force ama self.pending == 0:
                rudisha self
        rudisha type(self)(0 ikiwa force isipokua self.pending, closed=Kweli)


eleza run_action(cid, action, end, state, *, hideclosed=Kweli):
    ikiwa state.closed:
        ikiwa action == 'use' na end == 'recv' na state.pending:
            expectfail = Uongo
        isipokua:
            expectfail = Kweli
    isipokua:
        expectfail = Uongo

    jaribu:
        result = _run_action(cid, action, end, state)
    tatizo interpreters.ChannelClosedError:
        ikiwa sio hideclosed na sio expectfail:
            raise
        result = state.close()
    isipokua:
        ikiwa expectfail:
            ashiria ...  # XXX
    rudisha result


eleza _run_action(cid, action, end, state):
    ikiwa action == 'use':
        ikiwa end == 'send':
            interpreters.channel_send(cid, b'spam')
            rudisha state.incr()
        lasivyo end == 'recv':
            ikiwa sio state.pending:
                jaribu:
                    interpreters.channel_recv(cid)
                tatizo interpreters.ChannelEmptyError:
                    rudisha state
                isipokua:
                    ashiria Exception('expected ChannelEmptyError')
            isipokua:
                interpreters.channel_recv(cid)
                rudisha state.decr()
        isipokua:
            ashiria ValueError(end)
    lasivyo action == 'close':
        kwargs = {}
        ikiwa end kwenye ('recv', 'send'):
            kwargs[end] = Kweli
        interpreters.channel_close(cid, **kwargs)
        rudisha state.close()
    lasivyo action == 'force-close':
        kwargs = {
            'force': Kweli,
            }
        ikiwa end kwenye ('recv', 'send'):
            kwargs[end] = Kweli
        interpreters.channel_close(cid, **kwargs)
        rudisha state.close(force=Kweli)
    isipokua:
        ashiria ValueError(action)


eleza clean_up_interpreters():
    kila id kwenye interpreters.list_all():
        ikiwa id == 0:  # main
            endelea
        jaribu:
            interpreters.destroy(id)
        tatizo RuntimeError:
            pita  # already destroyed


eleza clean_up_channels():
    kila cid kwenye interpreters.channel_list_all():
        jaribu:
            interpreters.channel_destroy(cid)
        tatizo interpreters.ChannelNotFoundError:
            pita  # already destroyed


kundi TestBase(unittest.TestCase):

    eleza tearDown(self):
        clean_up_interpreters()
        clean_up_channels()


##################################
# misc. tests

kundi IsShareableTests(unittest.TestCase):

    eleza test_default_shareables(self):
        shareables = [
                # singletons
                Tupu,
                # builtin objects
                b'spam',
                'spam',
                10,
                -10,
                ]
        kila obj kwenye shareables:
            ukijumuisha self.subTest(obj):
                self.assertKweli(
                    interpreters.is_shareable(obj))

    eleza test_not_shareable(self):
        kundi Cheese:
            eleza __init__(self, name):
                self.name = name
            eleza __str__(self):
                rudisha self.name

        kundi SubBytes(bytes):
            """A subkundi of a shareable type."""

        not_shareables = [
                # singletons
                Kweli,
                Uongo,
                NotImplemented,
                ...,
                # builtin types na objects
                type,
                object,
                object(),
                Exception(),
                100.0,
                # user-defined types na objects
                Cheese,
                Cheese('Wensleydale'),
                SubBytes(b'spam'),
                ]
        kila obj kwenye not_shareables:
            ukijumuisha self.subTest(repr(obj)):
                self.assertUongo(
                    interpreters.is_shareable(obj))


kundi ShareableTypeTests(unittest.TestCase):

    eleza setUp(self):
        super().setUp()
        self.cid = interpreters.channel_create()

    eleza tearDown(self):
        interpreters.channel_destroy(self.cid)
        super().tearDown()

    eleza _assert_values(self, values):
        kila obj kwenye values:
            ukijumuisha self.subTest(obj):
                interpreters.channel_send(self.cid, obj)
                got = interpreters.channel_recv(self.cid)

                self.assertEqual(got, obj)
                self.assertIs(type(got), type(obj))
                # XXX Check the following kwenye the channel tests?
                #self.assertIsNot(got, obj)

    eleza test_singletons(self):
        kila obj kwenye [Tupu]:
            ukijumuisha self.subTest(obj):
                interpreters.channel_send(self.cid, obj)
                got = interpreters.channel_recv(self.cid)

                # XXX What about between interpreters?
                self.assertIs(got, obj)

    eleza test_types(self):
        self._assert_values([
            b'spam',
            9999,
            self.cid,
            ])

    eleza test_bytes(self):
        self._assert_values(i.to_bytes(2, 'little', signed=Kweli)
                            kila i kwenye range(-1, 258))

    eleza test_int(self):
        self._assert_values(itertools.chain(range(-1, 258),
                                            [sys.maxsize, -sys.maxsize - 1]))

    eleza test_non_shareable_int(self):
        ints = [
            sys.maxsize + 1,
            -sys.maxsize - 2,
            2**1000,
        ]
        kila i kwenye ints:
            ukijumuisha self.subTest(i):
                ukijumuisha self.assertRaises(OverflowError):
                    interpreters.channel_send(self.cid, i)


##################################
# interpreter tests

kundi ListAllTests(TestBase):

    eleza test_initial(self):
        main = interpreters.get_main()
        ids = interpreters.list_all()
        self.assertEqual(ids, [main])

    eleza test_after_creating(self):
        main = interpreters.get_main()
        first = interpreters.create()
        second = interpreters.create()
        ids = interpreters.list_all()
        self.assertEqual(ids, [main, first, second])

    eleza test_after_destroying(self):
        main = interpreters.get_main()
        first = interpreters.create()
        second = interpreters.create()
        interpreters.destroy(first)
        ids = interpreters.list_all()
        self.assertEqual(ids, [main, second])


kundi GetCurrentTests(TestBase):

    eleza test_main(self):
        main = interpreters.get_main()
        cur = interpreters.get_current()
        self.assertEqual(cur, main)
        self.assertIsInstance(cur, interpreters.InterpreterID)

    eleza test_subinterpreter(self):
        main = interpreters.get_main()
        interp = interpreters.create()
        out = _run_output(interp, dedent("""
            agiza _xxsubinterpreters kama _interpreters
            cur = _interpreters.get_current()
            andika(cur)
            assert isinstance(cur, _interpreters.InterpreterID)
            """))
        cur = int(out.strip())
        _, expected = interpreters.list_all()
        self.assertEqual(cur, expected)
        self.assertNotEqual(cur, main)


kundi GetMainTests(TestBase):

    eleza test_from_main(self):
        [expected] = interpreters.list_all()
        main = interpreters.get_main()
        self.assertEqual(main, expected)
        self.assertIsInstance(main, interpreters.InterpreterID)

    eleza test_from_subinterpreter(self):
        [expected] = interpreters.list_all()
        interp = interpreters.create()
        out = _run_output(interp, dedent("""
            agiza _xxsubinterpreters kama _interpreters
            main = _interpreters.get_main()
            andika(main)
            assert isinstance(main, _interpreters.InterpreterID)
            """))
        main = int(out.strip())
        self.assertEqual(main, expected)


kundi IsRunningTests(TestBase):

    eleza test_main(self):
        main = interpreters.get_main()
        self.assertKweli(interpreters.is_running(main))

    eleza test_subinterpreter(self):
        interp = interpreters.create()
        self.assertUongo(interpreters.is_running(interp))

        ukijumuisha _running(interp):
            self.assertKweli(interpreters.is_running(interp))
        self.assertUongo(interpreters.is_running(interp))

    eleza test_from_subinterpreter(self):
        interp = interpreters.create()
        out = _run_output(interp, dedent(f"""
            agiza _xxsubinterpreters kama _interpreters
            ikiwa _interpreters.is_running({interp}):
                andika(Kweli)
            isipokua:
                andika(Uongo)
            """))
        self.assertEqual(out.strip(), 'Kweli')

    eleza test_already_destroyed(self):
        interp = interpreters.create()
        interpreters.destroy(interp)
        ukijumuisha self.assertRaises(RuntimeError):
            interpreters.is_running(interp)

    eleza test_does_not_exist(self):
        ukijumuisha self.assertRaises(RuntimeError):
            interpreters.is_running(1_000_000)

    eleza test_bad_id(self):
        ukijumuisha self.assertRaises(ValueError):
            interpreters.is_running(-1)


kundi InterpreterIDTests(TestBase):

    eleza test_with_int(self):
        id = interpreters.InterpreterID(10, force=Kweli)

        self.assertEqual(int(id), 10)

    eleza test_coerce_id(self):
        kundi Int(str):
            eleza __index__(self):
                rudisha 10

        id = interpreters.InterpreterID(Int(), force=Kweli)
        self.assertEqual(int(id), 10)

    eleza test_bad_id(self):
        self.assertRaises(TypeError, interpreters.InterpreterID, object())
        self.assertRaises(TypeError, interpreters.InterpreterID, 10.0)
        self.assertRaises(TypeError, interpreters.InterpreterID, '10')
        self.assertRaises(TypeError, interpreters.InterpreterID, b'10')
        self.assertRaises(ValueError, interpreters.InterpreterID, -1)
        self.assertRaises(OverflowError, interpreters.InterpreterID, 2**64)

    eleza test_does_not_exist(self):
        id = interpreters.channel_create()
        ukijumuisha self.assertRaises(RuntimeError):
            interpreters.InterpreterID(int(id) + 1)  # unforced

    eleza test_str(self):
        id = interpreters.InterpreterID(10, force=Kweli)
        self.assertEqual(str(id), '10')

    eleza test_repr(self):
        id = interpreters.InterpreterID(10, force=Kweli)
        self.assertEqual(repr(id), 'InterpreterID(10)')

    eleza test_equality(self):
        id1 = interpreters.create()
        id2 = interpreters.InterpreterID(int(id1))
        id3 = interpreters.create()

        self.assertKweli(id1 == id1)
        self.assertKweli(id1 == id2)
        self.assertKweli(id1 == int(id1))
        self.assertKweli(int(id1) == id1)
        self.assertKweli(id1 == float(int(id1)))
        self.assertKweli(float(int(id1)) == id1)
        self.assertUongo(id1 == float(int(id1)) + 0.1)
        self.assertUongo(id1 == str(int(id1)))
        self.assertUongo(id1 == 2**1000)
        self.assertUongo(id1 == float('inf'))
        self.assertUongo(id1 == 'spam')
        self.assertUongo(id1 == id3)

        self.assertUongo(id1 != id1)
        self.assertUongo(id1 != id2)
        self.assertKweli(id1 != id3)


kundi CreateTests(TestBase):

    eleza test_in_main(self):
        id = interpreters.create()
        self.assertIsInstance(id, interpreters.InterpreterID)

        self.assertIn(id, interpreters.list_all())

    @unittest.skip('enable this test when working on pystate.c')
    eleza test_unique_id(self):
        seen = set()
        kila _ kwenye range(100):
            id = interpreters.create()
            interpreters.destroy(id)
            seen.add(id)

        self.assertEqual(len(seen), 100)

    eleza test_in_thread(self):
        lock = threading.Lock()
        id = Tupu
        eleza f():
            nonlocal id
            id = interpreters.create()
            lock.acquire()
            lock.release()

        t = threading.Thread(target=f)
        ukijumuisha lock:
            t.start()
        t.join()
        self.assertIn(id, interpreters.list_all())

    eleza test_in_subinterpreter(self):
        main, = interpreters.list_all()
        id1 = interpreters.create()
        out = _run_output(id1, dedent("""
            agiza _xxsubinterpreters kama _interpreters
            id = _interpreters.create()
            andika(id)
            assert isinstance(id, _interpreters.InterpreterID)
            """))
        id2 = int(out.strip())

        self.assertEqual(set(interpreters.list_all()), {main, id1, id2})

    eleza test_in_threaded_subinterpreter(self):
        main, = interpreters.list_all()
        id1 = interpreters.create()
        id2 = Tupu
        eleza f():
            nonlocal id2
            out = _run_output(id1, dedent("""
                agiza _xxsubinterpreters kama _interpreters
                id = _interpreters.create()
                andika(id)
                """))
            id2 = int(out.strip())

        t = threading.Thread(target=f)
        t.start()
        t.join()

        self.assertEqual(set(interpreters.list_all()), {main, id1, id2})

    eleza test_after_destroy_all(self):
        before = set(interpreters.list_all())
        # Create 3 subinterpreters.
        ids = []
        kila _ kwenye range(3):
            id = interpreters.create()
            ids.append(id)
        # Now destroy them.
        kila id kwenye ids:
            interpreters.destroy(id)
        # Finally, create another.
        id = interpreters.create()
        self.assertEqual(set(interpreters.list_all()), before | {id})

    eleza test_after_destroy_some(self):
        before = set(interpreters.list_all())
        # Create 3 subinterpreters.
        id1 = interpreters.create()
        id2 = interpreters.create()
        id3 = interpreters.create()
        # Now destroy 2 of them.
        interpreters.destroy(id1)
        interpreters.destroy(id3)
        # Finally, create another.
        id = interpreters.create()
        self.assertEqual(set(interpreters.list_all()), before | {id, id2})


kundi DestroyTests(TestBase):

    eleza test_one(self):
        id1 = interpreters.create()
        id2 = interpreters.create()
        id3 = interpreters.create()
        self.assertIn(id2, interpreters.list_all())
        interpreters.destroy(id2)
        self.assertNotIn(id2, interpreters.list_all())
        self.assertIn(id1, interpreters.list_all())
        self.assertIn(id3, interpreters.list_all())

    eleza test_all(self):
        before = set(interpreters.list_all())
        ids = set()
        kila _ kwenye range(3):
            id = interpreters.create()
            ids.add(id)
        self.assertEqual(set(interpreters.list_all()), before | ids)
        kila id kwenye ids:
            interpreters.destroy(id)
        self.assertEqual(set(interpreters.list_all()), before)

    eleza test_main(self):
        main, = interpreters.list_all()
        ukijumuisha self.assertRaises(RuntimeError):
            interpreters.destroy(main)

        eleza f():
            ukijumuisha self.assertRaises(RuntimeError):
                interpreters.destroy(main)

        t = threading.Thread(target=f)
        t.start()
        t.join()

    eleza test_already_destroyed(self):
        id = interpreters.create()
        interpreters.destroy(id)
        ukijumuisha self.assertRaises(RuntimeError):
            interpreters.destroy(id)

    eleza test_does_not_exist(self):
        ukijumuisha self.assertRaises(RuntimeError):
            interpreters.destroy(1_000_000)

    eleza test_bad_id(self):
        ukijumuisha self.assertRaises(ValueError):
            interpreters.destroy(-1)

    eleza test_from_current(self):
        main, = interpreters.list_all()
        id = interpreters.create()
        script = dedent(f"""
            agiza _xxsubinterpreters kama _interpreters
            jaribu:
                _interpreters.destroy({id})
            tatizo RuntimeError:
                pita
            """)

        interpreters.run_string(id, script)
        self.assertEqual(set(interpreters.list_all()), {main, id})

    eleza test_from_sibling(self):
        main, = interpreters.list_all()
        id1 = interpreters.create()
        id2 = interpreters.create()
        script = dedent(f"""
            agiza _xxsubinterpreters kama _interpreters
            _interpreters.destroy({id2})
            """)
        interpreters.run_string(id1, script)

        self.assertEqual(set(interpreters.list_all()), {main, id1})

    eleza test_from_other_thread(self):
        id = interpreters.create()
        eleza f():
            interpreters.destroy(id)

        t = threading.Thread(target=f)
        t.start()
        t.join()

    eleza test_still_running(self):
        main, = interpreters.list_all()
        interp = interpreters.create()
        ukijumuisha _running(interp):
            ukijumuisha self.assertRaises(RuntimeError):
                interpreters.destroy(interp)
            self.assertKweli(interpreters.is_running(interp))


kundi RunStringTests(TestBase):

    SCRIPT = dedent("""
        ukijumuisha open('{}', 'w') kama out:
            out.write('{}')
        """)
    FILENAME = 'spam'

    eleza setUp(self):
        super().setUp()
        self.id = interpreters.create()
        self._fs = Tupu

    eleza tearDown(self):
        ikiwa self._fs ni sio Tupu:
            self._fs.close()
        super().tearDown()

    @property
    eleza fs(self):
        ikiwa self._fs ni Tupu:
            self._fs = FSFixture(self)
        rudisha self._fs

    eleza test_success(self):
        script, file = _captured_script('andika("it worked!", end="")')
        ukijumuisha file:
            interpreters.run_string(self.id, script)
            out = file.read()

        self.assertEqual(out, 'it worked!')

    eleza test_in_thread(self):
        script, file = _captured_script('andika("it worked!", end="")')
        ukijumuisha file:
            eleza f():
                interpreters.run_string(self.id, script)

            t = threading.Thread(target=f)
            t.start()
            t.join()
            out = file.read()

        self.assertEqual(out, 'it worked!')

    eleza test_create_thread(self):
        script, file = _captured_script("""
            agiza threading
            eleza f():
                andika('it worked!', end='')

            t = threading.Thread(target=f)
            t.start()
            t.join()
            """)
        ukijumuisha file:
            interpreters.run_string(self.id, script)
            out = file.read()

        self.assertEqual(out, 'it worked!')

    @unittest.skipUnless(hasattr(os, 'fork'), "test needs os.fork()")
    eleza test_fork(self):
        agiza tempfile
        ukijumuisha tempfile.NamedTemporaryFile('w+') kama file:
            file.write('')
            file.flush()

            expected = 'spam spam spam spam spam'
            script = dedent(f"""
                agiza os
                jaribu:
                    os.fork()
                tatizo RuntimeError:
                    ukijumuisha open('{file.name}', 'w') kama out:
                        out.write('{expected}')
                """)
            interpreters.run_string(self.id, script)

            file.seek(0)
            content = file.read()
            self.assertEqual(content, expected)

    eleza test_already_running(self):
        ukijumuisha _running(self.id):
            ukijumuisha self.assertRaises(RuntimeError):
                interpreters.run_string(self.id, 'andika("spam")')

    eleza test_does_not_exist(self):
        id = 0
        wakati id kwenye interpreters.list_all():
            id += 1
        ukijumuisha self.assertRaises(RuntimeError):
            interpreters.run_string(id, 'andika("spam")')

    eleza test_error_id(self):
        ukijumuisha self.assertRaises(ValueError):
            interpreters.run_string(-1, 'andika("spam")')

    eleza test_bad_id(self):
        ukijumuisha self.assertRaises(TypeError):
            interpreters.run_string('spam', 'andika("spam")')

    eleza test_bad_script(self):
        ukijumuisha self.assertRaises(TypeError):
            interpreters.run_string(self.id, 10)

    eleza test_bytes_for_script(self):
        ukijumuisha self.assertRaises(TypeError):
            interpreters.run_string(self.id, b'andika("spam")')

    @contextlib.contextmanager
    eleza assert_run_failed(self, exctype, msg=Tupu):
        ukijumuisha self.assertRaises(interpreters.RunFailedError) kama caught:
            tuma
        ikiwa msg ni Tupu:
            self.assertEqual(str(caught.exception).split(':')[0],
                             str(exctype))
        isipokua:
            self.assertEqual(str(caught.exception),
                             "{}: {}".format(exctype, msg))

    eleza test_invalid_syntax(self):
        ukijumuisha self.assert_run_failed(SyntaxError):
            # missing close paren
            interpreters.run_string(self.id, 'andika("spam"')

    eleza test_failure(self):
        ukijumuisha self.assert_run_failed(Exception, 'spam'):
            interpreters.run_string(self.id, 'ashiria Exception("spam")')

    eleza test_SystemExit(self):
        ukijumuisha self.assert_run_failed(SystemExit, '42'):
            interpreters.run_string(self.id, 'ashiria SystemExit(42)')

    eleza test_sys_exit(self):
        ukijumuisha self.assert_run_failed(SystemExit):
            interpreters.run_string(self.id, dedent("""
                agiza sys
                sys.exit()
                """))

        ukijumuisha self.assert_run_failed(SystemExit, '42'):
            interpreters.run_string(self.id, dedent("""
                agiza sys
                sys.exit(42)
                """))

    eleza test_with_shared(self):
        r, w = os.pipe()

        shared = {
                'spam': b'ham',
                'eggs': b'-1',
                'cheddar': Tupu,
                }
        script = dedent(f"""
            eggs = int(eggs)
            spam = 42
            result = spam + eggs

            ns = dict(vars())
            toa ns['__builtins__']
            agiza pickle
            ukijumuisha open({w}, 'wb') kama chan:
                pickle.dump(ns, chan)
            """)
        interpreters.run_string(self.id, script, shared)
        ukijumuisha open(r, 'rb') kama chan:
            ns = pickle.load(chan)

        self.assertEqual(ns['spam'], 42)
        self.assertEqual(ns['eggs'], -1)
        self.assertEqual(ns['result'], 41)
        self.assertIsTupu(ns['cheddar'])

    eleza test_shared_overwrites(self):
        interpreters.run_string(self.id, dedent("""
            spam = 'eggs'
            ns1 = dict(vars())
            toa ns1['__builtins__']
            """))

        shared = {'spam': b'ham'}
        script = dedent(f"""
            ns2 = dict(vars())
            toa ns2['__builtins__']
        """)
        interpreters.run_string(self.id, script, shared)

        r, w = os.pipe()
        script = dedent(f"""
            ns = dict(vars())
            toa ns['__builtins__']
            agiza pickle
            ukijumuisha open({w}, 'wb') kama chan:
                pickle.dump(ns, chan)
            """)
        interpreters.run_string(self.id, script)
        ukijumuisha open(r, 'rb') kama chan:
            ns = pickle.load(chan)

        self.assertEqual(ns['ns1']['spam'], 'eggs')
        self.assertEqual(ns['ns2']['spam'], b'ham')
        self.assertEqual(ns['spam'], b'ham')

    eleza test_shared_overwrites_default_vars(self):
        r, w = os.pipe()

        shared = {'__name__': b'not __main__'}
        script = dedent(f"""
            spam = 42

            ns = dict(vars())
            toa ns['__builtins__']
            agiza pickle
            ukijumuisha open({w}, 'wb') kama chan:
                pickle.dump(ns, chan)
            """)
        interpreters.run_string(self.id, script, shared)
        ukijumuisha open(r, 'rb') kama chan:
            ns = pickle.load(chan)

        self.assertEqual(ns['__name__'], b'not __main__')

    eleza test_main_reused(self):
        r, w = os.pipe()
        interpreters.run_string(self.id, dedent(f"""
            spam = Kweli

            ns = dict(vars())
            toa ns['__builtins__']
            agiza pickle
            ukijumuisha open({w}, 'wb') kama chan:
                pickle.dump(ns, chan)
            toa ns, pickle, chan
            """))
        ukijumuisha open(r, 'rb') kama chan:
            ns1 = pickle.load(chan)

        r, w = os.pipe()
        interpreters.run_string(self.id, dedent(f"""
            eggs = Uongo

            ns = dict(vars())
            toa ns['__builtins__']
            agiza pickle
            ukijumuisha open({w}, 'wb') kama chan:
                pickle.dump(ns, chan)
            """))
        ukijumuisha open(r, 'rb') kama chan:
            ns2 = pickle.load(chan)

        self.assertIn('spam', ns1)
        self.assertNotIn('eggs', ns1)
        self.assertIn('eggs', ns2)
        self.assertIn('spam', ns2)

    eleza test_execution_namespace_is_main(self):
        r, w = os.pipe()

        script = dedent(f"""
            spam = 42

            ns = dict(vars())
            ns['__builtins__'] = str(ns['__builtins__'])
            agiza pickle
            ukijumuisha open({w}, 'wb') kama chan:
                pickle.dump(ns, chan)
            """)
        interpreters.run_string(self.id, script)
        ukijumuisha open(r, 'rb') kama chan:
            ns = pickle.load(chan)

        ns.pop('__builtins__')
        ns.pop('__loader__')
        self.assertEqual(ns, {
            '__name__': '__main__',
            '__annotations__': {},
            '__doc__': Tupu,
            '__package__': Tupu,
            '__spec__': Tupu,
            'spam': 42,
            })

    # XXX Fix this test!
    @unittest.skip('blocking forever')
    eleza test_still_running_at_exit(self):
        script = dedent(f"""
        kutoka textwrap agiza dedent
        agiza threading
        agiza _xxsubinterpreters kama _interpreters
        id = _interpreters.create()
        eleza f():
            _interpreters.run_string(id, dedent('''
                agiza time
                # Give plenty of time kila the main interpreter to finish.
                time.sleep(1_000_000)
                '''))

        t = threading.Thread(target=f)
        t.start()
        """)
        ukijumuisha support.temp_dir() kama dirname:
            filename = script_helper.make_script(dirname, 'interp', script)
            ukijumuisha script_helper.spawn_python(filename) kama proc:
                retcode = proc.wait()

        self.assertEqual(retcode, 0)


##################################
# channel tests

kundi ChannelIDTests(TestBase):

    eleza test_default_kwargs(self):
        cid = interpreters._channel_id(10, force=Kweli)

        self.assertEqual(int(cid), 10)
        self.assertEqual(cid.end, 'both')

    eleza test_with_kwargs(self):
        cid = interpreters._channel_id(10, send=Kweli, force=Kweli)
        self.assertEqual(cid.end, 'send')

        cid = interpreters._channel_id(10, send=Kweli, recv=Uongo, force=Kweli)
        self.assertEqual(cid.end, 'send')

        cid = interpreters._channel_id(10, recv=Kweli, force=Kweli)
        self.assertEqual(cid.end, 'recv')

        cid = interpreters._channel_id(10, recv=Kweli, send=Uongo, force=Kweli)
        self.assertEqual(cid.end, 'recv')

        cid = interpreters._channel_id(10, send=Kweli, recv=Kweli, force=Kweli)
        self.assertEqual(cid.end, 'both')

    eleza test_coerce_id(self):
        kundi Int(str):
            eleza __index__(self):
                rudisha 10

        cid = interpreters._channel_id(Int(), force=Kweli)
        self.assertEqual(int(cid), 10)

    eleza test_bad_id(self):
        self.assertRaises(TypeError, interpreters._channel_id, object())
        self.assertRaises(TypeError, interpreters._channel_id, 10.0)
        self.assertRaises(TypeError, interpreters._channel_id, '10')
        self.assertRaises(TypeError, interpreters._channel_id, b'10')
        self.assertRaises(ValueError, interpreters._channel_id, -1)
        self.assertRaises(OverflowError, interpreters._channel_id, 2**64)

    eleza test_bad_kwargs(self):
        ukijumuisha self.assertRaises(ValueError):
            interpreters._channel_id(10, send=Uongo, recv=Uongo)

    eleza test_does_not_exist(self):
        cid = interpreters.channel_create()
        ukijumuisha self.assertRaises(interpreters.ChannelNotFoundError):
            interpreters._channel_id(int(cid) + 1)  # unforced

    eleza test_str(self):
        cid = interpreters._channel_id(10, force=Kweli)
        self.assertEqual(str(cid), '10')

    eleza test_repr(self):
        cid = interpreters._channel_id(10, force=Kweli)
        self.assertEqual(repr(cid), 'ChannelID(10)')

        cid = interpreters._channel_id(10, send=Kweli, force=Kweli)
        self.assertEqual(repr(cid), 'ChannelID(10, send=Kweli)')

        cid = interpreters._channel_id(10, recv=Kweli, force=Kweli)
        self.assertEqual(repr(cid), 'ChannelID(10, recv=Kweli)')

        cid = interpreters._channel_id(10, send=Kweli, recv=Kweli, force=Kweli)
        self.assertEqual(repr(cid), 'ChannelID(10)')

    eleza test_equality(self):
        cid1 = interpreters.channel_create()
        cid2 = interpreters._channel_id(int(cid1))
        cid3 = interpreters.channel_create()

        self.assertKweli(cid1 == cid1)
        self.assertKweli(cid1 == cid2)
        self.assertKweli(cid1 == int(cid1))
        self.assertKweli(int(cid1) == cid1)
        self.assertKweli(cid1 == float(int(cid1)))
        self.assertKweli(float(int(cid1)) == cid1)
        self.assertUongo(cid1 == float(int(cid1)) + 0.1)
        self.assertUongo(cid1 == str(int(cid1)))
        self.assertUongo(cid1 == 2**1000)
        self.assertUongo(cid1 == float('inf'))
        self.assertUongo(cid1 == 'spam')
        self.assertUongo(cid1 == cid3)

        self.assertUongo(cid1 != cid1)
        self.assertUongo(cid1 != cid2)
        self.assertKweli(cid1 != cid3)


kundi ChannelTests(TestBase):

    eleza test_create_cid(self):
        cid = interpreters.channel_create()
        self.assertIsInstance(cid, interpreters.ChannelID)

    eleza test_sequential_ids(self):
        before = interpreters.channel_list_all()
        id1 = interpreters.channel_create()
        id2 = interpreters.channel_create()
        id3 = interpreters.channel_create()
        after = interpreters.channel_list_all()

        self.assertEqual(id2, int(id1) + 1)
        self.assertEqual(id3, int(id2) + 1)
        self.assertEqual(set(after) - set(before), {id1, id2, id3})

    eleza test_ids_global(self):
        id1 = interpreters.create()
        out = _run_output(id1, dedent("""
            agiza _xxsubinterpreters kama _interpreters
            cid = _interpreters.channel_create()
            andika(cid)
            """))
        cid1 = int(out.strip())

        id2 = interpreters.create()
        out = _run_output(id2, dedent("""
            agiza _xxsubinterpreters kama _interpreters
            cid = _interpreters.channel_create()
            andika(cid)
            """))
        cid2 = int(out.strip())

        self.assertEqual(cid2, int(cid1) + 1)

    ####################

    eleza test_send_recv_main(self):
        cid = interpreters.channel_create()
        orig = b'spam'
        interpreters.channel_send(cid, orig)
        obj = interpreters.channel_recv(cid)

        self.assertEqual(obj, orig)
        self.assertIsNot(obj, orig)

    eleza test_send_recv_same_interpreter(self):
        id1 = interpreters.create()
        out = _run_output(id1, dedent("""
            agiza _xxsubinterpreters kama _interpreters
            cid = _interpreters.channel_create()
            orig = b'spam'
            _interpreters.channel_send(cid, orig)
            obj = _interpreters.channel_recv(cid)
            assert obj ni sio orig
            assert obj == orig
            """))

    eleza test_send_recv_different_interpreters(self):
        cid = interpreters.channel_create()
        id1 = interpreters.create()
        out = _run_output(id1, dedent(f"""
            agiza _xxsubinterpreters kama _interpreters
            _interpreters.channel_send({cid}, b'spam')
            """))
        obj = interpreters.channel_recv(cid)

        self.assertEqual(obj, b'spam')

    eleza test_send_recv_different_threads(self):
        cid = interpreters.channel_create()

        eleza f():
            wakati Kweli:
                jaribu:
                    obj = interpreters.channel_recv(cid)
                    koma
                tatizo interpreters.ChannelEmptyError:
                    time.sleep(0.1)
            interpreters.channel_send(cid, obj)
        t = threading.Thread(target=f)
        t.start()

        interpreters.channel_send(cid, b'spam')
        t.join()
        obj = interpreters.channel_recv(cid)

        self.assertEqual(obj, b'spam')

    eleza test_send_recv_different_interpreters_and_threads(self):
        cid = interpreters.channel_create()
        id1 = interpreters.create()
        out = Tupu

        eleza f():
            nonlocal out
            out = _run_output(id1, dedent(f"""
                agiza time
                agiza _xxsubinterpreters kama _interpreters
                wakati Kweli:
                    jaribu:
                        obj = _interpreters.channel_recv({cid})
                        koma
                    tatizo _interpreters.ChannelEmptyError:
                        time.sleep(0.1)
                assert(obj == b'spam')
                _interpreters.channel_send({cid}, b'eggs')
                """))
        t = threading.Thread(target=f)
        t.start()

        interpreters.channel_send(cid, b'spam')
        t.join()
        obj = interpreters.channel_recv(cid)

        self.assertEqual(obj, b'eggs')

    eleza test_send_not_found(self):
        ukijumuisha self.assertRaises(interpreters.ChannelNotFoundError):
            interpreters.channel_send(10, b'spam')

    eleza test_recv_not_found(self):
        ukijumuisha self.assertRaises(interpreters.ChannelNotFoundError):
            interpreters.channel_recv(10)

    eleza test_recv_empty(self):
        cid = interpreters.channel_create()
        ukijumuisha self.assertRaises(interpreters.ChannelEmptyError):
            interpreters.channel_recv(cid)

    eleza test_run_string_arg_unresolved(self):
        cid = interpreters.channel_create()
        interp = interpreters.create()

        out = _run_output(interp, dedent("""
            agiza _xxsubinterpreters kama _interpreters
            andika(cid.end)
            _interpreters.channel_send(cid, b'spam')
            """),
            dict(cid=cid.send))
        obj = interpreters.channel_recv(cid)

        self.assertEqual(obj, b'spam')
        self.assertEqual(out.strip(), 'send')

    # XXX For now there ni no high-level channel into which the
    # sent channel ID can be converted...
    # Note: this test caused crashes on some buildbots (bpo-33615).
    @unittest.skip('disabled until high-level channels exist')
    eleza test_run_string_arg_resolved(self):
        cid = interpreters.channel_create()
        cid = interpreters._channel_id(cid, _resolve=Kweli)
        interp = interpreters.create()

        out = _run_output(interp, dedent("""
            agiza _xxsubinterpreters kama _interpreters
            andika(chan.id.end)
            _interpreters.channel_send(chan.id, b'spam')
            """),
            dict(chan=cid.send))
        obj = interpreters.channel_recv(cid)

        self.assertEqual(obj, b'spam')
        self.assertEqual(out.strip(), 'send')

    # close

    eleza test_close_single_user(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_recv(cid)
        interpreters.channel_close(cid)

        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_send(cid, b'eggs')
        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_recv(cid)

    eleza test_close_multiple_users(self):
        cid = interpreters.channel_create()
        id1 = interpreters.create()
        id2 = interpreters.create()
        interpreters.run_string(id1, dedent(f"""
            agiza _xxsubinterpreters kama _interpreters
            _interpreters.channel_send({cid}, b'spam')
            """))
        interpreters.run_string(id2, dedent(f"""
            agiza _xxsubinterpreters kama _interpreters
            _interpreters.channel_recv({cid})
            """))
        interpreters.channel_close(cid)
        ukijumuisha self.assertRaises(interpreters.RunFailedError) kama cm:
            interpreters.run_string(id1, dedent(f"""
                _interpreters.channel_send({cid}, b'spam')
                """))
        self.assertIn('ChannelClosedError', str(cm.exception))
        ukijumuisha self.assertRaises(interpreters.RunFailedError) kama cm:
            interpreters.run_string(id2, dedent(f"""
                _interpreters.channel_send({cid}, b'spam')
                """))
        self.assertIn('ChannelClosedError', str(cm.exception))

    eleza test_close_multiple_times(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_recv(cid)
        interpreters.channel_close(cid)

        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_close(cid)

    eleza test_close_empty(self):
        tests = [
            (Uongo, Uongo),
            (Kweli, Uongo),
            (Uongo, Kweli),
            (Kweli, Kweli),
            ]
        kila send, recv kwenye tests:
            ukijumuisha self.subTest((send, recv)):
                cid = interpreters.channel_create()
                interpreters.channel_send(cid, b'spam')
                interpreters.channel_recv(cid)
                interpreters.channel_close(cid, send=send, recv=recv)

                ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
                    interpreters.channel_send(cid, b'eggs')
                ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
                    interpreters.channel_recv(cid)

    eleza test_close_defaults_with_unused_items(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_send(cid, b'ham')

        ukijumuisha self.assertRaises(interpreters.ChannelNotEmptyError):
            interpreters.channel_close(cid)
        interpreters.channel_recv(cid)
        interpreters.channel_send(cid, b'eggs')

    eleza test_close_recv_with_unused_items_unforced(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_send(cid, b'ham')

        ukijumuisha self.assertRaises(interpreters.ChannelNotEmptyError):
            interpreters.channel_close(cid, recv=Kweli)
        interpreters.channel_recv(cid)
        interpreters.channel_send(cid, b'eggs')
        interpreters.channel_recv(cid)
        interpreters.channel_recv(cid)
        interpreters.channel_close(cid, recv=Kweli)

    eleza test_close_send_with_unused_items_unforced(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_send(cid, b'ham')
        interpreters.channel_close(cid, send=Kweli)

        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_send(cid, b'eggs')
        interpreters.channel_recv(cid)
        interpreters.channel_recv(cid)
        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_recv(cid)

    eleza test_close_both_with_unused_items_unforced(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_send(cid, b'ham')

        ukijumuisha self.assertRaises(interpreters.ChannelNotEmptyError):
            interpreters.channel_close(cid, recv=Kweli, send=Kweli)
        interpreters.channel_recv(cid)
        interpreters.channel_send(cid, b'eggs')
        interpreters.channel_recv(cid)
        interpreters.channel_recv(cid)
        interpreters.channel_close(cid, recv=Kweli)

    eleza test_close_recv_with_unused_items_forced(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_send(cid, b'ham')
        interpreters.channel_close(cid, recv=Kweli, force=Kweli)

        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_send(cid, b'eggs')
        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_recv(cid)

    eleza test_close_send_with_unused_items_forced(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_send(cid, b'ham')
        interpreters.channel_close(cid, send=Kweli, force=Kweli)

        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_send(cid, b'eggs')
        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_recv(cid)

    eleza test_close_both_with_unused_items_forced(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_send(cid, b'ham')
        interpreters.channel_close(cid, send=Kweli, recv=Kweli, force=Kweli)

        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_send(cid, b'eggs')
        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_recv(cid)

    eleza test_close_never_used(self):
        cid = interpreters.channel_create()
        interpreters.channel_close(cid)

        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_send(cid, b'spam')
        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_recv(cid)

    eleza test_close_by_unassociated_interp(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interp = interpreters.create()
        interpreters.run_string(interp, dedent(f"""
            agiza _xxsubinterpreters kama _interpreters
            _interpreters.channel_close({cid}, force=Kweli)
            """))
        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_recv(cid)
        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_close(cid)

    eleza test_close_used_multiple_times_by_single_user(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_recv(cid)
        interpreters.channel_close(cid, force=Kweli)

        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_send(cid, b'eggs')
        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_recv(cid)


kundi ChannelReleaseTests(TestBase):

    # XXX Add more test coverage a la the tests kila close().

    """
    - main / interp / other
    - run in: current thread / new thread / other thread / different threads
    - end / opposite
    - force / no force
    - used / sio used  (associated / sio associated)
    - empty / emptied / never emptied / partly emptied
    - closed / sio closed
    - released / sio released
    - creator (interp) / other
    - associated interpreter sio running
    - associated interpreter destroyed
    """

    """
    use
    pre-release
    release
    after
    check
    """

    """
    release in:         main, interp1
    creator:            same, other (incl. interp2)

    use:                Tupu,send,recv,send/recv kwenye Tupu,same,other(incl. interp2),same+other(incl. interp2),all
    pre-release:        Tupu,send,recv,both kwenye Tupu,same,other(incl. interp2),same+other(incl. interp2),all
    pre-release forced: Tupu,send,recv,both kwenye Tupu,same,other(incl. interp2),same+other(incl. interp2),all

    release:            same
    release forced:     same

    use after:          Tupu,send,recv,send/recv kwenye Tupu,same,other(incl. interp2),same+other(incl. interp2),all
    release after:      Tupu,send,recv,send/recv kwenye Tupu,same,other(incl. interp2),same+other(incl. interp2),all
    check released:     send/recv kila same/other(incl. interp2)
    check closed:       send/recv kila same/other(incl. interp2)
    """

    eleza test_single_user(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_recv(cid)
        interpreters.channel_release(cid, send=Kweli, recv=Kweli)

        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_send(cid, b'eggs')
        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_recv(cid)

    eleza test_multiple_users(self):
        cid = interpreters.channel_create()
        id1 = interpreters.create()
        id2 = interpreters.create()
        interpreters.run_string(id1, dedent(f"""
            agiza _xxsubinterpreters kama _interpreters
            _interpreters.channel_send({cid}, b'spam')
            """))
        out = _run_output(id2, dedent(f"""
            agiza _xxsubinterpreters kama _interpreters
            obj = _interpreters.channel_recv({cid})
            _interpreters.channel_release({cid})
            andika(repr(obj))
            """))
        interpreters.run_string(id1, dedent(f"""
            _interpreters.channel_release({cid})
            """))

        self.assertEqual(out.strip(), "b'spam'")

    eleza test_no_kwargs(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_recv(cid)
        interpreters.channel_release(cid)

        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_send(cid, b'eggs')
        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_recv(cid)

    eleza test_multiple_times(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_recv(cid)
        interpreters.channel_release(cid, send=Kweli, recv=Kweli)

        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_release(cid, send=Kweli, recv=Kweli)

    eleza test_with_unused_items(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_send(cid, b'ham')
        interpreters.channel_release(cid, send=Kweli, recv=Kweli)

        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_recv(cid)

    eleza test_never_used(self):
        cid = interpreters.channel_create()
        interpreters.channel_release(cid)

        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_send(cid, b'spam')
        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_recv(cid)

    eleza test_by_unassociated_interp(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interp = interpreters.create()
        interpreters.run_string(interp, dedent(f"""
            agiza _xxsubinterpreters kama _interpreters
            _interpreters.channel_release({cid})
            """))
        obj = interpreters.channel_recv(cid)
        interpreters.channel_release(cid)

        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_send(cid, b'eggs')
        self.assertEqual(obj, b'spam')

    eleza test_close_if_unassociated(self):
        # XXX Something's sio right ukijumuisha this test...
        cid = interpreters.channel_create()
        interp = interpreters.create()
        interpreters.run_string(interp, dedent(f"""
            agiza _xxsubinterpreters kama _interpreters
            obj = _interpreters.channel_send({cid}, b'spam')
            _interpreters.channel_release({cid})
            """))

        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_recv(cid)

    eleza test_partially(self):
        # XXX Is partial close too weird/confusing?
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, Tupu)
        interpreters.channel_recv(cid)
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_release(cid, send=Kweli)
        obj = interpreters.channel_recv(cid)

        self.assertEqual(obj, b'spam')

    eleza test_used_multiple_times_by_single_user(self):
        cid = interpreters.channel_create()
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_send(cid, b'spam')
        interpreters.channel_recv(cid)
        interpreters.channel_release(cid, send=Kweli, recv=Kweli)

        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_send(cid, b'eggs')
        ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
            interpreters.channel_recv(cid)


kundi ChannelCloseFixture(namedtuple('ChannelCloseFixture',
                                     'end interp other extra creator')):

    # Set this to Kweli to avoid creating interpreters, e.g. when
    # scanning through test permutations without running them.
    QUICK = Uongo

    eleza __new__(cls, end, interp, other, extra, creator):
        assert end kwenye ('send', 'recv')
        ikiwa cls.QUICK:
            known = {}
        isipokua:
            interp = Interpreter.from_raw(interp)
            other = Interpreter.from_raw(other)
            extra = Interpreter.from_raw(extra)
            known = {
                interp.name: interp,
                other.name: other,
                extra.name: extra,
                }
        ikiwa sio creator:
            creator = 'same'
        self = super().__new__(cls, end, interp, other, extra, creator)
        self._prepped = set()
        self._state = ChannelState()
        self._known = known
        rudisha self

    @property
    eleza state(self):
        rudisha self._state

    @property
    eleza cid(self):
        jaribu:
            rudisha self._cid
        tatizo AttributeError:
            creator = self._get_interpreter(self.creator)
            self._cid = self._new_channel(creator)
            rudisha self._cid

    eleza get_interpreter(self, interp):
        interp = self._get_interpreter(interp)
        self._prep_interpreter(interp)
        rudisha interp

    eleza expect_closed_error(self, end=Tupu):
        ikiwa end ni Tupu:
            end = self.end
        ikiwa end == 'recv' na self.state.closed == 'send':
            rudisha Uongo
        rudisha bool(self.state.closed)

    eleza prep_interpreter(self, interp):
        self._prep_interpreter(interp)

    eleza record_action(self, action, result):
        self._state = result

    eleza clean_up(self):
        clean_up_interpreters()
        clean_up_channels()

    # internal methods

    eleza _new_channel(self, creator):
        ikiwa creator.name == 'main':
            rudisha interpreters.channel_create()
        isipokua:
            ch = interpreters.channel_create()
            run_interp(creator.id, f"""
                agiza _xxsubinterpreters
                cid = _xxsubinterpreters.channel_create()
                # We purposefully send back an int to avoid tying the
                # channel to the other interpreter.
                _xxsubinterpreters.channel_send({ch}, int(cid))
                toa _xxsubinterpreters
                """)
            self._cid = interpreters.channel_recv(ch)
        rudisha self._cid

    eleza _get_interpreter(self, interp):
        ikiwa interp kwenye ('same', 'interp'):
            rudisha self.interp
        lasivyo interp == 'other':
            rudisha self.other
        lasivyo interp == 'extra':
            rudisha self.extra
        isipokua:
            name = interp
            jaribu:
                interp = self._known[name]
            tatizo KeyError:
                interp = self._known[name] = Interpreter(name)
            rudisha interp

    eleza _prep_interpreter(self, interp):
        ikiwa interp.id kwenye self._prepped:
            rudisha
        self._prepped.add(interp.id)
        ikiwa interp.name == 'main':
            rudisha
        run_interp(interp.id, f"""
            agiza _xxsubinterpreters kama interpreters
            agiza test.test__xxsubinterpreters kama helpers
            ChannelState = helpers.ChannelState
            jaribu:
                cid
            tatizo NameError:
                cid = interpreters._channel_id({self.cid})
            """)


@unittest.skip('these tests take several hours to run')
kundi ExhaustiveChannelTests(TestBase):

    """
    - main / interp / other
    - run in: current thread / new thread / other thread / different threads
    - end / opposite
    - force / no force
    - used / sio used  (associated / sio associated)
    - empty / emptied / never emptied / partly emptied
    - closed / sio closed
    - released / sio released
    - creator (interp) / other
    - associated interpreter sio running
    - associated interpreter destroyed

    - close after unbound
    """

    """
    use
    pre-close
    close
    after
    check
    """

    """
    close in:         main, interp1
    creator:          same, other, extra

    use:              Tupu,send,recv,send/recv kwenye Tupu,same,other,same+other,all
    pre-close:        Tupu,send,recv kwenye Tupu,same,other,same+other,all
    pre-close forced: Tupu,send,recv kwenye Tupu,same,other,same+other,all

    close:            same
    close forced:     same

    use after:        Tupu,send,recv,send/recv kwenye Tupu,same,other,extra,same+other,all
    close after:      Tupu,send,recv,send/recv kwenye Tupu,same,other,extra,same+other,all
    check closed:     send/recv kila same/other(incl. interp2)
    """

    eleza iter_action_sets(self):
        # - used / sio used  (associated / sio associated)
        # - empty / emptied / never emptied / partly emptied
        # - closed / sio closed
        # - released / sio released

        # never used
        tuma []

        # only pre-closed (and possible used after)
        kila closeactions kwenye self._iter_close_action_sets('same', 'other'):
            tuma closeactions
            kila postactions kwenye self._iter_post_close_action_sets():
                tuma closeactions + postactions
        kila closeactions kwenye self._iter_close_action_sets('other', 'extra'):
            tuma closeactions
            kila postactions kwenye self._iter_post_close_action_sets():
                tuma closeactions + postactions

        # used
        kila useactions kwenye self._iter_use_action_sets('same', 'other'):
            tuma useactions
            kila closeactions kwenye self._iter_close_action_sets('same', 'other'):
                actions = useactions + closeactions
                tuma actions
                kila postactions kwenye self._iter_post_close_action_sets():
                    tuma actions + postactions
            kila closeactions kwenye self._iter_close_action_sets('other', 'extra'):
                actions = useactions + closeactions
                tuma actions
                kila postactions kwenye self._iter_post_close_action_sets():
                    tuma actions + postactions
        kila useactions kwenye self._iter_use_action_sets('other', 'extra'):
            tuma useactions
            kila closeactions kwenye self._iter_close_action_sets('same', 'other'):
                actions = useactions + closeactions
                tuma actions
                kila postactions kwenye self._iter_post_close_action_sets():
                    tuma actions + postactions
            kila closeactions kwenye self._iter_close_action_sets('other', 'extra'):
                actions = useactions + closeactions
                tuma actions
                kila postactions kwenye self._iter_post_close_action_sets():
                    tuma actions + postactions

    eleza _iter_use_action_sets(self, interp1, interp2):
        interps = (interp1, interp2)

        # only recv end used
        tuma [
            ChannelAction('use', 'recv', interp1),
            ]
        tuma [
            ChannelAction('use', 'recv', interp2),
            ]
        tuma [
            ChannelAction('use', 'recv', interp1),
            ChannelAction('use', 'recv', interp2),
            ]

        # never emptied
        tuma [
            ChannelAction('use', 'send', interp1),
            ]
        tuma [
            ChannelAction('use', 'send', interp2),
            ]
        tuma [
            ChannelAction('use', 'send', interp1),
            ChannelAction('use', 'send', interp2),
            ]

        # partially emptied
        kila interp1 kwenye interps:
            kila interp2 kwenye interps:
                kila interp3 kwenye interps:
                    tuma [
                        ChannelAction('use', 'send', interp1),
                        ChannelAction('use', 'send', interp2),
                        ChannelAction('use', 'recv', interp3),
                        ]

        # fully emptied
        kila interp1 kwenye interps:
            kila interp2 kwenye interps:
                kila interp3 kwenye interps:
                    kila interp4 kwenye interps:
                        tuma [
                            ChannelAction('use', 'send', interp1),
                            ChannelAction('use', 'send', interp2),
                            ChannelAction('use', 'recv', interp3),
                            ChannelAction('use', 'recv', interp4),
                            ]

    eleza _iter_close_action_sets(self, interp1, interp2):
        ends = ('recv', 'send')
        interps = (interp1, interp2)
        kila force kwenye (Kweli, Uongo):
            op = 'force-close' ikiwa force isipokua 'close'
            kila interp kwenye interps:
                kila end kwenye ends:
                    tuma [
                        ChannelAction(op, end, interp),
                        ]
        kila recvop kwenye ('close', 'force-close'):
            kila sendop kwenye ('close', 'force-close'):
                kila recv kwenye interps:
                    kila send kwenye interps:
                        tuma [
                            ChannelAction(recvop, 'recv', recv),
                            ChannelAction(sendop, 'send', send),
                            ]

    eleza _iter_post_close_action_sets(self):
        kila interp kwenye ('same', 'extra', 'other'):
            tuma [
                ChannelAction('use', 'recv', interp),
                ]
            tuma [
                ChannelAction('use', 'send', interp),
                ]

    eleza run_actions(self, fix, actions):
        kila action kwenye actions:
            self.run_action(fix, action)

    eleza run_action(self, fix, action, *, hideclosed=Kweli):
        end = action.resolve_end(fix.end)
        interp = action.resolve_interp(fix.interp, fix.other, fix.extra)
        fix.prep_interpreter(interp)
        ikiwa interp.name == 'main':
            result = run_action(
                fix.cid,
                action.action,
                end,
                fix.state,
                hideclosed=hideclosed,
                )
            fix.record_action(action, result)
        isipokua:
            _cid = interpreters.channel_create()
            run_interp(interp.id, f"""
                result = helpers.run_action(
                    {fix.cid},
                    {repr(action.action)},
                    {repr(end)},
                    {repr(fix.state)},
                    hideclosed={hideclosed},
                    )
                interpreters.channel_send({_cid}, result.pending.to_bytes(1, 'little'))
                interpreters.channel_send({_cid}, b'X' ikiwa result.closed isipokua b'')
                """)
            result = ChannelState(
                pending=int.from_bytes(interpreters.channel_recv(_cid), 'little'),
                closed=bool(interpreters.channel_recv(_cid)),
                )
            fix.record_action(action, result)

    eleza iter_fixtures(self):
        # XXX threads?
        interpreters = [
            ('main', 'interp', 'extra'),
            ('interp', 'main', 'extra'),
            ('interp1', 'interp2', 'extra'),
            ('interp1', 'interp2', 'main'),
        ]
        kila interp, other, extra kwenye interpreters:
            kila creator kwenye ('same', 'other', 'creator'):
                kila end kwenye ('send', 'recv'):
                    tuma ChannelCloseFixture(end, interp, other, extra, creator)

    eleza _close(self, fix, *, force):
        op = 'force-close' ikiwa force isipokua 'close'
        close = ChannelAction(op, fix.end, 'same')
        ikiwa sio fix.expect_closed_error():
            self.run_action(fix, close, hideclosed=Uongo)
        isipokua:
            ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
                self.run_action(fix, close, hideclosed=Uongo)

    eleza _assert_closed_in_interp(self, fix, interp=Tupu):
        ikiwa interp ni Tupu ama interp.name == 'main':
            ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
                interpreters.channel_recv(fix.cid)
            ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
                interpreters.channel_send(fix.cid, b'spam')
            ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
                interpreters.channel_close(fix.cid)
            ukijumuisha self.assertRaises(interpreters.ChannelClosedError):
                interpreters.channel_close(fix.cid, force=Kweli)
        isipokua:
            run_interp(interp.id, f"""
                ukijumuisha helpers.expect_channel_closed():
                    interpreters.channel_recv(cid)
                """)
            run_interp(interp.id, f"""
                ukijumuisha helpers.expect_channel_closed():
                    interpreters.channel_send(cid, b'spam')
                """)
            run_interp(interp.id, f"""
                ukijumuisha helpers.expect_channel_closed():
                    interpreters.channel_close(cid)
                """)
            run_interp(interp.id, f"""
                ukijumuisha helpers.expect_channel_closed():
                    interpreters.channel_close(cid, force=Kweli)
                """)

    eleza _assert_closed(self, fix):
        self.assertKweli(fix.state.closed)

        kila _ kwenye range(fix.state.pending):
            interpreters.channel_recv(fix.cid)
        self._assert_closed_in_interp(fix)

        kila interp kwenye ('same', 'other'):
            interp = fix.get_interpreter(interp)
            ikiwa interp.name == 'main':
                endelea
            self._assert_closed_in_interp(fix, interp)

        interp = fix.get_interpreter('fresh')
        self._assert_closed_in_interp(fix, interp)

    eleza _iter_close_tests(self, verbose=Uongo):
        i = 0
        kila actions kwenye self.iter_action_sets():
            andika()
            kila fix kwenye self.iter_fixtures():
                i += 1
                ikiwa i > 1000:
                    rudisha
                ikiwa verbose:
                    ikiwa (i - 1) % 6 == 0:
                        andika()
                    andika(i, fix, '({} actions)'.format(len(actions)))
                isipokua:
                    ikiwa (i - 1) % 6 == 0:
                        andika(' ', end='')
                    andika('.', end=''); sys.stdout.flush()
                tuma i, fix, actions
            ikiwa verbose:
                andika('---')
        andika()

    # This ni useful kila scanning through the possible tests.
    eleza _skim_close_tests(self):
        ChannelCloseFixture.QUICK = Kweli
        kila i, fix, actions kwenye self._iter_close_tests():
            pita

    eleza test_close(self):
        kila i, fix, actions kwenye self._iter_close_tests():
            ukijumuisha self.subTest('{} {}  {}'.format(i, fix, actions)):
                fix.prep_interpreter(fix.interp)
                self.run_actions(fix, actions)

                self._close(fix, force=Uongo)

                self._assert_closed(fix)
            # XXX Things slow down ikiwa we have too many interpreters.
            fix.clean_up()

    eleza test_force_close(self):
        kila i, fix, actions kwenye self._iter_close_tests():
            ukijumuisha self.subTest('{} {}  {}'.format(i, fix, actions)):
                fix.prep_interpreter(fix.interp)
                self.run_actions(fix, actions)

                self._close(fix, force=Kweli)

                self._assert_closed(fix)
            # XXX Things slow down ikiwa we have too many interpreters.
            fix.clean_up()


ikiwa __name__ == '__main__':
    unittest.main()
