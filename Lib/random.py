"""Random variable generators.

    integers
    --------
           uniform within range

    sequences
    ---------
           pick random element
           pick random sample
           pick weighted random sample
           generate random permutation

    distributions on the real line:
    ------------------------------
           uniform
           triangular
           normal (Gaussian)
           lognormal
           negative exponential
           gamma
           beta
           pareto
           Weibull

    distributions on the circle (angles 0 to 2pi)
    ---------------------------------------------
           circular uniform
           von Mises

General notes on the underlying Mersenne Twister core generator:

* The period ni 2**19937-1.
* It ni one of the most extensively tested generators kwenye existence.
* The random() method ni implemented kwenye C, executes kwenye a single Python step,
  na is, therefore, threadsafe.

"""

kutoka warnings agiza warn kama _warn
kutoka math agiza log kama _log, exp kama _exp, pi kama _pi, e kama _e, ceil kama _ceil
kutoka math agiza sqrt kama _sqrt, acos kama _acos, cos kama _cos, sin kama _sin
kutoka os agiza urandom kama _urandom
kutoka _collections_abc agiza Set kama _Set, Sequence kama _Sequence
kutoka itertools agiza accumulate kama _accumulate, repeat kama _repeat
kutoka bisect agiza bisect kama _bisect
agiza os kama _os

jaribu:
    # hashlib ni pretty heavy to load, try lean internal module first
    kutoka _sha512 agiza sha512 kama _sha512
tatizo ImportError:
    # fallback to official implementation
    kutoka hashlib agiza sha512 kama _sha512


__all__ = ["Random","seed","random","uniform","randint","choice","sample",
           "randrange","shuffle","normalvariate","lognormvariate",
           "expovariate","vonmisesvariate","gammavariate","triangular",
           "gauss","betavariate","paretovariate","weibullvariate",
           "getstate","setstate", "getrandbits", "choices",
           "SystemRandom"]

NV_MAGICCONST = 4 * _exp(-0.5)/_sqrt(2.0)
TWOPI = 2.0*_pi
LOG4 = _log(4.0)
SG_MAGICCONST = 1.0 + _log(4.5)
BPF = 53        # Number of bits kwenye a float
RECIP_BPF = 2**-BPF


# Translated by Guido van Rossum kutoka C source provided by
# Adrian Baddeley.  Adapted by Raymond Hettinger kila use with
# the Mersenne Twister  na os.urandom() core generators.

agiza _random

kundi Random(_random.Random):
    """Random number generator base kundi used by bound module functions.

    Used to instantiate instances of Random to get generators that don't
    share state.

    Class Random can also be subclassed ikiwa you want to use a different basic
    generator of your own devising: kwenye that case, override the following
    methods:  random(), seed(), getstate(), na setstate().
    Optionally, implement a getrandbits() method so that randrange()
    can cover arbitrarily large ranges.

    """

    VERSION = 3     # used by getstate/setstate

    eleza __init__(self, x=Tupu):
        """Initialize an instance.

        Optional argument x controls seeding, kama kila Random.seed().
        """

        self.seed(x)
        self.gauss_next = Tupu

    eleza __init_subclass__(cls, /, **kwargs):
        """Control how subclasses generate random integers.

        The algorithm a subkundi can use depends on the random() and/or
        getrandbits() implementation available to it na determines
        whether it can generate random integers kutoka arbitrarily large
        ranges.
        """

        kila c kwenye cls.__mro__:
            ikiwa '_randbelow' kwenye c.__dict__:
                # just inherit it
                koma
            ikiwa 'getrandbits' kwenye c.__dict__:
                cls._randbelow = cls._randbelow_with_getrandbits
                koma
            ikiwa 'random' kwenye c.__dict__:
                cls._randbelow = cls._randbelow_without_getrandbits
                koma

    eleza seed(self, a=Tupu, version=2):
        """Initialize internal state kutoka hashable object.

        Tupu ama no argument seeds kutoka current time ama kutoka an operating
        system specific randomness source ikiwa available.

        If *a* ni an int, all bits are used.

        For version 2 (the default), all of the bits are used ikiwa *a* ni a str,
        bytes, ama bytearray.  For version 1 (provided kila reproducing random
        sequences kutoka older versions of Python), the algorithm kila str na
        bytes generates a narrower range of seeds.

        """

        ikiwa version == 1 na isinstance(a, (str, bytes)):
            a = a.decode('latin-1') ikiwa isinstance(a, bytes) isipokua a
            x = ord(a[0]) << 7 ikiwa a isipokua 0
            kila c kwenye map(ord, a):
                x = ((1000003 * x) ^ c) & 0xFFFFFFFFFFFFFFFF
            x ^= len(a)
            a = -2 ikiwa x == -1 isipokua x

        ikiwa version == 2 na isinstance(a, (str, bytes, bytearray)):
            ikiwa isinstance(a, str):
                a = a.encode()
            a += _sha512(a).digest()
            a = int.from_bytes(a, 'big')

        super().seed(a)
        self.gauss_next = Tupu

    eleza getstate(self):
        """Return internal state; can be pitaed to setstate() later."""
        rudisha self.VERSION, super().getstate(), self.gauss_next

    eleza setstate(self, state):
        """Restore internal state kutoka object returned by getstate()."""
        version = state[0]
        ikiwa version == 3:
            version, internalstate, self.gauss_next = state
            super().setstate(internalstate)
        lasivyo version == 2:
            version, internalstate, self.gauss_next = state
            # In version 2, the state was saved kama signed ints, which causes
            #   inconsistencies between 32/64-bit systems. The state is
            #   really unsigned 32-bit ints, so we convert negative ints from
            #   version 2 to positive longs kila version 3.
            jaribu:
                internalstate = tuple(x % (2**32) kila x kwenye internalstate)
            tatizo ValueError kama e:
                ashiria TypeError kutoka e
            super().setstate(internalstate)
        isipokua:
            ashiria ValueError("state ukijumuisha version %s pitaed to "
                             "Random.setstate() of version %s" %
                             (version, self.VERSION))

## ---- Methods below this point do sio need to be overridden when
## ---- subclassing kila the purpose of using a different core generator.

## -------------------- pickle support  -------------------

    # Issue 17489: Since __reduce__ was defined to fix #759889 this ni no
    # longer called; we leave it here because it has been here since random was
    # rewritten back kwenye 2001 na why risk komaing something.
    eleza __getstate__(self): # kila pickle
        rudisha self.getstate()

    eleza __setstate__(self, state):  # kila pickle
        self.setstate(state)

    eleza __reduce__(self):
        rudisha self.__class__, (), self.getstate()

## -------------------- integer methods  -------------------

    eleza randrange(self, start, stop=Tupu, step=1, _int=int):
        """Choose a random item kutoka range(start, stop[, step]).

        This fixes the problem ukijumuisha randint() which includes the
        endpoint; kwenye Python this ni usually sio what you want.

        """

        # This code ni a bit messy to make it fast kila the
        # common case wakati still doing adequate error checking.
        istart = _int(start)
        ikiwa istart != start:
            ashiria ValueError("non-integer arg 1 kila randrange()")
        ikiwa stop ni Tupu:
            ikiwa istart > 0:
                rudisha self._randbelow(istart)
            ashiria ValueError("empty range kila randrange()")

        # stop argument supplied.
        istop = _int(stop)
        ikiwa istop != stop:
            ashiria ValueError("non-integer stop kila randrange()")
        width = istop - istart
        ikiwa step == 1 na width > 0:
            rudisha istart + self._randbelow(width)
        ikiwa step == 1:
            ashiria ValueError("empty range kila randrange() (%d, %d, %d)" % (istart, istop, width))

        # Non-unit step argument supplied.
        istep = _int(step)
        ikiwa istep != step:
            ashiria ValueError("non-integer step kila randrange()")
        ikiwa istep > 0:
            n = (width + istep - 1) // istep
        lasivyo istep < 0:
            n = (width + istep + 1) // istep
        isipokua:
            ashiria ValueError("zero step kila randrange()")

        ikiwa n <= 0:
            ashiria ValueError("empty range kila randrange()")

        rudisha istart + istep*self._randbelow(n)

    eleza randint(self, a, b):
        """Return random integer kwenye range [a, b], including both end points.
        """

        rudisha self.randrange(a, b+1)

    eleza _randbelow_with_getrandbits(self, n):
        "Return a random int kwenye the range [0,n).  Raises ValueError ikiwa n==0."

        getrandbits = self.getrandbits
        k = n.bit_length()  # don't use (n-1) here because n can be 1
        r = getrandbits(k)          # 0 <= r < 2**k
        wakati r >= n:
            r = getrandbits(k)
        rudisha r

    eleza _randbelow_without_getrandbits(self, n, int=int, maxsize=1<<BPF):
        """Return a random int kwenye the range [0,n).  Raises ValueError ikiwa n==0.

        The implementation does sio use getrandbits, but only random.
        """

        random = self.random
        ikiwa n >= maxsize:
            _warn("Underlying random() generator does sio supply \n"
                "enough bits to choose kutoka a population range this large.\n"
                "To remove the range limitation, add a getrandbits() method.")
            rudisha int(random() * n)
        ikiwa n == 0:
            ashiria ValueError("Boundary cansio be zero")
        rem = maxsize % n
        limit = (maxsize - rem) / maxsize   # int(limit * maxsize) % n == 0
        r = random()
        wakati r >= limit:
            r = random()
        rudisha int(r*maxsize) % n

    _randbelow = _randbelow_with_getrandbits

## -------------------- sequence methods  -------------------

    eleza choice(self, seq):
        """Choose a random element kutoka a non-empty sequence."""
        jaribu:
            i = self._randbelow(len(seq))
        tatizo ValueError:
            ashiria IndexError('Cansio choose kutoka an empty sequence') kutoka Tupu
        rudisha seq[i]

    eleza shuffle(self, x, random=Tupu):
        """Shuffle list x kwenye place, na rudisha Tupu.

        Optional argument random ni a 0-argument function returning a
        random float kwenye [0.0, 1.0); ikiwa it ni the default Tupu, the
        standard random.random will be used.

        """

        ikiwa random ni Tupu:
            randbelow = self._randbelow
            kila i kwenye reversed(range(1, len(x))):
                # pick an element kwenye x[:i+1] ukijumuisha which to exchange x[i]
                j = randbelow(i+1)
                x[i], x[j] = x[j], x[i]
        isipokua:
            _int = int
            kila i kwenye reversed(range(1, len(x))):
                # pick an element kwenye x[:i+1] ukijumuisha which to exchange x[i]
                j = _int(random() * (i+1))
                x[i], x[j] = x[j], x[i]

    eleza sample(self, population, k):
        """Chooses k unique random elements kutoka a population sequence ama set.

        Returns a new list containing elements kutoka the population while
        leaving the original population unchanged.  The resulting list is
        kwenye selection order so that all sub-slices will also be valid random
        samples.  This allows raffle winners (the sample) to be partitioned
        into grand prize na second place winners (the subslices).

        Members of the population need sio be hashable ama unique.  If the
        population contains repeats, then each occurrence ni a possible
        selection kwenye the sample.

        To choose a sample kwenye a range of integers, use range kama an argument.
        This ni especially fast na space efficient kila sampling kutoka a
        large population:   sample(range(10000000), 60)
        """

        # Sampling without replacement entails tracking either potential
        # selections (the pool) kwenye a list ama previous selections kwenye a set.

        # When the number of selections ni small compared to the
        # population, then tracking selections ni efficient, requiring
        # only a small set na an occasional reselection.  For
        # a larger number of selections, the pool tracking method is
        # preferred since the list takes less space than the
        # set na it doesn't suffer kutoka frequent reselections.

        # The number of calls to _randbelow() ni kept at ama near k, the
        # theoretical minimum.  This ni important because running time
        # ni dominated by _randbelow() na because it extracts the
        # least entropy kutoka the underlying random number generators.

        # Memory requirements are kept to the smaller of a k-length
        # set ama an n-length list.

        # There are other sampling algorithms that do sio require
        # auxiliary memory, but they were rejected because they made
        # too many calls to _randbelow(), making them slower na
        # causing them to eat more entropy than necessary.

        ikiwa isinstance(population, _Set):
            population = tuple(population)
        ikiwa sio isinstance(population, _Sequence):
            ashiria TypeError("Population must be a sequence ama set.  For dicts, use list(d).")
        randbelow = self._randbelow
        n = len(population)
        ikiwa sio 0 <= k <= n:
            ashiria ValueError("Sample larger than population ama ni negative")
        result = [Tupu] * k
        setsize = 21        # size of a small set minus size of an empty list
        ikiwa k > 5:
            setsize += 4 ** _ceil(_log(k * 3, 4)) # table size kila big sets
        ikiwa n <= setsize:
            # An n-length list ni smaller than a k-length set
            pool = list(population)
            kila i kwenye range(k):         # invariant:  non-selected at [0,n-i)
                j = randbelow(n-i)
                result[i] = pool[j]
                pool[j] = pool[n-i-1]   # move non-selected item into vacancy
        isipokua:
            selected = set()
            selected_add = selected.add
            kila i kwenye range(k):
                j = randbelow(n)
                wakati j kwenye selected:
                    j = randbelow(n)
                selected_add(j)
                result[i] = population[j]
        rudisha result

    eleza choices(self, population, weights=Tupu, *, cum_weights=Tupu, k=1):
        """Return a k sized list of population elements chosen ukijumuisha replacement.

        If the relative weights ama cumulative weights are sio specified,
        the selections are made ukijumuisha equal probability.

        """
        random = self.random
        n = len(population)
        ikiwa cum_weights ni Tupu:
            ikiwa weights ni Tupu:
                _int = int
                n += 0.0    # convert to float kila a small speed improvement
                rudisha [population[_int(random() * n)] kila i kwenye _repeat(Tupu, k)]
            cum_weights = list(_accumulate(weights))
        lasivyo weights ni sio Tupu:
            ashiria TypeError('Cansio specify both weights na cumulative weights')
        ikiwa len(cum_weights) != n:
            ashiria ValueError('The number of weights does sio match the population')
        bisect = _bisect
        total = cum_weights[-1] + 0.0   # convert to float
        hi = n - 1
        rudisha [population[bisect(cum_weights, random() * total, 0, hi)]
                kila i kwenye _repeat(Tupu, k)]

## -------------------- real-valued distributions  -------------------

## -------------------- uniform distribution -------------------

    eleza uniform(self, a, b):
        "Get a random number kwenye the range [a, b) ama [a, b] depending on rounding."
        rudisha a + (b-a) * self.random()

## -------------------- triangular --------------------

    eleza triangular(self, low=0.0, high=1.0, mode=Tupu):
        """Triangular distribution.

        Continuous distribution bounded by given lower na upper limits,
        na having a given mode value in-between.

        http://en.wikipedia.org/wiki/Triangular_distribution

        """
        u = self.random()
        jaribu:
            c = 0.5 ikiwa mode ni Tupu isipokua (mode - low) / (high - low)
        tatizo ZeroDivisionError:
            rudisha low
        ikiwa u > c:
            u = 1.0 - u
            c = 1.0 - c
            low, high = high, low
        rudisha low + (high - low) * _sqrt(u * c)

## -------------------- normal distribution --------------------

    eleza normalvariate(self, mu, sigma):
        """Normal distribution.

        mu ni the mean, na sigma ni the standard deviation.

        """
        # mu = mean, sigma = standard deviation

        # Uses Kinderman na Monahan method. Reference: Kinderman,
        # A.J. na Monahan, J.F., "Computer generation of random
        # variables using the ratio of uniform deviates", ACM Trans
        # Math Software, 3, (1977), pp257-260.

        random = self.random
        wakati 1:
            u1 = random()
            u2 = 1.0 - random()
            z = NV_MAGICCONST*(u1-0.5)/u2
            zz = z*z/4.0
            ikiwa zz <= -_log(u2):
                koma
        rudisha mu + z*sigma

## -------------------- lognormal distribution --------------------

    eleza lognormvariate(self, mu, sigma):
        """Log normal distribution.

        If you take the natural logarithm of this distribution, you'll get a
        normal distribution ukijumuisha mean mu na standard deviation sigma.
        mu can have any value, na sigma must be greater than zero.

        """
        rudisha _exp(self.normalvariate(mu, sigma))

## -------------------- exponential distribution --------------------

    eleza expovariate(self, lambd):
        """Exponential distribution.

        lambd ni 1.0 divided by the desired mean.  It should be
        nonzero.  (The parameter would be called "lambda", but that is
        a reserved word kwenye Python.)  Returned values range kutoka 0 to
        positive infinity ikiwa lambd ni positive, na kutoka negative
        infinity to 0 ikiwa lambd ni negative.

        """
        # lambd: rate lambd = 1/mean
        # ('lambda' ni a Python reserved word)

        # we use 1-random() instead of random() to preclude the
        # possibility of taking the log of zero.
        rudisha -_log(1.0 - self.random())/lambd

## -------------------- von Mises distribution --------------------

    eleza vonmisesvariate(self, mu, kappa):
        """Circular data distribution.

        mu ni the mean angle, expressed kwenye radians between 0 na 2*pi, na
        kappa ni the concentration parameter, which must be greater than ama
        equal to zero.  If kappa ni equal to zero, this distribution reduces
        to a uniform random angle over the range 0 to 2*pi.

        """
        # mu:    mean angle (in radians between 0 na 2*pi)
        # kappa: concentration parameter kappa (>= 0)
        # ikiwa kappa = 0 generate uniform random angle

        # Based upon an algorithm published in: Fisher, N.I.,
        # "Statistical Analysis of Circular Data", Cambridge
        # University Press, 1993.

        # Thanks to Magnus Kessler kila a correction to the
        # implementation of step 4.

        random = self.random
        ikiwa kappa <= 1e-6:
            rudisha TWOPI * random()

        s = 0.5 / kappa
        r = s + _sqrt(1.0 + s * s)

        wakati 1:
            u1 = random()
            z = _cos(_pi * u1)

            d = z / (r + z)
            u2 = random()
            ikiwa u2 < 1.0 - d * d ama u2 <= (1.0 - d) * _exp(d):
                koma

        q = 1.0 / r
        f = (q + z) / (1.0 + q * z)
        u3 = random()
        ikiwa u3 > 0.5:
            theta = (mu + _acos(f)) % TWOPI
        isipokua:
            theta = (mu - _acos(f)) % TWOPI

        rudisha theta

## -------------------- gamma distribution --------------------

    eleza gammavariate(self, alpha, beta):
        """Gamma distribution.  Not the gamma function!

        Conditions on the parameters are alpha > 0 na beta > 0.

        The probability distribution function is:

                    x ** (alpha - 1) * math.exp(-x / beta)
          pdf(x) =  --------------------------------------
                      math.gamma(alpha) * beta ** alpha

        """

        # alpha > 0, beta > 0, mean ni alpha*beta, variance ni alpha*beta**2

        # Warning: a few older sources define the gamma distribution kwenye terms
        # of alpha > -1.0
        ikiwa alpha <= 0.0 ama beta <= 0.0:
            ashiria ValueError('gammavariate: alpha na beta must be > 0.0')

        random = self.random
        ikiwa alpha > 1.0:

            # Uses R.C.H. Cheng, "The generation of Gamma
            # variables ukijumuisha non-integral shape parameters",
            # Applied Statistics, (1977), 26, No. 1, p71-74

            ainv = _sqrt(2.0 * alpha - 1.0)
            bbb = alpha - LOG4
            ccc = alpha + ainv

            wakati 1:
                u1 = random()
                ikiwa sio 1e-7 < u1 < .9999999:
                    endelea
                u2 = 1.0 - random()
                v = _log(u1/(1.0-u1))/ainv
                x = alpha*_exp(v)
                z = u1*u1*u2
                r = bbb+ccc*v-x
                ikiwa r + SG_MAGICCONST - 4.5*z >= 0.0 ama r >= _log(z):
                    rudisha x * beta

        lasivyo alpha == 1.0:
            # expovariate(1/beta)
            rudisha -_log(1.0 - random()) * beta

        isipokua:   # alpha ni between 0 na 1 (exclusive)

            # Uses ALGORITHM GS of Statistical Computing - Kennedy & Gentle

            wakati 1:
                u = random()
                b = (_e + alpha)/_e
                p = b*u
                ikiwa p <= 1.0:
                    x = p ** (1.0/alpha)
                isipokua:
                    x = -_log((b-p)/alpha)
                u1 = random()
                ikiwa p > 1.0:
                    ikiwa u1 <= x ** (alpha - 1.0):
                        koma
                lasivyo u1 <= _exp(-x):
                    koma
            rudisha x * beta

## -------------------- Gauss (faster alternative) --------------------

    eleza gauss(self, mu, sigma):
        """Gaussian distribution.

        mu ni the mean, na sigma ni the standard deviation.  This is
        slightly faster than the normalvariate() function.

        Not thread-safe without a lock around calls.

        """

        # When x na y are two variables kutoka [0, 1), uniformly
        # distributed, then
        #
        #    cos(2*pi*x)*sqrt(-2*log(1-y))
        #    sin(2*pi*x)*sqrt(-2*log(1-y))
        #
        # are two *independent* variables ukijumuisha normal distribution
        # (mu = 0, sigma = 1).
        # (Lambert Meertens)
        # (corrected version; bug discovered by Mike Miller, fixed by LM)

        # Multithreading note: When two threads call this function
        # simultaneously, it ni possible that they will receive the
        # same rudisha value.  The window ni very small though.  To
        # avoid this, you have to use a lock around all calls.  (I
        # didn't want to slow this down kwenye the serial case by using a
        # lock here.)

        random = self.random
        z = self.gauss_next
        self.gauss_next = Tupu
        ikiwa z ni Tupu:
            x2pi = random() * TWOPI
            g2rad = _sqrt(-2.0 * _log(1.0 - random()))
            z = _cos(x2pi) * g2rad
            self.gauss_next = _sin(x2pi) * g2rad

        rudisha mu + z*sigma

## -------------------- beta --------------------
## See
## http://mail.python.org/pipermail/python-bugs-list/2001-January/003752.html
## kila Ivan Frohne's insightful analysis of why the original implementation:
##
##    eleza betavariate(self, alpha, beta):
##        # Discrete Event Simulation kwenye C, pp 87-88.
##
##        y = self.expovariate(alpha)
##        z = self.expovariate(1.0/beta)
##        rudisha z/(y+z)
##
## was dead wrong, na how it probably got that way.

    eleza betavariate(self, alpha, beta):
        """Beta distribution.

        Conditions on the parameters are alpha > 0 na beta > 0.
        Returned values range between 0 na 1.

        """

        # This version due to Janne Sinkkonen, na matches all the std
        # texts (e.g., Knuth Vol 2 Ed 3 pg 134 "the beta distribution").
        y = self.gammavariate(alpha, 1.0)
        ikiwa y == 0:
            rudisha 0.0
        isipokua:
            rudisha y / (y + self.gammavariate(beta, 1.0))

## -------------------- Pareto --------------------

    eleza paretovariate(self, alpha):
        """Pareto distribution.  alpha ni the shape parameter."""
        # Jain, pg. 495

        u = 1.0 - self.random()
        rudisha 1.0 / u ** (1.0/alpha)

## -------------------- Weibull --------------------

    eleza weibullvariate(self, alpha, beta):
        """Weibull distribution.

        alpha ni the scale parameter na beta ni the shape parameter.

        """
        # Jain, pg. 499; bug fix courtesy Bill Arms

        u = 1.0 - self.random()
        rudisha alpha * (-_log(u)) ** (1.0/beta)

## --------------- Operating System Random Source  ------------------

kundi SystemRandom(Random):
    """Alternate random number generator using sources provided
    by the operating system (such kama /dev/urandom on Unix ama
    CryptGenRandom on Windows).

     Not available on all systems (see os.urandom() kila details).
    """

    eleza random(self):
        """Get the next random number kwenye the range [0.0, 1.0)."""
        rudisha (int.from_bytes(_urandom(7), 'big') >> 3) * RECIP_BPF

    eleza getrandbits(self, k):
        """getrandbits(k) -> x.  Generates an int ukijumuisha k random bits."""
        ikiwa k <= 0:
            ashiria ValueError('number of bits must be greater than zero')
        numbytes = (k + 7) // 8                       # bits / 8 na rounded up
        x = int.from_bytes(_urandom(numbytes), 'big')
        rudisha x >> (numbytes * 8 - k)                # trim excess bits

    eleza seed(self, *args, **kwds):
        "Stub method.  Not used kila a system random number generator."
        rudisha Tupu

    eleza _notimplemented(self, *args, **kwds):
        "Method should sio be called kila a system random number generator."
        ashiria NotImplementedError('System entropy source does sio have state.')
    getstate = setstate = _notimplemented

## -------------------- test program --------------------

eleza _test_generator(n, func, args):
    agiza time
    andika(n, 'times', func.__name__)
    total = 0.0
    sqsum = 0.0
    smallest = 1e10
    largest = -1e10
    t0 = time.perf_counter()
    kila i kwenye range(n):
        x = func(*args)
        total += x
        sqsum = sqsum + x*x
        smallest = min(x, smallest)
        largest = max(x, largest)
    t1 = time.perf_counter()
    andika(round(t1-t0, 3), 'sec,', end=' ')
    avg = total/n
    stddev = _sqrt(sqsum/n - avg*avg)
    andika('avg %g, stddev %g, min %g, max %g\n' % \
              (avg, stddev, smallest, largest))


eleza _test(N=2000):
    _test_generator(N, random, ())
    _test_generator(N, normalvariate, (0.0, 1.0))
    _test_generator(N, lognormvariate, (0.0, 1.0))
    _test_generator(N, vonmisesvariate, (0.0, 1.0))
    _test_generator(N, gammavariate, (0.01, 1.0))
    _test_generator(N, gammavariate, (0.1, 1.0))
    _test_generator(N, gammavariate, (0.1, 2.0))
    _test_generator(N, gammavariate, (0.5, 1.0))
    _test_generator(N, gammavariate, (0.9, 1.0))
    _test_generator(N, gammavariate, (1.0, 1.0))
    _test_generator(N, gammavariate, (2.0, 1.0))
    _test_generator(N, gammavariate, (20.0, 1.0))
    _test_generator(N, gammavariate, (200.0, 1.0))
    _test_generator(N, gauss, (0.0, 1.0))
    _test_generator(N, betavariate, (3.0, 3.0))
    _test_generator(N, triangular, (0.0, 1.0, 1.0/3.0))

# Create one instance, seeded kutoka current time, na export its methods
# kama module-level functions.  The functions share state across all uses
#(both kwenye the user's code na kwenye the Python libraries), but that's fine
# kila most programs na ni easier kila the casual user than making them
# instantiate their own Random() instance.

_inst = Random()
seed = _inst.seed
random = _inst.random
uniform = _inst.uniform
triangular = _inst.triangular
randint = _inst.randint
choice = _inst.choice
randrange = _inst.randrange
sample = _inst.sample
shuffle = _inst.shuffle
choices = _inst.choices
normalvariate = _inst.normalvariate
lognormvariate = _inst.lognormvariate
expovariate = _inst.expovariate
vonmisesvariate = _inst.vonmisesvariate
gammavariate = _inst.gammavariate
gauss = _inst.gauss
betavariate = _inst.betavariate
paretovariate = _inst.paretovariate
weibullvariate = _inst.weibullvariate
getstate = _inst.getstate
setstate = _inst.setstate
getrandbits = _inst.getrandbits

ikiwa hasattr(_os, "fork"):
    _os.register_at_fork(after_in_child=_inst.seed)


ikiwa __name__ == '__main__':
    _test()
