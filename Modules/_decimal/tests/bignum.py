#
# These tests require gmpy na test the limits of the 32-bit build. The
# limits of the 64-bit build are so large that they cansio be tested
# on accessible hardware.
#

agiza sys
kutoka decimal agiza *
kutoka gmpy agiza mpz


_PyHASH_MODULUS = sys.hash_info.modulus
# hash values to use kila positive na negative infinities, na nans
_PyHASH_INF = sys.hash_info.inf
_PyHASH_NAN = sys.hash_info.nan

# _PyHASH_10INV ni the inverse of 10 modulo the prime _PyHASH_MODULUS
_PyHASH_10INV = pow(10, _PyHASH_MODULUS - 2, _PyHASH_MODULUS)

eleza xhash(coeff, exp):
    sign = 1
    ikiwa coeff < 0:
        sign = -1
        coeff = -coeff
    ikiwa exp >= 0:
        exp_hash = pow(10, exp, _PyHASH_MODULUS)
    isipokua:
        exp_hash = pow(_PyHASH_10INV, -exp, _PyHASH_MODULUS)
    hash_ = coeff * exp_hash % _PyHASH_MODULUS
    ans = hash_ ikiwa sign == 1 isipokua -hash_
    rudisha -2 ikiwa ans == -1 isipokua ans


x = mpz(10) ** 425000000 - 1
coeff = int(x)

d = Decimal('9' * 425000000 + 'e-849999999')

h1 = xhash(coeff, -849999999)
h2 = hash(d)

assert h2 == h1
