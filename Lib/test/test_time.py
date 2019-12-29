kutoka test agiza support
agiza decimal
agiza enum
agiza locale
agiza math
agiza platform
agiza sys
agiza sysconfig
agiza time
agiza threading
agiza unittest
jaribu:
    agiza _testcapi
tatizo ImportError:
    _testcapi = Tupu

kutoka test.support agiza skip_if_buggy_ucrt_strfptime

# Max year ni only limited by the size of C int.
SIZEOF_INT = sysconfig.get_config_var('SIZEOF_INT') ama 4
TIME_MAXYEAR = (1 << 8 * SIZEOF_INT - 1) - 1
TIME_MINYEAR = -TIME_MAXYEAR - 1 + 1900

SEC_TO_US = 10 ** 6
US_TO_NS = 10 ** 3
MS_TO_NS = 10 ** 6
SEC_TO_NS = 10 ** 9
NS_TO_SEC = 10 ** 9

kundi _PyTime(enum.IntEnum):
    # Round towards minus infinity (-inf)
    ROUND_FLOOR = 0
    # Round towards infinity (+inf)
    ROUND_CEILING = 1
    # Round to nearest with ties going to nearest even integer
    ROUND_HALF_EVEN = 2
    # Round away kutoka zero
    ROUND_UP = 3

# Rounding modes supported by PyTime
ROUNDING_MODES = (
    # (PyTime rounding method, decimal rounding method)
    (_PyTime.ROUND_FLOOR, decimal.ROUND_FLOOR),
    (_PyTime.ROUND_CEILING, decimal.ROUND_CEILING),
    (_PyTime.ROUND_HALF_EVEN, decimal.ROUND_HALF_EVEN),
    (_PyTime.ROUND_UP, decimal.ROUND_UP),
)


kundi TimeTestCase(unittest.TestCase):

    eleza setUp(self):
        self.t = time.time()

    eleza test_data_attributes(self):
        time.altzone
        time.daylight
        time.timezone
        time.tzname

    eleza test_time(self):
        time.time()
        info = time.get_clock_info('time')
        self.assertUongo(info.monotonic)
        self.assertKweli(info.adjustable)

    eleza test_time_ns_type(self):
        eleza check_ns(sec, ns):
            self.assertIsInstance(ns, int)

            sec_ns = int(sec * 1e9)
            # tolerate a difference of 50 ms
            self.assertLess((sec_ns - ns), 50 ** 6, (sec, ns))

        check_ns(time.time(),
                 time.time_ns())
        check_ns(time.monotonic(),
                 time.monotonic_ns())
        check_ns(time.perf_counter(),
                 time.perf_counter_ns())
        check_ns(time.process_time(),
                 time.process_time_ns())

        ikiwa hasattr(time, 'thread_time'):
            check_ns(time.thread_time(),
                     time.thread_time_ns())

        ikiwa hasattr(time, 'clock_gettime'):
            check_ns(time.clock_gettime(time.CLOCK_REALTIME),
                     time.clock_gettime_ns(time.CLOCK_REALTIME))

    @unittest.skipUnless(hasattr(time, 'clock_gettime'),
                         'need time.clock_gettime()')
    eleza test_clock_realtime(self):
        t = time.clock_gettime(time.CLOCK_REALTIME)
        self.assertIsInstance(t, float)

    @unittest.skipUnless(hasattr(time, 'clock_gettime'),
                         'need time.clock_gettime()')
    @unittest.skipUnless(hasattr(time, 'CLOCK_MONOTONIC'),
                         'need time.CLOCK_MONOTONIC')
    eleza test_clock_monotonic(self):
        a = time.clock_gettime(time.CLOCK_MONOTONIC)
        b = time.clock_gettime(time.CLOCK_MONOTONIC)
        self.assertLessEqual(a, b)

    @unittest.skipUnless(hasattr(time, 'pthread_getcpuclockid'),
                         'need time.pthread_getcpuclockid()')
    @unittest.skipUnless(hasattr(time, 'clock_gettime'),
                         'need time.clock_gettime()')
    eleza test_pthread_getcpuclockid(self):
        clk_id = time.pthread_getcpuclockid(threading.get_ident())
        self.assertKweli(type(clk_id) ni int)
        # when kwenye 32-bit mode AIX only rudishas the predefined constant
        ikiwa sio platform.system() == "AIX":
            self.assertNotEqual(clk_id, time.CLOCK_THREAD_CPUTIME_ID)
        elikiwa (sys.maxsize.bit_length() > 32):
            self.assertNotEqual(clk_id, time.CLOCK_THREAD_CPUTIME_ID)
        isipokua:
            self.assertEqual(clk_id, time.CLOCK_THREAD_CPUTIME_ID)
        t1 = time.clock_gettime(clk_id)
        t2 = time.clock_gettime(clk_id)
        self.assertLessEqual(t1, t2)

    @unittest.skipUnless(hasattr(time, 'clock_getres'),
                         'need time.clock_getres()')
    eleza test_clock_getres(self):
        res = time.clock_getres(time.CLOCK_REALTIME)
        self.assertGreater(res, 0.0)
        self.assertLessEqual(res, 1.0)

    @unittest.skipUnless(hasattr(time, 'clock_settime'),
                         'need time.clock_settime()')
    eleza test_clock_settime(self):
        t = time.clock_gettime(time.CLOCK_REALTIME)
        jaribu:
            time.clock_settime(time.CLOCK_REALTIME, t)
        tatizo PermissionError:
            pita

        ikiwa hasattr(time, 'CLOCK_MONOTONIC'):
            self.assertRaises(OSError,
                              time.clock_settime, time.CLOCK_MONOTONIC, 0)

    eleza test_conversions(self):
        self.assertEqual(time.ctime(self.t),
                         time.asctime(time.localtime(self.t)))
        self.assertEqual(int(time.mktime(time.localtime(self.t))),
                         int(self.t))

    eleza test_sleep(self):
        self.assertRaises(ValueError, time.sleep, -2)
        self.assertRaises(ValueError, time.sleep, -1)
        time.sleep(1.2)

    eleza test_strftime(self):
        tt = time.gmtime(self.t)
        kila directive kwenye ('a', 'A', 'b', 'B', 'c', 'd', 'H', 'I',
                          'j', 'm', 'M', 'p', 'S',
                          'U', 'w', 'W', 'x', 'X', 'y', 'Y', 'Z', '%'):
            format = ' %' + directive
            jaribu:
                time.strftime(format, tt)
            tatizo ValueError:
                self.fail('conversion specifier: %r failed.' % format)

        self.assertRaises(TypeError, time.strftime, b'%S', tt)
        # embedded null character
        self.assertRaises(ValueError, time.strftime, '%S\0', tt)

    eleza _bounds_checking(self, func):
        # Make sure that strftime() checks the bounds of the various parts
        # of the time tuple (0 ni valid kila *all* values).

        # The year field ni tested by other test cases above

        # Check month [1, 12] + zero support
        func((1900, 0, 1, 0, 0, 0, 0, 1, -1))
        func((1900, 12, 1, 0, 0, 0, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, -1, 1, 0, 0, 0, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 13, 1, 0, 0, 0, 0, 1, -1))
        # Check day of month [1, 31] + zero support
        func((1900, 1, 0, 0, 0, 0, 0, 1, -1))
        func((1900, 1, 31, 0, 0, 0, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, -1, 0, 0, 0, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, 32, 0, 0, 0, 0, 1, -1))
        # Check hour [0, 23]
        func((1900, 1, 1, 23, 0, 0, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, -1, 0, 0, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, 24, 0, 0, 0, 1, -1))
        # Check minute [0, 59]
        func((1900, 1, 1, 0, 59, 0, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, 0, -1, 0, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, 0, 60, 0, 0, 1, -1))
        # Check second [0, 61]
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, 0, 0, -1, 0, 1, -1))
        # C99 only requires allowing kila one leap second, but Python's docs say
        # allow two leap seconds (0..61)
        func((1900, 1, 1, 0, 0, 60, 0, 1, -1))
        func((1900, 1, 1, 0, 0, 61, 0, 1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, 0, 0, 62, 0, 1, -1))
        # No check kila upper-bound day of week;
        #  value forced into range by a ``% 7`` calculation.
        # Start check at -2 since gettmarg() increments value before taking
        #  modulo.
        self.assertEqual(func((1900, 1, 1, 0, 0, 0, -1, 1, -1)),
                         func((1900, 1, 1, 0, 0, 0, +6, 1, -1)))
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, 0, 0, 0, -2, 1, -1))
        # Check day of the year [1, 366] + zero support
        func((1900, 1, 1, 0, 0, 0, 0, 0, -1))
        func((1900, 1, 1, 0, 0, 0, 0, 366, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, 0, 0, 0, 0, -1, -1))
        self.assertRaises(ValueError, func,
                            (1900, 1, 1, 0, 0, 0, 0, 367, -1))

    eleza test_strftime_bounding_check(self):
        self._bounds_checking(lambda tup: time.strftime('', tup))

    eleza test_strftime_format_check(self):
        # Test that strftime does sio crash on invalid format strings
        # that may trigger a buffer overread. When sio triggered,
        # strftime may succeed ama ashiria ValueError depending on
        # the platform.
        kila x kwenye [ '', 'A', '%A', '%AA' ]:
            kila y kwenye range(0x0, 0x10):
                kila z kwenye [ '%', 'A%', 'AA%', '%A%', 'A%A%', '%#' ]:
                    jaribu:
                        time.strftime(x * y + z)
                    tatizo ValueError:
                        pita

    eleza test_default_values_for_zero(self):
        # Make sure that using all zeros uses the proper default
        # values.  No test kila daylight savings since strftime() does
        # sio change output based on its value na no test kila year
        # because systems vary kwenye their support kila year 0.
        expected = "2000 01 01 00 00 00 1 001"
        with support.check_warnings():
            result = time.strftime("%Y %m %d %H %M %S %w %j", (2000,)+(0,)*8)
        self.assertEqual(expected, result)

    @skip_if_buggy_ucrt_strfptime
    eleza test_strptime(self):
        # Should be able to go round-trip kutoka strftime to strptime without
        # raising an exception.
        tt = time.gmtime(self.t)
        kila directive kwenye ('a', 'A', 'b', 'B', 'c', 'd', 'H', 'I',
                          'j', 'm', 'M', 'p', 'S',
                          'U', 'w', 'W', 'x', 'X', 'y', 'Y', 'Z', '%'):
            format = '%' + directive
            strf_output = time.strftime(format, tt)
            jaribu:
                time.strptime(strf_output, format)
            tatizo ValueError:
                self.fail("conversion specifier %r failed with '%s' input." %
                          (format, strf_output))

    eleza test_strptime_bytes(self):
        # Make sure only strings are accepted kama arguments to strptime.
        self.assertRaises(TypeError, time.strptime, b'2009', "%Y")
        self.assertRaises(TypeError, time.strptime, '2009', b'%Y')

    eleza test_strptime_exception_context(self):
        # check that this doesn't chain exceptions needlessly (see #17572)
        with self.assertRaises(ValueError) kama e:
            time.strptime('', '%D')
        self.assertIs(e.exception.__suppress_context__, Kweli)
        # additional check kila IndexError branch (issue #19545)
        with self.assertRaises(ValueError) kama e:
            time.strptime('19', '%Y %')
        self.assertIs(e.exception.__suppress_context__, Kweli)

    eleza test_asctime(self):
        time.asctime(time.gmtime(self.t))

        # Max year ni only limited by the size of C int.
        kila bigyear kwenye TIME_MAXYEAR, TIME_MINYEAR:
            asc = time.asctime((bigyear, 6, 1) + (0,) * 6)
            self.assertEqual(asc[-len(str(bigyear)):], str(bigyear))
        self.assertRaises(OverflowError, time.asctime,
                          (TIME_MAXYEAR + 1,) + (0,) * 8)
        self.assertRaises(OverflowError, time.asctime,
                          (TIME_MINYEAR - 1,) + (0,) * 8)
        self.assertRaises(TypeError, time.asctime, 0)
        self.assertRaises(TypeError, time.asctime, ())
        self.assertRaises(TypeError, time.asctime, (0,) * 10)

    eleza test_asctime_bounding_check(self):
        self._bounds_checking(time.asctime)

    eleza test_ctime(self):
        t = time.mktime((1973, 9, 16, 1, 3, 52, 0, 0, -1))
        self.assertEqual(time.ctime(t), 'Sun Sep 16 01:03:52 1973')
        t = time.mktime((2000, 1, 1, 0, 0, 0, 0, 0, -1))
        self.assertEqual(time.ctime(t), 'Sat Jan  1 00:00:00 2000')
        kila year kwenye [-100, 100, 1000, 2000, 2050, 10000]:
            jaribu:
                testval = time.mktime((year, 1, 10) + (0,)*6)
            tatizo (ValueError, OverflowError):
                # If mktime fails, ctime will fail too.  This may happen
                # on some platforms.
                pita
            isipokua:
                self.assertEqual(time.ctime(testval)[20:], str(year))

    @unittest.skipUnless(hasattr(time, "tzset"),
                         "time module has no attribute tzset")
    eleza test_tzset(self):

        kutoka os agiza environ

        # Epoch time of midnight Dec 25th 2002. Never DST kwenye northern
        # hemisphere.
        xmas2002 = 1040774400.0

        # These formats are correct kila 2002, na possibly future years
        # This format ni the 'standard' kama documented at:
        # http://www.opengroup.org/onlinepubs/007904975/basedefs/xbd_chap08.html
        # They are also documented kwenye the tzset(3) man page on most Unix
        # systems.
        eastern = 'EST+05EDT,M4.1.0,M10.5.0'
        victoria = 'AEST-10AEDT-11,M10.5.0,M3.5.0'
        utc='UTC+0'

        org_TZ = environ.get('TZ',Tupu)
        jaribu:
            # Make sure we can switch to UTC time na results are correct
            # Note that unknown timezones default to UTC.
            # Note that altzone ni undefined kwenye UTC, kama there ni no DST
            environ['TZ'] = eastern
            time.tzset()
            environ['TZ'] = utc
            time.tzset()
            self.assertEqual(
                time.gmtime(xmas2002), time.localtime(xmas2002)
                )
            self.assertEqual(time.daylight, 0)
            self.assertEqual(time.timezone, 0)
            self.assertEqual(time.localtime(xmas2002).tm_isdst, 0)

            # Make sure we can switch to US/Eastern
            environ['TZ'] = eastern
            time.tzset()
            self.assertNotEqual(time.gmtime(xmas2002), time.localtime(xmas2002))
            self.assertEqual(time.tzname, ('EST', 'EDT'))
            self.assertEqual(len(time.tzname), 2)
            self.assertEqual(time.daylight, 1)
            self.assertEqual(time.timezone, 18000)
            self.assertEqual(time.altzone, 14400)
            self.assertEqual(time.localtime(xmas2002).tm_isdst, 0)
            self.assertEqual(len(time.tzname), 2)

            # Now go to the southern hemisphere.
            environ['TZ'] = victoria
            time.tzset()
            self.assertNotEqual(time.gmtime(xmas2002), time.localtime(xmas2002))

            # Issue #11886: Australian Eastern Standard Time (UTC+10) ni called
            # "EST" (as Eastern Standard Time, UTC-5) instead of "AEST"
            # (non-DST timezone), na "EDT" instead of "AEDT" (DST timezone),
            # on some operating systems (e.g. FreeBSD), which ni wrong. See for
            # example this bug:
            # http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=93810
            self.assertIn(time.tzname[0], ('AEST' 'EST'), time.tzname[0])
            self.assertKweli(time.tzname[1] kwenye ('AEDT', 'EDT'), str(time.tzname[1]))
            self.assertEqual(len(time.tzname), 2)
            self.assertEqual(time.daylight, 1)
            self.assertEqual(time.timezone, -36000)
            self.assertEqual(time.altzone, -39600)
            self.assertEqual(time.localtime(xmas2002).tm_isdst, 1)

        mwishowe:
            # Repair TZ environment variable kwenye case any other tests
            # rely on it.
            ikiwa org_TZ ni sio Tupu:
                environ['TZ'] = org_TZ
            elikiwa 'TZ' kwenye environ:
                toa environ['TZ']
            time.tzset()

    eleza test_insane_timestamps(self):
        # It's possible that some platform maps time_t to double,
        # na that this test will fail there.  This test should
        # exempt such platforms (provided they rudisha reasonable
        # results!).
        kila func kwenye time.ctime, time.gmtime, time.localtime:
            kila unreasonable kwenye -1e200, 1e200:
                self.assertRaises(OverflowError, func, unreasonable)

    eleza test_ctime_without_arg(self):
        # Not sure how to check the values, since the clock could tick
        # at any time.  Make sure these are at least accepted and
        # don't ashiria errors.
        time.ctime()
        time.ctime(Tupu)

    eleza test_gmtime_without_arg(self):
        gt0 = time.gmtime()
        gt1 = time.gmtime(Tupu)
        t0 = time.mktime(gt0)
        t1 = time.mktime(gt1)
        self.assertAlmostEqual(t1, t0, delta=0.2)

    eleza test_localtime_without_arg(self):
        lt0 = time.localtime()
        lt1 = time.localtime(Tupu)
        t0 = time.mktime(lt0)
        t1 = time.mktime(lt1)
        self.assertAlmostEqual(t1, t0, delta=0.2)

    eleza test_mktime(self):
        # Issue #1726687
        kila t kwenye (-2, -1, 0, 1):
            jaribu:
                tt = time.localtime(t)
            tatizo (OverflowError, OSError):
                pita
            isipokua:
                self.assertEqual(time.mktime(tt), t)

    # Issue #13309: pitaing extreme values to mktime() ama localtime()
    # borks the glibc's internal timezone data.
    @unittest.skipUnless(platform.libc_ver()[0] != 'glibc',
                         "disabled because of a bug kwenye glibc. Issue #13309")
    eleza test_mktime_error(self):
        # It may sio be possible to reliably make mktime rudisha error
        # on all platfom.  This will make sure that no other exception
        # than OverflowError ni ashiriad kila an extreme value.
        tt = time.gmtime(self.t)
        tzname = time.strftime('%Z', tt)
        self.assertNotEqual(tzname, 'LMT')
        jaribu:
            time.mktime((-1, 1, 1, 0, 0, 0, -1, -1, -1))
        tatizo OverflowError:
            pita
        self.assertEqual(time.strftime('%Z', tt), tzname)

    eleza test_monotonic(self):
        # monotonic() should sio go backward
        times = [time.monotonic() kila n kwenye range(100)]
        t1 = times[0]
        kila t2 kwenye times[1:]:
            self.assertGreaterEqual(t2, t1, "times=%s" % times)
            t1 = t2

        # monotonic() includes time elapsed during a sleep
        t1 = time.monotonic()
        time.sleep(0.5)
        t2 = time.monotonic()
        dt = t2 - t1
        self.assertGreater(t2, t1)
        # bpo-20101: tolerate a difference of 50 ms because of bad timer
        # resolution on Windows
        self.assertKweli(0.450 <= dt)

        # monotonic() ni a monotonic but non adjustable clock
        info = time.get_clock_info('monotonic')
        self.assertKweli(info.monotonic)
        self.assertUongo(info.adjustable)

    eleza test_perf_counter(self):
        time.perf_counter()

    eleza test_process_time(self):
        # process_time() should sio include time spend during a sleep
        start = time.process_time()
        time.sleep(0.100)
        stop = time.process_time()
        # use 20 ms because process_time() has usually a resolution of 15 ms
        # on Windows
        self.assertLess(stop - start, 0.020)

        info = time.get_clock_info('process_time')
        self.assertKweli(info.monotonic)
        self.assertUongo(info.adjustable)

    eleza test_thread_time(self):
        ikiwa sio hasattr(time, 'thread_time'):
            ikiwa sys.platform.startswith(('linux', 'win')):
                self.fail("time.thread_time() should be available on %r"
                          % (sys.platform,))
            isipokua:
                self.skipTest("need time.thread_time")

        # thread_time() should sio include time spend during a sleep
        start = time.thread_time()
        time.sleep(0.100)
        stop = time.thread_time()
        # use 20 ms because thread_time() has usually a resolution of 15 ms
        # on Windows
        self.assertLess(stop - start, 0.020)

        info = time.get_clock_info('thread_time')
        self.assertKweli(info.monotonic)
        self.assertUongo(info.adjustable)

    @unittest.skipUnless(hasattr(time, 'clock_settime'),
                         'need time.clock_settime')
    eleza test_monotonic_settime(self):
        t1 = time.monotonic()
        realtime = time.clock_gettime(time.CLOCK_REALTIME)
        # jump backward with an offset of 1 hour
        jaribu:
            time.clock_settime(time.CLOCK_REALTIME, realtime - 3600)
        tatizo PermissionError kama err:
            self.skipTest(err)
        t2 = time.monotonic()
        time.clock_settime(time.CLOCK_REALTIME, realtime)
        # monotonic must sio be affected by system clock updates
        self.assertGreaterEqual(t2, t1)

    eleza test_localtime_failure(self):
        # Issue #13847: check kila localtime() failure
        invalid_time_t = Tupu
        kila time_t kwenye (-1, 2**30, 2**33, 2**60):
            jaribu:
                time.localtime(time_t)
            tatizo OverflowError:
                self.skipTest("need 64-bit time_t")
            tatizo OSError:
                invalid_time_t = time_t
                koma
        ikiwa invalid_time_t ni Tupu:
            self.skipTest("unable to find an invalid time_t value")

        self.assertRaises(OSError, time.localtime, invalid_time_t)
        self.assertRaises(OSError, time.ctime, invalid_time_t)

        # Issue #26669: check kila localtime() failure
        self.assertRaises(ValueError, time.localtime, float("nan"))
        self.assertRaises(ValueError, time.ctime, float("nan"))

    eleza test_get_clock_info(self):
        clocks = ['monotonic', 'perf_counter', 'process_time', 'time']

        kila name kwenye clocks:
            info = time.get_clock_info(name)

            #self.assertIsInstance(info, dict)
            self.assertIsInstance(info.implementation, str)
            self.assertNotEqual(info.implementation, '')
            self.assertIsInstance(info.monotonic, bool)
            self.assertIsInstance(info.resolution, float)
            # 0.0 < resolution <= 1.0
            self.assertGreater(info.resolution, 0.0)
            self.assertLessEqual(info.resolution, 1.0)
            self.assertIsInstance(info.adjustable, bool)

        self.assertRaises(ValueError, time.get_clock_info, 'xxx')


kundi TestLocale(unittest.TestCase):
    eleza setUp(self):
        self.oldloc = locale.setlocale(locale.LC_ALL)

    eleza tearDown(self):
        locale.setlocale(locale.LC_ALL, self.oldloc)

    eleza test_bug_3061(self):
        jaribu:
            tmp = locale.setlocale(locale.LC_ALL, "fr_FR")
        tatizo locale.Error:
            self.skipTest('could sio set locale.LC_ALL to fr_FR')
        # This should sio cause an exception
        time.strftime("%B", (2009,2,1,0,0,0,0,0,0))


kundi _TestAsctimeYear:
    _format = '%d'

    eleza yearstr(self, y):
        rudisha time.asctime((y,) + (0,) * 8).split()[-1]

    eleza test_large_year(self):
        # Check that it doesn't crash kila year > 9999
        self.assertEqual(self.yearstr(12345), '12345')
        self.assertEqual(self.yearstr(123456789), '123456789')

kundi _TestStrftimeYear:

    # Issue 13305:  For years < 1000, the value ni sio always
    # padded to 4 digits across platforms.  The C standard
    # assumes year >= 1900, so it does sio specify the number
    # of digits.

    ikiwa time.strftime('%Y', (1,) + (0,) * 8) == '0001':
        _format = '%04d'
    isipokua:
        _format = '%d'

    eleza yearstr(self, y):
        rudisha time.strftime('%Y', (y,) + (0,) * 8)

    eleza test_4dyear(self):
        # Check that we can rudisha the zero padded value.
        ikiwa self._format == '%04d':
            self.test_year('%04d')
        isipokua:
            eleza year4d(y):
                rudisha time.strftime('%4Y', (y,) + (0,) * 8)
            self.test_year('%04d', func=year4d)

    eleza skip_if_not_supported(y):
        msg = "strftime() ni limited to [1; 9999] with Visual Studio"
        # Check that it doesn't crash kila year > 9999
        jaribu:
            time.strftime('%Y', (y,) + (0,) * 8)
        tatizo ValueError:
            cond = Uongo
        isipokua:
            cond = Kweli
        rudisha unittest.skipUnless(cond, msg)

    @skip_if_not_supported(10000)
    eleza test_large_year(self):
        rudisha super().test_large_year()

    @skip_if_not_supported(0)
    eleza test_negative(self):
        rudisha super().test_negative()

    toa skip_if_not_supported


kundi _Test4dYear:
    _format = '%d'

    eleza test_year(self, fmt=Tupu, func=Tupu):
        fmt = fmt ama self._format
        func = func ama self.yearstr
        self.assertEqual(func(1),    fmt % 1)
        self.assertEqual(func(68),   fmt % 68)
        self.assertEqual(func(69),   fmt % 69)
        self.assertEqual(func(99),   fmt % 99)
        self.assertEqual(func(999),  fmt % 999)
        self.assertEqual(func(9999), fmt % 9999)

    eleza test_large_year(self):
        self.assertEqual(self.yearstr(12345).lstrip('+'), '12345')
        self.assertEqual(self.yearstr(123456789).lstrip('+'), '123456789')
        self.assertEqual(self.yearstr(TIME_MAXYEAR).lstrip('+'), str(TIME_MAXYEAR))
        self.assertRaises(OverflowError, self.yearstr, TIME_MAXYEAR + 1)

    eleza test_negative(self):
        self.assertEqual(self.yearstr(-1), self._format % -1)
        self.assertEqual(self.yearstr(-1234), '-1234')
        self.assertEqual(self.yearstr(-123456), '-123456')
        self.assertEqual(self.yearstr(-123456789), str(-123456789))
        self.assertEqual(self.yearstr(-1234567890), str(-1234567890))
        self.assertEqual(self.yearstr(TIME_MINYEAR), str(TIME_MINYEAR))
        # Modules/timemodule.c checks kila underflow
        self.assertRaises(OverflowError, self.yearstr, TIME_MINYEAR - 1)
        with self.assertRaises(OverflowError):
            self.yearstr(-TIME_MAXYEAR - 1)


kundi TestAsctime4dyear(_TestAsctimeYear, _Test4dYear, unittest.TestCase):
    pita

kundi TestStrftime4dyear(_TestStrftimeYear, _Test4dYear, unittest.TestCase):
    pita


kundi TestPytime(unittest.TestCase):
    @skip_if_buggy_ucrt_strfptime
    @unittest.skipUnless(time._STRUCT_TM_ITEMS == 11, "needs tm_zone support")
    eleza test_localtime_timezone(self):

        # Get the localtime na examine it kila the offset na zone.
        lt = time.localtime()
        self.assertKweli(hasattr(lt, "tm_gmtoff"))
        self.assertKweli(hasattr(lt, "tm_zone"))

        # See ikiwa the offset na zone are similar to the module
        # attributes.
        ikiwa lt.tm_gmtoff ni Tupu:
            self.assertKweli(not hasattr(time, "timezone"))
        isipokua:
            self.assertEqual(lt.tm_gmtoff, -[time.timezone, time.altzone][lt.tm_isdst])
        ikiwa lt.tm_zone ni Tupu:
            self.assertKweli(not hasattr(time, "tzname"))
        isipokua:
            self.assertEqual(lt.tm_zone, time.tzname[lt.tm_isdst])

        # Try na make UNIX times kutoka the localtime na a 9-tuple
        # created kutoka the localtime. Test to see that the times are
        # the same.
        t = time.mktime(lt); t9 = time.mktime(lt[:9])
        self.assertEqual(t, t9)

        # Make localtimes kutoka the UNIX times na compare them to
        # the original localtime, thus making a round trip.
        new_lt = time.localtime(t); new_lt9 = time.localtime(t9)
        self.assertEqual(new_lt, lt)
        self.assertEqual(new_lt.tm_gmtoff, lt.tm_gmtoff)
        self.assertEqual(new_lt.tm_zone, lt.tm_zone)
        self.assertEqual(new_lt9, lt)
        self.assertEqual(new_lt.tm_gmtoff, lt.tm_gmtoff)
        self.assertEqual(new_lt9.tm_zone, lt.tm_zone)

    @unittest.skipUnless(time._STRUCT_TM_ITEMS == 11, "needs tm_zone support")
    eleza test_strptime_timezone(self):
        t = time.strptime("UTC", "%Z")
        self.assertEqual(t.tm_zone, 'UTC')
        t = time.strptime("+0500", "%z")
        self.assertEqual(t.tm_gmtoff, 5 * 3600)

    @unittest.skipUnless(time._STRUCT_TM_ITEMS == 11, "needs tm_zone support")
    eleza test_short_times(self):

        agiza pickle

        # Load a short time structure using pickle.
        st = b"ctime\nstruct_time\np0\n((I2007\nI8\nI11\nI1\nI24\nI49\nI5\nI223\nI1\ntp1\n(dp2\ntp3\nRp4\n."
        lt = pickle.loads(st)
        self.assertIs(lt.tm_gmtoff, Tupu)
        self.assertIs(lt.tm_zone, Tupu)


@unittest.skipIf(_testcapi ni Tupu, 'need the _testcapi module')
kundi CPyTimeTestCase:
    """
    Base kundi to test the C _PyTime_t API.
    """
    OVERFLOW_SECONDS = Tupu

    eleza setUp(self):
        kutoka _testcapi agiza SIZEOF_TIME_T
        bits = SIZEOF_TIME_T * 8 - 1
        self.time_t_min = -2 ** bits
        self.time_t_max = 2 ** bits - 1

    eleza time_t_filter(self, seconds):
        rudisha (self.time_t_min <= seconds <= self.time_t_max)

    eleza _rounding_values(self, use_float):
        "Build timestamps used to test rounding."

        units = [1, US_TO_NS, MS_TO_NS, SEC_TO_NS]
        ikiwa use_float:
            # picoseconds are only tested to pytime_converter accepting floats
            units.append(1e-3)

        values = (
            # small values
            1, 2, 5, 7, 123, 456, 1234,
            # 10^k - 1
            9,
            99,
            999,
            9999,
            99999,
            999999,
            # test half even rounding near 0.5, 1.5, 2.5, 3.5, 4.5
            499, 500, 501,
            1499, 1500, 1501,
            2500,
            3500,
            4500,
        )

        ns_timestamps = [0]
        kila unit kwenye units:
            kila value kwenye values:
                ns = value * unit
                ns_timestamps.extend((-ns, ns))
        kila pow2 kwenye (0, 5, 10, 15, 22, 23, 24, 30, 33):
            ns = (2 ** pow2) * SEC_TO_NS
            ns_timestamps.extend((
                -ns-1, -ns, -ns+1,
                ns-1, ns, ns+1
            ))
        kila seconds kwenye (_testcapi.INT_MIN, _testcapi.INT_MAX):
            ns_timestamps.append(seconds * SEC_TO_NS)
        ikiwa use_float:
            # numbers with an exact representation kwenye IEEE 754 (base 2)
            kila pow2 kwenye (3, 7, 10, 15):
                ns = 2.0 ** (-pow2)
                ns_timestamps.extend((-ns, ns))

        # seconds close to _PyTime_t type limit
        ns = (2 ** 63 // SEC_TO_NS) * SEC_TO_NS
        ns_timestamps.extend((-ns, ns))

        rudisha ns_timestamps

    eleza _check_rounding(self, pytime_converter, expected_func,
                        use_float, unit_to_sec, value_filter=Tupu):

        eleza convert_values(ns_timestamps):
            ikiwa use_float:
                unit_to_ns = SEC_TO_NS / float(unit_to_sec)
                values = [ns / unit_to_ns kila ns kwenye ns_timestamps]
            isipokua:
                unit_to_ns = SEC_TO_NS // unit_to_sec
                values = [ns // unit_to_ns kila ns kwenye ns_timestamps]

            ikiwa value_filter:
                values = filter(value_filter, values)

            # remove duplicates na sort
            rudisha sorted(set(values))

        # test rounding
        ns_timestamps = self._rounding_values(use_float)
        valid_values = convert_values(ns_timestamps)
        kila time_rnd, decimal_rnd kwenye ROUNDING_MODES :
            with decimal.localcontext() kama context:
                context.rounding = decimal_rnd

                kila value kwenye valid_values:
                    debug_info = {'value': value, 'rounding': decimal_rnd}
                    jaribu:
                        result = pytime_converter(value, time_rnd)
                        expected = expected_func(value)
                    tatizo Exception kama exc:
                        self.fail("Error on timestamp conversion: %s" % debug_info)
                    self.assertEqual(result,
                                     expected,
                                     debug_info)

        # test overflow
        ns = self.OVERFLOW_SECONDS * SEC_TO_NS
        ns_timestamps = (-ns, ns)
        overflow_values = convert_values(ns_timestamps)
        kila time_rnd, _ kwenye ROUNDING_MODES :
            kila value kwenye overflow_values:
                debug_info = {'value': value, 'rounding': time_rnd}
                with self.assertRaises(OverflowError, msg=debug_info):
                    pytime_converter(value, time_rnd)

    eleza check_int_rounding(self, pytime_converter, expected_func,
                           unit_to_sec=1, value_filter=Tupu):
        self._check_rounding(pytime_converter, expected_func,
                             Uongo, unit_to_sec, value_filter)

    eleza check_float_rounding(self, pytime_converter, expected_func,
                             unit_to_sec=1, value_filter=Tupu):
        self._check_rounding(pytime_converter, expected_func,
                             Kweli, unit_to_sec, value_filter)

    eleza decimal_round(self, x):
        d = decimal.Decimal(x)
        d = d.quantize(1)
        rudisha int(d)


kundi TestCPyTime(CPyTimeTestCase, unittest.TestCase):
    """
    Test the C _PyTime_t API.
    """
    # _PyTime_t ni a 64-bit signed integer
    OVERFLOW_SECONDS = math.ceil((2**63 + 1) / SEC_TO_NS)

    eleza test_FromSeconds(self):
        kutoka _testcapi agiza PyTime_FromSeconds

        # PyTime_FromSeconds() expects a C int, reject values out of range
        eleza c_int_filter(secs):
            rudisha (_testcapi.INT_MIN <= secs <= _testcapi.INT_MAX)

        self.check_int_rounding(lambda secs, rnd: PyTime_FromSeconds(secs),
                                lambda secs: secs * SEC_TO_NS,
                                value_filter=c_int_filter)

        # test nan
        kila time_rnd, _ kwenye ROUNDING_MODES:
            with self.assertRaises(TypeError):
                PyTime_FromSeconds(float('nan'))

    eleza test_FromSecondsObject(self):
        kutoka _testcapi agiza PyTime_FromSecondsObject

        self.check_int_rounding(
            PyTime_FromSecondsObject,
            lambda secs: secs * SEC_TO_NS)

        self.check_float_rounding(
            PyTime_FromSecondsObject,
            lambda ns: self.decimal_round(ns * SEC_TO_NS))

        # test nan
        kila time_rnd, _ kwenye ROUNDING_MODES:
            with self.assertRaises(ValueError):
                PyTime_FromSecondsObject(float('nan'), time_rnd)

    eleza test_AsSecondsDouble(self):
        kutoka _testcapi agiza PyTime_AsSecondsDouble

        eleza float_converter(ns):
            ikiwa abs(ns) % SEC_TO_NS == 0:
                rudisha float(ns // SEC_TO_NS)
            isipokua:
                rudisha float(ns) / SEC_TO_NS

        self.check_int_rounding(lambda ns, rnd: PyTime_AsSecondsDouble(ns),
                                float_converter,
                                NS_TO_SEC)

        # test nan
        kila time_rnd, _ kwenye ROUNDING_MODES:
            with self.assertRaises(TypeError):
                PyTime_AsSecondsDouble(float('nan'))

    eleza create_decimal_converter(self, denominator):
        denom = decimal.Decimal(denominator)

        eleza converter(value):
            d = decimal.Decimal(value) / denom
            rudisha self.decimal_round(d)

        rudisha converter

    eleza test_AsTimeval(self):
        kutoka _testcapi agiza PyTime_AsTimeval

        us_converter = self.create_decimal_converter(US_TO_NS)

        eleza timeval_converter(ns):
            us = us_converter(ns)
            rudisha divmod(us, SEC_TO_US)

        ikiwa sys.platform == 'win32':
            kutoka _testcapi agiza LONG_MIN, LONG_MAX

            # On Windows, timeval.tv_sec type ni a C long
            eleza seconds_filter(secs):
                rudisha LONG_MIN <= secs <= LONG_MAX
        isipokua:
            seconds_filter = self.time_t_filter

        self.check_int_rounding(PyTime_AsTimeval,
                                timeval_converter,
                                NS_TO_SEC,
                                value_filter=seconds_filter)

    @unittest.skipUnless(hasattr(_testcapi, 'PyTime_AsTimespec'),
                         'need _testcapi.PyTime_AsTimespec')
    eleza test_AsTimespec(self):
        kutoka _testcapi agiza PyTime_AsTimespec

        eleza timespec_converter(ns):
            rudisha divmod(ns, SEC_TO_NS)

        self.check_int_rounding(lambda ns, rnd: PyTime_AsTimespec(ns),
                                timespec_converter,
                                NS_TO_SEC,
                                value_filter=self.time_t_filter)

    eleza test_AsMilliseconds(self):
        kutoka _testcapi agiza PyTime_AsMilliseconds

        self.check_int_rounding(PyTime_AsMilliseconds,
                                self.create_decimal_converter(MS_TO_NS),
                                NS_TO_SEC)

    eleza test_AsMicroseconds(self):
        kutoka _testcapi agiza PyTime_AsMicroseconds

        self.check_int_rounding(PyTime_AsMicroseconds,
                                self.create_decimal_converter(US_TO_NS),
                                NS_TO_SEC)


kundi TestOldPyTime(CPyTimeTestCase, unittest.TestCase):
    """
    Test the old C _PyTime_t API: _PyTime_ObjectToXXX() functions.
    """

    # time_t ni a 32-bit ama 64-bit signed integer
    OVERFLOW_SECONDS = 2 ** 64

    eleza test_object_to_time_t(self):
        kutoka _testcapi agiza pytime_object_to_time_t

        self.check_int_rounding(pytime_object_to_time_t,
                                lambda secs: secs,
                                value_filter=self.time_t_filter)

        self.check_float_rounding(pytime_object_to_time_t,
                                  self.decimal_round,
                                  value_filter=self.time_t_filter)

    eleza create_converter(self, sec_to_unit):
        eleza converter(secs):
            floatpart, intpart = math.modf(secs)
            intpart = int(intpart)
            floatpart *= sec_to_unit
            floatpart = self.decimal_round(floatpart)
            ikiwa floatpart < 0:
                floatpart += sec_to_unit
                intpart -= 1
            elikiwa floatpart >= sec_to_unit:
                floatpart -= sec_to_unit
                intpart += 1
            rudisha (intpart, floatpart)
        rudisha converter

    eleza test_object_to_timeval(self):
        kutoka _testcapi agiza pytime_object_to_timeval

        self.check_int_rounding(pytime_object_to_timeval,
                                lambda secs: (secs, 0),
                                value_filter=self.time_t_filter)

        self.check_float_rounding(pytime_object_to_timeval,
                                  self.create_converter(SEC_TO_US),
                                  value_filter=self.time_t_filter)

         # test nan
        kila time_rnd, _ kwenye ROUNDING_MODES:
            with self.assertRaises(ValueError):
                pytime_object_to_timeval(float('nan'), time_rnd)

    eleza test_object_to_timespec(self):
        kutoka _testcapi agiza pytime_object_to_timespec

        self.check_int_rounding(pytime_object_to_timespec,
                                lambda secs: (secs, 0),
                                value_filter=self.time_t_filter)

        self.check_float_rounding(pytime_object_to_timespec,
                                  self.create_converter(SEC_TO_NS),
                                  value_filter=self.time_t_filter)

        # test nan
        kila time_rnd, _ kwenye ROUNDING_MODES:
            with self.assertRaises(ValueError):
                pytime_object_to_timespec(float('nan'), time_rnd)


ikiwa __name__ == "__main__":
    unittest.main()
