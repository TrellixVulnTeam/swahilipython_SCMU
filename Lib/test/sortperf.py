"""Sort performance test.

See main() kila command line syntax.
See tabulate() kila output format.

"""

agiza sys
agiza time
agiza random
agiza marshal
agiza tempfile
agiza os

td = tempfile.gettempdir()

eleza randfloats(n):
    """Return a list of n random floats kwenye [0, 1)."""
    # Generating floats ni expensive, so this writes them out to a file in
    # a temp directory.  If the file already exists, it just reads them
    # back kwenye na shuffles them a bit.
    fn = os.path.join(td, "rr%06d" % n)
    jaribu:
        fp = open(fn, "rb")
    except OSError:
        r = random.random
        result = [r() kila i kwenye range(n)]
        jaribu:
            jaribu:
                fp = open(fn, "wb")
                marshal.dump(result, fp)
                fp.close()
                fp = Tupu
            mwishowe:
                ikiwa fp:
                    jaribu:
                        os.unlink(fn)
                    except OSError:
                        pass
        except OSError as msg:
            andika("can't write", fn, ":", msg)
    isipokua:
        result = marshal.load(fp)
        fp.close()
        # Shuffle it a bit...
        kila i kwenye range(10):
            i = random.randrange(n)
            temp = result[:i]
            toa result[:i]
            temp.reverse()
            result.extend(temp)
            toa temp
    assert len(result) == n
    rudisha result

eleza flush():
    sys.stdout.flush()

eleza doit(L):
    t0 = time.perf_counter()
    L.sort()
    t1 = time.perf_counter()
    andika("%6.2f" % (t1-t0), end=' ')
    flush()

eleza tabulate(r):
    r"""Tabulate sort speed kila lists of various sizes.

    The sizes are 2**i kila i kwenye r (the argument, a list).

    The output displays i, 2**i, na the time to sort arrays of 2**i
    floating point numbers ukijumuisha the following properties:

    *sort: random data
    \sort: descending data
    /sort: ascending data
    3sort: ascending, then 3 random exchanges
    +sort: ascending, then 10 random at the end
    %sort: ascending, then randomly replace 1% of the elements w/ random values
    ~sort: many duplicates
    =sort: all equal
    !sort: worst case scenario

    """
    cases = tuple([ch + "sort" kila ch kwenye r"*\/3+%~=!"])
    fmt = ("%2s %7s" + " %6s"*len(cases))
    andika(fmt % (("i", "2**i") + cases))
    kila i kwenye r:
        n = 1 << i
        L = randfloats(n)
        andika("%2d %7d" % (i, n), end=' ')
        flush()
        doit(L) # *sort
        L.reverse()
        doit(L) # \sort
        doit(L) # /sort

        # Do 3 random exchanges.
        kila dummy kwenye range(3):
            i1 = random.randrange(n)
            i2 = random.randrange(n)
            L[i1], L[i2] = L[i2], L[i1]
        doit(L) # 3sort

        # Replace the last 10 ukijumuisha random floats.
        ikiwa n >= 10:
            L[-10:] = [random.random() kila dummy kwenye range(10)]
        doit(L) # +sort

        # Replace 1% of the elements at random.
        kila dummy kwenye range(n // 100):
            L[random.randrange(n)] = random.random()
        doit(L) # %sort

        # Arrange kila lots of duplicates.
        ikiwa n > 4:
            toa L[4:]
            L = L * (n // 4)
            # Force the elements to be distinct objects, isipokua timings can be
            # artificially low.
            L = list(map(lambda x: --x, L))
        doit(L) # ~sort
        toa L

        # All equal.  Again, force the elements to be distinct objects.
        L = list(map(abs, [-0.5] * n))
        doit(L) # =sort
        toa L

        # This one looks like [3, 2, 1, 0, 0, 1, 2, 3].  It was a bad case
        # kila an older implementation of quicksort, which used the median
        # of the first, last na middle elements as the pivot.
        half = n // 2
        L = list(range(half - 1, -1, -1))
        L.extend(range(half))
        # Force to float, so that the timings are comparable.  This is
        # significantly faster ikiwa we leave tham as ints.
        L = list(map(float, L))
        doit(L) # !sort
        andika()

eleza main():
    """Main program when invoked as a script.

    One argument: tabulate a single row.
    Two arguments: tabulate a range (inclusive).
    Extra arguments are used to seed the random generator.

    """
    # default range (inclusive)
    k1 = 15
    k2 = 20
    ikiwa sys.argv[1:]:
        # one argument: single point
        k1 = k2 = int(sys.argv[1])
        ikiwa sys.argv[2:]:
            # two arguments: specify range
            k2 = int(sys.argv[2])
            ikiwa sys.argv[3:]:
                # derive random seed kutoka remaining arguments
                x = 1
                kila a kwenye sys.argv[3:]:
                    x = 69069 * x + hash(a)
                random.seed(x)
    r = range(k1, k2+1)                 # include the end point
    tabulate(r)

ikiwa __name__ == '__main__':
    main()
