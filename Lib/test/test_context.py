agiza concurrent.futures
agiza contextvars
agiza functools
agiza gc
agiza random
agiza time
agiza unittest
agiza weakref

jaribu:
    kutoka _testcapi agiza hamt
except ImportError:
    hamt = Tupu


eleza isolated_context(func):
    """Needed to make reftracking test mode work."""
    @functools.wraps(func)
    eleza wrapper(*args, **kwargs):
        ctx = contextvars.Context()
        rudisha ctx.run(func, *args, **kwargs)
    rudisha wrapper


kundi ContextTest(unittest.TestCase):
    eleza test_context_var_new_1(self):
        ukijumuisha self.assertRaisesRegex(TypeError, 'takes exactly 1'):
            contextvars.ContextVar()

        ukijumuisha self.assertRaisesRegex(TypeError, 'must be a str'):
            contextvars.ContextVar(1)

        c = contextvars.ContextVar('aaa')
        self.assertEqual(c.name, 'aaa')

        ukijumuisha self.assertRaises(AttributeError):
            c.name = 'bbb'

        self.assertNotEqual(hash(c), hash('aaa'))

    eleza test_context_var_new_2(self):
        self.assertIsTupu(contextvars.ContextVar[int])

    @isolated_context
    eleza test_context_var_repr_1(self):
        c = contextvars.ContextVar('a')
        self.assertIn('a', repr(c))

        c = contextvars.ContextVar('a', default=123)
        self.assertIn('123', repr(c))

        lst = []
        c = contextvars.ContextVar('a', default=lst)
        lst.append(c)
        self.assertIn('...', repr(c))
        self.assertIn('...', repr(lst))

        t = c.set(1)
        self.assertIn(repr(c), repr(t))
        self.assertNotIn(' used ', repr(t))
        c.reset(t)
        self.assertIn(' used ', repr(t))

    eleza test_context_subclassing_1(self):
        ukijumuisha self.assertRaisesRegex(TypeError, 'not an acceptable base type'):
            kundi MyContextVar(contextvars.ContextVar):
                # Potentially we might want ContextVars to be subclassable.
                pass

        ukijumuisha self.assertRaisesRegex(TypeError, 'not an acceptable base type'):
            kundi MyContext(contextvars.Context):
                pass

        ukijumuisha self.assertRaisesRegex(TypeError, 'not an acceptable base type'):
            kundi MyToken(contextvars.Token):
                pass

    eleza test_context_new_1(self):
        ukijumuisha self.assertRaisesRegex(TypeError, 'any arguments'):
            contextvars.Context(1)
        ukijumuisha self.assertRaisesRegex(TypeError, 'any arguments'):
            contextvars.Context(1, a=1)
        ukijumuisha self.assertRaisesRegex(TypeError, 'any arguments'):
            contextvars.Context(a=1)
        contextvars.Context(**{})

    eleza test_context_typerrors_1(self):
        ctx = contextvars.Context()

        ukijumuisha self.assertRaisesRegex(TypeError, 'ContextVar key was expected'):
            ctx[1]
        ukijumuisha self.assertRaisesRegex(TypeError, 'ContextVar key was expected'):
            1 kwenye ctx
        ukijumuisha self.assertRaisesRegex(TypeError, 'ContextVar key was expected'):
            ctx.get(1)

    eleza test_context_get_context_1(self):
        ctx = contextvars.copy_context()
        self.assertIsInstance(ctx, contextvars.Context)

    eleza test_context_run_1(self):
        ctx = contextvars.Context()

        ukijumuisha self.assertRaisesRegex(TypeError, 'missing 1 required'):
            ctx.run()

    eleza test_context_run_2(self):
        ctx = contextvars.Context()

        eleza func(*args, **kwargs):
            kwargs['spam'] = 'foo'
            args += ('bar',)
            rudisha args, kwargs

        kila f kwenye (func, functools.partial(func)):
            # partial doesn't support FASTCALL

            self.assertEqual(ctx.run(f), (('bar',), {'spam': 'foo'}))
            self.assertEqual(ctx.run(f, 1), ((1, 'bar'), {'spam': 'foo'}))

            self.assertEqual(
                ctx.run(f, a=2),
                (('bar',), {'a': 2, 'spam': 'foo'}))

            self.assertEqual(
                ctx.run(f, 11, a=2),
                ((11, 'bar'), {'a': 2, 'spam': 'foo'}))

            a = {}
            self.assertEqual(
                ctx.run(f, 11, **a),
                ((11, 'bar'), {'spam': 'foo'}))
            self.assertEqual(a, {})

    eleza test_context_run_3(self):
        ctx = contextvars.Context()

        eleza func(*args, **kwargs):
            1 / 0

        ukijumuisha self.assertRaises(ZeroDivisionError):
            ctx.run(func)
        ukijumuisha self.assertRaises(ZeroDivisionError):
            ctx.run(func, 1, 2)
        ukijumuisha self.assertRaises(ZeroDivisionError):
            ctx.run(func, 1, 2, a=123)

    @isolated_context
    eleza test_context_run_4(self):
        ctx1 = contextvars.Context()
        ctx2 = contextvars.Context()
        var = contextvars.ContextVar('var')

        eleza func2():
            self.assertIsTupu(var.get(Tupu))

        eleza func1():
            self.assertIsTupu(var.get(Tupu))
            var.set('spam')
            ctx2.run(func2)
            self.assertEqual(var.get(Tupu), 'spam')

            cur = contextvars.copy_context()
            self.assertEqual(len(cur), 1)
            self.assertEqual(cur[var], 'spam')
            rudisha cur

        returned_ctx = ctx1.run(func1)
        self.assertEqual(ctx1, returned_ctx)
        self.assertEqual(returned_ctx[var], 'spam')
        self.assertIn(var, returned_ctx)

    eleza test_context_run_5(self):
        ctx = contextvars.Context()
        var = contextvars.ContextVar('var')

        eleza func():
            self.assertIsTupu(var.get(Tupu))
            var.set('spam')
            1 / 0

        ukijumuisha self.assertRaises(ZeroDivisionError):
            ctx.run(func)

        self.assertIsTupu(var.get(Tupu))

    eleza test_context_run_6(self):
        ctx = contextvars.Context()
        c = contextvars.ContextVar('a', default=0)

        eleza fun():
            self.assertEqual(c.get(), 0)
            self.assertIsTupu(ctx.get(c))

            c.set(42)
            self.assertEqual(c.get(), 42)
            self.assertEqual(ctx.get(c), 42)

        ctx.run(fun)

    eleza test_context_run_7(self):
        ctx = contextvars.Context()

        eleza fun():
            ukijumuisha self.assertRaisesRegex(RuntimeError, 'is already entered'):
                ctx.run(fun)

        ctx.run(fun)

    @isolated_context
    eleza test_context_getset_1(self):
        c = contextvars.ContextVar('c')
        ukijumuisha self.assertRaises(LookupError):
            c.get()

        self.assertIsTupu(c.get(Tupu))

        t0 = c.set(42)
        self.assertEqual(c.get(), 42)
        self.assertEqual(c.get(Tupu), 42)
        self.assertIs(t0.old_value, t0.MISSING)
        self.assertIs(t0.old_value, contextvars.Token.MISSING)
        self.assertIs(t0.var, c)

        t = c.set('spam')
        self.assertEqual(c.get(), 'spam')
        self.assertEqual(c.get(Tupu), 'spam')
        self.assertEqual(t.old_value, 42)
        c.reset(t)

        self.assertEqual(c.get(), 42)
        self.assertEqual(c.get(Tupu), 42)

        c.set('spam2')
        ukijumuisha self.assertRaisesRegex(RuntimeError, 'has already been used'):
            c.reset(t)
        self.assertEqual(c.get(), 'spam2')

        ctx1 = contextvars.copy_context()
        self.assertIn(c, ctx1)

        c.reset(t0)
        ukijumuisha self.assertRaisesRegex(RuntimeError, 'has already been used'):
            c.reset(t0)
        self.assertIsTupu(c.get(Tupu))

        self.assertIn(c, ctx1)
        self.assertEqual(ctx1[c], 'spam2')
        self.assertEqual(ctx1.get(c, 'aa'), 'spam2')
        self.assertEqual(len(ctx1), 1)
        self.assertEqual(list(ctx1.items()), [(c, 'spam2')])
        self.assertEqual(list(ctx1.values()), ['spam2'])
        self.assertEqual(list(ctx1.keys()), [c])
        self.assertEqual(list(ctx1), [c])

        ctx2 = contextvars.copy_context()
        self.assertNotIn(c, ctx2)
        ukijumuisha self.assertRaises(KeyError):
            ctx2[c]
        self.assertEqual(ctx2.get(c, 'aa'), 'aa')
        self.assertEqual(len(ctx2), 0)
        self.assertEqual(list(ctx2), [])

    @isolated_context
    eleza test_context_getset_2(self):
        v1 = contextvars.ContextVar('v1')
        v2 = contextvars.ContextVar('v2')

        t1 = v1.set(42)
        ukijumuisha self.assertRaisesRegex(ValueError, 'by a different'):
            v2.reset(t1)

    @isolated_context
    eleza test_context_getset_3(self):
        c = contextvars.ContextVar('c', default=42)
        ctx = contextvars.Context()

        eleza fun():
            self.assertEqual(c.get(), 42)
            ukijumuisha self.assertRaises(KeyError):
                ctx[c]
            self.assertIsTupu(ctx.get(c))
            self.assertEqual(ctx.get(c, 'spam'), 'spam')
            self.assertNotIn(c, ctx)
            self.assertEqual(list(ctx.keys()), [])

            t = c.set(1)
            self.assertEqual(list(ctx.keys()), [c])
            self.assertEqual(ctx[c], 1)

            c.reset(t)
            self.assertEqual(list(ctx.keys()), [])
            ukijumuisha self.assertRaises(KeyError):
                ctx[c]

        ctx.run(fun)

    @isolated_context
    eleza test_context_getset_4(self):
        c = contextvars.ContextVar('c', default=42)
        ctx = contextvars.Context()

        tok = ctx.run(c.set, 1)

        ukijumuisha self.assertRaisesRegex(ValueError, 'different Context'):
            c.reset(tok)

    @isolated_context
    eleza test_context_getset_5(self):
        c = contextvars.ContextVar('c', default=42)
        c.set([])

        eleza fun():
            c.set([])
            c.get().append(42)
            self.assertEqual(c.get(), [42])

        contextvars.copy_context().run(fun)
        self.assertEqual(c.get(), [])

    eleza test_context_copy_1(self):
        ctx1 = contextvars.Context()
        c = contextvars.ContextVar('c', default=42)

        eleza ctx1_fun():
            c.set(10)

            ctx2 = ctx1.copy()
            self.assertEqual(ctx2[c], 10)

            c.set(20)
            self.assertEqual(ctx1[c], 20)
            self.assertEqual(ctx2[c], 10)

            ctx2.run(ctx2_fun)
            self.assertEqual(ctx1[c], 20)
            self.assertEqual(ctx2[c], 30)

        eleza ctx2_fun():
            self.assertEqual(c.get(), 10)
            c.set(30)
            self.assertEqual(c.get(), 30)

        ctx1.run(ctx1_fun)

    @isolated_context
    eleza test_context_threads_1(self):
        cvar = contextvars.ContextVar('cvar')

        eleza sub(num):
            kila i kwenye range(10):
                cvar.set(num + i)
                time.sleep(random.uniform(0.001, 0.05))
                self.assertEqual(cvar.get(), num + i)
            rudisha num

        tp = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        jaribu:
            results = list(tp.map(sub, range(10)))
        mwishowe:
            tp.shutdown()
        self.assertEqual(results, list(range(10)))


# HAMT Tests


kundi HashKey:
    _crasher = Tupu

    eleza __init__(self, hash, name, *, error_on_eq_to=Tupu):
        assert hash != -1
        self.name = name
        self.hash = hash
        self.error_on_eq_to = error_on_eq_to

    eleza __repr__(self):
        rudisha f'<Key name:{self.name} hash:{self.hash}>'

    eleza __hash__(self):
        ikiwa self._crasher ni sio Tupu na self._crasher.error_on_hash:
             ashiria HashingError

        rudisha self.hash

    eleza __eq__(self, other):
        ikiwa sio isinstance(other, HashKey):
            rudisha NotImplemented

        ikiwa self._crasher ni sio Tupu na self._crasher.error_on_eq:
             ashiria EqError

        ikiwa self.error_on_eq_to ni sio Tupu na self.error_on_eq_to ni other:
             ashiria ValueError(f'cannot compare {self!r} to {other!r}')
        ikiwa other.error_on_eq_to ni sio Tupu na other.error_on_eq_to ni self:
             ashiria ValueError(f'cannot compare {other!r} to {self!r}')

        rudisha (self.name, self.hash) == (other.name, other.hash)


kundi KeyStr(str):
    eleza __hash__(self):
        ikiwa HashKey._crasher ni sio Tupu na HashKey._crasher.error_on_hash:
             ashiria HashingError
        rudisha super().__hash__()

    eleza __eq__(self, other):
        ikiwa HashKey._crasher ni sio Tupu na HashKey._crasher.error_on_eq:
             ashiria EqError
        rudisha super().__eq__(other)


kundi HaskKeyCrasher:
    eleza __init__(self, *, error_on_hash=Uongo, error_on_eq=Uongo):
        self.error_on_hash = error_on_hash
        self.error_on_eq = error_on_eq

    eleza __enter__(self):
        ikiwa HashKey._crasher ni sio Tupu:
             ashiria RuntimeError('cannot nest crashers')
        HashKey._crasher = self

    eleza __exit__(self, *exc):
        HashKey._crasher = Tupu


kundi HashingError(Exception):
    pass


kundi EqError(Exception):
    pass


@unittest.skipIf(hamt ni Tupu, '_testcapi lacks "hamt()" function')
kundi HamtTest(unittest.TestCase):

    eleza test_hashkey_helper_1(self):
        k1 = HashKey(10, 'aaa')
        k2 = HashKey(10, 'bbb')

        self.assertNotEqual(k1, k2)
        self.assertEqual(hash(k1), hash(k2))

        d = dict()
        d[k1] = 'a'
        d[k2] = 'b'

        self.assertEqual(d[k1], 'a')
        self.assertEqual(d[k2], 'b')

    eleza test_hamt_basics_1(self):
        h = hamt()
        h = Tupu  # NoQA

    eleza test_hamt_basics_2(self):
        h = hamt()
        self.assertEqual(len(h), 0)

        h2 = h.set('a', 'b')
        self.assertIsNot(h, h2)
        self.assertEqual(len(h), 0)
        self.assertEqual(len(h2), 1)

        self.assertIsTupu(h.get('a'))
        self.assertEqual(h.get('a', 42), 42)

        self.assertEqual(h2.get('a'), 'b')

        h3 = h2.set('b', 10)
        self.assertIsNot(h2, h3)
        self.assertEqual(len(h), 0)
        self.assertEqual(len(h2), 1)
        self.assertEqual(len(h3), 2)
        self.assertEqual(h3.get('a'), 'b')
        self.assertEqual(h3.get('b'), 10)

        self.assertIsTupu(h.get('b'))
        self.assertIsTupu(h2.get('b'))

        self.assertIsTupu(h.get('a'))
        self.assertEqual(h2.get('a'), 'b')

        h = h2 = h3 = Tupu

    eleza test_hamt_basics_3(self):
        h = hamt()
        o = object()
        h1 = h.set('1', o)
        h2 = h1.set('1', o)
        self.assertIs(h1, h2)

    eleza test_hamt_basics_4(self):
        h = hamt()
        h1 = h.set('key', [])
        h2 = h1.set('key', [])
        self.assertIsNot(h1, h2)
        self.assertEqual(len(h1), 1)
        self.assertEqual(len(h2), 1)
        self.assertIsNot(h1.get('key'), h2.get('key'))

    eleza test_hamt_collision_1(self):
        k1 = HashKey(10, 'aaa')
        k2 = HashKey(10, 'bbb')
        k3 = HashKey(10, 'ccc')

        h = hamt()
        h2 = h.set(k1, 'a')
        h3 = h2.set(k2, 'b')

        self.assertEqual(h.get(k1), Tupu)
        self.assertEqual(h.get(k2), Tupu)

        self.assertEqual(h2.get(k1), 'a')
        self.assertEqual(h2.get(k2), Tupu)

        self.assertEqual(h3.get(k1), 'a')
        self.assertEqual(h3.get(k2), 'b')

        h4 = h3.set(k2, 'cc')
        h5 = h4.set(k3, 'aa')

        self.assertEqual(h3.get(k1), 'a')
        self.assertEqual(h3.get(k2), 'b')
        self.assertEqual(h4.get(k1), 'a')
        self.assertEqual(h4.get(k2), 'cc')
        self.assertEqual(h4.get(k3), Tupu)
        self.assertEqual(h5.get(k1), 'a')
        self.assertEqual(h5.get(k2), 'cc')
        self.assertEqual(h5.get(k2), 'cc')
        self.assertEqual(h5.get(k3), 'aa')

        self.assertEqual(len(h), 0)
        self.assertEqual(len(h2), 1)
        self.assertEqual(len(h3), 2)
        self.assertEqual(len(h4), 2)
        self.assertEqual(len(h5), 3)

    eleza test_hamt_stress(self):
        COLLECTION_SIZE = 7000
        TEST_ITERS_EVERY = 647
        CRASH_HASH_EVERY = 97
        CRASH_EQ_EVERY = 11
        RUN_XTIMES = 3

        kila _ kwenye range(RUN_XTIMES):
            h = hamt()
            d = dict()

            kila i kwenye range(COLLECTION_SIZE):
                key = KeyStr(i)

                ikiwa sio (i % CRASH_HASH_EVERY):
                    ukijumuisha HaskKeyCrasher(error_on_hash=Kweli):
                        ukijumuisha self.assertRaises(HashingError):
                            h.set(key, i)

                h = h.set(key, i)

                ikiwa sio (i % CRASH_EQ_EVERY):
                    ukijumuisha HaskKeyCrasher(error_on_eq=Kweli):
                        ukijumuisha self.assertRaises(EqError):
                            h.get(KeyStr(i))  # really trigger __eq__

                d[key] = i
                self.assertEqual(len(d), len(h))

                ikiwa sio (i % TEST_ITERS_EVERY):
                    self.assertEqual(set(h.items()), set(d.items()))
                    self.assertEqual(len(h.items()), len(d.items()))

            self.assertEqual(len(h), COLLECTION_SIZE)

            kila key kwenye range(COLLECTION_SIZE):
                self.assertEqual(h.get(KeyStr(key), 'not found'), key)

            keys_to_delete = list(range(COLLECTION_SIZE))
            random.shuffle(keys_to_delete)
            kila iter_i, i kwenye enumerate(keys_to_delete):
                key = KeyStr(i)

                ikiwa sio (iter_i % CRASH_HASH_EVERY):
                    ukijumuisha HaskKeyCrasher(error_on_hash=Kweli):
                        ukijumuisha self.assertRaises(HashingError):
                            h.delete(key)

                ikiwa sio (iter_i % CRASH_EQ_EVERY):
                    ukijumuisha HaskKeyCrasher(error_on_eq=Kweli):
                        ukijumuisha self.assertRaises(EqError):
                            h.delete(KeyStr(i))

                h = h.delete(key)
                self.assertEqual(h.get(key, 'not found'), 'not found')
                toa d[key]
                self.assertEqual(len(d), len(h))

                ikiwa iter_i == COLLECTION_SIZE // 2:
                    hm = h
                    dm = d.copy()

                ikiwa sio (iter_i % TEST_ITERS_EVERY):
                    self.assertEqual(set(h.keys()), set(d.keys()))
                    self.assertEqual(len(h.keys()), len(d.keys()))

            self.assertEqual(len(d), 0)
            self.assertEqual(len(h), 0)

            # ============

            kila key kwenye dm:
                self.assertEqual(hm.get(str(key)), dm[key])
            self.assertEqual(len(dm), len(hm))

            kila i, key kwenye enumerate(keys_to_delete):
                hm = hm.delete(str(key))
                self.assertEqual(hm.get(str(key), 'not found'), 'not found')
                dm.pop(str(key), Tupu)
                self.assertEqual(len(d), len(h))

                ikiwa sio (i % TEST_ITERS_EVERY):
                    self.assertEqual(set(h.values()), set(d.values()))
                    self.assertEqual(len(h.values()), len(d.values()))

            self.assertEqual(len(d), 0)
            self.assertEqual(len(h), 0)
            self.assertEqual(list(h.items()), [])

    eleza test_hamt_delete_1(self):
        A = HashKey(100, 'A')
        B = HashKey(101, 'B')
        C = HashKey(102, 'C')
        D = HashKey(103, 'D')
        E = HashKey(104, 'E')
        Z = HashKey(-100, 'Z')

        Er = HashKey(103, 'Er', error_on_eq_to=D)

        h = hamt()
        h = h.set(A, 'a')
        h = h.set(B, 'b')
        h = h.set(C, 'c')
        h = h.set(D, 'd')
        h = h.set(E, 'e')

        orig_len = len(h)

        # BitmapNode(size=10 bitmap=0b111110000 id=0x10eadc618):
        #     <Key name:A hash:100>: 'a'
        #     <Key name:B hash:101>: 'b'
        #     <Key name:C hash:102>: 'c'
        #     <Key name:D hash:103>: 'd'
        #     <Key name:E hash:104>: 'e'

        h = h.delete(C)
        self.assertEqual(len(h), orig_len - 1)

        ukijumuisha self.assertRaisesRegex(ValueError, 'cannot compare'):
            h.delete(Er)

        h = h.delete(D)
        self.assertEqual(len(h), orig_len - 2)

        h2 = h.delete(Z)
        self.assertIs(h2, h)

        h = h.delete(A)
        self.assertEqual(len(h), orig_len - 3)

        self.assertEqual(h.get(A, 42), 42)
        self.assertEqual(h.get(B), 'b')
        self.assertEqual(h.get(E), 'e')

    eleza test_hamt_delete_2(self):
        A = HashKey(100, 'A')
        B = HashKey(201001, 'B')
        C = HashKey(101001, 'C')
        D = HashKey(103, 'D')
        E = HashKey(104, 'E')
        Z = HashKey(-100, 'Z')

        Er = HashKey(201001, 'Er', error_on_eq_to=B)

        h = hamt()
        h = h.set(A, 'a')
        h = h.set(B, 'b')
        h = h.set(C, 'c')
        h = h.set(D, 'd')
        h = h.set(E, 'e')

        orig_len = len(h)

        # BitmapNode(size=8 bitmap=0b1110010000):
        #     <Key name:A hash:100>: 'a'
        #     <Key name:D hash:103>: 'd'
        #     <Key name:E hash:104>: 'e'
        #     NULL:
        #         BitmapNode(size=4 bitmap=0b100000000001000000000):
        #             <Key name:B hash:201001>: 'b'
        #             <Key name:C hash:101001>: 'c'

        ukijumuisha self.assertRaisesRegex(ValueError, 'cannot compare'):
            h.delete(Er)

        h = h.delete(Z)
        self.assertEqual(len(h), orig_len)

        h = h.delete(C)
        self.assertEqual(len(h), orig_len - 1)

        h = h.delete(B)
        self.assertEqual(len(h), orig_len - 2)

        h = h.delete(A)
        self.assertEqual(len(h), orig_len - 3)

        self.assertEqual(h.get(D), 'd')
        self.assertEqual(h.get(E), 'e')

        h = h.delete(A)
        h = h.delete(B)
        h = h.delete(D)
        h = h.delete(E)
        self.assertEqual(len(h), 0)

    eleza test_hamt_delete_3(self):
        A = HashKey(100, 'A')
        B = HashKey(101, 'B')
        C = HashKey(100100, 'C')
        D = HashKey(100100, 'D')
        E = HashKey(104, 'E')

        h = hamt()
        h = h.set(A, 'a')
        h = h.set(B, 'b')
        h = h.set(C, 'c')
        h = h.set(D, 'd')
        h = h.set(E, 'e')

        orig_len = len(h)

        # BitmapNode(size=6 bitmap=0b100110000):
        #     NULL:
        #         BitmapNode(size=4 bitmap=0b1000000000000000000001000):
        #             <Key name:A hash:100>: 'a'
        #             NULL:
        #                 CollisionNode(size=4 id=0x108572410):
        #                     <Key name:C hash:100100>: 'c'
        #                     <Key name:D hash:100100>: 'd'
        #     <Key name:B hash:101>: 'b'
        #     <Key name:E hash:104>: 'e'

        h = h.delete(A)
        self.assertEqual(len(h), orig_len - 1)

        h = h.delete(E)
        self.assertEqual(len(h), orig_len - 2)

        self.assertEqual(h.get(C), 'c')
        self.assertEqual(h.get(B), 'b')

    eleza test_hamt_delete_4(self):
        A = HashKey(100, 'A')
        B = HashKey(101, 'B')
        C = HashKey(100100, 'C')
        D = HashKey(100100, 'D')
        E = HashKey(100100, 'E')

        h = hamt()
        h = h.set(A, 'a')
        h = h.set(B, 'b')
        h = h.set(C, 'c')
        h = h.set(D, 'd')
        h = h.set(E, 'e')

        orig_len = len(h)

        # BitmapNode(size=4 bitmap=0b110000):
        #     NULL:
        #         BitmapNode(size=4 bitmap=0b1000000000000000000001000):
        #             <Key name:A hash:100>: 'a'
        #             NULL:
        #                 CollisionNode(size=6 id=0x10515ef30):
        #                     <Key name:C hash:100100>: 'c'
        #                     <Key name:D hash:100100>: 'd'
        #                     <Key name:E hash:100100>: 'e'
        #     <Key name:B hash:101>: 'b'

        h = h.delete(D)
        self.assertEqual(len(h), orig_len - 1)

        h = h.delete(E)
        self.assertEqual(len(h), orig_len - 2)

        h = h.delete(C)
        self.assertEqual(len(h), orig_len - 3)

        h = h.delete(A)
        self.assertEqual(len(h), orig_len - 4)

        h = h.delete(B)
        self.assertEqual(len(h), 0)

    eleza test_hamt_delete_5(self):
        h = hamt()

        keys = []
        kila i kwenye range(17):
            key = HashKey(i, str(i))
            keys.append(key)
            h = h.set(key, f'val-{i}')

        collision_key16 = HashKey(16, '18')
        h = h.set(collision_key16, 'collision')

        # ArrayNode(id=0x10f8b9318):
        #     0::
        #     BitmapNode(size=2 count=1 bitmap=0b1):
        #         <Key name:0 hash:0>: 'val-0'
        #
        # ... 14 more BitmapNodes ...
        #
        #     15::
        #     BitmapNode(size=2 count=1 bitmap=0b1):
        #         <Key name:15 hash:15>: 'val-15'
        #
        #     16::
        #     BitmapNode(size=2 count=1 bitmap=0b1):
        #         NULL:
        #             CollisionNode(size=4 id=0x10f2f5af8):
        #                 <Key name:16 hash:16>: 'val-16'
        #                 <Key name:18 hash:16>: 'collision'

        self.assertEqual(len(h), 18)

        h = h.delete(keys[2])
        self.assertEqual(len(h), 17)

        h = h.delete(collision_key16)
        self.assertEqual(len(h), 16)
        h = h.delete(keys[16])
        self.assertEqual(len(h), 15)

        h = h.delete(keys[1])
        self.assertEqual(len(h), 14)
        h = h.delete(keys[1])
        self.assertEqual(len(h), 14)

        kila key kwenye keys:
            h = h.delete(key)
        self.assertEqual(len(h), 0)

    eleza test_hamt_items_1(self):
        A = HashKey(100, 'A')
        B = HashKey(201001, 'B')
        C = HashKey(101001, 'C')
        D = HashKey(103, 'D')
        E = HashKey(104, 'E')
        F = HashKey(110, 'F')

        h = hamt()
        h = h.set(A, 'a')
        h = h.set(B, 'b')
        h = h.set(C, 'c')
        h = h.set(D, 'd')
        h = h.set(E, 'e')
        h = h.set(F, 'f')

        it = h.items()
        self.assertEqual(
            set(list(it)),
            {(A, 'a'), (B, 'b'), (C, 'c'), (D, 'd'), (E, 'e'), (F, 'f')})

    eleza test_hamt_items_2(self):
        A = HashKey(100, 'A')
        B = HashKey(101, 'B')
        C = HashKey(100100, 'C')
        D = HashKey(100100, 'D')
        E = HashKey(100100, 'E')
        F = HashKey(110, 'F')

        h = hamt()
        h = h.set(A, 'a')
        h = h.set(B, 'b')
        h = h.set(C, 'c')
        h = h.set(D, 'd')
        h = h.set(E, 'e')
        h = h.set(F, 'f')

        it = h.items()
        self.assertEqual(
            set(list(it)),
            {(A, 'a'), (B, 'b'), (C, 'c'), (D, 'd'), (E, 'e'), (F, 'f')})

    eleza test_hamt_keys_1(self):
        A = HashKey(100, 'A')
        B = HashKey(101, 'B')
        C = HashKey(100100, 'C')
        D = HashKey(100100, 'D')
        E = HashKey(100100, 'E')
        F = HashKey(110, 'F')

        h = hamt()
        h = h.set(A, 'a')
        h = h.set(B, 'b')
        h = h.set(C, 'c')
        h = h.set(D, 'd')
        h = h.set(E, 'e')
        h = h.set(F, 'f')

        self.assertEqual(set(list(h.keys())), {A, B, C, D, E, F})
        self.assertEqual(set(list(h)), {A, B, C, D, E, F})

    eleza test_hamt_items_3(self):
        h = hamt()
        self.assertEqual(len(h.items()), 0)
        self.assertEqual(list(h.items()), [])

    eleza test_hamt_eq_1(self):
        A = HashKey(100, 'A')
        B = HashKey(101, 'B')
        C = HashKey(100100, 'C')
        D = HashKey(100100, 'D')
        E = HashKey(120, 'E')

        h1 = hamt()
        h1 = h1.set(A, 'a')
        h1 = h1.set(B, 'b')
        h1 = h1.set(C, 'c')
        h1 = h1.set(D, 'd')

        h2 = hamt()
        h2 = h2.set(A, 'a')

        self.assertUongo(h1 == h2)
        self.assertKweli(h1 != h2)

        h2 = h2.set(B, 'b')
        self.assertUongo(h1 == h2)
        self.assertKweli(h1 != h2)

        h2 = h2.set(C, 'c')
        self.assertUongo(h1 == h2)
        self.assertKweli(h1 != h2)

        h2 = h2.set(D, 'd2')
        self.assertUongo(h1 == h2)
        self.assertKweli(h1 != h2)

        h2 = h2.set(D, 'd')
        self.assertKweli(h1 == h2)
        self.assertUongo(h1 != h2)

        h2 = h2.set(E, 'e')
        self.assertUongo(h1 == h2)
        self.assertKweli(h1 != h2)

        h2 = h2.delete(D)
        self.assertUongo(h1 == h2)
        self.assertKweli(h1 != h2)

        h2 = h2.set(E, 'd')
        self.assertUongo(h1 == h2)
        self.assertKweli(h1 != h2)

    eleza test_hamt_eq_2(self):
        A = HashKey(100, 'A')
        Er = HashKey(100, 'Er', error_on_eq_to=A)

        h1 = hamt()
        h1 = h1.set(A, 'a')

        h2 = hamt()
        h2 = h2.set(Er, 'a')

        ukijumuisha self.assertRaisesRegex(ValueError, 'cannot compare'):
            h1 == h2

        ukijumuisha self.assertRaisesRegex(ValueError, 'cannot compare'):
            h1 != h2

    eleza test_hamt_gc_1(self):
        A = HashKey(100, 'A')

        h = hamt()
        h = h.set(0, 0)  # empty HAMT node ni memoized kwenye hamt.c
        ref = weakref.ref(h)

        a = []
        a.append(a)
        a.append(h)
        b = []
        a.append(b)
        b.append(a)
        h = h.set(A, b)

        toa h, a, b

        gc.collect()
        gc.collect()
        gc.collect()

        self.assertIsTupu(ref())

    eleza test_hamt_gc_2(self):
        A = HashKey(100, 'A')
        B = HashKey(101, 'B')

        h = hamt()
        h = h.set(A, 'a')
        h = h.set(A, h)

        ref = weakref.ref(h)
        hi = h.items()
        next(hi)

        toa h, hi

        gc.collect()
        gc.collect()
        gc.collect()

        self.assertIsTupu(ref())

    eleza test_hamt_in_1(self):
        A = HashKey(100, 'A')
        AA = HashKey(100, 'A')

        B = HashKey(101, 'B')

        h = hamt()
        h = h.set(A, 1)

        self.assertKweli(A kwenye h)
        self.assertUongo(B kwenye h)

        ukijumuisha self.assertRaises(EqError):
            ukijumuisha HaskKeyCrasher(error_on_eq=Kweli):
                AA kwenye h

        ukijumuisha self.assertRaises(HashingError):
            ukijumuisha HaskKeyCrasher(error_on_hash=Kweli):
                AA kwenye h

    eleza test_hamt_getitem_1(self):
        A = HashKey(100, 'A')
        AA = HashKey(100, 'A')

        B = HashKey(101, 'B')

        h = hamt()
        h = h.set(A, 1)

        self.assertEqual(h[A], 1)
        self.assertEqual(h[AA], 1)

        ukijumuisha self.assertRaises(KeyError):
            h[B]

        ukijumuisha self.assertRaises(EqError):
            ukijumuisha HaskKeyCrasher(error_on_eq=Kweli):
                h[AA]

        ukijumuisha self.assertRaises(HashingError):
            ukijumuisha HaskKeyCrasher(error_on_hash=Kweli):
                h[AA]


ikiwa __name__ == "__main__":
    unittest.main()
