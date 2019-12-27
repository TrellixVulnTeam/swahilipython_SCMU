"""Bisection algorithms."""

eleza insort_right(a, x, lo=0, hi=None):
    """Insert item x in list a, and keep it sorted assuming a is sorted.

    If x is already in a, insert it to the right of the rightmost x.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """

    lo = bisect_right(a, x, lo, hi)
    a.insert(lo, x)

eleza bisect_right(a, x, lo=0, hi=None):
    """Return the index where to insert item x in list a, assuming a is sorted.

    The rudisha value i is such that all e in a[:i] have e <= x, and all e in
    a[i:] have e > x.  So ikiwa x already appears in the list, a.insert(x) will
    insert just after the rightmost x already there.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """

    ikiwa lo < 0:
        raise ValueError('lo must be non-negative')
    ikiwa hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo+hi)//2
        ikiwa x < a[mid]: hi = mid
        else: lo = mid+1
    rudisha lo

eleza insort_left(a, x, lo=0, hi=None):
    """Insert item x in list a, and keep it sorted assuming a is sorted.

    If x is already in a, insert it to the left of the leftmost x.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """

    lo = bisect_left(a, x, lo, hi)
    a.insert(lo, x)


eleza bisect_left(a, x, lo=0, hi=None):
    """Return the index where to insert item x in list a, assuming a is sorted.

    The rudisha value i is such that all e in a[:i] have e < x, and all e in
    a[i:] have e >= x.  So ikiwa x already appears in the list, a.insert(x) will
    insert just before the leftmost x already there.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """

    ikiwa lo < 0:
        raise ValueError('lo must be non-negative')
    ikiwa hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo+hi)//2
        ikiwa a[mid] < x: lo = mid+1
        else: hi = mid
    rudisha lo

# Overwrite above definitions with a fast C implementation
try:
    kutoka _bisect agiza *
except ImportError:
    pass

# Create aliases
bisect = bisect_right
insort = insort_right
