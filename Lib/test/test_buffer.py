#
# The ndarray object kutoka _testbuffer.c ni a complete implementation of
# a PEP-3118 buffer provider. It ni independent kutoka NumPy's ndarray
# na the tests don't require NumPy.
#
# If NumPy ni present, some tests check both ndarray implementations
# against each other.
#
# Most ndarray tests also check that memoryview(ndarray) behaves in
# the same way kama the original. Thus, a substantial part of the
# memoryview tests ni now kwenye this module.
#

agiza contextlib
agiza unittest
kutoka test agiza support
kutoka itertools agiza permutations, product
kutoka random agiza randrange, sample, choice
agiza warnings
agiza sys, array, io, os
kutoka decimal agiza Decimal
kutoka fractions agiza Fraction

jaribu:
    kutoka _testbuffer agiza *
tatizo ImportError:
    ndarray = Tupu

jaribu:
    agiza struct
tatizo ImportError:
    struct = Tupu

jaribu:
    agiza ctypes
tatizo ImportError:
    ctypes = Tupu

jaribu:
    ukijumuisha support.EnvironmentVarGuard() kama os.environ, \
         warnings.catch_warnings():
        kutoka numpy agiza ndarray kama numpy_array
tatizo ImportError:
    numpy_array = Tupu


SHORT_TEST = Kweli


# ======================================================================
#                    Random lists by format specifier
# ======================================================================

# Native format chars na their ranges.
NATIVE = {
    '?':0, 'c':0, 'b':0, 'B':0,
    'h':0, 'H':0, 'i':0, 'I':0,
    'l':0, 'L':0, 'n':0, 'N':0,
    'f':0, 'd':0, 'P':0
}

# NumPy does sio have 'n' ama 'N':
ikiwa numpy_array:
    toa NATIVE['n']
    toa NATIVE['N']

ikiwa struct:
    jaribu:
        # Add "qQ" ikiwa present kwenye native mode.
        struct.pack('Q', 2**64-1)
        NATIVE['q'] = 0
        NATIVE['Q'] = 0
    tatizo struct.error:
        pita

# Standard format chars na their ranges.
STANDARD = {
    '?':(0, 2),            'c':(0, 1<<8),
    'b':(-(1<<7), 1<<7),   'B':(0, 1<<8),
    'h':(-(1<<15), 1<<15), 'H':(0, 1<<16),
    'i':(-(1<<31), 1<<31), 'I':(0, 1<<32),
    'l':(-(1<<31), 1<<31), 'L':(0, 1<<32),
    'q':(-(1<<63), 1<<63), 'Q':(0, 1<<64),
    'f':(-(1<<63), 1<<63), 'd':(-(1<<1023), 1<<1023)
}

eleza native_type_range(fmt):
    """Return range of a native type."""
    ikiwa fmt == 'c':
        lh = (0, 256)
    lasivyo fmt == '?':
        lh = (0, 2)
    lasivyo fmt == 'f':
        lh = (-(1<<63), 1<<63)
    lasivyo fmt == 'd':
        lh = (-(1<<1023), 1<<1023)
    isipokua:
        kila exp kwenye (128, 127, 64, 63, 32, 31, 16, 15, 8, 7):
            jaribu:
                struct.pack(fmt, (1<<exp)-1)
                koma
            tatizo struct.error:
                pita
        lh = (-(1<<exp), 1<<exp) ikiwa exp & 1 isipokua (0, 1<<exp)
    rudisha lh

fmtdict = {
    '':NATIVE,
    '@':NATIVE,
    '<':STANDARD,
    '>':STANDARD,
    '=':STANDARD,
    '!':STANDARD
}

ikiwa struct:
    kila fmt kwenye fmtdict['@']:
        fmtdict['@'][fmt] = native_type_range(fmt)

MEMORYVIEW = NATIVE.copy()
ARRAY = NATIVE.copy()
kila k kwenye NATIVE:
    ikiwa sio k kwenye "bBhHiIlLfd":
        toa ARRAY[k]

BYTEFMT = NATIVE.copy()
kila k kwenye NATIVE:
    ikiwa sio k kwenye "Bbc":
        toa BYTEFMT[k]

fmtdict['m']  = MEMORYVIEW
fmtdict['@m'] = MEMORYVIEW
fmtdict['a']  = ARRAY
fmtdict['b']  = BYTEFMT
fmtdict['@b']  = BYTEFMT

# Capabilities of the test objects:
MODE = 0
MULT = 1
cap = {         # format chars                  # multiplier
  'ndarray':    (['', '@', '<', '>', '=', '!'], ['', '1', '2', '3']),
  'array':      (['a'],                         ['']),
  'numpy':      ([''],                          ['']),
  'memoryview': (['@m', 'm'],                   ['']),
  'bytefmt':    (['@b', 'b'],                   ['']),
}

eleza randrange_fmt(mode, char, obj):
    """Return random item kila a type specified by a mode na a single
       format character."""
    x = randrange(*fmtdict[mode][char])
    ikiwa char == 'c':
        x = bytes([x])
        ikiwa obj == 'numpy' na x == b'\x00':
            # http://projects.scipy.org/numpy/ticket/1925
            x = b'\x01'
    ikiwa char == '?':
        x = bool(x)
    ikiwa char == 'f' ama char == 'd':
        x = struct.pack(char, x)
        x = struct.unpack(char, x)[0]
    rudisha x

eleza gen_item(fmt, obj):
    """Return single random item."""
    mode, chars = fmt.split('#')
    x = []
    kila c kwenye chars:
        x.append(randrange_fmt(mode, c, obj))
    rudisha x[0] ikiwa len(x) == 1 isipokua tuple(x)

eleza gen_items(n, fmt, obj):
    """Return a list of random items (or a scalar)."""
    ikiwa n == 0:
        rudisha gen_item(fmt, obj)
    lst = [0] * n
    kila i kwenye range(n):
        lst[i] = gen_item(fmt, obj)
    rudisha lst

eleza struct_items(n, obj):
    mode = choice(cap[obj][MODE])
    xfmt = mode + '#'
    fmt = mode.strip('amb')
    nmemb = randrange(2, 10) # number of struct members
    kila _ kwenye range(nmemb):
        char = choice(tuple(fmtdict[mode]))
        multiplier = choice(cap[obj][MULT])
        xfmt += (char * int(multiplier ikiwa multiplier isipokua 1))
        fmt += (multiplier + char)
    items = gen_items(n, xfmt, obj)
    item = gen_item(xfmt, obj)
    rudisha fmt, items, item

eleza randitems(n, obj='ndarray', mode=Tupu, char=Tupu):
    """Return random format, items, item."""
    ikiwa mode ni Tupu:
        mode = choice(cap[obj][MODE])
    ikiwa char ni Tupu:
        char = choice(tuple(fmtdict[mode]))
    multiplier = choice(cap[obj][MULT])
    fmt = mode + '#' + char * int(multiplier ikiwa multiplier isipokua 1)
    items = gen_items(n, fmt, obj)
    item = gen_item(fmt, obj)
    fmt = mode.strip('amb') + multiplier + char
    rudisha fmt, items, item

eleza iter_mode(n, obj='ndarray'):
    """Iterate through supported mode/char combinations."""
    kila mode kwenye cap[obj][MODE]:
        kila char kwenye fmtdict[mode]:
            tuma randitems(n, obj, mode, char)

eleza iter_format(nitems, testobj='ndarray'):
    """Yield (format, items, item) kila all possible modes na format
       characters plus one random compound format string."""
    kila t kwenye iter_mode(nitems, testobj):
        tuma t
    ikiwa testobj != 'ndarray':
        rudisha
    tuma struct_items(nitems, testobj)


eleza is_byte_format(fmt):
    rudisha 'c' kwenye fmt ama 'b' kwenye fmt ama 'B' kwenye fmt

eleza is_memoryview_format(fmt):
    """format suitable kila memoryview"""
    x = len(fmt)
    rudisha ((x == 1 ama (x == 2 na fmt[0] == '@')) na
            fmt[x-1] kwenye MEMORYVIEW)

NON_BYTE_FORMAT = [c kila c kwenye fmtdict['@'] ikiwa sio is_byte_format(c)]


# ======================================================================
#       Multi-dimensional tolist(), slicing na slice assignments
# ======================================================================

eleza atomp(lst):
    """Tuple items (representing structs) are regarded kama atoms."""
    rudisha sio isinstance(lst, list)

eleza listp(lst):
    rudisha isinstance(lst, list)

eleza prod(lst):
    """Product of list elements."""
    ikiwa len(lst) == 0:
        rudisha 0
    x = lst[0]
    kila v kwenye lst[1:]:
        x *= v
    rudisha x

eleza strides_from_shape(ndim, shape, itemsize, layout):
    """Calculate strides of a contiguous array. Layout ni 'C' ama
       'F' (Fortran)."""
    ikiwa ndim == 0:
        rudisha ()
    ikiwa layout == 'C':
        strides = list(shape[1:]) + [itemsize]
        kila i kwenye range(ndim-2, -1, -1):
            strides[i] *= strides[i+1]
    isipokua:
        strides = [itemsize] + list(shape[:-1])
        kila i kwenye range(1, ndim):
            strides[i] *= strides[i-1]
    rudisha strides

eleza _ca(items, s):
    """Convert flat item list to the nested list representation of a
       multidimensional C array ukijumuisha shape 's'."""
    ikiwa atomp(items):
        rudisha items
    ikiwa len(s) == 0:
        rudisha items[0]
    lst = [0] * s[0]
    stride = len(items) // s[0] ikiwa s[0] isipokua 0
    kila i kwenye range(s[0]):
        start = i*stride
        lst[i] = _ca(items[start:start+stride], s[1:])
    rudisha lst

eleza _fa(items, s):
    """Convert flat item list to the nested list representation of a
       multidimensional Fortran array ukijumuisha shape 's'."""
    ikiwa atomp(items):
        rudisha items
    ikiwa len(s) == 0:
        rudisha items[0]
    lst = [0] * s[0]
    stride = s[0]
    kila i kwenye range(s[0]):
        lst[i] = _fa(items[i::stride], s[1:])
    rudisha lst

eleza carray(items, shape):
    ikiwa listp(items) na sio 0 kwenye shape na prod(shape) != len(items):
        ashiria ValueError("prod(shape) != len(items)")
    rudisha _ca(items, shape)

eleza farray(items, shape):
    ikiwa listp(items) na sio 0 kwenye shape na prod(shape) != len(items):
        ashiria ValueError("prod(shape) != len(items)")
    rudisha _fa(items, shape)

eleza indices(shape):
    """Generate all possible tuples of indices."""
    iterables = [range(v) kila v kwenye shape]
    rudisha product(*iterables)

eleza getindex(ndim, ind, strides):
    """Convert multi-dimensional index to the position kwenye the flat list."""
    ret = 0
    kila i kwenye range(ndim):
        ret += strides[i] * ind[i]
    rudisha ret

eleza transpose(src, shape):
    """Transpose flat item list that ni regarded kama a multi-dimensional
       matrix defined by shape: dest...[k][j][i] = src[i][j][k]...  """
    ikiwa sio shape:
        rudisha src
    ndim = len(shape)
    sstrides = strides_from_shape(ndim, shape, 1, 'C')
    dstrides = strides_from_shape(ndim, shape[::-1], 1, 'C')
    dest = [0] * len(src)
    kila ind kwenye indices(shape):
        fr = getindex(ndim, ind, sstrides)
        to = getindex(ndim, ind[::-1], dstrides)
        dest[to] = src[fr]
    rudisha dest

eleza _flatten(lst):
    """flatten list"""
    ikiwa lst == []:
        rudisha lst
    ikiwa atomp(lst):
        rudisha [lst]
    rudisha _flatten(lst[0]) + _flatten(lst[1:])

eleza flatten(lst):
    """flatten list ama rudisha scalar"""
    ikiwa atomp(lst): # scalar
        rudisha lst
    rudisha _flatten(lst)

eleza slice_shape(lst, slices):
    """Get the shape of lst after slicing: slices ni a list of slice
       objects."""
    ikiwa atomp(lst):
        rudisha []
    rudisha [len(lst[slices[0]])] + slice_shape(lst[0], slices[1:])

eleza multislice(lst, slices):
    """Multi-dimensional slicing: slices ni a list of slice objects."""
    ikiwa atomp(lst):
        rudisha lst
    rudisha [multislice(sublst, slices[1:]) kila sublst kwenye lst[slices[0]]]

eleza m_assign(llst, rlst, lslices, rslices):
    """Multi-dimensional slice assignment: llst na rlst are the operands,
       lslices na rslices are lists of slice objects. llst na rlst must
       have the same structure.

       For a two-dimensional example, this ni sio implemented kwenye Python:

         llst[0:3:2, 0:3:2] = rlst[1:3:1, 1:3:1]

       Instead we write:

         lslices = [slice(0,3,2), slice(0,3,2)]
         rslices = [slice(1,3,1), slice(1,3,1)]
         multislice_assign(llst, rlst, lslices, rslices)
    """
    ikiwa atomp(rlst):
        rudisha rlst
    rlst = [m_assign(l, r, lslices[1:], rslices[1:])
            kila l, r kwenye zip(llst[lslices[0]], rlst[rslices[0]])]
    llst[lslices[0]] = rlst
    rudisha llst

eleza cmp_structure(llst, rlst, lslices, rslices):
    """Compare the structure of llst[lslices] na rlst[rslices]."""
    lshape = slice_shape(llst, lslices)
    rshape = slice_shape(rlst, rslices)
    ikiwa (len(lshape) != len(rshape)):
        rudisha -1
    kila i kwenye range(len(lshape)):
        ikiwa lshape[i] != rshape[i]:
            rudisha -1
        ikiwa lshape[i] == 0:
            rudisha 0
    rudisha 0

eleza multislice_assign(llst, rlst, lslices, rslices):
    """Return llst after assigning: llst[lslices] = rlst[rslices]"""
    ikiwa cmp_structure(llst, rlst, lslices, rslices) < 0:
        ashiria ValueError("lvalue na rvalue have different structures")
    rudisha m_assign(llst, rlst, lslices, rslices)


# ======================================================================
#                          Random structures
# ======================================================================

#
# PEP-3118 ni very permissive ukijumuisha respect to the contents of a
# Py_buffer. In particular:
#
#   - shape can be zero
#   - strides can be any integer, including zero
#   - offset can point to any location kwenye the underlying
#     memory block, provided that it ni a multiple of
#     itemsize.
#
# The functions kwenye this section test na verify random structures
# kwenye full generality. A structure ni valid iff it fits kwenye the
# underlying memory block.
#
# The structure 't' (short kila 'tuple') ni fully defined by:
#
#   t = (memlen, itemsize, ndim, shape, strides, offset)
#

eleza verify_structure(memlen, itemsize, ndim, shape, strides, offset):
    """Verify that the parameters represent a valid array within
       the bounds of the allocated memory:
           char *mem: start of the physical memory block
           memlen: length of the physical memory block
           offset: (char *)buf - mem
    """
    ikiwa offset % itemsize:
        rudisha Uongo
    ikiwa offset < 0 ama offset+itemsize > memlen:
        rudisha Uongo
    ikiwa any(v % itemsize kila v kwenye strides):
        rudisha Uongo

    ikiwa ndim <= 0:
        rudisha ndim == 0 na sio shape na sio strides
    ikiwa 0 kwenye shape:
        rudisha Kweli

    imin = sum(strides[j]*(shape[j]-1) kila j kwenye range(ndim)
               ikiwa strides[j] <= 0)
    imax = sum(strides[j]*(shape[j]-1) kila j kwenye range(ndim)
               ikiwa strides[j] > 0)

    rudisha 0 <= offset+imin na offset+imax+itemsize <= memlen

eleza get_item(lst, indices):
    kila i kwenye indices:
        lst = lst[i]
    rudisha lst

eleza memory_index(indices, t):
    """Location of an item kwenye the underlying memory."""
    memlen, itemsize, ndim, shape, strides, offset = t
    p = offset
    kila i kwenye range(ndim):
        p += strides[i]*indices[i]
    rudisha p

eleza is_overlapping(t):
    """The structure 't' ni overlapping ikiwa at least one memory location
       ni visited twice wakati iterating through all possible tuples of
       indices."""
    memlen, itemsize, ndim, shape, strides, offset = t
    visited = 1<<memlen
    kila ind kwenye indices(shape):
        i = memory_index(ind, t)
        bit = 1<<i
        ikiwa visited & bit:
            rudisha Kweli
        visited |= bit
    rudisha Uongo

eleza rand_structure(itemsize, valid, maxdim=5, maxshape=16, shape=()):
    """Return random structure:
           (memlen, itemsize, ndim, shape, strides, offset)
       If 'valid' ni true, the returned structure ni valid, otherwise invalid.
       If 'shape' ni given, use that instead of creating a random shape.
    """
    ikiwa sio shape:
        ndim = randrange(maxdim+1)
        ikiwa (ndim == 0):
            ikiwa valid:
                rudisha itemsize, itemsize, ndim, (), (), 0
            isipokua:
                nitems = randrange(1, 16+1)
                memlen = nitems * itemsize
                offset = -itemsize ikiwa randrange(2) == 0 isipokua memlen
                rudisha memlen, itemsize, ndim, (), (), offset

        minshape = 2
        n = randrange(100)
        ikiwa n >= 95 na valid:
            minshape = 0
        lasivyo n >= 90:
            minshape = 1
        shape = [0] * ndim

        kila i kwenye range(ndim):
            shape[i] = randrange(minshape, maxshape+1)
    isipokua:
        ndim = len(shape)

    maxstride = 5
    n = randrange(100)
    zero_stride = Kweli ikiwa n >= 95 na n & 1 isipokua Uongo

    strides = [0] * ndim
    strides[ndim-1] = itemsize * randrange(-maxstride, maxstride+1)
    ikiwa sio zero_stride na strides[ndim-1] == 0:
        strides[ndim-1] = itemsize

    kila i kwenye range(ndim-2, -1, -1):
        maxstride *= shape[i+1] ikiwa shape[i+1] isipokua 1
        ikiwa zero_stride:
            strides[i] = itemsize * randrange(-maxstride, maxstride+1)
        isipokua:
            strides[i] = ((1,-1)[randrange(2)] *
                          itemsize * randrange(1, maxstride+1))

    imin = imax = 0
    ikiwa sio 0 kwenye shape:
        imin = sum(strides[j]*(shape[j]-1) kila j kwenye range(ndim)
                   ikiwa strides[j] <= 0)
        imax = sum(strides[j]*(shape[j]-1) kila j kwenye range(ndim)
                   ikiwa strides[j] > 0)

    nitems = imax - imin
    ikiwa valid:
        offset = -imin * itemsize
        memlen = offset + (imax+1) * itemsize
    isipokua:
        memlen = (-imin + imax) * itemsize
        offset = -imin-itemsize ikiwa randrange(2) == 0 isipokua memlen
    rudisha memlen, itemsize, ndim, shape, strides, offset

eleza randslice_from_slicelen(slicelen, listlen):
    """Create a random slice of len slicelen that fits into listlen."""
    maxstart = listlen - slicelen
    start = randrange(maxstart+1)
    maxstep = (listlen - start) // slicelen ikiwa slicelen isipokua 1
    step = randrange(1, maxstep+1)
    stop = start + slicelen * step
    s = slice(start, stop, step)
    _, _, _, control = slice_indices(s, listlen)
    ikiwa control != slicelen:
        ashiria RuntimeError
    rudisha s

eleza randslice_from_shape(ndim, shape):
    """Create two sets of slices kila an array x ukijumuisha shape 'shape'
       such that shapeof(x[lslices]) == shapeof(x[rslices])."""
    lslices = [0] * ndim
    rslices = [0] * ndim
    kila n kwenye range(ndim):
        l = shape[n]
        slicelen = randrange(1, l+1) ikiwa l > 0 isipokua 0
        lslices[n] = randslice_from_slicelen(slicelen, l)
        rslices[n] = randslice_from_slicelen(slicelen, l)
    rudisha tuple(lslices), tuple(rslices)

eleza rand_aligned_slices(maxdim=5, maxshape=16):
    """Create (lshape, rshape, tuple(lslices), tuple(rslices)) such that
       shapeof(x[lslices]) == shapeof(y[rslices]), where x ni an array
       ukijumuisha shape 'lshape' na y ni an array ukijumuisha shape 'rshape'."""
    ndim = randrange(1, maxdim+1)
    minshape = 2
    n = randrange(100)
    ikiwa n >= 95:
        minshape = 0
    lasivyo n >= 90:
        minshape = 1
    all_random = Kweli ikiwa randrange(100) >= 80 isipokua Uongo
    lshape = [0]*ndim; rshape = [0]*ndim
    lslices = [0]*ndim; rslices = [0]*ndim

    kila n kwenye range(ndim):
        small = randrange(minshape, maxshape+1)
        big = randrange(minshape, maxshape+1)
        ikiwa big < small:
            big, small = small, big

        # Create a slice that fits the smaller value.
        ikiwa all_random:
            start = randrange(-small, small+1)
            stop = randrange(-small, small+1)
            step = (1,-1)[randrange(2)] * randrange(1, small+2)
            s_small = slice(start, stop, step)
            _, _, _, slicelen = slice_indices(s_small, small)
        isipokua:
            slicelen = randrange(1, small+1) ikiwa small > 0 isipokua 0
            s_small = randslice_from_slicelen(slicelen, small)

        # Create a slice of the same length kila the bigger value.
        s_big = randslice_from_slicelen(slicelen, big)
        ikiwa randrange(2) == 0:
            rshape[n], lshape[n] = big, small
            rslices[n], lslices[n] = s_big, s_small
        isipokua:
            rshape[n], lshape[n] = small, big
            rslices[n], lslices[n] = s_small, s_big

    rudisha lshape, rshape, tuple(lslices), tuple(rslices)

eleza randitems_from_structure(fmt, t):
    """Return a list of random items kila structure 't' ukijumuisha format
       'fmtchar'."""
    memlen, itemsize, _, _, _, _ = t
    rudisha gen_items(memlen//itemsize, '#'+fmt, 'numpy')

eleza ndarray_from_structure(items, fmt, t, flags=0):
    """Return ndarray kutoka the tuple returned by rand_structure()"""
    memlen, itemsize, ndim, shape, strides, offset = t
    rudisha ndarray(items, shape=shape, strides=strides, format=fmt,
                   offset=offset, flags=ND_WRITABLE|flags)

eleza numpy_array_from_structure(items, fmt, t):
    """Return numpy_array kutoka the tuple returned by rand_structure()"""
    memlen, itemsize, ndim, shape, strides, offset = t
    buf = bytearray(memlen)
    kila j, v kwenye enumerate(items):
        struct.pack_into(fmt, buf, j*itemsize, v)
    rudisha numpy_array(buffer=buf, shape=shape, strides=strides,
                       dtype=fmt, offset=offset)


# ======================================================================
#                          memoryview casts
# ======================================================================

eleza cast_items(exporter, fmt, itemsize, shape=Tupu):
    """Interpret the raw memory of 'exporter' kama a list of items with
       size 'itemsize'. If shape=Tupu, the new structure ni assumed to
       be 1-D ukijumuisha n * itemsize = bytelen. If shape ni given, the usual
       constraint kila contiguous arrays prod(shape) * itemsize = bytelen
       applies. On success, rudisha (items, shape). If the constraints
       cannot be met, rudisha (Tupu, Tupu). If a chunk of bytes ni interpreted
       kama NaN kama a result of float conversion, rudisha ('nan', Tupu)."""
    bytelen = exporter.nbytes
    ikiwa shape:
        ikiwa prod(shape) * itemsize != bytelen:
            rudisha Tupu, shape
    lasivyo shape == []:
        ikiwa exporter.ndim == 0 ama itemsize != bytelen:
            rudisha Tupu, shape
    isipokua:
        n, r = divmod(bytelen, itemsize)
        shape = [n]
        ikiwa r != 0:
            rudisha Tupu, shape

    mem = exporter.tobytes()
    byteitems = [mem[i:i+itemsize] kila i kwenye range(0, len(mem), itemsize)]

    items = []
    kila v kwenye byteitems:
        item = struct.unpack(fmt, v)[0]
        ikiwa item != item:
            rudisha 'nan', shape
        items.append(item)

    rudisha (items, shape) ikiwa shape != [] isipokua (items[0], shape)

eleza gencastshapes():
    """Generate shapes to test casting."""
    kila n kwenye range(32):
        tuma [n]
    ndim = randrange(4, 6)
    minshape = 1 ikiwa randrange(100) > 80 isipokua 2
    tuma [randrange(minshape, 5) kila _ kwenye range(ndim)]
    ndim = randrange(2, 4)
    minshape = 1 ikiwa randrange(100) > 80 isipokua 2
    tuma [randrange(minshape, 5) kila _ kwenye range(ndim)]


# ======================================================================
#                              Actual tests
# ======================================================================

eleza genslices(n):
    """Generate all possible slices kila a single dimension."""
    rudisha product(range(-n, n+1), range(-n, n+1), range(-n, n+1))

eleza genslices_ndim(ndim, shape):
    """Generate all possible slice tuples kila 'shape'."""
    iterables = [genslices(shape[n]) kila n kwenye range(ndim)]
    rudisha product(*iterables)

eleza rslice(n, allow_empty=Uongo):
    """Generate random slice kila a single dimension of length n.
       If zero=Kweli, the slices may be empty, otherwise they will
       be non-empty."""
    minlen = 0 ikiwa allow_empty ama n == 0 isipokua 1
    slicelen = randrange(minlen, n+1)
    rudisha randslice_from_slicelen(slicelen, n)

eleza rslices(n, allow_empty=Uongo):
    """Generate random slices kila a single dimension."""
    kila _ kwenye range(5):
        tuma rslice(n, allow_empty)

eleza rslices_ndim(ndim, shape, iterations=5):
    """Generate random slice tuples kila 'shape'."""
    # non-empty slices
    kila _ kwenye range(iterations):
        tuma tuple(rslice(shape[n]) kila n kwenye range(ndim))
    # possibly empty slices
    kila _ kwenye range(iterations):
        tuma tuple(rslice(shape[n], allow_empty=Kweli) kila n kwenye range(ndim))
    # invalid slices
    tuma tuple(slice(0,1,0) kila _ kwenye range(ndim))

eleza rpermutation(iterable, r=Tupu):
    pool = tuple(iterable)
    r = len(pool) ikiwa r ni Tupu isipokua r
    tuma tuple(sample(pool, r))

eleza ndarray_andika(nd):
    """Print ndarray kila debugging."""
    jaribu:
        x = nd.tolist()
    tatizo (TypeError, NotImplementedError):
        x = nd.tobytes()
    ikiwa isinstance(nd, ndarray):
        offset = nd.offset
        flags = nd.flags
    isipokua:
        offset = 'unknown'
        flags = 'unknown'
    andika("ndarray(%s, shape=%s, strides=%s, suboffsets=%s, offset=%s, "
          "format='%s', itemsize=%s, flags=%s)" %
          (x, nd.shape, nd.strides, nd.suboffsets, offset,
           nd.format, nd.itemsize, flags))
    sys.stdout.flush()


ITERATIONS = 100
MAXDIM = 5
MAXSHAPE = 10

ikiwa SHORT_TEST:
    ITERATIONS = 10
    MAXDIM = 3
    MAXSHAPE = 4
    genslices = rslices
    genslices_ndim = rslices_ndim
    permutations = rpermutation


@unittest.skipUnless(struct, 'struct module required kila this test.')
@unittest.skipUnless(ndarray, 'ndarray object required kila this test')
kundi TestBufferProtocol(unittest.TestCase):

    eleza setUp(self):
        # The suboffsets tests need sizeof(void *).
        self.sizeof_void_p = get_sizeof_void_p()

    eleza verify(self, result, *, obj,
                     itemsize, fmt, readonly,
                     ndim, shape, strides,
                     lst, sliced=Uongo, cast=Uongo):
        # Verify buffer contents against expected values.
        ikiwa shape:
            expected_len = prod(shape)*itemsize
        isipokua:
            ikiwa sio fmt: # array has been implicitly cast to unsigned bytes
                expected_len = len(lst)
            isipokua: # ndim = 0
                expected_len = itemsize

        # Reconstruct suboffsets kutoka strides. Support kila slicing
        # could be added, but ni currently only needed kila test_getbuf().
        suboffsets = ()
        ikiwa result.suboffsets:
            self.assertGreater(ndim, 0)

            suboffset0 = 0
            kila n kwenye range(1, ndim):
                ikiwa shape[n] == 0:
                    koma
                ikiwa strides[n] <= 0:
                    suboffset0 += -strides[n] * (shape[n]-1)

            suboffsets = [suboffset0] + [-1 kila v kwenye range(ndim-1)]

            # Not correct ikiwa slicing has occurred kwenye the first dimension.
            stride0 = self.sizeof_void_p
            ikiwa strides[0] < 0:
                stride0 = -stride0
            strides = [stride0] + list(strides[1:])

        self.assertIs(result.obj, obj)
        self.assertEqual(result.nbytes, expected_len)
        self.assertEqual(result.itemsize, itemsize)
        self.assertEqual(result.format, fmt)
        self.assertIs(result.readonly, readonly)
        self.assertEqual(result.ndim, ndim)
        self.assertEqual(result.shape, tuple(shape))
        ikiwa sio (sliced na suboffsets):
            self.assertEqual(result.strides, tuple(strides))
        self.assertEqual(result.suboffsets, tuple(suboffsets))

        ikiwa isinstance(result, ndarray) ama is_memoryview_format(fmt):
            rep = result.tolist() ikiwa fmt isipokua result.tobytes()
            self.assertEqual(rep, lst)

        ikiwa sio fmt: # array has been cast to unsigned bytes,
            rudisha  # the remaining tests won't work.

        # PyBuffer_GetPointer() ni the definition how to access an item.
        # If PyBuffer_GetPointer(indices) ni correct kila all possible
        # combinations of indices, the buffer ni correct.
        #
        # Also test tobytes() against the flattened 'lst', ukijumuisha all items
        # packed to bytes.
        ikiwa sio cast: # casts chop up 'lst' kwenye different ways
            b = bytearray()
            buf_err = Tupu
            kila ind kwenye indices(shape):
                jaribu:
                    item1 = get_pointer(result, ind)
                    item2 = get_item(lst, ind)
                    ikiwa isinstance(item2, tuple):
                        x = struct.pack(fmt, *item2)
                    isipokua:
                        x = struct.pack(fmt, item2)
                    b.extend(x)
                tatizo BufferError:
                    buf_err = Kweli # re-exporter does sio provide full buffer
                    koma
                self.assertEqual(item1, item2)

            ikiwa sio buf_err:
                # test tobytes()
                self.assertEqual(result.tobytes(), b)

                # test hex()
                m = memoryview(result)
                h = "".join("%02x" % c kila c kwenye b)
                self.assertEqual(m.hex(), h)

                # lst := expected multi-dimensional logical representation
                # flatten(lst) := elements kwenye C-order
                ff = fmt ikiwa fmt isipokua 'B'
                flattened = flatten(lst)

                # Rules kila 'A': ikiwa the array ni already contiguous, rudisha
                # the array unaltered. Otherwise, rudisha a contiguous 'C'
                # representation.
                kila order kwenye ['C', 'F', 'A']:
                    expected = result
                    ikiwa order == 'F':
                        ikiwa sio is_contiguous(result, 'A') ama \
                           is_contiguous(result, 'C'):
                            # For constructing the ndarray, convert the
                            # flattened logical representation to Fortran order.
                            trans = transpose(flattened, shape)
                            expected = ndarray(trans, shape=shape, format=ff,
                                               flags=ND_FORTRAN)
                    isipokua: # 'C', 'A'
                        ikiwa sio is_contiguous(result, 'A') ama \
                           is_contiguous(result, 'F') na order == 'C':
                            # The flattened list ni already kwenye C-order.
                            expected = ndarray(flattened, shape=shape, format=ff)

                    contig = get_contiguous(result, PyBUF_READ, order)
                    self.assertEqual(contig.tobytes(), b)
                    self.assertKweli(cmp_contig(contig, expected))

                    ikiwa ndim == 0:
                        endelea

                    nmemb = len(flattened)
                    ro = 0 ikiwa readonly isipokua ND_WRITABLE

                    ### See comment kwenye test_py_buffer_to_contiguous kila an
                    ### explanation why these tests are valid.

                    # To 'C'
                    contig = py_buffer_to_contiguous(result, 'C', PyBUF_FULL_RO)
                    self.assertEqual(len(contig), nmemb * itemsize)
                    initlst = [struct.unpack_from(fmt, contig, n*itemsize)
                               kila n kwenye range(nmemb)]
                    ikiwa len(initlst[0]) == 1:
                        initlst = [v[0] kila v kwenye initlst]

                    y = ndarray(initlst, shape=shape, flags=ro, format=fmt)
                    self.assertEqual(memoryview(y), memoryview(result))

                    contig_bytes = memoryview(result).tobytes()
                    self.assertEqual(contig_bytes, contig)

                    contig_bytes = memoryview(result).tobytes(order=Tupu)
                    self.assertEqual(contig_bytes, contig)

                    contig_bytes = memoryview(result).tobytes(order='C')
                    self.assertEqual(contig_bytes, contig)

                    # To 'F'
                    contig = py_buffer_to_contiguous(result, 'F', PyBUF_FULL_RO)
                    self.assertEqual(len(contig), nmemb * itemsize)
                    initlst = [struct.unpack_from(fmt, contig, n*itemsize)
                               kila n kwenye range(nmemb)]
                    ikiwa len(initlst[0]) == 1:
                        initlst = [v[0] kila v kwenye initlst]

                    y = ndarray(initlst, shape=shape, flags=ro|ND_FORTRAN,
                                format=fmt)
                    self.assertEqual(memoryview(y), memoryview(result))

                    contig_bytes = memoryview(result).tobytes(order='F')
                    self.assertEqual(contig_bytes, contig)

                    # To 'A'
                    contig = py_buffer_to_contiguous(result, 'A', PyBUF_FULL_RO)
                    self.assertEqual(len(contig), nmemb * itemsize)
                    initlst = [struct.unpack_from(fmt, contig, n*itemsize)
                               kila n kwenye range(nmemb)]
                    ikiwa len(initlst[0]) == 1:
                        initlst = [v[0] kila v kwenye initlst]

                    f = ND_FORTRAN ikiwa is_contiguous(result, 'F') isipokua 0
                    y = ndarray(initlst, shape=shape, flags=f|ro, format=fmt)
                    self.assertEqual(memoryview(y), memoryview(result))

                    contig_bytes = memoryview(result).tobytes(order='A')
                    self.assertEqual(contig_bytes, contig)

        ikiwa is_memoryview_format(fmt):
            jaribu:
                m = memoryview(result)
            tatizo BufferError: # re-exporter does sio provide full information
                rudisha
            ex = result.obj ikiwa isinstance(result, memoryview) isipokua result

            eleza check_memoryview(m, expected_readonly=readonly):
                self.assertIs(m.obj, ex)
                self.assertEqual(m.nbytes, expected_len)
                self.assertEqual(m.itemsize, itemsize)
                self.assertEqual(m.format, fmt)
                self.assertEqual(m.readonly, expected_readonly)
                self.assertEqual(m.ndim, ndim)
                self.assertEqual(m.shape, tuple(shape))
                ikiwa sio (sliced na suboffsets):
                    self.assertEqual(m.strides, tuple(strides))
                self.assertEqual(m.suboffsets, tuple(suboffsets))

                n = 1 ikiwa ndim == 0 isipokua len(lst)
                self.assertEqual(len(m), n)

                rep = result.tolist() ikiwa fmt isipokua result.tobytes()
                self.assertEqual(rep, lst)
                self.assertEqual(m, result)

            check_memoryview(m)
            ukijumuisha m.toreadonly() kama mm:
                check_memoryview(mm, expected_readonly=Kweli)
            m.tobytes()  # Releasing mm didn't release m

    eleza verify_getbuf(self, orig_ex, ex, req, sliced=Uongo):
        eleza simple_fmt(ex):
            rudisha ex.format == '' ama ex.format == 'B'
        eleza match(req, flag):
            rudisha ((req&flag) == flag)

        ikiwa (# writable request to read-only exporter
            (ex.readonly na match(req, PyBUF_WRITABLE)) ama
            # cannot match explicit contiguity request
            (match(req, PyBUF_C_CONTIGUOUS) na sio ex.c_contiguous) ama
            (match(req, PyBUF_F_CONTIGUOUS) na sio ex.f_contiguous) ama
            (match(req, PyBUF_ANY_CONTIGUOUS) na sio ex.contiguous) ama
            # buffer needs suboffsets
            (sio match(req, PyBUF_INDIRECT) na ex.suboffsets) ama
            # buffer without strides must be C-contiguous
            (sio match(req, PyBUF_STRIDES) na sio ex.c_contiguous) ama
            # PyBUF_SIMPLE|PyBUF_FORMAT na PyBUF_WRITABLE|PyBUF_FORMAT
            (sio match(req, PyBUF_ND) na match(req, PyBUF_FORMAT))):

            self.assertRaises(BufferError, ndarray, ex, getbuf=req)
            rudisha

        ikiwa isinstance(ex, ndarray) ama is_memoryview_format(ex.format):
            lst = ex.tolist()
        isipokua:
            nd = ndarray(ex, getbuf=PyBUF_FULL_RO)
            lst = nd.tolist()

        # The consumer may have requested default values ama a NULL format.
        ro = Uongo ikiwa match(req, PyBUF_WRITABLE) isipokua ex.readonly
        fmt = ex.format
        itemsize = ex.itemsize
        ndim = ex.ndim
        ikiwa sio match(req, PyBUF_FORMAT):
            # itemsize refers to the original itemsize before the cast.
            # The equality product(shape) * itemsize = len still holds.
            # The equality calcsize(format) = itemsize does _not_ hold.
            fmt = ''
            lst = orig_ex.tobytes() # Issue 12834
        ikiwa sio match(req, PyBUF_ND):
            ndim = 1
        shape = orig_ex.shape ikiwa match(req, PyBUF_ND) isipokua ()
        strides = orig_ex.strides ikiwa match(req, PyBUF_STRIDES) isipokua ()

        nd = ndarray(ex, getbuf=req)
        self.verify(nd, obj=ex,
                    itemsize=itemsize, fmt=fmt, readonly=ro,
                    ndim=ndim, shape=shape, strides=strides,
                    lst=lst, sliced=sliced)

    eleza test_ndarray_getbuf(self):
        requests = (
            # distinct flags
            PyBUF_INDIRECT, PyBUF_STRIDES, PyBUF_ND, PyBUF_SIMPLE,
            PyBUF_C_CONTIGUOUS, PyBUF_F_CONTIGUOUS, PyBUF_ANY_CONTIGUOUS,
            # compound requests
            PyBUF_FULL, PyBUF_FULL_RO,
            PyBUF_RECORDS, PyBUF_RECORDS_RO,
            PyBUF_STRIDED, PyBUF_STRIDED_RO,
            PyBUF_CONTIG, PyBUF_CONTIG_RO,
        )
        # items na format
        items_fmt = (
            ([Kweli ikiwa x % 2 isipokua Uongo kila x kwenye range(12)], '?'),
            ([1,2,3,4,5,6,7,8,9,10,11,12], 'b'),
            ([1,2,3,4,5,6,7,8,9,10,11,12], 'B'),
            ([(2**31-x) ikiwa x % 2 isipokua (-2**31+x) kila x kwenye range(12)], 'l')
        )
        # shape, strides, offset
        structure = (
            ([], [], 0),
            ([1,3,1], [], 0),
            ([12], [], 0),
            ([12], [-1], 11),
            ([6], [2], 0),
            ([6], [-2], 11),
            ([3, 4], [], 0),
            ([3, 4], [-4, -1], 11),
            ([2, 2], [4, 1], 4),
            ([2, 2], [-4, -1], 8)
        )
        # ndarray creation flags
        ndflags = (
            0, ND_WRITABLE, ND_FORTRAN, ND_FORTRAN|ND_WRITABLE,
            ND_PIL, ND_PIL|ND_WRITABLE
        )
        # flags that can actually be used kama flags
        real_flags = (0, PyBUF_WRITABLE, PyBUF_FORMAT,
                      PyBUF_WRITABLE|PyBUF_FORMAT)

        kila items, fmt kwenye items_fmt:
            itemsize = struct.calcsize(fmt)
            kila shape, strides, offset kwenye structure:
                strides = [v * itemsize kila v kwenye strides]
                offset *= itemsize
                kila flags kwenye ndflags:

                    ikiwa strides na (flags&ND_FORTRAN):
                        endelea
                    ikiwa sio shape na (flags&ND_PIL):
                        endelea

                    _items = items ikiwa shape isipokua items[0]
                    ex1 = ndarray(_items, format=fmt, flags=flags,
                                  shape=shape, strides=strides, offset=offset)
                    ex2 = ex1[::-2] ikiwa shape isipokua Tupu

                    m1 = memoryview(ex1)
                    ikiwa ex2:
                        m2 = memoryview(ex2)
                    ikiwa ex1.ndim == 0 ama (ex1.ndim == 1 na shape na strides):
                        self.assertEqual(m1, ex1)
                    ikiwa ex2 na ex2.ndim == 1 na shape na strides:
                        self.assertEqual(m2, ex2)

                    kila req kwenye requests:
                        kila bits kwenye real_flags:
                            self.verify_getbuf(ex1, ex1, req|bits)
                            self.verify_getbuf(ex1, m1, req|bits)
                            ikiwa ex2:
                                self.verify_getbuf(ex2, ex2, req|bits,
                                                   sliced=Kweli)
                                self.verify_getbuf(ex2, m2, req|bits,
                                                   sliced=Kweli)

        items = [1,2,3,4,5,6,7,8,9,10,11,12]

        # ND_GETBUF_FAIL
        ex = ndarray(items, shape=[12], flags=ND_GETBUF_FAIL)
        self.assertRaises(BufferError, ndarray, ex)

        # Request complex structure kutoka a simple exporter. In this
        # particular case the test object ni sio PEP-3118 compliant.
        base = ndarray([9], [1])
        ex = ndarray(base, getbuf=PyBUF_SIMPLE)
        self.assertRaises(BufferError, ndarray, ex, getbuf=PyBUF_WRITABLE)
        self.assertRaises(BufferError, ndarray, ex, getbuf=PyBUF_ND)
        self.assertRaises(BufferError, ndarray, ex, getbuf=PyBUF_STRIDES)
        self.assertRaises(BufferError, ndarray, ex, getbuf=PyBUF_C_CONTIGUOUS)
        self.assertRaises(BufferError, ndarray, ex, getbuf=PyBUF_F_CONTIGUOUS)
        self.assertRaises(BufferError, ndarray, ex, getbuf=PyBUF_ANY_CONTIGUOUS)
        nd = ndarray(ex, getbuf=PyBUF_SIMPLE)

        # Issue #22445: New precise contiguity definition.
        kila shape kwenye [1,12,1], [7,0,7]:
            kila order kwenye 0, ND_FORTRAN:
                ex = ndarray(items, shape=shape, flags=order|ND_WRITABLE)
                self.assertKweli(is_contiguous(ex, 'F'))
                self.assertKweli(is_contiguous(ex, 'C'))

                kila flags kwenye requests:
                    nd = ndarray(ex, getbuf=flags)
                    self.assertKweli(is_contiguous(nd, 'F'))
                    self.assertKweli(is_contiguous(nd, 'C'))

    eleza test_ndarray_exceptions(self):
        nd = ndarray([9], [1])
        ndm = ndarray([9], [1], flags=ND_VAREXPORT)

        # Initialization of a new ndarray ama mutation of an existing array.
        kila c kwenye (ndarray, nd.push, ndm.push):
            # Invalid types.
            self.assertRaises(TypeError, c, {1,2,3})
            self.assertRaises(TypeError, c, [1,2,'3'])
            self.assertRaises(TypeError, c, [1,2,(3,4)])
            self.assertRaises(TypeError, c, [1,2,3], shape={3})
            self.assertRaises(TypeError, c, [1,2,3], shape=[3], strides={1})
            self.assertRaises(TypeError, c, [1,2,3], shape=[3], offset=[])
            self.assertRaises(TypeError, c, [1], shape=[1], format={})
            self.assertRaises(TypeError, c, [1], shape=[1], flags={})
            self.assertRaises(TypeError, c, [1], shape=[1], getbuf={})

            # ND_FORTRAN flag ni only valid without strides.
            self.assertRaises(TypeError, c, [1], shape=[1], strides=[1],
                              flags=ND_FORTRAN)

            # ND_PIL flag ni only valid ukijumuisha ndim > 0.
            self.assertRaises(TypeError, c, [1], shape=[], flags=ND_PIL)

            # Invalid items.
            self.assertRaises(ValueError, c, [], shape=[1])
            self.assertRaises(ValueError, c, ['XXX'], shape=[1], format="L")
            # Invalid combination of items na format.
            self.assertRaises(struct.error, c, [1000], shape=[1], format="B")
            self.assertRaises(ValueError, c, [1,(2,3)], shape=[2], format="B")
            self.assertRaises(ValueError, c, [1,2,3], shape=[3], format="QL")

            # Invalid ndim.
            n = ND_MAX_NDIM+1
            self.assertRaises(ValueError, c, [1]*n, shape=[1]*n)

            # Invalid shape.
            self.assertRaises(ValueError, c, [1], shape=[-1])
            self.assertRaises(ValueError, c, [1,2,3], shape=['3'])
            self.assertRaises(OverflowError, c, [1], shape=[2**128])
            # prod(shape) * itemsize != len(items)
            self.assertRaises(ValueError, c, [1,2,3,4,5], shape=[2,2], offset=3)

            # Invalid strides.
            self.assertRaises(ValueError, c, [1,2,3], shape=[3], strides=['1'])
            self.assertRaises(OverflowError, c, [1], shape=[1],
                              strides=[2**128])

            # Invalid combination of strides na shape.
            self.assertRaises(ValueError, c, [1,2], shape=[2,1], strides=[1])
            # Invalid combination of strides na format.
            self.assertRaises(ValueError, c, [1,2,3,4], shape=[2], strides=[3],
                              format="L")

            # Invalid offset.
            self.assertRaises(ValueError, c, [1,2,3], shape=[3], offset=4)
            self.assertRaises(ValueError, c, [1,2,3], shape=[1], offset=3,
                              format="L")

            # Invalid format.
            self.assertRaises(ValueError, c, [1,2,3], shape=[3], format="")
            self.assertRaises(struct.error, c, [(1,2,3)], shape=[1],
                              format="@#$")

            # Striding out of the memory bounds.
            items = [1,2,3,4,5,6,7,8,9,10]
            self.assertRaises(ValueError, c, items, shape=[2,3],
                              strides=[-3, -2], offset=5)

            # Constructing consumer: format argument invalid.
            self.assertRaises(TypeError, c, bytearray(), format="Q")

            # Constructing original base object: getbuf argument invalid.
            self.assertRaises(TypeError, c, [1], shape=[1], getbuf=PyBUF_FULL)

            # Shape argument ni mandatory kila original base objects.
            self.assertRaises(TypeError, c, [1])


        # PyBUF_WRITABLE request to read-only provider.
        self.assertRaises(BufferError, ndarray, b'123', getbuf=PyBUF_WRITABLE)

        # ND_VAREXPORT can only be specified during construction.
        nd = ndarray([9], [1], flags=ND_VAREXPORT)
        self.assertRaises(ValueError, nd.push, [1], [1], flags=ND_VAREXPORT)

        # Invalid operation kila consumers: push/pop
        nd = ndarray(b'123')
        self.assertRaises(BufferError, nd.push, [1], [1])
        self.assertRaises(BufferError, nd.pop)

        # ND_VAREXPORT sio set: push/pop fail ukijumuisha exported buffers
        nd = ndarray([9], [1])
        nd.push([1], [1])
        m = memoryview(nd)
        self.assertRaises(BufferError, nd.push, [1], [1])
        self.assertRaises(BufferError, nd.pop)
        m.release()
        nd.pop()

        # Single remaining buffer: pop fails
        self.assertRaises(BufferError, nd.pop)
        toa nd

        # get_pointer()
        self.assertRaises(TypeError, get_pointer, {}, [1,2,3])
        self.assertRaises(TypeError, get_pointer, b'123', {})

        nd = ndarray(list(range(100)), shape=[1]*100)
        self.assertRaises(ValueError, get_pointer, nd, [5])

        nd = ndarray(list(range(12)), shape=[3,4])
        self.assertRaises(ValueError, get_pointer, nd, [2,3,4])
        self.assertRaises(ValueError, get_pointer, nd, [3,3])
        self.assertRaises(ValueError, get_pointer, nd, [-3,3])
        self.assertRaises(OverflowError, get_pointer, nd, [1<<64,3])

        # tolist() needs format
        ex = ndarray([1,2,3], shape=[3], format='L')
        nd = ndarray(ex, getbuf=PyBUF_SIMPLE)
        self.assertRaises(ValueError, nd.tolist)

        # memoryview_from_buffer()
        ex1 = ndarray([1,2,3], shape=[3], format='L')
        ex2 = ndarray(ex1)
        nd = ndarray(ex2)
        self.assertRaises(TypeError, nd.memoryview_from_buffer)

        nd = ndarray([(1,)*200], shape=[1], format='L'*200)
        self.assertRaises(TypeError, nd.memoryview_from_buffer)

        n = ND_MAX_NDIM
        nd = ndarray(list(range(n)), shape=[1]*n)
        self.assertRaises(ValueError, nd.memoryview_from_buffer)

        # get_contiguous()
        nd = ndarray([1], shape=[1])
        self.assertRaises(TypeError, get_contiguous, 1, 2, 3, 4, 5)
        self.assertRaises(TypeError, get_contiguous, nd, "xyz", 'C')
        self.assertRaises(OverflowError, get_contiguous, nd, 2**64, 'C')
        self.assertRaises(TypeError, get_contiguous, nd, PyBUF_READ, 961)
        self.assertRaises(UnicodeEncodeError, get_contiguous, nd, PyBUF_READ,
                          '\u2007')
        self.assertRaises(ValueError, get_contiguous, nd, PyBUF_READ, 'Z')
        self.assertRaises(ValueError, get_contiguous, nd, 255, 'A')

        # cmp_contig()
        nd = ndarray([1], shape=[1])
        self.assertRaises(TypeError, cmp_contig, 1, 2, 3, 4, 5)
        self.assertRaises(TypeError, cmp_contig, {}, nd)
        self.assertRaises(TypeError, cmp_contig, nd, {})

        # is_contiguous()
        nd = ndarray([1], shape=[1])
        self.assertRaises(TypeError, is_contiguous, 1, 2, 3, 4, 5)
        self.assertRaises(TypeError, is_contiguous, {}, 'A')
        self.assertRaises(TypeError, is_contiguous, nd, 201)

    eleza test_ndarray_linked_list(self):
        kila perm kwenye permutations(range(5)):
            m = [0]*5
            nd = ndarray([1,2,3], shape=[3], flags=ND_VAREXPORT)
            m[0] = memoryview(nd)

            kila i kwenye range(1, 5):
                nd.push([1,2,3], shape=[3])
                m[i] = memoryview(nd)

            kila i kwenye range(5):
                m[perm[i]].release()

            self.assertRaises(BufferError, nd.pop)
            toa nd

    eleza test_ndarray_format_scalar(self):
        # ndim = 0: scalar
        kila fmt, scalar, _ kwenye iter_format(0):
            itemsize = struct.calcsize(fmt)
            nd = ndarray(scalar, shape=(), format=fmt)
            self.verify(nd, obj=Tupu,
                        itemsize=itemsize, fmt=fmt, readonly=Kweli,
                        ndim=0, shape=(), strides=(),
                        lst=scalar)

    eleza test_ndarray_format_shape(self):
        # ndim = 1, shape = [n]
        nitems =  randrange(1, 10)
        kila fmt, items, _ kwenye iter_format(nitems):
            itemsize = struct.calcsize(fmt)
            kila flags kwenye (0, ND_PIL):
                nd = ndarray(items, shape=[nitems], format=fmt, flags=flags)
                self.verify(nd, obj=Tupu,
                            itemsize=itemsize, fmt=fmt, readonly=Kweli,
                            ndim=1, shape=(nitems,), strides=(itemsize,),
                            lst=items)

    eleza test_ndarray_format_strides(self):
        # ndim = 1, strides
        nitems = randrange(1, 30)
        kila fmt, items, _ kwenye iter_format(nitems):
            itemsize = struct.calcsize(fmt)
            kila step kwenye range(-5, 5):
                ikiwa step == 0:
                    endelea

                shape = [len(items[::step])]
                strides = [step*itemsize]
                offset = itemsize*(nitems-1) ikiwa step < 0 isipokua 0

                kila flags kwenye (0, ND_PIL):
                    nd = ndarray(items, shape=shape, strides=strides,
                                 format=fmt, offset=offset, flags=flags)
                    self.verify(nd, obj=Tupu,
                                itemsize=itemsize, fmt=fmt, readonly=Kweli,
                                ndim=1, shape=shape, strides=strides,
                                lst=items[::step])

    eleza test_ndarray_fortran(self):
        items = [1,2,3,4,5,6,7,8,9,10,11,12]
        ex = ndarray(items, shape=(3, 4), strides=(1, 3))
        nd = ndarray(ex, getbuf=PyBUF_F_CONTIGUOUS|PyBUF_FORMAT)
        self.assertEqual(nd.tolist(), farray(items, (3, 4)))

    eleza test_ndarray_multidim(self):
        kila ndim kwenye range(5):
            shape_t = [randrange(2, 10) kila _ kwenye range(ndim)]
            nitems = prod(shape_t)
            kila shape kwenye permutations(shape_t):

                fmt, items, _ = randitems(nitems)
                itemsize = struct.calcsize(fmt)

                kila flags kwenye (0, ND_PIL):
                    ikiwa ndim == 0 na flags == ND_PIL:
                        endelea

                    # C array
                    nd = ndarray(items, shape=shape, format=fmt, flags=flags)

                    strides = strides_from_shape(ndim, shape, itemsize, 'C')
                    lst = carray(items, shape)
                    self.verify(nd, obj=Tupu,
                                itemsize=itemsize, fmt=fmt, readonly=Kweli,
                                ndim=ndim, shape=shape, strides=strides,
                                lst=lst)

                    ikiwa is_memoryview_format(fmt):
                        # memoryview: reconstruct strides
                        ex = ndarray(items, shape=shape, format=fmt)
                        nd = ndarray(ex, getbuf=PyBUF_CONTIG_RO|PyBUF_FORMAT)
                        self.assertKweli(nd.strides == ())
                        mv = nd.memoryview_from_buffer()
                        self.verify(mv, obj=Tupu,
                                    itemsize=itemsize, fmt=fmt, readonly=Kweli,
                                    ndim=ndim, shape=shape, strides=strides,
                                    lst=lst)

                    # Fortran array
                    nd = ndarray(items, shape=shape, format=fmt,
                                 flags=flags|ND_FORTRAN)

                    strides = strides_from_shape(ndim, shape, itemsize, 'F')
                    lst = farray(items, shape)
                    self.verify(nd, obj=Tupu,
                                itemsize=itemsize, fmt=fmt, readonly=Kweli,
                                ndim=ndim, shape=shape, strides=strides,
                                lst=lst)

    eleza test_ndarray_index_invalid(self):
        # sio writable
        nd = ndarray([1], shape=[1])
        self.assertRaises(TypeError, nd.__setitem__, 1, 8)
        mv = memoryview(nd)
        self.assertEqual(mv, nd)
        self.assertRaises(TypeError, mv.__setitem__, 1, 8)

        # cannot be deleted
        nd = ndarray([1], shape=[1], flags=ND_WRITABLE)
        self.assertRaises(TypeError, nd.__delitem__, 1)
        mv = memoryview(nd)
        self.assertEqual(mv, nd)
        self.assertRaises(TypeError, mv.__delitem__, 1)

        # overflow
        nd = ndarray([1], shape=[1], flags=ND_WRITABLE)
        self.assertRaises(OverflowError, nd.__getitem__, 1<<64)
        self.assertRaises(OverflowError, nd.__setitem__, 1<<64, 8)
        mv = memoryview(nd)
        self.assertEqual(mv, nd)
        self.assertRaises(IndexError, mv.__getitem__, 1<<64)
        self.assertRaises(IndexError, mv.__setitem__, 1<<64, 8)

        # format
        items = [1,2,3,4,5,6,7,8]
        nd = ndarray(items, shape=[len(items)], format="B", flags=ND_WRITABLE)
        self.assertRaises(struct.error, nd.__setitem__, 2, 300)
        self.assertRaises(ValueError, nd.__setitem__, 1, (100, 200))
        mv = memoryview(nd)
        self.assertEqual(mv, nd)
        self.assertRaises(ValueError, mv.__setitem__, 2, 300)
        self.assertRaises(TypeError, mv.__setitem__, 1, (100, 200))

        items = [(1,2), (3,4), (5,6)]
        nd = ndarray(items, shape=[len(items)], format="LQ", flags=ND_WRITABLE)
        self.assertRaises(ValueError, nd.__setitem__, 2, 300)
        self.assertRaises(struct.error, nd.__setitem__, 1, (b'\x001', 200))

    eleza test_ndarray_index_scalar(self):
        # scalar
        nd = ndarray(1, shape=(), flags=ND_WRITABLE)
        mv = memoryview(nd)
        self.assertEqual(mv, nd)

        x = nd[()];  self.assertEqual(x, 1)
        x = nd[...]; self.assertEqual(x.tolist(), nd.tolist())

        x = mv[()];  self.assertEqual(x, 1)
        x = mv[...]; self.assertEqual(x.tolist(), nd.tolist())

        self.assertRaises(TypeError, nd.__getitem__, 0)
        self.assertRaises(TypeError, mv.__getitem__, 0)
        self.assertRaises(TypeError, nd.__setitem__, 0, 8)
        self.assertRaises(TypeError, mv.__setitem__, 0, 8)

        self.assertEqual(nd.tolist(), 1)
        self.assertEqual(mv.tolist(), 1)

        nd[()] = 9; self.assertEqual(nd.tolist(), 9)
        mv[()] = 9; self.assertEqual(mv.tolist(), 9)

        nd[...] = 5; self.assertEqual(nd.tolist(), 5)
        mv[...] = 5; self.assertEqual(mv.tolist(), 5)

    eleza test_ndarray_index_null_strides(self):
        ex = ndarray(list(range(2*4)), shape=[2, 4], flags=ND_WRITABLE)
        nd = ndarray(ex, getbuf=PyBUF_CONTIG)

        # Sub-views are only possible kila full exporters.
        self.assertRaises(BufferError, nd.__getitem__, 1)
        # Same kila slices.
        self.assertRaises(BufferError, nd.__getitem__, slice(3,5,1))

    eleza test_ndarray_index_getitem_single(self):
        # getitem
        kila fmt, items, _ kwenye iter_format(5):
            nd = ndarray(items, shape=[5], format=fmt)
            kila i kwenye range(-5, 5):
                self.assertEqual(nd[i], items[i])

            self.assertRaises(IndexError, nd.__getitem__, -6)
            self.assertRaises(IndexError, nd.__getitem__, 5)

            ikiwa is_memoryview_format(fmt):
                mv = memoryview(nd)
                self.assertEqual(mv, nd)
                kila i kwenye range(-5, 5):
                    self.assertEqual(mv[i], items[i])

                self.assertRaises(IndexError, mv.__getitem__, -6)
                self.assertRaises(IndexError, mv.__getitem__, 5)

        # getitem ukijumuisha null strides
        kila fmt, items, _ kwenye iter_format(5):
            ex = ndarray(items, shape=[5], flags=ND_WRITABLE, format=fmt)
            nd = ndarray(ex, getbuf=PyBUF_CONTIG|PyBUF_FORMAT)

            kila i kwenye range(-5, 5):
                self.assertEqual(nd[i], items[i])

            ikiwa is_memoryview_format(fmt):
                mv = nd.memoryview_from_buffer()
                self.assertIs(mv.__eq__(nd), NotImplemented)
                kila i kwenye range(-5, 5):
                    self.assertEqual(mv[i], items[i])

        # getitem ukijumuisha null format
        items = [1,2,3,4,5]
        ex = ndarray(items, shape=[5])
        nd = ndarray(ex, getbuf=PyBUF_CONTIG_RO)
        kila i kwenye range(-5, 5):
            self.assertEqual(nd[i], items[i])

        # getitem ukijumuisha null shape/strides/format
        items = [1,2,3,4,5]
        ex = ndarray(items, shape=[5])
        nd = ndarray(ex, getbuf=PyBUF_SIMPLE)

        kila i kwenye range(-5, 5):
            self.assertEqual(nd[i], items[i])

    eleza test_ndarray_index_setitem_single(self):
        # assign single value
        kila fmt, items, single_item kwenye iter_format(5):
            nd = ndarray(items, shape=[5], format=fmt, flags=ND_WRITABLE)
            kila i kwenye range(5):
                items[i] = single_item
                nd[i] = single_item
            self.assertEqual(nd.tolist(), items)

            self.assertRaises(IndexError, nd.__setitem__, -6, single_item)
            self.assertRaises(IndexError, nd.__setitem__, 5, single_item)

            ikiwa sio is_memoryview_format(fmt):
                endelea

            nd = ndarray(items, shape=[5], format=fmt, flags=ND_WRITABLE)
            mv = memoryview(nd)
            self.assertEqual(mv, nd)
            kila i kwenye range(5):
                items[i] = single_item
                mv[i] = single_item
            self.assertEqual(mv.tolist(), items)

            self.assertRaises(IndexError, mv.__setitem__, -6, single_item)
            self.assertRaises(IndexError, mv.__setitem__, 5, single_item)


        # assign single value: lobject = robject
        kila fmt, items, single_item kwenye iter_format(5):
            nd = ndarray(items, shape=[5], format=fmt, flags=ND_WRITABLE)
            kila i kwenye range(-5, 4):
                items[i] = items[i+1]
                nd[i] = nd[i+1]
            self.assertEqual(nd.tolist(), items)

            ikiwa sio is_memoryview_format(fmt):
                endelea

            nd = ndarray(items, shape=[5], format=fmt, flags=ND_WRITABLE)
            mv = memoryview(nd)
            self.assertEqual(mv, nd)
            kila i kwenye range(-5, 4):
                items[i] = items[i+1]
                mv[i] = mv[i+1]
            self.assertEqual(mv.tolist(), items)

    eleza test_ndarray_index_getitem_multidim(self):
        shape_t = (2, 3, 5)
        nitems = prod(shape_t)
        kila shape kwenye permutations(shape_t):

            fmt, items, _ = randitems(nitems)

            kila flags kwenye (0, ND_PIL):
                # C array
                nd = ndarray(items, shape=shape, format=fmt, flags=flags)
                lst = carray(items, shape)

                kila i kwenye range(-shape[0], shape[0]):
                    self.assertEqual(lst[i], nd[i].tolist())
                    kila j kwenye range(-shape[1], shape[1]):
                        self.assertEqual(lst[i][j], nd[i][j].tolist())
                        kila k kwenye range(-shape[2], shape[2]):
                            self.assertEqual(lst[i][j][k], nd[i][j][k])

                # Fortran array
                nd = ndarray(items, shape=shape, format=fmt,
                             flags=flags|ND_FORTRAN)
                lst = farray(items, shape)

                kila i kwenye range(-shape[0], shape[0]):
                    self.assertEqual(lst[i], nd[i].tolist())
                    kila j kwenye range(-shape[1], shape[1]):
                        self.assertEqual(lst[i][j], nd[i][j].tolist())
                        kila k kwenye range(shape[2], shape[2]):
                            self.assertEqual(lst[i][j][k], nd[i][j][k])

    eleza test_ndarray_sequence(self):
        nd = ndarray(1, shape=())
        self.assertRaises(TypeError, eval, "1 kwenye nd", locals())
        mv = memoryview(nd)
        self.assertEqual(mv, nd)
        self.assertRaises(TypeError, eval, "1 kwenye mv", locals())

        kila fmt, items, _ kwenye iter_format(5):
            nd = ndarray(items, shape=[5], format=fmt)
            kila i, v kwenye enumerate(nd):
                self.assertEqual(v, items[i])
                self.assertKweli(v kwenye nd)

            ikiwa is_memoryview_format(fmt):
                mv = memoryview(nd)
                kila i, v kwenye enumerate(mv):
                    self.assertEqual(v, items[i])
                    self.assertKweli(v kwenye mv)

    eleza test_ndarray_slice_invalid(self):
        items = [1,2,3,4,5,6,7,8]

        # rvalue ni sio an exporter
        xl = ndarray(items, shape=[8], flags=ND_WRITABLE)
        ml = memoryview(xl)
        self.assertRaises(TypeError, xl.__setitem__, slice(0,8,1), items)
        self.assertRaises(TypeError, ml.__setitem__, slice(0,8,1), items)

        # rvalue ni sio a full exporter
        xl = ndarray(items, shape=[8], flags=ND_WRITABLE)
        ex = ndarray(items, shape=[8], flags=ND_WRITABLE)
        xr = ndarray(ex, getbuf=PyBUF_ND)
        self.assertRaises(BufferError, xl.__setitem__, slice(0,8,1), xr)

        # zero step
        nd = ndarray(items, shape=[8], format="L", flags=ND_WRITABLE)
        mv = memoryview(nd)
        self.assertRaises(ValueError, nd.__getitem__, slice(0,1,0))
        self.assertRaises(ValueError, mv.__getitem__, slice(0,1,0))

        nd = ndarray(items, shape=[2,4], format="L", flags=ND_WRITABLE)
        mv = memoryview(nd)

        self.assertRaises(ValueError, nd.__getitem__,
                          (slice(0,1,1), slice(0,1,0)))
        self.assertRaises(ValueError, nd.__getitem__,
                          (slice(0,1,0), slice(0,1,1)))
        self.assertRaises(TypeError, nd.__getitem__, "@%$")
        self.assertRaises(TypeError, nd.__getitem__, ("@%$", slice(0,1,1)))
        self.assertRaises(TypeError, nd.__getitem__, (slice(0,1,1), {}))

        # memoryview: sio implemented
        self.assertRaises(NotImplementedError, mv.__getitem__,
                          (slice(0,1,1), slice(0,1,0)))
        self.assertRaises(TypeError, mv.__getitem__, "@%$")

        # differing format
        xl = ndarray(items, shape=[8], format="B", flags=ND_WRITABLE)
        xr = ndarray(items, shape=[8], format="b")
        ml = memoryview(xl)
        mr = memoryview(xr)
        self.assertRaises(ValueError, xl.__setitem__, slice(0,1,1), xr[7:8])
        self.assertEqual(xl.tolist(), items)
        self.assertRaises(ValueError, ml.__setitem__, slice(0,1,1), mr[7:8])
        self.assertEqual(ml.tolist(), items)

        # differing itemsize
        xl = ndarray(items, shape=[8], format="B", flags=ND_WRITABLE)
        yr = ndarray(items, shape=[8], format="L")
        ml = memoryview(xl)
        mr = memoryview(xr)
        self.assertRaises(ValueError, xl.__setitem__, slice(0,1,1), xr[7:8])
        self.assertEqual(xl.tolist(), items)
        self.assertRaises(ValueError, ml.__setitem__, slice(0,1,1), mr[7:8])
        self.assertEqual(ml.tolist(), items)

        # differing ndim
        xl = ndarray(items, shape=[2, 4], format="b", flags=ND_WRITABLE)
        xr = ndarray(items, shape=[8], format="b")
        ml = memoryview(xl)
        mr = memoryview(xr)
        self.assertRaises(ValueError, xl.__setitem__, slice(0,1,1), xr[7:8])
        self.assertEqual(xl.tolist(), [[1,2,3,4], [5,6,7,8]])
        self.assertRaises(NotImplementedError, ml.__setitem__, slice(0,1,1),
                          mr[7:8])

        # differing shape
        xl = ndarray(items, shape=[8], format="b", flags=ND_WRITABLE)
        xr = ndarray(items, shape=[8], format="b")
        ml = memoryview(xl)
        mr = memoryview(xr)
        self.assertRaises(ValueError, xl.__setitem__, slice(0,2,1), xr[7:8])
        self.assertEqual(xl.tolist(), items)
        self.assertRaises(ValueError, ml.__setitem__, slice(0,2,1), mr[7:8])
        self.assertEqual(ml.tolist(), items)

        # _testbuffer.c module functions
        self.assertRaises(TypeError, slice_indices, slice(0,1,2), {})
        self.assertRaises(TypeError, slice_indices, "###########", 1)
        self.assertRaises(ValueError, slice_indices, slice(0,1,0), 4)

        x = ndarray(items, shape=[8], format="b", flags=ND_PIL)
        self.assertRaises(TypeError, x.add_suboffsets)

        ex = ndarray(items, shape=[8], format="B")
        x = ndarray(ex, getbuf=PyBUF_SIMPLE)
        self.assertRaises(TypeError, x.add_suboffsets)

    eleza test_ndarray_slice_zero_shape(self):
        items = [1,2,3,4,5,6,7,8,9,10,11,12]

        x = ndarray(items, shape=[12], format="L", flags=ND_WRITABLE)
        y = ndarray(items, shape=[12], format="L")
        x[4:4] = y[9:9]
        self.assertEqual(x.tolist(), items)

        ml = memoryview(x)
        mr = memoryview(y)
        self.assertEqual(ml, x)
        self.assertEqual(ml, y)
        ml[4:4] = mr[9:9]
        self.assertEqual(ml.tolist(), items)

        x = ndarray(items, shape=[3, 4], format="L", flags=ND_WRITABLE)
        y = ndarray(items, shape=[4, 3], format="L")
        x[1:2, 2:2] = y[1:2, 3:3]
        self.assertEqual(x.tolist(), carray(items, [3, 4]))

    eleza test_ndarray_slice_multidim(self):
        shape_t = (2, 3, 5)
        ndim = len(shape_t)
        nitems = prod(shape_t)
        kila shape kwenye permutations(shape_t):

            fmt, items, _ = randitems(nitems)
            itemsize = struct.calcsize(fmt)

            kila flags kwenye (0, ND_PIL):
                nd = ndarray(items, shape=shape, format=fmt, flags=flags)
                lst = carray(items, shape)

                kila slices kwenye rslices_ndim(ndim, shape):

                    listerr = Tupu
                    jaribu:
                        sliced = multislice(lst, slices)
                    tatizo Exception kama e:
                        listerr = e.__class__

                    nderr = Tupu
                    jaribu:
                        ndsliced = nd[slices]
                    tatizo Exception kama e:
                        nderr = e.__class__

                    ikiwa nderr ama listerr:
                        self.assertIs(nderr, listerr)
                    isipokua:
                        self.assertEqual(ndsliced.tolist(), sliced)

    eleza test_ndarray_slice_redundant_suboffsets(self):
        shape_t = (2, 3, 5, 2)
        ndim = len(shape_t)
        nitems = prod(shape_t)
        kila shape kwenye permutations(shape_t):

            fmt, items, _ = randitems(nitems)
            itemsize = struct.calcsize(fmt)

            nd = ndarray(items, shape=shape, format=fmt)
            nd.add_suboffsets()
            ex = ndarray(items, shape=shape, format=fmt)
            ex.add_suboffsets()
            mv = memoryview(ex)
            lst = carray(items, shape)

            kila slices kwenye rslices_ndim(ndim, shape):

                listerr = Tupu
                jaribu:
                    sliced = multislice(lst, slices)
                tatizo Exception kama e:
                    listerr = e.__class__

                nderr = Tupu
                jaribu:
                    ndsliced = nd[slices]
                tatizo Exception kama e:
                    nderr = e.__class__

                ikiwa nderr ama listerr:
                    self.assertIs(nderr, listerr)
                isipokua:
                    self.assertEqual(ndsliced.tolist(), sliced)

    eleza test_ndarray_slice_assign_single(self):
        kila fmt, items, _ kwenye iter_format(5):
            kila lslice kwenye genslices(5):
                kila rslice kwenye genslices(5):
                    kila flags kwenye (0, ND_PIL):

                        f = flags|ND_WRITABLE
                        nd = ndarray(items, shape=[5], format=fmt, flags=f)
                        ex = ndarray(items, shape=[5], format=fmt, flags=f)
                        mv = memoryview(ex)

                        lsterr = Tupu
                        diff_structure = Tupu
                        lst = items[:]
                        jaribu:
                            lval = lst[lslice]
                            rval = lst[rslice]
                            lst[lslice] = lst[rslice]
                            diff_structure = len(lval) != len(rval)
                        tatizo Exception kama e:
                            lsterr = e.__class__

                        nderr = Tupu
                        jaribu:
                            nd[lslice] = nd[rslice]
                        tatizo Exception kama e:
                            nderr = e.__class__

                        ikiwa diff_structure: # ndarray cannot change shape
                            self.assertIs(nderr, ValueError)
                        isipokua:
                            self.assertEqual(nd.tolist(), lst)
                            self.assertIs(nderr, lsterr)

                        ikiwa sio is_memoryview_format(fmt):
                            endelea

                        mverr = Tupu
                        jaribu:
                            mv[lslice] = mv[rslice]
                        tatizo Exception kama e:
                            mverr = e.__class__

                        ikiwa diff_structure: # memoryview cannot change shape
                            self.assertIs(mverr, ValueError)
                        isipokua:
                            self.assertEqual(mv.tolist(), lst)
                            self.assertEqual(mv, nd)
                            self.assertIs(mverr, lsterr)
                            self.verify(mv, obj=ex,
                              itemsize=nd.itemsize, fmt=fmt, readonly=Uongo,
                              ndim=nd.ndim, shape=nd.shape, strides=nd.strides,
                              lst=nd.tolist())

    eleza test_ndarray_slice_assign_multidim(self):
        shape_t = (2, 3, 5)
        ndim = len(shape_t)
        nitems = prod(shape_t)
        kila shape kwenye permutations(shape_t):

            fmt, items, _ = randitems(nitems)

            kila flags kwenye (0, ND_PIL):
                kila _ kwenye range(ITERATIONS):
                    lslices, rslices = randslice_from_shape(ndim, shape)

                    nd = ndarray(items, shape=shape, format=fmt,
                                 flags=flags|ND_WRITABLE)
                    lst = carray(items, shape)

                    listerr = Tupu
                    jaribu:
                        result = multislice_assign(lst, lst, lslices, rslices)
                    tatizo Exception kama e:
                        listerr = e.__class__

                    nderr = Tupu
                    jaribu:
                        nd[lslices] = nd[rslices]
                    tatizo Exception kama e:
                        nderr = e.__class__

                    ikiwa nderr ama listerr:
                        self.assertIs(nderr, listerr)
                    isipokua:
                        self.assertEqual(nd.tolist(), result)

    eleza test_ndarray_random(self):
        # construction of valid arrays
        kila _ kwenye range(ITERATIONS):
            kila fmt kwenye fmtdict['@']:
                itemsize = struct.calcsize(fmt)

                t = rand_structure(itemsize, Kweli, maxdim=MAXDIM,
                                   maxshape=MAXSHAPE)
                self.assertKweli(verify_structure(*t))
                items = randitems_from_structure(fmt, t)

                x = ndarray_from_structure(items, fmt, t)
                xlist = x.tolist()

                mv = memoryview(x)
                ikiwa is_memoryview_format(fmt):
                    mvlist = mv.tolist()
                    self.assertEqual(mvlist, xlist)

                ikiwa t[2] > 0:
                    # ndim > 0: test against suboffsets representation.
                    y = ndarray_from_structure(items, fmt, t, flags=ND_PIL)
                    ylist = y.tolist()
                    self.assertEqual(xlist, ylist)

                    mv = memoryview(y)
                    ikiwa is_memoryview_format(fmt):
                        self.assertEqual(mv, y)
                        mvlist = mv.tolist()
                        self.assertEqual(mvlist, ylist)

                ikiwa numpy_array:
                    shape = t[3]
                    ikiwa 0 kwenye shape:
                        endelea # http://projects.scipy.org/numpy/ticket/1910
                    z = numpy_array_from_structure(items, fmt, t)
                    self.verify(x, obj=Tupu,
                                itemsize=z.itemsize, fmt=fmt, readonly=Uongo,
                                ndim=z.ndim, shape=z.shape, strides=z.strides,
                                lst=z.tolist())

    eleza test_ndarray_random_invalid(self):
        # exceptions during construction of invalid arrays
        kila _ kwenye range(ITERATIONS):
            kila fmt kwenye fmtdict['@']:
                itemsize = struct.calcsize(fmt)

                t = rand_structure(itemsize, Uongo, maxdim=MAXDIM,
                                   maxshape=MAXSHAPE)
                self.assertUongo(verify_structure(*t))
                items = randitems_from_structure(fmt, t)

                nderr = Uongo
                jaribu:
                    x = ndarray_from_structure(items, fmt, t)
                tatizo Exception kama e:
                    nderr = e.__class__
                self.assertKweli(nderr)

                ikiwa numpy_array:
                    numpy_err = Uongo
                    jaribu:
                        y = numpy_array_from_structure(items, fmt, t)
                    tatizo Exception kama e:
                        numpy_err = e.__class__

                    ikiwa 0: # http://projects.scipy.org/numpy/ticket/1910
                        self.assertKweli(numpy_err)

    eleza test_ndarray_random_slice_assign(self):
        # valid slice assignments
        kila _ kwenye range(ITERATIONS):
            kila fmt kwenye fmtdict['@']:
                itemsize = struct.calcsize(fmt)

                lshape, rshape, lslices, rslices = \
                    rand_aligned_slices(maxdim=MAXDIM, maxshape=MAXSHAPE)
                tl = rand_structure(itemsize, Kweli, shape=lshape)
                tr = rand_structure(itemsize, Kweli, shape=rshape)
                self.assertKweli(verify_structure(*tl))
                self.assertKweli(verify_structure(*tr))
                litems = randitems_from_structure(fmt, tl)
                ritems = randitems_from_structure(fmt, tr)

                xl = ndarray_from_structure(litems, fmt, tl)
                xr = ndarray_from_structure(ritems, fmt, tr)
                xl[lslices] = xr[rslices]
                xllist = xl.tolist()
                xrlist = xr.tolist()

                ml = memoryview(xl)
                mr = memoryview(xr)
                self.assertEqual(ml.tolist(), xllist)
                self.assertEqual(mr.tolist(), xrlist)

                ikiwa tl[2] > 0 na tr[2] > 0:
                    # ndim > 0: test against suboffsets representation.
                    yl = ndarray_from_structure(litems, fmt, tl, flags=ND_PIL)
                    yr = ndarray_from_structure(ritems, fmt, tr, flags=ND_PIL)
                    yl[lslices] = yr[rslices]
                    yllist = yl.tolist()
                    yrlist = yr.tolist()
                    self.assertEqual(xllist, yllist)
                    self.assertEqual(xrlist, yrlist)

                    ml = memoryview(yl)
                    mr = memoryview(yr)
                    self.assertEqual(ml.tolist(), yllist)
                    self.assertEqual(mr.tolist(), yrlist)

                ikiwa numpy_array:
                    ikiwa 0 kwenye lshape ama 0 kwenye rshape:
                        endelea # http://projects.scipy.org/numpy/ticket/1910

                    zl = numpy_array_from_structure(litems, fmt, tl)
                    zr = numpy_array_from_structure(ritems, fmt, tr)
                    zl[lslices] = zr[rslices]

                    ikiwa sio is_overlapping(tl) na sio is_overlapping(tr):
                        # Slice assignment of overlapping structures
                        # ni undefined kwenye NumPy.
                        self.verify(xl, obj=Tupu,
                                    itemsize=zl.itemsize, fmt=fmt, readonly=Uongo,
                                    ndim=zl.ndim, shape=zl.shape,
                                    strides=zl.strides, lst=zl.tolist())

                    self.verify(xr, obj=Tupu,
                                itemsize=zr.itemsize, fmt=fmt, readonly=Uongo,
                                ndim=zr.ndim, shape=zr.shape,
                                strides=zr.strides, lst=zr.tolist())

    eleza test_ndarray_re_export(self):
        items = [1,2,3,4,5,6,7,8,9,10,11,12]

        nd = ndarray(items, shape=[3,4], flags=ND_PIL)
        ex = ndarray(nd)

        self.assertKweli(ex.flags & ND_PIL)
        self.assertIs(ex.obj, nd)
        self.assertEqual(ex.suboffsets, (0, -1))
        self.assertUongo(ex.c_contiguous)
        self.assertUongo(ex.f_contiguous)
        self.assertUongo(ex.contiguous)

    eleza test_ndarray_zero_shape(self):
        # zeros kwenye shape
        kila flags kwenye (0, ND_PIL):
            nd = ndarray([1,2,3], shape=[0], flags=flags)
            mv = memoryview(nd)
            self.assertEqual(mv, nd)
            self.assertEqual(nd.tolist(), [])
            self.assertEqual(mv.tolist(), [])

            nd = ndarray([1,2,3], shape=[0,3,3], flags=flags)
            self.assertEqual(nd.tolist(), [])

            nd = ndarray([1,2,3], shape=[3,0,3], flags=flags)
            self.assertEqual(nd.tolist(), [[], [], []])

            nd = ndarray([1,2,3], shape=[3,3,0], flags=flags)
            self.assertEqual(nd.tolist(),
                             [[[], [], []], [[], [], []], [[], [], []]])

    eleza test_ndarray_zero_strides(self):
        # zero strides
        kila flags kwenye (0, ND_PIL):
            nd = ndarray([1], shape=[5], strides=[0], flags=flags)
            mv = memoryview(nd)
            self.assertEqual(mv, nd)
            self.assertEqual(nd.tolist(), [1, 1, 1, 1, 1])
            self.assertEqual(mv.tolist(), [1, 1, 1, 1, 1])

    eleza test_ndarray_offset(self):
        nd = ndarray(list(range(20)), shape=[3], offset=7)
        self.assertEqual(nd.offset, 7)
        self.assertEqual(nd.tolist(), [7,8,9])

    eleza test_ndarray_memoryview_from_buffer(self):
        kila flags kwenye (0, ND_PIL):
            nd = ndarray(list(range(3)), shape=[3], flags=flags)
            m = nd.memoryview_from_buffer()
            self.assertEqual(m, nd)

    eleza test_ndarray_get_pointer(self):
        kila flags kwenye (0, ND_PIL):
            nd = ndarray(list(range(3)), shape=[3], flags=flags)
            kila i kwenye range(3):
                self.assertEqual(nd[i], get_pointer(nd, [i]))

    eleza test_ndarray_tolist_null_strides(self):
        ex = ndarray(list(range(20)), shape=[2,2,5])

        nd = ndarray(ex, getbuf=PyBUF_ND|PyBUF_FORMAT)
        self.assertEqual(nd.tolist(), ex.tolist())

        m = memoryview(ex)
        self.assertEqual(m.tolist(), ex.tolist())

    eleza test_ndarray_cmp_contig(self):

        self.assertUongo(cmp_contig(b"123", b"456"))

        x = ndarray(list(range(12)), shape=[3,4])
        y = ndarray(list(range(12)), shape=[4,3])
        self.assertUongo(cmp_contig(x, y))

        x = ndarray([1], shape=[1], format="B")
        self.assertKweli(cmp_contig(x, b'\x01'))
        self.assertKweli(cmp_contig(b'\x01', x))

    eleza test_ndarray_hash(self):

        a = array.array('L', [1,2,3])
        nd = ndarray(a)
        self.assertRaises(ValueError, hash, nd)

        # one-dimensional
        b = bytes(list(range(12)))

        nd = ndarray(list(range(12)), shape=[12])
        self.assertEqual(hash(nd), hash(b))

        # C-contiguous
        nd = ndarray(list(range(12)), shape=[3,4])
        self.assertEqual(hash(nd), hash(b))

        nd = ndarray(list(range(12)), shape=[3,2,2])
        self.assertEqual(hash(nd), hash(b))

        # Fortran contiguous
        b = bytes(transpose(list(range(12)), shape=[4,3]))
        nd = ndarray(list(range(12)), shape=[3,4], flags=ND_FORTRAN)
        self.assertEqual(hash(nd), hash(b))

        b = bytes(transpose(list(range(12)), shape=[2,3,2]))
        nd = ndarray(list(range(12)), shape=[2,3,2], flags=ND_FORTRAN)
        self.assertEqual(hash(nd), hash(b))

        # suboffsets
        b = bytes(list(range(12)))
        nd = ndarray(list(range(12)), shape=[2,2,3], flags=ND_PIL)
        self.assertEqual(hash(nd), hash(b))

        # non-byte formats
        nd = ndarray(list(range(12)), shape=[2,2,3], format='L')
        self.assertEqual(hash(nd), hash(nd.tobytes()))

    eleza test_py_buffer_to_contiguous(self):

        # The requests are used kwenye _testbuffer.c:py_buffer_to_contiguous
        # to generate buffers without full information kila testing.
        requests = (
            # distinct flags
            PyBUF_INDIRECT, PyBUF_STRIDES, PyBUF_ND, PyBUF_SIMPLE,
            # compound requests
            PyBUF_FULL, PyBUF_FULL_RO,
            PyBUF_RECORDS, PyBUF_RECORDS_RO,
            PyBUF_STRIDED, PyBUF_STRIDED_RO,
            PyBUF_CONTIG, PyBUF_CONTIG_RO,
        )

        # no buffer interface
        self.assertRaises(TypeError, py_buffer_to_contiguous, {}, 'F',
                          PyBUF_FULL_RO)

        # scalar, read-only request
        nd = ndarray(9, shape=(), format="L", flags=ND_WRITABLE)
        kila order kwenye ['C', 'F', 'A']:
            kila request kwenye requests:
                b = py_buffer_to_contiguous(nd, order, request)
                self.assertEqual(b, nd.tobytes())

        # zeros kwenye shape
        nd = ndarray([1], shape=[0], format="L", flags=ND_WRITABLE)
        kila order kwenye ['C', 'F', 'A']:
            kila request kwenye requests:
                b = py_buffer_to_contiguous(nd, order, request)
                self.assertEqual(b, b'')

        nd = ndarray(list(range(8)), shape=[2, 0, 7], format="L",
                     flags=ND_WRITABLE)
        kila order kwenye ['C', 'F', 'A']:
            kila request kwenye requests:
                b = py_buffer_to_contiguous(nd, order, request)
                self.assertEqual(b, b'')

        ### One-dimensional arrays are trivial, since Fortran na C order
        ### are the same.

        # one-dimensional
        kila f kwenye [0, ND_FORTRAN]:
            nd = ndarray([1], shape=[1], format="h", flags=f|ND_WRITABLE)
            ndbytes = nd.tobytes()
            kila order kwenye ['C', 'F', 'A']:
                kila request kwenye requests:
                    b = py_buffer_to_contiguous(nd, order, request)
                    self.assertEqual(b, ndbytes)

            nd = ndarray([1, 2, 3], shape=[3], format="b", flags=f|ND_WRITABLE)
            ndbytes = nd.tobytes()
            kila order kwenye ['C', 'F', 'A']:
                kila request kwenye requests:
                    b = py_buffer_to_contiguous(nd, order, request)
                    self.assertEqual(b, ndbytes)

        # one-dimensional, non-contiguous input
        nd = ndarray([1, 2, 3], shape=[2], strides=[2], flags=ND_WRITABLE)
        ndbytes = nd.tobytes()
        kila order kwenye ['C', 'F', 'A']:
            kila request kwenye [PyBUF_STRIDES, PyBUF_FULL]:
                b = py_buffer_to_contiguous(nd, order, request)
                self.assertEqual(b, ndbytes)

        nd = nd[::-1]
        ndbytes = nd.tobytes()
        kila order kwenye ['C', 'F', 'A']:
            kila request kwenye requests:
                jaribu:
                    b = py_buffer_to_contiguous(nd, order, request)
                tatizo BufferError:
                    endelea
                self.assertEqual(b, ndbytes)

        ###
        ### Multi-dimensional arrays:
        ###
        ### The goal here ni to preserve the logical representation of the
        ### input array but change the physical representation ikiwa necessary.
        ###
        ### _testbuffer example:
        ### ====================
        ###
        ###    C input array:
        ###    --------------
        ###       >>> nd = ndarray(list(range(12)), shape=[3, 4])
        ###       >>> nd.tolist()
        ###       [[0, 1, 2, 3],
        ###        [4, 5, 6, 7],
        ###        [8, 9, 10, 11]]
        ###
        ###    Fortran output:
        ###    ---------------
        ###       >>> py_buffer_to_contiguous(nd, 'F', PyBUF_FULL_RO)
        ###       >>> b'\x00\x04\x08\x01\x05\t\x02\x06\n\x03\x07\x0b'
        ###
        ###    The rudisha value corresponds to this input list for
        ###    _testbuffer's ndarray:
        ###       >>> nd = ndarray([0,4,8,1,5,9,2,6,10,3,7,11], shape=[3,4],
        ###                        flags=ND_FORTRAN)
        ###       >>> nd.tolist()
        ###       [[0, 1, 2, 3],
        ###        [4, 5, 6, 7],
        ###        [8, 9, 10, 11]]
        ###
        ###    The logical array ni the same, but the values kwenye memory are now
        ###    kwenye Fortran order.
        ###
        ### NumPy example:
        ### ==============
        ###    _testbuffer's ndarray takes lists to initialize the memory.
        ###    Here's the same sequence kwenye NumPy:
        ###
        ###    C input:
        ###    --------
        ###       >>> nd = ndarray(buffer=bytearray(list(range(12))),
        ###                        shape=[3, 4], dtype='B')
        ###       >>> nd
        ###       array([[ 0,  1,  2,  3],
        ###              [ 4,  5,  6,  7],
        ###              [ 8,  9, 10, 11]], dtype=uint8)
        ###
        ###    Fortran output:
        ###    ---------------
        ###       >>> fortran_buf = nd.tostring(order='F')
        ###       >>> fortran_buf
        ###       b'\x00\x04\x08\x01\x05\t\x02\x06\n\x03\x07\x0b'
        ###
        ###       >>> nd = ndarray(buffer=fortran_buf, shape=[3, 4],
        ###                        dtype='B', order='F')
        ###
        ###       >>> nd
        ###       array([[ 0,  1,  2,  3],
        ###              [ 4,  5,  6,  7],
        ###              [ 8,  9, 10, 11]], dtype=uint8)
        ###

        # multi-dimensional, contiguous input
        lst = list(range(12))
        kila f kwenye [0, ND_FORTRAN]:
            nd = ndarray(lst, shape=[3, 4], flags=f|ND_WRITABLE)
            ikiwa numpy_array:
                na = numpy_array(buffer=bytearray(lst),
                                 shape=[3, 4], dtype='B',
                                 order='C' ikiwa f == 0 isipokua 'F')

            # 'C' request
            ikiwa f == ND_FORTRAN: # 'F' to 'C'
                x = ndarray(transpose(lst, [4, 3]), shape=[3, 4],
                            flags=ND_WRITABLE)
                expected = x.tobytes()
            isipokua:
                expected = nd.tobytes()
            kila request kwenye requests:
                jaribu:
                    b = py_buffer_to_contiguous(nd, 'C', request)
                tatizo BufferError:
                    endelea

                self.assertEqual(b, expected)

                # Check that output can be used kama the basis kila constructing
                # a C array that ni logically identical to the input array.
                y = ndarray([v kila v kwenye b], shape=[3, 4], flags=ND_WRITABLE)
                self.assertEqual(memoryview(y), memoryview(nd))

                ikiwa numpy_array:
                    self.assertEqual(b, na.tostring(order='C'))

            # 'F' request
            ikiwa f == 0: # 'C' to 'F'
                x = ndarray(transpose(lst, [3, 4]), shape=[4, 3],
                            flags=ND_WRITABLE)
            isipokua:
                x = ndarray(lst, shape=[3, 4], flags=ND_WRITABLE)
            expected = x.tobytes()
            kila request kwenye [PyBUF_FULL, PyBUF_FULL_RO, PyBUF_INDIRECT,
                            PyBUF_STRIDES, PyBUF_ND]:
                jaribu:
                    b = py_buffer_to_contiguous(nd, 'F', request)
                tatizo BufferError:
                    endelea
                self.assertEqual(b, expected)

                # Check that output can be used kama the basis kila constructing
                # a Fortran array that ni logically identical to the input array.
                y = ndarray([v kila v kwenye b], shape=[3, 4], flags=ND_FORTRAN|ND_WRITABLE)
                self.assertEqual(memoryview(y), memoryview(nd))

                ikiwa numpy_array:
                    self.assertEqual(b, na.tostring(order='F'))

            # 'A' request
            ikiwa f == ND_FORTRAN:
                x = ndarray(lst, shape=[3, 4], flags=ND_WRITABLE)
                expected = x.tobytes()
            isipokua:
                expected = nd.tobytes()
            kila request kwenye [PyBUF_FULL, PyBUF_FULL_RO, PyBUF_INDIRECT,
                            PyBUF_STRIDES, PyBUF_ND]:
                jaribu:
                    b = py_buffer_to_contiguous(nd, 'A', request)
                tatizo BufferError:
                    endelea

                self.assertEqual(b, expected)

                # Check that output can be used kama the basis kila constructing
                # an array ukijumuisha order=f that ni logically identical to the input
                # array.
                y = ndarray([v kila v kwenye b], shape=[3, 4], flags=f|ND_WRITABLE)
                self.assertEqual(memoryview(y), memoryview(nd))

                ikiwa numpy_array:
                    self.assertEqual(b, na.tostring(order='A'))

        # multi-dimensional, non-contiguous input
        nd = ndarray(list(range(12)), shape=[3, 4], flags=ND_WRITABLE|ND_PIL)

        # 'C'
        b = py_buffer_to_contiguous(nd, 'C', PyBUF_FULL_RO)
        self.assertEqual(b, nd.tobytes())
        y = ndarray([v kila v kwenye b], shape=[3, 4], flags=ND_WRITABLE)
        self.assertEqual(memoryview(y), memoryview(nd))

        # 'F'
        b = py_buffer_to_contiguous(nd, 'F', PyBUF_FULL_RO)
        x = ndarray(transpose(lst, [3, 4]), shape=[4, 3], flags=ND_WRITABLE)
        self.assertEqual(b, x.tobytes())
        y = ndarray([v kila v kwenye b], shape=[3, 4], flags=ND_FORTRAN|ND_WRITABLE)
        self.assertEqual(memoryview(y), memoryview(nd))

        # 'A'
        b = py_buffer_to_contiguous(nd, 'A', PyBUF_FULL_RO)
        self.assertEqual(b, nd.tobytes())
        y = ndarray([v kila v kwenye b], shape=[3, 4], flags=ND_WRITABLE)
        self.assertEqual(memoryview(y), memoryview(nd))

    eleza test_memoryview_construction(self):

        items_shape = [(9, []), ([1,2,3], [3]), (list(range(2*3*5)), [2,3,5])]

        # NumPy style, C-contiguous:
        kila items, shape kwenye items_shape:

            # From PEP-3118 compliant exporter:
            ex = ndarray(items, shape=shape)
            m = memoryview(ex)
            self.assertKweli(m.c_contiguous)
            self.assertKweli(m.contiguous)

            ndim = len(shape)
            strides = strides_from_shape(ndim, shape, 1, 'C')
            lst = carray(items, shape)

            self.verify(m, obj=ex,
                        itemsize=1, fmt='B', readonly=Kweli,
                        ndim=ndim, shape=shape, strides=strides,
                        lst=lst)

            # From memoryview:
            m2 = memoryview(m)
            self.verify(m2, obj=ex,
                        itemsize=1, fmt='B', readonly=Kweli,
                        ndim=ndim, shape=shape, strides=strides,
                        lst=lst)

            # PyMemoryView_FromBuffer(): no strides
            nd = ndarray(ex, getbuf=PyBUF_CONTIG_RO|PyBUF_FORMAT)
            self.assertEqual(nd.strides, ())
            m = nd.memoryview_from_buffer()
            self.verify(m, obj=Tupu,
                        itemsize=1, fmt='B', readonly=Kweli,
                        ndim=ndim, shape=shape, strides=strides,
                        lst=lst)

            # PyMemoryView_FromBuffer(): no format, shape, strides
            nd = ndarray(ex, getbuf=PyBUF_SIMPLE)
            self.assertEqual(nd.format, '')
            self.assertEqual(nd.shape, ())
            self.assertEqual(nd.strides, ())
            m = nd.memoryview_from_buffer()

            lst = [items] ikiwa ndim == 0 isipokua items
            self.verify(m, obj=Tupu,
                        itemsize=1, fmt='B', readonly=Kweli,
                        ndim=1, shape=[ex.nbytes], strides=(1,),
                        lst=lst)

        # NumPy style, Fortran contiguous:
        kila items, shape kwenye items_shape:

            # From PEP-3118 compliant exporter:
            ex = ndarray(items, shape=shape, flags=ND_FORTRAN)
            m = memoryview(ex)
            self.assertKweli(m.f_contiguous)
            self.assertKweli(m.contiguous)

            ndim = len(shape)
            strides = strides_from_shape(ndim, shape, 1, 'F')
            lst = farray(items, shape)

            self.verify(m, obj=ex,
                        itemsize=1, fmt='B', readonly=Kweli,
                        ndim=ndim, shape=shape, strides=strides,
                        lst=lst)

            # From memoryview:
            m2 = memoryview(m)
            self.verify(m2, obj=ex,
                        itemsize=1, fmt='B', readonly=Kweli,
                        ndim=ndim, shape=shape, strides=strides,
                        lst=lst)

        # PIL style:
        kila items, shape kwenye items_shape[1:]:

            # From PEP-3118 compliant exporter:
            ex = ndarray(items, shape=shape, flags=ND_PIL)
            m = memoryview(ex)

            ndim = len(shape)
            lst = carray(items, shape)

            self.verify(m, obj=ex,
                        itemsize=1, fmt='B', readonly=Kweli,
                        ndim=ndim, shape=shape, strides=ex.strides,
                        lst=lst)

            # From memoryview:
            m2 = memoryview(m)
            self.verify(m2, obj=ex,
                        itemsize=1, fmt='B', readonly=Kweli,
                        ndim=ndim, shape=shape, strides=ex.strides,
                        lst=lst)

        # Invalid number of arguments:
        self.assertRaises(TypeError, memoryview, b'9', 'x')
        # Not a buffer provider:
        self.assertRaises(TypeError, memoryview, {})
        # Non-compliant buffer provider:
        ex = ndarray([1,2,3], shape=[3])
        nd = ndarray(ex, getbuf=PyBUF_SIMPLE)
        self.assertRaises(BufferError, memoryview, nd)
        nd = ndarray(ex, getbuf=PyBUF_CONTIG_RO|PyBUF_FORMAT)
        self.assertRaises(BufferError, memoryview, nd)

        # ndim > 64
        nd = ndarray([1]*128, shape=[1]*128, format='L')
        self.assertRaises(ValueError, memoryview, nd)
        self.assertRaises(ValueError, nd.memoryview_from_buffer)
        self.assertRaises(ValueError, get_contiguous, nd, PyBUF_READ, 'C')
        self.assertRaises(ValueError, get_contiguous, nd, PyBUF_READ, 'F')
        self.assertRaises(ValueError, get_contiguous, nd[::-1], PyBUF_READ, 'C')

    eleza test_memoryview_cast_zero_shape(self):
        # Casts are undefined ikiwa buffer ni multidimensional na shape
        # contains zeros. These arrays are regarded kama C-contiguous by
        # Numpy na PyBuffer_GetContiguous(), so they are sio caught by
        # the test kila C-contiguity kwenye memory_cast().
        items = [1,2,3]
        kila shape kwenye ([0,3,3], [3,0,3], [0,3,3]):
            ex = ndarray(items, shape=shape)
            self.assertKweli(ex.c_contiguous)
            msrc = memoryview(ex)
            self.assertRaises(TypeError, msrc.cast, 'c')
        # Monodimensional empty view can be cast (issue #19014).
        kila fmt, _, _ kwenye iter_format(1, 'memoryview'):
            msrc = memoryview(b'')
            m = msrc.cast(fmt)
            self.assertEqual(m.tobytes(), b'')
            self.assertEqual(m.tolist(), [])

    check_sizeof = support.check_sizeof

    eleza test_memoryview_sizeof(self):
        check = self.check_sizeof
        vsize = support.calcvobjsize
        base_struct = 'Pnin 2P2n2i5P P'
        per_dim = '3n'

        items = list(range(8))
        check(memoryview(b''), vsize(base_struct + 1 * per_dim))
        a = ndarray(items, shape=[2, 4], format="b")
        check(memoryview(a), vsize(base_struct + 2 * per_dim))
        a = ndarray(items, shape=[2, 2, 2], format="b")
        check(memoryview(a), vsize(base_struct + 3 * per_dim))

    eleza test_memoryview_struct_module(self):

        kundi INT(object):
            eleza __init__(self, val):
                self.val = val
            eleza __int__(self):
                rudisha self.val

        kundi IDX(object):
            eleza __init__(self, val):
                self.val = val
            eleza __index__(self):
                rudisha self.val

        eleza f(): rudisha 7

        values = [INT(9), IDX(9),
                  2.2+3j, Decimal("-21.1"), 12.2, Fraction(5, 2),
                  [1,2,3], {4,5,6}, {7:8}, (), (9,),
                  Kweli, Uongo, Tupu, NotImplemented,
                  b'a', b'abc', bytearray(b'a'), bytearray(b'abc'),
                  'a', 'abc', r'a', r'abc',
                  f, lambda x: x]

        kila fmt, items, item kwenye iter_format(10, 'memoryview'):
            ex = ndarray(items, shape=[10], format=fmt, flags=ND_WRITABLE)
            nd = ndarray(items, shape=[10], format=fmt, flags=ND_WRITABLE)
            m = memoryview(ex)

            struct.pack_into(fmt, nd, 0, item)
            m[0] = item
            self.assertEqual(m[0], nd[0])

            itemsize = struct.calcsize(fmt)
            ikiwa 'P' kwenye fmt:
                endelea

            kila v kwenye values:
                struct_err = Tupu
                jaribu:
                    struct.pack_into(fmt, nd, itemsize, v)
                tatizo struct.error:
                    struct_err = struct.error

                mv_err = Tupu
                jaribu:
                    m[1] = v
                tatizo (TypeError, ValueError) kama e:
                    mv_err = e.__class__

                ikiwa struct_err ama mv_err:
                    self.assertIsNot(struct_err, Tupu)
                    self.assertIsNot(mv_err, Tupu)
                isipokua:
                    self.assertEqual(m[1], nd[1])

    eleza test_memoryview_cast_zero_strides(self):
        # Casts are undefined ikiwa strides contains zeros. These arrays are
        # (sometimes!) regarded kama C-contiguous by Numpy, but sio by
        # PyBuffer_GetContiguous().
        ex = ndarray([1,2,3], shape=[3], strides=[0])
        self.assertUongo(ex.c_contiguous)
        msrc = memoryview(ex)
        self.assertRaises(TypeError, msrc.cast, 'c')

    eleza test_memoryview_cast_invalid(self):
        # invalid format
        kila sfmt kwenye NON_BYTE_FORMAT:
            sformat = '@' + sfmt ikiwa randrange(2) isipokua sfmt
            ssize = struct.calcsize(sformat)
            kila dfmt kwenye NON_BYTE_FORMAT:
                dformat = '@' + dfmt ikiwa randrange(2) isipokua dfmt
                dsize = struct.calcsize(dformat)
                ex = ndarray(list(range(32)), shape=[32//ssize], format=sformat)
                msrc = memoryview(ex)
                self.assertRaises(TypeError, msrc.cast, dfmt, [32//dsize])

        kila sfmt, sitems, _ kwenye iter_format(1):
            ex = ndarray(sitems, shape=[1], format=sfmt)
            msrc = memoryview(ex)
            kila dfmt, _, _ kwenye iter_format(1):
                ikiwa sio is_memoryview_format(dfmt):
                    self.assertRaises(ValueError, msrc.cast, dfmt,
                                      [32//dsize])
                isipokua:
                    ikiwa sio is_byte_format(sfmt) na sio is_byte_format(dfmt):
                        self.assertRaises(TypeError, msrc.cast, dfmt,
                                          [32//dsize])

        # invalid shape
        size_h = struct.calcsize('h')
        size_d = struct.calcsize('d')
        ex = ndarray(list(range(2*2*size_d)), shape=[2,2,size_d], format='h')
        msrc = memoryview(ex)
        self.assertRaises(TypeError, msrc.cast, shape=[2,2,size_h], format='d')

        ex = ndarray(list(range(120)), shape=[1,2,3,4,5])
        m = memoryview(ex)

        # incorrect number of args
        self.assertRaises(TypeError, m.cast)
        self.assertRaises(TypeError, m.cast, 1, 2, 3)

        # incorrect dest format type
        self.assertRaises(TypeError, m.cast, {})

        # incorrect dest format
        self.assertRaises(ValueError, m.cast, "X")
        self.assertRaises(ValueError, m.cast, "@X")
        self.assertRaises(ValueError, m.cast, "@XY")

        # dest format sio implemented
        self.assertRaises(ValueError, m.cast, "=B")
        self.assertRaises(ValueError, m.cast, "!L")
        self.assertRaises(ValueError, m.cast, "<P")
        self.assertRaises(ValueError, m.cast, ">l")
        self.assertRaises(ValueError, m.cast, "BI")
        self.assertRaises(ValueError, m.cast, "xBI")

        # src format sio implemented
        ex = ndarray([(1,2), (3,4)], shape=[2], format="II")
        m = memoryview(ex)
        self.assertRaises(NotImplementedError, m.__getitem__, 0)
        self.assertRaises(NotImplementedError, m.__setitem__, 0, 8)
        self.assertRaises(NotImplementedError, m.tolist)

        # incorrect shape type
        ex = ndarray(list(range(120)), shape=[1,2,3,4,5])
        m = memoryview(ex)
        self.assertRaises(TypeError, m.cast, "B", shape={})

        # incorrect shape elements
        ex = ndarray(list(range(120)), shape=[2*3*4*5])
        m = memoryview(ex)
        self.assertRaises(OverflowError, m.cast, "B", shape=[2**64])
        self.assertRaises(ValueError, m.cast, "B", shape=[-1])
        self.assertRaises(ValueError, m.cast, "B", shape=[2,3,4,5,6,7,-1])
        self.assertRaises(ValueError, m.cast, "B", shape=[2,3,4,5,6,7,0])
        self.assertRaises(TypeError, m.cast, "B", shape=[2,3,4,5,6,7,'x'])

        # N-D -> N-D cast
        ex = ndarray(list([9 kila _ kwenye range(3*5*7*11)]), shape=[3,5,7,11])
        m = memoryview(ex)
        self.assertRaises(TypeError, m.cast, "I", shape=[2,3,4,5])

        # cast ukijumuisha ndim > 64
        nd = ndarray(list(range(128)), shape=[128], format='I')
        m = memoryview(nd)
        self.assertRaises(ValueError, m.cast, 'I', [1]*128)

        # view->len sio a multiple of itemsize
        ex = ndarray(list([9 kila _ kwenye range(3*5*7*11)]), shape=[3*5*7*11])
        m = memoryview(ex)
        self.assertRaises(TypeError, m.cast, "I", shape=[2,3,4,5])

        # product(shape) * itemsize != buffer size
        ex = ndarray(list([9 kila _ kwenye range(3*5*7*11)]), shape=[3*5*7*11])
        m = memoryview(ex)
        self.assertRaises(TypeError, m.cast, "B", shape=[2,3,4,5])

        # product(shape) * itemsize overflow
        nd = ndarray(list(range(128)), shape=[128], format='I')
        m1 = memoryview(nd)
        nd = ndarray(list(range(128)), shape=[128], format='B')
        m2 = memoryview(nd)
        ikiwa sys.maxsize == 2**63-1:
            self.assertRaises(TypeError, m1.cast, 'B',
                              [7, 7, 73, 127, 337, 92737, 649657])
            self.assertRaises(ValueError, m1.cast, 'B',
                              [2**20, 2**20, 2**10, 2**10, 2**3])
            self.assertRaises(ValueError, m2.cast, 'I',
                              [2**20, 2**20, 2**10, 2**10, 2**1])
        isipokua:
            self.assertRaises(TypeError, m1.cast, 'B',
                              [1, 2147483647])
            self.assertRaises(ValueError, m1.cast, 'B',
                              [2**10, 2**10, 2**5, 2**5, 2**1])
            self.assertRaises(ValueError, m2.cast, 'I',
                              [2**10, 2**10, 2**5, 2**3, 2**1])

    eleza test_memoryview_cast(self):
        bytespec = (
          ('B', lambda ex: list(ex.tobytes())),
          ('b', lambda ex: [x-256 ikiwa x > 127 isipokua x kila x kwenye list(ex.tobytes())]),
          ('c', lambda ex: [bytes(chr(x), 'latin-1') kila x kwenye list(ex.tobytes())]),
        )

        eleza iter_roundtrip(ex, m, items, fmt):
            srcsize = struct.calcsize(fmt)
            kila bytefmt, to_bytelist kwenye bytespec:

                m2 = m.cast(bytefmt)
                lst = to_bytelist(ex)
                self.verify(m2, obj=ex,
                            itemsize=1, fmt=bytefmt, readonly=Uongo,
                            ndim=1, shape=[31*srcsize], strides=(1,),
                            lst=lst, cast=Kweli)

                m3 = m2.cast(fmt)
                self.assertEqual(m3, ex)
                lst = ex.tolist()
                self.verify(m3, obj=ex,
                            itemsize=srcsize, fmt=fmt, readonly=Uongo,
                            ndim=1, shape=[31], strides=(srcsize,),
                            lst=lst, cast=Kweli)

        # cast kutoka ndim = 0 to ndim = 1
        srcsize = struct.calcsize('I')
        ex = ndarray(9, shape=[], format='I')
        destitems, destshape = cast_items(ex, 'B', 1)
        m = memoryview(ex)
        m2 = m.cast('B')
        self.verify(m2, obj=ex,
                    itemsize=1, fmt='B', readonly=Kweli,
                    ndim=1, shape=destshape, strides=(1,),
                    lst=destitems, cast=Kweli)

        # cast kutoka ndim = 1 to ndim = 0
        destsize = struct.calcsize('I')
        ex = ndarray([9]*destsize, shape=[destsize], format='B')
        destitems, destshape = cast_items(ex, 'I', destsize, shape=[])
        m = memoryview(ex)
        m2 = m.cast('I', shape=[])
        self.verify(m2, obj=ex,
                    itemsize=destsize, fmt='I', readonly=Kweli,
                    ndim=0, shape=(), strides=(),
                    lst=destitems, cast=Kweli)

        # array.array: roundtrip to/kutoka bytes
        kila fmt, items, _ kwenye iter_format(31, 'array'):
            ex = array.array(fmt, items)
            m = memoryview(ex)
            iter_roundtrip(ex, m, items, fmt)

        # ndarray: roundtrip to/kutoka bytes
        kila fmt, items, _ kwenye iter_format(31, 'memoryview'):
            ex = ndarray(items, shape=[31], format=fmt, flags=ND_WRITABLE)
            m = memoryview(ex)
            iter_roundtrip(ex, m, items, fmt)

    eleza test_memoryview_cast_1D_ND(self):
        # Cast between C-contiguous buffers. At least one buffer must
        # be 1D, at least one format must be 'c', 'b' ama 'B'.
        kila _tshape kwenye gencastshapes():
            kila char kwenye fmtdict['@']:
                tfmt = ('', '@')[randrange(2)] + char
                tsize = struct.calcsize(tfmt)
                n = prod(_tshape) * tsize
                obj = 'memoryview' ikiwa is_byte_format(tfmt) isipokua 'bytefmt'
                kila fmt, items, _ kwenye iter_format(n, obj):
                    size = struct.calcsize(fmt)
                    shape = [n] ikiwa n > 0 isipokua []
                    tshape = _tshape + [size]

                    ex = ndarray(items, shape=shape, format=fmt)
                    m = memoryview(ex)

                    titems, tshape = cast_items(ex, tfmt, tsize, shape=tshape)

                    ikiwa titems ni Tupu:
                        self.assertRaises(TypeError, m.cast, tfmt, tshape)
                        endelea
                    ikiwa titems == 'nan':
                        endelea # NaNs kwenye lists are a recipe kila trouble.

                    # 1D -> ND
                    nd = ndarray(titems, shape=tshape, format=tfmt)

                    m2 = m.cast(tfmt, shape=tshape)
                    ndim = len(tshape)
                    strides = nd.strides
                    lst = nd.tolist()
                    self.verify(m2, obj=ex,
                                itemsize=tsize, fmt=tfmt, readonly=Kweli,
                                ndim=ndim, shape=tshape, strides=strides,
                                lst=lst, cast=Kweli)

                    # ND -> 1D
                    m3 = m2.cast(fmt)
                    m4 = m2.cast(fmt, shape=shape)
                    ndim = len(shape)
                    strides = ex.strides
                    lst = ex.tolist()

                    self.verify(m3, obj=ex,
                                itemsize=size, fmt=fmt, readonly=Kweli,
                                ndim=ndim, shape=shape, strides=strides,
                                lst=lst, cast=Kweli)

                    self.verify(m4, obj=ex,
                                itemsize=size, fmt=fmt, readonly=Kweli,
                                ndim=ndim, shape=shape, strides=strides,
                                lst=lst, cast=Kweli)

        ikiwa ctypes:
            # format: "T{>l:x:>d:y:}"
            kundi BEPoint(ctypes.BigEndianStructure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_double)]
            point = BEPoint(100, 200.1)
            m1 = memoryview(point)
            m2 = m1.cast('B')
            self.assertEqual(m2.obj, point)
            self.assertEqual(m2.itemsize, 1)
            self.assertIs(m2.readonly, Uongo)
            self.assertEqual(m2.ndim, 1)
            self.assertEqual(m2.shape, (m2.nbytes,))
            self.assertEqual(m2.strides, (1,))
            self.assertEqual(m2.suboffsets, ())

            x = ctypes.c_double(1.2)
            m1 = memoryview(x)
            m2 = m1.cast('c')
            self.assertEqual(m2.obj, x)
            self.assertEqual(m2.itemsize, 1)
            self.assertIs(m2.readonly, Uongo)
            self.assertEqual(m2.ndim, 1)
            self.assertEqual(m2.shape, (m2.nbytes,))
            self.assertEqual(m2.strides, (1,))
            self.assertEqual(m2.suboffsets, ())

    eleza test_memoryview_tolist(self):

        # Most tolist() tests are kwenye self.verify() etc.

        a = array.array('h', list(range(-6, 6)))
        m = memoryview(a)
        self.assertEqual(m, a)
        self.assertEqual(m.tolist(), a.tolist())

        a = a[2::3]
        m = m[2::3]
        self.assertEqual(m, a)
        self.assertEqual(m.tolist(), a.tolist())

        ex = ndarray(list(range(2*3*5*7*11)), shape=[11,2,7,3,5], format='L')
        m = memoryview(ex)
        self.assertEqual(m.tolist(), ex.tolist())

        ex = ndarray([(2, 5), (7, 11)], shape=[2], format='lh')
        m = memoryview(ex)
        self.assertRaises(NotImplementedError, m.tolist)

        ex = ndarray([b'12345'], shape=[1], format="s")
        m = memoryview(ex)
        self.assertRaises(NotImplementedError, m.tolist)

        ex = ndarray([b"a",b"b",b"c",b"d",b"e",b"f"], shape=[2,3], format='s')
        m = memoryview(ex)
        self.assertRaises(NotImplementedError, m.tolist)

    eleza test_memoryview_repr(self):
        m = memoryview(bytearray(9))
        r = m.__repr__()
        self.assertKweli(r.startswith("<memory"))

        m.release()
        r = m.__repr__()
        self.assertKweli(r.startswith("<released"))

    eleza test_memoryview_sequence(self):

        kila fmt kwenye ('d', 'f'):
            inf = float(3e400)
            ex = array.array(fmt, [1.0, inf, 3.0])
            m = memoryview(ex)
            self.assertIn(1.0, m)
            self.assertIn(5e700, m)
            self.assertIn(3.0, m)

        ex = ndarray(9.0, [], format='f')
        m = memoryview(ex)
        self.assertRaises(TypeError, eval, "9.0 kwenye m", locals())

    @contextlib.contextmanager
    eleza assert_out_of_bounds_error(self, dim):
        ukijumuisha self.assertRaises(IndexError) kama cm:
            tuma
        self.assertEqual(str(cm.exception),
                         "index out of bounds on dimension %d" % (dim,))

    eleza test_memoryview_index(self):

        # ndim = 0
        ex = ndarray(12.5, shape=[], format='d')
        m = memoryview(ex)
        self.assertEqual(m[()], 12.5)
        self.assertEqual(m[...], m)
        self.assertEqual(m[...], ex)
        self.assertRaises(TypeError, m.__getitem__, 0)

        ex = ndarray((1,2,3), shape=[], format='iii')
        m = memoryview(ex)
        self.assertRaises(NotImplementedError, m.__getitem__, ())

        # range
        ex = ndarray(list(range(7)), shape=[7], flags=ND_WRITABLE)
        m = memoryview(ex)

        self.assertRaises(IndexError, m.__getitem__, 2**64)
        self.assertRaises(TypeError, m.__getitem__, 2.0)
        self.assertRaises(TypeError, m.__getitem__, 0.0)

        # out of bounds
        self.assertRaises(IndexError, m.__getitem__, -8)
        self.assertRaises(IndexError, m.__getitem__, 8)

        # multi-dimensional
        ex = ndarray(list(range(12)), shape=[3,4], flags=ND_WRITABLE)
        m = memoryview(ex)

        self.assertEqual(m[0, 0], 0)
        self.assertEqual(m[2, 0], 8)
        self.assertEqual(m[2, 3], 11)
        self.assertEqual(m[-1, -1], 11)
        self.assertEqual(m[-3, -4], 0)

        # out of bounds
        kila index kwenye (3, -4):
            ukijumuisha self.assert_out_of_bounds_error(dim=1):
                m[index, 0]
        kila index kwenye (4, -5):
            ukijumuisha self.assert_out_of_bounds_error(dim=2):
                m[0, index]
        self.assertRaises(IndexError, m.__getitem__, (2**64, 0))
        self.assertRaises(IndexError, m.__getitem__, (0, 2**64))

        self.assertRaises(TypeError, m.__getitem__, (0, 0, 0))
        self.assertRaises(TypeError, m.__getitem__, (0.0, 0.0))

        # Not implemented: multidimensional sub-views
        self.assertRaises(NotImplementedError, m.__getitem__, ())
        self.assertRaises(NotImplementedError, m.__getitem__, 0)

    eleza test_memoryview_assign(self):

        # ndim = 0
        ex = ndarray(12.5, shape=[], format='f', flags=ND_WRITABLE)
        m = memoryview(ex)
        m[()] = 22.5
        self.assertEqual(m[()], 22.5)
        m[...] = 23.5
        self.assertEqual(m[()], 23.5)
        self.assertRaises(TypeError, m.__setitem__, 0, 24.7)

        # read-only
        ex = ndarray(list(range(7)), shape=[7])
        m = memoryview(ex)
        self.assertRaises(TypeError, m.__setitem__, 2, 10)

        # range
        ex = ndarray(list(range(7)), shape=[7], flags=ND_WRITABLE)
        m = memoryview(ex)

        self.assertRaises(IndexError, m.__setitem__, 2**64, 9)
        self.assertRaises(TypeError, m.__setitem__, 2.0, 10)
        self.assertRaises(TypeError, m.__setitem__, 0.0, 11)

        # out of bounds
        self.assertRaises(IndexError, m.__setitem__, -8, 20)
        self.assertRaises(IndexError, m.__setitem__, 8, 25)

        # pack_single() success:
        kila fmt kwenye fmtdict['@']:
            ikiwa fmt == 'c' ama fmt == '?':
                endelea
            ex = ndarray([1,2,3], shape=[3], format=fmt, flags=ND_WRITABLE)
            m = memoryview(ex)
            i = randrange(-3, 3)
            m[i] = 8
            self.assertEqual(m[i], 8)
            self.assertEqual(m[i], ex[i])

        ex = ndarray([b'1', b'2', b'3'], shape=[3], format='c',
                     flags=ND_WRITABLE)
        m = memoryview(ex)
        m[2] = b'9'
        self.assertEqual(m[2], b'9')

        ex = ndarray([Kweli, Uongo, Kweli], shape=[3], format='?',
                     flags=ND_WRITABLE)
        m = memoryview(ex)
        m[1] = Kweli
        self.assertIs(m[1], Kweli)

        # pack_single() exceptions:
        nd = ndarray([b'x'], shape=[1], format='c', flags=ND_WRITABLE)
        m = memoryview(nd)
        self.assertRaises(TypeError, m.__setitem__, 0, 100)

        ex = ndarray(list(range(120)), shape=[1,2,3,4,5], flags=ND_WRITABLE)
        m1 = memoryview(ex)

        kila fmt, _range kwenye fmtdict['@'].items():
            ikiwa (fmt == '?'): # PyObject_IsKweli() accepts anything
                endelea
            ikiwa fmt == 'c': # special case tested above
                endelea
            m2 = m1.cast(fmt)
            lo, hi = _range
            ikiwa fmt == 'd' ama fmt == 'f':
                lo, hi = -2**1024, 2**1024
            ikiwa fmt != 'P': # PyLong_AsVoidPtr() accepts negative numbers
                self.assertRaises(ValueError, m2.__setitem__, 0, lo-1)
                self.assertRaises(TypeError, m2.__setitem__, 0, "xyz")
            self.assertRaises(ValueError, m2.__setitem__, 0, hi)

        # invalid item
        m2 = m1.cast('c')
        self.assertRaises(ValueError, m2.__setitem__, 0, b'\xff\xff')

        # format sio implemented
        ex = ndarray(list(range(1)), shape=[1], format="xL", flags=ND_WRITABLE)
        m = memoryview(ex)
        self.assertRaises(NotImplementedError, m.__setitem__, 0, 1)

        ex = ndarray([b'12345'], shape=[1], format="s", flags=ND_WRITABLE)
        m = memoryview(ex)
        self.assertRaises(NotImplementedError, m.__setitem__, 0, 1)

        # multi-dimensional
        ex = ndarray(list(range(12)), shape=[3,4], flags=ND_WRITABLE)
        m = memoryview(ex)
        m[0,1] = 42
        self.assertEqual(ex[0][1], 42)
        m[-1,-1] = 43
        self.assertEqual(ex[2][3], 43)
        # errors
        kila index kwenye (3, -4):
            ukijumuisha self.assert_out_of_bounds_error(dim=1):
                m[index, 0] = 0
        kila index kwenye (4, -5):
            ukijumuisha self.assert_out_of_bounds_error(dim=2):
                m[0, index] = 0
        self.assertRaises(IndexError, m.__setitem__, (2**64, 0), 0)
        self.assertRaises(IndexError, m.__setitem__, (0, 2**64), 0)

        self.assertRaises(TypeError, m.__setitem__, (0, 0, 0), 0)
        self.assertRaises(TypeError, m.__setitem__, (0.0, 0.0), 0)

        # Not implemented: multidimensional sub-views
        self.assertRaises(NotImplementedError, m.__setitem__, 0, [2, 3])

    eleza test_memoryview_slice(self):

        ex = ndarray(list(range(12)), shape=[12], flags=ND_WRITABLE)
        m = memoryview(ex)

        # zero step
        self.assertRaises(ValueError, m.__getitem__, slice(0,2,0))
        self.assertRaises(ValueError, m.__setitem__, slice(0,2,0),
                          bytearray([1,2]))

        # 0-dim slicing (identity function)
        self.assertRaises(NotImplementedError, m.__getitem__, ())

        # multidimensional slices
        ex = ndarray(list(range(12)), shape=[12], flags=ND_WRITABLE)
        m = memoryview(ex)

        self.assertRaises(NotImplementedError, m.__getitem__,
                          (slice(0,2,1), slice(0,2,1)))
        self.assertRaises(NotImplementedError, m.__setitem__,
                          (slice(0,2,1), slice(0,2,1)), bytearray([1,2]))

        # invalid slice tuple
        self.assertRaises(TypeError, m.__getitem__, (slice(0,2,1), {}))
        self.assertRaises(TypeError, m.__setitem__, (slice(0,2,1), {}),
                          bytearray([1,2]))

        # rvalue ni sio an exporter
        self.assertRaises(TypeError, m.__setitem__, slice(0,1,1), [1])

        # non-contiguous slice assignment
        kila flags kwenye (0, ND_PIL):
            ex1 = ndarray(list(range(12)), shape=[12], strides=[-1], offset=11,
                          flags=ND_WRITABLE|flags)
            ex2 = ndarray(list(range(24)), shape=[12], strides=[2], flags=flags)
            m1 = memoryview(ex1)
            m2 = memoryview(ex2)

            ex1[2:5] = ex1[2:5]
            m1[2:5] = m2[2:5]

            self.assertEqual(m1, ex1)
            self.assertEqual(m2, ex2)

            ex1[1:3][::-1] = ex2[0:2][::1]
            m1[1:3][::-1] = m2[0:2][::1]

            self.assertEqual(m1, ex1)
            self.assertEqual(m2, ex2)

            ex1[4:1:-2][::-1] = ex1[1:4:2][::1]
            m1[4:1:-2][::-1] = m1[1:4:2][::1]

            self.assertEqual(m1, ex1)
            self.assertEqual(m2, ex2)

    eleza test_memoryview_array(self):

        eleza cmptest(testcase, a, b, m, singleitem):
            kila i, _ kwenye enumerate(a):
                ai = a[i]
                mi = m[i]
                testcase.assertEqual(ai, mi)
                a[i] = singleitem
                ikiwa singleitem != ai:
                    testcase.assertNotEqual(a, m)
                    testcase.assertNotEqual(a, b)
                isipokua:
                    testcase.assertEqual(a, m)
                    testcase.assertEqual(a, b)
                m[i] = singleitem
                testcase.assertEqual(a, m)
                testcase.assertEqual(b, m)
                a[i] = ai
                m[i] = mi

        kila n kwenye range(1, 5):
            kila fmt, items, singleitem kwenye iter_format(n, 'array'):
                kila lslice kwenye genslices(n):
                    kila rslice kwenye genslices(n):

                        a = array.array(fmt, items)
                        b = array.array(fmt, items)
                        m = memoryview(b)

                        self.assertEqual(m, a)
                        self.assertEqual(m.tolist(), a.tolist())
                        self.assertEqual(m.tobytes(), a.tobytes())
                        self.assertEqual(len(m), len(a))

                        cmptest(self, a, b, m, singleitem)

                        array_err = Tupu
                        have_resize = Tupu
                        jaribu:
                            al = a[lslice]
                            ar = a[rslice]
                            a[lslice] = a[rslice]
                            have_resize = len(al) != len(ar)
                        tatizo Exception kama e:
                            array_err = e.__class__

                        m_err = Tupu
                        jaribu:
                            m[lslice] = m[rslice]
                        tatizo Exception kama e:
                            m_err = e.__class__

                        ikiwa have_resize: # memoryview cannot change shape
                            self.assertIs(m_err, ValueError)
                        lasivyo m_err ama array_err:
                            self.assertIs(m_err, array_err)
                        isipokua:
                            self.assertEqual(m, a)
                            self.assertEqual(m.tolist(), a.tolist())
                            self.assertEqual(m.tobytes(), a.tobytes())
                            cmptest(self, a, b, m, singleitem)

    eleza test_memoryview_compare_special_cases(self):

        a = array.array('L', [1, 2, 3])
        b = array.array('L', [1, 2, 7])

        # Ordering comparisons raise:
        v = memoryview(a)
        w = memoryview(b)
        kila attr kwenye ('__lt__', '__le__', '__gt__', '__ge__'):
            self.assertIs(getattr(v, attr)(w), NotImplemented)
            self.assertIs(getattr(a, attr)(v), NotImplemented)

        # Released views compare equal to themselves:
        v = memoryview(a)
        v.release()
        self.assertEqual(v, v)
        self.assertNotEqual(v, a)
        self.assertNotEqual(a, v)

        v = memoryview(a)
        w = memoryview(a)
        w.release()
        self.assertNotEqual(v, w)
        self.assertNotEqual(w, v)

        # Operand does sio implement the buffer protocol:
        v = memoryview(a)
        self.assertNotEqual(v, [1, 2, 3])

        # NaNs
        nd = ndarray([(0, 0)], shape=[1], format='l x d x', flags=ND_WRITABLE)
        nd[0] = (-1, float('nan'))
        self.assertNotEqual(memoryview(nd), nd)

        # Depends on issue #15625: the struct module does sio understand 'u'.
        a = array.array('u', 'xyz')
        v = memoryview(a)
        self.assertNotEqual(a, v)
        self.assertNotEqual(v, a)

        # Some ctypes format strings are unknown to the struct module.
        ikiwa ctypes:
            # format: "T{>l:x:>l:y:}"
            kundi BEPoint(ctypes.BigEndianStructure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            point = BEPoint(100, 200)
            a = memoryview(point)
            b = memoryview(point)
            self.assertNotEqual(a, b)
            self.assertNotEqual(a, point)
            self.assertNotEqual(point, a)
            self.assertRaises(NotImplementedError, a.tolist)

    eleza test_memoryview_compare_ndim_zero(self):

        nd1 = ndarray(1729, shape=[], format='@L')
        nd2 = ndarray(1729, shape=[], format='L', flags=ND_WRITABLE)
        v = memoryview(nd1)
        w = memoryview(nd2)
        self.assertEqual(v, w)
        self.assertEqual(w, v)
        self.assertEqual(v, nd2)
        self.assertEqual(nd2, v)
        self.assertEqual(w, nd1)
        self.assertEqual(nd1, w)

        self.assertUongo(v.__ne__(w))
        self.assertUongo(w.__ne__(v))

        w[()] = 1728
        self.assertNotEqual(v, w)
        self.assertNotEqual(w, v)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(nd2, v)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(nd1, w)

        self.assertUongo(v.__eq__(w))
        self.assertUongo(w.__eq__(v))

        nd = ndarray(list(range(12)), shape=[12], flags=ND_WRITABLE|ND_PIL)
        ex = ndarray(list(range(12)), shape=[12], flags=ND_WRITABLE|ND_PIL)
        m = memoryview(ex)

        self.assertEqual(m, nd)
        m[9] = 100
        self.assertNotEqual(m, nd)

        # struct module: equal
        nd1 = ndarray((1729, 1.2, b'12345'), shape=[], format='Lf5s')
        nd2 = ndarray((1729, 1.2, b'12345'), shape=[], format='hf5s',
                      flags=ND_WRITABLE)
        v = memoryview(nd1)
        w = memoryview(nd2)
        self.assertEqual(v, w)
        self.assertEqual(w, v)
        self.assertEqual(v, nd2)
        self.assertEqual(nd2, v)
        self.assertEqual(w, nd1)
        self.assertEqual(nd1, w)

        # struct module: sio equal
        nd1 = ndarray((1729, 1.2, b'12345'), shape=[], format='Lf5s')
        nd2 = ndarray((-1729, 1.2, b'12345'), shape=[], format='hf5s',
                      flags=ND_WRITABLE)
        v = memoryview(nd1)
        w = memoryview(nd2)
        self.assertNotEqual(v, w)
        self.assertNotEqual(w, v)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(nd2, v)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(nd1, w)
        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)

    eleza test_memoryview_compare_ndim_one(self):

        # contiguous
        nd1 = ndarray([-529, 576, -625, 676, -729], shape=[5], format='@h')
        nd2 = ndarray([-529, 576, -625, 676, 729], shape=[5], format='@h')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # contiguous, struct module
        nd1 = ndarray([-529, 576, -625, 676, -729], shape=[5], format='<i')
        nd2 = ndarray([-529, 576, -625, 676, 729], shape=[5], format='>h')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # non-contiguous
        nd1 = ndarray([-529, -625, -729], shape=[3], format='@h')
        nd2 = ndarray([-529, 576, -625, 676, -729], shape=[5], format='@h')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd2[::2])
        self.assertEqual(w[::2], nd1)
        self.assertEqual(v, w[::2])
        self.assertEqual(v[::-1], w[::-2])

        # non-contiguous, struct module
        nd1 = ndarray([-529, -625, -729], shape=[3], format='!h')
        nd2 = ndarray([-529, 576, -625, 676, -729], shape=[5], format='<l')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd2[::2])
        self.assertEqual(w[::2], nd1)
        self.assertEqual(v, w[::2])
        self.assertEqual(v[::-1], w[::-2])

        # non-contiguous, suboffsets
        nd1 = ndarray([-529, -625, -729], shape=[3], format='@h')
        nd2 = ndarray([-529, 576, -625, 676, -729], shape=[5], format='@h',
                      flags=ND_PIL)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd2[::2])
        self.assertEqual(w[::2], nd1)
        self.assertEqual(v, w[::2])
        self.assertEqual(v[::-1], w[::-2])

        # non-contiguous, suboffsets, struct module
        nd1 = ndarray([-529, -625, -729], shape=[3], format='h  0c')
        nd2 = ndarray([-529, 576, -625, 676, -729], shape=[5], format='>  h',
                      flags=ND_PIL)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd2[::2])
        self.assertEqual(w[::2], nd1)
        self.assertEqual(v, w[::2])
        self.assertEqual(v[::-1], w[::-2])

    eleza test_memoryview_compare_zero_shape(self):

        # zeros kwenye shape
        nd1 = ndarray([900, 961], shape=[0], format='@h')
        nd2 = ndarray([-900, -961], shape=[0], format='@h')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

        # zeros kwenye shape, struct module
        nd1 = ndarray([900, 961], shape=[0], format='= h0c')
        nd2 = ndarray([-900, -961], shape=[0], format='@   i')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

    eleza test_memoryview_compare_zero_strides(self):

        # zero strides
        nd1 = ndarray([900, 900, 900, 900], shape=[4], format='@L')
        nd2 = ndarray([900], shape=[4], strides=[0], format='L')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

        # zero strides, struct module
        nd1 = ndarray([(900, 900)]*4, shape=[4], format='@ Li')
        nd2 = ndarray([(900, 900)], shape=[4], strides=[0], format='!L  h')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

    eleza test_memoryview_compare_random_formats(self):

        # random single character native formats
        n = 10
        kila char kwenye fmtdict['@m']:
            fmt, items, singleitem = randitems(n, 'memoryview', '@', char)
            kila flags kwenye (0, ND_PIL):
                nd = ndarray(items, shape=[n], format=fmt, flags=flags)
                m = memoryview(nd)
                self.assertEqual(m, nd)

                nd = nd[::-3]
                m = memoryview(nd)
                self.assertEqual(m, nd)

        # random formats
        n = 10
        kila _ kwenye range(100):
            fmt, items, singleitem = randitems(n)
            kila flags kwenye (0, ND_PIL):
                nd = ndarray(items, shape=[n], format=fmt, flags=flags)
                m = memoryview(nd)
                self.assertEqual(m, nd)

                nd = nd[::-3]
                m = memoryview(nd)
                self.assertEqual(m, nd)

    eleza test_memoryview_compare_multidim_c(self):

        # C-contiguous, different values
        nd1 = ndarray(list(range(-15, 15)), shape=[3, 2, 5], format='@h')
        nd2 = ndarray(list(range(0, 30)), shape=[3, 2, 5], format='@h')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # C-contiguous, different values, struct module
        nd1 = ndarray([(0, 1, 2)]*30, shape=[3, 2, 5], format='=f q xxL')
        nd2 = ndarray([(-1.2, 1, 2)]*30, shape=[3, 2, 5], format='< f 2Q')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # C-contiguous, different shape
        nd1 = ndarray(list(range(30)), shape=[2, 3, 5], format='L')
        nd2 = ndarray(list(range(30)), shape=[3, 2, 5], format='L')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # C-contiguous, different shape, struct module
        nd1 = ndarray([(0, 1, 2)]*21, shape=[3, 7], format='! b B xL')
        nd2 = ndarray([(0, 1, 2)]*21, shape=[7, 3], format='= Qx l xxL')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # C-contiguous, different format, struct module
        nd1 = ndarray(list(range(30)), shape=[2, 3, 5], format='L')
        nd2 = ndarray(list(range(30)), shape=[2, 3, 5], format='l')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

    eleza test_memoryview_compare_multidim_fortran(self):

        # Fortran-contiguous, different values
        nd1 = ndarray(list(range(-15, 15)), shape=[5, 2, 3], format='@h',
                      flags=ND_FORTRAN)
        nd2 = ndarray(list(range(0, 30)), shape=[5, 2, 3], format='@h',
                      flags=ND_FORTRAN)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # Fortran-contiguous, different values, struct module
        nd1 = ndarray([(2**64-1, -1)]*6, shape=[2, 3], format='=Qq',
                      flags=ND_FORTRAN)
        nd2 = ndarray([(-1, 2**64-1)]*6, shape=[2, 3], format='=qQ',
                      flags=ND_FORTRAN)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # Fortran-contiguous, different shape
        nd1 = ndarray(list(range(-15, 15)), shape=[2, 3, 5], format='l',
                      flags=ND_FORTRAN)
        nd2 = ndarray(list(range(-15, 15)), shape=[3, 2, 5], format='l',
                      flags=ND_FORTRAN)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # Fortran-contiguous, different shape, struct module
        nd1 = ndarray(list(range(-15, 15)), shape=[2, 3, 5], format='0ll',
                      flags=ND_FORTRAN)
        nd2 = ndarray(list(range(-15, 15)), shape=[3, 2, 5], format='l',
                      flags=ND_FORTRAN)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # Fortran-contiguous, different format, struct module
        nd1 = ndarray(list(range(30)), shape=[5, 2, 3], format='@h',
                      flags=ND_FORTRAN)
        nd2 = ndarray(list(range(30)), shape=[5, 2, 3], format='@b',
                      flags=ND_FORTRAN)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

    eleza test_memoryview_compare_multidim_mixed(self):

        # mixed C/Fortran contiguous
        lst1 = list(range(-15, 15))
        lst2 = transpose(lst1, [3, 2, 5])
        nd1 = ndarray(lst1, shape=[3, 2, 5], format='@l')
        nd2 = ndarray(lst2, shape=[3, 2, 5], format='l', flags=ND_FORTRAN)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, w)

        # mixed C/Fortran contiguous, struct module
        lst1 = [(-3.3, -22, b'x')]*30
        lst1[5] = (-2.2, -22, b'x')
        lst2 = transpose(lst1, [3, 2, 5])
        nd1 = ndarray(lst1, shape=[3, 2, 5], format='d b c')
        nd2 = ndarray(lst2, shape=[3, 2, 5], format='d h c', flags=ND_FORTRAN)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, w)

        # different values, non-contiguous
        ex1 = ndarray(list(range(40)), shape=[5, 8], format='@I')
        nd1 = ex1[3:1:-1, ::-2]
        ex2 = ndarray(list(range(40)), shape=[5, 8], format='I')
        nd2 = ex2[1:3:1, ::-2]
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # same values, non-contiguous, struct module
        ex1 = ndarray([(2**31-1, -2**31)]*22, shape=[11, 2], format='=ii')
        nd1 = ex1[3:1:-1, ::-2]
        ex2 = ndarray([(2**31-1, -2**31)]*22, shape=[11, 2], format='>ii')
        nd2 = ex2[1:3:1, ::-2]
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

        # different shape
        ex1 = ndarray(list(range(30)), shape=[2, 3, 5], format='b')
        nd1 = ex1[1:3:, ::-2]
        nd2 = ndarray(list(range(30)), shape=[3, 2, 5], format='b')
        nd2 = ex2[1:3:, ::-2]
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # different shape, struct module
        ex1 = ndarray(list(range(30)), shape=[2, 3, 5], format='B')
        nd1 = ex1[1:3:, ::-2]
        nd2 = ndarray(list(range(30)), shape=[3, 2, 5], format='b')
        nd2 = ex2[1:3:, ::-2]
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # different format, struct module
        ex1 = ndarray([(2, b'123')]*30, shape=[5, 3, 2], format='b3s')
        nd1 = ex1[1:3:, ::-2]
        nd2 = ndarray([(2, b'123')]*30, shape=[5, 3, 2], format='i3s')
        nd2 = ex2[1:3:, ::-2]
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

    eleza test_memoryview_compare_multidim_zero_shape(self):

        # zeros kwenye shape
        nd1 = ndarray(list(range(30)), shape=[0, 3, 2], format='i')
        nd2 = ndarray(list(range(30)), shape=[5, 0, 2], format='@i')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # zeros kwenye shape, struct module
        nd1 = ndarray(list(range(30)), shape=[0, 3, 2], format='i')
        nd2 = ndarray(list(range(30)), shape=[5, 0, 2], format='@i')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

    eleza test_memoryview_compare_multidim_zero_strides(self):

        # zero strides
        nd1 = ndarray([900]*80, shape=[4, 5, 4], format='@L')
        nd2 = ndarray([900], shape=[4, 5, 4], strides=[0, 0, 0], format='L')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)
        self.assertEqual(v.tolist(), w.tolist())

        # zero strides, struct module
        nd1 = ndarray([(1, 2)]*10, shape=[2, 5], format='=lQ')
        nd2 = ndarray([(1, 2)], shape=[2, 5], strides=[0, 0], format='<lQ')
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

    eleza test_memoryview_compare_multidim_suboffsets(self):

        # suboffsets
        ex1 = ndarray(list(range(40)), shape=[5, 8], format='@I')
        nd1 = ex1[3:1:-1, ::-2]
        ex2 = ndarray(list(range(40)), shape=[5, 8], format='I', flags=ND_PIL)
        nd2 = ex2[1:3:1, ::-2]
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # suboffsets, struct module
        ex1 = ndarray([(2**64-1, -1)]*40, shape=[5, 8], format='=Qq',
                      flags=ND_WRITABLE)
        ex1[2][7] = (1, -2)
        nd1 = ex1[3:1:-1, ::-2]

        ex2 = ndarray([(2**64-1, -1)]*40, shape=[5, 8], format='>Qq',
                      flags=ND_PIL|ND_WRITABLE)
        ex2[2][7] = (1, -2)
        nd2 = ex2[1:3:1, ::-2]

        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

        # suboffsets, different shape
        ex1 = ndarray(list(range(30)), shape=[2, 3, 5], format='b',
                      flags=ND_PIL)
        nd1 = ex1[1:3:, ::-2]
        nd2 = ndarray(list(range(30)), shape=[3, 2, 5], format='b')
        nd2 = ex2[1:3:, ::-2]
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # suboffsets, different shape, struct module
        ex1 = ndarray([(2**8-1, -1)]*40, shape=[2, 3, 5], format='Bb',
                      flags=ND_PIL|ND_WRITABLE)
        nd1 = ex1[1:2:, ::-2]

        ex2 = ndarray([(2**8-1, -1)]*40, shape=[3, 2, 5], format='Bb')
        nd2 = ex2[1:2:, ::-2]

        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # suboffsets, different format
        ex1 = ndarray(list(range(30)), shape=[5, 3, 2], format='i', flags=ND_PIL)
        nd1 = ex1[1:3:, ::-2]
        ex2 = ndarray(list(range(30)), shape=[5, 3, 2], format='@I', flags=ND_PIL)
        nd2 = ex2[1:3:, ::-2]
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, nd2)
        self.assertEqual(w, nd1)
        self.assertEqual(v, w)

        # suboffsets, different format, struct module
        ex1 = ndarray([(b'hello', b'', 1)]*27, shape=[3, 3, 3], format='5s0sP',
                      flags=ND_PIL|ND_WRITABLE)
        ex1[1][2][2] = (b'sushi', b'', 1)
        nd1 = ex1[1:3:, ::-2]

        ex2 = ndarray([(b'hello', b'', 1)]*27, shape=[3, 3, 3], format='5s0sP',
                      flags=ND_PIL|ND_WRITABLE)
        ex1[1][2][2] = (b'sushi', b'', 1)
        nd2 = ex2[1:3:, ::-2]

        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertNotEqual(v, nd2)
        self.assertNotEqual(w, nd1)
        self.assertNotEqual(v, w)

        # initialize mixed C/Fortran + suboffsets
        lst1 = list(range(-15, 15))
        lst2 = transpose(lst1, [3, 2, 5])
        nd1 = ndarray(lst1, shape=[3, 2, 5], format='@l', flags=ND_PIL)
        nd2 = ndarray(lst2, shape=[3, 2, 5], format='l', flags=ND_FORTRAN|ND_PIL)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, w)

        # initialize mixed C/Fortran + suboffsets, struct module
        lst1 = [(b'sashimi', b'sliced', 20.05)]*30
        lst1[11] = (b'ramen', b'spicy', 9.45)
        lst2 = transpose(lst1, [3, 2, 5])

        nd1 = ndarray(lst1, shape=[3, 2, 5], format='< 10p 9p d', flags=ND_PIL)
        nd2 = ndarray(lst2, shape=[3, 2, 5], format='> 10p 9p d',
                      flags=ND_FORTRAN|ND_PIL)
        v = memoryview(nd1)
        w = memoryview(nd2)

        self.assertEqual(v, nd1)
        self.assertEqual(w, nd2)
        self.assertEqual(v, w)

    eleza test_memoryview_compare_not_equal(self):

        # items sio equal
        kila byteorder kwenye ['=', '<', '>', '!']:
            x = ndarray([2**63]*120, shape=[3,5,2,2,2], format=byteorder+'Q')
            y = ndarray([2**63]*120, shape=[3,5,2,2,2], format=byteorder+'Q',
                        flags=ND_WRITABLE|ND_FORTRAN)
            y[2][3][1][1][1] = 1
            a = memoryview(x)
            b = memoryview(y)
            self.assertEqual(a, x)
            self.assertEqual(b, y)
            self.assertNotEqual(a, b)
            self.assertNotEqual(a, y)
            self.assertNotEqual(b, x)

            x = ndarray([(2**63, 2**31, 2**15)]*120, shape=[3,5,2,2,2],
                        format=byteorder+'QLH')
            y = ndarray([(2**63, 2**31, 2**15)]*120, shape=[3,5,2,2,2],
                        format=byteorder+'QLH', flags=ND_WRITABLE|ND_FORTRAN)
            y[2][3][1][1][1] = (1, 1, 1)
            a = memoryview(x)
            b = memoryview(y)
            self.assertEqual(a, x)
            self.assertEqual(b, y)
            self.assertNotEqual(a, b)
            self.assertNotEqual(a, y)
            self.assertNotEqual(b, x)

    eleza test_memoryview_check_released(self):

        a = array.array('d', [1.1, 2.2, 3.3])

        m = memoryview(a)
        m.release()

        # PyMemoryView_FromObject()
        self.assertRaises(ValueError, memoryview, m)
        # memoryview.cast()
        self.assertRaises(ValueError, m.cast, 'c')
        # getbuffer()
        self.assertRaises(ValueError, ndarray, m)
        # memoryview.tolist()
        self.assertRaises(ValueError, m.tolist)
        # memoryview.tobytes()
        self.assertRaises(ValueError, m.tobytes)
        # sequence
        self.assertRaises(ValueError, eval, "1.0 kwenye m", locals())
        # subscript
        self.assertRaises(ValueError, m.__getitem__, 0)
        # assignment
        self.assertRaises(ValueError, m.__setitem__, 0, 1)

        kila attr kwenye ('obj', 'nbytes', 'readonly', 'itemsize', 'format', 'ndim',
                     'shape', 'strides', 'suboffsets', 'c_contiguous',
                     'f_contiguous', 'contiguous'):
            self.assertRaises(ValueError, m.__getattribute__, attr)

        # richcompare
        b = array.array('d', [1.1, 2.2, 3.3])
        m1 = memoryview(a)
        m2 = memoryview(b)

        self.assertEqual(m1, m2)
        m1.release()
        self.assertNotEqual(m1, m2)
        self.assertNotEqual(m1, a)
        self.assertEqual(m1, m1)

    eleza test_memoryview_tobytes(self):
        # Many implicit tests are already kwenye self.verify().

        t = (-529, 576, -625, 676, -729)

        nd = ndarray(t, shape=[5], format='@h')
        m = memoryview(nd)
        self.assertEqual(m, nd)
        self.assertEqual(m.tobytes(), nd.tobytes())

        nd = ndarray([t], shape=[1], format='>hQiLl')
        m = memoryview(nd)
        self.assertEqual(m, nd)
        self.assertEqual(m.tobytes(), nd.tobytes())

        nd = ndarray([t kila _ kwenye range(12)], shape=[2,2,3], format='=hQiLl')
        m = memoryview(nd)
        self.assertEqual(m, nd)
        self.assertEqual(m.tobytes(), nd.tobytes())

        nd = ndarray([t kila _ kwenye range(120)], shape=[5,2,2,3,2],
                     format='<hQiLl')
        m = memoryview(nd)
        self.assertEqual(m, nd)
        self.assertEqual(m.tobytes(), nd.tobytes())

        # Unknown formats are handled: tobytes() purely depends on itemsize.
        ikiwa ctypes:
            # format: "T{>l:x:>l:y:}"
            kundi BEPoint(ctypes.BigEndianStructure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            point = BEPoint(100, 200)
            a = memoryview(point)
            self.assertEqual(a.tobytes(), bytes(point))

    eleza test_memoryview_get_contiguous(self):
        # Many implicit tests are already kwenye self.verify().

        # no buffer interface
        self.assertRaises(TypeError, get_contiguous, {}, PyBUF_READ, 'F')

        # writable request to read-only object
        self.assertRaises(BufferError, get_contiguous, b'x', PyBUF_WRITE, 'C')

        # writable request to non-contiguous object
        nd = ndarray([1, 2, 3], shape=[2], strides=[2])
        self.assertRaises(BufferError, get_contiguous, nd, PyBUF_WRITE, 'A')

        # scalar, read-only request kutoka read-only exporter
        nd = ndarray(9, shape=(), format="L")
        kila order kwenye ['C', 'F', 'A']:
            m = get_contiguous(nd, PyBUF_READ, order)
            self.assertEqual(m, nd)
            self.assertEqual(m[()], 9)

        # scalar, read-only request kutoka writable exporter
        nd = ndarray(9, shape=(), format="L", flags=ND_WRITABLE)
        kila order kwenye ['C', 'F', 'A']:
            m = get_contiguous(nd, PyBUF_READ, order)
            self.assertEqual(m, nd)
            self.assertEqual(m[()], 9)

        # scalar, writable request
        kila order kwenye ['C', 'F', 'A']:
            nd[()] = 9
            m = get_contiguous(nd, PyBUF_WRITE, order)
            self.assertEqual(m, nd)
            self.assertEqual(m[()], 9)

            m[()] = 10
            self.assertEqual(m[()], 10)
            self.assertEqual(nd[()], 10)

        # zeros kwenye shape
        nd = ndarray([1], shape=[0], format="L", flags=ND_WRITABLE)
        kila order kwenye ['C', 'F', 'A']:
            m = get_contiguous(nd, PyBUF_READ, order)
            self.assertRaises(IndexError, m.__getitem__, 0)
            self.assertEqual(m, nd)
            self.assertEqual(m.tolist(), [])

        nd = ndarray(list(range(8)), shape=[2, 0, 7], format="L",
                     flags=ND_WRITABLE)
        kila order kwenye ['C', 'F', 'A']:
            m = get_contiguous(nd, PyBUF_READ, order)
            self.assertEqual(ndarray(m).tolist(), [[], []])

        # one-dimensional
        nd = ndarray([1], shape=[1], format="h", flags=ND_WRITABLE)
        kila order kwenye ['C', 'F', 'A']:
            m = get_contiguous(nd, PyBUF_WRITE, order)
            self.assertEqual(m, nd)
            self.assertEqual(m.tolist(), nd.tolist())

        nd = ndarray([1, 2, 3], shape=[3], format="b", flags=ND_WRITABLE)
        kila order kwenye ['C', 'F', 'A']:
            m = get_contiguous(nd, PyBUF_WRITE, order)
            self.assertEqual(m, nd)
            self.assertEqual(m.tolist(), nd.tolist())

        # one-dimensional, non-contiguous
        nd = ndarray([1, 2, 3], shape=[2], strides=[2], flags=ND_WRITABLE)
        kila order kwenye ['C', 'F', 'A']:
            m = get_contiguous(nd, PyBUF_READ, order)
            self.assertEqual(m, nd)
            self.assertEqual(m.tolist(), nd.tolist())
            self.assertRaises(TypeError, m.__setitem__, 1, 20)
            self.assertEqual(m[1], 3)
            self.assertEqual(nd[1], 3)

        nd = nd[::-1]
        kila order kwenye ['C', 'F', 'A']:
            m = get_contiguous(nd, PyBUF_READ, order)
            self.assertEqual(m, nd)
            self.assertEqual(m.tolist(), nd.tolist())
            self.assertRaises(TypeError, m.__setitem__, 1, 20)
            self.assertEqual(m[1], 1)
            self.assertEqual(nd[1], 1)

        # multi-dimensional, contiguous input
        nd = ndarray(list(range(12)), shape=[3, 4], flags=ND_WRITABLE)
        kila order kwenye ['C', 'A']:
            m = get_contiguous(nd, PyBUF_WRITE, order)
            self.assertEqual(ndarray(m).tolist(), nd.tolist())

        self.assertRaises(BufferError, get_contiguous, nd, PyBUF_WRITE, 'F')
        m = get_contiguous(nd, PyBUF_READ, order)
        self.assertEqual(ndarray(m).tolist(), nd.tolist())

        nd = ndarray(list(range(12)), shape=[3, 4],
                     flags=ND_WRITABLE|ND_FORTRAN)
        kila order kwenye ['F', 'A']:
            m = get_contiguous(nd, PyBUF_WRITE, order)
            self.assertEqual(ndarray(m).tolist(), nd.tolist())

        self.assertRaises(BufferError, get_contiguous, nd, PyBUF_WRITE, 'C')
        m = get_contiguous(nd, PyBUF_READ, order)
        self.assertEqual(ndarray(m).tolist(), nd.tolist())

        # multi-dimensional, non-contiguous input
        nd = ndarray(list(range(12)), shape=[3, 4], flags=ND_WRITABLE|ND_PIL)
        kila order kwenye ['C', 'F', 'A']:
            self.assertRaises(BufferError, get_contiguous, nd, PyBUF_WRITE,
                              order)
            m = get_contiguous(nd, PyBUF_READ, order)
            self.assertEqual(ndarray(m).tolist(), nd.tolist())

        # flags
        nd = ndarray([1,2,3,4,5], shape=[3], strides=[2])
        m = get_contiguous(nd, PyBUF_READ, 'C')
        self.assertKweli(m.c_contiguous)

    eleza test_memoryview_serializing(self):

        # C-contiguous
        size = struct.calcsize('i')
        a = array.array('i', [1,2,3,4,5])
        m = memoryview(a)
        buf = io.BytesIO(m)
        b = bytearray(5*size)
        buf.readinto(b)
        self.assertEqual(m.tobytes(), b)

        # C-contiguous, multi-dimensional
        size = struct.calcsize('L')
        nd = ndarray(list(range(12)), shape=[2,3,2], format="L")
        m = memoryview(nd)
        buf = io.BytesIO(m)
        b = bytearray(2*3*2*size)
        buf.readinto(b)
        self.assertEqual(m.tobytes(), b)

        # Fortran contiguous, multi-dimensional
        #size = struct.calcsize('L')
        #nd = ndarray(list(range(12)), shape=[2,3,2], format="L",
        #             flags=ND_FORTRAN)
        #m = memoryview(nd)
        #buf = io.BytesIO(m)
        #b = bytearray(2*3*2*size)
        #buf.readinto(b)
        #self.assertEqual(m.tobytes(), b)

    eleza test_memoryview_hash(self):

        # bytes exporter
        b = bytes(list(range(12)))
        m = memoryview(b)
        self.assertEqual(hash(b), hash(m))

        # C-contiguous
        mc = m.cast('c', shape=[3,4])
        self.assertEqual(hash(mc), hash(b))

        # non-contiguous
        mx = m[::-2]
        b = bytes(list(range(12))[::-2])
        self.assertEqual(hash(mx), hash(b))

        # Fortran contiguous
        nd = ndarray(list(range(30)), shape=[3,2,5], flags=ND_FORTRAN)
        m = memoryview(nd)
        self.assertEqual(hash(m), hash(nd))

        # multi-dimensional slice
        nd = ndarray(list(range(30)), shape=[3,2,5])
        x = nd[::2, ::, ::-1]
        m = memoryview(x)
        self.assertEqual(hash(m), hash(x))

        # multi-dimensional slice ukijumuisha suboffsets
        nd = ndarray(list(range(30)), shape=[2,5,3], flags=ND_PIL)
        x = nd[::2, ::, ::-1]
        m = memoryview(x)
        self.assertEqual(hash(m), hash(x))

        # equality-hash invariant
        x = ndarray(list(range(12)), shape=[12], format='B')
        a = memoryview(x)

        y = ndarray(list(range(12)), shape=[12], format='b')
        b = memoryview(y)

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

        # non-byte formats
        nd = ndarray(list(range(12)), shape=[2,2,3], format='L')
        m = memoryview(nd)
        self.assertRaises(ValueError, m.__hash__)

        nd = ndarray(list(range(-6, 6)), shape=[2,2,3], format='h')
        m = memoryview(nd)
        self.assertRaises(ValueError, m.__hash__)

        nd = ndarray(list(range(12)), shape=[2,2,3], format='= L')
        m = memoryview(nd)
        self.assertRaises(ValueError, m.__hash__)

        nd = ndarray(list(range(-6, 6)), shape=[2,2,3], format='< h')
        m = memoryview(nd)
        self.assertRaises(ValueError, m.__hash__)

    eleza test_memoryview_release(self):

        # Create re-exporter kutoka getbuffer(memoryview), then release the view.
        a = bytearray([1,2,3])
        m = memoryview(a)
        nd = ndarray(m) # re-exporter
        self.assertRaises(BufferError, m.release)
        toa nd
        m.release()

        a = bytearray([1,2,3])
        m = memoryview(a)
        nd1 = ndarray(m, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        nd2 = ndarray(nd1, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        self.assertIs(nd2.obj, m)
        self.assertRaises(BufferError, m.release)
        toa nd1, nd2
        m.release()

        # chained views
        a = bytearray([1,2,3])
        m1 = memoryview(a)
        m2 = memoryview(m1)
        nd = ndarray(m2) # re-exporter
        m1.release()
        self.assertRaises(BufferError, m2.release)
        toa nd
        m2.release()

        a = bytearray([1,2,3])
        m1 = memoryview(a)
        m2 = memoryview(m1)
        nd1 = ndarray(m2, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        nd2 = ndarray(nd1, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        self.assertIs(nd2.obj, m2)
        m1.release()
        self.assertRaises(BufferError, m2.release)
        toa nd1, nd2
        m2.release()

        # Allow changing layout wakati buffers are exported.
        nd = ndarray([1,2,3], shape=[3], flags=ND_VAREXPORT)
        m1 = memoryview(nd)

        nd.push([4,5,6,7,8], shape=[5]) # mutate nd
        m2 = memoryview(nd)

        x = memoryview(m1)
        self.assertEqual(x.tolist(), m1.tolist())

        y = memoryview(m2)
        self.assertEqual(y.tolist(), m2.tolist())
        self.assertEqual(y.tolist(), nd.tolist())
        m2.release()
        y.release()

        nd.pop() # pop the current view
        self.assertEqual(x.tolist(), nd.tolist())

        toa nd
        m1.release()
        x.release()

        # If multiple memoryviews share the same managed buffer, implicit
        # release() kwenye the context manager's __exit__() method should still
        # work.
        eleza catch22(b):
            ukijumuisha memoryview(b) kama m2:
                pita

        x = bytearray(b'123')
        ukijumuisha memoryview(x) kama m1:
            catch22(m1)
            self.assertEqual(m1[0], ord(b'1'))

        x = ndarray(list(range(12)), shape=[2,2,3], format='l')
        y = ndarray(x, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        z = ndarray(y, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        self.assertIs(z.obj, x)
        ukijumuisha memoryview(z) kama m:
            catch22(m)
            self.assertEqual(m[0:1].tolist(), [[[0, 1, 2], [3, 4, 5]]])

        # Test garbage collection.
        kila flags kwenye (0, ND_REDIRECT):
            x = bytearray(b'123')
            ukijumuisha memoryview(x) kama m1:
                toa x
                y = ndarray(m1, getbuf=PyBUF_FULL_RO, flags=flags)
                ukijumuisha memoryview(y) kama m2:
                    toa y
                    z = ndarray(m2, getbuf=PyBUF_FULL_RO, flags=flags)
                    ukijumuisha memoryview(z) kama m3:
                        toa z
                        catch22(m3)
                        catch22(m2)
                        catch22(m1)
                        self.assertEqual(m1[0], ord(b'1'))
                        self.assertEqual(m2[1], ord(b'2'))
                        self.assertEqual(m3[2], ord(b'3'))
                        toa m3
                    toa m2
                toa m1

            x = bytearray(b'123')
            ukijumuisha memoryview(x) kama m1:
                toa x
                y = ndarray(m1, getbuf=PyBUF_FULL_RO, flags=flags)
                ukijumuisha memoryview(y) kama m2:
                    toa y
                    z = ndarray(m2, getbuf=PyBUF_FULL_RO, flags=flags)
                    ukijumuisha memoryview(z) kama m3:
                        toa z
                        catch22(m1)
                        catch22(m2)
                        catch22(m3)
                        self.assertEqual(m1[0], ord(b'1'))
                        self.assertEqual(m2[1], ord(b'2'))
                        self.assertEqual(m3[2], ord(b'3'))
                        toa m1, m2, m3

        # memoryview.release() fails ikiwa the view has exported buffers.
        x = bytearray(b'123')
        ukijumuisha self.assertRaises(BufferError):
            ukijumuisha memoryview(x) kama m:
                ex = ndarray(m)
                m[0] == ord(b'1')

    eleza test_memoryview_redirect(self):

        nd = ndarray([1.0 * x kila x kwenye range(12)], shape=[12], format='d')
        a = array.array('d', [1.0 * x kila x kwenye range(12)])

        kila x kwenye (nd, a):
            y = ndarray(x, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
            z = ndarray(y, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
            m = memoryview(z)

            self.assertIs(y.obj, x)
            self.assertIs(z.obj, x)
            self.assertIs(m.obj, x)

            self.assertEqual(m, x)
            self.assertEqual(m, y)
            self.assertEqual(m, z)

            self.assertEqual(m[1:3], x[1:3])
            self.assertEqual(m[1:3], y[1:3])
            self.assertEqual(m[1:3], z[1:3])
            toa y, z
            self.assertEqual(m[1:3], x[1:3])

    eleza test_memoryview_from_static_exporter(self):

        fmt = 'B'
        lst = [0,1,2,3,4,5,6,7,8,9,10,11]

        # exceptions
        self.assertRaises(TypeError, staticarray, 1, 2, 3)

        # view.obj==x
        x = staticarray()
        y = memoryview(x)
        self.verify(y, obj=x,
                    itemsize=1, fmt=fmt, readonly=Kweli,
                    ndim=1, shape=[12], strides=[1],
                    lst=lst)
        kila i kwenye range(12):
            self.assertEqual(y[i], i)
        toa x
        toa y

        x = staticarray()
        y = memoryview(x)
        toa y
        toa x

        x = staticarray()
        y = ndarray(x, getbuf=PyBUF_FULL_RO)
        z = ndarray(y, getbuf=PyBUF_FULL_RO)
        m = memoryview(z)
        self.assertIs(y.obj, x)
        self.assertIs(m.obj, z)
        self.verify(m, obj=z,
                    itemsize=1, fmt=fmt, readonly=Kweli,
                    ndim=1, shape=[12], strides=[1],
                    lst=lst)
        toa x, y, z, m

        x = staticarray()
        y = ndarray(x, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        z = ndarray(y, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        m = memoryview(z)
        self.assertIs(y.obj, x)
        self.assertIs(z.obj, x)
        self.assertIs(m.obj, x)
        self.verify(m, obj=x,
                    itemsize=1, fmt=fmt, readonly=Kweli,
                    ndim=1, shape=[12], strides=[1],
                    lst=lst)
        toa x, y, z, m

        # view.obj==NULL
        x = staticarray(legacy_mode=Kweli)
        y = memoryview(x)
        self.verify(y, obj=Tupu,
                    itemsize=1, fmt=fmt, readonly=Kweli,
                    ndim=1, shape=[12], strides=[1],
                    lst=lst)
        kila i kwenye range(12):
            self.assertEqual(y[i], i)
        toa x
        toa y

        x = staticarray(legacy_mode=Kweli)
        y = memoryview(x)
        toa y
        toa x

        x = staticarray(legacy_mode=Kweli)
        y = ndarray(x, getbuf=PyBUF_FULL_RO)
        z = ndarray(y, getbuf=PyBUF_FULL_RO)
        m = memoryview(z)
        self.assertIs(y.obj, Tupu)
        self.assertIs(m.obj, z)
        self.verify(m, obj=z,
                    itemsize=1, fmt=fmt, readonly=Kweli,
                    ndim=1, shape=[12], strides=[1],
                    lst=lst)
        toa x, y, z, m

        x = staticarray(legacy_mode=Kweli)
        y = ndarray(x, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        z = ndarray(y, getbuf=PyBUF_FULL_RO, flags=ND_REDIRECT)
        m = memoryview(z)
        # Clearly setting view.obj==NULL ni inferior, since it
        # messes up the redirection chain:
        self.assertIs(y.obj, Tupu)
        self.assertIs(z.obj, y)
        self.assertIs(m.obj, y)
        self.verify(m, obj=y,
                    itemsize=1, fmt=fmt, readonly=Kweli,
                    ndim=1, shape=[12], strides=[1],
                    lst=lst)
        toa x, y, z, m

    eleza test_memoryview_getbuffer_undefined(self):

        # getbufferproc does sio adhere to the new documentation
        nd = ndarray([1,2,3], [3], flags=ND_GETBUF_FAIL|ND_GETBUF_UNDEFINED)
        self.assertRaises(BufferError, memoryview, nd)

    eleza test_issue_7385(self):
        x = ndarray([1,2,3], shape=[3], flags=ND_GETBUF_FAIL)
        self.assertRaises(BufferError, memoryview, x)


ikiwa __name__ == "__main__":
    unittest.main()
