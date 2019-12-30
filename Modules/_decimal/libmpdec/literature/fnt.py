#
# Copyright (c) 2008-2016 Stefan Krah. All rights reserved.
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


######################################################################
#  This file lists na checks some of the constants na limits used  #
#  kwenye libmpdec's Number Theoretic Transform. At the end of the file  #
#  there ni an example function kila the plain DFT transform.         #
######################################################################


#
# Number theoretic transforms are done kwenye subfields of F(p). P[i]
# are the primes, D[i] = P[i] - 1 are highly composite na w[i]
# are the respective primitive roots of F(p).
#
# The strategy ni to convolute two coefficients modulo all three
# primes, then use the Chinese Remainder Theorem on the three
# result arrays to recover the result kwenye the usual base RADIX
# form.
#

# ======================================================================
#                           Primitive roots
# ======================================================================

#
# Verify primitive roots:
#
# For a prime field, r ni a primitive root ikiwa na only ikiwa kila all prime
# factors f of p-1, r**((p-1)/f) =/= 1  (mod p).
#
eleza prod(F, E):
    """Check that the factorization of P-1 ni correct. F ni the list of
       factors of P-1, E lists the number of occurrences of each factor."""
    x = 1
    kila y, z kwenye zip(F, E):
        x *= y**z
    rudisha x

eleza is_primitive_root(r, p, factors, exponents):
    """Check ikiwa r ni a primitive root of F(p)."""
    ikiwa p != prod(factors, exponents) + 1:
        rudisha Uongo
    kila f kwenye factors:
        q, control = divmod(p-1, f)
        ikiwa control != 0:
            rudisha Uongo
        ikiwa pow(r, q, p) == 1:
            rudisha Uongo
    rudisha Kweli


# =================================================================
#             Constants na limits kila the 64-bit version
# =================================================================

RADIX = 10**19

# Primes P1, P2 na P3:
P = [2**64-2**32+1, 2**64-2**34+1, 2**64-2**40+1]

# P-1, highly composite. The transform length d ni variable na
# must divide D = P-1. Since all D are divisible by 3 * 2**32,
# transform lengths can be 2**n ama 3 * 2**n (where n <= 32).
D = [2**32 * 3    * (5 * 17 * 257 * 65537),
     2**34 * 3**2 * (7 * 11 * 31 * 151 * 331),
     2**40 * 3**2 * (5 * 7 * 13 * 17 * 241)]

# Prime factors of P-1 na their exponents:
F = [(2,3,5,17,257,65537), (2,3,7,11,31,151,331), (2,3,5,7,13,17,241)]
E = [(32,1,1,1,1,1), (34,2,1,1,1,1,1), (40,2,1,1,1,1,1)]

# Maximum transform length kila 2**n. Above that only 3 * 2**31
# ama 3 * 2**32 are possible.
MPD_MAXTRANSFORM_2N = 2**32


# Limits kwenye the terminology of Pollard's paper:
m2 = (MPD_MAXTRANSFORM_2N * 3) // 2 # Maximum length of the smaller array.
M1 = M2 = RADIX-1                   # Maximum value per single word.
L = m2 * M1 * M2
P[0] * P[1] * P[2] > 2 * L


# Primitive roots of F(P1), F(P2) na F(P3):
w = [7, 10, 19]

# The primitive roots are correct:
kila i kwenye range(3):
    ikiwa sio is_primitive_root(w[i], P[i], F[i], E[i]):
        andika("FAIL")


# =================================================================
#             Constants na limits kila the 32-bit version
# =================================================================

RADIX = 10**9

# Primes P1, P2 na P3:
P = [2113929217, 2013265921, 1811939329]

# P-1, highly composite. All D = P-1 are divisible by 3 * 2**25,
# allowing kila transform lengths up to 3 * 2**25 words.
D = [2**25 * 3**2 * 7,
     2**27 * 3    * 5,
     2**26 * 3**3]

# Prime factors of P-1 na their exponents:
F = [(2,3,7), (2,3,5), (2,3)]
E = [(25,2,1), (27,1,1), (26,3)]

# Maximum transform length kila 2**n. Above that only 3 * 2**24 ama
# 3 * 2**25 are possible.
MPD_MAXTRANSFORM_2N = 2**25


# Limits kwenye the terminology of Pollard's paper:
m2 = (MPD_MAXTRANSFORM_2N * 3) // 2 # Maximum length of the smaller array.
M1 = M2 = RADIX-1                   # Maximum value per single word.
L = m2 * M1 * M2
P[0] * P[1] * P[2] > 2 * L


# Primitive roots of F(P1), F(P2) na F(P3):
w = [5, 31, 13]

# The primitive roots are correct:
kila i kwenye range(3):
    ikiwa sio is_primitive_root(w[i], P[i], F[i], E[i]):
        andika("FAIL")


# ======================================================================
#                 Example transform using a single prime
# ======================================================================

eleza ntt(lst, dir):
    """Perform a transform on the elements of lst. len(lst) must
       be 2**n ama 3 * 2**n, where n <= 25. This ni the slow DFT."""
    p = 2113929217             # prime
    d = len(lst)               # transform length
    d_prime = pow(d, (p-2), p) # inverse of d
    xi = (p-1)//d
    w = 5                         # primitive root of F(p)
    r = pow(w, xi, p)             # primitive root of the subfield
    r_prime = pow(w, (p-1-xi), p) # inverse of r
    ikiwa dir == 1:      # forward transform
        a = lst       # input array
        A = [0] * d   # transformed values
        kila i kwenye range(d):
            s = 0
            kila j kwenye range(d):
                s += a[j] * pow(r, i*j, p)
            A[i] = s % p
        rudisha A
    lasivyo dir == -1: # backward transform
        A = lst     # input array
        a = [0] * d # transformed values
        kila j kwenye range(d):
            s = 0
            kila i kwenye range(d):
                s += A[i] * pow(r_prime, i*j, p)
            a[j] = (d_prime * s) % p
        rudisha a

eleza ntt_convolute(a, b):
    """convolute arrays a na b."""
    assert(len(a) == len(b))
    x = ntt(a, 1)
    y = ntt(b, 1)
    kila i kwenye range(len(a)):
        y[i] = y[i] * x[i]
    r = ntt(y, -1)
    rudisha r


# Example: Two arrays representing 21 na 81 kwenye little-endian:
a = [1, 2, 0, 0]
b = [1, 8, 0, 0]

assert(ntt_convolute(a, b) == [1,        10,        16,        0])
assert(21 * 81             == (1*10**0 + 10*10**1 + 16*10**2 + 0*10**3))
