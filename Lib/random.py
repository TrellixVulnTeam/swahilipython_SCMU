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

* The period is 2**19937-1.
* It is one of the most extensively tested generators in existence.
* The random() method is implemented in C, executes in a single Python step,
  and is, therefore, threadsafe.

"""

kutoka warnings agiza warn as _warn
kutoka math agiza log as _log, exp as _exp, pi as _pi, e as _e, ceil as _ceil
kutoka math agiza sqrt as _sqrt, acos as _acos, cos as _cos, sin as _sin
kutoka os agiza urandom as _urandom
kutoka _collections_abc agiza Set as _Set, Sequence as _Sequence
kutoka itertools agiza accumulate as _accumulate, repeat as _repeat
kutoka bisect agiza bisect as _bisect
agiza os as _os

try:
    # hashlib is pretty heavy to load, try lean internal module first
    kutoka _sha512 agiza sha512 as _sha512
except ImportError:
    # fallback to official implementation
    kutoka hashlib agiza sha512 as _sha512


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
BPF = 53        # Number of bits in a float
RECIP_BPF = 2**-BPF


# Translated by Guido van Rossum kutoka C source provided by
# Adrian Baddeley.  Adapted by Raymond Hettinger for use with
# the Mersenne Twister  and os.urandom() core generators.

agiza _random

kundi Random(_random.Random):
    """Random number generator base kundi used by bound module functions.

    Used to instantiate instances of Random to get generators that don't
    share state.

    Class Random can also be subclassed ikiwa you want to use a different basic
    generator of your own devising: in that case, override the following
    methods:  random(), seed(), getstate(), and setstate().
    Optionally, implement a getrandbits() method so that randrange()
    can cover arbitrarily large ranges.

    """

    VERSION = 3     # used by getstate/setstate

    eleza __init__(self, x=None):
        """Initialize an instance.

        Optional argument x controls seeding, as for Random.seed().
        """

        self.seed(x)
        self.gauss_next = None

    eleza __init_subclass__(cls, /, **kwargs):
        """Control how subclasses generate random integers.

        The algorithm a subkundi can use depends on the random() and/or
        getrandbits() implementation available to it and determines
        whether it can generate random integers kutoka arbitrarily large
        ranges.
        """

        for c in cls.__mro__:
            ikiwa '_randbelow' in c.__dict__:
                # just inherit it
                break
            ikiwa 'getrandbits' in c.__dict__:
                cls._randbelow = cls._randbelow_with_getrandbits
                break
            ikiwa 'random' in c.__dict__:
                cls._randbelow = cls._randbelow_without_getrandbits
                break

    eleza seed(self, a=None, version=2):
        """Initialize internal state kutoka hashable object.

        None or no argument seeds kutoka current time or kutoka an operating
        system specific randomness source ikiwa available.

        If *a* is an int, all bits are used.

        For version 2 (the default), all of the bits are used ikiwa *a* is a str,
        bytes, or bytearray.  For version 1 (provided for reproducing random
        sequences kutoka older versions of Python), the algorithm for str and
        bytes generates a narrower range of seeds.

        """

        ikiwa version == 1 and isinstance(a, (str, bytes)):
            a = a.decode('latin-1') ikiwa isinstance(a, bytes) else a
            x = ord(a[0]) << 7 ikiwa a else 0
            for c in map(ord, a):
                x = ((1000003 * x) ^ c) & 0xFFFFFFFFFFFFFFFF
            x ^= len(a)
            a = -2 ikiwa x == -1 else x

        ikiwa version == 2 and isinstance(a, (str, bytes, bytearray)):
            ikiwa isinstance(a, str):
                a = a.encode()
            a += _sha512(a).digest()
            a = int.kutoka_bytes(a, 'big')

        super().seed(a)
        self.gauss_next = None

    eleza getstate(self):
        """Return internal state; can be passed to setstate() later."""
        rudisha self.VERSION, super().getstate(), self.gauss_next

    eleza setstate(self, state):
        """Restore internal state kutoka object returned by getstate()."""
        version = state[0]
        ikiwa version == 3:
            version, internalstate, self.gauss_next = state
            super().setstate(internalstate)
        elikiwa version == 2:
            version, internalstate, self.gauss_next = state
            # In version 2, the state was saved as signed ints, which causes
            #   inconsistencies between 32/64-bit systems. The state is
            #   really unsigned 32-bit ints, so we convert negative ints kutoka
            #   version 2 to positive longs for version 3.
            try:
                internalstate = tuple(x % (2**32) for x in internalstate)
            except ValueError as e:
                raise TypeError kutoka e
            super().setstate(internalstate)
        else:
            raise ValueError("state with version %s passed to "
                             "Random.setstate() of version %s" %
                             (version, self.VERSION))

## ---- Methods below this point do not need to be overridden when
## ---- subclassing for the purpose of using a different core generator.

## -------------------- pickle support  -------------------

    # Issue 17489: Since __reduce__ was defined to fix #759889 this is no
    # longer called; we leave it here because it has been here since random was
    # rewritten back in 2001 and why risk breaking something.
    eleza __getstate__(self): # for pickle
        rudisha self.getstate()

    eleza __setstate__(self, state):  # for pickle
        self.setstate(state)

    eleza __reduce__(self):
        rudisha self.__class__, (), self.getstate()

## -------------------- integer methods  -------------------

    eleza randrange(self, start, stop=None, step=1, _int=int):
        """Choose a random item kutoka range(start, stop[, step]).

        This fixes the problem with randint() which includes the
        endpoint; in Python this is usually not what you want.

        """

        # This code is a bit messy to make it fast for the
        # common case while still doing adequate error checking.
        istart = _int(start)
        ikiwa istart != start:
            raise ValueError("non-integer arg 1 for randrange()")
        ikiwa stop is None:
            ikiwa istart > 0:
                rudisha self._randbelow(istart)
            raise ValueError("empty range for randrange()")

        # stop argument supplied.
        istop = _int(stop)
        ikiwa istop != stop:
            raise ValueError("non-integer stop for randrange()")
        width = istop - istart
        ikiwa step == 1 and width > 0:
            rudisha istart + self._randbelow(width)
        ikiwa step == 1:
            raise ValueError("empty range for randrange() (%d, %d, %d)" % (istart, istop, width))

        # Non-unit step argument supplied.
        istep = _int(step)
        ikiwa istep != step:
            raise ValueError("non-integer step for randrange()")
        ikiwa istep > 0:
            n = (width + istep - 1) // istep
        elikiwa istep < 0:
            n = (width + istep + 1) // istep
        else:
            raise ValueError("zero step for randrange()")

        ikiwa n <= 0:
            raise ValueError("empty range for randrange()")

        rudisha istart + istep*self._randbelow(n)

    eleza randint(self, a, b):
        """Return random integer in range [a, b], including both end points.
        """

        rudisha self.randrange(a, b+1)

    eleza _randbelow_with_getrandbits(self, n):
        "Return a random int in the range [0,n).  Raises ValueError ikiwa n==0."

        getrandbits = self.getrandbits
        k = n.bit_length()  # don't use (n-1) here because n can be 1
        r = getrandbits(k)          # 0 <= r < 2**k
        while r >= n:
            r = getrandbits(k)
        rudisha r

    eleza _randbelow_without_getrandbits(self, n, int=int, maxsize=1<<BPF):
        """Return a random int in the range [0,n).  Raises ValueError ikiwa n==0.

        The implementation does not use getrandbits, but only random.
        """

        random = self.random
        ikiwa n >= maxsize:
            _warn("Underlying random() generator does not supply \n"
                "enough bits to choose kutoka a population range this large.\n"
                "To remove the range limitation, add a getrandbits() method.")
            rudisha int(random() * n)
        ikiwa n == 0:
            raise ValueError("Boundary cannot be zero")
        rem = maxsize % n
        limit = (maxsize - rem) / maxsize   # int(limit * maxsize) % n == 0
        r = random()
        while r >= limit:
            r = random()
        rudisha int(r*maxsize) % n

    _randbelow = _randbelow_with_getrandbits

## -------------------- sequence methods  -------------------

    eleza choice(self, seq):
        """Choose a random element kutoka a non-empty sequence."""
        try:
            i = self._randbelow(len(seq))
        except ValueError:
            raise IndexError('Cannot choose kutoka an empty sequence') kutoka None
        rudisha seq[i]

    eleza shuffle(self, x, random=None):
        """Shuffle list x in place, and rudisha None.

        Optional argument random is a 0-argument function returning a
        random float in [0.0, 1.0); ikiwa it is the default None, the
        standard random.random will be used.

        """

        ikiwa random is None:
            randbelow = self._randbelow
            for i in reversed(range(1, len(x))):
                # pick an element in x[:i+1] with which to exchange x[i]
                j = randbelow(i+1)
                x[i], x[j] = x[j], x[i]
        else:
            _int = int
            for i in reversed(range(1, len(x))):
                # pick an element in x[:i+1] with which to exchange x[i]
                j = _int(random() * (i+1))
                x[i], x[j] = x[j], x[i]

    eleza sample(self, population, k):
        """Chooses k unique random elements kutoka a population sequence or set.

        Returns a new list containing elements kutoka the population while
        leaving the original population unchanged.  The resulting list is
        in selection order so that all sub-slices will also be valid random
        samples.  This allows raffle winners (the sample) to be partitioned
        into grand prize and second place winners (the subslices).

        Members of the population need not be hashable or unique.  If the
        population contains repeats, then each occurrence is a possible
        selection in the sample.

        To choose a sample in a range of integers, use range as an argument.
        This is especially fast and space efficient for sampling kutoka a
        large population:   sample(range(10000000), 60)
        """

        # Sampling without replacement entails tracking either potential
        # selections (the pool) in a list or previous selections in a set.

        # When the number of selections is small compared to the
        # population, then tracking selections is efficient, requiring
        # only a small set and an occasional reselection.  For
        # a larger number of selections, the pool tracking method is
        # preferred since the list takes less space than the
        # set and it doesn't suffer kutoka frequent reselections.

        # The number of calls to _randbelow() is kept at or near k, the
        # theoretical minimum.  This is agizaant because running time
        # is dominated by _randbelow() and because it extracts the
        # least entropy kutoka the underlying random number generators.

        # Memory requirements are kept to the smaller of a k-length
        # set or an n-length list.

        # There are other sampling algorithms that do not require
        # auxiliary memory, but they were rejected because they made
        # too many calls to _randbelow(), making them slower and
        # causing them to eat more entropy than necessary.

        ikiwa isinstance(population, _Set):
            population = tuple(population)
        ikiwa not isinstance(population, _Sequence):
            raise TypeError("Population must be a sequence or set.  For dicts, use list(d).")
        randbelow = self._randbelow
        n = len(population)
        ikiwa not 0 <= k <= n:
            raise ValueError("Sample larger than population or is negative")
        result = [None] * k
        setsize = 21        # size of a small set minus size of an empty list
        ikiwa k > 5:
            setsize += 4 ** _ceil(_log(k * 3, 4)) # table size for big sets
        ikiwa n <= setsize:
            # An n-length list is smaller than a k-length set
            pool = list(population)
            for i in range(k):         # invariant:  non-selected at [0,n-i)
                j = randbelow(n-i)
                result[i] = pool[j]
                pool[j] = pool[n-i-1]   # move non-selected item into vacancy
        else:
            selected = set()
            selected_add = selected.add
            for i in range(k):
                j = randbelow(n)
                while j in selected:
                    j = randbelow(n)
                selected_add(j)
                result[i] = population[j]
        rudisha result

    eleza choices(self, population, weights=None, *, cum_weights=None, k=1):
        """Return a k sized list of population elements chosen with replacement.

        If the relative weights or cumulative weights are not specified,
        the selections are made with equal probability.

        """
        random = self.random
        n = len(population)
        ikiwa cum_weights is None:
            ikiwa weights is None:
                _int = int
                n += 0.0    # convert to float for a small speed improvement
                rudisha [population[_int(random() * n)] for i in _repeat(None, k)]
            cum_weights = list(_accumulate(weights))
        elikiwa weights is not None:
            raise TypeError('Cannot specify both weights and cumulative weights')
        ikiwa len(cum_weights) != n:
            raise ValueError('The number of weights does not match the population')
        bisect = _bisect
        total = cum_weights[-1] + 0.0   # convert to float
        hi = n - 1
        rudisha [population[bisect(cum_weights, random() * total, 0, hi)]
                for i in _repeat(None, k)]

## -------------------- real-valued distributions  -------------------

## -------------------- uniform distribution -------------------

    eleza uniform(self, a, b):
        "Get a random number in the range [a, b) or [a, b] depending on rounding."
        rudisha a + (b-a) * self.random()

## -------------------- triangular --------------------

    eleza triangular(self, low=0.0, high=1.0, mode=None):
        """Triangular distribution.

        Continuous distribution bounded by given lower and upper limits,
        and having a given mode value in-between.

        http://en.wikipedia.org/wiki/Triangular_distribution

        """
        u = self.random()
        try:
            c = 0.5 ikiwa mode is None else (mode - low) / (high - low)
        except ZeroDivisionError:
            rudisha low
        ikiwa u > c:
            u = 1.0 - u
            c = 1.0 - c
            low, high = high, low
        rudisha low + (high - low) * _sqrt(u * c)

## -------------------- normal distribution --------------------

    eleza normalvariate(self, mu, sigma):
        """Normal distribution.

        mu is the mean, and sigma is the standard deviation.

        """
        # mu = mean, sigma = standard deviation

        # Uses Kinderman and Monahan method. Reference: Kinderman,
        # A.J. and Monahan, J.F., "Computer generation of random
        # variables using the ratio of uniform deviates", ACM Trans
        # Math Software, 3, (1977), pp257-260.

        random = self.random
        while 1:
            u1 = random()
            u2 = 1.0 - random()
            z = NV_MAGICCONST*(u1-0.5)/u2
            zz = z*z/4.0
            ikiwa zz <= -_log(u2):
                break
        rudisha mu + z*sigma

## -------------------- lognormal distribution --------------------

    eleza lognormvariate(self, mu, sigma):
        """Log normal distribution.

        If you take the natural logarithm of this distribution, you'll get a
        normal distribution with mean mu and standard deviation sigma.
        mu can have any value, and sigma must be greater than zero.

        """
        rudisha _exp(self.normalvariate(mu, sigma))

## -------------------- exponential distribution --------------------

    eleza expovariate(self, lambd):
        """Exponential distribution.

        lambd is 1.0 divided by the desired mean.  It should be
        nonzero.  (The parameter would be called "lambda", but that is
        a reserved word in Python.)  Returned values range kutoka 0 to
        positive infinity ikiwa lambd is positive, and kutoka negative
        infinity to 0 ikiwa lambd is negative.

        """
        # lambd: rate lambd = 1/mean
        # ('lambda' is a Python reserved word)

        # we use 1-random() instead of random() to preclude the
        # possibility of taking the log of zero.
        rudisha -_log(1.0 - self.random())/lambd

## -------------------- von Mises distribution --------------------

    eleza vonmisesvariate(self, mu, kappa):
        """Circular data distribution.

        mu is the mean angle, expressed in radians between 0 and 2*pi, and
        kappa is the concentration parameter, which must be greater than or
        equal to zero.  If kappa is equal to zero, this distribution reduces
        to a uniform random angle over the range 0 to 2*pi.

        """
        # mu:    mean angle (in radians between 0 and 2*pi)
        # kappa: concentration parameter kappa (>= 0)
        # ikiwa kappa = 0 generate uniform random angle

        # Based upon an algorithm published in: Fisher, N.I.,
        # "Statistical Analysis of Circular Data", Cambridge
        # University Press, 1993.

        # Thanks to Magnus Kessler for a correction to the
        # implementation of step 4.

        random = self.random
        ikiwa kappa <= 1e-6:
            rudisha TWOPI * random()

        s = 0.5 / kappa
        r = s + _sqrt(1.0 + s * s)

        while 1:
            u1 = random()
            z = _cos(_pi * u1)

            d = z / (r + z)
            u2 = random()
            ikiwa u2 < 1.0 - d * d or u2 <= (1.0 - d) * _exp(d):
                break

        q = 1.0 / r
        f = (q + z) / (1.0 + q * z)
        u3 = random()
        ikiwa u3 > 0.5:
            theta = (mu + _acos(f)) % TWOPI
        else:
            theta = (mu - _acos(f)) % TWOPI

        rudisha theta

## -------------------- gamma distribution --------------------

    eleza gammavariate(self, alpha, beta):
        """Gamma distribution.  Not the gamma function!

        Conditions on the parameters are alpha > 0 and beta > 0.

        The probability distribution function is:

                    x ** (alpha - 1) * math.exp(-x / beta)
          pdf(x) =  --------------------------------------
                      math.gamma(alpha) * beta ** alpha

        """

        # alpha > 0, beta > 0, mean is alpha*beta, variance is alpha*beta**2

        # Warning: a few older sources define the gamma distribution in terms
        # of alpha > -1.0
        ikiwa alpha <= 0.0 or beta <= 0.0:
            raise ValueError('gammavariate: alpha and beta must be > 0.0')

        random = self.random
        ikiwa alpha > 1.0:

            # Uses R.C.H. Cheng, "The generation of Gamma
            # variables with non-integral shape parameters",
            # Applied Statistics, (1977), 26, No. 1, p71-74

            ainv = _sqrt(2.0 * alpha - 1.0)
            bbb = alpha - LOG4
            ccc = alpha + ainv

            while 1:
                u1 = random()
                ikiwa not 1e-7 < u1 < .9999999:
                    continue
                u2 = 1.0 - random()
                v = _log(u1/(1.0-u1))/ainv
                x = alpha*_exp(v)
                z = u1*u1*u2
                r = bbb+ccc*v-x
                ikiwa r + SG_MAGICCONST - 4.5*z >= 0.0 or r >= _log(z):
                    rudisha x * beta

        elikiwa alpha == 1.0:
            # expovariate(1/beta)
            rudisha -_log(1.0 - random()) * beta

        else:   # alpha is between 0 and 1 (exclusive)

            # Uses ALGORITHM GS of Statistical Computing - Kennedy & Gentle

            while 1:
                u = random()
                b = (_e + alpha)/_e
                p = b*u
                ikiwa p <= 1.0:
                    x = p ** (1.0/alpha)
                else:
                    x = -_log((b-p)/alpha)
                u1 = random()
                ikiwa p > 1.0:
                    ikiwa u1 <= x ** (alpha - 1.0):
                        break
                elikiwa u1 <= _exp(-x):
                    break
            rudisha x * beta

## -------------------- Gauss (faster alternative) --------------------

    eleza gauss(self, mu, sigma):
        """Gaussian distribution.

        mu is the mean, and sigma is the standard deviation.  This is
        slightly faster than the normalvariate() function.

        Not thread-safe without a lock around calls.

        """

        # When x and y are two variables kutoka [0, 1), uniformly
        # distributed, then
        #
        #    cos(2*pi*x)*sqrt(-2*log(1-y))
        #    sin(2*pi*x)*sqrt(-2*log(1-y))
        #
        # are two *independent* variables with normal distribution
        # (mu = 0, sigma = 1).
        # (Lambert Meertens)
        # (corrected version; bug discovered by Mike Miller, fixed by LM)

        # Multithreading note: When two threads call this function
        # simultaneously, it is possible that they will receive the
        # same rudisha value.  The window is very small though.  To
        # avoid this, you have to use a lock around all calls.  (I
        # didn't want to slow this down in the serial case by using a
        # lock here.)

        random = self.random
        z = self.gauss_next
        self.gauss_next = None
        ikiwa z is None:
            x2pi = random() * TWOPI
            g2rad = _sqrt(-2.0 * _log(1.0 - random()))
            z = _cos(x2pi) * g2rad
            self.gauss_next = _sin(x2pi) * g2rad

        rudisha mu + z*sigma

## -------------------- beta --------------------
## See
## http://mail.python.org/pipermail/python-bugs-list/2001-January/003752.html
## for Ivan Frohne's insightful analysis of why the original implementation:
##
##    eleza betavariate(self, alpha, beta):
##        # Discrete Event Simulation in C, pp 87-88.
##
##        y = self.expovariate(alpha)
##        z = self.expovariate(1.0/beta)
##        rudisha z/(y+z)
##
## was dead wrong, and how it probably got that way.

    eleza betavariate(self, alpha, beta):
        """Beta distribution.

        Conditions on the parameters are alpha > 0 and beta > 0.
        Returned values range between 0 and 1.

        """

        # This version due to Janne Sinkkonen, and matches all the std
        # texts (e.g., Knuth Vol 2 Ed 3 pg 134 "the beta distribution").
        y = self.gammavariate(alpha, 1.0)
        ikiwa y == 0:
            rudisha 0.0
        else:
            rudisha y / (y + self.gammavariate(beta, 1.0))

## -------------------- Pareto --------------------

    eleza paretovariate(self, alpha):
        """Pareto distribution.  alpha is the shape parameter."""
        # Jain, pg. 495

        u = 1.0 - self.random()
        rudisha 1.0 / u ** (1.0/alpha)

## -------------------- Weibull --------------------

    eleza weibullvariate(self, alpha, beta):
        """Weibull distribution.

        alpha is the scale parameter and beta is the shape parameter.

        """
        # Jain, pg. 499; bug fix courtesy Bill Arms

        u = 1.0 - self.random()
        rudisha alpha * (-_log(u)) ** (1.0/beta)

## --------------- Operating System Random Source  ------------------

kundi SystemRandom(Random):
    """Alternate random number generator using sources provided
    by the operating system (such as /dev/urandom on Unix or
    CryptGenRandom on Windows).

     Not available on all systems (see os.urandom() for details).
    """

    eleza random(self):
        """Get the next random number in the range [0.0, 1.0)."""
        rudisha (int.kutoka_bytes(_urandom(7), 'big') >> 3) * RECIP_BPF

    eleza getrandbits(self, k):
        """getrandbits(k) -> x.  Generates an int with k random bits."""
        ikiwa k <= 0:
            raise ValueError('number of bits must be greater than zero')
        numbytes = (k + 7) // 8                       # bits / 8 and rounded up
        x = int.kutoka_bytes(_urandom(numbytes), 'big')
        rudisha x >> (numbytes * 8 - k)                # trim excess bits

    eleza seed(self, *args, **kwds):
        "Stub method.  Not used for a system random number generator."
        rudisha None

    eleza _notimplemented(self, *args, **kwds):
        "Method should not be called for a system random number generator."
        raise NotImplementedError('System entropy source does not have state.')
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
    for i in range(n):
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

# Create one instance, seeded kutoka current time, and export its methods
# as module-level functions.  The functions share state across all uses
#(both in the user's code and in the Python libraries), but that's fine
# for most programs and is easier for the casual user than making them
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
