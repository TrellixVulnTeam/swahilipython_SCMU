"""Heap queue algorithm (a.k.a. priority queue).

Heaps are arrays kila which a[k] <= a[2*k+1] na a[k] <= a[2*k+2] for
all k, counting elements kutoka 0.  For the sake of comparison,
non-existing elements are considered to be infinite.  The interesting
property of a heap ni that a[0] ni always its smallest element.

Usage:

heap = []            # creates an empty heap
heappush(heap, item) # pushes a new item on the heap
item = heappop(heap) # pops the smallest item kutoka the heap
item = heap[0]       # smallest item on the heap without popping it
heapify(x)           # transforms list into a heap, in-place, kwenye linear time
item = heapreplace(heap, item) # pops na rudishas smallest item, na adds
                               # new item; the heap size ni unchanged

Our API differs kutoka textbook heap algorithms kama follows:

- We use 0-based indexing.  This makes the relationship between the
  index kila a node na the indexes kila its children slightly less
  obvious, but ni more suitable since Python uses 0-based indexing.

- Our heappop() method rudishas the smallest item, sio the largest.

These two make it possible to view the heap kama a regular Python list
without surprises: heap[0] ni the smallest item, na heap.sort()
maintains the heap invariant!
"""

# Original code by Kevin O'Connor, augmented by Tim Peters na Raymond Hettinger

__about__ = """Heap queues

[explanation by François Pinard]

Heaps are arrays kila which a[k] <= a[2*k+1] na a[k] <= a[2*k+2] for
all k, counting elements kutoka 0.  For the sake of comparison,
non-existing elements are considered to be infinite.  The interesting
property of a heap ni that a[0] ni always its smallest element.

The strange invariant above ni meant to be an efficient memory
representation kila a tournament.  The numbers below are `k', sio a[k]:

                                   0

                  1                                 2

          3               4                5               6

      7       8       9       10      11      12      13      14

    15 16   17 18   19 20   21 22   23 24   25 26   27 28   29 30


In the tree above, each cell `k' ni topping `2*k+1' na `2*k+2'.  In
a usual binary tournament we see kwenye sports, each cell ni the winner
over the two cells it tops, na we can trace the winner down the tree
to see all opponents s/he had.  However, kwenye many computer applications
of such tournaments, we do sio need to trace the history of a winner.
To be more memory efficient, when a winner ni promoted, we try to
replace it by something isipokua at a lower level, na the rule becomes
that a cell na the two cells it tops contain three different items,
but the top cell "wins" over the two topped cells.

If this heap invariant ni protected at all time, index 0 ni clearly
the overall winner.  The simplest algorithmic way to remove it and
find the "next" winner ni to move some loser (let's say cell 30 kwenye the
diagram above) into the 0 position, na then percolate this new 0 down
the tree, exchanging values, until the invariant ni re-established.
This ni clearly logarithmic on the total number of items kwenye the tree.
By iterating over all items, you get an O(n ln n) sort.

A nice feature of this sort ni that you can efficiently insert new
items wakati the sort ni going on, provided that the inserted items are
not "better" than the last 0'th element you extracted.  This is
especially useful kwenye simulation contexts, where the tree holds all
incoming events, na the "win" condition means the smallest scheduled
time.  When an event schedule other events kila execution, they are
scheduled into the future, so they can easily go into the heap.  So, a
heap ni a good structure kila implementing schedulers (this ni what I
used kila my MIDI sequencer :-).

Various structures kila implementing schedulers have been extensively
studied, na heaps are good kila this, kama they are reasonably speedy,
the speed ni almost constant, na the worst case ni sio much different
than the average case.  However, there are other representations which
are more efficient overall, yet the worst cases might be terrible.

Heaps are also very useful kwenye big disk sorts.  You most probably all
know that a big sort implies producing "runs" (which are pre-sorted
sequences, which size ni usually related to the amount of CPU memory),
followed by a merging pitaes kila these runs, which merging ni often
very cleverly organised[1].  It ni very agizaant that the initial
sort produces the longest runs possible.  Tournaments are a good way
to that.  If, using all the memory available to hold a tournament, you
replace na percolate items that happen to fit the current run, you'll
produce runs which are twice the size of the memory kila random input,
and much better kila input fuzzily ordered.

Moreover, ikiwa you output the 0'th item on disk na get an input which
may sio fit kwenye the current tournament (because the value "wins" over
the last output value), it cannot fit kwenye the heap, so the size of the
heap decreases.  The freed memory could be cleverly reused immediately
kila progressively building a second heap, which grows at exactly the
same rate the first heap ni melting.  When the first heap completely
vanishes, you switch heaps na start a new run.  Clever na quite
effective!

In a word, heaps are useful memory structures to know.  I use them in
a few applications, na I think it ni good to keep a `heap' module
around. :-)

--------------------
[1] The disk balancing algorithms which are current, nowadays, are
more annoying than clever, na this ni a consequence of the seeking
capabilities of the disks.  On devices which cannot seek, like big
tape drives, the story was quite different, na one had to be very
clever to ensure (far kwenye advance) that each tape movement will be the
most effective possible (that is, will best participate at
"progressing" the merge).  Some tapes were even able to read
backwards, na this was also used to avoid the rewinding time.
Believe me, real good tape sorts were quite spectacular to watch!
From all times, sorting has always been a Great Art! :-)
"""

__all__ = ['heappush', 'heappop', 'heapify', 'heapreplace', 'merge',
           'nlargest', 'nsmallest', 'heappushpop']

eleza heappush(heap, item):
    """Push item onto heap, maintaining the heap invariant."""
    heap.append(item)
    _siftdown(heap, 0, len(heap)-1)

eleza heappop(heap):
    """Pop the smallest item off the heap, maintaining the heap invariant."""
    lastelt = heap.pop()    # ashirias appropriate IndexError ikiwa heap ni empty
    ikiwa heap:
        rudishaitem = heap[0]
        heap[0] = lastelt
        _siftup(heap, 0)
        rudisha rudishaitem
    rudisha lastelt

eleza heapreplace(heap, item):
    """Pop na rudisha the current smallest value, na add the new item.

    This ni more efficient than heappop() followed by heappush(), na can be
    more appropriate when using a fixed-size heap.  Note that the value
    rudishaed may be larger than item!  That constrains reasonable uses of
    this routine unless written kama part of a conditional replacement:

        ikiwa item > heap[0]:
            item = heapreplace(heap, item)
    """
    rudishaitem = heap[0]    # ashirias appropriate IndexError ikiwa heap ni empty
    heap[0] = item
    _siftup(heap, 0)
    rudisha rudishaitem

eleza heappushpop(heap, item):
    """Fast version of a heappush followed by a heappop."""
    ikiwa heap na heap[0] < item:
        item, heap[0] = heap[0], item
        _siftup(heap, 0)
    rudisha item

eleza heapify(x):
    """Transform list into a heap, in-place, kwenye O(len(x)) time."""
    n = len(x)
    # Transform bottom-up.  The largest index there's any point to looking at
    # ni the largest ukijumuisha a child index in-range, so must have 2*i + 1 < n,
    # ama i < (n-1)/2.  If n ni even = 2*j, this ni (2*j-1)/2 = j-1/2 so
    # j-1 ni the largest, which ni n//2 - 1.  If n ni odd = 2*j+1, this is
    # (2*j+1-1)/2 = j so j-1 ni the largest, na that's again n//2-1.
    kila i kwenye reversed(range(n//2)):
        _siftup(x, i)

eleza _heappop_max(heap):
    """Maxheap version of a heappop."""
    lastelt = heap.pop()    # ashirias appropriate IndexError ikiwa heap ni empty
    ikiwa heap:
        rudishaitem = heap[0]
        heap[0] = lastelt
        _siftup_max(heap, 0)
        rudisha rudishaitem
    rudisha lastelt

eleza _heapreplace_max(heap, item):
    """Maxheap version of a heappop followed by a heappush."""
    rudishaitem = heap[0]    # ashirias appropriate IndexError ikiwa heap ni empty
    heap[0] = item
    _siftup_max(heap, 0)
    rudisha rudishaitem

eleza _heapify_max(x):
    """Transform list into a maxheap, in-place, kwenye O(len(x)) time."""
    n = len(x)
    kila i kwenye reversed(range(n//2)):
        _siftup_max(x, i)

# 'heap' ni a heap at all indices >= startpos, tatizo possibly kila pos.  pos
# ni the index of a leaf ukijumuisha a possibly out-of-order value.  Restore the
# heap invariant.
eleza _siftdown(heap, startpos, pos):
    newitem = heap[pos]
    # Follow the path to the root, moving parents down until finding a place
    # newitem fits.
    wakati pos > startpos:
        parentpos = (pos - 1) >> 1
        parent = heap[parentpos]
        ikiwa newitem < parent:
            heap[pos] = parent
            pos = parentpos
            endelea
        koma
    heap[pos] = newitem

# The child indices of heap index pos are already heaps, na we want to make
# a heap at index pos too.  We do this by bubbling the smaller child of
# pos up (and so on ukijumuisha that child's children, etc) until hitting a leaf,
# then using _siftdown to move the oddball originally at index pos into place.
#
# We *could* koma out of the loop kama soon kama we find a pos where newitem <=
# both its children, but turns out that's sio a good idea, na despite that
# many books write the algorithm that way.  During a heap pop, the last array
# element ni sifted in, na that tends to be large, so that comparing it
# against values starting kutoka the root usually doesn't pay (= usually doesn't
# get us out of the loop early).  See Knuth, Volume 3, where this is
# explained na quantified kwenye an exercise.
#
# Cutting the # of comparisons ni agizaant, since these routines have no
# way to extract "the priority" kutoka an array element, so that intelligence
# ni likely to be hiding kwenye custom comparison methods, ama kwenye array elements
# storing (priority, record) tuples.  Comparisons are thus potentially
# expensive.
#
# On random arrays of length 1000, making this change cut the number of
# comparisons made by heapify() a little, na those made by exhaustive
# heappop() a lot, kwenye accord ukijumuisha theory.  Here are typical results kutoka 3
# runs (3 just to demonstrate how small the variance is):
#
# Compares needed by heapify     Compares needed by 1000 heappops
# --------------------------     --------------------------------
# 1837 cut to 1663               14996 cut to 8680
# 1855 cut to 1659               14966 cut to 8678
# 1847 cut to 1660               15024 cut to 8703
#
# Building the heap by using heappush() 1000 times instead required
# 2198, 2148, na 2219 compares:  heapify() ni more efficient, when
# you can use it.
#
# The total compares needed by list.sort() on the same lists were 8627,
# 8627, na 8632 (this should be compared to the sum of heapify() and
# heappop() compares):  list.sort() ni (unsurprisingly!) more efficient
# kila sorting.

eleza _siftup(heap, pos):
    endpos = len(heap)
    startpos = pos
    newitem = heap[pos]
    # Bubble up the smaller child until hitting a leaf.
    childpos = 2*pos + 1    # leftmost child position
    wakati childpos < endpos:
        # Set childpos to index of smaller child.
        rightpos = childpos + 1
        ikiwa rightpos < endpos na sio heap[childpos] < heap[rightpos]:
            childpos = rightpos
        # Move the smaller child up.
        heap[pos] = heap[childpos]
        pos = childpos
        childpos = 2*pos + 1
    # The leaf at pos ni empty now.  Put newitem there, na bubble it up
    # to its final resting place (by sifting its parents down).
    heap[pos] = newitem
    _siftdown(heap, startpos, pos)

eleza _siftdown_max(heap, startpos, pos):
    'Maxheap variant of _siftdown'
    newitem = heap[pos]
    # Follow the path to the root, moving parents down until finding a place
    # newitem fits.
    wakati pos > startpos:
        parentpos = (pos - 1) >> 1
        parent = heap[parentpos]
        ikiwa parent < newitem:
            heap[pos] = parent
            pos = parentpos
            endelea
        koma
    heap[pos] = newitem

eleza _siftup_max(heap, pos):
    'Maxheap variant of _siftup'
    endpos = len(heap)
    startpos = pos
    newitem = heap[pos]
    # Bubble up the larger child until hitting a leaf.
    childpos = 2*pos + 1    # leftmost child position
    wakati childpos < endpos:
        # Set childpos to index of larger child.
        rightpos = childpos + 1
        ikiwa rightpos < endpos na sio heap[rightpos] < heap[childpos]:
            childpos = rightpos
        # Move the larger child up.
        heap[pos] = heap[childpos]
        pos = childpos
        childpos = 2*pos + 1
    # The leaf at pos ni empty now.  Put newitem there, na bubble it up
    # to its final resting place (by sifting its parents down).
    heap[pos] = newitem
    _siftdown_max(heap, startpos, pos)

eleza merge(*iterables, key=Tupu, reverse=Uongo):
    '''Merge multiple sorted inputs into a single sorted output.

    Similar to sorted(itertools.chain(*iterables)) but rudishas a generator,
    does sio pull the data into memory all at once, na assumes that each of
    the input streams ni already sorted (smallest to largest).

    >>> list(merge([1,3,5,7], [0,2,4,8], [5,10,15,20], [], [25]))
    [0, 1, 2, 3, 4, 5, 5, 7, 8, 10, 15, 20, 25]

    If *key* ni sio Tupu, applies a key function to each element to determine
    its sort order.

    >>> list(merge(['dog', 'horse'], ['cat', 'fish', 'kangaroo'], key=len))
    ['dog', 'cat', 'fish', 'horse', 'kangaroo']

    '''

    h = []
    h_append = h.append

    ikiwa reverse:
        _heapify = _heapify_max
        _heappop = _heappop_max
        _heapreplace = _heapreplace_max
        direction = -1
    isipokua:
        _heapify = heapify
        _heappop = heappop
        _heapreplace = heapreplace
        direction = 1

    ikiwa key ni Tupu:
        kila order, it kwenye enumerate(map(iter, iterables)):
            jaribu:
                next = it.__next__
                h_append([next(), order * direction, next])
            tatizo StopIteration:
                pita
        _heapify(h)
        wakati len(h) > 1:
            jaribu:
                wakati Kweli:
                    value, order, next = s = h[0]
                    tuma value
                    s[0] = next()           # ashirias StopIteration when exhausted
                    _heapreplace(h, s)      # restore heap condition
            tatizo StopIteration:
                _heappop(h)                 # remove empty iterator
        ikiwa h:
            # fast case when only a single iterator remains
            value, order, next = h[0]
            tuma value
            tuma kutoka next.__self__
        rudisha

    kila order, it kwenye enumerate(map(iter, iterables)):
        jaribu:
            next = it.__next__
            value = next()
            h_append([key(value), order * direction, value, next])
        tatizo StopIteration:
            pita
    _heapify(h)
    wakati len(h) > 1:
        jaribu:
            wakati Kweli:
                key_value, order, value, next = s = h[0]
                tuma value
                value = next()
                s[0] = key(value)
                s[2] = value
                _heapreplace(h, s)
        tatizo StopIteration:
            _heappop(h)
    ikiwa h:
        key_value, order, value, next = h[0]
        tuma value
        tuma kutoka next.__self__


# Algorithm notes kila nlargest() na nsmallest()
# ==============================================
#
# Make a single pita over the data wakati keeping the k most extreme values
# kwenye a heap.  Memory consumption ni limited to keeping k values kwenye a list.
#
# Measured performance kila random inputs:
#
#                                   number of comparisons
#    n inputs     k-extreme values  (average of 5 trials)   % more than min()
# -------------   ----------------  ---------------------   -----------------
#      1,000           100                  3,317               231.7%
#     10,000           100                 14,046                40.5%
#    100,000           100                105,749                 5.7%
#  1,000,000           100              1,007,751                 0.8%
# 10,000,000           100             10,009,401                 0.1%
#
# Theoretical number of comparisons kila k smallest of n random inputs:
#
# Step   Comparisons                  Action
# ----   --------------------------   ---------------------------
#  1     1.66 * k                     heapify the first k-inputs
#  2     n - k                        compare remaining elements to top of heap
#  3     k * (1 + lg2(k)) * ln(n/k)   replace the topmost value on the heap
#  4     k * lg2(k) - (k/2)           final sort of the k most extreme values
#
# Combining na simplifying kila a rough estimate gives:
#
#        comparisons = n + k * (log(k, 2) * log(n/k) + log(k, 2) + log(n/k))
#
# Computing the number of comparisons kila step 3:
# -----------------------------------------------
# * For the i-th new value kutoka the iterable, the probability of being kwenye the
#   k most extreme values ni k/i.  For example, the probability of the 101st
#   value seen being kwenye the 100 most extreme values ni 100/101.
# * If the value ni a new extreme value, the cost of inserting it into the
#   heap ni 1 + log(k, 2).
# * The probability times the cost gives:
#            (k/i) * (1 + log(k, 2))
# * Summing across the remaining n-k elements gives:
#            sum((k/i) * (1 + log(k, 2)) kila i kwenye range(k+1, n+1))
# * This reduces to:
#            (H(n) - H(k)) * k * (1 + log(k, 2))
# * Where H(n) ni the n-th harmonic number estimated by:
#            gamma = 0.5772156649
#            H(n) = log(n, e) + gamma + 1 / (2 * n)
#   http://en.wikipedia.org/wiki/Harmonic_series_(mathematics)#Rate_of_divergence
# * Substituting the H(n) formula:
#            comparisons = k * (1 + log(k, 2)) * (log(n/k, e) + (1/n - 1/k) / 2)
#
# Worst-case kila step 3:
# ----------------------
# In the worst case, the input data ni reversed sorted so that every new element
# must be inserted kwenye the heap:
#
#             comparisons = 1.66 * k + log(k, 2) * (n - k)
#
# Alternative Algorithms
# ----------------------
# Other algorithms were sio used because they:
# 1) Took much more auxiliary memory,
# 2) Made multiple pitaes over the data.
# 3) Made more comparisons kwenye common cases (small k, large n, semi-random input).
# See the more detailed comparison of approach at:
# http://code.activestate.com/recipes/577573-compare-algorithms-for-heapqsmallest

eleza nsmallest(n, iterable, key=Tupu):
    """Find the n smallest elements kwenye a dataset.

    Equivalent to:  sorted(iterable, key=key)[:n]
    """

    # Short-cut kila n==1 ni to use min()
    ikiwa n == 1:
        it = iter(iterable)
        sentinel = object()
        result = min(it, default=sentinel, key=key)
        rudisha [] ikiwa result ni sentinel isipokua [result]

    # When n>=size, it's faster to use sorted()
    jaribu:
        size = len(iterable)
    tatizo (TypeError, AttributeError):
        pita
    isipokua:
        ikiwa n >= size:
            rudisha sorted(iterable, key=key)[:n]

    # When key ni none, use simpler decoration
    ikiwa key ni Tupu:
        it = iter(iterable)
        # put the range(n) first so that zip() doesn't
        # consume one too many elements kutoka the iterator
        result = [(elem, i) kila i, elem kwenye zip(range(n), it)]
        ikiwa sio result:
            rudisha result
        _heapify_max(result)
        top = result[0][0]
        order = n
        _heapreplace = _heapreplace_max
        kila elem kwenye it:
            ikiwa elem < top:
                _heapreplace(result, (elem, order))
                top, _order = result[0]
                order += 1
        result.sort()
        rudisha [elem kila (elem, order) kwenye result]

    # General case, slowest method
    it = iter(iterable)
    result = [(key(elem), i, elem) kila i, elem kwenye zip(range(n), it)]
    ikiwa sio result:
        rudisha result
    _heapify_max(result)
    top = result[0][0]
    order = n
    _heapreplace = _heapreplace_max
    kila elem kwenye it:
        k = key(elem)
        ikiwa k < top:
            _heapreplace(result, (k, order, elem))
            top, _order, _elem = result[0]
            order += 1
    result.sort()
    rudisha [elem kila (k, order, elem) kwenye result]

eleza nlargest(n, iterable, key=Tupu):
    """Find the n largest elements kwenye a dataset.

    Equivalent to:  sorted(iterable, key=key, reverse=Kweli)[:n]
    """

    # Short-cut kila n==1 ni to use max()
    ikiwa n == 1:
        it = iter(iterable)
        sentinel = object()
        result = max(it, default=sentinel, key=key)
        rudisha [] ikiwa result ni sentinel isipokua [result]

    # When n>=size, it's faster to use sorted()
    jaribu:
        size = len(iterable)
    tatizo (TypeError, AttributeError):
        pita
    isipokua:
        ikiwa n >= size:
            rudisha sorted(iterable, key=key, reverse=Kweli)[:n]

    # When key ni none, use simpler decoration
    ikiwa key ni Tupu:
        it = iter(iterable)
        result = [(elem, i) kila i, elem kwenye zip(range(0, -n, -1), it)]
        ikiwa sio result:
            rudisha result
        heapify(result)
        top = result[0][0]
        order = -n
        _heapreplace = heapreplace
        kila elem kwenye it:
            ikiwa top < elem:
                _heapreplace(result, (elem, order))
                top, _order = result[0]
                order -= 1
        result.sort(reverse=Kweli)
        rudisha [elem kila (elem, order) kwenye result]

    # General case, slowest method
    it = iter(iterable)
    result = [(key(elem), i, elem) kila i, elem kwenye zip(range(0, -n, -1), it)]
    ikiwa sio result:
        rudisha result
    heapify(result)
    top = result[0][0]
    order = -n
    _heapreplace = heapreplace
    kila elem kwenye it:
        k = key(elem)
        ikiwa top < k:
            _heapreplace(result, (k, order, elem))
            top, _order, _elem = result[0]
            order -= 1
    result.sort(reverse=Kweli)
    rudisha [elem kila (k, order, elem) kwenye result]

# If available, use C implementation
jaribu:
    kutoka _heapq agiza *
tatizo ImportError:
    pita
jaribu:
    kutoka _heapq agiza _heapreplace_max
tatizo ImportError:
    pita
jaribu:
    kutoka _heapq agiza _heapify_max
tatizo ImportError:
    pita
jaribu:
    kutoka _heapq agiza _heappop_max
tatizo ImportError:
    pita


ikiwa __name__ == "__main__":

    agiza doctest # pragma: no cover
    andika(doctest.testmod()) # pragma: no cover
