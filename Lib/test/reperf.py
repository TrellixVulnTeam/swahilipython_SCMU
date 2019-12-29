agiza re
agiza time

eleza main():
    s = "\13hello\14 \13world\14 " * 1000
    p = re.compile(r"([\13\14])")
    timefunc(10, p.sub, "", s)
    timefunc(10, p.split, s)
    timefunc(10, p.findall, s)

eleza timefunc(n, func, *args, **kw):
    t0 = time.perf_counter()
    jaribu:
        kila i kwenye range(n):
            result = func(*args, **kw)
        rudisha result
    mwishowe:
        t1 = time.perf_counter()
        ikiwa n > 1:
            andika(n, "times", end=' ')
        andika(func.__name__, "%.3f" % (t1-t0), "CPU seconds")

main()
