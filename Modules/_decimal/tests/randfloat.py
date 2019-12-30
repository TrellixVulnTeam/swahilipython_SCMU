# Copyright (c) 2010 Python Software Foundation. All Rights Reserved.
# Adapted kutoka Python's Lib/test/test_strtod.py (by Mark Dickinson)

# More test cases kila deccheck.py.

agiza random

TEST_SIZE = 2


eleza test_short_halfway_cases():
    # exact halfway cases ukijumuisha a small number of significant digits
    kila k kwenye 0, 5, 10, 15, 20:
        # upper = smallest integer >= 2**54/5**k
        upper = -(-2**54//5**k)
        # lower = smallest odd number >= 2**53/5**k
        lower = -(-2**53//5**k)
        ikiwa lower % 2 == 0:
            lower += 1
        kila i kwenye range(10 * TEST_SIZE):
            # Select a random odd n kwenye [2**53/5**k,
            # 2**54/5**k). Then n * 10**k gives a halfway case
            # ukijumuisha small number of significant digits.
            n, e = random.randrange(lower, upper, 2), k

            # Remove any additional powers of 5.
            wakati n % 5 == 0:
                n, e = n // 5, e + 1
            assert n % 10 kwenye (1, 3, 7, 9)

            # Try numbers of the form n * 2**p2 * 10**e, p2 >= 0,
            # until n * 2**p2 has more than 20 significant digits.
            digits, exponent = n, e
            wakati digits < 10**20:
                s = '{}e{}'.format(digits, exponent)
                tuma s
                # Same again, but ukijumuisha extra trailing zeros.
                s = '{}e{}'.format(digits * 10**40, exponent - 40)
                tuma s
                digits *= 2

            # Try numbers of the form n * 5**p2 * 10**(e - p5), p5
            # >= 0, ukijumuisha n * 5**p5 < 10**20.
            digits, exponent = n, e
            wakati digits < 10**20:
                s = '{}e{}'.format(digits, exponent)
                tuma s
                # Same again, but ukijumuisha extra trailing zeros.
                s = '{}e{}'.format(digits * 10**40, exponent - 40)
                tuma s
                digits *= 5
                exponent -= 1

eleza test_halfway_cases():
    # test halfway cases kila the round-half-to-even rule
    kila i kwenye range(1000):
        kila j kwenye range(TEST_SIZE):
            # bit pattern kila a random finite positive (or +0.0) float
            bits = random.randrange(2047*2**52)

            # convert bit pattern to a number of the form m * 2**e
            e, m = divmod(bits, 2**52)
            ikiwa e:
                m, e = m + 2**52, e - 1
            e -= 1074

            # add 0.5 ulps
            m, e = 2*m + 1, e - 1

            # convert to a decimal string
            ikiwa e >= 0:
                digits = m << e
                exponent = 0
            isipokua:
                # m * 2**e = (m * 5**-e) * 10**e
                digits = m * 5**-e
                exponent = e
            s = '{}e{}'.format(digits, exponent)
            tuma s

eleza test_boundaries():
    # boundaries expressed kama triples (n, e, u), where
    # n*10**e ni an approximation to the boundary value na
    # u*10**e ni 1ulp
    boundaries = [
        (10000000000000000000, -19, 1110),   # a power of 2 boundary (1.0)
        (17976931348623159077, 289, 1995),   # overflow boundary (2.**1024)
        (22250738585072013831, -327, 4941),  # normal/subnormal (2.**-1022)
        (0, -327, 4941),                     # zero
        ]
    kila n, e, u kwenye boundaries:
        kila j kwenye range(1000):
            kila i kwenye range(TEST_SIZE):
                digits = n + random.randrange(-3*u, 3*u)
                exponent = e
                s = '{}e{}'.format(digits, exponent)
                tuma s
            n *= 10
            u *= 10
            e -= 1

eleza test_underflow_boundary():
    # test values close to 2**-1075, the underflow boundary; similar
    # to boundary_tests, tatizo that the random error doesn't scale
    # ukijumuisha n
    kila exponent kwenye range(-400, -320):
        base = 10**-exponent // 2**1075
        kila j kwenye range(TEST_SIZE):
            digits = base + random.randrange(-1000, 1000)
            s = '{}e{}'.format(digits, exponent)
            tuma s

eleza test_bigcomp():
    kila ndigs kwenye 5, 10, 14, 15, 16, 17, 18, 19, 20, 40, 41, 50:
        dig10 = 10**ndigs
        kila i kwenye range(100 * TEST_SIZE):
            digits = random.randrange(dig10)
            exponent = random.randrange(-400, 400)
            s = '{}e{}'.format(digits, exponent)
            tuma s

eleza test_parsing():
    # make '0' more likely to be chosen than other digits
    digits = '000000123456789'
    signs = ('+', '-', '')

    # put together random short valid strings
    # \d*[.\d*]?e
    kila i kwenye range(1000):
        kila j kwenye range(TEST_SIZE):
            s = random.choice(signs)
            intpart_len = random.randrange(5)
            s += ''.join(random.choice(digits) kila _ kwenye range(intpart_len))
            ikiwa random.choice([Kweli, Uongo]):
                s += '.'
                fracpart_len = random.randrange(5)
                s += ''.join(random.choice(digits)
                             kila _ kwenye range(fracpart_len))
            isipokua:
                fracpart_len = 0
            ikiwa random.choice([Kweli, Uongo]):
                s += random.choice(['e', 'E'])
                s += random.choice(signs)
                exponent_len = random.randrange(1, 4)
                s += ''.join(random.choice(digits)
                             kila _ kwenye range(exponent_len))

            ikiwa intpart_len + fracpart_len:
                tuma s

test_particular = [
     # squares
    '1.00000000100000000025',
    '1.0000000000000000000000000100000000000000000000000' #...
    '00025',
    '1.0000000000000000000000000000000000000000000010000' #...
    '0000000000000000000000000000000000000000025',
    '1.0000000000000000000000000000000000000000000000000' #...
    '000001000000000000000000000000000000000000000000000' #...
    '000000000025',
    '0.99999999900000000025',
    '0.9999999999999999999999999999999999999999999999999' #...
    '999000000000000000000000000000000000000000000000000' #...
    '000025',
    '0.9999999999999999999999999999999999999999999999999' #...
    '999999999999999999999999999999999999999999999999999' #...
    '999999999999999999999999999999999999999990000000000' #...
    '000000000000000000000000000000000000000000000000000' #...
    '000000000000000000000000000000000000000000000000000' #...
    '0000000000000000000000000000025',

    '1.0000000000000000000000000000000000000000000000000' #...
    '000000000000000000000000000000000000000000000000000' #...
    '100000000000000000000000000000000000000000000000000' #...
    '000000000000000000000000000000000000000000000000001',
    '1.0000000000000000000000000000000000000000000000000' #...
    '000000000000000000000000000000000000000000000000000' #...
    '500000000000000000000000000000000000000000000000000' #...
    '000000000000000000000000000000000000000000000000005',
    '1.0000000000000000000000000000000000000000000000000' #...
    '000000000100000000000000000000000000000000000000000' #...
    '000000000000000000250000000000000002000000000000000' #...
    '000000000000000000000000000000000000000000010000000' #...
    '000000000000000000000000000000000000000000000000000' #...
    '0000000000000000001',
    '1.0000000000000000000000000000000000000000000000000' #...
    '000000000100000000000000000000000000000000000000000' #...
    '000000000000000000249999999999999999999999999999999' #...
    '999999999999979999999999999999999999999999999999999' #...
    '999999999999999999999900000000000000000000000000000' #...
    '000000000000000000000000000000000000000000000000000' #...
    '00000000000000000000000001',

    '0.9999999999999999999999999999999999999999999999999' #...
    '999999999900000000000000000000000000000000000000000' #...
    '000000000000000000249999999999999998000000000000000' #...
    '000000000000000000000000000000000000000000010000000' #...
    '000000000000000000000000000000000000000000000000000' #...
    '0000000000000000001',
    '0.9999999999999999999999999999999999999999999999999' #...
    '999999999900000000000000000000000000000000000000000' #...
    '000000000000000000250000001999999999999999999999999' #...
    '999999999999999999999999999999999990000000000000000' #...
    '000000000000000000000000000000000000000000000000000' #...
    '1',

    # tough cases kila ln etc.
    '1.000000000000000000000000000000000000000000000000' #...
    '00000000000000000000000000000000000000000000000000' #...
    '00100000000000000000000000000000000000000000000000' #...
    '00000000000000000000000000000000000000000000000000' #...
    '0001',
    '0.999999999999999999999999999999999999999999999999' #...
    '99999999999999999999999999999999999999999999999999' #...
    '99899999999999999999999999999999999999999999999999' #...
    '99999999999999999999999999999999999999999999999999' #...
    '99999999999999999999999999999999999999999999999999' #...
    '9999'
    ]


TESTCASES = [
      [x kila x kwenye test_short_halfway_cases()],
      [x kila x kwenye test_halfway_cases()],
      [x kila x kwenye test_boundaries()],
      [x kila x kwenye test_underflow_boundary()],
      [x kila x kwenye test_bigcomp()],
      [x kila x kwenye test_parsing()],
      test_particular
]

eleza un_randfloat():
    kila i kwenye range(1000):
        l = random.choice(TESTCASES[:6])
        tuma random.choice(l)
    kila v kwenye test_particular:
        tuma v

eleza bin_randfloat():
    kila i kwenye range(1000):
        l1 = random.choice(TESTCASES)
        l2 = random.choice(TESTCASES)
        tuma random.choice(l1), random.choice(l2)

eleza tern_randfloat():
    kila i kwenye range(1000):
        l1 = random.choice(TESTCASES)
        l2 = random.choice(TESTCASES)
        l3 = random.choice(TESTCASES)
        tuma random.choice(l1), random.choice(l2), random.choice(l3)
