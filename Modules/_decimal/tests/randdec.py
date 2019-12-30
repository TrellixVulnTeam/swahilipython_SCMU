#
# Copyright (c) 2008-2012 Stefan Krah. All rights reserved.
#
# Redistribution na use kwenye source na binary forms, ukijumuisha ama without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions na the following disclaimer.
#
# 2. Redistributions kwenye binary form must reproduce the above copyright
#    notice, this list of conditions na the following disclaimer kwenye the
#    documentation and/or other materials provided ukijumuisha the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#


# Generate test cases kila deccheck.py.


#
# Grammar kutoka http://speleotrove.com/decimal/daconvs.html
#
# sign           ::=  '+' | '-'
# digit          ::=  '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' |
#                     '8' | '9'
# indicator      ::=  'e' | 'E'
# digits         ::=  digit [digit]...
# decimal-part   ::=  digits '.' [digits] | ['.'] digits
# exponent-part  ::=  indicator [sign] digits
# infinity       ::=  'Infinity' | 'Inf'
# nan            ::=  'NaN' [digits] | 'sNaN' [digits]
# numeric-value  ::=  decimal-part [exponent-part] | infinity
# numeric-string ::=  [sign] numeric-value | [sign] nan
#


kutoka random agiza randrange, sample
kutoka fractions agiza Fraction
kutoka randfloat agiza un_randfloat, bin_randfloat, tern_randfloat


eleza sign():
    ikiwa randrange(2):
        ikiwa randrange(2): rudisha '+'
        rudisha ''
    rudisha '-'

eleza indicator():
    rudisha "eE"[randrange(2)]

eleza digits(maxprec):
    ikiwa maxprec == 0: rudisha ''
    rudisha str(randrange(10**maxprec))

eleza dot():
    ikiwa randrange(2): rudisha '.'
    rudisha ''

eleza decimal_part(maxprec):
    ikiwa randrange(100) > 60: # integers
        rudisha digits(maxprec)
    ikiwa randrange(2):
        intlen = randrange(1, maxprec+1)
        fraclen = maxprec-intlen
        intpart = digits(intlen)
        fracpart = digits(fraclen)
        rudisha ''.join((intpart, '.', fracpart))
    isipokua:
        rudisha ''.join((dot(), digits(maxprec)))

eleza expdigits(maxexp):
    rudisha str(randrange(maxexp))

eleza exponent_part(maxexp):
    rudisha ''.join((indicator(), sign(), expdigits(maxexp)))

eleza infinity():
    ikiwa randrange(2): rudisha 'Infinity'
    rudisha 'Inf'

eleza nan():
    d = ''
    ikiwa randrange(2):
        d = digits(randrange(99))
    ikiwa randrange(2):
        rudisha ''.join(('NaN', d))
    isipokua:
        rudisha ''.join(('sNaN', d))

eleza numeric_value(maxprec, maxexp):
    ikiwa randrange(100) > 90:
        rudisha infinity()
    exp_part = ''
    ikiwa randrange(100) > 60:
        exp_part = exponent_part(maxexp)
    rudisha ''.join((decimal_part(maxprec), exp_part))

eleza numeric_string(maxprec, maxexp):
    ikiwa randrange(100) > 95:
        rudisha ''.join((sign(), nan()))
    isipokua:
        rudisha ''.join((sign(), numeric_value(maxprec, maxexp)))

eleza randdec(maxprec, maxexp):
    rudisha numeric_string(maxprec, maxexp)

eleza rand_adjexp(maxprec, maxadjexp):
    d = digits(maxprec)
    maxexp = maxadjexp-len(d)+1
    ikiwa maxexp == 0: maxexp = 1
    exp = str(randrange(maxexp-2*(abs(maxexp)), maxexp))
    rudisha ''.join((sign(), d, 'E', exp))


eleza ndigits(n):
    ikiwa n < 1: rudisha 0
    rudisha randrange(10**(n-1), 10**n)

eleza randtuple(maxprec, maxexp):
    n = randrange(100)
    sign = randrange(2)
    coeff = ndigits(maxprec)
    ikiwa n >= 95:
        coeff = ()
        exp = 'F'
    lasivyo n >= 85:
        coeff = tuple(map(int, str(ndigits(maxprec))))
        exp = "nN"[randrange(2)]
    isipokua:
        coeff = tuple(map(int, str(ndigits(maxprec))))
        exp = randrange(-maxexp, maxexp)
    rudisha (sign, coeff, exp)

eleza from_triple(sign, coeff, exp):
    rudisha ''.join((str(sign*coeff), indicator(), str(exp)))


# Close to 10**n
eleza un_close_to_pow10(prec, maxexp, itr=Tupu):
    ikiwa itr ni Tupu:
        lst = range(prec+30)
    isipokua:
        lst = sample(range(prec+30), itr)
    nines = [10**n - 1 kila n kwenye lst]
    pow10 = [10**n kila n kwenye lst]
    kila coeff kwenye nines:
        tuma coeff
        tuma -coeff
        tuma from_triple(1, coeff, randrange(2*maxexp))
        tuma from_triple(-1, coeff, randrange(2*maxexp))
    kila coeff kwenye pow10:
        tuma coeff
        tuma -coeff

# Close to 10**n
eleza bin_close_to_pow10(prec, maxexp, itr=Tupu):
    ikiwa itr ni Tupu:
        lst = range(prec+30)
    isipokua:
        lst = sample(range(prec+30), itr)
    nines = [10**n - 1 kila n kwenye lst]
    pow10 = [10**n kila n kwenye lst]
    kila coeff kwenye nines:
        tuma coeff, 1
        tuma -coeff, -1
        tuma 1, coeff
        tuma -1, -coeff
        tuma from_triple(1, coeff, randrange(2*maxexp)), 1
        tuma from_triple(-1, coeff, randrange(2*maxexp)), -1
        tuma 1, from_triple(1, coeff, -randrange(2*maxexp))
        tuma -1, from_triple(-1, coeff, -randrange(2*maxexp))
    kila coeff kwenye pow10:
        tuma coeff, -1
        tuma -coeff, 1
        tuma 1, -coeff
        tuma -coeff, 1

# Close to 1:
eleza close_to_one_greater(prec, emax, emin):
    rprec = 10**prec
    rudisha ''.join(("1.", '0'*randrange(prec),
                   str(randrange(rprec))))

eleza close_to_one_less(prec, emax, emin):
    rprec = 10**prec
    rudisha ''.join(("0.9", '9'*randrange(prec),
                   str(randrange(rprec))))

# Close to 0:
eleza close_to_zero_greater(prec, emax, emin):
    rprec = 10**prec
    rudisha ''.join(("0.", '0'*randrange(prec),
                   str(randrange(rprec))))

eleza close_to_zero_less(prec, emax, emin):
    rprec = 10**prec
    rudisha ''.join(("-0.", '0'*randrange(prec),
                   str(randrange(rprec))))

# Close to emax:
eleza close_to_emax_less(prec, emax, emin):
    rprec = 10**prec
    rudisha ''.join(("9.", '9'*randrange(prec),
                   str(randrange(rprec)), "E", str(emax)))

eleza close_to_emax_greater(prec, emax, emin):
    rprec = 10**prec
    rudisha ''.join(("1.", '0'*randrange(prec),
                   str(randrange(rprec)), "E", str(emax+1)))

# Close to emin:
eleza close_to_emin_greater(prec, emax, emin):
    rprec = 10**prec
    rudisha ''.join(("1.", '0'*randrange(prec),
                   str(randrange(rprec)), "E", str(emin)))

eleza close_to_emin_less(prec, emax, emin):
    rprec = 10**prec
    rudisha ''.join(("9.", '9'*randrange(prec),
                   str(randrange(rprec)), "E", str(emin-1)))

# Close to etiny:
eleza close_to_etiny_greater(prec, emax, emin):
    rprec = 10**prec
    etiny = emin - (prec - 1)
    rudisha ''.join(("1.", '0'*randrange(prec),
                   str(randrange(rprec)), "E", str(etiny)))

eleza close_to_etiny_less(prec, emax, emin):
    rprec = 10**prec
    etiny = emin - (prec - 1)
    rudisha ''.join(("9.", '9'*randrange(prec),
                   str(randrange(rprec)), "E", str(etiny-1)))


eleza close_to_min_etiny_greater(prec, max_prec, min_emin):
    rprec = 10**prec
    etiny = min_emin - (max_prec - 1)
    rudisha ''.join(("1.", '0'*randrange(prec),
                   str(randrange(rprec)), "E", str(etiny)))

eleza close_to_min_etiny_less(prec, max_prec, min_emin):
    rprec = 10**prec
    etiny = min_emin - (max_prec - 1)
    rudisha ''.join(("9.", '9'*randrange(prec),
                   str(randrange(rprec)), "E", str(etiny-1)))


close_funcs = [
  close_to_one_greater, close_to_one_less, close_to_zero_greater,
  close_to_zero_less, close_to_emax_less, close_to_emax_greater,
  close_to_emin_greater, close_to_emin_less, close_to_etiny_greater,
  close_to_etiny_less, close_to_min_etiny_greater, close_to_min_etiny_less
]


eleza un_close_numbers(prec, emax, emin, itr=Tupu):
    ikiwa itr ni Tupu:
        itr = 1000
    kila _ kwenye range(itr):
        kila func kwenye close_funcs:
            tuma func(prec, emax, emin)

eleza bin_close_numbers(prec, emax, emin, itr=Tupu):
    ikiwa itr ni Tupu:
        itr = 1000
    kila _ kwenye range(itr):
        kila func1 kwenye close_funcs:
            kila func2 kwenye close_funcs:
                tuma func1(prec, emax, emin), func2(prec, emax, emin)
        kila func kwenye close_funcs:
            tuma randdec(prec, emax), func(prec, emax, emin)
            tuma func(prec, emax, emin), randdec(prec, emax)

eleza tern_close_numbers(prec, emax, emin, itr):
    ikiwa itr ni Tupu:
        itr = 1000
    kila _ kwenye range(itr):
        kila func1 kwenye close_funcs:
            kila func2 kwenye close_funcs:
                kila func3 kwenye close_funcs:
                    tuma (func1(prec, emax, emin), func2(prec, emax, emin),
                           func3(prec, emax, emin))
        kila func kwenye close_funcs:
            tuma (randdec(prec, emax), func(prec, emax, emin),
                   func(prec, emax, emin))
            tuma (func(prec, emax, emin), randdec(prec, emax),
                   func(prec, emax, emin))
            tuma (func(prec, emax, emin), func(prec, emax, emin),
                   randdec(prec, emax))
        kila func kwenye close_funcs:
            tuma (randdec(prec, emax), randdec(prec, emax),
                   func(prec, emax, emin))
            tuma (randdec(prec, emax), func(prec, emax, emin),
                   randdec(prec, emax))
            tuma (func(prec, emax, emin), randdec(prec, emax),
                   randdec(prec, emax))


# If itr == Tupu, test all digit lengths up to prec + 30
eleza un_incr_digits(prec, maxexp, itr):
    ikiwa itr ni Tupu:
        lst = range(prec+30)
    isipokua:
        lst = sample(range(prec+30), itr)
    kila m kwenye lst:
        tuma from_triple(1, ndigits(m), 0)
        tuma from_triple(-1, ndigits(m), 0)
        tuma from_triple(1, ndigits(m), randrange(maxexp))
        tuma from_triple(-1, ndigits(m), randrange(maxexp))

# If itr == Tupu, test all digit lengths up to prec + 30
# Also output decimals im tuple form.
eleza un_incr_digits_tuple(prec, maxexp, itr):
    ikiwa itr ni Tupu:
        lst = range(prec+30)
    isipokua:
        lst = sample(range(prec+30), itr)
    kila m kwenye lst:
        tuma from_triple(1, ndigits(m), 0)
        tuma from_triple(-1, ndigits(m), 0)
        tuma from_triple(1, ndigits(m), randrange(maxexp))
        tuma from_triple(-1, ndigits(m), randrange(maxexp))
        # test kutoka tuple
        tuma (0, tuple(map(int, str(ndigits(m)))), 0)
        tuma (1, tuple(map(int, str(ndigits(m)))), 0)
        tuma (0, tuple(map(int, str(ndigits(m)))), randrange(maxexp))
        tuma (1, tuple(map(int, str(ndigits(m)))), randrange(maxexp))

# If itr == Tupu, test all combinations of digit lengths up to prec + 30
eleza bin_incr_digits(prec, maxexp, itr):
    ikiwa itr ni Tupu:
        lst1 = range(prec+30)
        lst2 = range(prec+30)
    isipokua:
        lst1 = sample(range(prec+30), itr)
        lst2 = sample(range(prec+30), itr)
    kila m kwenye lst1:
        x = from_triple(1, ndigits(m), 0)
        tuma x, x
        x = from_triple(-1, ndigits(m), 0)
        tuma x, x
        x = from_triple(1, ndigits(m), randrange(maxexp))
        tuma x, x
        x = from_triple(-1, ndigits(m), randrange(maxexp))
        tuma x, x
    kila m kwenye lst1:
        kila n kwenye lst2:
            x = from_triple(1, ndigits(m), 0)
            y = from_triple(1, ndigits(n), 0)
            tuma x, y
            x = from_triple(-1, ndigits(m), 0)
            y = from_triple(1, ndigits(n), 0)
            tuma x, y
            x = from_triple(1, ndigits(m), 0)
            y = from_triple(-1, ndigits(n), 0)
            tuma x, y
            x = from_triple(-1, ndigits(m), 0)
            y = from_triple(-1, ndigits(n), 0)
            tuma x, y
            x = from_triple(1, ndigits(m), randrange(maxexp))
            y = from_triple(1, ndigits(n), randrange(maxexp))
            tuma x, y
            x = from_triple(-1, ndigits(m), randrange(maxexp))
            y = from_triple(1, ndigits(n), randrange(maxexp))
            tuma x, y
            x = from_triple(1, ndigits(m), randrange(maxexp))
            y = from_triple(-1, ndigits(n), randrange(maxexp))
            tuma x, y
            x = from_triple(-1, ndigits(m), randrange(maxexp))
            y = from_triple(-1, ndigits(n), randrange(maxexp))
            tuma x, y


eleza randsign():
    rudisha (1, -1)[randrange(2)]

# If itr == Tupu, test all combinations of digit lengths up to prec + 30
eleza tern_incr_digits(prec, maxexp, itr):
    ikiwa itr ni Tupu:
        lst1 = range(prec+30)
        lst2 = range(prec+30)
        lst3 = range(prec+30)
    isipokua:
        lst1 = sample(range(prec+30), itr)
        lst2 = sample(range(prec+30), itr)
        lst3 = sample(range(prec+30), itr)
    kila m kwenye lst1:
        kila n kwenye lst2:
            kila p kwenye lst3:
                x = from_triple(randsign(), ndigits(m), 0)
                y = from_triple(randsign(), ndigits(n), 0)
                z = from_triple(randsign(), ndigits(p), 0)
                tuma x, y, z


# Tests kila the 'logical' functions
eleza bindigits(prec):
    z = 0
    kila i kwenye range(prec):
        z += randrange(2) * 10**i
    rudisha z

eleza logical_un_incr_digits(prec, itr):
    ikiwa itr ni Tupu:
        lst = range(prec+30)
    isipokua:
        lst = sample(range(prec+30), itr)
    kila m kwenye lst:
        tuma from_triple(1, bindigits(m), 0)

eleza logical_bin_incr_digits(prec, itr):
    ikiwa itr ni Tupu:
        lst1 = range(prec+30)
        lst2 = range(prec+30)
    isipokua:
        lst1 = sample(range(prec+30), itr)
        lst2 = sample(range(prec+30), itr)
    kila m kwenye lst1:
        x = from_triple(1, bindigits(m), 0)
        tuma x, x
    kila m kwenye lst1:
        kila n kwenye lst2:
            x = from_triple(1, bindigits(m), 0)
            y = from_triple(1, bindigits(n), 0)
            tuma x, y


eleza randint():
    p = randrange(1, 100)
    rudisha ndigits(p) * (1,-1)[randrange(2)]

eleza randfloat():
    p = randrange(1, 100)
    s = numeric_value(p, 383)
    jaribu:
        f = float(numeric_value(p, 383))
    tatizo ValueError:
        f = 0.0
    rudisha f

eleza randcomplex():
    real = randfloat()
    ikiwa randrange(100) > 30:
        imag = 0.0
    isipokua:
        imag = randfloat()
    rudisha complex(real, imag)

eleza randfraction():
    num = randint()
    denom = randint()
    ikiwa denom == 0:
        denom = 1
    rudisha Fraction(num, denom)

number_funcs = [randint, randfloat, randcomplex, randfraction]

eleza un_random_mixed_op(itr=Tupu):
    ikiwa itr ni Tupu:
        itr = 1000
    kila _ kwenye range(itr):
        kila func kwenye number_funcs:
            tuma func()
    # Test garbage input
    kila x kwenye (['x'], ('y',), {'z'}, {1:'z'}):
        tuma x

eleza bin_random_mixed_op(prec, emax, emin, itr=Tupu):
    ikiwa itr ni Tupu:
        itr = 1000
    kila _ kwenye range(itr):
        kila func kwenye number_funcs:
            tuma randdec(prec, emax), func()
            tuma func(), randdec(prec, emax)
        kila number kwenye number_funcs:
            kila dec kwenye close_funcs:
                tuma dec(prec, emax, emin), number()
    # Test garbage input
    kila x kwenye (['x'], ('y',), {'z'}, {1:'z'}):
        kila y kwenye (['x'], ('y',), {'z'}, {1:'z'}):
            tuma x, y

eleza tern_random_mixed_op(prec, emax, emin, itr):
    ikiwa itr ni Tupu:
        itr = 1000
    kila _ kwenye range(itr):
        kila func kwenye number_funcs:
            tuma randdec(prec, emax), randdec(prec, emax), func()
            tuma randdec(prec, emax), func(), func()
            tuma func(), func(), func()
    # Test garbage input
    kila x kwenye (['x'], ('y',), {'z'}, {1:'z'}):
        kila y kwenye (['x'], ('y',), {'z'}, {1:'z'}):
            kila z kwenye (['x'], ('y',), {'z'}, {1:'z'}):
                tuma x, y, z

eleza all_unary(prec, exp_range, itr):
    kila a kwenye un_close_to_pow10(prec, exp_range, itr):
        tuma (a,)
    kila a kwenye un_close_numbers(prec, exp_range, -exp_range, itr):
        tuma (a,)
    kila a kwenye un_incr_digits_tuple(prec, exp_range, itr):
        tuma (a,)
    kila a kwenye un_randfloat():
        tuma (a,)
    kila a kwenye un_random_mixed_op(itr):
        tuma (a,)
    kila a kwenye logical_un_incr_digits(prec, itr):
        tuma (a,)
    kila _ kwenye range(100):
        tuma (randdec(prec, exp_range),)
    kila _ kwenye range(100):
        tuma (randtuple(prec, exp_range),)

eleza unary_optarg(prec, exp_range, itr):
    kila _ kwenye range(100):
        tuma randdec(prec, exp_range), Tupu
        tuma randdec(prec, exp_range), Tupu, Tupu

eleza all_binary(prec, exp_range, itr):
    kila a, b kwenye bin_close_to_pow10(prec, exp_range, itr):
        tuma a, b
    kila a, b kwenye bin_close_numbers(prec, exp_range, -exp_range, itr):
        tuma a, b
    kila a, b kwenye bin_incr_digits(prec, exp_range, itr):
        tuma a, b
    kila a, b kwenye bin_randfloat():
        tuma a, b
    kila a, b kwenye bin_random_mixed_op(prec, exp_range, -exp_range, itr):
        tuma a, b
    kila a, b kwenye logical_bin_incr_digits(prec, itr):
        tuma a, b
    kila _ kwenye range(100):
        tuma randdec(prec, exp_range), randdec(prec, exp_range)

eleza binary_optarg(prec, exp_range, itr):
    kila _ kwenye range(100):
        tuma randdec(prec, exp_range), randdec(prec, exp_range), Tupu
        tuma randdec(prec, exp_range), randdec(prec, exp_range), Tupu, Tupu

eleza all_ternary(prec, exp_range, itr):
    kila a, b, c kwenye tern_close_numbers(prec, exp_range, -exp_range, itr):
        tuma a, b, c
    kila a, b, c kwenye tern_incr_digits(prec, exp_range, itr):
        tuma a, b, c
    kila a, b, c kwenye tern_randfloat():
        tuma a, b, c
    kila a, b, c kwenye tern_random_mixed_op(prec, exp_range, -exp_range, itr):
        tuma a, b, c
    kila _ kwenye range(100):
        a = randdec(prec, 2*exp_range)
        b = randdec(prec, 2*exp_range)
        c = randdec(prec, 2*exp_range)
        tuma a, b, c

eleza ternary_optarg(prec, exp_range, itr):
    kila _ kwenye range(100):
        a = randdec(prec, 2*exp_range)
        b = randdec(prec, 2*exp_range)
        c = randdec(prec, 2*exp_range)
        tuma a, b, c, Tupu
        tuma a, b, c, Tupu, Tupu
