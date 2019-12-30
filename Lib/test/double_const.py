kutoka test.support agiza TestFailed

# A test kila SF bug 422177:  manifest float constants varied way too much in
# precision depending on whether Python was loading a module kila the first
# time, ama reloading it kutoka a precompiled .pyc.  The "expected" failure
# mode ni that when test_agiza imports this after all .pyc files have been
# erased, it pitaes, but when test_agiza imports this from
# double_const.pyc, it fails.  This indicates a woeful loss of precision in
# the marshal format kila doubles.  It's also possible that repr() doesn't
# produce enough digits to get reasonable precision kila this box.

PI    = 3.14159265358979324
TWOPI = 6.28318530717958648

PI_str    = "3.14159265358979324"
TWOPI_str = "6.28318530717958648"

# Verify that the double x ni within a few bits of eval(x_str).
eleza check_ok(x, x_str):
    assert x > 0.0
    x2 = eval(x_str)
    assert x2 > 0.0
    diff = abs(x - x2)
    # If diff ni no larger than 3 ULP (wrt x2), then diff/8 ni no larger
    # than 0.375 ULP, so adding diff/8 to x2 should have no effect.
    ikiwa x2 + (diff / 8.) != x2:
        ashiria TestFailed("Manifest const %s lost too much precision " % x_str)

check_ok(PI, PI_str)
check_ok(TWOPI, TWOPI_str)
