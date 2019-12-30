agiza copy
agiza gc
agiza pickle
agiza sys
agiza unittest
agiza weakref
agiza inspect

kutoka test agiza support

jaribu:
    agiza _testcapi
tatizo ImportError:
    _testcapi = Tupu


# This tests to make sure that ikiwa a SIGINT arrives just before we send into a
# tuma kutoka chain, the KeyboardInterrupt ni raised kwenye the innermost
# generator (see bpo-30039).
@unittest.skipUnless(_testcapi ni sio Tupu na
                     hasattr(_testcapi, "raise_SIGINT_then_send_Tupu"),
                     "needs _testcapi.raise_SIGINT_then_send_Tupu")
kundi SignalAndYieldFromTest(unittest.TestCase):

    eleza generator1(self):
        rudisha (tuma kutoka self.generator2())

    eleza generator2(self):
        jaribu:
            tuma
        tatizo KeyboardInterrupt:
            rudisha "PASSED"
        isipokua:
            rudisha "FAILED"

    eleza test_raise_and_tuma_from(self):
        gen = self.generator1()
        gen.send(Tupu)
        jaribu:
            _testcapi.raise_SIGINT_then_send_Tupu(gen)
        tatizo BaseException kama _exc:
            exc = _exc
        self.assertIs(type(exc), StopIteration)
        self.assertEqual(exc.value, "PASSED")


kundi FinalizationTest(unittest.TestCase):

    eleza test_frame_resurrect(self):
        # A generator frame can be resurrected by a generator's finalization.
        eleza gen():
            nonlocal frame
            jaribu:
                tuma
            mwishowe:
                frame = sys._getframe()

        g = gen()
        wr = weakref.ref(g)
        next(g)
        toa g
        support.gc_collect()
        self.assertIs(wr(), Tupu)
        self.assertKweli(frame)
        toa frame
        support.gc_collect()

    eleza test_refcycle(self):
        # A generator caught kwenye a refcycle gets finalized anyway.
        old_garbage = gc.garbage[:]
        finalized = Uongo
        eleza gen():
            nonlocal finalized
            jaribu:
                g = tuma
                tuma 1
            mwishowe:
                finalized = Kweli

        g = gen()
        next(g)
        g.send(g)
        self.assertGreater(sys.getrefcount(g), 2)
        self.assertUongo(finalized)
        toa g
        support.gc_collect()
        self.assertKweli(finalized)
        self.assertEqual(gc.garbage, old_garbage)

    eleza test_lambda_generator(self):
        # Issue #23192: Test that a lambda returning a generator behaves
        # like the equivalent function
        f = lambda: (tuma 1)
        eleza g(): rudisha (tuma 1)

        # test 'tuma from'
        f2 = lambda: (tuma kutoka g())
        eleza g2(): rudisha (tuma kutoka g())

        f3 = lambda: (tuma kutoka f())
        eleza g3(): rudisha (tuma kutoka f())

        kila gen_fun kwenye (f, g, f2, g2, f3, g3):
            gen = gen_fun()
            self.assertEqual(next(gen), 1)
            ukijumuisha self.assertRaises(StopIteration) kama cm:
                gen.send(2)
            self.assertEqual(cm.exception.value, 2)


kundi GeneratorTest(unittest.TestCase):

    eleza test_name(self):
        eleza func():
            tuma 1

        # check generator names
        gen = func()
        self.assertEqual(gen.__name__, "func")
        self.assertEqual(gen.__qualname__,
                         "GeneratorTest.test_name.<locals>.func")

        # modify generator names
        gen.__name__ = "name"
        gen.__qualname__ = "qualname"
        self.assertEqual(gen.__name__, "name")
        self.assertEqual(gen.__qualname__, "qualname")

        # generator names must be a string na cannot be deleted
        self.assertRaises(TypeError, setattr, gen, '__name__', 123)
        self.assertRaises(TypeError, setattr, gen, '__qualname__', 123)
        self.assertRaises(TypeError, delattr, gen, '__name__')
        self.assertRaises(TypeError, delattr, gen, '__qualname__')

        # modify names of the function creating the generator
        func.__qualname__ = "func_qualname"
        func.__name__ = "func_name"
        gen = func()
        self.assertEqual(gen.__name__, "func_name")
        self.assertEqual(gen.__qualname__, "func_qualname")

        # unnamed generator
        gen = (x kila x kwenye range(10))
        self.assertEqual(gen.__name__,
                         "<genexpr>")
        self.assertEqual(gen.__qualname__,
                         "GeneratorTest.test_name.<locals>.<genexpr>")

    eleza test_copy(self):
        eleza f():
            tuma 1
        g = f()
        ukijumuisha self.assertRaises(TypeError):
            copy.copy(g)

    eleza test_pickle(self):
        eleza f():
            tuma 1
        g = f()
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            ukijumuisha self.assertRaises((TypeError, pickle.PicklingError)):
                pickle.dumps(g, proto)


kundi ExceptionTest(unittest.TestCase):
    # Tests kila the issue #23353: check that the currently handled exception
    # ni correctly saved/restored kwenye PyEval_EvalFrameEx().

    eleza test_except_throw(self):
        eleza store_raise_exc_generator():
            jaribu:
                self.assertEqual(sys.exc_info()[0], Tupu)
                tuma
            tatizo Exception kama exc:
                # exception raised by gen.throw(exc)
                self.assertEqual(sys.exc_info()[0], ValueError)
                self.assertIsTupu(exc.__context__)
                tuma

                # ensure that the exception ni sio lost
                self.assertEqual(sys.exc_info()[0], ValueError)
                tuma

                # we should be able to ashiria back the ValueError
                raise

        make = store_raise_exc_generator()
        next(make)

        jaribu:
            ashiria ValueError()
        tatizo Exception kama exc:
            jaribu:
                make.throw(exc)
            tatizo Exception:
                pita

        next(make)
        ukijumuisha self.assertRaises(ValueError) kama cm:
            next(make)
        self.assertIsTupu(cm.exception.__context__)

        self.assertEqual(sys.exc_info(), (Tupu, Tupu, Tupu))

    eleza test_except_next(self):
        eleza gen():
            self.assertEqual(sys.exc_info()[0], ValueError)
            tuma "done"

        g = gen()
        jaribu:
            ashiria ValueError
        tatizo Exception:
            self.assertEqual(next(g), "done")
        self.assertEqual(sys.exc_info(), (Tupu, Tupu, Tupu))

    eleza test_except_gen_except(self):
        eleza gen():
            jaribu:
                self.assertEqual(sys.exc_info()[0], Tupu)
                tuma
                # we are called kutoka "tatizo ValueError:", TypeError must
                # inherit ValueError kwenye its context
                ashiria TypeError()
            tatizo TypeError kama exc:
                self.assertEqual(sys.exc_info()[0], TypeError)
                self.assertEqual(type(exc.__context__), ValueError)
            # here we are still called kutoka the "tatizo ValueError:"
            self.assertEqual(sys.exc_info()[0], ValueError)
            tuma
            self.assertIsTupu(sys.exc_info()[0])
            tuma "done"

        g = gen()
        next(g)
        jaribu:
            ashiria ValueError
        tatizo Exception:
            next(g)

        self.assertEqual(next(g), "done")
        self.assertEqual(sys.exc_info(), (Tupu, Tupu, Tupu))

    eleza test_except_throw_exception_context(self):
        eleza gen():
            jaribu:
                jaribu:
                    self.assertEqual(sys.exc_info()[0], Tupu)
                    tuma
                tatizo ValueError:
                    # we are called kutoka "tatizo ValueError:"
                    self.assertEqual(sys.exc_info()[0], ValueError)
                    ashiria TypeError()
            tatizo Exception kama exc:
                self.assertEqual(sys.exc_info()[0], TypeError)
                self.assertEqual(type(exc.__context__), ValueError)
            # we are still called kutoka "tatizo ValueError:"
            self.assertEqual(sys.exc_info()[0], ValueError)
            tuma
            self.assertIsTupu(sys.exc_info()[0])
            tuma "done"

        g = gen()
        next(g)
        jaribu:
            ashiria ValueError
        tatizo Exception kama exc:
            g.throw(exc)

        self.assertEqual(next(g), "done")
        self.assertEqual(sys.exc_info(), (Tupu, Tupu, Tupu))

    eleza test_stopiteration_error(self):
        # See also PEP 479.

        eleza gen():
            ashiria StopIteration
            tuma

        ukijumuisha self.assertRaisesRegex(RuntimeError, 'raised StopIteration'):
            next(gen())

    eleza test_tutorial_stopiteration(self):
        # Raise StopIteration" stops the generator too:

        eleza f():
            tuma 1
            ashiria StopIteration
            tuma 2 # never reached

        g = f()
        self.assertEqual(next(g), 1)

        ukijumuisha self.assertRaisesRegex(RuntimeError, 'raised StopIteration'):
            next(g)

    eleza test_return_tuple(self):
        eleza g():
            rudisha (tuma 1)

        gen = g()
        self.assertEqual(next(gen), 1)
        ukijumuisha self.assertRaises(StopIteration) kama cm:
            gen.send((2,))
        self.assertEqual(cm.exception.value, (2,))

    eleza test_return_stopiteration(self):
        eleza g():
            rudisha (tuma 1)

        gen = g()
        self.assertEqual(next(gen), 1)
        ukijumuisha self.assertRaises(StopIteration) kama cm:
            gen.send(StopIteration(2))
        self.assertIsInstance(cm.exception.value, StopIteration)
        self.assertEqual(cm.exception.value.value, 2)


kundi YieldFromTests(unittest.TestCase):
    eleza test_generator_gi_tumafrom(self):
        eleza a():
            self.assertEqual(inspect.getgeneratorstate(gen_b), inspect.GEN_RUNNING)
            self.assertIsTupu(gen_b.gi_tumafrom)
            tuma
            self.assertEqual(inspect.getgeneratorstate(gen_b), inspect.GEN_RUNNING)
            self.assertIsTupu(gen_b.gi_tumafrom)

        eleza b():
            self.assertIsTupu(gen_b.gi_tumafrom)
            tuma kutoka a()
            self.assertIsTupu(gen_b.gi_tumafrom)
            tuma
            self.assertIsTupu(gen_b.gi_tumafrom)

        gen_b = b()
        self.assertEqual(inspect.getgeneratorstate(gen_b), inspect.GEN_CREATED)
        self.assertIsTupu(gen_b.gi_tumafrom)

        gen_b.send(Tupu)
        self.assertEqual(inspect.getgeneratorstate(gen_b), inspect.GEN_SUSPENDED)
        self.assertEqual(gen_b.gi_tumafrom.gi_code.co_name, 'a')

        gen_b.send(Tupu)
        self.assertEqual(inspect.getgeneratorstate(gen_b), inspect.GEN_SUSPENDED)
        self.assertIsTupu(gen_b.gi_tumafrom)

        [] = gen_b  # Exhaust generator
        self.assertEqual(inspect.getgeneratorstate(gen_b), inspect.GEN_CLOSED)
        self.assertIsTupu(gen_b.gi_tumafrom)


tutorial_tests = """
Let's try a simple generator:

    >>> eleza f():
    ...    tuma 1
    ...    tuma 2

    >>> kila i kwenye f():
    ...     andika(i)
    1
    2
    >>> g = f()
    >>> next(g)
    1
    >>> next(g)
    2

"Falling off the end" stops the generator:

    >>> next(g)
    Traceback (most recent call last):
      File "<stdin>", line 1, kwenye ?
      File "<stdin>", line 2, kwenye g
    StopIteration

"return" also stops the generator:

    >>> eleza f():
    ...     tuma 1
    ...     return
    ...     tuma 2 # never reached
    ...
    >>> g = f()
    >>> next(g)
    1
    >>> next(g)
    Traceback (most recent call last):
      File "<stdin>", line 1, kwenye ?
      File "<stdin>", line 3, kwenye f
    StopIteration
    >>> next(g) # once stopped, can't be resumed
    Traceback (most recent call last):
      File "<stdin>", line 1, kwenye ?
    StopIteration

However, "return" na StopIteration are sio exactly equivalent:

    >>> eleza g1():
    ...     jaribu:
    ...         return
    ...     tatizo:
    ...         tuma 1
    ...
    >>> list(g1())
    []

    >>> eleza g2():
    ...     jaribu:
    ...         ashiria StopIteration
    ...     tatizo:
    ...         tuma 42
    >>> andika(list(g2()))
    [42]

This may be surprising at first:

    >>> eleza g3():
    ...     jaribu:
    ...         return
    ...     mwishowe:
    ...         tuma 1
    ...
    >>> list(g3())
    [1]

Let's create an alternate range() function implemented kama a generator:

    >>> eleza yrange(n):
    ...     kila i kwenye range(n):
    ...         tuma i
    ...
    >>> list(yrange(5))
    [0, 1, 2, 3, 4]

Generators always rudisha to the most recent caller:

    >>> eleza creator():
    ...     r = yrange(5)
    ...     andika("creator", next(r))
    ...     rudisha r
    ...
    >>> eleza caller():
    ...     r = creator()
    ...     kila i kwenye r:
    ...             andika("caller", i)
    ...
    >>> caller()
    creator 0
    caller 1
    caller 2
    caller 3
    caller 4

Generators can call other generators:

    >>> eleza zrange(n):
    ...     kila i kwenye yrange(n):
    ...         tuma i
    ...
    >>> list(zrange(5))
    [0, 1, 2, 3, 4]

"""

# The examples kutoka PEP 255.

pep_tests = """

Specification:  Yield

    Restriction:  A generator cannot be resumed wakati it ni actively
    running:

    >>> eleza g():
    ...     i = next(me)
    ...     tuma i
    >>> me = g()
    >>> next(me)
    Traceback (most recent call last):
     ...
      File "<string>", line 2, kwenye g
    ValueError: generator already executing

Specification: Return

    Note that rudisha isn't always equivalent to raising StopIteration:  the
    difference lies kwenye how enclosing try/tatizo constructs are treated.
    For example,

        >>> eleza f1():
        ...     jaribu:
        ...         return
        ...     tatizo:
        ...        tuma 1
        >>> andika(list(f1()))
        []

    because, kama kwenye any function, rudisha simply exits, but

        >>> eleza f2():
        ...     jaribu:
        ...         ashiria StopIteration
        ...     tatizo:
        ...         tuma 42
        >>> andika(list(f2()))
        [42]

    because StopIteration ni captured by a bare "except", kama ni any
    exception.

Specification: Generators na Exception Propagation

    >>> eleza f():
    ...     rudisha 1//0
    >>> eleza g():
    ...     tuma f()  # the zero division exception propagates
    ...     tuma 42   # na we'll never get here
    >>> k = g()
    >>> next(k)
    Traceback (most recent call last):
      File "<stdin>", line 1, kwenye ?
      File "<stdin>", line 2, kwenye g
      File "<stdin>", line 2, kwenye f
    ZeroDivisionError: integer division ama modulo by zero
    >>> next(k)  # na the generator cannot be resumed
    Traceback (most recent call last):
      File "<stdin>", line 1, kwenye ?
    StopIteration
    >>>

Specification: Try/Except/Finally

    >>> eleza f():
    ...     jaribu:
    ...         tuma 1
    ...         jaribu:
    ...             tuma 2
    ...             1//0
    ...             tuma 3  # never get here
    ...         tatizo ZeroDivisionError:
    ...             tuma 4
    ...             tuma 5
    ...             raise
    ...         tatizo:
    ...             tuma 6
    ...         tuma 7     # the "raise" above stops this
    ...     tatizo:
    ...         tuma 8
    ...     tuma 9
    ...     jaribu:
    ...         x = 12
    ...     mwishowe:
    ...         tuma 10
    ...     tuma 11
    >>> andika(list(f()))
    [1, 2, 4, 5, 8, 9, 10, 11]
    >>>

Guido's binary tree example.

    >>> # A binary tree class.
    >>> kundi Tree:
    ...
    ...     eleza __init__(self, label, left=Tupu, right=Tupu):
    ...         self.label = label
    ...         self.left = left
    ...         self.right = right
    ...
    ...     eleza __repr__(self, level=0, indent="    "):
    ...         s = level*indent + repr(self.label)
    ...         ikiwa self.left:
    ...             s = s + "\\n" + self.left.__repr__(level+1, indent)
    ...         ikiwa self.right:
    ...             s = s + "\\n" + self.right.__repr__(level+1, indent)
    ...         rudisha s
    ...
    ...     eleza __iter__(self):
    ...         rudisha inorder(self)

    >>> # Create a Tree kutoka a list.
    >>> eleza tree(list):
    ...     n = len(list)
    ...     ikiwa n == 0:
    ...         rudisha []
    ...     i = n // 2
    ...     rudisha Tree(list[i], tree(list[:i]), tree(list[i+1:]))

    >>> # Show it off: create a tree.
    >>> t = tree("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    >>> # A recursive generator that generates Tree labels kwenye in-order.
    >>> eleza inorder(t):
    ...     ikiwa t:
    ...         kila x kwenye inorder(t.left):
    ...             tuma x
    ...         tuma t.label
    ...         kila x kwenye inorder(t.right):
    ...             tuma x

    >>> # Show it off: create a tree.
    >>> t = tree("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    >>> # Print the nodes of the tree kwenye in-order.
    >>> kila x kwenye t:
    ...     andika(' '+x, end='')
     A B C D E F G H I J K L M N O P Q R S T U V W X Y Z

    >>> # A non-recursive generator.
    >>> eleza inorder(node):
    ...     stack = []
    ...     wakati node:
    ...         wakati node.left:
    ...             stack.append(node)
    ...             node = node.left
    ...         tuma node.label
    ...         wakati sio node.right:
    ...             jaribu:
    ...                 node = stack.pop()
    ...             tatizo IndexError:
    ...                 return
    ...             tuma node.label
    ...         node = node.right

    >>> # Exercise the non-recursive generator.
    >>> kila x kwenye t:
    ...     andika(' '+x, end='')
     A B C D E F G H I J K L M N O P Q R S T U V W X Y Z

"""

# Examples kutoka Iterator-List na Python-Dev na c.l.py.

email_tests = """

The difference between tumaing Tupu na returning it.

>>> eleza g():
...     kila i kwenye range(3):
...         tuma Tupu
...     tuma Tupu
...     return
>>> list(g())
[Tupu, Tupu, Tupu, Tupu]

Ensure that explicitly raising StopIteration acts like any other exception
in try/except, sio like a return.

>>> eleza g():
...     tuma 1
...     jaribu:
...         ashiria StopIteration
...     tatizo:
...         tuma 2
...     tuma 3
>>> list(g())
[1, 2, 3]

Next one was posted to c.l.py.

>>> eleza gcomb(x, k):
...     "Generate all combinations of k elements kutoka list x."
...
...     ikiwa k > len(x):
...         return
...     ikiwa k == 0:
...         tuma []
...     isipokua:
...         first, rest = x[0], x[1:]
...         # A combination does ama doesn't contain first.
...         # If it does, the remainder ni a k-1 comb of rest.
...         kila c kwenye gcomb(rest, k-1):
...             c.insert(0, first)
...             tuma c
...         # If it doesn't contain first, it's a k comb of rest.
...         kila c kwenye gcomb(rest, k):
...             tuma c

>>> seq = list(range(1, 5))
>>> kila k kwenye range(len(seq) + 2):
...     andika("%d-combs of %s:" % (k, seq))
...     kila c kwenye gcomb(seq, k):
...         andika("   ", c)
0-combs of [1, 2, 3, 4]:
    []
1-combs of [1, 2, 3, 4]:
    [1]
    [2]
    [3]
    [4]
2-combs of [1, 2, 3, 4]:
    [1, 2]
    [1, 3]
    [1, 4]
    [2, 3]
    [2, 4]
    [3, 4]
3-combs of [1, 2, 3, 4]:
    [1, 2, 3]
    [1, 2, 4]
    [1, 3, 4]
    [2, 3, 4]
4-combs of [1, 2, 3, 4]:
    [1, 2, 3, 4]
5-combs of [1, 2, 3, 4]:

From the Iterators list, about the types of these things.

>>> eleza g():
...     tuma 1
...
>>> type(g)
<kundi 'function'>
>>> i = g()
>>> type(i)
<kundi 'generator'>
>>> [s kila s kwenye dir(i) ikiwa sio s.startswith('_')]
['close', 'gi_code', 'gi_frame', 'gi_running', 'gi_tumafrom', 'send', 'throw']
>>> kutoka test.support agiza HAVE_DOCSTRINGS
>>> andika(i.__next__.__doc__ ikiwa HAVE_DOCSTRINGS isipokua 'Implement next(self).')
Implement next(self).
>>> iter(i) ni i
Kweli
>>> agiza types
>>> isinstance(i, types.GeneratorType)
Kweli

And more, added later.

>>> i.gi_running
0
>>> type(i.gi_frame)
<kundi 'frame'>
>>> i.gi_running = 42
Traceback (most recent call last):
  ...
AttributeError: readonly attribute
>>> eleza g():
...     tuma me.gi_running
>>> me = g()
>>> me.gi_running
0
>>> next(me)
1
>>> me.gi_running
0

A clever union-find implementation kutoka c.l.py, due to David Eppstein.
Sent: Friday, June 29, 2001 12:16 PM
To: python-list@python.org
Subject: Re: PEP 255: Simple Generators

>>> kundi disjointSet:
...     eleza __init__(self, name):
...         self.name = name
...         self.parent = Tupu
...         self.generator = self.generate()
...
...     eleza generate(self):
...         wakati sio self.parent:
...             tuma self
...         kila x kwenye self.parent.generator:
...             tuma x
...
...     eleza find(self):
...         rudisha next(self.generator)
...
...     eleza union(self, parent):
...         ikiwa self.parent:
...             ashiria ValueError("Sorry, I'm sio a root!")
...         self.parent = parent
...
...     eleza __str__(self):
...         rudisha self.name

>>> names = "ABCDEFGHIJKLM"
>>> sets = [disjointSet(name) kila name kwenye names]
>>> roots = sets[:]

>>> agiza random
>>> gen = random.Random(42)
>>> wakati 1:
...     kila s kwenye sets:
...         andika(" %s->%s" % (s, s.find()), end='')
...     andika()
...     ikiwa len(roots) > 1:
...         s1 = gen.choice(roots)
...         roots.remove(s1)
...         s2 = gen.choice(roots)
...         s1.union(s2)
...         andika("merged", s1, "into", s2)
...     isipokua:
...         koma
 A->A B->B C->C D->D E->E F->F G->G H->H I->I J->J K->K L->L M->M
merged K into B
 A->A B->B C->C D->D E->E F->F G->G H->H I->I J->J K->B L->L M->M
merged A into F
 A->F B->B C->C D->D E->E F->F G->G H->H I->I J->J K->B L->L M->M
merged E into F
 A->F B->B C->C D->D E->F F->F G->G H->H I->I J->J K->B L->L M->M
merged D into C
 A->F B->B C->C D->C E->F F->F G->G H->H I->I J->J K->B L->L M->M
merged M into C
 A->F B->B C->C D->C E->F F->F G->G H->H I->I J->J K->B L->L M->C
merged J into B
 A->F B->B C->C D->C E->F F->F G->G H->H I->I J->B K->B L->L M->C
merged B into C
 A->F B->C C->C D->C E->F F->F G->G H->H I->I J->C K->C L->L M->C
merged F into G
 A->G B->C C->C D->C E->G F->G G->G H->H I->I J->C K->C L->L M->C
merged L into C
 A->G B->C C->C D->C E->G F->G G->G H->H I->I J->C K->C L->C M->C
merged G into I
 A->I B->C C->C D->C E->I F->I G->I H->H I->I J->C K->C L->C M->C
merged I into H
 A->H B->C C->C D->C E->H F->H G->H H->H I->H J->C K->C L->C M->C
merged C into H
 A->H B->H C->H D->H E->H F->H G->H H->H I->H J->H K->H L->H M->H

"""
# Emacs turd '

# Fun tests (kila sufficiently warped notions of "fun").

fun_tests = """

Build up to a recursive Sieve of Eratosthenes generator.

>>> eleza firstn(g, n):
...     rudisha [next(g) kila i kwenye range(n)]

>>> eleza intsfrom(i):
...     wakati 1:
...         tuma i
...         i += 1

>>> firstn(intsfrom(5), 7)
[5, 6, 7, 8, 9, 10, 11]

>>> eleza exclude_multiples(n, ints):
...     kila i kwenye ints:
...         ikiwa i % n:
...             tuma i

>>> firstn(exclude_multiples(3, intsfrom(1)), 6)
[1, 2, 4, 5, 7, 8]

>>> eleza sieve(ints):
...     prime = next(ints)
...     tuma prime
...     not_divisible_by_prime = exclude_multiples(prime, ints)
...     kila p kwenye sieve(not_divisible_by_prime):
...         tuma p

>>> primes = sieve(intsfrom(2))
>>> firstn(primes, 20)
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]


Another famous problem:  generate all integers of the form
    2**i * 3**j  * 5**k
in increasing order, where i,j,k >= 0.  Trickier than it may look at first!
Try writing it without generators, na correctly, na without generating
3 internal results kila each result output.

>>> eleza times(n, g):
...     kila i kwenye g:
...         tuma n * i
>>> firstn(times(10, intsfrom(1)), 10)
[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

>>> eleza merge(g, h):
...     ng = next(g)
...     nh = next(h)
...     wakati 1:
...         ikiwa ng < nh:
...             tuma ng
...             ng = next(g)
...         lasivyo ng > nh:
...             tuma nh
...             nh = next(h)
...         isipokua:
...             tuma ng
...             ng = next(g)
...             nh = next(h)

The following works, but ni doing a whale of a lot of redundant work --
it's sio clear how to get the internal uses of m235 to share a single
generator.  Note that me_times2 (etc) each need to see every element kwenye the
result sequence.  So this ni an example where lazy lists are more natural
(you can look at the head of a lazy list any number of times).

>>> eleza m235():
...     tuma 1
...     me_times2 = times(2, m235())
...     me_times3 = times(3, m235())
...     me_times5 = times(5, m235())
...     kila i kwenye merge(merge(me_times2,
...                          me_times3),
...                    me_times5):
...         tuma i

Don't print "too many" of these -- the implementation above ni extremely
inefficient:  each call of m235() leads to 3 recursive calls, na in
turn each of those 3 more, na so on, na so on, until we've descended
enough levels to satisfy the print stmts.  Very odd:  when I printed 5
lines of results below, this managed to screw up Win98's malloc kwenye "the
usual" way, i.e. the heap grew over 4Mb so Win98 started fragmenting
address space, na it *looked* like a very slow leak.

>>> result = m235()
>>> kila i kwenye range(3):
...     andika(firstn(result, 15))
[1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24]
[25, 27, 30, 32, 36, 40, 45, 48, 50, 54, 60, 64, 72, 75, 80]
[81, 90, 96, 100, 108, 120, 125, 128, 135, 144, 150, 160, 162, 180, 192]

Heh.  Here's one way to get a shared list, complete ukijumuisha an excruciating
namespace renaming trick.  The *pretty* part ni that the times() na merge()
functions can be reused as-is, because they only assume their stream
arguments are iterable -- a LazyList ni the same kama a generator to times().

>>> kundi LazyList:
...     eleza __init__(self, g):
...         self.sofar = []
...         self.fetch = g.__next__
...
...     eleza __getitem__(self, i):
...         sofar, fetch = self.sofar, self.fetch
...         wakati i >= len(sofar):
...             sofar.append(fetch())
...         rudisha sofar[i]

>>> eleza m235():
...     tuma 1
...     # Gack:  m235 below actually refers to a LazyList.
...     me_times2 = times(2, m235)
...     me_times3 = times(3, m235)
...     me_times5 = times(5, m235)
...     kila i kwenye merge(merge(me_times2,
...                          me_times3),
...                    me_times5):
...         tuma i

Print kama many of these kama you like -- *this* implementation ni memory-
efficient.

>>> m235 = LazyList(m235())
>>> kila i kwenye range(5):
...     andika([m235[j] kila j kwenye range(15*i, 15*(i+1))])
[1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24]
[25, 27, 30, 32, 36, 40, 45, 48, 50, 54, 60, 64, 72, 75, 80]
[81, 90, 96, 100, 108, 120, 125, 128, 135, 144, 150, 160, 162, 180, 192]
[200, 216, 225, 240, 243, 250, 256, 270, 288, 300, 320, 324, 360, 375, 384]
[400, 405, 432, 450, 480, 486, 500, 512, 540, 576, 600, 625, 640, 648, 675]

Ye olde Fibonacci generator, LazyList style.

>>> eleza fibgen(a, b):
...
...     eleza sum(g, h):
...         wakati 1:
...             tuma next(g) + next(h)
...
...     eleza tail(g):
...         next(g)    # throw first away
...         kila x kwenye g:
...             tuma x
...
...     tuma a
...     tuma b
...     kila s kwenye sum(iter(fib),
...                  tail(iter(fib))):
...         tuma s

>>> fib = LazyList(fibgen(1, 2))
>>> firstn(iter(fib), 17)
[1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584]


Running after your tail ukijumuisha itertools.tee (new kwenye version 2.4)

The algorithms "m235" (Hamming) na Fibonacci presented above are both
examples of a whole family of FP (functional programming) algorithms
where a function produces na returns a list wakati the production algorithm
suppose the list kama already produced by recursively calling itself.
For these algorithms to work, they must:

- produce at least a first element without presupposing the existence of
  the rest of the list
- produce their elements kwenye a lazy manner

To work efficiently, the beginning of the list must sio be recomputed over
and over again. This ni ensured kwenye most FP languages kama a built-in feature.
In python, we have to explicitly maintain a list of already computed results
and abandon genuine recursivity.

This ni what had been attempted above ukijumuisha the LazyList class. One problem
ukijumuisha that kundi ni that it keeps a list of all of the generated results na
therefore continually grows. This partially defeats the goal of the generator
concept, viz. produce the results only kama needed instead of producing them
all na thereby wasting memory.

Thanks to itertools.tee, it ni now clear "how to get the internal uses of
m235 to share a single generator".

>>> kutoka itertools agiza tee
>>> eleza m235():
...     eleza _m235():
...         tuma 1
...         kila n kwenye merge(times(2, m2),
...                        merge(times(3, m3),
...                              times(5, m5))):
...             tuma n
...     m1 = _m235()
...     m2, m3, m5, mRes = tee(m1, 4)
...     rudisha mRes

>>> it = m235()
>>> kila i kwenye range(5):
...     andika(firstn(it, 15))
[1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24]
[25, 27, 30, 32, 36, 40, 45, 48, 50, 54, 60, 64, 72, 75, 80]
[81, 90, 96, 100, 108, 120, 125, 128, 135, 144, 150, 160, 162, 180, 192]
[200, 216, 225, 240, 243, 250, 256, 270, 288, 300, 320, 324, 360, 375, 384]
[400, 405, 432, 450, 480, 486, 500, 512, 540, 576, 600, 625, 640, 648, 675]

The "tee" function does just what we want. It internally keeps a generated
result kila kama long kama it has sio been "consumed" kutoka all of the duplicated
iterators, whereupon it ni deleted. You can therefore print the hamming
sequence during hours without increasing memory usage, ama very little.

The beauty of it ni that recursive running-after-their-tail FP algorithms
are quite straightforwardly expressed ukijumuisha this Python idiom.

Ye olde Fibonacci generator, tee style.

>>> eleza fib():
...
...     eleza _isum(g, h):
...         wakati 1:
...             tuma next(g) + next(h)
...
...     eleza _fib():
...         tuma 1
...         tuma 2
...         next(fibTail) # throw first away
...         kila res kwenye _isum(fibHead, fibTail):
...             tuma res
...
...     realfib = _fib()
...     fibHead, fibTail, fibRes = tee(realfib, 3)
...     rudisha fibRes

>>> firstn(fib(), 17)
[1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584]

"""

# syntax_tests mostly provokes SyntaxErrors.  Also fiddling ukijumuisha #ikiwa 0
# hackery.

syntax_tests = """

These are fine:

>>> eleza f():
...     tuma 1
...     return

>>> eleza f():
...     jaribu:
...         tuma 1
...     mwishowe:
...         pita

>>> eleza f():
...     jaribu:
...         jaribu:
...             1//0
...         tatizo ZeroDivisionError:
...             tuma 666
...         tatizo:
...             pita
...     mwishowe:
...         pita

>>> eleza f():
...     jaribu:
...         jaribu:
...             tuma 12
...             1//0
...         tatizo ZeroDivisionError:
...             tuma 666
...         tatizo:
...             jaribu:
...                 x = 12
...             mwishowe:
...                 tuma 12
...     tatizo:
...         return
>>> list(f())
[12, 666]

>>> eleza f():
...    tuma
>>> type(f())
<kundi 'generator'>


>>> eleza f():
...    ikiwa 0:
...        tuma
>>> type(f())
<kundi 'generator'>


>>> eleza f():
...     ikiwa 0:
...         tuma 1
>>> type(f())
<kundi 'generator'>

>>> eleza f():
...    ikiwa "":
...        tuma Tupu
>>> type(f())
<kundi 'generator'>

>>> eleza f():
...     return
...     jaribu:
...         ikiwa x==4:
...             pita
...         lasivyo 0:
...             jaribu:
...                 1//0
...             tatizo SyntaxError:
...                 pita
...             isipokua:
...                 ikiwa 0:
...                     wakati 12:
...                         x += 1
...                         tuma 2 # don't blink
...                         f(a, b, c, d, e)
...         isipokua:
...             pita
...     tatizo:
...         x = 1
...     return
>>> type(f())
<kundi 'generator'>

>>> eleza f():
...     ikiwa 0:
...         eleza g():
...             tuma 1
...
>>> type(f())
<kundi 'TupuType'>

>>> eleza f():
...     ikiwa 0:
...         kundi C:
...             eleza __init__(self):
...                 tuma 1
...             eleza f(self):
...                 tuma 2
>>> type(f())
<kundi 'TupuType'>

>>> eleza f():
...     ikiwa 0:
...         return
...     ikiwa 0:
...         tuma 2
>>> type(f())
<kundi 'generator'>

This one caused a crash (see SF bug 567538):

>>> eleza f():
...     kila i kwenye range(3):
...         jaribu:
...             endelea
...         mwishowe:
...             tuma i
...
>>> g = f()
>>> andika(next(g))
0
>>> andika(next(g))
1
>>> andika(next(g))
2
>>> andika(next(g))
Traceback (most recent call last):
StopIteration


Test the gi_code attribute

>>> eleza f():
...     tuma 5
...
>>> g = f()
>>> g.gi_code ni f.__code__
Kweli
>>> next(g)
5
>>> next(g)
Traceback (most recent call last):
StopIteration
>>> g.gi_code ni f.__code__
Kweli


Test the __name__ attribute na the repr()

>>> eleza f():
...    tuma 5
...
>>> g = f()
>>> g.__name__
'f'
>>> repr(g)  # doctest: +ELLIPSIS
'<generator object f at ...>'

Lambdas shouldn't have their usual rudisha behavior.

>>> x = lambda: (tuma 1)
>>> list(x())
[1]

>>> x = lambda: ((tuma 1), (tuma 2))
>>> list(x())
[1, 2]
"""

# conjoin ni a simple backtracking generator, named kwenye honor of Icon's
# "conjunction" control structure.  Pass a list of no-argument functions
# that rudisha iterable objects.  Easiest to explain by example:  assume the
# function list [x, y, z] ni pitaed.  Then conjoin acts like:
#
# eleza g():
#     values = [Tupu] * 3
#     kila values[0] kwenye x():
#         kila values[1] kwenye y():
#             kila values[2] kwenye z():
#                 tuma values
#
# So some 3-lists of values *may* be generated, each time we successfully
# get into the innermost loop.  If an iterator fails (is exhausted) before
# then, it "backtracks" to get the next value kutoka the nearest enclosing
# iterator (the one "to the left"), na starts all over again at the next
# slot (pumps a fresh iterator).  Of course this ni most useful when the
# iterators have side-effects, so that which values *can* be generated at
# each slot depend on the values iterated at previous slots.

eleza simple_conjoin(gs):

    values = [Tupu] * len(gs)

    eleza gen(i):
        ikiwa i >= len(gs):
            tuma values
        isipokua:
            kila values[i] kwenye gs[i]():
                kila x kwenye gen(i+1):
                    tuma x

    kila x kwenye gen(0):
        tuma x

# That works fine, but recursing a level na checking i against len(gs) for
# each item produced ni inefficient.  By doing manual loop unrolling across
# generator boundaries, it's possible to eliminate most of that overhead.
# This isn't worth the bother *in general* kila generators, but conjoin() is
# a core building block kila some CPU-intensive generator applications.

eleza conjoin(gs):

    n = len(gs)
    values = [Tupu] * n

    # Do one loop nest at time recursively, until the # of loop nests
    # remaining ni divisible by 3.

    eleza gen(i):
        ikiwa i >= n:
            tuma values

        lasivyo (n-i) % 3:
            ip1 = i+1
            kila values[i] kwenye gs[i]():
                kila x kwenye gen(ip1):
                    tuma x

        isipokua:
            kila x kwenye _gen3(i):
                tuma x

    # Do three loop nests at a time, recursing only ikiwa at least three more
    # remain.  Don't call directly:  this ni an internal optimization for
    # gen's use.

    eleza _gen3(i):
        assert i < n na (n-i) % 3 == 0
        ip1, ip2, ip3 = i+1, i+2, i+3
        g, g1, g2 = gs[i : ip3]

        ikiwa ip3 >= n:
            # These are the last three, so we can tuma values directly.
            kila values[i] kwenye g():
                kila values[ip1] kwenye g1():
                    kila values[ip2] kwenye g2():
                        tuma values

        isipokua:
            # At least 6 loop nests remain; peel off 3 na recurse kila the
            # rest.
            kila values[i] kwenye g():
                kila values[ip1] kwenye g1():
                    kila values[ip2] kwenye g2():
                        kila x kwenye _gen3(ip3):
                            tuma x

    kila x kwenye gen(0):
        tuma x

# And one more approach:  For backtracking apps like the Knight's Tour
# solver below, the number of backtracking levels can be enormous (one
# level per square, kila the Knight's Tour, so that e.g. a 100x100 board
# needs 10,000 levels).  In such cases Python ni likely to run out of
# stack space due to recursion.  So here's a recursion-free version of
# conjoin too.
# NOTE WELL:  This allows large problems to be solved ukijumuisha only trivial
# demands on stack space.  Without explicitly resumable generators, this is
# much harder to achieve.  OTOH, this ni much slower (up to a factor of 2)
# than the fancy unrolled recursive conjoin.

eleza flat_conjoin(gs):  # rename to conjoin to run tests ukijumuisha this instead
    n = len(gs)
    values = [Tupu] * n
    iters  = [Tupu] * n
    _StopIteration = StopIteration  # make local because caught a *lot*
    i = 0
    wakati 1:
        # Descend.
        jaribu:
            wakati i < n:
                it = iters[i] = gs[i]().__next__
                values[i] = it()
                i += 1
        tatizo _StopIteration:
            pita
        isipokua:
            assert i == n
            tuma values

        # Backtrack until an older iterator can be resumed.
        i -= 1
        wakati i >= 0:
            jaribu:
                values[i] = iters[i]()
                # Success!  Start fresh at next level.
                i += 1
                koma
            tatizo _StopIteration:
                # Continue backtracking.
                i -= 1
        isipokua:
            assert i < 0
            koma

# A conjoin-based N-Queens solver.

kundi Queens:
    eleza __init__(self, n):
        self.n = n
        rangen = range(n)

        # Assign a unique int to each column na diagonal.
        # columns:  n of those, range(n).
        # NW-SE diagonals: 2n-1 of these, i-j unique na invariant along
        # each, smallest i-j ni 0-(n-1) = 1-n, so add n-1 to shift to 0-
        # based.
        # NE-SW diagonals: 2n-1 of these, i+j unique na invariant along
        # each, smallest i+j ni 0, largest ni 2n-2.

        # For each square, compute a bit vector of the columns na
        # diagonals it covers, na kila each row compute a function that
        # generates the possibilities kila the columns kwenye that row.
        self.rowgenerators = []
        kila i kwenye rangen:
            rowuses = [(1 << j) |                  # column ordinal
                       (1 << (n + i-j + n-1)) |    # NW-SE ordinal
                       (1 << (n + 2*n-1 + i+j))    # NE-SW ordinal
                            kila j kwenye rangen]

            eleza rowgen(rowuses=rowuses):
                kila j kwenye rangen:
                    uses = rowuses[j]
                    ikiwa uses & self.used == 0:
                        self.used |= uses
                        tuma j
                        self.used &= ~uses

            self.rowgenerators.append(rowgen)

    # Generate solutions.
    eleza solve(self):
        self.used = 0
        kila row2col kwenye conjoin(self.rowgenerators):
            tuma row2col

    eleza printsolution(self, row2col):
        n = self.n
        assert n == len(row2col)
        sep = "+" + "-+" * n
        andika(sep)
        kila i kwenye range(n):
            squares = [" " kila j kwenye range(n)]
            squares[row2col[i]] = "Q"
            andika("|" + "|".join(squares) + "|")
            andika(sep)

# A conjoin-based Knight's Tour solver.  This ni pretty sophisticated
# (e.g., when used ukijumuisha flat_conjoin above, na pitaing hard=1 to the
# constructor, a 200x200 Knight's Tour was found quickly -- note that we're
# creating 10s of thousands of generators then!), na ni lengthy.

kundi Knights:
    eleza __init__(self, m, n, hard=0):
        self.m, self.n = m, n

        # solve() will set up succs[i] to be a list of square #i's
        # successors.
        succs = self.succs = []

        # Remove i0 kutoka each of its successor's successor lists, i.e.
        # successors can't go back to i0 again.  Return 0 ikiwa we can
        # detect this makes a solution impossible, isipokua rudisha 1.

        eleza remove_from_successors(i0, len=len):
            # If we remove all exits kutoka a free square, we're dead:
            # even ikiwa we move to it next, we can't leave it again.
            # If we create a square ukijumuisha one exit, we must visit it next;
            # isipokua somebody isipokua will have to visit it, na since there's
            # only one adjacent, there won't be a way to leave it again.
            # Finally, ikiwa we create more than one free square ukijumuisha a
            # single exit, we can only move to one of them next, leaving
            # the other one a dead end.
            ne0 = ne1 = 0
            kila i kwenye succs[i0]:
                s = succs[i]
                s.remove(i0)
                e = len(s)
                ikiwa e == 0:
                    ne0 += 1
                lasivyo e == 1:
                    ne1 += 1
            rudisha ne0 == 0 na ne1 < 2

        # Put i0 back kwenye each of its successor's successor lists.

        eleza add_to_successors(i0):
            kila i kwenye succs[i0]:
                succs[i].append(i0)

        # Generate the first move.
        eleza first():
            ikiwa m < 1 ama n < 1:
                return

            # Since we're looking kila a cycle, it doesn't matter where we
            # start.  Starting kwenye a corner makes the 2nd move easy.
            corner = self.coords2index(0, 0)
            remove_from_successors(corner)
            self.lastij = corner
            tuma corner
            add_to_successors(corner)

        # Generate the second moves.
        eleza second():
            corner = self.coords2index(0, 0)
            assert self.lastij == corner  # i.e., we started kwenye the corner
            ikiwa m < 3 ama n < 3:
                return
            assert len(succs[corner]) == 2
            assert self.coords2index(1, 2) kwenye succs[corner]
            assert self.coords2index(2, 1) kwenye succs[corner]
            # Only two choices.  Whichever we pick, the other must be the
            # square picked on move m*n, kama it's the only way to get back
            # to (0, 0).  Save its index kwenye self.final so that moves before
            # the last know it must be kept free.
            kila i, j kwenye (1, 2), (2, 1):
                this  = self.coords2index(i, j)
                final = self.coords2index(3-i, 3-j)
                self.final = final

                remove_from_successors(this)
                succs[final].append(corner)
                self.lastij = this
                tuma this
                succs[final].remove(corner)
                add_to_successors(this)

        # Generate moves 3 through m*n-1.
        eleza advance(len=len):
            # If some successor has only one exit, must take it.
            # Else favor successors ukijumuisha fewer exits.
            candidates = []
            kila i kwenye succs[self.lastij]:
                e = len(succs[i])
                assert e > 0, "else remove_from_successors() pruning flawed"
                ikiwa e == 1:
                    candidates = [(e, i)]
                    koma
                candidates.append((e, i))
            isipokua:
                candidates.sort()

            kila e, i kwenye candidates:
                ikiwa i != self.final:
                    ikiwa remove_from_successors(i):
                        self.lastij = i
                        tuma i
                    add_to_successors(i)

        # Generate moves 3 through m*n-1.  Alternative version using a
        # stronger (but more expensive) heuristic to order successors.
        # Since the # of backtracking levels ni m*n, a poor move early on
        # can take eons to undo.  Smallest square board kila which this
        # matters a lot ni 52x52.
        eleza advance_hard(vmid=(m-1)/2.0, hmid=(n-1)/2.0, len=len):
            # If some successor has only one exit, must take it.
            # Else favor successors ukijumuisha fewer exits.
            # Break ties via max distance kutoka board centerpoint (favor
            # corners na edges whenever possible).
            candidates = []
            kila i kwenye succs[self.lastij]:
                e = len(succs[i])
                assert e > 0, "else remove_from_successors() pruning flawed"
                ikiwa e == 1:
                    candidates = [(e, 0, i)]
                    koma
                i1, j1 = self.index2coords(i)
                d = (i1 - vmid)**2 + (j1 - hmid)**2
                candidates.append((e, -d, i))
            isipokua:
                candidates.sort()

            kila e, d, i kwenye candidates:
                ikiwa i != self.final:
                    ikiwa remove_from_successors(i):
                        self.lastij = i
                        tuma i
                    add_to_successors(i)

        # Generate the last move.
        eleza last():
            assert self.final kwenye succs[self.lastij]
            tuma self.final

        ikiwa m*n < 4:
            self.squaregenerators = [first]
        isipokua:
            self.squaregenerators = [first, second] + \
                [hard na advance_hard ama advance] * (m*n - 3) + \
                [last]

    eleza coords2index(self, i, j):
        assert 0 <= i < self.m
        assert 0 <= j < self.n
        rudisha i * self.n + j

    eleza index2coords(self, index):
        assert 0 <= index < self.m * self.n
        rudisha divmod(index, self.n)

    eleza _init_board(self):
        succs = self.succs
        toa succs[:]
        m, n = self.m, self.n
        c2i = self.coords2index

        offsets = [( 1,  2), ( 2,  1), ( 2, -1), ( 1, -2),
                   (-1, -2), (-2, -1), (-2,  1), (-1,  2)]
        rangen = range(n)
        kila i kwenye range(m):
            kila j kwenye rangen:
                s = [c2i(i+io, j+jo) kila io, jo kwenye offsets
                                     ikiwa 0 <= i+io < m na
                                        0 <= j+jo < n]
                succs.append(s)

    # Generate solutions.
    eleza solve(self):
        self._init_board()
        kila x kwenye conjoin(self.squaregenerators):
            tuma x

    eleza printsolution(self, x):
        m, n = self.m, self.n
        assert len(x) == m*n
        w = len(str(m*n))
        format = "%" + str(w) + "d"

        squares = [[Tupu] * n kila i kwenye range(m)]
        k = 1
        kila i kwenye x:
            i1, j1 = self.index2coords(i)
            squares[i1][j1] = format % k
            k += 1

        sep = "+" + ("-" * w + "+") * n
        andika(sep)
        kila i kwenye range(m):
            row = squares[i]
            andika("|" + "|".join(row) + "|")
            andika(sep)

conjoin_tests = """

Generate the 3-bit binary numbers kwenye order.  This illustrates dumbest-
possible use of conjoin, just to generate the full cross-product.

>>> kila c kwenye conjoin([lambda: iter((0, 1))] * 3):
...     andika(c)
[0, 0, 0]
[0, 0, 1]
[0, 1, 0]
[0, 1, 1]
[1, 0, 0]
[1, 0, 1]
[1, 1, 0]
[1, 1, 1]

For efficiency kwenye typical backtracking apps, conjoin() tumas the same list
object each time.  So ikiwa you want to save away a full account of its
generated sequence, you need to copy its results.

>>> eleza gencopy(iterator):
...     kila x kwenye iterator:
...         tuma x[:]

>>> kila n kwenye range(10):
...     all = list(gencopy(conjoin([lambda: iter((0, 1))] * n)))
...     andika(n, len(all), all[0] == [0] * n, all[-1] == [1] * n)
0 1 Kweli Kweli
1 2 Kweli Kweli
2 4 Kweli Kweli
3 8 Kweli Kweli
4 16 Kweli Kweli
5 32 Kweli Kweli
6 64 Kweli Kweli
7 128 Kweli Kweli
8 256 Kweli Kweli
9 512 Kweli Kweli

And run an 8-queens solver.

>>> q = Queens(8)
>>> LIMIT = 2
>>> count = 0
>>> kila row2col kwenye q.solve():
...     count += 1
...     ikiwa count <= LIMIT:
...         andika("Solution", count)
...         q.printsolution(row2col)
Solution 1
+-+-+-+-+-+-+-+-+
|Q| | | | | | | |
+-+-+-+-+-+-+-+-+
| | | | |Q| | | |
+-+-+-+-+-+-+-+-+
| | | | | | | |Q|
+-+-+-+-+-+-+-+-+
| | | | | |Q| | |
+-+-+-+-+-+-+-+-+
| | |Q| | | | | |
+-+-+-+-+-+-+-+-+
| | | | | | |Q| |
+-+-+-+-+-+-+-+-+
| |Q| | | | | | |
+-+-+-+-+-+-+-+-+
| | | |Q| | | | |
+-+-+-+-+-+-+-+-+
Solution 2
+-+-+-+-+-+-+-+-+
|Q| | | | | | | |
+-+-+-+-+-+-+-+-+
| | | | | |Q| | |
+-+-+-+-+-+-+-+-+
| | | | | | | |Q|
+-+-+-+-+-+-+-+-+
| | |Q| | | | | |
+-+-+-+-+-+-+-+-+
| | | | | | |Q| |
+-+-+-+-+-+-+-+-+
| | | |Q| | | | |
+-+-+-+-+-+-+-+-+
| |Q| | | | | | |
+-+-+-+-+-+-+-+-+
| | | | |Q| | | |
+-+-+-+-+-+-+-+-+

>>> andika(count, "solutions kwenye all.")
92 solutions kwenye all.

And run a Knight's Tour on a 10x10 board.  Note that there are about
20,000 solutions even on a 6x6 board, so don't dare run this to exhaustion.

>>> k = Knights(10, 10)
>>> LIMIT = 2
>>> count = 0
>>> kila x kwenye k.solve():
...     count += 1
...     ikiwa count <= LIMIT:
...         andika("Solution", count)
...         k.printsolution(x)
...     isipokua:
...         koma
Solution 1
+---+---+---+---+---+---+---+---+---+---+
|  1| 58| 27| 34|  3| 40| 29| 10|  5|  8|
+---+---+---+---+---+---+---+---+---+---+
| 26| 35|  2| 57| 28| 33|  4|  7| 30| 11|
+---+---+---+---+---+---+---+---+---+---+
| 59|100| 73| 36| 41| 56| 39| 32|  9|  6|
+---+---+---+---+---+---+---+---+---+---+
| 74| 25| 60| 55| 72| 37| 42| 49| 12| 31|
+---+---+---+---+---+---+---+---+---+---+
| 61| 86| 99| 76| 63| 52| 47| 38| 43| 50|
+---+---+---+---+---+---+---+---+---+---+
| 24| 75| 62| 85| 54| 71| 64| 51| 48| 13|
+---+---+---+---+---+---+---+---+---+---+
| 87| 98| 91| 80| 77| 84| 53| 46| 65| 44|
+---+---+---+---+---+---+---+---+---+---+
| 90| 23| 88| 95| 70| 79| 68| 83| 14| 17|
+---+---+---+---+---+---+---+---+---+---+
| 97| 92| 21| 78| 81| 94| 19| 16| 45| 66|
+---+---+---+---+---+---+---+---+---+---+
| 22| 89| 96| 93| 20| 69| 82| 67| 18| 15|
+---+---+---+---+---+---+---+---+---+---+
Solution 2
+---+---+---+---+---+---+---+---+---+---+
|  1| 58| 27| 34|  3| 40| 29| 10|  5|  8|
+---+---+---+---+---+---+---+---+---+---+
| 26| 35|  2| 57| 28| 33|  4|  7| 30| 11|
+---+---+---+---+---+---+---+---+---+---+
| 59|100| 73| 36| 41| 56| 39| 32|  9|  6|
+---+---+---+---+---+---+---+---+---+---+
| 74| 25| 60| 55| 72| 37| 42| 49| 12| 31|
+---+---+---+---+---+---+---+---+---+---+
| 61| 86| 99| 76| 63| 52| 47| 38| 43| 50|
+---+---+---+---+---+---+---+---+---+---+
| 24| 75| 62| 85| 54| 71| 64| 51| 48| 13|
+---+---+---+---+---+---+---+---+---+---+
| 87| 98| 89| 80| 77| 84| 53| 46| 65| 44|
+---+---+---+---+---+---+---+---+---+---+
| 90| 23| 92| 95| 70| 79| 68| 83| 14| 17|
+---+---+---+---+---+---+---+---+---+---+
| 97| 88| 21| 78| 81| 94| 19| 16| 45| 66|
+---+---+---+---+---+---+---+---+---+---+
| 22| 91| 96| 93| 20| 69| 82| 67| 18| 15|
+---+---+---+---+---+---+---+---+---+---+
"""

weakref_tests = """\
Generators are weakly referencable:

>>> agiza weakref
>>> eleza gen():
...     tuma 'foo!'
...
>>> wr = weakref.ref(gen)
>>> wr() ni gen
Kweli
>>> p = weakref.proxy(gen)

Generator-iterators are weakly referencable kama well:

>>> gi = gen()
>>> wr = weakref.ref(gi)
>>> wr() ni gi
Kweli
>>> p = weakref.proxy(gi)
>>> list(p)
['foo!']

"""

coroutine_tests = """\
Sending a value into a started generator:

>>> eleza f():
...     andika((tuma 1))
...     tuma 2
>>> g = f()
>>> next(g)
1
>>> g.send(42)
42
2

Sending a value into a new generator produces a TypeError:

>>> f().send("foo")
Traceback (most recent call last):
...
TypeError: can't send non-Tupu value to a just-started generator


Yield by itself tumas Tupu:

>>> eleza f(): tuma
>>> list(f())
[Tupu]


Yield ni allowed only kwenye the outermost iterable kwenye generator expression:

>>> eleza f(): list(i kila i kwenye [(tuma 26)])
>>> type(f())
<kundi 'generator'>


A tuma expression ukijumuisha augmented assignment.

>>> eleza coroutine(seq):
...     count = 0
...     wakati count < 200:
...         count += tuma
...         seq.append(count)
>>> seq = []
>>> c = coroutine(seq)
>>> next(c)
>>> andika(seq)
[]
>>> c.send(10)
>>> andika(seq)
[10]
>>> c.send(10)
>>> andika(seq)
[10, 20]
>>> c.send(10)
>>> andika(seq)
[10, 20, 30]


Check some syntax errors kila tuma expressions:

>>> f=lambda: (tuma 1),(tuma 2)
Traceback (most recent call last):
  ...
SyntaxError: 'tuma' outside function

>>> eleza f(): x = tuma = y
Traceback (most recent call last):
  ...
SyntaxError: assignment to tuma expression sio possible

>>> eleza f(): (tuma bar) = y
Traceback (most recent call last):
  ...
SyntaxError: cannot assign to tuma expression

>>> eleza f(): (tuma bar) += y
Traceback (most recent call last):
  ...
SyntaxError: cannot assign to tuma expression


Now check some throw() conditions:

>>> eleza f():
...     wakati Kweli:
...         jaribu:
...             andika((tuma))
...         tatizo ValueError kama v:
...             andika("caught ValueError (%s)" % (v))
>>> agiza sys
>>> g = f()
>>> next(g)

>>> g.throw(ValueError) # type only
caught ValueError ()

>>> g.throw(ValueError("xyz"))  # value only
caught ValueError (xyz)

>>> g.throw(ValueError, ValueError(1))   # value+matching type
caught ValueError (1)

>>> g.throw(ValueError, TypeError(1))  # mismatched type, rewrapped
caught ValueError (1)

>>> g.throw(ValueError, ValueError(1), Tupu)   # explicit Tupu traceback
caught ValueError (1)

>>> g.throw(ValueError(1), "foo")       # bad args
Traceback (most recent call last):
  ...
TypeError: instance exception may sio have a separate value

>>> g.throw(ValueError, "foo", 23)      # bad args
Traceback (most recent call last):
  ...
TypeError: throw() third argument must be a traceback object

>>> g.throw("abc")
Traceback (most recent call last):
  ...
TypeError: exceptions must be classes ama instances deriving kutoka BaseException, sio str

>>> g.throw(0)
Traceback (most recent call last):
  ...
TypeError: exceptions must be classes ama instances deriving kutoka BaseException, sio int

>>> g.throw(list)
Traceback (most recent call last):
  ...
TypeError: exceptions must be classes ama instances deriving kutoka BaseException, sio type

>>> eleza throw(g,exc):
...     jaribu:
...         ashiria exc
...     tatizo:
...         g.throw(*sys.exc_info())
>>> throw(g,ValueError) # do it ukijumuisha traceback included
caught ValueError ()

>>> g.send(1)
1

>>> throw(g,TypeError)  # terminate the generator
Traceback (most recent call last):
  ...
TypeError

>>> andika(g.gi_frame)
Tupu

>>> g.send(2)
Traceback (most recent call last):
  ...
StopIteration

>>> g.throw(ValueError,6)       # throw on closed generator
Traceback (most recent call last):
  ...
ValueError: 6

>>> f().throw(ValueError,7)     # throw on just-opened generator
Traceback (most recent call last):
  ...
ValueError: 7

Plain "raise" inside a generator should preserve the traceback (#13188).
The traceback should have 3 levels:
- g.throw()
- f()
- 1/0

>>> eleza f():
...     jaribu:
...         tuma
...     tatizo:
...         raise
>>> g = f()
>>> jaribu:
...     1/0
... tatizo ZeroDivisionError kama v:
...     jaribu:
...         g.throw(v)
...     tatizo Exception kama w:
...         tb = w.__traceback__
>>> levels = 0
>>> wakati tb:
...     levels += 1
...     tb = tb.tb_next
>>> levels
3

Now let's try closing a generator:

>>> eleza f():
...     jaribu: tuma
...     tatizo GeneratorExit:
...         andika("exiting")

>>> g = f()
>>> next(g)
>>> g.close()
exiting
>>> g.close()  # should be no-op now

>>> f().close()  # close on just-opened generator should be fine

>>> eleza f(): tuma      # an even simpler generator
>>> f().close()         # close before opening
>>> g = f()
>>> next(g)
>>> g.close()           # close normally

And finalization:

>>> eleza f():
...     jaribu: tuma
...     mwishowe:
...         andika("exiting")

>>> g = f()
>>> next(g)
>>> toa g
exiting


GeneratorExit ni sio caught by tatizo Exception:

>>> eleza f():
...     jaribu: tuma
...     tatizo Exception:
...         andika('except')
...     mwishowe:
...         andika('finally')

>>> g = f()
>>> next(g)
>>> toa g
finally


Now let's try some ill-behaved generators:

>>> eleza f():
...     jaribu: tuma
...     tatizo GeneratorExit:
...         tuma "foo!"
>>> g = f()
>>> next(g)
>>> g.close()
Traceback (most recent call last):
  ...
RuntimeError: generator ignored GeneratorExit
>>> g.close()


Our ill-behaved code should be invoked during GC:

>>> ukijumuisha support.catch_unraisable_exception() kama cm:
...     g = f()
...     next(g)
...     toa g
...
...     cm.unraisable.exc_type == RuntimeError
...     "generator ignored GeneratorExit" kwenye str(cm.unraisable.exc_value)
...     cm.unraisable.exc_traceback ni sio Tupu
Kweli
Kweli
Kweli

And errors thrown during closing should propagate:

>>> eleza f():
...     jaribu: tuma
...     tatizo GeneratorExit:
...         ashiria TypeError("fie!")
>>> g = f()
>>> next(g)
>>> g.close()
Traceback (most recent call last):
  ...
TypeError: fie!


Ensure that various tuma expression constructs make their
enclosing function a generator:

>>> eleza f(): x += tuma
>>> type(f())
<kundi 'generator'>

>>> eleza f(): x = tuma
>>> type(f())
<kundi 'generator'>

>>> eleza f(): lambda x=(tuma): 1
>>> type(f())
<kundi 'generator'>

>>> eleza f(d): d[(tuma "a")] = d[(tuma "b")] = 27
>>> data = [1,2]
>>> g = f(data)
>>> type(g)
<kundi 'generator'>
>>> g.send(Tupu)
'a'
>>> data
[1, 2]
>>> g.send(0)
'b'
>>> data
[27, 2]
>>> jaribu: g.send(1)
... tatizo StopIteration: pita
>>> data
[27, 27]

"""

refleaks_tests = """
Prior to adding cycle-GC support to itertools.tee, this code would leak
references. We add it to the standard suite so the routine refleak-tests
would trigger ikiwa it starts being uncleanable again.

>>> agiza itertools
>>> eleza leak():
...     kundi gen:
...         eleza __iter__(self):
...             rudisha self
...         eleza __next__(self):
...             rudisha self.item
...     g = gen()
...     head, tail = itertools.tee(g)
...     g.item = head
...     rudisha head
>>> it = leak()

Make sure to also test the involvement of the tee-internal teedataobject,
which stores returned items.

>>> item = next(it)



This test leaked at one point due to generator finalization/destruction.
It was copied kutoka Lib/test/leakers/test_generator_cycle.py before the file
was removed.

>>> eleza leak():
...    eleza gen():
...        wakati Kweli:
...            tuma g
...    g = gen()

>>> leak()



This test isn't really generator related, but rather exception-in-cleanup
related. The coroutine tests (above) just happen to cause an exception in
the generator's __del__ (tp_del) method. We can also test kila this
explicitly, without generators. We do have to redirect stderr to avoid
printing warnings na to doublecheck that we actually tested what we wanted
to test.

>>> kutoka test agiza support
>>> kundi Leaker:
...     eleza __del__(self):
...         eleza invoke(message):
...             ashiria RuntimeError(message)
...         invoke("toa failed")
...
>>> ukijumuisha support.catch_unraisable_exception() kama cm:
...     l = Leaker()
...     toa l
...
...     cm.unraisable.object == Leaker.__del__
...     cm.unraisable.exc_type == RuntimeError
...     str(cm.unraisable.exc_value) == "toa failed"
...     cm.unraisable.exc_traceback ni sio Tupu
Kweli
Kweli
Kweli
Kweli


These refleak tests should perhaps be kwenye a testfile of their own,
test_generators just happened to be the test that drew these out.

"""

__test__ = {"tut":      tutorial_tests,
            "pep":      pep_tests,
            "email":    email_tests,
            "fun":      fun_tests,
            "syntax":   syntax_tests,
            "conjoin":  conjoin_tests,
            "weakref":  weakref_tests,
            "coroutine":  coroutine_tests,
            "refleaks": refleaks_tests,
            }

# Magic test name that regrtest.py invokes *after* importing this module.
# This worms around a bootstrap problem.
# Note that doctest na regrtest both look kwenye sys.argv kila a "-v" argument,
# so this works kama expected kwenye both ways of running regrtest.
eleza test_main(verbose=Tupu):
    kutoka test agiza support, test_generators
    support.run_unittest(__name__)
    support.run_doctest(test_generators, verbose)

# This part isn't needed kila regrtest, but kila running the test directly.
ikiwa __name__ == "__main__":
    test_main(1)
