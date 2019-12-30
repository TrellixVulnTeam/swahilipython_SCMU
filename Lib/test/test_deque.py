kutoka collections agiza deque
agiza unittest
kutoka test agiza support, seq_tests
agiza gc
agiza weakref
agiza copy
agiza pickle
agiza random
agiza struct

BIG = 100000

eleza fail():
     ashiria SyntaxError
    tuma 1

kundi BadCmp:
    eleza __eq__(self, other):
         ashiria RuntimeError

kundi MutateCmp:
    eleza __init__(self, deque, result):
        self.deque = deque
        self.result = result
    eleza __eq__(self, other):
        self.deque.clear()
        rudisha self.result

kundi TestBasic(unittest.TestCase):

    eleza test_basics(self):
        d = deque(range(-5125, -5000))
        d.__init__(range(200))
        kila i kwenye range(200, 400):
            d.append(i)
        kila i kwenye reversed(range(-200, 0)):
            d.appendleft(i)
        self.assertEqual(list(d), list(range(-200, 400)))
        self.assertEqual(len(d), 600)

        left = [d.popleft() kila i kwenye range(250)]
        self.assertEqual(left, list(range(-200, 50)))
        self.assertEqual(list(d), list(range(50, 400)))

        right = [d.pop() kila i kwenye range(250)]
        right.reverse()
        self.assertEqual(right, list(range(150, 400)))
        self.assertEqual(list(d), list(range(50, 150)))

    eleza test_maxlen(self):
        self.assertRaises(ValueError, deque, 'abc', -1)
        self.assertRaises(ValueError, deque, 'abc', -2)
        it = iter(range(10))
        d = deque(it, maxlen=3)
        self.assertEqual(list(it), [])
        self.assertEqual(repr(d), 'deque([7, 8, 9], maxlen=3)')
        self.assertEqual(list(d), [7, 8, 9])
        self.assertEqual(d, deque(range(10), 3))
        d.append(10)
        self.assertEqual(list(d), [8, 9, 10])
        d.appendleft(7)
        self.assertEqual(list(d), [7, 8, 9])
        d.extend([10, 11])
        self.assertEqual(list(d), [9, 10, 11])
        d.extendleft([8, 7])
        self.assertEqual(list(d), [7, 8, 9])
        d = deque(range(200), maxlen=10)
        d.append(d)
        support.unlink(support.TESTFN)
        fo = open(support.TESTFN, "w")
        jaribu:
            fo.write(str(d))
            fo.close()
            fo = open(support.TESTFN, "r")
            self.assertEqual(fo.read(), repr(d))
        mwishowe:
            fo.close()
            support.unlink(support.TESTFN)

        d = deque(range(10), maxlen=Tupu)
        self.assertEqual(repr(d), 'deque([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])')
        fo = open(support.TESTFN, "w")
        jaribu:
            fo.write(str(d))
            fo.close()
            fo = open(support.TESTFN, "r")
            self.assertEqual(fo.read(), repr(d))
        mwishowe:
            fo.close()
            support.unlink(support.TESTFN)

    eleza test_maxlen_zero(self):
        it = iter(range(100))
        deque(it, maxlen=0)
        self.assertEqual(list(it), [])

        it = iter(range(100))
        d = deque(maxlen=0)
        d.extend(it)
        self.assertEqual(list(it), [])

        it = iter(range(100))
        d = deque(maxlen=0)
        d.extendleft(it)
        self.assertEqual(list(it), [])

    eleza test_maxlen_attribute(self):
        self.assertEqual(deque().maxlen, Tupu)
        self.assertEqual(deque('abc').maxlen, Tupu)
        self.assertEqual(deque('abc', maxlen=4).maxlen, 4)
        self.assertEqual(deque('abc', maxlen=2).maxlen, 2)
        self.assertEqual(deque('abc', maxlen=0).maxlen, 0)
        ukijumuisha self.assertRaises(AttributeError):
            d = deque('abc')
            d.maxlen = 10

    eleza test_count(self):
        kila s kwenye ('', 'abracadabra', 'simsalabim'*500+'abc'):
            s = list(s)
            d = deque(s)
            kila letter kwenye 'abcdefghijklmnopqrstuvwxyz':
                self.assertEqual(s.count(letter), d.count(letter), (s, d, letter))
        self.assertRaises(TypeError, d.count)       # too few args
        self.assertRaises(TypeError, d.count, 1, 2) # too many args
        kundi BadCompare:
            eleza __eq__(self, other):
                 ashiria ArithmeticError
        d = deque([1, 2, BadCompare(), 3])
        self.assertRaises(ArithmeticError, d.count, 2)
        d = deque([1, 2, 3])
        self.assertRaises(ArithmeticError, d.count, BadCompare())
        kundi MutatingCompare:
            eleza __eq__(self, other):
                self.d.pop()
                rudisha Kweli
        m = MutatingCompare()
        d = deque([1, 2, 3, m, 4, 5])
        m.d = d
        self.assertRaises(RuntimeError, d.count, 3)

        # test issue11004
        # block advance failed after rotation aligned elements on right side of block
        d = deque([Tupu]*16)
        kila i kwenye range(len(d)):
            d.rotate(-1)
        d.rotate(1)
        self.assertEqual(d.count(1), 0)
        self.assertEqual(d.count(Tupu), 16)

    eleza test_comparisons(self):
        d = deque('xabc'); d.popleft()
        kila e kwenye [d, deque('abc'), deque('ab'), deque(), list(d)]:
            self.assertEqual(d==e, type(d)==type(e) na list(d)==list(e))
            self.assertEqual(d!=e, not(type(d)==type(e) na list(d)==list(e)))

        args = map(deque, ('', 'a', 'b', 'ab', 'ba', 'abc', 'xba', 'xabc', 'cba'))
        kila x kwenye args:
            kila y kwenye args:
                self.assertEqual(x == y, list(x) == list(y), (x,y))
                self.assertEqual(x != y, list(x) != list(y), (x,y))
                self.assertEqual(x <  y, list(x) <  list(y), (x,y))
                self.assertEqual(x <= y, list(x) <= list(y), (x,y))
                self.assertEqual(x >  y, list(x) >  list(y), (x,y))
                self.assertEqual(x >= y, list(x) >= list(y), (x,y))

    eleza test_contains(self):
        n = 200

        d = deque(range(n))
        kila i kwenye range(n):
            self.assertKweli(i kwenye d)
        self.assertKweli((n+1) sio kwenye d)

        # Test detection of mutation during iteration
        d = deque(range(n))
        d[n//2] = MutateCmp(d, Uongo)
        ukijumuisha self.assertRaises(RuntimeError):
            n kwenye d

        # Test detection of comparison exceptions
        d = deque(range(n))
        d[n//2] = BadCmp()
        ukijumuisha self.assertRaises(RuntimeError):
            n kwenye d

    eleza test_extend(self):
        d = deque('a')
        self.assertRaises(TypeError, d.extend, 1)
        d.extend('bcd')
        self.assertEqual(list(d), list('abcd'))
        d.extend(d)
        self.assertEqual(list(d), list('abcdabcd'))

    eleza test_add(self):
        d = deque()
        e = deque('abc')
        f = deque('def')
        self.assertEqual(d + d, deque())
        self.assertEqual(e + f, deque('abcdef'))
        self.assertEqual(e + e, deque('abcabc'))
        self.assertEqual(e + d, deque('abc'))
        self.assertEqual(d + e, deque('abc'))
        self.assertIsNot(d + d, deque())
        self.assertIsNot(e + d, deque('abc'))
        self.assertIsNot(d + e, deque('abc'))

        g = deque('abcdef', maxlen=4)
        h = deque('gh')
        self.assertEqual(g + h, deque('efgh'))

        ukijumuisha self.assertRaises(TypeError):
            deque('abc') + 'def'

    eleza test_iadd(self):
        d = deque('a')
        d += 'bcd'
        self.assertEqual(list(d), list('abcd'))
        d += d
        self.assertEqual(list(d), list('abcdabcd'))

    eleza test_extendleft(self):
        d = deque('a')
        self.assertRaises(TypeError, d.extendleft, 1)
        d.extendleft('bcd')
        self.assertEqual(list(d), list(reversed('abcd')))
        d.extendleft(d)
        self.assertEqual(list(d), list('abcddcba'))
        d = deque()
        d.extendleft(range(1000))
        self.assertEqual(list(d), list(reversed(range(1000))))
        self.assertRaises(SyntaxError, d.extendleft, fail())

    eleza test_getitem(self):
        n = 200
        d = deque(range(n))
        l = list(range(n))
        kila i kwenye range(n):
            d.popleft()
            l.pop(0)
            ikiwa random.random() < 0.5:
                d.append(i)
                l.append(i)
            kila j kwenye range(1-len(l), len(l)):
                assert d[j] == l[j]

        d = deque('superman')
        self.assertEqual(d[0], 's')
        self.assertEqual(d[-1], 'n')
        d = deque()
        self.assertRaises(IndexError, d.__getitem__, 0)
        self.assertRaises(IndexError, d.__getitem__, -1)

    eleza test_index(self):
        kila n kwenye 1, 2, 30, 40, 200:

            d = deque(range(n))
            kila i kwenye range(n):
                self.assertEqual(d.index(i), i)

            ukijumuisha self.assertRaises(ValueError):
                d.index(n+1)

            # Test detection of mutation during iteration
            d = deque(range(n))
            d[n//2] = MutateCmp(d, Uongo)
            ukijumuisha self.assertRaises(RuntimeError):
                d.index(n)

            # Test detection of comparison exceptions
            d = deque(range(n))
            d[n//2] = BadCmp()
            ukijumuisha self.assertRaises(RuntimeError):
                d.index(n)

        # Test start na stop arguments behavior matches list.index()
        elements = 'ABCDEFGHI'
        nonelement = 'Z'
        d = deque(elements * 2)
        s = list(elements * 2)
        kila start kwenye range(-5 - len(s)*2, 5 + len(s) * 2):
            kila stop kwenye range(-5 - len(s)*2, 5 + len(s) * 2):
                kila element kwenye elements + 'Z':
                    jaribu:
                        target = s.index(element, start, stop)
                    except ValueError:
                        ukijumuisha self.assertRaises(ValueError):
                            d.index(element, start, stop)
                    isipokua:
                        self.assertEqual(d.index(element, start, stop), target)

        # Test large start argument
        d = deque(range(0, 10000, 10))
        kila step kwenye range(100):
            i = d.index(8500, 700)
            self.assertEqual(d[i], 8500)
            # Repeat test ukijumuisha a different internal offset
            d.rotate()

    eleza test_index_bug_24913(self):
        d = deque('A' * 3)
        ukijumuisha self.assertRaises(ValueError):
            i = d.index("Hello world", 0, 4)

    eleza test_insert(self):
        # Test to make sure insert behaves like lists
        elements = 'ABCDEFGHI'
        kila i kwenye range(-5 - len(elements)*2, 5 + len(elements) * 2):
            d = deque('ABCDEFGHI')
            s = list('ABCDEFGHI')
            d.insert(i, 'Z')
            s.insert(i, 'Z')
            self.assertEqual(list(d), s)

    eleza test_insert_bug_26194(self):
        data = 'ABC'
        d = deque(data, maxlen=len(data))
        ukijumuisha self.assertRaises(IndexError):
            d.insert(2, Tupu)

        elements = 'ABCDEFGHI'
        kila i kwenye range(-len(elements), len(elements)):
            d = deque(elements, maxlen=len(elements)+1)
            d.insert(i, 'Z')
            ikiwa i >= 0:
                self.assertEqual(d[i], 'Z')
            isipokua:
                self.assertEqual(d[i-1], 'Z')

    eleza test_imul(self):
        kila n kwenye (-10, -1, 0, 1, 2, 10, 1000):
            d = deque()
            d *= n
            self.assertEqual(d, deque())
            self.assertIsTupu(d.maxlen)

        kila n kwenye (-10, -1, 0, 1, 2, 10, 1000):
            d = deque('a')
            d *= n
            self.assertEqual(d, deque('a' * n))
            self.assertIsTupu(d.maxlen)

        kila n kwenye (-10, -1, 0, 1, 2, 10, 499, 500, 501, 1000):
            d = deque('a', 500)
            d *= n
            self.assertEqual(d, deque('a' * min(n, 500)))
            self.assertEqual(d.maxlen, 500)

        kila n kwenye (-10, -1, 0, 1, 2, 10, 1000):
            d = deque('abcdef')
            d *= n
            self.assertEqual(d, deque('abcdef' * n))
            self.assertIsTupu(d.maxlen)

        kila n kwenye (-10, -1, 0, 1, 2, 10, 499, 500, 501, 1000):
            d = deque('abcdef', 500)
            d *= n
            self.assertEqual(d, deque(('abcdef' * n)[-500:]))
            self.assertEqual(d.maxlen, 500)

    eleza test_mul(self):
        d = deque('abc')
        self.assertEqual(d * -5, deque())
        self.assertEqual(d * 0, deque())
        self.assertEqual(d * 1, deque('abc'))
        self.assertEqual(d * 2, deque('abcabc'))
        self.assertEqual(d * 3, deque('abcabcabc'))
        self.assertIsNot(d * 1, d)

        self.assertEqual(deque() * 0, deque())
        self.assertEqual(deque() * 1, deque())
        self.assertEqual(deque() * 5, deque())

        self.assertEqual(-5 * d, deque())
        self.assertEqual(0 * d, deque())
        self.assertEqual(1 * d, deque('abc'))
        self.assertEqual(2 * d, deque('abcabc'))
        self.assertEqual(3 * d, deque('abcabcabc'))

        d = deque('abc', maxlen=5)
        self.assertEqual(d * -5, deque())
        self.assertEqual(d * 0, deque())
        self.assertEqual(d * 1, deque('abc'))
        self.assertEqual(d * 2, deque('bcabc'))
        self.assertEqual(d * 30, deque('bcabc'))

    eleza test_setitem(self):
        n = 200
        d = deque(range(n))
        kila i kwenye range(n):
            d[i] = 10 * i
        self.assertEqual(list(d), [10*i kila i kwenye range(n)])
        l = list(d)
        kila i kwenye range(1-n, 0, -1):
            d[i] = 7*i
            l[i] = 7*i
        self.assertEqual(list(d), l)

    eleza test_delitem(self):
        n = 500         # O(n**2) test, don't make this too big
        d = deque(range(n))
        self.assertRaises(IndexError, d.__delitem__, -n-1)
        self.assertRaises(IndexError, d.__delitem__, n)
        kila i kwenye range(n):
            self.assertEqual(len(d), n-i)
            j = random.randrange(-len(d), len(d))
            val = d[j]
            self.assertIn(val, d)
            toa d[j]
            self.assertNotIn(val, d)
        self.assertEqual(len(d), 0)

    eleza test_reverse(self):
        n = 500         # O(n**2) test, don't make this too big
        data = [random.random() kila i kwenye range(n)]
        kila i kwenye range(n):
            d = deque(data[:i])
            r = d.reverse()
            self.assertEqual(list(d), list(reversed(data[:i])))
            self.assertIs(r, Tupu)
            d.reverse()
            self.assertEqual(list(d), data[:i])
        self.assertRaises(TypeError, d.reverse, 1)          # Arity ni zero

    eleza test_rotate(self):
        s = tuple('abcde')
        n = len(s)

        d = deque(s)
        d.rotate(1)             # verify rot(1)
        self.assertEqual(''.join(d), 'eabcd')

        d = deque(s)
        d.rotate(-1)            # verify rot(-1)
        self.assertEqual(''.join(d), 'bcdea')
        d.rotate()              # check default to 1
        self.assertEqual(tuple(d), s)

        kila i kwenye range(n*3):
            d = deque(s)
            e = deque(d)
            d.rotate(i)         # check vs. rot(1) n times
            kila j kwenye range(i):
                e.rotate(1)
            self.assertEqual(tuple(d), tuple(e))
            d.rotate(-i)        # check that it works kwenye reverse
            self.assertEqual(tuple(d), s)
            e.rotate(n-i)       # check that it wraps forward
            self.assertEqual(tuple(e), s)

        kila i kwenye range(n*3):
            d = deque(s)
            e = deque(d)
            d.rotate(-i)
            kila j kwenye range(i):
                e.rotate(-1)    # check vs. rot(-1) n times
            self.assertEqual(tuple(d), tuple(e))
            d.rotate(i)         # check that it works kwenye reverse
            self.assertEqual(tuple(d), s)
            e.rotate(i-n)       # check that it wraps backaround
            self.assertEqual(tuple(e), s)

        d = deque(s)
        e = deque(s)
        e.rotate(BIG+17)        # verify on long series of rotates
        dr = d.rotate
        kila i kwenye range(BIG+17):
            dr()
        self.assertEqual(tuple(d), tuple(e))

        self.assertRaises(TypeError, d.rotate, 'x')   # Wrong arg type
        self.assertRaises(TypeError, d.rotate, 1, 10) # Too many args

        d = deque()
        d.rotate()              # rotate an empty deque
        self.assertEqual(d, deque())

    eleza test_len(self):
        d = deque('ab')
        self.assertEqual(len(d), 2)
        d.popleft()
        self.assertEqual(len(d), 1)
        d.pop()
        self.assertEqual(len(d), 0)
        self.assertRaises(IndexError, d.pop)
        self.assertEqual(len(d), 0)
        d.append('c')
        self.assertEqual(len(d), 1)
        d.appendleft('d')
        self.assertEqual(len(d), 2)
        d.clear()
        self.assertEqual(len(d), 0)

    eleza test_underflow(self):
        d = deque()
        self.assertRaises(IndexError, d.pop)
        self.assertRaises(IndexError, d.popleft)

    eleza test_clear(self):
        d = deque(range(100))
        self.assertEqual(len(d), 100)
        d.clear()
        self.assertEqual(len(d), 0)
        self.assertEqual(list(d), [])
        d.clear()               # clear an empty deque
        self.assertEqual(list(d), [])

    eleza test_remove(self):
        d = deque('abcdefghcij')
        d.remove('c')
        self.assertEqual(d, deque('abdefghcij'))
        d.remove('c')
        self.assertEqual(d, deque('abdefghij'))
        self.assertRaises(ValueError, d.remove, 'c')
        self.assertEqual(d, deque('abdefghij'))

        # Handle comparison errors
        d = deque(['a', 'b', BadCmp(), 'c'])
        e = deque(d)
        self.assertRaises(RuntimeError, d.remove, 'c')
        kila x, y kwenye zip(d, e):
            # verify that original order na values are retained.
            self.assertKweli(x ni y)

        # Handle evil mutator
        kila match kwenye (Kweli, Uongo):
            d = deque(['ab'])
            d.extend([MutateCmp(d, match), 'c'])
            self.assertRaises(IndexError, d.remove, 'c')
            self.assertEqual(d, deque())

    eleza test_repr(self):
        d = deque(range(200))
        e = eval(repr(d))
        self.assertEqual(list(d), list(e))
        d.append(d)
        self.assertIn('...', repr(d))

    eleza test_andika(self):
        d = deque(range(200))
        d.append(d)
        jaribu:
            support.unlink(support.TESTFN)
            fo = open(support.TESTFN, "w")
            andika(d, file=fo, end='')
            fo.close()
            fo = open(support.TESTFN, "r")
            self.assertEqual(fo.read(), repr(d))
        mwishowe:
            fo.close()
            support.unlink(support.TESTFN)

    eleza test_init(self):
        self.assertRaises(TypeError, deque, 'abc', 2, 3);
        self.assertRaises(TypeError, deque, 1);

    eleza test_hash(self):
        self.assertRaises(TypeError, hash, deque('abc'))

    eleza test_long_steadystate_queue_popleft(self):
        kila size kwenye (0, 1, 2, 100, 1000):
            d = deque(range(size))
            append, pop = d.append, d.popleft
            kila i kwenye range(size, BIG):
                append(i)
                x = pop()
                ikiwa x != i - size:
                    self.assertEqual(x, i-size)
            self.assertEqual(list(d), list(range(BIG-size, BIG)))

    eleza test_long_steadystate_queue_popright(self):
        kila size kwenye (0, 1, 2, 100, 1000):
            d = deque(reversed(range(size)))
            append, pop = d.appendleft, d.pop
            kila i kwenye range(size, BIG):
                append(i)
                x = pop()
                ikiwa x != i - size:
                    self.assertEqual(x, i-size)
            self.assertEqual(list(reversed(list(d))),
                             list(range(BIG-size, BIG)))

    eleza test_big_queue_popleft(self):
        pass
        d = deque()
        append, pop = d.append, d.popleft
        kila i kwenye range(BIG):
            append(i)
        kila i kwenye range(BIG):
            x = pop()
            ikiwa x != i:
                self.assertEqual(x, i)

    eleza test_big_queue_popright(self):
        d = deque()
        append, pop = d.appendleft, d.pop
        kila i kwenye range(BIG):
            append(i)
        kila i kwenye range(BIG):
            x = pop()
            ikiwa x != i:
                self.assertEqual(x, i)

    eleza test_big_stack_right(self):
        d = deque()
        append, pop = d.append, d.pop
        kila i kwenye range(BIG):
            append(i)
        kila i kwenye reversed(range(BIG)):
            x = pop()
            ikiwa x != i:
                self.assertEqual(x, i)
        self.assertEqual(len(d), 0)

    eleza test_big_stack_left(self):
        d = deque()
        append, pop = d.appendleft, d.popleft
        kila i kwenye range(BIG):
            append(i)
        kila i kwenye reversed(range(BIG)):
            x = pop()
            ikiwa x != i:
                self.assertEqual(x, i)
        self.assertEqual(len(d), 0)

    eleza test_roundtrip_iter_init(self):
        d = deque(range(200))
        e = deque(d)
        self.assertNotEqual(id(d), id(e))
        self.assertEqual(list(d), list(e))

    eleza test_pickle(self):
        kila d kwenye deque(range(200)), deque(range(200), 100):
            kila i kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                s = pickle.dumps(d, i)
                e = pickle.loads(s)
                self.assertNotEqual(id(e), id(d))
                self.assertEqual(list(e), list(d))
                self.assertEqual(e.maxlen, d.maxlen)

    eleza test_pickle_recursive(self):
        kila d kwenye deque('abc'), deque('abc', 3):
            d.append(d)
            kila i kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                e = pickle.loads(pickle.dumps(d, i))
                self.assertNotEqual(id(e), id(d))
                self.assertEqual(id(e[-1]), id(e))
                self.assertEqual(e.maxlen, d.maxlen)

    eleza test_iterator_pickle(self):
        orig = deque(range(200))
        data = [i*1.01 kila i kwenye orig]
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            # initial iterator
            itorg = iter(orig)
            dump = pickle.dumps((itorg, orig), proto)
            it, d = pickle.loads(dump)
            kila i, x kwenye enumerate(data):
                d[i] = x
            self.assertEqual(type(it), type(itorg))
            self.assertEqual(list(it), data)

            # running iterator
            next(itorg)
            dump = pickle.dumps((itorg, orig), proto)
            it, d = pickle.loads(dump)
            kila i, x kwenye enumerate(data):
                d[i] = x
            self.assertEqual(type(it), type(itorg))
            self.assertEqual(list(it), data[1:])

            # empty iterator
            kila i kwenye range(1, len(data)):
                next(itorg)
            dump = pickle.dumps((itorg, orig), proto)
            it, d = pickle.loads(dump)
            kila i, x kwenye enumerate(data):
                d[i] = x
            self.assertEqual(type(it), type(itorg))
            self.assertEqual(list(it), [])

            # exhausted iterator
            self.assertRaises(StopIteration, next, itorg)
            dump = pickle.dumps((itorg, orig), proto)
            it, d = pickle.loads(dump)
            kila i, x kwenye enumerate(data):
                d[i] = x
            self.assertEqual(type(it), type(itorg))
            self.assertEqual(list(it), [])

    eleza test_deepcopy(self):
        mut = [10]
        d = deque([mut])
        e = copy.deepcopy(d)
        self.assertEqual(list(d), list(e))
        mut[0] = 11
        self.assertNotEqual(id(d), id(e))
        self.assertNotEqual(list(d), list(e))

    eleza test_copy(self):
        mut = [10]
        d = deque([mut])
        e = copy.copy(d)
        self.assertEqual(list(d), list(e))
        mut[0] = 11
        self.assertNotEqual(id(d), id(e))
        self.assertEqual(list(d), list(e))

        kila i kwenye range(5):
            kila maxlen kwenye range(-1, 6):
                s = [random.random() kila j kwenye range(i)]
                d = deque(s) ikiwa maxlen == -1 isipokua deque(s, maxlen)
                e = d.copy()
                self.assertEqual(d, e)
                self.assertEqual(d.maxlen, e.maxlen)
                self.assertKweli(all(x ni y kila x, y kwenye zip(d, e)))

    eleza test_copy_method(self):
        mut = [10]
        d = deque([mut])
        e = d.copy()
        self.assertEqual(list(d), list(e))
        mut[0] = 11
        self.assertNotEqual(id(d), id(e))
        self.assertEqual(list(d), list(e))

    eleza test_reversed(self):
        kila s kwenye ('abcd', range(2000)):
            self.assertEqual(list(reversed(deque(s))), list(reversed(s)))

    eleza test_reversed_new(self):
        klass = type(reversed(deque()))
        kila s kwenye ('abcd', range(2000)):
            self.assertEqual(list(klass(deque(s))), list(reversed(s)))

    eleza test_gc_doesnt_blowup(self):
        agiza gc
        # This used to assert-fail kwenye deque_traverse() under a debug
        # build, ama run wild ukijumuisha a NULL pointer kwenye a release build.
        d = deque()
        kila i kwenye range(100):
            d.append(1)
            gc.collect()

    eleza test_container_iterator(self):
        # Bug #3680: tp_traverse was sio implemented kila deque iterator objects
        kundi C(object):
            pass
        kila i kwenye range(2):
            obj = C()
            ref = weakref.ref(obj)
            ikiwa i == 0:
                container = deque([obj, 1])
            isipokua:
                container = reversed(deque([obj, 1]))
            obj.x = iter(container)
            toa obj, container
            gc.collect()
            self.assertKweli(ref() ni Tupu, "Cycle was sio collected")

    check_sizeof = support.check_sizeof

    @support.cpython_only
    eleza test_sizeof(self):
        BLOCKLEN = 64
        basesize = support.calcvobjsize('2P4nP')
        blocksize = struct.calcsize('P%dPP' % BLOCKLEN)
        self.assertEqual(object.__sizeof__(deque()), basesize)
        check = self.check_sizeof
        check(deque(), basesize + blocksize)
        check(deque('a'), basesize + blocksize)
        check(deque('a' * (BLOCKLEN - 1)), basesize + blocksize)
        check(deque('a' * BLOCKLEN), basesize + 2 * blocksize)
        check(deque('a' * (42 * BLOCKLEN)), basesize + 43 * blocksize)

kundi TestVariousIteratorArgs(unittest.TestCase):

    eleza test_constructor(self):
        kila s kwenye ("123", "", range(1000), ('do', 1.2), range(2000,2200,5)):
            kila g kwenye (seq_tests.Sequence, seq_tests.IterFunc,
                      seq_tests.IterGen, seq_tests.IterFuncStop,
                      seq_tests.itermulti, seq_tests.iterfunc):
                self.assertEqual(list(deque(g(s))), list(g(s)))
            self.assertRaises(TypeError, deque, seq_tests.IterNextOnly(s))
            self.assertRaises(TypeError, deque, seq_tests.IterNoNext(s))
            self.assertRaises(ZeroDivisionError, deque, seq_tests.IterGenExc(s))

    eleza test_iter_with_altered_data(self):
        d = deque('abcdefg')
        it = iter(d)
        d.pop()
        self.assertRaises(RuntimeError, next, it)

    eleza test_runtime_error_on_empty_deque(self):
        d = deque()
        it = iter(d)
        d.append(10)
        self.assertRaises(RuntimeError, next, it)

kundi Deque(deque):
    pass

kundi DequeWithBadIter(deque):
    eleza __iter__(self):
         ashiria TypeError

kundi TestSubclass(unittest.TestCase):

    eleza test_basics(self):
        d = Deque(range(25))
        d.__init__(range(200))
        kila i kwenye range(200, 400):
            d.append(i)
        kila i kwenye reversed(range(-200, 0)):
            d.appendleft(i)
        self.assertEqual(list(d), list(range(-200, 400)))
        self.assertEqual(len(d), 600)

        left = [d.popleft() kila i kwenye range(250)]
        self.assertEqual(left, list(range(-200, 50)))
        self.assertEqual(list(d), list(range(50, 400)))

        right = [d.pop() kila i kwenye range(250)]
        right.reverse()
        self.assertEqual(right, list(range(150, 400)))
        self.assertEqual(list(d), list(range(50, 150)))

        d.clear()
        self.assertEqual(len(d), 0)

    eleza test_copy_pickle(self):

        d = Deque('abc')

        e = d.__copy__()
        self.assertEqual(type(d), type(e))
        self.assertEqual(list(d), list(e))

        e = Deque(d)
        self.assertEqual(type(d), type(e))
        self.assertEqual(list(d), list(e))

        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            s = pickle.dumps(d, proto)
            e = pickle.loads(s)
            self.assertNotEqual(id(d), id(e))
            self.assertEqual(type(d), type(e))
            self.assertEqual(list(d), list(e))

        d = Deque('abcde', maxlen=4)

        e = d.__copy__()
        self.assertEqual(type(d), type(e))
        self.assertEqual(list(d), list(e))

        e = Deque(d)
        self.assertEqual(type(d), type(e))
        self.assertEqual(list(d), list(e))

        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            s = pickle.dumps(d, proto)
            e = pickle.loads(s)
            self.assertNotEqual(id(d), id(e))
            self.assertEqual(type(d), type(e))
            self.assertEqual(list(d), list(e))

    eleza test_pickle_recursive(self):
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            kila d kwenye Deque('abc'), Deque('abc', 3):
                d.append(d)

                e = pickle.loads(pickle.dumps(d, proto))
                self.assertNotEqual(id(e), id(d))
                self.assertEqual(type(e), type(d))
                self.assertEqual(e.maxlen, d.maxlen)
                dd = d.pop()
                ee = e.pop()
                self.assertEqual(id(ee), id(e))
                self.assertEqual(e, d)

                d.x = d
                e = pickle.loads(pickle.dumps(d, proto))
                self.assertEqual(id(e.x), id(e))

            kila d kwenye DequeWithBadIter('abc'), DequeWithBadIter('abc', 2):
                self.assertRaises(TypeError, pickle.dumps, d, proto)

    eleza test_weakref(self):
        d = deque('gallahad')
        p = weakref.proxy(d)
        self.assertEqual(str(p), str(d))
        d = Tupu
        self.assertRaises(ReferenceError, str, p)

    eleza test_strange_subclass(self):
        kundi X(deque):
            eleza __iter__(self):
                rudisha iter([])
        d1 = X([1,2,3])
        d2 = X([4,5,6])
        d1 == d2   # sio clear ikiwa this ni supposed to be Kweli ama Uongo,
                   # but it used to give a SystemError

    @support.cpython_only
    eleza test_bug_31608(self):
        # The interpreter used to crash kwenye specific cases where a deque
        # subkundi returned a non-deque.
        kundi X(deque):
            pass
        d = X()
        eleza bad___new__(cls, *args, **kwargs):
            rudisha [42]
        X.__new__ = bad___new__
        ukijumuisha self.assertRaises(TypeError):
            d * 42  # shouldn't crash
        ukijumuisha self.assertRaises(TypeError):
            d + deque([1, 2, 3])  # shouldn't crash


kundi SubclassWithKwargs(deque):
    eleza __init__(self, newarg=1):
        deque.__init__(self)

kundi TestSubclassWithKwargs(unittest.TestCase):
    eleza test_subclass_with_kwargs(self):
        # SF bug #1486663 -- this used to erroneously  ashiria a TypeError
        SubclassWithKwargs(newarg=1)

kundi TestSequence(seq_tests.CommonTest):
    type2test = deque

    eleza test_getitem(self):
        # For now, bypass tests that require slicing
        pass

    eleza test_getslice(self):
        # For now, bypass tests that require slicing
        pass

    eleza test_subscript(self):
        # For now, bypass tests that require slicing
        pass

    eleza test_free_after_iterating(self):
        # For now, bypass tests that require slicing
        self.skipTest("Exhausted deque iterator doesn't free a deque")

#==============================================================================

libreftest = """
Example kutoka the Library Reference:  Doc/lib/libcollections.tex

>>> kutoka collections agiza deque
>>> d = deque('ghi')                 # make a new deque ukijumuisha three items
>>> kila elem kwenye d:                   # iterate over the deque's elements
...     andika(elem.upper())
G
H
I
>>> d.append('j')                    # add a new entry to the right side
>>> d.appendleft('f')                # add a new entry to the left side
>>> d                                # show the representation of the deque
deque(['f', 'g', 'h', 'i', 'j'])
>>> d.pop()                          # rudisha na remove the rightmost item
'j'
>>> d.popleft()                      # rudisha na remove the leftmost item
'f'
>>> list(d)                          # list the contents of the deque
['g', 'h', 'i']
>>> d[0]                             # peek at leftmost item
'g'
>>> d[-1]                            # peek at rightmost item
'i'
>>> list(reversed(d))                # list the contents of a deque kwenye reverse
['i', 'h', 'g']
>>> 'h' kwenye d                         # search the deque
Kweli
>>> d.extend('jkl')                  # add multiple elements at once
>>> d
deque(['g', 'h', 'i', 'j', 'k', 'l'])
>>> d.rotate(1)                      # right rotation
>>> d
deque(['l', 'g', 'h', 'i', 'j', 'k'])
>>> d.rotate(-1)                     # left rotation
>>> d
deque(['g', 'h', 'i', 'j', 'k', 'l'])
>>> deque(reversed(d))               # make a new deque kwenye reverse order
deque(['l', 'k', 'j', 'i', 'h', 'g'])
>>> d.clear()                        # empty the deque
>>> d.pop()                          # cannot pop kutoka an empty deque
Traceback (most recent call last):
  File "<pyshell#6>", line 1, kwenye -toplevel-
    d.pop()
IndexError: pop kutoka an empty deque

>>> d.extendleft('abc')              # extendleft() reverses the input order
>>> d
deque(['c', 'b', 'a'])



>>> eleza delete_nth(d, n):
...     d.rotate(-n)
...     d.popleft()
...     d.rotate(n)
...
>>> d = deque('abcdef')
>>> delete_nth(d, 2)   # remove the entry at d[2]
>>> d
deque(['a', 'b', 'd', 'e', 'f'])



>>> eleza roundrobin(*iterables):
...     pending = deque(iter(i) kila i kwenye iterables)
...     wakati pending:
...         task = pending.popleft()
...         jaribu:
...             tuma next(task)
...         except StopIteration:
...             endelea
...         pending.append(task)
...

>>> kila value kwenye roundrobin('abc', 'd', 'efgh'):
...     andika(value)
...
a
d
e
b
f
c
g
h


>>> eleza maketree(iterable):
...     d = deque(iterable)
...     wakati len(d) > 1:
...         pair = [d.popleft(), d.popleft()]
...         d.append(pair)
...     rudisha list(d)
...
>>> andika(maketree('abcdefgh'))
[[[['a', 'b'], ['c', 'd']], [['e', 'f'], ['g', 'h']]]]

"""


#==============================================================================

__test__ = {'libreftest' : libreftest}

eleza test_main(verbose=Tupu):
    agiza sys
    test_classes = (
        TestBasic,
        TestVariousIteratorArgs,
        TestSubclass,
        TestSubclassWithKwargs,
        TestSequence,
    )

    support.run_unittest(*test_classes)

    # verify reference counting
    ikiwa verbose na hasattr(sys, "gettotalrefcount"):
        agiza gc
        counts = [Tupu] * 5
        kila i kwenye range(len(counts)):
            support.run_unittest(*test_classes)
            gc.collect()
            counts[i] = sys.gettotalrefcount()
        andika(counts)

    # doctests
    kutoka test agiza test_deque
    support.run_doctest(test_deque, verbose)

ikiwa __name__ == "__main__":
    test_main(verbose=Kweli)
