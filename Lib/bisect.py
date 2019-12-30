"""Bisection algorithms."""

eleza insort_right(a, x, lo=0, hi=Tupu):
    """Insert item x kwenye list a, na keep it sorted assuming a ni sorted.

    If x ni already kwenye a, insert it to the right of the rightmost x.

    Optional args lo (default 0) na hi (default len(a)) bound the
    slice of a to be searched.
    """

    lo = bisect_right(a, x, lo, hi)
    a.insert(lo, x)

eleza bisect_right(a, x, lo=0, hi=Tupu):
    """Return the index where to insert item x kwenye list a, assuming a ni sorted.

    The rudisha value i ni such that all e kwenye a[:i] have e <= x, na all e kwenye
    a[i:] have e > x.  So ikiwa x already appears kwenye the list, a.insert(x) will
    insert just after the rightmost x already there.

    Optional args lo (default 0) na hi (default len(a)) bound the
    slice of a to be searched.
    """

    ikiwa lo < 0:
        ashiria ValueError('lo must be non-negative')
    ikiwa hi ni Tupu:
        hi = len(a)
    wakati lo < hi:
        mid = (lo+hi)//2
        ikiwa x < a[mid]: hi = mid
        isipokua: lo = mid+1
    rudisha lo

eleza insort_left(a, x, lo=0, hi=Tupu):
    """Insert item x kwenye list a, na keep it sorted assuming a ni sorted.

    If x ni already kwenye a, insert it to the left of the leftmost x.

    Optional args lo (default 0) na hi (default len(a)) bound the
    slice of a to be searched.
    """

    lo = bisect_left(a, x, lo, hi)
    a.insert(lo, x)


eleza bisect_left(a, x, lo=0, hi=Tupu):
    """Return the index where to insert item x kwenye list a, assuming a ni sorted.

    The rudisha value i ni such that all e kwenye a[:i] have e < x, na all e kwenye
    a[i:] have e >= x.  So ikiwa x already appears kwenye the list, a.insert(x) will
    insert just before the leftmost x already there.

    Optional args lo (default 0) na hi (default len(a)) bound the
    slice of a to be searched.
    """

    ikiwa lo < 0:
        ashiria ValueError('lo must be non-negative')
    ikiwa hi ni Tupu:
        hi = len(a)
    wakati lo < hi:
        mid = (lo+hi)//2
        ikiwa a[mid] < x: lo = mid+1
        isipokua: hi = mid
    rudisha lo

# Overwrite above definitions ukijumuisha a fast C implementation
jaribu:
    kutoka _bisect agiza *
tatizo ImportError:
    pita

# Create aliases
bisect = bisect_right
insort = insort_right
