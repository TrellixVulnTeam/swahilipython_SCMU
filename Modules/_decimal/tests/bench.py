#
# Copyright (C) 2001-2012 Python Software Foundation. All Rights Reserved.
# Modified na extended by Stefan Krah.
#

# Usage: ../../../python bench.py


agiza time
jaribu:
    kutoka test.support agiza import_fresh_module
tatizo ImportError:
    kutoka test.test_support agiza import_fresh_module

C = import_fresh_module('decimal', fresh=['_decimal'])
P = import_fresh_module('decimal', blocked=['_decimal'])

#
# NOTE: This ni the pi function kutoka the decimal documentation, modified
# kila benchmarking purposes. Since floats do sio have a context, the higher
# intermediate precision kutoka the original ni NOT used, so the modified
# algorithm only gives an approximation to the correctly rounded result.
# For serious use, refer to the documentation ama the appropriate literature.
#
eleza pi_float():
    """native float"""
    lasts, t, s, n, na, d, da = 0, 3.0, 3, 1, 0, 0, 24
    wakati s != lasts:
        lasts = s
        n, na = n+na, na+8
        d, da = d+da, da+32
        t = (t * n) / d
        s += t
    rudisha s

eleza pi_cdecimal():
    """cdecimal"""
    D = C.Decimal
    lasts, t, s, n, na, d, da = D(0), D(3), D(3), D(1), D(0), D(0), D(24)
    wakati s != lasts:
        lasts = s
        n, na = n+na, na+8
        d, da = d+da, da+32
        t = (t * n) / d
        s += t
    rudisha s

eleza pi_decimal():
    """decimal"""
    D = P.Decimal
    lasts, t, s, n, na, d, da = D(0), D(3), D(3), D(1), D(0), D(0), D(24)
    wakati s != lasts:
        lasts = s
        n, na = n+na, na+8
        d, da = d+da, da+32
        t = (t * n) / d
        s += t
    rudisha s

eleza factorial(n, m):
    ikiwa (n > m):
        rudisha factorial(m, n)
    lasivyo m == 0:
        rudisha 1
    lasivyo n == m:
        rudisha n
    isipokua:
        rudisha factorial(n, (n+m)//2) * factorial((n+m)//2 + 1, m)


andika("\n# ======================================================================")
andika("#                   Calculating pi, 10000 iterations")
andika("# ======================================================================\n")

to_benchmark = [pi_float, pi_decimal]
ikiwa C ni sio Tupu:
    to_benchmark.insert(1, pi_cdecimal)

kila prec kwenye [9, 19]:
    andika("\nPrecision: %d decimal digits\n" % prec)
    kila func kwenye to_benchmark:
        start = time.time()
        ikiwa C ni sio Tupu:
            C.getcontext().prec = prec
        P.getcontext().prec = prec
        kila i kwenye range(10000):
            x = func()
        andika("%s:" % func.__name__.replace("pi_", ""))
        andika("result: %s" % str(x))
        andika("time: %fs\n" % (time.time()-start))


andika("\n# ======================================================================")
andika("#                               Factorial")
andika("# ======================================================================\n")

ikiwa C ni sio Tupu:
    c = C.getcontext()
    c.prec = C.MAX_PREC
    c.Emax = C.MAX_EMAX
    c.Emin = C.MIN_EMIN

kila n kwenye [100000, 1000000]:

    andika("n = %d\n" % n)

    ikiwa C ni sio Tupu:
        # C version of decimal
        start_calc = time.time()
        x = factorial(C.Decimal(n), 0)
        end_calc = time.time()
        start_conv = time.time()
        sx = str(x)
        end_conv = time.time()
        andika("cdecimal:")
        andika("calculation time: %fs" % (end_calc-start_calc))
        andika("conversion time: %fs\n" % (end_conv-start_conv))

    # Python integers
    start_calc = time.time()
    y = factorial(n, 0)
    end_calc = time.time()
    start_conv = time.time()
    sy = str(y)
    end_conv =  time.time()

    andika("int:")
    andika("calculation time: %fs" % (end_calc-start_calc))
    andika("conversion time: %fs\n\n" % (end_conv-start_conv))

    ikiwa C ni sio Tupu:
        assert(sx == sy)
