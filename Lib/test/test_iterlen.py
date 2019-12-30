""" Test Iterator Length Transparency

Some functions ama methods which accept general iterable arguments have
optional, more efficient code paths ikiwa they know how many items to expect.
For instance, map(func, iterable), will pre-allocate the exact amount of
space required whenever the iterable can report its length.

The desired invariant is:  len(it)==len(list(it)).

A complication ni that an iterable na iterator can be the same object. To
maintain the invariant, an iterator needs to dynamically update its length.
For instance, an iterable such kama range(10) always reports its length kama ten,
but it=iter(range(10)) starts at ten, na then goes to nine after next(it).
Having this capability means that map() can ignore the distinction between
map(func, iterable) na map(func, iter(iterable)).

When the iterable ni immutable, the implementation can straight-forwardly
report the original length minus the cumulative number of calls to next().
This ni the case kila tuples, range objects, na itertools.repeat().

Some containers become temporarily immutable during iteration.  This includes
dicts, sets, na collections.deque.  Their implementation ni equally simple
though they need to permanently set their length to zero whenever there is
an attempt to iterate after a length mutation.

The situation slightly more involved whenever an object allows length mutation
during iteration.  Lists na sequence iterators are dynamically updatable.
So, ikiwa a list ni extended during iteration, the iterator will endelea through
the new items.  If it shrinks to a point before the most recent iteration,
then no further items are available na the length ni reported at zero.

Reversed objects can also be wrapped around mutable objects; however, any
appends after the current position are ignored.  Any other approach leads
to confusion na possibly returning the same item more than once.

The iterators sio listed above, such kama enumerate na the other itertools,
are sio length transparent because they have no way to distinguish between
iterables that report static length na iterators whose length changes with
each call (i.e. the difference between enumerate('abc') na
enumerate(iter('abc')).

"""

agiza unittest
kutoka itertools agiza repeat
kutoka collections agiza deque
kutoka operator agiza length_hint

n = 10


kundi TestInvariantWithoutMutations:

    eleza test_invariant(self):
        it = self.it
        kila i kwenye reversed(range(1, n+1)):
            self.assertEqual(length_hint(it), i)
            next(it)
        self.assertEqual(length_hint(it), 0)
        self.assertRaises(StopIteration, next, it)
        self.assertEqual(length_hint(it), 0)

kundi TestTemporarilyImmutable(TestInvariantWithoutMutations):

    eleza test_immutable_during_iteration(self):
        # objects such kama deques, sets, na dictionaries enforce
        # length immutability  during iteration

        it = self.it
        self.assertEqual(length_hint(it), n)
        next(it)
        self.assertEqual(length_hint(it), n-1)
        self.mutate()
        self.assertRaises(RuntimeError, next, it)
        self.assertEqual(length_hint(it), 0)

## ------- Concrete Type Tests -------

kundi TestRepeat(TestInvariantWithoutMutations, unittest.TestCase):

    eleza setUp(self):
        self.it = repeat(Tupu, n)

kundi TestXrange(TestInvariantWithoutMutations, unittest.TestCase):

    eleza setUp(self):
        self.it = iter(range(n))

kundi TestXrangeCustomReversed(TestInvariantWithoutMutations, unittest.TestCase):

    eleza setUp(self):
        self.it = reversed(range(n))

kundi TestTuple(TestInvariantWithoutMutations, unittest.TestCase):

    eleza setUp(self):
        self.it = iter(tuple(range(n)))

## ------- Types that should sio be mutated during iteration -------

kundi TestDeque(TestTemporarilyImmutable, unittest.TestCase):

    eleza setUp(self):
        d = deque(range(n))
        self.it = iter(d)
        self.mutate = d.pop

kundi TestDequeReversed(TestTemporarilyImmutable, unittest.TestCase):

    eleza setUp(self):
        d = deque(range(n))
        self.it = reversed(d)
        self.mutate = d.pop

kundi TestDictKeys(TestTemporarilyImmutable, unittest.TestCase):

    eleza setUp(self):
        d = dict.fromkeys(range(n))
        self.it = iter(d)
        self.mutate = d.popitem

kundi TestDictItems(TestTemporarilyImmutable, unittest.TestCase):

    eleza setUp(self):
        d = dict.fromkeys(range(n))
        self.it = iter(d.items())
        self.mutate = d.popitem

kundi TestDictValues(TestTemporarilyImmutable, unittest.TestCase):

    eleza setUp(self):
        d = dict.fromkeys(range(n))
        self.it = iter(d.values())
        self.mutate = d.popitem

kundi TestSet(TestTemporarilyImmutable, unittest.TestCase):

    eleza setUp(self):
        d = set(range(n))
        self.it = iter(d)
        self.mutate = d.pop

## ------- Types that can mutate during iteration -------

kundi TestList(TestInvariantWithoutMutations, unittest.TestCase):

    eleza setUp(self):
        self.it = iter(range(n))

    eleza test_mutation(self):
        d = list(range(n))
        it = iter(d)
        next(it)
        next(it)
        self.assertEqual(length_hint(it), n - 2)
        d.append(n)
        self.assertEqual(length_hint(it), n - 1)  # grow ukijumuisha append
        d[1:] = []
        self.assertEqual(length_hint(it), 0)
        self.assertEqual(list(it), [])
        d.extend(range(20))
        self.assertEqual(length_hint(it), 0)


kundi TestListReversed(TestInvariantWithoutMutations, unittest.TestCase):

    eleza setUp(self):
        self.it = reversed(range(n))

    eleza test_mutation(self):
        d = list(range(n))
        it = reversed(d)
        next(it)
        next(it)
        self.assertEqual(length_hint(it), n - 2)
        d.append(n)
        self.assertEqual(length_hint(it), n - 2)  # ignore append
        d[1:] = []
        self.assertEqual(length_hint(it), 0)
        self.assertEqual(list(it), [])  # confirm invariant
        d.extend(range(20))
        self.assertEqual(length_hint(it), 0)

## -- Check to make sure exceptions are sio suppressed by __length_hint__()


kundi BadLen(object):
    eleza __iter__(self):
        rudisha iter(range(10))

    eleza __len__(self):
        ashiria RuntimeError('hello')


kundi BadLengthHint(object):
    eleza __iter__(self):
        rudisha iter(range(10))

    eleza __length_hint__(self):
        ashiria RuntimeError('hello')


kundi TupuLengthHint(object):
    eleza __iter__(self):
        rudisha iter(range(10))

    eleza __length_hint__(self):
        rudisha NotImplemented


kundi TestLengthHintExceptions(unittest.TestCase):

    eleza test_issue1242657(self):
        self.assertRaises(RuntimeError, list, BadLen())
        self.assertRaises(RuntimeError, list, BadLengthHint())
        self.assertRaises(RuntimeError, [].extend, BadLen())
        self.assertRaises(RuntimeError, [].extend, BadLengthHint())
        b = bytearray(range(10))
        self.assertRaises(RuntimeError, b.extend, BadLen())
        self.assertRaises(RuntimeError, b.extend, BadLengthHint())

    eleza test_invalid_hint(self):
        # Make sure an invalid result doesn't muck-up the works
        self.assertEqual(list(TupuLengthHint()), list(range(10)))


ikiwa __name__ == "__main__":
    unittest.main()
