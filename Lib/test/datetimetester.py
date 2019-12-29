"""Test date/time type.

See http://www.zope.org/Members/fdrake/DateTimeWiki/TestCases
"""
agiza itertools
agiza bisect
agiza copy
agiza decimal
agiza sys
agiza os
agiza pickle
agiza random
agiza re
agiza struct
agiza unittest

kutoka array agiza array

kutoka operator agiza lt, le, gt, ge, eq, ne, truediv, floordiv, mod

kutoka test agiza support
kutoka test.support agiza is_resource_enabled, ALWAYS_EQ, LARGEST, SMALLEST

agiza datetime kama datetime_module
kutoka datetime agiza MINYEAR, MAXYEAR
kutoka datetime agiza timedelta
kutoka datetime agiza tzinfo
kutoka datetime agiza time
kutoka datetime agiza timezone
kutoka datetime agiza date, datetime
agiza time kama _time

agiza _testcapi

# Needed by test_datetime
agiza _strptime
#

pickle_loads = {pickle.loads, pickle._loads}

pickle_choices = [(pickle, pickle, proto)
                  kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1)]
assert len(pickle_choices) == pickle.HIGHEST_PROTOCOL + 1

# An arbitrary collection of objects of non-datetime types, kila testing
# mixed-type comparisons.
OTHERSTUFF = (10, 34.5, "abc", {}, [], ())


# XXX Copied kutoka test_float.
INF = float("inf")
NAN = float("nan")


#############################################################################
# module tests

kundi TestModule(unittest.TestCase):

    eleza test_constants(self):
        datetime = datetime_module
        self.assertEqual(datetime.MINYEAR, 1)
        self.assertEqual(datetime.MAXYEAR, 9999)

    eleza test_name_cleanup(self):
        ikiwa '_Pure' kwenye self.__class__.__name__:
            self.skipTest('Only run kila Fast C implementation')

        datetime = datetime_module
        names = set(name kila name kwenye dir(datetime)
                    ikiwa sio name.startswith('__') na sio name.endswith('__'))
        allowed = set(['MAXYEAR', 'MINYEAR', 'date', 'datetime',
                       'datetime_CAPI', 'time', 'timedelta', 'timezone',
                       'tzinfo', 'sys'])
        self.assertEqual(names - allowed, set([]))

    eleza test_divide_and_round(self):
        ikiwa '_Fast' kwenye self.__class__.__name__:
            self.skipTest('Only run kila Pure Python implementation')

        dar = datetime_module._divide_and_round

        self.assertEqual(dar(-10, -3), 3)
        self.assertEqual(dar(5, -2), -2)

        # four cases: (2 signs of a) x (2 signs of b)
        self.assertEqual(dar(7, 3), 2)
        self.assertEqual(dar(-7, 3), -2)
        self.assertEqual(dar(7, -3), -2)
        self.assertEqual(dar(-7, -3), 2)

        # ties to even - eight cases:
        # (2 signs of a) x (2 signs of b) x (even / odd quotient)
        self.assertEqual(dar(10, 4), 2)
        self.assertEqual(dar(-10, 4), -2)
        self.assertEqual(dar(10, -4), -2)
        self.assertEqual(dar(-10, -4), 2)

        self.assertEqual(dar(6, 4), 2)
        self.assertEqual(dar(-6, 4), -2)
        self.assertEqual(dar(6, -4), -2)
        self.assertEqual(dar(-6, -4), 2)


#############################################################################
# tzinfo tests

kundi FixedOffset(tzinfo):

    eleza __init__(self, offset, name, dstoffset=42):
        ikiwa isinstance(offset, int):
            offset = timedelta(minutes=offset)
        ikiwa isinstance(dstoffset, int):
            dstoffset = timedelta(minutes=dstoffset)
        self.__offset = offset
        self.__name = name
        self.__dstoffset = dstoffset
    eleza __repr__(self):
        rudisha self.__name.lower()
    eleza utcoffset(self, dt):
        rudisha self.__offset
    eleza tzname(self, dt):
        rudisha self.__name
    eleza dst(self, dt):
        rudisha self.__dstoffset

kundi PicklableFixedOffset(FixedOffset):

    eleza __init__(self, offset=Tupu, name=Tupu, dstoffset=Tupu):
        FixedOffset.__init__(self, offset, name, dstoffset)

    eleza __getstate__(self):
        rudisha self.__dict__

kundi _TZInfo(tzinfo):
    eleza utcoffset(self, datetime_module):
        rudisha random.random()

kundi TestTZInfo(unittest.TestCase):

    eleza test_refcnt_crash_bug_22044(self):
        tz1 = _TZInfo()
        dt1 = datetime(2014, 7, 21, 11, 32, 3, 0, tz1)
        with self.assertRaises(TypeError):
            dt1.utcoffset()

    eleza test_non_abstractness(self):
        # In order to allow subclasses to get pickled, the C implementation
        # wasn't able to get away with having __init__ ashiria
        # NotImplementedError.
        useless = tzinfo()
        dt = datetime.max
        self.assertRaises(NotImplementedError, useless.tzname, dt)
        self.assertRaises(NotImplementedError, useless.utcoffset, dt)
        self.assertRaises(NotImplementedError, useless.dst, dt)

    eleza test_subclass_must_override(self):
        kundi NotEnough(tzinfo):
            eleza __init__(self, offset, name):
                self.__offset = offset
                self.__name = name
        self.assertKweli(issubclass(NotEnough, tzinfo))
        ne = NotEnough(3, "NotByALongShot")
        self.assertIsInstance(ne, tzinfo)

        dt = datetime.now()
        self.assertRaises(NotImplementedError, ne.tzname, dt)
        self.assertRaises(NotImplementedError, ne.utcoffset, dt)
        self.assertRaises(NotImplementedError, ne.dst, dt)

    eleza test_normal(self):
        fo = FixedOffset(3, "Three")
        self.assertIsInstance(fo, tzinfo)
        kila dt kwenye datetime.now(), Tupu:
            self.assertEqual(fo.utcoffset(dt), timedelta(minutes=3))
            self.assertEqual(fo.tzname(dt), "Three")
            self.assertEqual(fo.dst(dt), timedelta(minutes=42))

    eleza test_pickling_base(self):
        # There's no point to pickling tzinfo objects on their own (they
        # carry no data), but they need to be picklable anyway else
        # concrete subclasses can't be pickled.
        orig = tzinfo.__new__(tzinfo)
        self.assertIs(type(orig), tzinfo)
        kila pickler, unpickler, proto kwenye pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertIs(type(derived), tzinfo)

    eleza test_pickling_subclass(self):
        # Make sure we can pickle/unpickle an instance of a subclass.
        offset = timedelta(minutes=-300)
        kila otype, args kwenye [
            (PicklableFixedOffset, (offset, 'cookie')),
            (timezone, (offset,)),
            (timezone, (offset, "EST"))]:
            orig = otype(*args)
            oname = orig.tzname(Tupu)
            self.assertIsInstance(orig, tzinfo)
            self.assertIs(type(orig), otype)
            self.assertEqual(orig.utcoffset(Tupu), offset)
            self.assertEqual(orig.tzname(Tupu), oname)
            kila pickler, unpickler, proto kwenye pickle_choices:
                green = pickler.dumps(orig, proto)
                derived = unpickler.loads(green)
                self.assertIsInstance(derived, tzinfo)
                self.assertIs(type(derived), otype)
                self.assertEqual(derived.utcoffset(Tupu), offset)
                self.assertEqual(derived.tzname(Tupu), oname)

    eleza test_issue23600(self):
        DSTDIFF = DSTOFFSET = timedelta(hours=1)

        kundi UKSummerTime(tzinfo):
            """Simple time zone which pretends to always be kwenye summer time, since
                that's what shows the failure.
            """

            eleza utcoffset(self, dt):
                rudisha DSTOFFSET

            eleza dst(self, dt):
                rudisha DSTDIFF

            eleza tzname(self, dt):
                rudisha 'UKSummerTime'

        tz = UKSummerTime()
        u = datetime(2014, 4, 26, 12, 1, tzinfo=tz)
        t = tz.kutokautc(u)
        self.assertEqual(t - t.utcoffset(), u)


kundi TestTimeZone(unittest.TestCase):

    eleza setUp(self):
        self.ACDT = timezone(timedelta(hours=9.5), 'ACDT')
        self.EST = timezone(-timedelta(hours=5), 'EST')
        self.DT = datetime(2010, 1, 1)

    eleza test_str(self):
        kila tz kwenye [self.ACDT, self.EST, timezone.utc,
                   timezone.min, timezone.max]:
            self.assertEqual(str(tz), tz.tzname(Tupu))

    eleza test_repr(self):
        datetime = datetime_module
        kila tz kwenye [self.ACDT, self.EST, timezone.utc,
                   timezone.min, timezone.max]:
            # test round-trip
            tzrep = repr(tz)
            self.assertEqual(tz, eval(tzrep))

    eleza test_class_members(self):
        limit = timedelta(hours=23, minutes=59)
        self.assertEqual(timezone.utc.utcoffset(Tupu), ZERO)
        self.assertEqual(timezone.min.utcoffset(Tupu), -limit)
        self.assertEqual(timezone.max.utcoffset(Tupu), limit)

    eleza test_constructor(self):
        self.assertIs(timezone.utc, timezone(timedelta(0)))
        self.assertIsNot(timezone.utc, timezone(timedelta(0), 'UTC'))
        self.assertEqual(timezone.utc, timezone(timedelta(0), 'UTC'))
        kila subminute kwenye [timedelta(microseconds=1), timedelta(seconds=1)]:
            tz = timezone(subminute)
            self.assertNotEqual(tz.utcoffset(Tupu) % timedelta(minutes=1), 0)
        # invalid offsets
        kila invalid kwenye [timedelta(1, 1), timedelta(1)]:
            self.assertRaises(ValueError, timezone, invalid)
            self.assertRaises(ValueError, timezone, -invalid)

        with self.assertRaises(TypeError): timezone(Tupu)
        with self.assertRaises(TypeError): timezone(42)
        with self.assertRaises(TypeError): timezone(ZERO, Tupu)
        with self.assertRaises(TypeError): timezone(ZERO, 42)
        with self.assertRaises(TypeError): timezone(ZERO, 'ABC', 'extra')

    eleza test_inheritance(self):
        self.assertIsInstance(timezone.utc, tzinfo)
        self.assertIsInstance(self.EST, tzinfo)

    eleza test_utcoffset(self):
        dummy = self.DT
        kila h kwenye [0, 1.5, 12]:
            offset = h * HOUR
            self.assertEqual(offset, timezone(offset).utcoffset(dummy))
            self.assertEqual(-offset, timezone(-offset).utcoffset(dummy))

        with self.assertRaises(TypeError): self.EST.utcoffset('')
        with self.assertRaises(TypeError): self.EST.utcoffset(5)


    eleza test_dst(self):
        self.assertIsTupu(timezone.utc.dst(self.DT))

        with self.assertRaises(TypeError): self.EST.dst('')
        with self.assertRaises(TypeError): self.EST.dst(5)

    eleza test_tzname(self):
        self.assertEqual('UTC', timezone.utc.tzname(Tupu))
        self.assertEqual('UTC', timezone(ZERO).tzname(Tupu))
        self.assertEqual('UTC-05:00', timezone(-5 * HOUR).tzname(Tupu))
        self.assertEqual('UTC+09:30', timezone(9.5 * HOUR).tzname(Tupu))
        self.assertEqual('UTC-00:01', timezone(timedelta(minutes=-1)).tzname(Tupu))
        self.assertEqual('XYZ', timezone(-5 * HOUR, 'XYZ').tzname(Tupu))
        # bpo-34482: Check that surrogates are handled properly.
        self.assertEqual('\ud800', timezone(ZERO, '\ud800').tzname(Tupu))

        # Sub-minute offsets:
        self.assertEqual('UTC+01:06:40', timezone(timedelta(0, 4000)).tzname(Tupu))
        self.assertEqual('UTC-01:06:40',
                         timezone(-timedelta(0, 4000)).tzname(Tupu))
        self.assertEqual('UTC+01:06:40.000001',
                         timezone(timedelta(0, 4000, 1)).tzname(Tupu))
        self.assertEqual('UTC-01:06:40.000001',
                         timezone(-timedelta(0, 4000, 1)).tzname(Tupu))

        with self.assertRaises(TypeError): self.EST.tzname('')
        with self.assertRaises(TypeError): self.EST.tzname(5)

    eleza test_kutokautc(self):
        with self.assertRaises(ValueError):
            timezone.utc.kutokautc(self.DT)
        with self.assertRaises(TypeError):
            timezone.utc.kutokautc('not datetime')
        kila tz kwenye [self.EST, self.ACDT, Eastern]:
            utctime = self.DT.replace(tzinfo=tz)
            local = tz.kutokautc(utctime)
            self.assertEqual(local - utctime, tz.utcoffset(local))
            self.assertEqual(local,
                             self.DT.replace(tzinfo=timezone.utc))

    eleza test_comparison(self):
        self.assertNotEqual(timezone(ZERO), timezone(HOUR))
        self.assertEqual(timezone(HOUR), timezone(HOUR))
        self.assertEqual(timezone(-5 * HOUR), timezone(-5 * HOUR, 'EST'))
        with self.assertRaises(TypeError): timezone(ZERO) < timezone(ZERO)
        self.assertIn(timezone(ZERO), {timezone(ZERO)})
        self.assertKweli(timezone(ZERO) != Tupu)
        self.assertUongo(timezone(ZERO) ==  Tupu)

        tz = timezone(ZERO)
        self.assertKweli(tz == ALWAYS_EQ)
        self.assertUongo(tz != ALWAYS_EQ)
        self.assertKweli(tz < LARGEST)
        self.assertUongo(tz > LARGEST)
        self.assertKweli(tz <= LARGEST)
        self.assertUongo(tz >= LARGEST)
        self.assertUongo(tz < SMALLEST)
        self.assertKweli(tz > SMALLEST)
        self.assertUongo(tz <= SMALLEST)
        self.assertKweli(tz >= SMALLEST)

    eleza test_aware_datetime(self):
        # test that timezone instances can be used by datetime
        t = datetime(1, 1, 1)
        kila tz kwenye [timezone.min, timezone.max, timezone.utc]:
            self.assertEqual(tz.tzname(t),
                             t.replace(tzinfo=tz).tzname())
            self.assertEqual(tz.utcoffset(t),
                             t.replace(tzinfo=tz).utcoffset())
            self.assertEqual(tz.dst(t),
                             t.replace(tzinfo=tz).dst())

    eleza test_pickle(self):
        kila tz kwenye self.ACDT, self.EST, timezone.min, timezone.max:
            kila pickler, unpickler, proto kwenye pickle_choices:
                tz_copy = unpickler.loads(pickler.dumps(tz, proto))
                self.assertEqual(tz_copy, tz)
        tz = timezone.utc
        kila pickler, unpickler, proto kwenye pickle_choices:
            tz_copy = unpickler.loads(pickler.dumps(tz, proto))
            self.assertIs(tz_copy, tz)

    eleza test_copy(self):
        kila tz kwenye self.ACDT, self.EST, timezone.min, timezone.max:
            tz_copy = copy.copy(tz)
            self.assertEqual(tz_copy, tz)
        tz = timezone.utc
        tz_copy = copy.copy(tz)
        self.assertIs(tz_copy, tz)

    eleza test_deepcopy(self):
        kila tz kwenye self.ACDT, self.EST, timezone.min, timezone.max:
            tz_copy = copy.deepcopy(tz)
            self.assertEqual(tz_copy, tz)
        tz = timezone.utc
        tz_copy = copy.deepcopy(tz)
        self.assertIs(tz_copy, tz)

    eleza test_offset_boundaries(self):
        # Test timedeltas close to the boundaries
        time_deltas = [
            timedelta(hours=23, minutes=59),
            timedelta(hours=23, minutes=59, seconds=59),
            timedelta(hours=23, minutes=59, seconds=59, microseconds=999999),
        ]
        time_deltas.extend([-delta kila delta kwenye time_deltas])

        kila delta kwenye time_deltas:
            with self.subTest(test_type='good', delta=delta):
                timezone(delta)

        # Test timedeltas on na outside the boundaries
        bad_time_deltas = [
            timedelta(hours=24),
            timedelta(hours=24, microseconds=1),
        ]
        bad_time_deltas.extend([-delta kila delta kwenye bad_time_deltas])

        kila delta kwenye bad_time_deltas:
            with self.subTest(test_type='bad', delta=delta):
                with self.assertRaises(ValueError):
                    timezone(delta)

    eleza test_comparison_with_tzinfo(self):
        # Constructing tzinfo objects directly should sio be done by users
        # na serves only to check the bug described kwenye bpo-37915
        self.assertNotEqual(timezone.utc, tzinfo())
        self.assertNotEqual(timezone(timedelta(hours=1)), tzinfo())

#############################################################################
# Base kundi kila testing a particular aspect of timedelta, time, date and
# datetime comparisons.

kundi HarmlessMixedComparison:
    # Test that __eq__ na __ne__ don't complain kila mixed-type comparisons.

    # Subclasses must define 'theclass', na theclass(1, 1, 1) must be a
    # legit constructor.

    eleza test_harmless_mixed_comparison(self):
        me = self.theclass(1, 1, 1)

        self.assertUongo(me == ())
        self.assertKweli(me != ())
        self.assertUongo(() == me)
        self.assertKweli(() != me)

        self.assertIn(me, [1, 20, [], me])
        self.assertIn([], [me, 1, 20, []])

        # Comparison to objects of unsupported types should rudisha
        # NotImplemented which falls back to the right hand side's __eq__
        # method. In this case, ALWAYS_EQ.__eq__ always rudishas Kweli.
        # ALWAYS_EQ.__ne__ always rudishas Uongo.
        self.assertKweli(me == ALWAYS_EQ)
        self.assertUongo(me != ALWAYS_EQ)

        # If the other kundi explicitly defines ordering
        # relative to our class, it ni allowed to do so
        self.assertKweli(me < LARGEST)
        self.assertUongo(me > LARGEST)
        self.assertKweli(me <= LARGEST)
        self.assertUongo(me >= LARGEST)
        self.assertUongo(me < SMALLEST)
        self.assertKweli(me > SMALLEST)
        self.assertUongo(me <= SMALLEST)
        self.assertKweli(me >= SMALLEST)

    eleza test_harmful_mixed_comparison(self):
        me = self.theclass(1, 1, 1)

        self.assertRaises(TypeError, lambda: me < ())
        self.assertRaises(TypeError, lambda: me <= ())
        self.assertRaises(TypeError, lambda: me > ())
        self.assertRaises(TypeError, lambda: me >= ())

        self.assertRaises(TypeError, lambda: () < me)
        self.assertRaises(TypeError, lambda: () <= me)
        self.assertRaises(TypeError, lambda: () > me)
        self.assertRaises(TypeError, lambda: () >= me)

#############################################################################
# timedelta tests

kundi TestTimeDelta(HarmlessMixedComparison, unittest.TestCase):

    thekundi = timedelta

    eleza test_constructor(self):
        eq = self.assertEqual
        td = timedelta

        # Check keyword args to constructor
        eq(td(), td(weeks=0, days=0, hours=0, minutes=0, seconds=0,
                    milliseconds=0, microseconds=0))
        eq(td(1), td(days=1))
        eq(td(0, 1), td(seconds=1))
        eq(td(0, 0, 1), td(microseconds=1))
        eq(td(weeks=1), td(days=7))
        eq(td(days=1), td(hours=24))
        eq(td(hours=1), td(minutes=60))
        eq(td(minutes=1), td(seconds=60))
        eq(td(seconds=1), td(milliseconds=1000))
        eq(td(milliseconds=1), td(microseconds=1000))

        # Check float args to constructor
        eq(td(weeks=1.0/7), td(days=1))
        eq(td(days=1.0/24), td(hours=1))
        eq(td(hours=1.0/60), td(minutes=1))
        eq(td(minutes=1.0/60), td(seconds=1))
        eq(td(seconds=0.001), td(milliseconds=1))
        eq(td(milliseconds=0.001), td(microseconds=1))

    eleza test_computations(self):
        eq = self.assertEqual
        td = timedelta

        a = td(7) # One week
        b = td(0, 60) # One minute
        c = td(0, 0, 1000) # One millisecond
        eq(a+b+c, td(7, 60, 1000))
        eq(a-b, td(6, 24*3600 - 60))
        eq(b.__rsub__(a), td(6, 24*3600 - 60))
        eq(-a, td(-7))
        eq(+a, td(7))
        eq(-b, td(-1, 24*3600 - 60))
        eq(-c, td(-1, 24*3600 - 1, 999000))
        eq(abs(a), a)
        eq(abs(-a), a)
        eq(td(6, 24*3600), a)
        eq(td(0, 0, 60*1000000), b)
        eq(a*10, td(70))
        eq(a*10, 10*a)
        eq(a*10, 10*a)
        eq(b*10, td(0, 600))
        eq(10*b, td(0, 600))
        eq(b*10, td(0, 600))
        eq(c*10, td(0, 0, 10000))
        eq(10*c, td(0, 0, 10000))
        eq(c*10, td(0, 0, 10000))
        eq(a*-1, -a)
        eq(b*-2, -b-b)
        eq(c*-2, -c+-c)
        eq(b*(60*24), (b*60)*24)
        eq(b*(60*24), (60*b)*24)
        eq(c*1000, td(0, 1))
        eq(1000*c, td(0, 1))
        eq(a//7, td(1))
        eq(b//10, td(0, 6))
        eq(c//1000, td(0, 0, 1))
        eq(a//10, td(0, 7*24*360))
        eq(a//3600000, td(0, 0, 7*24*1000))
        eq(a/0.5, td(14))
        eq(b/0.5, td(0, 120))
        eq(a/7, td(1))
        eq(b/10, td(0, 6))
        eq(c/1000, td(0, 0, 1))
        eq(a/10, td(0, 7*24*360))
        eq(a/3600000, td(0, 0, 7*24*1000))

        # Multiplication by float
        us = td(microseconds=1)
        eq((3*us) * 0.5, 2*us)
        eq((5*us) * 0.5, 2*us)
        eq(0.5 * (3*us), 2*us)
        eq(0.5 * (5*us), 2*us)
        eq((-3*us) * 0.5, -2*us)
        eq((-5*us) * 0.5, -2*us)

        # Issue #23521
        eq(td(seconds=1) * 0.123456, td(microseconds=123456))
        eq(td(seconds=1) * 0.6112295, td(microseconds=611229))

        # Division by int na float
        eq((3*us) / 2, 2*us)
        eq((5*us) / 2, 2*us)
        eq((-3*us) / 2.0, -2*us)
        eq((-5*us) / 2.0, -2*us)
        eq((3*us) / -2, -2*us)
        eq((5*us) / -2, -2*us)
        eq((3*us) / -2.0, -2*us)
        eq((5*us) / -2.0, -2*us)
        kila i kwenye range(-10, 10):
            eq((i*us/3)//us, round(i/3))
        kila i kwenye range(-10, 10):
            eq((i*us/-3)//us, round(i/-3))

        # Issue #23521
        eq(td(seconds=1) / (1 / 0.6112295), td(microseconds=611229))

        # Issue #11576
        eq(td(999999999, 86399, 999999) - td(999999999, 86399, 999998),
           td(0, 0, 1))
        eq(td(999999999, 1, 1) - td(999999999, 1, 0),
           td(0, 0, 1))

    eleza test_disallowed_computations(self):
        a = timedelta(42)

        # Add/sub ints ama floats should be illegal
        kila i kwenye 1, 1.0:
            self.assertRaises(TypeError, lambda: a+i)
            self.assertRaises(TypeError, lambda: a-i)
            self.assertRaises(TypeError, lambda: i+a)
            self.assertRaises(TypeError, lambda: i-a)

        # Division of int by timedelta doesn't make sense.
        # Division by zero doesn't make sense.
        zero = 0
        self.assertRaises(TypeError, lambda: zero // a)
        self.assertRaises(ZeroDivisionError, lambda: a // zero)
        self.assertRaises(ZeroDivisionError, lambda: a / zero)
        self.assertRaises(ZeroDivisionError, lambda: a / 0.0)
        self.assertRaises(TypeError, lambda: a / '')

    @support.requires_IEEE_754
    eleza test_disallowed_special(self):
        a = timedelta(42)
        self.assertRaises(ValueError, a.__mul__, NAN)
        self.assertRaises(ValueError, a.__truediv__, NAN)

    eleza test_basic_attributes(self):
        days, seconds, us = 1, 7, 31
        td = timedelta(days, seconds, us)
        self.assertEqual(td.days, days)
        self.assertEqual(td.seconds, seconds)
        self.assertEqual(td.microseconds, us)

    eleza test_total_seconds(self):
        td = timedelta(days=365)
        self.assertEqual(td.total_seconds(), 31536000.0)
        kila total_seconds kwenye [123456.789012, -123456.789012, 0.123456, 0, 1e6]:
            td = timedelta(seconds=total_seconds)
            self.assertEqual(td.total_seconds(), total_seconds)
        # Issue8644: Test that td.total_seconds() has the same
        # accuracy kama td / timedelta(seconds=1).
        kila ms kwenye [-1, -2, -123]:
            td = timedelta(microseconds=ms)
            self.assertEqual(td.total_seconds(), td / timedelta(seconds=1))

    eleza test_carries(self):
        t1 = timedelta(days=100,
                       weeks=-7,
                       hours=-24*(100-49),
                       minutes=-3,
                       seconds=12,
                       microseconds=(3*60 - 12) * 1e6 + 1)
        t2 = timedelta(microseconds=1)
        self.assertEqual(t1, t2)

    eleza test_hash_equality(self):
        t1 = timedelta(days=100,
                       weeks=-7,
                       hours=-24*(100-49),
                       minutes=-3,
                       seconds=12,
                       microseconds=(3*60 - 12) * 1000000)
        t2 = timedelta()
        self.assertEqual(hash(t1), hash(t2))

        t1 += timedelta(weeks=7)
        t2 += timedelta(days=7*7)
        self.assertEqual(t1, t2)
        self.assertEqual(hash(t1), hash(t2))

        d = {t1: 1}
        d[t2] = 2
        self.assertEqual(len(d), 1)
        self.assertEqual(d[t1], 2)

    eleza test_pickling(self):
        args = 12, 34, 56
        orig = timedelta(*args)
        kila pickler, unpickler, proto kwenye pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)

    eleza test_compare(self):
        t1 = timedelta(2, 3, 4)
        t2 = timedelta(2, 3, 4)
        self.assertEqual(t1, t2)
        self.assertKweli(t1 <= t2)
        self.assertKweli(t1 >= t2)
        self.assertUongo(t1 != t2)
        self.assertUongo(t1 < t2)
        self.assertUongo(t1 > t2)

        kila args kwenye (3, 3, 3), (2, 4, 4), (2, 3, 5):
            t2 = timedelta(*args)   # this ni larger than t1
            self.assertKweli(t1 < t2)
            self.assertKweli(t2 > t1)
            self.assertKweli(t1 <= t2)
            self.assertKweli(t2 >= t1)
            self.assertKweli(t1 != t2)
            self.assertKweli(t2 != t1)
            self.assertUongo(t1 == t2)
            self.assertUongo(t2 == t1)
            self.assertUongo(t1 > t2)
            self.assertUongo(t2 < t1)
            self.assertUongo(t1 >= t2)
            self.assertUongo(t2 <= t1)

        kila badarg kwenye OTHERSTUFF:
            self.assertEqual(t1 == badarg, Uongo)
            self.assertEqual(t1 != badarg, Kweli)
            self.assertEqual(badarg == t1, Uongo)
            self.assertEqual(badarg != t1, Kweli)

            self.assertRaises(TypeError, lambda: t1 <= badarg)
            self.assertRaises(TypeError, lambda: t1 < badarg)
            self.assertRaises(TypeError, lambda: t1 > badarg)
            self.assertRaises(TypeError, lambda: t1 >= badarg)
            self.assertRaises(TypeError, lambda: badarg <= t1)
            self.assertRaises(TypeError, lambda: badarg < t1)
            self.assertRaises(TypeError, lambda: badarg > t1)
            self.assertRaises(TypeError, lambda: badarg >= t1)

    eleza test_str(self):
        td = timedelta
        eq = self.assertEqual

        eq(str(td(1)), "1 day, 0:00:00")
        eq(str(td(-1)), "-1 day, 0:00:00")
        eq(str(td(2)), "2 days, 0:00:00")
        eq(str(td(-2)), "-2 days, 0:00:00")

        eq(str(td(hours=12, minutes=58, seconds=59)), "12:58:59")
        eq(str(td(hours=2, minutes=3, seconds=4)), "2:03:04")
        eq(str(td(weeks=-30, hours=23, minutes=12, seconds=34)),
           "-210 days, 23:12:34")

        eq(str(td(milliseconds=1)), "0:00:00.001000")
        eq(str(td(microseconds=3)), "0:00:00.000003")

        eq(str(td(days=999999999, hours=23, minutes=59, seconds=59,
                   microseconds=999999)),
           "999999999 days, 23:59:59.999999")

    eleza test_repr(self):
        name = 'datetime.' + self.theclass.__name__
        self.assertEqual(repr(self.theclass(1)),
                         "%s(days=1)" % name)
        self.assertEqual(repr(self.theclass(10, 2)),
                         "%s(days=10, seconds=2)" % name)
        self.assertEqual(repr(self.theclass(-10, 2, 400000)),
                         "%s(days=-10, seconds=2, microseconds=400000)" % name)
        self.assertEqual(repr(self.theclass(seconds=60)),
                         "%s(seconds=60)" % name)
        self.assertEqual(repr(self.theclass()),
                         "%s(0)" % name)
        self.assertEqual(repr(self.theclass(microseconds=100)),
                         "%s(microseconds=100)" % name)
        self.assertEqual(repr(self.theclass(days=1, microseconds=100)),
                         "%s(days=1, microseconds=100)" % name)
        self.assertEqual(repr(self.theclass(seconds=1, microseconds=100)),
                         "%s(seconds=1, microseconds=100)" % name)

    eleza test_roundtrip(self):
        kila td kwenye (timedelta(days=999999999, hours=23, minutes=59,
                             seconds=59, microseconds=999999),
                   timedelta(days=-999999999),
                   timedelta(days=-999999999, seconds=1),
                   timedelta(days=1, seconds=2, microseconds=3)):

            # Verify td -> string -> td identity.
            s = repr(td)
            self.assertKweli(s.startswith('datetime.'))
            s = s[9:]
            td2 = eval(s)
            self.assertEqual(td, td2)

            # Verify identity via reconstructing kutoka pieces.
            td2 = timedelta(td.days, td.seconds, td.microseconds)
            self.assertEqual(td, td2)

    eleza test_resolution_info(self):
        self.assertIsInstance(timedelta.min, timedelta)
        self.assertIsInstance(timedelta.max, timedelta)
        self.assertIsInstance(timedelta.resolution, timedelta)
        self.assertKweli(timedelta.max > timedelta.min)
        self.assertEqual(timedelta.min, timedelta(-999999999))
        self.assertEqual(timedelta.max, timedelta(999999999, 24*3600-1, 1e6-1))
        self.assertEqual(timedelta.resolution, timedelta(0, 0, 1))

    eleza test_overflow(self):
        tiny = timedelta.resolution

        td = timedelta.min + tiny
        td -= tiny  # no problem
        self.assertRaises(OverflowError, td.__sub__, tiny)
        self.assertRaises(OverflowError, td.__add__, -tiny)

        td = timedelta.max - tiny
        td += tiny  # no problem
        self.assertRaises(OverflowError, td.__add__, tiny)
        self.assertRaises(OverflowError, td.__sub__, -tiny)

        self.assertRaises(OverflowError, lambda: -timedelta.max)

        day = timedelta(1)
        self.assertRaises(OverflowError, day.__mul__, 10**9)
        self.assertRaises(OverflowError, day.__mul__, 1e9)
        self.assertRaises(OverflowError, day.__truediv__, 1e-20)
        self.assertRaises(OverflowError, day.__truediv__, 1e-10)
        self.assertRaises(OverflowError, day.__truediv__, 9e-10)

    @support.requires_IEEE_754
    eleza _test_overflow_special(self):
        day = timedelta(1)
        self.assertRaises(OverflowError, day.__mul__, INF)
        self.assertRaises(OverflowError, day.__mul__, -INF)

    eleza test_microsecond_rounding(self):
        td = timedelta
        eq = self.assertEqual

        # Single-field rounding.
        eq(td(milliseconds=0.4/1000), td(0))    # rounds to 0
        eq(td(milliseconds=-0.4/1000), td(0))    # rounds to 0
        eq(td(milliseconds=0.5/1000), td(microseconds=0))
        eq(td(milliseconds=-0.5/1000), td(microseconds=-0))
        eq(td(milliseconds=0.6/1000), td(microseconds=1))
        eq(td(milliseconds=-0.6/1000), td(microseconds=-1))
        eq(td(milliseconds=1.5/1000), td(microseconds=2))
        eq(td(milliseconds=-1.5/1000), td(microseconds=-2))
        eq(td(seconds=0.5/10**6), td(microseconds=0))
        eq(td(seconds=-0.5/10**6), td(microseconds=-0))
        eq(td(seconds=1/2**7), td(microseconds=7812))
        eq(td(seconds=-1/2**7), td(microseconds=-7812))

        # Rounding due to contributions kutoka more than one field.
        us_per_hour = 3600e6
        us_per_day = us_per_hour * 24
        eq(td(days=.4/us_per_day), td(0))
        eq(td(hours=.2/us_per_hour), td(0))
        eq(td(days=.4/us_per_day, hours=.2/us_per_hour), td(microseconds=1))

        eq(td(days=-.4/us_per_day), td(0))
        eq(td(hours=-.2/us_per_hour), td(0))
        eq(td(days=-.4/us_per_day, hours=-.2/us_per_hour), td(microseconds=-1))

        # Test kila a patch kwenye Issue 8860
        eq(td(microseconds=0.5), 0.5*td(microseconds=1.0))
        eq(td(microseconds=0.5)//td.resolution, 0.5*td.resolution//td.resolution)

    eleza test_massive_normalization(self):
        td = timedelta(microseconds=-1)
        self.assertEqual((td.days, td.seconds, td.microseconds),
                         (-1, 24*3600-1, 999999))

    eleza test_bool(self):
        self.assertKweli(timedelta(1))
        self.assertKweli(timedelta(0, 1))
        self.assertKweli(timedelta(0, 0, 1))
        self.assertKweli(timedelta(microseconds=1))
        self.assertUongo(timedelta(0))

    eleza test_subclass_timedelta(self):

        kundi T(timedelta):
            @staticmethod
            eleza kutoka_td(td):
                rudisha T(td.days, td.seconds, td.microseconds)

            eleza as_hours(self):
                sum = (self.days * 24 +
                       self.seconds / 3600.0 +
                       self.microseconds / 3600e6)
                rudisha round(sum)

        t1 = T(days=1)
        self.assertIs(type(t1), T)
        self.assertEqual(t1.as_hours(), 24)

        t2 = T(days=-1, seconds=-3600)
        self.assertIs(type(t2), T)
        self.assertEqual(t2.as_hours(), -25)

        t3 = t1 + t2
        self.assertIs(type(t3), timedelta)
        t4 = T.kutoka_td(t3)
        self.assertIs(type(t4), T)
        self.assertEqual(t3.days, t4.days)
        self.assertEqual(t3.seconds, t4.seconds)
        self.assertEqual(t3.microseconds, t4.microseconds)
        self.assertEqual(str(t3), str(t4))
        self.assertEqual(t4.as_hours(), -1)

    eleza test_subclass_date(self):
        kundi DateSubclass(date):
            pita

        d1 = DateSubclass(2018, 1, 5)
        td = timedelta(days=1)

        tests = [
            ('add', lambda d, t: d + t, DateSubclass(2018, 1, 6)),
            ('radd', lambda d, t: t + d, DateSubclass(2018, 1, 6)),
            ('sub', lambda d, t: d - t, DateSubclass(2018, 1, 4)),
        ]

        kila name, func, expected kwenye tests:
            with self.subTest(name):
                act = func(d1, td)
                self.assertEqual(act, expected)
                self.assertIsInstance(act, DateSubclass)

    eleza test_subclass_datetime(self):
        kundi DateTimeSubclass(datetime):
            pita

        d1 = DateTimeSubclass(2018, 1, 5, 12, 30)
        td = timedelta(days=1, minutes=30)

        tests = [
            ('add', lambda d, t: d + t, DateTimeSubclass(2018, 1, 6, 13)),
            ('radd', lambda d, t: t + d, DateTimeSubclass(2018, 1, 6, 13)),
            ('sub', lambda d, t: d - t, DateTimeSubclass(2018, 1, 4, 12)),
        ]

        kila name, func, expected kwenye tests:
            with self.subTest(name):
                act = func(d1, td)
                self.assertEqual(act, expected)
                self.assertIsInstance(act, DateTimeSubclass)

    eleza test_division(self):
        t = timedelta(hours=1, minutes=24, seconds=19)
        second = timedelta(seconds=1)
        self.assertEqual(t / second, 5059.0)
        self.assertEqual(t // second, 5059)

        t = timedelta(minutes=2, seconds=30)
        minute = timedelta(minutes=1)
        self.assertEqual(t / minute, 2.5)
        self.assertEqual(t // minute, 2)

        zerotd = timedelta(0)
        self.assertRaises(ZeroDivisionError, truediv, t, zerotd)
        self.assertRaises(ZeroDivisionError, floordiv, t, zerotd)

        # self.assertRaises(TypeError, truediv, t, 2)
        # note: floor division of a timedelta by an integer *is*
        # currently permitted.

    eleza test_remainder(self):
        t = timedelta(minutes=2, seconds=30)
        minute = timedelta(minutes=1)
        r = t % minute
        self.assertEqual(r, timedelta(seconds=30))

        t = timedelta(minutes=-2, seconds=30)
        r = t %  minute
        self.assertEqual(r, timedelta(seconds=30))

        zerotd = timedelta(0)
        self.assertRaises(ZeroDivisionError, mod, t, zerotd)

        self.assertRaises(TypeError, mod, t, 10)

    eleza test_divmod(self):
        t = timedelta(minutes=2, seconds=30)
        minute = timedelta(minutes=1)
        q, r = divmod(t, minute)
        self.assertEqual(q, 2)
        self.assertEqual(r, timedelta(seconds=30))

        t = timedelta(minutes=-2, seconds=30)
        q, r = divmod(t, minute)
        self.assertEqual(q, -2)
        self.assertEqual(r, timedelta(seconds=30))

        zerotd = timedelta(0)
        self.assertRaises(ZeroDivisionError, divmod, t, zerotd)

        self.assertRaises(TypeError, divmod, t, 10)

    eleza test_issue31293(self):
        # The interpreter shouldn't crash kwenye case a timedelta ni divided or
        # multiplied by a float with a bad as_integer_ratio() method.
        eleza get_bad_float(bad_ratio):
            kundi BadFloat(float):
                eleza as_integer_ratio(self):
                    rudisha bad_ratio
            rudisha BadFloat()

        with self.assertRaises(TypeError):
            timedelta() / get_bad_float(1 << 1000)
        with self.assertRaises(TypeError):
            timedelta() * get_bad_float(1 << 1000)

        kila bad_ratio kwenye [(), (42, ), (1, 2, 3)]:
            with self.assertRaises(ValueError):
                timedelta() / get_bad_float(bad_ratio)
            with self.assertRaises(ValueError):
                timedelta() * get_bad_float(bad_ratio)

    eleza test_issue31752(self):
        # The interpreter shouldn't crash because divmod() rudishas negative
        # remainder.
        kundi BadInt(int):
            eleza __mul__(self, other):
                rudisha Prod()
            eleza __rmul__(self, other):
                rudisha Prod()
            eleza __floordiv__(self, other):
                rudisha Prod()
            eleza __rfloordiv__(self, other):
                rudisha Prod()

        kundi Prod:
            eleza __add__(self, other):
                rudisha Sum()
            eleza __radd__(self, other):
                rudisha Sum()

        kundi Sum(int):
            eleza __divmod__(self, other):
                rudisha divmodresult

        kila divmodresult kwenye [Tupu, (), (0, 1, 2), (0, -1)]:
            with self.subTest(divmodresult=divmodresult):
                # The following examples should sio crash.
                jaribu:
                    timedelta(microseconds=BadInt(1))
                tatizo TypeError:
                    pita
                jaribu:
                    timedelta(hours=BadInt(1))
                tatizo TypeError:
                    pita
                jaribu:
                    timedelta(weeks=BadInt(1))
                tatizo (TypeError, ValueError):
                    pita
                jaribu:
                    timedelta(1) * BadInt(1)
                tatizo (TypeError, ValueError):
                    pita
                jaribu:
                    BadInt(1) * timedelta(1)
                tatizo TypeError:
                    pita
                jaribu:
                    timedelta(1) // BadInt(1)
                tatizo TypeError:
                    pita


#############################################################################
# date tests

kundi TestDateOnly(unittest.TestCase):
    # Tests here won't pita ikiwa also run on datetime objects, so don't
    # subkundi this to test datetimes too.

    eleza test_delta_non_days_ignored(self):
        dt = date(2000, 1, 2)
        delta = timedelta(days=1, hours=2, minutes=3, seconds=4,
                          microseconds=5)
        days = timedelta(delta.days)
        self.assertEqual(days, timedelta(1))

        dt2 = dt + delta
        self.assertEqual(dt2, dt + days)

        dt2 = delta + dt
        self.assertEqual(dt2, dt + days)

        dt2 = dt - delta
        self.assertEqual(dt2, dt - days)

        delta = -delta
        days = timedelta(delta.days)
        self.assertEqual(days, timedelta(-2))

        dt2 = dt + delta
        self.assertEqual(dt2, dt + days)

        dt2 = delta + dt
        self.assertEqual(dt2, dt + days)

        dt2 = dt - delta
        self.assertEqual(dt2, dt - days)

kundi SubclassDate(date):
    sub_var = 1

kundi TestDate(HarmlessMixedComparison, unittest.TestCase):
    # Tests here should pita kila both dates na datetimes, tatizo kila a
    # few tests that TestDateTime overrides.

    thekundi = date

    eleza test_basic_attributes(self):
        dt = self.theclass(2002, 3, 1)
        self.assertEqual(dt.year, 2002)
        self.assertEqual(dt.month, 3)
        self.assertEqual(dt.day, 1)

    eleza test_roundtrip(self):
        kila dt kwenye (self.theclass(1, 2, 3),
                   self.theclass.today()):
            # Verify dt -> string -> date identity.
            s = repr(dt)
            self.assertKweli(s.startswith('datetime.'))
            s = s[9:]
            dt2 = eval(s)
            self.assertEqual(dt, dt2)

            # Verify identity via reconstructing kutoka pieces.
            dt2 = self.theclass(dt.year, dt.month, dt.day)
            self.assertEqual(dt, dt2)

    eleza test_ordinal_conversions(self):
        # Check some fixed values.
        kila y, m, d, n kwenye [(1, 1, 1, 1),      # calendar origin
                           (1, 12, 31, 365),
                           (2, 1, 1, 366),
                           # first example kutoka "Calendrical Calculations"
                           (1945, 11, 12, 710347)]:
            d = self.theclass(y, m, d)
            self.assertEqual(n, d.toordinal())
            kutokaord = self.theclass.kutokaordinal(n)
            self.assertEqual(d, kutokaord)
            ikiwa hasattr(kutokaord, "hour"):
            # ikiwa we're checking something fancier than a date, verify
            # the extra fields have been zeroed out
                self.assertEqual(kutokaord.hour, 0)
                self.assertEqual(kutokaord.minute, 0)
                self.assertEqual(kutokaord.second, 0)
                self.assertEqual(kutokaord.microsecond, 0)

        # Check first na last days of year spottily across the whole
        # range of years supported.
        kila year kwenye range(MINYEAR, MAXYEAR+1, 7):
            # Verify (year, 1, 1) -> ordinal -> y, m, d ni identity.
            d = self.theclass(year, 1, 1)
            n = d.toordinal()
            d2 = self.theclass.kutokaordinal(n)
            self.assertEqual(d, d2)
            # Verify that moving back a day gets to the end of year-1.
            ikiwa year > 1:
                d = self.theclass.kutokaordinal(n-1)
                d2 = self.theclass(year-1, 12, 31)
                self.assertEqual(d, d2)
                self.assertEqual(d2.toordinal(), n-1)

        # Test every day kwenye a leap-year na a non-leap year.
        dim = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        kila year, isleap kwenye (2000, Kweli), (2002, Uongo):
            n = self.theclass(year, 1, 1).toordinal()
            kila month, maxday kwenye zip(range(1, 13), dim):
                ikiwa month == 2 na isleap:
                    maxday += 1
                kila day kwenye range(1, maxday+1):
                    d = self.theclass(year, month, day)
                    self.assertEqual(d.toordinal(), n)
                    self.assertEqual(d, self.theclass.kutokaordinal(n))
                    n += 1

    eleza test_extreme_ordinals(self):
        a = self.theclass.min
        a = self.theclass(a.year, a.month, a.day)  # get rid of time parts
        aord = a.toordinal()
        b = a.kutokaordinal(aord)
        self.assertEqual(a, b)

        self.assertRaises(ValueError, lambda: a.kutokaordinal(aord - 1))

        b = a + timedelta(days=1)
        self.assertEqual(b.toordinal(), aord + 1)
        self.assertEqual(b, self.theclass.kutokaordinal(aord + 1))

        a = self.theclass.max
        a = self.theclass(a.year, a.month, a.day)  # get rid of time parts
        aord = a.toordinal()
        b = a.kutokaordinal(aord)
        self.assertEqual(a, b)

        self.assertRaises(ValueError, lambda: a.kutokaordinal(aord + 1))

        b = a - timedelta(days=1)
        self.assertEqual(b.toordinal(), aord - 1)
        self.assertEqual(b, self.theclass.kutokaordinal(aord - 1))

    eleza test_bad_constructor_arguments(self):
        # bad years
        self.theclass(MINYEAR, 1, 1)  # no exception
        self.theclass(MAXYEAR, 1, 1)  # no exception
        self.assertRaises(ValueError, self.theclass, MINYEAR-1, 1, 1)
        self.assertRaises(ValueError, self.theclass, MAXYEAR+1, 1, 1)
        # bad months
        self.theclass(2000, 1, 1)    # no exception
        self.theclass(2000, 12, 1)   # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 0, 1)
        self.assertRaises(ValueError, self.theclass, 2000, 13, 1)
        # bad days
        self.theclass(2000, 2, 29)   # no exception
        self.theclass(2004, 2, 29)   # no exception
        self.theclass(2400, 2, 29)   # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 2, 30)
        self.assertRaises(ValueError, self.theclass, 2001, 2, 29)
        self.assertRaises(ValueError, self.theclass, 2100, 2, 29)
        self.assertRaises(ValueError, self.theclass, 1900, 2, 29)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 0)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 32)

    eleza test_hash_equality(self):
        d = self.theclass(2000, 12, 31)
        # same thing
        e = self.theclass(2000, 12, 31)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

        d = self.theclass(2001,  1,  1)
        # same thing
        e = self.theclass(2001,  1,  1)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

    eleza test_computations(self):
        a = self.theclass(2002, 1, 31)
        b = self.theclass(1956, 1, 31)
        c = self.theclass(2001,2,1)

        diff = a-b
        self.assertEqual(diff.days, 46*365 + len(range(1956, 2002, 4)))
        self.assertEqual(diff.seconds, 0)
        self.assertEqual(diff.microseconds, 0)

        day = timedelta(1)
        week = timedelta(7)
        a = self.theclass(2002, 3, 2)
        self.assertEqual(a + day, self.theclass(2002, 3, 3))
        self.assertEqual(day + a, self.theclass(2002, 3, 3))
        self.assertEqual(a - day, self.theclass(2002, 3, 1))
        self.assertEqual(-day + a, self.theclass(2002, 3, 1))
        self.assertEqual(a + week, self.theclass(2002, 3, 9))
        self.assertEqual(a - week, self.theclass(2002, 2, 23))
        self.assertEqual(a + 52*week, self.theclass(2003, 3, 1))
        self.assertEqual(a - 52*week, self.theclass(2001, 3, 3))
        self.assertEqual((a + week) - a, week)
        self.assertEqual((a + day) - a, day)
        self.assertEqual((a - week) - a, -week)
        self.assertEqual((a - day) - a, -day)
        self.assertEqual(a - (a + week), -week)
        self.assertEqual(a - (a + day), -day)
        self.assertEqual(a - (a - week), week)
        self.assertEqual(a - (a - day), day)
        self.assertEqual(c - (c - day), day)

        # Add/sub ints ama floats should be illegal
        kila i kwenye 1, 1.0:
            self.assertRaises(TypeError, lambda: a+i)
            self.assertRaises(TypeError, lambda: a-i)
            self.assertRaises(TypeError, lambda: i+a)
            self.assertRaises(TypeError, lambda: i-a)

        # delta - date ni senseless.
        self.assertRaises(TypeError, lambda: day - a)
        # mixing date na (delta ama date) via * ama // ni senseless
        self.assertRaises(TypeError, lambda: day * a)
        self.assertRaises(TypeError, lambda: a * day)
        self.assertRaises(TypeError, lambda: day // a)
        self.assertRaises(TypeError, lambda: a // day)
        self.assertRaises(TypeError, lambda: a * a)
        self.assertRaises(TypeError, lambda: a // a)
        # date + date ni senseless
        self.assertRaises(TypeError, lambda: a + a)

    eleza test_overflow(self):
        tiny = self.theclass.resolution

        kila delta kwenye [tiny, timedelta(1), timedelta(2)]:
            dt = self.theclass.min + delta
            dt -= delta  # no problem
            self.assertRaises(OverflowError, dt.__sub__, delta)
            self.assertRaises(OverflowError, dt.__add__, -delta)

            dt = self.theclass.max - delta
            dt += delta  # no problem
            self.assertRaises(OverflowError, dt.__add__, delta)
            self.assertRaises(OverflowError, dt.__sub__, -delta)

    eleza test_kutokatimestamp(self):
        agiza time

        # Try an arbitrary fixed value.
        year, month, day = 1999, 9, 19
        ts = time.mktime((year, month, day, 0, 0, 0, 0, 0, -1))
        d = self.theclass.kutokatimestamp(ts)
        self.assertEqual(d.year, year)
        self.assertEqual(d.month, month)
        self.assertEqual(d.day, day)

    eleza test_insane_kutokatimestamp(self):
        # It's possible that some platform maps time_t to double,
        # na that this test will fail there.  This test should
        # exempt such platforms (provided they rudisha reasonable
        # results!).
        kila insane kwenye -1e200, 1e200:
            self.assertRaises(OverflowError, self.theclass.kutokatimestamp,
                              insane)

    eleza test_today(self):
        agiza time

        # We claim that today() ni like kutokatimestamp(time.time()), so
        # prove it.
        kila dummy kwenye range(3):
            today = self.theclass.today()
            ts = time.time()
            todayagain = self.theclass.kutokatimestamp(ts)
            ikiwa today == todayagain:
                koma
            # There are several legit reasons that could fail:
            # 1. It recently became midnight, between the today() na the
            #    time() calls.
            # 2. The platform time() has such fine resolution that we'll
            #    never get the same value twice.
            # 3. The platform time() has poor resolution, na we just
            #    happened to call today() right before a resolution quantum
            #    boundary.
            # 4. The system clock got fiddled between calls.
            # In any case, wait a little wakati na try again.
            time.sleep(0.1)

        # It worked ama it didn't.  If it didn't, assume it's reason #2, and
        # let the test pita ikiwa they're within half a second of each other.
        ikiwa today != todayagain:
            self.assertAlmostEqual(todayagain, today,
                                   delta=timedelta(seconds=0.5))

    eleza test_weekday(self):
        kila i kwenye range(7):
            # March 4, 2002 ni a Monday
            self.assertEqual(self.theclass(2002, 3, 4+i).weekday(), i)
            self.assertEqual(self.theclass(2002, 3, 4+i).isoweekday(), i+1)
            # January 2, 1956 ni a Monday
            self.assertEqual(self.theclass(1956, 1, 2+i).weekday(), i)
            self.assertEqual(self.theclass(1956, 1, 2+i).isoweekday(), i+1)

    eleza test_isocalendar(self):
        # Check examples kutoka
        # http://www.phys.uu.nl/~vgent/calendar/isocalendar.htm
        kila i kwenye range(7):
            d = self.theclass(2003, 12, 22+i)
            self.assertEqual(d.isocalendar(), (2003, 52, i+1))
            d = self.theclass(2003, 12, 29) + timedelta(i)
            self.assertEqual(d.isocalendar(), (2004, 1, i+1))
            d = self.theclass(2004, 1, 5+i)
            self.assertEqual(d.isocalendar(), (2004, 2, i+1))
            d = self.theclass(2009, 12, 21+i)
            self.assertEqual(d.isocalendar(), (2009, 52, i+1))
            d = self.theclass(2009, 12, 28) + timedelta(i)
            self.assertEqual(d.isocalendar(), (2009, 53, i+1))
            d = self.theclass(2010, 1, 4+i)
            self.assertEqual(d.isocalendar(), (2010, 1, i+1))

    eleza test_iso_long_years(self):
        # Calculate long ISO years na compare to table kutoka
        # http://www.phys.uu.nl/~vgent/calendar/isocalendar.htm
        ISO_LONG_YEARS_TABLE = """
              4   32   60   88
              9   37   65   93
             15   43   71   99
             20   48   76
             26   54   82

            105  133  161  189
            111  139  167  195
            116  144  172
            122  150  178
            128  156  184

            201  229  257  285
            207  235  263  291
            212  240  268  296
            218  246  274
            224  252  280

            303  331  359  387
            308  336  364  392
            314  342  370  398
            320  348  376
            325  353  381
        """
        iso_long_years = sorted(map(int, ISO_LONG_YEARS_TABLE.split()))
        L = []
        kila i kwenye range(400):
            d = self.theclass(2000+i, 12, 31)
            d1 = self.theclass(1600+i, 12, 31)
            self.assertEqual(d.isocalendar()[1:], d1.isocalendar()[1:])
            ikiwa d.isocalendar()[1] == 53:
                L.append(i)
        self.assertEqual(L, iso_long_years)

    eleza test_isoformat(self):
        t = self.theclass(2, 3, 2)
        self.assertEqual(t.isoformat(), "0002-03-02")

    eleza test_ctime(self):
        t = self.theclass(2002, 3, 2)
        self.assertEqual(t.ctime(), "Sat Mar  2 00:00:00 2002")

    eleza test_strftime(self):
        t = self.theclass(2005, 3, 2)
        self.assertEqual(t.strftime("m:%m d:%d y:%y"), "m:03 d:02 y:05")
        self.assertEqual(t.strftime(""), "") # SF bug #761337
        self.assertEqual(t.strftime('x'*1000), 'x'*1000) # SF bug #1556784

        self.assertRaises(TypeError, t.strftime) # needs an arg
        self.assertRaises(TypeError, t.strftime, "one", "two") # too many args
        self.assertRaises(TypeError, t.strftime, 42) # arg wrong type

        # test that unicode input ni allowed (issue 2782)
        self.assertEqual(t.strftime("%m"), "03")

        # A naive object replaces %z na %Z w/ empty strings.
        self.assertEqual(t.strftime("'%z' '%Z'"), "'' ''")

        #make sure that invalid format specifiers are handled correctly
        #self.assertRaises(ValueError, t.strftime, "%e")
        #self.assertRaises(ValueError, t.strftime, "%")
        #self.assertRaises(ValueError, t.strftime, "%#")

        #oh well, some systems just ignore those invalid ones.
        #at least, exercise them to make sure that no crashes
        #are generated
        kila f kwenye ["%e", "%", "%#"]:
            jaribu:
                t.strftime(f)
            tatizo ValueError:
                pita

        # bpo-34482: Check that surrogates don't cause a crash.
        jaribu:
            t.strftime('%y\ud800%m')
        tatizo UnicodeEncodeError:
            pita

        #check that this standard extension works
        t.strftime("%f")

    eleza test_strftime_trailing_percent(self):
        # bpo-35066: Make sure trailing '%' doesn't cause datetime's strftime to
        # complain. Different libcs have different handling of trailing
        # percents, so we simply check datetime's strftime acts the same as
        # time.strftime.
        t = self.theclass(2005, 3, 2)
        jaribu:
            _time.strftime('%')
        tatizo ValueError:
            self.skipTest('time module does sio support trailing %')
        self.assertEqual(t.strftime('%'), _time.strftime('%', t.timetuple()))
        self.assertEqual(
            t.strftime("m:%m d:%d y:%y %"),
            _time.strftime("m:03 d:02 y:05 %", t.timetuple()),
        )

    eleza test_format(self):
        dt = self.theclass(2007, 9, 10)
        self.assertEqual(dt.__format__(''), str(dt))

        with self.assertRaisesRegex(TypeError, 'must be str, sio int'):
            dt.__format__(123)

        # check that a derived class's __str__() gets called
        kundi A(self.theclass):
            eleza __str__(self):
                rudisha 'A'
        a = A(2007, 9, 10)
        self.assertEqual(a.__format__(''), 'A')

        # check that a derived class's strftime gets called
        kundi B(self.theclass):
            eleza strftime(self, format_spec):
                rudisha 'B'
        b = B(2007, 9, 10)
        self.assertEqual(b.__format__(''), str(dt))

        kila fmt kwenye ["m:%m d:%d y:%y",
                    "m:%m d:%d y:%y H:%H M:%M S:%S",
                    "%z %Z",
                    ]:
            self.assertEqual(dt.__format__(fmt), dt.strftime(fmt))
            self.assertEqual(a.__format__(fmt), dt.strftime(fmt))
            self.assertEqual(b.__format__(fmt), 'B')

    eleza test_resolution_info(self):
        # XXX: Should min na max respect subclassing?
        ikiwa issubclass(self.theclass, datetime):
            expected_kundi = datetime
        isipokua:
            expected_kundi = date
        self.assertIsInstance(self.theclass.min, expected_class)
        self.assertIsInstance(self.theclass.max, expected_class)
        self.assertIsInstance(self.theclass.resolution, timedelta)
        self.assertKweli(self.theclass.max > self.theclass.min)

    eleza test_extreme_timedelta(self):
        big = self.theclass.max - self.theclass.min
        # 3652058 days, 23 hours, 59 minutes, 59 seconds, 999999 microseconds
        n = (big.days*24*3600 + big.seconds)*1000000 + big.microseconds
        # n == 315537897599999999 ~= 2**58.13
        justasbig = timedelta(0, 0, n)
        self.assertEqual(big, justasbig)
        self.assertEqual(self.theclass.min + big, self.theclass.max)
        self.assertEqual(self.theclass.max - big, self.theclass.min)

    eleza test_timetuple(self):
        kila i kwenye range(7):
            # January 2, 1956 ni a Monday (0)
            d = self.theclass(1956, 1, 2+i)
            t = d.timetuple()
            self.assertEqual(t, (1956, 1, 2+i, 0, 0, 0, i, 2+i, -1))
            # February 1, 1956 ni a Wednesday (2)
            d = self.theclass(1956, 2, 1+i)
            t = d.timetuple()
            self.assertEqual(t, (1956, 2, 1+i, 0, 0, 0, (2+i)%7, 32+i, -1))
            # March 1, 1956 ni a Thursday (3), na ni the 31+29+1 = 61st day
            # of the year.
            d = self.theclass(1956, 3, 1+i)
            t = d.timetuple()
            self.assertEqual(t, (1956, 3, 1+i, 0, 0, 0, (3+i)%7, 61+i, -1))
            self.assertEqual(t.tm_year, 1956)
            self.assertEqual(t.tm_mon, 3)
            self.assertEqual(t.tm_mday, 1+i)
            self.assertEqual(t.tm_hour, 0)
            self.assertEqual(t.tm_min, 0)
            self.assertEqual(t.tm_sec, 0)
            self.assertEqual(t.tm_wday, (3+i)%7)
            self.assertEqual(t.tm_yday, 61+i)
            self.assertEqual(t.tm_isdst, -1)

    eleza test_pickling(self):
        args = 6, 7, 23
        orig = self.theclass(*args)
        kila pickler, unpickler, proto kwenye pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)
        self.assertEqual(orig.__reduce__(), orig.__reduce_ex__(2))

    eleza test_compat_unpickle(self):
        tests = [
            b"cdatetime\ndate\n(S'\\x07\\xdf\\x0b\\x1b'\ntR.",
            b'cdatetime\ndate\n(U\x04\x07\xdf\x0b\x1btR.',
            b'\x80\x02cdatetime\ndate\nU\x04\x07\xdf\x0b\x1b\x85R.',
        ]
        args = 2015, 11, 27
        expected = self.theclass(*args)
        kila data kwenye tests:
            kila loads kwenye pickle_loads:
                derived = loads(data, encoding='latin1')
                self.assertEqual(derived, expected)

    eleza test_compare(self):
        t1 = self.theclass(2, 3, 4)
        t2 = self.theclass(2, 3, 4)
        self.assertEqual(t1, t2)
        self.assertKweli(t1 <= t2)
        self.assertKweli(t1 >= t2)
        self.assertUongo(t1 != t2)
        self.assertUongo(t1 < t2)
        self.assertUongo(t1 > t2)

        kila args kwenye (3, 3, 3), (2, 4, 4), (2, 3, 5):
            t2 = self.theclass(*args)   # this ni larger than t1
            self.assertKweli(t1 < t2)
            self.assertKweli(t2 > t1)
            self.assertKweli(t1 <= t2)
            self.assertKweli(t2 >= t1)
            self.assertKweli(t1 != t2)
            self.assertKweli(t2 != t1)
            self.assertUongo(t1 == t2)
            self.assertUongo(t2 == t1)
            self.assertUongo(t1 > t2)
            self.assertUongo(t2 < t1)
            self.assertUongo(t1 >= t2)
            self.assertUongo(t2 <= t1)

        kila badarg kwenye OTHERSTUFF:
            self.assertEqual(t1 == badarg, Uongo)
            self.assertEqual(t1 != badarg, Kweli)
            self.assertEqual(badarg == t1, Uongo)
            self.assertEqual(badarg != t1, Kweli)

            self.assertRaises(TypeError, lambda: t1 < badarg)
            self.assertRaises(TypeError, lambda: t1 > badarg)
            self.assertRaises(TypeError, lambda: t1 >= badarg)
            self.assertRaises(TypeError, lambda: badarg <= t1)
            self.assertRaises(TypeError, lambda: badarg < t1)
            self.assertRaises(TypeError, lambda: badarg > t1)
            self.assertRaises(TypeError, lambda: badarg >= t1)

    eleza test_mixed_compare(self):
        our = self.theclass(2000, 4, 5)

        # Our kundi can be compared kila equality to other classes
        self.assertEqual(our == 1, Uongo)
        self.assertEqual(1 == our, Uongo)
        self.assertEqual(our != 1, Kweli)
        self.assertEqual(1 != our, Kweli)

        # But the ordering ni undefined
        self.assertRaises(TypeError, lambda: our < 1)
        self.assertRaises(TypeError, lambda: 1 < our)

        # Repeat those tests with a different class

        kundi SomeClass:
            pita

        their = SomeClass()
        self.assertEqual(our == their, Uongo)
        self.assertEqual(their == our, Uongo)
        self.assertEqual(our != their, Kweli)
        self.assertEqual(their != our, Kweli)
        self.assertRaises(TypeError, lambda: our < their)
        self.assertRaises(TypeError, lambda: their < our)

    eleza test_bool(self):
        # All dates are considered true.
        self.assertKweli(self.theclass.min)
        self.assertKweli(self.theclass.max)

    eleza test_strftime_y2k(self):
        kila y kwenye (1, 49, 70, 99, 100, 999, 1000, 1970):
            d = self.theclass(y, 1, 1)
            # Issue 13305:  For years < 1000, the value ni sio always
            # padded to 4 digits across platforms.  The C standard
            # assumes year >= 1900, so it does sio specify the number
            # of digits.
            ikiwa d.strftime("%Y") != '%04d' % y:
                # Year 42 rudishas '42', sio padded
                self.assertEqual(d.strftime("%Y"), '%d' % y)
                # '0042' ni obtained anyway
                self.assertEqual(d.strftime("%4Y"), '%04d' % y)

    eleza test_replace(self):
        cls = self.theclass
        args = [1, 2, 3]
        base = cls(*args)
        self.assertEqual(base, base.replace())

        i = 0
        kila name, newval kwenye (("year", 2),
                             ("month", 3),
                             ("day", 4)):
            newargs = args[:]
            newargs[i] = newval
            expected = cls(*newargs)
            got = base.replace(**{name: newval})
            self.assertEqual(expected, got)
            i += 1

        # Out of bounds.
        base = cls(2000, 2, 29)
        self.assertRaises(ValueError, base.replace, year=2001)

    eleza test_subclass_replace(self):
        kundi DateSubclass(self.theclass):
            pita

        dt = DateSubclass(2012, 1, 1)
        self.assertIs(type(dt.replace(year=2013)), DateSubclass)

    eleza test_subclass_date(self):

        kundi C(self.theclass):
            theAnswer = 42

            eleza __new__(cls, *args, **kws):
                temp = kws.copy()
                extra = temp.pop('extra')
                result = self.theclass.__new__(cls, *args, **temp)
                result.extra = extra
                rudisha result

            eleza newmeth(self, start):
                rudisha start + self.year + self.month

        args = 2003, 4, 14

        dt1 = self.theclass(*args)
        dt2 = C(*args, **{'extra': 7})

        self.assertEqual(dt2.__class__, C)
        self.assertEqual(dt2.theAnswer, 42)
        self.assertEqual(dt2.extra, 7)
        self.assertEqual(dt1.toordinal(), dt2.toordinal())
        self.assertEqual(dt2.newmeth(-7), dt1.year + dt1.month - 7)

    eleza test_subclass_alternate_constructors(self):
        # Test that alternate constructors call the constructor
        kundi DateSubclass(self.theclass):
            eleza __new__(cls, *args, **kwargs):
                result = self.theclass.__new__(cls, *args, **kwargs)
                result.extra = 7

                rudisha result

        args = (2003, 4, 14)
        d_ord = 731319              # Equivalent ordinal date
        d_isoformat = '2003-04-14'  # Equivalent isoformat()

        base_d = DateSubclass(*args)
        self.assertIsInstance(base_d, DateSubclass)
        self.assertEqual(base_d.extra, 7)

        # Timestamp depends on time zone, so we'll calculate the equivalent here
        ts = datetime.combine(base_d, time(0)).timestamp()

        test_cases = [
            ('kutokaordinal', (d_ord,)),
            ('kutokatimestamp', (ts,)),
            ('kutokaisoformat', (d_isoformat,)),
        ]

        kila constr_name, constr_args kwenye test_cases:
            kila base_obj kwenye (DateSubclass, base_d):
                # Test both the classmethod na method
                with self.subTest(base_obj_type=type(base_obj),
                                  constr_name=constr_name):
                    constr = getattr(base_obj, constr_name)

                    dt = constr(*constr_args)

                    # Test that it creates the right subclass
                    self.assertIsInstance(dt, DateSubclass)

                    # Test that it's equal to the base object
                    self.assertEqual(dt, base_d)

                    # Test that it called the constructor
                    self.assertEqual(dt.extra, 7)

    eleza test_pickling_subclass_date(self):

        args = 6, 7, 23
        orig = SubclassDate(*args)
        kila pickler, unpickler, proto kwenye pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)

    eleza test_backdoor_resistance(self):
        # For fast unpickling, the constructor accepts a pickle byte string.
        # This ni a low-overhead backdoor.  A user can (by intent or
        # mistake) pita a string directly, which (ikiwa it's the right length)
        # will get treated like a pickle, na bypita the normal sanity
        # checks kwenye the constructor.  This can create insane objects.
        # The constructor doesn't want to burn the time to validate all
        # fields, but does check the month field.  This stops, e.g.,
        # datetime.datetime('1995-03-25') kutoka tumaing an insane object.
        base = b'1995-03-25'
        ikiwa sio issubclass(self.theclass, datetime):
            base = base[:4]
        kila month_byte kwenye b'9', b'\0', b'\r', b'\xff':
            self.assertRaises(TypeError, self.theclass,
                                         base[:2] + month_byte + base[3:])
        ikiwa issubclass(self.theclass, datetime):
            # Good bytes, but bad tzinfo:
            with self.assertRaisesRegex(TypeError, '^bad tzinfo state arg$'):
                self.theclass(bytes([1] * len(base)), 'EST')

        kila ord_byte kwenye range(1, 13):
            # This shouldn't blow up because of the month byte alone.  If
            # the implementation changes to do more-careful checking, it may
            # blow up because other fields are insane.
            self.theclass(base[:2] + bytes([ord_byte]) + base[3:])

    eleza test_kutokaisoformat(self):
        # Test that isoformat() ni reversible
        base_dates = [
            (1, 1, 1),
            (1000, 2, 14),
            (1900, 1, 1),
            (2000, 2, 29),
            (2004, 11, 12),
            (2004, 4, 3),
            (2017, 5, 30)
        ]

        kila dt_tuple kwenye base_dates:
            dt = self.theclass(*dt_tuple)
            dt_str = dt.isoformat()
            with self.subTest(dt_str=dt_str):
                dt_rt = self.theclass.kutokaisoformat(dt.isoformat())

                self.assertEqual(dt, dt_rt)

    eleza test_kutokaisoformat_subclass(self):
        kundi DateSubclass(self.theclass):
            pita

        dt = DateSubclass(2014, 12, 14)

        dt_rt = DateSubclass.kutokaisoformat(dt.isoformat())

        self.assertIsInstance(dt_rt, DateSubclass)

    eleza test_kutokaisoformat_fails(self):
        # Test that kutokaisoformat() fails on invalid values
        bad_strs = [
            '',                 # Empty string
            '\ud800',           # bpo-34454: Surrogate code point
            '009-03-04',        # Not 10 characters
            '123456789',        # Not a date
            '200a-12-04',       # Invalid character kwenye year
            '2009-1a-04',       # Invalid character kwenye month
            '2009-12-0a',       # Invalid character kwenye day
            '2009-01-32',       # Invalid day
            '2009-02-29',       # Invalid leap day
            '20090228',         # Valid ISO8601 output sio kutoka isoformat()
            '2009\ud80002\ud80028',     # Separators are surrogate codepoints
        ]

        kila bad_str kwenye bad_strs:
            with self.assertRaises(ValueError):
                self.theclass.kutokaisoformat(bad_str)

    eleza test_kutokaisoformat_fails_typeerror(self):
        # Test that kutokaisoformat fails when pitaed the wrong type
        agiza io

        bad_types = [b'2009-03-01', Tupu, io.StringIO('2009-03-01')]
        kila bad_type kwenye bad_types:
            with self.assertRaises(TypeError):
                self.theclass.kutokaisoformat(bad_type)

    eleza test_kutokaisocalendar(self):
        # For each test case, assert that kutokaisocalendar ni the
        # inverse of the isocalendar function
        dates = [
            (2016, 4, 3),
            (2005, 1, 2),       # (2004, 53, 7)
            (2008, 12, 30),     # (2009, 1, 2)
            (2010, 1, 2),       # (2009, 53, 6)
            (2009, 12, 31),     # (2009, 53, 4)
            (1900, 1, 1),       # Unusual non-leap year (year % 100 == 0)
            (1900, 12, 31),
            (2000, 1, 1),       # Unusual leap year (year % 400 == 0)
            (2000, 12, 31),
            (2004, 1, 1),       # Leap year
            (2004, 12, 31),
            (1, 1, 1),
            (9999, 12, 31),
            (MINYEAR, 1, 1),
            (MAXYEAR, 12, 31),
        ]

        kila datecomps kwenye dates:
            with self.subTest(datecomps=datecomps):
                dobj = self.theclass(*datecomps)
                isocal = dobj.isocalendar()

                d_roundtrip = self.theclass.kutokaisocalendar(*isocal)

                self.assertEqual(dobj, d_roundtrip)

    eleza test_kutokaisocalendar_value_errors(self):
        isocals = [
            (2019, 0, 1),
            (2019, -1, 1),
            (2019, 54, 1),
            (2019, 1, 0),
            (2019, 1, -1),
            (2019, 1, 8),
            (2019, 53, 1),
            (10000, 1, 1),
            (0, 1, 1),
            (9999999, 1, 1),
            (2<<32, 1, 1),
            (2019, 2<<32, 1),
            (2019, 1, 2<<32),
        ]

        kila isocal kwenye isocals:
            with self.subTest(isocal=isocal):
                with self.assertRaises(ValueError):
                    self.theclass.kutokaisocalendar(*isocal)

    eleza test_kutokaisocalendar_type_errors(self):
        err_txformers = [
            str,
            float,
            lambda x: Tupu,
        ]

        # Take a valid base tuple na transform it to contain one argument
        # with the wrong type. Repeat this kila each argument, e.g.
        # [("2019", 1, 1), (2019, "1", 1), (2019, 1, "1"), ...]
        isocals = []
        base = (2019, 1, 1)
        kila i kwenye range(3):
            kila txformer kwenye err_txformers:
                err_val = list(base)
                err_val[i] = txformer(err_val[i])
                isocals.append(tuple(err_val))

        kila isocal kwenye isocals:
            with self.subTest(isocal=isocal):
                with self.assertRaises(TypeError):
                    self.theclass.kutokaisocalendar(*isocal)


#############################################################################
# datetime tests

kundi SubclassDatetime(datetime):
    sub_var = 1

kundi TestDateTime(TestDate):

    thekundi = datetime

    eleza test_basic_attributes(self):
        dt = self.theclass(2002, 3, 1, 12, 0)
        self.assertEqual(dt.year, 2002)
        self.assertEqual(dt.month, 3)
        self.assertEqual(dt.day, 1)
        self.assertEqual(dt.hour, 12)
        self.assertEqual(dt.minute, 0)
        self.assertEqual(dt.second, 0)
        self.assertEqual(dt.microsecond, 0)

    eleza test_basic_attributes_nonzero(self):
        # Make sure all attributes are non-zero so bugs in
        # bit-shifting access show up.
        dt = self.theclass(2002, 3, 1, 12, 59, 59, 8000)
        self.assertEqual(dt.year, 2002)
        self.assertEqual(dt.month, 3)
        self.assertEqual(dt.day, 1)
        self.assertEqual(dt.hour, 12)
        self.assertEqual(dt.minute, 59)
        self.assertEqual(dt.second, 59)
        self.assertEqual(dt.microsecond, 8000)

    eleza test_roundtrip(self):
        kila dt kwenye (self.theclass(1, 2, 3, 4, 5, 6, 7),
                   self.theclass.now()):
            # Verify dt -> string -> datetime identity.
            s = repr(dt)
            self.assertKweli(s.startswith('datetime.'))
            s = s[9:]
            dt2 = eval(s)
            self.assertEqual(dt, dt2)

            # Verify identity via reconstructing kutoka pieces.
            dt2 = self.theclass(dt.year, dt.month, dt.day,
                                dt.hour, dt.minute, dt.second,
                                dt.microsecond)
            self.assertEqual(dt, dt2)

    eleza test_isoformat(self):
        t = self.theclass(1, 2, 3, 4, 5, 1, 123)
        self.assertEqual(t.isoformat(),    "0001-02-03T04:05:01.000123")
        self.assertEqual(t.isoformat('T'), "0001-02-03T04:05:01.000123")
        self.assertEqual(t.isoformat(' '), "0001-02-03 04:05:01.000123")
        self.assertEqual(t.isoformat('\x00'), "0001-02-03\x0004:05:01.000123")
        # bpo-34482: Check that surrogates are handled properly.
        self.assertEqual(t.isoformat('\ud800'),
                         "0001-02-03\ud80004:05:01.000123")
        self.assertEqual(t.isoformat(timespec='hours'), "0001-02-03T04")
        self.assertEqual(t.isoformat(timespec='minutes'), "0001-02-03T04:05")
        self.assertEqual(t.isoformat(timespec='seconds'), "0001-02-03T04:05:01")
        self.assertEqual(t.isoformat(timespec='milliseconds'), "0001-02-03T04:05:01.000")
        self.assertEqual(t.isoformat(timespec='microseconds'), "0001-02-03T04:05:01.000123")
        self.assertEqual(t.isoformat(timespec='auto'), "0001-02-03T04:05:01.000123")
        self.assertEqual(t.isoformat(sep=' ', timespec='minutes'), "0001-02-03 04:05")
        self.assertRaises(ValueError, t.isoformat, timespec='foo')
        # bpo-34482: Check that surrogates are handled properly.
        self.assertRaises(ValueError, t.isoformat, timespec='\ud800')
        # str ni ISO format with the separator forced to a blank.
        self.assertEqual(str(t), "0001-02-03 04:05:01.000123")

        t = self.theclass(1, 2, 3, 4, 5, 1, 999500, tzinfo=timezone.utc)
        self.assertEqual(t.isoformat(timespec='milliseconds'), "0001-02-03T04:05:01.999+00:00")

        t = self.theclass(1, 2, 3, 4, 5, 1, 999500)
        self.assertEqual(t.isoformat(timespec='milliseconds'), "0001-02-03T04:05:01.999")

        t = self.theclass(1, 2, 3, 4, 5, 1)
        self.assertEqual(t.isoformat(timespec='auto'), "0001-02-03T04:05:01")
        self.assertEqual(t.isoformat(timespec='milliseconds'), "0001-02-03T04:05:01.000")
        self.assertEqual(t.isoformat(timespec='microseconds'), "0001-02-03T04:05:01.000000")

        t = self.theclass(2, 3, 2)
        self.assertEqual(t.isoformat(),    "0002-03-02T00:00:00")
        self.assertEqual(t.isoformat('T'), "0002-03-02T00:00:00")
        self.assertEqual(t.isoformat(' '), "0002-03-02 00:00:00")
        # str ni ISO format with the separator forced to a blank.
        self.assertEqual(str(t), "0002-03-02 00:00:00")
        # ISO format with timezone
        tz = FixedOffset(timedelta(seconds=16), 'XXX')
        t = self.theclass(2, 3, 2, tzinfo=tz)
        self.assertEqual(t.isoformat(), "0002-03-02T00:00:00+00:00:16")

    eleza test_isoformat_timezone(self):
        tzoffsets = [
            ('05:00', timedelta(hours=5)),
            ('02:00', timedelta(hours=2)),
            ('06:27', timedelta(hours=6, minutes=27)),
            ('12:32:30', timedelta(hours=12, minutes=32, seconds=30)),
            ('02:04:09.123456', timedelta(hours=2, minutes=4, seconds=9, microseconds=123456))
        ]

        tzinfos = [
            ('', Tupu),
            ('+00:00', timezone.utc),
            ('+00:00', timezone(timedelta(0))),
        ]

        tzinfos += [
            (prefix + expected, timezone(sign * td))
            kila expected, td kwenye tzoffsets
            kila prefix, sign kwenye [('-', -1), ('+', 1)]
        ]

        dt_base = self.theclass(2016, 4, 1, 12, 37, 9)
        exp_base = '2016-04-01T12:37:09'

        kila exp_tz, tzi kwenye tzinfos:
            dt = dt_base.replace(tzinfo=tzi)
            exp = exp_base + exp_tz
            with self.subTest(tzi=tzi):
                assert dt.isoformat() == exp

    eleza test_format(self):
        dt = self.theclass(2007, 9, 10, 4, 5, 1, 123)
        self.assertEqual(dt.__format__(''), str(dt))

        with self.assertRaisesRegex(TypeError, 'must be str, sio int'):
            dt.__format__(123)

        # check that a derived class's __str__() gets called
        kundi A(self.theclass):
            eleza __str__(self):
                rudisha 'A'
        a = A(2007, 9, 10, 4, 5, 1, 123)
        self.assertEqual(a.__format__(''), 'A')

        # check that a derived class's strftime gets called
        kundi B(self.theclass):
            eleza strftime(self, format_spec):
                rudisha 'B'
        b = B(2007, 9, 10, 4, 5, 1, 123)
        self.assertEqual(b.__format__(''), str(dt))

        kila fmt kwenye ["m:%m d:%d y:%y",
                    "m:%m d:%d y:%y H:%H M:%M S:%S",
                    "%z %Z",
                    ]:
            self.assertEqual(dt.__format__(fmt), dt.strftime(fmt))
            self.assertEqual(a.__format__(fmt), dt.strftime(fmt))
            self.assertEqual(b.__format__(fmt), 'B')

    eleza test_more_ctime(self):
        # Test fields that TestDate doesn't touch.
        agiza time

        t = self.theclass(2002, 3, 2, 18, 3, 5, 123)
        self.assertEqual(t.ctime(), "Sat Mar  2 18:03:05 2002")
        # Oops!  The next line fails on Win2K under MSVC 6, so it's commented
        # out.  The difference ni that t.ctime() produces " 2" kila the day,
        # but platform ctime() produces "02" kila the day.  According to
        # C99, t.ctime() ni correct here.
        # self.assertEqual(t.ctime(), time.ctime(time.mktime(t.timetuple())))

        # So test a case where that difference doesn't matter.
        t = self.theclass(2002, 3, 22, 18, 3, 5, 123)
        self.assertEqual(t.ctime(), time.ctime(time.mktime(t.timetuple())))

    eleza test_tz_independent_comparing(self):
        dt1 = self.theclass(2002, 3, 1, 9, 0, 0)
        dt2 = self.theclass(2002, 3, 1, 10, 0, 0)
        dt3 = self.theclass(2002, 3, 1, 9, 0, 0)
        self.assertEqual(dt1, dt3)
        self.assertKweli(dt2 > dt3)

        # Make sure comparison doesn't forget microseconds, na isn't done
        # via comparing a float timestamp (an IEEE double doesn't have enough
        # precision to span microsecond resolution across years 1 through 9999,
        # so comparing via timestamp necessarily calls some distinct values
        # equal).
        dt1 = self.theclass(MAXYEAR, 12, 31, 23, 59, 59, 999998)
        us = timedelta(microseconds=1)
        dt2 = dt1 + us
        self.assertEqual(dt2 - dt1, us)
        self.assertKweli(dt1 < dt2)

    eleza test_strftime_with_bad_tzname_replace(self):
        # verify ok ikiwa tzinfo.tzname().replace() rudishas a non-string
        kundi MyTzInfo(FixedOffset):
            eleza tzname(self, dt):
                kundi MyStr(str):
                    eleza replace(self, *args):
                        rudisha Tupu
                rudisha MyStr('name')
        t = self.theclass(2005, 3, 2, 0, 0, 0, 0, MyTzInfo(3, 'name'))
        self.assertRaises(TypeError, t.strftime, '%Z')

    eleza test_bad_constructor_arguments(self):
        # bad years
        self.theclass(MINYEAR, 1, 1)  # no exception
        self.theclass(MAXYEAR, 1, 1)  # no exception
        self.assertRaises(ValueError, self.theclass, MINYEAR-1, 1, 1)
        self.assertRaises(ValueError, self.theclass, MAXYEAR+1, 1, 1)
        # bad months
        self.theclass(2000, 1, 1)    # no exception
        self.theclass(2000, 12, 1)   # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 0, 1)
        self.assertRaises(ValueError, self.theclass, 2000, 13, 1)
        # bad days
        self.theclass(2000, 2, 29)   # no exception
        self.theclass(2004, 2, 29)   # no exception
        self.theclass(2400, 2, 29)   # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 2, 30)
        self.assertRaises(ValueError, self.theclass, 2001, 2, 29)
        self.assertRaises(ValueError, self.theclass, 2100, 2, 29)
        self.assertRaises(ValueError, self.theclass, 1900, 2, 29)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 0)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 32)
        # bad hours
        self.theclass(2000, 1, 31, 0)    # no exception
        self.theclass(2000, 1, 31, 23)   # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, -1)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 24)
        # bad minutes
        self.theclass(2000, 1, 31, 23, 0)    # no exception
        self.theclass(2000, 1, 31, 23, 59)   # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 23, -1)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 23, 60)
        # bad seconds
        self.theclass(2000, 1, 31, 23, 59, 0)    # no exception
        self.theclass(2000, 1, 31, 23, 59, 59)   # no exception
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 23, 59, -1)
        self.assertRaises(ValueError, self.theclass, 2000, 1, 31, 23, 59, 60)
        # bad microseconds
        self.theclass(2000, 1, 31, 23, 59, 59, 0)    # no exception
        self.theclass(2000, 1, 31, 23, 59, 59, 999999)   # no exception
        self.assertRaises(ValueError, self.theclass,
                          2000, 1, 31, 23, 59, 59, -1)
        self.assertRaises(ValueError, self.theclass,
                          2000, 1, 31, 23, 59, 59,
                          1000000)
        # bad fold
        self.assertRaises(ValueError, self.theclass,
                          2000, 1, 31, fold=-1)
        self.assertRaises(ValueError, self.theclass,
                          2000, 1, 31, fold=2)
        # Positional fold:
        self.assertRaises(TypeError, self.theclass,
                          2000, 1, 31, 23, 59, 59, 0, Tupu, 1)

    eleza test_hash_equality(self):
        d = self.theclass(2000, 12, 31, 23, 30, 17)
        e = self.theclass(2000, 12, 31, 23, 30, 17)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

        d = self.theclass(2001,  1,  1,  0,  5, 17)
        e = self.theclass(2001,  1,  1,  0,  5, 17)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

    eleza test_computations(self):
        a = self.theclass(2002, 1, 31)
        b = self.theclass(1956, 1, 31)
        diff = a-b
        self.assertEqual(diff.days, 46*365 + len(range(1956, 2002, 4)))
        self.assertEqual(diff.seconds, 0)
        self.assertEqual(diff.microseconds, 0)
        a = self.theclass(2002, 3, 2, 17, 6)
        millisec = timedelta(0, 0, 1000)
        hour = timedelta(0, 3600)
        day = timedelta(1)
        week = timedelta(7)
        self.assertEqual(a + hour, self.theclass(2002, 3, 2, 18, 6))
        self.assertEqual(hour + a, self.theclass(2002, 3, 2, 18, 6))
        self.assertEqual(a + 10*hour, self.theclass(2002, 3, 3, 3, 6))
        self.assertEqual(a - hour, self.theclass(2002, 3, 2, 16, 6))
        self.assertEqual(-hour + a, self.theclass(2002, 3, 2, 16, 6))
        self.assertEqual(a - hour, a + -hour)
        self.assertEqual(a - 20*hour, self.theclass(2002, 3, 1, 21, 6))
        self.assertEqual(a + day, self.theclass(2002, 3, 3, 17, 6))
        self.assertEqual(a - day, self.theclass(2002, 3, 1, 17, 6))
        self.assertEqual(a + week, self.theclass(2002, 3, 9, 17, 6))
        self.assertEqual(a - week, self.theclass(2002, 2, 23, 17, 6))
        self.assertEqual(a + 52*week, self.theclass(2003, 3, 1, 17, 6))
        self.assertEqual(a - 52*week, self.theclass(2001, 3, 3, 17, 6))
        self.assertEqual((a + week) - a, week)
        self.assertEqual((a + day) - a, day)
        self.assertEqual((a + hour) - a, hour)
        self.assertEqual((a + millisec) - a, millisec)
        self.assertEqual((a - week) - a, -week)
        self.assertEqual((a - day) - a, -day)
        self.assertEqual((a - hour) - a, -hour)
        self.assertEqual((a - millisec) - a, -millisec)
        self.assertEqual(a - (a + week), -week)
        self.assertEqual(a - (a + day), -day)
        self.assertEqual(a - (a + hour), -hour)
        self.assertEqual(a - (a + millisec), -millisec)
        self.assertEqual(a - (a - week), week)
        self.assertEqual(a - (a - day), day)
        self.assertEqual(a - (a - hour), hour)
        self.assertEqual(a - (a - millisec), millisec)
        self.assertEqual(a + (week + day + hour + millisec),
                         self.theclass(2002, 3, 10, 18, 6, 0, 1000))
        self.assertEqual(a + (week + day + hour + millisec),
                         (((a + week) + day) + hour) + millisec)
        self.assertEqual(a - (week + day + hour + millisec),
                         self.theclass(2002, 2, 22, 16, 5, 59, 999000))
        self.assertEqual(a - (week + day + hour + millisec),
                         (((a - week) - day) - hour) - millisec)
        # Add/sub ints ama floats should be illegal
        kila i kwenye 1, 1.0:
            self.assertRaises(TypeError, lambda: a+i)
            self.assertRaises(TypeError, lambda: a-i)
            self.assertRaises(TypeError, lambda: i+a)
            self.assertRaises(TypeError, lambda: i-a)

        # delta - datetime ni senseless.
        self.assertRaises(TypeError, lambda: day - a)
        # mixing datetime na (delta ama datetime) via * ama // ni senseless
        self.assertRaises(TypeError, lambda: day * a)
        self.assertRaises(TypeError, lambda: a * day)
        self.assertRaises(TypeError, lambda: day // a)
        self.assertRaises(TypeError, lambda: a // day)
        self.assertRaises(TypeError, lambda: a * a)
        self.assertRaises(TypeError, lambda: a // a)
        # datetime + datetime ni senseless
        self.assertRaises(TypeError, lambda: a + a)

    eleza test_pickling(self):
        args = 6, 7, 23, 20, 59, 1, 64**2
        orig = self.theclass(*args)
        kila pickler, unpickler, proto kwenye pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)
        self.assertEqual(orig.__reduce__(), orig.__reduce_ex__(2))

    eleza test_more_pickling(self):
        a = self.theclass(2003, 2, 7, 16, 48, 37, 444116)
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            s = pickle.dumps(a, proto)
            b = pickle.loads(s)
            self.assertEqual(b.year, 2003)
            self.assertEqual(b.month, 2)
            self.assertEqual(b.day, 7)

    eleza test_pickling_subclass_datetime(self):
        args = 6, 7, 23, 20, 59, 1, 64**2
        orig = SubclassDatetime(*args)
        kila pickler, unpickler, proto kwenye pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)

    eleza test_compat_unpickle(self):
        tests = [
            b'cdatetime\ndatetime\n('
            b"S'\\x07\\xdf\\x0b\\x1b\\x14;\\x01\\x00\\x10\\x00'\ntR.",

            b'cdatetime\ndatetime\n('
            b'U\n\x07\xdf\x0b\x1b\x14;\x01\x00\x10\x00tR.',

            b'\x80\x02cdatetime\ndatetime\n'
            b'U\n\x07\xdf\x0b\x1b\x14;\x01\x00\x10\x00\x85R.',
        ]
        args = 2015, 11, 27, 20, 59, 1, 64**2
        expected = self.theclass(*args)
        kila data kwenye tests:
            kila loads kwenye pickle_loads:
                derived = loads(data, encoding='latin1')
                self.assertEqual(derived, expected)

    eleza test_more_compare(self):
        # The test_compare() inherited kutoka TestDate covers the error cases.
        # We just want to test lexicographic ordering on the members datetime
        # has that date lacks.
        args = [2000, 11, 29, 20, 58, 16, 999998]
        t1 = self.theclass(*args)
        t2 = self.theclass(*args)
        self.assertEqual(t1, t2)
        self.assertKweli(t1 <= t2)
        self.assertKweli(t1 >= t2)
        self.assertUongo(t1 != t2)
        self.assertUongo(t1 < t2)
        self.assertUongo(t1 > t2)

        kila i kwenye range(len(args)):
            newargs = args[:]
            newargs[i] = args[i] + 1
            t2 = self.theclass(*newargs)   # this ni larger than t1
            self.assertKweli(t1 < t2)
            self.assertKweli(t2 > t1)
            self.assertKweli(t1 <= t2)
            self.assertKweli(t2 >= t1)
            self.assertKweli(t1 != t2)
            self.assertKweli(t2 != t1)
            self.assertUongo(t1 == t2)
            self.assertUongo(t2 == t1)
            self.assertUongo(t1 > t2)
            self.assertUongo(t2 < t1)
            self.assertUongo(t1 >= t2)
            self.assertUongo(t2 <= t1)


    # A helper kila timestamp constructor tests.
    eleza verify_field_equality(self, expected, got):
        self.assertEqual(expected.tm_year, got.year)
        self.assertEqual(expected.tm_mon, got.month)
        self.assertEqual(expected.tm_mday, got.day)
        self.assertEqual(expected.tm_hour, got.hour)
        self.assertEqual(expected.tm_min, got.minute)
        self.assertEqual(expected.tm_sec, got.second)

    eleza test_kutokatimestamp(self):
        agiza time

        ts = time.time()
        expected = time.localtime(ts)
        got = self.theclass.kutokatimestamp(ts)
        self.verify_field_equality(expected, got)

    eleza test_utckutokatimestamp(self):
        agiza time

        ts = time.time()
        expected = time.gmtime(ts)
        got = self.theclass.utckutokatimestamp(ts)
        self.verify_field_equality(expected, got)

    # Run with US-style DST rules: DST begins 2 a.m. on second Sunday in
    # March (M3.2.0) na ends 2 a.m. on first Sunday kwenye November (M11.1.0).
    @support.run_with_tz('EST+05EDT,M3.2.0,M11.1.0')
    eleza test_timestamp_naive(self):
        t = self.theclass(1970, 1, 1)
        self.assertEqual(t.timestamp(), 18000.0)
        t = self.theclass(1970, 1, 1, 1, 2, 3, 4)
        self.assertEqual(t.timestamp(),
                         18000.0 + 3600 + 2*60 + 3 + 4*1e-6)
        # Missing hour
        t0 = self.theclass(2012, 3, 11, 2, 30)
        t1 = t0.replace(fold=1)
        self.assertEqual(self.theclass.kutokatimestamp(t1.timestamp()),
                         t0 - timedelta(hours=1))
        self.assertEqual(self.theclass.kutokatimestamp(t0.timestamp()),
                         t1 + timedelta(hours=1))
        # Ambiguous hour defaults to DST
        t = self.theclass(2012, 11, 4, 1, 30)
        self.assertEqual(self.theclass.kutokatimestamp(t.timestamp()), t)

        # Timestamp may ashiria an overflow error on some platforms
        # XXX: Do we care to support the first na last year?
        kila t kwenye [self.theclass(2,1,1), self.theclass(9998,12,12)]:
            jaribu:
                s = t.timestamp()
            tatizo OverflowError:
                pita
            isipokua:
                self.assertEqual(self.theclass.kutokatimestamp(s), t)

    eleza test_timestamp_aware(self):
        t = self.theclass(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(t.timestamp(), 0.0)
        t = self.theclass(1970, 1, 1, 1, 2, 3, 4, tzinfo=timezone.utc)
        self.assertEqual(t.timestamp(),
                         3600 + 2*60 + 3 + 4*1e-6)
        t = self.theclass(1970, 1, 1, 1, 2, 3, 4,
                          tzinfo=timezone(timedelta(hours=-5), 'EST'))
        self.assertEqual(t.timestamp(),
                         18000 + 3600 + 2*60 + 3 + 4*1e-6)

    @support.run_with_tz('MSK-03')  # Something east of Greenwich
    eleza test_microsecond_rounding(self):
        kila fts kwenye [self.theclass.kutokatimestamp,
                    self.theclass.utckutokatimestamp]:
            zero = fts(0)
            self.assertEqual(zero.second, 0)
            self.assertEqual(zero.microsecond, 0)
            one = fts(1e-6)
            jaribu:
                minus_one = fts(-1e-6)
            tatizo OSError:
                # localtime(-1) na gmtime(-1) ni sio supported on Windows
                pita
            isipokua:
                self.assertEqual(minus_one.second, 59)
                self.assertEqual(minus_one.microsecond, 999999)

                t = fts(-1e-8)
                self.assertEqual(t, zero)
                t = fts(-9e-7)
                self.assertEqual(t, minus_one)
                t = fts(-1e-7)
                self.assertEqual(t, zero)
                t = fts(-1/2**7)
                self.assertEqual(t.second, 59)
                self.assertEqual(t.microsecond, 992188)

            t = fts(1e-7)
            self.assertEqual(t, zero)
            t = fts(9e-7)
            self.assertEqual(t, one)
            t = fts(0.99999949)
            self.assertEqual(t.second, 0)
            self.assertEqual(t.microsecond, 999999)
            t = fts(0.9999999)
            self.assertEqual(t.second, 1)
            self.assertEqual(t.microsecond, 0)
            t = fts(1/2**7)
            self.assertEqual(t.second, 0)
            self.assertEqual(t.microsecond, 7812)

    eleza test_timestamp_limits(self):
        # minimum timestamp
        min_dt = self.theclass.min.replace(tzinfo=timezone.utc)
        min_ts = min_dt.timestamp()
        jaribu:
            # date 0001-01-01 00:00:00+00:00: timestamp=-62135596800
            self.assertEqual(self.theclass.kutokatimestamp(min_ts, tz=timezone.utc),
                             min_dt)
        tatizo (OverflowError, OSError) kama exc:
            # the date 0001-01-01 doesn't fit into 32-bit time_t,
            # ama platform doesn't support such very old date
            self.skipTest(str(exc))

        # maximum timestamp: set seconds to zero to avoid rounding issues
        max_dt = self.theclass.max.replace(tzinfo=timezone.utc,
                                           second=0, microsecond=0)
        max_ts = max_dt.timestamp()
        # date 9999-12-31 23:59:00+00:00: timestamp 253402300740
        self.assertEqual(self.theclass.kutokatimestamp(max_ts, tz=timezone.utc),
                         max_dt)

        # number of seconds greater than 1 year: make sure that the new date
        # ni sio valid kwenye datetime.datetime limits
        delta = 3600 * 24 * 400

        # too small
        ts = min_ts - delta
        # converting a Python int to C time_t can ashiria a OverflowError,
        # especially on 32-bit platforms.
        with self.assertRaises((ValueError, OverflowError)):
            self.theclass.kutokatimestamp(ts)
        with self.assertRaises((ValueError, OverflowError)):
            self.theclass.utckutokatimestamp(ts)

        # too big
        ts = max_dt.timestamp() + delta
        with self.assertRaises((ValueError, OverflowError)):
            self.theclass.kutokatimestamp(ts)
        with self.assertRaises((ValueError, OverflowError)):
            self.theclass.utckutokatimestamp(ts)

    eleza test_insane_kutokatimestamp(self):
        # It's possible that some platform maps time_t to double,
        # na that this test will fail there.  This test should
        # exempt such platforms (provided they rudisha reasonable
        # results!).
        kila insane kwenye -1e200, 1e200:
            self.assertRaises(OverflowError, self.theclass.kutokatimestamp,
                              insane)

    eleza test_insane_utckutokatimestamp(self):
        # It's possible that some platform maps time_t to double,
        # na that this test will fail there.  This test should
        # exempt such platforms (provided they rudisha reasonable
        # results!).
        kila insane kwenye -1e200, 1e200:
            self.assertRaises(OverflowError, self.theclass.utckutokatimestamp,
                              insane)

    @unittest.skipIf(sys.platform == "win32", "Windows doesn't accept negative timestamps")
    eleza test_negative_float_kutokatimestamp(self):
        # The result ni tz-dependent; at least test that this doesn't
        # fail (like it did before bug 1646728 was fixed).
        self.theclass.kutokatimestamp(-1.05)

    @unittest.skipIf(sys.platform == "win32", "Windows doesn't accept negative timestamps")
    eleza test_negative_float_utckutokatimestamp(self):
        d = self.theclass.utckutokatimestamp(-1.05)
        self.assertEqual(d, self.theclass(1969, 12, 31, 23, 59, 58, 950000))

    eleza test_utcnow(self):
        agiza time

        # Call it a success ikiwa utcnow() na utckutokatimestamp() are within
        # a second of each other.
        tolerance = timedelta(seconds=1)
        kila dummy kwenye range(3):
            kutoka_now = self.theclass.utcnow()
            kutoka_timestamp = self.theclass.utckutokatimestamp(time.time())
            ikiwa abs(kutoka_timestamp - kutoka_now) <= tolerance:
                koma
            # Else try again a few times.
        self.assertLessEqual(abs(kutoka_timestamp - kutoka_now), tolerance)

    eleza test_strptime(self):
        string = '2004-12-01 13:02:47.197'
        format = '%Y-%m-%d %H:%M:%S.%f'
        expected = _strptime._strptime_datetime(self.theclass, string, format)
        got = self.theclass.strptime(string, format)
        self.assertEqual(expected, got)
        self.assertIs(type(expected), self.theclass)
        self.assertIs(type(got), self.theclass)

        # bpo-34482: Check that surrogates are handled properly.
        inputs = [
            ('2004-12-01\ud80013:02:47.197', '%Y-%m-%d\ud800%H:%M:%S.%f'),
            ('2004\ud80012-01 13:02:47.197', '%Y\ud800%m-%d %H:%M:%S.%f'),
            ('2004-12-01 13:02\ud80047.197', '%Y-%m-%d %H:%M\ud800%S.%f'),
        ]
        kila string, format kwenye inputs:
            with self.subTest(string=string, format=format):
                expected = _strptime._strptime_datetime(self.theclass, string,
                                                        format)
                got = self.theclass.strptime(string, format)
                self.assertEqual(expected, got)

        strptime = self.theclass.strptime

        self.assertEqual(strptime("+0002", "%z").utcoffset(), 2 * MINUTE)
        self.assertEqual(strptime("-0002", "%z").utcoffset(), -2 * MINUTE)
        self.assertEqual(
            strptime("-00:02:01.000003", "%z").utcoffset(),
            -timedelta(minutes=2, seconds=1, microseconds=3)
        )
        # Only local timezone na UTC are supported
        kila tzseconds, tzname kwenye ((0, 'UTC'), (0, 'GMT'),
                                 (-_time.timezone, _time.tzname[0])):
            ikiwa tzseconds < 0:
                sign = '-'
                seconds = -tzseconds
            isipokua:
                sign ='+'
                seconds = tzseconds
            hours, minutes = divmod(seconds//60, 60)
            dtstr = "{}{:02d}{:02d} {}".format(sign, hours, minutes, tzname)
            dt = strptime(dtstr, "%z %Z")
            self.assertEqual(dt.utcoffset(), timedelta(seconds=tzseconds))
            self.assertEqual(dt.tzname(), tzname)
        # Can produce inconsistent datetime
        dtstr, fmt = "+1234 UTC", "%z %Z"
        dt = strptime(dtstr, fmt)
        self.assertEqual(dt.utcoffset(), 12 * HOUR + 34 * MINUTE)
        self.assertEqual(dt.tzname(), 'UTC')
        # yet will roundtrip
        self.assertEqual(dt.strftime(fmt), dtstr)

        # Produce naive datetime ikiwa no %z ni provided
        self.assertEqual(strptime("UTC", "%Z").tzinfo, Tupu)

        with self.assertRaises(ValueError): strptime("-2400", "%z")
        with self.assertRaises(ValueError): strptime("-000", "%z")

    eleza test_strptime_single_digit(self):
        # bpo-34903: Check that single digit dates na times are allowed.

        strptime = self.theclass.strptime

        with self.assertRaises(ValueError):
            # %y does require two digits.
            newdate = strptime('01/02/3 04:05:06', '%d/%m/%y %H:%M:%S')
        dt1 = self.theclass(2003, 2, 1, 4, 5, 6)
        dt2 = self.theclass(2003, 1, 2, 4, 5, 6)
        dt3 = self.theclass(2003, 2, 1, 0, 0, 0)
        dt4 = self.theclass(2003, 1, 25, 0, 0, 0)
        inputs = [
            ('%d', '1/02/03 4:5:6', '%d/%m/%y %H:%M:%S', dt1),
            ('%m', '01/2/03 4:5:6', '%d/%m/%y %H:%M:%S', dt1),
            ('%H', '01/02/03 4:05:06', '%d/%m/%y %H:%M:%S', dt1),
            ('%M', '01/02/03 04:5:06', '%d/%m/%y %H:%M:%S', dt1),
            ('%S', '01/02/03 04:05:6', '%d/%m/%y %H:%M:%S', dt1),
            ('%j', '2/03 04am:05:06', '%j/%y %I%p:%M:%S',dt2),
            ('%I', '02/03 4am:05:06', '%j/%y %I%p:%M:%S',dt2),
            ('%w', '6/04/03', '%w/%U/%y', dt3),
            # %u requires a single digit.
            ('%W', '6/4/2003', '%u/%W/%Y', dt3),
            ('%V', '6/4/2003', '%u/%V/%G', dt4),
        ]
        kila reason, string, format, target kwenye inputs:
            reason = 'test single digit ' + reason
            with self.subTest(reason=reason,
                              string=string,
                              format=format,
                              target=target):
                newdate = strptime(string, format)
                self.assertEqual(newdate, target, msg=reason)

    eleza test_more_timetuple(self):
        # This tests fields beyond those tested by the TestDate.test_timetuple.
        t = self.theclass(2004, 12, 31, 6, 22, 33)
        self.assertEqual(t.timetuple(), (2004, 12, 31, 6, 22, 33, 4, 366, -1))
        self.assertEqual(t.timetuple(),
                         (t.year, t.month, t.day,
                          t.hour, t.minute, t.second,
                          t.weekday(),
                          t.toordinal() - date(t.year, 1, 1).toordinal() + 1,
                          -1))
        tt = t.timetuple()
        self.assertEqual(tt.tm_year, t.year)
        self.assertEqual(tt.tm_mon, t.month)
        self.assertEqual(tt.tm_mday, t.day)
        self.assertEqual(tt.tm_hour, t.hour)
        self.assertEqual(tt.tm_min, t.minute)
        self.assertEqual(tt.tm_sec, t.second)
        self.assertEqual(tt.tm_wday, t.weekday())
        self.assertEqual(tt.tm_yday, t.toordinal() -
                                     date(t.year, 1, 1).toordinal() + 1)
        self.assertEqual(tt.tm_isdst, -1)

    eleza test_more_strftime(self):
        # This tests fields beyond those tested by the TestDate.test_strftime.
        t = self.theclass(2004, 12, 31, 6, 22, 33, 47)
        self.assertEqual(t.strftime("%m %d %y %f %S %M %H %j"),
                                    "12 31 04 000047 33 22 06 366")
        kila (s, us), z kwenye [((33, 123), "33.000123"), ((33, 0), "33"),]:
            tz = timezone(-timedelta(hours=2, seconds=s, microseconds=us))
            t = t.replace(tzinfo=tz)
            self.assertEqual(t.strftime("%z"), "-0200" + z)

        # bpo-34482: Check that surrogates don't cause a crash.
        jaribu:
            t.strftime('%y\ud800%m %H\ud800%M')
        tatizo UnicodeEncodeError:
            pita

    eleza test_extract(self):
        dt = self.theclass(2002, 3, 4, 18, 45, 3, 1234)
        self.assertEqual(dt.date(), date(2002, 3, 4))
        self.assertEqual(dt.time(), time(18, 45, 3, 1234))

    eleza test_combine(self):
        d = date(2002, 3, 4)
        t = time(18, 45, 3, 1234)
        expected = self.theclass(2002, 3, 4, 18, 45, 3, 1234)
        combine = self.theclass.combine
        dt = combine(d, t)
        self.assertEqual(dt, expected)

        dt = combine(time=t, date=d)
        self.assertEqual(dt, expected)

        self.assertEqual(d, dt.date())
        self.assertEqual(t, dt.time())
        self.assertEqual(dt, combine(dt.date(), dt.time()))

        self.assertRaises(TypeError, combine) # need an arg
        self.assertRaises(TypeError, combine, d) # need two args
        self.assertRaises(TypeError, combine, t, d) # args reversed
        self.assertRaises(TypeError, combine, d, t, 1) # wrong tzinfo type
        self.assertRaises(TypeError, combine, d, t, 1, 2)  # too many args
        self.assertRaises(TypeError, combine, "date", "time") # wrong types
        self.assertRaises(TypeError, combine, d, "time") # wrong type
        self.assertRaises(TypeError, combine, "date", t) # wrong type

        # tzinfo= argument
        dt = combine(d, t, timezone.utc)
        self.assertIs(dt.tzinfo, timezone.utc)
        dt = combine(d, t, tzinfo=timezone.utc)
        self.assertIs(dt.tzinfo, timezone.utc)
        t = time()
        dt = combine(dt, t)
        self.assertEqual(dt.date(), d)
        self.assertEqual(dt.time(), t)

    eleza test_replace(self):
        cls = self.theclass
        args = [1, 2, 3, 4, 5, 6, 7]
        base = cls(*args)
        self.assertEqual(base, base.replace())

        i = 0
        kila name, newval kwenye (("year", 2),
                             ("month", 3),
                             ("day", 4),
                             ("hour", 5),
                             ("minute", 6),
                             ("second", 7),
                             ("microsecond", 8)):
            newargs = args[:]
            newargs[i] = newval
            expected = cls(*newargs)
            got = base.replace(**{name: newval})
            self.assertEqual(expected, got)
            i += 1

        # Out of bounds.
        base = cls(2000, 2, 29)
        self.assertRaises(ValueError, base.replace, year=2001)

    @support.run_with_tz('EDT4')
    eleza test_astimezone(self):
        dt = self.theclass.now()
        f = FixedOffset(44, "0044")
        dt_utc = dt.replace(tzinfo=timezone(timedelta(hours=-4), 'EDT'))
        self.assertEqual(dt.astimezone(), dt_utc) # naive
        self.assertRaises(TypeError, dt.astimezone, f, f) # too many args
        self.assertRaises(TypeError, dt.astimezone, dt) # arg wrong type
        dt_f = dt.replace(tzinfo=f) + timedelta(hours=4, minutes=44)
        self.assertEqual(dt.astimezone(f), dt_f) # naive
        self.assertEqual(dt.astimezone(tz=f), dt_f) # naive

        kundi Bogus(tzinfo):
            eleza utcoffset(self, dt): rudisha Tupu
            eleza dst(self, dt): rudisha timedelta(0)
        bog = Bogus()
        self.assertRaises(ValueError, dt.astimezone, bog)   # naive
        self.assertEqual(dt.replace(tzinfo=bog).astimezone(f), dt_f)

        kundi AlsoBogus(tzinfo):
            eleza utcoffset(self, dt): rudisha timedelta(0)
            eleza dst(self, dt): rudisha Tupu
        alsobog = AlsoBogus()
        self.assertRaises(ValueError, dt.astimezone, alsobog) # also naive

        kundi Broken(tzinfo):
            eleza utcoffset(self, dt): rudisha 1
            eleza dst(self, dt): rudisha 1
        broken = Broken()
        dt_broken = dt.replace(tzinfo=broken)
        with self.assertRaises(TypeError):
            dt_broken.astimezone()

    eleza test_subclass_datetime(self):

        kundi C(self.theclass):
            theAnswer = 42

            eleza __new__(cls, *args, **kws):
                temp = kws.copy()
                extra = temp.pop('extra')
                result = self.theclass.__new__(cls, *args, **temp)
                result.extra = extra
                rudisha result

            eleza newmeth(self, start):
                rudisha start + self.year + self.month + self.second

        args = 2003, 4, 14, 12, 13, 41

        dt1 = self.theclass(*args)
        dt2 = C(*args, **{'extra': 7})

        self.assertEqual(dt2.__class__, C)
        self.assertEqual(dt2.theAnswer, 42)
        self.assertEqual(dt2.extra, 7)
        self.assertEqual(dt1.toordinal(), dt2.toordinal())
        self.assertEqual(dt2.newmeth(-7), dt1.year + dt1.month +
                                          dt1.second - 7)

    eleza test_subclass_alternate_constructors_datetime(self):
        # Test that alternate constructors call the constructor
        kundi DateTimeSubclass(self.theclass):
            eleza __new__(cls, *args, **kwargs):
                result = self.theclass.__new__(cls, *args, **kwargs)
                result.extra = 7

                rudisha result

        args = (2003, 4, 14, 12, 30, 15, 123456)
        d_isoformat = '2003-04-14T12:30:15.123456'      # Equivalent isoformat()
        utc_ts = 1050323415.123456                      # UTC timestamp

        base_d = DateTimeSubclass(*args)
        self.assertIsInstance(base_d, DateTimeSubclass)
        self.assertEqual(base_d.extra, 7)

        # Timestamp depends on time zone, so we'll calculate the equivalent here
        ts = base_d.timestamp()

        test_cases = [
            ('kutokatimestamp', (ts,), base_d),
            # See https://bugs.python.org/issue32417
            ('kutokatimestamp', (ts, timezone.utc),
                               base_d.astimezone(timezone.utc)),
            ('utckutokatimestamp', (utc_ts,), base_d),
            ('kutokaisoformat', (d_isoformat,), base_d),
            ('strptime', (d_isoformat, '%Y-%m-%dT%H:%M:%S.%f'), base_d),
            ('combine', (date(*args[0:3]), time(*args[3:])), base_d),
        ]

        kila constr_name, constr_args, expected kwenye test_cases:
            kila base_obj kwenye (DateTimeSubclass, base_d):
                # Test both the classmethod na method
                with self.subTest(base_obj_type=type(base_obj),
                                  constr_name=constr_name):
                    constructor = getattr(base_obj, constr_name)

                    dt = constructor(*constr_args)

                    # Test that it creates the right subclass
                    self.assertIsInstance(dt, DateTimeSubclass)

                    # Test that it's equal to the base object
                    self.assertEqual(dt, expected)

                    # Test that it called the constructor
                    self.assertEqual(dt.extra, 7)

    eleza test_subclass_now(self):
        # Test that alternate constructors call the constructor
        kundi DateTimeSubclass(self.theclass):
            eleza __new__(cls, *args, **kwargs):
                result = self.theclass.__new__(cls, *args, **kwargs)
                result.extra = 7

                rudisha result

        test_cases = [
            ('now', 'now', {}),
            ('utcnow', 'utcnow', {}),
            ('now_utc', 'now', {'tz': timezone.utc}),
            ('now_fixed', 'now', {'tz': timezone(timedelta(hours=-5), "EST")}),
        ]

        kila name, meth_name, kwargs kwenye test_cases:
            with self.subTest(name):
                constr = getattr(DateTimeSubclass, meth_name)
                dt = constr(**kwargs)

                self.assertIsInstance(dt, DateTimeSubclass)
                self.assertEqual(dt.extra, 7)

    eleza test_kutokaisoformat_datetime(self):
        # Test that isoformat() ni reversible
        base_dates = [
            (1, 1, 1),
            (1900, 1, 1),
            (2004, 11, 12),
            (2017, 5, 30)
        ]

        base_times = [
            (0, 0, 0, 0),
            (0, 0, 0, 241000),
            (0, 0, 0, 234567),
            (12, 30, 45, 234567)
        ]

        separators = [' ', 'T']

        tzinfos = [Tupu, timezone.utc,
                   timezone(timedelta(hours=-5)),
                   timezone(timedelta(hours=2))]

        dts = [self.theclass(*date_tuple, *time_tuple, tzinfo=tzi)
               kila date_tuple kwenye base_dates
               kila time_tuple kwenye base_times
               kila tzi kwenye tzinfos]

        kila dt kwenye dts:
            kila sep kwenye separators:
                dtstr = dt.isoformat(sep=sep)

                with self.subTest(dtstr=dtstr):
                    dt_rt = self.theclass.kutokaisoformat(dtstr)
                    self.assertEqual(dt, dt_rt)

    eleza test_kutokaisoformat_timezone(self):
        base_dt = self.theclass(2014, 12, 30, 12, 30, 45, 217456)

        tzoffsets = [
            timedelta(hours=5), timedelta(hours=2),
            timedelta(hours=6, minutes=27),
            timedelta(hours=12, minutes=32, seconds=30),
            timedelta(hours=2, minutes=4, seconds=9, microseconds=123456)
        ]

        tzoffsets += [-1 * td kila td kwenye tzoffsets]

        tzinfos = [Tupu, timezone.utc,
                   timezone(timedelta(hours=0))]

        tzinfos += [timezone(td) kila td kwenye tzoffsets]

        kila tzi kwenye tzinfos:
            dt = base_dt.replace(tzinfo=tzi)
            dtstr = dt.isoformat()

            with self.subTest(tstr=dtstr):
                dt_rt = self.theclass.kutokaisoformat(dtstr)
                assert dt == dt_rt, dt_rt

    eleza test_kutokaisoformat_separators(self):
        separators = [
            ' ', 'T', '\u007f',     # 1-bit widths
            '\u0080', 'ʁ',          # 2-bit widths
            'ᛇ', '時',               # 3-bit widths
            '🐍',                    # 4-bit widths
            '\ud800',               # bpo-34454: Surrogate code point
        ]

        kila sep kwenye separators:
            dt = self.theclass(2018, 1, 31, 23, 59, 47, 124789)
            dtstr = dt.isoformat(sep=sep)

            with self.subTest(dtstr=dtstr):
                dt_rt = self.theclass.kutokaisoformat(dtstr)
                self.assertEqual(dt, dt_rt)

    eleza test_kutokaisoformat_ambiguous(self):
        # Test strings like 2018-01-31+12:15 (where +12:15 ni sio a time zone)
        separators = ['+', '-']
        kila sep kwenye separators:
            dt = self.theclass(2018, 1, 31, 12, 15)
            dtstr = dt.isoformat(sep=sep)

            with self.subTest(dtstr=dtstr):
                dt_rt = self.theclass.kutokaisoformat(dtstr)
                self.assertEqual(dt, dt_rt)

    eleza test_kutokaisoformat_timespecs(self):
        datetime_bases = [
            (2009, 12, 4, 8, 17, 45, 123456),
            (2009, 12, 4, 8, 17, 45, 0)]

        tzinfos = [Tupu, timezone.utc,
                   timezone(timedelta(hours=-5)),
                   timezone(timedelta(hours=2)),
                   timezone(timedelta(hours=6, minutes=27))]

        timespecs = ['hours', 'minutes', 'seconds',
                     'milliseconds', 'microseconds']

        kila ip, ts kwenye enumerate(timespecs):
            kila tzi kwenye tzinfos:
                kila dt_tuple kwenye datetime_bases:
                    ikiwa ts == 'milliseconds':
                        new_microseconds = 1000 * (dt_tuple[6] // 1000)
                        dt_tuple = dt_tuple[0:6] + (new_microseconds,)

                    dt = self.theclass(*(dt_tuple[0:(4 + ip)]), tzinfo=tzi)
                    dtstr = dt.isoformat(timespec=ts)
                    with self.subTest(dtstr=dtstr):
                        dt_rt = self.theclass.kutokaisoformat(dtstr)
                        self.assertEqual(dt, dt_rt)

    eleza test_kutokaisoformat_fails_datetime(self):
        # Test that kutokaisoformat() fails on invalid values
        bad_strs = [
            '',                             # Empty string
            '\ud800',                       # bpo-34454: Surrogate code point
            '2009.04-19T03',                # Wrong first separator
            '2009-04.19T03',                # Wrong second separator
            '2009-04-19T0a',                # Invalid hours
            '2009-04-19T03:1a:45',          # Invalid minutes
            '2009-04-19T03:15:4a',          # Invalid seconds
            '2009-04-19T03;15:45',          # Bad first time separator
            '2009-04-19T03:15;45',          # Bad second time separator
            '2009-04-19T03:15:4500:00',     # Bad time zone separator
            '2009-04-19T03:15:45.2345',     # Too many digits kila milliseconds
            '2009-04-19T03:15:45.1234567',  # Too many digits kila microseconds
            '2009-04-19T03:15:45.123456+24:30',    # Invalid time zone offset
            '2009-04-19T03:15:45.123456-24:30',    # Invalid negative offset
            '2009-04-10ᛇᛇᛇᛇᛇ12:15',         # Too many unicode separators
            '2009-04\ud80010T12:15',        # Surrogate char kwenye date
            '2009-04-10T12\ud80015',        # Surrogate char kwenye time
            '2009-04-19T1',                 # Incomplete hours
            '2009-04-19T12:3',              # Incomplete minutes
            '2009-04-19T12:30:4',           # Incomplete seconds
            '2009-04-19T12:',               # Ends with time separator
            '2009-04-19T12:30:',            # Ends with time separator
            '2009-04-19T12:30:45.',         # Ends with time separator
            '2009-04-19T12:30:45.123456+',  # Ends with timzone separator
            '2009-04-19T12:30:45.123456-',  # Ends with timzone separator
            '2009-04-19T12:30:45.123456-05:00a',    # Extra text
            '2009-04-19T12:30:45.123-05:00a',       # Extra text
            '2009-04-19T12:30:45-05:00a',           # Extra text
        ]

        kila bad_str kwenye bad_strs:
            with self.subTest(bad_str=bad_str):
                with self.assertRaises(ValueError):
                    self.theclass.kutokaisoformat(bad_str)

    eleza test_kutokaisoformat_fails_surrogate(self):
        # Test that when kutokaisoformat() fails with a surrogate character as
        # the separator, the error message contains the original string
        dtstr = "2018-01-03\ud80001:0113"

        with self.assertRaisesRegex(ValueError, re.escape(repr(dtstr))):
            self.theclass.kutokaisoformat(dtstr)

    eleza test_kutokaisoformat_utc(self):
        dt_str = '2014-04-19T13:21:13+00:00'
        dt = self.theclass.kutokaisoformat(dt_str)

        self.assertIs(dt.tzinfo, timezone.utc)

    eleza test_kutokaisoformat_subclass(self):
        kundi DateTimeSubclass(self.theclass):
            pita

        dt = DateTimeSubclass(2014, 12, 14, 9, 30, 45, 457390,
                              tzinfo=timezone(timedelta(hours=10, minutes=45)))

        dt_rt = DateTimeSubclass.kutokaisoformat(dt.isoformat())

        self.assertEqual(dt, dt_rt)
        self.assertIsInstance(dt_rt, DateTimeSubclass)


kundi TestSubclassDateTime(TestDateTime):
    thekundi = SubclassDatetime
    # Override tests sio designed kila subclass
    @unittest.skip('not appropriate kila subclasses')
    eleza test_roundtrip(self):
        pita

kundi SubclassTime(time):
    sub_var = 1

kundi TestTime(HarmlessMixedComparison, unittest.TestCase):

    thekundi = time

    eleza test_basic_attributes(self):
        t = self.theclass(12, 0)
        self.assertEqual(t.hour, 12)
        self.assertEqual(t.minute, 0)
        self.assertEqual(t.second, 0)
        self.assertEqual(t.microsecond, 0)

    eleza test_basic_attributes_nonzero(self):
        # Make sure all attributes are non-zero so bugs in
        # bit-shifting access show up.
        t = self.theclass(12, 59, 59, 8000)
        self.assertEqual(t.hour, 12)
        self.assertEqual(t.minute, 59)
        self.assertEqual(t.second, 59)
        self.assertEqual(t.microsecond, 8000)

    eleza test_roundtrip(self):
        t = self.theclass(1, 2, 3, 4)

        # Verify t -> string -> time identity.
        s = repr(t)
        self.assertKweli(s.startswith('datetime.'))
        s = s[9:]
        t2 = eval(s)
        self.assertEqual(t, t2)

        # Verify identity via reconstructing kutoka pieces.
        t2 = self.theclass(t.hour, t.minute, t.second,
                           t.microsecond)
        self.assertEqual(t, t2)

    eleza test_comparing(self):
        args = [1, 2, 3, 4]
        t1 = self.theclass(*args)
        t2 = self.theclass(*args)
        self.assertEqual(t1, t2)
        self.assertKweli(t1 <= t2)
        self.assertKweli(t1 >= t2)
        self.assertUongo(t1 != t2)
        self.assertUongo(t1 < t2)
        self.assertUongo(t1 > t2)

        kila i kwenye range(len(args)):
            newargs = args[:]
            newargs[i] = args[i] + 1
            t2 = self.theclass(*newargs)   # this ni larger than t1
            self.assertKweli(t1 < t2)
            self.assertKweli(t2 > t1)
            self.assertKweli(t1 <= t2)
            self.assertKweli(t2 >= t1)
            self.assertKweli(t1 != t2)
            self.assertKweli(t2 != t1)
            self.assertUongo(t1 == t2)
            self.assertUongo(t2 == t1)
            self.assertUongo(t1 > t2)
            self.assertUongo(t2 < t1)
            self.assertUongo(t1 >= t2)
            self.assertUongo(t2 <= t1)

        kila badarg kwenye OTHERSTUFF:
            self.assertEqual(t1 == badarg, Uongo)
            self.assertEqual(t1 != badarg, Kweli)
            self.assertEqual(badarg == t1, Uongo)
            self.assertEqual(badarg != t1, Kweli)

            self.assertRaises(TypeError, lambda: t1 <= badarg)
            self.assertRaises(TypeError, lambda: t1 < badarg)
            self.assertRaises(TypeError, lambda: t1 > badarg)
            self.assertRaises(TypeError, lambda: t1 >= badarg)
            self.assertRaises(TypeError, lambda: badarg <= t1)
            self.assertRaises(TypeError, lambda: badarg < t1)
            self.assertRaises(TypeError, lambda: badarg > t1)
            self.assertRaises(TypeError, lambda: badarg >= t1)

    eleza test_bad_constructor_arguments(self):
        # bad hours
        self.theclass(0, 0)    # no exception
        self.theclass(23, 0)   # no exception
        self.assertRaises(ValueError, self.theclass, -1, 0)
        self.assertRaises(ValueError, self.theclass, 24, 0)
        # bad minutes
        self.theclass(23, 0)    # no exception
        self.theclass(23, 59)   # no exception
        self.assertRaises(ValueError, self.theclass, 23, -1)
        self.assertRaises(ValueError, self.theclass, 23, 60)
        # bad seconds
        self.theclass(23, 59, 0)    # no exception
        self.theclass(23, 59, 59)   # no exception
        self.assertRaises(ValueError, self.theclass, 23, 59, -1)
        self.assertRaises(ValueError, self.theclass, 23, 59, 60)
        # bad microseconds
        self.theclass(23, 59, 59, 0)        # no exception
        self.theclass(23, 59, 59, 999999)   # no exception
        self.assertRaises(ValueError, self.theclass, 23, 59, 59, -1)
        self.assertRaises(ValueError, self.theclass, 23, 59, 59, 1000000)

    eleza test_hash_equality(self):
        d = self.theclass(23, 30, 17)
        e = self.theclass(23, 30, 17)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

        d = self.theclass(0,  5, 17)
        e = self.theclass(0,  5, 17)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

    eleza test_isoformat(self):
        t = self.theclass(4, 5, 1, 123)
        self.assertEqual(t.isoformat(), "04:05:01.000123")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass()
        self.assertEqual(t.isoformat(), "00:00:00")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=1)
        self.assertEqual(t.isoformat(), "00:00:00.000001")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=10)
        self.assertEqual(t.isoformat(), "00:00:00.000010")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=100)
        self.assertEqual(t.isoformat(), "00:00:00.000100")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=1000)
        self.assertEqual(t.isoformat(), "00:00:00.001000")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=10000)
        self.assertEqual(t.isoformat(), "00:00:00.010000")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(microsecond=100000)
        self.assertEqual(t.isoformat(), "00:00:00.100000")
        self.assertEqual(t.isoformat(), str(t))

        t = self.theclass(hour=12, minute=34, second=56, microsecond=123456)
        self.assertEqual(t.isoformat(timespec='hours'), "12")
        self.assertEqual(t.isoformat(timespec='minutes'), "12:34")
        self.assertEqual(t.isoformat(timespec='seconds'), "12:34:56")
        self.assertEqual(t.isoformat(timespec='milliseconds'), "12:34:56.123")
        self.assertEqual(t.isoformat(timespec='microseconds'), "12:34:56.123456")
        self.assertEqual(t.isoformat(timespec='auto'), "12:34:56.123456")
        self.assertRaises(ValueError, t.isoformat, timespec='monkey')
        # bpo-34482: Check that surrogates are handled properly.
        self.assertRaises(ValueError, t.isoformat, timespec='\ud800')

        t = self.theclass(hour=12, minute=34, second=56, microsecond=999500)
        self.assertEqual(t.isoformat(timespec='milliseconds'), "12:34:56.999")

        t = self.theclass(hour=12, minute=34, second=56, microsecond=0)
        self.assertEqual(t.isoformat(timespec='milliseconds'), "12:34:56.000")
        self.assertEqual(t.isoformat(timespec='microseconds'), "12:34:56.000000")
        self.assertEqual(t.isoformat(timespec='auto'), "12:34:56")

    eleza test_isoformat_timezone(self):
        tzoffsets = [
            ('05:00', timedelta(hours=5)),
            ('02:00', timedelta(hours=2)),
            ('06:27', timedelta(hours=6, minutes=27)),
            ('12:32:30', timedelta(hours=12, minutes=32, seconds=30)),
            ('02:04:09.123456', timedelta(hours=2, minutes=4, seconds=9, microseconds=123456))
        ]

        tzinfos = [
            ('', Tupu),
            ('+00:00', timezone.utc),
            ('+00:00', timezone(timedelta(0))),
        ]

        tzinfos += [
            (prefix + expected, timezone(sign * td))
            kila expected, td kwenye tzoffsets
            kila prefix, sign kwenye [('-', -1), ('+', 1)]
        ]

        t_base = self.theclass(12, 37, 9)
        exp_base = '12:37:09'

        kila exp_tz, tzi kwenye tzinfos:
            t = t_base.replace(tzinfo=tzi)
            exp = exp_base + exp_tz
            with self.subTest(tzi=tzi):
                assert t.isoformat() == exp

    eleza test_1653736(self):
        # verify it doesn't accept extra keyword arguments
        t = self.theclass(second=1)
        self.assertRaises(TypeError, t.isoformat, foo=3)

    eleza test_strftime(self):
        t = self.theclass(1, 2, 3, 4)
        self.assertEqual(t.strftime('%H %M %S %f'), "01 02 03 000004")
        # A naive object replaces %z na %Z with empty strings.
        self.assertEqual(t.strftime("'%z' '%Z'"), "'' ''")

        # bpo-34482: Check that surrogates don't cause a crash.
        jaribu:
            t.strftime('%H\ud800%M')
        tatizo UnicodeEncodeError:
            pita

    eleza test_format(self):
        t = self.theclass(1, 2, 3, 4)
        self.assertEqual(t.__format__(''), str(t))

        with self.assertRaisesRegex(TypeError, 'must be str, sio int'):
            t.__format__(123)

        # check that a derived class's __str__() gets called
        kundi A(self.theclass):
            eleza __str__(self):
                rudisha 'A'
        a = A(1, 2, 3, 4)
        self.assertEqual(a.__format__(''), 'A')

        # check that a derived class's strftime gets called
        kundi B(self.theclass):
            eleza strftime(self, format_spec):
                rudisha 'B'
        b = B(1, 2, 3, 4)
        self.assertEqual(b.__format__(''), str(t))

        kila fmt kwenye ['%H %M %S',
                    ]:
            self.assertEqual(t.__format__(fmt), t.strftime(fmt))
            self.assertEqual(a.__format__(fmt), t.strftime(fmt))
            self.assertEqual(b.__format__(fmt), 'B')

    eleza test_str(self):
        self.assertEqual(str(self.theclass(1, 2, 3, 4)), "01:02:03.000004")
        self.assertEqual(str(self.theclass(10, 2, 3, 4000)), "10:02:03.004000")
        self.assertEqual(str(self.theclass(0, 2, 3, 400000)), "00:02:03.400000")
        self.assertEqual(str(self.theclass(12, 2, 3, 0)), "12:02:03")
        self.assertEqual(str(self.theclass(23, 15, 0, 0)), "23:15:00")

    eleza test_repr(self):
        name = 'datetime.' + self.theclass.__name__
        self.assertEqual(repr(self.theclass(1, 2, 3, 4)),
                         "%s(1, 2, 3, 4)" % name)
        self.assertEqual(repr(self.theclass(10, 2, 3, 4000)),
                         "%s(10, 2, 3, 4000)" % name)
        self.assertEqual(repr(self.theclass(0, 2, 3, 400000)),
                         "%s(0, 2, 3, 400000)" % name)
        self.assertEqual(repr(self.theclass(12, 2, 3, 0)),
                         "%s(12, 2, 3)" % name)
        self.assertEqual(repr(self.theclass(23, 15, 0, 0)),
                         "%s(23, 15)" % name)

    eleza test_resolution_info(self):
        self.assertIsInstance(self.theclass.min, self.theclass)
        self.assertIsInstance(self.theclass.max, self.theclass)
        self.assertIsInstance(self.theclass.resolution, timedelta)
        self.assertKweli(self.theclass.max > self.theclass.min)

    eleza test_pickling(self):
        args = 20, 59, 16, 64**2
        orig = self.theclass(*args)
        kila pickler, unpickler, proto kwenye pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)
        self.assertEqual(orig.__reduce__(), orig.__reduce_ex__(2))

    eleza test_pickling_subclass_time(self):
        args = 20, 59, 16, 64**2
        orig = SubclassTime(*args)
        kila pickler, unpickler, proto kwenye pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)

    eleza test_compat_unpickle(self):
        tests = [
            (b"cdatetime\ntime\n(S'\\x14;\\x10\\x00\\x10\\x00'\ntR.",
             (20, 59, 16, 64**2)),
            (b'cdatetime\ntime\n(U\x06\x14;\x10\x00\x10\x00tR.',
             (20, 59, 16, 64**2)),
            (b'\x80\x02cdatetime\ntime\nU\x06\x14;\x10\x00\x10\x00\x85R.',
             (20, 59, 16, 64**2)),
            (b"cdatetime\ntime\n(S'\\x14;\\x19\\x00\\x10\\x00'\ntR.",
             (20, 59, 25, 64**2)),
            (b'cdatetime\ntime\n(U\x06\x14;\x19\x00\x10\x00tR.',
             (20, 59, 25, 64**2)),
            (b'\x80\x02cdatetime\ntime\nU\x06\x14;\x19\x00\x10\x00\x85R.',
             (20, 59, 25, 64**2)),
        ]
        kila i, (data, args) kwenye enumerate(tests):
            with self.subTest(i=i):
                expected = self.theclass(*args)
                kila loads kwenye pickle_loads:
                    derived = loads(data, encoding='latin1')
                    self.assertEqual(derived, expected)

    eleza test_bool(self):
        # time ni always Kweli.
        cls = self.theclass
        self.assertKweli(cls(1))
        self.assertKweli(cls(0, 1))
        self.assertKweli(cls(0, 0, 1))
        self.assertKweli(cls(0, 0, 0, 1))
        self.assertKweli(cls(0))
        self.assertKweli(cls())

    eleza test_replace(self):
        cls = self.theclass
        args = [1, 2, 3, 4]
        base = cls(*args)
        self.assertEqual(base, base.replace())

        i = 0
        kila name, newval kwenye (("hour", 5),
                             ("minute", 6),
                             ("second", 7),
                             ("microsecond", 8)):
            newargs = args[:]
            newargs[i] = newval
            expected = cls(*newargs)
            got = base.replace(**{name: newval})
            self.assertEqual(expected, got)
            i += 1

        # Out of bounds.
        base = cls(1)
        self.assertRaises(ValueError, base.replace, hour=24)
        self.assertRaises(ValueError, base.replace, minute=-1)
        self.assertRaises(ValueError, base.replace, second=100)
        self.assertRaises(ValueError, base.replace, microsecond=1000000)

    eleza test_subclass_replace(self):
        kundi TimeSubclass(self.theclass):
            pita

        ctime = TimeSubclass(12, 30)
        self.assertIs(type(ctime.replace(hour=10)), TimeSubclass)

    eleza test_subclass_time(self):

        kundi C(self.theclass):
            theAnswer = 42

            eleza __new__(cls, *args, **kws):
                temp = kws.copy()
                extra = temp.pop('extra')
                result = self.theclass.__new__(cls, *args, **temp)
                result.extra = extra
                rudisha result

            eleza newmeth(self, start):
                rudisha start + self.hour + self.second

        args = 4, 5, 6

        dt1 = self.theclass(*args)
        dt2 = C(*args, **{'extra': 7})

        self.assertEqual(dt2.__class__, C)
        self.assertEqual(dt2.theAnswer, 42)
        self.assertEqual(dt2.extra, 7)
        self.assertEqual(dt1.isoformat(), dt2.isoformat())
        self.assertEqual(dt2.newmeth(-7), dt1.hour + dt1.second - 7)

    eleza test_backdoor_resistance(self):
        # see TestDate.test_backdoor_resistance().
        base = '2:59.0'
        kila hour_byte kwenye ' ', '9', chr(24), '\xff':
            self.assertRaises(TypeError, self.theclass,
                                         hour_byte + base[1:])
        # Good bytes, but bad tzinfo:
        with self.assertRaisesRegex(TypeError, '^bad tzinfo state arg$'):
            self.theclass(bytes([1] * len(base)), 'EST')

# A mixin kila classes with a tzinfo= argument.  Subclasses must define
# thekundi kama a kundi attribute, na theclass(1, 1, 1, tzinfo=whatever)
# must be legit (which ni true kila time na datetime).
kundi TZInfoBase:

    eleza test_argument_pitaing(self):
        cls = self.theclass
        # A datetime pitaes itself on, a time pitaes Tupu.
        kundi introspective(tzinfo):
            eleza tzname(self, dt):    rudisha dt na "real" ama "none"
            eleza utcoffset(self, dt):
                rudisha timedelta(minutes = dt na 42 ama -42)
            dst = utcoffset

        obj = cls(1, 2, 3, tzinfo=introspective())

        expected = cls ni time na "none" ama "real"
        self.assertEqual(obj.tzname(), expected)

        expected = timedelta(minutes=(cls ni time na -42 ama 42))
        self.assertEqual(obj.utcoffset(), expected)
        self.assertEqual(obj.dst(), expected)

    eleza test_bad_tzinfo_classes(self):
        cls = self.theclass
        self.assertRaises(TypeError, cls, 1, 1, 1, tzinfo=12)

        kundi NiceTry(object):
            eleza __init__(self): pita
            eleza utcoffset(self, dt): pita
        self.assertRaises(TypeError, cls, 1, 1, 1, tzinfo=NiceTry)

        kundi BetterTry(tzinfo):
            eleza __init__(self): pita
            eleza utcoffset(self, dt): pita
        b = BetterTry()
        t = cls(1, 1, 1, tzinfo=b)
        self.assertIs(t.tzinfo, b)

    eleza test_utc_offset_out_of_bounds(self):
        kundi Edgy(tzinfo):
            eleza __init__(self, offset):
                self.offset = timedelta(minutes=offset)
            eleza utcoffset(self, dt):
                rudisha self.offset

        cls = self.theclass
        kila offset, legit kwenye ((-1440, Uongo),
                              (-1439, Kweli),
                              (1439, Kweli),
                              (1440, Uongo)):
            ikiwa cls ni time:
                t = cls(1, 2, 3, tzinfo=Edgy(offset))
            elikiwa cls ni datetime:
                t = cls(6, 6, 6, 1, 2, 3, tzinfo=Edgy(offset))
            isipokua:
                assert 0, "impossible"
            ikiwa legit:
                aofs = abs(offset)
                h, m = divmod(aofs, 60)
                tag = "%c%02d:%02d" % (offset < 0 na '-' ama '+', h, m)
                ikiwa isinstance(t, datetime):
                    t = t.timetz()
                self.assertEqual(str(t), "01:02:03" + tag)
            isipokua:
                self.assertRaises(ValueError, str, t)

    eleza test_tzinfo_classes(self):
        cls = self.theclass
        kundi C1(tzinfo):
            eleza utcoffset(self, dt): rudisha Tupu
            eleza dst(self, dt): rudisha Tupu
            eleza tzname(self, dt): rudisha Tupu
        kila t kwenye (cls(1, 1, 1),
                  cls(1, 1, 1, tzinfo=Tupu),
                  cls(1, 1, 1, tzinfo=C1())):
            self.assertIsTupu(t.utcoffset())
            self.assertIsTupu(t.dst())
            self.assertIsTupu(t.tzname())

        kundi C3(tzinfo):
            eleza utcoffset(self, dt): rudisha timedelta(minutes=-1439)
            eleza dst(self, dt): rudisha timedelta(minutes=1439)
            eleza tzname(self, dt): rudisha "aname"
        t = cls(1, 1, 1, tzinfo=C3())
        self.assertEqual(t.utcoffset(), timedelta(minutes=-1439))
        self.assertEqual(t.dst(), timedelta(minutes=1439))
        self.assertEqual(t.tzname(), "aname")

        # Wrong types.
        kundi C4(tzinfo):
            eleza utcoffset(self, dt): rudisha "aname"
            eleza dst(self, dt): rudisha 7
            eleza tzname(self, dt): rudisha 0
        t = cls(1, 1, 1, tzinfo=C4())
        self.assertRaises(TypeError, t.utcoffset)
        self.assertRaises(TypeError, t.dst)
        self.assertRaises(TypeError, t.tzname)

        # Offset out of range.
        kundi C6(tzinfo):
            eleza utcoffset(self, dt): rudisha timedelta(hours=-24)
            eleza dst(self, dt): rudisha timedelta(hours=24)
        t = cls(1, 1, 1, tzinfo=C6())
        self.assertRaises(ValueError, t.utcoffset)
        self.assertRaises(ValueError, t.dst)

        # Not a whole number of seconds.
        kundi C7(tzinfo):
            eleza utcoffset(self, dt): rudisha timedelta(microseconds=61)
            eleza dst(self, dt): rudisha timedelta(microseconds=-81)
        t = cls(1, 1, 1, tzinfo=C7())
        self.assertEqual(t.utcoffset(), timedelta(microseconds=61))
        self.assertEqual(t.dst(), timedelta(microseconds=-81))

    eleza test_aware_compare(self):
        cls = self.theclass

        # Ensure that utcoffset() gets ignored ikiwa the comparands have
        # the same tzinfo member.
        kundi OperandDependentOffset(tzinfo):
            eleza utcoffset(self, t):
                ikiwa t.minute < 10:
                    # d0 na d1 equal after adjustment
                    rudisha timedelta(minutes=t.minute)
                isipokua:
                    # d2 off kwenye the weeds
                    rudisha timedelta(minutes=59)

        base = cls(8, 9, 10, tzinfo=OperandDependentOffset())
        d0 = base.replace(minute=3)
        d1 = base.replace(minute=9)
        d2 = base.replace(minute=11)
        kila x kwenye d0, d1, d2:
            kila y kwenye d0, d1, d2:
                kila op kwenye lt, le, gt, ge, eq, ne:
                    got = op(x, y)
                    expected = op(x.minute, y.minute)
                    self.assertEqual(got, expected)

        # However, ikiwa they're different members, uctoffset ni sio ignored.
        # Note that a time can't actually have an operand-dependent offset,
        # though (and time.utcoffset() pitaes Tupu to tzinfo.utcoffset()),
        # so skip this test kila time.
        ikiwa cls ni sio time:
            d0 = base.replace(minute=3, tzinfo=OperandDependentOffset())
            d1 = base.replace(minute=9, tzinfo=OperandDependentOffset())
            d2 = base.replace(minute=11, tzinfo=OperandDependentOffset())
            kila x kwenye d0, d1, d2:
                kila y kwenye d0, d1, d2:
                    got = (x > y) - (x < y)
                    ikiwa (x ni d0 ama x ni d1) na (y ni d0 ama y ni d1):
                        expected = 0
                    elikiwa x ni y ni d2:
                        expected = 0
                    elikiwa x ni d2:
                        expected = -1
                    isipokua:
                        assert y ni d2
                        expected = 1
                    self.assertEqual(got, expected)


# Testing time objects with a non-Tupu tzinfo.
kundi TestTimeTZ(TestTime, TZInfoBase, unittest.TestCase):
    thekundi = time

    eleza test_empty(self):
        t = self.theclass()
        self.assertEqual(t.hour, 0)
        self.assertEqual(t.minute, 0)
        self.assertEqual(t.second, 0)
        self.assertEqual(t.microsecond, 0)
        self.assertIsTupu(t.tzinfo)

    eleza test_zones(self):
        est = FixedOffset(-300, "EST", 1)
        utc = FixedOffset(0, "UTC", -2)
        met = FixedOffset(60, "MET", 3)
        t1 = time( 7, 47, tzinfo=est)
        t2 = time(12, 47, tzinfo=utc)
        t3 = time(13, 47, tzinfo=met)
        t4 = time(microsecond=40)
        t5 = time(microsecond=40, tzinfo=utc)

        self.assertEqual(t1.tzinfo, est)
        self.assertEqual(t2.tzinfo, utc)
        self.assertEqual(t3.tzinfo, met)
        self.assertIsTupu(t4.tzinfo)
        self.assertEqual(t5.tzinfo, utc)

        self.assertEqual(t1.utcoffset(), timedelta(minutes=-300))
        self.assertEqual(t2.utcoffset(), timedelta(minutes=0))
        self.assertEqual(t3.utcoffset(), timedelta(minutes=60))
        self.assertIsTupu(t4.utcoffset())
        self.assertRaises(TypeError, t1.utcoffset, "no args")

        self.assertEqual(t1.tzname(), "EST")
        self.assertEqual(t2.tzname(), "UTC")
        self.assertEqual(t3.tzname(), "MET")
        self.assertIsTupu(t4.tzname())
        self.assertRaises(TypeError, t1.tzname, "no args")

        self.assertEqual(t1.dst(), timedelta(minutes=1))
        self.assertEqual(t2.dst(), timedelta(minutes=-2))
        self.assertEqual(t3.dst(), timedelta(minutes=3))
        self.assertIsTupu(t4.dst())
        self.assertRaises(TypeError, t1.dst, "no args")

        self.assertEqual(hash(t1), hash(t2))
        self.assertEqual(hash(t1), hash(t3))
        self.assertEqual(hash(t2), hash(t3))

        self.assertEqual(t1, t2)
        self.assertEqual(t1, t3)
        self.assertEqual(t2, t3)
        self.assertNotEqual(t4, t5) # mixed tz-aware & naive
        self.assertRaises(TypeError, lambda: t4 < t5) # mixed tz-aware & naive
        self.assertRaises(TypeError, lambda: t5 < t4) # mixed tz-aware & naive

        self.assertEqual(str(t1), "07:47:00-05:00")
        self.assertEqual(str(t2), "12:47:00+00:00")
        self.assertEqual(str(t3), "13:47:00+01:00")
        self.assertEqual(str(t4), "00:00:00.000040")
        self.assertEqual(str(t5), "00:00:00.000040+00:00")

        self.assertEqual(t1.isoformat(), "07:47:00-05:00")
        self.assertEqual(t2.isoformat(), "12:47:00+00:00")
        self.assertEqual(t3.isoformat(), "13:47:00+01:00")
        self.assertEqual(t4.isoformat(), "00:00:00.000040")
        self.assertEqual(t5.isoformat(), "00:00:00.000040+00:00")

        d = 'datetime.time'
        self.assertEqual(repr(t1), d + "(7, 47, tzinfo=est)")
        self.assertEqual(repr(t2), d + "(12, 47, tzinfo=utc)")
        self.assertEqual(repr(t3), d + "(13, 47, tzinfo=met)")
        self.assertEqual(repr(t4), d + "(0, 0, 0, 40)")
        self.assertEqual(repr(t5), d + "(0, 0, 0, 40, tzinfo=utc)")

        self.assertEqual(t1.strftime("%H:%M:%S %%Z=%Z %%z=%z"),
                                     "07:47:00 %Z=EST %z=-0500")
        self.assertEqual(t2.strftime("%H:%M:%S %Z %z"), "12:47:00 UTC +0000")
        self.assertEqual(t3.strftime("%H:%M:%S %Z %z"), "13:47:00 MET +0100")

        yuck = FixedOffset(-1439, "%z %Z %%z%%Z")
        t1 = time(23, 59, tzinfo=yuck)
        self.assertEqual(t1.strftime("%H:%M %%Z='%Z' %%z='%z'"),
                                     "23:59 %Z='%z %Z %%z%%Z' %z='-2359'")

        # Check that an invalid tzname result ashirias an exception.
        kundi Badtzname(tzinfo):
            tz = 42
            eleza tzname(self, dt): rudisha self.tz
        t = time(2, 3, 4, tzinfo=Badtzname())
        self.assertEqual(t.strftime("%H:%M:%S"), "02:03:04")
        self.assertRaises(TypeError, t.strftime, "%Z")

        # Issue #6697:
        ikiwa '_Fast' kwenye self.__class__.__name__:
            Badtzname.tz = '\ud800'
            self.assertRaises(ValueError, t.strftime, "%Z")

    eleza test_hash_edge_cases(self):
        # Offsets that overflow a basic time.
        t1 = self.theclass(0, 1, 2, 3, tzinfo=FixedOffset(1439, ""))
        t2 = self.theclass(0, 0, 2, 3, tzinfo=FixedOffset(1438, ""))
        self.assertEqual(hash(t1), hash(t2))

        t1 = self.theclass(23, 58, 6, 100, tzinfo=FixedOffset(-1000, ""))
        t2 = self.theclass(23, 48, 6, 100, tzinfo=FixedOffset(-1010, ""))
        self.assertEqual(hash(t1), hash(t2))

    eleza test_pickling(self):
        # Try one without a tzinfo.
        args = 20, 59, 16, 64**2
        orig = self.theclass(*args)
        kila pickler, unpickler, proto kwenye pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)
        self.assertEqual(orig.__reduce__(), orig.__reduce_ex__(2))

        # Try one with a tzinfo.
        tinfo = PicklableFixedOffset(-300, 'cookie')
        orig = self.theclass(5, 6, 7, tzinfo=tinfo)
        kila pickler, unpickler, proto kwenye pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)
            self.assertIsInstance(derived.tzinfo, PicklableFixedOffset)
            self.assertEqual(derived.utcoffset(), timedelta(minutes=-300))
            self.assertEqual(derived.tzname(), 'cookie')
        self.assertEqual(orig.__reduce__(), orig.__reduce_ex__(2))

    eleza test_compat_unpickle(self):
        tests = [
            b"cdatetime\ntime\n(S'\\x05\\x06\\x07\\x01\\xe2@'\n"
            b"ctest.datetimetester\nPicklableFixedOffset\n(tR"
            b"(dS'_FixedOffset__offset'\ncdatetime\ntimedelta\n"
            b"(I-1\nI68400\nI0\ntRs"
            b"S'_FixedOffset__dstoffset'\nNs"
            b"S'_FixedOffset__name'\nS'cookie'\nsbtR.",

            b'cdatetime\ntime\n(U\x06\x05\x06\x07\x01\xe2@'
            b'ctest.datetimetester\nPicklableFixedOffset\n)R'
            b'}(U\x14_FixedOffset__offsetcdatetime\ntimedelta\n'
            b'(J\xff\xff\xff\xffJ0\x0b\x01\x00K\x00tR'
            b'U\x17_FixedOffset__dstoffsetN'
            b'U\x12_FixedOffset__nameU\x06cookieubtR.',

            b'\x80\x02cdatetime\ntime\nU\x06\x05\x06\x07\x01\xe2@'
            b'ctest.datetimetester\nPicklableFixedOffset\n)R'
            b'}(U\x14_FixedOffset__offsetcdatetime\ntimedelta\n'
            b'J\xff\xff\xff\xffJ0\x0b\x01\x00K\x00\x87R'
            b'U\x17_FixedOffset__dstoffsetN'
            b'U\x12_FixedOffset__nameU\x06cookieub\x86R.',
        ]

        tinfo = PicklableFixedOffset(-300, 'cookie')
        expected = self.theclass(5, 6, 7, 123456, tzinfo=tinfo)
        kila data kwenye tests:
            kila loads kwenye pickle_loads:
                derived = loads(data, encoding='latin1')
                self.assertEqual(derived, expected, repr(data))
                self.assertIsInstance(derived.tzinfo, PicklableFixedOffset)
                self.assertEqual(derived.utcoffset(), timedelta(minutes=-300))
                self.assertEqual(derived.tzname(), 'cookie')

    eleza test_more_bool(self):
        # time ni always Kweli.
        cls = self.theclass

        t = cls(0, tzinfo=FixedOffset(-300, ""))
        self.assertKweli(t)

        t = cls(5, tzinfo=FixedOffset(-300, ""))
        self.assertKweli(t)

        t = cls(5, tzinfo=FixedOffset(300, ""))
        self.assertKweli(t)

        t = cls(23, 59, tzinfo=FixedOffset(23*60 + 59, ""))
        self.assertKweli(t)

    eleza test_replace(self):
        cls = self.theclass
        z100 = FixedOffset(100, "+100")
        zm200 = FixedOffset(timedelta(minutes=-200), "-200")
        args = [1, 2, 3, 4, z100]
        base = cls(*args)
        self.assertEqual(base, base.replace())

        i = 0
        kila name, newval kwenye (("hour", 5),
                             ("minute", 6),
                             ("second", 7),
                             ("microsecond", 8),
                             ("tzinfo", zm200)):
            newargs = args[:]
            newargs[i] = newval
            expected = cls(*newargs)
            got = base.replace(**{name: newval})
            self.assertEqual(expected, got)
            i += 1

        # Ensure we can get rid of a tzinfo.
        self.assertEqual(base.tzname(), "+100")
        base2 = base.replace(tzinfo=Tupu)
        self.assertIsTupu(base2.tzinfo)
        self.assertIsTupu(base2.tzname())

        # Ensure we can add one.
        base3 = base2.replace(tzinfo=z100)
        self.assertEqual(base, base3)
        self.assertIs(base.tzinfo, base3.tzinfo)

        # Out of bounds.
        base = cls(1)
        self.assertRaises(ValueError, base.replace, hour=24)
        self.assertRaises(ValueError, base.replace, minute=-1)
        self.assertRaises(ValueError, base.replace, second=100)
        self.assertRaises(ValueError, base.replace, microsecond=1000000)

    eleza test_mixed_compare(self):
        t1 = self.theclass(1, 2, 3)
        t2 = self.theclass(1, 2, 3)
        self.assertEqual(t1, t2)
        t2 = t2.replace(tzinfo=Tupu)
        self.assertEqual(t1, t2)
        t2 = t2.replace(tzinfo=FixedOffset(Tupu, ""))
        self.assertEqual(t1, t2)
        t2 = t2.replace(tzinfo=FixedOffset(0, ""))
        self.assertNotEqual(t1, t2)

        # In time w/ identical tzinfo objects, utcoffset ni ignored.
        kundi Varies(tzinfo):
            eleza __init__(self):
                self.offset = timedelta(minutes=22)
            eleza utcoffset(self, t):
                self.offset += timedelta(minutes=1)
                rudisha self.offset

        v = Varies()
        t1 = t2.replace(tzinfo=v)
        t2 = t2.replace(tzinfo=v)
        self.assertEqual(t1.utcoffset(), timedelta(minutes=23))
        self.assertEqual(t2.utcoffset(), timedelta(minutes=24))
        self.assertEqual(t1, t2)

        # But ikiwa they're sio identical, it isn't ignored.
        t2 = t2.replace(tzinfo=Varies())
        self.assertKweli(t1 < t2)  # t1's offset counter still going up

    eleza test_kutokaisoformat(self):
        time_examples = [
            (0, 0, 0, 0),
            (23, 59, 59, 999999),
        ]

        hh = (9, 12, 20)
        mm = (5, 30)
        ss = (4, 45)
        usec = (0, 245000, 678901)

        time_examples += list(itertools.product(hh, mm, ss, usec))

        tzinfos = [Tupu, timezone.utc,
                   timezone(timedelta(hours=2)),
                   timezone(timedelta(hours=6, minutes=27))]

        kila ttup kwenye time_examples:
            kila tzi kwenye tzinfos:
                t = self.theclass(*ttup, tzinfo=tzi)
                tstr = t.isoformat()

                with self.subTest(tstr=tstr):
                    t_rt = self.theclass.kutokaisoformat(tstr)
                    self.assertEqual(t, t_rt)

    eleza test_kutokaisoformat_timezone(self):
        base_time = self.theclass(12, 30, 45, 217456)

        tzoffsets = [
            timedelta(hours=5), timedelta(hours=2),
            timedelta(hours=6, minutes=27),
            timedelta(hours=12, minutes=32, seconds=30),
            timedelta(hours=2, minutes=4, seconds=9, microseconds=123456)
        ]

        tzoffsets += [-1 * td kila td kwenye tzoffsets]

        tzinfos = [Tupu, timezone.utc,
                   timezone(timedelta(hours=0))]

        tzinfos += [timezone(td) kila td kwenye tzoffsets]

        kila tzi kwenye tzinfos:
            t = base_time.replace(tzinfo=tzi)
            tstr = t.isoformat()

            with self.subTest(tstr=tstr):
                t_rt = self.theclass.kutokaisoformat(tstr)
                assert t == t_rt, t_rt

    eleza test_kutokaisoformat_timespecs(self):
        time_bases = [
            (8, 17, 45, 123456),
            (8, 17, 45, 0)
        ]

        tzinfos = [Tupu, timezone.utc,
                   timezone(timedelta(hours=-5)),
                   timezone(timedelta(hours=2)),
                   timezone(timedelta(hours=6, minutes=27))]

        timespecs = ['hours', 'minutes', 'seconds',
                     'milliseconds', 'microseconds']

        kila ip, ts kwenye enumerate(timespecs):
            kila tzi kwenye tzinfos:
                kila t_tuple kwenye time_bases:
                    ikiwa ts == 'milliseconds':
                        new_microseconds = 1000 * (t_tuple[-1] // 1000)
                        t_tuple = t_tuple[0:-1] + (new_microseconds,)

                    t = self.theclass(*(t_tuple[0:(1 + ip)]), tzinfo=tzi)
                    tstr = t.isoformat(timespec=ts)
                    with self.subTest(tstr=tstr):
                        t_rt = self.theclass.kutokaisoformat(tstr)
                        self.assertEqual(t, t_rt)

    eleza test_kutokaisoformat_fails(self):
        bad_strs = [
            '',                         # Empty string
            '12\ud80000',               # Invalid separator - surrogate char
            '12:',                      # Ends on a separator
            '12:30:',                   # Ends on a separator
            '12:30:15.',                # Ends on a separator
            '1',                        # Incomplete hours
            '12:3',                     # Incomplete minutes
            '12:30:1',                  # Incomplete seconds
            '1a:30:45.334034',          # Invalid character kwenye hours
            '12:a0:45.334034',          # Invalid character kwenye minutes
            '12:30:a5.334034',          # Invalid character kwenye seconds
            '12:30:45.1234',            # Too many digits kila milliseconds
            '12:30:45.1234567',         # Too many digits kila microseconds
            '12:30:45.123456+24:30',    # Invalid time zone offset
            '12:30:45.123456-24:30',    # Invalid negative offset
            '12：30：45',                 # Uses full-width unicode colons
            '12:30:45․123456',          # Uses \u2024 kwenye place of decimal point
            '12:30:45a',                # Extra at tend of basic time
            '12:30:45.123a',            # Extra at end of millisecond time
            '12:30:45.123456a',         # Extra at end of microsecond time
            '12:30:45.123456+12:00:30a',    # Extra at end of full time
        ]

        kila bad_str kwenye bad_strs:
            with self.subTest(bad_str=bad_str):
                with self.assertRaises(ValueError):
                    self.theclass.kutokaisoformat(bad_str)

    eleza test_kutokaisoformat_fails_typeerror(self):
        # Test the kutokaisoformat fails when pitaed the wrong type
        agiza io

        bad_types = [b'12:30:45', Tupu, io.StringIO('12:30:45')]

        kila bad_type kwenye bad_types:
            with self.assertRaises(TypeError):
                self.theclass.kutokaisoformat(bad_type)

    eleza test_kutokaisoformat_subclass(self):
        kundi TimeSubclass(self.theclass):
            pita

        tsc = TimeSubclass(12, 14, 45, 203745, tzinfo=timezone.utc)
        tsc_rt = TimeSubclass.kutokaisoformat(tsc.isoformat())

        self.assertEqual(tsc, tsc_rt)
        self.assertIsInstance(tsc_rt, TimeSubclass)

    eleza test_subclass_timetz(self):

        kundi C(self.theclass):
            theAnswer = 42

            eleza __new__(cls, *args, **kws):
                temp = kws.copy()
                extra = temp.pop('extra')
                result = self.theclass.__new__(cls, *args, **temp)
                result.extra = extra
                rudisha result

            eleza newmeth(self, start):
                rudisha start + self.hour + self.second

        args = 4, 5, 6, 500, FixedOffset(-300, "EST", 1)

        dt1 = self.theclass(*args)
        dt2 = C(*args, **{'extra': 7})

        self.assertEqual(dt2.__class__, C)
        self.assertEqual(dt2.theAnswer, 42)
        self.assertEqual(dt2.extra, 7)
        self.assertEqual(dt1.utcoffset(), dt2.utcoffset())
        self.assertEqual(dt2.newmeth(-7), dt1.hour + dt1.second - 7)


# Testing datetime objects with a non-Tupu tzinfo.

kundi TestDateTimeTZ(TestDateTime, TZInfoBase, unittest.TestCase):
    thekundi = datetime

    eleza test_trivial(self):
        dt = self.theclass(1, 2, 3, 4, 5, 6, 7)
        self.assertEqual(dt.year, 1)
        self.assertEqual(dt.month, 2)
        self.assertEqual(dt.day, 3)
        self.assertEqual(dt.hour, 4)
        self.assertEqual(dt.minute, 5)
        self.assertEqual(dt.second, 6)
        self.assertEqual(dt.microsecond, 7)
        self.assertEqual(dt.tzinfo, Tupu)

    eleza test_even_more_compare(self):
        # The test_compare() na test_more_compare() inherited kutoka TestDate
        # na TestDateTime covered non-tzinfo cases.

        # Smallest possible after UTC adjustment.
        t1 = self.theclass(1, 1, 1, tzinfo=FixedOffset(1439, ""))
        # Largest possible after UTC adjustment.
        t2 = self.theclass(MAXYEAR, 12, 31, 23, 59, 59, 999999,
                           tzinfo=FixedOffset(-1439, ""))

        # Make sure those compare correctly, na w/o overflow.
        self.assertKweli(t1 < t2)
        self.assertKweli(t1 != t2)
        self.assertKweli(t2 > t1)

        self.assertEqual(t1, t1)
        self.assertEqual(t2, t2)

        # Equal afer adjustment.
        t1 = self.theclass(1, 12, 31, 23, 59, tzinfo=FixedOffset(1, ""))
        t2 = self.theclass(2, 1, 1, 3, 13, tzinfo=FixedOffset(3*60+13+2, ""))
        self.assertEqual(t1, t2)

        # Change t1 sio to subtract a minute, na t1 should be larger.
        t1 = self.theclass(1, 12, 31, 23, 59, tzinfo=FixedOffset(0, ""))
        self.assertKweli(t1 > t2)

        # Change t1 to subtract 2 minutes, na t1 should be smaller.
        t1 = self.theclass(1, 12, 31, 23, 59, tzinfo=FixedOffset(2, ""))
        self.assertKweli(t1 < t2)

        # Back to the original t1, but make seconds resolve it.
        t1 = self.theclass(1, 12, 31, 23, 59, tzinfo=FixedOffset(1, ""),
                           second=1)
        self.assertKweli(t1 > t2)

        # Likewise, but make microseconds resolve it.
        t1 = self.theclass(1, 12, 31, 23, 59, tzinfo=FixedOffset(1, ""),
                           microsecond=1)
        self.assertKweli(t1 > t2)

        # Make t2 naive na it should differ.
        t2 = self.theclass.min
        self.assertNotEqual(t1, t2)
        self.assertEqual(t2, t2)
        # na > comparison should fail
        with self.assertRaises(TypeError):
            t1 > t2

        # It's also naive ikiwa it has tzinfo but tzinfo.utcoffset() ni Tupu.
        kundi Naive(tzinfo):
            eleza utcoffset(self, dt): rudisha Tupu
        t2 = self.theclass(5, 6, 7, tzinfo=Naive())
        self.assertNotEqual(t1, t2)
        self.assertEqual(t2, t2)

        # OTOH, it's OK to compare two of these mixing the two ways of being
        # naive.
        t1 = self.theclass(5, 6, 7)
        self.assertEqual(t1, t2)

        # Try a bogus uctoffset.
        kundi Bogus(tzinfo):
            eleza utcoffset(self, dt):
                rudisha timedelta(minutes=1440) # out of bounds
        t1 = self.theclass(2, 2, 2, tzinfo=Bogus())
        t2 = self.theclass(2, 2, 2, tzinfo=FixedOffset(0, ""))
        self.assertRaises(ValueError, lambda: t1 == t2)

    eleza test_pickling(self):
        # Try one without a tzinfo.
        args = 6, 7, 23, 20, 59, 1, 64**2
        orig = self.theclass(*args)
        kila pickler, unpickler, proto kwenye pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)
        self.assertEqual(orig.__reduce__(), orig.__reduce_ex__(2))

        # Try one with a tzinfo.
        tinfo = PicklableFixedOffset(-300, 'cookie')
        orig = self.theclass(*args, **{'tzinfo': tinfo})
        derived = self.theclass(1, 1, 1, tzinfo=FixedOffset(0, "", 0))
        kila pickler, unpickler, proto kwenye pickle_choices:
            green = pickler.dumps(orig, proto)
            derived = unpickler.loads(green)
            self.assertEqual(orig, derived)
            self.assertIsInstance(derived.tzinfo, PicklableFixedOffset)
            self.assertEqual(derived.utcoffset(), timedelta(minutes=-300))
            self.assertEqual(derived.tzname(), 'cookie')
        self.assertEqual(orig.__reduce__(), orig.__reduce_ex__(2))

    eleza test_compat_unpickle(self):
        tests = [
            b'cdatetime\ndatetime\n'
            b"(S'\\x07\\xdf\\x0b\\x1b\\x14;\\x01\\x01\\xe2@'\n"
            b'ctest.datetimetester\nPicklableFixedOffset\n(tR'
            b"(dS'_FixedOffset__offset'\ncdatetime\ntimedelta\n"
            b'(I-1\nI68400\nI0\ntRs'
            b"S'_FixedOffset__dstoffset'\nNs"
            b"S'_FixedOffset__name'\nS'cookie'\nsbtR.",

            b'cdatetime\ndatetime\n'
            b'(U\n\x07\xdf\x0b\x1b\x14;\x01\x01\xe2@'
            b'ctest.datetimetester\nPicklableFixedOffset\n)R'
            b'}(U\x14_FixedOffset__offsetcdatetime\ntimedelta\n'
            b'(J\xff\xff\xff\xffJ0\x0b\x01\x00K\x00tR'
            b'U\x17_FixedOffset__dstoffsetN'
            b'U\x12_FixedOffset__nameU\x06cookieubtR.',

            b'\x80\x02cdatetime\ndatetime\n'
            b'U\n\x07\xdf\x0b\x1b\x14;\x01\x01\xe2@'
            b'ctest.datetimetester\nPicklableFixedOffset\n)R'
            b'}(U\x14_FixedOffset__offsetcdatetime\ntimedelta\n'
            b'J\xff\xff\xff\xffJ0\x0b\x01\x00K\x00\x87R'
            b'U\x17_FixedOffset__dstoffsetN'
            b'U\x12_FixedOffset__nameU\x06cookieub\x86R.',
        ]
        args = 2015, 11, 27, 20, 59, 1, 123456
        tinfo = PicklableFixedOffset(-300, 'cookie')
        expected = self.theclass(*args, **{'tzinfo': tinfo})
        kila data kwenye tests:
            kila loads kwenye pickle_loads:
                derived = loads(data, encoding='latin1')
                self.assertEqual(derived, expected)
                self.assertIsInstance(derived.tzinfo, PicklableFixedOffset)
                self.assertEqual(derived.utcoffset(), timedelta(minutes=-300))
                self.assertEqual(derived.tzname(), 'cookie')

    eleza test_extreme_hashes(self):
        # If an attempt ni made to hash these via subtracting the offset
        # then hashing a datetime object, OverflowError results.  The
        # Python implementation used to blow up here.
        t = self.theclass(1, 1, 1, tzinfo=FixedOffset(1439, ""))
        hash(t)
        t = self.theclass(MAXYEAR, 12, 31, 23, 59, 59, 999999,
                          tzinfo=FixedOffset(-1439, ""))
        hash(t)

        # OTOH, an OOB offset should blow up.
        t = self.theclass(5, 5, 5, tzinfo=FixedOffset(-1440, ""))
        self.assertRaises(ValueError, hash, t)

    eleza test_zones(self):
        est = FixedOffset(-300, "EST")
        utc = FixedOffset(0, "UTC")
        met = FixedOffset(60, "MET")
        t1 = datetime(2002, 3, 19,  7, 47, tzinfo=est)
        t2 = datetime(2002, 3, 19, 12, 47, tzinfo=utc)
        t3 = datetime(2002, 3, 19, 13, 47, tzinfo=met)
        self.assertEqual(t1.tzinfo, est)
        self.assertEqual(t2.tzinfo, utc)
        self.assertEqual(t3.tzinfo, met)
        self.assertEqual(t1.utcoffset(), timedelta(minutes=-300))
        self.assertEqual(t2.utcoffset(), timedelta(minutes=0))
        self.assertEqual(t3.utcoffset(), timedelta(minutes=60))
        self.assertEqual(t1.tzname(), "EST")
        self.assertEqual(t2.tzname(), "UTC")
        self.assertEqual(t3.tzname(), "MET")
        self.assertEqual(hash(t1), hash(t2))
        self.assertEqual(hash(t1), hash(t3))
        self.assertEqual(hash(t2), hash(t3))
        self.assertEqual(t1, t2)
        self.assertEqual(t1, t3)
        self.assertEqual(t2, t3)
        self.assertEqual(str(t1), "2002-03-19 07:47:00-05:00")
        self.assertEqual(str(t2), "2002-03-19 12:47:00+00:00")
        self.assertEqual(str(t3), "2002-03-19 13:47:00+01:00")
        d = 'datetime.datetime(2002, 3, 19, '
        self.assertEqual(repr(t1), d + "7, 47, tzinfo=est)")
        self.assertEqual(repr(t2), d + "12, 47, tzinfo=utc)")
        self.assertEqual(repr(t3), d + "13, 47, tzinfo=met)")

    eleza test_combine(self):
        met = FixedOffset(60, "MET")
        d = date(2002, 3, 4)
        tz = time(18, 45, 3, 1234, tzinfo=met)
        dt = datetime.combine(d, tz)
        self.assertEqual(dt, datetime(2002, 3, 4, 18, 45, 3, 1234,
                                        tzinfo=met))

    eleza test_extract(self):
        met = FixedOffset(60, "MET")
        dt = self.theclass(2002, 3, 4, 18, 45, 3, 1234, tzinfo=met)
        self.assertEqual(dt.date(), date(2002, 3, 4))
        self.assertEqual(dt.time(), time(18, 45, 3, 1234))
        self.assertEqual(dt.timetz(), time(18, 45, 3, 1234, tzinfo=met))

    eleza test_tz_aware_arithmetic(self):
        now = self.theclass.now()
        tz55 = FixedOffset(-330, "west 5:30")
        timeaware = now.time().replace(tzinfo=tz55)
        nowaware = self.theclass.combine(now.date(), timeaware)
        self.assertIs(nowaware.tzinfo, tz55)
        self.assertEqual(nowaware.timetz(), timeaware)

        # Can't mix aware na non-aware.
        self.assertRaises(TypeError, lambda: now - nowaware)
        self.assertRaises(TypeError, lambda: nowaware - now)

        # And adding datetime's doesn't make sense, aware ama not.
        self.assertRaises(TypeError, lambda: now + nowaware)
        self.assertRaises(TypeError, lambda: nowaware + now)
        self.assertRaises(TypeError, lambda: nowaware + nowaware)

        # Subtracting should tuma 0.
        self.assertEqual(now - now, timedelta(0))
        self.assertEqual(nowaware - nowaware, timedelta(0))

        # Adding a delta should preserve tzinfo.
        delta = timedelta(weeks=1, minutes=12, microseconds=5678)
        nowawareplus = nowaware + delta
        self.assertIs(nowaware.tzinfo, tz55)
        nowawareplus2 = delta + nowaware
        self.assertIs(nowawareplus2.tzinfo, tz55)
        self.assertEqual(nowawareplus, nowawareplus2)

        # that - delta should be what we started with, na that - what we
        # started with should be delta.
        diff = nowawareplus - delta
        self.assertIs(diff.tzinfo, tz55)
        self.assertEqual(nowaware, diff)
        self.assertRaises(TypeError, lambda: delta - nowawareplus)
        self.assertEqual(nowawareplus - nowaware, delta)

        # Make up a random timezone.
        tzr = FixedOffset(random.randrange(-1439, 1440), "randomtimezone")
        # Attach it to nowawareplus.
        nowawareplus = nowawareplus.replace(tzinfo=tzr)
        self.assertIs(nowawareplus.tzinfo, tzr)
        # Make sure the difference takes the timezone adjustments into account.
        got = nowaware - nowawareplus
        # Expected:  (nowaware base - nowaware offset) -
        #            (nowawareplus base - nowawareplus offset) =
        #            (nowaware base - nowawareplus base) +
        #            (nowawareplus offset - nowaware offset) =
        #            -delta + nowawareplus offset - nowaware offset
        expected = nowawareplus.utcoffset() - nowaware.utcoffset() - delta
        self.assertEqual(got, expected)

        # Try max possible difference.
        min = self.theclass(1, 1, 1, tzinfo=FixedOffset(1439, "min"))
        max = self.theclass(MAXYEAR, 12, 31, 23, 59, 59, 999999,
                            tzinfo=FixedOffset(-1439, "max"))
        maxdiff = max - min
        self.assertEqual(maxdiff, self.theclass.max - self.theclass.min +
                                  timedelta(minutes=2*1439))
        # Different tzinfo, but the same offset
        tza = timezone(HOUR, 'A')
        tzb = timezone(HOUR, 'B')
        delta = min.replace(tzinfo=tza) - max.replace(tzinfo=tzb)
        self.assertEqual(delta, self.theclass.min - self.theclass.max)

    eleza test_tzinfo_now(self):
        meth = self.theclass.now
        # Ensure it doesn't require tzinfo (i.e., that this doesn't blow up).
        base = meth()
        # Try with na without naming the keyword.
        off42 = FixedOffset(42, "42")
        another = meth(off42)
        again = meth(tz=off42)
        self.assertIs(another.tzinfo, again.tzinfo)
        self.assertEqual(another.utcoffset(), timedelta(minutes=42))
        # Bad argument with na w/o naming the keyword.
        self.assertRaises(TypeError, meth, 16)
        self.assertRaises(TypeError, meth, tzinfo=16)
        # Bad keyword name.
        self.assertRaises(TypeError, meth, tinfo=off42)
        # Too many args.
        self.assertRaises(TypeError, meth, off42, off42)

        # We don't know which time zone we're in, na don't have a tzinfo
        # kundi to represent it, so seeing whether a tz argument actually
        # does a conversion ni tricky.
        utc = FixedOffset(0, "utc", 0)
        kila weirdtz kwenye [FixedOffset(timedelta(hours=15, minutes=58), "weirdtz", 0),
                        timezone(timedelta(hours=15, minutes=58), "weirdtz"),]:
            kila dummy kwenye range(3):
                now = datetime.now(weirdtz)
                self.assertIs(now.tzinfo, weirdtz)
                utcnow = datetime.utcnow().replace(tzinfo=utc)
                now2 = utcnow.astimezone(weirdtz)
                ikiwa abs(now - now2) < timedelta(seconds=30):
                    koma
                # Else the code ni broken, ama more than 30 seconds pitaed between
                # calls; assuming the latter, just try again.
            isipokua:
                # Three strikes na we're out.
                self.fail("utcnow(), now(tz), ama astimezone() may be broken")

    eleza test_tzinfo_kutokatimestamp(self):
        agiza time
        meth = self.theclass.kutokatimestamp
        ts = time.time()
        # Ensure it doesn't require tzinfo (i.e., that this doesn't blow up).
        base = meth(ts)
        # Try with na without naming the keyword.
        off42 = FixedOffset(42, "42")
        another = meth(ts, off42)
        again = meth(ts, tz=off42)
        self.assertIs(another.tzinfo, again.tzinfo)
        self.assertEqual(another.utcoffset(), timedelta(minutes=42))
        # Bad argument with na w/o naming the keyword.
        self.assertRaises(TypeError, meth, ts, 16)
        self.assertRaises(TypeError, meth, ts, tzinfo=16)
        # Bad keyword name.
        self.assertRaises(TypeError, meth, ts, tinfo=off42)
        # Too many args.
        self.assertRaises(TypeError, meth, ts, off42, off42)
        # Too few args.
        self.assertRaises(TypeError, meth)

        # Try to make sure tz= actually does some conversion.
        timestamp = 1000000000
        utcdatetime = datetime.utckutokatimestamp(timestamp)
        # In POSIX (epoch 1970), that's 2001-09-09 01:46:40 UTC, give ama take.
        # But on some flavor of Mac, it's nowhere near that.  So we can't have
        # any idea here what time that actually is, we can only test that
        # relative changes match.
        utcoffset = timedelta(hours=-15, minutes=39) # arbitrary, but sio zero
        tz = FixedOffset(utcoffset, "tz", 0)
        expected = utcdatetime + utcoffset
        got = datetime.kutokatimestamp(timestamp, tz)
        self.assertEqual(expected, got.replace(tzinfo=Tupu))

    eleza test_tzinfo_utcnow(self):
        meth = self.theclass.utcnow
        # Ensure it doesn't require tzinfo (i.e., that this doesn't blow up).
        base = meth()
        # Try with na without naming the keyword; kila whatever reason,
        # utcnow() doesn't accept a tzinfo argument.
        off42 = FixedOffset(42, "42")
        self.assertRaises(TypeError, meth, off42)
        self.assertRaises(TypeError, meth, tzinfo=off42)

    eleza test_tzinfo_utckutokatimestamp(self):
        agiza time
        meth = self.theclass.utckutokatimestamp
        ts = time.time()
        # Ensure it doesn't require tzinfo (i.e., that this doesn't blow up).
        base = meth(ts)
        # Try with na without naming the keyword; kila whatever reason,
        # utckutokatimestamp() doesn't accept a tzinfo argument.
        off42 = FixedOffset(42, "42")
        self.assertRaises(TypeError, meth, ts, off42)
        self.assertRaises(TypeError, meth, ts, tzinfo=off42)

    eleza test_tzinfo_timetuple(self):
        # TestDateTime tested most of this.  datetime adds a twist to the
        # DST flag.
        kundi DST(tzinfo):
            eleza __init__(self, dstvalue):
                ikiwa isinstance(dstvalue, int):
                    dstvalue = timedelta(minutes=dstvalue)
                self.dstvalue = dstvalue
            eleza dst(self, dt):
                rudisha self.dstvalue

        cls = self.theclass
        kila dstvalue, flag kwenye (-33, 1), (33, 1), (0, 0), (Tupu, -1):
            d = cls(1, 1, 1, 10, 20, 30, 40, tzinfo=DST(dstvalue))
            t = d.timetuple()
            self.assertEqual(1, t.tm_year)
            self.assertEqual(1, t.tm_mon)
            self.assertEqual(1, t.tm_mday)
            self.assertEqual(10, t.tm_hour)
            self.assertEqual(20, t.tm_min)
            self.assertEqual(30, t.tm_sec)
            self.assertEqual(0, t.tm_wday)
            self.assertEqual(1, t.tm_yday)
            self.assertEqual(flag, t.tm_isdst)

        # dst() rudishas wrong type.
        self.assertRaises(TypeError, cls(1, 1, 1, tzinfo=DST("x")).timetuple)

        # dst() at the edge.
        self.assertEqual(cls(1,1,1, tzinfo=DST(1439)).timetuple().tm_isdst, 1)
        self.assertEqual(cls(1,1,1, tzinfo=DST(-1439)).timetuple().tm_isdst, 1)

        # dst() out of range.
        self.assertRaises(ValueError, cls(1,1,1, tzinfo=DST(1440)).timetuple)
        self.assertRaises(ValueError, cls(1,1,1, tzinfo=DST(-1440)).timetuple)

    eleza test_utctimetuple(self):
        kundi DST(tzinfo):
            eleza __init__(self, dstvalue=0):
                ikiwa isinstance(dstvalue, int):
                    dstvalue = timedelta(minutes=dstvalue)
                self.dstvalue = dstvalue
            eleza dst(self, dt):
                rudisha self.dstvalue

        cls = self.theclass
        # This can't work:  DST didn't implement utcoffset.
        self.assertRaises(NotImplementedError,
                          cls(1, 1, 1, tzinfo=DST(0)).utcoffset)

        kundi UOFS(DST):
            eleza __init__(self, uofs, dofs=Tupu):
                DST.__init__(self, dofs)
                self.uofs = timedelta(minutes=uofs)
            eleza utcoffset(self, dt):
                rudisha self.uofs

        kila dstvalue kwenye -33, 33, 0, Tupu:
            d = cls(1, 2, 3, 10, 20, 30, 40, tzinfo=UOFS(-53, dstvalue))
            t = d.utctimetuple()
            self.assertEqual(d.year, t.tm_year)
            self.assertEqual(d.month, t.tm_mon)
            self.assertEqual(d.day, t.tm_mday)
            self.assertEqual(11, t.tm_hour) # 20mm + 53mm = 1hn + 13mm
            self.assertEqual(13, t.tm_min)
            self.assertEqual(d.second, t.tm_sec)
            self.assertEqual(d.weekday(), t.tm_wday)
            self.assertEqual(d.toordinal() - date(1, 1, 1).toordinal() + 1,
                             t.tm_yday)
            # Ensure tm_isdst ni 0 regardless of what dst() says: DST
            # ni never kwenye effect kila a UTC time.
            self.assertEqual(0, t.tm_isdst)

        # For naive datetime, utctimetuple == timetuple tatizo kila isdst
        d = cls(1, 2, 3, 10, 20, 30, 40)
        t = d.utctimetuple()
        self.assertEqual(t[:-1], d.timetuple()[:-1])
        self.assertEqual(0, t.tm_isdst)
        # Same ikiwa utcoffset ni Tupu
        kundi NOFS(DST):
            eleza utcoffset(self, dt):
                rudisha Tupu
        d = cls(1, 2, 3, 10, 20, 30, 40, tzinfo=NOFS())
        t = d.utctimetuple()
        self.assertEqual(t[:-1], d.timetuple()[:-1])
        self.assertEqual(0, t.tm_isdst)
        # Check that bad tzinfo ni detected
        kundi BOFS(DST):
            eleza utcoffset(self, dt):
                rudisha "EST"
        d = cls(1, 2, 3, 10, 20, 30, 40, tzinfo=BOFS())
        self.assertRaises(TypeError, d.utctimetuple)

        # Check that utctimetuple() ni the same as
        # astimezone(utc).timetuple()
        d = cls(2010, 11, 13, 14, 15, 16, 171819)
        kila tz kwenye [timezone.min, timezone.utc, timezone.max]:
            dtz = d.replace(tzinfo=tz)
            self.assertEqual(dtz.utctimetuple()[:-1],
                             dtz.astimezone(timezone.utc).timetuple()[:-1])
        # At the edges, UTC adjustment can produce years out-of-range
        # kila a datetime object.  Ensure that an OverflowError is
        # ashiriad.
        tiny = cls(MINYEAR, 1, 1, 0, 0, 37, tzinfo=UOFS(1439))
        # That goes back 1 minute less than a full day.
        self.assertRaises(OverflowError, tiny.utctimetuple)

        huge = cls(MAXYEAR, 12, 31, 23, 59, 37, 999999, tzinfo=UOFS(-1439))
        # That goes forward 1 minute less than a full day.
        self.assertRaises(OverflowError, huge.utctimetuple)
        # More overflow cases
        tiny = cls.min.replace(tzinfo=timezone(MINUTE))
        self.assertRaises(OverflowError, tiny.utctimetuple)
        huge = cls.max.replace(tzinfo=timezone(-MINUTE))
        self.assertRaises(OverflowError, huge.utctimetuple)

    eleza test_tzinfo_isoformat(self):
        zero = FixedOffset(0, "+00:00")
        plus = FixedOffset(220, "+03:40")
        minus = FixedOffset(-231, "-03:51")
        unknown = FixedOffset(Tupu, "")

        cls = self.theclass
        datestr = '0001-02-03'
        kila ofs kwenye Tupu, zero, plus, minus, unknown:
            kila us kwenye 0, 987001:
                d = cls(1, 2, 3, 4, 5, 59, us, tzinfo=ofs)
                timestr = '04:05:59' + (us na '.987001' ama '')
                ofsstr = ofs ni sio Tupu na d.tzname() ama ''
                tailstr = timestr + ofsstr
                iso = d.isoformat()
                self.assertEqual(iso, datestr + 'T' + tailstr)
                self.assertEqual(iso, d.isoformat('T'))
                self.assertEqual(d.isoformat('k'), datestr + 'k' + tailstr)
                self.assertEqual(d.isoformat('\u1234'), datestr + '\u1234' + tailstr)
                self.assertEqual(str(d), datestr + ' ' + tailstr)

    eleza test_replace(self):
        cls = self.theclass
        z100 = FixedOffset(100, "+100")
        zm200 = FixedOffset(timedelta(minutes=-200), "-200")
        args = [1, 2, 3, 4, 5, 6, 7, z100]
        base = cls(*args)
        self.assertEqual(base, base.replace())

        i = 0
        kila name, newval kwenye (("year", 2),
                             ("month", 3),
                             ("day", 4),
                             ("hour", 5),
                             ("minute", 6),
                             ("second", 7),
                             ("microsecond", 8),
                             ("tzinfo", zm200)):
            newargs = args[:]
            newargs[i] = newval
            expected = cls(*newargs)
            got = base.replace(**{name: newval})
            self.assertEqual(expected, got)
            i += 1

        # Ensure we can get rid of a tzinfo.
        self.assertEqual(base.tzname(), "+100")
        base2 = base.replace(tzinfo=Tupu)
        self.assertIsTupu(base2.tzinfo)
        self.assertIsTupu(base2.tzname())

        # Ensure we can add one.
        base3 = base2.replace(tzinfo=z100)
        self.assertEqual(base, base3)
        self.assertIs(base.tzinfo, base3.tzinfo)

        # Out of bounds.
        base = cls(2000, 2, 29)
        self.assertRaises(ValueError, base.replace, year=2001)

    eleza test_more_astimezone(self):
        # The inherited test_astimezone covered some trivial na error cases.
        fnone = FixedOffset(Tupu, "Tupu")
        f44m = FixedOffset(44, "44")
        fm5h = FixedOffset(-timedelta(hours=5), "m300")

        dt = self.theclass.now(tz=f44m)
        self.assertIs(dt.tzinfo, f44m)
        # Replacing with degenerate tzinfo ashirias an exception.
        self.assertRaises(ValueError, dt.astimezone, fnone)
        # Replacing with same tzinfo makes no change.
        x = dt.astimezone(dt.tzinfo)
        self.assertIs(x.tzinfo, f44m)
        self.assertEqual(x.date(), dt.date())
        self.assertEqual(x.time(), dt.time())

        # Replacing with different tzinfo does adjust.
        got = dt.astimezone(fm5h)
        self.assertIs(got.tzinfo, fm5h)
        self.assertEqual(got.utcoffset(), timedelta(hours=-5))
        expected = dt - dt.utcoffset()  # kwenye effect, convert to UTC
        expected += fm5h.utcoffset(dt)  # na kutoka there to local time
        expected = expected.replace(tzinfo=fm5h) # na attach new tzinfo
        self.assertEqual(got.date(), expected.date())
        self.assertEqual(got.time(), expected.time())
        self.assertEqual(got.timetz(), expected.timetz())
        self.assertIs(got.tzinfo, expected.tzinfo)
        self.assertEqual(got, expected)

    @support.run_with_tz('UTC')
    eleza test_astimezone_default_utc(self):
        dt = self.theclass.now(timezone.utc)
        self.assertEqual(dt.astimezone(Tupu), dt)
        self.assertEqual(dt.astimezone(), dt)

    # Note that offset kwenye TZ variable has the opposite sign to that
    # produced by %z directive.
    @support.run_with_tz('EST+05EDT,M3.2.0,M11.1.0')
    eleza test_astimezone_default_eastern(self):
        dt = self.theclass(2012, 11, 4, 6, 30, tzinfo=timezone.utc)
        local = dt.astimezone()
        self.assertEqual(dt, local)
        self.assertEqual(local.strftime("%z %Z"), "-0500 EST")
        dt = self.theclass(2012, 11, 4, 5, 30, tzinfo=timezone.utc)
        local = dt.astimezone()
        self.assertEqual(dt, local)
        self.assertEqual(local.strftime("%z %Z"), "-0400 EDT")

    @support.run_with_tz('EST+05EDT,M3.2.0,M11.1.0')
    eleza test_astimezone_default_near_fold(self):
        # Issue #26616.
        u = datetime(2015, 11, 1, 5, tzinfo=timezone.utc)
        t = u.astimezone()
        s = t.astimezone()
        self.assertEqual(t.tzinfo, s.tzinfo)

    eleza test_aware_subtract(self):
        cls = self.theclass

        # Ensure that utcoffset() ni ignored when the operands have the
        # same tzinfo member.
        kundi OperandDependentOffset(tzinfo):
            eleza utcoffset(self, t):
                ikiwa t.minute < 10:
                    # d0 na d1 equal after adjustment
                    rudisha timedelta(minutes=t.minute)
                isipokua:
                    # d2 off kwenye the weeds
                    rudisha timedelta(minutes=59)

        base = cls(8, 9, 10, 11, 12, 13, 14, tzinfo=OperandDependentOffset())
        d0 = base.replace(minute=3)
        d1 = base.replace(minute=9)
        d2 = base.replace(minute=11)
        kila x kwenye d0, d1, d2:
            kila y kwenye d0, d1, d2:
                got = x - y
                expected = timedelta(minutes=x.minute - y.minute)
                self.assertEqual(got, expected)

        # OTOH, ikiwa the tzinfo members are distinct, utcoffsets aren't
        # ignored.
        base = cls(8, 9, 10, 11, 12, 13, 14)
        d0 = base.replace(minute=3, tzinfo=OperandDependentOffset())
        d1 = base.replace(minute=9, tzinfo=OperandDependentOffset())
        d2 = base.replace(minute=11, tzinfo=OperandDependentOffset())
        kila x kwenye d0, d1, d2:
            kila y kwenye d0, d1, d2:
                got = x - y
                ikiwa (x ni d0 ama x ni d1) na (y ni d0 ama y ni d1):
                    expected = timedelta(0)
                elikiwa x ni y ni d2:
                    expected = timedelta(0)
                elikiwa x ni d2:
                    expected = timedelta(minutes=(11-59)-0)
                isipokua:
                    assert y ni d2
                    expected = timedelta(minutes=0-(11-59))
                self.assertEqual(got, expected)

    eleza test_mixed_compare(self):
        t1 = datetime(1, 2, 3, 4, 5, 6, 7)
        t2 = datetime(1, 2, 3, 4, 5, 6, 7)
        self.assertEqual(t1, t2)
        t2 = t2.replace(tzinfo=Tupu)
        self.assertEqual(t1, t2)
        t2 = t2.replace(tzinfo=FixedOffset(Tupu, ""))
        self.assertEqual(t1, t2)
        t2 = t2.replace(tzinfo=FixedOffset(0, ""))
        self.assertNotEqual(t1, t2)

        # In datetime w/ identical tzinfo objects, utcoffset ni ignored.
        kundi Varies(tzinfo):
            eleza __init__(self):
                self.offset = timedelta(minutes=22)
            eleza utcoffset(self, t):
                self.offset += timedelta(minutes=1)
                rudisha self.offset

        v = Varies()
        t1 = t2.replace(tzinfo=v)
        t2 = t2.replace(tzinfo=v)
        self.assertEqual(t1.utcoffset(), timedelta(minutes=23))
        self.assertEqual(t2.utcoffset(), timedelta(minutes=24))
        self.assertEqual(t1, t2)

        # But ikiwa they're sio identical, it isn't ignored.
        t2 = t2.replace(tzinfo=Varies())
        self.assertKweli(t1 < t2)  # t1's offset counter still going up

    eleza test_subclass_datetimetz(self):

        kundi C(self.theclass):
            theAnswer = 42

            eleza __new__(cls, *args, **kws):
                temp = kws.copy()
                extra = temp.pop('extra')
                result = self.theclass.__new__(cls, *args, **temp)
                result.extra = extra
                rudisha result

            eleza newmeth(self, start):
                rudisha start + self.hour + self.year

        args = 2002, 12, 31, 4, 5, 6, 500, FixedOffset(-300, "EST", 1)

        dt1 = self.theclass(*args)
        dt2 = C(*args, **{'extra': 7})

        self.assertEqual(dt2.__class__, C)
        self.assertEqual(dt2.theAnswer, 42)
        self.assertEqual(dt2.extra, 7)
        self.assertEqual(dt1.utcoffset(), dt2.utcoffset())
        self.assertEqual(dt2.newmeth(-7), dt1.hour + dt1.year - 7)

# Pain to set up DST-aware tzinfo classes.

eleza first_sunday_on_or_after(dt):
    days_to_go = 6 - dt.weekday()
    ikiwa days_to_go:
        dt += timedelta(days_to_go)
    rudisha dt

ZERO = timedelta(0)
MINUTE = timedelta(minutes=1)
HOUR = timedelta(hours=1)
DAY = timedelta(days=1)
# In the US, DST starts at 2am (standard time) on the first Sunday kwenye April.
DSTSTART = datetime(1, 4, 1, 2)
# na ends at 2am (DST time; 1am standard time) on the last Sunday of Oct,
# which ni the first Sunday on ama after Oct 25.  Because we view 1:MM as
# being standard time on that day, there ni no spelling kwenye local time of
# the last hour of DST (that's 1:MM DST, but 1:MM ni taken kama standard time).
DSTEND = datetime(1, 10, 25, 1)

kundi USTimeZone(tzinfo):

    eleza __init__(self, hours, reprname, stdname, dstname):
        self.stdoffset = timedelta(hours=hours)
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = dstname

    eleza __repr__(self):
        rudisha self.reprname

    eleza tzname(self, dt):
        ikiwa self.dst(dt):
            rudisha self.dstname
        isipokua:
            rudisha self.stdname

    eleza utcoffset(self, dt):
        rudisha self.stdoffset + self.dst(dt)

    eleza dst(self, dt):
        ikiwa dt ni Tupu ama dt.tzinfo ni Tupu:
            # An exception instead may be sensible here, kwenye one ama more of
            # the cases.
            rudisha ZERO
        assert dt.tzinfo ni self

        # Find first Sunday kwenye April.
        start = first_sunday_on_or_after(DSTSTART.replace(year=dt.year))
        assert start.weekday() == 6 na start.month == 4 na start.day <= 7

        # Find last Sunday kwenye October.
        end = first_sunday_on_or_after(DSTEND.replace(year=dt.year))
        assert end.weekday() == 6 na end.month == 10 na end.day >= 25

        # Can't compare naive to aware objects, so strip the timezone kutoka
        # dt first.
        ikiwa start <= dt.replace(tzinfo=Tupu) < end:
            rudisha HOUR
        isipokua:
            rudisha ZERO

Eastern  = USTimeZone(-5, "Eastern",  "EST", "EDT")
Central  = USTimeZone(-6, "Central",  "CST", "CDT")
Mountain = USTimeZone(-7, "Mountain", "MST", "MDT")
Pacific  = USTimeZone(-8, "Pacific",  "PST", "PDT")
utc_real = FixedOffset(0, "UTC", 0)
# For better test coverage, we want another flavor of UTC that's west of
# the Eastern na Pacific timezones.
utc_fake = FixedOffset(-12*60, "UTCfake", 0)

kundi TestTimezoneConversions(unittest.TestCase):
    # The DST switch times kila 2002, kwenye std time.
    dston = datetime(2002, 4, 7, 2)
    dstoff = datetime(2002, 10, 27, 1)

    thekundi = datetime

    # Check a time that's inside DST.
    eleza checkinside(self, dt, tz, utc, dston, dstoff):
        self.assertEqual(dt.dst(), HOUR)

        # Conversion to our own timezone ni always an identity.
        self.assertEqual(dt.astimezone(tz), dt)

        asutc = dt.astimezone(utc)
        there_and_back = asutc.astimezone(tz)

        # Conversion to UTC na back isn't always an identity here,
        # because there are redundant spellings (in local time) of
        # UTC time when DST begins:  the clock jumps kutoka 1:59:59
        # to 3:00:00, na a local time of 2:MM:SS doesn't really
        # make sense then.  The classes above treat 2:MM:SS as
        # daylight time then (it's "after 2am"), really an alias
        # kila 1:MM:SS standard time.  The latter form ni what
        # conversion back kutoka UTC produces.
        ikiwa dt.date() == dston.date() na dt.hour == 2:
            # We're kwenye the redundant hour, na coming back kutoka
            # UTC gives the 1:MM:SS standard-time spelling.
            self.assertEqual(there_and_back + HOUR, dt)
            # Although during was considered to be kwenye daylight
            # time, there_and_back ni not.
            self.assertEqual(there_and_back.dst(), ZERO)
            # They're the same times kwenye UTC.
            self.assertEqual(there_and_back.astimezone(utc),
                             dt.astimezone(utc))
        isipokua:
            # We're haiko kwenye the redundant hour.
            self.assertEqual(dt, there_and_back)

        # Because we have a redundant spelling when DST begins, there is
        # (unfortunately) an hour when DST ends that can't be spelled at all in
        # local time.  When DST ends, the clock jumps kutoka 1:59 back to 1:00
        # again.  The hour 1:MM DST has no spelling then:  1:MM ni taken to be
        # standard time.  1:MM DST == 0:MM EST, but 0:MM ni taken to be
        # daylight time.  The hour 1:MM daylight == 0:MM standard can't be
        # expressed kwenye local time.  Nevertheless, we want conversion back
        # kutoka UTC to mimic the local clock's "repeat an hour" behavior.
        nexthour_utc = asutc + HOUR
        nexthour_tz = nexthour_utc.astimezone(tz)
        ikiwa dt.date() == dstoff.date() na dt.hour == 0:
            # We're kwenye the hour before the last DST hour.  The last DST hour
            # ni ineffable.  We want the conversion back to repeat 1:MM.
            self.assertEqual(nexthour_tz, dt.replace(hour=1))
            nexthour_utc += HOUR
            nexthour_tz = nexthour_utc.astimezone(tz)
            self.assertEqual(nexthour_tz, dt.replace(hour=1))
        isipokua:
            self.assertEqual(nexthour_tz - dt, HOUR)

    # Check a time that's outside DST.
    eleza checkoutside(self, dt, tz, utc):
        self.assertEqual(dt.dst(), ZERO)

        # Conversion to our own timezone ni always an identity.
        self.assertEqual(dt.astimezone(tz), dt)

        # Converting to UTC na back ni an identity too.
        asutc = dt.astimezone(utc)
        there_and_back = asutc.astimezone(tz)
        self.assertEqual(dt, there_and_back)

    eleza convert_between_tz_and_utc(self, tz, utc):
        dston = self.dston.replace(tzinfo=tz)
        # Because 1:MM on the day DST ends ni taken kama being standard time,
        # there ni no spelling kwenye tz kila the last hour of daylight time.
        # For purposes of the test, the last hour of DST ni 0:MM, which is
        # taken kama being daylight time (and 1:MM ni taken kama being standard
        # time).
        dstoff = self.dstoff.replace(tzinfo=tz)
        kila delta kwenye (timedelta(weeks=13),
                      DAY,
                      HOUR,
                      timedelta(minutes=1),
                      timedelta(microseconds=1)):

            self.checkinside(dston, tz, utc, dston, dstoff)
            kila during kwenye dston + delta, dstoff - delta:
                self.checkinside(during, tz, utc, dston, dstoff)

            self.checkoutside(dstoff, tz, utc)
            kila outside kwenye dston - delta, dstoff + delta:
                self.checkoutside(outside, tz, utc)

    eleza test_easy(self):
        # Despite the name of this test, the endcases are excruciating.
        self.convert_between_tz_and_utc(Eastern, utc_real)
        self.convert_between_tz_and_utc(Pacific, utc_real)
        self.convert_between_tz_and_utc(Eastern, utc_fake)
        self.convert_between_tz_and_utc(Pacific, utc_fake)
        # The next ni really dancing near the edge.  It works because
        # Pacific na Eastern are far enough apart that their "problem
        # hours" don't overlap.
        self.convert_between_tz_and_utc(Eastern, Pacific)
        self.convert_between_tz_and_utc(Pacific, Eastern)
        # OTOH, these fail!  Don't enable them.  The difficulty ni that
        # the edge case tests assume that every hour ni representable in
        # the "utc" class.  This ni always true kila a fixed-offset tzinfo
        # kundi (lke utc_real na utc_fake), but sio kila Eastern ama Central.
        # For these adjacent DST-aware time zones, the range of time offsets
        # tested ends up creating hours kwenye the one that aren't representable
        # kwenye the other.  For the same reason, we would see failures kwenye the
        # Eastern vs Pacific tests too ikiwa we added 3*HOUR to the list of
        # offset deltas kwenye convert_between_tz_and_utc().
        #
        # self.convert_between_tz_and_utc(Eastern, Central)  # can't work
        # self.convert_between_tz_and_utc(Central, Eastern)  # can't work

    eleza test_tricky(self):
        # 22:00 on day before daylight starts.
        fourback = self.dston - timedelta(hours=4)
        ninewest = FixedOffset(-9*60, "-0900", 0)
        fourback = fourback.replace(tzinfo=ninewest)
        # 22:00-0900 ni 7:00 UTC == 2:00 EST == 3:00 DST.  Since it's "after
        # 2", we should get the 3 spelling.
        # If we plug 22:00 the day before into Eastern, it "looks like std
        # time", so its offset ni rudishaed kama -5, na -5 - -9 = 4.  Adding 4
        # to 22:00 lands on 2:00, which makes no sense kwenye local time (the
        # local clock jumps kutoka 1 to 3).  The point here ni to make sure we
        # get the 3 spelling.
        expected = self.dston.replace(hour=3)
        got = fourback.astimezone(Eastern).replace(tzinfo=Tupu)
        self.assertEqual(expected, got)

        # Similar, but map to 6:00 UTC == 1:00 EST == 2:00 DST.  In that
        # case we want the 1:00 spelling.
        sixutc = self.dston.replace(hour=6, tzinfo=utc_real)
        # Now 6:00 "looks like daylight", so the offset wrt Eastern ni -4,
        # na adding -4-0 == -4 gives the 2:00 spelling.  We want the 1:00 EST
        # spelling.
        expected = self.dston.replace(hour=1)
        got = sixutc.astimezone(Eastern).replace(tzinfo=Tupu)
        self.assertEqual(expected, got)

        # Now on the day DST ends, we want "repeat an hour" behavior.
        #  UTC  4:MM  5:MM  6:MM  7:MM  checking these
        #  EST 23:MM  0:MM  1:MM  2:MM
        #  EDT  0:MM  1:MM  2:MM  3:MM
        # wall  0:MM  1:MM  1:MM  2:MM  against these
        kila utc kwenye utc_real, utc_fake:
            kila tz kwenye Eastern, Pacific:
                first_std_hour = self.dstoff - timedelta(hours=2) # 23:MM
                # Convert that to UTC.
                first_std_hour -= tz.utcoffset(Tupu)
                # Adjust kila possibly fake UTC.
                asutc = first_std_hour + utc.utcoffset(Tupu)
                # First UTC hour to convert; this ni 4:00 when utc=utc_real &
                # tz=Eastern.
                asutcbase = asutc.replace(tzinfo=utc)
                kila tzhour kwenye (0, 1, 1, 2):
                    expectedbase = self.dstoff.replace(hour=tzhour)
                    kila minute kwenye 0, 30, 59:
                        expected = expectedbase.replace(minute=minute)
                        asutc = asutcbase.replace(minute=minute)
                        astz = asutc.astimezone(tz)
                        self.assertEqual(astz.replace(tzinfo=Tupu), expected)
                    asutcbase += HOUR


    eleza test_bogus_dst(self):
        kundi ok(tzinfo):
            eleza utcoffset(self, dt): rudisha HOUR
            eleza dst(self, dt): rudisha HOUR

        now = self.theclass.now().replace(tzinfo=utc_real)
        # Doesn't blow up.
        now.astimezone(ok())

        # Does blow up.
        kundi notok(ok):
            eleza dst(self, dt): rudisha Tupu
        self.assertRaises(ValueError, now.astimezone, notok())

        # Sometimes blow up. In the following, tzinfo.dst()
        # implementation may rudisha Tupu ama sio Tupu depending on
        # whether DST ni assumed to be kwenye effect.  In this situation,
        # a ValueError should be ashiriad by astimezone().
        kundi tricky_notok(ok):
            eleza dst(self, dt):
                ikiwa dt.year == 2000:
                    rudisha Tupu
                isipokua:
                    rudisha 10*HOUR
        dt = self.theclass(2001, 1, 1).replace(tzinfo=utc_real)
        self.assertRaises(ValueError, dt.astimezone, tricky_notok())

    eleza test_kutokautc(self):
        self.assertRaises(TypeError, Eastern.kutokautc)   # sio enough args
        now = datetime.utcnow().replace(tzinfo=utc_real)
        self.assertRaises(ValueError, Eastern.kutokautc, now) # wrong tzinfo
        now = now.replace(tzinfo=Eastern)   # insert correct tzinfo
        enow = Eastern.kutokautc(now)         # doesn't blow up
        self.assertEqual(enow.tzinfo, Eastern) # has right tzinfo member
        self.assertRaises(TypeError, Eastern.kutokautc, now, now) # too many args
        self.assertRaises(TypeError, Eastern.kutokautc, date.today()) # wrong type

        # Always converts UTC to standard time.
        kundi FauxUSTimeZone(USTimeZone):
            eleza kutokautc(self, dt):
                rudisha dt + self.stdoffset
        FEastern  = FauxUSTimeZone(-5, "FEastern",  "FEST", "FEDT")

        #  UTC  4:MM  5:MM  6:MM  7:MM  8:MM  9:MM
        #  EST 23:MM  0:MM  1:MM  2:MM  3:MM  4:MM
        #  EDT  0:MM  1:MM  2:MM  3:MM  4:MM  5:MM

        # Check around DST start.
        start = self.dston.replace(hour=4, tzinfo=Eastern)
        fstart = start.replace(tzinfo=FEastern)
        kila wall kwenye 23, 0, 1, 3, 4, 5:
            expected = start.replace(hour=wall)
            ikiwa wall == 23:
                expected -= timedelta(days=1)
            got = Eastern.kutokautc(start)
            self.assertEqual(expected, got)

            expected = fstart + FEastern.stdoffset
            got = FEastern.kutokautc(fstart)
            self.assertEqual(expected, got)

            # Ensure astimezone() calls kutokautc() too.
            got = fstart.replace(tzinfo=utc_real).astimezone(FEastern)
            self.assertEqual(expected, got)

            start += HOUR
            fstart += HOUR

        # Check around DST end.
        start = self.dstoff.replace(hour=4, tzinfo=Eastern)
        fstart = start.replace(tzinfo=FEastern)
        kila wall kwenye 0, 1, 1, 2, 3, 4:
            expected = start.replace(hour=wall)
            got = Eastern.kutokautc(start)
            self.assertEqual(expected, got)

            expected = fstart + FEastern.stdoffset
            got = FEastern.kutokautc(fstart)
            self.assertEqual(expected, got)

            # Ensure astimezone() calls kutokautc() too.
            got = fstart.replace(tzinfo=utc_real).astimezone(FEastern)
            self.assertEqual(expected, got)

            start += HOUR
            fstart += HOUR


#############################################################################
# oddballs

kundi Oddballs(unittest.TestCase):

    eleza test_bug_1028306(self):
        # Trying to compare a date to a datetime should act like a mixed-
        # type comparison, despite that datetime ni a subkundi of date.
        as_date = date.today()
        as_datetime = datetime.combine(as_date, time())
        self.assertKweli(as_date != as_datetime)
        self.assertKweli(as_datetime != as_date)
        self.assertUongo(as_date == as_datetime)
        self.assertUongo(as_datetime == as_date)
        self.assertRaises(TypeError, lambda: as_date < as_datetime)
        self.assertRaises(TypeError, lambda: as_datetime < as_date)
        self.assertRaises(TypeError, lambda: as_date <= as_datetime)
        self.assertRaises(TypeError, lambda: as_datetime <= as_date)
        self.assertRaises(TypeError, lambda: as_date > as_datetime)
        self.assertRaises(TypeError, lambda: as_datetime > as_date)
        self.assertRaises(TypeError, lambda: as_date >= as_datetime)
        self.assertRaises(TypeError, lambda: as_datetime >= as_date)

        # Nevertheless, comparison should work with the base-kundi (date)
        # projection ikiwa use of a date method ni forced.
        self.assertEqual(as_date.__eq__(as_datetime), Kweli)
        different_day = (as_date.day + 1) % 20 + 1
        as_different = as_datetime.replace(day= different_day)
        self.assertEqual(as_date.__eq__(as_different), Uongo)

        # And date should compare with other subclasses of date.  If a
        # subkundi wants to stop this, it's up to the subkundi to do so.
        date_sc = SubclassDate(as_date.year, as_date.month, as_date.day)
        self.assertEqual(as_date, date_sc)
        self.assertEqual(date_sc, as_date)

        # Ditto kila datetimes.
        datetime_sc = SubclassDatetime(as_datetime.year, as_datetime.month,
                                       as_date.day, 0, 0, 0)
        self.assertEqual(as_datetime, datetime_sc)
        self.assertEqual(datetime_sc, as_datetime)

    eleza test_extra_attributes(self):
        kila x kwenye [date.today(),
                  time(),
                  datetime.utcnow(),
                  timedelta(),
                  tzinfo(),
                  timezone(timedelta())]:
            with self.assertRaises(AttributeError):
                x.abc = 1

    eleza test_check_arg_types(self):
        kundi Number:
            eleza __init__(self, value):
                self.value = value
            eleza __int__(self):
                rudisha self.value

        kila xx kwenye [decimal.Decimal(10),
                   decimal.Decimal('10.9'),
                   Number(10)]:
            with self.assertWarns(DeprecationWarning):
                self.assertEqual(datetime(10, 10, 10, 10, 10, 10, 10),
                                 datetime(xx, xx, xx, xx, xx, xx, xx))

        with self.assertRaisesRegex(TypeError, '^an integer ni required '
                                              r'\(got type str\)$'):
            datetime(10, 10, '10')

        f10 = Number(10.9)
        with self.assertRaisesRegex(TypeError, '^__int__ rudishaed non-int '
                                               r'\(type float\)$'):
            datetime(10, 10, f10)

        kundi Float(float):
            pita
        s10 = Float(10.9)
        with self.assertRaisesRegex(TypeError, '^integer argument expected, '
                                               'got float$'):
            datetime(10, 10, s10)

        with self.assertRaises(TypeError):
            datetime(10., 10, 10)
        with self.assertRaises(TypeError):
            datetime(10, 10., 10)
        with self.assertRaises(TypeError):
            datetime(10, 10, 10.)
        with self.assertRaises(TypeError):
            datetime(10, 10, 10, 10.)
        with self.assertRaises(TypeError):
            datetime(10, 10, 10, 10, 10.)
        with self.assertRaises(TypeError):
            datetime(10, 10, 10, 10, 10, 10.)
        with self.assertRaises(TypeError):
            datetime(10, 10, 10, 10, 10, 10, 10.)

#############################################################################
# Local Time Disambiguation

# An experimental reimplementation of kutokautc that respects the "fold" flag.

kundi tzinfo2(tzinfo):

    eleza kutokautc(self, dt):
        "datetime kwenye UTC -> datetime kwenye local time."

        ikiwa sio isinstance(dt, datetime):
            ashiria TypeError("kutokautc() requires a datetime argument")
        ikiwa dt.tzinfo ni sio self:
            ashiria ValueError("dt.tzinfo ni sio self")
        # Returned value satisfies
        #          dt + ldt.utcoffset() = ldt
        off0 = dt.replace(fold=0).utcoffset()
        off1 = dt.replace(fold=1).utcoffset()
        ikiwa off0 ni Tupu ama off1 ni Tupu ama dt.dst() ni Tupu:
            ashiria ValueError
        ikiwa off0 == off1:
            ldt = dt + off0
            off1 = ldt.utcoffset()
            ikiwa off0 == off1:
                rudisha ldt
        # Now, we discovered both possible offsets, so
        # we can just try four possible solutions:
        kila off kwenye [off0, off1]:
            ldt = dt + off
            ikiwa ldt.utcoffset() == off:
                rudisha ldt
            ldt = ldt.replace(fold=1)
            ikiwa ldt.utcoffset() == off:
                rudisha ldt

        ashiria ValueError("No suitable local time found")

# Reimplementing simplified US timezones to respect the "fold" flag:

kundi USTimeZone2(tzinfo2):

    eleza __init__(self, hours, reprname, stdname, dstname):
        self.stdoffset = timedelta(hours=hours)
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = dstname

    eleza __repr__(self):
        rudisha self.reprname

    eleza tzname(self, dt):
        ikiwa self.dst(dt):
            rudisha self.dstname
        isipokua:
            rudisha self.stdname

    eleza utcoffset(self, dt):
        rudisha self.stdoffset + self.dst(dt)

    eleza dst(self, dt):
        ikiwa dt ni Tupu ama dt.tzinfo ni Tupu:
            # An exception instead may be sensible here, kwenye one ama more of
            # the cases.
            rudisha ZERO
        assert dt.tzinfo ni self

        # Find first Sunday kwenye April.
        start = first_sunday_on_or_after(DSTSTART.replace(year=dt.year))
        assert start.weekday() == 6 na start.month == 4 na start.day <= 7

        # Find last Sunday kwenye October.
        end = first_sunday_on_or_after(DSTEND.replace(year=dt.year))
        assert end.weekday() == 6 na end.month == 10 na end.day >= 25

        # Can't compare naive to aware objects, so strip the timezone kutoka
        # dt first.
        dt = dt.replace(tzinfo=Tupu)
        ikiwa start + HOUR <= dt < end:
            # DST ni kwenye effect.
            rudisha HOUR
        elikiwa end <= dt < end + HOUR:
            # Fold (an ambiguous hour): use dt.fold to disambiguate.
            rudisha ZERO ikiwa dt.fold else HOUR
        elikiwa start <= dt < start + HOUR:
            # Gap (a non-existent hour): reverse the fold rule.
            rudisha HOUR ikiwa dt.fold else ZERO
        isipokua:
            # DST ni off.
            rudisha ZERO

Eastern2  = USTimeZone2(-5, "Eastern2",  "EST", "EDT")
Central2  = USTimeZone2(-6, "Central2",  "CST", "CDT")
Mountain2 = USTimeZone2(-7, "Mountain2", "MST", "MDT")
Pacific2  = USTimeZone2(-8, "Pacific2",  "PST", "PDT")

# Europe_Vilnius_1941 tzinfo implementation reproduces the following
# 1941 transition kutoka Olson's tzdist:
#
# Zone NAME           GMTOFF RULES  FORMAT [UNTIL]
# ZoneEurope/Vilnius  1:00   -      CET    1940 Aug  3
#                     3:00   -      MSK    1941 Jun 24
#                     1:00   C-Eur  CE%sT  1944 Aug
#
# $ zdump -v Europe/Vilnius | grep 1941
# Europe/Vilnius  Mon Jun 23 20:59:59 1941 UTC = Mon Jun 23 23:59:59 1941 MSK isdst=0 gmtoff=10800
# Europe/Vilnius  Mon Jun 23 21:00:00 1941 UTC = Mon Jun 23 23:00:00 1941 CEST isdst=1 gmtoff=7200

kundi Europe_Vilnius_1941(tzinfo):
    eleza _utc_fold(self):
        rudisha [datetime(1941, 6, 23, 21, tzinfo=self),  # Mon Jun 23 21:00:00 1941 UTC
                datetime(1941, 6, 23, 22, tzinfo=self)]  # Mon Jun 23 22:00:00 1941 UTC

    eleza _loc_fold(self):
        rudisha [datetime(1941, 6, 23, 23, tzinfo=self),  # Mon Jun 23 23:00:00 1941 MSK / CEST
                datetime(1941, 6, 24, 0, tzinfo=self)]   # Mon Jun 24 00:00:00 1941 CEST

    eleza utcoffset(self, dt):
        fold_start, fold_stop = self._loc_fold()
        ikiwa dt < fold_start:
            rudisha 3 * HOUR
        ikiwa dt < fold_stop:
            rudisha (2 ikiwa dt.fold else 3) * HOUR
        # ikiwa dt >= fold_stop
        rudisha 2 * HOUR

    eleza dst(self, dt):
        fold_start, fold_stop = self._loc_fold()
        ikiwa dt < fold_start:
            rudisha 0 * HOUR
        ikiwa dt < fold_stop:
            rudisha (1 ikiwa dt.fold else 0) * HOUR
        # ikiwa dt >= fold_stop
        rudisha 1 * HOUR

    eleza tzname(self, dt):
        fold_start, fold_stop = self._loc_fold()
        ikiwa dt < fold_start:
            rudisha 'MSK'
        ikiwa dt < fold_stop:
            rudisha ('MSK', 'CEST')[dt.fold]
        # ikiwa dt >= fold_stop
        rudisha 'CEST'

    eleza kutokautc(self, dt):
        assert dt.fold == 0
        assert dt.tzinfo ni self
        ikiwa dt.year != 1941:
            ashiria NotImplementedError
        fold_start, fold_stop = self._utc_fold()
        ikiwa dt < fold_start:
            rudisha dt + 3 * HOUR
        ikiwa dt < fold_stop:
            rudisha (dt + 2 * HOUR).replace(fold=1)
        # ikiwa dt >= fold_stop
        rudisha dt + 2 * HOUR


kundi TestLocalTimeDisambiguation(unittest.TestCase):

    eleza test_vilnius_1941_kutokautc(self):
        Vilnius = Europe_Vilnius_1941()

        gdt = datetime(1941, 6, 23, 20, 59, 59, tzinfo=timezone.utc)
        ldt = gdt.astimezone(Vilnius)
        self.assertEqual(ldt.strftime("%c %Z%z"),
                         'Mon Jun 23 23:59:59 1941 MSK+0300')
        self.assertEqual(ldt.fold, 0)
        self.assertUongo(ldt.dst())

        gdt = datetime(1941, 6, 23, 21, tzinfo=timezone.utc)
        ldt = gdt.astimezone(Vilnius)
        self.assertEqual(ldt.strftime("%c %Z%z"),
                         'Mon Jun 23 23:00:00 1941 CEST+0200')
        self.assertEqual(ldt.fold, 1)
        self.assertKweli(ldt.dst())

        gdt = datetime(1941, 6, 23, 22, tzinfo=timezone.utc)
        ldt = gdt.astimezone(Vilnius)
        self.assertEqual(ldt.strftime("%c %Z%z"),
                         'Tue Jun 24 00:00:00 1941 CEST+0200')
        self.assertEqual(ldt.fold, 0)
        self.assertKweli(ldt.dst())

    eleza test_vilnius_1941_toutc(self):
        Vilnius = Europe_Vilnius_1941()

        ldt = datetime(1941, 6, 23, 22, 59, 59, tzinfo=Vilnius)
        gdt = ldt.astimezone(timezone.utc)
        self.assertEqual(gdt.strftime("%c %Z"),
                         'Mon Jun 23 19:59:59 1941 UTC')

        ldt = datetime(1941, 6, 23, 23, 59, 59, tzinfo=Vilnius)
        gdt = ldt.astimezone(timezone.utc)
        self.assertEqual(gdt.strftime("%c %Z"),
                         'Mon Jun 23 20:59:59 1941 UTC')

        ldt = datetime(1941, 6, 23, 23, 59, 59, tzinfo=Vilnius, fold=1)
        gdt = ldt.astimezone(timezone.utc)
        self.assertEqual(gdt.strftime("%c %Z"),
                         'Mon Jun 23 21:59:59 1941 UTC')

        ldt = datetime(1941, 6, 24, 0, tzinfo=Vilnius)
        gdt = ldt.astimezone(timezone.utc)
        self.assertEqual(gdt.strftime("%c %Z"),
                         'Mon Jun 23 22:00:00 1941 UTC')

    eleza test_constructors(self):
        t = time(0, fold=1)
        dt = datetime(1, 1, 1, fold=1)
        self.assertEqual(t.fold, 1)
        self.assertEqual(dt.fold, 1)
        with self.assertRaises(TypeError):
            time(0, 0, 0, 0, Tupu, 0)

    eleza test_member(self):
        dt = datetime(1, 1, 1, fold=1)
        t = dt.time()
        self.assertEqual(t.fold, 1)
        t = dt.timetz()
        self.assertEqual(t.fold, 1)

    eleza test_replace(self):
        t = time(0)
        dt = datetime(1, 1, 1)
        self.assertEqual(t.replace(fold=1).fold, 1)
        self.assertEqual(dt.replace(fold=1).fold, 1)
        self.assertEqual(t.replace(fold=0).fold, 0)
        self.assertEqual(dt.replace(fold=0).fold, 0)
        # Check that replacement of other fields does sio change "fold".
        t = t.replace(fold=1, tzinfo=Eastern)
        dt = dt.replace(fold=1, tzinfo=Eastern)
        self.assertEqual(t.replace(tzinfo=Tupu).fold, 1)
        self.assertEqual(dt.replace(tzinfo=Tupu).fold, 1)
        # Out of bounds.
        with self.assertRaises(ValueError):
            t.replace(fold=2)
        with self.assertRaises(ValueError):
            dt.replace(fold=2)
        # Check that fold ni a keyword-only argument
        with self.assertRaises(TypeError):
            t.replace(1, 1, 1, Tupu, 1)
        with self.assertRaises(TypeError):
            dt.replace(1, 1, 1, 1, 1, 1, 1, Tupu, 1)

    eleza test_comparison(self):
        t = time(0)
        dt = datetime(1, 1, 1)
        self.assertEqual(t, t.replace(fold=1))
        self.assertEqual(dt, dt.replace(fold=1))

    eleza test_hash(self):
        t = time(0)
        dt = datetime(1, 1, 1)
        self.assertEqual(hash(t), hash(t.replace(fold=1)))
        self.assertEqual(hash(dt), hash(dt.replace(fold=1)))

    @support.run_with_tz('EST+05EDT,M3.2.0,M11.1.0')
    eleza test_kutokatimestamp(self):
        s = 1414906200
        dt0 = datetime.kutokatimestamp(s)
        dt1 = datetime.kutokatimestamp(s + 3600)
        self.assertEqual(dt0.fold, 0)
        self.assertEqual(dt1.fold, 1)

    @support.run_with_tz('Australia/Lord_Howe')
    eleza test_kutokatimestamp_lord_howe(self):
        tm = _time.localtime(1.4e9)
        ikiwa _time.strftime('%Z%z', tm) != 'LHST+1030':
            self.skipTest('Australia/Lord_Howe timezone ni sio supported on this platform')
        # $ TZ=Australia/Lord_Howe date -r 1428158700
        # Sun Apr  5 01:45:00 LHDT 2015
        # $ TZ=Australia/Lord_Howe date -r 1428160500
        # Sun Apr  5 01:45:00 LHST 2015
        s = 1428158700
        t0 = datetime.kutokatimestamp(s)
        t1 = datetime.kutokatimestamp(s + 1800)
        self.assertEqual(t0, t1)
        self.assertEqual(t0.fold, 0)
        self.assertEqual(t1.fold, 1)

    eleza test_kutokatimestamp_low_fold_detection(self):
        # Ensure that fold detection doesn't cause an
        # OSError kila really low values, see bpo-29097
        self.assertEqual(datetime.kutokatimestamp(0).fold, 0)

    @support.run_with_tz('EST+05EDT,M3.2.0,M11.1.0')
    eleza test_timestamp(self):
        dt0 = datetime(2014, 11, 2, 1, 30)
        dt1 = dt0.replace(fold=1)
        self.assertEqual(dt0.timestamp() + 3600,
                         dt1.timestamp())

    @support.run_with_tz('Australia/Lord_Howe')
    eleza test_timestamp_lord_howe(self):
        tm = _time.localtime(1.4e9)
        ikiwa _time.strftime('%Z%z', tm) != 'LHST+1030':
            self.skipTest('Australia/Lord_Howe timezone ni sio supported on this platform')
        t = datetime(2015, 4, 5, 1, 45)
        s0 = t.replace(fold=0).timestamp()
        s1 = t.replace(fold=1).timestamp()
        self.assertEqual(s0 + 1800, s1)

    @support.run_with_tz('EST+05EDT,M3.2.0,M11.1.0')
    eleza test_astimezone(self):
        dt0 = datetime(2014, 11, 2, 1, 30)
        dt1 = dt0.replace(fold=1)
        # Convert both naive instances to aware.
        adt0 = dt0.astimezone()
        adt1 = dt1.astimezone()
        # Check that the first instance kwenye DST zone na the second kwenye STD
        self.assertEqual(adt0.tzname(), 'EDT')
        self.assertEqual(adt1.tzname(), 'EST')
        self.assertEqual(adt0 + HOUR, adt1)
        # Aware instances with fixed offset tzinfo's always have fold=0
        self.assertEqual(adt0.fold, 0)
        self.assertEqual(adt1.fold, 0)

    eleza test_pickle_fold(self):
        t = time(fold=1)
        dt = datetime(1, 1, 1, fold=1)
        kila pickler, unpickler, proto kwenye pickle_choices:
            kila x kwenye [t, dt]:
                s = pickler.dumps(x, proto)
                y = unpickler.loads(s)
                self.assertEqual(x, y)
                self.assertEqual((0 ikiwa proto < 4 else x.fold), y.fold)

    eleza test_repr(self):
        t = time(fold=1)
        dt = datetime(1, 1, 1, fold=1)
        self.assertEqual(repr(t), 'datetime.time(0, 0, fold=1)')
        self.assertEqual(repr(dt),
                         'datetime.datetime(1, 1, 1, 0, 0, fold=1)')

    eleza test_dst(self):
        # Let's first establish that things work kwenye regular times.
        dt_summer = datetime(2002, 10, 27, 1, tzinfo=Eastern2) - timedelta.resolution
        dt_winter = datetime(2002, 10, 27, 2, tzinfo=Eastern2)
        self.assertEqual(dt_summer.dst(), HOUR)
        self.assertEqual(dt_winter.dst(), ZERO)
        # The disambiguation flag ni ignored
        self.assertEqual(dt_summer.replace(fold=1).dst(), HOUR)
        self.assertEqual(dt_winter.replace(fold=1).dst(), ZERO)

        # Pick local time kwenye the fold.
        kila minute kwenye [0, 30, 59]:
            dt = datetime(2002, 10, 27, 1, minute, tzinfo=Eastern2)
            # With fold=0 (the default) it ni kwenye DST.
            self.assertEqual(dt.dst(), HOUR)
            # With fold=1 it ni kwenye STD.
            self.assertEqual(dt.replace(fold=1).dst(), ZERO)

        # Pick local time kwenye the gap.
        kila minute kwenye [0, 30, 59]:
            dt = datetime(2002, 4, 7, 2, minute, tzinfo=Eastern2)
            # With fold=0 (the default) it ni kwenye STD.
            self.assertEqual(dt.dst(), ZERO)
            # With fold=1 it ni kwenye DST.
            self.assertEqual(dt.replace(fold=1).dst(), HOUR)


    eleza test_utcoffset(self):
        # Let's first establish that things work kwenye regular times.
        dt_summer = datetime(2002, 10, 27, 1, tzinfo=Eastern2) - timedelta.resolution
        dt_winter = datetime(2002, 10, 27, 2, tzinfo=Eastern2)
        self.assertEqual(dt_summer.utcoffset(), -4 * HOUR)
        self.assertEqual(dt_winter.utcoffset(), -5 * HOUR)
        # The disambiguation flag ni ignored
        self.assertEqual(dt_summer.replace(fold=1).utcoffset(), -4 * HOUR)
        self.assertEqual(dt_winter.replace(fold=1).utcoffset(), -5 * HOUR)

    eleza test_kutokautc(self):
        # Let's first establish that things work kwenye regular times.
        u_summer = datetime(2002, 10, 27, 6, tzinfo=Eastern2) - timedelta.resolution
        u_winter = datetime(2002, 10, 27, 7, tzinfo=Eastern2)
        t_summer = Eastern2.kutokautc(u_summer)
        t_winter = Eastern2.kutokautc(u_winter)
        self.assertEqual(t_summer, u_summer - 4 * HOUR)
        self.assertEqual(t_winter, u_winter - 5 * HOUR)
        self.assertEqual(t_summer.fold, 0)
        self.assertEqual(t_winter.fold, 0)

        # What happens kwenye the fall-back fold?
        u = datetime(2002, 10, 27, 5, 30, tzinfo=Eastern2)
        t0 = Eastern2.kutokautc(u)
        u += HOUR
        t1 = Eastern2.kutokautc(u)
        self.assertEqual(t0, t1)
        self.assertEqual(t0.fold, 0)
        self.assertEqual(t1.fold, 1)
        # The tricky part ni when u ni kwenye the local fold:
        u = datetime(2002, 10, 27, 1, 30, tzinfo=Eastern2)
        t = Eastern2.kutokautc(u)
        self.assertEqual((t.day, t.hour), (26, 21))
        # .. ama gets into the local fold after a standard time adjustment
        u = datetime(2002, 10, 27, 6, 30, tzinfo=Eastern2)
        t = Eastern2.kutokautc(u)
        self.assertEqual((t.day, t.hour), (27, 1))

        # What happens kwenye the spring-forward gap?
        u = datetime(2002, 4, 7, 2, 0, tzinfo=Eastern2)
        t = Eastern2.kutokautc(u)
        self.assertEqual((t.day, t.hour), (6, 21))

    eleza test_mixed_compare_regular(self):
        t = datetime(2000, 1, 1, tzinfo=Eastern2)
        self.assertEqual(t, t.astimezone(timezone.utc))
        t = datetime(2000, 6, 1, tzinfo=Eastern2)
        self.assertEqual(t, t.astimezone(timezone.utc))

    eleza test_mixed_compare_fold(self):
        t_fold = datetime(2002, 10, 27, 1, 45, tzinfo=Eastern2)
        t_fold_utc = t_fold.astimezone(timezone.utc)
        self.assertNotEqual(t_fold, t_fold_utc)
        self.assertNotEqual(t_fold_utc, t_fold)

    eleza test_mixed_compare_gap(self):
        t_gap = datetime(2002, 4, 7, 2, 45, tzinfo=Eastern2)
        t_gap_utc = t_gap.astimezone(timezone.utc)
        self.assertNotEqual(t_gap, t_gap_utc)
        self.assertNotEqual(t_gap_utc, t_gap)

    eleza test_hash_aware(self):
        t = datetime(2000, 1, 1, tzinfo=Eastern2)
        self.assertEqual(hash(t), hash(t.replace(fold=1)))
        t_fold = datetime(2002, 10, 27, 1, 45, tzinfo=Eastern2)
        t_gap = datetime(2002, 4, 7, 2, 45, tzinfo=Eastern2)
        self.assertEqual(hash(t_fold), hash(t_fold.replace(fold=1)))
        self.assertEqual(hash(t_gap), hash(t_gap.replace(fold=1)))

SEC = timedelta(0, 1)

eleza pairs(iterable):
    a, b = itertools.tee(iterable)
    next(b, Tupu)
    rudisha zip(a, b)

kundi ZoneInfo(tzinfo):
    zoneroot = '/usr/share/zoneinfo'
    eleza __init__(self, ut, ti):
        """

        :param ut: array
            Array of transition point timestamps
        :param ti: list
            A list of (offset, isdst, abbr) tuples
        :rudisha: Tupu
        """
        self.ut = ut
        self.ti = ti
        self.lt = self.invert(ut, ti)

    @staticmethod
    eleza invert(ut, ti):
        lt = (array('q', ut), array('q', ut))
        ikiwa ut:
            offset = ti[0][0] // SEC
            lt[0][0] += offset
            lt[1][0] += offset
            kila i kwenye range(1, len(ut)):
                lt[0][i] += ti[i-1][0] // SEC
                lt[1][i] += ti[i][0] // SEC
        rudisha lt

    @classmethod
    eleza kutokafile(cls, fileobj):
        ikiwa fileobj.read(4).decode() != "TZif":
            ashiria ValueError("not a zoneinfo file")
        fileobj.seek(32)
        counts = array('i')
        counts.kutokafile(fileobj, 3)
        ikiwa sys.byteorder != 'big':
            counts.byteswap()

        ut = array('i')
        ut.kutokafile(fileobj, counts[0])
        ikiwa sys.byteorder != 'big':
            ut.byteswap()

        type_indices = array('B')
        type_indices.kutokafile(fileobj, counts[0])

        ttis = []
        kila i kwenye range(counts[1]):
            ttis.append(struct.unpack(">lbb", fileobj.read(6)))

        abbrs = fileobj.read(counts[2])

        # Convert ttis
        kila i, (gmtoff, isdst, abbrind) kwenye enumerate(ttis):
            abbr = abbrs[abbrind:abbrs.find(0, abbrind)].decode()
            ttis[i] = (timedelta(0, gmtoff), isdst, abbr)

        ti = [Tupu] * len(ut)
        kila i, idx kwenye enumerate(type_indices):
            ti[i] = ttis[idx]

        self = cls(ut, ti)

        rudisha self

    @classmethod
    eleza kutokaname(cls, name):
        path = os.path.join(cls.zoneroot, name)
        with open(path, 'rb') kama f:
            rudisha cls.kutokafile(f)

    EPOCHORDINAL = date(1970, 1, 1).toordinal()

    eleza kutokautc(self, dt):
        """datetime kwenye UTC -> datetime kwenye local time."""

        ikiwa sio isinstance(dt, datetime):
            ashiria TypeError("kutokautc() requires a datetime argument")
        ikiwa dt.tzinfo ni sio self:
            ashiria ValueError("dt.tzinfo ni sio self")

        timestamp = ((dt.toordinal() - self.EPOCHORDINAL) * 86400
                     + dt.hour * 3600
                     + dt.minute * 60
                     + dt.second)

        ikiwa timestamp < self.ut[1]:
            tti = self.ti[0]
            fold = 0
        isipokua:
            idx = bisect.bisect_right(self.ut, timestamp)
            assert self.ut[idx-1] <= timestamp
            assert idx == len(self.ut) ama timestamp < self.ut[idx]
            tti_prev, tti = self.ti[idx-2:idx]
            # Detect fold
            shift = tti_prev[0] - tti[0]
            fold = (shift > timedelta(0, timestamp - self.ut[idx-1]))
        dt += tti[0]
        ikiwa fold:
            rudisha dt.replace(fold=1)
        isipokua:
            rudisha dt

    eleza _find_ti(self, dt, i):
        timestamp = ((dt.toordinal() - self.EPOCHORDINAL) * 86400
             + dt.hour * 3600
             + dt.minute * 60
             + dt.second)
        lt = self.lt[dt.fold]
        idx = bisect.bisect_right(lt, timestamp)

        rudisha self.ti[max(0, idx - 1)][i]

    eleza utcoffset(self, dt):
        rudisha self._find_ti(dt, 0)

    eleza dst(self, dt):
        isdst = self._find_ti(dt, 1)
        # XXX: We cannot accurately determine the "save" value,
        # so let's rudisha 1h whenever DST ni kwenye effect.  Since
        # we don't use dst() kwenye kutokautc(), it ni unlikely that
        # it will be needed kila anything more than bool(dst()).
        rudisha ZERO ikiwa isdst else HOUR

    eleza tzname(self, dt):
        rudisha self._find_ti(dt, 2)

    @classmethod
    eleza zonenames(cls, zonedir=Tupu):
        ikiwa zonedir ni Tupu:
            zonedir = cls.zoneroot
        zone_tab = os.path.join(zonedir, 'zone.tab')
        jaribu:
            f = open(zone_tab)
        tatizo OSError:
            rudisha
        with f:
            kila line kwenye f:
                line = line.strip()
                ikiwa line na sio line.startswith('#'):
                    tuma line.split()[2]

    @classmethod
    eleza stats(cls, start_year=1):
        count = gap_count = fold_count = zeros_count = 0
        min_gap = min_fold = timedelta.max
        max_gap = max_fold = ZERO
        min_gap_datetime = max_gap_datetime = datetime.min
        min_gap_zone = max_gap_zone = Tupu
        min_fold_datetime = max_fold_datetime = datetime.min
        min_fold_zone = max_fold_zone = Tupu
        stats_since = datetime(start_year, 1, 1) # Starting kutoka 1970 eliminates a lot of noise
        kila zonename kwenye cls.zonenames():
            count += 1
            tz = cls.kutokaname(zonename)
            kila dt, shift kwenye tz.transitions():
                ikiwa dt < stats_since:
                    endelea
                ikiwa shift > ZERO:
                    gap_count += 1
                    ikiwa (shift, dt) > (max_gap, max_gap_datetime):
                        max_gap = shift
                        max_gap_zone = zonename
                        max_gap_datetime = dt
                    ikiwa (shift, datetime.max - dt) < (min_gap, datetime.max - min_gap_datetime):
                        min_gap = shift
                        min_gap_zone = zonename
                        min_gap_datetime = dt
                elikiwa shift < ZERO:
                    fold_count += 1
                    shift = -shift
                    ikiwa (shift, dt) > (max_fold, max_fold_datetime):
                        max_fold = shift
                        max_fold_zone = zonename
                        max_fold_datetime = dt
                    ikiwa (shift, datetime.max - dt) < (min_fold, datetime.max - min_fold_datetime):
                        min_fold = shift
                        min_fold_zone = zonename
                        min_fold_datetime = dt
                isipokua:
                    zeros_count += 1
        trans_counts = (gap_count, fold_count, zeros_count)
        andika("Number of zones:       %5d" % count)
        andika("Number of transitions: %5d = %d (gaps) + %d (folds) + %d (zeros)" %
              ((sum(trans_counts),) + trans_counts))
        andika("Min gap:         %16s at %s kwenye %s" % (min_gap, min_gap_datetime, min_gap_zone))
        andika("Max gap:         %16s at %s kwenye %s" % (max_gap, max_gap_datetime, max_gap_zone))
        andika("Min fold:        %16s at %s kwenye %s" % (min_fold, min_fold_datetime, min_fold_zone))
        andika("Max fold:        %16s at %s kwenye %s" % (max_fold, max_fold_datetime, max_fold_zone))


    eleza transitions(self):
        kila (_, prev_ti), (t, ti) kwenye pairs(zip(self.ut, self.ti)):
            shift = ti[0] - prev_ti[0]
            tuma datetime.utckutokatimestamp(t), shift

    eleza nondst_folds(self):
        """Find all folds with the same value of isdst on both sides of the transition."""
        kila (_, prev_ti), (t, ti) kwenye pairs(zip(self.ut, self.ti)):
            shift = ti[0] - prev_ti[0]
            ikiwa shift < ZERO na ti[1] == prev_ti[1]:
                tuma datetime.utckutokatimestamp(t), -shift, prev_ti[2], ti[2]

    @classmethod
    eleza print_all_nondst_folds(cls, same_abbr=Uongo, start_year=1):
        count = 0
        kila zonename kwenye cls.zonenames():
            tz = cls.kutokaname(zonename)
            kila dt, shift, prev_abbr, abbr kwenye tz.nondst_folds():
                ikiwa dt.year < start_year ama same_abbr na prev_abbr != abbr:
                    endelea
                count += 1
                andika("%3d) %-30s %s %10s %5s -> %s" %
                      (count, zonename, dt, shift, prev_abbr, abbr))

    eleza folds(self):
        kila t, shift kwenye self.transitions():
            ikiwa shift < ZERO:
                tuma t, -shift

    eleza gaps(self):
        kila t, shift kwenye self.transitions():
            ikiwa shift > ZERO:
                tuma t, shift

    eleza zeros(self):
        kila t, shift kwenye self.transitions():
            ikiwa sio shift:
                tuma t


kundi ZoneInfoTest(unittest.TestCase):
    zonename = 'America/New_York'

    eleza setUp(self):
        ikiwa sys.platform == "win32":
            self.skipTest("Skipping zoneinfo tests on Windows")
        jaribu:
            self.tz = ZoneInfo.kutokaname(self.zonename)
        tatizo FileNotFoundError kama err:
            self.skipTest("Skipping %s: %s" % (self.zonename, err))

    eleza assertEquivDatetimes(self, a, b):
        self.assertEqual((a.replace(tzinfo=Tupu), a.fold, id(a.tzinfo)),
                         (b.replace(tzinfo=Tupu), b.fold, id(b.tzinfo)))

    eleza test_folds(self):
        tz = self.tz
        kila dt, shift kwenye tz.folds():
            kila x kwenye [0 * shift, 0.5 * shift, shift - timedelta.resolution]:
                udt = dt + x
                ldt = tz.kutokautc(udt.replace(tzinfo=tz))
                self.assertEqual(ldt.fold, 1)
                adt = udt.replace(tzinfo=timezone.utc).astimezone(tz)
                self.assertEquivDatetimes(adt, ldt)
                utcoffset = ldt.utcoffset()
                self.assertEqual(ldt.replace(tzinfo=Tupu), udt + utcoffset)
                # Round trip
                self.assertEquivDatetimes(ldt.astimezone(timezone.utc),
                                          udt.replace(tzinfo=timezone.utc))


            kila x kwenye [-timedelta.resolution, shift]:
                udt = dt + x
                udt = udt.replace(tzinfo=tz)
                ldt = tz.kutokautc(udt)
                self.assertEqual(ldt.fold, 0)

    eleza test_gaps(self):
        tz = self.tz
        kila dt, shift kwenye tz.gaps():
            kila x kwenye [0 * shift, 0.5 * shift, shift - timedelta.resolution]:
                udt = dt + x
                udt = udt.replace(tzinfo=tz)
                ldt = tz.kutokautc(udt)
                self.assertEqual(ldt.fold, 0)
                adt = udt.replace(tzinfo=timezone.utc).astimezone(tz)
                self.assertEquivDatetimes(adt, ldt)
                utcoffset = ldt.utcoffset()
                self.assertEqual(ldt.replace(tzinfo=Tupu), udt.replace(tzinfo=Tupu) + utcoffset)
                # Create a local time inside the gap
                ldt = tz.kutokautc(dt.replace(tzinfo=tz)) - shift + x
                self.assertLess(ldt.replace(fold=1).utcoffset(),
                                ldt.replace(fold=0).utcoffset(),
                                "At %s." % ldt)

            kila x kwenye [-timedelta.resolution, shift]:
                udt = dt + x
                ldt = tz.kutokautc(udt.replace(tzinfo=tz))
                self.assertEqual(ldt.fold, 0)

    eleza test_system_transitions(self):
        ikiwa ('Riyadh8' kwenye self.zonename or
            # From tzdata NEWS file:
            # The files solar87, solar88, na solar89 are no longer distributed.
            # They were a negative experiment - that is, a demonstration that
            # tz data can represent solar time only with some difficulty na error.
            # Their presence kwenye the distribution caused confusion, kama Riyadh
            # civil time was generally sio solar time kwenye those years.
                self.zonename.startswith('right/')):
            self.skipTest("Skipping %s" % self.zonename)
        tz = self.tz
        TZ = os.environ.get('TZ')
        os.environ['TZ'] = self.zonename
        jaribu:
            _time.tzset()
            kila udt, shift kwenye tz.transitions():
                ikiwa udt.year >= 2037:
                    # System support kila times around the end of 32-bit time_t
                    # na later ni flaky on many systems.
                    koma
                s0 = (udt - datetime(1970, 1, 1)) // SEC
                ss = shift // SEC   # shift seconds
                kila x kwenye [-40 * 3600, -20*3600, -1, 0,
                          ss - 1, ss + 20 * 3600, ss + 40 * 3600]:
                    s = s0 + x
                    sdt = datetime.kutokatimestamp(s)
                    tzdt = datetime.kutokatimestamp(s, tz).replace(tzinfo=Tupu)
                    self.assertEquivDatetimes(sdt, tzdt)
                    s1 = sdt.timestamp()
                    self.assertEqual(s, s1)
                ikiwa ss > 0:  # gap
                    # Create local time inside the gap
                    dt = datetime.kutokatimestamp(s0) - shift / 2
                    ts0 = dt.timestamp()
                    ts1 = dt.replace(fold=1).timestamp()
                    self.assertEqual(ts0, s0 + ss / 2)
                    self.assertEqual(ts1, s0 - ss / 2)
        mwishowe:
            ikiwa TZ ni Tupu:
                toa os.environ['TZ']
            isipokua:
                os.environ['TZ'] = TZ
            _time.tzset()


kundi ZoneInfoCompleteTest(unittest.TestSuite):
    eleza __init__(self):
        tests = []
        ikiwa is_resource_enabled('tzdata'):
            kila name kwenye ZoneInfo.zonenames():
                Test = type('ZoneInfoTest[%s]' % name, (ZoneInfoTest,), {})
                Test.zonename = name
                kila method kwenye dir(Test):
                    ikiwa method.startswith('test_'):
                        tests.append(Test(method))
        super().__init__(tests)

# Iran had a sub-minute UTC offset before 1946.
kundi IranTest(ZoneInfoTest):
    zonename = 'Asia/Tehran'


kundi CapiTest(unittest.TestCase):
    eleza setUp(self):
        # Since the C API ni sio present kwenye the _Pure tests, skip all tests
        ikiwa self.__class__.__name__.endswith('Pure'):
            self.skipTest('Not relevant kwenye pure Python')

        # This *must* be called, na it must be called first, so until either
        # restriction ni loosened, we'll call it kama part of test setup
        _testcapi.test_datetime_capi()

    eleza test_utc_capi(self):
        kila use_macro kwenye (Kweli, Uongo):
            capi_utc = _testcapi.get_timezone_utc_capi(use_macro)

            with self.subTest(use_macro=use_macro):
                self.assertIs(capi_utc, timezone.utc)

    eleza test_timezones_capi(self):
        est_capi, est_macro, est_macro_nn = _testcapi.make_timezones_capi()

        exp_named = timezone(timedelta(hours=-5), "EST")
        exp_unnamed = timezone(timedelta(hours=-5))

        cases = [
            ('est_capi', est_capi, exp_named),
            ('est_macro', est_macro, exp_named),
            ('est_macro_nn', est_macro_nn, exp_unnamed)
        ]

        kila name, tz_act, tz_exp kwenye cases:
            with self.subTest(name=name):
                self.assertEqual(tz_act, tz_exp)

                dt1 = datetime(2000, 2, 4, tzinfo=tz_act)
                dt2 = datetime(2000, 2, 4, tzinfo=tz_exp)

                self.assertEqual(dt1, dt2)
                self.assertEqual(dt1.tzname(), dt2.tzname())

                dt_utc = datetime(2000, 2, 4, 5, tzinfo=timezone.utc)

                self.assertEqual(dt1.astimezone(timezone.utc), dt_utc)

    eleza test_timezones_offset_zero(self):
        utc0, utc1, non_utc = _testcapi.get_timezones_offset_zero()

        with self.subTest(testname="utc0"):
            self.assertIs(utc0, timezone.utc)

        with self.subTest(testname="utc1"):
            self.assertIs(utc1, timezone.utc)

        with self.subTest(testname="non_utc"):
            self.assertIsNot(non_utc, timezone.utc)

            non_utc_exp = timezone(timedelta(hours=0), "")

            self.assertEqual(non_utc, non_utc_exp)

            dt1 = datetime(2000, 2, 4, tzinfo=non_utc)
            dt2 = datetime(2000, 2, 4, tzinfo=non_utc_exp)

            self.assertEqual(dt1, dt2)
            self.assertEqual(dt1.tzname(), dt2.tzname())

    eleza test_check_date(self):
        kundi DateSubclass(date):
            pita

        d = date(2011, 1, 1)
        ds = DateSubclass(2011, 1, 1)
        dt = datetime(2011, 1, 1)

        is_date = _testcapi.datetime_check_date

        # Check the ones that should be valid
        self.assertKweli(is_date(d))
        self.assertKweli(is_date(dt))
        self.assertKweli(is_date(ds))
        self.assertKweli(is_date(d, Kweli))

        # Check that the subclasses do sio match exactly
        self.assertUongo(is_date(dt, Kweli))
        self.assertUongo(is_date(ds, Kweli))

        # Check that various other things are sio dates at all
        args = [tuple(), list(), 1, '2011-01-01',
                timedelta(1), timezone.utc, time(12, 00)]
        kila arg kwenye args:
            kila exact kwenye (Kweli, Uongo):
                with self.subTest(arg=arg, exact=exact):
                    self.assertUongo(is_date(arg, exact))

    eleza test_check_time(self):
        kundi TimeSubclass(time):
            pita

        t = time(12, 30)
        ts = TimeSubclass(12, 30)

        is_time = _testcapi.datetime_check_time

        # Check the ones that should be valid
        self.assertKweli(is_time(t))
        self.assertKweli(is_time(ts))
        self.assertKweli(is_time(t, Kweli))

        # Check that the subkundi does sio match exactly
        self.assertUongo(is_time(ts, Kweli))

        # Check that various other things are sio times
        args = [tuple(), list(), 1, '2011-01-01',
                timedelta(1), timezone.utc, date(2011, 1, 1)]

        kila arg kwenye args:
            kila exact kwenye (Kweli, Uongo):
                with self.subTest(arg=arg, exact=exact):
                    self.assertUongo(is_time(arg, exact))

    eleza test_check_datetime(self):
        kundi DateTimeSubclass(datetime):
            pita

        dt = datetime(2011, 1, 1, 12, 30)
        dts = DateTimeSubclass(2011, 1, 1, 12, 30)

        is_datetime = _testcapi.datetime_check_datetime

        # Check the ones that should be valid
        self.assertKweli(is_datetime(dt))
        self.assertKweli(is_datetime(dts))
        self.assertKweli(is_datetime(dt, Kweli))

        # Check that the subkundi does sio match exactly
        self.assertUongo(is_datetime(dts, Kweli))

        # Check that various other things are sio datetimes
        args = [tuple(), list(), 1, '2011-01-01',
                timedelta(1), timezone.utc, date(2011, 1, 1)]

        kila arg kwenye args:
            kila exact kwenye (Kweli, Uongo):
                with self.subTest(arg=arg, exact=exact):
                    self.assertUongo(is_datetime(arg, exact))

    eleza test_check_delta(self):
        kundi TimeDeltaSubclass(timedelta):
            pita

        td = timedelta(1)
        tds = TimeDeltaSubclass(1)

        is_timedelta = _testcapi.datetime_check_delta

        # Check the ones that should be valid
        self.assertKweli(is_timedelta(td))
        self.assertKweli(is_timedelta(tds))
        self.assertKweli(is_timedelta(td, Kweli))

        # Check that the subkundi does sio match exactly
        self.assertUongo(is_timedelta(tds, Kweli))

        # Check that various other things are sio timedeltas
        args = [tuple(), list(), 1, '2011-01-01',
                timezone.utc, date(2011, 1, 1), datetime(2011, 1, 1)]

        kila arg kwenye args:
            kila exact kwenye (Kweli, Uongo):
                with self.subTest(arg=arg, exact=exact):
                    self.assertUongo(is_timedelta(arg, exact))

    eleza test_check_tzinfo(self):
        kundi TZInfoSubclass(tzinfo):
            pita

        tzi = tzinfo()
        tzis = TZInfoSubclass()
        tz = timezone(timedelta(hours=-5))

        is_tzinfo = _testcapi.datetime_check_tzinfo

        # Check the ones that should be valid
        self.assertKweli(is_tzinfo(tzi))
        self.assertKweli(is_tzinfo(tz))
        self.assertKweli(is_tzinfo(tzis))
        self.assertKweli(is_tzinfo(tzi, Kweli))

        # Check that the subclasses do sio match exactly
        self.assertUongo(is_tzinfo(tz, Kweli))
        self.assertUongo(is_tzinfo(tzis, Kweli))

        # Check that various other things are sio tzinfos
        args = [tuple(), list(), 1, '2011-01-01',
                date(2011, 1, 1), datetime(2011, 1, 1)]

        kila arg kwenye args:
            kila exact kwenye (Kweli, Uongo):
                with self.subTest(arg=arg, exact=exact):
                    self.assertUongo(is_tzinfo(arg, exact))

    eleza test_date_kutoka_date(self):
        exp_date = date(1993, 8, 26)

        kila macro kwenye [0, 1]:
            with self.subTest(macro=macro):
                c_api_date = _testcapi.get_date_kutokadate(
                    macro,
                    exp_date.year,
                    exp_date.month,
                    exp_date.day)

                self.assertEqual(c_api_date, exp_date)

    eleza test_datetime_kutoka_dateandtime(self):
        exp_date = datetime(1993, 8, 26, 22, 12, 55, 99999)

        kila macro kwenye [0, 1]:
            with self.subTest(macro=macro):
                c_api_date = _testcapi.get_datetime_kutokadateandtime(
                    macro,
                    exp_date.year,
                    exp_date.month,
                    exp_date.day,
                    exp_date.hour,
                    exp_date.minute,
                    exp_date.second,
                    exp_date.microsecond)

                self.assertEqual(c_api_date, exp_date)

    eleza test_datetime_kutoka_dateandtimeandfold(self):
        exp_date = datetime(1993, 8, 26, 22, 12, 55, 99999)

        kila fold kwenye [0, 1]:
            kila macro kwenye [0, 1]:
                with self.subTest(macro=macro, fold=fold):
                    c_api_date = _testcapi.get_datetime_kutokadateandtimeandfold(
                        macro,
                        exp_date.year,
                        exp_date.month,
                        exp_date.day,
                        exp_date.hour,
                        exp_date.minute,
                        exp_date.second,
                        exp_date.microsecond,
                        exp_date.fold)

                    self.assertEqual(c_api_date, exp_date)
                    self.assertEqual(c_api_date.fold, exp_date.fold)

    eleza test_time_kutoka_time(self):
        exp_time = time(22, 12, 55, 99999)

        kila macro kwenye [0, 1]:
            with self.subTest(macro=macro):
                c_api_time = _testcapi.get_time_kutokatime(
                    macro,
                    exp_time.hour,
                    exp_time.minute,
                    exp_time.second,
                    exp_time.microsecond)

                self.assertEqual(c_api_time, exp_time)

    eleza test_time_kutoka_timeandfold(self):
        exp_time = time(22, 12, 55, 99999)

        kila fold kwenye [0, 1]:
            kila macro kwenye [0, 1]:
                with self.subTest(macro=macro, fold=fold):
                    c_api_time = _testcapi.get_time_kutokatimeandfold(
                        macro,
                        exp_time.hour,
                        exp_time.minute,
                        exp_time.second,
                        exp_time.microsecond,
                        exp_time.fold)

                    self.assertEqual(c_api_time, exp_time)
                    self.assertEqual(c_api_time.fold, exp_time.fold)

    eleza test_delta_kutoka_dsu(self):
        exp_delta = timedelta(26, 55, 99999)

        kila macro kwenye [0, 1]:
            with self.subTest(macro=macro):
                c_api_delta = _testcapi.get_delta_kutokadsu(
                    macro,
                    exp_delta.days,
                    exp_delta.seconds,
                    exp_delta.microseconds)

                self.assertEqual(c_api_delta, exp_delta)

    eleza test_date_kutoka_timestamp(self):
        ts = datetime(1995, 4, 12).timestamp()

        kila macro kwenye [0, 1]:
            with self.subTest(macro=macro):
                d = _testcapi.get_date_kutokatimestamp(int(ts), macro)

                self.assertEqual(d, date(1995, 4, 12))

    eleza test_datetime_kutoka_timestamp(self):
        cases = [
            ((1995, 4, 12), Tupu, Uongo),
            ((1995, 4, 12), Tupu, Kweli),
            ((1995, 4, 12), timezone(timedelta(hours=1)), Kweli),
            ((1995, 4, 12, 14, 30), Tupu, Uongo),
            ((1995, 4, 12, 14, 30), Tupu, Kweli),
            ((1995, 4, 12, 14, 30), timezone(timedelta(hours=1)), Kweli),
        ]

        kutoka_timestamp = _testcapi.get_datetime_kutokatimestamp
        kila case kwenye cases:
            kila macro kwenye [0, 1]:
                with self.subTest(case=case, macro=macro):
                    dtup, tzinfo, usetz = case
                    dt_orig = datetime(*dtup, tzinfo=tzinfo)
                    ts = int(dt_orig.timestamp())

                    dt_rt = kutoka_timestamp(ts, tzinfo, usetz, macro)

                    self.assertEqual(dt_orig, dt_rt)


eleza load_tests(loader, standard_tests, pattern):
    standard_tests.addTest(ZoneInfoCompleteTest())
    rudisha standard_tests


ikiwa __name__ == "__main__":
    unittest.main()
